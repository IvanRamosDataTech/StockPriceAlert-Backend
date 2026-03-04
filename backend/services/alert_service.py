from ..models.alert import Alert, ALERT_TYPE_MONTH_LOW, ALERT_TYPE_PRICE_BELOW, ALERT_TYPE_PRICE_ABOVE
from ..persistance.db_manager import get_db_session
import logging

logger = logging.getLogger(__name__)

### Quick testing in flask shell
# from backend.services.alert_service import AlertService
# AlertService.check_all_alerts()

class AlertService:
    
    """
    Business logic for managing alerts.
    
    """

    @staticmethod
    def check_alert(alert):

        """
        Check if a specific alert condition is met and log the result.
        Contains all supported alerts in system.
        """

        def trigger_alert(alert, message):
            with get_db_session() as session:
                alert.update_trigger_time()
                session.commit()
            
            logger.info(message)
                # Here you would add code to send a notification to the user

        def month_minimum(alert):
            asset = alert.asset
            if asset.price <= asset.min_month_price:
                trigger_alert(alert, f"Month low alert triggered for {asset.ticker}: current price {asset.price} is at or below the monthly low of {asset.min_month_price}")
    
        def price_below(alert):
            asset = alert.asset
            if asset.price <= alert.price_threshold:
                trigger_alert(alert, f"Price below alert triggered for {asset.ticker}: current price {asset.price} is at or below the threshold of {alert.price_threshold}")

        def price_above(alert):
            asset = alert.asset
            if asset.price >= alert.price_threshold:
                trigger_alert(alert, f"Price above alert triggered for {asset.ticker}: current price {asset.price} is at or above the threshold of {alert.price_threshold}")

        if alert.alert_type == ALERT_TYPE_MONTH_LOW:
            month_minimum(alert)
        elif alert.alert_type == ALERT_TYPE_PRICE_BELOW:
            price_below(alert)
        elif alert.alert_type == ALERT_TYPE_PRICE_ABOVE:
            price_above(alert)

    
    @staticmethod
    def check_all_alerts():
        alerts = Alert.query.all()
        for alert in alerts:
            AlertService.check_alert(alert)
