from flask import Flask

def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_prefixed_env() # Load configuration from environment variables with "FLASK_" prefix
    
    @flask_app.route('/')
    def index():
        return '<H1>Stock Price Alert for long investors Service.</H1>'
    
    return flask_app