# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
"""Main interaction class."""

import logging
import os
import sys
import threading
from queue import Queue

from peewee import SqliteDatabase

import pomito.plugins
from pomito.config import Configuration

PACKAGE_NAME = "pomito"
DATA_HOME = CONFIG_HOME = os.path.expanduser("~")
if sys.platform.startswith("linux"):
    home_dir = os.getenv("HOME")
    DATA_HOME = os.getenv("XDG_DATA_HOME") or os.path.join(home_dir, ".local/share")
    CONFIG_HOME = os.getenv("XDG_CONFIG_HOME") or os.path.join(home_dir, ".config")

DATA_DIR = os.path.join(DATA_HOME, PACKAGE_NAME)
CONFIG_DIR = os.path.join(CONFIG_HOME, PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)


class Message(object):
    """A wrapper for signals/parameters to be sent across plugins via the
    dispatcher."""

    def __init__(self, signal, **kwargs):
        self.signal = signal
        self.kwargs = kwargs

    def send(self):
        self.signal.send(**self.kwargs)


class MessageDispatcher(threading.Thread):
    """Simple queue based message dispatcher."""

    def __init__(self):
        threading.Thread.__init__(self)

        self._message_queue = Queue()
        self._stop_event = threading.Event()

    def start(self):
        """ Starts the dispatcher.  """
        if threading.currentThread() == self:
            raise RuntimeError("Cannot call start on the thread itself.")
        threading.Thread.start(self)

    def stop(self):
        """Stops processing the queue.

        Doesn't ensure that queue is empty before stop. Message are thrown away.
        Look at _message_queue.join() in future.
        """
        if threading.currentThread() == self:
            raise RuntimeError("Cannot call start on the thread itself.")
        self._stop_event.set()

    def queue_message(self, message):
        """Queue a Message to be dispatched.

        Args:
            message: message to be dispatched. Type: Message.
        """
        if type(message) is not Message:
            raise TypeError("Only objects of type Message can be queued.")
        if message.signal.receivers:
            logger.info("MessageDispatcher: added message: " +
                        message.kwargs.__str__())
            logger.debug("MessageDispatcher: receivers: " +
                         message.signal.receivers.__str__())
            self._message_queue.put(message)
        else:
            logger.info("MessageDispatcher: skipped message: " +
                        message.kwargs.__str__())

    def run(self):
        """Worker for the message dispatcher thread."""
        while self._stop_event.is_set() is False:
            while self._message_queue.empty() is False:
                message = self._message_queue.get()

                # It is possible that we a signal is dispatched to a receiver
                # not present during enqueue of the message, how ever is present
                # now. YAGNI call for the moment.
                logger.debug("MessageDispatcher: dispatch message: " +
                             message.kwargs.__str__())
                logger.debug("MessageDispatcher: receivers: " +
                             message.signal.receivers.__str__())
                message.send()
                logger.debug("MessageDispatcher: message dispatched!")
                self._message_queue.task_done()
            self._stop_event.wait(0.01)


class Pomito(object):
    """Controls the application lifetime.

    Responsibilities:
        - Read and initialize the configuration
        - Choose the run mode
        - Handover execution to UI plugin
    """

    def __init__(self, config=None, database=None, message_dispatcher=None):
        """Create a Pomito object.

        Arguments:
            config   Configuration  Path to the configuration file
            database peewee.SqliteDatabase database to use for tasks etc.
            message_dispatcher MessageDispatcher message dispatcher instance
        """
        from pomito import pomodoro

        self._config = config
        self._database = database
        self._message_dispatcher = message_dispatcher
        self._threads = {}
        self._hooks = []

        if self._message_dispatcher is None:
            self._message_dispatcher = MessageDispatcher()
        if self._config is None:
            self._config_file = os.path.join(CONFIG_DIR, "config.ini")
            self._config = Configuration(self._config_file)
        self._config.load()

        # Pomodoro service instance. Order of initializations are important
        self.pomodoro_service = pomodoro.Pomodoro(self)

        # Default plugins
        pomito.plugins.initialize(self.pomodoro_service)
        self.ui_plugin = pomito.plugins.get_plugin(self._config.ui_plugin)
        self.task_plugin = pomito.plugins.get_plugin(self._config.task_plugin)

        # Add the plugins to threads list
        self._threads['task_plugin'] = threading.Thread(target=self.task_plugin)

        # Default hooks
        from pomito.hooks import activity
        self._hooks.append(activity.ActivityHook(self.pomodoro_service))
        return

    def initialize(self):
        """Initialize configuration, database and starts worker threads."""
        # if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

        database_path = os.path.join(DATA_DIR, "pomito.db")
        if self._database is None:
            self._database = SqliteDatabase(None)
            self._database.init(database_path)
        self._database.connect()

        # Initialize the plugins
        self.ui_plugin.initialize()
        self.task_plugin.initialize()

        # Initialize the hooks
        for hook in self._hooks:
            hook.initialize()
        return

    def run(self):
        """Start the application."""
        if not self._validate_state():
            logger.critical("Pomito.Run: Invalid state. Exiting.")
            return
        self.initialize()
        self._message_dispatcher.start()
        self.ui_plugin.run()
        self.exit()
        return

    def exit(self):
        """Clean up and save any configuration data. Prepare for exiting the application."""
        # FIXME Write out current configuration!
        if self._message_dispatcher.is_alive():
            self._message_dispatcher.stop()
            self._message_dispatcher.join()
        for hook in self._hooks:
            hook.close()
        # self._validate_state()
        if self._database is not None:
            self._database.close()
        return

    def get_db(self):
        """Get the database object.

        Returns:
            database peewee.SqliteDatabase object
        """
        return self._database

    def get_configuration(self):
        return self._config

    def queue_signal(self, message):
        self._message_dispatcher.queue_message(message)

    def _validate_state(self):
        """Validates configuration, plugins."""
        import pomito.plugins

        _retval = True

        if not issubclass(type(self.ui_plugin), pomito.plugins.ui.UIPlugin):
            logger.error("Invalid UIPlugin object = {0}".format(self.ui_plugin))
            _retval = False

        if not issubclass(type(self.task_plugin), pomito.plugins.task.TaskPlugin):
            logger.error("Invalid TaskPlugin object = {0}".format(self.task_plugin))
            _retval = False

        return _retval


def main():
    p = Pomito()
    p.run()

    return
