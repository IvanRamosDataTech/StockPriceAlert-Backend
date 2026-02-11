# from database.persistance import db

# watchlist_asset = db.Table('watchlist_asset',
#                             db.Column('watchlist_id', db.ForeignKey('watchlist.id'), primary_key=True),
#                             db.Column('asset_ticker', db.ForeignKey('asset.ticker'), primary_key=True)
#                             )


# class Asset(db.Model):

#     __tablename__ = 'asset'

#     ticker = db.Column(db.String(10), nullable=False, primary_key=True)
#     displayed_name = db.Column(db.String(20), nullable=False)
#     price = db.Column(db.Float, nullable=False)
#     price_change = db.Column(db.Float, nullable=True)
#     price_change_percent = db.Column(db.Float, nullable=True)
#     min_month_price = db.Column(db.Float, nullable=True)
#     alerts = db.relationship('Alert', back_populates='asset', cascade='all, delete-orphan')
#     watchlists = db.relationship('Watchlist', secondary=watchlist_asset, back_populates='assets')


# class Watchlist(db.Model):

#     __tablename__ = 'watchlist'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False, unique=True)
#     assets = db.relationship('Asset', secondary=watchlist_asset, back_populates='watchlists')


# class Alert(db.Model):

#     __tablename__ = 'alert'

#     id = db.Column(db.Integer, primary_key=True)
#     ticker = db.Column(db.ForeignKey('asset.ticker'), nullable=False)
#     asset = db.relationship('Asset', back_populates='alerts')
#     alert_type = db.Column(db.String(20), nullable=False)  #  month low, fall below, rise above"
#     price_threshold = db.Column(db.Float, nullable=True)
    
