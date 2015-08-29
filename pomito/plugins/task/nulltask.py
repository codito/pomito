# -*- coding: utf-8 -*-
"""Null task implementation."""

from pomito.plugins.task import TaskPlugin


class NullTask(TaskPlugin):

    """Implements a task plugin that does nothing."""

    def __init__(self, pomodoro_service):
        """Create an instance of TaskPlugin."""
        super(NullTask, self).__init__()

    def initialize(self):
        """Initialize the Task Plugin implementation."""
        pass

    def get_tasks(self):
        """Get list of all tasks from the plugin."""
        return []

    def get_tasks_by_filter(self, task_filter):
        """Get list of tasks from the plugin.

        Args:
            task_filter: string. substring in Task string representation
                         Task.__str__.
        """
        return []

    def get_task_by_id(self, task_id):
        """Get a task with matching task_id-ish.

        Args:
            task_id: string. substring in Task id matched from left.
            Like commit-ish in case of git.
        """
        return None
