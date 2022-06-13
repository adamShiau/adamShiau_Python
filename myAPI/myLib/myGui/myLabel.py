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


class logo(QLabel):
    def __init__(self, pic_path):
        super(logo, self).__init__()
        self.setStyleSheet('''QLabel{background-color: #3b234d}''')
        self.setAlignment(Qt.AlignCenter)
        self.setPixmap(QPixmap(pic_path))


class displayOneBlock(QGroupBox):
    def __init__(self, name='name'):
        super(displayOneBlock, self).__init__()
        self.setTitle(name)
        self.setFont(QFont('', 10))
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.yellow)
        pe.setColor(QPalette.Window, Qt.black)
        self.lb = QLabel()
        self.lb.setPalette(pe)
        self.lb.setFont(QFont('Arial', 20))
        self.lb.setAutoFillBackground(True)
        self.lb.setText('buffer')

        layout = QVBoxLayout()
        layout.addWidget(self.lb)
        self.setLayout(layout)
