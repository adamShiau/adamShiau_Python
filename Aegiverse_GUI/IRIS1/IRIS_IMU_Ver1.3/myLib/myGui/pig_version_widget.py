# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import sys



if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

from PySide6.QtWidgets import QGroupBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView, QApplication


class VersionTable(QGroupBox):
    def __init__(self):
        super(VersionTable, self).__init__()
        self.setWindowTitle("Version")
        self.resize(450, 150)
        self.versionTable = QTableWidget(self)
        self.versionTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.versionTable.setRowCount(2)
        self.versionTable.setColumnCount(2)


    def ViewVersion(self, DeviceVer, GUIVer):
        self.versionTable.setItem(0, 0, QTableWidgetItem("MCU & FPGA Version"))
        self.versionTable.setItem(0, 1, QTableWidgetItem("GUI Version"))
        self.versionTable.setItem(1, 0, QTableWidgetItem(DeviceVer))
        self.versionTable.setItem(1, 1, QTableWidgetItem(GUIVer))
        # 列寬自動分配
        self.versionTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.versionTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.versionTable.resizeRowsToContents()
        self.versionTable.resizeColumnsToContents()

        # #自定義寬
        # self.versionTable.setColumnWidth(0, 250)
        # self.versionTable.setColumnWidth(1, 150)

        layout = QVBoxLayout()
        layout.addWidget(self.versionTable)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ver = VersionTable()
    ver.ViewVersion("MCU & FOG")
    ver.show()
    app.exec()