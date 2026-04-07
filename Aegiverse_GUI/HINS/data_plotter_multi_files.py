import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QFileDialog, QComboBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QMessageBox)
from PySide6.QtCore import Qt


class MvcPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = None
        super().__init__(self.fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多檔案感測器數據分析工具")
        self.resize(1200, 800)

        # 儲存多個檔案的數據 { "檔名.txt": dataframe }
        self.data_dict = {}

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- 左側控制面板 ---
        left_panel = QVBoxLayout()

        self.btn_load = QPushButton("1. 選取多個 .txt 檔案 (按住 Ctrl 可複選)")
        self.btn_load.clicked.connect(self.load_files)
        left_panel.addWidget(self.btn_load)

        self.lbl_info = QLabel("已載入檔案數: 0")
        left_panel.addWidget(self.lbl_info)

        left_panel.addWidget(QLabel("2. 選擇 X 軸 (所有檔案共用):"))
        self.combo_x = QComboBox()
        left_panel.addWidget(self.combo_x)

        left_panel.addWidget(QLabel("3. 選擇 Y 軸數據與 Y2 設定:"))
        self.table_y = QTableWidget()
        self.table_y.setColumnCount(3)
        self.table_y.setHorizontalHeaderLabels(["欄位名稱", "選取 (Y)", "放在 Y2"])
        self.table_y.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_panel.addWidget(self.table_y)

        self.btn_plot = QPushButton("開始繪圖 (所有檔案)")
        self.btn_plot.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 40px;")
        self.btn_plot.clicked.connect(self.plot_data)
        left_panel.addWidget(self.btn_plot)

        # --- 右側繪圖區域 ---
        right_panel = QVBoxLayout()
        self.canvas = MvcPlotCanvas(self, width=8, height=6)
        self.toolbar = NavigationToolbar(self.canvas, self)
        right_panel.addWidget(self.toolbar)
        right_panel.addWidget(self.canvas)

        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 3)

    def load_files(self):
        # 使用 getOpenFileNames 支援多選
        file_paths, _ = QFileDialog.getOpenFileNames(self, "選取一個或多個數據檔案", "",
                                                     "Text Files (*.txt);;CSV Files (*.csv)")

        if file_paths:
            self.data_dict = {}  # 清除舊數據
            common_columns = None

            try:
                for path in file_paths:
                    filename = os.path.basename(path)
                    df = pd.read_csv(path)
                    df.columns = df.columns.str.strip()
                    self.data_dict[filename] = df

                    # 取出所有檔案共同擁有的欄位名稱
                    if common_columns is None:
                        common_columns = set(df.columns)
                    else:
                        common_columns = common_columns.intersection(set(df.columns))

                if not common_columns:
                    QMessageBox.warning(self, "錯誤", "選取的檔案之間沒有共同的欄位名稱！")
                    return

                # 更新 UI
                self.lbl_info.setText(f"已載入檔案數: {len(self.data_dict)}")

                sorted_cols = sorted(list(common_columns))
                self.combo_x.clear()
                self.combo_x.addItems(sorted_cols)

                self.table_y.setRowCount(len(sorted_cols))
                for i, col in enumerate(sorted_cols):
                    self.table_y.setItem(i, 0, QTableWidgetItem(col))

                    check_y = QTableWidgetItem()
                    check_y.setCheckState(Qt.Unchecked)
                    self.table_y.setItem(i, 1, check_y)

                    check_y2 = QTableWidgetItem()
                    check_y2.setCheckState(Qt.Unchecked)
                    self.table_y.setItem(i, 2, check_y2)

                QMessageBox.information(self, "成功", f"成功載入 {len(self.data_dict)} 個檔案")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"讀取失敗: {str(e)}")

    def plot_data(self):
        if not self.data_dict:
            QMessageBox.warning(self, "警告", "請先載入數據！")
            return

        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False

        x_col = self.combo_x.currentText()

        # 找出哪些欄位被勾選
        selected_fields = []
        for i in range(self.table_y.rowCount()):
            col_name = self.table_y.item(i, 0).text()
            is_checked_y = self.table_y.item(i, 1).checkState() == Qt.Checked
            is_checked_y2 = self.table_y.item(i, 2).checkState() == Qt.Checked

            if is_checked_y2:
                selected_fields.append((col_name, True))
            elif is_checked_y:
                selected_fields.append((col_name, False))

        if not selected_fields:
            QMessageBox.warning(self, "警告", "請至少選取一個欄位！")
            return

        # 清除舊圖
        self.canvas.ax1.clear()
        if self.canvas.ax2:
            try:
                self.canvas.ax2.remove()
            except:
                pass
            self.canvas.ax2 = None

        # 開始繪製 (遍歷所有檔案 x 遍歷選取欄位)
        colors = plt.cm.get_cmap('tab10', 10)
        c_idx = 0
        lines_labels = []

        for filename, df in self.data_dict.items():
            # 移除副檔名以便顯示在 legend
            short_name = os.path.splitext(filename)[0]

            for col, is_y2 in selected_fields:
                # Legend 格式：[檔案名] 欄位名
                label_name = f"[{short_name}] {col}"

                if is_y2:
                    if self.canvas.ax2 is None:
                        self.canvas.ax2 = self.canvas.ax1.twinx()
                    ln = self.canvas.ax2.plot(df[x_col], df[col], label=label_name,
                                              color=colors(c_idx % 10), linestyle='--')
                    lines_labels.append(ln[0])
                else:
                    ln = self.canvas.ax1.plot(df[x_col], df[df.columns.intersection([col])[0]], label=label_name,
                                              color=colors(c_idx % 10), linestyle='-')
                    lines_labels.append(ln[0])
                c_idx += 1

        # 設定標籤
        self.canvas.ax1.set_xlabel(x_col)
        self.canvas.ax1.set_ylabel("Y1 軸數據")
        if self.canvas.ax2:
            self.canvas.ax2.set_ylabel("Y2 軸數據")

        # 圖例處理
        if lines_labels:
            labs = [l.get_label() for l in lines_labels]
            # 如果檔案很多，圖例會很長，將圖例放在圖外或縮小字體
            self.canvas.ax1.legend(lines_labels, labs, loc='upper left',
                                   bbox_to_anchor=(1.05, 1), borderaxespad=0., fontsize='small')

        self.canvas.ax1.grid(True, linestyle=':', alpha=0.6)

        # 因為圖例在外面，手動調整邊距
        self.canvas.fig.subplots_adjust(right=0.75)
        # self.canvas.fig.tight_layout() # tight_layout 有時會與 legend 外置衝突，改用 adjust

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())