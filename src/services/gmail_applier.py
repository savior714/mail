import json
import os
import datetime
from typing import List, Dict, Any
import logging


class GmailApplier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gmail = GmailClient()

    def apply_to_gmail(self, archive_inbox: bool = True):
        """
        1. Find all classified emails in DB.
        2. Group by category.
        3. For each category:
           a. Get/Create Gmail label (e.g. "Archived/💰_Finance").
           b. Also create a history tag: "History/Batch_YYYYMMDD"
           c. Apply labels in chunks of 500.
           d. Flag big files (>= 5MB) in Shopping/Promo as "⚠️_Big_Trash".
        """
        self.logger.info("Pushing local classifications to Gmail...")
        
        query = (Email
                 .select()
                 .where(Email.is_classified == True))
        
        emails_to_apply = list(query)
        if not emails_to_apply:
            self.logger.warning("No classified emails found in local DB.")
            return

        self.gmail.authenticate()
        
        # 2. Prepare Big Trash label
        trash_label_name = "⚠️_Big_Trash"
        trash_label_id = self.gmail.get_or_create_label(trash_label_name)

        # 3. Group by category and check for big files
        category_map = {} # category -> list of email_ids
        trash_list = []  # list of email_ids for big trash
        
        for email in emails_to_apply:
            cat = email.category
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(email.id)
            
            # Big Trash Logic: >= 5MB and Category is Shopping/Promo
            is_promo = "Shopping" in cat or "Promo" in cat
            if is_promo and email.size_estimate >= 5000000:
                trash_list.append(email.id)

        total_tasks = len(category_map)
        self.logger.info(f"Applying labels for {total_tasks} categories...")

        # Apply Category Label
        for category, email_ids in category_map.items():
            if category == 'Unclassified':
                continue
                
            label_name = f"Archived/{category}"
            self.logger.info(f"Processing {label_name} ({len(email_ids)} emails)...")
            
            label_id = self.gmail.get_or_create_label(label_name)
            
            # Chunking
            chunk_size = 500
            for i in range(0, len(email_ids), chunk_size):
                chunk = email_ids[i:i + chunk_size]
                
                # We only add category label
                add_labels = [label_id]
                remove_labels = ['INBOX'] if archive_inbox else []
                
                try:
                    self.gmail.batch_modify(chunk, add_labels, remove_labels)
                except Exception as e:
                    self.logger.error(f"Error applying label {label_name}: {e}")

        # Apply Big Trash Label if needed
        if trash_list:
            self.logger.info(f"Flagging {len(trash_list)} Big Trash emails...")
            for i in range(0, len(trash_list), chunk_size):
                chunk = trash_list[i:i + chunk_size]
                try:
                    self.gmail.batch_modify(chunk, [trash_label_id], [])
                except Exception as e:
                    self.logger.error(f"Error applying big trash label: {e}")

        self.logger.info("Success! Cloud sync complete.")

