from flask import Flask
from backend.persistance.db_manager import db, init_db

print("Loading backend package ...")

def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_prefixed_env() # Load configuration from environment variables with "FLASK_" prefix
    
    #db.init_app(flask_app)
    init_db(flask_app) # Initialize database with Flask app context

    @flask_app.route('/')
    def index():
        return '<H1>Stock Price Alert for long investors Service.</H1>'
    
    return flask_app