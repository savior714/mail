import os
import sys
import time
import warnings
warnings.simplefilter('ignore')
from tqdm import tqdm
from dotenv import load_dotenv

from src.config import AppConfig
from src.services.gmail_client import GmailClient
from src.services.classifier import EmailClassifier
from src.services.reporter import Reporter
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)

def main():
    logger.info("Starting Gmail-AI-Archivist Dry Run...")

    # 1. Initialize Components
    try:
        gmail = GmailClient()
        classifier = EmailClassifier()
    except Exception as e:
        logger.critical("Initialization failed: %s", e)
        sys.exit(1)

    # 2. Fetch Emails
    logger.info("Fetching last %d emails...", AppConfig.FETCH_LIMIT)
    emails = gmail.fetch_emails(limit=AppConfig.FETCH_LIMIT)
    
    if not emails:
        logger.warning("No emails to process. Exiting.")
        return

    # 3. Classify Emails
    results = []
    logger.info("Classifying emails...")
    
    for email in tqdm(emails, desc="Processing"):
        try:
            result = classifier.classify(email)
            results.append(result)
            # Sleep briefly to avoid hitting rate limits slightly (though usually okay for 50)
            time.sleep(0.1) 
        except Exception as e:
            logger.error("Error processing email %s: %s", email.get('id'), e)
            # Append as error/unclassified so we track it
            results.append({**email, "category": "Error", "method": "Error", "reasoning": str(e)})

    # 4. Generate Report
    Reporter.save_report(results)
    
    logger.info("Dry run completed successfully.")

if __name__ == "__main__":
    main()
