#!/usr/bin/env python3

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from jinja2 import Environment, FileSystemLoader

from best_new_music_digest import settings
from best_new_music_digest.scrapers import factory


class BestNewMusicDigest:

    def __init__(self):
        self._scrapers = factory.get_scrapers()

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
