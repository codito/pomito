# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
# Test doubles

from unittest.mock import Mock, MagicMock
from unittest.mock import patch

from peewee import SqliteDatabase

from pomito import main, pomodoro
from pomito.plugins.ui import UIPlugin
from pomito.plugins.task import TaskPlugin


class FakeTimer(object):
    """A synchronous fake timer."""

    def __init__(self, duration, callback, interval=1):
        self.duration = duration
        self.time_elapsed = interval
        self._interval = interval
        self._parent_callback = callback
        self._alive = False

    def is_running(self):
        return True

    def is_alive(self):
        return self._alive

    def join(self):
        # We're forcing join to be called for all fake timers
        self._alive = False

    def start(self):
        self._alive = True
        self._parent_callback('increment')

    def stop(self):
        self._parent_callback('interrupt')

    def trigger_callback(self, notify_reason):
        """Trigger a callback with given reason. Test only function."""
        self._parent_callback(notify_reason)


class FakeMessageDispatcher(object):
    """A synchronous fake message dispatcher."""
    def start(self):
        pass

    def stop(self):
        pass

    def is_alive(self):
        return False

    def queue_message(self, message):
        message.send()


class FakeTaskPlugin(TaskPlugin):
    """A fake task plugin which returns pre-defined task list."""
    task_list = []

    def __init__(self):
        pass

    def initialize(self):
        pass

    def get_tasks(self):
        return self.task_list


class PomitoTestFactory(object):
    """Creates fake pomodoro framework instances for testing."""
    config_file = None
    database = SqliteDatabase(':memory:')
    message_dispatcher = FakeMessageDispatcher()

    def create_fake_service(self):
        """Create a fake instance of `Pomodoro` service.

        Note: call `create_patch` before calling this method if you want to
        replace os/path calls. See tests/hooks/test_activity.py for example.
        """
        pomito = main.Pomito(self.config_file, self.database,
                             create_message_dispatcher=lambda:
                             self.message_dispatcher)
        pomito.ui_plugin = Mock(spec=UIPlugin)
        pomito.task_plugin = MagicMock(spec=TaskPlugin)

        def create_fake_timer(duration, callback, interval=0.1):
            """Create a fake timer."""
            return FakeTimer(duration, callback, interval)

        return pomodoro.Pomodoro(pomito, create_timer=create_fake_timer)

    @staticmethod
    def create_patch(testcase, target, new):
        """Creates a patcher for `target` to be replaced with `new`. Adds the
        patcher to cleanup of `testcase`.

        Args:
            testcase: unittest.TestCase object
            target: string name of the object to replace
            new: object replacement for `target`
        """
        patcher = patch(target, new)
        patcher.start()
        testcase.addCleanup(patcher.stop)
