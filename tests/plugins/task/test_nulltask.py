# -*- coding: utf-8 -*-
"""Tests for NullTask plugin."""

import unittest

from pomito.plugins.task import nulltask, TaskPlugin


class NullTaskTests(unittest.TestCase):
    """Tests for NullTask."""

    def setUp(self):
        self.task = nulltask.NullTask(None)

    def test_nulltask_is_a_task_plugin(self):
        assert issubclass(nulltask.NullTask, TaskPlugin)

    def test_nulltask_initialize_should_not_throw(self):
        self.task.initialize()

    def test_nulltask_get_tasks_returns_empty_list(self):
        assert len(self.task.get_tasks()) == 0

    def test_nulltask_get_tasks_by_filter_returns_empty_list(self):
        assert len(self.task.get_tasks_by_filter("")) == 0

    def test_nulltask_get_task_by_id_returns_none(self):
        assert self.task.get_task_by_id(1) is None
