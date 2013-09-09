# Pomito - Pomodoro timer on steroids
# Task concept and routines

import hashlib

class Task(object):
    """A Task is an activity that the user is working on during a pomodoro session."""

    def __init__(self, uid, estimate, actual, tags, description):
        """Constructor for a Task

        Args:
            description: Description of the task
            estimated_time: Estimated time to complete the task
            priority: Priority associated with the task
            percent_complete: Amount of task completed (a percent)
        """
        try:
            self.uid = uid
            self.description = description
            self.estimate = int(estimate)
            self.actual = int(actual)
            self.tags = tags
            self.completed = 0  # If a task is completed, there should be no object created
        except ValueError:
            print("Attempt to parse invalid task. Task attributes: '{0}' '{1}' '{2}' '{3}' '{4}'"\
                  .format(uid, description, estimate, actual, tags))

        # Every task will have a unique id, which is the md5sum of description.
        if self.uid == None:
            m = hashlib.md5()
            m.update(self.description)
            self.uid = m.hexdigest()

        return

    def __str__(self):
        return "I:{0} | E:{1} | A:{2} | T:{3} | D:{4}".format(self.uid, self.estimate,
                                                              self.actual, self.tags,
                                                              self.description)

    def update_actual(self):
        self.actual += 1
        return

    def update_estimate(self, new_estimate):
        self.estimate = new_estimate
        return

    def completed(self):
        self.completed = 1
        return

    @staticmethod
    def parse(task):
        from .plugins.task import text

        return Task(*text.TextTask.parse(str(task)))

def get_null_task():
    """Returns a null task."""
    return Task(0, 0, 0, None, "No task selected.")
