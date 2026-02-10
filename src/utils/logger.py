import logging
import sys
from typing import Optional

def setup_logger(name: str = "GmailArchivist", level: int = logging.INFO) -> logging.Logger:
    """Sets up a logger with a standard format."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(level)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def clean_snippet(snippet: str) -> str:
    """Cleans up the email snippet for better processing."""
    if not snippet:
        return ""
    # Remove excessive whitespace and newlines
    return " ".join(snippet.split())
