# api/v1/webhooks/paddle_webhook_router.py
from fastapi import APIRouter, Request, HTTPException, status, Header, Depends
from typing import Dict, Any, Optional, Annotated
import os
import hmac
import hashlib

from core.logger import log
from core.license_generator import load_private_key, create_signed_license_payload, DEFAULT_APP_PRIVATE_KEY_PATH
from core.license_manager import LicenseTier # To validate tier from webhook
# For using BasicEmailSkill
from core.skill_manager import SkillManager

# --- Webhook Security Configuration ---
# This secret should be known only to Praximous and the Merchant of Record (e.g., Paddle)
# This is your Webhook Signing Secret from the Paddle dashboard.
PADDLE_WEBHOOK_SIGNING_SECRET = os.getenv("PADDLE_WEBHOOK_SIGNING_SECRET") 
# Deprecated: WEBHOOK_AUTH_HEADER = "X-Praximous-Webhook-Signature" 
# We will now use Paddle's standard 'Paddle-Signature'

router = APIRouter(
    prefix="/webhooks/paddle", # Example: /api/v1/webhooks/paddle
    tags=["Webhooks - Paddle"]
)

async def verify_webhook_signature(
    request: Request, # FastAPI Request object to access raw body
    paddle_signature: Annotated[Optional[str], Header(alias="Paddle-Signature")] = None 
):
    """
    Verifies the webhook signature sent by Paddle.
    Ref: https://developer.paddle.com/webhook-reference/verifying-webhooks
    """
    if not PADDLE_WEBHOOK_SIGNING_SECRET:
        log.error("PADDLE_WEBHOOK_SIGNING_SECRET is not configured. Webhook verification cannot proceed.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook processing misconfigured.")

    if not paddle_signature:
        log.warning("Missing 'Paddle-Signature' header.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing webhook signature.")

    try:
        # The Paddle-Signature header is in the format:
        # "ts=<timestamp>;h1=<hash>"
        parts = {p.split("=")[0]: p.split("=")[1] for p in paddle_signature.split(";")}
        ts = parts.get("ts")
        h1 = parts.get("h1")

        if not ts or not h1:
            log.error(f"Malformed Paddle-Signature header: {paddle_signature}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed Paddle-Signature header.")

        # Get the raw request body
        raw_body = await request.body()

        # Construct the signed payload string: "ts:request_body"
        signed_payload = f"{ts}:{raw_body.decode('utf-8')}"

        # Calculate the expected signature
        expected_signature = hmac.new(
            PADDLE_WEBHOOK_SIGNING_SECRET.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, h1):
            log.error(f"Invalid webhook signature. Expected hash does not match provided hash h1.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook signature.")
        
        log.info("Paddle webhook signature verified successfully.")
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        log.error(f"Error during Paddle signature verification: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error verifying webhook signature.")

@router.post("/purchase_completed", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(verify_webhook_signature)])
async def handle_purchase_completed(
    payload: Dict[str, Any], # The raw JSON payload from Paddle
    request: Request # To access app.state for SkillManager and SystemContext
):
    """
    Handles the 'purchase_completed' (or similar) webhook from Paddle.
    Generates and "delivers" a license key.
    Signature verification is handled by the `verify_webhook_signature` dependency.
    """
    log.info(f"Received 'purchase_completed' webhook from Paddle. Payload: {payload}")

    # Extract necessary information from the payload (this will vary based on Paddle's actual payload structure)
    # Example: Paddle's newer API might use `data.customer.email` or similar
    customer_email = payload.get("customer_email") # Adjust based on actual Paddle payload
    if not customer_email and "data" in payload and "customer" in payload["data"]: # Example for newer Paddle API structure
        customer_email = payload["data"]["customer"].get("email", "unknown_customer@example.com")
    
    customer_name = payload.get("customer_name", customer_email) 
    
    # Example: product_id might be in `data.items[0].price.product_id` for newer Paddle API
    product_id = payload.get("product_id") # Adjust based on actual Paddle payload
    if not product_id and "data" in payload and "items" in payload["data"] and len(payload["data"]["items"]) > 0:
        product_id = payload["data"]["items"][0].get("price", {}).get("product_id")

    # --- Map product_id to LicenseTier and validity_days ---
    # This mapping needs to be defined based on your product setup in Paddle.
    # Example:
    if product_id == "praximous_pro_yearly": # Replace with your actual Paddle Product ID
        tier = LicenseTier.PRO.value
        validity_days = 365
    elif product_id == "praximous_enterprise_yearly": # Replace with your actual Paddle Product ID
        tier = LicenseTier.ENTERPRISE.value
        validity_days = 365
    else:
        log.error(f"Unknown product_id '{product_id}' in webhook payload. Cannot generate license.")
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

        # --- License Delivery via BasicEmailSkill ---
        skill_manager: Optional[SkillManager] = getattr(request.app.state, 'skill_manager', None)
        system_context = getattr(request.app.state, 'system_context', None)

        if skill_manager and system_context and customer_email:
            email_skill = skill_manager.get_skill("email_sender")
            if email_skill:
                email_subject = f"Your Praximous License Key - {tier.capitalize()} Tier"
                email_body = (
                    f"Dear {customer_name},\n\n"
                    f"Thank you for your Praximous purchase!\n\n"
                    f"Your License Tier: {tier.capitalize()}\n"
                    f"Validity: {validity_days} days\n\n"
                    f"Please use the following license key to activate Praximous:\n\n"
                    f"{license_key_string}\n\n"
                    f"To apply this license, set the PRAXIMOUS_LICENSE_KEY environment variable in your .env file or system environment.\n\n"
                    f"If you have any questions, please contact support.\n\n"
                    f"Thanks,\nThe Praximous Team"
                )
                email_result = await email_skill.execute(
                    prompt=email_body, # Using prompt for body as per BasicEmailSkill
                    to=customer_email,
                    subject=email_subject,
                    # system_context=system_context # Pass context if skill expects it
                )
                if email_result.get("success"):
                    log.info(f"License key successfully emailed to {customer_email}.")
                else:
                    log.error(f"Failed to email license key to {customer_email}. Skill response: {email_result.get('error_details', email_result.get('error', 'Unknown email error'))}")
            else:
                log.error("Email sender skill not found. Cannot email license key.")
        else:
            log.error("SkillManager, SystemContext, or customer_email not available. Cannot email license key.")
            if not customer_email:
                log.error("Customer email not found in webhook payload. Cannot send license.")
        
        return {"status": "success", "message": "License generated and (simulated) delivery initiated."}

    except FileNotFoundError:
        log.critical(f"Application private signing key not found at {DEFAULT_APP_PRIVATE_KEY_PATH}. Cannot generate license via webhook.")
        # Return 500 as this is a server configuration issue.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="License generation system misconfigured.")
    except Exception as e:
        log.error(f"Error during license generation via webhook: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate license.")
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