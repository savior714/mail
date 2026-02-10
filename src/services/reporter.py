import json
import os
from datetime import datetime
from typing import List, Dict, Any

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class Reporter:
    @staticmethod
    def save_report(results: List[Dict[str, Any]], prefix: str = "dry_run_report") -> str:
        """
        Saves the classification results to a JSON file.
        Returns the filename.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            logger.info("Report saved successfully to %s", filename)
            return filename
        except Exception as e:
            logger.error("Failed to save report: %s", e)
            return ""
