#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time
import unittest
from unittest.mock import Mock

from pomito import main, pomodoro, task
from pomito.plugins.ui import UIPlugin
from pomito.test import FakeMessageDispatcher, FakeTimer, PomitoTestFactory

import py
import sure

class PomodoroServiceTests(unittest.TestCase):
    """
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

    def test_get_config_gets_value_for_plugin_and_key(self):
        pass

    def test_get_config_throws_for_invalid_plugin(self):
        import configparser

        self.pomodoro_service \
            .get_config.when \
            .called_with("dummy_plugin", "dummy_key") \
            .should.throw(configparser.NoSectionError)

    def test_session_started_is_called_with_correct_session_count(self):
        self.pomodoro_service.signal_session_started \
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_session(self.dummy_task)

        self.dummy_callback.assert_called_once_with(None,
                                               session_count=0,
                                               session_duration=1500,
                                               task=self.dummy_task)

        self.pomodoro_service.signal_session_started \
            .disconnect(self.dummy_callback)
        self.pomodoro_service.stop_session()

    def test_session_stopped_for_reason_interrupt(self):
        self.pomodoro_service.signal_session_stopped \
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_session(self.dummy_task)
        self.pomodoro_service.stop_session()

        self.dummy_callback.assert_called_once_with(None, session_count=0,
                task=self.dummy_task, reason='interrupt')

        self.pomodoro_service.signal_session_stopped \
            .disconnect(self.dummy_callback)

    def test_session_stopped_for_reason_complete(self):
        self.pomodoro_service.signal_session_stopped \
            .connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_session(self.dummy_task)
        self.pomodoro_service._timer.trigger_callback('complete')

        self.dummy_callback.assert_called_once_with(None, session_count=1,
                task=self.dummy_task, reason='complete')

        self.pomodoro_service.signal_session_stopped \
            .disconnect(self.dummy_callback)

    def test_break_started_shortbreak(self):
        self._test_break_started("short_break")

    def test_break_started_longbreak(self):
        self.pomodoro_service._session_count = 4
        self._test_break_started("long_break")

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
        self.pomodoro_service.signal_break_stopped.connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_break()
        self.pomodoro_service._timer.trigger_callback('complete')

        self.dummy_callback.assert_called_once_with(None,
                break_type='short_break', reason='complete')

        self.pomodoro_service.signal_break_stopped.disconnect(self.dummy_callback)

    def test_break_stopped_shortbreak_for_reason_interrupt(self):
        self.pomodoro_service.signal_break_stopped.connect(self.dummy_callback, weak=False)

        self.pomodoro_service.start_break()
        self.pomodoro_service.stop_break()

        self.dummy_callback.assert_called_once_with(None,
                break_type='short_break', reason='interrupt')

        self.pomodoro_service.signal_break_stopped.disconnect(self.dummy_callback)

    def test_break_stopped_longbreak_for_interrupt(self):
        self.pomodoro_service._session_count = 4
        self.pomodoro_service.signal_break_stopped.connect(self.dummy_callback,
                weak=False)

        self.pomodoro_service.start_break()
        self.pomodoro_service.stop_break()

        self.dummy_callback.assert_called_once_with(None,
                break_type='long_break', reason='interrupt')

        self.pomodoro_service.signal_break_stopped.disconnect(self.dummy_callback)

    def test_get_data_dir_returns_correct_default(self):
        expected_data_dir = os.path.join(os.getenv("XDG_DATA_HOME"), "pomito")
        if sys.platform.startswith("win"):
            expected_data_dir = os.path.join(os.path.expanduser("~"), "pomito")

        data_dir = self.pomodoro_service.get_data_dir()

        data_dir.should.be.equal(expected_data_dir)

    def test_get_db_returns_a_valid_database(self):
        test_db = "dummy_db"
        pomodoro_service = pomodoro.Pomodoro(main.Pomito(database=test_db))

        pomodoro_service.get_db().should.be.equal(test_db)

    @py.test.mark.perf
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

        self.mock_callback.call_count.should.be.equal(2)
        self.assertListEqual(self.mock_callback.call_args_list, [(('increment',), {}),
            (('complete',), {})], 'invalid notify_reason')

    def test_mock_callback_reason_interrupt(self):
        timer = pomodoro.Timer(10, self.mock_callback, 1)

        timer.start()
        timer.stop()
        time.sleep(0.1)

        self.mock_callback.call_count.should.be.equal(1)
        self.assertListEqual(self.mock_callback.call_args_list, [(('interrupt',),
            {})], 'invalid notify_reason')

    @py.test.mark.perf
    def test_callback_granular(self):
        duration = 60.00
        delta_granular = 1.0    # windows
        if sys.platform.startswith("linux"):
            delta_granular = 0.03

        timer = pomodoro.Timer(duration, self.dummy_callback)
        self.timestamp_start = time.time()
        timer.start()
        time.sleep(duration + 2)

        self.reason.should.equal('complete')
        self.assertAlmostEqual(self.delta, duration, delta=delta_granular)


class DummyUIPlugin(UIPlugin):
    def __init__(self):
        self.timestamp = 100.0
        return

    def run(self):
        pass

    def notify_session_started(self, sender, **kwargs):
        self.timestamp = time.time()
        return

    def initialize(self):
        pass
