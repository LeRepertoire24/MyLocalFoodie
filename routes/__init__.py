"""
__init__.py for routes/

This module registers all application route blueprints with the Flask app.
It imports and registers blueprints from submodules (currently the search routes).

Usage:
    from routes import register_routes
    register_routes(app)
"""

import logging
from flask import Flask

def register_routes(app: Flask) -> None:
    """
    Registers all route blueprints with the provided Flask application.

    This function imports and registers blueprints from all route modules.
    Currently included:
      - Search routes (from routes/search/__init__.py)

    Args:
        app (Flask): The Flask application instance.

    Raises:
        ImportError: If a blueprint module cannot be imported.
        Exception: If an error occurs during blueprint registration.
    """
    try:
        from .search import register_search_routes
    except ImportError as imp_err:
        logging.error(f"Error importing search routes: {imp_err}")
        raise

    try:
        register_search_routes(app)
        logging.info("Search routes registered successfully.")
    except Exception as reg_err:
        logging.error(f"Error registering search routes: {reg_err}")
        raise

    logging.info("All routes registered successfully.")

