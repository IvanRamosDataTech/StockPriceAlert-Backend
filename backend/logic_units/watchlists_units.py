"""Business logic helpers for watchlist operations."""

from __future__ import annotations

from typing import List, Optional

from ..models.watchlist import Watchlist
from ..persistance.db_manager import get_db_session


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