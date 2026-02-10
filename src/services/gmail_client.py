import os.path
import pickle
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailClient:
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None

    def authenticate(self):
        """Authenticates the user and creates the service."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                logger.error("Error loading token.json: %s", e)
                creds = None

        # If there are no (valid) credentials available, let the user log in.
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

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API service built successfully.")
        except HttpError as error:
            logger.error("An error occurred building the service: %s", error)
            raise

    def fetch_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetches a list of emails.
        Returns a list of dictionaries with 'id', 'snippet', 'sender', 'subject'.
        """
        if not self.service:
            self.authenticate()

        if self.service is None:
            raise RuntimeError("Gmail service authentication failed.")

        results = []
        try:
            # Call the Gmail API
            response = self.service.users().messages().list(userId='me', maxResults=limit).execute()
            messages = response.get('messages', [])

            if not messages:
                logger.info("No messages found.")
                return []

            logger.info("Fetching details for %d messages...", len(messages))

            # Batch request could be optimized here, but for 50 it's okay to loop for MVP simplicity
            # or we can use batch execute if strict performance is needed. 
            # For this MVP, we will fetch individually but ensure we handle errors.
            
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='metadata').execute()
                
                headers = msg.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "(No Subject)")
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "(Unknown Sender)")
                snippet = msg.get('snippet', '')

                results.append({
                    'id': message['id'],
                    'snippet': snippet,
                    'sender': sender,
                    'subject': subject
                })

        except HttpError as error:
            logger.error("An error occurred fetching emails: %s", error)
            return []

        return results
