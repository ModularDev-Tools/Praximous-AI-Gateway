# api/v1/webhooks/paddle_webhook_router.py
from fastapi import APIRouter, Request, HTTPException, status, Header
from typing import Dict, Any, Optional
import os
import hmac
import hashlib

from core.logger import log
from core.license_generator import load_private_key, create_signed_license_payload, DEFAULT_APP_PRIVATE_KEY_PATH
from core.license_manager import LicenseTier # To validate tier from webhook

# --- Webhook Security Configuration ---
# This secret should be known only to Praximous and the Merchant of Record (e.g., Paddle)
# For production, use a strong, randomly generated secret stored securely.
PADDLE_WEBHOOK_SECRET = os.getenv("PADDLE_WEBHOOK_SECRET", "your-super-secret-webhook-key-for-mvp")
# It's highly recommended to use Paddle's signature verification instead of just a secret key.
# Paddle sends a 'Paddle-Signature' header.
# For MVP, we'll use a simpler shared secret in a custom header for demonstration.
WEBHOOK_AUTH_HEADER = "X-Praximous-Webhook-Signature" # Or use Paddle's standard if implementing full verification

router = APIRouter(
    prefix="/webhooks/paddle", # Example: /api/v1/webhooks/paddle
    tags=["Webhooks - Paddle"]
)

async def verify_webhook_signature(
    request: Request,
    x_praximous_webhook_signature: Optional[str] = Header(None) # Our custom header for simple auth
    # paddle_signature: Optional[str] = Header(None) # For Paddle's actual signature
):
    """
    Verifies the webhook signature.
    For MVP, this uses a simple shared secret.
    TODO: Implement proper Paddle signature verification for production.
    (https://developer.paddle.com/webhook-reference/verifying-webhooks)
    """
    if not PADDLE_WEBHOOK_SECRET:
        log.error("PADDLE_WEBHOOK_SECRET is not configured. Webhook verification cannot proceed.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook processing misconfigured.")

    if not x_praximous_webhook_signature:
        log.warning("Missing webhook signature header.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing webhook signature.")

    # Simple shared secret check for MVP
    if x_praximous_webhook_signature != PADDLE_WEBHOOK_SECRET: # Replace with actual signature verification
        log.error(f"Invalid webhook signature. Expected '{PADDLE_WEBHOOK_SECRET}', got '{x_praximous_webhook_signature}'")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook signature.")
    log.info("Webhook signature verified successfully (MVP simple check).")


@router.post("/purchase_completed", status_code=status.HTTP_202_ACCEPTED)
async def handle_purchase_completed(
    payload: Dict[str, Any], # The raw JSON payload from Paddle
    request: Request # To access headers or raw body if needed for full signature verification
    # signature_dependency: Any = Depends(verify_webhook_signature) # Enable when ready
):
    """
    Handles the 'purchase_completed' (or similar) webhook from Paddle.
    Generates and "delivers" a license key.
    """
    log.info(f"Received 'purchase_completed' webhook from Paddle. Payload: {payload}")

    # --- TODO: Implement proper Paddle signature verification using request.body() and paddle_signature header ---
    # For now, we'll rely on a simpler custom header check if enabled via Depends.
    # If not using Depends, manually call a verification function here.
    # For MVP, we might just log and proceed if the secret is very basic and for internal testing.
    # Example: if not verify_paddle_actual_signature(await request.body(), paddle_signature_header_value):
    # raise HTTPException(...)

    # Extract necessary information from the payload (this will vary based on Paddle's actual payload structure)
    customer_email = payload.get("customer_email", "unknown_customer@example.com")
    customer_name = payload.get("customer_name", customer_email) # Fallback to email if name not present
    product_id = payload.get("product_id") # Or product_name
    # transaction_id = payload.get("transaction_id") # Useful for idempotency

    # --- Map product_id to LicenseTier and validity_days ---
    # This mapping needs to be defined based on your product setup in Paddle.
    # Example:
    if product_id == "praximous_pro_yearly":
        tier = LicenseTier.PRO.value
        validity_days = 365
    elif product_id == "praximous_enterprise_yearly":
        tier = LicenseTier.ENTERPRISE.value
        validity_days = 365
    else:
        log.error(f"Unknown product_id '{product_id}' in webhook payload. Cannot generate license.")
        # Return 202 to acknowledge receipt but log error, or 400 if it's a clear client error.
        # For now, we'll let it proceed to generation with a default if not found, or raise.
        # For a real system, you'd likely return an error or have robust default handling.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown product_id: {product_id}")

    try:
        # Load the application's private signing key
        # IMPORTANT: Ensure config/praximous_signing_private.pem exists and is protected!
        app_private_key = load_private_key(DEFAULT_APP_PRIVATE_KEY_PATH)
        
        license_key_string = create_signed_license_payload(
            customer_name=customer_name,
            tier=tier,
            validity_days=validity_days,
            private_key=app_private_key
        )
        log.info(f"Generated license key for {customer_name} (Tier: {tier}): {license_key_string}")

        # --- TODO: License Delivery ---
        # 1. Store the license key in your database, associated with the customer/transaction.
        # 2. Email the license key to customer_email.
        #    (Could use BasicEmailSkill or a direct email function here)
        log.info(f"SIMULATING LICENSE DELIVERY: License for {customer_email} would be sent here.")

        return {"status": "success", "message": "License generated and (simulated) delivery initiated."}

    except FileNotFoundError:
        log.critical(f"Application private signing key not found at {DEFAULT_APP_PRIVATE_KEY_PATH}. Cannot generate license via webhook.")
        # Return 500 as this is a server configuration issue.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="License generation system misconfigured.")
    except Exception as e:
        log.error(f"Error during license generation via webhook: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate license.")