#!/usr/bin/env python3

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import smtplib
import sys

from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests

class Scraper:

    _saved_checkpoint = False

    def __init__(self, checkpointer, title, link):
        self._checkpointer = checkpointer
        self._title = title
        self._link = link

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

class SputnikmusicScraper(Scraper):

    _base_url = "https://www.sputnikmusic.com"
    _scrape_url = "{}/bestnewmusic".format(_base_url)

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "Sputnikmusic Albums", self._scrape_url)

    def _get_items(self):
        items = []

        response = requests.get(self._scrape_url)
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._get_checkpoint()

        for td in soup.find_all("td", "bestnewmusic"):
            a = td.find("a")

            item = {
                "artist": a.find("strong").contents[0],
                "title": a.find_all("font")[1].contents[1],
                "link": "{}{}".format(self._base_url, a.get("href")),
            }

            if item == checkpoint:
                break

            self._save_checkpoint(item)

            items.append(item)

        return items

class PitchforkAlbumScraper(Scraper):

    _base_url = "https://www.pitchfork.com"
    _scrape_url = "{}/reviews/best/albums/".format(_base_url)

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "Pitchfork Albums", self._scrape_url)

    def _get_items(self):
        items = []

        response = requests.get(self._scrape_url)
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._get_checkpoint()

        for div in soup.find_all("div", "review"):
            item = {
                "artist": " / ".join([li.contents[0] for li in div.find("ul").find_all("li")]),
                "title": div.find("h2").contents[0],
                "link": "{}{}".format(self._base_url, div.find("a").get("href")),
            }

            if item == checkpoint:
                break

            self._save_checkpoint(item)

            items.append(item)

        return items

class PitchforkTrackScraper(Scraper):

    _base_url = "https://www.pitchfork.com"
    _scrape_url = "{}/reviews/best/tracks/".format(_base_url)

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "Pitchfork Tracks", self._scrape_url)

    def _get_items(self):
        items = []

        response = requests.get(self._scrape_url)
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._get_checkpoint()

        details = soup.find("div", "track-details")

        item = {
            "artist": " / ".join([li.contents[0] for li in details.find("ul").find_all("li")]),
            "title": details.find("h2").contents[0][1:-1],
            "link": "{}{}".format(self._base_url, details.find("a").get("href")),
        }

        if item == checkpoint:
            return []

        self._save_checkpoint(item)

        items.append(item)

        for details in soup.find_all("a", "track-collection-item__track-link"):
            items.append({
                "artist": " / ".join([li.contents[0] for li in details.find("ul").find_all("li")]),
                "title": details.find("h2").contents[0][1:-1],
                "link": "{}{}".format(self._base_url, details.get("href")),
            })

        return items

class TheNeedleDropAlbumScraper(Scraper):

    _base_url = "https://www.youtube.com"

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "The Needle Drop Albums", "{}/user/theneedledrop".format(self._base_url))

    def _get_items(self):
        items = []

        response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&" \
                                "playlistId=PLP4CSgl7K7oo93I49tQa0TLB8qY3u7xuO&" \
                                "key={}".format(os.environ["YOUTUBE_API_KEY"]))

        checkpoint = self._get_checkpoint()

        for response_item in response.json()["items"]:
            snippet = response_item["snippet"]
            video_title = snippet["title"].split(" - ")

            item = {
                "artist": video_title[0],
                "title": video_title[1].replace("ALBUM REVIEW", ""),
                "link": "{}/watch?v={}".format(self._base_url, snippet["resourceId"]["videoId"]),
            }

            if item == checkpoint:
                break

            self._save_checkpoint(item)

            items.append(item)

        return items

class TheNeedleDropTrackScraper(Scraper):

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "The Needle Drop Tracks", "https://www.youtube.com/user/theneedledrop")

    # TODO implement this
    def _get_items(self):
        return []

class Checkpointer:

    client = MongoClient(os.environ["MONGODB_URI"])
    db = client["best-new-music-digest"]
    checkpoints = db.checkpoints

    def get_checkpoint(self, name):
        checkpoint = self.checkpoints.find_one({ "name": name })
        return checkpoint["checkpoint"] if checkpoint else {}

    def save_checkpoint(self, name, checkpoint):
        self.checkpoints.insert_one({ "name": name, "checkpoint": checkpoint })

class BestNewMusicDigest:

    _checkpointer = Checkpointer()

    _scrapers = [
        SputnikmusicScraper(_checkpointer),
        PitchforkAlbumScraper(_checkpointer),
        PitchforkTrackScraper(_checkpointer),
        TheNeedleDropAlbumScraper(_checkpointer),
        TheNeedleDropTrackScraper(_checkpointer),
    ]

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

        digest_html += "<p>Until tomorrow 🤘</p>"

        return digest_html

    def _get_dad_joke(self):
        try:
            return requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}).json()["joke"]
        except:
            return "It would seem that I've run out of dad jokes. I hope you're happy now."

    def _send_email(self, content):
        smtp = smtplib.SMTP(host="smtp.gmail.com", port=587)
        smtp.starttls()
        smtp.login(os.environ["SENDER_EMAIL"], os.environ["SENDER_PASSWORD"])
        msg = MIMEMultipart()
        msg["From"] = "Ume the Unicorn"
        msg["To"] = os.environ["RECIPIENT_EMAIL"]
        msg["Subject"] = "🎧 Best New Music - {} 🎧".format(datetime.now().strftime("%d/%m/%Y"))
        msg.attach(MIMEText(content, "html"))
        smtp.send_message(msg)
        smtp.quit()

if __name__ == "__main__":
    BestNewMusicDigest().run()
