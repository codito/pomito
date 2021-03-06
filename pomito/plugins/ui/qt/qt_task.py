# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/qt/task.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TaskWindow(object):
    def setupUi(self, TaskWindow):
        TaskWindow.setObjectName("TaskWindow")
        TaskWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        TaskWindow.resize(420, 400)
        TaskWindow.setMaximumSize(QtCore.QSize(600, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon_pomito"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TaskWindow.setWindowIcon(icon)
        self.gridLayout_2 = QtWidgets.QGridLayout(TaskWindow)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.list_task = QtWidgets.QListView(TaskWindow)
        self.list_task.setObjectName("list_task")
        self.gridLayout.addWidget(self.list_task, 2, 0, 1, 5)
        self.txt_filter = QtWidgets.QLineEdit(TaskWindow)
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        self.txt_filter.setFont(font)
        self.txt_filter.setStatusTip("")
        self.txt_filter.setAutoFillBackground(False)
        self.txt_filter.setStyleSheet("")
        self.txt_filter.setInputMask("")
        self.txt_filter.setText("")
        self.txt_filter.setFrame(True)
        self.txt_filter.setObjectName("txt_filter")
        self.gridLayout.addWidget(self.txt_filter, 1, 0, 1, 5)
        self.btn_rtm = QtWidgets.QPushButton(TaskWindow)
        self.btn_rtm.setEnabled(False)
        self.btn_rtm.setMinimumSize(QtCore.QSize(16, 16))
        self.btn_rtm.setMaximumSize(QtCore.QSize(16, 16))
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        self.btn_rtm.setFont(font)
        self.btn_rtm.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon_rtm"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_rtm.setIcon(icon1)
        self.btn_rtm.setFlat(True)
        self.btn_rtm.setObjectName("btn_rtm")
        self.gridLayout.addWidget(self.btn_rtm, 3, 0, 1, 1)
        self.btn_trello = QtWidgets.QPushButton(TaskWindow)
        self.btn_trello.setEnabled(False)
        self.btn_trello.setMinimumSize(QtCore.QSize(16, 16))
        self.btn_trello.setMaximumSize(QtCore.QSize(16, 16))
        self.btn_trello.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon_trello"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_trello.setIcon(icon2)
        self.btn_trello.setFlat(True)
        self.btn_trello.setObjectName("btn_trello")
        self.gridLayout.addWidget(self.btn_trello, 3, 2, 1, 1)
        self.btn_owa = QtWidgets.QPushButton(TaskWindow)
        self.btn_owa.setEnabled(False)
        self.btn_owa.setMinimumSize(QtCore.QSize(16, 16))
        self.btn_owa.setMaximumSize(QtCore.QSize(16, 16))
        self.btn_owa.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon_owa"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_owa.setIcon(icon3)
        self.btn_owa.setFlat(True)
        self.btn_owa.setObjectName("btn_owa")
        self.gridLayout.addWidget(self.btn_owa, 3, 1, 1, 1)
        self.btn_text = QtWidgets.QPushButton(TaskWindow)
        self.btn_text.setEnabled(False)
        self.btn_text.setMinimumSize(QtCore.QSize(16, 16))
        self.btn_text.setMaximumSize(QtCore.QSize(16, 16))
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        self.btn_text.setFont(font)
        self.btn_text.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icon_text"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_text.setIcon(icon4)
        self.btn_text.setFlat(True)
        self.btn_text.setObjectName("btn_text")
        self.gridLayout.addWidget(self.btn_text, 3, 3, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.act_hide_window = QtWidgets.QAction(TaskWindow)
        self.act_hide_window.setObjectName("act_hide_window")
        self.act_focus_txt = QtWidgets.QAction(TaskWindow)
        self.act_focus_txt.setObjectName("act_focus_txt")
        self.act_select_task = QtWidgets.QAction(TaskWindow)
        self.act_select_task.setShortcutContext(QtCore.Qt.WidgetShortcut)
        self.act_select_task.setObjectName("act_select_task")

        self.retranslateUi(TaskWindow)
        QtCore.QMetaObject.connectSlotsByName(TaskWindow)

    def retranslateUi(self, TaskWindow):
        _translate = QtCore.QCoreApplication.translate
        TaskWindow.setWindowTitle(_translate("TaskWindow", "Pomito - Tasks"))
        self.txt_filter.setPlaceholderText(_translate("TaskWindow", "Filter task (Ctrl+L). Double click task below to select. Esc exits."))
        self.act_hide_window.setText(_translate("TaskWindow", "hide"))
        self.act_hide_window.setShortcut(_translate("TaskWindow", "Esc"))
        self.act_focus_txt.setText(_translate("TaskWindow", "focus_txt"))
        self.act_focus_txt.setShortcut(_translate("TaskWindow", "Ctrl+L"))
        self.act_select_task.setText(_translate("TaskWindow", "act_select_task"))
        self.act_select_task.setToolTip(_translate("TaskWindow", "select_task"))
        self.act_select_task.setShortcut(_translate("TaskWindow", "Return"))

from . import pomito_rc
