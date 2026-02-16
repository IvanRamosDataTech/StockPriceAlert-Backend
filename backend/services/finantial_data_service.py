import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FinancialDataService:

    @staticmethod
    def get_latest_prices(tickers=[]):
        """
        Get the latest prices for a list of tickers
        
        tickers should be provided as a list of strings e.g. ["AAPL", "GOOGL", "MSFT"]
        """
        ticker_list = [ticker.strip() for ticker in tickers]
        
        try:
            indexed_prices = yf.Tickers(ticker_list)
            prices = {ticker: indexed_prices.tickers[ticker].info['regularMarketPrice'] for ticker in ticker_list}
            return prices
        except Exception as e:
            logger.error(f"Error fetching prices for tickers {ticker_list}: {e}")
            raise e
