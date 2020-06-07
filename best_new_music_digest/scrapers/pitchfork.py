# pylint: disable=invalid-name, too-few-public-methods

"""
Pitchfork scrapers.
"""

import requests
from bs4 import BeautifulSoup

from best_new_music_digest.scrapers import Scraper


class AlbumScraper(Scraper):
    """
    Pitchfork album scraper.
    """

    __BASE_URL = "https://www.pitchfork.com"
    __SCRAPE_URL = f"{__BASE_URL}/reviews/best/albums/"

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "Pitchfork Albums", self.__SCRAPE_URL)

    def _get_items(self):
        items = []

        response = requests.get(self.__SCRAPE_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        checkpoint = self._get_checkpoint()

        for div in soup.find_all("div", "review"):
            link = f"{self.__BASE_URL}{div.find('a').get('href')}"

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
