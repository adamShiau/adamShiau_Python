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
        DeviceVer 固定順序: MCU, TOP(FPGA), CPU(NIOS2), JIC
        例如: "HINS_MCU_V3.1_M,HINS_TOP_V1,HINS_CPU_V1_0,HINS_2026-01-15"
        """
        dev = (DeviceVer or "").strip()
        tokens = [t.strip() for t in dev.split(",") if t.strip()]

        # 初始化預設值，避免 tokens 數量不足時報錯
        mcu_ver = tokens[0] if len(tokens) > 0 else ""
        fpga_ver = tokens[1] if len(tokens) > 1 else ""
        nios2_ver = tokens[2] if len(tokens) > 2 else ""
        jic_ver = tokens[3] if len(tokens) > 3 else ""

        # 定義顯示標籤與對應數值
        labels = [
            "NIOS2 VERSION",
            "FPGA VERSION",
            "MCU VERSION",
            "JIC VERSION",  # 新增項目
            "GUI VERSION"
        ]
        values = [nios2_ver, fpga_ver, mcu_ver, jic_ver, GUIVer]

        # 更新表格設定
        self.versionTable.clear()
        self.versionTable.setRowCount(len(labels))  # 動態設定為 5 列
        self.versionTable.setColumnCount(2)

        for r, (lab, val) in enumerate(zip(labels, values)):
            self.versionTable.setItem(r, 0, QTableWidgetItem(lab))
            self.versionTable.setItem(r, 1, QTableWidgetItem(str(val)))

        # 介面調整
        self.versionTable.horizontalHeader().setVisible(False)
        self.versionTable.verticalHeader().setVisible(False)
        self.versionTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.versionTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.versionTable.resizeRowsToContents()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ver = VersionTable()
    ver.ViewVersion("HINS_MCU_V3.1_M,HINS_TOP_V1,HINS_CPU_V1_0,HINS_2026-01-15", "V1.0.0")
    ver.show()
    app.exec()