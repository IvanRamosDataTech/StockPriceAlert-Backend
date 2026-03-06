## This experimental job is for testing purposes.
## It fetches real prices from a given asset and sends a Telegram message with updated price, price change and percentage change.
import logging

from backend.services.finantial_data_service import FinancialDataService
from backend.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)

def updated_price_send_alert(app, ticker="AAPL"):
    with app.app_context():
        try:
            prices = FinancialDataService.latest_prices(tickers=[ticker])
        except Exception as exc:
            logger.error(f"Failed to fetch latest price for {ticker}: {exc}")
            return

        message = f"Latest price for {ticker}: ${prices[ticker]:.2f}"
        if TelegramService.send_message(app, message):
            logger.info(f"Sent price update for {ticker} to Telegram successfully")
        else:
            logger.error(f"Failed to send price update for {ticker} to Telegram")