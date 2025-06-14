# core/license_generator.py
import json
import os
from datetime import datetime, timezone
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

from core.logger import log

# Path for the private key when used by the main application (e.g., for webhook generation)
APP_PRIVATE_KEY_NAME = "praximous_signing_private.pem"
CONFIG_DIR = "config"
DEFAULT_APP_PRIVATE_KEY_PATH = os.path.join(CONFIG_DIR, APP_PRIVATE_KEY_NAME)

def load_private_key(key_path: str) -> rsa.RSAPrivateKey:
    """
    Loads the RSA private key from the specified file path.
    Raises FileNotFoundError if the key is not found.
    """
    if not os.path.exists(key_path):
        log.error(f"Private key file not found at {key_path}.")
        raise FileNotFoundError(f"Private key file not found at {key_path}.")
    try:
        with open(key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None, # Add password handling if your key is encrypted
                backend=default_backend()
            )
        log.info(f"Successfully loaded private key from {key_path}")
        return private_key
    except Exception as e:
        log.error(f"Error loading private key from {key_path}: {e}", exc_info=True)
        raise # Re-raise the exception after logging

def create_signed_license_payload(customer_name: str, tier: str, validity_days: int, private_key: rsa.RSAPrivateKey) -> str:
    """
    Creates a license payload, signs it, and returns the structured license key string.

    Args:
        customer_name: Name of the customer.
        tier: License tier (e.g., "pro", "enterprise").
        validity_days: How many days the license is valid for from the issue date.
        private_key: The RSA private key object for signing.

    Returns:
        A JSON string representing the license key, containing the base64 encoded
        payload and signature.
    """
    payload_data = {
        "customerName": customer_name,
        "tier": tier.lower(), # Ensure tier is lowercase for consistency
        "validityPeriodDays": validity_days,
        "issueDate": datetime.now(timezone.utc).isoformat()
    }
    # Sort keys for consistent signing, ensuring the same byte string for the same logical payload
    payload_json_str = json.dumps(payload_data, sort_keys=True)
    payload_bytes = payload_json_str.encode('utf-8')

    # Sign the payload
    signature = private_key.sign(
        payload_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Create the final license key structure
    license_key_obj = {
        "payload": base64.b64encode(payload_bytes).decode('utf-8'),
        "signature": base64.b64encode(signature).decode('utf-8')
    }

    # Return as a compact JSON string for storage/transmission,
    # or pretty printed if preferred for readability in files.
    return json.dumps(license_key_obj) # Compact JSON
    # return json.dumps(license_key_obj, indent=2) # Pretty printed JSON