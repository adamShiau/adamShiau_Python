import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QTableWidget, QApplication, QTableWidgetItem, QHeaderView


class pig_events_view(QTableWidget):
    def __init__(self):
        super(pig_events_view, self).__init__()
        self.setWindowTitle("Events View")
        self.resize(800, 450)
        self.setRowCount(1)
        self.setColumnCount(3)
        # self.setWordWrap(True)
        # self.resizeRowsToContents()
        self.verticalHeader().setMinimumSectionSize(35)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 設定table的外觀
        font = QFont("Arial", 12)
        font.setBold(True)
        # 設定欄位，文字置中
        time_table = QTableWidgetItem("Time")
        time_table.setTextAlignment(Qt.AlignCenter)
        time_table.setFont(font)
        level_table = QTableWidgetItem("Level")
        level_table.setTextAlignment(Qt.AlignCenter)
        level_table.setFont(font)
        mes_table = QTableWidgetItem("Message")
        mes_table.setTextAlignment(Qt.AlignCenter)
        mes_table.setFont(font)
        self.setItem(0, 0, time_table)
        self.setItem(0, 1, level_table)
        self.setItem(0, 2, mes_table)

        # 設定table無法被修改
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        # 將原本會看到的欄位與列表編號隱藏
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        # 調整整個table的寬度
        self.setColumnWidth(0, 180)
        self.setColumnWidth(1, 120)
        self.setColumnWidth(2, 500)

        # self.setItem(1, 0, QTableWidgetItem("2025/05/21"))
        # self.setItem(1, 1, QTableWidgetItem("ERROR"))
        # mesInfo_table = QTableWidgetItem("DeprecationWarning: 'exec_' will be removed in the future. Use 'exec' instead.\
        #  app.exec_()")
        # self.setItem(1, 2, mesInfo_table)


    def split_log_info(self, mes):
        # print("分割...")
        splitLog = mes.split(" ； ")
        self.create_info_view(splitLog[0], splitLog[1], splitLog[2])
        # print(splitLog[2])
        # print("完整log資訊 -- "+str(mes))

    # 將接收到的資料放置table中顯示
    def create_info_view(self, time, level, message):
        val_list = [time, level, message]

        row_num = self.rowCount()
        self.insertRow(row_num)
        for i, value in enumerate(val_list):
            item = QTableWidgetItem(value)
            if "ERROR" in val_list[1]:
                item.setBackground(QColor("#fc4e4e"))
            if "WARNING" in val_list[1]:
                item.setBackground(QColor("#fcca42"))
            self.setItem(row_num, i, item)
            # print("串接到顯示log的table中。")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = pig_events_view()
    main.show()
    app.exec_()