# -*- coding: utf-8 -*-
"""
pomito.plugins package.

Base package for plugins.
"""

__all__ = ['initialize', 'get_plugin']

# TODO Enable plugin discovery, support for drop-in plugins
# TODO Validate plugins
# TODO Handle plugins may fail to import due to dependencies
PLUGINS = {}


def initialize(pomodoro_service):
    """Discover plugins.

    Every plugin has access to the pomodoro_service layer only.

    Args:
        pomodoro_service (pomodoro.Pomodoro): The pomodoro service object
    """
    import os

    from .ui import console
    from .task import asana
    from .task import rtm
    from .task import text
    from .task import nulltask

    global PLUGINS
    PLUGINS = {'console': console.Console(pomodoro_service),
               'asana': asana.AsanaTask(pomodoro_service),
               'text': text.TextTask(pomodoro_service),
               'rtm': rtm.RTMTask(pomodoro_service),
               'nulltask': nulltask.NullTask(pomodoro_service)}

    if os.environ.get("POMITO_TEST") is None:
        from .ui import qtapp

        PLUGINS['qtapp'] = qtapp.QtUI(pomodoro_service)
    else:
        # CI machines may not have Qt installed, ensure the lookup
        # doesn't fail
        PLUGINS['qtapp'] = None


def get_plugin(plugin_name):
    """Get a plugin by name.

    Args:
        plugin_name (string): name of the plugin.
    """
    return PLUGINS[plugin_name]


def get_plugins():
    """Get all plugins."""
    return PLUGINS
