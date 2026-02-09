# Stock Price Alert POC: Technical Decision Report (Updated)

**Project:** Personal Stock Price Alert System (Proof of Concept)  
**Date:** February 2026  
**Target User:** Long-term investors (DCA/periodic buyers, not traders) — Global markets (ETFs + Stocks)  
**Duration:** POC phase; path to MVP within 2-3 months if viable  
**Status:** Tech stack revised from Node.js → Flask (Python backend) due to yfinance requirements

---

## Executive Summary

This report documents the **updated technology stack** chosen for a minimal stock price alerting system. Following the decision to use **yfinance** (Python library) for unrestricted access to global ETF/stock data, the backend was shifted from Node.js to **Flask + Python**, maintaining all other architectural decisions.

The stack continues to prioritize **developer velocity, operational simplicity, and zero-cost development** while gaining unrestricted financial data access (critical for long-term investors tracking passive ETFs globally).

### Stack Overview (Updated)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Backend** | Flask + Python | yfinance integration; sync-first simplicity for POC |
| **Scheduler** | APScheduler | Native Python; in-process polling; proven for small apps |
| **Frontend** | Vue.js 3 + Chart.js | Unchanged; keeps frontend strategy intact |
| **Database** | SQLite + SQLAlchemy ORM | File-based; zero setup; migration path to PostgreSQL |
| **Stock Data** | yfinance | Free, unrestricted access to 15,000+ global ETFs/stocks |
| **Alerts** | Telegram Bot API | Push notifications to mobile; free tier |
| **Hosting** | Railway | $5-15/month or free tier; supports Python natively |
| **Cost** | ~$0-15/month | yfinance frees constraint; no API subscription needed |

---

## Revision Context: Why Python Backend?

### The API Cost Constraint

**Original Decision:** Financial Modeling Prep (FMP) API  
- Free tier: 250 requests/day  
- **Problem:** For global ETF tracking, insufficient (need multiple updates across US, EU, Asia markets)  
- **Cost:** $20-50/month for paid tiers; not viable for POC  

**New Decision:** yfinance Library  
- **Advantage:** Python library wrapping Yahoo Finance; no API key; unlimited calls (non-commercial)  
- **Coverage:** 15,000+ ETFs, stocks, crypto, forex — all global markets  
- **Cost:** $0  
- **Trade-off:** 15-20min delayed data (acceptable for long-term investors, not traders)  

### Why Python > Node.js for yfinance?

| Aspect | Node.js | Python | Winner |
|--------|---------|--------|--------|
| **yfinance Integration** | Wrapper library (node-yfinance); indirect | Native; direct | Python ✅ |
| **Data Processing** | Manual manipulation | pandas/numpy | Python ✅ |
| **Learning Curve** | Still async/await | Simpler (sync-first) | Python ✅ |
| **POC Timeline** | ~6-8 hrs | ~4-5 hrs | Python ✅ |
| **Runtime Footprint** | ~80 MB | ~50-100 MB | Comparable |

**Decision:** Shift to Flask backend; keep Vue frontend. Both simplified.

---

## 1. Backend: Flask + Python

### Why Flask (Not FastAPI)

**Trade-off Analysis:**

| Criterion | Flask | FastAPI | POC Fit |
|-----------|-------|---------|---------|
| **Setup Time** | 5 min | 10 min | Flask ✅ |
| **Async Complexity** | None (sync) | Native (required) | Flask ✅ |
| **yfinance Ease** | Direct call | Needs executor wrapper | Flask ✅ |
| **Learning Curve** | Minimal | Moderate (type hints, ASGI) | Flask ✅ |
| **Single-User POC** | Adequate | Over-engineered | Flask ✅ |
| **Scaling to MVP** | Need rewrite if concurrent load | Incremental async | FastAPI (marginal) |

**Decision Rationale:**

For a **single-user POC with no concurrency**, Flask's synchronous model eliminates unnecessary complexity. Advantages:

1. **Direct yfinance calls** — No threading/executor wrapper needed
   ```python
   @app.route('/api/prices/<symbol>')
   def get_price(symbol):
       price = yf.Ticker(symbol).history(period="1d")['Close'].iloc[-1]
       return {'price': price}
   ```

2. **Seamless APScheduler integration** — Runs in same process as Flask
   ```python
   scheduler = APScheduler()
   scheduler.init_app(app)
   scheduler.start()
   ```

3. **Faster iteration** — One mental model; no async/await semantics
4. **Smaller memory footprint** — ~50-80 MB vs FastAPI ~80-100 MB
5. **Proven for small projects** — Flask's maturity and simplicity = lower risk for POC

### Architecture

```
backend/
├── app.py                          # Flask app factory
├── config.py                       # Config (dev/prod)
├── requirements.txt                # Python deps
├── .env.example                    # Secrets template
│
├── db/
│   ├── __init__.py
│   └── database.py                 # SQLAlchemy + SQLite init
│
├── models/
│   ├── watchlist.py               # ORM: Watchlist table
│   └── alert.py                   # ORM: Alert table
│
├── services/
│   ├── yfinance_service.py        # Ticker data fetching
│   ├── alert_service.py           # Price comparison logic
│   └── telegram_service.py        # Telegram notifications
│
├── routes/
│   ├── watchlist_routes.py        # GET/POST/DELETE /api/watchlist
│   ├── alert_routes.py            # GET/POST/DELETE /api/alerts
│   └── price_routes.py            # GET /api/prices/:symbol
│
└── scheduler/
    └── price_monitor.py           # APScheduler polling job
```

### Key Technical Decisions

**ORM: SQLAlchemy**
- Abstraction layer for future DB migration (SQLite → PostgreSQL)
- Clean migration support (Alembic)
- Type hints via hybrid_property for clarity

**Error Handling:**
- Graceful failures in scheduler (log, continue)
- 404/400 responses for invalid API calls
- Telegram fallback if message send fails (logged, non-blocking)

**Testing:**
- Unit tests for alert_service (threshold logic)
- Integration tests for API endpoints
- Manual testing of scheduler (add test watchlist, verify Telegram)

---

## 2. Database: SQLite + SQLAlchemy

### Why SQLite for POC

**Pros:**
- Zero setup; single `.db` file
- Sufficient for 5-50 watchlist items + alert history
- Fast enough for polling every 5 minutes
- SQLAlchemy ORM abstracts SQL dialect

**Migration Path (POC → MVP):**
1. Design schema in SQLAlchemy (day 1)
2. Never use SQLite-specific features (avoid `AUTOINCREMENT`, etc.)
3. When scaling: swap connection string → PostgreSQL on Railway/Supabase
4. Run migrations; code changes minimal

### Schema

```sql
-- Watchlist
CREATE TABLE watchlist (
  id INTEGER PRIMARY KEY,
  symbol VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(100),
  price_at_add FLOAT,
  created_at DATETIME,
  updated_at DATETIME
);

-- Alerts
CREATE TABLE alert (
  id INTEGER PRIMARY KEY,
  watchlist_id INTEGER NOT NULL,
  alert_type VARCHAR(20),                -- 'price_above' or 'price_below'
  threshold_price FLOAT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  triggered BOOLEAN DEFAULT FALSE,
  triggered_at DATETIME,
  created_at DATETIME,
  updated_at DATETIME,
  FOREIGN KEY (watchlist_id) REFERENCES watchlist(id) ON DELETE CASCADE
);
```

---

## 3. Scheduler: APScheduler

### Why APScheduler (In-Process)

**Alternative Considered: Celery + Redis**
- **Pros:** Distributed; retries; task persistence
- **Cons:** Requires Redis broker; separate worker process; overkill for POC

**APScheduler Decision:**
- Runs inside Flask process (same as node-cron logic)
- Executes polling every 5 minutes (configurable via `.env`)
- Single point of failure (acceptable; Railway auto-restarts)
- Easy to upgrade to Celery later if needed

### Polling Job Logic

```python
# scheduler/price_monitor.py
@scheduler.task('interval', id='price_monitor', seconds=300)  # 5 minutes
def check_all_prices():
    """
    1. Fetch watchlist items
    2. Get current price for each (yfinance)
    3. Check alert thresholds
    4. Send Telegram if triggered
    5. Log to database
    """
    for item in watchlist_items:
        price = yfinance_service.get_current_price(item.symbol)
        triggered = alert_service.check_threshold(price, item)
        
        if triggered:
            telegram_service.send_alert(...)
            alert.triggered = True
            db.session.commit()
```

**Cost/Benefit:**
- No infrastructure overhead (vs. separate worker)
- Transparent logging and error handling
- **Downside:** Polling pauses if Flask process crashes (mitigated by Railway auto-restart)

---

## 4. Frontend: Vue.js 3 + Chart.js (Unchanged)

### Why Vue.js Remains Best Choice

**Not Changed:**
- Vue.js reactive component model fits POC UI perfectly
- Chart.js renders OHLC + price history easily
- Vite dev server provides fast iteration
- Separation from backend enables independent scaling

### Layout (Matches StockAlarm Reference)

**Left Sidebar:** Watchlist items (search, add, delete)  
**Center:** Stock info card + price chart (line chart, period selector)  
**Right Sidebar:** Alert management (create, delete, reset)

**Polling Update:** Frontend refreshes data every 30s (HTTP GET to backend)

---

## 5. API Integration: yfinance

### Why yfinance Over Alternatives

| API | Free Tier | Global Coverage | Latency | POC Fit |
|-----|-----------|-----------------|---------|---------|
| **yfinance** | Unlimited | 15,000+ ETF/stocks | 15-20 min delayed | ★★★★★ |
| FMP | 250/day | US stocks only | Real-time | ★★★☆☆ |
| Finnhub | Free tier | Limited | Real-time | ★★★☆☆ |
| Alpha Vantage | 5/min | US + forex | Real-time | ★★★☆☆ |

**Trade-off Clarity:**
- Accept 15-20 min data delay (irrelevant for long-term investors)
- Gain access to global markets (VOO, VTI, VXUS, Asian ETFs, etc.)
- Zero cost; unlimited queries

---

## 6. Alerts: Telegram Bot

### Why Telegram (Unchanged)

**Advantages:**
- Free (no Twilio costs)
- Instant push notifications to mobile
- Simple bot API
- Works globally (unlike email, which lands in spam)

### Implementation

```python
# services/telegram_service.py
def send_alert(symbol, alert_type, threshold, current_price):
    """Send Telegram message via bot API"""
    message = f"📈 {symbol} reached ${current_price:.2f} (above ${threshold:.2f})"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", ...)
```

**Setup:** 
1. Create bot with BotFather on Telegram
2. Get token + chat ID
3. Add to `.env`

---

## 7. Deployment: Railway

### Why Railway (Unchanged)

**Hosting Comparison:**

| Platform | Cost | Setup | Python Support | Free Tier |
|----------|------|-------|-----------------|-----------|
| **Railway** | $5-15/month | Minimal (git push) | ✅ Excellent | $5 credit |
| Render | Free tier | Minimal | ✅ Good | 750 hrs/mo |
| Heroku | $7/month min | Simple | ✅ Good | **Killed** |
| Fly.io | Free tier | Moderate | ✅ Good | ✅ Limited |
| AWS Lambda | Free tier | Complex | ✅ Serverless | 1M req/mo |

**Decision:** Railway best balance of simplicity + cost for stateful scheduler app.

### Deployment Steps

```bash
# 1. Connect Railway to GitHub
# 2. Railway detects requirements.txt (Python project)
# 3. Builds: pip install -r requirements.txt
# 4. Runs: gunicorn + uvicorn (or python app.py)
# 5. Auto-restarts on crash
# 6. Logs streamed to terminal
```

**Cost Estimate:**
- Flask + APScheduler: ~$5-10/month
- Database (SQLite file): $0
- **Total:** ~$5-15/month

---

## 8. Development Workflow

### Local Setup (4-5 hours)

```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py                          # Runs on localhost:5000

# Frontend
npm install
npm run dev                            # Runs on localhost:5173
```

### Testing Flow

1. **Add VOO (Vanguard) to watchlist**
2. **Create alert:** "Price above $150"
3. **Monitor logs:** Check scheduler running
4. **Trigger test:** Manually update DB (or wait for market move)
5. **Verify Telegram:** Message arrives on mobile

---

## 9. POC Goals Alignment

### Original Constraints

| Goal | Status | Tech Support |
|------|--------|--------------|
| **$0-cost development** | ✅ Met | yfinance free + SQLite + Flask |
| **Relaxed data latency** | ✅ Met | yfinance 15-20 min acceptable |
| **Imperfect > Perfect** | ✅ Met | Minimal UI, core logic only |
| **Simplicity of requirements** | ✅ Met | Single-user; no auth; one scheduler job |
| **Unrestricted global market access** | ✅ Met (NEW) | yfinance solves original API constraint |

### What We're NOT Building (Scope Reduction)

- ❌ Real-time trading alerts
- ❌ Technical analysis (RSI, MACD, Bollinger Bands)
- ❌ Multi-user support / authentication
- ❌ Mobile app (Telegram is the "app")
- ❌ Historical backfill / data warehouse
- ❌ Email support (Telegram only)

---

## 10. Migration Path: POC → MVP

If POC succeeds and user base grows:

### Phase 1: Performance (Month 2-3)
- Profile Flask app for bottlenecks
- If needed: migrate to FastAPI (add async/await to routes, executor for yfinance)
- Cost: ~1-2 days

### Phase 2: Data (Month 3-4)
- Swap SQLite → PostgreSQL (1 connection string change)
- Run SQLAlchemy migrations
- Cost: ~2-4 hours

### Phase 3: Scaling (Month 4+)
- Add Redis cache for price data (avoid yfinance throttling)
- Celery queue if 100+ concurrent users
- S3 for price history exports
- Cost: +$20-50/month

---

## 11. Technical Debt & Risks

### Identified Risks

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| **yfinance API changes** | Low | Abstraction layer (service); easy to swap |
| **Telegram bot blocked** | Very Low | Use email as fallback |
| **Scheduler misses alerts** | Low | Logging + manual retry logic |
| **SQLite corrupted** | Very Low | Railway backups; daily exports |
| **Rate limit (yfinance)** | Low | APScheduler runs 12x/day per symbol; under limit |

### Technical Debt

- Minimal TypeScript/type hints (Flask is dynamically typed)
  - Mitigation: Docstrings + unit tests
- No caching layer (yfinance hits Yahoo Finance every poll)
  - Mitigation: Acceptable for POC; upgrade to Redis later
- No horizontal scaling (single process)
  - Mitigation: POC assumes single-user; non-issue currently

---

## 12. Comparison: Final Decision vs Alternatives

### Decision Summary Table

| Component | Chosen | Alternative | Why Chosen |
|-----------|--------|-------------|-----------|
| Backend | **Flask** | FastAPI | Sync simplicity for single-user POC; faster iteration |
| Stock Data | **yfinance** | FMP API | Free global access vs $20/month + limited coverage |
| Scheduler | **APScheduler** | Celery | In-process; zero infrastructure vs separate broker |
| Frontend | **Vue 3** | React | Smaller bundle; simpler learning curve |
| Database | **SQLite** | PostgreSQL | Zero setup; ORM-abstracted for later migration |
| Hosting | **Railway** | Render | Better Python support + scheduler statefulness |
| Alerts | **Telegram** | Email | Instant mobile push; better UX than email |

---

## 13. Success Metrics (MVP Threshold)

**POC is successful if:**
1. ✅ Can add 10+ global ETFs/stocks to watchlist
2. ✅ Scheduler runs continuously without crashes (72 hours)
3. ✅ Telegram alerts arrive within 1 minute of threshold trigger
4. ✅ Full UI implemented (watchlist, alerts, charts)
5. ✅ Total development time < 20 hours

**If 4/5 met → Proceed to MVP; otherwise → Iterate on feedback**

---

## Conclusion

The **Python + Flask backend** represents an optimal trade-off for a single-developer POC:

- **Removes API cost constraint** (yfinance $0 vs FMP $20+/month)
- **Simplifies backend logic** (sync Flask vs async FastAPI)
- **Maintains clean architecture** (services + ORM for future scaling)
- **Preserves frontend strategy** (Vue.js unchanged)
- **Keeps deployment simple** (Railway auto-detect Python)

This decision trades theoretical scalability (FastAPI async) for pragmatic iteration speed—exactly what a POC needs.

---

**Report Version:** 2.0 (Updated Feb 2026)  
**Status:** Ready for development sprint  
**Scaffolding:** Complete (both backend + frontend provided)
