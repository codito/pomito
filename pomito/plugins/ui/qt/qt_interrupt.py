# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/qt/interrupt.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_InterruptionWindow(object):
    def setupUi(self, InterruptionWindow):
        InterruptionWindow.setObjectName("InterruptionWindow")
        InterruptionWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        InterruptionWindow.resize(420, 145)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon_pomito"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        InterruptionWindow.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(InterruptionWindow)
        self.gridLayout.setObjectName("gridLayout")
        self.txt_description = QtWidgets.QPlainTextEdit(InterruptionWindow)
        self.txt_description.setTabChangesFocus(False)
        self.txt_description.setObjectName("txt_description")
        self.gridLayout.addWidget(self.txt_description, 0, 0, 1, 2)
        self.chk_external = QtWidgets.QCheckBox(InterruptionWindow)
        self.chk_external.setObjectName("chk_external")
        self.gridLayout.addWidget(self.chk_external, 3, 0, 1, 1)
        self.btn_start_interrupt = QtWidgets.QPushButton(InterruptionWindow)
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        self.btn_start_interrupt.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon_interrupt"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_start_interrupt.setIcon(icon1)
        self.btn_start_interrupt.setDefault(True)
        self.btn_start_interrupt.setFlat(True)
        self.btn_start_interrupt.setObjectName("btn_start_interrupt")
        self.gridLayout.addWidget(self.btn_start_interrupt, 3, 1, 1, 1)
        self.act_hide_window = QtWidgets.QAction(InterruptionWindow)
        self.act_hide_window.setObjectName("act_hide_window")

        self.retranslateUi(InterruptionWindow)
        QtCore.QMetaObject.connectSlotsByName(InterruptionWindow)

    def retranslateUi(self, InterruptionWindow):
        _translate = QtCore.QCoreApplication.translate
        InterruptionWindow.setWindowTitle(_translate("InterruptionWindow", "Pomito - Interruption"))
        self.txt_description.setPlainText(_translate("InterruptionWindow", "Describe the interruption briefly"))
        self.chk_external.setText(_translate("InterruptionWindow", "&External interruption"))
        self.btn_start_interrupt.setText(_translate("InterruptionWindow", "&Start Interruption"))
        self.act_hide_window.setText(_translate("InterruptionWindow", "hide"))
        self.act_hide_window.setShortcut(_translate("InterruptionWindow", "Esc"))

from . import pomito_rc
