# from persistance.db_manager import db
# from ..models import *

# # ##Demo functions to show how to interact with the database, you can run these functions in the flask shell to see how they work.
# def populate_database():
#     # Add some assets for testing
#     apple = Asset(ticker="AAPL", price=150.00, display_name="Apple Inc.", price_change=1.5, price_change_percent=1.0, min_month_price=140.00)
#     amazon = Asset(ticker="AMZN", price=3305.00, display_name="Amazon.com Inc.", price_change=-10.0, price_change_percent=-0.3, min_month_price=3200.00)
#     chevron = Asset(ticker="CVX", price=98.20, display_name="Chevron Corporation", price_change=0.5, price_change_percent=0.5, min_month_price=95.00)
#     robo = Asset(ticker="ROBO", price=123.69, display_name="ROBO Global Robotics and Automation Index ETF", price_change=-2.0, price_change_percent=-1.6, min_month_price=120.00)
#     ihya = Asset(ticker="IHYA", price=45.67, display_name="iShares iBoxx $ High Yield Corporate Bond ETF", price_change=-0.2, price_change_percent=-0.4, min_month_price=44.00)

#     # Add some alerts for testing
#     apple_alert = Alert(ticker="AAPL", price_threshold=129.00, alert_type="fall below")
#     chevron_alert = Alert(ticker="CVX", price_threshold=175.00, alert_type="rise above")
#     chevron_alert2 = Alert(ticker="CVX", price_threshold=200.00, alert_type="rise above")
#     ihya_alert = Alert(ticker="IHYA", price_threshold=44.9, alert_type="fall below")
#     robo_alert = Alert(ticker="ROBO", price_threshold=None, alert_type="month low")
#     robo_alert_2 = Alert(ticker="ROBO", price_threshold=115.00, alert_type="fall below")
#     robo_alert_3 = Alert(ticker="ROBO", price_threshold=90.00, alert_type="fall below")
    
#     db.session.add_all([apple, amazon, chevron, robo, ihya])
#     db.session.add_all([apple_alert, chevron_alert, chevron_alert2, ihya_alert, robo_alert, robo_alert_2, robo_alert_3])

#     # Add some watchlists for testing
#     hot_strategy = Watchlist(name="Hot stocks")
#     apple = Asset.query.filter_by(ticker="AAPL").first()
#     amazon = Asset.query.filter_by(ticker="AMZN").first()
#     chevron = Asset.query.filter_by(ticker="CVX").first()

#     if apple:
#         hot_strategy.assets.append(apple)
#     if amazon:
#         hot_strategy.assets.append(amazon)
#     if chevron:
#         hot_strategy.assets.append(chevron)
    
#     long_strategy = Watchlist(name="Long term holds")
#     ihya = Asset.query.filter_by(ticker="IHYA").first()
#     robo = Asset.query.filter_by(ticker="ROBO").first()
#     if robo:
#         long_strategy.assets.append(robo)
#     if ihya:
#         long_strategy.assets.append(ihya)
#     long_strategy.assets.append(chevron)

#     db.session.add(hot_strategy)
#     db.session.add(long_strategy)
    
#     db.session.commit()

# if __name__ == "__main__":
#     populate_database()

# def update_assets():
#     apple = Asset.query.filter_by(ticker="AAPL").first()
#     robo = Asset.query.filter_by(ticker="ROBO").first()
#     if apple:
#         apple.price = 155.00
#         db.session.commit()

#     if robo:
#         robo.price = 118.43
#         db.session.commit()


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

# def clean_database():
#     db.session.query(Alert).delete()
#     db.session.query(Asset).delete()
#     db.session.commit()
        
# def query_all_assets():
#     assets = Asset.query.all()
#     for asset in assets:
#         print(f"Ticker: {asset.ticker}, Price: {asset.price}, Market Cap: {asset.market_cap}, Type: {asset.asset_type}")
#         for alert in asset.alerts:
#             print(f"  Alert ID: {alert.id}, Threshold: {alert.price_threshold}, Type: {alert.alert_type}, Min Month Price: {alert.min_month_price}")    
#         for list in asset.watchlists:
#             print(f"  Watchlist: {list.name}")

# def query_asset(ticker):
#     asset = Asset.query.filter_by(ticker=ticker).first()
#     if asset:
#         print(f"Ticker: {asset.ticker}, Price: {asset.price}, Market Cap: {asset.market_cap}, Type: {asset.asset_type}")
#         for alert in asset.alerts:
#             print(f"  Alert ID: {alert.id}, Threshold: {alert.price_threshold}, Type: {alert.alert_type}, Min Month Price: {alert.min_month_price}")    
#         for list in asset.watchlists:
#             print(f"  Watchlist: {list.name}")     
#     else:
#         print(f"No asset found with ticker: {ticker}")

# def query_watchlist(name):
#     watchlist = Watchlist.query.filter_by(name=name).first()
#     if watchlist:
#         print(f"Watchlist: {watchlist.name}")
#         for asset in watchlist.assets:
#             print(f"  Asset Ticker: {asset.ticker}, Price: {asset.price}, Market Cap: {asset.market_cap}, Type: {asset.asset_type}")
#     else:
#         print(f"No watchlist found with name: {name}")
