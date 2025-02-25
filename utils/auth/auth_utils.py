import re
from flask import current_app
from extensions import bcrypt  # Direct import from root-level extensions.py

def validate_payroll_id(payroll_id: str) -> bool:
    """
    Validate payroll ID format:
    Must be of the form: D{work_area_letter}-XXXXXX
    where:
      - 'D' stands for Department.
      - {work_area_letter} is one of:
          A (admin), B (bar), C (cleaners), F (functions),
          G (guest services), H (house keeping), K (kitchen),
          M (maintenance), O (operations), R (restaurant),
          S (store room), V (venue)
      - 'XXXXXX' are exactly six digits.
    
    Examples:
      - DA-123456
      - DR-654321
    """
    pattern = r"^D[ABCFGHKMORSV]-\d{6}$"
    return bool(re.match(pattern, payroll_id))

def hash_password(plain_text_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Returns:
        A string containing the hashed password.
    """
    return bcrypt.generate_password_hash(
        plain_text_password,
        rounds=current_app.config["BCRYPT_LOG_ROUNDS"]
    ).decode("utf-8")

def check_password(hashed_password: str, plain_text_password: str) -> bool:
    """
    Verify a plaintext password against the stored hash.
    
    Args:
        hashed_password: The hashed password from the database.
        plain_text_password: The plaintext password to verify.
    
    Returns:
        True if the password matches, False otherwise.
    """
    return bcrypt.check_password_hash(hashed_password, plain_text_password)
