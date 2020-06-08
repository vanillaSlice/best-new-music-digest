# pylint: disable=import-outside-toplevel, missing-class-docstring, missing-function-docstring, missing-module-docstring

import json
import unittest

import requests_mock

from tests import fixtures


class TestAlbumScraper(unittest.TestCase):

    def setUp(self):
        self.__checkpointer = fixtures.mock_checkpointer()
        from best_new_music_digest.scrapers import the_needle_drop
        self.__scraper = the_needle_drop.AlbumScraper(self.__checkpointer)

    def test_scrape_without_checkpoint(self):
        self.__test_scrape("the_needle_drop_albums_output_without_checkpoint.json")

    def test_scrape_with_checkpoint(self):
        self.__checkpointer.save_checkpoint(
            "The Needle Drop Albums",
            "https://www.youtube.com/watch?v=OBcYr05W8Cs"
        )

        self.__test_scrape("the_needle_drop_albums_output_with_checkpoint.json")

    def test_scrape_up_to_date(self):
        self.__checkpointer.save_checkpoint(
            "The Needle Drop Albums",
            "https://www.youtube.com/watch?v=xjNG90UjuII"
        )

        self.__test_scrape("the_needle_drop_albums_output_up_to_date.json")

    def test_scrape_saves_checkpoint(self):
        self.__test_scrape("the_needle_drop_albums_output_without_checkpoint.json")
        self.__test_scrape("the_needle_drop_albums_output_up_to_date.json")

    def __test_scrape(self, output):
        test_data = fixtures.load_test_data("the_needle_drop_albums_input.json")

        with requests_mock.Mocker() as req_mock:
            req_mock.get("https://www.googleapis.com/youtube/v3/playlistItems?" \
                         "part=snippet&playlistId=PLP4CSgl7K7oo93I49tQa0TLB8qY3u7xuO&" \
                         f"key={fixtures.YOUTUBE_API_KEY}", text=test_data)
            items = self.__scraper.scrape()

        assert items == json.loads(fixtures.load_test_data(output))

class TestTrackScraper(unittest.TestCase):

    def setUp(self):
        self.__checkpointer = fixtures.mock_checkpointer()
        from best_new_music_digest.scrapers import the_needle_drop
        self.__scraper = the_needle_drop.TrackScraper(self.__checkpointer)

    def test_scrape_without_checkpoint(self):
        self.__test_scrape("the_needle_drop_tracks_output_without_checkpoint.json")

    def test_scrape_with_checkpoint(self):
        self.__checkpointer.save_checkpoint(
            "The Needle Drop Tracks",
            "https://www.youtube.com/watch?v=BH-yi1Ilekg"
        )

        self.__test_scrape("the_needle_drop_tracks_output_with_checkpoint.json")

    def test_scrape_up_to_date(self):
        self.__checkpointer.save_checkpoint(
            "The Needle Drop Tracks",
            "https://www.youtube.com/watch?v=FriRf3olBpo"
        )

        self.__test_scrape("the_needle_drop_tracks_output_up_to_date.json")

    def test_scrape_saves_checkpoint(self):
        self.__test_scrape("the_needle_drop_tracks_output_without_checkpoint.json")
        self.__test_scrape("the_needle_drop_tracks_output_up_to_date.json")

    def __test_scrape(self, output):
        items = self.__scraper.scrape()

        test_data = fixtures.load_test_data("the_needle_drop_tracks_input.json")

        with requests_mock.Mocker() as req_mock:
            req_mock.get("https://www.googleapis.com/youtube/v3/playlistItems?" \
                         "part=snippet&playlistId=PLP4CSgl7K7or84AAhr7zlLNpghEnKWu2c&" \
                         f"key={fixtures.YOUTUBE_API_KEY}", text=test_data)
            items = self.__scraper.scrape()

        assert items == json.loads(fixtures.load_test_data(output))
