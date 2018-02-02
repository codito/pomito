# -*- coding: utf-8 -*-
"""Utilities for Qt integration."""

from PyQt5 import QtCore, QtGui, QtWidgets


def get_elided_text(rect, font, text):
    """Get elided text to fit given rectangle.

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


class WorkerCompletedEvent(QtCore.QEvent):
    """Event raised on completion of worker thread."""

    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, func, *args, **kwargs):
        """Create an instance of WorkerCompletedEvent.

        Args:
            func: callback function
            args: arguments for the callback
            kwargs: keyword args for the callback
        """
        super(WorkerCompletedEvent, self).__init__(self.EVENT_TYPE)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def callback(self):
        """Invoke callback with args and kwargs."""
        self.func(*self.args, **self.kwargs)

    @classmethod
    def post_to(cls, receiver, func, *args, **kwargs):
        """Post a callable to be delivered to a specific receiver as a CallbackEvent.

        Creates the event instance and uses Qt event loop to post it.
        Args:
            receiver: target thread to receive the event
            func: callback
            args: callback arguments
            kwargs: callback keyword arguments
        """
        event = cls(func, *args, **kwargs)

        # post the event to the given receiver
        QtWidgets.QApplication.postEvent(receiver, event)


class Worker(QtCore.QThread):
    """A worker thread to offload long running tasks.

    Raises WorkerCompletedEvent on completion of task. Event is posted on
    Qt event loop.
    """

    def __init__(self, parent, on_complete, func, *args, **kwargs):
        """Create an instance of the worker thread.

        Args:
            parent: owning widget/thread
            on_complete: callback on completion of task
            func: task method
            args: arguments for the task
            kwargs: keyword arguments for the task
        """
        super(Worker, self).__init__(parent)
        self._parent = parent
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._on_complete = on_complete

    def run(self):
        """Run the worker thread."""
        try:
            result = self._func(*self._args, **self._kwargs)
        except Exception as e:
            result = e
        finally:
            WorkerCompletedEvent.post_to(self.parent(), self._on_complete, result)
