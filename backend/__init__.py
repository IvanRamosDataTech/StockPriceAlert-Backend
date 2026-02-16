from flask import Flask
from backend.persistance.db_manager import db, init_db
from backend.routes.general import general_blueprint
from backend.routes.prices import price_blueprint
import logging

print("Loading backend package ...")

def create_app():
    flask_app = Flask(__name__)
    # Change to logging.DEBUG for more verbose output during development
    logging.basicConfig(level=logging.INFO)
    flask_app.config.from_prefixed_env() # Load configuration from environment variables with "FLASK_" prefix

    init_db(flask_app) # Initialize database with Flask app context

    # Hook up blueprints
    flask_app.register_blueprint(general_blueprint)
    flask_app.register_blueprint(price_blueprint)
    
    return flask_app
    
