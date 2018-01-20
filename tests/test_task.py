#!/usr/bin/env python
"""Tests for the Task module."""

import unittest
import pomito.task


class TaskTests(unittest.TestCase):
    """TODO: incomplete."""

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
        assert self.test_task.description == self.task_description
        assert self.test_task.estimate == int(self.task_estimate_pomodoros)
        assert self.test_task.actual == self.task_actual_pomodoros
        assert self.test_task.tags == self.task_tags
        assert self.test_task.uid == self.task_uid

    def test_task_should_throw_on_invalid_task(self):
        self.assertRaises(Exception, pomito.task.Task, self.task_uid,
                          "invalid estimate", self.task_actual_pomodoros,
                          self.task_tags, self.task_description)

    def test_task_uid_is_set_if_uid_parameter_is_none(self):
        t = pomito.task.Task(None,
                             self.task_estimate_pomodoros,
                             self.task_actual_pomodoros,
                             self.task_tags,
                             self.task_description)

        assert t.uid is not None

    def test_task_update_actual_increases_actual_pomodoros_by_one(self):
        self.test_task.update_actual()

        assert self.test_task.actual == self.task_actual_pomodoros + 1

    def test_task_update_estimate_sets_task_estimate(self):
        self.test_task.update_estimate(99)

        assert self.test_task.estimate == 99

    def test_task_update_estimate_raises_if_estimate_is_not_int(self):
        self.assertRaises(ValueError, self.test_task.update_estimate, "abc")

    def test_task_mark_complete_sets_completed_to_one(self):
        self.test_task.mark_complete()

        assert self.test_task.completed == 1

    def test_get_null_task_returns_dummy_task(self):
        dummy_task = pomito.task.get_null_task()

        assert dummy_task.actual == 0
        assert dummy_task.completed == 0
        assert dummy_task.description == "No task selected."
        assert dummy_task.estimate == 0
        assert dummy_task.tags is None
