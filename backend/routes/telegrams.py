from flask import Blueprint, jsonify, request
import logging
from ..services.telegram_service import TelegramService
from flask import current_app

logger = logging.getLogger(__name__)

telegrams_blueprint = Blueprint('telegrams', __name__, url_prefix='/telegram')

@telegrams_blueprint.route('/', methods=["POST"])
def send_telegram_message():
    logger.info("Telegram message route called")
    data = request.get_json()
    # if not data.get("message"):
    #     return jsonify({"error": "json input needs a message property "}), 400
    try:
        logger.info(f"Received message to send: {data}")
        TelegramService.send_message(current_app, str(data))
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({"error": "Failed to parse message. json with 'text' property is required"}), 400
