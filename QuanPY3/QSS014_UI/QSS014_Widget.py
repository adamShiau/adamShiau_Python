import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *
TITLE_TEXT = "QSS014"

freq_MIN = 10
freq_MAX = 1000

phase_MIN = 0
phase_MAX = 180

Time_Min = 1
Time_Max = 100

Loop_Min = 1
Loop_Max = 1000

SHOW_Time_IMG = "set/time.png"

class timeDialog(QDialog):
    def __init__(self, init_data, parent = None):
        super(timeDialog, self).__init__(parent)
        self.setWindowTitle("Time Parameter")
        self.showFig = QLabel()
        fig = QPixmap(SHOW_Time_IMG)
        self.showFig.setPixmap(fig)
        self.showFig.show()

        self.t1 = spinBlock("T1 (ms)", Time_Min, Time_Max)
        self.t2 = spinBlock("T2 (ms)", Time_Min, Time_Max)
        self.t3 = spinBlock("T3 (ms)", Time_Min, Time_Max)
        self.loop = spinBlock("Loop Times", Loop_Min, Loop_Max)

        self.OKbtn = QPushButton("OK")
        self.data = init_data

        self.layout()
        self.connectFunction()
        self.setSpinValue(self.data)

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.showFig,0,0,1,4)

        layout.addWidget(self.t1,1,0,1,1)
        layout.addWidget(self.t2,1,1,1,1)
        layout.addWidget(self.t3,1,2,1,1)
        layout.addWidget(self.loop,1,3,1,1)
        layout.addWidget(self.OKbtn,2,3,1,1)

        self.setLayout(layout)

    def setSpinValue(self, data):
        self.t1.spin.setValue(int(data[0]))
        self.t2.spin.setValue(int(data[1]))
        self.t3.spin.setValue(int(data[2]))
        self.loop.spin.setValue(int(data[3]))

    def getSpinValue(self):
        data = [1, 1, 1, 1]

        data[0] = self.t1.spin.value()
        data[1] = self.t2.spin.value()
        data[2] = self.t3.spin.value()
        data[3] = self.loop.spin.value()

        return data

    def connectFunction(self):
        self.OKbtn.clicked.connect(self.okButtonPress)

    def okButtonPress(self):
        self.data = self.getSpinValue()
        self.close()

    @staticmethod
    def getParameter(init_data, parent = None):
        dialog = timeDialog(init_data, parent)
        result = dialog.exec_()
        return dialog.data


class TestGroup(QWidget):
    def __init__(self, parent=None):
        super(TestGroup, self).__init__(parent)
        self.freq = spinBlock("Modulation Frequency (Hz)", freq_MIN, freq_MAX)
        self.phase = spinBlock("Phase Delay (degree)", phase_MIN, phase_MAX)
        self.timeBtn = QPushButton("Set Time")
        self.send = QPushButton("Send")
        self.send.setEnabled(False)

        self.Test_UI()

    def Test_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.freq, 0,0,1,1)
        layout.addWidget(self.phase, 0,1,1,1)
        layout.addWidget(self.timeBtn, 1,0,1,1)
        layout.addWidget(self.send, 1,1,1,1)
        self.setLayout(layout)


class Signal_Read_Group(QGroupBox):
    def __init__(self, parent=None):
        super(Signal_Read_Group, self).__init__(parent)
        self.setTitle("Signal Read (V)")
        self.text = QLabel("0")
        self.start_rd = QPushButton("start")
        self.stop_rd = QPushButton("stop")
        pe = QPalette()
        pe.setColor(QPalette.WindowText,Qt.yellow)
        self.text.setAutoFillBackground(True)
        pe.setColor(QPalette.Window,Qt.black)
        self.text.setPalette(pe)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setFont(QFont("",32,QFont.Bold))

        layout = QGridLayout()
        layout.addWidget(self.start_rd,0,0,1,1)
        layout.addWidget(self.stop_rd,0,1,1,1)
        layout.addWidget(self.text,1,0,2,2)
        self.setLayout(layout)


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super(mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.usb = connectBlock("USB Connection")
        self.test = TestGroup()
        self.adc = Signal_Read_Group()
        self.adc_plot = outputPlot()
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.test, 0,0,1,1)
        mainLayout.addWidget(self.usb.layout1(), 0,2,1,1)
        mainLayout.addWidget(self.adc, 0,1,1,1)
        mainLayout.addWidget(self.adc_plot, 1,0,3,3)
        # mainLayout.setRowStretch(0, 1)
        # mainLayout.setRowStretch(1, 1)
        # mainLayout.setColumnStretch(0, 1)
        # mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())

