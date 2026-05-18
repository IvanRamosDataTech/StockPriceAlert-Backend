import logging
import os


from apscheduler.schedulers.background import BackgroundScheduler

from ..utils.time_utils import GMT_MINUS_6, now_cts_time
from .price_updater_job import update_prices_and_alerts
from .history_fetcher_job import update_monthly_stats
from .experimental.telegram_messages_job import send_test_telegram_message
from .experimental.simulated_price_updater_job import simulate_fecthing_prices
from .experimental.simulated_history_fetcher_job import simulate_fecthing_history
from .experimental.forced_alert_job import updated_price_send_alert

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

    scheduler = BackgroundScheduler()
    
    ### Test orchestration queue - uncomment for testing experimenta job executions


    # scheduler.add_job(
    #     func=update_monthly_stats,
    #     trigger='interval',
    #     seconds=30,  # Use seconds for testing
    #     args=[app],
    #     id="monthly_prices_fetch",
    #     replace_existing=True
    # )

    # scheduler.add_job(
    #     func=update_prices_and_alerts,
    #     trigger="interval",
    #     seconds=30,  # Use seconds for testing
    #     args=[app],
    #     id="last_prices_fetch",
    #     replace_existing=True,
    # )

    # scheduler.add_job(
    #     func=updated_price_send_alert,
    #     trigger='interval',
    #     seconds=120,  # Use seconds for testing
    #     args=[app],
    #     replace_existing=True,
    #     id="experimental_telegram_price_alert_job"
    # )

    # scheduler.add_job(
    #     func=send_test_telegram_message,
    #     trigger='interval',
    #     seconds=10,
    #     args=[app, "Automatic message from experimentalscheduler job - testing Telegram bot communication"],
    #     replace_existing=True,
    #     id="experimental_telegram_message_job"
    # )

    # scheduler.add_job(
    #     # func=update_prices_and_alerts,
    #     func=simulate_fecthing_prices,
    #     trigger="interval",
    #     # minutes=last_prices_minutes,
    #     seconds=last_prices_minutes,  # Use seconds for testing
    #     args=[last_prices_minutes],
    #     id="last_prices_fetch",
    #     replace_existing=True,
    # )
    # scheduler.add_job(
    #     # func=fetch_daily_history,
    #     func=simulate_fecthing_history,
    #     trigger="interval",
    #     # minutes=history_minutes,
    #     seconds=history_minutes,  # Use seconds for testing
    #     args=[history_minutes],
    #     id="historical_fetch",
    #     replace_existing=True,
    # )


    ### Development orchestrationt queue - uncomment for real data fetching
    
    scheduler.add_job(
        func=update_prices_and_alerts,
        trigger="interval",
        minutes=last_prices_minutes,
        args=[app],
        id="last_prices_fetch",
        replace_existing=True,
    )

    #runs when markets close in Mexico 
    scheduler.add_job(
        func=update_monthly_stats,
        trigger="cron",
        hour=15,
        minute=30,
        timezone=GMT_MINUS_6,
        args=[app],
        id="historical_fetch",
        replace_existing=True,
    )

    scheduler.add_job(
        func=update_monthly_stats,
        trigger="date",
        run_date=now_cts_time(),
        args=[app],
        id="historical_fetch_on_boot",
        replace_existing=True,
    )

    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "Scheduler started: last_prices every %s minutes, historical_fetch now on boot and daily at 15:30 CTS",
        last_prices_minutes,
    )
    return scheduler