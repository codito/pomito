# -*- coding: utf-8 -*-
"""Trello plugin for pomito."""

import logging

from trello import TrelloClient

from pomito.plugins import task
from pomito.task import Task

__all__ = ['TrelloTask']

logger = logging.getLogger('pomito.plugins.task.trello')


def _create_trello_client(api_key, api_secret):
    """Create default TrelloClient instance."""
    return TrelloClient(api_key=api_key, api_secret=api_secret)


class TrelloTask(task.TaskPlugin):
    """Trello task plugin for pomito."""

    def __init__(self, pomodoro_service, get_trello_api=_create_trello_client):
        """Create an instance of TrelloTask."""
        if pomodoro_service is None:
            raise ValueError("pomodoro_service must not be None.")
        self._get_trello_client = get_trello_api
        self._pomodoro_service = pomodoro_service

        self.trello_api = None
        self.trello_board = None
        self.trello_list = None

    def initialize(self):
        """Initialize the trello task plugin."""
        def _get_config(config):
            return self._pomodoro_service.get_config("task.trello", config)

        api_key = _get_config("api_key")
        api_secret = _get_config("api_secret")
        self.trello_board = _get_config("board")
        self.trello_list = _get_config("list")

        self.trello_api = self._get_trello_client(api_key, api_secret)
        if api_key is None or api_secret is None\
                or self.trello_board is None or self.trello_list is None:
            logger.error("Error initializing plugin: invalid configuration")

    def get_tasks(self):
        """Get all incomplete tasks assigned to the user."""
        # TODO support for dueDates
        try:
            def create_task(card):
                """Create a `Task` object from a trello dict."""
                return Task(uid=card.id,
                            estimate=0,
                            actual=0,
                            tags=card.labels,
                            description=card.name)

            for b in self.trello_api.list_boards():
                if self.trello_board is not None and b.name != self.trello_board:
                    continue

                if self.trello_list is not None:
                    lists = [lo for lo in b.list_lists() if lo.name == self.trello_list]
                else:
                    lists = b.list_lists()

                for l in lists:
                    yield from map(create_task, l.list_cards())
        except AttributeError as attrib_error:
            logger.error("Error getting tasklist: {0}".format(attrib_error))
