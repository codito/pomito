# Pomito - Pomodoro timer on steroids
# Task plugins package

import abc

class TaskPlugin(metaclass=abc.ABCMeta):
    """Defines the contract for all Task plugins."""

    @abc.abstractmethod
    def initialize(self):
        pass

    @abc.abstractmethod
    def get_tasks(self):
        pass

    @abc.abstractmethod
    def is_valid_task(self, task):
        pass
