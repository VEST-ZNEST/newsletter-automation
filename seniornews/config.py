import os
from pathlib import Path

basedir = Path(__file__).parent

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database
    # Handle Render PostgreSQL connection string
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or f'sqlite:///{basedir / "app.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mailchimp
   #MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY')
    #MAILCHIMP_LIST_ID = os.environ.get('MAILCHIMP_LIST_ID')
    #MAILCHIMP_REPLY_TO = os.environ.get('MAILCHIMP_REPLY_TO', 'your-email@example.com')
