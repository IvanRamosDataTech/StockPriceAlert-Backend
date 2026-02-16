from flask import Blueprint, jsonify, request
import yfinance as yf
import logging

logger = logging.getLogger(__name__)

price_blueprint = Blueprint('prices', __name__, url_prefix='/api/prices')

@price_blueprint.route('/latest', methods=['GET'])
def get_latest_prices():
    """
    Endpoint to get the latest prices for a list of tickers
    
    tickers should be provided as a comma-separated string in the query parameters, e.g.:
    /api/prices/latest?tickers=AAPL,GOOGL,MSFT
    """
    logger.info("/api/prices/latest route called")
    
    tickers = request.args.get('tickers', '')
    ticker_list = [ticker.strip() for ticker in tickers.split(',') if ticker.strip()]
    
    if not ticker_list:
        return jsonify({"error": "No tickers provided"}), 400
    
    try:
        indexed_prices = yf.Tickers(ticker_list)
        prices = {ticker: indexed_prices.tickers[ticker].info['regularMarketPrice'] for ticker in ticker_list}
        return jsonify(prices)
    except Exception as e:
        logger.error(f"Error fetching prices for tickers {ticker_list}: {e}")
        return jsonify({"error": "Failed to fetch prices"}), 500
    

@price_blueprint.route('/exchange-rate', methods=['GET'])
def get_exchange_rate():
    """
    Endpoint to get the latest exchange rate for a currency pair
    
    pair should be provided as a comma-separated string in the query parameters, e.g.:
    /api/prices/exchange-rate?pair=USD/EUR
    """
    logger.info("/api/prices/exchange-rate route called")
    
    pair = request.args.get('pair', "USD/MXN")
    if '/' not in pair:
        return jsonify({"error": "Invalid currency pair format. Use 'BASE/QUOTE' format."}), 400
    
    #base_currency, quote_currency = [currency.strip() for currency in pair.split('/')]
    
    try:
        #ticker_symbol = f"{base_currency}{quote_currency}=X"
        exchange_rate = yf.Lookup(pair).currency
        if not exchange_rate.empty:
            shortName = exchange_rate["shortName"].values[0]
            rate = exchange_rate["regularMarketPrice"].values[0]
            return jsonify({"exchange_rate": shortName, "rate": rate})
        else:
            return jsonify({"error": "Exchange rate not found for the given pair"}), 404
    except Exception as e:
        logger.error(f"Fetched object: {exchange_rate}")
        logger.error(f"Error fetching exchange rate for pair {pair}: {e}")
        return jsonify({"error": "Failed to fetch exchange rate"}), 500
    

@price_blueprint.route('/historical', methods=['GET'])
def get_historical_prices():
    """
    Endpoint to get historical prices for a ticker
    
    tickers should be provided as a comma-separated string in the query parameters, e.g.:
    /api/prices/historical?
    Parameters:
    [tickers] A list of comma separated valid tickers e.g. tickers=AAPL,GOOGL,MSFT
    [period] The period to fetch historical data. Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max Default is 1mo
    [interval] The interval for historical data.  Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo Intraday data cannot extend last 60 days
    """
    logger.info("/api/prices/historical route called")
    
    tickers = request.args.get('tickers', '')
    selected_period = request.args.get('period', '1mo')
    selected_interval = request.args.get('interval', '1d')
    
    ticker_list = [ticker.strip() for ticker in tickers.split(',') if ticker.strip()]
    
    if not ticker_list:
        return jsonify({"error": "No tickers provided"}), 400
    
    try:
        historical_prices = yf.download(ticker_list, period=selected_period, interval=selected_interval)
        clean_prices = historical_prices.drop(columns=["Volume"], level=0)
        clean_prices = clean_prices.stack(level=1)
        clean_prices = clean_prices.reset_index()
        clean_prices = clean_prices.rename(columns={"level_1": "Ticker"})
        clean_prices["Date"] = clean_prices["Date"].dt.strftime('%d-%m-%Y')
        # clean_prices
        grouped = clean_prices.groupby("Ticker")
        return jsonify({
            ticker: group.to_dict(orient="records") for ticker, group in grouped
        })
    except Exception as e:
        logger.error(f"Error fetching historical prices for tickers {ticker_list}: {e}")
        return jsonify({"error": "Failed to fetch historical prices"}), 500
    

@price_blueprint.route('/search', methods=['GET'])
def search_tickers():
    """
    Endpoint to search for tickers based on a query string
    
    query should be provided as a string in the query parameters, e.g.:
    /api/prices/search?query=Bitcoin
    """
    logger.info("/api/prices/search route called")
    
    query = request.args.get('query', '')
    maximum_results = request.args.get('max_results', 7, type=int)
    
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
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
        return jsonify(refined_results)
    except Exception as e:
        logger.error(f"Error searching for tickers with query '{query}': {e}")
        return jsonify({"error": "Failed to search for tickers"}), 500