import os
import sys
from functools import wraps
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter - use in-memory storage by default for reliability
# In production with Redis, you can pass storage_uri
# For now, we'll use the default in-memory storage which is more reliable
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"]  # Very permissive for development
)

def _is_test_mode():
    """Check if we're running in test mode"""
    # Check for pytest environment variable
    if os.getenv("PYTEST_CURRENT_TEST") is not None:
        return True
    # Check if pytest is in sys.modules (imported)
    if "pytest" in sys.modules:
        return True
    # Check for TESTING environment variable
    if os.getenv("TESTING") == "true":
        return True
    return False

def conditional_limit(limit_string: str):
    """
    Conditionally apply rate limiting - skips in test mode.
    Usage: @conditional_limit("10/minute") instead of @limiter.limit("10/minute")
    """
    def decorator(func):
        # Check if we're in test mode
        if _is_test_mode():
            # In test mode, don't apply rate limiting - just return the function as-is
            return func
        else:
            # In production/development, apply rate limiting
            return limiter.limit(limit_string)(func)
    
    return decorator

