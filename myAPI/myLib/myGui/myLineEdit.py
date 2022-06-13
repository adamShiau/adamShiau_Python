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


class dataSaveBlock(QGroupBox):
    def __init__(self, name=""):
        super(dataSaveBlock, self).__init__()
        self.setTitle(name)
        self.setFont(QFont('Arial', 10))
        self.rb = QRadioButton("save")
        self.le_filename = QLineEdit("enter_file_name")
        self.le_ext = QLineEdit(".txt")
        self.le_ext.setFixedWidth(50)
        self.rb.setChecked(False)

        layout = QGridLayout()
        layout.addWidget(self.rb, 0, 0, 1, 1)
        layout.addWidget(self.le_filename, 0, 1, 1, 1)
        layout.addWidget(self.le_ext, 0, 4, 1, 1)
        self.setLayout(layout)


class lineEditBlock(QGroupBox):
    def __init__(self, name=""):
        super(lineEditBlock, self).__init__()
        self.setTitle(name)
        self.setFont(QFont('', 10))
        self.le_filename = QLineEdit("parameters_SP9")

        layout = QGridLayout()
        layout.addWidget(self.le_filename, 0, 1, 1, 1)
        self.setLayout(layout)

if __name__ == '__main__':

    app = QApplication
    w = dataSaveBlock('test')
    w.show()
    app.exec_()

