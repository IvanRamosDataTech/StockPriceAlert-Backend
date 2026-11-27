from unittest.mock import patch

import pytest

from backend.routes.telegrams import _convert_command, _help_command
from backend.services.finantial_data_service import SUPPORTED_CURRENCY_PAIRS


def _run(app, args, rate=20.0):
    with app.app_context(), \
         patch("backend.routes.telegrams.FinancialDataService.exchange_rate", return_value={"rate": rate} if rate else {}) as ex, \
         patch("backend.routes.telegrams.TelegramService.send_message") as send:
        _convert_command(args)
    return ex, send


def test_convert_defaults_to_usd_mxn_when_pair_missing(app):
    ex, send = _run(app, ["100"])
    ex.assert_called_once_with(pair="USD/MXN")
    assert send.call_args[0][1] == "100 USD = 2000.0 MXN at rate 20.0 MXN/USD"


def test_convert_with_pair_is_case_insensitive(app):
    ex, send = _run(app, ["eur/mxn", "50"], rate=21.5)
    ex.assert_called_once_with(pair="EUR/MXN")
    assert send.call_args[0][1] == "50 EUR = 1075.0 MXN at rate 21.5 MXN/EUR"


def test_convert_unsupported_pair_lists_all_supported_pairs(app):
    ex, send = _run(app, ["XXX/YYY", "10"])
    ex.assert_not_called()
    text = send.call_args[0][1]
    assert "Unsupported currency pair 'XXX/YYY'" in text


def test_convert_pair_without_amount(app):
    ex, send = _run(app, ["EUR/USD"])
    ex.assert_not_called()
    assert "Missing amount" in send.call_args[0][1]


@pytest.mark.parametrize("args", [["abc"], ["EUR/USD", "abc"], ["EUR/USD", "nan"], ["USD/MXN", "inf"]])
def test_convert_invalid_amount(app, args):
    ex, send = _run(app, args)
    ex.assert_not_called()
    assert "Invalid amount" in send.call_args[0][1]


@pytest.mark.parametrize("args", [[], ["EUR/USD", "10", "extra"]])
def test_convert_wrong_number_of_args(app, args):
    ex, send = _run(app, args)
    ex.assert_not_called()
    assert "Usage: /convert" in send.call_args[0][1]


def test_convert_rate_unavailable(app):
    _, send = _run(app, ["EUR/USD", "10"], rate=None)
    assert send.call_args[0][1] == "Could not retrieve exchange rate for EUR/USD."


def test_help_documents_convert_pairs(app):
    with app.app_context(), patch("backend.routes.telegrams.TelegramService.send_message") as send:
        _help_command([])
    text = send.call_args[0][1]
    assert "/convert {currency pair} {amount}" in text
    assert "EUR/MXN" in text
    assert "USD/MXN is used" in text


def test_no_duplicate_or_self_pairs():
    assert len(set(SUPPORTED_CURRENCY_PAIRS)) == len(SUPPORTED_CURRENCY_PAIRS) == 88
    assert all(p.split("/")[0] != p.split("/")[1] for p in SUPPORTED_CURRENCY_PAIRS)
