from backend.models.asset import Asset
from backend.models.alert import Alert, ALERT_TYPE_PRICE_ABOVE
from backend.logic_units.alerts_units import fetch_alerts
from backend.utils.time_utils import now_cts_time


def _asset(db):
    asset = Asset(ticker="AAPL", displayed_name="AAPL", price=100.0, min_month_price=90.0)
    db.session.add(asset)
    db.session.commit()
    return asset


def test_fetch_alerts_includes_triggered_price(app, db):
    _asset(db)
    alert = Alert(ticker="AAPL", alert_type=ALERT_TYPE_PRICE_ABOVE, price_threshold=95.0)
    alert.update_trigger(101.5)
    db.session.add(alert)
    db.session.commit()

    result = fetch_alerts()["alerts"][0]
    assert result["triggered_price"] == 101.5
    assert result["triggered_at"] is not None


def test_fetch_alerts_triggered_price_none_when_never_triggered(app, db):
    _asset(db)
    db.session.add(Alert(ticker="AAPL", alert_type=ALERT_TYPE_PRICE_ABOVE, price_threshold=95.0))
    db.session.commit()

    result = fetch_alerts()["alerts"][0]
    assert result["triggered_price"] is None
    assert result["triggered_at"] is None
