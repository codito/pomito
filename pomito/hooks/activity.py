# -*- coding: utf-8 -*-
# Pomito - Pomodoro timer on steroids.
"""Activity module maintains a log of all user activities."""


from datetime import datetime

from pomito.hooks import Hook

from peewee import Model, Proxy, DateTimeField, CharField, TextField

database_proxy = Proxy()


class ActivityHook(Hook):
    """Activity hook listens to session and interruption events.

    Keeps a record of pomodoro statistics.
    """

    def __init__(self, service):
        self._service = service

    def initialize(self):
        database_proxy.initialize(self._service.get_db())
        ActivityModel.create_table(True)

        self._service.signal_session_stopped\
            .connect(self.handle_session_stopped)
        self._service.signal_break_stopped.connect(self.handle_break_stopped)
        self._service.signal_interruption_stopped\
            .connect(self.handle_interruption_stopped)

    def log(self, category, data):
        activity = ActivityModel(timestamp=datetime.now(),
                                 category=category,
                                 data=data)
        activity.save()

    def close(self):
        self._service.signal_session_stopped\
            .disconnect(self.handle_session_stopped)
        self._service.signal_break_stopped\
            .disconnect(self.handle_break_stopped)
        self._service.signal_interruption_stopped\
            .disconnect(self.handle_interruption_stopped)

    ####
    # Pomodoro service signal handlers
    ####
    def handler(category):
        def wrapper(func):
            def inner(self, *args, **kwargs):
                data = ";".join(["{0}={1}".format(k, v.__str__()) for k, v in
                                 list(kwargs.items())])
                self.log(category, data)
            return inner
        return wrapper

    @handler(category="break")
    def handle_break_stopped(self, *args, **kwargs): pass    # pragma: no cover

    @handler(category="session")
    def handle_session_stopped(self, *args, **kwargs): pass  # pragma: no cover

    @handler(category="interruption")
    def handle_interruption_stopped(self, *args, **kwargs):  # pragma: no cover
        pass


class ActivityModel(Model):
    timestamp = DateTimeField()
    category = CharField(index=True)
    data = TextField()

    class Meta:
        database = database_proxy
