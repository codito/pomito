"""Tests for console user interface
"""

import unittest
from unittest.mock import Mock

from pomito import task
from pomito.plugins.ui.console import *
from pomito.test import FakeMessageDispatcher, PomitoTestFactory

# pylint: disable=too-many-public-methods, invalid-name, missing-docstring
class ConsoleTests(unittest.TestCase):
    """Test suite for shell."""

    def setUp(self):
        test_factory = PomitoTestFactory()
        self.pomodoro_service = test_factory.create_fake_service()
        self.console = Console(self.pomodoro_service)

        self.dummy_task = Mock(spec=task.Task)
        self.dummy_callback = Mock()

    def tearDown(self):
        # pylint: disable=protected-access
        self.pomodoro_service._pomito_instance.exit()

    def test_shell_text_should_be_pomito(self):
        self.console.prompt.should.equal("pomito> ")

    def test_start_starts_a_pomodoro_session(self):
        # TODO
        pass
