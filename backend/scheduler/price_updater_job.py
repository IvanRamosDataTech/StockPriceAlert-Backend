import logging

from ..models.asset import Asset
from ..persistance.db_manager import get_db_session
from ..services.finantial_data_service import FinancialDataService
from ..services.alert_service import AlertService

logger = logging.getLogger(__name__)


def update_prices_and_alerts(app):
	"""
	Fetch latest prices for all assets attached to watchlists, persist updates,
	then check all alerts.
	"""
	with app.app_context():
		try:
			with get_db_session() as session:
				assets = session.query(Asset).all()
				tickers = [asset.ticker for asset in assets]
				prices = FinancialDataService.latest_prices(tickers)
				for asset in assets:
					latest_price = prices.get(asset.ticker, asset.price)
					asset.update_price_statistics(latest_price)
				AlertService.check_all_alerts(app)
			
		except Exception as exc:
			logger.error(f"Failed to fetch latest prices: {exc}")
			return
