from flask import Blueprint, request, jsonify
from ..models.alert import Alert
from ..models.asset import Asset
from ..persistance.db_manager import get_db_session

import logging

logger = logging.getLogger(__name__)

alerts_blueprint = Blueprint('alerts', __name__, url_prefix='/api/alerts')

@alerts_blueprint.route('/', methods=['GET'])
def get_alerts():
    """
    Endpoint to get all alerts for a user
    Optionally filtered by stock of interest
    query parameters: stock (optional) - ticker symbol to filter alerts by stock
    """
    logger.info("/api/alerts route called")
    
    stock = request.args.get('stock', None)
    try:
        if stock:        
            asset = Asset.query.filter_by(ticker=stock).first()
            if not asset:
                return jsonify({"error": f"No asset found with ticker {stock} in any of your watchlists"}), 404
            else:
                alerts = asset.alerts
                return jsonify({"message": f"All alerts registered for {stock}", "alerts": [str(alert) for alert in alerts]})
        else:
            alerts = Alert.query.all()
            return jsonify({"message": "All alerts registered in system", "alerts": [str(alert) for alert in alerts]})
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        return jsonify({"error": "Failed to fetch alerts"}), 500
    
@alerts_blueprint.route('/', methods=['POST'])
def set_alert():
    """
    Endpoint to create a new alert for a stock in a watchlist
    Expects JSON body with keys: 
        {"ticker" : [string] - The ticker symbol of the stock to set alert for,
         "alert_type": [string] - Accepted values: MonthMinimum | MonthMaximum | PriceBelow | PriceAbove,
         "target_price": [float] - Threshold price (required) in case alert is of type PriceBelow or PriceAbove
    """
    logger.info("/api/alerts POST route called")
    
    data = request.get_json()
    
    ticker = data.get('ticker')
    alert_type = data.get('alert_type')
    target_price = data.get('target_price')
    
    # Data type validations
    if not isinstance(ticker, str):
        return jsonify({"error": "ticker must be a string"}), 400
    
    if not isinstance(alert_type, str):
        return jsonify({"error": "alert_type must be a string"}), 400
    
    if not isinstance(target_price, (int, float)) and target_price is not None:
        return jsonify({"error": "target_price must be a number"}), 400


    if alert_type not in ["MonthMinimum", "MonthMaximum", "PriceBelow", "PriceAbove"]:
        return jsonify({"error": "Invalid alert_type. Accepted values are: MonthMinimum, MonthMaximum, PriceBelow, PriceAbove"}), 400

    if alert_type in ["PriceBelow", "PriceAbove"] and target_price is None:
        return jsonify({"error": "target_price is required for PriceBelow and PriceAbove alert types"}), 400
    

    try:
        with get_db_session() as session:
            asset = Asset.query.filter_by(ticker=ticker).first()
            if not asset:
                return jsonify({"error": f"No asset found with ticker {ticker} in any of your watchlists"}), 404
            
            new_alert = Alert(ticker=ticker, alert_type=alert_type, price_threshold=target_price)
            session.add(new_alert)
            return jsonify({"message": "Alert created successfully", "stock": str(asset)}), 201
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return jsonify({"error": "Failed to create alert"}), 500