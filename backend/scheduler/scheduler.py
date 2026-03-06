import logging
import os


from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime
import time
from .price_updater_job import update_prices_and_alerts
from .history_fetcher_job import fetch_daily_history
from .experimental.telegram_messages_job import send_test_telegram_message
from .experimental.simulated_price_updater_job import simulate_fecthing_prices
from .experimental.simulated_history_fetcher_job import simulate_fecthing_history

logger = logging.getLogger(__name__)

_scheduler = None

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
    
    ### Test orchestration queue - uncomment for testing experimenta job executions

    # scheduler.add_job(
    #     func=send_test_telegram_message,
    #     trigger='interval',
    #     seconds=21,
    #     args=[app, "Automatic message from scheduler job - testing Telegram bot communication"],
    #     replace_existing=True,
    #     id="experimental_telegram_message_job"
    # )

    scheduler.add_job(
        # func=update_prices_and_alerts,
        func=simulate_fecthing_prices,
        trigger="interval",
        # minutes=last_prices_minutes,
        seconds=last_prices_minutes,  # Use seconds for testing
        args=[last_prices_minutes],
        id="last_prices_fetch",
        replace_existing=True,
    )
    scheduler.add_job(
        # func=fetch_daily_history,
        func=simulate_fecthing_history,
        trigger="interval",
        # minutes=history_minutes,
        seconds=history_minutes,  # Use seconds for testing
        args=[history_minutes],
        id="historical_fetch",
        replace_existing=True,
    )


    ### Development orchestrationt queue - uncomment for real data fetching
    
    # scheduler.add_job(
    #     func=update_prices_and_alerts,
    #     trigger="interval",
    #     minutes=last_prices_minutes,
    #     args=[app],
    #     id="last_prices_fetch",
    #     replace_existing=True,
    # )
    # scheduler.add_job(
    #     func=fetch_daily_history,
    #     trigger="interval",
    #     minutes=history_minutes,
    #     args=[app],
    #     id="historical_fetch",
    #     replace_existing=True,
    # )

    scheduler.start()
    _scheduler = scheduler
    logger.info(
        #"Scheduler started with intervals (minutes): last_prices=%s, history=%s",
        "Scheduler started in test mode with intervals (seconds): last_prices=%s, history=%s",
        last_prices_minutes,
        history_minutes,
    )
    return scheduler