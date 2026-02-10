from typing import List, Dict, Any, Optional
from tqdm import tqdm
from peewee import IntegrityError, fn
import email.utils
from dateutil import parser
import datetime

from src.services.gmail_client import GmailClient
from src.models import Email, db

class EmailSyncer:
    def __init__(self):
        self.gmail = GmailClient()

    def sync(self, limit: Optional[int] = 200, year: Optional[int] = None, after: Optional[str] = None, before: Optional[str] = None):
        """Fetch emails from Gmail and save to SQLite."""
        if after and before:
            query = f"after:{after} before:{before}"
        elif year:
            query = f"after:{year}/01/01 before:{year}/12/31"
        else:
            query = None
        
        print(f"Syncing last {limit} emails{' for range ' + after + ' to ' + before if after else (' for year ' + str(year) if year else '')}...")
        
        # Authenticate first
        self.gmail.authenticate()
        
        raw_emails = self.gmail.fetch_emails(limit=limit, query=query)
        
        new_count = 0
        with db.atomic():
            for email_data in tqdm(raw_emails, desc="Saving to DB"):
                try:
                    # Normalize sender
                    raw_sender = email_data.get('sender', '')
                    _, sender_email = email.utils.parseaddr(raw_sender)
                    sender = sender_email if sender_email else raw_sender

                    # Parse date
                    raw_date = email_data.get('date')
                    try:
                        date_obj = parser.parse(raw_date) if raw_date else datetime.datetime.now()
                    except Exception:
                        date_obj = datetime.datetime.now()

                    Email.create(
                        id=email_data['id'],
                        sender=sender,
                        subject=email_data.get('subject', ''),
                        snippet=email_data.get('snippet', ''),
                        date=date_obj,
                        size_estimate=email_data.get('sizeEstimate', 0)
                    )
                    new_count += 1
                except IntegrityError:
                    # Already exists
                    pass
        
        print(f"Sync complete. New emails: {new_count}")

    def get_top_senders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return top senders by frequency."""
        query = (Email
                 .select(Email.sender, fn.COUNT(Email.id).alias('count'))
                 .group_by(Email.sender)
                 .order_by(fn.COUNT(Email.id).desc())
                 .limit(limit))
        
        return [{'sender': row.sender, 'count': row.count} for row in query]
