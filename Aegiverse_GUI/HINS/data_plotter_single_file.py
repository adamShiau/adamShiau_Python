import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QComboBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QMessageBox)
from PySide6.QtCore import Qt

# 解決中文顯示問題
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 設定字體為微軟正黑體
plt.rcParams['axes.unicode_minus'] = False              # 解決負號 '-' 顯示為方塊的問題


class MvcPlotCanvas(FigureCanvas):
    """這是一個封裝了 matplotlib 圖表的畫布類別"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = None  # 用於 Y2 軸
        super().__init__(self.fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("感測器數據分析工具 (PySide6 + Matplotlib)")
        self.resize(1000, 700)

        self.df = None

        # 主佈局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- 左側控制面板 ---
        left_panel = QVBoxLayout()

        self.btn_load = QPushButton("1. 載入 .txt 檔案")
        self.btn_load.clicked.connect(self.load_file)
        left_panel.addWidget(self.btn_load)

        left_panel.addWidget(QLabel("2. 選擇 X 軸:"))
        self.combo_x = QComboBox()
        left_panel.addWidget(self.combo_x)

        left_panel.addWidget(QLabel("3. 選擇 Y 軸數據與 Y2 設定:"))
        self.table_y = QTableWidget()
        self.table_y.setColumnCount(3)
        self.table_y.setHorizontalHeaderLabels(["欄位名稱", "選取 (Y)", "放在 Y2"])
        self.table_y.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_panel.addWidget(self.table_y)

        self.btn_plot = QPushButton("開始繪圖")
        self.btn_plot.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 40px;")
        self.btn_plot.clicked.connect(self.plot_data)
        left_panel.addWidget(self.btn_plot)

        # --- 右側繪圖區域 ---
        right_panel = QVBoxLayout()
        self.canvas = MvcPlotCanvas(self, width=8, height=6)

        # 加上 Matplotlib 的工具列 (這就是你要的功能)
        self.toolbar = NavigationToolbar(self.canvas, self)

        right_panel.addWidget(self.toolbar)  # 工具列在上方
        right_panel.addWidget(self.canvas)  # 圖表在下方

        # 組合佈局
        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 3)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選取數據檔案", "", "Text Files (*.txt);;CSV Files (*.csv)")
        if file_path:
            try:
                # 讀取並清洗數據
                self.df = pd.read_csv(file_path)
                self.df.columns = self.df.columns.str.strip()

                # 更新 X 軸下拉選單
                self.combo_x.clear()
                self.combo_x.addItems(self.df.columns)

                # 更新 Y 軸表格
                self.table_y.setRowCount(len(self.df.columns))
                for i, col in enumerate(self.df.columns):
                    # 欄位名
                    self.table_y.setItem(i, 0, QTableWidgetItem(col))

                    # 選取 Y 軸的 Checkbox
                    check_y = QTableWidgetItem()
                    check_y.setCheckState(Qt.Unchecked)
                    self.table_y.setItem(i, 1, check_y)

                    # 選取 Y2 軸的 Checkbox
                    check_y2 = QTableWidgetItem()
                    check_y2.setCheckState(Qt.Unchecked)
                    self.table_y.setItem(i, 2, check_y2)

                QMessageBox.information(self, "成功", f"成功載入: {len(self.df)} 筆數據")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"讀取失敗: {str(e)}")

    def plot_data(self):
        if self.df is None:
            QMessageBox.warning(self, "警告", "請先載入數據！")
            return

        # 解決中文顯示問題：設定為微軟正黑體，並修正負號顯示
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False

        x_col = self.combo_x.currentText()

        # 找出哪些 Y 被勾選了，並確定其所屬的軸
        selected_y_info = []  # 儲存格式: (col_name, is_y2)

        for i in range(self.table_y.rowCount()):
            col_name = self.table_y.item(i, 0).text()

            # 獲取勾選狀態 (處理可能為 None 的情況)
            check_y_item = self.table_y.item(i, 1)
            check_y2_item = self.table_y.item(i, 2)

            is_checked_y = check_y_item and check_y_item.checkState() == Qt.Checked
            is_checked_y2 = check_y2_item and check_y2_item.checkState() == Qt.Checked

            # --- 核心邏輯優化 ---
            # 只要兩個 checkbox 有一個被勾選，該欄位就會被畫出來
            # 若勾選 Y2，優先放 Y2；若只勾選 Y，則放 Y1
            if is_checked_y2:
                selected_y_info.append((col_name, True))
            elif is_checked_y:
                selected_y_info.append((col_name, False))

        if not selected_y_info:
            QMessageBox.warning(self, "警告", "請至少選取一個 Y 或 Y2 數據！")
            return

        # 清除舊圖
        self.canvas.ax1.clear()
        if self.canvas.ax2:
            try:
                self.canvas.ax2.remove()
            except:
                pass
            self.canvas.ax2 = None

        # 開始繪製
        colors = plt.cm.tab10.colors
        c_idx = 0
        lines_labels = []

        for col, is_y2 in selected_y_info:
            # 決定圖例的標籤：移除原本的 (Y1) (Y2)，直接使用純欄位名
            label_name = f"{col}"

            if is_y2:
                # 如果還沒建立過 Y2 軸，則建立一個共用 X 軸的獨立 Y 軸
                if self.canvas.ax2 is None:
                    self.canvas.ax2 = self.canvas.ax1.twinx()

                ln = self.canvas.ax2.plot(self.df[x_col], self.df[col], label=label_name,
                                          color=colors[c_idx % 10], linestyle='--')
                lines_labels.append(ln[0])
            else:
                ln = self.canvas.ax1.plot(self.df[x_col], self.df[col], label=label_name,
                                          color=colors[c_idx % 10], linestyle='-')  # Y1 預設為實線
                lines_labels.append(ln[0])
            c_idx += 1

        # 設定 UI 標籤 (此處已支援中文)
        self.canvas.ax1.set_xlabel(x_col)
        self.canvas.ax1.set_ylabel("Y1 軸數據")

        if self.canvas.ax2:
            self.canvas.ax2.set_ylabel("Y2 軸數據")

        # 合併兩軸的圖例 (Legend)，統一顯示在右上方
        if lines_labels:
            labs = [l.get_label() for l in lines_labels]
            self.canvas.ax1.legend(lines_labels, labs, loc='upper right', framealpha=0.8)

        # 顯示網格與自動調整佈局
        self.canvas.ax1.grid(True, linestyle=':', alpha=0.6)

        # 確保繪圖內容不會超出邊框
        self.canvas.fig.tight_layout()

        # 強制刷新畫布顯示結果
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())