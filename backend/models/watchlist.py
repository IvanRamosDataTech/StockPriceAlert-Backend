from ..persistance.db_manager import db
from .asset_watchlist import watchlist_asset

class Watchlist(db.Model):

    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    assets = db.relationship('Asset', secondary=watchlist_asset, back_populates='watchlists')

    def name_available(self):
        existing_watchlist = Watchlist.query.filter_by(name=self.name).first()
        return existing_watchlist is None

    def __str__(self):
        info = f"<Watchlist {self.name}>"
        info += "Assets: \n"
        for asset in self.assets:
            info += str(asset.displayed_name) + "; "
        return info
