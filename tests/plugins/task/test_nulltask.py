# -*- coding: utf-8 -*-
"""Tests for NullTask plugin."""

import unittest
from sure import expect

from pomito.plugins.task import nulltask, TaskPlugin


# flake8: noqa
class NullTaskTests(unittest.TestCase):

    """Tests for NullTask."""

    def setUp(self):
        self.task = nulltask.NullTask(None)

    def test_nulltask_is_a_task_plugin(self):
        expect(issubclass(nulltask.NullTask, TaskPlugin)).true

    def test_nulltask_initialize_should_not_throw(self):
        expect(self.task.initialize).when.called.to_not.throw()

    def test_nulltask_get_tasks_returns_empty_list(self):
        expect(self.task.get_tasks()).to.be.empty

    def test_nulltask_get_tasks_by_filter_returns_empty_list(self):
        expect(self.task.get_tasks_by_filter("")).to.be.empty

    def test_nulltask_get_task_by_id_returns_none(self):
        expect(self.task.get_task_by_id(1)).to.be.none
