# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1221, 504)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.groupBox_TelescopeStatus = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_TelescopeStatus.setGeometry(QtCore.QRect(0, 0, 401, 291))
        self.groupBox_TelescopeStatus.setObjectName("groupBox_TelescopeStatus")
        self.groupBox_tracking = QtWidgets.QGroupBox(self.groupBox_TelescopeStatus)
        self.groupBox_tracking.setGeometry(QtCore.QRect(210, 60, 181, 221))
        self.groupBox_tracking.setObjectName("groupBox_tracking")
        self.gridLayout_tracking = QtWidgets.QGridLayout(self.groupBox_tracking)
        self.gridLayout_tracking.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_tracking.setSpacing(6)
        self.gridLayout_tracking.setObjectName("gridLayout_tracking")
        self.lineEdit_Elevation = QtWidgets.QLineEdit(self.groupBox_tracking)
        self.lineEdit_Elevation.setReadOnly(True)
        self.lineEdit_Elevation.setObjectName("lineEdit_Elevation")
        self.gridLayout_tracking.addWidget(self.lineEdit_Elevation, 1, 1, 1, 1)
        self.lineEdit_ElError = QtWidgets.QLineEdit(self.groupBox_tracking)
        self.lineEdit_ElError.setReadOnly(True)
        self.lineEdit_ElError.setObjectName("lineEdit_ElError")
        self.gridLayout_tracking.addWidget(self.lineEdit_ElError, 5, 1, 1, 1)
        self.label_ElError = QtWidgets.QLabel(self.groupBox_tracking)
        self.label_ElError.setObjectName("label_ElError")
        self.gridLayout_tracking.addWidget(self.label_ElError, 5, 0, 1, 1)
        self.label_AzOffset = QtWidgets.QLabel(self.groupBox_tracking)
        self.label_AzOffset.setObjectName("label_AzOffset")
        self.gridLayout_tracking.addWidget(self.label_AzOffset, 2, 0, 1, 1)
        self.lineEdit_AzError = QtWidgets.QLineEdit(self.groupBox_tracking)
        self.lineEdit_AzError.setReadOnly(True)
        self.lineEdit_AzError.setObjectName("lineEdit_AzError")
        self.gridLayout_tracking.addWidget(self.lineEdit_AzError, 4, 1, 1, 1)
        self.lineEdit_ElOffset = QtWidgets.QLineEdit(self.groupBox_tracking)
        self.lineEdit_ElOffset.setReadOnly(True)
        self.lineEdit_ElOffset.setObjectName("lineEdit_ElOffset")
        self.gridLayout_tracking.addWidget(self.lineEdit_ElOffset, 3, 1, 1, 1)
        self.label_ElOffset = QtWidgets.QLabel(self.groupBox_tracking)
        self.label_ElOffset.setObjectName("label_ElOffset")
        self.gridLayout_tracking.addWidget(self.label_ElOffset, 3, 0, 1, 1)
        self.lineEdit_AzOffset = QtWidgets.QLineEdit(self.groupBox_tracking)
        self.lineEdit_AzOffset.setReadOnly(True)
        self.lineEdit_AzOffset.setObjectName("lineEdit_AzOffset")
        self.gridLayout_tracking.addWidget(self.lineEdit_AzOffset, 2, 1, 1, 1)
        self.lineEdit_Azimuth = QtWidgets.QLineEdit(self.groupBox_tracking)
        self.lineEdit_Azimuth.setReadOnly(True)
        self.lineEdit_Azimuth.setObjectName("lineEdit_Azimuth")
        self.gridLayout_tracking.addWidget(self.lineEdit_Azimuth, 0, 1, 1, 1)
        self.label_AzError = QtWidgets.QLabel(self.groupBox_tracking)
        self.label_AzError.setObjectName("label_AzError")
        self.gridLayout_tracking.addWidget(self.label_AzError, 4, 0, 1, 1)
        self.label_Elevation = QtWidgets.QLabel(self.groupBox_tracking)
        self.label_Elevation.setObjectName("label_Elevation")
        self.gridLayout_tracking.addWidget(self.label_Elevation, 1, 0, 1, 1)
        self.label_Azimuth = QtWidgets.QLabel(self.groupBox_tracking)
        self.label_Azimuth.setObjectName("label_Azimuth")
        self.gridLayout_tracking.addWidget(self.label_Azimuth, 0, 0, 1, 1)
        self.groupBox_GeneralStatus = QtWidgets.QGroupBox(self.groupBox_TelescopeStatus)
        self.groupBox_GeneralStatus.setGeometry(QtCore.QRect(20, 60, 191, 221))
        self.groupBox_GeneralStatus.setObjectName("groupBox_GeneralStatus")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_GeneralStatus)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_Allocation = QtWidgets.QLineEdit(self.groupBox_GeneralStatus)
        self.lineEdit_Allocation.setReadOnly(True)
        self.lineEdit_Allocation.setObjectName("lineEdit_Allocation")
        self.gridLayout.addWidget(self.lineEdit_Allocation, 0, 1, 1, 1)
        self.lineEdit_LO1 = QtWidgets.QLineEdit(self.groupBox_GeneralStatus)
        self.lineEdit_LO1.setReadOnly(True)
        self.lineEdit_LO1.setObjectName("lineEdit_LO1")
        self.gridLayout.addWidget(self.lineEdit_LO1, 3, 1, 1, 1)
        self.label_LO1 = QtWidgets.QLabel(self.groupBox_GeneralStatus)
        self.label_LO1.setObjectName("label_LO1")
        self.gridLayout.addWidget(self.label_LO1, 3, 0, 1, 1)
        self.lineEdit_LO2 = QtWidgets.QLineEdit(self.groupBox_GeneralStatus)
        self.lineEdit_LO2.setReadOnly(True)
        self.lineEdit_LO2.setObjectName("lineEdit_LO2")
        self.gridLayout.addWidget(self.lineEdit_LO2, 4, 1, 1, 1)
        self.label_LO2 = QtWidgets.QLabel(self.groupBox_GeneralStatus)
        self.label_LO2.setObjectName("label_LO2")
        self.gridLayout.addWidget(self.label_LO2, 4, 0, 1, 1)
        self.lineEdit_Receiver = QtWidgets.QLineEdit(self.groupBox_GeneralStatus)
        self.lineEdit_Receiver.setReadOnly(True)
        self.lineEdit_Receiver.setObjectName("lineEdit_Receiver")
        self.gridLayout.addWidget(self.lineEdit_Receiver, 2, 1, 1, 1)
        self.label_Control = QtWidgets.QLabel(self.groupBox_GeneralStatus)
        self.label_Control.setObjectName("label_Control")
        self.gridLayout.addWidget(self.label_Control, 1, 0, 1, 1)
        self.label_Allocation = QtWidgets.QLabel(self.groupBox_GeneralStatus)
        self.label_Allocation.setObjectName("label_Allocation")
        self.gridLayout.addWidget(self.label_Allocation, 0, 0, 1, 1)
        self.label_Receiver = QtWidgets.QLabel(self.groupBox_GeneralStatus)
        self.label_Receiver.setObjectName("label_Receiver")
        self.gridLayout.addWidget(self.label_Receiver, 2, 0, 1, 1)
        self.lineEdit_Control = QtWidgets.QLineEdit(self.groupBox_GeneralStatus)
        self.lineEdit_Control.setReadOnly(True)
        self.lineEdit_Control.setObjectName("lineEdit_Control")
        self.gridLayout.addWidget(self.lineEdit_Control, 1, 1, 1, 1)
        self.label_Coordsys = QtWidgets.QLabel(self.groupBox_GeneralStatus)
        self.label_Coordsys.setObjectName("label_Coordsys")
        self.gridLayout.addWidget(self.label_Coordsys, 5, 0, 1, 1)
        self.lineEdit_Coordsys = QtWidgets.QLineEdit(self.groupBox_GeneralStatus)
        self.lineEdit_Coordsys.setReadOnly(True)
        self.lineEdit_Coordsys.setObjectName("lineEdit_Coordsys")
        self.gridLayout.addWidget(self.lineEdit_Coordsys, 5, 1, 1, 1)
        self.label_Timestamp = QtWidgets.QLabel(self.groupBox_TelescopeStatus)
        self.label_Timestamp.setGeometry(QtCore.QRect(30, 30, 111, 20))
        self.label_Timestamp.setObjectName("label_Timestamp")
        self.lineEdit_Timestamp = QtWidgets.QLineEdit(self.groupBox_TelescopeStatus)
        self.lineEdit_Timestamp.setGeometry(QtCore.QRect(140, 30, 241, 20))
        self.lineEdit_Timestamp.setReadOnly(True)
        self.lineEdit_Timestamp.setObjectName("lineEdit_Timestamp")
        self.groupBox_ObservingStatus = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_ObservingStatus.setGeometry(QtCore.QRect(410, 0, 221, 431))
        self.groupBox_ObservingStatus.setObjectName("groupBox_ObservingStatus")
        self.groupBox_CurrentObservation = QtWidgets.QGroupBox(self.groupBox_ObservingStatus)
        self.groupBox_CurrentObservation.setGeometry(QtCore.QRect(10, 20, 201, 181))
        self.groupBox_CurrentObservation.setObjectName("groupBox_CurrentObservation")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_CurrentObservation)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_Source = QtWidgets.QLabel(self.groupBox_CurrentObservation)
        self.label_Source.setObjectName("label_Source")
        self.gridLayout_2.addWidget(self.label_Source, 0, 0, 1, 1)
        self.lineEdit_Source = QtWidgets.QLineEdit(self.groupBox_CurrentObservation)
        self.lineEdit_Source.setReadOnly(True)
        self.lineEdit_Source.setObjectName("lineEdit_Source")
        self.gridLayout_2.addWidget(self.lineEdit_Source, 0, 1, 1, 1)
        self.label_Status = QtWidgets.QLabel(self.groupBox_CurrentObservation)
        self.label_Status.setObjectName("label_Status")
        self.gridLayout_2.addWidget(self.label_Status, 1, 0, 1, 1)
        self.lineEdit_Status = QtWidgets.QLineEdit(self.groupBox_CurrentObservation)
        self.lineEdit_Status.setReadOnly(True)
        self.lineEdit_Status.setObjectName("lineEdit_Status")
        self.gridLayout_2.addWidget(self.lineEdit_Status, 1, 1, 1, 1)
        self.label_StartUT = QtWidgets.QLabel(self.groupBox_CurrentObservation)
        self.label_StartUT.setObjectName("label_StartUT")
        self.gridLayout_2.addWidget(self.label_StartUT, 2, 0, 1, 1)
        self.lineEdit_StartUT = QtWidgets.QLineEdit(self.groupBox_CurrentObservation)
        self.lineEdit_StartUT.setReadOnly(True)
        self.lineEdit_StartUT.setObjectName("lineEdit_StartUT")
        self.gridLayout_2.addWidget(self.lineEdit_StartUT, 2, 1, 1, 1)
        self.label_EndUT = QtWidgets.QLabel(self.groupBox_CurrentObservation)
        self.label_EndUT.setObjectName("label_EndUT")
        self.gridLayout_2.addWidget(self.label_EndUT, 3, 0, 1, 1)
        self.lineEdit_EndUT = QtWidgets.QLineEdit(self.groupBox_CurrentObservation)
        self.lineEdit_EndUT.setReadOnly(True)
        self.lineEdit_EndUT.setObjectName("lineEdit_EndUT")
        self.gridLayout_2.addWidget(self.lineEdit_EndUT, 3, 1, 1, 1)
        self.label_Progress = QtWidgets.QLabel(self.groupBox_CurrentObservation)
        self.label_Progress.setObjectName("label_Progress")
        self.gridLayout_2.addWidget(self.label_Progress, 4, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.groupBox_CurrentObservation)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout_2.addWidget(self.progressBar, 4, 1, 1, 1)
        self.groupBox_ObservingQueue = QtWidgets.QGroupBox(self.groupBox_ObservingStatus)
        self.groupBox_ObservingQueue.setGeometry(QtCore.QRect(10, 200, 201, 221))
        self.groupBox_ObservingQueue.setObjectName("groupBox_ObservingQueue")
        self.pushButton_RemoveScheduledSource = QtWidgets.QPushButton(self.groupBox_ObservingQueue)
        self.pushButton_RemoveScheduledSource.setGeometry(QtCore.QRect(10, 150, 181, 32))
        self.pushButton_RemoveScheduledSource.setObjectName("pushButton_RemoveScheduledSource")
        self.checkBox_AutoSchedule = QtWidgets.QCheckBox(self.groupBox_ObservingQueue)
        self.checkBox_AutoSchedule.setGeometry(QtCore.QRect(20, 190, 181, 16))
        self.checkBox_AutoSchedule.setChecked(True)
        self.checkBox_AutoSchedule.setObjectName("checkBox_AutoSchedule")
        self.tableWidget_ObservingQueue = QtWidgets.QTableWidget(self.groupBox_ObservingQueue)
        self.tableWidget_ObservingQueue.setGeometry(QtCore.QRect(10, 30, 181, 111))
        self.tableWidget_ObservingQueue.setObjectName("tableWidget_ObservingQueue")
        self.tableWidget_ObservingQueue.setColumnCount(0)
        self.tableWidget_ObservingQueue.setRowCount(0)
        self.eventLogGroupBox = QtWidgets.QGroupBox(self.centralWidget)
        self.eventLogGroupBox.setGeometry(QtCore.QRect(0, 290, 401, 141))
        self.eventLogGroupBox.setObjectName("eventLogGroupBox")
        self.eventLogTextEdit = QtWidgets.QTextEdit(self.eventLogGroupBox)
        self.eventLogTextEdit.setGeometry(QtCore.QRect(10, 30, 381, 101))
        self.eventLogTextEdit.setObjectName("eventLogTextEdit")
        self.groupBox_TargetList = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_TargetList.setGeometry(QtCore.QRect(630, 0, 581, 431))
        self.groupBox_TargetList.setObjectName("groupBox_TargetList")
        self.pushButton_addTargetButton = QtWidgets.QPushButton(self.groupBox_TargetList)
        self.pushButton_addTargetButton.setGeometry(QtCore.QRect(0, 390, 181, 32))
        self.pushButton_addTargetButton.setObjectName("pushButton_addTargetButton")
        self.tableWidget_TargetList = QtWidgets.QTableWidget(self.groupBox_TargetList)
        self.tableWidget_TargetList.setGeometry(QtCore.QRect(10, 30, 561, 351))
        self.tableWidget_TargetList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_TargetList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_TargetList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget_TargetList.setObjectName("tableWidget_TargetList")
        self.tableWidget_TargetList.setColumnCount(0)
        self.tableWidget_TargetList.setRowCount(0)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1221, 22))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PulsarObserver"))
        self.groupBox_TelescopeStatus.setTitle(_translate("MainWindow", "Telescope status"))
        self.groupBox_tracking.setTitle(_translate("MainWindow", "Tracking"))
        self.label_ElError.setText(_translate("MainWindow", "Elerror"))
        self.label_AzOffset.setText(_translate("MainWindow", "Azoffset"))
        self.label_ElOffset.setText(_translate("MainWindow", "Eloffset"))
        self.label_AzError.setText(_translate("MainWindow", "Azerror"))
        self.label_Elevation.setText(_translate("MainWindow", "Elevation"))
        self.label_Azimuth.setText(_translate("MainWindow", "Azimuth"))
        self.groupBox_GeneralStatus.setTitle(_translate("MainWindow", "General"))
        self.label_LO1.setText(_translate("MainWindow", "LO1 [MHz]"))
        self.label_LO2.setText(_translate("MainWindow", "LO2 [MHz]"))
        self.label_Control.setText(_translate("MainWindow", "Control"))
        self.label_Allocation.setText(_translate("MainWindow", "Allocation"))
        self.label_Receiver.setText(_translate("MainWindow", "Receiver"))
        self.label_Coordsys.setText(_translate("MainWindow", "Coordsys"))
        self.label_Timestamp.setText(_translate("MainWindow", "HSL2 timestamp"))
        self.groupBox_ObservingStatus.setTitle(_translate("MainWindow", "Observing status"))
        self.groupBox_CurrentObservation.setTitle(_translate("MainWindow", "Current observation"))
        self.label_Source.setText(_translate("MainWindow", "Source"))
        self.label_Status.setText(_translate("MainWindow", "Status"))
        self.label_StartUT.setText(_translate("MainWindow", "Start UT"))
        self.label_EndUT.setText(_translate("MainWindow", "End UT"))
        self.label_Progress.setText(_translate("MainWindow", "Progress"))
        self.groupBox_ObservingQueue.setTitle(_translate("MainWindow", "Observing queue"))
        self.pushButton_RemoveScheduledSource.setText(_translate("MainWindow", "Remove selected"))
        self.checkBox_AutoSchedule.setText(_translate("MainWindow", "Auto-fill empty queue"))
        self.eventLogGroupBox.setTitle(_translate("MainWindow", "Event log"))
        self.groupBox_TargetList.setTitle(_translate("MainWindow", "Available targets"))
        self.pushButton_addTargetButton.setText(_translate("MainWindow", "Add selected to queue"))

