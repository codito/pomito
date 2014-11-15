# Pomito - Pomodoro timer on steroids
# A text file based task plugin implementation

import pomito.task
from pomito.plugins import task
from io import open



class TextTask(task.TaskPlugin):
    """Implements a plugin to read/write Tasks from a text file.
    See doc/sample_tasks.txt for details of task file.
    """
    _file = None

    def __init__(self, pomodoro_service):
        self._pomodoro_service = pomodoro_service
        self.tasks = []

    def initialize(self):
        # Read plugin configuration
        try:
            file_path = self._pomodoro_service.get_config("task.text", "file")
            self._file = open(file_path, 'r')
            for t in self._file.readlines():
                if not t.startswith("--"):
                    task_tuple = self.parse_task(t)
                    self.tasks.append(pomito.task.Task(*task_tuple))
        except Exception as e:
            print(("Task.Text: Error initializing plugin: {0}".format(e)))
        finally:
            if self._file is not None:
                self._file.close()
        return

    def get_tasks(self):
        return self.tasks

    def parse_task(self, task):
        return TextTask.parse_task(task)

    @staticmethod
    def parse_task(task):
        import re

        # Sample task format: I:<id> | E:<estimate> | A:<actual> | T:<tags> | D:<desc>
        # Only <desc> can contain spaces. <tags> can be comma separated
        p = re.compile("[IEATD]:([\w,\s]*)\|?")
        task_tuple = tuple(map(lambda x: x.groups()[-1].strip('\n '), p.finditer(task)))
        return task_tuple
