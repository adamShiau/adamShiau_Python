# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import os

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
ExternalName_log = __name__
if os.getenv('verNum') == str(True) :
    ExternalName_log = "CBox_logger"

logger = logging.getLogger(logger_name + '.' + ExternalName_log)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class checkBoxBlock_2(QGroupBox):
    def __init__(self, title='', name1='', name2=''):
        super(checkBoxBlock_2, self).__init__()
        self.setFont(QFont('Arial', 10))
        self.setTitle(title)
        self.cb_1 = QCheckBox(name1)
        self.cb_2 = QCheckBox(name2)
        self.cb_1.setChecked(True)
        # pe = QPalette()
        # pe.setColor(QPalette.Window, Qt.white)
        # self.setPalette(pe)
        # self.setAutoFillBackground(True)

        layout = QHBoxLayout()
        layout.addWidget(self.cb_1)
        layout.addWidget(self.cb_2)
        self.setLayout(layout)


class checkBoxBlock_3(QGroupBox):
    def __init__(self, title="", name1="", name2="", name3=""):
        super(checkBoxBlock_3, self).__init__()
        self.setFont(QFont('Arial', 10))
        self.setTitle(title)
        self.cb1 = QCheckBox(name1)
        self.cb2 = QCheckBox(name2)
        self.cb3 = QCheckBox(name3)
        self.cb1.setChecked(True)
        self.cb2.setChecked(True)
        self.cb3.setChecked(True)


        layout = QVBoxLayout()
        layout.addWidget(self.cb1)
        layout.addWidget(self.cb2)
        layout.addWidget(self.cb3)
        self.setLayout(layout)

