"""
Emails.
"""

from datetime import datetime

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from best_new_music_digest import settings


def send_email(digest, dad_joke=None):
    """
    Sends out digest email.
    """

    should_send = any(d["items"] or d["errors"] for d in digest) or settings.ALWAYS_EMAIL

    if not should_send:
        return

    message = Mail(
        from_email=(settings.SENDER_EMAIL, settings.SENDER_NAME),
        to_emails=settings.RECIPIENT_EMAIL,
    )

    message.template_id = settings.SENDGRID_TEMPLATE_ID

    message.dynamic_template_data = {
        "subject": f"🎧 Best New Music - {datetime.now().strftime('%d/%m/%Y')} 🎧",
        "dad_joke": dad_joke,
        "digest": digest,
    }

    SendGridAPIClient(settings.SENDGRID_API_KEY).send(message)
