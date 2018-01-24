# -*- coding: utf-8 -*-
"""Task plugin for http://www.asana.com."""

import logging

import asana

from pomito.plugins import task
from pomito.task import Task

__all__ = ['AsanaTask']

logger = logging.getLogger('pomito.plugins.task.asana')


def _create_asana_api(api_key, debug=False):
    """Create default AsanaAPI instance."""
    return asana.Client.access_token(api_key)


class AsanaTask(task.TaskPlugin):
    """Asana task plugin for pomito."""

    def __init__(self, pomodoro_service, get_asana_api=_create_asana_api):
        """Create an instance of AsanaTask."""
        if pomodoro_service is None:
            raise ValueError("pomodoro_service must not be None.")
        self._get_asana_api = get_asana_api
        self._pomodoro_service = pomodoro_service

        self.asana_api = None

    def initialize(self):
        """Initialize the asana task plugin."""
        try:
            api_key = self._pomodoro_service.get_config("task.asana", "api_key")
            self.asana_api = self._get_asana_api(api_key)
        except Exception as ex:
            logger.error("Error initializing plugin: {0}".format(ex))

    def get_tasks(self):
        """Get all incomplete tasks assigned to the user."""
        # TODO support for sections, tags
        try:
            def create_task(asana_task):
                """Create a `Task` object from a asana dict."""
                return Task(uid=asana_task['id'],
                            estimate=0,
                            actual=0,
                            tags=None,
                            description=asana_task['name'])

            me = self.asana_api.users.me()
            for w in me['workspaces']:
                yield from map(create_task,
                               self.asana_api.tasks.find_all({'assignee': "me",
                                                              'workspace': w['id'],
                                                              'completed_since': "now"}))
        except AttributeError as attrib_error:
            logger.error("Error getting tasklist: {0}".format(attrib_error))
