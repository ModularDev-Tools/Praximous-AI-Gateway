# licensing_tool/generate_license.py
import argparse
import json
import os
import sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

# Adjust import path to use the core license generator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the core_load_private_key and create_signed_license_payload from your core module
from core.license_generator import core_load_private_key, create_signed_license_payload

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

def create_license_key(customer_name: str, tier: str, validity_days: int) -> str:
    """
    Creates a signed license key.
    The license key will be a JSON string containing the payload and its signature,
    both base64 encoded.
    """
    # Use the core function, loading the key specifically from the tool's key directory
    private_key = core_load_private_key(PRIVATE_KEY_PATH)
    license_payload_str = create_signed_license_payload(customer_name, tier, validity_days, private_key)
    return json.dumps(json.loads(license_payload_str), indent=2) # Pretty print for CLI output

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