## Definir los requerimientos inciales de Stock Alarm.

Requerimientos
---

Functionality

Search. As user, I expect simple but functional search capabilities to find out assets.

I want a search bar that gives me a list of assets according to the entered text

I want search results to drop down as I enter and update results as I keep typing

Search Results To be automatically filtered by available in BMV

I want to see Ticker, asset name,  market and Asset type in each of the results

* I want search results to change as I delete a letter in the search bar (Optional)

*I want to see TER when applicable in the search result (Optional)

*I want to see Volume in BMV (Optional)

 

Watchlists. As user, I want to keep an eye on a list of assets of my interest.

I can add assets to my watchlist by clicking on the search result.

My items in watchlist must show Ticker, Name, price in origin market,  change in price and change in %.

App calculates Fair prices in MXN automatically by multiplying origin market price by current USD MXN exchange.

If I click on an item in the watchlist, then center chart is updated and shows price graphics in the chart panel and shows associated alerts in the alert panel

I have a trash button at the edge right of the item in case I want to delete it from my watchlist

If I click trash button, it’s going to show me an alaert message to confirm deletion

Once item is deleted from watch list, then all associated alerts get deleted as well

I have a button with a campana left next to the trash button. This icon shows up if there are at least 1 alarm associated with this asset and shows a count number of alerts setup.

 

 

 

Alerts

If  I click on watchlist item, then it populates Alarm Panel

As user I want to define an alert by minimum Monthly price. This alert triggers when assets reaches a new minimum price in a 30 day trailing window.

As user I want to define an alert by price target fall below a certain price.

As user, I want to get notified via Telegram once an alert gets trigger.

 

Dashboard UI

Price Chart Panel

Loads prices of last 30 days by default.

Shows Asset name at top left

As user, I can change price chart window by 1 month, 3 months and 1 year.

Shows  price in origin market, open, low, high , close at the top right of chart

I can follow along with my mouse in the timeline and above values change accordingly

Statistics Panel

This panel is allocated below Chart panel

Statistics Panels shows difference in price and % and fair price in MXN,

Watchlist Panel

 

Alarm Panel

By default is grayed out if no asset is selected.

Panel gets activated once user selects a watchlist item.\

If Panel is active and watchlist item has alerts, then it loads all alarms set for such asset

If panel is activated, then itshows by default a big blue button “Set your alert for [TICKER]” as last item in the alert list

 

Alarm Setup Panel

If user taps on Set Alert button, then it pops up a dialog with available alerts. (minimum monthly price and price target fall for POC)

When user taps on Monthly Minimum Price, Then an alarm of this type is set to the asset, app closes dialog and shows newly alarm in the Alarm Panel

When user taps on Price Target Fall, then dialog loads a second screen with lower limit price edit text box and a note text box.

Price Target Fall second screen shows two buttons at bottom: Back and Setup

When Back is touched, then it goes back to the Select alarms dialog

When Setup is touched, then app closes dialog and shows newly alarm in the Alarm Panel.

Setup Panel has a cross top right button that once is touched, app closes dialog

 

Notifications Channels. As user, I want to get notified somehow when one of my assets reach target price or reach minimum price within a month so I can take action and act accordingly.

 

Telegram

As User, I want a dedicated bot I can subscribe to in order to get custom notifications for my stock alerts.

Once an alert fulfills parameters, the app addresses a custom message to Subscribers With following information: Stock Ticker, Stock Name, Name of alert fulfilled, current price in origin market, fair price in BMV

As subscribed user to the Telegram Bot, I want a command that retrieves my watchlist. Each row contains Ticker, Asset name, current price in origin market and change in price /change %

As subscribed user, I want a command that gives me statistics of a given stock within my watchlist

 

 

Feature and Technical Restrictions

Limit price pooling as much as possible as we only have 250 calls per day (probably we want to liimit pooling to trading hours in BMV Mex time from 8:00 am to 2:00 pm) and from Monday to Friday

Email (This is out of scope for PoC)

Native App Push notification (This is out of scope for PoC)

Call (This is out of scope for PoC)

Authentication (This is out of scope for PoC)

Connection to a Database server instance mongoDB, Postgresql (This is out of scope for PoC as it adds friction to the development and testing) Instead, we are going to use better sqlite3 lib