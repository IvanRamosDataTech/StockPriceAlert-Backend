import logging

from flask import Blueprint, jsonify, request

from ..logic_units.watchlists_units import (
    add_asset_to_watchlist as add_asset_to_watchlist_logic,
    delete_watchlist as delete_watchlist_logic,
    fetch_watchlists,
    new_watchlist,
    refresh_watchlist_prices as refresh_watchlist_prices_logic,
    remove_asset_from_watchlist as remove_asset_from_watchlist_logic,
    update_watchlist as update_watchlist_logic,
)

logger = logging.getLogger(__name__)

watchlist_blueprint = Blueprint('watchlists', __name__, url_prefix='/api/watchlists')

@watchlist_blueprint.route('/', methods=['GET'])
def get_watchlists():
    """
    Endpoint to retrieve all watchlists with their associated assets.
    Example: GET /api/watchlists/
    Optionally accepts a name query parameter to filter watchlists by name (case-insensitive, partial match).
    Example: GET /api/watchlists/?name=tech
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
        name_filter = request.args.get('name')
        watchlists_data = fetch_watchlists(name_filter)
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
        (id, name) = new_watchlist(name)        
        return jsonify({"message": f"Watchlist created successfully", "watchlist": {"id": id, "name": name}}), 201                
    except ValueError as ve:
        logger.error(f"Error creating watchlist: {ve}")
        return jsonify({"error": f"Watchlist with name '{name}' already exists"}), 409
    except Exception as e:
        logger.error(f"Error creating watchlist: {e}")
        return jsonify({"error": f"Failed to create watchlist: {e}"}), 500
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
        deleted_watchlist = delete_watchlist_logic(watchlist_id)
        return jsonify({"message": f"Watchlist '{deleted_watchlist['name']}' with ID {watchlist_id} deleted successfully", "watchlist": deleted_watchlist}), 200
    except LookupError as le:
        logger.error(f"Error deleting watchlist: {le}")
        return jsonify({"error": str(le)}), 404
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
        updated_watchlist = update_watchlist_logic(watchlist_id, new_name)
        return jsonify({"message": f"Watchlist with ID {watchlist_id} updated successfully", "watchlist": updated_watchlist}), 200
    except LookupError as le:
        logger.error(f"Error updating watchlist: {le}")
        return jsonify({"error": str(le)}), 404
    except ValueError as ve:
        logger.error(f"Error updating watchlist: {ve}")
        return jsonify({"error": str(ve)}), 409
    except Exception as e:
        logger.error(f"Error updating watchlist: {e}")
        return jsonify({"error": "Failed to update watchlist"}), 500
    

@watchlist_blueprint.route('/<int:watchlist_id>/add-asset', methods=['POST'])
def add_asset_to_watchlist(watchlist_id):
    """
    Endpoint to add an asset to a watchlist by its ID. Expects a 'ticker' query parameter.
    Example: POST /api/watchlists/1/add-asset

    Required Raw Body:   {
                    "ticker": "COIN"
                }
    """
    data = request.get_json()
    if not data or 'ticker' not in data:
        return jsonify({"error": "Missing 'ticker' in request body"}), 400
    ticker = data['ticker']

    try:
        watchlist = add_asset_to_watchlist_logic(watchlist_id, ticker)
        return jsonify({"message": f"Asset with ticker '{ticker}' added to watchlist with ID {watchlist_id} successfully", "watchlist": watchlist}), 200
    except LookupError as le:
        logger.error(f"Error adding asset {ticker} to watchlist: {le}")
        return jsonify({"error": str(le)}), 404
    except ValueError as ve:
        logger.error(f"Error adding asset {ticker} to watchlist: {ve}")
        return jsonify({"error": str(ve)}), 409
    except Exception as e:
        logger.error(f"Error adding asset {ticker} to watchlist: {e}")
        return jsonify({"error": f"Failed to add asset {ticker} to watchlist"}), 500
    

@watchlist_blueprint.route('/<int:watchlist_id>/remove-asset', methods=['DELETE'])
def remove_asset_from_watchlist(watchlist_id):
    """
    Endpoint to remove an asset from a watchlist by its ID. Expects a 'ticker' query parameter.
    Example: DELETE /api/watchlists/1/remove-asset

    Required Raw Body:   {
                    "ticker": "COIN"
                }
    """
    data = request.get_json()
    if not data or 'ticker' not in data:
        return jsonify({"error": "Missing 'ticker' in request body"}), 400
    ticker = data['ticker']

    try:
        watchlist = remove_asset_from_watchlist_logic(watchlist_id, ticker)
        return jsonify({"message": f"Asset with ticker '{ticker}' removed from watchlist with ID {watchlist_id} successfully", "watchlist": watchlist}), 200
    except LookupError as le:
        logger.error(f"Error removing asset {ticker} from watchlist: {le}")
        return jsonify({"error": str(le)}), 404
    except Exception as e:
        logger.error(f"Error removing asset {ticker} from watchlist: {e}")
        return jsonify({"error": f"Failed to remove asset {ticker} from watchlist"}), 500
    

@watchlist_blueprint.route('/<int:watchlist_id>/refresh-prices', methods=['GET']) 
def refresh_watchlist_prices(watchlist_id):
    """
        Endpoint to refresh the prices of all assets in a watchlist by its ID. 
        Mainly used for manual refreshing of the watchlist prices, but also called by the background scheduler to keep the prices updated.
    """
    try:
        watchlist = refresh_watchlist_prices_logic(watchlist_id)
        #return jsonify({"message": f"watchlist {watchlist['name']} refreshed successfully", "watchlist": watchlist}), 200
        return jsonify(watchlist), 200
    except LookupError as le:
        logger.error(f"Error refreshing prices for watchlist with ID {watchlist_id}: {le}")
        return jsonify({"error": str(le)}), 404
    except Exception as e:
        logger.error(f"Error refreshing prices for watchlist with ID {watchlist_id}: {e}")
        return jsonify({"error": f"Failed to refresh prices for watchlist with ID {watchlist_id}: {e}"}), 500
