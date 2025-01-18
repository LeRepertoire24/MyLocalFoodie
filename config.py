import os
from dotenv import load_dotenv
import warnings

# Load environment variables from .env file
load_dotenv()

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    MONGO_DBNAME = os.getenv('MONGO_DBNAME', 'MyCookBook')

    # MongoDB Collection Names
    COLLECTION_TAGS = os.getenv('COLLECTION_TAGS', 'tags')
    COLLECTION_GLOBAL_RECIPES = os.getenv('COLLECTION_GLOBAL_RECIPES', 'global_recipes')
    COLLECTION_USER_RECIPES = os.getenv('COLLECTION_USER_RECIPES', 'user_recipes')
    COLLECTION_USERS = os.getenv('COLLECTION_USERS', 'users')
    COLLECTION_PRODUCT_LIST = os.getenv('COLLECTION_PRODUCT_LIST', 'product_list')
    COLLECTION_ALLERGENS = os.getenv('COLLECTION_ALLERGENS', 'allergens')
    COLLECTION_USER_NOTES = os.getenv('COLLECTION_USER_NOTES', 'user_notes')

    # Business Onboarding Collections
    COLLECTION_BUSINESSES = os.getenv('COLLECTION_BUSINESSES', 'business_entities')
    COLLECTION_BUSINESS_CONFIG = os.getenv('COLLECTION_BUSINESS_CONFIG', 'business_config')
    COLLECTION_BUSINESS_USERS = os.getenv('COLLECTION_BUSINESS_USERS', 'business_users')
    COLLECTION_BUSINESS_ROLES = os.getenv('COLLECTION_BUSINESS_ROLES', 'business_roles')
    COLLECTION_BUSINESS_PERMISSIONS = os.getenv('COLLECTION_BUSINESS_PERMISSIONS', 'business_permissions')

    # Deprecation Notice for MONGO_SEARCH_DBNAME
    MONGO_SEARCH_DBNAME = os.getenv('MONGO_SEARCH_DBNAME')
    if MONGO_SEARCH_DBNAME:
        warnings.warn(
            "MONGO_SEARCH_DBNAME is deprecated. Use COLLECTION_PRODUCT_LIST instead.",
            DeprecationWarning
        )

    # Application Secrets
    SECRET_KEY = os.getenv('SECRET_KEY', 'a_secure_random_key')

    # Google API Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', '')

    # API Key for Google Keep and other APIs
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

    # File Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')  # Directory where images are stored on disk
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB default
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg').split(',')
    
    # MongoDB GridFS Bucket Configuration
    GRIDFS_BUCKET_NAME = os.getenv('GRIDFS_BUCKET_NAME', 'img')  # Default to 'img' if not provided

    # Business Configuration Defaults
    DEFAULT_BUSINESS_ROLES = {
        'owner': ['all'],
        'manager': ['read', 'write', 'update'],
        'staff': ['read', 'write'],
        'employee': ['read']
    }

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Debug Configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']

    # Business Setup Configuration
    BUSINESS_SETUP_STEPS = [
        'business_info',
        'venue_setup',
        'work_areas',
        'roles_permissions',
        'complete'
    ]

    # Debugging statements for confirmation
    print(f"Loaded Configuration:")
    print(f"- MONGO_URI: {MONGO_URI}")
    print(f"- MONGO_DBNAME: {MONGO_DBNAME}")
    print(f"- COLLECTION_TAGS: {COLLECTION_TAGS}")
    print(f"- COLLECTION_GLOBAL_RECIPES: {COLLECTION_GLOBAL_RECIPES}")
    print(f"- COLLECTION_USER_RECIPES: {COLLECTION_USER_RECIPES}")
    print(f"- COLLECTION_USERS: {COLLECTION_USERS}")
    print(f"- COLLECTION_PRODUCT_LIST: {COLLECTION_PRODUCT_LIST}")
    print(f"- COLLECTION_ALLERGENS: {COLLECTION_ALLERGENS}")
    print(f"- COLLECTION_USER_NOTES: {COLLECTION_USER_NOTES}")
    if MONGO_SEARCH_DBNAME:
        print(f"- MONGO_SEARCH_DBNAME (Deprecated): {MONGO_SEARCH_DBNAME}")

    # Business Collections Debug Output
    print(f"- COLLECTION_BUSINESSES: {COLLECTION_BUSINESSES}")
    print(f"- COLLECTION_BUSINESS_CONFIG: {COLLECTION_BUSINESS_CONFIG}")
    print(f"- COLLECTION_BUSINESS_USERS: {COLLECTION_BUSINESS_USERS}")
    print(f"- COLLECTION_BUSINESS_ROLES: {COLLECTION_BUSINESS_ROLES}")
    print(f"- COLLECTION_BUSINESS_PERMISSIONS: {COLLECTION_BUSINESS_PERMISSIONS}")

    print(f"- SECRET_KEY: {'Set' if SECRET_KEY else 'Not Set'}")
    print(f"- UPLOAD_FOLDER: {UPLOAD_FOLDER}")
    print(f"- MAX_FILE_SIZE: {MAX_FILE_SIZE}")
    print(f"- ALLOWED_EXTENSIONS: {ALLOWED_EXTENSIONS}")
    print(f"- GOOGLE_CLIENT_ID: {'Set' if GOOGLE_CLIENT_ID else 'Not Set'}")
    print(f"- GOOGLE_CLIENT_SECRET: {'Set' if GOOGLE_CLIENT_SECRET else 'Not Set'}")
    print(f"- GOOGLE_REDIRECT_URI: {GOOGLE_REDIRECT_URI}")
    print(f"- GOOGLE_API_KEY: {'Set' if GOOGLE_API_KEY else 'Not Set'}")

    @classmethod
    def init_business_collections(cls, db):
        """Initialize business-related collections with indexes and default data"""
        # Businesses collection indexes
        db[cls.COLLECTION_BUSINESSES].create_index([("business_id", 1)], unique=True)
        db[cls.COLLECTION_BUSINESSES].create_index([("admin_user_id", 1)])
        db[cls.COLLECTION_BUSINESSES].create_index([("venues.venue_id", 1)])
        db[cls.COLLECTION_BUSINESSES].create_index([("venues.work_areas.work_area_id", 1)])

        # Business users collection indexes
        db[cls.COLLECTION_BUSINESS_USERS].create_index([ 
            ("business_id", 1), 
            ("user_id", 1) 
        ], unique=True)

        # Business roles collection indexes
        db[cls.COLLECTION_BUSINESS_ROLES].create_index([ 
            ("business_id", 1), 
            ("role_name", 1) 
        ], unique=True)

        # Insert default roles if they don't exist
        for role_name, permissions in cls.DEFAULT_BUSINESS_ROLES.items():
            db[cls.COLLECTION_BUSINESS_ROLES].update_one(
                {"role_name": role_name},
                {"$setOnInsert": {
                    "role_name": role_name,
                    "permissions": permissions,
                    "is_default": True
                }},
                upsert=True
            )
