from ..persistance.db_manager import db

#supported types of alerts
ALERT_TYPE_MONTH_LOW = "MonthMinimum"
ALERT_TYPE_PRICE_BELOW = "PriceBelow"
ALERT_TYPE_PRICE_ABOVE = "PriceAbove"

class Alert(db.Model):

    __tablename__ = 'alert'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.ForeignKey('asset.ticker'), nullable=False)
    asset = db.relationship('Asset', back_populates='alerts')
    alert_type = db.Column(db.String(20), nullable=False)  #  month low, fall below, rise above"
    price_threshold = db.Column(db.Float, nullable=True)
    last_triggered_at = db.Column(db.DateTime, nullable=True)

    def update_trigger_time(self):
        self.last_triggered_at = db.func.current_timestamp()

    def __str__(self):
        info = f"<Alert {self.id} - {self.alert_type}  {self.price_threshold} for {self.ticker}>"
        
        return info