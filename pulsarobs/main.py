from mainWindowUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import sys
import socket
import json

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.telescope = "Mark 2"
        self.initHSL2()
        self.initUi()

    def initHSL2(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(('localhost', 50000))
        except socket.error as serr:
            if serr.errno != errno.ECONNREFUSED:
                # Not the error we are looking for, re-raise
                raise serr
            else:
                print("ERROR: Cannot connect to HSL2 server, is it not running?")
                sys.exit(1)
        print("HSL2 init complete")


    def initUi(self):
        tl = self.tableWidget_TargetList
        self.targetList = []
        for line in open("testObsList.txt"):
            if not line.startswith("#"):
                fl = line.split()[0:8] # ignore comments
                self.targetList.append(fl)
        self.targetList = np.array(self.targetList)
        (nr, nc) = np.shape(self.targetList)
        nc = 4
        tl.setRowCount(nr)
        tl.setColumnCount(nc)
        tl.setHorizontalHeaderLabels(["Name","Priority", "R.A", "Dec."])
        tl.setSortingEnabled(True)
        for k, d in enumerate(self.targetList):
            tl.setItem(k, 0, QtWidgets.QTableWidgetItem(d[0]))
            tl.setItem(k, 1, QtWidgets.QTableWidgetItem(d[7]))
            tl.setItem(k, 2, QtWidgets.QTableWidgetItem(d[1]))
            tl.setItem(k, 3, QtWidgets.QTableWidgetItem(d[2]))
        # Set up buttons etc
        self.pushButton_addTargetButton.clicked.connect(self.addObsItem)
        self.pushButton_RemoveScheduledSource.clicked.connect(self.delObsItem)
        
        # Observing queue init
        oq = self.tableWidget_ObservingQueue
        oq.setColumnCount(1)
        oq.setHorizontalHeaderLabels(["Name"])

        # Timer init
        self.uitimer = QtCore.QTimer()
        self.uitimer.timeout.connect(self.updateUi)
        self.uitimer.start(1000)
        
        self.updateUi()


    def addObsItem(self):
        tl = self.tableWidget_TargetList
        name = tl.item(tl.currentRow(), 0).text()
        oq = self.tableWidget_ObservingQueue
        oq.insertRow(oq.rowCount())
        oq.setItem(oq.rowCount()-1, 0, QtWidgets.QTableWidgetItem(name))
    
    def delObsItem(self):
        oq = self.tableWidget_ObservingQueue
        oq.removeRow(oq.currentRow())

    def updateUi(self):
        self.getTeldata()
        td = self.teldata
        rec = td['status']['receiverstatus']['currentrec']
        act = np.array(td['status']['actual_azel'][0:2])*180/np.pi
        dem = np.array(td['status']['demanded_azel'][0:2])*180/np.pi
        LO1 = td['status']['receiverstatus']['currentLOs'][0]['loidfreq']/1e6
        LO2 = td['status']['receiverstatus']['currentLOs'][1]['loidfreq']/1e6
        self.lineEdit_Allocation.setText(td['status']['allocation'])
        self.lineEdit_Control.setText(td['status']['control'])
        self.lineEdit_Azimuth.setText('{:.5f}'.format(act[0]))
        self.lineEdit_Elevation.setText('{:.5f}'.format(act[1]))
        self.lineEdit_Receiver.setText(rec)
        self.lineEdit_LO1.setText('{0}'.format(LO1))
        self.lineEdit_LO2.setText('{0}'.format(LO2))
        self.lineEdit_Timestamp.setText(td['status']['time_isot'] + ' UTC')
        #print(self.teldata)
    
    def getTeldata(self):
        self.sock.sendall(self.telescope.encode()) # Encode to bytestring
        data = self.sock.recv(65536)
        data = data.decode() # From bytestring
        self.teldata = json.loads(data)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()    
