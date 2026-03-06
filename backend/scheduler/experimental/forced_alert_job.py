## This experimental job is for testing purposes.
## It fetches real prices from a given asset and sends a Telegram message with updated price, price change and percentage change.
import logging

from backend.services.finantial_data_service import FinancialDataService
from backend.services.telegram_service import TelegramService
from backend.persistance.db_manager import get_db_session
from backend.models.asset import Asset

logger = logging.getLogger(__name__)

def updated_price_send_alert(app):
    with app.app_context():
        try:
            with get_db_session() as session:
                price_change_message = "Forced alert job executed successfully. Latest prices:\n" 
                assets = session.query(Asset).all()
                tickers = [asset.ticker for asset in assets]
                prices = FinancialDataService.latest_prices(tickers)
                
                for asset in assets:
                    asset.update_price_statistics(prices.get(asset.ticker, asset.price))
                    price_change_message += f"{asset.ticker}: ${(asset.price):.2f},  change {(asset.price_change):.2f}, {(asset.price_change_percent):.2f}% \n"
                
                if TelegramService.send_message(app, price_change_message):
                    logger.info("Forced alert job: Telegram message sent successfully")
                else:
                    logger.error("Forced alert job: Failed to send Telegram message")
        except Exception as exc:
            logger.error(f"Failed to fetch latest prices for some of the tickers: {exc}")
            return
