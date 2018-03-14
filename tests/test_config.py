# -*- coding: utf-8 -*-
"""Tests for pomito configuration."""

import os
import pytest
from pyfakefs import fake_filesystem

from pomito.config import Configuration


config_file = "config.ini"
config_data = {"pomito": {"session_duration": 10,
                          "short_break_duration": 2,
                          "long_break_duration": 5,
                          "long_break_frequency": 2},
               "plugins": {"ui": "customUI", "task": "customTask"},
               "section1": {"k1": "v1"}}


@pytest.fixture(scope="function")
def config(fs, mocker):
    # Create a fake config file
    os_module = fake_filesystem.FakeOsModule(fs)
    fileopen = fake_filesystem.FakeFileOpen(fs)

    # Patch filesystem calls with fake implementations
    mocker.patch("os.path", os_module.path)
    mocker.patch("builtins.open", fileopen)

    fs.CreateFile(config_file)
    _create_config(config_file, config_data)

    return Configuration(config_file)


def _create_config(config_file, config_data):
    with open(config_file, "w") as f:
        for section in config_data:
            f.write("[{0}]\n".format(section))
            for k, v in config_data[section].items():
                f.write("{0}={1}\n".format(k, v))


def test_default_settings_config_file_not_exist():
    config = Configuration("dummy_file")

    config.load()

    assert config.session_duration == 25 * 60
    assert config.short_break_duration == 5 * 60
    assert config.long_break_duration == 15 * 60
    assert config.long_break_frequency == 4


def test_default_settings_config_file_no_content(fs):
    config_file = "/tmp/empty_file.ini"
    fs.CreateFile(config_file)
    config = Configuration(config_file)

    config.load()

    assert config.session_duration == 25 * 60
    assert config.short_break_duration == 5 * 60
    assert config.long_break_duration == 15 * 60
    assert config.long_break_frequency == 4
    assert config.ui_plugin == "qtapp"
    assert config.task_plugin == "nulltask"


def test_load_reads_default_settings_from_config(config):
    config.load()

    assert config.session_duration == 10 * 60
    assert config.short_break_duration == 2 * 60
    assert config.long_break_duration == 5 * 60
    assert config.long_break_frequency == 2


def test_load_reads_config_data_if_available():
    config = Configuration(None, config_data)

    config.load()

    assert config.session_duration == 10 * 60
    assert config.short_break_duration == 2 * 60
    assert config.long_break_duration == 5 * 60
    assert config.long_break_frequency == 2


def test_load_reads_fractional_config_duration():
    fraction_data = {"pomito": {"session_duration": 0.12,
                                "short_break_duration": 0.21,
                                "long_break_duration": 0.53,
                                "long_break_frequency": 2}}
    config = Configuration(None, fraction_data)

    config.load()

    assert config.session_duration == 7
    assert config.short_break_duration == 12
    assert config.long_break_duration == 31
    assert config.long_break_frequency == 2


def test_load_prefers_config_data_over_file_settings(config):
    config._config_data = {"section1": {"k1": "v2"}}

    config.load()

    assert config.session_duration == 10 * 60
    assert config.short_break_duration == 2 * 60
    assert config.long_break_duration == 5 * 60
    assert config.long_break_frequency == 2
    assert config.get_setting("section1") == [("k1", "v2")]


def test_load_prefers_env_config_file_over_specified(config, fs):
    os.environ["POMITO_CONFIG"] = config_file
    try:
        c = Configuration("/tmp/non_existent.ini")

        c.load()

        assert c.session_duration == 10 * 60
        assert c.get_setting("section1") == [("k1", "v1")]
    finally:
        del os.environ["POMITO_CONFIG"]


def test_get_setting_throws_if_not_loaded(config):
    with pytest.raises(Exception):
        config.get_setting("section1")


def test_get_setting_returns_empty_dictionary_if_section_not_exist(config):
    config.load()

    v = config.get_setting("no_plugin")

    assert v == []


def test_get_setting_returns_configuration_for_plugin(config):
    config.load()

    v = config.get_setting("section1")

    assert v == [("k1", "v1")]
