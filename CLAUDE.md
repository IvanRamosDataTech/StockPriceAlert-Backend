# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-user stock price monitoring and alerting backend. Targets long-term investors (DCA strategy) tracking BMV (Mexican) and global equities. Data comes from yfinance (free, no API key), notifications go through Telegram. Designed to be cost-free to run.

Requires Python 3.12+ (the Docker image uses `python:3.12-slim`, and `routes/telegrams.py` uses nested same-quote f-strings, which are a syntax error on older versions).

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
Current development subdomain: `https://preverbal-ileen-overtimorously.ngrok-free.dev/telegram/`. Recycle this subdomain when possible.

Manual exploration uses the Flask shell (`flask shell`) or `yFinance Playground.ipynb`.

## Testing

```bash
pip install -r requirements-dev.txt   # adds pytest and pytest-flask
pytest -v                             # all tests (config in pytest.ini, testpaths = tests)
pytest tests/services/test_alert_service.py::test_price_below_triggers_when_price_at_threshold  # single test
```

`/verify` (defined in `.claude/commands/verify.md`) runs `pytest -v` and reports failures with stack traces.

Test setup lives in `tests/conftest.py`:
- The `app` fixture builds its own bare `Flask` app with in-memory SQLite. It does **not** use `create_app()`, so there is no scheduler and no DB seeding.
- It registers only the general, prices, watchlists and alerts blueprints. The **Telegram blueprint is not registered**, so Telegram routes are not testable through the `client` fixture as it stands.
- The `db` fixture wipes all tables after each test.
- External calls are mocked with `unittest.mock.patch`, e.g. `patch("backend.services.alert_service.TelegramService.send_message")`.

Coverage is currently limited to `AlertService` (`tests/services/`). The `tests/routes/` and `tests/logic_units/` directories are empty placeholders.

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
- **Alert trigger cycle (every 15 min):** `price_updater_job.update_prices_and_alerts()` fetches latest prices from yfinance, updates `Asset` rows, then `AlertService.check_all_alerts()` evaluates conditions and calls `TelegramService.send_message()` if met. The job is skipped when the database is empty.
- **Monthly stats refresh:** Runs at app boot and daily at 15:30 CTS (just after BMV close) via `history_fetcher_job.update_monthly_stats()`.
- **First boot:** `init_db()` calls `db.create_all()`, then `populate_database()` (from `backend/persistance/db_utils.py`) if all three tables are empty. This seeds the default watchlists (Indexed, Bonds, Patrimonial, Satelites, Exchanges) and `MonthMinimum` alerts on the indexed and satellite assets. Seeded assets have price `0.00` until the first scheduler run fills them in.

### Alert types

`MonthMinimum`, `PriceBelow`, `PriceAbove`. They are evaluated in `backend/services/alert_service.py`; the constants are in `backend/models/alert.py`. `MonthMinimum` has no price threshold.

### Telegram bot

The webhook is `POST /telegram/` in `backend/routes/telegrams.py`. `_process_command()` dispatches the first token of the message through a dict to `_<name>_command(args)` handlers. Handlers reply via `TelegramService.send_message(current_app, text)` as a side effect, so the HTTP response body is not what the user sees.

| Group | Commands |
|---|---|
| Info | `/help`, `/search`, `/info`, `/prices` |
| FX | `/ex_rate`, `/convert` (USD to MXN) |
| Watchlists | `/watchlists`, `/watchlist_new`, `/watchlist_add`, `/watchlist_remove`, `/watchlist_delete` |
| Alerts | `/alerts`, `/alert_set`, `/alert_unset`, `/alert_update` |

When adding a command, update three places: the handler, the `switcher` dict in `_process_command`, and the text in `_help_command`.

Commands and arguments are case-insensitive. The command name is lowercased in `_process_command`. Tickers go through `_normalize_ticker()` (uppercase) and alert types through `normalize_alert_type()` in `alerts_units.py`, which returns the canonical spelling. Use these helpers for any new command, because `AlertService` compares alert types with exact `==`, so a mis-cased stored type would silently never fire. Watchlist names are unique ignoring case.

Known gaps in this file:
- `float(args[2])` in `_alert_set_command` and `_alert_update_command` runs outside the `try` block, so a non-numeric price gets no reply.
- There is no check that the sender matches `FLASK_TELEGRAM_CHAT_ID`.

### Scheduler

`backend/scheduler/scheduler.py` registers the jobs. It contains large commented-out blocks that swap in the simulated jobs from `scheduler/experimental/` (fake prices and history, forced alerts, test Telegram messages) for testing with short second-level intervals. Uncomment those and comment out the "Development orchestration queue" block to use them.

## Environment Variables

All config is loaded from `.env` via `python-dotenv`. Prefixed with `FLASK_` so Flask sees them as config keys (`flask_app.config.from_prefixed_env()`):

| Variable | Purpose |
|---|---|
| `FLASK_SQLALCHEMY_DATABASE_URI` | SQLite path (`sqlite:///stockalert.db`) |
| `FLASK_TELEGRAM_BOT_TOKEN` | Telegram Bot API token |
| `FLASK_TELEGRAM_CHAT_ID` | Target Telegram chat for alerts |
| `FLASK_LAST_PRICES_FETCH_INTERVAL` | Background job interval in minutes (default 15) |
| `FLASK_FRONTEND_URL` | CORS origin for Vue.js frontend |

`.env` is gitignored and dockerignored. See `.env.example`.

## Database

SQLite file at `instance/stockalert.db` in development. In Docker it lives on the `stockdata` volume mounted at `/data`.

- `Asset` (ticker PK) → has many `Alert`s; M:M with `Watchlist` via `watchlist_asset`
- Cascade deletes: removing a watchlist cleans up M2M rows; if an asset becomes orphaned it is deleted; deleting an asset cascades to its alerts.
- Use the `get_db_session()` context manager from `backend/persistance/db_manager.py` for all writes. It auto-commits on success and rolls back on exception.
- `db_utils.py` also has helpers for the Flask shell (`populate_test_database()`, `clean_database()`, `update_asset()`, `query_*()`). Load them inside `flask shell` only, because they need an app context.

## Deployment (Docker + Caddy on a VPS)

```bash
docker compose up -d --build
```

- `Dockerfile` runs `gunicorn "backend:create_app()" --workers=1 --threads=4 --bind=0.0.0.0:8000`. **Keep `--workers=1`**: APScheduler runs in-process, so more workers start duplicate schedulers and send duplicate alerts.
- Only `backend/` is copied into the image. `.dockerignore` excludes `tests/`, `docs/`, `.env`, `instance/` and `*.db`.
- `docker-compose.yml` injects `.env` at runtime from the VPS (never baked into the image) and tags the image `stockalertapp:<version>`. **Bump that version tag when releasing.**
- The app container only `expose`s 8000. TLS is terminated by a Caddy instance that already runs on the VPS for another app (n8n). The app joins that Caddy's Docker network (`external_caddy`, which maps to `n8n_default`), and `Caddyfile` documents the entry to add there (`ivanstockalert.duckdns.org` → `app:8000`). The `caddy` service in the compose file is commented out on purpose.
- The Telegram webhook in production is `https://ivanstockalert.duckdns.org/telegram/`.

## Timezones

All timestamps use GMT-6 (CTS — Central Time Standard, aligned with BMV trading hours). Use `now_cts_time()` from `backend/utils/time_utils.py` instead of `datetime.now()`. `create_app()` also sets the process `TZ` to `Etc/GMT+6`.

## Conventions

- `backend/__init__.py` is the Flask app factory. Blueprints and the scheduler are registered there, and the scheduler is started on every `create_app()` call, including production.
- Route files in `backend/routes/` are thin: they parse/validate HTTP input and delegate to `logic_units/`.
- `logic_units/` orchestrates multi-step operations (create asset if needed, then add to watchlist, etc.) and calls services.
- `services/` talks to external systems only — no direct DB access from services.
- The `backend/persistance/` directory name is spelled this way (not "persistence"), and `services/finantial_data_service.py` likewise. Match the existing spelling in imports.

## Tooling

- `.github/workflows/claude.yml` and `claude-code-review.yml` run the Claude PR assistant and automated PR review on GitHub.
- `Procfile` (gunicorn bound to `$PORT`) and the "Render" comment in `create_app()` are leftovers from an earlier PaaS deployment. Docker is the current production path.
