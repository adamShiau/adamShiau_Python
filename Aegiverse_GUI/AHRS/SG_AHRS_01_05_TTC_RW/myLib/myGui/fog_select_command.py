""" ####### log stuff creation, always on the top ########  """
import builtins
import os
from myLib.logProcess import logProcess

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__

ExternalName_log = __name__
if os.getenv('verNum') == str(True) :
    ExternalName_log = "chooseCMD_logger"

logProcess.fileStartedInfo(logger_name, ExternalName_log)
""" ####### end of log stuff creation ########  """
import sys

from PySide6.QtWidgets import QGroupBox, QLabel, QComboBox, QListWidget, QPushButton, QGridLayout, QApplication


class Select_comMD(QGroupBox):
    def __init__(self, act):
        super(Select_comMD, self).__init__()
        self.resize(350, 250)
        self.setWindowTitle("fog select command")
        self.__act = act
        self.CMDwid()
        self.linkfunc()
        self.winDefault()

    def CMDwid(self):
        type_lb = QLabel("Command Type：")
        self.select_type = QComboBox()
        cmd_lb = QLabel("Select Command：")
        self.selectCMD = QListWidget()
        self.submit = QPushButton("Submit")
        self.confirm = QPushButton("OK")

        # function的部分
        self.typeItem()
        self.CMDItem()

        layout = QGridLayout()
        layout.addWidget(type_lb, 0, 0, 1, 1)
        layout.addWidget(self.select_type, 0, 1, 1, 6)
        layout.addWidget(cmd_lb, 1, 0, 1, 1)
        layout.addWidget(self.selectCMD, 1, 1, 5, 6)
        layout.addWidget(self.confirm, 6, 5, 1, 1)
        layout.addWidget(self.submit, 6, 6, 1, 1)
        self.setLayout(layout)

    def linkfunc(self):
        self.select_type.currentIndexChanged.connect(self.CMDItem)
        self.selectCMD.currentItemChanged.connect(self.selectCMDChange)
        self.submit.clicked.connect(self.submitCMD)
        self.confirm.clicked.connect(self.close)

    def typeItem(self):
        type_content = ["start", "stop"]
        self.select_type.addItems(type_content)

    def CMDItem(self):
        if self.select_type.currentText() == "start":
            self.selectCMD.clear()
            self.selectCMD.addItem("02, 02, 02")
            self.selectCMD.addItem("02, 03, 02")
        if self.select_type.currentText() == "stop":
            self.selectCMD.clear()
            self.selectCMD.addItem("02, 04, 02")

        self.winDefault()

    def winDefault(self):
        if self.selectCMD.count() >= 1:
            # 預設選中狀態
            self.selectCMD.item(0).setSelected(True)
        self.submit.setDisabled(True)

    def selectCMDChange(self):
        self.submit.setDisabled(False)

    def submitCMD(self):
        self.submit.setDisabled(True)
        self.__act.selectCMD(self.select_type.currentText(), self.selectCMD.currentItem().text())



if __name__ == "__main__":
    app = QApplication([])
    act = None
    win = Select_comMD(act)
    win.show()
    app.exec()