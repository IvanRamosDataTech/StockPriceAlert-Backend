"""Business logic helper functions for alert operations."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from ..models.alert import Alert
from ..models.asset import Asset
from ..persistance.db_manager import get_db_session

logger = logging.getLogger(__name__)

_ALLOWED_ALERT_TYPES = {
    "MonthMinimum",
    "MonthMaximum",
    "PriceBelow",
    "PriceAbove",
}
_PRICE_THRESHOLD_TYPES = {"PriceBelow", "PriceAbove"}


def fetch_alerts(asset_ticker: Optional[str] = None) -> Dict[str, List[str] | str]:
    """Return serialized alerts, optionally filtered by asset ticker."""

    if asset_ticker:
        asset = Asset.query.filter_by(ticker=asset_ticker).first()
        if not asset:
            raise LookupError(
                f"No asset found with ticker {asset_ticker} in any of your watchlists"
            )
        alerts = asset.alerts
        message = f"All alerts registered for {asset_ticker}"
    else:
        alerts = Alert.query.all()
        message = "All alerts registered in system"

    return {"message": message, "alerts": [
						{
							"id": alert.id,
                            "ticker": alert.ticker,
							"type": alert.alert_type,
							"threshold": alert.price_threshold,
                            "triggered_at": alert.last_triggered_at.isoformat() if alert.last_triggered_at else None,
						}
						for alert in alerts
					]}


def create_alert(ticker: str, alert_type: str, target_price: Optional[float]) -> dict:
    """Create a new alert for a given ticker after validating the asset exists."""
    if alert_type not in _ALLOWED_ALERT_TYPES:
        raise ValueError(
            f"Invalid alert_type '{alert_type}'. Must be one of: MonthMinimum, MonthMaximum, PriceBelow, PriceAbove"
        )
    
    if alert_type in _PRICE_THRESHOLD_TYPES and target_price is None:
        raise ValueError("target_price is required for PriceBelow and PriceAbove alert types")

    with get_db_session() as session:
        asset = Asset.query.filter_by(ticker=ticker).first()
        if not asset:
            raise LookupError(
                f"No asset found with ticker {ticker} in any of your watchlists"
            )

        new_alert = Alert(
            ticker=ticker, alert_type=alert_type, price_threshold=target_price
        )
        session.add(new_alert)
        return {"message": "Alert created successfully", "stock": str(asset)}


def delete_alert(alert_id: int) -> dict:
    """Delete an alert by ID and return a confirmation payload."""

    with get_db_session() as session:
        alert = Alert.query.get(alert_id)
        if not alert:
            raise LookupError(f"No alert found with ID {alert_id}")

        payload = {
            "message": (
                f"Alert {alert.alert_type} "
                f"{alert.price_threshold if alert.price_threshold is not None else ''} "
                f"for asset {alert.asset.ticker} successfully deleted"
            ).strip(),
            "alert_id": alert.id,
        }
        session.delete(alert)
        return payload


def update_alert(alert_id: int, alert_type: str, target_price: Optional[float]) -> dict:
    """Update the alert type/threshold for a given alert ID."""

    if alert_type not in _ALLOWED_ALERT_TYPES:
        raise ValueError(
            f"Invalid alert_type '{alert_type}'. Must be one of: MonthMinimum, MonthMaximum, PriceBelow, PriceAbove"
        )

    if alert_type in _PRICE_THRESHOLD_TYPES and target_price is None:
        raise ValueError("target_price is required for PriceBelow and PriceAbove alert types")

    with get_db_session() as session:
        alert = Alert.query.get(alert_id)
        if not alert:
            raise LookupError(f"No alert found with ID {alert_id}")

        alert.alert_type = alert_type
        alert.price_threshold = target_price
        session.add(alert)

        return {
            "message": (
                f"Alert {alert.alert_type} "
                f"{alert.price_threshold if alert.price_threshold is not None else ''} "
                f"for asset {alert.asset.ticker} updated successfully"
            ).strip(),
            "alert_id": alert.id,
        }