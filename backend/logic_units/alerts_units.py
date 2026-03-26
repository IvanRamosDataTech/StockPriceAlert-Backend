"""Business logic helper functions for alert operations."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from ..models.alert import Alert
from ..models.asset import Asset
from ..persistance.db_manager import get_db_session

logger = logging.getLogger(__name__)


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

    return {"message": message, "alerts": [str(alert) for alert in alerts]}


def create_alert(ticker: str, alert_type: str, target_price: Optional[float]) -> dict:
    """Create a new alert for a given ticker after validating the asset exists."""

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