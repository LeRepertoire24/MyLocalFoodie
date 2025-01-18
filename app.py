# ------------------------------------------------------------
# /app.py
# ------------------------------------------------------------
import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory, Response, send_file, g
from pymongo import MongoClient
from flask_cors import CORS
from pymongo.errors import ConnectionFailure
from bson.json_util import dumps
from bson.objectid import ObjectId
from dotenv import load_dotenv
import logging
from flask_wtf.csrf import CSRFProtect
from BunnyCDN.Storage import Storage
from BunnyCDN.CDN import CDN
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO
import gridfs
import json

from utils import (
    lookup_ingredient, 
    lookup_tag, 
    lookup_cuisine, 
    lookup_method, 
    lookup_dietary, 
    lookup_mealtype, 
    timeago
)
from config import Config
from id_service import IDService
from models import get_db, get_search_db

# Initialize logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.info("Environment variables loaded successfully")

# Initialize Flask app
app = Flask(__name__, static_folder="static", static_url_path="/static")

# Initialize CORS
CORS(app)

# Application Configuration
app.config.from_object(Config)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize CSRF protection
csrf = CSRFProtect(app)

CORS(app, resources={r"/*": {"origins": "*"}})

# MongoDB client initialization
try:
    client = MongoClient(Config.MONGO_URI)
    app.config['MONGO_CLIENT'] = client
    db = client[Config.MONGO_DBNAME]  # Database reference

    # Test database connection
    client.admin.command('ping')
    logger.info("MongoDB connection established successfully")
except Exception as e:
    logger.critical(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Initialize GridFS bucket
try:
    fs = gridfs.GridFS(db, collection=Config.GRIDFS_BUCKET_NAME)
    app.config['fs'] = fs  # Make GridFS available globally
    logger.info("GridFS initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize GridFS: {str(e)}")
    raise

# Initialize IDService
try:
    id_service = IDService(db)
    app.config['ID_SERVICE'] = id_service  # Make IDService available globally
    logger.info("ID Service initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize ID Service: {str(e)}")
    raise

# Define a Custom JSON Encoder
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)

# Set the custom JSON encoder
app.json_encoder = JSONEncoder

# Import blueprints
from routes.auth_routes import auth
from routes.allergen_routes import allergens
from routes.home_routes import home
from routes.error_routes import error_routes
from routes.finance_routes import finance
from routes.common_routes import common
from routes.google_routes import google_api
from routes.employment_routes import employment
from routes.product_routes import products
from routes.recipeSearch_routes import recipe_search
from routes.googleTasks_routes import google_tasks
from routes.notes_routes import notes
from modules import module_manager

# Register blueprints
blueprints = [
    (auth, "auth"),
    (allergens, "allergens"),
    (home, "home"),
    (error_routes, "error_routes"),
    (finance, "finance_routes"),
    (common, "common_routes"),
    (employment, "employment_routes"),
    (google_api, "google_routes"),
    (products, "product_routes"),
    (recipe_search, "recipe_search"),
    (google_tasks, "google_tasks_routes"),
    (notes, "notes_routes")
]

for bp, name in blueprints:
    app.register_blueprint(bp)
    logger.info(f"{name} blueprint initialized successfully")

# Initialize modules
try:
    module_manager.init_app(app)
    logger.info("Module system initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize module system: {str(e)}")
    raise
    
@app.after_request
def set_csp_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'https://cdnjs.cloudflare.com' 'https://fonts.googleapis.com'; "
        "font-src 'https://fonts.gstatic.com'; "
        "script-src 'self';"
    )
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/image/<filename>', methods=['GET'])
def get_image(filename):
    try:
        file = fs.find_one({'filename': filename})
        
        if file:
            return send_file(
                BytesIO(file.read()), 
                mimetype=file.content_type or 'image/jpeg',
                download_name=filename
            )
        
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        if os.path.exists(file_path):
            return send_from_directory(Config.UPLOAD_FOLDER, filename)
        
        logger.warning(f"Image not found: {filename}")
        return "Image not found", 404

    except Exception as e:
        logger.error(f"Error fetching image {filename}: {str(e)}")
        return str(e), 500

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    if not file or not allowed_file(file.filename):
        return 'Invalid file type', 400
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{timestamp}_{file.filename}")
        
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        fs.put(
            file, 
            filename=filename, 
            content_type=file.content_type
        )
        
        logger.info(f"File {filename} successfully uploaded to both disk and GridFS")
        return jsonify({
            'status': 'success',
            'message': 'File successfully uploaded',
            'filename': filename
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error uploading file: {str(e)}"
        }), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.errorhandler(404)
def page_not_found(e):
    logger.warning("404 error: Page not found")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 error: {str(e)}")
    return render_template('errors/500.html'), 500

@app.before_request
def before_request():
    g.start_time = datetime.utcnow()
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    g.request_id = id_service.generate_request_id()



@app.teardown_appcontext
def teardown_db(exception):
    if hasattr(g, 'mongo_client'):
        g.mongo_client.close()

def create_app(config_object=None):
    if config_object:
        app.config.from_object(config_object)
    return app

if __name__ == '__main__':
    app = create_app(Config)
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        ssl_context=Config.SSL_CONTEXT if Config.USE_SSL else None
    )
