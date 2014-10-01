# Pomito - Pomodoro timer on steroids
# Task plugins package

import abc

class TaskPlugin(metaclass=abc.ABCMeta):
    """Defines the contract for all Task plugins."""

    def __init__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def initialize(self):
        """Initializes the Task Plugin implementation.

        Called by pomito on start up."""
        pass

    @abc.abstractmethod
    def get_tasks(self):
        """Gets list of all tasks from the plugin.
        """
        pass

    def get_tasks_by_filter(self, task_filter):
        """Gets list of tasks from the plugin.

        Args:
            task_filter: string. substring in Task string representation
                         Task.__str__.
        """
        if task_filter is None or task_filter == "*":
            yield from self.get_tasks()
        else:
            for task in self.get_tasks():
                if task_filter in str(task):
                    yield task

    @abc.abstractmethod
    def is_valid_task(self, task):
        """Validate a task. Return true if the task is valid.

        Args:
            task: Task object.
        """
        pass
