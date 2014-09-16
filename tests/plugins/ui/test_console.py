"""Tests for console user interface
"""

import unittest
from unittest.mock import Mock

from click.testing import CliRunner
from sure import expect

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
        expect(self.console.prompt).to.equal("pomito> ")

    def test_shell_provides_start_command(self):
        out = self._invoke_command("start", "0")
        expect(out.exception).to.be.none
        out.exit_code.should.be.equal(0)

    def test_start_starts_a_pomodoro_session(self):
        self.pomodoro_service.signal_session_started\
            .connect(self.dummy_callback, weak=False)

        out = self._invoke_command("start", "0")

        expect(out.exit_code).to.be(0)
        expect(self.dummy_callback.call_count).to.equal(1)

        self.pomodoro_service.signal_session_started\
            .disconnect(self.dummy_callback)

    def _invoke_command(self, command, args):
        out = self.runner.invoke(pomito_shell, args=[command, args],
                                 catch_exceptions=False)
        return out
