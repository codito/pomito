# -*- coding: utf-8 -*-
# Tests for the Activity hook

import unittest
from unittest.mock import Mock, patch

from peewee import SqliteDatabase

from pomito.hooks.activity import ActivityHook, ActivityModel
from pomito.test import PomitoTestFactory

import fake_filesystem
import sure

class ActivityHookTests(unittest.TestCase):
    def setUp(self):
        test_factory = PomitoTestFactory()

        # Encapsulate platform concerns
        filesystem = fake_filesystem.FakeFilesystem()
        os_module = fake_filesystem.FakeOsModule(filesystem)
        test_factory.create_patch(self, 'os.path', os_module.path)
        test_factory.create_patch(self, 'os.makedirs', os_module.makedirs)

        ActivityModel.drop_table(True)

        self.pomodoro_service = test_factory.create_fake_service()
        self.activityhook = ActivityHook(self.pomodoro_service)
        self.activityhook.initialize()

    def tearDown(self):
        ActivityModel.drop_table(True)
        self.activityhook.close()

    def test_initialize_sets_activity_db(self):
        activityhook = ActivityHook(self.pomodoro_service)

        activityhook.initialize()

        ActivityHook.activity_db.shouldnt.be.equal(None)
        activityhook.close()

    def test_initialize_creates_signal_handlers(self):
        activityhook = ActivityHook(self.pomodoro_service)

        activityhook.initialize()

        self._count_receivers(self.pomodoro_service.signal_session_stopped)\
            .should.be.equal(2)
        self._count_receivers(self.pomodoro_service.signal_break_stopped)\
            .should.be.equal(2)
        self._count_receivers(self.pomodoro_service.signal_interruption_stopped)\
            .should.be.equal(2)
        activityhook.close()

    def test_close_disconnects_signal_handlers(self):
        activityhook = ActivityHook(self.pomodoro_service)
        activityhook.initialize()

        activityhook.close()

        # Count is one because there is already a listener for self.activityhook
        self._count_receivers(self.pomodoro_service.signal_session_stopped)\
            .should.be.equal(1)
        self._count_receivers(self.pomodoro_service.signal_break_stopped)\
            .should.be.equal(1)
        self._count_receivers(self.pomodoro_service.signal_interruption_stopped)\
            .should.be.equal(1)

    def test_log_handles_session_stop_event(self):
        test_task = self._create_task(100, 'session_start_task')
        self.pomodoro_service.start_session(test_task)
        self.pomodoro_service.stop_session()

        ActivityModel.select().where(ActivityModel.category ==\
                'session').count().should.be.equal(1)

    def test_log_handles_break_stop_event(self):
        self.pomodoro_service.start_break()
        self.pomodoro_service.stop_break()

        self._dump_activity_model()
        ActivityModel.select().where(ActivityModel.category ==\
                'break').count().should.be.equal(1)

    def test_log_handles_interruption_stop_event(self):
        self.pomodoro_service.start_interruption(None, False, False)
        self.pomodoro_service.stop_interruption()

        ActivityModel.select().where(ActivityModel.category ==\
                'interruption').count().should.be.equal(1)
        pass

    def _create_task(self, uid, description):
        from pomito.task import Task
        return Task(uid=uid, description=description, estimate=0, actual=0,
                tags=None)

    def _get_latest_entry(self):
        pass

    def _dump_activity_model(self):
        for activity in ActivityModel.select():
            print("{0};{1};{2}".format(activity.timestamp, activity.category,
                activity.data))

    def _count_receivers(self, signal):
        from blinker.base import ANY

        return sum(1 for r in signal.receivers_for(ANY))
        
