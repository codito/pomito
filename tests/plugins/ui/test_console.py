"""Tests for console user interface
"""

import unittest
from unittest.mock import Mock

from click.testing import CliRunner

from pomito import task
from pomito.plugins.ui.console import *
from pomito.test import FakeMessageDispatcher, PomitoTestFactory

# pylint: disable=too-many-public-methods, invalid-name, missing-docstring
class ConsoleTests(unittest.TestCase):
    """Test suite for shell."""

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

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

    def test_shell_pomodoro_service_is_none_by_default(self):
        Console.pomodoro_service.should.be.none

    def test_shell_pomodoro_service_is_set(self):
        self.console.pomodoro_service.should.be(self.pomodoro_service)

    def test_shell_provides_start_command(self):
        out = self._invoke_command("start")
        out.exception.should.be.none
        out.exit_code.should.be.equal(0)

    def test_start_starts_a_pomodoro_session(self):
        out = self._invoke_command("start")
        # TODO

    def _invoke_command(self, command):
        return self.runner.invoke(pomito_shell, args=[command])
