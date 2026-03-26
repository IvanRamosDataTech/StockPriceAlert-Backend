from flask import Blueprint, request, jsonify
from ..logic_units.alerts_units import (
    create_alert,
    delete_alert,
    fetch_alerts,
    update_alert as update_alert_logic,
)

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
        payload = delete_alert(alert_id)
        return jsonify(payload), 200
    except LookupError as le:
        logger.error(f"Error deleting alert: {le}")
        return jsonify({"error": str(le)}), 404
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
        payload = update_alert_logic(alert_id, alert_type, target_price)
        return jsonify(payload), 200
    except LookupError as le:
        logger.error(f"Error updating alert: {le}")
        return jsonify({"error": str(le)}), 404
    except ValueError as ve:
        logger.error(f"Error updating alert: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error updating alert: {e}")
        return jsonify({"error": "Failed to update alert"}), 500