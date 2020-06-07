# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring

import unittest

from tests import fixtures


class TestCheckpointer(unittest.TestCase):

    def setUp(self):
        self.__checkpointer = fixtures.mock_checkpointer()

    def test_get_checkpoint_new(self):
        assert self.__checkpointer.get_checkpoint("checkpoint-1") == ""

    def test_get_checkpoint_old(self):
        self.__checkpointer.save_checkpoint("checkpoint-2", "some-link")
        assert self.__checkpointer.get_checkpoint("checkpoint-2") == "some-link"
