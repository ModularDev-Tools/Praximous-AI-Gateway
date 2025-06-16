# core/security.py
import os
from typing import Set, Optional

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv

from core.logger import log

# Load environment variables from .env file
load_dotenv()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
VALID_API_KEYS: Set[str] = set()

def load_api_keys():
    """Loads API keys from the environment variable."""
    global VALID_API_KEYS
    VALID_API_KEYS.clear() # Clear any existing keys before loading
    keys_str = os.getenv("PRAXIMOUS_API_KEYS", "")
    if keys_str:
        VALID_API_KEYS = {key.strip() for key in keys_str.split(',') if key.strip()}
        if VALID_API_KEYS:
            log.info(f"Loaded {len(VALID_API_KEYS)} API key(s) for endpoint protection.")
        else:
            log.warning("PRAXIMOUS_API_KEYS environment variable is set but contains no valid keys after stripping/splitting.")
    else:
        log.warning("PRAXIMOUS_API_KEYS environment variable not set or empty. API endpoints will be unprotected if this is not intended for development.")

# Load keys when the module is imported
load_api_keys()

async def validate_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Validates the provided API key.
    Raises HTTPException if the key is missing or invalid.
    Returns the API key if valid.
    """
    # If PRAXIMOUS_API_KEYS was not set or empty, VALID_API_KEYS will be empty.
    # In this scenario, for development or specific configurations, we might allow access.
    # However, for a secure default, if keys are configured, one must be provided.
    if not VALID_API_KEYS:
        # If no keys are configured in .env, and we want to allow access (e.g. for local dev without keys)
        # we could return a placeholder or skip validation.
        # For now, let's assume if it's empty, it's an oversight in a secure setup.
        # If you want to allow access when no keys are defined, this logic needs adjustment.
        log.warning("No API keys configured in PRAXIMOUS_API_KEYS. Access is currently open. This might be a security risk.")
        # To enforce keys if the variable is just empty, you might raise an error here or ensure `load_api_keys` logs a critical warning.
        # For now, we'll let it pass if no keys are defined, but this is a point of consideration for security policy.
        return "unprotected_access_no_keys_defined" # Or raise HTTPException(status_code=500, detail="API keys not configured on server")

    if not api_key:
        log.warning("API key missing from request.")
        raise HTTPException(
            status_code=401, # Unauthorized
            detail="Not authenticated: API key is missing."
        )
    if api_key not in VALID_API_KEYS:
        log.warning(f"Invalid API key received: '{api_key[:10]}...'") # Log a snippet for security
        raise HTTPException(
            status_code=403, # Forbidden
            detail="Access denied: Invalid API key."
        )
    log.debug(f"API key validated successfully: '{api_key[:10]}...'")
    return api_key
