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

class SputnikmusicScraper:

    _name = "Sputnikmusic Albums"
    _url = "https://www.sputnikmusic.com"

    def __init__(self, checkpointer):
        self._checkpointer = checkpointer

    def scrape(self):
        errors = False

        try:
            albums = self._get_albums()
        except Exception as e:
            logging.error(e)
            albums = []
            errors = True

        return {
            "title": self._name,
            "link": self._url + "/bestnewmusic",
            "items": albums,
            "errors": errors,
        }

    def _get_albums(self):
        albums = []

        response = requests.get(self._url + "/bestnewmusic")
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._checkpointer.get_checkpoint(self._name)
        updated_checkpoint = False

        for item in soup.find_all("td", "bestnewmusic"):
            a = item.find("a")

            entry = {
                "artist": a.find("strong").contents[0],
                "title": a.find_all("font")[1].contents[1],
                "link": self._url + a.get("href"),
            }

            if entry == checkpoint:
                break

            if not updated_checkpoint:
                self._checkpointer.save_checkpoint(self._name, entry)
                updated_checkpoint = True

            albums.append(entry)

        return albums

class PitchforkAlbumScraper:

    _name = "Pitchfork Albums"
    _url = "https://www.pitchfork.com"

    def __init__(self, checkpointer):
        self._checkpointer = checkpointer

    def scrape(self):
        errors = False

        try:
            albums = self._get_albums()
        except Exception as e:
            logging.error(e)
            albums = []
            errors = True

        return {
            "title": self._name,
            "link": self._url + "/reviews/best/albums/",
            "items": albums,
            "errors": errors,
        }

    def _get_albums(self):
        albums = []

        response = requests.get(self._url + "/reviews/best/albums/")
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._checkpointer.get_checkpoint(self._name)
        updated_checkpoint = False

        for item in soup.find_all("div", "review"):
            entry = {
                "artist": " / ".join([i.contents[0] for i in item.find("ul", "artist-list").find_all("li")]),
                "title": item.find("h2", "review__title-album").contents[0],
                "link": self._url + item.find("a", "review__link").get("href"),
            }

            if entry == checkpoint:
                break

            if not updated_checkpoint:
                self._checkpointer.save_checkpoint(self._name, entry)
                updated_checkpoint = True

            albums.append(entry)

        return albums

class PitchforkTrackScraper:

    _name = "Pitchfork Tracks"
    _url = "https://www.pitchfork.com"

    def __init__(self, checkpointer):
        self._checkpointer = checkpointer

    def scrape(self):
        errors = False

        try:
            tracks = self._get_tracks()
        except Exception as e:
            logging.error(e)
            tracks = []
            errors = True

        return {
            "title": self._name,
            "link": self._url + "/reviews/best/tracks/",
            "items": tracks,
            "errors": errors,
        }

    def _get_tracks(self):
        tracks = []

        response = requests.get(self._url + "/reviews/best/tracks/")
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._checkpointer.get_checkpoint(self._name)
        updated_checkpoint = False

        item = soup.find("div", "track-details")

        entry = {
            "artist": " / ".join([i.contents[0] for i in item.find("ul", "artist-list").find_all("li")]),
            "title": item.find("h2", "title").contents[0][1:-1],
            "link": self._url + item.find("a", "title-link").get("href"),
        }

        if entry == checkpoint:
            return []

        self._checkpointer.save_checkpoint(self._name, entry)

        tracks.append(entry)

        for item in soup.find_all("a", "track-collection-item__track-link"):
            entry = {
                "artist": " / ".join([i.contents[0] for i in item.find("ul", "artist-list").find_all("li")]),
                "title": item.find("h2", "track-collection-item__title").contents[0][1:-1],
                "link": self._url + item.get("href"),
            }

            if entry == checkpoint:
                break

            tracks.append(entry)

        return tracks

class TheNeedleDropAlbumScraper:

    _name = "The Needle Drop Albums"
    _url = "https://www.youtube.com/user/theneedledrop"

    def __init__(self, checkpointer):
        self._checkpointer = checkpointer

    def scrape(self):
        errors = False

        try:
            albums = self._get_albums()
        except Exception as e:
            logging.error(e)
            albums = []
            errors = True

        return {
            "title": self._name,
            "link": self._url,
            "items": albums,
            "errors": errors,
        }

    def _get_albums(self):
        albums = []

        response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&" \
                                "playlistId=PLP4CSgl7K7oo93I49tQa0TLB8qY3u7xuO&" \
                                "key={}".format(os.environ["YOUTUBE_API_KEY"]))

        checkpoint = self._checkpointer.get_checkpoint(self._name)
        updated_checkpoint = False

        for item in response.json()["items"]:
            snippet = item["snippet"]
            video_title = snippet["title"].split(" - ")

            entry = {
                "artist": video_title[0].strip(),
                "title": video_title[1].replace("ALBUM REVIEW", "").strip(),
                "link": "https://www.youtube.com/watch?v={}".format(snippet["resourceId"]["videoId"]),
            }

            if entry == checkpoint:
                break

            if not updated_checkpoint:
                self._checkpointer.save_checkpoint(self._name, entry)
                updated_checkpoint = True

            albums.append(entry)

        return albums

class TheNeedleDropTrackScraper:

    _url = "https://www.youtube.com/user/theneedledrop"

    def __init__(self, checkpointer):
        self._checkpointer = checkpointer

    # TODO implement this
    def scrape(self):
        tracks = []

        return {
            "title": "theneedledrop Tracks",
            "link": self._url,
            "items": tracks,
            "errors": False,
        }

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
