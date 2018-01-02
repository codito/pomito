# -*- coding: utf-8 -*-
"""
Pomito - Pomodoro timer on steroids.

Implementation of Qt user interface.
"""

from .qt_timer import Ui_MainWindow
from .qt_task import Ui_TaskWindow
from .qt_interrupt import Ui_InterruptionWindow
from pyqtkeybind import keybinder

import datetime
import logging
import sys

from pomito.task import Task
from pomito.plugins import ui
from PyQt5 import QtCore, QtDBus, QtGui, QtWidgets
from PyQt5.QtCore import QAbstractNativeEventFilter, QAbstractEventDispatcher

QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot

logger = logging.getLogger("pomito.plugins.ui.qtapp")


class QtUI(ui.UIPlugin):
    def __init__(self, pomodoro_service):
        self._pomodoro_service = pomodoro_service

    def initialize(self):
        import sys
        self._app = PomitoApp(sys.argv)
        self._app.initialize(self._pomodoro_service)
        return

    def run(self):
        return self._app.run()


# FIXME: we're accessing UI QObjects in timer callbacks; this may cause cross
# thread violation.
class PomitoApp(QtWidgets.QApplication):
    keybinder = None

    def __init__(self, argv):
        QtWidgets.QApplication.__init__(self, argv)
        self.keybinder = keybinder
        return

    def initialize(self, pomodoro_service):
        self._pomodoro_service = pomodoro_service
        self.keybinder.init()

        # Create all windows/taskbars
        self._timer_window = TimerWindow(self._pomodoro_service, self.keybinder)
        icon = QtGui.QIcon(":/icon_pomito")
        self._timer_window.setWindowIcon(icon)

        return

    def run(self):
        # self.keybinder.init()
        # callback = lambda: print("hello world")
        # self.keybinder.register_hotkey(None, "Shift-F3", callback)

        # Install a native event filter to receive events from the OS
        win_event_filter = WinEventFilter(self.keybinder)
        event_dispatcher = QAbstractEventDispatcher.instance()
        event_dispatcher.installNativeEventFilter(win_event_filter)

        self._timer_window.show()
        self.exec_()
        return


class TaskbarList(object):
    """ Support for Windows Taskbar"""
    TBPF_NOPROGRESS = 0
    TBPF_INDETERMINATE = 0x1
    TBPF_NORMAL = 0x2
    TBPF_ERROR = 0x4
    TBPF_PAUSED = 0x8

    taskbar = None

    def __init__(self):
        import sys
        if not sys.platform.startswith("win"):
            return
        import comtypes.client as cc
        cc.GetModule("wintaskbar.tlb")

        import comtypes.gen.TaskbarLib as tbl
        self.taskbar = cc.CreateObject(
            "{56FDF344-FD6D-11d0-958A-006097C9A090}",
            interface=tbl.ITaskbarList3)
        self.taskbar.HrInit()
        return

    @classmethod
    def getptr(cls, pycobject):
        # Imports all we need
        from ctypes import pythonapi, c_void_p, py_object

        # Setup arguments and return types
        pythonapi.PyCapsule_GetPointer.restype = c_void_p
        pythonapi.PyCapsule_GetPointer.argtypes = [py_object]

        # Convert PyCObject to a void pointer
        # return pythonapi.PyCapsule_GetPointer(pycobject)
        return pycobject


class QtUtilities:
    @classmethod
    def getElidedText(cls, rect, font, text):
        """Gets elided text so that the text can fit given rectangle.

        Args:
        rect: Rectangle which will contain the text. Type: QtCore.QRect
        font: Font used to render text. Type: QtCore.QFont
        text: String to render
        """
        textLayout = QtGui.QTextLayout(text, font)
        metrics = QtGui.QFontMetrics(font)
        textLayout.beginLayout()
        line = textLayout.createLine()
        totalWidth = 0
        totalHeight = 0
        while line.isValid():
            line.setLineWidth(rect.width())
            rectCovered = line.naturalTextRect()
            totalWidth += rectCovered.width()
            if totalHeight + rectCovered.width() > rect.height():
                break
            else:
                totalHeight += rectCovered.height()

            line = textLayout.createLine()
        textLayout.endLayout()

        # XXX are we calculating the width correctly?
        return metrics.elidedText(text, QtCore.Qt.ElideRight, totalWidth + rect.width())
    #return metrics.elidedText(text, QtCore.Qt.ElideRight, totalWidth)


class TimerWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, service, keybinder):
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
        self._task_bar = TaskbarList().taskbar
        self._timer_tray = None
        if QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            self._timer_tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(":/icon_pomito"),
                                                         parent=self)
            self._current_task = None

        # Setup user interface from designer
        self.setupUi(self)
        self.initialize()

    def initialize(self):
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
            return

        def toggle_interrupt():
            self.btn_interrupt_clicked(checked=self.btn_interrupt.isChecked,
                                       keyboard_context=True)
            return
        wid = None
        if sys.platform.startswith("win"):
            wid = TaskbarList.getptr(self.winId())

        self.keybinder.register_hotkey(wid, "Alt+Ctrl+P", toggle_timer)
        self.keybinder.register_hotkey(wid, "Alt+Ctrl+I", toggle_interrupt)

        if self._timer_tray is not None:
            self._timer_tray.show()
            # TODO Find a way to bring timerwindow into focus when user clicks
            # on system tray notification
            # self._timer_tray.messageClicked.connect(lambda: self.raise_() and self.setFocus())

    def reset_timer(self, reset_session):
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
            if self._timer_tray is not None:
                self._timer_tray.hide()
                return
        if self._timer_tray is not None:
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
        if not text is None:
            label = text

        label = QtUtilities.getElidedText(self.activity_label.rect(), self.activity_label.font(), label)
        self.activity_label.setText(label)
        return

    @QtCore.Slot(str, bool, bool)
    def interrupt_selected(self, reason, is_external, add_unplanned_task):
        # Uncheck state if user opened interrupt window but closed it
        if reason is None or reason is "":
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
        if not self._task_bar is None:
            hwnd = TaskbarList.getptr(self.winId())
            if not self.btn_interrupt.isChecked():
                self._task_bar.SetProgressValue(hwnd, time_elapsed,
                                                self._session_duration)
                self._task_bar.SetProgressState(hwnd, TaskbarList.TBPF_NORMAL)
            else:
                self._task_bar.SetProgressState(hwnd, TaskbarList.TBPF_INDETERMINATE)
                return

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
        if kwargs["reason"] == "complete":
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
        if self._task_bar is not None:
            hwnd = TaskbarList.getptr(self.winId())
            self._task_bar.SetProgressState(hwnd, TaskbarList.TBPF_NOPROGRESS)

    def _notify_session_start(self):
        header = "Pomodoro started!"
        msg = "Stay focused..."
        if self._task_bar is not None:
            self._task_bar.SetProgressValue(TaskbarList.getptr(self.winId()),
                                            0, self._session_duration)
        if self._timer_tray is not None:
            info_icon = QtWidgets.QSystemTrayIcon.Information
            self._timer_tray.showMessage(header, msg, info_icon, 500)
        elif not sys.platform.startswith("win"):
            self._notify(header, msg)

    def _notify_session_stop(self, reason):
        header = "Pomodoro ended!"
        msg = "{0} Sessions completed: {1}".format(reason, self._session_count)
        if self._task_bar is not None:
            hwnd = TaskbarList.getptr(self.winId())
            self._task_bar.SetProgressState(hwnd, TaskbarList.TBPF_PAUSED)

        if self._timer_tray is not None:
            info_icon = QtWidgets.QSystemTrayIcon.Information
            self._timer_tray.showMessage(header, msg, info_icon, 500)
        elif not sys.platform.startswith("win"):
            self._notify(header, msg)

    def _notify(self, header, msg):
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
        notify = QtDBus.QDBusInterface(item, path, interface, bus)
        if notify.isValid():
            x = notify.call(QtDBus.QDBus.AutoDetect, "Notify", app_name,
                            id_replace, icon, title, text,
                            actions_list, hint, time)
            if x.errorName():
                logger.debug("Failed to send notification!")
                logger.debug(x.errorMessage())
        else:
            logger.debug("Invalid dbus interface")


class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, keybinder):
        self.keybinder = keybinder
        super().__init__()

    def nativeEventFilter(self, eventType, message):
        self.keybinder.handler(eventType, message)
        return False, 0


class TaskWindow(QtWidgets.QWidget, Ui_TaskWindow):
    task_selected = QtCore.Signal(Task)
    pending_session_start = False

    def __init__(self, service):
        QtWidgets.QWidget.__init__(self)
        self._service = service

        # Set up user interface from designer
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        # Hide disabled features
        self.btn_owa.hide()
        self.btn_rtm.hide()
        self.btn_trello.hide()
        self.btn_text.hide()

        # Set data model
        self._taskmodel = TaskWindow.TaskModel()
        item = TaskWindow.TaskItemDelegate()

        self.list_task.setModel(self._taskmodel)
        self.list_task.setItemDelegate(item)

        self.setWindowFlags(QtCore.Qt.Popup)
        self.addAction(self.act_hide_window)
        self.addAction(self.act_focus_txt)
        self.list_task.addAction(self.act_select_task)

        # Setup signal handlers for UI elements
        self.txt_filter.textChanged.connect(lambda:
                                            self._apply_task_filter(self.txt_filter.text()))
        self.list_task.doubleClicked.connect(self.list_task_selected)
        self.act_focus_txt.triggered.connect(lambda: self.txt_filter.setFocus())
        self.act_hide_window.triggered.connect(lambda:
                                               self.list_task_selected(None))
        self.act_select_task.triggered.connect(lambda:
                                               self.list_task_selected(self.list_task.currentIndex()))

        self._apply_task_filter("")
        return

    def get_task(self):
        tasks = list(self._service.get_tasks())
        self._taskmodel.updateTasks(tasks)
        self._apply_task_filter("")
        if len(tasks) > 0:
            self.show()
        else:
            logger.debug("Task plugin didn't find any tasks to show.")
            self.list_task_selected(None)
        return

    def _apply_task_filter(self, text):
        #self.list_task.clearContents()
        #self.list_task.setRowCount(0)
        #self.list_task.setSortingEnabled(False)

        #for t in self._tasks.values():
        #if text == u"" or t.description.lower().find(text.lower()) >= 0:
        #self.list_task.insertRow(0)
        #self.list_task.setItem(0, 0,
        #QtWidgets.QTableWidgetItem(unicode(t.estimate)))
        #self.list_task.setItem(0, 1,
        #QtWidgets.QTableWidgetItem(unicode(t.actual)))
        ## Reuse statusTip to store the uid, need to map the uid into
        ## Task object later!
        #_item = QtWidgets.QTableWidgetItem(t.description)
        #_item.setStatusTip(unicode(t.uid))
        #self.list_task.setItem(0, 2, _item)
        #self.list_task.setSortingEnabled(True)
        return

    ###
    # Widget function overrides
    ###
    def closeEvent(self, event):
        event.accept()

    ###
    # UI signal handler slots
    ###
    def list_task_selected(self, index):
        self.hide()
        if index is not None:
            self.task_selected.emit(self._taskmodel.data(index, QtCore.Qt.DisplayRole))
        else:
            from pomito.task import get_null_task
            self.task_selected.emit(get_null_task())

    ###
    # Task UI helpers
    ###
    class TaskModel(QtCore.QAbstractListModel):
        def __init__(self):
            QtCore.QAbstractListModel.__init__(self)
            return

        def rowCount(self, index):
            return len(self._tasks)

        def data(self, index, role):
            if index.isValid() and role == QtCore.Qt.DisplayRole:
                return self._tasks[index.row()]

        def updateTasks(self, tasks):
            self._tasks = tasks
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self._tasks), 0))
            return


    class TaskItemDelegate(QtWidgets.QStyledItemDelegate):
        def __init__(self):
            QtWidgets.QStyledItemDelegate.__init__(self)
            return

        def paint(self, painter, option, index):
            self.initStyleOption(option, index)

            data = index.data()

            style = option.widget.style()
            hor_padding = option.rect.width() * 0.02
            ver_padding = option.rect.height() * 0.02
            inner_rect = option.rect.adjusted(hor_padding, ver_padding, -hor_padding, -ver_padding)
            lineHeight = option.fontMetrics.lineSpacing()

            painter.save()
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight());
                style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)

            # first item: draw task description
            text_space = inner_rect.adjusted(0, 0, 0, -option.rect.height() * 0.33)
            elidedText = QtUtilities.getElidedText(text_space,
                                                   painter.font(),
                                                   data.description)
            painter.drawText(text_space,
                             option.displayAlignment | QtCore.Qt.TextWordWrap,
                             elidedText)

            # second item: draw priority and other meta information
            text_space = inner_rect.adjusted(0, text_space.height() + ver_padding, 0, 0)
            meta_text = QtUtilities.getElidedText(text_space,
                                                  painter.font(),
                                                  "Estimate: {0}, Actual: {1}, Tags: {2}".format(data.estimate, data.actual, data.tags))
            painter.drawText(text_space,
                             option.displayAlignment | QtCore.Qt.TextWordWrap,
                             meta_text)

            # last item: draw border
            dotted_pen = QtGui.QPen(QtCore.Qt.DotLine)
            painter.setPen(dotted_pen)
            painter.drawLine(inner_rect.x(),
                             inner_rect.y() + inner_rect.height(),
                             inner_rect.x() + inner_rect.width(),
                             inner_rect.y() + inner_rect.height())

            painter.restore()
            return

        def sizeHint(self, option, index):
            size = QtCore.QSize(option.rect.width(), option.fontMetrics.lineSpacing() * 5)
            return size


class InterruptWindow(QtWidgets.QWidget, Ui_InterruptionWindow):
    interrupt_selected = QtCore.Signal(str, bool, bool)

    def __init__(self, service):
        QtWidgets.QWidget.__init__(self)
        self._service = service

        # Set up user interface from designer
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        # Setup signal handlers for UI elements
        self.btn_start_interrupt.clicked.connect(self.btn_start_interrupt_clicked)
        self.act_hide_window.triggered.connect(lambda: self.hide())

        # Setup signal handlers for pomodoro service
        #self._apply_task_filter(u"")
        return

    def get_interruption(self):
        self.show()
        return

    ###
    # Widget function overrides
    ###
    def showEvent(self, event):
        event.accept()
        self.txt_description.selectAll()
        self.txt_description.setFocus()

    def closeEvent(self, event):
        event.accept()
        self.interrupt_selected.emit(None, False, False)

    ###
    # UI signal handler slots
    ###
    def btn_start_interrupt_clicked(self):
        self.hide()
        # TODO add support for creation of unplanned task
        self.interrupt_selected.emit(self.txt_description.toPlainText(),
                                     self.chk_external.isChecked(),
                                     False)
