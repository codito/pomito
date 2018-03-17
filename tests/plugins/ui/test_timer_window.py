# -*- coding: utf-8 -*-
"""Tests for the timer window."""

import pytest

from pomito.plugins.ui.qt.timer_window import TimerWindow
from pomito.test import PomitoTestFactory, FakeKeyBinder


@pytest.fixture(scope="function")
def timer_window(qtbot):
    factory = PomitoTestFactory()

    pomodoro_service = factory.create_fake_service()
    timer = TimerWindow(pomodoro_service, FakeKeyBinder())
    qtbot.addWidget(timer)
    return timer


@pytest.mark.integration
def test_timer_window_pomodoro_session(qtbot, timer_window):
    # with qtbot.waitSignal(task_window.task_selected):
    #    task_window.get_task()

    # assert task_window.list_task is not None
    pass
