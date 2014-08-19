#!/usr/bin/env python
# Tests for the Task module

import unittest
import pomito.task

import sure


class TaskTests(unittest.TestCase):
    """TODO: incomplete"""
    task_description = "A Simple Task"
    task_estimate_time = "20"
    task_actual_time = 100
    task_tags = "tag1 tag2"
    task_uid = 111

    def test_task_should_set_attributes(self):
        _task = pomito.task.Task(self.task_uid, self.task_estimate_time,
                                 self.task_actual_time, self.task_tags,
                                 self.task_description)

        _task.description.should.be.equal(self.task_description)
        _task.estimate.should.be.equal(int(self.task_estimate_time))
        _task.actual.should.be.equal(self.task_actual_time)
        _task.tags.should.be.equal(self.task_tags)
        _task.uid.should.be.equal(self.task_uid)

    def test_task_should_throw_on_invalid_task(self):
        _task = lambda: pomito.task.Task(self.task_uid,
                                         "invalid estimate",
                                         self.task_actual_time,
                                         self.task_tags,
                                         self.task_description)

        _task.when.called_with().should.throw(Exception)

    def test_task_uid_is_set_if_uid_parameter_is_none(self):
        _task = pomito.task.Task(None, self.task_estimate_time,
                                 self.task_actual_time, self.task_tags,
                                 self.task_description)

        _task.uid.should_not.be.none
