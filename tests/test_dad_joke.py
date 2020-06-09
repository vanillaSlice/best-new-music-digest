# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring, no-self-use)

import unittest

import requests_mock

from best_new_music_digest.dad_joke import get_dad_joke


class TestDadJoke(unittest.TestCase):

    def test_get_dad_joke(self):
        response = {"joke": "some-joke"}

        with requests_mock.Mocker() as req_mock:
            req_mock.get("https://icanhazdadjoke.com/",
                         headers={"Accept": "application/json"},
                         json=response)
            joke = get_dad_joke()

        assert joke == "some-joke"

    def test_get_dad_joke_error(self):
        with requests_mock.Mocker() as req_mock:
            req_mock.get("https://icanhazdadjoke.com/",
                         headers={"Accept": "application/json"},
                         status_code=404)
            joke = get_dad_joke()

        assert joke == "It would seem that I've run out of dad jokes. I hope you're happy now 😞."
