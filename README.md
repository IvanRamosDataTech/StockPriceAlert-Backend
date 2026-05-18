# StockPriceAlertPoC

Developed in Python to leverage yfinance library and ecosystem of finantial libraries.

## Development server

To make localhost flask web app to communicate with external services like Telegram, you need to connect to 
ngrok reverse proxy 
> ngrok http 127.0.0.1:5000 --url https://preverbal-ileen-overtimorously.ngrok-free.dev


## Telegram bot
Webhook url must follow this format:
https://{your-host}/telegram/