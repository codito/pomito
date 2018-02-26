# -*- coding: utf-8 -*-
"""Tests for task widget."""

import os
# import pytest

from pomito.plugins.ui.qt.task_widget import TaskWindow
from pomito.test import PomitoTestFactory


# @pytest.fixture(scope="function")
def task_window(qtbot):
    factory = PomitoTestFactory()
    use_trello = False
    if use_trello:
        api_key = os.getenv("TRELLO_API_KEY")
        api_secret = os.getenv("TRELLO_API_SECRET")
        if api_key is not None and api_secret is not None:
            factory.config_data["task.trello"] = {
                "api_key": api_key,
                "api_secret": api_secret,
                "board": "",
                "list": ""
            }
            factory.config_data["plugins"]["task"] = "trello"

    pomodoro_service = factory.create_fake_service()
    task_window = TaskWindow(pomodoro_service)
    qtbot.addWidget(task_window)
    return task_window


# @pytest.mark.integration
# def test_task_widget_lists_tasks(qtbot, task_window):
    # task_window.initialize()

    # with qtbot.waitSignal(task_window.task_selected):
    #    task_window.get_task()

    # assert task_window.list_task is not None
    # pass
