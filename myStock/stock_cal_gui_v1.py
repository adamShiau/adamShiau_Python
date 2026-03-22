import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QLineEdit, QFileDialog, QTableWidget,
                               QTableWidgetItem, QHeaderView, QComboBox, QMessageBox)
from PySide6.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False


class MyStockSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ETF 績效報告")
        self.setGeometry(100, 100, 1550, 900)
        self.df_price = None
        self.df_div = None
        self.ax = None
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        ctrl_layout = QHBoxLayout()
        self.btn_price = QPushButton("1. 讀取股價")
        self.btn_div = QPushButton("2. 讀取配息")
        self.btn_plot = QPushButton("繪製走勢")
        self.btn_plot.setStyleSheet("background-color: #FF9800; color: white;")

        self.txt_start = QLineEdit("")
        self.txt_end = QLineEdit("")
        self.combo_freq = QComboBox()
        self.combo_freq.addItems(["每月", "每週"])
        self.txt_amount = QLineEdit("10000")

        for w in [self.btn_price, self.btn_div, self.btn_plot, QLabel(" | 區間:"),
                  self.txt_start, QLabel("-"), self.txt_end, QLabel("金額:"),
                  self.txt_amount, self.combo_freq]:
            ctrl_layout.addWidget(w)

        self.btn_run = QPushButton("執行計算")
        self.btn_run.setStyleSheet("background-color: #0078D7; color: white; font-weight: bold;")
        ctrl_layout.addWidget(self.btn_run)
        main_layout.addLayout(ctrl_layout)

        content_layout = QHBoxLayout()

        chart_widget = QWidget()
        chart_vbox = QVBoxLayout(chart_widget)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        chart_vbox.addWidget(self.toolbar)
        chart_vbox.addWidget(self.canvas)
        content_layout.addWidget(chart_widget, stretch=6)

        right_panel = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["日期", "事件", "成交價", "配息金額", "變動股數", "累積本金", "累積股數", "平均成本"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 100)
        right_panel.addWidget(self.table, stretch=7)

        self.lbl_report = QLabel("【分析報告】等待計算...")
        self.lbl_report.setStyleSheet(
            "font-size: 17px; line-height: 150%; border: 2px solid #0078D7; padding: 15px; background-color: #f0f8ff;")
        self.lbl_report.setWordWrap(True)
        right_panel.addWidget(self.lbl_report, stretch=3)

        content_layout.addLayout(right_panel, stretch=4)
        main_layout.addLayout(content_layout)

        self.btn_price.clicked.connect(self.load_price)
        self.btn_div.clicked.connect(self.load_div)
        self.btn_plot.clicked.connect(self.draw_plot_action)
        self.btn_run.clicked.connect(self.run_simulation_with_visual_feedback)

    def load_price(self):
        path, _ = QFileDialog.getOpenFileName(self, "讀取股價")
        if path:
            df = None
            for enc in ['utf-8-sig', 'utf-8', 'big5', 'cp950']:
                try:
                    df = pd.read_csv(path, encoding=enc)
                    break
                except:
                    continue
            if df is not None:
                try:
                    self.df_price = df
                    self.df_price['Date'] = pd.to_datetime(self.df_price['Date'])
                    self.df_price.sort_values('Date', inplace=True)
                    min_d = self.df_price['Date'].min().strftime('%Y-%m-%d')
                    max_d = self.df_price['Date'].max().strftime('%Y-%m-%d')
                    self.txt_start.setText(min_d)
                    self.txt_end.setText(max_d)
                    QMessageBox.information(self, "成功", f"股價載入成功\n範圍: {min_d} ~ {max_d}")
                except Exception as e:
                    QMessageBox.critical(self, "錯誤", f"格式解析失敗: {e}")
            else:
                QMessageBox.critical(self, "錯誤", "無法讀取 CSV 檔案，請檢查編碼")

    def load_div(self):
        path, _ = QFileDialog.getOpenFileName(self, "讀取配息")
        if not path: return
        df = None
        for enc in ['big5', 'utf-8-sig', 'utf-8', 'cp950']:
            try:
                df = pd.read_csv(path, encoding=enc, header=None)
                break
            except:
                continue
        if df is not None:
            recs, year = [], None
            for _, row in df.iterrows():
                if len(row) < 6: continue
                v0, v1 = str(row[0]).strip(), str(row[1]).strip()
                if v0.isdigit() and len(v0) == 4: year = v0
                if '/' in v1 and year:
                    try:
                        amt = float(str(row[5]).strip().replace(',', ''))
                        recs.append({'D': pd.to_datetime(f"{year}/{v1}"), 'V': amt})
                    except:
                        continue
            self.df_div = pd.DataFrame(recs).sort_values('D')
            QMessageBox.information(self, "成功", "配息載入完成")

    def draw_plot_action(self):
        if self.df_price is None:
            QMessageBox.warning(self, "提示", "請先讀取股價檔案")
            return
        try:
            s = pd.to_datetime(self.txt_start.text())
            e = pd.to_datetime(self.txt_end.text())
            self._update_chart(s, e)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"繪圖失敗: {e}")

    def _update_chart(self, s, e):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        mask = (self.df_price['Date'] >= s) & (self.df_price['Date'] <= e)
        sub = self.df_price[mask]
        if sub.empty: return

        self.ax.plot(sub['Date'], sub['Close'], color='#1f77b4', label='00919 歷史趨勢', linewidth=1.5)

        if self.df_div is not None:
            dm = (self.df_div['D'] >= s) & (self.df_div['D'] <= e)
            for d in self.df_div[dm]['D']:
                self.ax.axvline(x=d, color='red', linestyle='--', alpha=0.3)

        min_csv_d = self.df_price['Date'].min().strftime('%Y-%m-%d')
        max_csv_d = self.df_price['Date'].max().strftime('%Y-%m-%d')
        self.ax.set_title(f"00919 歷史趨勢 ({min_csv_d} ~ {max_csv_d})")

        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.fig.autofmt_xdate()
        self.canvas.draw()

    def run_simulation_with_visual_feedback(self):
        self.run_simulation_action()
        if self.ax and self.df_price is not None:
            try:
                s_calc = pd.to_datetime(self.txt_start.text())
                e_calc = pd.to_datetime(self.txt_end.text())
                self._highlight_calc_range(s_calc, e_calc)
            except:
                pass

    def _highlight_calc_range(self, s_calc, e_calc):
        for line in self.ax.lines:
            if line.get_label() == '計算區間 (綠色)':
                line.remove()

        calc_mask = (self.df_price['Date'] >= s_calc) & (self.df_price['Date'] <= e_calc)
        calc_sub = self.df_price[calc_mask]

        if not calc_sub.empty:
            self.ax.plot(calc_sub['Date'], calc_sub['Close'], color='#33FF33', label='計算區間 (綠色)', linewidth=2.0)
            self.canvas.draw_idle()

    def run_simulation_action(self):
        if self.df_price is None or self.df_div is None:
            QMessageBox.warning(self, "提示", "請確認股價與配息檔案皆已載入")
            return
        try:
            s_dt = pd.to_datetime(self.txt_start.text())
            e_dt = pd.to_datetime(self.txt_end.text())
            base_amt = float(self.txt_amount.text())
            freq = self.combo_freq.currentText()

            inv, sh, total_div = 0, 0, 0
            recs = []
            d_map = {d.date(): v for d, v in zip(self.df_div['D'], self.df_div['V'])}

            curr, next_p = s_dt, s_dt
            while curr <= e_dt:
                if curr.date() in d_map and sh > 0:
                    c = sh * d_map[curr.date()]
                    total_div += c
                    recs.append([curr.strftime('%Y-%m-%d'), "配息", "-", f"{c:,.0f}", "0", inv, sh])
                if curr == next_p:
                    p_row = self.df_price[self.df_price['Date'] >= curr].head(1)
                    if not p_row.empty:
                        p = p_row['Close'].values[0]
                        sh += base_amt / p
                        inv += base_amt
                        recs.append(
                            [pd.to_datetime(p_row['Date'].values[0]).strftime('%Y-%m-%d'), "買入", f"{p:.2f}", "0",
                             f"{(base_amt / p):.2f}", inv, sh])
                    next_p += pd.DateOffset(months=1) if freq == "每月" else timedelta(weeks=1)
                curr += timedelta(days=1)

            self.table.setRowCount(0)
            for r in recs:
                idx = self.table.rowCount()
                self.table.insertRow(idx)
                avg = r[5] / r[6] if r[6] > 0 else 0
                vals = [r[0], r[1], r[2], r[3], r[4], f"{r[5]:,.0f}", f"{r[6]:.2f}", f"{avg:.2f}"]
                for c, v in enumerate(vals):
                    it = QTableWidgetItem(str(v))
                    it.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(idx, c, it)

            final_p = self.df_price[self.df_price['Date'] <= e_dt].tail(1)['Close'].values[0]
            curr_stock_val = sh * final_p
            total_assets = curr_stock_val + total_div
            delta_days = (e_dt - s_dt).days
            years = max(delta_days / 365.25, 0.01)
            cagr = ((total_assets / inv) ** (1 / years) - 1) * 100 if inv > 0 else 0
            avg_cost = inv / sh if sh > 0 else 0  # 計算平均成本

            self.lbl_report.setText(
                f"<b>【分析績效報告】</b><br>"
                f"● 總投資時間：<b>{delta_days} 天 (約 {years:.2f} 年)</b><br>"
                f"● 目前持有總股數：<b>{sh:,.2f} 股</b><br>"
                f"● 平均持有成本：<b>${avg_cost:.2f}</b><br>"
                f"● 累積投入本金：${inv:,.0f}<br>"
                f"● 累積領取配息：${total_div:,.0f}<br>"
                f"● 期末持股市值：${curr_stock_val:,.0f}<br>"
                f"● 總結算資產：<b>${total_assets:,.0f}</b> ({((total_assets - inv) / inv * 100):.2f}%)<br>"
                f"● <b>等效年化報酬率：<span style='color:red; font-size:22px;'>{cagr:.2f}%</span></b>"
            )
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"計算失敗: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyStockSimulator()
    ex.show()
    sys.exit(app.exec())