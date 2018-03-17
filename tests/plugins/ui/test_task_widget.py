# -*- coding: utf-8 -*-
"""Tests for task widget."""

import pytest

from pomito.plugins.ui.qt.task_widget import TaskWindow
from pomito.test import PomitoTestFactory


@pytest.fixture(scope="function")
def task_window(qtbot):
    factory = PomitoTestFactory()
    factory.config_file = "tests/data/config.ini"
    factory.config_data["plugins"]["task"] = "text"

    pomodoro_service = factory.create_fake_service()
    task_window = TaskWindow(pomodoro_service)
    qtbot.addWidget(task_window)
    return task_window


@pytest.mark.integration
def test_task_widget_lists_tasks(qtbot, task_window):
    def tasks_loaded():
        assert task_window.list_task.model().rowCount(0) == 7

    task_window.get_task()

    qtbot.waitUntil(tasks_loaded, timeout=10000)
    assert task_window.list_task.model().rowCount(0) == 7
