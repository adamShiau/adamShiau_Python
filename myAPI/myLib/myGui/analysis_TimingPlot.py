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
from myLib.myGui import myProgressBar
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
        self.timing_plot = graph.mplGraph_1()
        # self.read_bt = QPushButton('read')
        self.cal_bt = QPushButton('plot')
        self.cal_bt.setEnabled(False)
        # self.file_le = QLineEdit('0619.txt')
        self.pbar = myProgressBar.progress_bar_with_read()
        # self.pbar.filename = self.file_le.text()
        self.datahub = cmn.data_hub_manager()
        # self.datahub.key = 'wz'  # set default key
        self.__time = None
        self.linkfunction()
        # this line will emit a cb defaut key, must after linkfunction()
        self.cb.addItem(['wx', 'wy', 'wz', 'ax', 'ay', 'az'])
        # self.cb.addItem(['fog', 'wz', 'pd_T'])
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.cal_bt, 0, 0, 1, 1)
        # layout.addWidget(self.read_bt, 0, 1, 1, 1)
        # layout.addWidget(self.file_le, 0, 2, 1, 3)
        layout.addWidget(self.pbar.inst(), 0, 5, 1, 5)
        layout.addWidget(self.cb, 2, 0, 1, 1)
        layout.addWidget(self.timing_plot, 2, 1, 10, 10)
        self.setLayout(layout)

    def linkfunction(self):
        self.cb.getText_connect(self.datahub.connect_combobox)
        # self.read_bt.clicked.connect(self.readData)
        self.cal_bt.clicked.connect(self.plot)
        self.pbar.data_qt.connect(self.store_data)
        self.pbar.is_load_done_qt.connect(self.set_is_load_done_connect)
        self.cb.default_Item_qt.connect(self.set_default_key)

    def set_is_load_done_connect(self, done):
        self.cal_bt.setEnabled(done)
        if done:
            self.pbar.pbar_text = 'loading data: finish'
        else:
            self.pbar.pbar_text = 'loading data: start'

    def set_default_key(self, key):
        self.datahub.key = key

    def set_file_name(self):
        self.pbar.filename = self.file_le.text()

    def update_progress_bar(self, idx, total):
        pass

    def readData(self):
        self.pbar.read_btn()

    def store_data(self, data=None):
        self.__time = data['time']
        self.datahub.store_df_data(data)

    def plot(self):
        x = self.__time
        y = self.datahub.switch_df_data()
        self.timing_plot.ax.clear()
        self.timing_plot.ax.plot(x, y)
        self.timing_plot.fig.canvas.draw()


class analysis_timing_plot_widget_thread(QWidget):
    def __init__(self):
        super(analysis_timing_plot_widget_thread, self).__init__()
        self.data = None
        self.setWindowTitle('Plot Timing Data')
        self.cb = myComboBox.comboGroup_1('select data', 'select')
        # self.cb.addItem(['wx', 'wy', 'wz', 'ax', 'ay', 'az'])
        self.timing_plot = graph.mplGraph_1()
        self.read_bt = QPushButton('read')
        self.cal_bt = QPushButton('cal')
        self.cal_bt.setEnabled(False)
        self.file_le = QLineEdit('0619.txt')
        self.pbar = myProgressBar.progress_bar_with_read_thread()
        self.pbar.filename = self.file_le.text()
        self.datahub = cmn.data_hub_manager()
        # self.datahub.key = 'wz'  # set default key
        self.__time = None
        self.linkfunction()
        # this line will emit a cb defaut key, must after linkfunction()
        # self.cb.addItem(['wx', 'wy', 'wz', 'ax', 'ay', 'az'])
        self.cb.addItem(['fog', 'wz', 'pd_T'])
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.cal_bt, 0, 0, 1, 1)
        layout.addWidget(self.read_bt, 0, 1, 1, 1)
        layout.addWidget(self.file_le, 0, 2, 1, 3)
        layout.addWidget(self.pbar.inst(), 0, 5, 1, 5)
        layout.addWidget(self.cb, 2, 0, 1, 1)
        layout.addWidget(self.timing_plot, 2, 1, 10, 10)
        self.setLayout(layout)

    def linkfunction(self):
        self.cb.getText_connect(self.datahub.connect_combobox)
        self.file_le.editingFinished.connect(self.set_file_name)
        self.read_bt.clicked.connect(self.readData)
        self.cal_bt.clicked.connect(self.plot)
        self.pbar.data_qt.connect(self.store_data)
        self.pbar.finished.connect(self.thread_finish)
        self.pbar.started.connect(self.thread_start)
        self.cb.default_Item_qt.connect(self.set_default_key)

    def set_default_key(self, key):
        self.datahub.key = key

    def set_file_name(self):
        self.pbar.filename = self.file_le.text()

    def update_progress_bar(self, idx, total):
        pass

    def readData(self):
        self.pbar.start()

    def store_data(self, data=None):
        self.__time = data['t']
        self.datahub.store_df_data(data)

    def plot(self):
        x = self.__time
        y = self.datahub.switch_df_data()
        self.timing_plot.ax.clear()
        self.timing_plot.ax.plot(x, y)
        self.timing_plot.fig.canvas.draw()

    def thread_start(self):
        self.cal_bt.setEnabled(False)
        self.pbar.pbar_text = 'loading data: start'
        pass

    def thread_finish(self):
        self.cal_bt.setEnabled(True)
        self.pbar.pbar_text = 'loading data: finish'
        self.pbar.wait()
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = analysis_timing_plot_widget()
    # w = analysis_timing_plot_widget_thread()
    w.show()
    app.exec_()
