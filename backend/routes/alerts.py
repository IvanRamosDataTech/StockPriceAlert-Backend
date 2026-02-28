from flask import Blueprint, request, jsonify
from ..models.alert import Alert
from ..models.asset import Asset
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