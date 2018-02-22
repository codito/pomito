# -*- coding: utf-8 -*-
"""Tests for the Activity hook."""

import unittest

from pomito.hooks.activity import ActivityHook, ActivityModel
from pomito.test import PomitoTestFactory


class ActivityHookTests(unittest.TestCase):
    def setUp(self):
        test_factory = PomitoTestFactory()

        self.pomodoro_service = test_factory.create_fake_service()
        self.activityhook = ActivityHook(self.pomodoro_service)
        self.activityhook.initialize()
        self.database = self.pomodoro_service.get_db()

    def tearDown(self):
        ActivityModel.drop_table(True)
        self.activityhook.close()

    def test_initialize_sets_activity_db(self):
        count = ActivityModel.select().count()

        assert count == 0

    def test_initialize_creates_signal_handlers(self):
        activityhook = ActivityHook(self.pomodoro_service)

        activityhook.initialize()

        # assert self._receivers(self.pomodoro_service.signal_session_stopped, 2)
        # assert self._receivers(self.pomodoro_service.signal_break_stopped, 2)
        # assert self._receivers(self.pomodoro_service.signal_interruption_stopped, 2)
        activityhook.close()

    def test_close_disconnects_signal_handlers(self):
        activityhook = ActivityHook(self.pomodoro_service)
        activityhook.initialize()

        activityhook.close()

        # Count is one because there is already a listener for self.activityhook
        assert self._receivers(self.pomodoro_service.signal_session_stopped, 2)
        assert self._receivers(self.pomodoro_service.signal_break_stopped, 2)
        assert self._receivers(self.pomodoro_service.signal_interruption_stopped, 2)

    def test_log_handles_session_stop_event(self):
        test_task = self._create_task(100, 'session_start_task')
        self.pomodoro_service.start_session(test_task)
        self.pomodoro_service.stop_session()

        activities = ActivityModel.get(ActivityModel.category == 'session')
        assert activities is not None

    def test_log_handles_break_stop_event(self):
        self.pomodoro_service.start_break()
        self.pomodoro_service.stop_break()

        self._dump_activity_model()
        activities = ActivityModel.get(ActivityModel.category == 'break')
        assert activities is not None

    def test_log_handles_interruption_stop_event(self):
        self.pomodoro_service.start_interruption(None, False, False)
        self.pomodoro_service.stop_interruption()

        act = ActivityModel.get(ActivityModel.category == 'interruption')
        assert act is not None

    def _create_task(self, uid, description):
        from pomito.task import Task
        return Task(uid=uid, description=description,
                    estimate=0, actual=0,
                    tags=None)

    def _dump_activity_model(self):
        for activity in ActivityModel.select():
            print("{0};{1};{2}".format(activity.timestamp, activity.category,
                                       activity.data))

    def _receivers(self, signal, count):
        from blinker.base import ANY

        return sum(1 for r in signal.receivers_for(ANY)) == count
