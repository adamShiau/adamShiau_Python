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
        self.versionTable.setRowCount(4)
        self.versionTable.setColumnCount(2)


    def ViewVersion(self, DeviceVer, GUIVer):
        """
        DeviceVer is a merged comma-separated string returned by MCU, e.g.
            "HINS_MCU_V2.0,HINS_TOP_V1,HINS_CPU_V1_0"
        Display as separate rows:
            NIOS2 VERSION, FPGA VERSION, MCU VERSION, GUI VERSION
        Parse by token prefix; if prefix not found, fall back to order (NIOS2, FPGA, MCU).
        """
        dev = (DeviceVer or "").strip()
        tokens = [t.strip() for t in dev.split(",") if t.strip()]

        nios2_ver = ""
        fpga_ver = ""
        mcu_ver = ""

        # Prefix-based parsing (robust to ordering)
        for t in tokens:
            up = t.upper()
            if up.startswith("HINS_CPU_") or "NIOS" in up or ("CPU" in up and "MCU" not in up):
                nios2_ver = t
            elif up.startswith("HINS_TOP_") or "TOP" in up or "FPGA" in up:
                fpga_ver = t
            elif up.startswith("HINS_MCU_") or "MCU" in up:
                mcu_ver = t

        # Fallback to declared order: NIOS2, FPGA, MCU
        if (nios2_ver == "" or fpga_ver == "" or mcu_ver == "") and len(tokens) >= 3:
            if nios2_ver == "":
                nios2_ver = tokens[0]
            if fpga_ver == "":
                fpga_ver = tokens[1]
            if mcu_ver == "":
                mcu_ver = tokens[2]

        labels = ["NIOS2 VERSION", "FPGA VERSION", "MCU VERSION", "GUI VERSION"]
        values = [nios2_ver, fpga_ver, mcu_ver, GUIVer]

        self.versionTable.clear()
        self.versionTable.setRowCount(4)
        self.versionTable.setColumnCount(2)

        for r, (lab, val) in enumerate(zip(labels, values)):
            self.versionTable.setItem(r, 0, QTableWidgetItem(lab))
            self.versionTable.setItem(r, 1, QTableWidgetItem(str(val)))

        # Hide headers (labels are in col 0)
        self.versionTable.horizontalHeader().setVisible(False)
        self.versionTable.verticalHeader().setVisible(False)

        # Column sizing
        self.versionTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.versionTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.versionTable.resizeRowsToContents()
        self.versionTable.resizeColumnsToContents()

        layout = QVBoxLayout()
        layout.addWidget(self.versionTable)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ver = VersionTable()
    ver.ViewVersion("MCU & FOG")
    ver.show()
    app.exec()