import os
import sys
sys.path.append("../")
from py3lib.QuGUIclass import *

TITLE_TEXT = "Charge detector"

Time_Min = 1
Time_Max = 100

SHOW_Time_IMG = "set/time.png"
SHOW_Mode1_IMG = "set/mode1.png"
SHOW_Mode2_IMG = "set/mode2.png"
SHOW_Mode3_IMG = "set/mode3.png"


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
        self.t4 = spinBlock("T4 (ms)", Time_Min, Time_Max)

        self.OKbtn = QPushButton("OK")
        self.data = init_data

        self.layout()
        self.linkFunction()
        self.setSpinValue(self.data)

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.showFig,0,0,1,4)

        layout.addWidget(self.t1,1,0,1,1)
        layout.addWidget(self.t2,1,1,1,1)
        layout.addWidget(self.t3,1,2,1,1)
        layout.addWidget(self.t4,1,3,1,1)
        layout.addWidget(self.OKbtn,2,3,1,1)

        self.setLayout(layout)

    def setSpinValue(self, data):
        self.t1.spin.setValue(int(data[0]))
        self.t2.spin.setValue(int(data[1]))
        self.t3.spin.setValue(int(data[2]))
        self.t4.spin.setValue(int(data[3]))

    def getSpinValue(self):
        data = [1, 1, 1, 1]

        data[0] = self.t1.spin.value()
        data[1] = self.t2.spin.value()
        data[2] = self.t3.spin.value()
        data[3] = self.t4.spin.value()

        return data

    def linkFunction(self):
        self.t1.spin.valueChanged.connect(self.adjt4)
        self.t4.spin.valueChanged.connect(self.adjt1)
        self.OKbtn.clicked.connect(self.okButtonPress)

    def okButtonPress(self):
        self.data = self.getSpinValue()
        self.close()

    @staticmethod
    def getParameter(init_data, parent = None):
        dialog = timeDialog(init_data, parent)
        result = dialog.exec_()
        return dialog.data

    def adjt1(self):
        t4 = self.t4.spin.value()
        self.t1.spin.setRange(t4+1, Time_Max)
        # print("adj t1 min = "+str(self.t1.spin.value()))

    def adjt4(self):
        t1 = self.t1.spin.value()
        self.t4.spin.setRange(Time_Min, t1-1)
        # print("adj t4 max = "+str(self.t4.spin.value()))

class ModeGroup(QGroupBox):
    def __init__(self, parent=None):
        super(ModeGroup, self).__init__(parent)
        self.setTitle("Select Mode")

        self.showFig1 = QLabel()
        fig1 = QPixmap(SHOW_Mode1_IMG)
        self.showFig1.setPixmap(fig1)
        self.showFig1.show()

        self.showFig2 = QLabel()
        fig2 = QPixmap(SHOW_Mode2_IMG)
        self.showFig2.setPixmap(fig2)
        self.showFig2.show()

        self.showFig3 = QLabel()
        fig3 = QPixmap(SHOW_Mode3_IMG)
        self.showFig3.setPixmap(fig3)
        self.showFig3.show()

        self.mode1 = QRadioButton("Mode 1", self)
        self.mode2 = QRadioButton("Mode 2", self)
        self.mode3 = QRadioButton("Mode 3", self)
        self.Mode_UI()

    def Mode_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.mode1, 0,0,1,1)
        layout.addWidget(self.mode2, 0,1,1,1)
        layout.addWidget(self.mode3, 0,2,1,1)
        layout.addWidget(self.showFig1, 1,0,1,1)
        layout.addWidget(self.showFig2, 1,1,1,1)
        layout.addWidget(self.showFig3, 1,2,1,1)
        self.setLayout(layout)


class ChGroup(QGroupBox):
    def __init__(self, parent=None):
        super(ChGroup, self).__init__(parent)
        self.setTitle("Select Channel")

        self.ch1 = QRadioButton("CH 1", self)
        self.ch2 = QRadioButton("CH 2", self)
        self.ch3 = QRadioButton("CH 3", self)
        self.ch4 = QRadioButton("CH 4", self)
        self.CH_UI()

    def CH_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.ch1, 0,0,1,1)
        layout.addWidget(self.ch2, 0,1,1,1)
        layout.addWidget(self.ch3, 0,2,1,1)
        layout.addWidget(self.ch4, 0,3,1,1)
        self.setLayout(layout)


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.usb = connectBlock("USB Connection")
        self.FHedit = editBlock("File Header")
        self.ch = ChGroup()
        self.mode = ModeGroup()
        self.timeBtn = QPushButton("Set Time")
        self.run = QPushButton("Run")
        self.stop = QPushButton("Stop")
        self.save = QPushButton("Save")
        self.run.setEnabled(False)
        self.stop.setEnabled(False)
        self.save.setEnabled(False)
        self.plot = outputPlot()
        self.plot.ax.set_ylabel("Vlotage(V)")
        self.plot.ax.set_xlabel("dT(ms)")
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.ch, 0,0,1,4)
        mainLayout.addWidget(self.mode, 1,0,2,4)
        mainLayout.addWidget(self.usb.layout1(), 0,4,2,1)
        mainLayout.addWidget(self.FHedit, 2,4,2,1)
        mainLayout.addWidget(self.timeBtn, 3,0,1,1)
        mainLayout.addWidget(self.run, 3,1,1,1)
        mainLayout.addWidget(self.stop, 3,2,1,1)
        mainLayout.addWidget(self.save, 3,3,1,1)
        mainLayout.addWidget(self.plot, 4,0,5,4)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        mainLayout.setColumnStretch(4, 1)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setRowStretch(4, 2)
        mainLayout.setRowStretch(5, 2)
        mainLayout.setRowStretch(6, 2)
        mainLayout.setRowStretch(7, 2)
        mainLayout.setRowStretch(8, 2)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
