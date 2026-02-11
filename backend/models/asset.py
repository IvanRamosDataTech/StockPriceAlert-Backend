from ..persistance.db_manager import db
from .asset_watchlist import watchlist_asset

class Asset(db.Model):

    __tablename__ = 'asset'

    ticker = db.Column(db.String(10), nullable=False, primary_key=True)
    displayed_name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    price_change = db.Column(db.Float, nullable=True)
    price_change_percent = db.Column(db.Float, nullable=True)
    min_month_price = db.Column(db.Float, nullable=True)
    alerts = db.relationship('Alert', back_populates='asset', cascade='all, delete-orphan')
    watchlists = db.relationship('Watchlist', secondary=watchlist_asset, back_populates='assets')