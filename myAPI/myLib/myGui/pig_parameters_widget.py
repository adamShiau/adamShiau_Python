import sys
sys.path.append("../")
# print("pig wid")
# print(sys.path)
from myLib.myGui.mygui_serial import *


class pigParameters(QGroupBox):
    def __init__(self, parent=None):
        super(pigParameters, self).__init__(parent)

        self.setTitle("parameters")
        self.wait_cnt = spinBlock(title='Wait cnt', minValue=0, maxValue=100, double=False, step=1)
        self.avg = spinBlock(title='avg', minValue=0, maxValue=6, double=False, step=1)
        self.err_offset = spinBlock(title='Err offset', minValue=-10000, maxValue=10000, double=False, step=1)
        self.polarity = spinBlock(title='polarity', minValue=0, maxValue=1, double=False, step=1)
        self.mod_H = spinBlock(title='MOD_H', minValue=-32768, maxValue=32767, double=False, step=100)
        self.mod_L = spinBlock(title='MOD_L', minValue=-32768, maxValue=0, double=False, step=100)
        self.gain1 = spinBlock(title='GAIN1', minValue=0, maxValue=14, double=False, step=1)
        self.gain2 = spinBlock(title='GAIN2', minValue=0, maxValue=14, double=False, step=1)
        self.const_step = spinBlock(title='const_step', minValue=-32768, maxValue=32767, double=False, step=1)
        self.dac_gain = spinBlock(title='DAC_GAIN', minValue=0, maxValue=1023, double=False, step=10)
        self.fb_on = spinBlock(title='mode(0:OPEN)', minValue=0, maxValue=2, double=False, step=1)
        self.err_th = spinBlock(title='ERR_TH', minValue=0, maxValue=16384, double=False, step=1)
        self.freq = spinBlockOneLabel(title='frequency', minValue=10, maxValue=1500, double=False, step=1)
        self.SW_Q = spinBlock(title='SW_Q', minValue=1, maxValue=100000, double=False, step=1)
        self.SW_R = spinBlock(title='SW_R', minValue=0, maxValue=100000, double=False, step=1)
        self.HD_Q = spinBlock(title='FPGA_Q', minValue=1, maxValue=100000, double=False, step=1)
        self.HD_R = spinBlock(title='FPGA_R', minValue=0, maxValue=100000, double=False, step=1)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.wait_cnt, 1, 10, 1, 2)
        mainLayout.addWidget(self.avg, 1, 12, 1, 2)
        mainLayout.addWidget(self.mod_H, 2, 10, 1, 2)
        mainLayout.addWidget(self.mod_L, 2, 12, 1, 2)
        mainLayout.addWidget(self.err_offset, 3, 10, 1, 2)
        mainLayout.addWidget(self.polarity, 3, 12, 1, 2)
        mainLayout.addWidget(self.gain1, 4, 10, 1, 2)
        mainLayout.addWidget(self.const_step, 5, 12, 1, 2)
        mainLayout.addWidget(self.dac_gain, 5, 10, 1, 2)
        mainLayout.addWidget(self.gain2, 4, 12, 1, 2)
        mainLayout.addWidget(self.fb_on, 6, 12, 1, 2)
        mainLayout.addWidget(self.err_th, 6, 10, 1, 2)
        mainLayout.addWidget(self.freq, 7, 10, 1, 4)

        mainLayout.addWidget(self.HD_Q, 8, 10, 1, 2)
        mainLayout.addWidget(self.HD_R, 8, 12, 1, 2)
        mainLayout.addWidget(self.SW_Q, 9, 10, 1, 2)
        mainLayout.addWidget(self.SW_R, 9, 12, 1, 2)
        self.setLayout(mainLayout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pigParameters()
    w.show()
    app.exec_()