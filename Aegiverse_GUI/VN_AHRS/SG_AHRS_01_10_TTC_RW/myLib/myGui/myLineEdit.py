# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import os
import sys
from myLib.logProcess import logProcess

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__

ExternalName_log = __name__
if os.getenv('verNum') == str(True) :
    ExternalName_log = "Ledit_logger"

logProcess.fileStartedInfo(logger_name, ExternalName_log)
# logger = logging.getLogger(logger_name + '.' + ExternalName_log)
# logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class dataSaveBlock(QGroupBox):
    def __init__(self, name=""):
        super(dataSaveBlock, self).__init__()
        self.setTitle(name)
        self.setFont(QFont('Arial', 10))
        self.rb = QRadioButton("save")
        self.le_filename = QLineEdit("enter_file_name")
        # self.le_filename.editingFinished.connect(lambda: self.le_text_connect(self.le_filename))
        self.le_ext = QLineEdit(".txt")
        self.le_ext.setFixedWidth(50)
        self.rb.setChecked(False)

        layout = QGridLayout()
        layout.addWidget(self.rb, 0, 0, 1, 1)
        layout.addWidget(self.le_filename, 0, 1, 1, 1)
        layout.addWidget(self.le_ext, 0, 4, 1, 1)
        self.setLayout(layout)

class dataSaveBlock_Rcs(QGroupBox):
    def __init__(self, name=""):
        super().__init__()
        self.setTitle(name)
        self.setFont(QFont('Arial', 10))

        self.rb = QRadioButton("Save")          # 如果真的要用 Radio，表示「選擇某種存檔模式」
        self.rcs_cb = QCheckBox("Rcs?")         # ← 改成 CheckBox，彼此不互斥

        self.le_filename = QLineEdit("enter_file_name")
        self.le_ext = QLineEdit(".txt"); self.le_ext.setFixedWidth(50)

        self.rb.setChecked(False)
        self.rcs_cb.setChecked(False)

        layout = QGridLayout()
        layout.addWidget(self.rb,        0, 0, 1, 1)
        layout.addWidget(self.rcs_cb,    0, 1, 1, 1)
        layout.addWidget(self.le_filename,0, 2, 1, 1)
        layout.addWidget(self.le_ext,    0, 3, 1, 1)
        self.setLayout(layout)


class dataSaveBlock_noExt(QGroupBox):
    def __init__(self, title="", path='.'):
        super(dataSaveBlock_noExt, self).__init__()
        self.setTitle(title)
        self.setFont(QFont('Arial', 10))
        self.rb = QRadioButton("save")
        self.le_filename = QLineEdit(path)
        self.le_filename.setFixedWidth(410)
        self.rb.setChecked(False)

        layout = QGridLayout()
        layout.addWidget(self.rb, 0, 0, 1, 1)
        layout.addWidget(self.le_filename, 0, 1, 1, 1)
        # layout.addWidget(self.le_ext, 0, 4, 1, 1)
        self.setLayout(layout)


class btnLineEditBlock(QGroupBox):
    def __init__(self, title='', bt_name='', le_name=''):
        super(btnLineEditBlock, self).__init__()
        self.setTitle(title)
        self.setFixedWidth(150)
        self.setFont(QFont('', 10))
        self.bt = QPushButton(bt_name)
        self.le = QLineEdit(le_name)
        self.bt.setFixedWidth(100)
        self.le.setFixedWidth(130)
        layout = QVBoxLayout()
        layout.addWidget(self.bt)
        layout.addWidget(self.le)
        self.setLayout(layout)

class compensateBlock(QGroupBox):
    def __init__(self, title='', bt_name='', lb_name=''):
        super(compensateBlock, self).__init__()
        self.setTitle(title)
        self.setFont(QFont('Arial', 10))
        self.bt = QPushButton(bt_name)
        self.lb = QLabel(lb_name)
        self.le = QLineEdit("120")
        validate = QIntValidator()
        self.le.setValidator(validate)
        self.bt.setEnabled(False)
        layout = QHBoxLayout()
        layout.addWidget(self.lb)
        layout.addWidget(self.le)
        layout.addWidget(self.bt)
        self.setLayout(layout)


class lineEditBlock(QGroupBox):
    def __init__(self, name="", le_name=""):
        super(lineEditBlock, self).__init__()
        self.setTitle(name)
        self.setFont(QFont('Arial', 10))
        self.le_filename = QLineEdit(le_name)

        layout = QGridLayout()
        layout.addWidget(self.le_filename, 0, 1, 1, 1)
        self.setLayout(layout)

    def inst(self):
        return self


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # w = btnLineEditBlock('read file', 'read', 'abc.txt')
    w = lineEditBlock('parameter configuration').inst()
    w.show()
    app.exec_()
