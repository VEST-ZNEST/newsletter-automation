import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Log important configuration for debugging
    app.logger.info(f"Starting application with DATABASE_URL: {app.config.get('SQLALCHEMY_DATABASE_URI')[:20]}...")
    app.logger.info(f"NEWSAPI_KEY configured: {'Yes' if os.environ.get('NEWSAPI_KEY') else 'No'}")

    # Enable CORS for development with full access
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True
        }
    })

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
