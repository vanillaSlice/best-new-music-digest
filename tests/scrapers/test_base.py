# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring, no-self-use, too-few-public-methods

import unittest

from best_new_music_digest.scrapers.base import Scraper
from tests import fixtures


class MockScraper(Scraper):

    def __init__(self):
        super().__init__(fixtures.mock_checkpointer(), "scraper", "scraper-link")

class MockErrorScraper(Scraper):

    def __init__(self):
        super().__init__(fixtures.mock_checkpointer(), "error", "error-link")

    def _get_items(self):
        raise Exception()

class TestScraper(unittest.TestCase):

    def test_scrape(self):
        assert MockScraper().scrape() == {
            "title": "scraper",
            "link": "scraper-link",
            "items": [],
            "errors": False,
        }

    def test_scrape_with_error(self):
        assert MockErrorScraper().scrape() == {
            "title": "error",
            "link": "error-link",
            "items": [],
            "errors": True,
        }
