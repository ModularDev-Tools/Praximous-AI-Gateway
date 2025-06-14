# skills/basic_email_skill.py
from typing import Dict, Any, List, Optional
from core.skill_manager import BaseSkill
from core.logger import log
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration - these should be set in your .env file
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT", 587) # Default to 587 (TLS)
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SENDER_EMAIL = os.getenv("SMTP_SENDER_EMAIL", SMTP_USER) # Default sender to user if not specified

class BasicEmailSkill(BaseSkill):
    name: str = "email_sender"

    def __init__(self):
        super().__init__()
        if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_SENDER_EMAIL]):
            log.warning(f"{self.name}: SMTP configuration is incomplete. Email sending will likely fail. "
                        "Ensure SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, and SMTP_SENDER_EMAIL are set.")
        try:
            self.smtp_port_int = int(SMTP_PORT)
        except (ValueError, TypeError):
            log.error(f"{self.name}: SMTP_PORT ('{SMTP_PORT}') is not a valid integer. Defaulting to 587 for checks, but sending might fail.")
            self.smtp_port_int = 587 # Fallback for checks, actual sending might still use original string if not int

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "send_email").lower()
        
        recipient_to = kwargs.get("to") # Can be a single email string or list of strings
        subject = kwargs.get("subject", "Message from Praximous")
        body_text = kwargs.get("body", prompt) # Use 'body' kwarg or the main prompt

        log.info(f"{self.name} executing. Operation: '{operation}', To: '{recipient_to}', Subject: '{subject}'")

        if not all([SMTP_HOST, self.smtp_port_int, SMTP_USER, SMTP_PASSWORD, SMTP_SENDER_EMAIL]):
            return self._build_response(success=False, error="Configuration Error", details="SMTP server settings are not fully configured in environment variables.")

        if not recipient_to:
            return self._build_response(success=False, error="Input Error", details="'to' (recipient email address) is required.")
        if not body_text or not body_text.strip():
            return self._build_response(success=False, error="Input Error", details="'body' (email content) cannot be empty.")

        if isinstance(recipient_to, str):
            recipients_list = [r.strip() for r in recipient_to.split(',')]
        elif isinstance(recipient_to, list):
            recipients_list = [str(r).strip() for r in recipient_to]
        else:
            return self._build_response(success=False, error="Input Error", details="'to' must be a string (comma-separated for multiple) or a list of strings.")

        if operation == "send_email":
            try:
                msg = MIMEMultipart()
                msg['From'] = SMTP_SENDER_EMAIL
                msg['To'] = ", ".join(recipients_list)
                msg['Subject'] = subject
                msg.attach(MIMEText(body_text, 'plain'))

                # Using a context manager for the SMTP connection is good practice
                # Note: smtplib is synchronous. For a truly async skill with many emails,
                # you might look into libraries like aiosmtplib, but for basic use,
                # running this in a thread pool executor via asyncio.to_thread might be an option
                # if it becomes a blocking issue. For now, direct call for simplicity.
                with smtplib.SMTP(SMTP_HOST, self.smtp_port_int) as server:
                    server.starttls() # Upgrade connection to secure
                    server.login(SMTP_USER, SMTP_PASSWORD)
                    server.sendmail(SMTP_SENDER_EMAIL, recipients_list, msg.as_string())
                
                log.info(f"Email sent successfully to {', '.join(recipients_list)}")
                return self._build_response(success=True, data={"message": "Email sent successfully.", "to": recipients_list, "subject": subject})
            except smtplib.SMTPException as e:
                log.error(f"{self.name} SMTP error: {e}", exc_info=True)
                return self._build_response(success=False, error="SMTP Error", details=f"Failed to send email: {str(e)}")
            except Exception as e:
                log.error(f"{self.name} unexpected error: {e}", exc_info=True)
                return self._build_response(success=False, error="Internal Skill Error", details=str(e))
        else:
            return self._build_response(success=False, error="Unsupported Operation", details=f"Operation '{operation}' is not supported.")

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Sends an email using configured SMTP settings. Requires SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_SENDER_EMAIL environment variables.",
            "operations": {
                "send_email": {
                    "description": "Sends an email to one or more recipients.",
                    "parameters_schema": {
                        "to": {"type": "string_or_list", "description": "Recipient email address(es). Comma-separated string or list of strings."},
                        "subject": {"type": "string", "default": "Message from Praximous", "description": "The subject of the email."},
                        "body": {"type": "string", "description": "The plain text body of the email. Can also be passed via 'prompt'."}
                    },
                    "example_request_payload": {"task_type": self.name, "operation": "send_email", "to": "recipient@example.com", "subject": "Test Email", "body": "This is a test email from Praximous."}
                }
            }
        }