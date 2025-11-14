"""SMS notification utilities using Twilio"""

from django.conf import settings
from twilio.rest import Client


def send_sms(to: str, body: str) -> bool:
    """
    Send an SMS message using Twilio.

    Args:
        to: Phone number to send to (E.164 format, e.g., "+1234567890")
        body: Message body text

    Returns:
        True if message was sent successfully, False otherwise
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to,
            body=body,
        )
        return message.sid is not None
    except Exception as e:
        # Log the error in production - for now just return False
        print(f"Error sending SMS to {to}: {e}")
        return False


def format_kitty_notification(new_kitties: list[dict], shelter_name: str) -> str:
    """
    Format a notification message for new kitties.

    Args:
        new_kitties: List of kitty data dictionaries
        shelter_name: Name of the shelter

    Returns:
        Formatted SMS message string
    """
    if not new_kitties:
        return ""

    message = f"🐱 New kitties at {shelter_name}!\n\n"

    for kitty in new_kitties[:5]:  # Limit to 5 kitties per message
        name = kitty.get("name", "Unknown")
        message += f"• {name}\n"

    if len(new_kitties) > 5:
        message += f"\n...and {len(new_kitties) - 5} more!"

    message += "\nVisit your dashboard to see all new kitties!"

    return message
