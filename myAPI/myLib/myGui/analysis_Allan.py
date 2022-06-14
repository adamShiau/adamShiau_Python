# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys

sys.path.append("../../")
import numpy as np
import pandas as pd
import time
from myLib.myGui import graph
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal


class analysis_allan_widget(QWidget):
    def __init__(self):
        super(analysis_allan_widget, self).__init__()
        self.setWindowTitle('Allen Variance Analysis')
        self.dev = np.empty(0)  # Create empty array to store the output.
        self.actualTau = np.empty(0)
        self.allan = allan_dev(100)
        self.allan_plot = graph.mplGraph_1()
        # self.allan_plot = graph.pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        self.cal_bt = QPushButton('cal')
        self.linkfunction()
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.allan_plot, 1, 0, 10, 10)
        layout.addWidget(self.cal_bt, 0, 0, 1, 1)
        self.setLayout(layout)

    def linkfunction(self):
        self.cal_bt.clicked.connect(self.cal_allan_dev)
        self.allan.allan_qt.connect(self.collect_data)

    def cal_allan_dev(self):
        print('start cal allan')
        self.allan.readData('0402_noKAL.txt') #0402_noKAL
        self.allan.start()

    def collect_data(self, tau, dev):
        self.dev = np.append(self.dev, dev)  # Create empty array to store the output.
        self.actualTau = np.append(self.actualTau, tau)
        # self.plot(np.log(tau), np.log(dev))
        self.plot(self.actualTau, self.dev)

    def plot(self, tau, dev):
        # print(tau, dev)
        # self.allan_plot.ax.setData(tau, dev)
        self.allan_plot.ax.clear()
        self.allan_plot.ax.loglog(tau, dev, '-*')
        self.allan_plot.fig.canvas.draw()

    # def show(self):
    #     self.show()


class allan_dev(QThread):
    allan_qt = pyqtSignal(object, object)

    def __init__(self, rate):
        super(allan_dev, self).__init__()
        self.data = None
        tau0 = 1 / rate
        self.tau0 = tau0
        # N = len(data)  # Calculate N, data length
        # maxTau = (N - 1) * tau0 / 2
        self.tauArray = [tau0, 3 * tau0, 5 * tau0, 10 * tau0, 30 * tau0, 50 * tau0,
                    100 * tau0, 300 * tau0, 500 * tau0, 1000 * tau0, 3e3 * tau0,
                    5000 * tau0, 10000 * tau0, 3e4 * tau0, 50000 * tau0, 100000 * tau0,
                    5e5 * tau0, 1e6 * tau0, 2e6 * tau0, 8e6 * tau0]
        # data = self.readData(file, tau0)
        # tau, allanDev = self.cal_oadev(data, tau0, tauArray)

    def readData(self, file):
        print('file: ', file)
        t1 = time.perf_counter()
        Var = pd.read_csv(file, comment='#')
        t2 = time.perf_counter()
        print('read: ', (t2-t1)*1e3)
        # Var.columns = ['time', 'wx', 'wy', 'wz', 'ax', 'ay', 'az']
        Var.columns = ['time', 'wz', 'err', 'temp']
        # wz = np.array(Var.wz)
        theta_wz = tuple(np.cumsum(np.array(Var.wz)) * self.tau0)
        self.data = theta_wz
        return theta_wz

    def run(self):
        dataLength = len(self.data)  # Calculate N, data length
        dev = np.array([])  # Create empty array to store the output.
        actualTau = np.array([])
        print('run')
        for i in self.tauArray:
            n = int(np.floor(i / self.tau0))  # Calculate n given a tau value.
            if n == 0:
                n = 1  # Use minimal n if tau is less than the sampling period.
            currentSum = 0  # Initialize the sum
            # print('n: ', n)
            tlp_s = time.perf_counter()
            for j in range(0, dataLength - 2 * n):
                currentSum = (self.data[j + 2 * n] - 2 * self.data[j + n] + self.data[j]) ** 2 + currentSum  # Cumulate the sum squared
                # currentSum += np.square((data[j + 2 * n] - 2 * data[j + n] + data[j]))
            tlp_e = time.perf_counter()
            print('n= ', n, end=', ')
            print(dataLength - 2 * n, end=', ')
            print((tlp_e-tlp_s)*1e3)
            devAtThisTau = currentSum / (2 * n ** 2 * self.tau0 ** 2 * (dataLength - 2 * n))  # Divide by the coefficient
            dev = np.append(dev, np.sqrt(devAtThisTau))
            self.allan_qt.emit(n * self.tau0, np.sqrt(devAtThisTau))
            actualTau = np.append(actualTau, n * self.tau0)
        # return actualTau, dev  # Return the actual tau and overlapped Allan deviation


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = analysis_allan_widget()
    w.show()
    app.exec_()
