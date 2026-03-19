import requests
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    @staticmethod
    def send_message(app, message):
        """
        Sends messages to the configured Telegram bot and chat.
        """
        with app.app_context():
            bot_token = app.config.get("TELEGRAM_BOT_TOKEN")
            chat_id = app.config.get("TELEGRAM_CHAT_ID")

            if not bot_token or not chat_id:
                logger.error("Telegram bot token or chat ID not configured")
                return False

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
            }

            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info("Message sent to Telegram successfully")
                    return True
                else:
                    logger.error(f"Failed to send message to Telegram: {response.text}")
                    return False
            except requests.RequestException as exc:
                logger.error(f"Failed to send message to Telegram: {exc}")
                return False