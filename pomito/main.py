# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
# Main interaction class

import logging
import os
import sys
import threading
from queue import Queue

from peewee import SqliteDatabase

import pomito.plugins

PACKAGE_NAME = "pomito"
DATA_HOME = CONFIG_HOME = os.path.expanduser("~")
if sys.platform.startswith("linux"):
    DATA_HOME = os.getenv("XDG_DATA_HOME")
    CONFIG_HOME = os.getenv("XDG_CONFIG_HOME")

DATA_DIR = os.path.join(DATA_HOME, PACKAGE_NAME)
CONFIG_DIR = os.path.join(CONFIG_HOME, PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)


class Message(object):
    """A wrapper for signals/parameters to be sent across plugins via the dispatcher"""
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

    def __init__(self, config_file=None, database=None,
            create_message_dispatcher=lambda: MessageDispatcher()):
        """Creates a Pomito object.

        Arguments:
            config_file string  Path to the configuration file
            database    peewee.SqliteDatabase database to use for tasks etc.
            create_message_dispatcher function creates a MessageDispatcher
        """
        from configparser import SafeConfigParser
        from pomito import pomodoro

        self._config_file = config_file
        self._database = database
        self._parser = SafeConfigParser()
        self._message_dispatcher = create_message_dispatcher()
        self._threads = {}
        self._plugins = {}
        self._hooks = []

        # Set default options
        self.session_duration = 25 * 60      # Duration of a pomodoro session
        self.short_break_duration = 5 * 60   # Duration of a short break between two sessions
        self.long_break_duration = 15 * 60   # Duration of a longer break after every 4 sessions
        self.long_break_frequency = 4        # Frequency of long breaks
        self._plugins['ui'] = 'console'
        self._plugins['task'] = 'text'

        self._parse_config_file(self._config_file)

        # Pomodoro service instance. Order of initializations are important
        self.pomodoro_service = pomodoro.Pomodoro(self)

        # Default plugins
        pomito.plugins.initialize(self.pomodoro_service)
        self.ui_plugin = pomito.plugins.get_plugin(self._plugins['ui'])
        self.task_plugin = pomito.plugins.get_plugin(self._plugins['task'])

        # Add the plugins to threads list
        self._threads['task_plugin'] = threading.Thread(target=self.task_plugin)

        # Default hooks
        from pomito.hooks import activity
        self._hooks.append(activity.ActivityHook(self.pomodoro_service))
        return

    def initialize(self):
        """Initializes configuration, database and starts worker threads."""
        database_path = os.path.join(DATA_DIR, "pomito_data.db")
        if not os.path.exists(database_path) and not self._database:
            self._database = SqliteDatabase(database_path)

        # Initialize the plugins
        self.ui_plugin.initialize()
        self.task_plugin.initialize()
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
        #self._validate_state()
        #self._parser.write()
        return

    def get_db(self):
        """Gets the database object.

        Returns:
            database peewee.SqliteDatabase object
        """
        return self._database

    def get_parser(self):
        """Gets the parser object.

        Returns:
            parser ConfigParser
        """
        return self._parser

    def queue_signal(self, message):
        self._message_dispatcher.queue_message(message)

    def _parse_config_file(self, config_file):
        """Parse the pomito user configuration file. Sample config at
        $Src/docs/sample_config.ini.

        Args:
            config_file: string Path to the configuration file
        """
        if config_file is None or not os.path.isfile(config_file):
            logger.info("Config file '{0}' not found. Using defaults.".format(config_file))
            return

        self._parser.read(config_file)
        if self._parser.has_section('pomito'):
            self.session_duration = self._parser.getint('pomito', 'session_duration') * 60
            self.short_break_duration = self._parser.getint('pomito', 'short_break_duration') * 60
            self.long_break_duration = self._parser.getint('pomito', 'long_break_duration') * 60
            self.long_break_frequency = self._parser.getint('pomito', 'long_break_frequency') * 60

        if self._parser.has_section('plugins'):
            self._plugins['ui'] = self._parser.get('plugins', 'ui')
            self._plugins['task'] = self._parser.get('plugins', 'task')
        return

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
    p = Pomito(os.path.join(CONFIG_DIR, "config.ini"))
    p.run()

    return
