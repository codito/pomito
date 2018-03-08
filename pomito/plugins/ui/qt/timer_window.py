# -*- coding: utf-8 -*-
"""Timer window for pomito."""
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

from pomito.plugins.ui.qt.task_widget import TaskWindow
from pomito.plugins.ui.qt.interrupt_widget import InterruptWindow
from pomito.plugins.ui.qt.shell import Taskbar, Tray
from pomito.plugins.ui.qt.utils import get_elided_text
from pomito.plugins.ui.qt.qt_timer import Ui_MainWindow
from pomito.pomodoro import TimerChange
from pomito.task import Task


class TimerWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Main window for the app."""

    def __init__(self, service, keybinder):
        """Create an instance of the main window.

        Args:
            service     pomito service instance.
            keybinder   keybinder instance.
        """
        QtWidgets.QMainWindow.__init__(self)
        self.keybinder = keybinder
        self._service = service
        self._session_active = False
        self._session_count = 0
        self._session_duration = 0
        self._interrupt_duration = 0
        self._last_session_timestamp = datetime.datetime.min

        # Setup exit action
        self._exit = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self)
        self._exit.activated.connect(self.close)

        # Setup child windows and taskbar
        self._interrupt_window = InterruptWindow(service)
        self._task_window = TaskWindow(service)
        self._task_bar = Taskbar()
        self._timer_tray = Tray(self, QtGui.QIcon(":/icon_pomito"))
        self._current_task = None

        # Setup user interface from designer
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        """Initialize the main window.

        Setup signals and event handlers.
        """
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.reset_timer(True)
        self.update_activity_label(None)

        # Setup signal handlers for UI elements
        self.btn_interrupt.clicked.connect(self.btn_interrupt_clicked)
        self.btn_timer.clicked.connect(self.btn_timer_clicked)
        self.btn_task.clicked.connect(self.btn_task_clicked)
        self._interrupt_window.interrupt_selected.connect(self.interrupt_selected)
        self._task_window.task_selected.connect(self.task_selected)

        # Setup signal handlers for pomodoro service
        self._service.signal_timer_increment.connect(self.on_timer_increment)
        self._service.signal_session_started.connect(self.on_session_start)
        self._service.signal_session_stopped.connect(self.on_session_stop)
        self._service.signal_interruption_started.connect(self.on_interrupt_start)
        self._service.signal_interruption_stopped.connect(self.on_interrupt_stop)

        # Setup platform specific configuration
        def toggle_timer():
            self.btn_timer_clicked(checked=self.btn_timer.isChecked,
                                   keyboard_context=True)

        def toggle_interrupt():
            self.btn_interrupt_clicked(checked=self.btn_interrupt.isChecked,
                                       keyboard_context=True)

        wid = self.winId()
        self.keybinder.register_hotkey(wid, "Alt+Ctrl+P", toggle_timer)
        self.keybinder.register_hotkey(wid, "Alt+Ctrl+I", toggle_interrupt)
        self._timer_tray.show()

    def reset_timer(self, reset_session):
        """Reset timer to initial state.

        Args:
            reset_session   starts a new pomodoro session if True
        """
        self._session_count = 0 if reset_session else self._session_count
        self.timer_lcd.display("00:00")
        self.update_activity_label(None)

    ###
    # UI overrides
    ###
    def closeEvent(self, event):
        event.accept()
        if self._session_active:
            self._service.stop_session()
        elif self.btn_interrupt.isChecked():
            self._service.stop_interruption()
        elif self.btn_timer.isChecked():
            self._service.stop_break()
        self._timer_tray.hide()

    def resizeEvent(self, resize_event):
        super(self.__class__, self).resizeEvent(resize_event)
        self.update_activity_label(None)
        return

    ###
    # UI signal handler slots
    ###
    def btn_interrupt_clicked(self, checked, keyboard_context=False):
        if keyboard_context:
            self.btn_interrupt.toggle()

        # Terminate curent session if one is active
        if self._session_active is True:
            self.btn_timer_clicked(False)

        if self.btn_interrupt.isChecked():
            self._interrupt_window.get_interruption()
        else:
            self._service.stop_interruption()
            self.reset_timer(False)

    def btn_task_clicked(self):
        self._task_window.get_task()

    def btn_timer_clicked(self, checked, keyboard_context=False):
        if keyboard_context:
            self.btn_timer.toggle()

        if self._session_active:
            self._service.stop_session()
            self.reset_timer(False)
        else:
            self._task_window.pending_session_start = True
            self._task_window.get_task()

    def update_activity_label(self, text):
        label = "Journey so far...\r\n"
        label += "Completed {0} pomodoros\r\n".format(self._session_count)
        label += "Spent {0:02d}:{1:02d}:{2:02d}hrs in interruptions".format(int(self._interrupt_duration / 60 / 60),
                                                                            int(self._interrupt_duration / 60),
                                                                            self._interrupt_duration % 60)
        if text is not None:
            label = text

        label = get_elided_text(self.activity_label.rect(), self.activity_label.font(), label)
        self.activity_label.setText(label)
        return

    @QtCore.Slot(str, bool, bool)
    def interrupt_selected(self, reason, is_external, add_unplanned_task):
        # Uncheck state if user opened interrupt window but closed it
        if reason is None:
            self.btn_interrupt.setChecked(False)
            return

        if self.btn_interrupt.isChecked():
            self._service.start_interruption(reason, is_external,
                                             add_unplanned_task)
            self.update_activity_label(reason)
            self.btn_timer.setChecked(True)
            self.btn_timer.setDisabled(True)
        else:
            raise Exception("Invalid state: selected interrupt while UI is checked!")
        return

    @QtCore.Slot(Task)
    def task_selected(self, task):
        if self.btn_interrupt.isChecked():
            # Don't do anything if session is active or interruption is running
            return

        if task is None:
            # User didn't select a task, uncheck the timer button
            self.btn_timer.setChecked(False)

        if self._session_active is False:
            # Uncheck state if user opened task window but closed it
            if task is None:
                self.btn_timer.setChecked(False)
                return

            # TODO display a nice animation of % task complete
            self._current_task = task
            self.update_activity_label(task.description)

            if self._task_window.pending_session_start:
                self._service.start_session(self._current_task)
                self._task_window.pending_session_start = False
                return

    ###
    # Pomodoro service signal handlers
    ###
    def on_timer_increment(self, time_elapsed):
        display_time = time_elapsed if self.btn_interrupt.isChecked() else (self._session_duration - time_elapsed)
        text = "{0:02d}:{1:02d}".format(int(display_time / 60), display_time % 60)
        self.timer_lcd.display(text)
        if not self.btn_interrupt.isChecked():
            self._task_bar.update(self.winId(), time_elapsed,
                                  self._session_duration)
        else:
            self._task_bar.indeterminate(self.winId())

    def on_session_start(self, *args, **kwargs):
        self._session_duration = kwargs["session_duration"]
        self._session_active = True
        self._notify_session_start()

    def on_session_stop(self, *args, **kwargs):
        # Reset session count if this is the first session of the day
        if self._last_session_timestamp.date() != datetime.datetime.now().date():
            self._session_count = 0
            self._last_session_timestamp = datetime.datetime.now()

        reason = "Ouch! Interrupted."
        if kwargs["reason"] == TimerChange.COMPLETE:
            self._session_count += 1
            reason = "Done done."

        self._session_active = False
        self.btn_timer.setChecked(False)
        self.update_activity_label(None)
        self._notify_session_stop(reason)

    def on_interrupt_start(self, *args, **kwargs):
        return

    def on_interrupt_stop(self, *args, **kwargs):
        self._interrupt_duration += kwargs['duration']
        self.btn_interrupt.setChecked(False)
        self.btn_timer.setDisabled(False)
        self.btn_timer.setChecked(False)
        self.update_activity_label(None)
        self._task_bar.reset(self.winId())

    def _notify_session_start(self):
        header = "Pomodoro started!"
        msg = "Stay focused..."
        self._task_bar.update(self.winId(), 0, self._session_duration)
        self._timer_tray.info(header, msg)

    def _notify_session_stop(self, reason):
        header = "Pomodoro ended!"
        msg = "{0} Sessions completed: {1}".format(reason, self._session_count)
        self._task_bar.pause(self.winId())

        self._timer_tray.info(header, msg)
