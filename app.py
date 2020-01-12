#!/usr/bin/env python3

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import re
import smtplib
import sys

from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests

import settings

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

class SputnikmusicAlbumScraper(Scraper):

    _BASE_URL = "https://www.sputnikmusic.com"
    _SCRAPE_URL = "{}/bestnewmusic".format(_BASE_URL)

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "Sputnikmusic Albums", self._SCRAPE_URL)

    def _get_items(self):
        items = []

        response = requests.get(self._SCRAPE_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._get_checkpoint()

        for td in soup.find_all("td", "bestnewmusic"):
            a = td.find("a")

            item = {
                "artist": a.find("strong").contents[0],
                "title": a.find_all("font")[1].contents[1],
                "link": "{}{}".format(self._BASE_URL, a.get("href")),
            }

            if item == checkpoint:
                break

            self._save_checkpoint(item)

            items.append(item)

        return items

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
            item = {
                "artist": " / ".join([li.contents[0] for li in div.find("ul").find_all("li")]),
                "title": div.find("h2").contents[0],
                "link": "{}{}".format(self._BASE_URL, div.find("a").get("href")),
            }

            if item == checkpoint:
                break

            self._save_checkpoint(item)

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

        item = {
            "artist": " / ".join([li.contents[0] for li in details.find("ul").find_all("li")]),
            "title": details.find("h2").contents[0][1:-1],
            "link": "{}{}".format(self._BASE_URL, details.find("a").get("href")),
        }

        if item == checkpoint:
            return []

        self._save_checkpoint(item)

        items.append(item)

        for details in soup.find_all("a", "track-collection-item__track-link"):
            items.append({
                "artist": " / ".join([li.contents[0] for li in details.find("ul").find_all("li")]),
                "title": details.find("h2").contents[0][1:-1],
                "link": "{}{}".format(self._BASE_URL, details.get("href")),
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
            video_title = snippet["title"].split(" - ")

            item = {
                "artist": video_title[0],
                "title": video_title[1].replace("ALBUM REVIEW", ""),
                "link": "{}/watch?v={}".format(self._BASE_URL, snippet["resourceId"]["videoId"]),
            }

            if item == checkpoint:
                break

            self._save_checkpoint(item)

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

            new_checkpoint = { "link": link }

            if new_checkpoint == checkpoint:
                break

            self._save_checkpoint(new_checkpoint)

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

class Checkpointer:

    def __init__(self):
        self.checkpoints = MongoClient(settings.MONGODB_URI)["best-new-music-digest"].checkpoints

    def get_checkpoint(self, name):
        checkpoint = self.checkpoints.find_one({ "name": name })
        return checkpoint["checkpoint"] if checkpoint else {}

    def save_checkpoint(self, name, checkpoint):
        self.checkpoints.insert_one({ "name": name, "checkpoint": checkpoint })

class BestNewMusicDigest:

    def __init__(self):
        self._checkpointer = Checkpointer()

        self._scrapers = []

        if settings.SPUTNIKMUSIC_ALBUMS:
            self._scrapers.append(SputnikmusicAlbumScraper(self._checkpointer))

        if settings.PITCHFORK_ALBUMS:
            self._scrapers.append(PitchforkAlbumScraper(self._checkpointer))

        if settings.PITCHFORK_TRACKS:
            self._scrapers.append(PitchforkTrackScraper(self._checkpointer))

        if settings.THE_NEEDLE_DROP_ALBUMS:
            self._scrapers.append(TheNeedleDropAlbumScraper(self._checkpointer))

        if settings.THE_NEEDLE_DROP_TRACKS:
            self._scrapers.append(TheNeedleDropTrackScraper(self._checkpointer))

    def run(self):
        digest = self._get_digest()
        if self._should_send_email(digest):
            self._send_email(self._to_html(digest))

    def _get_digest(self):
        return [scraper.scrape() for scraper in self._scrapers]

    def _should_send_email(self, digest):
        return any(d["items"] or d["errors"] for d in digest)

    def _to_html(self, digest):
        digest_html = "<p>Sappenin' bro?</p>"
        digest_html += "<p><em>{}</em> 🤦‍♂️</p>".format(self._get_dad_joke())
        digest_html += "<p>Anyway, here's some choons to stick in your ear holes:</p><br />"

        for d in digest:
            digest_html += "<h3><a href=\"{}\">{}</a></h3>".format(d["link"], d["title"])

            if d["errors"]:
                digest_html += "<p><strong>😱 Error getting digest 😱</strong></p><br />"
                continue

            if not d["items"]:
                digest_html += "<p>No updates today!</p><br />"
                continue

            digest_html += "<ol>"
            for i in d["items"]:
                digest_html += "<li><a href=\"{}\">{} - {}</a></li>".format(i["link"], i["artist"], i["title"])
            digest_html += "</ol><br />"

        digest_html += "<p>Until next time 🤘</p>"

        return digest_html

    def _get_dad_joke(self):
        try:
            return requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}).json()["joke"]
        except:
            return "It would seem that I've run out of dad jokes. I hope you're happy now 😞."

    def _send_email(self, content):
        smtp = smtplib.SMTP(host="smtp.gmail.com", port=587)
        smtp.starttls()
        smtp.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        msg = MIMEMultipart()
        msg["From"] = settings.SENDER_NAME
        msg["To"] = settings.RECIPIENT_EMAIL
        msg["Subject"] = "🎧 Best New Music - {} 🎧".format(datetime.now().strftime("%d/%m/%Y"))
        msg.attach(MIMEText(content, "html"))
        smtp.send_message(msg)
        smtp.quit()

if __name__ == "__main__":
    BestNewMusicDigest().run()
