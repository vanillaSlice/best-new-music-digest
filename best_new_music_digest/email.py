"""
Emails.
"""

from datetime import datetime

from jinja2 import Environment, FileSystemLoader
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

    file_loader = FileSystemLoader("templates")
    env = Environment(loader=file_loader)
    template = env.get_template("email.html")
    content = template.render(digest=digest, dad_joke=dad_joke)

    SendGridAPIClient(settings.SENDER_PASSWORD).send(Mail(
        from_email=(settings.SENDER_EMAIL, settings.SENDER_NAME),
        to_emails=settings.RECIPIENT_EMAIL,
        subject=f"🎧 Best New Music - {datetime.now().strftime('%d/%m/%Y')} 🎧",
        html_content=content
    ))
