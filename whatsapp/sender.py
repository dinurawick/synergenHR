"""
Thin wrapper around the Twilio REST client for sending WhatsApp messages.
Credentials are read from environment variables — never hardcoded.
"""
import logging
import os

logger = logging.getLogger(__name__)


def send_whatsapp(to: str, body: str) -> bool:
    """
    Send a WhatsApp message via Twilio.

    Args:
        to:   Recipient number in E.164 format, e.g. '+94771234567'
        body: Message text

    Returns:
        True on success, False on failure.
    """
    try:
        from twilio.rest import Client

        account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        from_number = os.environ.get(
            "TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"
        )

        if not account_sid or not auth_token:
            logger.error("Twilio credentials not configured in environment.")
            return False

        # Ensure numbers are in whatsapp: format
        to_wa = to if to.startswith("whatsapp:") else f"whatsapp:{to}"

        client = Client(account_sid, auth_token)
        client.messages.create(body=body, from_=from_number, to=to_wa)
        return True

    except Exception as exc:
        logger.exception("Failed to send WhatsApp message to %s: %s", to, exc)
        return False
