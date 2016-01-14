# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/qt/timer.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 140)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(600, 140))
        MainWindow.setMaximumSize(QtCore.QSize(600, 140))
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        MainWindow.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon_pomito"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(11, 11, 571, 121))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_timer = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_timer.sizePolicy().hasHeightForWidth())
        self.btn_timer.setSizePolicy(sizePolicy)
        self.btn_timer.setMinimumSize(QtCore.QSize(24, 24))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icon_start_timer"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/icon_start_timer"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/icon_stop_timer"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.btn_timer.setIcon(icon1)
        self.btn_timer.setCheckable(True)
        self.btn_timer.setAutoDefault(True)
        self.btn_timer.setDefault(True)
        self.btn_timer.setFlat(True)
        self.btn_timer.setObjectName("btn_timer")
        self.horizontalLayout.addWidget(self.btn_timer)
        self.btn_interrupt = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_interrupt.sizePolicy().hasHeightForWidth())
        self.btn_interrupt.setSizePolicy(sizePolicy)
        self.btn_interrupt.setMinimumSize(QtCore.QSize(24, 24))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon_interrupt"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_interrupt.setIcon(icon2)
        self.btn_interrupt.setCheckable(True)
        self.btn_interrupt.setFlat(True)
        self.btn_interrupt.setObjectName("btn_interrupt")
        self.horizontalLayout.addWidget(self.btn_interrupt)
        self.btn_stats = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_stats.sizePolicy().hasHeightForWidth())
        self.btn_stats.setSizePolicy(sizePolicy)
        self.btn_stats.setMinimumSize(QtCore.QSize(24, 24))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon_stats"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_stats.setIcon(icon3)
        self.btn_stats.setAutoDefault(False)
        self.btn_stats.setFlat(True)
        self.btn_stats.setObjectName("btn_stats")
        self.horizontalLayout.addWidget(self.btn_stats)
        self.btn_options = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_options.sizePolicy().hasHeightForWidth())
        self.btn_options.setSizePolicy(sizePolicy)
        self.btn_options.setMinimumSize(QtCore.QSize(24, 24))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icon_options"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_options.setIcon(icon4)
        self.btn_options.setFlat(True)
        self.btn_options.setObjectName("btn_options")
        self.horizontalLayout.addWidget(self.btn_options)
        self.btn_task = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_task.sizePolicy().hasHeightForWidth())
        self.btn_task.setSizePolicy(sizePolicy)
        self.btn_task.setMinimumSize(QtCore.QSize(24, 24))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icon_task_list"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_task.setIcon(icon5)
        self.btn_task.setFlat(True)
        self.btn_task.setObjectName("btn_task")
        self.horizontalLayout.addWidget(self.btn_task)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 3)
        self.line = QtWidgets.QFrame(self.layoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 0, 1, 3)
        self.timer_lcd = QtWidgets.QLCDNumber(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timer_lcd.sizePolicy().hasHeightForWidth())
        self.timer_lcd.setSizePolicy(sizePolicy)
        self.timer_lcd.setMinimumSize(QtCore.QSize(64, 32))
        self.timer_lcd.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.timer_lcd.setFrameShadow(QtWidgets.QFrame.Plain)
        self.timer_lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.timer_lcd.setProperty("value", 11005.0)
        self.timer_lcd.setProperty("intValue", 11005)
        self.timer_lcd.setObjectName("timer_lcd")
        self.gridLayout.addWidget(self.timer_lcd, 1, 0, 1, 2)
        self.activity_label = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.activity_label.sizePolicy().hasHeightForWidth())
        self.activity_label.setSizePolicy(sizePolicy)
        self.activity_label.setMinimumSize(QtCore.QSize(318, 0))
        self.activity_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.activity_label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.activity_label.setLineWidth(1)
        self.activity_label.setTextFormat(QtCore.Qt.PlainText)
        self.activity_label.setScaledContents(True)
        self.activity_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.activity_label.setWordWrap(True)
        self.activity_label.setIndent(-1)
        self.activity_label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.activity_label.setObjectName("activity_label")
        self.gridLayout.addWidget(self.activity_label, 1, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Pomito"))
        self.btn_timer.setToolTip(_translate("MainWindow", "Start/Stop timer"))
        self.btn_timer.setText(_translate("MainWindow", "&Timer"))
        self.btn_interrupt.setToolTip(_translate("MainWindow", "Start tracking an interruption (stops ongoing pomodoro session)"))
        self.btn_interrupt.setText(_translate("MainWindow", "&Interrupt"))
        self.btn_stats.setText(_translate("MainWindow", "&Stats"))
        self.btn_options.setText(_translate("MainWindow", "&Options"))
        self.btn_task.setText(_translate("MainWindow", "T&asks"))
        self.activity_label.setText(_translate("MainWindow", "A long long and more long, still longer task andmore and more and more and still more, a bit more"))

from . import pomito_rc
