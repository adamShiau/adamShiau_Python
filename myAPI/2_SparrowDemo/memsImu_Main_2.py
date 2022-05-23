import logging
import sys

sys.path.append("../")
from myLib import common as cmn
import time

from PyQt5.QtWidgets import *
from memsImu_Widget_2 import memsImuWidget as TOP
from memsImuReader_2 import memsImuReader as ACTION
from memsImuReader_2 import IMU_DATA_STRUCTURE_ARRAY
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
        self.act.arrayNum = 5

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
        return {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE_ARRAY.get(k)))]
                for k in set(IMU_DATA_STRUCTURE_ARRAY)}

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
        print("MAIN: ", end=", ")
        print(self.act.readInputBuffer(), end=", ")
        t0 = time.perf_counter()
        imuoffset["TIME"] = [0]
        # print(self.act.readInputBuffer(), imudata)
        imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE_ARRAY)
        t1 = time.perf_counter()
        # self.imudata = cmn.dictOperation(self.imudata, imudata, "APPEND", IMU_DATA_STRUCTURE_ARRAY)
        self.imudata["TIME"] = np.append(self.imudata["TIME"], imudata["TIME"])
        self.imudata["SPARROW"] = np.append(self.imudata["SPARROW"], imudata["SPARROW"])
        self.imudata["NANO33_A"][0] = np.append(self.imudata["NANO33_A"][0], imudata["NANO33_A"][0])
        self.imudata["NANO33_A"][1] = np.append(self.imudata["NANO33_A"][1], imudata["NANO33_A"][1])
        self.imudata["NANO33_A"][2] = np.append(self.imudata["NANO33_A"][2], imudata["NANO33_A"][2])
        self.imudata["NANO33_W"][0] = np.append(self.imudata["NANO33_W"][0], imudata["NANO33_W"][0])
        self.imudata["NANO33_W"][1] = np.append(self.imudata["NANO33_W"][1], imudata["NANO33_W"][1])
        self.imudata["NANO33_W"][2] = np.append(self.imudata["NANO33_W"][2], imudata["NANO33_W"][2])
        t2 = time.perf_counter()
        # print( self.imudata["TIME"])
        if len(self.imudata["TIME"]) > 1000:
            self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:-1]
            self.imudata["SPARROW"] = self.imudata["SPARROW"][self.act.arrayNum:-1]
            self.imudata["NANO33_A"][0] = self.imudata["NANO33_A"][0][self.act.arrayNum:-1]
            self.imudata["NANO33_A"][1] = self.imudata["NANO33_A"][1][self.act.arrayNum:-1]
            self.imudata["NANO33_A"][2] = self.imudata["NANO33_A"][2][self.act.arrayNum:-1]
            self.imudata["NANO33_W"][0] = self.imudata["NANO33_W"][0][self.act.arrayNum:-1]
            self.imudata["NANO33_W"][1] = self.imudata["NANO33_W"][1][self.act.arrayNum:-1]
            self.imudata["NANO33_W"][2] = self.imudata["NANO33_W"][2][self.act.arrayNum:-1]
        t3 = time.perf_counter()
        print((t3 - t0) * 1000, end=", ")
        print((t1 - t0) * 1000, end=", ")
        print((t2 - t1) * 1000, end=", ")
        print((t3 - t2) * 1000)
        self.plotdata(self.imudata)
        # print(self.imudata["TIME"])
        # print(len(self.imudata["TIME"]))

    def plotdata(self, imudata):
        self.top.plot1.ax1.setData(imudata["TIME"], imudata["SPARROW"])
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
