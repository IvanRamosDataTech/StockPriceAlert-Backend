from ..persistance.db_manager import db

class Alert(db.Model):

    __tablename__ = 'alert'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.ForeignKey('asset.ticker'), nullable=False)
    asset = db.relationship('Asset', back_populates='alerts')
    alert_type = db.Column(db.String(20), nullable=False)  #  month low, fall below, rise above"
    price_threshold = db.Column(db.Float, nullable=True)

    def __str__(self):
        info = f"<Alert {self.id} - {self.alert_type}  {self.price_threshold} for {self.ticker}>"
        
        return info