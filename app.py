#!/usr/bin/env python3

import logging
import re
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from pymongo import MongoClient

from best_new_music_digest import settings
from best_new_music_digest.checkpoint import Checkpointer
from best_new_music_digest.scrapers import sputnikmusic


class Scraper:

    def __init__(self, checkpointer, title, link):
        self._checkpointer = checkpointer
        self._title = title
        self._link = link
        self._saved_checkpoint = False

    def scrape(self):
        errors = False

        try:
            items = self._get_items()
        except Exception as e:
            logging.error(e)
            items = []
            errors = True

        return {
            "title": self._title,
            "link": self._link,
            "items": items,
            "errors": errors,
        }

    def _get_items(self):
        return []

    def _get_checkpoint(self):
        return self._checkpointer.get_checkpoint(self._title)

    def _save_checkpoint(self, item):
        if not self._saved_checkpoint:
            self._checkpointer.save_checkpoint(self._title, item)
            self._saved_checkpoint = True

class PitchforkAlbumScraper(Scraper):

    _BASE_URL = "https://www.pitchfork.com"
    _SCRAPE_URL = "{}/reviews/best/albums/".format(_BASE_URL)

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "Pitchfork Albums", self._SCRAPE_URL)

    def _get_items(self):
        items = []

        response = requests.get(self._SCRAPE_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._get_checkpoint()

        for div in soup.find_all("div", "review"):
            link = "{}{}".format(self._BASE_URL, div.find("a").get("href"))

            if link == checkpoint:
                break

            self._save_checkpoint(link)

            item = {
                "artist": " / ".join([li.contents[0] for li in div.find("ul").find_all("li")]),
                "title": div.find("h2").contents[0],
                "link": link,
            }

            items.append(item)

        return items

class PitchforkTrackScraper(Scraper):

    _BASE_URL = "https://www.pitchfork.com"
    _SCRAPE_URL = "{}/reviews/best/tracks/".format(_BASE_URL)

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "Pitchfork Tracks", self._SCRAPE_URL)

    def _get_items(self):
        items = []

        response = requests.get(self._SCRAPE_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._get_checkpoint()

        details = soup.find("div", "track-details")
        link = "{}{}".format(self._BASE_URL, details.find("a").get("href"))

        if link == checkpoint:
            return []

        self._save_checkpoint(link)

        item = {
            "artist": " / ".join([li.contents[0] for li in details.find("ul").find_all("li")]),
            "title": details.find("h2").contents[0][1:-1],
            "link": link,
        }

        items.append(item)

        for details in soup.find_all("a", "track-collection-item__track-link"):
            link = "{}{}".format(self._BASE_URL, details.get("href"))

            if link == checkpoint:
                break

            items.append({
                "artist": " / ".join([li.contents[0] for li in details.find("ul").find_all("li")]),
                "title": details.find("h2").contents[0][1:-1],
                "link": link,
            })

        return items

class TheNeedleDropAlbumScraper(Scraper):

    _BASE_URL = "https://www.youtube.com"

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "The Needle Drop Albums", "{}/user/theneedledrop".format(self._BASE_URL))

    def _get_items(self):
        items = []

        response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&" \
                                "playlistId=PLP4CSgl7K7oo93I49tQa0TLB8qY3u7xuO&" \
                                "key={}".format(settings.YOUTUBE_API_KEY))

        checkpoint = self._get_checkpoint()

        for response_item in response.json()["items"]:
            snippet = response_item["snippet"]
            link = "{}/watch?v={}".format(self._BASE_URL, snippet["resourceId"]["videoId"])

            if link == checkpoint:
                break

            self._save_checkpoint(link)

            video_title = snippet["title"].split(" - ")

            item = {
                "artist": video_title[0],
                "title": video_title[1].replace("ALBUM REVIEW", ""),
                "link": link,
            }

            items.append(item)

        return items

class TheNeedleDropTrackScraper(Scraper):

    _BASE_URL = "https://www.youtube.com"

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "The Needle Drop Tracks", "{}/user/theneedledrop".format(self._BASE_URL))
        self._pattern = re.compile(r"!!!BEST TRACKS THIS WEEK!!!(.*?)\.\.\.meh\.\.\.", re.DOTALL)

    def _get_items(self):
        items = []

        response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&" \
                                "playlistId=PLP4CSgl7K7or84AAhr7zlLNpghEnKWu2c&" \
                                "key={}".format(settings.YOUTUBE_API_KEY))

        checkpoint = self._get_checkpoint()

        for response_item in response.json()["items"]:
            snippet = response_item["snippet"]

            if not snippet["title"].startswith("Weekly Track Roundup"):
                continue

            link = "{}/watch?v={}".format(self._BASE_URL, snippet["resourceId"]["videoId"])

            if link == checkpoint:
                break

            self._save_checkpoint(link)

            for line in self._pattern.findall(snippet["description"])[0].split("\n"):
                if " - " not in line:
                    continue

                video_title = line.split(" - ")

                item = {
                    "artist": video_title[0],
                    "title": video_title[1],
                    "link": link,
                }

                items.append(item)

        return items


class BestNewMusicDigest:

    def __init__(self):
        self._scrapers = self.__init_scrapers()

    def __init_scrapers(self):
        scrapers = []

        checkpointer = Checkpointer()

        if settings.SPUTNIKMUSIC_ALBUMS:
            scrapers.append(sputnikmusic.AlbumScraper(checkpointer))

        if settings.PITCHFORK_ALBUMS:
            scrapers.append(PitchforkAlbumScraper(checkpointer))

        if settings.PITCHFORK_TRACKS:
            scrapers.append(PitchforkTrackScraper(checkpointer))

        if settings.THE_NEEDLE_DROP_ALBUMS:
            scrapers.append(TheNeedleDropAlbumScraper(checkpointer))

        if settings.THE_NEEDLE_DROP_TRACKS:
            scrapers.append(TheNeedleDropTrackScraper(checkpointer))

        return scrapers

    def run(self):
        digest = self.__get_digest()
        if self.__should_send_email(digest):
            dad_joke = self.__get_dad_joke() if settings.DAD_JOKE else None
            self.__send_email(self.__to_email(digest, dad_joke))

    def __get_digest(self):
        return [scraper.scrape() for scraper in self._scrapers]

    def __should_send_email(self, digest):
        return any(d["items"] or d["errors"] for d in digest) or settings.ALWAYS_EMAIL

    def __get_dad_joke(self):
        try:
            return requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}).json()["joke"]
        except:
            return "It would seem that I've run out of dad jokes. I hope you're happy now 😞."

    def __to_email(self, digest, dad_joke):
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template('email.html')
        return template.render(digest=digest, dad_joke=dad_joke)

    def __send_email(self, content):
        smtp = smtplib.SMTP(host="smtp.sendgrid.net", port=587)
        smtp.starttls()
        smtp.login("apikey", settings.SENDER_PASSWORD)
        msg = MIMEMultipart()
        msg["From"] = f"{settings.SENDER_NAME} <{settings.SENDER_EMAIL}>"
        msg["To"] = settings.RECIPIENT_EMAIL
        msg["Subject"] = "🎧 Best New Music - {} 🎧".format(datetime.now().strftime("%d/%m/%Y"))
        msg.attach(MIMEText(content, "html"))
        smtp.send_message(msg)
        smtp.quit()

if __name__ == "__main__":
    BestNewMusicDigest().run()
