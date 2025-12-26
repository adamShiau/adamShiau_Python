from PySide6.QtCore import QRect, QPointFList
from PySide6.QtGui import QPainter, QColor, QFont, Qt
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QDialog


class RectWidget(QDialog):
    def __init__(self):
        super(RectWidget, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(300, 300)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 92);")
        # self.setAttribute(Qt.WA_TranslucentBackground)


    def rectFrame(self):
        rect = QFrame(self)
        rect.setStyleSheet(""""
            QFrame {
                background-color: rgba(0, 0, 0, 0);
                border: 0px solid;
            }
        """)
        layout = QVBoxLayout(self)
        layout.addWidget(rect)

        self.lb = QLabel("misalignment自動補償計算中...")
        self.lb.setAlignment(Qt.AlignCenter)
        self.lb.setFont(QFont('Arial', 12))
        self.lb.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        frame_layout = QVBoxLayout(rect)
        frame_layout.addWidget(self.lb)


    def show_message(self):
        self.rectFrame()
        self.show()
        self.raise_()


    def hide_message(self):
        # self.hide()
        self.close()

    # def rectPaint(self):
    #     paint = QPainter(self)
    #     paint.setPen(QColor(0, 0, 0))
    #
    #     rect = QRect(100, 100, 200, 150)
    #     paint.drawRect(rect)
    #
    #     font = QFont('Arial', 14)
    #     paint.setFont(font)
    #     paint.setPen(QColor(0, 0, 0))
    #
    #     rectText = "misalignment自動補償計算中..."
    #     paint.drawText(rect, Qt.AlignCenter, rectText)
    #     self.raise_()
