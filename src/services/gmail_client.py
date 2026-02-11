import os.path
import pickle
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest
import threading

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# If modifying these scopes, delete the file token.json.
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailClient:
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._local = threading.local()
        self._labels_cache = {}

    def authenticate(self):
        """Authenticates the user and creates the service."""
        creds = None
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                logger.error("Error loading token.json: %s", e)
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error("Error refreshing token: %s", e)
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}. Please download it from Google Cloud Console.")
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error("Error during authentication flow: %s", e)
                    raise

            # Save the credentials for the next run
            try:
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                logger.error("Error saving token.json: %s", e)
        
        return creds

    def _get_service(self):
        """Returns a thread-local service instance."""
        if not hasattr(self._local, 'service'):
            creds = self.authenticate()
            try:
                self._local.service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
                logger.info("Thread-local Gmail API service built.")
            except HttpError as error:
                logger.error("An error occurred building the service: %s", error)
                raise
        return self._local.service

    @property
    def service(self):
        return self._get_service()

    def get_labels(self) -> Dict[str, str]:
        """Returns a mapping of {name: id} for all labels."""
        
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            self._labels_cache = {l['name']: l['id'] for l in labels}
            return self._labels_cache
        except HttpError as error:
            logger.error("Error fetching labels: %s", error)
            return {}

    def create_label(self, label_name: str) -> str:
        """Creates a label and returns its ID."""
        try:
            label_body = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            label = self.service.users().labels().create(userId='me', body=label_body).execute()
            logger.info("Created label: %s", label_name)
            return label['id']
        except HttpError as error:
            if error.resp.status == 409: # Already exists
                labels = self.get_labels()
                return labels.get(label_name)
            logger.error("Error creating label %s: %s", label_name, error)
            raise

    def get_or_create_label(self, label_name: str) -> str:
        """Ensures a label exists and returns its ID."""
        labels = self.get_labels()
        if label_name in labels:
            return labels[label_name]
        return self.create_label(label_name)

    def batch_modify(self, message_ids: List[str], add_labels: List[str], remove_labels: List[str]):
        """Modifies labels for multiple messages."""
        if not message_ids:
            return

        body = {
            'ids': message_ids,
            'addLabelIds': add_labels,
            'removeLabelIds': remove_labels
        }
        try:
            self.service.users().messages().batchModify(userId='me', body=body).execute()
            logger.info("Batch modified %d messages.", len(message_ids))
        except HttpError as error:
            logger.error("Error in batchModify: %s", error)
            raise

    def fetch_emails(self, limit: Optional[int] = 50, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches a list of emails with optional query.
        If limit is None, fetches all matching messages using pagination.
        Returns a list of dictionaries with 'id', 'snippet', 'sender', 'subject', 'date'.
        """
        if not self.service:
            self.authenticate()

        if self.service is None:
            raise RuntimeError("Gmail service authentication failed.")

        results = []
        try:
            page_token = None
            while True:
                # Call the Gmail API
                max_results = min(limit - len(results), 500) if limit else 500
                if limit and max_results <= 0:
                    break

                response = self.service.users().messages().list(
                    userId='me', maxResults=max_results, q=query, pageToken=page_token
                ).execute()
                
                messages = response.get('messages', [])
                if not messages:
                    break

                logger.info("Fetching details for %d messages using batch request...", len(messages))

                # Use batch request instead of ThreadPoolExecutor to reduce API calls
                batch_results = []
                
                def callback(request_id, response, exception):
                    """Callback for batch request"""
                    if exception:
                        logger.error(f"Batch request error for {request_id}: {exception}")
                    else:
                        try:
                            headers = response.get('payload', {}).get('headers', [])
                            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "(No Subject)")
                            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "(Unknown Sender)")
                            date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), None)
                            snippet = response.get('snippet', '')

                            batch_results.append({
                                'id': response['id'],
                                'snippet': snippet,
                                'sender': sender,
                                'subject': subject,
                                'date': date_str,
                                'sizeEstimate': response.get('sizeEstimate', 0)
                            })
                        except Exception as e:
                            logger.error(f"Error parsing batch response: {e}")

                # Create batch request
                batch = self.service.new_batch_http_request(callback=callback)
                for message in messages:
                    batch.add(self.service.users().messages().get(
                        userId='me', 
                        id=message['id'], 
                        format='metadata'
                    ))
                
                # Execute batch request
                try:
                    batch.execute()
                except HttpError as error:
                    logger.error(f"Batch execution error: {error}")
                
                results.extend(batch_results)
                
                if limit and len(results) >= limit:
                    results = results[:limit]
                    break

                page_token = response.get('nextPageToken')
                if not page_token or (limit and len(results) >= limit):
                    break

        except HttpError as error:
            logger.error("An error occurred fetching emails: %s", error)
            return []

        return results
