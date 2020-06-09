# pylint: disable=bare-except, import-outside-toplevel, missing-class-docstring, missing-function-docstring, missing-module-docstring

import os
import unittest
from importlib import reload

from tests import fixtures


class TestFactory(unittest.TestCase):

    def setUp(self):
        fixtures.set_env_vars()

        os.environ["PITCHFORK_ALBUMS"] = "false"
        os.environ["PITCHFORK_TRACKS"] = "false"
        os.environ["SPUTNIKMUSIC_ALBUMS"] = "false"
        os.environ["THE_NEEDLE_DROP_ALBUMS"] = "false"
        os.environ["THE_NEEDLE_DROP_TRACKS"] = "false"

        from best_new_music_digest import settings
        self.__settings = settings
        from best_new_music_digest.scrapers import factory
        self.__factory = factory

    def tearDown(self):
        fixtures.set_env_vars()
        try:
            reload(self.__settings)
        except:
            pass

    def test_get_scrapers_pitchfork_albums(self):
        os.environ["PITCHFORK_ALBUMS"] = "true"
        self.__test_get_scrapers(["Pitchfork Albums"])

    def test_get_scrapers_pitchfork_tracks(self):
        os.environ["PITCHFORK_TRACKS"] = "true"
        self.__test_get_scrapers(["Pitchfork Tracks"])

    def test_get_scrapers_sputnikmusic_albums(self):
        os.environ["SPUTNIKMUSIC_ALBUMS"] = "true"
        self.__test_get_scrapers(["Sputnikmusic Albums"])

    def test_get_scrapers_the_needle_drop_albums(self):
        os.environ["THE_NEEDLE_DROP_ALBUMS"] = "true"
        self.__test_get_scrapers(["The Needle Drop Albums"])

    def test_get_scrapers_the_needle_drop_tracks(self):
        os.environ["THE_NEEDLE_DROP_TRACKS"] = "true"
        self.__test_get_scrapers(["The Needle Drop Tracks"])

    def test_get_scrapers_all_scrapers(self):
        os.environ["PITCHFORK_ALBUMS"] = "true"
        os.environ["PITCHFORK_TRACKS"] = "true"
        os.environ["SPUTNIKMUSIC_ALBUMS"] = "true"
        os.environ["THE_NEEDLE_DROP_ALBUMS"] = "true"
        os.environ["THE_NEEDLE_DROP_TRACKS"] = "true"

        self.__test_get_scrapers([
            "Pitchfork Albums",
            "Pitchfork Tracks",
            "Sputnikmusic Albums",
            "The Needle Drop Albums",
            "The Needle Drop Tracks",
        ])

    def __test_get_scrapers(self, expected_scrapers):
        reload(self.__settings)

        actual_scrapers = self.__factory.get_scrapers()

        assert len(actual_scrapers) == len(expected_scrapers)

        for scraper in actual_scrapers:
            assert scraper.get_title() in expected_scrapers
