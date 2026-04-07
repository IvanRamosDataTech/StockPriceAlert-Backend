from datetime import datetime, timedelta, timezone


# Fixed offset timezone for GMT-6 standardization across the app.
GMT_MINUS_6 = timezone(timedelta(hours=-6))


def now_cts_time() -> datetime:
    """Return current datetime normalized to GMT-6.
        This is the Central Time Standard (CTS)
    """
    return datetime.now(GMT_MINUS_6)
