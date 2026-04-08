"""Business logic helpers for watchlist operations."""

from __future__ import annotations

import logging
from typing import List, Optional

from ..models.asset import Asset
from ..models.watchlist import Watchlist
from ..persistance.db_manager import get_db_session
from ..services.finantial_data_service import FinancialDataService

logger = logging.getLogger(__name__)


def fetch_watchlists(name_filter: Optional[str] = None) -> List[dict]:
	"""Return serialized watchlists with optional case-insensitive name filtering."""
	if name_filter:
		watchlists = (
			Watchlist.query.filter(Watchlist.name.ilike(f"%{name_filter}%")).all()
		)
	else:
		watchlists = Watchlist.query.all()

	watchlists_data: List[dict] = []
	for watchlist in watchlists:
		assets_in_watchlist = []
		for asset in watchlist.assets:
			assets_in_watchlist.append(
				{
					"ticker": asset.ticker,
					"displayed_name": asset.displayed_name,
					"previous_price": asset.previous_price,
					"price": asset.price,
					"change %": asset.price_change_percent,
					"alerts": [
						{
							"id": alert.id,
							"type": alert.alert_type,
							"threshold": alert.price_threshold,
						}
						for alert in asset.alerts
					],
				}
			)

		watchlists_data.append(
			{
				"id": watchlist.id,
				"name": watchlist.name,
				"assets": assets_in_watchlist,
			}
		)

	return watchlists_data


def new_watchlist(name: str) -> tuple[int, str]:
    """Create and return a new watchlist.
    Args:
        name (str): The name of the new watchlist.
    Returns:
        tuple[int, str]: The ID and name of the newly created watchlist.
    Raises:
        ValueError: If a watchlist with the same name already exists.
	"""
    with get_db_session() as session:
        new_watchlist = Watchlist(name=name)
        # Check if watchlist with the same name already exists
        if new_watchlist.name_available():
            session.add(new_watchlist)
            session.commit()
            return new_watchlist.id, new_watchlist.name
        else:
            raise ValueError(f"Watchlist with name '{name}' already exists")


def delete_watchlist(watchlist_id: int) -> dict:
	"""Delete a watchlist and orphaned assets, returning a summary."""

	with get_db_session() as session:
		watchlist = session.query(Watchlist).filter_by(id=watchlist_id).first()
		if not watchlist:
			raise LookupError(f"Watchlist with ID {watchlist_id} not found")

		watchlist_summary = {"id": watchlist.id, "name": watchlist.name}
		for asset in list(watchlist.assets):
			if len(asset.watchlists) == 1:
				session.delete(asset)
				logger.info(
					"Asset with ticker '%s' removed from database as it is no longer in any watchlist",
					asset.ticker,
				)

		session.delete(watchlist)
		return watchlist_summary


def update_watchlist(watchlist_id: int, new_name: str) -> dict:
	"""Rename a watchlist while enforcing name uniqueness."""

	with get_db_session() as session:
		watchlist = session.query(Watchlist).filter_by(id=watchlist_id).first()
		if not watchlist:
			raise LookupError(f"Watchlist with ID {watchlist_id} not found")

		if watchlist.name != new_name and not Watchlist(name=new_name).name_available():
			raise ValueError(f"Another watchlist with name '{new_name}' already exists")

		watchlist.name = new_name
		return {"id": watchlist.id, "name": watchlist.name}


def add_asset_to_watchlist(watchlist_id: int, ticker: str) -> dict:
	"""Add an asset to a watchlist, creating it if needed."""

	with get_db_session() as session:
		watchlist = session.query(Watchlist).filter_by(id=watchlist_id).first()
		if not watchlist:
			raise LookupError(f"Watchlist with ID {watchlist_id} not found")

		asset = session.query(Asset).filter_by(ticker=ticker).first()
		if asset and asset in watchlist.assets:
			raise ValueError(f"Asset with ticker '{ticker}' is already in the watchlist")

		if not asset:
			asset_data = FinancialDataService.get_ticker_info(
				ticker, period="1mo", interval="1d"
			)
			asset = Asset(
				ticker=asset_data["ticker"],
				displayed_name=asset_data["displayed_name"],
			)
			asset.previous_price = asset_data["previous_price"]
			asset.price = asset_data["current_price"]
			asset.price_change = asset_data["price_change"]
			asset.price_change_percent = asset_data["price_change_percent"]
			asset.min_month_price = asset_data["min_price_in_period"]
			asset.max_month_price = asset_data["max_price_in_period"]
			asset.avg_month_price = asset_data["avg_price_in_period"]
			session.add(asset)

		watchlist.assets.append(asset)
		return _serialize_watchlist_summary(watchlist)


def remove_asset_from_watchlist(watchlist_id: int, ticker: str) -> dict:
	"""Remove an asset from a watchlist and delete it if orphaned."""

	with get_db_session() as session:
		watchlist = session.query(Watchlist).filter_by(id=watchlist_id).first()
		if not watchlist:
			raise LookupError(f"Watchlist with ID {watchlist_id} not found")

		asset = session.query(Asset).filter_by(ticker=ticker).first()
		if not asset or asset not in watchlist.assets:
			raise LookupError(f'Asset with ticker "{ticker}" is not in "{watchlist.name}".')

		watchlist.assets.remove(asset)
		if len(asset.watchlists) == 0:
			session.delete(asset)

		return _serialize_watchlist_summary(watchlist)


def refresh_watchlist_prices(watchlist_id: int) -> dict:
	"""Refresh the prices of all assets in a watchlist."""

	with get_db_session() as session:
		watchlist = session.query(Watchlist).filter_by(id=watchlist_id).first()
		if not watchlist:
			raise LookupError(f"Watchlist with ID {watchlist_id} not found")

		ticker_list = [asset.ticker for asset in watchlist.assets]
		prices = FinancialDataService.latest_prices(ticker_list)
		for asset in watchlist.assets:
			price_pair = prices.get(asset.ticker, asset.price)
			asset.update_price_statistics(price_pair["original_price"])

		return _serialize_watchlist_with_prices(watchlist)


def _serialize_watchlist_summary(watchlist: Watchlist) -> dict:
	return {
		"id": watchlist.id,
		"name": watchlist.name,
		"assets": [_serialize_asset_summary(asset) for asset in watchlist.assets],
	}


def _serialize_watchlist_with_prices(watchlist: Watchlist) -> dict:
	return {
		"id": watchlist.id,
		"name": watchlist.name,
		"assets": [_serialize_asset_with_prices(asset) for asset in watchlist.assets],
	}


def _serialize_asset_summary(asset: Asset) -> dict:
	return {"ticker": asset.ticker, "displayed_name": asset.displayed_name}


def _serialize_asset_with_prices(asset: Asset) -> dict:
	data = _serialize_asset_summary(asset)
	data.update(
		{
			"previous_price": asset.previous_price,
			"price": asset.price,
			"change %": asset.price_change_percent,
		}
	)
	return data