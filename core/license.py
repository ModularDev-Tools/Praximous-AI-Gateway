# core/license.py
import json
import os
import base64
from datetime import datetime, timezone, timedelta
from typing import Optional, NamedTuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend

from core.logger import log
from .enums import LicenseTier # Import LicenseTier from the new enums.py

PUBLIC_KEY_NAME = "praximous_signing_public.pem"
CONFIG_DIR = "config"
DEFAULT_PUBLIC_KEY_PATH = os.path.join(CONFIG_DIR, PUBLIC_KEY_NAME)

# Environment variable to hold the license key string
LICENSE_KEY_ENV_VAR = "PRAXIMOUS_LICENSE_KEY"

class LicenseInfo(NamedTuple):
    customer_name: str
    tier: LicenseTier
    issue_date: datetime
    expiry_date: datetime
    is_valid: bool # Overall validity including signature and date checks
    is_expired: bool
    raw_payload: dict

def load_public_key(key_path: str = DEFAULT_PUBLIC_KEY_PATH) -> Optional[RSAPublicKey]:
    """Loads the RSA public key from the specified path."""
    try:
        with open(key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        log.info(f"Successfully loaded public key from {key_path}")
        return public_key
    except FileNotFoundError:
        log.error(f"Public key file not found at {key_path}. License verification will fail.")
    except Exception as e:
        log.error(f"Error loading public key from {key_path}: {e}", exc_info=True)
    return None

def verify_license_key(license_key_str: str, public_key: RSAPublicKey) -> Optional[LicenseInfo]:
    """
    Verifies the provided license key string using the public key.
    Checks signature and validity period.
    """
    if not license_key_str:
        log.warning("License key string is empty.")
        return None
    if not public_key:
        log.error("Public key not available for license verification.")
        return None

    try:
        license_obj = json.loads(license_key_str)
        payload_b64 = license_obj.get("payload")
        signature_b64 = license_obj.get("signature")

        if not payload_b64 or not signature_b64:
            log.error("License key is malformed: missing payload or signature.")
            return None

        payload_bytes = base64.b64decode(payload_b64)
        signature = base64.b64decode(signature_b64)

        # Verify signature
        public_key.verify(
            signature,
            payload_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        log.info("License signature verified successfully.")

        # Parse payload
        payload_data = json.loads(payload_bytes.decode('utf-8'))
        customer_name = payload_data.get("customerName")
        tier_str = payload_data.get("tier")
        validity_days = payload_data.get("validityPeriodDays")
        issue_date_str = payload_data.get("issueDate")

        if not all([customer_name, tier_str, isinstance(validity_days, int), issue_date_str]):
            log.error("License payload is incomplete or has invalid types.")
            return None

        try:
            tier = LicenseTier(tier_str)
        except ValueError:
            log.error(f"Invalid tier '{tier_str}' in license payload.")
            return None

        issue_date = datetime.fromisoformat(issue_date_str)
        expiry_date = issue_date + timedelta(days=validity_days)
        current_date = datetime.now(timezone.utc)

        is_expired = current_date > expiry_date
        is_valid_overall = not is_expired # For now, only expiry check after signature

        if is_expired:
            log.warning(f"License for '{customer_name}' expired on {expiry_date.isoformat()}.")
        else:
            log.info(f"License for '{customer_name}' (Tier: {tier.name}) is valid until {expiry_date.isoformat()}.")

        return LicenseInfo(
            customer_name=customer_name,
            tier=tier,
            issue_date=issue_date,
            expiry_date=expiry_date,
            is_valid=is_valid_overall,
            is_expired=is_expired,
            raw_payload=payload_data
        )

    except InvalidSignature:
        log.error("License signature verification failed: Invalid signature.")
    except json.JSONDecodeError:
        log.error("Failed to decode license key string or payload: Invalid JSON.")
    except base64.binascii.Error:
        log.error("Failed to decode base64 content in license key.")
    except Exception as e:
        log.error(f"An unexpected error occurred during license verification: {e}", exc_info=True)
    
    return None

_cached_public_key: Optional[RSAPublicKey] = None
_cached_license_info: Optional[LicenseInfo] = None

def get_active_license_info() -> Optional[LicenseInfo]:
    """
    Retrieves and verifies the license key from the environment variable.
    Caches the public key and license info for performance.
    """
    global _cached_public_key, _cached_license_info

    if _cached_license_info and _cached_license_info.is_valid and not _cached_license_info.is_expired:
         # Basic check, re-verify if expiry is a concern for long-running apps without restart
        if datetime.now(timezone.utc) <= _cached_license_info.expiry_date:
            return _cached_license_info

    if _cached_public_key is None:
        _cached_public_key = load_public_key()
    
    if _cached_public_key is None: # Still None after trying to load
        return None # Cannot verify without public key

    license_key_str = os.getenv(LICENSE_KEY_ENV_VAR)
    if not license_key_str:
        log.info(f"{LICENSE_KEY_ENV_VAR} not set. Praximous will operate with default (Community) tier features.")
        return None

    _cached_license_info = verify_license_key(license_key_str, _cached_public_key)
    return _cached_license_info

# Example of how this might be called on startup (e.g., in main.py or app initialization)
# if __name__ == '__main__':
#     # For testing, set PRAXIMOUS_LICENSE_KEY in your environment
#     # e.g., PRAXIMOUS_LICENSE_KEY='{"payload": "...", "signature": "..."}'
#     active_license = get_active_license_info()
#     if active_license:
#         log.info(f"Active License Details: Customer: {active_license.customer_name}, Tier: {active_license.tier.name}, Valid: {active_license.is_valid}, Expired: {active_license.is_expired}, Expires: {active_license.expiry_date}")
#     else:
#         log.warning("No valid active license found.")
