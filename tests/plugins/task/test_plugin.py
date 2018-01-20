# -*- coding: utf-8 -*-
"""Tests for the TaskPlugin."""

import unittest
from unittest.mock import MagicMock

from pomito import task
from pomito.test import FakeTaskPlugin


class TaskPluginTests(unittest.TestCase):
    def setUp(self):
        self.taskPlugin = FakeTaskPlugin()
        self.task_list = []
        for i in range(12):
            t = MagicMock(spec=task.Task)
            t.uid = 100982 + 10 * i
            t.__str__.return_value = str(i)
            self.task_list.append(t)
        self.taskPlugin.task_list = (t for t in self.task_list)

    def test_get_tasks_by_filter_returns_generator_type(self):
        import types

        tasks = self.taskPlugin.get_tasks_by_filter(None)

        assert isinstance(tasks, types.GeneratorType)

    def test_get_tasks_by_filter_returns_all_tasks_for_no_filter(self):
        tasks = list(self.taskPlugin.get_tasks_by_filter(None))

        assert len(tasks) == 12
        assert tasks == self.task_list

    def test_get_tasks_by_filter_returns_all_tasks_for_star_filter(self):
        tasks = list(self.taskPlugin.get_tasks_by_filter("*"))

        assert len(tasks) == 12
        assert tasks == self.task_list

    def test_get_task_by_id_returns_none_if_no_matching_task(self):
        t = self.taskPlugin.get_task_by_id(9)

        assert t is None

    def test_get_task_by_id_returns_task_with_full_id(self):
        t = self.taskPlugin.get_task_by_id(100982)

        assert t == self.task_list[0]

    def test_get_task_by_id_returns_task_with_matching_idish(self):
        t = self.taskPlugin.get_task_by_id(10099)

        assert t == self.task_list[1]

    def test_get_task_by_id_throws_if_multiple_tasks_match_idish(self):
        self.assertRaises(ValueError, self.taskPlugin.get_task_by_id, 1009)
