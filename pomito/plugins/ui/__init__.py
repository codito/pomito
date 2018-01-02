# Pomito - Pomodoro timer on steroids
# UI plugins package
import abc

class UIPlugin(metaclass=abc.ABCMeta):
    """Defines the contract for all UI plugins"""

    @abc.abstractmethod
    def initialize(self):
        pass

    #@abc.abstractmethod
    #def notify_session_started(self):
        #"""Called when a new pomodoro is started"""
        #pass

    #@abc.abstractmethod
    #def notify_session_end(self, reason):
        #"""Called when a pomodoro session ends.

        #Args:
            #reason Reason for ending this session. Possible values =
        #"""
        #return

    #@abc.abstractmethod
    #def notify_break_started(self, break_type):
        #"""Called when a pomodoro session ends.

        #Args:
            #break_type Type of break. Possible values = short_break, long_break
        #"""
        #pass

    #@abc.abstractmethod
    #def notify_break_end(self, reason):
        #"""Called when a pomodoro session ends.

        #Args:
            #reason Reason for break end. Possible values =
        #"""
        #pass

    @abc.abstractmethod
    def run(self):
        """Driver method for the UI. Should initiate and run the plugin."""
        pass


