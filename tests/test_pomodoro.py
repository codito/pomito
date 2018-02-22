# -*- coding: utf-8 -*-
"""Tests for pomodoro service."""
import os
import sys
import time
import unittest
import pytest

from unittest.mock import Mock

from pomito import main, pomodoro, task
from pomito.plugins.ui import UIPlugin
from pomito.plugins.task import TaskPlugin
from pomito.test import PomitoTestFactory


class PomodoroServiceTests(unittest.TestCase):
    """Tests for pomodoro service.

    - test_break_stopped_without_start
    - test_session_stopped_without_start
    - test_interruption_stopped_without_start
    - test_get_config_gets_value_for_plugin_and_key
    - test_get_config_throws_for_invalid_plugin
    - test_get_config_throws_for_invalid_key
    - test_get_config_throws_for_invalid_inifile
    """

    def setUp(self):
        test_factory = PomitoTestFactory()
        self.pomodoro_service = test_factory.create_fake_service()

        self.dummy_task = Mock(spec=task.Task)
        self.dummy_callback = Mock()

    def tearDown(self):
        self.pomodoro_service._pomito_instance.exit()

    def test_current_task_none_for_default_pomodoro(self):
        assert self.pomodoro_service.current_task is None

    def test_current_task_is_set_for_running_session(self):
        self.pomodoro_service.start_session(self.dummy_task)

        assert self.pomodoro_service.current_task == self.dummy_task

        self.pomodoro_service.stop_session()

    def test_current_task_none_after_session_stop(self):
        self.pomodoro_service.start_session(self.dummy_task)
        self.pomodoro_service.stop_session()

        assert self.pomodoro_service.current_task is None

    def test_get_config_gets_value_for_plugin_and_key(self):
        pass

    def test_get_config_returns_none_invalid_plugin(self):
        val = self.pomodoro_service.get_config("dummy_plugin", "dummy_key")

        assert val is None

    def test_get_task_plugins_gets_list_of_all_task_plugins(self):
        from pomito import plugins
        plugins.PLUGINS = {'a': plugins.task.nulltask.NullTask(None),
                           'b': self.pomodoro_service}
        task_plugins = self.pomodoro_service.get_task_plugins()

        assert task_plugins == [plugins.PLUGINS['a']]

    def test_get_tasks_returns_tasks_for_the_user(self):
        self.pomodoro_service.get_tasks()

        self.pomodoro_service \
            ._pomito_instance \
            .task_plugin.get_tasks.assert_called_once_with()

    def test_get_tasks_by_filter_returns_tasks_match_filter(self):
        self.pomodoro_service.get_tasks_by_filter("dummy_filter")

        self.pomodoro_service \
            ._pomito_instance \
            .task_plugin.get_tasks_by_filter \
            .assert_called_once_with("dummy_filter")

    def test_get_task_by_id_returns_task_matching_task_idish(self):
        self.pomodoro_service.get_task_by_id(10)

        self.pomodoro_service \
            ._pomito_instance \
            .task_plugin.get_task_by_id \
            .assert_called_once_with(10)

    def test_start_session_throws_if_no_task_is_provided(self):
        self.assertRaises(Exception, self.pomodoro_service.start_session, None)

    def test_stop_session_waits_for_timer_thread_to_join(self):
        self.pomodoro_service.start_session(self.dummy_task)
        assert self.pomodoro_service._timer.is_alive()

        self.pomodoro_service.stop_session()
        assert self.pomodoro_service._timer.is_alive() is False

    def test_stop_break_waits_for_timer_thread_to_join(self):
        self.pomodoro_service.start_break()
        assert self.pomodoro_service._timer.is_alive()

        self.pomodoro_service.stop_break()
        assert self.pomodoro_service._timer.is_alive() is False

    def test_session_started_is_called_with_correct_session_count(self):
        self.pomodoro_service.signal_session_started \
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_session(self.dummy_task)

        self.dummy_callback.assert_called_once_with(None,
                                                    session_count=0,
                                                    session_duration=600,
                                                    task=self.dummy_task)

        self.pomodoro_service.signal_session_started \
            .disconnect(self.dummy_callback)
        self.pomodoro_service.stop_session()

    def test_session_stopped_for_reason_interrupt(self):
        self.pomodoro_service.signal_session_stopped \
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_session(self.dummy_task)
        self.pomodoro_service.stop_session()

        self.dummy_callback.\
            assert_called_once_with(None, session_count=0,
                                    task=self.dummy_task,
                                    reason=pomodoro.TimerChange.INTERRUPT)

        self.pomodoro_service.signal_session_stopped \
            .disconnect(self.dummy_callback)

    def test_session_stopped_for_reason_complete(self):
        self.pomodoro_service.signal_session_stopped \
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_session(self.dummy_task)
        self.pomodoro_service._timer.trigger_callback(pomodoro.TimerChange.COMPLETE)

        self.dummy_callback.assert_called_once_with(None, session_count=1,
                                                    task=self.dummy_task,
                                                    reason=pomodoro.TimerChange.COMPLETE)

        self.pomodoro_service.signal_session_stopped\
            .disconnect(self.dummy_callback)

    def test_break_started_shortbreak(self):
        self._test_break_started(pomodoro.TimerType.SHORT_BREAK)

    def test_break_started_longbreak(self):
        self.pomodoro_service._session_count = 4
        self._test_break_started(pomodoro.TimerType.LONG_BREAK)

    def _test_break_started(self, break_type):
        self.pomodoro_service.signal_break_started \
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_break()

        self.dummy_callback.assert_called_once_with(None,
                                                    break_type=break_type)

        self.pomodoro_service.stop_break()
        self.pomodoro_service.signal_break_started \
            .disconnect(self.dummy_callback)

    def test_break_stopped_shortbreak_for_reason_complete(self):
        self.pomodoro_service.signal_break_stopped\
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_break()
        self.pomodoro_service._timer.trigger_callback(pomodoro.TimerChange.COMPLETE)

        self.dummy_callback.assert_called_once_with(None,
                                                    break_type=pomodoro.TimerType.SHORT_BREAK,
                                                    reason=pomodoro.TimerChange.COMPLETE)

        self.pomodoro_service.signal_break_stopped\
            .disconnect(self.dummy_callback)

    def test_break_stopped_shortbreak_for_reason_interrupt(self):
        self.pomodoro_service.signal_break_stopped\
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_break()
        self.pomodoro_service.stop_break()

        self.dummy_callback.assert_called_once_with(None,
                                                    break_type=pomodoro.TimerType.SHORT_BREAK,
                                                    reason=pomodoro.TimerChange.INTERRUPT)

        self.pomodoro_service.signal_break_stopped\
            .disconnect(self.dummy_callback)

    def test_break_stopped_longbreak_for_interrupt(self):
        self.pomodoro_service._session_count = 4
        self.pomodoro_service.signal_break_stopped\
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_break()
        self.pomodoro_service.stop_break()

        self.dummy_callback.assert_called_once_with(None,
                                                    break_type=pomodoro.TimerType.LONG_BREAK,
                                                    reason=pomodoro.TimerChange.INTERRUPT)

        self.pomodoro_service.signal_break_stopped\
            .disconnect(self.dummy_callback)

    def test_get_data_dir_returns_correct_default(self):
        expected_data_dir = os.path.join(os.path.expanduser("~"), "pomito")
        if sys.platform.startswith("linux"):
            home_dir = os.getenv("HOME")
            alt_data_dir = os.path.join(home_dir, ".local/share")
            expected_data_dir = os.path\
                .join(os.getenv("XDG_DATA_HOME") or alt_data_dir, "pomito")

        data_dir = self.pomodoro_service.get_data_dir()

        assert data_dir == expected_data_dir

    def test_get_db_returns_a_valid_database(self):
        test_db = "dummy_db"
        pomodoro_service = pomodoro.Pomodoro(main.Pomito(database=test_db))

        assert pomodoro_service.get_db() == test_db

    @pytest.mark.perf
    def test_session_started_perf(self):
        t = Mock(spec=task.Task)
        pomito = main.Pomito(None)
        pomito.ui_plugin = DummyUIPlugin()
        pomito.task_plugin = Mock(spec=TaskPlugin)
        pomito._message_dispatcher.start()
        pomito.pomodoro_service.signal_session_started \
              .connect(pomito.ui_plugin.notify_session_started, weak=False)

        time_start = time.time()    # initial timestamp
        pomito.pomodoro_service.start_session(t)
        time.sleep(1)
        time_end = pomito.ui_plugin.timestamp

        self.assertAlmostEqual(time_start, time_end, delta=0.1)
        pomito.ui_plugin.timestamp = None
        pomito.pomodoro_service.stop_session()
        pomito.exit()


class TimerTests(unittest.TestCase):
    def setUp(self):
        self.timestamp_start = 0.0
        self.timestamp_end = 0.0
        self.delta = 0.0
        self.mock_callback = Mock()

    def tearDown(self):
        self.timestamp_start = self.timestamp_end = self.delta = 0.0

    def dummy_callback(self, reason='whatever'):
        self.timestamp_end = time.time()
        self.delta += (self.timestamp_end - self.timestamp_start)
        self.timestamp_start = self.timestamp_end
        self.reason = reason

    def test_mock_callback_reason_increment_and_complete(self):
        timer = pomodoro.Timer(0.2, self.mock_callback, 0.1)

        timer.start()
        time.sleep(0.3)

        assert self.mock_callback.call_count == 2
        self.assertListEqual(self.mock_callback.call_args_list,
                             [((pomodoro.TimerChange.INCREMENT,), {}), ((pomodoro.TimerChange.COMPLETE,), {})],
                             'invalid notify_reason')

    def test_mock_callback_reason_interrupt(self):
        timer = pomodoro.Timer(10, self.mock_callback, 1)

        timer.start()
        timer.stop()
        time.sleep(0.1)

        assert self.mock_callback.call_count == 1
        self.assertListEqual(self.mock_callback.call_args_list,
                             [((pomodoro.TimerChange.INTERRUPT,), {})],
                             'invalid notify_reason')

    def test_start_throws_when_called_on_same_thread(self):
        def callback_with_catch(reason):
            try:
                timer.start()
                assert False    # expect previous call to throw
            except RuntimeError:
                pass
        timer = pomodoro.Timer(10, callback_with_catch, 1)

        timer.start()
        timer.stop()
        time.sleep(0.1)

    def test_stop_throws_when_called_on_same_thread(self):
        def callback_with_catch(reason):
            try:
                timer.stop()
                assert False    # expect previous call to throw
            except RuntimeError:
                pass
        timer = pomodoro.Timer(10, callback_with_catch, 1)

        timer.start()
        timer.stop()
        time.sleep(0.1)

    @pytest.mark.perf
    def test_callback_granular(self):
        duration = 60.00
        delta_granular = 1.0    # windows
        if sys.platform.startswith("linux"):
            delta_granular = 0.03

        timer = pomodoro.Timer(duration, self.dummy_callback)
        self.timestamp_start = time.time()
        timer.start()
        time.sleep(duration + 2)

        assert self.reason == pomodoro.TimerChange.COMPLETE
        self.assertAlmostEqual(self.delta, duration, delta=delta_granular)


class DummyUIPlugin(UIPlugin):
    def __init__(self):
        """Create an instance of dummy plugin."""
        self.timestamp = 100.0
        return

    def run(self):
        pass

    def notify_session_started(self, sender, **kwargs):
        self.timestamp = time.time()
        return

    def initialize(self):
        pass
