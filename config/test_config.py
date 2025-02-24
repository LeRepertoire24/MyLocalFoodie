
# ------------------------------------------------#
#            config/test_config.py                #
# ------------------------------------------------#

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestConfig:
    """Test Configuration"""
    
    # Flask Configuration
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'test_secret_key'
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DBNAME = os.getenv('MONGO_DBNAME')
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    
    # CSRF Protection
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
