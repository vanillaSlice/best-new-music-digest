"""
Best New Music Digest App.
"""

from datetime import datetime

from best_new_music_digest import settings
from best_new_music_digest.dad_joke import get_dad_joke
from best_new_music_digest.email import send_email
from best_new_music_digest.playlist import create_playlists
from best_new_music_digest.scrapers import factory


def run():
    """
    Run the app.
    """

    today = datetime.utcnow().strftime("%A").lower()

    if today != settings.DAY_OF_WEEK_TO_RUN:
        print(f"Job is configured to run on {settings.DAY_OF_WEEK_TO_RUN.capitalize()} " \
              f"but today is {today.capitalize()}")
        print("Shutting down")
        return

    scrapers = factory.get_scrapers()
    digest = [scraper.scrape() for scraper in scrapers]
    dad_joke = get_dad_joke()
    albums_playlist_url, tracks_playlist_url = create_playlists(digest)
    send_email(digest, dad_joke, albums_playlist_url, tracks_playlist_url)
