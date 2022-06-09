from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class usbConnect():
    def __init__(self, group_name='Connect COM port'):
        self.__portList = None
        self.__groupBox = QGroupBox(group_name)
        # self.__groupBox.setCheckable(True)
        self.bt_update = QPushButton("update")
        self.bt_connect = QPushButton('connect')
        self.bt_disconnect = QPushButton('disconnect')
        self.bt_disconnect.setEnabled(False)
        self.cb = QComboBox()
        self.lb_status = QLabel(" ")
        self.lb_comDisp = QLabel(" ")

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.bt_update, 0, 0, 1, 1)
        layout.addWidget(self.cb, 0, 1, 1, 1)
        layout.addWidget(self.bt_connect, 0, 2, 1, 1)
        layout.addWidget(self.bt_disconnect, 0, 3, 1, 1)
        layout.addWidget(self.lb_comDisp, 1, 0, 1, 2)
        layout.addWidget(self.lb_status, 1, 2, 1, 1)
        self.__groupBox.setLayout(layout)
        return self.__groupBox

    def addPortItems(self, num, ports):
        self.__portList = ports
        self.cb.clear()
        if num > 0:
            for i in range(num):
                self.cb.addItem(ports[i].name)

    def selectPort(self):
        idx = self.cb.currentIndex()
        self.lb_comDisp.setText(self.__portList[idx].description)
        return self.__portList[idx].name

    def updateStatusLabel(self, is_open):
        self.bt_connect.setEnabled(not is_open)
        self.bt_disconnect.setEnabled(is_open)

        if is_open:
            self.SetConnectText(Qt.blue, "is connected")
            # self.lb_status.setText("is connected")
        else:
            self.SetConnectText(Qt.red, "is disconnected")
            # self.lb_status.setText("is disconnected")

    def show(self):
        QB = self.layout()
        QB.show()

    def SetConnectText(self, color, text):
        pe = QPalette()
        pe.setColor(QPalette.WindowText, color)
        self.lb_status.setPalette(pe)
        self.lb_status.setFont(QFont("Arial", 12))
        self.lb_status.setText(text)
        # self.lb_status.setAlignment(Qt.AlignCenter)
        # self.lb_comDisp.show()


class dataSaveBlock(QGroupBox):
    def __init__(self, name=""):
        super(dataSaveBlock, self).__init__()
        self.setTitle(name)
        self.rb = QRadioButton("save")
        self.le_filename = QLineEdit("enter_file_name")
        self.le_ext = QLineEdit(".txt")
        self.rb.setChecked(False)

        layout = QGridLayout()
        layout.addWidget(self.rb, 0, 0, 1, 1)
        layout.addWidget(self.le_filename, 0, 1, 1, 3)
        layout.addWidget(self.le_ext, 0, 4, 1, 1)
        self.setLayout(layout)


class spinBlock(QGroupBox):
    def __init__(self, title, minValue, maxValue, step=1, double=False, Decimals=2):
        super(spinBlock, self).__init__()
        if double:
            self.spin = QDoubleSpinBox()
            self.spin.setDecimals(Decimals)
        else:
            self.spin = QSpinBox()

        self.spin.setRange(minValue, maxValue)
        self.spin.setSingleStep(step)
        self.setTitle(title)

        layout = QHBoxLayout()
        layout.addWidget(self.spin)
        self.setLayout(layout)


class spinBlockOneLabel(QGroupBox):
    def __init__(self, title, minValue, maxValue, double=False, step=1, Decimals=2):
        super(spinBlockOneLabel, self).__init__()
        if double:
            self.spin = QDoubleSpinBox()
            self.spin.setDecimals(Decimals)
        else:
            self.spin = QSpinBox()

        self.spin.setRange(minValue, maxValue)
        self.spin.setSingleStep(step)
        self.lb = QLabel('freq')
        self.setTitle(title)

        layout = QHBoxLayout()
        layout.addWidget(self.spin)
        layout.addWidget(self.lb)
        self.setLayout(layout)


class sliderBlock(QGroupBox):
    def __init__(self, title, minValue, maxValue, curValue, step=1, interval=100, parent=None):
        super(sliderBlock, self).__init__(parent)
        self.setTitle(title)
        self.sd = QSlider(Qt.Horizontal)
        self.sd.setMinimum(minValue)
        self.sd.setMaximum(maxValue)
        self.sd.setValue(curValue)
        self.sd.setSingleStep(step)
        self.sd.setTickInterval(interval)
        self.sd.setTickPosition(QSlider.TicksBelow)
        layout = QVBoxLayout()
        layout.addWidget(self.sd)
        self.setLayout(layout)


class editBlock(QGroupBox):
    def __init__(self, title, parent=None):
        super(editBlock, self).__init__(parent)
        self.le = QLineEdit()
        self.setTitle(title)

        layout = QHBoxLayout()
        layout.addWidget(self.le)
        self.setLayout(layout)


class displayOneBlock(QGroupBox):
    def __init__(self, name='name'):
        super(displayOneBlock, self).__init__()
        self.setTitle(name)
        self.setFont(QFont('', 10))
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.yellow)
        pe.setColor(QPalette.Window, Qt.black)
        self.lb = QLabel()
        self.lb.setPalette(pe)
        self.lb.setFont(QFont('Arial', 20))
        self.lb.setAutoFillBackground(True)
        self.lb.setText('buffer')

        layout = QVBoxLayout()
        layout.addWidget(self.lb)
        self.setLayout(layout)


class checkBoxBlock_2(QGroupBox):
    def __init__(self, title='', name1='', name2=''):
        super(checkBoxBlock_2, self).__init__()
        self.setTitle(title)
        self.cb_1 = QCheckBox(name1)
        self.cb_2 = QCheckBox(name2)
        pe = QPalette()
        pe.setColor(QPalette.Window, Qt.white)
        self.setPalette(pe)
        self.setAutoFillBackground(True)

        layout = QHBoxLayout()
        layout.addWidget(self.cb_1)
        layout.addWidget(self.cb_2)
        self.setLayout(layout)


class radioButtonBlock_2(QGroupBox):
    def __init__(self, title='', name1='', name2=''):
        super(radioButtonBlock_2, self).__init__()
        self.__btn_status = 1
        self.name1 = name1
        self.name2 = name2
        self.setTitle(title)
        self.rb1 = QRadioButton(name1)
        self.rb2 = QRadioButton(name2)
        self.rb1.toggled.connect(lambda: self.btnstate_connect(self.rb1))
        self.rb2.toggled.connect(lambda: self.btnstate_connect(self.rb2))
        pe = QPalette()
        pe.setColor(QPalette.Window, Qt.white)
        self.setPalette(pe)
        self.setAutoFillBackground(True)
        layout = QHBoxLayout()
        layout.addWidget(self.rb1)
        layout.addWidget(self.rb2)
        self.setLayout(layout)

    def btnstate_connect(self, btn):
        if btn.isChecked():
            if btn.text() == self.name1:
                self.btn_status = 1
            else:
                self.btn_status = 2

    @property
    def btn_status(self):
        return self.__btn_status

    @btn_status.setter
    def btn_status(self, state):
        self.__btn_status = state


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = pigParameters()
    main.show()
    app.exec_()
