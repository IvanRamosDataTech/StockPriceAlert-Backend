from flask import Blueprint, jsonify, request
import logging
from ..services.telegram_service import TelegramService
from flask import current_app

logger = logging.getLogger(__name__)

telegrams_blueprint = Blueprint('telegrams', __name__, url_prefix='/telegram')

def _help_command(args):
    help_text = (
        "Available commands:\n"
        "/help - Show this help message\n"
        "/search {query} - Searches for assets matching with given term. \n"
        "/status - Get the current status of the system\n"
        # Add more commands as needed
    )
    TelegramService.send_message(current_app, help_text)

def _search_command(args):
    # Implement search logic here, e.g., query a database or an API
    try:
        if len(args) == 0:
            TelegramService.send_message(current_app, "Please provide a search term after the /search command.")
            return
        
        query = args[0]
        search_results = f"Search results for '{query}':\n1. Result 1\n2. Result 2\n3. Result 3"
        TelegramService.send_message(current_app, search_results)
    except Exception as e:
        logger.error(f"Error processing search command: {e}")
        TelegramService.send_message(current_app, "An error occurred while processing your search. Please try again.")
        return
    

def _process_command(command):
    logger.info(f"Processing Telegram command: {command}")
    args = command.split()
    cmd = args[0].lower()
    switcher = {
        "/help": _help_command,
        "/search": _search_command,
    }
    func = switcher.get(cmd, None)
    if func:
        func(args[1:])
    else:
        TelegramService.send_message(current_app, f"Unknown command: {cmd}")


@telegrams_blueprint.route('/', methods=["POST"])
def send_telegram_message():
    data = request.get_json()
    try:
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
