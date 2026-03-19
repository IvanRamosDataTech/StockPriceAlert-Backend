import logging
from datetime import datetime

def simulate_fecthing_history(interval):
    """
    Simulate fetching historical data for testing purposes.
    """
    logger = logging.getLogger(__name__)
    logger.info("Simulating historical data fetch... Interval: %s seconds -  %s", interval, datetime.now())
