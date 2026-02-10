# Production Usage Guide

## Step 1: Initial Sync
Start by syncing your emails to the local database. For large mailboxes (10+ years), use the year filter:
```bash
python src/main_local.py --year 2024
```
This will fetch metadata for the specified year and store it in `emails.db`.

## Step 2: AI Classification Audit
Once synced, open the TUI:
```bash
python src/main_local.py
```
1.  Select **[2] Generate Rules**.
2.  Open `rules.json` in your editor. You will see senders with their counts and last interaction dates.
3.  **Audit**: If you see a sender you want to classify differently, change the `"category"` value.
4.  **Save**: Your changes will be preserved and prioritized over future AI suggestions.

## Step 3: Cloud Synchronization
Ready to organize your actual Gmail?
1.  Select **[4] Cloud Sync**.
2.  Choose whether to archive processed emails from the Inbox (`y/n`).
3.  The system will apply:
    -   Category Label (e.g., `Archived/💰_Finance`)
    -   History Tag (e.g., `History/Batch_20260211`)
    -   Cleanup Tag (`⚠️_Big_Trash` for files >= 5MB in Promo)

## 🛡️ Rollback Strategy
If you discover a batch was misclassified:
1.  Go to Gmail.
2.  Search for the tag: `label:History-Batch_20260211`.
3.  **Action**: Use the search result to bulk move emails back to the inbox or change labels.

## 💾 Storage Cleanup
To reclaim space:
1.  Search `label:⚠️-Big-Trash`.
2.  Verify the contents (typically high-res newsletter PDFs or promotional attachments).
3.  Select All -> Delete.
