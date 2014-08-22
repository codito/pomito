#!/usr/bin/env python
# Tests for the Task module

import unittest
import pomito.task

import sure


class TaskTests(unittest.TestCase):
    """TODO: incomplete"""
    task_description = "A Simple Task"
    task_estimate_pomodoros = "20"
    task_actual_pomodoros = 100
    task_tags = "tag1 tag2"
    task_uid = 111

    test_task = pomito.task.Task(task_uid,
                                 task_estimate_pomodoros,
                                 task_actual_pomodoros,
                                 task_tags,
                                 task_description)

    def test_task_should_set_attributes(self):
        self.test_task.description.should.be.equal(self.task_description)
        self.test_task.estimate.should.be.equal(int(self.task_estimate_pomodoros))
        self.test_task.actual.should.be.equal(self.task_actual_pomodoros)
        self.test_task.tags.should.be.equal(self.task_tags)
        self.test_task.uid.should.be.equal(self.task_uid)

    def test_task_should_throw_on_invalid_task(self):
        _task = lambda: pomito.task.Task(self.task_uid,
                                         "invalid estimate",
                                         self.task_actual_pomodoros,
                                         self.task_tags,
                                         self.task_description)

        _task.when.called_with().should.throw(Exception)

    def test_task_uid_is_set_if_uid_parameter_is_none(self):
        _task = pomito.task.Task(None,
                                 self.task_estimate_pomodoros,
                                 self.task_actual_pomodoros,
                                 self.task_tags,
                                 self.task_description)

        _task.uid.should_not.be.none

    def test_task_update_actual_increases_actual_pomodoros_by_one(self):
        self.test_task.update_actual()

        self.test_task.actual.should.be(self.task_actual_pomodoros + 1)

    def test_task_update_estimate_sets_task_estimate(self):
        self.test_task.update_estimate(99)

        self.test_task.estimate.should.be(99)

    def test_task_update_estimate_raises_if_estimate_is_not_int(self):
        _update = lambda: self.test_task.update_estimate("abc")

        _update.when.called_with().should.throw(ValueError)

    def test_task_mark_complete_sets_completed_to_one(self):
        self.test_task.mark_complete()

        self.test_task.completed.should.be(1)
