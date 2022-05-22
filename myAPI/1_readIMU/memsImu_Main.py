import sys

sys.path.append("../")
from myLib import common as cmn
import time

from PyQt5.QtWidgets import *
from memsImu_Widget import memsImuWidget as TOP
from memsImuReader import memsImuReader as ACTION
from memsImuReader import IMU_DATA_STRUCTURE
import numpy as np


class mainWindow(QWidget):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setWindowTitle("memsImuPlot")
        self.top = TOP()
        self.act = ACTION()
        self.mainUI()
        self.linkfunciton()
        self.imudata = self.resetDataContainer()
        self.act.arrayNum = 30

    def mainUI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.top, 0, 0, 1, 1)
        self.setLayout(mainLayout)

    def linkfunciton(self):
        self.top.connect_bt.clicked.connect(self.connect)
        self.top.start_bt.clicked.connect(self.start)
        self.top.stop_bt.clicked.connect(self.stop)
        self.act.imudata_qt.connect(self.collectData)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)

    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def resetDataContainer(self):
        return {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
                for k in set(IMU_DATA_STRUCTURE)}

    def start(self):
        self.act.readIMU()
        self.act.isRun = True
        self.act.start()

    def stop(self):
        self.act.isRun = False

    def connect(self):
        self.act.connect()
        self.act.isCali = True

    def collectData(self, imudata, imuoffset):
        imuoffset["TIME"] = [0]
        imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
        self.imudata = cmn.dictOperation(self.imudata, imudata, "APPEND")

        if len(self.imudata["TIME"]) > 1000:
            self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:-1]
            self.imudata["NANO33_A"][0] = self.imudata["NANO33_A"][0][self.act.arrayNum:-1]
            self.imudata["NANO33_A"][1] = self.imudata["NANO33_A"][1][self.act.arrayNum:-1]
            self.imudata["NANO33_A"][2] = self.imudata["NANO33_A"][2][self.act.arrayNum:-1]
            self.imudata["NANO33_W"][0] = self.imudata["NANO33_W"][0][self.act.arrayNum:-1]
            self.imudata["NANO33_W"][1] = self.imudata["NANO33_W"][1][self.act.arrayNum:-1]
            self.imudata["NANO33_W"][2] = self.imudata["NANO33_W"][2][self.act.arrayNum:-1]
        self.plotdata(self.imudata)
        print(len(self.imudata["TIME"]))

    def plotdata(self, imudata):
        self.top.plot1.ax2.setData(imudata["TIME"], imudata["NANO33_W"][2])
        self.top.plot2.ax.setData(imudata["NANO33_A"][0])
        self.top.plot3.ax.setData(imudata["NANO33_A"][1])
        self.top.plot4.ax.setData(imudata["NANO33_A"][2])
        self.top.plot5.ax.setData(imudata["NANO33_W"][0])
        self.top.plot6.ax.setData(imudata["NANO33_W"][1])


if __name__ == "__main__":
    app = QApplication([])
    main = mainWindow()
    main.show()
    app.exec_()
