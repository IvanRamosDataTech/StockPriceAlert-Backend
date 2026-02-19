# !! Load script funcions using >flask shell app context only.
# > from backend.persistance.db_utils import *

# ##Demo functions to show how to interact with the database, you can run these functions in the flask shell to see how they work.
from backend.models.asset import Asset
from backend.models.alert import Alert
from backend.models.watchlist import Watchlist
from backend.persistance.db_manager import db

def populate_database():
    # Add some assets for testing
    apple = Asset(ticker="AAPL", price=150.00, displayed_name="Apple Inc.")
    amazon = Asset(ticker="AMZN", price=3305.00, displayed_name="Amazon.com Inc.")
    chevron = Asset(ticker="CVX", price=98.20, displayed_name="Chevron Corporation", price_change=0.5, price_change_percent=0.5, min_month_price=95.00)
    robo = Asset(ticker="ROBO", price=123.69, displayed_name="ROBO Global Robotics and Automation Index ETF", price_change=-2.0, price_change_percent=-1.6, min_month_price=120.00)
    ihya = Asset(ticker="IHYA", price=45.67, displayed_name="iShares iBoxx $ High Yield Corporate Bond ETF", price_change=-0.2, price_change_percent=-0.4, min_month_price=44.00)

    # Add some alerts for testing
    apple_alert = Alert(ticker="AAPL", price_threshold=129.00, alert_type="fall below")
    chevron_alert = Alert(ticker="CVX", price_threshold=175.00, alert_type="rise above")
    chevron_alert2 = Alert(ticker="CVX", price_threshold=200.00, alert_type="rise above")
    ihya_alert = Alert(ticker="IHYA", price_threshold=44.9, alert_type="fall below")
    robo_alert = Alert(ticker="ROBO", price_threshold=None, alert_type="month low")
    robo_alert_2 = Alert(ticker="ROBO", price_threshold=115.00, alert_type="fall below")
    robo_alert_3 = Alert(ticker="ROBO", price_threshold=90.00, alert_type="fall below")
    
    db.session.add_all([apple, amazon, chevron, robo, ihya])
    db.session.add_all([apple_alert, chevron_alert, chevron_alert2, ihya_alert, robo_alert, robo_alert_2, robo_alert_3])

    # Add some watchlists for testing
    hot_strategy = Watchlist(name="Hot stocks")
    apple = Asset.query.filter_by(ticker="AAPL").first()
    amazon = Asset.query.filter_by(ticker="AMZN").first()
    chevron = Asset.query.filter_by(ticker="CVX").first()

    if apple:
        hot_strategy.assets.append(apple)
    if amazon:
        hot_strategy.assets.append(amazon)
    if chevron:
        hot_strategy.assets.append(chevron)
    
    long_strategy = Watchlist(name="Long term holds")
    ihya = Asset.query.filter_by(ticker="IHYA").first()
    robo = Asset.query.filter_by(ticker="ROBO").first()
    if robo:
        long_strategy.assets.append(robo)
    if ihya:
        long_strategy.assets.append(ihya)
    

    db.session.add(hot_strategy)
    db.session.add(long_strategy)
    
    db.session.commit()

def update_asset(ticker, new_price, historical_prices=None):
    
    asset = Asset.query.filter_by(ticker=ticker).first()

    if asset:
        asset.previous_price = asset.price
        asset.price = new_price
        asset.price_change = asset.price - asset.previous_price
        asset.price_change_percent = (asset.price_change / asset.previous_price) * 100 if asset.previous_price else 0.0
        asset.updated_at = db.func.current_timestamp()
        if historical_prices:
            asset.min_month_price = historical_prices.get("min_month_price", asset.min_month_price)
            asset.max_month_price = historical_prices.get("max_month_price", asset.max_month_price)
            asset.avg_month_price = historical_prices.get("avg_month_price", asset.avg_month_price)


        db.session.commit()
    else:
        print(f"No asset found with ticker: {ticker}")


# def delete_asset(ticker):  
#     asset = Asset.query.filter_by(ticker=ticker).first()
#     if asset:
#         db.session.delete(asset)
#         db.session.commit()
#     else:
#         print(f"No asset found with ticker: {ticker}")

# def delete_all_assets():
#     Asset.query.all().delete()
#     db.session.commit()

def clean_database():
    db.session.query(Watchlist).delete()
    db.session.query(Asset).delete()
    db.session.commit()
        
def query_all_assets():
    assets = Asset.query.all()
    for asset in assets:
        print(asset)

def query_asset(ticker):
    asset = Asset.query.filter_by(ticker=ticker).first()
    if asset:
        print(asset)
    else:
        print(f"No asset found with ticker: {ticker}")

def query_watchlist(name):
    watchlist = Watchlist.query.filter_by(name=name).first()
    if watchlist:
        print(watchlist)
    else:
        print(f"No watchlist found with name: {name}")

if __name__ == "__main__":
    populate_database()