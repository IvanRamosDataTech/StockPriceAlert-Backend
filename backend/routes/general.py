from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

general_blueprint = Blueprint('general', __name__, url_prefix='/api')

@general_blueprint.route('/', methods=['GET'])
def index():
    logger.info("/ route called")
    return '<H1>Welcome to the Stock Price Alert API for long investors Service.</H1>'

@general_blueprint.route('/help', methods=['GET'])
def help():
    logger.info("/help route called")
    available_endpoints = {
        "/": "Home page",
        "/help": "This help page",
        "/api/prices/latest?tickers=...": "Get latest prices for specified tickers (comma-separated)"
    }

    
    return '<H1>About this API Service</H1>' + ''.join([f'<p><b>{endpoint}</b>: {description}</p>' for endpoint, description in available_endpoints.items()])