from flask import Blueprint, jsonify, request
import logging
from ..services.telegram_service import TelegramService
from ..services.finantial_data_service import FinancialDataService
from flask import current_app

logger = logging.getLogger(__name__)

telegrams_blueprint = Blueprint('telegrams', __name__, url_prefix='/telegram')

def _help_command(args):
    help_text = (
        "Available commands:\n"
        "/help - Show this help message\n"
        "/search {query} - Searches for assets matching with given term. \n"
        "/ex_rate - Returns the latest exchange rate for USD/MXN.\n"
        "/watchlists {watchlist_name} - Returns all user's watchlists. Optionally, can provide a name to filter.\n"
        "/watchlist-new {watchlist_name} - Creates a new watchlist with the given name.\n"
        "/watchlist-add {watchlist_name} {asset_ticker} - Adds an asset to a watchlist.\n"
        "/watchlist-remove {watchlist_name} {asset_ticker} - Removes an asset from a watchlist.\n"
        "/watchlist-delete {watchlist_name} - Deletes a watchlist.\n"
        "/alerts {asset_ticker} - Returns all user's alerts. Optionally, can filter alerts by asset ticker.\n"
        "/alert_set {asset_ticker} {alert_type} {target_price} - Sets a new alert for an asset. Alert type can be 'MonthMinimum', 'PriceAbove' or 'PriceBelow'.\n"
        "/alert_unset {alert_id} - Removes an alert by its ID.\n"
        "/alert_update {alert_id} {alert_type} {new_target_price} - Updates the target price of an existing alert.\n"
    )
    TelegramService.send_message(current_app, help_text)

def _search_command(args):
    # Implement search logic here, e.g., query a database or an API
    try:
        if len(args) == 0:
            TelegramService.send_message(current_app, "Please provide a search term after the /search command.")
            return
        
        query = " ".join(args)
        search_results = FinancialDataService.search_tickers(query, maximum_results=15)
        TelegramService.send_message(current_app, search_results)
    except Exception as e:
        logger.error(f"Error processing search command: {e}")
        TelegramService.send_message(current_app, f"Error processing search command: {e}")
        return
    
def _exchange_rate_command(args):
    try:
        rate = "USD/MXN"
        exchange_rate = FinancialDataService.exchange_rate(rate)
        if exchange_rate:
            TelegramService.send_message(current_app, f"{round(exchange_rate['rate'], 4)}")
        else:
            TelegramService.send_message(current_app, f"Could not retrieve exchange rate for {rate}.")
    except Exception as e:
        logger.error(f"Error fetching exchange rate {rate}: {e}")
        TelegramService.send_message(current_app, f"Error fetching exchange rate {rate}: {e}")
        return

def _process_command(command):
    logger.info(f"Processing Telegram command: {command}")
    args = command.split()
    cmd = args[0].lower()
    switcher = {
        "/help": _help_command,
        "/search": _search_command,
        "/ex_rate": _exchange_rate_command
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
