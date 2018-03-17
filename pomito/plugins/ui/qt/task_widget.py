# -*- coding: utf-8 -*-
"""Task widget for pomito."""

import logging
from PyQt5 import QtCore, QtGui, QtWidgets

from pomito.plugins.ui.qt.qt_task import Ui_TaskWindow
from pomito.plugins.ui.qt.utils import get_elided_text, Worker, WorkerCompletedEvent
from pomito.task import Task

logger = logging.getLogger("pomito.plugins.ui.qtapp.task")
QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot


class TaskWindow(QtWidgets.QWidget, Ui_TaskWindow):
    """Task widget."""

    task_selected = QtCore.Signal(Task)
    pending_session_start = False

    def __init__(self, service):
        """Create an instance of Task Widget.

        Args:
            service: pomodoro service instance.
        """
        QtWidgets.QWidget.__init__(self)
        self._service = service

        # Set up user interface from designer
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        """Initialize the task widget."""
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

    def customEvent(self, event):
        """Override for custom events."""
        if isinstance(event, WorkerCompletedEvent):
            event.callback()

    def get_task(self):
        """Get tasks for plugin."""
        def func():
            try:
                return list(self._service.get_tasks())
            except Exception as e:
                logger.debug("Error: {0}".format(e))
                return []

        def on_complete(result):
            if isinstance(result, list):
                logger.debug("Got {0} tasks".format(len(result)))
                self._taskmodel.updateTasks(result)
                self._apply_task_filter("")
            else:
                logger.debug("Error in worker thread: {0}".format(result))

        t = Worker(self, on_complete, func)
        t.start()
        self.show()

    def _apply_task_filter(self, text):
        # self.list_task.clearContents()
        # self.list_task.setRowCount(0)
        # self.list_task.setSortingEnabled(False)

        # for t in self._tasks.values():
        # if text == u"" or t.description.lower().find(text.lower()) >= 0:
        # self.list_task.insertRow(0)
        # self.list_task.setItem(0, 0,
        # QtWidgets.QTableWidgetItem(unicode(t.estimate)))
        # self.list_task.setItem(0, 1,
        # QtWidgets.QTableWidgetItem(unicode(t.actual)))
        # # Reuse statusTip to store the uid, need to map the uid into
        # # Task object later!
        # _item = QtWidgets.QTableWidgetItem(t.description)
        # _item.setStatusTip(unicode(t.uid))
        # self.list_task.setItem(0, 2, _item)
        # self.list_task.setSortingEnabled(True)
        return

    ###
    # Widget function overrides
    ###
    def closeEvent(self, event):
        """Close the window."""
        event.accept()

    ###
    # UI signal handler slots
    ###
    def list_task_selected(self, index):
        """Task selection handler.

        Raises `task_selected` event for the parent window.
        """
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
        """Model for the task entity."""

        def __init__(self):
            """Create a task model instance."""
            self._tasks = []
            QtCore.QAbstractListModel.__init__(self)
            return

        def rowCount(self, index):
            """Get number of rows in the model."""
            return len(self._tasks)

        def data(self, index, role):
            """Get the data for a row."""
            if index.isValid() and role == QtCore.Qt.DisplayRole:
                return self._tasks[index.row()]

        def updateTasks(self, tasks):
            """Update the tasks from plugin."""
            self._tasks = tasks
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self._tasks), 0))
            return

    class TaskItemDelegate(QtWidgets.QStyledItemDelegate):
        """Delegate for visual representation of each task."""

        def __init__(self):
            """Create a styled delegate for tasks."""
            QtWidgets.QStyledItemDelegate.__init__(self)
            return

        def paint(self, painter, option, index):
            """Paint the task row for visual representation."""
            self.initStyleOption(option, index)

            data = index.data()

            style = option.widget.style()
            hor_padding = option.rect.width() * 0.02
            ver_padding = option.rect.height() * 0.02
            inner_rect = option.rect.adjusted(hor_padding, ver_padding, -hor_padding, -ver_padding)
            # lineHeight = option.fontMetrics.lineSpacing()

            painter.save()
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
                style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)

            # first item: draw task description
            text_space = inner_rect.adjusted(0, 0, 0, -option.rect.height() * 0.33)
            elidedText = get_elided_text(text_space,
                                         painter.font(),
                                         data.description)
            painter.drawText(text_space,
                             option.displayAlignment | QtCore.Qt.TextWordWrap,
                             elidedText)

            # second item: draw priority and other meta information
            text_space = inner_rect.adjusted(0, text_space.height() + ver_padding, 0, 0)
            text_msg = "Estimate: {0}, Actual: {1}, Tags: {2}".format(data.estimate,
                                                                      data.actual,
                                                                      data.tags)
            meta_text = get_elided_text(text_space, painter.font(), text_msg)
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
            """Hint size of each row."""
            size = QtCore.QSize(option.rect.width(), option.fontMetrics.lineSpacing() * 5)
            return size
