# -*- coding: utf-8 -*-
"""
Pomito - Pomodoro timer on steroids.

Implementation of Qt user interface.
"""

import logging
import sys

from pyqtkeybind import keybinder
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QAbstractNativeEventFilter, QAbstractEventDispatcher

from pomito.plugins.ui import UIPlugin
from pomito.plugins.ui.qt.timer_window import TimerWindow

# Required for bundling svg icon support
from PyQt5 import QtSvg, QtXml  # noqa

QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot

logger = logging.getLogger("pomito.plugins.ui.qtapp")


class QtUI(UIPlugin):
    """UI plugin implementation with Qt."""

    def __init__(self, pomodoro_service):
        """Create an instance of the UI plugin.

        Args:
            pomodoro_service    service instance.
        """
        self._pomodoro_service = pomodoro_service

    def initialize(self):
        """Initialize the ui plugin."""
        self._app = PomitoApp(sys.argv)
        self._app.initialize(self._pomodoro_service)
        return

    def run(self):
        """Start ui loop."""
        return self._app.run()


# FIXME: we're accessing UI QObjects in timer callbacks; this may cause cross
# thread violation.
class PomitoApp(QtWidgets.QApplication):
    """Qt application."""

    keybinder = None

    def __init__(self, argv):
        """Create an instance of pomito application."""
        QtWidgets.QApplication.__init__(self, argv)
        self.keybinder = keybinder

    def initialize(self, pomodoro_service):
        """Initialize the application."""
        self._service = pomodoro_service
        self.keybinder.init()

        # Create all windows/taskbars
        self._timer_window = TimerWindow(self._service, self.keybinder)
        icon = QtGui.QIcon(":/icon_pomito")
        self._timer_window.setWindowIcon(icon)

    def run(self):
        """Start application loop."""
        # Install a native event filter to receive events from the OS
        win_event_filter = WinEventFilter(self.keybinder)
        event_dispatcher = QAbstractEventDispatcher.instance()
        event_dispatcher.installNativeEventFilter(win_event_filter)

        self._timer_window.show()
        self.exec_()


class WinEventFilter(QAbstractNativeEventFilter):
    """Event filter to trap hot keys."""

    def __init__(self, keybinder):
        """Create an instance of the event filter."""
        self.keybinder = keybinder
        super().__init__()

    def nativeEventFilter(self, eventType, message):
        """Filter shell events."""
        ret = self.keybinder.handler(eventType, message)
        return ret, 0
