# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring, too-few-public-methods

from best_new_music_digest.scrapers.base import Scraper
from tests import fixtures


class MockScraper(Scraper):

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "scraper", "scraper-link")

class MockErrorScraper(Scraper):

    def __init__(self, checkpointer):
        super().__init__(checkpointer, "error", "error-link")

    def _get_items(self):
        raise Exception()

class TestScraper(fixtures.TestBase):

    def test_scrape(self):
        assert MockScraper(self._checkpointer).scrape() == {
            "title": "scraper",
            "link": "scraper-link",
            "items": [],
            "errors": False,
        }

    def test_scrape_with_error(self):
        assert MockErrorScraper(self._checkpointer).scrape() == {
            "title": "error",
            "link": "error-link",
            "items": [],
            "errors": True,
        }
