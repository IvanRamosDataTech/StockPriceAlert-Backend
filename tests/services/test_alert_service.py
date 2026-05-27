from unittest.mock import patch
from backend.models.asset import Asset
from backend.models.alert import Alert, ALERT_TYPE_PRICE_BELOW, ALERT_TYPE_PRICE_ABOVE, ALERT_TYPE_MONTH_LOW
from backend.services.alert_service import AlertService


def _make_asset(db, ticker="AAPL", price=100.0, min_month_price=90.0):
    asset = Asset(ticker=ticker, displayed_name=ticker, price=price, min_month_price=min_month_price)
    db.session.add(asset)
    db.session.commit()
    return asset


def test_price_below_triggers_when_price_at_threshold(app, db):
    asset = _make_asset(db, price=23.0)
    alert = Alert(ticker=asset.ticker, alert_type=ALERT_TYPE_PRICE_BELOW, price_threshold=23.0)
    db.session.add(alert)
    db.session.commit()

    with patch("backend.services.alert_service.TelegramService.send_message") as mock_send:
        AlertService.check_alert(app, alert)
        mock_send.assert_called_once()


def test_price_below_does_not_trigger_when_price_above_threshold(app, db):
    asset = _make_asset(db, price=55.0)
    alert = Alert(ticker=asset.ticker, alert_type=ALERT_TYPE_PRICE_BELOW, price_threshold=50.0)
    db.session.add(alert)
    db.session.commit()

    with patch("backend.services.alert_service.TelegramService.send_message") as mock_send:
        AlertService.check_alert(app, alert)
        mock_send.assert_not_called()


def test_price_above_triggers_when_price_at_threshold(app, db):
    asset = _make_asset(db, price=150.0)
    alert = Alert(ticker=asset.ticker, alert_type=ALERT_TYPE_PRICE_ABOVE, price_threshold=150.0)
    db.session.add(alert)
    db.session.commit()

    with patch("backend.services.alert_service.TelegramService.send_message") as mock_send:
        AlertService.check_alert(app, alert)
        mock_send.assert_called_once()


def test_month_minimum_triggers_when_price_at_monthly_low(app, db):
    asset = _make_asset(db, price=90.0, min_month_price=90.0)
    alert = Alert(ticker=asset.ticker, alert_type=ALERT_TYPE_MONTH_LOW)
    db.session.add(alert)
    db.session.commit()

    with patch("backend.services.alert_service.TelegramService.send_message") as mock_send:
        AlertService.check_alert(app, alert)
        mock_send.assert_called_once()
