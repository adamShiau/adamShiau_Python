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
from myLib.myGui import myLabel
from myLib.myGui import myComboBox
import myLib.common as cmn
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import matplotlib.pyplot as plt


class analysis_allan_widget(QWidget):
    def __init__(self):
        super(analysis_allan_widget, self).__init__()
        self.data = None
        self.setWindowTitle('Allen Variance Analysis')
        self.dev = np.empty(0)  # Create empty array to store the output.
        self.actualTau = np.empty(0)
        self.allan = allan_dev()
        # add widget
        self.cb = myComboBox.comboGroup_1('select data', 'select')
        self.cb.addItem(['fog', 'wz'])
        self.allan_plot = graph.mplGraph_1()
        self.cal_bt = QPushButton('cal')
        self.adj_tau = adj_tau_widget()
        self.progress = myLabel.twoLabelBlock(title='Allan dev. Progress')
        # end of add widget
        self.linkfunction()
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.cal_bt, 0, 0, 1, 1)
        layout.addWidget(self.adj_tau, 0, 1, 1, 5)
        layout.addWidget(self.progress, 0, 6, 1, 1)
        layout.addWidget(self.cb, 2, 0, 1, 1)
        layout.addWidget(self.allan_plot, 2, 1, 10, 10)
        self.setLayout(layout)

    def linkfunction(self):
        self.cb.getText_connect(self.allan.datahub.connect_combobox)
        # self.cb.getText_connect(testfn)
        self.cal_bt.clicked.connect(self.cal_allan_dev)
        # self.adj_tau.read_bt.clicked.connect(lambda: self.allan.readData(self.adj_tau.file_le.text()))
        self.adj_tau.read_bt.clicked.connect(self.readData)
        self.adj_tau.tauarray_le.editingFinished.connect(
            lambda: self.allan.set_tau_array(self.adj_tau.tauarray_le))
        self.adj_tau.tp_le.editingFinished.connect(lambda: self.allan.set_tau_array(self.adj_tau.tp_le))
        self.allan.allan_qt.connect(self.plot)
        self.allan.finish_qt.connect(self.fit_data)
        self.allan.tauarray_qt.connect(self.setTauArray)
        self.allan.progress_qt.connect(self.update_progress_bar)

    def update_progress_bar(self, idx, total):
        progress = int(idx / total * 100)
        if progress == 100:
            self.progress.lb1.setText('Finish')
        else:
            self.progress.lb1.setText('Running')
        self.progress.lb2.setText(str(progress) + '%')

    def readData(self):
        self.allan.readData(self.adj_tau.file_le.text())

    def setTauArray(self, tauarray):
        tauarray = [round(i * self.allan.tau0, 2) for i in tauarray]
        self.adj_tau.tauarray_le.setText(str(tauarray))

    def cal_allan_dev(self):
        # print('start cal allan')
        self.allan.start()

    def fit_data(self, tau, dev):
        idx_arw = np.where(tau == 1)[0][0]
        x = np.log10(tau[0:idx_arw + 1])
        y = np.log10(dev[0:idx_arw + 1])
        # print(x)
        # print(y)
        a, b = np.polyfit(x, y, 1)
        self.allan_plot.ax.loglog(tau[0:idx_arw + 3], 10 ** (a * np.log10(tau[0:idx_arw + 3]) + b) * 3600, color='blue',
                                  linestyle='--', linewidth=2)
        bias = self.findBias(tau, dev)
        if bias is not None:
            bias = (10 ** bias) * 3600
            self.allan_plot.ax.loglog(tau, [bias] * len(tau), color='green', linestyle='--', linewidth=2)
        self.allan_plot.fig.canvas.draw()
        arw = (10 ** b * 3600) / 60
        print(a, b, arw)
        print(bias)

    def findBias(self, tau, dev):
        size = len(tau)
        tau2 = tau[1:size]
        dev2 = dev[1:size]
        dx = tau2 - tau[0:size - 1]
        dy = dev2 - dev[0:size - 1]
        slope = dy / dx
        # print(slope)
        try:
            idx = np.where(slope > 0)[0][0]
            return np.log10(dev[idx])
        except IndexError:
            logger.info('no bias instability value.')
            return None

    def plot(self, tau, dev):
        self.allan_plot.ax.clear()
        self.allan_plot.ax.loglog(tau, dev * 3600, 'k-*')  # convert unit to dph
        self.allan_plot.fig.canvas.draw()

    # def show(self):
    #     self.show()


def testfn(i):
    cmn.print_debug('name: %s' % i.property('name'), 1)
    cmn.print_debug('key: %s' % i.currentText(), 1)


class allan_dev(QThread):
    allan_qt = pyqtSignal(object, object)
    finish_qt = pyqtSignal(object, object)
    tauarray_qt = pyqtSignal(object)
    progress_qt = pyqtSignal(int, int)

    def __init__(self):
        super(allan_dev, self).__init__()
        self.datahub = cmn.data_hub_manager()
        self.datahub.key = 'fog'  # set default key
        self.tauArray = []
        self.datalength = None
        self.data = None
        self.is_tauArray_done = False
        # tau0 = 1 / rate
        self.tau0 = None

    @property
    def is_tauArray_done(self):
        return self.__is_tauArray_done

    @is_tauArray_done.setter
    def is_tauArray_done(self, flag):
        self.__is_tauArray_done = flag

    def readData(self, file):
        print('do readData ')
        t1 = time.perf_counter()
        # data = pd.read_csv(file, sep=r'\s*,\s*', engine='python', comment='#')
        data = pd.read_csv(file, comment='#')
        self.datahub.store_df_data(data)
        t2 = time.perf_counter()
        print('read: ', round((t2 - t1), 2))
        t = np.array(data.t)
        self.datalength = len(t)
        tau0 = round((t[-1] - t[0]) / (self.datalength - 1), 3)
        self.tau0 = tau0
        self.cal_tau_array(self.datalength, tau0)
        # theta_wz = tuple(np.cumsum(np.array(self.datahub.df_data)) * tau0)
        # self.data = theta_wz

    def getdata(self):
        theta_wz = tuple(np.cumsum(np.array(self.datahub.switch_df_data())) * self.tau0)
        return theta_wz

    def cal_tau_array(self, size, tau0):
        rate = int(1 / tau0)
        m_max = int(np.floor((size - 1) / 2))
        print(m_max)
        print(np.log10(m_max))
        n = np.logspace(0, np.log10(m_max), 10, dtype=int)
        print(n)
        n = np.append(n, rate)
        tauArray = np.sort(n)
        self.tauArray = [int(i) for i in tauArray]
        print(self.tauArray)
        self.tauarray_qt.emit(self.tauArray)

    def set_tau_array(self, value):
        # print(value.property('name'))
        le_name = value.property('name')
        if le_name == 'tau':
            temp = value.text().strip('[]').split(',')
            temp = [np.floor(float(i) / self.tau0) for i in temp]
            temp = np.array(temp, dtype=int)
            self.tauArray = np.unique(temp)
            self.tauArray = [int(i) for i in self.tauArray]
            print(self.tauArray, type(self.tauArray[0]))

        elif le_name == 'tp':
            if bool(value.text()):
                try:
                    temp = value.text().strip('[]').split(',')
                    temp = [np.floor(float(i) / self.tau0) for i in temp]
                    temp = np.array(temp, dtype=int)
                    tp1 = temp[0]
                    tp2 = temp[1]
                    n = np.logspace(np.log10(tp1), np.log10(tp2), 5, dtype=int)
                    # n = n[1:-1]
                    self.tauArray = np.unique(np.append(self.tauArray, n))
                    self.tauArray = [int(i) for i in self.tauArray]
                    self.tauarray_qt.emit(self.tauArray)
                    print(self.tauArray, type(self.tauArray[0]))

                except ValueError:
                    print('ValueError')

    def run(self):
        dev = np.array([])  # Create empty array to store the output.
        actualTau = np.array([])
        print('run')
        progress_bar_total = len(self.tauArray)
        progress_bar_current = 0
        self.progress_qt.emit(progress_bar_current, progress_bar_total)
        for n in self.tauArray:
            currentSum = 0  # Initialize the sum

            tlp_s = time.perf_counter()
            data = self.getdata()
            for j in range(0, self.datalength - 2 * n):
                currentSum = (data[j + 2 * n] - 2 * data[j + n] + data[j]) ** 2 + currentSum

            tlp_e = time.perf_counter()
            print('n= ', n, end=', ')
            print(self.datalength - 2 * n, end=', ')
            print(round((tlp_e - tlp_s), 2))
            devAtThisTau = currentSum / (
                    2 * n ** 2 * self.tau0 ** 2 * (self.datalength - 2 * n))  # Divide by the coefficient
            dev = np.append(dev, np.sqrt(devAtThisTau))
            actualTau = np.append(actualTau, n * self.tau0)
            progress_bar_current += 1
            self.progress_qt.emit(progress_bar_current, progress_bar_total)
            self.allan_qt.emit(actualTau, dev)
        # end of for loop
        self.finish_qt.emit(actualTau, dev)
    # end of run()


class adj_tau_widget(QGroupBox):
    def __init__(self):
        super(adj_tau_widget, self).__init__()
        self.setFont(QFont('Arial', 10))
        self.setTitle('Adjust Tau Array')
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.blue)
        # pe.setColor(QPalette.Window, Qt.black)
        # button
        self.read_bt = QPushButton('Read File')
        self.read_bt.setProperty('name', 'read_bt')
        qssStyle = '''QPushButton[name='read_bt']{background-color:#F9F900}'''
        self.setStyleSheet(qssStyle)
        # line editor
        self.file_le = QLineEdit('0616_long.txt')
        self.tp_le = QLineEdit()
        self.tp_le.setFixedWidth(100)
        self.tp_le.setProperty('name', 'tp')
        self.tauarray_le = QLineEdit('')
        self.tauarray_le.setProperty('name', 'tau')
        # label
        self.tp_lb = QLabel('t1, t2 : insert 5 points between t1 and t2 seconds')
        self.tp_lb.setPalette(pe)
        self.tp_lb.setFixedWidth(100)
        self.tp_lb.setFont(QFont('Arial', 12))
        self.tp_lb.setFixedWidth(500)
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.read_bt, 0, 0, 1, 1)
        layout.addWidget(self.tp_le, 0, 1, 1, 1)
        layout.addWidget(self.tp_lb, 0, 2, 1, 5)
        layout.addWidget(self.file_le, 1, 0, 1, 1)
        layout.addWidget(self.tauarray_le, 1, 1, 1, 6)
        self.setLayout(layout)
        return self


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = analysis_allan_widget()
    # w = adj_tau_widget()
    w.show()
    app.exec_()
