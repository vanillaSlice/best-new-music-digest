# pylint: disable=import-outside-toplevel, missing-class-docstring, missing-function-docstring, missing-module-docstring

import json
from unittest.mock import patch

from tests import fixtures


class TestEmail(fixtures.TestBase):

    def setUp(self):
        super().setUp()

        from best_new_music_digest import email
        self.__email = email

    @patch("best_new_music_digest.email.SendGridAPIClient.send")
    def test_send_email_no_digest_no_errors(self, send):
        self.__email.send_email([
            {
                "items": [],
                "errors": False,
            },
            {
                "items": [],
                "errors": False,
            },
        ])

        send.assert_not_called()

    @patch("best_new_music_digest.email.SendGridAPIClient.send")
    def test_send_email_no_digest_no_errors_always_send(self, send):
        self._settings.ALWAYS_EMAIL = True

        self.__email.send_email([
            {
                "items": [],
                "errors": False,
            },
            {
                "items": [],
                "errors": False,
            },
        ])

        send.assert_called()

    @patch("best_new_music_digest.email.SendGridAPIClient.send")
    def test_send_email_no_digest_with_errors(self, send):
        self.__email.send_email([
            {
                "items": [],
                "errors": False,
            },
            {
                "items": [],
                "errors": True,
            },
        ])

        send.assert_called()

    @patch("best_new_music_digest.email.SendGridAPIClient.send")
    def test_send_email_digest(self, send):
        self.__email.send_email([
            json.loads(self._load_test_data("the_needle_drop_albums_output_with_checkpoint.json")),
            json.loads(self._load_test_data("the_needle_drop_tracks_output_with_checkpoint.json")),
        ])

        send.assert_called()
