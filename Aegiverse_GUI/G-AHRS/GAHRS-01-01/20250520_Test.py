# from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QLabel, QWidget, QVBoxLayout
# from PySide6.QtCore import Qt
# import sys
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         # 垂直 Splitter
#         splitter = QSplitter(Qt.Vertical)
#
#         # 上下的元件
#         text_edit = QTextEdit("上方內容")
#         label = QLabel("下方內容")
#
#         # 加入 Splitter
#         splitter.addWidget(label)
#         splitter.addWidget(text_edit)
#
#
#         # 設定 central widget
#         container = QWidget()
#         layout = QVBoxLayout(container)
#         layout.addWidget(splitter)
#
#         self.setCentralWidget(container)
#         self.setWindowTitle("上下可伸縮的介面")
#         self.resize(400, 300)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())


# from PySide6.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QPushButton,
#     QVBoxLayout, QLabel, QScrollArea
# )
# from PySide6.QtCore import QPropertyAnimation, QSize, QEasingCurve
# import sys
#
# class CollapsibleSection(QWidget):
#     def __init__(self, title: str, content: QWidget):
#         super().__init__()
#         self.content = content
#         self.toggle_button = QPushButton(title)
#         self.toggle_button.setCheckable(True)
#         self.toggle_button.setChecked(False)
#
#         self.content_area = QScrollArea()
#         self.content_area.setWidgetResizable(True)
#         self.content_area.setMaximumHeight(0)  # 預設收合
#         self.content_area.setMinimumHeight(0)
#         self.content_area.setFrameShape(QScrollArea.NoFrame)
#         self.content_area.setWidget(self.content)
#
#         self.toggle_animation = QPropertyAnimation(self.content_area, b"maximumHeight")
#         self.toggle_animation.setDuration(200)
#         self.toggle_animation.setEasingCurve(QEasingCurve.OutCubic)
#
#         layout = QVBoxLayout(self)
#         layout.addWidget(self.toggle_button)
#         layout.addWidget(self.content_area)
#         layout.setContentsMargins(0, 0, 0, 0)
#
#         self.toggle_button.clicked.connect(self.toggle)
#
#     def toggle(self):
#         checked = self.toggle_button.isChecked()
#         content_height = self.content.sizeHint().height()
#         start = self.content_area.maximumHeight()
#         end = content_height if checked else 0
#
#         self.toggle_animation.stop()
#         self.toggle_animation.setStartValue(start)
#         self.toggle_animation.setEndValue(end)
#         self.toggle_animation.start()
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("可伸縮內容區塊")
#         self.resize(400, 300)
#
#         main_layout = QVBoxLayout()
#
#         # 建立要被伸縮的內容
#         content_widget = QWidget()
#         content_layout = QVBoxLayout(content_widget)
#         content_layout.addWidget(QLabel("這是展開後的內容"))
#         content_layout.addWidget(QLabel("你可以在這放更多元件"))
#
#         # 放入可收合區塊
#         collapsible = CollapsibleSection("點我展開/收合", content_widget)
#         main_layout.addWidget(collapsible)
#
#         container = QWidget()
#         container.setLayout(main_layout)
#         self.setCentralWidget(container)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

# from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton, \
#     QSplitter, QGridLayout, QTableWidget, QTableWidgetItem
# from PySide6.QtCore import Qt
# import sys
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.setWindowTitle("按鈕控制 QSplitter 展開收合")
#         self.resize(500, 400)
#
#         # 主容器和 layout
#         container = QWidget()
#         layout = QVBoxLayout()
#
#         # Splitter 垂直分割
#         self.splitter = QSplitter(Qt.Horizontal)
#
#         # 👉 將 QTextEdit 換成 QTableWidget
#         table = QTableWidget(3, 2)  # 3 列 2 欄
#         table.setHorizontalHeaderLabels(["名稱", "年齡"])
#         table.setItem(0, 0, QTableWidgetItem("Alice"))
#         table.setItem(0, 1, QTableWidgetItem("25"))
#         table.setItem(1, 0, QTableWidgetItem("Bob"))
#         table.setItem(1, 1, QTableWidgetItem("30"))
#         table.setItem(2, 0, QTableWidgetItem("Charlie"))
#         table.setItem(2, 1, QTableWidgetItem("28"))
#
#         # self.top_widget = QTextEdit("上方內容")
#         self.bottom_widget = QLabel("下方內容")
#
#         # 控制按鈕
#         toggle_btn = QPushButton("展開/收合下方區塊")
#         toggle_btn.clicked.connect(self.toggle_splitter)
#         lay = QGridLayout()
#         lay.addWidget(toggle_btn, 0, 0, 1, 1)
#         lay.addWidget(table, 1, 0, 5, 5)
#         logwed = QWidget()
#         logwed.setLayout(lay)
#
#         self.splitter.addWidget(self.bottom_widget)
#         self.splitter.addWidget(logwed)
#         # 記住展開與收合狀態
#         self.collapsed = False
#
#
#         # 加到 layout 裡
#         # layout.addWidget(toggle_btn)
#         layout.addWidget(self.splitter)
#
#         container.setLayout(layout)
#         self.setCentralWidget(container)
#
#         # 初始大小分配
#         self.splitter.setSizes([300, 100])
#
#     def toggle_splitter(self):
#         if not self.collapsed:
#             # 將下方 widget 高度設為 0，模擬收合
#             self.splitter.setSizes([1, 1])
#         else:
#             # 還原上下比例
#             self.splitter.setSizes([300, 100])
#         self.collapsed = not self.collapsed
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())


# from PySide6.QtWidgets import (
#     QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QSizePolicy
# )
# from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt
#
#
# class CollapsibleBox(QWidget):
#     def __init__(self, title=""):
#         super().__init__()
#         self.toggle_button = QPushButton(title)
#         self.toggle_button.setCheckable(True)
#         self.toggle_button.setChecked(False)
#         self.toggle_button.setStyleSheet("text-align: left; padding: 5px;")
#
#         self.content_area = QScrollArea()
#         self.content_area.setStyleSheet("border: none;")
#         self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
#         self.content_area.setMaximumHeight(0)
#         self.content_area.setMinimumHeight(0)
#         self.content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.content_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.content_area.setWidgetResizable(True)
#
#         self.content_widget = QWidget()
#         self.content_layout = QVBoxLayout(self.content_widget)
#         self.content_area.setWidget(self.content_widget)
#
#         self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
#         self.animation.setDuration(300)
#         self.animation.setEasingCurve(QEasingCurve.InOutCubic)
#
#         layout = QVBoxLayout(self)
#         layout.setSpacing(0)
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(self.toggle_button)
#         layout.addWidget(self.content_area)
#
#         self.toggle_button.toggled.connect(self.start_animation)
#
#     def start_animation(self, checked):
#         content_height = self.content_widget.sizeHint().height()
#         self.animation.stop()
#         self.animation.setStartValue(self.content_area.maximumHeight())
#         self.animation.setEndValue(content_height if checked else 0)
#         self.animation.start()
#
#     def setContentLayout(self, layout):
#         self.clearContent()
#         self.content_layout.addLayout(layout)
#
#     def clearContent(self):
#         while self.content_layout.count():
#             child = self.content_layout.takeAt(0)
#             if child.widget():
#                 child.widget().deleteLater()
#
#     def collapse(self):
#         if self.toggle_button.isChecked():
#             self.toggle_button.setChecked(False)
#
#     def expand(self):
#         if not self.toggle_button.isChecked():
#             self.toggle_button.setChecked(True)
#
#
# class Accordion(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.layout = QVBoxLayout(self)
#         self.layout.setSpacing(2)
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.boxes = []
#
#     def addSection(self, title, content_layout):
#         box = CollapsibleBox(title)
#         box.setContentLayout(content_layout)
#         box.toggle_button.clicked.connect(lambda: self._toggle_only(box))
#         self.layout.addWidget(box)
#         self.boxes.append(box)
#
#     def _toggle_only(self, active_box):
#         for box in self.boxes:
#             if box != active_box:
#                 box.collapse()
#
#
# # 使用範例
# if __name__ == "__main__":
#     app = QApplication([])
#
#     accordion = Accordion()
#
#     # 加入三個區塊
#     for name in ["設定", "帳號", "進階"]:
#         layout = QVBoxLayout()
#         layout.addWidget(QLabel(f"{name}內容 1"))
#         layout.addWidget(QLabel(f"{name}內容 2"))
#         accordion.addSection(name, layout)
#
#     window = QWidget()
#     win_layout = QVBoxLayout(window)
#     win_layout.addWidget(accordion)
#
#     window.setWindowTitle("Accordion 示範")
#     window.resize(400, 300)
#     window.show()
#
#     app.exec()



# import logging
#
# # 你的處理函數
# def handle_log_message(message):
#     print("👋 收到 log 訊息：", message)
#
# # 自訂一個 handler
# class FunctionHandler(logging.Handler):
#     def emit(self, record):
#         msg = self.format(record)
#         handle_log_message(msg)
#
# if __name__ == "__main__":
#     # 設定 logger
#     logger = logging.getLogger("my_logger")
#     logger.setLevel(logging.INFO)
#
#     # 加上自訂的 handler
#     custom_handler = FunctionHandler()
#     formatter = logging.Formatter('%(levelname)s - %(message)s')
#     custom_handler.setFormatter(formatter)
#     logger.addHandler(custom_handler)
#
#     # 測試
#     logger.info("這是一個 logger 的訊息")


import logging

# 自定義過濾器，只處理 INFO 和 ERROR 級別的日誌
class InfoAndErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in (logging.INFO, logging.ERROR)

# 創建 logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 創建處理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 設置處理器的級別為 DEBUG

# 添加自定義過濾器
console_handler.addFilter(InfoAndErrorFilter())

# 設置日誌格式
formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(formatter)

# 將處理器添加到 logger
logger.addHandler(console_handler)

# 測試日誌
logger.debug("This is a DEBUG message.")  # 會被過濾掉
logger.info("This is an INFO message.")   # 會顯示
logger.error("This is an ERROR message.") # 會顯示
logger.warning("This is a WARNING message.")  # 會被過濾掉

