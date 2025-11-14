"""Email notification utilities"""

from django.conf import settings
from django.core.mail import send_mail


def send_email_notification(to_email: str, subject: str, message: str) -> bool:
    """
    Send an email notification.

    Args:
        to_email: Email address to send to
        subject: Email subject line
        message: Email message body (plain text)

    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        if not to_email:
            print("Error: No email address provided")
            return False

        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        import traceback

        traceback.print_exc()
        return False


def format_kitty_notification(
    new_kitties: list[dict], shelter_name: str, shelter_url: str = ""
) -> tuple[str, str]:
    """
    Format an email notification for new kitties.

    Args:
        new_kitties: List of kitty data dictionaries
        shelter_name: Name of the shelter
        shelter_url: URL of the shelter's website (optional)

    Returns:
        Tuple of (subject, message_body)
    """
    subject = f"🐱 New kitties available for adoption at {shelter_name}!"

    message = f"There are new kitties at {shelter_name} since yesterday!\n\n"
    message += f"Visit {shelter_url} to see all new kitties!\n\n"

    for kitty in new_kitties:
        name = kitty["name"]
        link = kitty["link"]
        message += f"• {name}: {link}\n"

    return subject, message
