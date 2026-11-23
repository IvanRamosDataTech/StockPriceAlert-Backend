import pytest
from backend.models.asset import Asset
from backend.models.watchlist import Watchlist
from backend.logic_units.alerts_units import normalize_alert_type, create_alert, update_alert, fetch_alerts
from backend.logic_units.watchlists_units import new_watchlist, update_watchlist


@pytest.mark.parametrize("raw, expected", [
    ("pricebelow", "PriceBelow"),
    ("PRICEABOVE", "PriceAbove"),
    ("pRiCeBeLoW", "PriceBelow"),
    ("monthminimum", "MonthMinimum"),
    ("  MonthMinimum ", "MonthMinimum"),
])
def test_normalize_alert_type_ignores_case(raw, expected):
    assert normalize_alert_type(raw) == expected


def test_normalize_alert_type_rejects_unknown():
    with pytest.raises(ValueError):
        normalize_alert_type("sideways")


def test_create_alert_stores_canonical_alert_type(app, db):
    db.session.add(Asset(ticker="AAPL", displayed_name="Apple", price=100.0))
    db.session.commit()

    create_alert("AAPL", "pricebelow", 90.0)

    alerts = fetch_alerts("AAPL")["alerts"]
    assert [a["type"] for a in alerts] == ["PriceBelow"]


def test_update_alert_stores_canonical_alert_type(app, db):
    db.session.add(Asset(ticker="AAPL", displayed_name="Apple", price=100.0))
    db.session.commit()
    create_alert("AAPL", "PriceBelow", 90.0)
    alert_id = fetch_alerts("AAPL")["alerts"][0]["id"]

    update_alert(alert_id, "PRICEABOVE", 120.0)

    assert fetch_alerts("AAPL")["alerts"][0]["type"] == "PriceAbove"


def test_watchlist_names_are_unique_ignoring_case(app, db):
    new_watchlist("Tech")
    with pytest.raises(ValueError):
        new_watchlist("tECH")


def test_watchlist_can_be_renamed_with_case_change_only(app, db):
    watchlist_id, _ = new_watchlist("tech")
    update_watchlist(watchlist_id, "Tech")
    assert db.session.get(Watchlist, watchlist_id).name == "Tech"
