# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring

import json
import unittest

import requests_mock

from best_new_music_digest.scrapers import sputnikmusic
from tests import fixtures

class TestAlbumScraper(unittest.TestCase):

    def setUp(self):
        self.__checkpointer = fixtures.mock_checkpointer()
        self.__scraper = sputnikmusic.AlbumScraper(self.__checkpointer)

    def test_scrape_without_checkpoint(self):
        self.__test_scrape("sputnikmusic_albums_output_without_checkpoint.json")

    def test_scrape_with_checkpoint(self):
        self.__checkpointer.save_checkpoint(
            "Sputnikmusic Albums",
            "https://www.sputnikmusic.com/album/357694/Jeff-Rosenstock-NO-DREAM/"
        )

        self.__test_scrape("sputnikmusic_albums_output_with_checkpoint.json")

    def test_scrape_up_to_date(self):
        self.__checkpointer.save_checkpoint(
            "Sputnikmusic Albums",
            "https://www.sputnikmusic.com/album/356763/Run-the-Jewels-Run-the-Jewels-4/"
        )

        self.__test_scrape("sputnikmusic_albums_output_up_to_date.json")

    def __test_scrape(self, output):
        test_data = fixtures.load_test_data("sputnikmusic_albums_input.html")

        with requests_mock.Mocker() as req_mock:
            req_mock.get("https://www.sputnikmusic.com/bestnewmusic", text=test_data)
            items = self.__scraper.scrape()

        assert items == json.loads(fixtures.load_test_data(output))
