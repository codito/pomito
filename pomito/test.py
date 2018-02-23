# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
"""Test doubles for pomito."""

from unittest.mock import Mock, MagicMock
from unittest.mock import patch

from peewee import SqliteDatabase

from pomito import main, pomodoro
from pomito.config import Configuration
from pomito.plugins.ui import UIPlugin
from pomito.plugins.task import TaskPlugin


class FakeTimer:
    """A synchronous fake timer."""

    def __init__(self, duration, callback, interval=1):
        """Create a fake timer instance."""
        self.duration = duration
        self.time_elapsed = interval
        self._interval = interval
        self._parent_callback = callback
        self._alive = False

    def is_alive(self):
        """Get alive status of timer."""
        return self._alive

    def join(self):
        """Wait for timer to be complete."""
        # We're forcing join to be called for all fake timers
        self._alive = False

    def start(self):
        """Start the timer."""
        self._alive = True
        self._parent_callback(pomodoro.TimerChange.INCREMENT)

    def stop(self):
        """Stop the timer."""
        self._parent_callback(pomodoro.TimerChange.INTERRUPT)

    def trigger_callback(self, notify_reason):
        """Trigger a callback with given reason. Test only function."""
        self._parent_callback(notify_reason)


class FakeMessageDispatcher:
    """A synchronous fake message dispatcher."""

    def start(self):
        """Start the dispatcher."""
        pass

    def stop(self):
        """Stop the dispatcher."""
        pass

    def is_alive(self):
        """Get alive status of dispatcher."""
        return False

    def queue_message(self, message):
        """Queue a message in dispatcher."""
        message.send()


class FakeTaskPlugin(TaskPlugin):
    """A fake task plugin which returns pre-defined task list."""

    task_list = []

    def __init__(self):
        """Create a fake task plugin."""
        pass

    def initialize(self):
        """Initialize the fake task plugin."""
        pass

    def get_tasks(self):
        """Get tasks in the plugin."""
        return self.task_list


class FakeUIPlugin(UIPlugin):
    """A fake ui plugin implementation."""

    started = False

    def initialize(self):
        """Initialize the fake UI."""
        pass

    def run(self):
        """Start the UI."""
        self.started = True


class PomitoTestFactory:
    """Creates fake pomodoro framework instances for testing."""

    config_data = {"pomito": {"session_duration": 10,
                              "short_break_duration": 2,
                              "long_break_duration": 5,
                              "long_break_frequency": 4},
                   "plugins": {"ui": "dummyUI", "task": "dummyTask"}}
    config_file = None
    message_dispatcher = FakeMessageDispatcher()

    def create_fake_service(self):
        """Create a fake instance of `Pomodoro` service.

        Note: call `create_patch` before calling this method if you want to
        replace os/path calls. See tests/hooks/test_activity.py for example.
        """
        database = SqliteDatabase(':memory:')
        config = self.create_fake_config()
        pomito = main.Pomito(config, database, self.message_dispatcher)
        pomito.initialize()

        def create_fake_timer(duration, callback, interval=0.1):
            """Create a fake timer."""
            return FakeTimer(duration, callback, interval)

        return pomodoro.Pomodoro(pomito, create_timer=create_fake_timer)

    def create_fake_config(self):
        """Create a fake configuration instance."""
        from pomito.plugins import PLUGINS

        PLUGINS['dummyUI'] = Mock(spec=UIPlugin)
        PLUGINS['dummyTask'] = MagicMock(spec=TaskPlugin)

        return Configuration(self.config_file, self.config_data)

    @staticmethod
    def create_patch(testcase, target, new):
        """Create a patcher for `target` to be replaced with `new`.

        Adds the patcher to cleanup of `testcase`.

        Args:
            testcase: unittest.TestCase object
            target: string name of the object to replace
            new: object replacement for `target`
        """
        patcher = patch(target, new)
        patcher.start()
        testcase.addCleanup(patcher.stop)
