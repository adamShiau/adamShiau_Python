from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QVBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QTimer
import sys

class FloatingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 👉 移除標題列（純淨方框）
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedSize(300, 150)

        # 🔳 外層 layout：讓 QFrame 置中顯示
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 🔲 QFrame：視覺上的方框
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #0078d7;
                border-radius: 12px;
            }
        """)
        layout.addWidget(self.frame)

        # 🧾 QLabel 放進 QFrame 中
        inner_layout = QVBoxLayout(self.frame)
        self.label = QLabel("這是一段訊息")
        self.label.setAlignment(Qt.AlignCenter)
        inner_layout.addWidget(self.label)

    def show_message(self, text: str, duration=2000):
        self.label.setText(text)
        self.show()
        self.raise_()
        QTimer.singleShot(duration, self.hide)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QWidget + QFrame + QLabel")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)
        button = QPushButton("顯示浮出框")
        layout.addWidget(button)

        self.floating = FloatingWidget(self)
        self.floating.move(50, 80)  # 你可以調整顯示位置
        self.floating.hide()

        button.clicked.connect(self.show_floating)

    def show_floating(self):
        self.floating.show_message("嗨！這是浮出訊息", duration=3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
