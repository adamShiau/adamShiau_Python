from memsImuReader_QT import memsImuReader as imu
import common as cmn
import time
import sys

sys.path.append("../")
# from myLib.myGui.graph import mplGraph_1
# from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from memsImu_Widget import memsImuWidget as TOP
from memsImuReader_QT import memsImuReader as ACTION
import numpy as np


class mainWindow(QWidget):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setWindowTitle("memsImuPlot")
        self.top = TOP()
        self.act = ACTION()
        self.mainUI()
        self.linkfunciton()
        self.wz = np.empty(0)
        self.t0 = time.perf_counter()
        self.__plot_ref = self.top.plot.ax.plot()

    def mainUI(self):
        mainLayout = QGridLayout()
        # self.setCentralWidget(QWidget(self))
        mainLayout.addWidget(self.top, 0, 0, 1, 1)
        self.setLayout(mainLayout)
        # self.setCentralWidget().setLayout(mainLayout)

    def linkfunciton(self):
        self.top.connect_bt.clicked.connect(self.connect)
        self.top.start_bt.clicked.connect(self.start)
        self.top.stop_bt.clicked.connect(self.disconnect)
        self.act.imudata_qt.connect(self.collectData)

    def start(self):
        self.act.isRun = True
        self.act.start()
        self.act.startIMU()

    def connect(self):
        # self.myImu = imu("COM5")
        # self.myImu.setCallback(self.myCallBack)
        self.act.connectIMU()
        self.act.start()
        self.act.isCali = False

        # cmn.wait_ms(5000)
        # myImu.isRun = False
        # myImu.disconnectIMU()
        # myImu.join()
        # print('KeyboardInterrupt success')

    def disconnect(self):
        self.act.isRun = False
        self.act.stopIMU()
        # self.act.disconnectIMU()
        # self.act.wait()

    def collectData(self, imudata, imuoffset):
        # self.wz = np.append(self.wz, imudata["NANO33_W"][2])
        # self.wz = np.append(self.wz, imudata["ADXL_A"][2])
        # print(len(self.wz))
        imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
        wx = imudata["NANO33_W"][0]
        wy = imudata["NANO33_W"][1]
        wz = imudata["NANO33_W"][2]
        ax = imudata["ADXL_A"][0]
        ay = imudata["ADXL_A"][1]
        az = imudata["ADXL_A"][2]
        fog = imudata["SPARROW"][0]
        # print(wx)
        # print(wy)
        # print(wz)
        # print(ax)
        # print(ay)
        # print(fog)

        self.plotdata2(fog)

    def plotdata2(self, wz):
        # imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
        # print(wz)
        # self.wz = self.wz + [imudata["NANO33_W"][2]]
        self.wz = np.append(self.wz, wz)
        if len(self.wz) > 1000:
            self.wz = self.wz[self.act.arrayNum:-1]
        # print(len(self.wz), end=", ")
        # print(self.act.readInputBuffer())
        self.__plot_ref.setData(self.wz)

    def plotdata(self, wz):
        self.top.plot.ax.clear()
        # imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
        # print(wz)
        # self.wz = self.wz + [imudata["NANO33_W"][2]]
        self.wzz = np.append(self.wzz, wz)
        if len(self.wzz) > 1000:
            self.wzz = self.wzz[50:-1]
        print(len(self.wzz))
        print(self.act.readInputBuffer())
        # print(len(self.wz))
        # print("%f, %f, %d" % ((time.perf_counter() - self.t0)*1e6, imudata["NANO33_W"][2], self.act.readInputBuffer()))
        # self.t0 = time.perf_counter()
        self.top.plot.ax.plot(self.wzz)
        self.top.plot.fig.canvas.draw()

    # def myCallBack(self, imudata, imuoffset):
    #     self.top.plot.ax.clear()
    #     imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
    #     self.wz = self.wz + [imudata["NANO33_W"][2]]
    #     if len(self.wz) > 200:
    #         self.wz = self.wz[1:-1]
    #     # print(len(self.wz))
    #     print("%f, %f, %d" % (time.perf_counter() - self.t0, imudata["NANO33_W"][2], self.act.readInputBuffer()))
    #     self.t0 = time.perf_counter()
    #     self.top.plot.ax.plot(self.wz)
    #     self.top.plot.fig.canvas.draw()
    #     self.top.plot.fig.canvas.flush_events()


if __name__ == "__main__":
    app = QApplication([])
    main = mainWindow()
    main.show()
    # myImu = imu("COM5")
    # myImu.setCallback(myCallBack)
    # myImu.isCali = True
    # myImu.connectIMU()
    # myImu.start()
    # try:
    #     while True:
    #         time.sleep(.1)
    # except KeyboardInterrupt:
    #     myImu.isRun = False
    #     myImu.disconnectIMU()
    #     myImu.join()
    #     print('KeyboardInterrupt success')
    app.exec_()
