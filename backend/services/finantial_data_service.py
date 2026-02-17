import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FinancialDataService:

    @staticmethod
    def latest_prices(tickers=[]):
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
    def exchange_rate(pair="USD/MXN"):
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
        
    @staticmethod
    def historical_prices(ticker_list, period="1d", interval="15m"):
        """
        Get historical prices for a list of tickers
        
        tickers - List of stock ticker symbols as strings e.g. ["AAPL", "GOOGL"]
        period - Data period to fetch (e.g. "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        interval - Data interval (e.g. "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo")
        
        return - A list of dictionaries containing date and closing price
        """
        try:    
            historical_prices = yf.download(ticker_list, period=period, interval=interval)
            clean_prices = historical_prices.drop(columns=["Volume"], level=0)
            clean_prices = clean_prices.stack(level=1)
            clean_prices = clean_prices.reset_index()
            clean_prices = clean_prices.rename(columns={"level_1": "Ticker"})
            clean_prices["Date"] = clean_prices["Date"].dt.strftime('%d-%m-%Y')
            # clean_prices
            grouped = clean_prices.groupby("Ticker")
            return {
                ticker: group.to_dict(orient="records") for ticker, group in grouped
            }
        except Exception as e:
            logger.error(f"Error fetching historical prices for tickers {ticker_list}: {e}")
            raise e
        
    @staticmethod
    def search_tickers(query, maximum_results=10):
        """
        Search for tickers based on a query string
        
        query - The search query string e.g. "Micron Tech"
        
        return - A list of dictionaries containing ticker symbol and short name
        """
        try:
            search_results = yf.Search(query=query, max_results=maximum_results).quotes
            refined_results = []
            for result in search_results:
                refined_results.append({
                    "ticker": result['symbol'],
                    "displayed_name": result['shortname'],
                    "exchange": result['exchange'],
                    "asset_type": result['quoteType']
                })
            return refined_results
        except Exception as e:
            logger.error(f"Error searching for tickers with query '{query}': {e}")
            raise e