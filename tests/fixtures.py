# pylint: disable=import-outside-toplevel, missing-function-docstring, missing-module-docstring

import os
from unittest.mock import patch

import mongomock

ALWAYS_EMAIL = False
DAD_JOKE = True
MONGODB_URI = "some-mongodb-uri"
PITCHFORK_ALBUMS = True
PITCHFORK_TRACKS = True
RECIPIENT_EMAIL = "some-recipient-email"
SENDER_EMAIL = "some-sender-email"
SENDER_NAME = "some-sender-name"
SENDER_PASSWORD = "some-sender-password"
SPUTNIKMUSIC_ALBUMS = True
THE_NEEDLE_DROP_ALBUMS = True
THE_NEEDLE_DROP_TRACKS = True
YOUTUBE_API_KEY = "some-youtube-api-key"

def set_env_vars():
    os.environ["ALWAYS_EMAIL"] = str(ALWAYS_EMAIL)
    os.environ["DAD_JOKE"] = str(DAD_JOKE)
    os.environ["MONGODB_URI"] = MONGODB_URI
    os.environ["PITCHFORK_ALBUMS"] = str(PITCHFORK_ALBUMS)
    os.environ["PITCHFORK_TRACKS"] = str(PITCHFORK_TRACKS)
    os.environ["RECIPIENT_EMAIL"] = RECIPIENT_EMAIL
    os.environ["SENDER_EMAIL"] = SENDER_EMAIL
    os.environ["SENDER_NAME"] = SENDER_NAME
    os.environ["SENDER_PASSWORD"] = SENDER_PASSWORD
    os.environ["SPUTNIKMUSIC_ALBUMS"] = str(SPUTNIKMUSIC_ALBUMS)
    os.environ["THE_NEEDLE_DROP_ALBUMS"] = str(THE_NEEDLE_DROP_ALBUMS)
    os.environ["THE_NEEDLE_DROP_TRACKS"] = str(THE_NEEDLE_DROP_TRACKS)
    os.environ["YOUTUBE_API_KEY"] = YOUTUBE_API_KEY

def mock_checkpointer():
    set_env_vars()
    from best_new_music_digest.checkpoint import Checkpointer
    with patch("best_new_music_digest.checkpoint.MongoClient") as client:
        client.return_value = mongomock.MongoClient()
        return Checkpointer()

def load_test_data(file_name):
    with open(os.path.join(os.path.dirname(__file__), "test_data", file_name)) as test_data:
        return test_data.read()
