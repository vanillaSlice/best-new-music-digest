# pylint: disable=import-outside-toplevel, missing-class-docstring, missing-function-docstring, missing-module-docstring, too-many-public-methods

import os
import unittest
from importlib import reload

import pytest

from tests import fixtures


class TestSettings(unittest.TestCase):

    def setUp(self):
        fixtures.set_env_vars()
        from best_new_music_digest import settings
        self.__settings = settings

    def test_always_email_not_set(self):
        self.__test_missing_property("ALWAYS_EMAIL", expected_value=False)

    def test_always_email_set(self):
        self.__test_boolean_property("ALWAYS_EMAIL")

    def test_dad_joke_not_set(self):
        self.__test_missing_property("DAD_JOKE", expected_value=True)

    def test_dad_joke_set(self):
        self.__test_boolean_property("DAD_JOKE")

    def test_mongodb_uri_not_set(self):
        self.__test_missing_property("MONGODB_URI", expect_exception=True)

    def test_mongodb_uri_set(self):
        self.__test_string_property("MONGODB_URI")

    def test_pitchfork_albums_not_set(self):
        self.__test_missing_property("PITCHFORK_ALBUMS", expected_value=True)

    def test_pitchfork_albums_set(self):
        self.__test_boolean_property("PITCHFORK_ALBUMS")

    def test_pitchfork_tracks_not_set(self):
        self.__test_missing_property("PITCHFORK_TRACKS", expected_value=True)

    def test_pitchfork_tracks_set(self):
        self.__test_boolean_property("PITCHFORK_TRACKS")

    def test_recipient_email_not_set(self):
        self.__test_missing_property("RECIPIENT_EMAIL", expect_exception=True)

    def test_recipient_email_set(self):
        self.__test_string_property("RECIPIENT_EMAIL")

    def test_sender_email_not_set(self):
        self.__test_missing_property("SENDER_EMAIL", expect_exception=True)

    def test_sender_email_set(self):
        self.__test_string_property("SENDER_EMAIL")

    def test_sender_password_not_set(self):
        self.__test_missing_property("SENDER_PASSWORD", expect_exception=True)

    def test_sender_password_set(self):
        self.__test_string_property("SENDER_PASSWORD")

    def test_sputnikmusic_albums_not_set(self):
        self.__test_missing_property("SPUTNIKMUSIC_ALBUMS", expected_value=True)

    def test_sputnikmusic_albums_set(self):
        self.__test_boolean_property("SPUTNIKMUSIC_ALBUMS")

    def test_the_needle_drop_albums_not_set(self):
        self.__test_missing_property("THE_NEEDLE_DROP_ALBUMS", expected_value=True)

    def test_the_needle_drop_albums_set(self):
        self.__test_boolean_property("THE_NEEDLE_DROP_ALBUMS")

    def test_the_needle_drop_tracks_not_set(self):
        self.__test_missing_property("THE_NEEDLE_DROP_TRACKS", expected_value=True)

    def test_the_needle_drop_tracks_set(self):
        self.__test_boolean_property("THE_NEEDLE_DROP_TRACKS")

    def test_youtube_api_key_not_set_when_required(self):
        os.environ["THE_NEEDLE_DROP_ALBUMS"] = "true"
        os.environ["THE_NEEDLE_DROP_TRACKS"] = "true"
        self.__test_missing_property("YOUTUBE_API_KEY", expect_exception=True)

        os.environ["THE_NEEDLE_DROP_ALBUMS"] = "true"
        os.environ["THE_NEEDLE_DROP_TRACKS"] = "false"
        self.__test_missing_property("YOUTUBE_API_KEY", expect_exception=True)

        os.environ["THE_NEEDLE_DROP_ALBUMS"] = "false"
        os.environ["THE_NEEDLE_DROP_TRACKS"] = "true"
        self.__test_missing_property("YOUTUBE_API_KEY", expect_exception=True)

    def test_youtube_api_key_not_set_when_not_required(self):
        os.environ["THE_NEEDLE_DROP_ALBUMS"] = "false"
        os.environ["THE_NEEDLE_DROP_TRACKS"] = "false"
        self.__test_missing_property("YOUTUBE_API_KEY", expected_value="None")

    def test_youtube_api_key_set(self):
        self.__test_string_property("YOUTUBE_API_KEY")

    def test_all_required_properties_missing(self):
        del os.environ["MONGODB_URI"]
        del os.environ["RECIPIENT_EMAIL"]
        del os.environ["SENDER_EMAIL"]
        del os.environ["SENDER_PASSWORD"]
        with pytest.raises(Exception) as exception:
            reload(self.__settings)
        assert str(exception.value) == "Missing mandatory properties: ['MONGODB_URI', " \
                                       "'RECIPIENT_EMAIL', 'SENDER_EMAIL', 'SENDER_PASSWORD']."

    def __test_missing_property(self, property_name, expect_exception=False, expected_value=None):
        if property_name in os.environ:
            del os.environ[property_name]

        if expect_exception:
            with pytest.raises(Exception) as exception:
                reload(self.__settings)
            assert str(exception.value) == f"Missing mandatory properties: ['{property_name}']."
        else:
            reload(self.__settings)
            assert getattr(self.__settings, property_name) == expected_value

    def __test_boolean_property(self, property_name):
        self.__test_property(property_name, "true", True)
        self.__test_property(property_name, "false", False)

    def __test_string_property(self, property_name):
        self.__test_property(property_name, "some-string-property", "some-string-property")

    def __test_property(self, property_name, value, expected_value):
        os.environ[property_name] = value
        reload(self.__settings)
        assert getattr(self.__settings, property_name) == expected_value
