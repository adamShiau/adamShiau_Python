# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import sys

from PyQt5.QtWidgets import QGroupBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QApplication

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """


class VersionTable(QGroupBox):
    def __init__(self):
        super(VersionTable, self).__init__()
        self.setWindowTitle('Version')
        self.resize(400, 190)
        self.FPGA_version = ""
        self.MCU_version = ""
        self.versionTable = QTableWidget(self)
        self.versionTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.versionTable.setRowCount(3)
        self.versionTable.setColumnCount(2)
        # UsingData = [[, ], [, ], [, ], [, ]]
        # versionTable.setItem(0, 0, QTableWidgetItem("System Name"))
        # versionTable.setItem(0, 1, QTableWidgetItem("Version"))


    def createTable(self, Vtext, GUIVers):
        Vtext_split = Vtext.split(",")
        self.FPGA_version = Vtext_split[0]
        self.MCU_version = Vtext_split[1].replace("\n", "")
        self.versionTable.setItem(0, 0, QTableWidgetItem("MCU"))
        self.versionTable.setItem(0, 1, QTableWidgetItem(self.FPGA_version))
        self.versionTable.setItem(1, 0, QTableWidgetItem("FPGA"))
        self.versionTable.setItem(1, 1, QTableWidgetItem(self.MCU_version))
        self.versionTable.setItem(2, 0, QTableWidgetItem("GUI"))
        self.versionTable.setItem(2, 1, QTableWidgetItem(GUIVers))
        self.versionTable.resizeRowsToContents()
        self.versionTable.resizeColumnsToContents()

        layout = QVBoxLayout()
        layout.addWidget(self.versionTable)
        self.setLayout(layout)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = VersionTable()
    win.show()
    sys.exit(app.exec_())