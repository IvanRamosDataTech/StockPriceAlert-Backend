from flask import Blueprint, request, jsonify
from ..models.alert import Alert
from ..models.asset import Asset
from ..persistance.db_manager import get_db_session
from ..logic_units.alerts_units import fetch_alerts, create_alert

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
        payload = fetch_alerts(stock)
        return jsonify(payload), 200
    except LookupError as le:
        logger.error(f"Error fetching alerts: {le}")
        return jsonify({"error": str(le)}), 404
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

    try:
        payload = create_alert(ticker, alert_type, target_price)
        return jsonify(payload), 201
    except LookupError as le:
        logger.error(f"Error creating alert: {le}")
        return jsonify({"error": str(le)}), 404
    except ValueError as ve:
        logger.error(f"Error creating alert: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return jsonify({"error": "Failed to create alert"}), 500
    

@alerts_blueprint.route('/<int:alert_id>', methods=['DELETE'])
def unset_alert(alert_id):
    """
    Endpoint to delete an alert by its ID
    """
    logger.info(f"/api/alerts/{alert_id} DELETE route called")
    
    try:
        with get_db_session() as session:
            alert = Alert.query.get(alert_id)
            if not alert:
                return jsonify({"error": f"No alert found with ID {alert_id}"}), 404
    
            session.delete(alert)
            return jsonify({"message": f"Alert {alert.alert_type} {alert.price_threshold if alert.price_threshold is not None else ''} for asset {alert.asset.ticker} successfully deleted"})
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        return jsonify({"error": "Failed to delete alert"}), 500
    

@alerts_blueprint.route('/<int:alert_id>', methods=['PATCH'])
def update_alert(alert_id):
    """
    Endpoint to update an existing alert by its ID
    Expects JSON body with keys:
        {"alert_type": [string] - Accepted values: MonthMinimum | MonthMaximum | PriceBelow | PriceAbove,
         "target_price": [float] - Threshold price (required) in case alert is of type PriceBelow or PriceAbove
    }
    """
    logger.info(f"/api/alerts/{alert_id} PATCH route called")
    
    data = request.get_json()
    
    alert_type = data.get('alert_type')
    target_price = data.get('target_price')
    
    # Data type validations
    if not isinstance(alert_type, str):
        return jsonify({"error": "alert_type must be a string"}), 400
    
    if not isinstance(target_price, (int, float)) and target_price is not None:
        return jsonify({"error": "target_price must be a number"}), 400
    
    try:
        with get_db_session() as session:
            alert = Alert.query.get(alert_id)
            if not alert:
                return jsonify({"error": f"No alert found with ID {alert_id}"}), 404
            
            alert.alert_type = alert_type
            alert.price_threshold = target_price
            session.add(alert)
            return jsonify({"message": f"Alert {alert.alert_type} {alert.price_threshold if alert.price_threshold is not None else ''} for asset {alert.asset.ticker} updated successfully"})
    except ValueError as ve:
        logger.error(f"Error updating alert: {ve}")
        return jsonify({"error": str(ve)}), 400
    
    except Exception as e:
        logger.error(f"Error updating alert: {e}")
        return jsonify({"error": "Failed to update alert"}), 500