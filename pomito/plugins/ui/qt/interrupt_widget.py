# -*- coding: utf-8 -*-
"""Interruption widget."""

from PyQt5 import QtCore, QtWidgets

from pomito.plugins.ui.qt.qt_interrupt import Ui_InterruptionWindow


class InterruptWindow(QtWidgets.QWidget, Ui_InterruptionWindow):
    """Interruption window."""

    interrupt_selected = QtCore.Signal(str, bool, bool)

    def __init__(self, service):
        """Create an instance of the interruption window.

        Args:
            service     pomodoro service instance.
        """
        QtWidgets.QWidget.__init__(self)
        self._service = service

        # Set up user interface from designer
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        """Initialize the interruption window."""
        # Setup signal handlers for UI elements
        self.btn_start_interrupt.clicked.connect(self.btn_start_interrupt_clicked)
        self.act_hide_window.triggered.connect(lambda: self.hide())

    def get_interruption(self):
        """Get the interruption reason."""
        self.show()

    ###
    # Widget function overrides
    ###
    def showEvent(self, event):
        """Event handler for show event.

        Selects the watermark text by default.
        """
        event.accept()
        self.txt_description.selectAll()
        self.txt_description.setFocus()

    def closeEvent(self, event):
        """Event handler for the close event.

        Signals interrupt event.
        """
        event.accept()
        self.interrupt_selected.emit(None, False, False)

    ###
    # UI signal handler slots
    ###
    def btn_start_interrupt_clicked(self):
        """Event handler for interrupt button click.

        Signals interrupt selected event with reason.
        """
        self.hide()
        # TODO add support for creation of unplanned task
        self.interrupt_selected.emit(self.txt_description.toPlainText(),
                                     self.chk_external.isChecked(),
                                     False)
