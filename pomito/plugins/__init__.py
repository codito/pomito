# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
# Base package for plugins

__all__ = ['initialize', 'get_plugin']

# TODO Enable plugin discovery, support for drop-in plugins
# TODO Validate plugins
# TODO Some plugins may fail to import due to dependencies, gracefully handle them
PLUGINS = {}

def initialize(pomodoro_service):
    """Discover plugins. Every plugin has access to the pomodoro_service layer only.

    Args:
        pomodoro_service pomodoro.Pomodoro - The pomodoro service object
    """
    import os

    from .ui import console
    from .task import text
    from .task import rtm

    global PLUGINS
    PLUGINS = {'console': console.Console(pomodoro_service),
               'text': text.TextTask(pomodoro_service),
               'rtm': rtm.RTMTask(pomodoro_service)}

    if os.environ.get("POMITO_TEST") is None:
        from .ui import qtapp

        PLUGINS['qtapp'] = qtapp.QtUI(pomodoro_service)

def get_plugin(plugin_name):
    return PLUGINS[plugin_name]
