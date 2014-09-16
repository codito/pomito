# Pomito - Pomodoro timer in steroids
# A simple console UI plugin

import cmd

import click

from pomito.plugins import ui

_POMODORO_SERVICE = None
def _get_pomodoro_service():
    """Gets pomodoro service."""
    if _POMODORO_SERVICE is None:
        raise RuntimeError("Console.pomodoro_service is not initialized.")
    return _POMODORO_SERVICE

def _set_pomodoro_service(pomodoro_service):
    """Sets pomodoro service."""
    # pylint: disable=global-statement
    global _POMODORO_SERVICE
    _POMODORO_SERVICE = pomodoro_service

class Console(ui.UIPlugin, cmd.Cmd):
    """Interactive shell for pomito app."""
    intro = "Welcome to Pomito shell.\n\
Type 'help' or '?' to list available commands."
    prompt = "pomito> "

    def __init__(self, pomodoro_service):
        self._message_queue = []
        _set_pomodoro_service(pomodoro_service)
        cmd.Cmd.__init__(self)

    def initialize(self):
        pass

    def do_help(self, args):
        print("List of commands:")
        print("?/help   Show this help")
        print("start    Start a session")
        print("stop     Stop the currently running session")
        print("quit     Quit the application")
        return

    def do_quit(self, args):
        """Quit the shell."""
        print("Good bye!")
        return False

    def do_start(self, args):
        tasks = self._pomodoro.get_tasks()
        c = 0
        for t in tasks:
            print("[{0}] {1}".format(c, t))
            c += 1

        tid = ""
        while tid.isdigit() == False:
            tid = input("Enter task id: ")
        self._pomodoro.start_session(tasks[int(tid)])
        return

    def do_stop(self, args):
        self._pomodoro.stop_session()
        return

    def postcmd(self, stop, line):
        if line == "quit":
            stop = True
        return stop

    def _print_message(self, msg):
        print(msg)
        return

    def notify_session_started(self):
        self._print_message("Pomodoro session started.")
        self._message_queue.append("Pomodoro session started.")
        return

    def notify_session_end(self, reason):
        self._print_message("Pomodoro session ended.")
        self._message_queue.append("Pomodoro session ended.")
        return

    def notify_break_started(self, break_type):
        self._print_message("Pomodoro break started: {0}".format(break_type))
        self._message_queue.append("Pomodoro break started: {0}".format(break_type))
        return

    def notify_break_end(self, reason):
        self._print_message("Pomodoro break ended: {0}".format(reason))
        self._message_queue.append("Pomodoro break ended: {0}".format(reason))
        return

    def run(self):
        if len(self._message_queue) > 0:
            print("-- msg: {0}".format(self._message_queue.pop()))
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            self._print_message("Got keyboard interrupt.")
            self.do_quit(None)
        return

@click.group()
def pomito_shell():
    """Command group for pomito interactive shell."""
    pass

@pomito_shell.command("start")
@click.argument('task_id', type=int)
def pomito_start(task_id):
    """Starts a pomito session."""
    pomodoro_service = _get_pomodoro_service()
    tasks = pomodoro_service.get_tasks()
    pomodoro_service.start_session(tasks[int(task_id)])

