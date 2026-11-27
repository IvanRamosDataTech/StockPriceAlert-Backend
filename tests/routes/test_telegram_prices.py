from unittest.mock import patch

from backend.models.asset import Asset
from backend.models.watchlist import Watchlist
from backend.routes.telegrams import _prices_command


def _setup(db):
    aapl = Asset(ticker="AAPL", displayed_name="Apple", price=1.0, min_month_price=1.0)
    msft = Asset(ticker="MSFT", displayed_name="Microsoft", price=1.0, min_month_price=1.0)
    indexed = Watchlist(name="Indexed")
    indexed.assets.extend([aapl, msft])
    tech = Watchlist(name="Tech Stocks")
    tech.assets.append(msft)
    empty = Watchlist(name="Empty")
    db.session.add_all([aapl, msft, indexed, tech, empty])
    db.session.commit()


def _fake_prices(tickers):
    return {t: {"original_price": 10.0, "converted_price": 200.0} for t in tickers}


def _run(app, args):
    with app.app_context(), \
         patch("backend.routes.telegrams.FinancialDataService.latest_prices", side_effect=_fake_prices) as prices, \
         patch("backend.routes.telegrams.TelegramService.send_message") as send:
        _prices_command(args)
    return prices, send


def test_prices_plain_tickers_still_work(app, db):
    _setup(db)
    prices, send = _run(app, ["aapl", "goog"])
    prices.assert_called_once_with(["AAPL", "GOOG"])
    assert "AAPL 10.0" in send.call_args[0][1]


def test_prices_watchlist_name_expands_to_assets_case_insensitive(app, db):
    _setup(db)
    prices, send = _run(app, ["indexed"])
    prices.assert_called_once_with(["AAPL", "MSFT"])
    text = send.call_args[0][1]
    assert '"Indexed":' in text and "AAPL" in text and "MSFT" in text


def test_prices_multiword_watchlist_name(app, db):
    _setup(db)
    prices, _ = _run(app, ["tech", "stocks"])
    prices.assert_called_once_with(["MSFT"])


def test_prices_mixed_ticker_and_watchlist_fetches_each_ticker_once(app, db):
    _setup(db)
    prices, _ = _run(app, ["MSFT", "Indexed"])
    prices.assert_called_once_with(["MSFT", "AAPL"])


def test_prices_empty_watchlist_replies_without_fetching(app, db):
    _setup(db)
    prices, send = _run(app, ["Empty"])
    prices.assert_not_called()
    assert "no assets" in send.call_args[0][1]
