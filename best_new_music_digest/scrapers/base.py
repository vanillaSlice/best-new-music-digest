# pylint: disable=broad-except, no-self-use, too-few-public-methods

"""
Base scrapers.
"""

import logging


class Scraper:
    """
    Base scraper.
    """

    def __init__(self, checkpointer, title, link):
        self.__checkpointer = checkpointer
        self.__title = title
        self.__link = link
        self.__saved_checkpoint = False

    def scrape(self):
        """
        Scrapes music information.
        """

        errors = False

        try:
            items = self._get_items()
        except Exception as exception:
            logging.error(exception)
            items = []
            errors = True

        return {
            "title": self.__title,
            "link": self.__link,
            "items": items,
            "errors": errors,
        }

    def _get_items(self):
        return []

    def _get_checkpoint(self):
        return self.__checkpointer.get_checkpoint(self.__title)

    def _save_checkpoint(self, link):
        if not self.__saved_checkpoint:
            self.__checkpointer.save_checkpoint(self.__title, link)
            self.__saved_checkpoint = True

    def get_title(self):
        """
        Return scraper title.
        """

        return self.__title
