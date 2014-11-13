"""Tests for console user interface
"""

import unittest
from unittest.mock import Mock, MagicMock

from click.testing import CliRunner
from sure import expect

from pomito import task
from pomito.plugins.ui.console import *
from pomito.test import FakeTaskPlugin, PomitoTestFactory

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

        self.task_list = []
        for i in range(12):
            t = MagicMock(spec=task.Task)
            t.__str__.return_value = str(i)
            self.task_list.append(t)
        self.pomodoro_service._pomito_instance\
            .task_plugin = FakeTaskPlugin()
        # Task list should be a generator as per TaskPlugin.get_tasks
        self.pomodoro_service._pomito_instance\
            .task_plugin.task_list = (t for t in self.task_list)
        self.dummy_callback = Mock()

    def tearDown(self):
        # pylint: disable=protected-access
        self.pomodoro_service._pomito_instance.exit()

    def test_completenames_should_list_matching_commands(self):
        names = self.console.completenames("st")
        expect(names).to.equal(["start", "stop"])

    def test_completenames_should_not_list_not_match_commands(self):
        names = self.console.completenames("nonexist")
        expect(names).to.equal([])

    def test_completenames_should_not_list_shell(self):
        names = self.console.completenames("")
        expect(names).to_not.contain("shell")

    def test_shell_text_should_be_pomito(self):
        expect(self.console.prompt).to.equal("pomito> ")

    def test_shell_provides_start_command(self):
        out = self._invoke_command("start", "0")
        expect(out.exception).to.be.none
        out.exit_code.should.be.equal(0)

    def test_list_prints_first_ten_available_tasks(self):
        more_task_msg = "\nShowing first 10 tasks, use `list *`"\
            + "to show all tasks.\n"
        expected_out = "\n".join(map(str, self.task_list[0:11])) + "\n"

        out = self._invoke_command("list")

        expect(out.exit_code).to.equal(0)
        expect(out.output).to.equal(expected_out + more_task_msg)

    def test_list_prints_tasks_matching_filter(self):
        expected_task_list = [self.task_list[1], self.task_list[10],
                              self.task_list[11]]
        expected_out = "\n".join(map(str, expected_task_list)) + "\n"

        out = self._invoke_command("list", "1")

        expect(out.exit_code).to.equal(0)
        expect(out.output).to.equal(expected_out)

    def test_list_star_prints_all_tasks(self):
        expected_out = "\n".join(map(str, self.task_list)) + "\n"

        out = self._invoke_command("list", "*")

        expect(out.exit_code).to.equal(0)
        expect(out.output).to.equal(expected_out)

    def test_start_starts_a_pomodoro_session(self):
        self.pomodoro_service.signal_session_started\
            .connect(self.dummy_callback, weak=False)

        out = self._invoke_command("start", "0")

        expect(out.exit_code).to.be(0)
        expect(self.dummy_callback.call_count).to.equal(1)

        self.pomodoro_service.signal_session_started\
            .disconnect(self.dummy_callback)

    def test_stop_stops_a_pomodoro_session(self):
        self.pomodoro_service.signal_session_stopped\
            .connect(self.dummy_callback, weak=False)

        out = self._invoke_command("stop")

        expect(out.exit_code).to.be(0)
        expect(self.dummy_callback.call_count).to.equal(1)

        self.pomodoro_service.signal_session_stopped\
            .disconnect(self.dummy_callback)

    def test_stop_shows_message_if_no_active_session(self):
        pass

    def test_quit_should_return_exit_code_one(self):
        out = self._invoke_command("quit")
        expect(out.exit_code).to.be(1)

    def test_quit_should_print_exit_message(self):
        out = self._invoke_command("quit")
        expect(out.output).to.equal("Good bye!\n")

    def test_eof_should_return_exit_code_one(self):
        out = self._invoke_command("EOF")
        expect(out.exit_code).to.be(1)

    def test_eof_should_print_exit_message(self):
        out = self._invoke_command("EOF")
        expect(out.output).to.equal("Good bye!\n")

    def _invoke_command(self, command, args=None):
        args_list = [command, args] if args is not None else [command]
        out = self.runner.invoke(pomito_shell, args_list,
                                 catch_exceptions=False)
        print(out.output)
        return out
