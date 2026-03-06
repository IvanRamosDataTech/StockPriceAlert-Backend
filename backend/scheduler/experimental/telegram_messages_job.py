## Experimental job to verify communication of web app and Telegram bot for testing purposes.
#  Not intended for production use. Uncomment in scheduler.py to activate.

import logging
from datetime import datetime

from backend.services.telegram_service import TelegramService

def send_test_telegram_message(app, message):
    """
    Send a test message to Telegram to verify communication.
    """
    logger = logging.getLogger(__name__)
    logger.info(f" Telegram Message Job - executed at {datetime.now()}")
    success = TelegramService.send_message(app, message)
    if success:
        logger.info("Test message sent successfully")
    else:
        logger.error("Failed to send test message")

