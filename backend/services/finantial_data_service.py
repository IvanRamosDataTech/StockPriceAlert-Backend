import statistics

import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FinancialDataService:

    @staticmethod
    def latest_prices(tickers=[], conversion="USD/MXN"):
        """
        Get the latest prices for a list of tickers
        
        tickers should be provided as a list of strings e.g. ["AAPL", "GOOGL", "MSFT"]
        """
        ticker_list = [ticker.strip() for ticker in tickers]
        
        try:
            indexed_prices = yf.Tickers(ticker_list)
            conversion_rate = FinancialDataService.exchange_rate(conversion)
            prices = {ticker: {"original_price": indexed_prices.tickers[ticker].info['regularMarketPrice'], "converted_price": round(indexed_prices.tickers[ticker].info['regularMarketPrice'] * conversion_rate['rate'], 2)} for ticker in ticker_list}
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
    def historical_tickers_prices(ticker_list, period="1d", interval="15m"):
        """
        Get historical prices for a list of tickers
        
        tickers - List of stock ticker symbols as strings e.g. ["AAPL", "GOOGL"]
        period - Data period to fetch (e.g. "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        interval - Data interval (e.g. "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo")
        
        return - A Grouped dataframe containing date and closing price
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
            return grouped
        except Exception as e:
            logger.error(f"Error fetching historical prices for tickers {ticker_list}: {e}")
            raise e


    @staticmethod
    def statistics_in_period(ticker_list, period="1mo", interval="1d"):
        """
        Get statistics for a list of tickers within a time window
        
        tickers - List of stock ticker symbols as strings e.g. ["AAPL", "GOOGL"]
        period - Data period to fetch (e.g. "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        interval - Data interval (e.g. "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo")
        
        return - A dictionary with tickers and their respective statistics
        """
        prices_in_period = FinancialDataService.historical_tickers_prices(ticker_list, period, interval) 
        statistics = {}
        for ticker, group in prices_in_period:
            statistics[ticker] = {
                    "previous_price": round(group["Close"].iloc[-1], 2),
                    "minimum": round(group["Low"].min(), 2),
                    "maximum": round(group["High"].max(), 2),
                    "average": round(group["Close"].mean(), 2),
                    "volatility": round(group["Close"].std(), 2)
                }
        
        return statistics
         
        
    @staticmethod
    def get_ticker_info(ticker, period, interval):
        """
        Get basic statistics of price for a ticker in a given period, which can be used for alerting rules
        
        ticker - Stock ticker symbol as string e.g. "LLY"
        period - Data period to fetch (e.g. "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        interval - Data interval (e.g. "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo")
        
        return - A dictionary containing min_price_in_period, max_price_in_period and avg_price_in_period
        """
        try:
            ticker_data = yf.Ticker(ticker)
            recent_history = ticker_data.history(period=period, interval=interval)
            return { "ticker": ticker_data.ticker,
               ## Asset General info
               "displayed_name": ticker_data.info['shortName'],
               "sector": ticker_data.info['sector'] if 'sector' in ticker_data.info else None,
               "industry": ticker_data.info['industry'] if 'industry' in ticker_data.info else None,
                ## Volume statistics
                'volume': ticker_data.info['volume'] if 'volume' in ticker_data.info else None,
                'averageVolume': ticker_data.info['averageVolume'] if 'averageVolume' in ticker_data.info else None,
                'averageVolume10days': ticker_data.info['averageVolume10days'] if 'averageVolume10days' in ticker_data.info else None,
                'averageDailyVolume10Day': ticker_data.info['averageDailyVolume10Day'] if 'averageDailyVolume10Day' in ticker_data.info else None,
                'bid': ticker_data.info['bid'] if 'bid' in ticker_data.info else None,
                'bidSize': ticker_data.info['bidSize'] if 'bidSize' in ticker_data.info else None,
                'ask': ticker_data.info['ask'] if 'ask' in ticker_data.info else None,
                'askSize': ticker_data.info['askSize'] if 'askSize' in ticker_data.info else None,
                ## Price statistics 
               "previous_price": ticker_data.info['previousClose'],
                "current_price": ticker_data.info['regularMarketPrice'],
                "min_price_in_period": round(recent_history["Low"].min(), 2),
                "max_price_in_period": round(recent_history["High"].max(), 2),
                "avg_price_in_period": round(recent_history["Close"].mean(), 2),
                "50DayAverage": ticker_data.info['fiftyDayAverage'] if 'fiftyDayAverage' in ticker_data.info else None,
                "200DayAverage": ticker_data.info['twoHundredDayAverage'] if 'twoHundredDayAverage' in ticker_data.info else None,
                "price_change": round(ticker_data.info['regularMarketPrice'] - ticker_data.info['previousClose'], 2),
                "price_change_percent": round((ticker_data.info['regularMarketPrice'] - ticker_data.info['previousClose']) / ticker_data.info['previousClose'] * 100, 3),
                "52wkLow": ticker_data.info['fiftyTwoWeekLow'] if 'fiftyTwoWeekLow' in ticker_data.info else None,
                "52wkHigh": ticker_data.info['fiftyTwoWeekHigh'] if 'fiftyTwoWeekHigh' in ticker_data.info else None,
                "allTimeHigh": ticker_data.info['allTimeHigh'] if 'allTimeHigh' in ticker_data.info else None,
                "allTimeLow": ticker_data.info['allTimeLow'] if 'allTimeLow' in ticker_data.info else None,
                "targetHighPrice": ticker_data.info['targetHighPrice'] if 'targetHighPrice' in ticker_data.info else None,
                "targetLowPrice": ticker_data.info['targetLowPrice'] if 'targetLowPrice' in ticker_data.info else None,
                "targetMeanPrice": ticker_data.info['targetMeanPrice'] if 'targetMeanPrice  ' in ticker_data.info else None,
                "targetMedianPrice": ticker_data.info['targetMedianPrice'] if 'targetMedianPrice' in ticker_data.info else None
              }
        except Exception as e:
            logger.error(f"Error fetching statistics for ticker {ticker}: {e}")
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
                    "displayed_name": result['shortname'] if 'shortname' in result else result['longname'] if 'longname' in result else result['symbol'],
                    "exchange": result['exchange'],
                    "asset_type": result['quoteType']
                })
            return refined_results
        except Exception as e:
            logger.error(f"Error searching for tickers with query '{query}': {e}")
            raise e