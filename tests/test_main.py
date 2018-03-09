# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
"""Tests for the Main module."""

import os
from unittest.mock import Mock, MagicMock, patch

import tempfile
import pytest
from contextlib import contextmanager
from peewee import SqliteDatabase

from pomito import main
from pomito.plugins.ui import UIPlugin
from pomito.plugins.task import TaskPlugin
from pomito.hooks import Hook
from pomito.test import FakeTaskPlugin, FakeUIPlugin, PomitoTestFactory


"""
Tests for main class.

TODO
run: returns for invalid state

exit: sets the stop event
exit: calls close on all hooks
exit: writes the configuration
"""


@pytest.fixture(scope="function")
def memory_db():
    return SqliteDatabase(':memory:')


@pytest.fixture(scope="function")
def pomito_instance(memory_db):
    test_factory = PomitoTestFactory()

    dummy_config = test_factory.create_fake_config()
    pomito = main.Pomito(config=dummy_config, database=memory_db)
    _setup_pomito_plugins(pomito)
    _setup_pomito_hooks(pomito)
    return pomito


def test_default_hooks():
    from pomito.hooks.activity import ActivityHook

    pomito = main.Pomito()

    assert len(pomito._hooks) == 1
    assert isinstance(pomito._hooks[0], ActivityHook)
    pomito.exit()


def test_default_plugins():
    from pomito.plugins import PLUGINS
    default_plugins = ["console", "asana", "rtm", "text", "trello",
                       "nulltask", "qtapp"]

    assert all([x in set(PLUGINS.keys()) for x in default_plugins])


def test_custom_plugins():
    pass


def test_initialize_creates_database_if_not_present():
    with _setup_data_dir():
        pomito = main.Pomito()
        _setup_pomito_plugins(pomito)

        with patch('sqlite3.connect', MagicMock()):
            pomito.initialize()

        assert pomito.get_db() is not None
        pomito.exit()


def test_initialize_uses_injected_database():
    dummy_db = SqliteDatabase(':memory:')
    pomito = main.Pomito(database=dummy_db)
    _setup_pomito_plugins(pomito)

    with patch('sqlite3.connect', MagicMock()):
        pomito.initialize()

    assert pomito.get_db() == dummy_db
    pomito.exit()


def test_initialize_setup_plugins_and_hooks():
    with _setup_data_dir():
        pomito = main.Pomito()
        _setup_pomito_plugins(pomito)
        _setup_pomito_hooks(pomito)

        with patch('sqlite3.connect', MagicMock()):
            pomito.initialize()

        assert pomito.ui_plugin.initialize.call_count == 1
        assert pomito.task_plugin.initialize.call_count == 1
        assert pomito._hooks[0].initialize.call_count == 1
        pomito.exit()


def test_run_no_op_for_invalid_state(pomito_instance):
    pomito_instance.run()

    pomito_instance.ui_plugin.run.assert_not_called()


def test_run_invokes_ui_plugin(pomito_instance):
    pomito_instance.ui_plugin = FakeUIPlugin()
    pomito_instance.task_plugin = FakeTaskPlugin()

    pomito_instance.run()

    assert pomito_instance.ui_plugin.started


def test_exit_closes_database(pomito_instance, memory_db):
    pomito_instance.exit()

    assert memory_db.is_closed


def _setup_pomito_plugins(pomito):
    pomito.ui_plugin = Mock(spec=UIPlugin)
    pomito.task_plugin = Mock(spec=TaskPlugin)


def _setup_pomito_hooks(pomito):
    pomito._hooks[0] = Mock(spec=Hook)


@contextmanager
def _setup_data_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = main.DATA_DIR
        main.DATA_DIR = os.path.join(tmpdir, "pomito")
        try:
            yield
        finally:
            main.DATA_DIR = data_dir
