#!/usr/bin/env python3

from best_new_music_digest.dad_joke import get_dad_joke
from best_new_music_digest.email import send_email
from best_new_music_digest.scrapers import factory


def run():
    scrapers = factory.get_scrapers()
    digest = [scraper.scrape() for scraper in scrapers]
    dad_joke = get_dad_joke()
    send_email(digest, dad_joke)

if __name__ == "__main__":
   run()
