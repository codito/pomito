# -*- coding: utf-8 -*-
"""
Pomito - Pomodoro timer on steroids.

Abstractions over the OS shell.
"""
import logging
import sys

from PyQt5 import QtCore, QtDBus, QtWidgets

logger = logging.getLogger("pomito.plugins.ui.qtapp.shell")


class Taskbar(object):
    """Taskbar component for Qt user interface.

    Provides a safe abstraction on the Windows Taskbar.
    """

    TBPF_NOPROGRESS = 0
    TBPF_INDETERMINATE = 0x1
    TBPF_NORMAL = 0x2
    TBPF_ERROR = 0x4
    TBPF_PAUSED = 0x8

    taskbar = None

    def __init__(self):
        """Create an instance of the task bar."""
        if not self._is_windows():
            return

        import comtypes.client as cc
        cc.GetModule("wintaskbar.tlb")

        import comtypes.gen.TaskbarLib as tbl
        self.taskbar = cc.CreateObject(
            "{56FDF344-FD6D-11d0-958A-006097C9A090}",
            interface=tbl.ITaskbarList3)
        self.taskbar.HrInit()

    def indeterminate(self, win_id):
        """Set task bar progress to indeterminate.

        Args:
            win_id (HANDLE):    handle to the main Window.
        """
        if not self._is_windows():
            return
        self.taskbar.SetProgressState(win_id, Taskbar.TBPF_INDETERMINATE)

    def update(self, win_id, progress, limit):
        """Set task bar progress.

        Args:
            win_id (HANDLE): handle to the main Window.
            progress (int): current progress.
            limit (int): maximum limit for the progress.
        """
        if not self._is_windows():
            return
        self.taskbar.SetProgressValue(win_id, progress, limit)
        self.taskbar.SetProgressState(win_id, Taskbar.TBPF_NORMAL)

    def reset(self, win_id):
        """Reset the taskbar to zero state.

        Args:
            win_id (HANDLE): handle to the main Window.
        """
        if not self._is_windows():
            return
        self.taskbar.SetProgressState(win_id, Taskbar.TBPF_NOPROGRESS)

    def pause(self, win_id):
        """Pause the progress bar.

        Args:
            win_id (HANDLE): handle to the main Window.
        """
        if not self._is_windows():
            return
        self.taskbar.SetProgressState(win_id, Taskbar.TBPF_PAUSED)

    def _is_windows(self):
        return sys.platform.startswith("win")


class Tray(object):
    """A system tray component for the Qt app."""

    # TODO Find a way to bring timerwindow into focus when user clicks
    # on system tray notification
    # self._timer_tray.messageClicked.connect
    _supported = False

    def __init__(self, parent, icon):
        """Create an instance of the system tray component.

        Args:
            parent (QWidget): owner widget for this component
            icon (QIcon): an icon for the tray
        """
        if QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            self._timer_tray = QtWidgets.QSystemTrayIcon(parent)
            self._timer_tray.setIcon(icon)
            self._supported = True

    def show(self):
        """Show the tray icon."""
        if self._supported:
            self._timer_tray.show()

    def hide(self):
        """Hide the tray icon."""
        if self._supported:
            self._timer_tray.hide()

    def info(self, header, message):
        """Show an informational message on the system tray.

        Uses system tray for notifications in Windows.
        Prefers DBus notifications in Linux, fallback to system tray if not
        available.

        Args:
            header (str): header for the message
            message (str): message text
        """
        if not self._notify(header, message):
            info_icon = QtWidgets.QSystemTrayIcon.Information
            self._timer_tray.showMessage(header, message, info_icon)

    def _notify(self, header, msg):
        if self._is_windows():
            return False

        item = "org.freedesktop.Notifications"
        path = "/org/freedesktop/Notifications"
        interface = "org.freedesktop.Notifications"
        app_name = "pomito"
        v = QtCore.QVariant(100021)  # random int to identify all notifications
        if v.convert(QtCore.QVariant.UInt):
            id_replace = v
        icon = ""
        title = header
        text = msg
        actions_list = QtDBus.QDBusArgument([], QtCore.QMetaType.QStringList)
        hint = {}
        time = 100   # milliseconds for display timeout

        bus = QtDBus.QDBusConnection.sessionBus()
        if not bus.isConnected():
            logger.debug("Not connected to dbus!")
            return False

        notify = QtDBus.QDBusInterface(item, path, interface, bus)
        if notify.isValid():
            x = notify.call(QtDBus.QDBus.AutoDetect, "Notify", app_name,
                            id_replace, icon, title, text,
                            actions_list, hint, time)
            if x.errorName():
                logger.debug("Failed to send notification!")
                logger.debug(x.errorMessage())
                return False
        else:
            logger.debug("Invalid dbus interface")
            return False
        return True

    def _is_windows(self):
        return sys.platform.startswith("win")
