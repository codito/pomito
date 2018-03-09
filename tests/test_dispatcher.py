# -*- coding: utf-8 -*-
"""Tests for message dispatcher."""

import unittest
from unittest.mock import Mock

import blinker

from pomito import main


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
