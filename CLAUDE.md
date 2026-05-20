# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-user stock price monitoring and alerting backend. Targets long-term investors (DCA strategy) tracking BMV (Mexican) and global equities. Data comes from yfinance (free, no API key), notifications go through Telegram. Designed to be cost-free to run.

## Running the App

```bash
source venv/bin/activate
flask run  # development server at http://127.0.0.1:5000
```

For Telegram webhook access during development, expose the local server via ngrok:
```bash
ngrok http 127.0.0.1:5000 --url https://<your-ngrok-subdomain>.ngrok-free.dev
```

The ngrok URL must then be registered as the Telegram webhook:
```
POST https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<ngrok-url>/telegram/
```

There are no automated tests. Manual exploration uses the Flask shell (`flask shell`) or `yFinance Playground.ipynb`.

## Architecture

```
Routes (Flask Blueprints)
    ↓
Logic Units  (request-level orchestration: CRUD, validation, asset hydration)
    ↓
Services     (external integrations: yfinance, Telegram, alert evaluation)
    ↓
Persistence  (SQLAlchemy ORM over SQLite: Asset, Alert, Watchlist, M2M junction)

+ APScheduler (background jobs running independently of HTTP requests)
```

### Key data flow

- **Adding an asset:** Route → `watchlists_units.add_asset_to_watchlist()` → `FinancialDataService.get_ticker_info()` → creates `Asset` row → writes M2M row.
- **Alert trigger cycle (every 15 min):** `price_updater_job.update_prices_and_alerts()` fetches latest prices from yfinance, updates `Asset` rows, then `AlertService.check_all_alerts()` evaluates conditions and calls `TelegramService.send_message()` if met.
- **Monthly stats refresh:** Runs at app boot and daily at 15:30 CTS (just after BMV close) via `history_fetcher_job.update_monthly_stats()`.

### Alert types

`MonthMinimum`, `PriceBelow`, `PriceAbove` — evaluated in `backend/services/alert_service.py`.

### Telegram commands

`/help`, `/search`, `/info`, `/prices`, `/watchlists`, `/alerts` — handled in `backend/routes/telegrams.py`. Each command calls into logic units and replies via `TelegramService`.

## Environment Variables

All config is loaded from `.env` via `python-dotenv`. Prefixed with `FLASK_` so Flask sees them as config keys:

| Variable | Purpose |
|---|---|
| `FLASK_SQLALCHEMY_DATABASE_URI` | SQLite path (`sqlite:///stockalert.db`) |
| `FLASK_TELEGRAM_BOT_TOKEN` | Telegram Bot API token |
| `FLASK_TELEGRAM_CHAT_ID` | Target Telegram chat for alerts |
| `FLASK_LAST_PRICES_FETCH_INTERVAL` | Background job interval in minutes (default 15) |
| `FLASK_FRONTEND_URL` | CORS origin for Vue.js frontend |

## Database

SQLite file at `instance/stockalert.db`, created automatically on first run via `db.create_all()` in the app factory.

- `Asset` (ticker PK) → has many `Alert`s; M:M with `Watchlist` via `watchlist_asset`
- Cascade deletes: removing a watchlist cleans up M2M rows; if an asset becomes orphaned it is deleted; deleting an asset cascades to its alerts.
- Use the `get_db_session()` context manager from `backend/persistance/db_manager.py` for all writes — it auto-commits on success and rolls back on exception.

## Timezones

All timestamps use GMT-6 (CTS — Central Time Standard, aligned with BMV trading hours). Use `now_cts_time()` from `backend/utils/time_utils.py` instead of `datetime.now()`.

## Conventions

- `backend/__init__.py` is the Flask app factory — blueprints and the scheduler are registered there.
- Route files in `backend/routes/` are thin: they parse/validate HTTP input and delegate to `logic_units/`.
- `logic_units/` orchestrates multi-step operations (create asset if needed, then add to watchlist, etc.) and calls services.
- `services/` talks to external systems only — no direct DB access from services.
- FastAPI and uvicorn are in `requirements.txt` but not in use; they were added anticipating a future migration.
