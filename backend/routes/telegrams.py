from flask import Blueprint, jsonify, request
import logging
from ..services.telegram_service import TelegramService
from ..services.finantial_data_service import FinancialDataService
from ..logic_units.watchlists_units import fetch_watchlists, new_watchlist, add_asset_to_watchlist, remove_asset_from_watchlist, delete_watchlist
from ..logic_units.alerts_units import fetch_alerts, create_alert, delete_alert, update_alert

from flask import current_app

logger = logging.getLogger(__name__)

telegrams_blueprint = Blueprint('telegrams', __name__, url_prefix='/telegram')

def _help_command(args):
    help_text = (
        "Available commands:\n"
        "/help - Show this help message\n"
        "/search {query} - Searches for assets matching with given term. \n"
        "/ex_rate - Returns the latest exchange rate for USD/MXN.\n"
        "/prices {ticker1 ticker2 ...} - Returns the latest prices for a list of asset tickers. Asset tickers should be provided as space separated values.\n"
        "/watchlists {watchlist_name} - Returns all user's watchlists. Optionally, can provide a name to filter.\n"
        "/watchlist_new {watchlist_id} - Creates a new watchlist with the given name.\n"
        "/watchlist_add {watchlist_id} {asset_ticker} - Adds an asset to a watchlist.\n"
        "/watchlist_remove {watchlist_id} {asset_ticker} - Removes an asset from a watchlist.\n"
        "/watchlist_delete {watchlist_id} - Deletes a watchlist.\n"
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

def _prices_command(args):
    try:
        if len(args) == 0:
            TelegramService.send_message(current_app, "Missing tickers. Please provide a list of asset tickers e.g. /prices AAPL GOOGL MSFT")
            return
        
        tickers = [arg.strip() for arg in args if arg.strip()]
        prices = FinancialDataService.latest_prices(tickers)
        TelegramService.send_message(current_app, prices)
    except Exception as e:
        logger.error(f"Error processing prices command: {e}")
        TelegramService.send_message(current_app, f"Error processing prices command: {e}")
        return
    
def _watchlists_command(args):
    try:
        name_filter = " ".join(args) if len(args) > 0 else None
        watchlists = fetch_watchlists(name_filter)
        TelegramService.send_message(current_app, watchlists)
    except Exception as e:
        logger.error(f"Error processing watchlists command: {e}")
        TelegramService.send_message(current_app, f"Error processing watchlists command: {e}")
        return
    
def _watchlist_new_command(args):
    try:
        if len(args) == 0:
            TelegramService.send_message(current_app, "Missing watchlist name. Please provide a name for the new watchlist e.g. /watchlist_new Tech Stocks")
            return
        
        name = " ".join(args)
        (id, name) = new_watchlist(name)        
        TelegramService.send_message(current_app, f"Watchlist created successfully with id {id} and name '{name}'")
    except ValueError as ve:
        logger.error(f"Error creating watchlist: {ve}")
        TelegramService.send_message(current_app, f"Error creating watchlist: {ve}")
    except Exception as e:
        logger.error(f"Error processing watchlist_new command: {e}")
        TelegramService.send_message(current_app, f"Error processing watchlist_new command: {e}")
        return

def _watchlist_add_asset_command(args):
    
    if not args or len(args) != 2:
        TelegramService.send_message(current_app, "Missing parameters. Please provide a watchlist id and an asset ticker e.g. /watchlist_add 1 HOOD")
        return
    
    watchlist_id = args[0]
    ticker = args[1]
    
    try:
        updated_watchlist = add_asset_to_watchlist(watchlist_id, ticker)
        TelegramService.send_message(current_app, f"Asset '{ticker}' added to watchlist '{updated_watchlist['name']}' successfully.")
    except ValueError as ve:
        logger.error(f"Error adding asset to watchlist: {ve}")
        TelegramService.send_message(current_app, f"Error adding asset to watchlist: {ve}")
    except LookupError as le:
        logger.error(f"Error adding asset to watchlist: {le}")
        TelegramService.send_message(current_app, f"Error adding asset to watchlist: {le}")
    except Exception as e:
        logger.error(f"Error processing watchlist_add command: {e}")
        TelegramService.send_message(current_app, f"Error processing watchlist_add command: {e}")
        return
        
def _watchlist_remove_asset_command(args):
    
    if not args or len(args) != 2:
        TelegramService.send_message(current_app, "Missing parameters. Please provide a watchlist id and an asset ticker e.g. /watchlist_remove 3 GLXL")
        return

    watchlist_id = args[0]
    ticker = args[1]
    
    try:
        updated_watchlist = remove_asset_from_watchlist(watchlist_id, ticker)
        TelegramService.send_message(current_app, f"Asset '{ticker}' removed from watchlist '{updated_watchlist['name']}' successfully.")
    except ValueError as ve:
        logger.error(f"Error removing asset from watchlist: {ve}")
        TelegramService.send_message(current_app, f"Error removing asset from watchlist: {ve}")
    except LookupError as le:
        logger.error(f"Error removing asset from watchlist: {le}")
        TelegramService.send_message(current_app, f"Error removing asset from watchlist: {le}")
    except Exception as e:
        logger.error(f"Error processing watchlist_remove command: {e}")
        TelegramService.send_message(current_app, f"Error processing watchlist_remove command: {e}")
        return
    
def _watchlist_delete_command(args):
    
    if not args or len(args) != 1:
        TelegramService.send_message(current_app, "Missing parameters. Please provide a watchlist id e.g. /watchlist_delete 2")
        return

    watchlist_id = args[0]
    
    try:
        deleted_watchlist = delete_watchlist(watchlist_id)
        TelegramService.send_message(current_app, f"Watchlist '{deleted_watchlist['name']}' deleted successfully.")
    except LookupError as le:
        logger.error(f"Error deleting watchlist: {le}")
        TelegramService.send_message(current_app, f"Error deleting watchlist: {le}")
    except Exception as e:
        logger.error(f"Error processing watchlist_delete command: {e}")
        TelegramService.send_message(current_app, f"Error processing watchlist_delete command: {e}")
        return

def _alerts_command(args):
    try:
        ticker = args[0] if len(args) > 0 else None
        alerts = fetch_alerts(ticker)
        TelegramService.send_message(current_app, alerts)
    except LookupError as le:   
        logger.error(f"Error fetching alerts: {le}")
        TelegramService.send_message(current_app, f"Error fetching alerts: {le}")
    except Exception as e:
        logger.error(f"Error processing alerts command: {e}")
        TelegramService.send_message(current_app, f"Error processing alerts command: {e}")
        return

def _process_command(command):
    logger.info(f"Processing Telegram command: {command}")
    args = command.split()
    cmd = args[0].lower()
    switcher = {
        "/help": _help_command,
        "/search": _search_command,
        "/ex_rate": _exchange_rate_command,
        "/prices": _prices_command,
        "/watchlists": _watchlists_command,
        "/watchlist_new": _watchlist_new_command,
        "/watchlist_add": _watchlist_add_asset_command,
        "/watchlist_remove": _watchlist_remove_asset_command,
        "/watchlist_delete": _watchlist_delete_command,
        "/alerts": _alerts_command
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
