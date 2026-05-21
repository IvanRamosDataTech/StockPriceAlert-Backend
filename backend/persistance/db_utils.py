# !! Load script funcions using >flask shell app context only.
# > from backend.persistance.db_utils import *

# ##Demo functions to show how to interact with the database, you can run these functions in the flask shell to see how they work.
from backend.models.asset import Asset
from backend.models.alert import Alert, ALERT_TYPE_MONTH_LOW, ALERT_TYPE_PRICE_BELOW, ALERT_TYPE_PRICE_ABOVE
from backend.models.watchlist import Watchlist
from backend.persistance.db_manager import db
from backend.utils.time_utils import now_cts_time


def populate_database():
    # Add some assets for testing
    # spym = Asset(ticker="SPYM", price=0.00, previous_price=0.00, displayed_name="SPDR S&P 500 ETF Trust", price_change=0.0, price_change_percent=0.0, min_month_price=0.00)
    # vgk = Asset(ticker="VGK", price=0.00, previous_price=0.00, displayed_name="Vanguard FTSE Europe ETF", price_change=0.0, price_change_percent=0.0, min_month_price=0.00) 
    # vwo = Asset(ticker="VWO", price=0.00, previous_price=0.00, displayed_name="Vanguard FTSE Emerging Markets ETF", price_change=0.0, price_change_percent=0.0, min_month_price=0.00)   
    # vapu = Asset(ticker="VAPU.L", price=0.00, previous_price=0.00, displayed_name="Vanguard FTSE All-World ex-US ETF", price_change=0.0, price_change_percent=0.0, min_month_price=0.00)    
    
    # Add some alerts for testing
    # spym_alert = Alert(asset_ticker="SPYM", alert_type=ALERT_TYPE_MONTH_LOW)
    # vgk_alert = Alert(asset_ticker="VGK", alert_type=ALERT_TYPE_MONTH_LOW)
    # vwo_alert = Alert(asset_ticker="VWO", alert_type=ALERT_TYPE_MONTH_LOW)
    # vapu_alert = Alert(asset_ticker="VAPU.L", alert_type=ALERT_TYPE_MONTH_LOW)


    # db.session.add_all([spym])
    # db.session.add_all([spym_alert])

    # Add some watchlists for testing
    # indexed_list = Watchlist(name="Indexed ETFs")

    # indexed_list.assets.append(spym)
    # indexed_list.assets.append(vgk)
    # indexed_list.assets.append(vwo)
    # indexed_list.assets.append(vapu)
    # if trade_desk:
    #     indexed_list.assets.append(trade_desk)
    
    # long_strategy = Watchlist(name="Long term holds")
    # ihya = Asset.query.filter_by(ticker="IHYA.L").first()
    # robo = Asset.query.filter_by(ticker="ROBO").first()
    # if robo:
    #     long_strategy.assets.append(robo)
    # if ihya:
    #     long_strategy.assets.append(ihya)

    # alternatives = Watchlist(name="Alternatives")
    # alternatives.assets.append(microstrategy)

    # db.session.add(indexed_list)
    # db.session.add(long_strategy)
    # db.session.add(alternatives)
    
    db.session.commit()

def update_asset(ticker, new_price, historical_prices=None):
    
    asset = Asset.query.filter_by(ticker=ticker).first()

    if asset:
        asset.previous_price = asset.price
        asset.price = new_price
        asset.price_change = asset.price - asset.previous_price
        asset.price_change_percent = (asset.price_change / asset.previous_price) * 100 if asset.previous_price else 0.0
        asset.updated_at = now_cts_time()
        if historical_prices:
            asset.min_month_price = historical_prices.get("min_month_price", asset.min_month_price)
            asset.max_month_price = historical_prices.get("max_month_price", asset.max_month_price)
            asset.avg_month_price = historical_prices.get("avg_month_price", asset.avg_month_price)


        db.session.commit()
    else:
        print(f"No asset found with ticker: {ticker}")


def delete_asset(ticker):  
    asset = Asset.query.filter_by(ticker=ticker).first()
    if asset:
        db.session.delete(asset)
        db.session.commit()
    else:
        print(f"No asset found with ticker: {ticker}")

def delete_all_assets():
    Asset.query.all().delete()
    db.session.commit()

def is_db_empty():
    return Asset.query.count() == 0 and Alert.query.count() == 0 and Watchlist.query.count() == 0

def clean_database():
    db.session.query(Watchlist).delete()
    db.session.query(Asset).delete()
    db.session.query(Alert).delete()
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