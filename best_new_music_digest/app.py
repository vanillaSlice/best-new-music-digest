"""
Best New Music Digest App.
"""

from datetime import datetime

from best_new_music_digest import settings
from best_new_music_digest.dad_joke import get_dad_joke
from best_new_music_digest.email import send_email
from best_new_music_digest.scrapers import factory


def run():
    """
    Run the app.
    """

    if datetime.utcnow().strftime("%A").lower() != settings.DAY_OF_WEEK_TO_RUN:
        return

    scrapers = factory.get_scrapers()
    digest = [scraper.scrape() for scraper in scrapers]
    dad_joke = get_dad_joke()
    send_email(digest, dad_joke)
