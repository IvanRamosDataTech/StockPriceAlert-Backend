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
        
    @staticmethod
    def get_exchange_rate(pair="USD/MXN"):
        """
        Get the latest exchange rate for a currency pair
        
        pair - Valid exchange rate symbol. Should be provided as a string in the format "BASE/QUOTE" e.g. "USD/EUR"
        return - A dictionary containing the exchange rate information, or an empty dictionary if no data found
        """
        if '/' not in pair:
            raise ValueError("Invalid currency pair format. Use 'BASE/QUOTE' format.")
        
        try:
            exchange_rate = yf.Lookup(pair).currency
            if not exchange_rate.empty:
                shortName = exchange_rate["shortName"].values[0]
                rate = exchange_rate["regularMarketPrice"].values[0]
                return {"exchange_rate": shortName, "rate": rate}
            else:
                return {}  # Return empty dictionary if no data found
        except Exception as e:
            logger.error(f"Fetched object: {exchange_rate}")
            logger.error(f"Error fetching exchange rate for pair {pair}: {e}")
            raise e
