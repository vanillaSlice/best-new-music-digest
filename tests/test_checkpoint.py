# pylint: disable=import-outside-toplevel, missing-class-docstring, missing-function-docstring, missing-module-docstring

import unittest
from unittest.mock import patch

import mongomock

from tests import fixtures


class TestCheckpointer(unittest.TestCase):

    def setUp(self):
        fixtures.set_env_vars()
        from best_new_music_digest.checkpoint import Checkpointer
        with patch("best_new_music_digest.checkpoint.MongoClient") as client:
            client.return_value = mongomock.MongoClient()
            self.__checkpointer = Checkpointer()

    def test_get_checkpoint_new(self):
        assert self.__checkpointer.get_checkpoint("checkpoint-1") == ""

    def test_get_checkpoint_old(self):
        self.__checkpointer.save_checkpoint("checkpoint-1", "some-link")
        assert self.__checkpointer.get_checkpoint("checkpoint-1") == "some-link"
