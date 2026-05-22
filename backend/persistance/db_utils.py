# !! Load script funcions using >flask shell app context only.
# > from backend.persistance.db_utils import *

# ##Demo functions to show how to interact with the database, you can run these functions in the flask shell to see how they work.
from backend.models.asset import Asset
from backend.models.alert import Alert, ALERT_TYPE_MONTH_LOW, ALERT_TYPE_PRICE_BELOW, ALERT_TYPE_PRICE_ABOVE
from backend.models.watchlist import Watchlist
from backend.persistance.db_manager import db
from backend.utils.time_utils import now_cts_time

def populate_database():
    spym = Asset(ticker="SPYM", price=0.00, previous_price=0.00, displayed_name="SPDR Portfolio S&P 500 Growth ETF")
    vgk = Asset(ticker="VGK", price=0.00, previous_price=0.00, displayed_name="Vanguard FTSE Europe ETF")
    vwo = Asset(ticker="VWO", price=0.00, previous_price=0.00, displayed_name="Vanguard FTSE Emerging Markets ETF")
    vapu = Asset(ticker="VAPU.L", price=0.00, previous_price=0.00, displayed_name="Vanguard FTSE Developed Asia ex Japan ETF")
    indexed_strategy = Watchlist(name="Indexed")
    indexed_strategy.assets.extend([spym, vgk, vwo, vapu])
    db.session.add_all([spym, vgk, vwo, vapu, indexed_strategy])

    cbu7 = Asset(ticker="CBU7.L", price=0.00, previous_price=0.00, displayed_name="iShares USD TRSRY ETF")
    ihya = Asset(ticker="IHYA.L", price=0.00, previous_price=0.00, displayed_name="iShares iBoxx $ High Yield Corporate Bond ETF")
    jpea = Asset(ticker="JPEA.L", price=0.00, previous_price=0.00, displayed_name="iShares J.P. Morgan $ EM Corp Bond ETF")
    vdca = Asset(ticker="VDCA.L", price=0.00, previous_price=0.00, displayed_name="Vanguard USD Short-Term Corporate Bond ETF")
    vdst = Asset(ticker="VDST.L", price=0.00, previous_price=0.00, displayed_name="Vanguard Short-Term Treasury Bond ETF")
    bonds_strategy = Watchlist(name="Bonds")
    bonds_strategy.assets.extend([cbu7, ihya, jpea, vdca, vdst])
    db.session.add_all([cbu7, ihya, jpea, vdca, vdst, bonds_strategy])

    aged = Asset(ticker="AGED.L", price=0.00, previous_price=0.00, displayed_name="iShares Ageing Population UCITS ETF")
    fragua = Asset(ticker="FRAGUAB.MX", price=0.00, previous_price=0.00, displayed_name="Grupo Fragua SAB de CV")
    se = Asset(ticker="SE", price=0.00, previous_price=0.00, displayed_name="Sea Limited")
    patrimonial = Watchlist(name="Patrimonial")
    patrimonial.assets.extend([aged, fragua, se])
    db.session.add_all([aged, fragua, se, patrimonial])

    ewc = Asset(ticker="EWC", price=0.00, previous_price=0.00, displayed_name="iShares MSCI Canada ETF")
    ewz = Asset(ticker="EWZ", price=0.00, previous_price=0.00, displayed_name="iShares MSCI Brazil ETF")
    inda = Asset(ticker="INDA", price=0.00, previous_price=0.00, displayed_name="iShares MSCI India ETF")
    mchi = Asset(ticker="MCHI", price=0.00, previous_price=0.00, displayed_name="iShares MSCI China ETF")
    naftrac = Asset(ticker="NAFTRACISHRS.MX", price=0.00, previous_price=0.00, displayed_name="Nacional Financiera MX")
    satelites = Watchlist(name="Satelites")
    satelites.assets.extend([ewc, ewz, inda, mchi, naftrac])
    db.session.add_all([ewc, ewz, inda, mchi, naftrac, satelites])

    bitcoin = Asset(ticker="BTC-USD", price=0.00, previous_price=0.00, displayed_name="Bitcoin USD")
    gold = Asset(ticker="GC=F", price=0.00, previous_price=0.00, displayed_name="Gold Futures")
    mxn = Asset(ticker="MXN=X", price=0.00, previous_price=0.00, displayed_name="USD/MXN Exchange Rate")
    exchanges = Watchlist(name="Exchanges")
    exchanges.assets.extend([bitcoin, gold, mxn])
    db.session.add_all([bitcoin, gold, mxn, exchanges])

    # By default , MonthMinimum alerts to indexed assets
    spym_alert = Alert(ticker="SPYM", alert_type=ALERT_TYPE_MONTH_LOW)
    vgk_alert = Alert(ticker="VGK", alert_type=ALERT_TYPE_MONTH_LOW)
    vwo_alert = Alert(ticker="VWO", alert_type=ALERT_TYPE_MONTH_LOW)
    vapu_alert = Alert(ticker="VAPU.L", alert_type=ALERT_TYPE_MONTH_LOW)
    db.session.add_all([spym_alert, vgk_alert, vwo_alert, vapu_alert])

    ewc_alert = Alert(ticker="EWC", alert_type=ALERT_TYPE_MONTH_LOW)
    ewz_alert = Alert(ticker="EWZ", alert_type=ALERT_TYPE_MONTH_LOW)
    inda_alert = Alert(ticker="INDA", alert_type=ALERT_TYPE_MONTH_LOW)
    mchi_alert = Alert(ticker="MCHI", alert_type=ALERT_TYPE_MONTH_LOW)
    naftrac_alert = Alert(ticker="NAFTRACISHRS.MX", alert_type=ALERT_TYPE_MONTH_LOW)
    db.session.add_all([ewc_alert, ewz_alert, inda_alert, mchi_alert, naftrac_alert])

    db.session.commit()
    

def populate_test_database():
    # Add some assets for testing
    apple = Asset(ticker="AAPL", price=150.00, previous_price=150.00, displayed_name="Apple Inc.")
    amazon = Asset(ticker="AMZN", price=3305.00, previous_price=3305.00, displayed_name="Amazon.com Inc.")
    chevron = Asset(ticker="CVX", price=98.20, previous_price=98.20, displayed_name="Chevron Corporation", price_change=0.5, price_change_percent=0.5, min_month_price=95.00)
    robo = Asset(ticker="ROBO", price=123.69, previous_price=123.69, displayed_name="ROBO Global Robotics and Automation Index ETF", price_change=-2.0, price_change_percent=-1.6, min_month_price=120.00)
    ihya = Asset(ticker="IHYA.L", price=45.67, previous_price=45.67, displayed_name="iShares iBoxx $ High Yield Corporate Bond ETF", price_change=-0.2, price_change_percent=-0.4, min_month_price=44.00)
    trade_desk = Asset(ticker="TTD", price=85.00, previous_price=85.00, displayed_name="The Trade Desk Inc.", price_change=1.0, price_change_percent=1.2, min_month_price=80.00)
    microstrategy = Asset(ticker="MSTR", price=250.00, previous_price=250.00, displayed_name="MicroStrategy Incorporated", price_change=-5.0, price_change_percent=-2.0, min_month_price=240.00)

    # Add some alerts for testing
    apple_alert = Alert(ticker="AAPL", price_threshold=129.00, alert_type=ALERT_TYPE_PRICE_BELOW)
    chevron_alert = Alert(ticker="CVX", price_threshold=175.00, alert_type=ALERT_TYPE_PRICE_ABOVE)
    chevron_alert2 = Alert(ticker="CVX", price_threshold=200.00, alert_type=ALERT_TYPE_PRICE_ABOVE)
    ihya_alert = Alert(ticker="IHYA.L", price_threshold=44.9, alert_type=ALERT_TYPE_PRICE_BELOW)
    robo_alert = Alert(ticker="ROBO", price_threshold=None, alert_type=ALERT_TYPE_MONTH_LOW)
    robo_alert_2 = Alert(ticker="ROBO", price_threshold=115.00, alert_type=ALERT_TYPE_PRICE_BELOW)
    robo_alert_3 = Alert(ticker="ROBO", price_threshold=90.00, alert_type=ALERT_TYPE_PRICE_BELOW)
    mstr_alert = Alert(ticker="MSTR", price_threshold=None, alert_type=ALERT_TYPE_MONTH_LOW)

    db.session.add_all([apple, amazon, chevron, robo, ihya, trade_desk, microstrategy])
    db.session.add_all([apple_alert, chevron_alert, chevron_alert2, ihya_alert, robo_alert, robo_alert_2, robo_alert_3, mstr_alert])

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
    if microstrategy:
        hot_strategy.assets.append(microstrategy)
    if trade_desk:
        hot_strategy.assets.append(trade_desk)
    
    long_strategy = Watchlist(name="Long term holds")
    ihya = Asset.query.filter_by(ticker="IHYA.L").first()
    robo = Asset.query.filter_by(ticker="ROBO").first()
    if robo:
        long_strategy.assets.append(robo)
    if ihya:
        long_strategy.assets.append(ihya)

    alternatives = Watchlist(name="Alternatives")
    alternatives.assets.append(microstrategy)

    db.session.add(hot_strategy)
    db.session.add(long_strategy)
    db.session.add(alternatives)
    
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