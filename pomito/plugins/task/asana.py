"""Task plugin for http://www.asana.com"""

import logging

from asana.asana import AsanaAPI

from pomito.plugins import task
from pomito.task import Task

__all__ = ['AsanaTask']

# pylint: disable=invalid-name
logger = logging.getLogger('pomito.plugins.task.asana')

def _create_asana_api(api_key, debug=False):
    """Creates default AsanaAPI instance."""
    return AsanaAPI(api_key, debug)

class AsanaTask(task.TaskPlugin):
    """Asana task plugin for pomito."""

    def __init__(self, pomodoro_service, get_asana_api=_create_asana_api):
        if pomodoro_service is None:
            raise ValueError("pomodoro_service must not be None.")
        self._get_asana_api = get_asana_api
        self._pomodoro_service = pomodoro_service

        self.asana_api = None

    def initialize(self):
        try:
            api_key = self._pomodoro_service.get_config("task.asana", "api_key")
            self.asana_api = self._get_asana_api(api_key)
        except Exception as ex: # pylint: disable=broad-except
            logger.error("Error initializing plugin: {0}".format(ex))

    def get_tasks(self):
        try:
            def create_task(asana_task):
                """Create a `Task` object from a asana dict."""
                return Task(uid=asana_task['id'],
                            estimate=0,
                            actual=0,
                            tags=None,
                            description=asana_task['name'])

            for workspace in self.asana_api.list_workspaces():
                # pylint: disable=bad-builtin
                yield from map(create_task,
                               self.asana_api.list_tasks(workspace['id'], "me"))
        except AttributeError as attrib_error:
            logger.error("Error getting tasklist: {0}".format(attrib_error))

    def is_valid_task(self, input_task):
        raise NotImplementedError
