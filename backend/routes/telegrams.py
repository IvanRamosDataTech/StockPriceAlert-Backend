from flask import Blueprint, jsonify, request
import logging
from ..services.telegram_service import TelegramService
from flask import current_app

logger = logging.getLogger(__name__)

telegrams_blueprint = Blueprint('telegrams', __name__, url_prefix='/telegram')

def _process_command(command):
    logger.info(f"Processing command: {command}")
    # Implement command processing logic here
    TelegramService.send_message(current_app, f"Processed command: {command}")


@telegrams_blueprint.route('/', methods=["POST"])
def send_telegram_message():
    logger.info("Telegram message route called")
    data = request.get_json()
    # if not data.get("message"):
    #     return jsonify({"error": "json input needs a message property "}), 400
    try:
        logger.info(f"Received message to send: {data}")
        message_obj = data.get("message", None)
        if message_obj and "entities" in message_obj and message_obj["entities"][0]["type"] == "bot_command":
            text = message_obj["text"]
            _process_command(text)
        else:
            TelegramService.send_message(current_app, "I didn't get that. Please use /help to see available commands.")
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"error": "Failed to parse message. json with 'text' property is required"}), 400
