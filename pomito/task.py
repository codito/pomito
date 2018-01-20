# Pomito - Pomodoro timer on steroids
"""Task concept and routines."""

import hashlib


class Task(object):
    """A Task is an activity that the user is working on during a pomodoro session."""

    def __init__(self, uid, estimate, actual, tags, description):
        """Create a Task.

        Args:
            description: Description of the task
            estimated_time: Estimated pomodoros to complete the task
            priority: Priority associated with the task
            actual: Number of pomodoros completed
        """
        try:
            self.uid = uid
            self.description = description
            self.estimate = int(estimate)
            self.actual = int(actual)
            self.tags = tags
            self.completed = 0  # If a task is completed, there should be no object created
        except ValueError:
            raise Exception("Attempt to parse invalid task. Task attributes: '{0}' '{1}' '{2}' '{3}' '{4}'"
                            .format(uid, description, estimate, actual, tags))

        # Every task will have a unique id, which is the md5sum of description.
        if self.uid is None:
            m = hashlib.md5()
            m.update(self.description.encode('utf-8'))
            self.uid = m.hexdigest()

        return

    def __str__(self):
        """Get a string representation for the task."""
        return "I:{0} | E:{1} | A:{2} | T:{3} | D:{4}"\
            .format(self.uid, self.estimate, self.actual, self.tags,
                    self.description)

    def update_actual(self):
        """Update actual pomodoros for a task."""
        self.actual += 1

    def update_estimate(self, new_estimate):
        """Update estimated pomodoros for a task."""
        self.estimate = int(new_estimate)

    def mark_complete(self):
        """Mark a task as complete."""
        self.completed = 1


def get_null_task():
    """Get a null task."""
    return Task(0, 0, 0, None, "No task selected.")
