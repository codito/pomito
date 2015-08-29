# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
# Tests for the Main module

import unittest
from unittest.mock import Mock

import blinker
import sure
from peewee import SqliteDatabase

from pomito import main
from pomito.plugins.ui import UIPlugin
from pomito.plugins.task import TaskPlugin

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
        self.dispatcher.queue_message.when.called_with(None).should.throw(TypeError)

    def test_queue_message_doesnt_queue_message_if_there_are_no_receivers(self):
        self.dispatcher.queue_message(self.test_message)

        self.dispatcher._message_queue.qsize().should.be.equal(0)

    def test_queue_message_queues_message_if_there_are_receivers(self):
        self.test_message.signal.connect(Mock(), weak=False)

        self.dispatcher.queue_message(self.test_message)

        self.dispatcher._message_queue.qsize().should.be.equal(1)

    def test_start_should_start_the_dispatcher_thread(self):
        self.dispatcher.start()

        self.dispatcher.is_alive().should.be.equal(True)
        self.dispatcher._stop_event.is_set().should.be.equal(False)

    def test_start_should_throw_if_dispatcher_is_already_started(self):
        self.dispatcher.start()

        self.dispatcher.start.when.called_with().should.throw(RuntimeError)

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

        self.mock_callback.called.should.be.equal(False)


class PomitoTests(unittest.TestCase):
    """
    TODO
    default: durations for session, breaks
    default: config is parsed appropriately

    run: returns for invalid state
    run: runs the ui_plugin

    exit: sets the stop event
    exit: calls close on all hooks
    exit: writes the configuration

    get_parser: returns an instance of configparser
    get_parser: returns none if there is no config file

    platform: setup data dir and config home
    """
    def setUp(self):
        from pomito.test import PomitoTestFactory
        import fake_filesystem
        test_factory = PomitoTestFactory()

        # Encapsulate platform concerns
        filesystem = fake_filesystem.FakeFilesystem()
        os_module = fake_filesystem.FakeOsModule(filesystem)
        test_factory.create_patch(self, 'os.path', os_module.path)
        test_factory.create_patch(self, 'os.makedirs', os_module.makedirs)

        dummy_db = SqliteDatabase(':memory:')
        self.main = main
        self.pomito = main.Pomito(database=dummy_db)
        self._setup_pomito_plugins(self.pomito)

    def test_default_settings(self):
        self.pomito.session_duration.should.be.equal(25 * 60)
        self.pomito.short_break_duration.should.be.equal(5 * 60)
        self.pomito.long_break_duration.should.be.equal(15 * 60)
        self.pomito.long_break_frequency.should.be.equal(4)

    def test_default_plugins(self):
        self.pomito._plugins['task'].should.be.equal('nulltask')
        self.pomito._plugins['ui'].should.be.equal('qtapp')

    def test_initialize_creates_database_if_not_present(self):
        pomito = self.main.Pomito()
        self._setup_pomito_plugins(pomito)

        pomito.initialize()

        pomito.get_db().shouldnt.be.equal(None)

    def test_initialize_uses_injected_database(self):
        dummy_db = SqliteDatabase(':memory:')
        pomito = self.main.Pomito(database=dummy_db)
        self._setup_pomito_plugins(pomito)

        pomito.initialize()

        pomito.get_db().should.be.equal(dummy_db)

    def test_get_parser_returns_a_configparser_with_config_data(self):
        pass

    def test_get_parser_returns_a_configparser_for_no_config(self):
        import configparser

        self.pomito.get_parser().should.be.a(configparser.SafeConfigParser)

    def _setup_pomito_plugins(self, pomito):
        pomito.ui_plugin = Mock(spec=UIPlugin)
        pomito.task_plugin = Mock(spec=TaskPlugin)
