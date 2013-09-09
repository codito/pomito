# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
# Test doubles

from unittest.mock import Mock
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

    def is_running(self):
        return not self._finished.is_set()

    def is_alive(self):
        return False

    def start(self):
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


class PomitoTestFactory(object):
    """Creates fake pomodoro framework instances for testing."""
    def create_fake_service(self):
        """Create a fake instance of `Pomodoro` service.

        Note: call `create_patch` before calling this method if you want to
        replace os/path calls. See tests/hooks/test_activity.py for example.
        """
        pomito = main.Pomito(None, database=SqliteDatabase(':memory'),
                create_message_dispatcher=lambda: FakeMessageDispatcher())
        pomito.ui_plugin = Mock(spec=UIPlugin)
        pomito.task_plugin = Mock(spec=TaskPlugin)
        pomito.task_plugin.is_valid_task.return_value = True

        return pomodoro.Pomodoro(pomito, create_timer=lambda duration, callback, interval=0.1: FakeTimer(duration, callback, interval))

    def create_patch(self, testcase, target, new):
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
