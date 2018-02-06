# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
"""Tests for the Main module."""

import os
import unittest
from unittest.mock import Mock, MagicMock, patch

import blinker
import tempfile
from contextlib import contextmanager
from peewee import SqliteDatabase
from pyfakefs import fake_filesystem

from pomito import main
from pomito.config import Configuration
from pomito.plugins.ui import UIPlugin
from pomito.plugins.task import TaskPlugin
from pomito.hooks import Hook


class MessageTests(unittest.TestCase):
    def test_send_calls_signal_send_with_kwargs(self):
        mock_signal = Mock(blinker.Signal)
        msg = main.Message(mock_signal, arg1="arg1", arg2=1)

        msg.send()

        mock_signal.send.assert_called_once_with(arg1="arg1", arg2=1)


class MessageDispatcherTests(unittest.TestCase):
    def setUp(self):
        dummy_signal = blinker.signal('dummy_signal')
        self.test_message = main.Message(dummy_signal, arg1="arg1", arg2=1)
        self.dispatcher = main.MessageDispatcher()
        self.mock_callback = Mock()

    def tearDown(self):
        if self.dispatcher.is_alive():
            self.dispatcher.stop()
            self.dispatcher.join()

    def test_queue_message_throws_for_invalid_message(self):
        self.assertRaises(TypeError, self.dispatcher.queue_message, None)

    def test_queue_message_doesnt_queue_message_if_there_are_no_receivers(self):
        self.dispatcher.queue_message(self.test_message)

        assert self.dispatcher._message_queue.qsize() == 0

    def test_queue_message_queues_message_if_there_are_receivers(self):
        self.test_message.signal.connect(Mock(), weak=False)

        self.dispatcher.queue_message(self.test_message)

        assert self.dispatcher._message_queue.qsize() == 1

    def test_start_should_start_the_dispatcher_thread(self):
        self.dispatcher.start()

        assert self.dispatcher.is_alive()
        assert self.dispatcher._stop_event.is_set() is False

    def test_start_should_throw_if_dispatcher_is_already_started(self):
        self.dispatcher.start()

        self.assertRaises(RuntimeError, self.dispatcher.start)

    def test_started_dispatcher_should_process_messages_in_queue(self):
        self.test_message.signal.connect(self.mock_callback, weak=False)
        self.dispatcher.start()

        self.dispatcher.queue_message(self.test_message)

        self.dispatcher._message_queue.join()
        self.mock_callback.assert_called_once_with(None, arg1="arg1", arg2=1)

    def test_stopped_dispatcher_shouldnt_process_messages_in_queue(self):
        self.test_message.signal.connect(self.mock_callback, weak=False)
        self.dispatcher.start()
        self.dispatcher.stop()
        self.dispatcher.join()

        self.dispatcher.queue_message(self.test_message)

        assert self.mock_callback.called is False


class PomitoTests(unittest.TestCase):
    """
    Tests for main class.

    TODO
    default: durations for session, breaks
    default: config is parsed appropriately

    run: returns for invalid state
    run: runs the ui_plugin

    exit: sets the stop event
    exit: calls close on all hooks
    exit: writes the configuration

    platform: setup data dir and config home
    """

    def setUp(self):
        from pomito.test import PomitoTestFactory
        test_factory = PomitoTestFactory()

        # Encapsulate platform concerns
        filesystem = fake_filesystem.FakeFilesystem()
        os_module = fake_filesystem.FakeOsModule(filesystem)
        test_factory.create_patch(self, 'os.path', os_module.path)
        test_factory.create_patch(self, 'os.makedirs', os_module.makedirs)

        dummy_db = SqliteDatabase(':memory:')
        dummy_config = Configuration("dummy_config.ini")
        self.main = main
        self.pomito = main.Pomito(config=dummy_config, database=dummy_db)
        self._setup_pomito_plugins(self.pomito)
        self._setup_pomito_hooks(self.pomito)

    def test_default_hooks(self):
        from pomito.hooks.activity import ActivityHook

        pomito = self.main.Pomito()

        assert len(pomito._hooks) == 1
        assert isinstance(pomito._hooks[0], ActivityHook)
        pomito.exit()

    def test_initialize_creates_database_if_not_present(self):
        with self._setup_data_dir():
            pomito = self.main.Pomito()
            self._setup_pomito_plugins(pomito)

            with patch('sqlite3.connect', MagicMock()):
                pomito.initialize()

            assert pomito.get_db() is not None
            pomito.exit()

    def test_initialize_uses_injected_database(self):
        dummy_db = SqliteDatabase(':memory:')
        pomito = self.main.Pomito(database=dummy_db)
        self._setup_pomito_plugins(pomito)

        with patch('sqlite3.connect', MagicMock()):
            pomito.initialize()

        assert pomito.get_db() == dummy_db
        pomito.exit()

    def test_initialize_setup_plugins_and_hooks(self):
        with self._setup_data_dir():
            pomito = self.main.Pomito()
            self._setup_pomito_plugins(pomito)
            self._setup_pomito_hooks(pomito)

            with patch('sqlite3.connect', MagicMock()):
                pomito.initialize()

            assert pomito.ui_plugin.initialize.call_count == 1
            assert pomito.task_plugin.initialize.call_count == 1
            assert pomito._hooks[0].initialize.call_count == 1
            pomito.exit()

    def _setup_pomito_plugins(self, pomito):
        pomito.ui_plugin = Mock(spec=UIPlugin)
        pomito.task_plugin = Mock(spec=TaskPlugin)

    def _setup_pomito_hooks(self, pomito):
        pomito._hooks[0] = Mock(spec=Hook)

    @contextmanager
    def _setup_data_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = self.main.DATA_DIR
            self.main.DATA_DIR = os.path.join(tmpdir, "pomito")
            try:
                yield
            finally:
                self.main.DATA_DIR = data_dir
