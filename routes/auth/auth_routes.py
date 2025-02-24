# ------------------------------------------------------------
# routes/auth_routes.py
# ------------------------------------------------------------
from flask import Blueprint, request, jsonify, current_app, g, session
from functools import wraps
import bcrypt
import jwt
from datetime import datetime, timedelta
import logging

from utils.validation_utils import validate_request_data
from utils.security_utils import generate_random_string
from utils.google_utils import validate_google_token, get_google_service
from utils.business_utils import lookup_business
from utils.time_utils import generate_timestamp
from utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

# Initialize rate limiter for login attempts
login_limiter = RateLimiter(
    max_attempts=5,
    window_seconds=300,  # 5 minutes
    block_seconds=900    # 15 minutes
)

class AuthError(Exception):
    """Custom exception for authentication errors"""
    def __init__(self, message, status_code=401):
        self.message = message
        self.status_code = status_code

def create_session_token(user):
    """Create a JWT token containing essential user data"""
    try:
        payload = {
            'payroll_id': user['pay_details']['payroll_id'],
            'email_work': user['pay_details']['email_work'],
            'role': user['role'],
            'business_id': user['linked']['business_id'],
            'venue_id': user['linked']['venue_id'],
            'work_area_id': user['work_area_id'],
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow()
        }
        return jwt.encode(
            payload, 
            current_app.config['SECRET_KEY'], 
            algorithm='HS256'
        )
    except Exception as e:
        logger.error(f"Token creation failed: {str(e)}")
        raise AuthError("Failed to create authentication token")

def verify_token(token):
    """Verify and decode JWT token"""
    try:
        return jwt.decode(
            token, 
            current_app.config['SECRET_KEY'], 
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")

def login_required(f):
    """Decorator to protect routes requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                raise AuthError("No authentication token provided")

            token = auth_header.replace('Bearer ', '')
            payload = verify_token(token)
            
            # Verify user still exists and is active
            user = current_app.mongo.db.business_users.find_one({
                "pay_details.payroll_id": payload['payroll_id'],
                "status": {"$ne": "inactive"}
            })
            
            if not user:
                raise AuthError("User account is no longer active")
            
            g.user = payload
            g.current_user = user  # Store full user object for route handlers
            return f(*args, **kwargs)
            
        except AuthError as e:
            return jsonify({
                "success": False,
                "message": e.message
            }), e.status_code
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Authentication failed"
            }), 401
            
    return decorated_function

@auth.route("/auth/login", methods=['POST'])
def login():
    """Handle user login with payroll ID and password"""
    try:
        data = request.get_json()
        payroll_id = data.get('payroll_id')
        password = data.get('password')

        # Validate input
        if not payroll_id or not password:
            return jsonify({
                "success": False,
                "message": "Please provide both payroll ID and password"
            }), 400

        # Check rate limiting
        if login_limiter.is_blocked(payroll_id):
            logger.warning(f"Rate limit exceeded for payroll ID: {payroll_id}")
            return jsonify({
                "success": False,
                "message": "Too many failed attempts. Please try again later."
            }), 429

        # Validate payroll ID format
        if not payroll_id.startswith('USR-') or len(payroll_id) != 12:
            login_limiter.record_attempt(payroll_id, success=False)
            return jsonify({
                "success": False,
                "message": "Invalid payroll ID format"
            }), 400

        # Find user in MongoDB
        user = current_app.mongo.db.business_users.find_one({
            "pay_details.payroll_id": payroll_id,
            "status": {"$ne": "inactive"}
        })

        if not user:
            login_limiter.record_attempt(payroll_id, success=False)
            logger.warning(f"Login attempt with non-existent payroll ID: {payroll_id}")
            return jsonify({
                "success": False,
                "message": "Invalid payroll ID or password"
            }), 401

        # Verify password
        if not bcrypt.checkpw(
            password.encode('utf-8'), 
            user['pay_details']['password'].encode('utf-8')
        ):
            login_limiter.record_attempt(payroll_id, success=False)
            logger.warning(f"Failed login attempt for payroll ID: {payroll_id}")
            return jsonify({
                "success": False,
                "message": "Invalid payroll ID or password"
            }), 401

        # Clear rate limiting on successful login
        login_limiter.clear_attempts(payroll_id)

        # Create session token
        token = create_session_token(user)

        # Update last login timestamp
        current_app.mongo.db.business_users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "last_login": datetime.utcnow()
                }
            }
        )

        # Log successful login
        AuditLogger.log_event(
            'user_login',
            payroll_id,
            user['linked']['business_id'],
            'Successful login',
            ip_address=request.remote_addr
        )

        # Prepare user data for response
        user_data = {
            "payroll_id": user['pay_details']['payroll_id'],
            "email_work": user['pay_details']['email_work'],
            "name_first": user['name_first'],
            "name_preferred": user.get('name_preferred'),
            "role": user['role'],
            "permissions": user['permissions'],
            "linked": {
                "business_id": user['linked']['business_id'],
                "venue_id": user['linked']['venue_id']
            },
            "work_area_id": user['work_area_id']
        }

        return jsonify({
            "success": True,
            "token": token,
            "user": user_data
        })

    except AuthError as e:
        return jsonify({
            "success": False,
            "message": e.message
        }), e.status_code
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred"
        }), 500

@auth.route("/auth/verify-token", methods=['POST'])
def verify_token_route():
    """Verify token validity and return user data"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthError("No token provided")

        token = auth_header.replace('Bearer ', '')
        payload = verify_token(token)

        # Verify user still exists and is active
        user = current_app.mongo.db.business_users.find_one({
            "pay_details.payroll_id": payload['payroll_id'],
            "status": {"$ne": "inactive"}
        })

        if not user:
            raise AuthError("User account is no longer active")

        return jsonify({
            "success": True,
            "valid": True,
            "user": {
                "payroll_id": user['pay_details']['payroll_id'],
                "email_work": user['pay_details']['email_work'],
                "name_first": user['name_first'],
                "name_preferred": user.get('name_preferred'),
                "role": user['role'],
                "permissions": user['permissions']
            }
        })

    except AuthError as e:
        return jsonify({
            "success": False,
            "message": e.message
        }), e.status_code
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Token verification failed"
        }), 401

@auth.route("/auth/logout", methods=['POST'])
@login_required
def logout():
    """Handle user logout with audit logging"""
    try:
        # Log logout event
        AuditLogger.log_event(
            'user_logout',
            g.user['payroll_id'],
            g.user['business_id'],
            'User logged out',
            ip_address=request.remote_addr
        )
        
        # Clear session
        session.clear()
        
        return jsonify({
            "success": True,
            "message": "Successfully logged out"
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Logout failed"
        }), 500

# Error handlers
@auth.errorhandler(AuthError)
def handle_auth_error(error):
    """Handle authentication errors"""
    return jsonify({
        "success": False,
        "message": error.message
    }), error.status_code

@auth.errorhandler(Exception)
def handle_generic_error(error):
    """Handle generic errors"""
    logger.error(f"Unexpected error: {str(error)}")
    return jsonify({
        "success": False,
        "message": "An unexpected error occurred"
    }), 500
