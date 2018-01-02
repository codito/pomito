"""
Hooks are notification only agents. They are notified of special events in a
Pomodoro lifecycle.
"""

import abc


class Hook(metaclass=abc.ABCMeta):
    """Base class for all hooks"""

    @abc.abstractmethod
    def initialize(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass
