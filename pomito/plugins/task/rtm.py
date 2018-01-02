# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids
# A Remember The Milk based task plugin implementation

import pomito.task
from pomito.plugins import task

class RTMTask(task.TaskPlugin):
    """Implements a plugin to read/write Tasks from a RememberTheMilk account."""
    _file = None

    def __init__(self, pomodoro_service):
        self._pomodoro_service = pomodoro_service
        self.name = "rtm"
        self.tasks = []
        return

    def get_tasks(self):
        return self.tasks

    def initialize(self):
        self.update_config()
        self.refresh_tasks()
        return

    def parse_task(self, taskseries):
        # Sample task format: I:<id> | E:<estimate> | A:<actual> | T:<tags> | D:<desc>
        # Only <desc> can contain spaces. <tags> can be comma separated
        # TODO maintain journal in the task notes itself? Actual should also go
        # there
        # XXX estimate must be digits only, strip off the digits?
        tags = taskseries.tags
        if hasattr(taskseries.tags, "tag") and \
           hasattr(taskseries.tags.tag, "__getitem__"):
            tags = taskseries.tags.tag
        return (taskseries.task.id, 0, 0, tags, taskseries.name)

    def refresh_tasks(self):
        rspTasks = self._rtm.tasks.getList(filter=self._task_filter)
        if hasattr(rspTasks.tasks, "list") and \
           hasattr(rspTasks.tasks.list, "__getitem__"):
            for l in rspTasks.tasks.list:
                # XXX: taskseries *may* be a list
                if isinstance(l.taskseries, (list, tuple)):
                    for t in l.taskseries:
                        task_tuple = self.parse_task(t)
                        self.tasks.append(pomito.task.Task(*task_tuple))
                else:
                    raise Exception("RTM plugin: failed to get tasks!")

    def update_config(self):
        """Read configuration from ini file. Update the local values."""
        self._config = self._pomodoro_service.get_config(self.name)
        self._apikey = self._config["apikey"]
        self._secret = self._config["secret"]
        self._token = self._config["token"]
        self._task_filter = self._config["filter"]
        self._rtm = rtm.createRTM(self._apikey, self._secret, self._token)

        if self._token is None:
            # TODO invoke xdg-open, browser, get authentication
            # save token into config file...
            pass
        self._task_filter = 'dueBefore:tomorrow AND status:incomplete'
        return
