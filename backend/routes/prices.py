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