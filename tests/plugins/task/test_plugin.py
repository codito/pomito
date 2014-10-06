"""Tests for the TaskPlugin"""

import unittest
from unittest.mock import MagicMock

from sure import expect

from pomito import task
from pomito.test import FakeTaskPlugin

# pylint: disable=missing-docstring, invalid-name
class TaskPluginTests(unittest.TestCase):
    def setUp(self):
        self.taskPlugin = FakeTaskPlugin()
        self.task_list = []
        for i in range(12):
            t = MagicMock(spec=task.Task)
            t.id = 100982 + 10 * i
            t.__str__.return_value = str(i)
            self.task_list.append(t)
        self.taskPlugin.task_list = (t for t in self.task_list)

    def test_get_tasks_by_filter_returns_generator_type(self):
        import types

        tasks = self.taskPlugin.get_tasks_by_filter(None)

        expect(tasks).to.be.a(types.GeneratorType)

    def test_get_tasks_by_filter_returns_all_tasks_for_no_filter(self):
        tasks = list(self.taskPlugin.get_tasks_by_filter(None))

        expect(tasks).to.have.length_of(12)
        expect(tasks).to.equal(self.task_list)

    def test_get_tasks_by_filter_returns_all_tasks_for_star_filter(self):
        tasks = list(self.taskPlugin.get_tasks_by_filter("*"))

        expect(tasks).to.have.length_of(12)
        expect(tasks).to.equal(self.task_list)

    def test_get_task_by_id_returns_none_if_no_matching_task(self):
        t = self.taskPlugin.get_task_by_id(9)

        expect(t).to.be.none

    def test_get_task_by_id_returns_task_with_full_id(self):
        t = self.taskPlugin.get_task_by_id(100982)

        expect(t).to.equal(self.task_list[0])

    def test_get_task_by_id_returns_task_with_matching_idish(self):
        t = self.taskPlugin.get_task_by_id(10099)

        expect(t).to.equal(self.task_list[1])

    def test_get_task_by_id_throws_if_multiple_tasks_match_idish(self):
        expect(self.taskPlugin.get_task_by_id)\
            .when.called_with(1009).to.throw(ValueError)
