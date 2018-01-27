# -*- coding: utf-8 -*-
"""Tests for trello plugin."""

import logging
import os
import pytest

from trello import TrelloClient
from pyfakefs import fake_filesystem
from unittest.mock import MagicMock

from pomito.pomodoro import Pomodoro
from pomito.plugins.task.trello import TrelloTask
from pomito.test import PomitoTestFactory


@pytest.fixture(scope="module")
def test_factory():
    """Create a pomodoro test factory."""
    test_factory = PomitoTestFactory()
    test_factory.config_file = "/tmp/fake_config.ini"
    return test_factory


@pytest.fixture
def trello_api(request):
    """Create a mock trello api client."""
    api_key = os.getenv("TRELLO_API_KEY")
    api_secret = os.getenv("TRELLO_API_SECRET")
    if api_key is None or api_secret is None:
        if request.node.get_marker("integration") is not None:
            pytest.skip("Trello integration test requires API keys.")
        return MagicMock(spec=TrelloClient)
    return TrelloClient(api_key, api_secret)


@pytest.fixture
def trello(request, test_factory, trello_api, fs, mocker):
    """Create a trello task object with fakes setup."""
    # Create a fake config file
    os_module = fake_filesystem.FakeOsModule(fs)
    fileopen = fake_filesystem.FakeFileOpen(fs)
    skip_key = getattr(request, 'param', None)
    _create_fake_config(fs, test_factory.config_file, skip_key)

    # Patch filesystem calls with fake implementations
    mocker.patch("os.path", os_module.path)
    mocker.patch("os.makedirs", os_module.makedirs)
    mocker.patch("builtins.open", fileopen)

    # Setup fake boards and lists
    pomodoro_service = test_factory.create_fake_service()
    trello = TrelloTask(pomodoro_service, lambda api_key, api_secret: trello_api)
    yield trello
    pomodoro_service._pomito_instance.exit()


def _create_fake_config(fs, config_file, skip_key=None):
    text = "[task.trello]\n"
    configs = {"api_key": "a", "api_secret": "a",
               "board": "PomitoTest", "list": "TestList"}
    if skip_key is not None:
        del configs[skip_key]

    fs.CreateFile(config_file)
    with open("/tmp/fake_config.ini", "w") as f:
        f.write(text)
        for c, v in configs.items():
            f.write("{0}={1}\n".format(c, v))


def test_trello_throws_for_invalid_pomodoro_service(trello):
    with pytest.raises(ValueError):
        TrelloTask(None, lambda key, secret: None)


def test_trello_can_create_trello_instance(trello):
    assert trello is not None


@pytest.mark.parametrize("trello",
                         ["api_key", "api_secret", "board", "list"],
                         indirect=True)
def test_initialize_logs_error_for_invalid_config(trello, caplog):
    trello.initialize()

    err_msg = "Error initializing plugin: No option"
    err_rec = [r for r in caplog.record_tuples if r[1] == logging.ERROR]
    assert 1 == len(err_rec)
    assert err_msg in err_rec[0][2]


@pytest.mark.integration
def test_get_tasks_returns_tasks_for_board_and_list(trello_api):
    pomodoro_service = MagicMock(spec=Pomodoro)
    trello = TrelloTask(pomodoro_service, lambda api_key, api_secret: trello_api)
    trello.initialize()
    trello.trello_board = "PomitoTest"
    trello.trello_list = "TestList"

    t = list(trello.get_tasks())

    assert len(t) == 2
