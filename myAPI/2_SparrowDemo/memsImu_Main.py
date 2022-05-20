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
        self.wx = np.empty(0)
        self.wy = np.empty(0)
        self.wz = np.empty(0)
        self.ax = np.empty(0)
        self.ay = np.empty(0)
        self.az = np.empty(0)
        self.fog = np.empty(0)
        self.t = np.empty(0)
        self.t0 = time.perf_counter()
        # self.__plot_ref = self.top.plot.ax.plot()

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
        self.act.isCali = True

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

    def collectData(self, imudata, imuoffset, t):
        imudata = cmn.dictOperation(imudata, imuoffset, "SUB")
        wx = imudata["NANO33_W"][0]
        wy = imudata["NANO33_W"][1]
        wz = imudata["NANO33_W"][2]
        ax = imudata["ADXL_A"][0]
        ay = imudata["ADXL_A"][1]
        az = imudata["ADXL_A"][2]
        fog = imudata["SPARROW"][0]
        self.plotdata2(wx, wy, wz, ax, ay, az, fog, t)
        # self.plotdata2(fog)

    def plotdata2(self, wx, wy, wz, ax, ay, az, fog, t):
        self.ax = np.append(self.ax, ax)
        self.ay = np.append(self.ay, ay)
        self.az = np.append(self.az, az)
        self.wx = np.append(self.wx, wx)
        self.wy = np.append(self.wy, wy)
        self.wz = np.append(self.wz, wz)
        self.fog = np.append(self.fog, fog)
        self.t = np.append(self.t, t)
        if len(self.wz) > 1000:
            self.ax = self.ax[self.act.arrayNum:-1]
            self.ay = self.ay[self.act.arrayNum:-1]
            self.az = self.az[self.act.arrayNum:-1]
            self.wx = self.wx[self.act.arrayNum:-1]
            self.wy = self.wy[self.act.arrayNum:-1]
            self.wz = self.wz[self.act.arrayNum:-1]
            self.fog = self.fog[self.act.arrayNum:-1]
            self.t = self.t[self.act.arrayNum:-1]
        self.top.plot1.ax1.setData(self.t, self.fog)
        self.top.plot1.ax2.setData(self.t, self.wz)
        self.top.plot2.ax.setData(self.ax)
        self.top.plot3.ax.setData(self.ay)
        self.top.plot4.ax.setData(self.az)
        self.top.plot5.ax.setData(self.wx)
        self.top.plot6.ax.setData(self.wy)
        # self.top.plot2.ax2_1.setData(self.az)
        # self.top.plot2.ax2_1.plot(self.az)

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
