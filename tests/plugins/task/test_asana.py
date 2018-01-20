"""Tests for asana task plugin."""

import unittest
from unittest.mock import Mock, MagicMock

from asana.asana import AsanaAPI
from pyfakefs import fake_filesystem

from pomito.plugins.task.asana import AsanaTask
from pomito.test import PomitoTestFactory


class AsanaTests(unittest.TestCase):
    dummy_workspace_list = [{'id': 1, 'name': "ws1"}, {'id': 2, 'name': "ws2"}]
    dummy_task_list = [{'id': 1, 'name': "task1"}, {'id': 2, 'name': "task2"}]

    @classmethod
    def setUpClass(cls):
        cls.test_factory = PomitoTestFactory()
        cls.test_factory.config_file = "/tmp/fake_config.ini"

        # Create a fake config file
        filesystem = fake_filesystem.FakeFilesystem()
        cls.os_module = fake_filesystem.FakeOsModule(filesystem)
        cls.fileopen = fake_filesystem.FakeFileOpen(filesystem)
        fake_config_file = filesystem.CreateFile(cls.test_factory.config_file)
        fake_config_file.SetContents("""[task.asana]
                                     api_key = dummy_key
                                     """)

    def setUp(self):
        # Patch filesystem calls with fake implementations
        self.test_factory.create_patch(self, 'os.path', self.os_module.path)
        self.test_factory.create_patch(self, 'builtins.open', self.fileopen)

        self.pomodoro_service = self.test_factory.create_fake_service()

        self.asana_api = MagicMock(spec=AsanaAPI)
        self.asana = AsanaTask(self.pomodoro_service,
                               lambda api_key, debug=False: self.asana_api)

    def tearDown(self):
        self.pomodoro_service._pomito_instance.exit()

    def test_asana_can_create_asana_plugin(self):
        assert self.asana is not None

    def test_asana_raises_valueerror_for_no_pomodoro_service(self):
        self.assertRaises(ValueError, AsanaTask, None)

    def test_initialize_reads_api_key_from_config_file(self):
        # Create a mock factory to create AsanaAPI object
        get_asana_api = Mock()
        asana = AsanaTask(self.pomodoro_service, get_asana_api)

        asana.initialize()

        get_asana_api.assert_called_with("dummy_key")

    def test_initialize_does_not_throw_for_no_config(self):
        # Set _get_asana_api as None to ensure initialize throws
        a = AsanaTask(self.pomodoro_service, None)

        a.initialize()

    def test_initialize_does_not_throw_for_default_get_asana_api(self):
        a = AsanaTask(self.pomodoro_service)

        a.initialize()

    def test_get_tasks_does_not_throw_without_initialize(self):
        # Set asana_api as None so that AttributeError is thrown
        assert list(self.asana.get_tasks()) is not None

    def test_get_tasks_returns_list_of_task_objects(self):
        self.asana_api.list_workspaces\
            .return_value = [self.dummy_workspace_list[0]]
        self.asana_api.list_tasks.return_value = [{'id': 1, 'name': "t"}]
        self.asana.initialize()

        tasks = list(self.asana.get_tasks())

        assert len(tasks) == 1
        assert tasks[0].uid == 1
        assert tasks[0].description == "t"
        assert tasks[0].estimate == 0
        assert tasks[0].actual == 0
        assert tasks[0].tags is None

    def test_get_tasks_gets_tasks_from_all_workspaces(self):
        self.asana_api.list_workspaces.return_value = self.dummy_workspace_list
        self.asana_api.list_tasks.return_value = self.dummy_task_list
        self.asana.initialize()

        tasks = list(self.asana.get_tasks())

        self.asana_api.list_workspaces.assert_called_once_with()
        assert len(tasks) == 4

    def test_get_tasks_only_gets_tasks_assigned_to_me(self):
        self.asana_api.list_workspaces.return_value = self.dummy_workspace_list
        self.asana.initialize()

        tasks = list(self.asana.get_tasks())

        assert tasks is not None
        assert self.asana_api.list_tasks.call_count == 2
        self.asana_api.list_tasks.assert_any_call(1, "me")
        self.asana_api.list_tasks.assert_any_call(2, "me")

    def test_get_tasks_returns_empty_list_for_no_workspace(self):
        self.asana_api.list_tasks.return_value = self.dummy_task_list
        self.asana.initialize()

        tasks = list(self.asana.get_tasks())

        assert tasks == []

    def test_get_tasks_returns_empty_list_for_no_tasks(self):
        self.asana_api.list_workspaces.return_value = self.dummy_workspace_list
        self.asana.initialize()

        tasks = list(self.asana.get_tasks())

        assert tasks == []
