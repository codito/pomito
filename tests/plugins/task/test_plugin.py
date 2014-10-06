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
        tasks = list(self.taskPlugin.get_tasks_by_filter(None))

        expect(len(tasks)).to.equal(12)
        expect(tasks).to.equal(self.task_list)
