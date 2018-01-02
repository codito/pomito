# Pomito - Pomodoro timer on steroids
# Task plugins package

import abc

class TaskPlugin(metaclass=abc.ABCMeta):
    """Defines the contract for all Task plugins."""

    def __init__(self):
        pass

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

    def get_task_by_id(self, task_id):
        """Gets a task with matching task_id-ish.

        Args:
            task_id: string. substring in Task id matched from left.
            Like commit-ish in case of git.
        """
        tasks = []
        for tsk in self.get_tasks():
            if str(tsk.uid).startswith(str(task_id)):
                tasks.append(tsk)
        if len(tasks) > 1:
            raise ValueError("Found {0} tasks matching id {1}."\
                             .format(len(tasks), task_id))
        return None if len(tasks) == 0 else tasks[0]
