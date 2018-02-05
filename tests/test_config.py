# -*- coding: utf-8 -*-
"""Tests for pomito configuration."""

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


def test_load_reads_default_settings_from_config(config):
    config.load()

    assert config.session_duration == 10 * 60
    assert config.short_break_duration == 2 * 60
    assert config.long_break_duration == 5 * 60
    assert config.long_break_frequency == 2


def test_get_setting_returns_empty_dictionary_if_section_not_exist(config):
    config.load()

    v = config.get_setting("no_plugin")

    assert v == []


def test_get_setting_returns_configuration_for_plugin(config):
    config.load()

    v = config.get_setting("section1")

    assert v == [("k1", "v1")]
