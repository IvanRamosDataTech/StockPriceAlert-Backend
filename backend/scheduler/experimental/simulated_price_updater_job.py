
import logging
from datetime import datetime


def simulate_fecthing_prices(interval):
    """
    Simulate fetching prices for testing purposes.
    """
    logger = logging.getLogger(__name__)
    logger.info("Simulating price fetch... Interval - %s seconds - %s", interval, datetime.now())