# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\gui\MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(462, 371)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btnSearchSerialPort = QtWidgets.QPushButton(self.centralwidget)
        self.btnSearchSerialPort.setGeometry(QtCore.QRect(170, 10, 81, 31))
        self.btnSearchSerialPort.setObjectName("btnSearchSerialPort")
        self.comboPort = QtWidgets.QComboBox(self.centralwidget)
        self.comboPort.setGeometry(QtCore.QRect(20, 10, 111, 31))
        self.comboPort.setObjectName("comboPort")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(260, 0, 191, 321))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl_test_1 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_1.setObjectName("lbl_test_1")
        self.verticalLayout.addWidget(self.lbl_test_1)
        self.lbl_test_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_2.setObjectName("lbl_test_2")
        self.verticalLayout.addWidget(self.lbl_test_2)
        self.lbl_test_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_3.setObjectName("lbl_test_3")
        self.verticalLayout.addWidget(self.lbl_test_3)
        self.lbl_test_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_4.setObjectName("lbl_test_4")
        self.verticalLayout.addWidget(self.lbl_test_4)
        self.lbl_test_5 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_5.setObjectName("lbl_test_5")
        self.verticalLayout.addWidget(self.lbl_test_5)
        self.lbl_test_6 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_6.setObjectName("lbl_test_6")
        self.verticalLayout.addWidget(self.lbl_test_6)
        self.lbl_test_7 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_7.setObjectName("lbl_test_7")
        self.verticalLayout.addWidget(self.lbl_test_7)
        self.lbl_test_8 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_8.setObjectName("lbl_test_8")
        self.verticalLayout.addWidget(self.lbl_test_8)
        self.lbl_test_9 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_9.setObjectName("lbl_test_9")
        self.verticalLayout.addWidget(self.lbl_test_9)
        self.lbl_test_10 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_10.setObjectName("lbl_test_10")
        self.verticalLayout.addWidget(self.lbl_test_10)
        self.lbl_test_11 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_11.setObjectName("lbl_test_11")
        self.verticalLayout.addWidget(self.lbl_test_11)
        self.lbl_test_12 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_12.setObjectName("lbl_test_12")
        self.verticalLayout.addWidget(self.lbl_test_12)
        self.lbl_test_13 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lbl_test_13.setObjectName("lbl_test_13")
        self.verticalLayout.addWidget(self.lbl_test_13)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(20, 50, 231, 271))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.btnTestComm = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.btnTestComm.setObjectName("btnTestComm")
        self.verticalLayout_2.addWidget(self.btnTestComm)
        self.btnStartComm = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.btnStartComm.setObjectName("btnStartComm")
        self.verticalLayout_2.addWidget(self.btnStartComm)
        self.btnStopComm = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.btnStopComm.setObjectName("btnStopComm")
        self.verticalLayout_2.addWidget(self.btnStopComm)
        self.btn_program_main = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.btn_program_main.setObjectName("btn_program_main")
        self.verticalLayout_2.addWidget(self.btn_program_main)
        self.btn_program_main_def = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.btn_program_main_def.setObjectName("btn_program_main_def")
        self.verticalLayout_2.addWidget(self.btn_program_main_def)
        self.btn_wr_idt = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.btn_wr_idt.setObjectName("btn_wr_idt")
        self.verticalLayout_2.addWidget(self.btn_wr_idt)
        self.btn_wr_cli = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.btn_wr_cli.setObjectName("btn_wr_cli")
        self.verticalLayout_2.addWidget(self.btn_wr_cli)
        self.btn_wr_hw = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.btn_wr_hw.setObjectName("btn_wr_hw")
        self.verticalLayout_2.addWidget(self.btn_wr_hw)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 462, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Collaudo Leonardo L24"))
        self.btnSearchSerialPort.setText(_translate("MainWindow", "Search Port"))
        self.lbl_test_1.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_2.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_3.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_4.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_5.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_6.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_7.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_8.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_9.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_10.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_11.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_12.setText(_translate("MainWindow", "TextLabel"))
        self.lbl_test_13.setText(_translate("MainWindow", "TextLabel"))
        self.btnTestComm.setText(_translate("MainWindow", "Test Comm"))
        self.btnStartComm.setText(_translate("MainWindow", "Start Comm"))
        self.btnStopComm.setText(_translate("MainWindow", "Stop Comm"))
        self.btn_program_main.setText(_translate("MainWindow", "Program Main Collaudo"))
        self.btn_program_main_def.setText(_translate("MainWindow", "Program Main Produzione"))
        self.btn_wr_idt.setText(_translate("MainWindow", "Program IDT"))
        self.btn_wr_cli.setText(_translate("MainWindow", "Program CLI"))
        self.btn_wr_hw.setText(_translate("MainWindow", "Program HW"))
