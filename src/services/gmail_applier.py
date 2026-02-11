import json
import os
import datetime
from typing import List, Dict, Any
import logging
from src.services.gmail_client import GmailClient
from src.models import Email


class GmailApplier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gmail = GmailClient()

    def apply_to_gmail(self, archive_inbox: bool = True):
        """
        1. Find all emails classified but NOT synced in DB.
        2. Group by category.
        3. For each category:
           a. Add target label (e.g. "Archived/💰_Finance").
           b. REMOVE all other "Archived/*" labels found in Gmail for cleanup.
           c. Apply in chunks of 500.
        4. Mark DB as is_synced=True.
        """
        self.logger.info("Pushing local classifications to Gmail (Delta Sync)...")
        
        query = (Email
                 .select()
                 .where((Email.is_classified == True) & (Email.is_synced == False)))
        
        emails_to_apply = list(query)
        if not emails_to_apply:
            self.logger.warning("No unsynced classified emails found in local DB.")
            return

        # Fetch all Gmail labels to identify "Archived/*" labels for removal
        all_labels = self.gmail.get_labels() # name -> id
        archived_label_ids = [lid for name, lid in all_labels.items() if name.startswith("Archived/")]
        
        # 2. Prepare Big Trash label
        trash_label_name = "⚠️_Big_Trash"
        trash_label_id = self.gmail.get_or_create_label(trash_label_name)

        # 3. Group by category
        category_map = {} # category -> list of email_ids
        trash_list = []
        
        for email in emails_to_apply:
            cat = email.category
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(email.id)
            
            # Big Trash Logic
            is_promo = "Shopping" in cat or "Promo" in cat
            if is_promo and email.size_estimate >= 5000000:
                trash_list.append(email.id)

        # 4. Process each category
        for category, email_ids in category_map.items():
            if category == 'Unclassified':
                continue
                
            label_name = f"Archived/{category}"
            label_id = self.gmail.get_or_create_label(label_name)
            
            # Labels to remove: INBOX + all other Archived/* labels
            other_archived_ids = [lid for lid in archived_label_ids if lid != label_id]
            remove_labels = other_archived_ids
            if archive_inbox:
                remove_labels.append('INBOX')

            self.logger.info(f"Processing {label_name} ({len(email_ids)} emails)...")
            
            chunk_size = 500
            for i in range(0, len(email_ids), chunk_size):
                chunk = email_ids[i:i + chunk_size]
                try:
                    self.gmail.batch_modify(chunk, [label_id], remove_labels)
                    # Mark as synced in DB
                    Email.update(is_synced=True).where(Email.id << chunk).execute()
                except Exception as e:
                    self.logger.error(f"Error applying label {label_name}: {e}")

        # Big Trash Label
        if trash_list:
            self.logger.info(f"Flagging {len(trash_list)} Big Trash emails...")
            for i in range(0, len(trash_list), 500):
                chunk = trash_list[i:i + 500]
                try:
                    # Note: we don't remove other labels here, just add trash label
                    self.gmail.batch_modify(chunk, [trash_label_id], [])
                except Exception as e:
                    self.logger.error(f"Error applying big trash label: {e}")

        self.logger.info("Success! Delta cloud sync complete.")

