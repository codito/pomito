# -*- coding: utf-8 -*-
"""A text file based task plugin implementation."""

import logging

from pomito.plugins import task
from pomito.task import Task
from io import open


__all__ = ['TextTask']
logger = logging.getLogger('pomito.plugins.task.text')


class TextTask(task.TaskPlugin):
    """Implements a plugin to read/write Tasks from a text file.
    See doc/sample_tasks.txt for details of task file.
    """

    def __init__(self, pomodoro_service):
        self._pomodoro_service = pomodoro_service
        self.tasks = []

    def initialize(self):
        # Read plugin configuration
        try:
            file_path = self._pomodoro_service.get_config("task.text", "file")
            with open(file_path, 'r') as f:
                for t in f.readlines():
                    if not t.startswith("--"):
                        task_tuple = self.parse_task(t)
                        self.tasks.append(Task(*task_tuple))
        except Exception as e:
            logger.debug(("Error initializing plugin: {0}".format(e)))
        return

    def get_tasks(self):
        return self.tasks

    def parse_task(self, task):
        return TextTask._parse_task(task)

    @staticmethod
    def _parse_task(task):
        import re

        # Sample task format: I:<id> | E:<estimate> | A:<actual> | T:<tags> | D:<desc>
        # Only <desc> can contain spaces. <tags> can be comma separated
        p = re.compile("[IEATD]:([\w,\s]*)\|?")
        task_tuple = tuple(map(lambda x: x.groups()[-1].strip('\n '), p.finditer(task)))
        return task_tuple
