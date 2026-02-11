print("Loading  models subpackage ...")

# Import all models explicitly to ensure they are registered with SQLAlchemy.
from .asset import Asset
from .alert import Alert
from .watchlist import Watchlist

__all__ = ['asset', 'alert', 'watchlist']

