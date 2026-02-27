from ..persistance.db_manager import db
from .asset_watchlist import watchlist_asset

class Asset(db.Model):

    __tablename__ = 'asset'

    ticker = db.Column(db.String(10), nullable=False, primary_key=True)
    displayed_name = db.Column(db.String(20), nullable=False)
    # We'll need a previous_price to calculate price change and price change percent
    # previous_price will persiste the last price pooled from yFinance, and will be updated with price field.
    # If it's the first time we save an asset, previous_price will be the same as current price, so that the price change and price change percent will be 0.0 by default.
    # same as price as default value.
    previous_price = db.Column(db.Float, nullable=False, default=0.0)
    price = db.Column(db.Float, nullable=False)
    ## Basic statistics of price in last trailing 30 days, which can be used for alerting rules
    price_change = db.Column(db.Float, nullable=False, default=0.0)
    price_change_percent = db.Column(db.Float, nullable=False, default=0.0)
    min_month_price = db.Column(db.Float, nullable=False, default=0.0)
    max_month_price = db.Column(db.Float, nullable=False, default=0.0)
    avg_month_price = db.Column(db.Float, nullable=False, default=0.0)
    alerts = db.relationship('Alert', back_populates='asset', cascade='all, delete-orphan')
    watchlists = db.relationship('Watchlist', secondary=watchlist_asset, back_populates='assets')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def update_price_statistics(self, latest_price):
        self.previous_price = self.price
        self.price = latest_price
        self.price_change = round(self.price - self.previous_price, 2)
        self.price_change_percent = round((self.price_change / self.previous_price) * 100, 2) if self.previous_price else 0.0
        # # Update the min and max intraday
        if self.price < self.min_month_price:
            self.min_month_price = self.price
        if self.price > self.max_month_price:
            self.max_month_price = self.price
        self.updated_at = db.func.current_timestamp()

    def __str__(self):
        info = f"<Asset {self.ticker} - {self.displayed_name}> \n"
        info += "Alerts: \n"
        for alert in self.alerts:
            info += str(alert) + "; \n"
        info += "Watchlists: \n"
        for list in self.watchlists:
            info += f"{list.name}; \n"
        return info