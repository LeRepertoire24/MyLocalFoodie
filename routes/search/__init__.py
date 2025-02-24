"""
__init__.py for routes/search/

This module registers all search-related blueprints with the Flask application.
It imports blueprints from the following modules:
  - allergens_routes.py (exposing `allergens_bp`)
  - recipe_routes.py (exposing `recipe_search`)
  - product_routes.py (exposing `products`)

Usage:
    from routes.search import register_search_routes
    register_search_routes(app)
"""

import logging
from flask import Flask

def register_search_routes(app: Flask) -> None:
    """
    Registers search-related blueprints with the provided Flask application.

    Blueprints imported and registered:
        - allergens_bp: Handles endpoints related to allergen searches.
        - recipe_search: Manages endpoints for recipe searches.
        - products: Provides endpoints for product searches.

    Args:
        app (Flask): The Flask application instance.

    Raises:
        ImportError: If any blueprint module cannot be imported.
        Exception: If an error occurs during blueprint registration.
    """
    try:
        from .allergens_routes import allergens_bp  # Expected blueprint for allergens
        from .recipe_routes import recipe_search     # Blueprint for recipe search
        from .product_routes import products          # Blueprint for product routes
    except ImportError as imp_err:
        logging.error(f"Error importing search routes blueprints: {imp_err}")
        raise

    try:
        app.register_blueprint(allergens_bp)
        app.register_blueprint(recipe_search)
        app.register_blueprint(products)
        logging.info("Search routes blueprints registered successfully.")
    except Exception as reg_err:
        logging.error(f"Error registering search routes blueprints: {reg_err}")
        raise
