# -*- coding: utf-8 -*-
"""Configuration for pomito."""
import logging
import math
import os
from configparser import ConfigParser

__all__ = ["Configuration"]
logger = logging.getLogger("pomito.config")


class Configuration(object):
    """Configuration settings for pomito.

    Configuration is read from `config.ini` file in pomito data directory.
    See documentation for more details.
    """

    # Set sensible defaults
    session_duration = 25 * 60      # Pomodoro session duration
    short_break_duration = 5 * 60
    long_break_duration = 15 * 60
    long_break_frequency = 4        # A long break after 4 sessions
    ui_plugin = "qtapp"
    task_plugin = "nulltask"

    def __init__(self, config_file, config_data={}):
        """Create an instance of pomito configuration."""
        self._config_file = os.environ.get("POMITO_CONFIG")
        if not self._config_file:
            self._config_file = config_file
        self._config_data = config_data
        self._parser = ConfigParser()
        self._initialized = False

    def get_setting(self, plugin):
        """Get setting for a plugin."""
        if not self._initialized:
            raise Exception("Configuration is not initialized. Did you call `load()`.")
        if self._parser.has_section(plugin):
            return self._parser.items(plugin)
        return []

    def load(self):
        """Parse the pomito user configuration file."""
        config_file = self._config_file
        config_data = self._config_data
        self._initialized = True

        data_loaded = False
        if config_file is not None and os.path.isfile(config_file):
            logger.info("Using configuration file '{0}'.".format(config_file))
            self._parser.read(config_file)
            data_loaded = True

        if config_data != {}:
            logger.info("Using config dictionary for configuration.")
            self._parser.read_dict(config_data)
            data_loaded = True

        if not data_loaded:
            logger.info("Config file '{0}' not found. Using defaults.".format(config_file))
            return

        if self._parser.has_section("pomito"):
            self.session_duration = self._get_seconds("pomito", "session_duration")
            self.short_break_duration = self._get_seconds("pomito", "short_break_duration")
            self.long_break_duration = self._get_seconds("pomito", "long_break_duration")
            self.long_break_frequency = self._parser.getint("pomito", "long_break_frequency")

        if self._parser.has_section("plugins"):
            self.ui_plugin = self._parser.get("plugins", "ui")
            self.task_plugin = self._parser.get("plugins", "task")

    def _get_seconds(self, section, setting):
        return math.floor(self._parser.getfloat(section, setting) * 60)
