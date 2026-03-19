import logging

from ..models.asset import Asset
from ..persistance.db_manager import get_db_session
from ..services.finantial_data_service import FinancialDataService

logger = logging.getLogger(__name__)


def update_monthly_stats(app):
	"""
	Fetch historical prices for watchlist assets and update price statistics.
	"""
	with app.app_context():
		try:
			with get_db_session() as session:
				assets = session.query(Asset).all()
				tickers = [asset.ticker for asset in assets]
				statistics = FinancialDataService.statistics_in_period(tickers, period="1mo", interval="1d")
				for asset in assets:
					if asset.ticker in statistics:
						asset.min_month_price = statistics[asset.ticker]["minimum"]
						asset.max_month_price = statistics[asset.ticker]["maximum"]
						asset.avg_month_price = statistics[asset.ticker]["average"]
						asset.update_modification_date()
						
		except Exception as exc:
			logger.error(f"Failed to fetch historical prices: {exc}")
			return