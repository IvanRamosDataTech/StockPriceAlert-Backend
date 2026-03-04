import logging
import os


from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime
import time
from .price_updater import update_prices_and_alerts
from .history_fetcher import fetch_daily_history

logger = logging.getLogger(__name__)

_scheduler = None


def simulate_fecthing_prices(interval):
    """
    Simulate fetching prices for testing purposes.
    """
    logger.info("Simulating price fetch... Interval: %s seconds, Current time: %s", interval, datetime.now())


def simulate_fecthing_history(interval):
    """
    Simulate fetching historical data for testing purposes.
    """
    logger.info("Simulating historical data fetch... Interval: %s seconds, Current time: %s", interval, datetime.now())


def start_scheduler(app):
    """
    Start APScheduler with two interval jobs:
    - Update latest prices + check alerts
    - Fetch historical prices + update stats
    """
    global _scheduler

    if _scheduler and _scheduler.running:
        return _scheduler

    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return None

    last_prices_minutes = int(app.config.get("LAST_PRICES_FETCH_INTERVAL", 15))
    history_minutes = int(app.config.get("HISTORICAL_FETCH_INTERVAL", 1440))

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        # func=update_prices_and_alerts,
        func=simulate_fecthing_prices,
        trigger="interval",
        # minutes=last_prices_minutes,
        seconds=last_prices_minutes,  # Use seconds for testing
        args=[app],
        id="last_prices_fetch",
        replace_existing=True,
    )
    scheduler.add_job(
        # func=fetch_daily_history,
        func=simulate_fecthing_history,
        trigger="interval",
        # minutes=history_minutes,
        seconds=history_minutes,  # Use seconds for testing
        args=[app],
        id="historical_fetch",
        replace_existing=True,
    )

    scheduler.start()
    _scheduler = scheduler
    logger.info(
        #"Scheduler started with intervals (minutes): last_prices=%s, history=%s",
        "Scheduler started in test mode with intervals (seconds): last_prices=%s, history=%s",
        last_prices_minutes,
        history_minutes,
    )
    return scheduler