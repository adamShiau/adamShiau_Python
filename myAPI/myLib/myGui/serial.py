from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys


class usbConnect():
    def __init__(self, btn_name="COM update", group_name='Connect COM port'):
        self.groupBox = QGroupBox(group_name)
        self.bt_update = QPushButton(btn_name)
        self.bt_connect = QPushButton('connect')
        self.cb = QComboBox()
        self.lb = QLabel(" ")
        self.lb_com = QLabel(" ")

    def layoutG(self):
        layout = QGridLayout()
        layout.addWidget(self.bt_update, 0, 0, 1, 1)
        layout.addWidget(self.cb, 0, 1, 1, 1)
        layout.addWidget(self.bt_connect, 0, 2, 1, 1)
        layout.addWidget(self.lb, 1, 0, 1, 2)
        layout.addWidget(self.lb_com, 1, 2, 1, 1)
        self.groupBox.setLayout(layout)
        self.groupBox.show()
        return self.groupBox

    def SetConnectText(self, color, text):
        pe = QPalette()
        pe.setColor(QPalette.WindowText, color)
        self.lb_com.setPalette(pe)
        self.lb_com.setText(text)
        self.lb_com.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = usbConnect()
    main.layoutG()
    app.exec_()