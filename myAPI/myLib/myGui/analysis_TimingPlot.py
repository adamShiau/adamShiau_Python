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
import os
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


class analysis_timing_plot_widget(QWidget):
    def __init__(self):
        super(analysis_timing_plot_widget, self).__init__()
        self.data = None
        self.setWindowTitle('Plot Timing Data')
        self.cb = myComboBox.comboGroup_1('select data', 'select')
        self.cb.addItem(['fog', 'wz'])
        self.timing_plot = graph.mplGraph_1()
        self.read_bt = QPushButton('read')
        self.cal_bt = QPushButton('cal')
        self.pbar = QProgressBar(self)
        self.load_data = load_data()
        self.progress = myLabel.twoLabelBlock(title='Plotting Progress')
        # end of add widget
        self.linkfunction()
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.cal_bt, 0, 0, 1, 1)
        layout.addWidget(self.read_bt, 0, 1, 1, 1)
        layout.addWidget(self.progress, 0, 2, 1, 1)
        layout.addWidget(self.pbar, 0, 3, 1, 3)
        layout.addWidget(self.cb, 2, 0, 1, 1)
        layout.addWidget(self.timing_plot, 2, 1, 10, 10)
        self.setLayout(layout)

    def linkfunction(self):
        self.cb.getText_connect(self.load_data.datahub.connect_combobox)
        self.read_bt.clicked.connect(self.readData)
        self.cal_bt.clicked.connect(self.plot)
        self.load_data.progress_qt.connect(self.update_progress_bar)

    def update_progress_bar(self, idx, total):
        progress = int(idx / total * 100)
        if progress == 100:
            self.progress.lb1.setText('Finish')
        else:
            self.progress.lb1.setText('Running')
        self.progress.lb2.setText(str(progress) + '%')

    def readData(self):
        self.load_data.start()

    def plot(self):
        x = self.load_data.t
        y = self.load_data.getdata()
        self.timing_plot.ax.clear()
        self.timing_plot.ax.plot(x, y)
        self.timing_plot.fig.canvas.draw()

    # def show(self):
    #     self.show()


class load_data(QThread):
    allan_qt = pyqtSignal(object, object)
    finish_qt = pyqtSignal(object, object)
    tauarray_qt = pyqtSignal(object)
    progress_qt = pyqtSignal(object)

    def __init__(self):
        super(load_data, self).__init__()
        self.t = None
        self.datahub = cmn.data_hub_manager()
        self.datahub.key = 'fog'  # set default key

        self.tauArray = []
        self.datalength = None
        self.data = None
        self.is_tauArray_done = False
        self.tau0 = None

    def readData(self, file):
        print('do readData ')
        t1 = time.perf_counter()
        data = pd.read_csv(file, sep=r'\s*,\s*', engine='python', comment='#')
        self.datahub.store_df_data(data)
        t2 = time.perf_counter()
        print('read: ', round((t2 - t1), 2))
        self.t = np.array(data.time)
        self.datalength = len(self.t)

        temp = pd.read_csv(file, nrows=20)
        N = len(temp.to_csv(index=False))
        df = [temp[:0]]
        t = int(os.path.getsize(file) / N * 20 / 10 ** 4) + 1
        for i, chunk in enumerate(pd.read_csv(file, chunksize=10 ** 4, low_memory=False)):
            df.append(chunk)
            self.progress_qt.emit()
            pbar.set_description('Importing: %d' % (1 + i))
            pbar.update(1)

        data = temp[:0].append(df)
        del df

    def getdata(self):
        # theta_wz = tuple(np.cumsum() * self.tau0)
        data = np.array(self.datahub.switch_df_data())
        return data
        # self.data = theta_wz

    def run(self):
        print('run')
        # progress_bar_total = 100
        # progress_bar_current = 0
        # self.progress_qt.emit(progress_bar_current, progress_bar_total)
        self.readData('0402.txt')

        # progress_bar_current += 1
        # self.progress_qt.emit(progress_bar_current, progress_bar_total)
        print('run done')
    # end of run()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = analysis_timing_plot_widget()
    # w = adj_tau_widget()
    w.show()
    app.exec_()
