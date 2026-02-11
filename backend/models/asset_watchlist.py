from ..persistance.db_manager import db

watchlist_asset = db.Table('watchlist_asset',
                            db.Column('watchlist_id', db.ForeignKey('watchlist.id'), primary_key=True),
                            db.Column('asset_ticker', db.ForeignKey('asset.ticker'), primary_key=True)
                            )
