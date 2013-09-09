# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
# Implementation of Pomodoro service layer

import logging
import threading
import blinker

from .main import Message

logger = logging.getLogger('pomito.service')


class Pomodoro(object):

    """Basic services provided by the pomodoro application fall into these
    categories:
        - Config management: handled by lower layer (main.Pomito), we act as
        proxy and bubble them to user
        - Database management: handled by peewee, wraps around a in application
        database
        - Tasks management: handled by plugin.task.TaskPlugin, we only bubble
        up few methods
        - Session management: completely handled in this layer, we know the
        state for this

    Primary consumers are:
        - Task plugins: implemented by plugin.task.TaskPlugin
        - UI plugins: implemented by plugin.ui.UIPlugin
        - Hooks: implemented by plugin.hook.HookPlugin
    """

    # Signals
    # timer_increment
    #   - args: timer_type, timer_value
    # session_started, session_stopped
    #   - args: session_count, task, reason (only for stop)
    # break_started, break_stopped
    #   - args: break_type, reason (only for *_stopped signal)
    # interruption_started, interruption_stopped
    #   - args: duration (only for stop)
    signal_timer_increment = blinker.signal('timer_increment')
    signal_session_started = blinker.signal('session_started')
    signal_session_stopped = blinker.signal('session_stopped')
    signal_break_started = blinker.signal('break_started')
    signal_break_stopped = blinker.signal('break_stopped')
    signal_interruption_started = blinker.signal('interruption_started')
    signal_interruption_stopped = blinker.signal('interruption_stopped')

    def __init__(self, pomito_instance,
                 create_timer=lambda duration, callback, interval=1:\
                         Timer(duration, callback, interval)):
        self._pomito_instance = pomito_instance
        self._session_count = 0
        self._create_timer = create_timer
        self._timer = self._create_timer(self._pomito_instance.session_duration,
                                         self._update_state)
        # other values = "{short, long}_break", "interruption"
        self._timer_type = "session"

    def _stop_timer(self):
        # TODO cleanup: decorator for stop* methods. Similar method for start*
        # methods
        self._timer.stop()
        if self._timer.is_alive():
            self._timer.join()
        return

    def get_config(self, plugin_name, config_key):
        """Gets the config dict for <plugin_name> from pomito ini file"""
        return self._pomito_instance.get_parser().get(plugin_name, config_key)

    def get_db(self):
        """Gets the in application database for Pomito."""
        return self._pomito_instance.get_db()

    def get_data_dir(self):
        """Gets the data directory for pomito application."""
        from .main import DATA_DIR
        return DATA_DIR

    def get_tasks(self):
        return self._pomito_instance.task_plugin.get_tasks()

    def start_session(self, task):
        """Starts a pomodoro session.

        Args:
            task: Task - A task object, to be performed during this session
        """
        if not self._pomito_instance.task_plugin.is_valid_task(task):
            raise Exception("Cannot start a session without a valid task!")

        self.current_task = task
        self._timer_type = "session"
        self._timer = self._create_timer(self._pomito_instance.session_duration,
                            self._update_state)
        msg = Message(self.signal_session_started,
                      session_count=self._session_count,
                      session_duration=self._pomito_instance.session_duration,
                      task=self.current_task)
        self._pomito_instance.queue_signal(msg)
        self._timer.start()

    def stop_session(self):
        """Stops a pomodoro session."""
        self._stop_timer()

    def start_break(self):
        """Starts a break on completion of a session.

        A short break of 5 minutes is introduced after each session.
        A longer break of duration 15 minutes is introduced after 4 consecutive
        sessions.
        """
        if self._session_count == self._pomito_instance.long_break_frequency:
            self._timer_type = "long_break"
            _duration = self._pomito_instance.long_break_duration
        else:
            self._timer_type = "short_break"
            _duration = self._pomito_instance.short_break_duration
        self._timer = self._create_timer(_duration, self._update_state)
        msg = Message(self.signal_break_started, break_type=self._timer_type)
        self._pomito_instance.queue_signal(msg)
        self._timer.start()

    def stop_break(self):
        """Stops a break session."""
        self._stop_timer()

    def start_interruption(self, reason, is_external, add_unplanned_task):
        # TODO option to stop auto monitoring of interruptions
        # TODO add the interruption activity
        # TODO support interruption type for interruption_stop
        self._timer_type = "interruption"
        if self._timer.is_alive():
            logger.debug('Another timer is alive. Wait for join()')
            self._timer.join()
        self._timer = self._create_timer(0, self._update_state)
        self._pomito_instance.queue_signal(
            Message(self.signal_interruption_started,
                    reason=reason, external=is_external))
        self._timer.start()

    def stop_interruption(self):
        """Stops the interruption timer."""
        self._stop_timer()

    def _update_state(self, notify_reason):
        """This is called in context of timer thread. Try to keep execution as
        minimal as possible in case of increment notifications.

        This method queues the signals into the dispatcher queue.
        """
        msg = None
        if notify_reason == "increment":
            self.signal_timer_increment.send(self._timer.time_elapsed)
        elif notify_reason == "complete":
            if self._timer_type == "session":
                self._session_count += 1
                msg = Message(
                    self.signal_session_stopped,
                    session_count=self._session_count, task=self.current_task,
                    reason=notify_reason)
            elif self._timer_type.endswith("_break"):
                msg = Message(self.signal_break_stopped,
                              break_type=self._timer_type,
                              reason=notify_reason)
        elif notify_reason == "interrupt":
            if self._timer_type == "session":
                # TODO cancel session w/ task. Start interruption timer?
                msg = Message(
                    self.signal_session_stopped,
                    session_count=self._session_count, task=self.current_task,
                    reason=notify_reason)
            elif self._timer_type.endswith("_break"):
                msg = Message(
                    self.signal_break_stopped, break_type=self._timer_type,
                    reason=notify_reason)
            else:
                msg = Message(self.signal_interruption_stopped,
                              duration=self._timer.time_elapsed)
        else:
            raise Exception(
                "Invalid state. Notify reason = {0}.".format(notify_reason))
        if msg is not None:
            self._pomito_instance.queue_signal(msg)


class Timer(threading.Thread):

    """Inspired by threading.Timer. Two major differences:
        - We call the parent_callback every interval (default = one second)
        - We support notify_reason with callbacks. We support "interrupt" as
        reason because of support for other plugins and hooks which listen to
        events
        - We stop only when a) stop is called explicitly, notify_reason =
        interrupt; or b) duration is complete, notify_reason = complete

    This runs in its own thread, on which parent_callback is called. User can
    screw us up due to nature of callbacks, by doing bad stuff in the callback.

    Performance overhead: ~0.03s per minute for vanilla callbacks
    (see tests/test_timer.py).
    """

    def __init__(self, duration, callback, interval=1):
        """
        Args:
            duration: total duration for the timer
            callback: callback that will be invoked on stop or completion
            interval: duration to increment the timer on each loop
        """
        threading.Thread.__init__(self)

        self.duration = duration
        self.time_elapsed = interval
        self._interval = interval
        self._notify_reason = "complete"
        self._parent_callback = callback
        self._finished = threading.Event()

    def is_running(self):
        return not self._finished.is_set()

    def start(self):
        if threading.currentThread() == self:
            raise RuntimeError("Cannot call start on the timer thread itself.")
        self._notify_reason = "increment"
        threading.Thread.start(self)

    def stop(self):
        if threading.currentThread() == self:
            raise RuntimeError("Cannot call stop on the timer thread itself.")
        self._notify_reason = "interrupt"
        self._finished.set()

    def run(self):
        """Thread run loop. Do not call directly."""
        while True:
            self._finished.wait(self._interval)

            if self.time_elapsed == self.duration:
                self._notify_reason = "complete"
                self._finished.set()
            else:
                self.time_elapsed += self._interval
            self._parent_callback(self._notify_reason)

            if self._finished.is_set():
                break
