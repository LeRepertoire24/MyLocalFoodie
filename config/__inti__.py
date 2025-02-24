"""
Configuration package for MyLocalFoodie application.

This package consolidates application configurations and credentials from the following modules:
  - base_config.py: Provides the production/staging configuration via the Config class.
  - google_oauth_config.py: Contains Google OAuth settings via the GoogleOAuthConfig class,
    along with a custom exception class GoogleOAuthConfigError.
  - test_config.py: Defines the TestConfig class for testing purposes.

Usage:
    from config import Config, GoogleOAuthConfig, GoogleOAuthConfigError, TestConfig
"""

import logging

from .base_config import Config
from .google_oauth_config import GoogleOAuthConfig, GoogleOAuthConfigError
from .test_config import TestConfig

logging.getLogger(__name__).info("Configuration module loaded successfully.")

__all__ = [
    "Config",
    "GoogleOAuthConfig",
    "GoogleOAuthConfigError",
    "TestConfig"
]

