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