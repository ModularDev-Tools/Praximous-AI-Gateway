# licensing_tool/generate_license.py
import argparse
import json
import os
from datetime import datetime, timezone
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

# Define key file names (your "crypto key giblets")
PRIVATE_KEY_FILE = "praximous_signing_private.pem"
PUBLIC_KEY_FILE = "praximous_signing_public.pem"
KEY_DIRECTORY = "keys" # Store keys in a subdirectory

# Ensure the key directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), KEY_DIRECTORY), exist_ok=True)

PRIVATE_KEY_PATH = os.path.join(os.path.dirname(__file__), KEY_DIRECTORY, PRIVATE_KEY_FILE)
PUBLIC_KEY_PATH = os.path.join(os.path.dirname(__file__), KEY_DIRECTORY, PUBLIC_KEY_FILE)


def generate_key_pair():
    """Generates an RSA private/public key pair and saves them to files."""
    if os.path.exists(PRIVATE_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH):
        print(f"Key pair already exists at {KEY_DIRECTORY}/. Skipping generation.")
        return

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Save private key
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption() # For simplicity; consider password protection
        ))
    print(f"Private key saved to {PRIVATE_KEY_PATH}")

    # Save public key
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print(f"Public key saved to {PUBLIC_KEY_PATH}")

def load_private_key() -> rsa.RSAPrivateKey:
    """Loads the RSA private key from its file."""
    if not os.path.exists(PRIVATE_KEY_PATH):
        raise FileNotFoundError(f"Private key file not found at {PRIVATE_KEY_PATH}. "
                                "Run with --generate-keys first.")
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None, # Add password if key is encrypted
            backend=default_backend()
        )
    return private_key

def create_license_key(customer_name: str, tier: str, validity_days: int) -> str:
    """
    Creates a signed license key.
    The license key will be a JSON string containing the payload and its signature,
    both base64 encoded.
    """
    private_key = load_private_key()

    payload_data = {
        "customerName": customer_name,
        "tier": tier.lower(), # Ensure tier is lowercase for consistency
        "validityPeriodDays": validity_days,
        "issueDate": datetime.now(timezone.utc).isoformat()
    }
    payload_json_str = json.dumps(payload_data, sort_keys=True) # Sort keys for consistent signing
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

    return json.dumps(license_key_obj, indent=2) # Pretty print the final JSON license key

def main():
    parser = argparse.ArgumentParser(description="Praximous License Key Generator")
    parser.add_argument("--generate-keys", action="store_true",
                        help="Generate a new RSA public/private key pair if they don't exist.")

    parser.add_argument("--customer", type=str, help="Customer Name")
    parser.add_argument("--tier", type=str, choices=["community", "pro", "enterprise"],
                        help="License Tier (community, pro, enterprise)")
    parser.add_argument("--validity", type=int, help="Validity period in days")
    parser.add_argument("--output-file", type=str, help="Optional: File to save the generated license key")

    args = parser.parse_args()

    if args.generate_keys:
        generate_key_pair()
        # If only generating keys, no need to proceed further unless other args are also present
        if not (args.customer and args.tier and args.validity is not None):
            return

    if not (args.customer and args.tier and args.validity is not None):
        if not args.generate_keys: # Only show error if not just generating keys
            parser.error("Arguments --customer, --tier, and --validity are required to generate a license key.")
        return

    try:
        license_key_str = create_license_key(args.customer, args.tier, args.validity)
        print("\nGenerated License Key:")
        print(license_key_str)

        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(license_key_str)
            print(f"\nLicense key saved to {args.output_file}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure keys are generated first using --generate-keys.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()