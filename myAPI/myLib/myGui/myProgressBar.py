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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os, sys
import pandas as pd


class progress_bar_with_read(QGroupBox):
    def __init__(self, title='', file=''):
        super(progress_bar_with_read, self).__init__()
        # self.__file = file
        # self.win = QGroupBox()
        self.setTitle(title)
        self.file_le = QLineEdit('0619.txt')
        self.read_bt = QPushButton('read')
        self.filename = self.file_le.text()
        self.pbar = QProgressBar(self)
        # self.pbar.setValue(50)
        self.connect()
        self.layout()

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.read_bt, 0, 0, 1, 1)
        layout.addWidget(self.file_le, 1, 0, 1, 1)
        layout.addWidget(self.pbar, 1, 1, 1, 3)
        self.setLayout(layout)

    def connect(self):
        self.file_le.editingFinished.connect(self.set_filename)
        self.read_bt.clicked.connect(self.start_read)

    def set_filename(self):
        self.filename = self.file_le.text()
        print(self.file_le.text())

    @property
    def filename(self):
        return self.__filename
    
    @filename.setter
    def filename(self, name):
        self.__filename = name

    def start_read(self):
        self.readData()

    def readData(self, chunksize=6000, row_len=20, skiprows=2):
        nrows = row_len - 1
        total_data_len = self.find_data_length(self.filename, nrows, row_len, skiprows)
        df = []
        for chunk in pd.read_csv(self.filename, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0, chunksize=chunksize):
            df.append(chunk)
            current_data_len = len(df) * chunksize
            self.updatePbar(current_data_len, total_data_len)
        self.updatePbar(total_data_len, total_data_len)
        return pd.concat((f for f in df))

    def find_data_length(self, file, nrows, row_len, skiprows):
        temp = pd.read_csv(file, sep=r'\s*,\s*', engine='python', comment='#', skiprows=skiprows, nrows=nrows)
        file_size = os.path.getsize(file)
        block_size = len(temp.to_csv(index=False)) * 1.05
        total_data_len = int(file_size / block_size) * row_len
        return total_data_len

    def updatePbar(self, now, total):
        print(round(now/total, 2))
        self.pbar.setValue(int(now * 100 / total))

    def inst(self):
        return self


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = progress_bar_with_read('test', '0619.txt')
    w.inst()
    w.show()
    # w.start()
    # w.readData()
    app.exec_()
