from flask import Blueprint, jsonify, request
from ..services.finantial_data_service import FinancialDataService
from ..models.watchlist import Watchlist
from ..persistance.db_manager import get_db_session
import logging

logger = logging.getLogger(__name__)

watchlist_blueprint = Blueprint('watchlists', __name__, url_prefix='/api/watchlists')

@watchlist_blueprint.route('/', methods=['GET'])
def get_watchlists():
    """
    Endpoint to retrieve all watchlists with their associated assets.
    Example: GET /api/watchlists/
    Return format: json list of watchlists with their assets
    example response:
    {
    "watchlists": [
        {
            "id": 1,
            "name": "Tech Stocks",
            "assets": [
                {"ticker": "AAPL", "displayed_name": "Apple Inc."},
                {"ticker": "AMZN", "displayed_name": "Amazon.com Inc."}
            ]
        },
        ...
    ]
    """
    try:
        watchlists = Watchlist.query.all()
        watchlists_data = []
        for watchlist in watchlists:
            watchlists_data.append({
                "id": watchlist.id,
                "name": watchlist.name,
                "assets": [{"ticker": asset.ticker, "displayed_name": asset.displayed_name} for asset in watchlist.assets]
            })
        return jsonify({"watchlists": watchlists_data}), 200
    except Exception as e:
        logger.error(f"Error retrieving watchlists: {e}")
        return jsonify({"error": "Failed to retrieve watchlists"}), 500


@watchlist_blueprint.route('/new', methods=['POST'])
def create_watchlist():
    """
    Endpoint to create a new watchlist. Expects a 'name' query parameter.
    Example: POST /api/watchlists/new

    Raw Body: {"name": "Tech Stocks"}
    """
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing 'name' in request body"}), 400
    name = data['name']

    
    try:
        with get_db_session() as session:
            new_watchlist = Watchlist(name=name)
            # Check if watchlist with the same name already exists
            if new_watchlist.name_available():
                session.add(new_watchlist)
                session.commit()
                return jsonify({"message": f"Watchlist '{name}' created successfully", "watchlist": {"id": new_watchlist.id, "name": new_watchlist.name}}), 201
            else:
                return jsonify({"error": f"Watchlist with name '{name}' already exists"}), 409
    except Exception as e:
        logger.error(f"Error creating watchlist: {e}")
        return jsonify({"error": "Failed to create watchlist"}), 500
    finally:
        pass


@watchlist_blueprint.route('/delete/<int:watchlist_id>', methods=['DELETE'])
def delete_watchlist(watchlist_id):
    """
    Endpoint to delete a watchlist by its ID.
    Example: DELETE /api/watchlists/delete/1
    """
    
    if not watchlist_id:
        return jsonify({"error": "Missing 'watchlist id' query parameter"}), 400

    try:
        with get_db_session() as session:
            watchlist = session.query(Watchlist).filter_by(id=watchlist_id).first()
            if not watchlist:
                return jsonify({"error": f"Watchlist with ID {watchlist_id} not found"}), 404
            # wathclist_name = watchlist.name
            session.delete(watchlist)
            return jsonify({"message": f"Watchlist '{watchlist.name}' with ID {watchlist_id} deleted successfully", "watchlist": {"id": watchlist_id, "name": watchlist.name}}), 200
    except Exception as e:
        logger.error(f"Error deleting watchlist: {e}")
        return jsonify({"error": "Failed to delete watchlist"}), 500
    
    
@watchlist_blueprint.route('/update/<int:watchlist_id>', methods=['PATCH'])
def update_watchlist(watchlist_id):
    """
    Endpoint to update a watchlist's name by its ID. Expects a 'name' query parameter.
    Example: PATCH /api/watchlists/update/1

    Raw Body: {"name": "New Watchlist Name"}
    """
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing 'name' in request body"}), 400
    new_name = data['name']

    try:
        with get_db_session() as session:
            watchlist = session.query(Watchlist).filter_by(id=watchlist_id).first()
            if not watchlist:
                return jsonify({"error": f"Watchlist with ID {watchlist_id} not found"}), 404
            
            # Check if another watchlist with the new name already exists
            if watchlist.name != new_name and not Watchlist(name=new_name).name_available():
                return jsonify({"error": f"Another watchlist with name '{new_name}' already exists"}), 409
            
            watchlist.name = new_name
            
            return jsonify({"message": f"Watchlist with ID {watchlist_id} updated successfully", "watchlist": {"id": watchlist_id, "name": new_name}}), 200
    except Exception as e:
        logger.error(f"Error updating watchlist: {e}")
        return jsonify({"error": "Failed to update watchlist"}), 500
    
