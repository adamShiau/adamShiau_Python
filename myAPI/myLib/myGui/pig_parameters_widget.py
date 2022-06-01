import sys

sys.path.append("../../")
print(__name__)
print(sys.path)
from myLib.myGui.mygui_serial import *
from myLib import common as cmn

'''-------define CMD address map-------'''
'''0~7 for output mode setting'''
'''8~255 for parameter setting'''
MODE_STOP = 0
MODE_FOG = 1
MODE_IMU = 2
MODE_EQ = 3
MODE_IMU_FAKE = 4
CMD_FOG_MOD_FREQ = 8
CMD_FOG_MOD_AMP_H = 9
CMD_FOG_MOD_AMP_L = 10
CMD_FOG_ERR_OFFSET = 11
CMD_FOG_POLARITY = 12
CMD_FOG_WAIT_CNT = 13
CMD_FOG_ERR_TH = 14
CMD_FOG_ERR_AVG = 15
CMD_FOG_TIMER_RST = 16
CMD_FOG_GAIN1 = 17
CMD_FOG_GAIN2 = 18
CMD_FOG_FB_ON = 19
CMD_FOG_CONST_STEP = 20
CMD_FOG_FPGA_Q = 21
CMD_FOG_FPGA_R = 22
CMD_FOG_DAC_GAIN = 23
CMD_FOG_INT_DELAY = 24
CMD_FOG_OUT_START = 25

''' FOG PARAMETERS'''
INIT_PARAMETERS = {"MOD_H": 6850,
                   "MOD_L": -6850,
                   "FREQ": 135,
                   "DAC_GAIN": 20,
                   "ERR_OFFSET": 0,
                   "POLARITY": 1,
                   "WAIT_CNT": 65,
                   "ERR_TH": 0,
                   "ERR_AVG": 6,
                   "GAIN1": 6,
                   "GAIN2": 5,
                   "FB_ON": 1,
                   "CONST_STEP": 0,
                   "KF_Q": 1,
                   "KF_R": 6,
                   "SF_A": 0.00295210451588764 * 1.02 / 2,
                   "SF_B": -0.00137052112589694,
                   "DATA_RATE": 2200
                   }
MOD_H_INIT 			= 6850
MOD_L_INIT 			= -6850
FREQ_INIT 			= 135
DAC_GAIN_INIT 		= 20
ERR_OFFSET_INIT 	= 0
POLARITY_INIT 		= 1
WAIT_CNT_INIT 		= 65
ERR_TH_INIT 		= 0
ERR_AVG_INIT 		= 6
GAIN1_SEL_INIT 		= 6
GAIN2_SEL_INIT 		= 5
FB_ON_INIT			= 1
CONST_STEP_INIT		= 0
FPGA_Q_INIT			= 1
FPGA_R_INIT			= 6
SW_Q_INIT			= 1
SW_R_INIT			= 6
SF_A_INIT = 0.00295210451588764*1.02/2
SF_B_INIT = -0.00137052112589694
DATA_RATE_INIT		= 2200

''' FOG paras position'''
POS_MOD_H_INIT = 0
POS_MOD_L_INIT = 1
POS_FREQ_INIT = 2
POS_DAC_GAIN_INIT = 3
POS_ERR_OFFSET_INIT = 4
POS_POLARITY_INIT = 5
POS_WAIT_CNT_INIT = 6
POS_ERR_TH_INIT = 7
POS_ERR_AVG_INIT = 8
POS_GAIN1_SEL_INIT = 9
POS_GAIN2_SEL_INIT = 10
POS_FB_ON_INIT = 11
POS_CONST_STEP_INIT = 12
POS_FPGA_Q_INIT = 13
POS_FPGA_R_INIT = 14
POS_SW_Q_INIT = 15
POS_SW_R_INIT = 16
POS_SF_A_INIT = 17
POS_SF_B_INIT = 18
POS_DATA_RATE_INIT = 19


class pig_parameters_widget(QGroupBox):
    def __init__(self, act):
        super(pig_parameters_widget, self).__init__()
        print("import pigParameters")
        self.__act = act
        self.__par_manager = cmn.parameters_manager("parameters_SP9.json", INIT_PARAMETERS, 1)
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
        self.KF_Q = spinBlock(title='SW_Q', minValue=1, maxValue=100000, double=False, step=1)
        self.KF_R = spinBlock(title='SW_R', minValue=0, maxValue=100000, double=False, step=1)
        self.HD_Q = spinBlock(title='FPGA_Q', minValue=1, maxValue=100000, double=False, step=1)
        self.HD_R = spinBlock(title='FPGA_R', minValue=0, maxValue=100000, double=False, step=1)
        '''slider'''
        self.dataRate_sd = sliderBlock(title='DATE RATE', minValue=400, maxValue=2200, curValue=2135, interval=100)
        ''' edit line '''
        self.sf_a = editBlock('SF_a')
        self.sf_b = editBlock('SF_b')

        self.initUI()
        initPara = self.__par_manager.check_file_exist()
        self.set_init_value(initPara)
        self.linkfunction()

    def initUI(self):
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
        mainLayout.addWidget(self.KF_Q, 9, 10, 1, 2)
        mainLayout.addWidget(self.KF_R, 9, 12, 1, 2)
        mainLayout.addWidget(self.sf_a, 10, 10, 1, 2)
        mainLayout.addWidget(self.sf_b, 10, 12, 1, 2)
        mainLayout.addWidget(self.dataRate_sd, 11, 10, 1, 4)
        self.setLayout(mainLayout)

    def linkfunction(self):
        ''' spin box connect'''
        self.wait_cnt.spin.valueChanged.connect(self.send_WAIT_CNT_CMD)
        self.avg.spin.valueChanged.connect(self.send_AVG_CMD)
        self.mod_H.spin.valueChanged.connect(self.send_MOD_H_CMD)
        self.mod_L.spin.valueChanged.connect(self.send_MOD_L_CMD)
        self.freq.spin.valueChanged.connect(self.send_FREQ_CMD)
        self.err_th.spin.valueChanged.connect(self.send_ERR_TH_CMD)
        self.err_offset.spin.valueChanged.connect(self.send_ERR_OFFSET_CMD)
        self.polarity.spin.valueChanged.connect(self.send_POLARITY_CMD)
        self.const_step.spin.valueChanged.connect(self.send_CONST_STEP_CMD)
        self.KF_Q.spin.valueChanged.connect(self.update_KF_Q)
        self.KF_R.spin.valueChanged.connect(self.update_KF_R)
        self.gain1.spin.valueChanged.connect(self.send_GAIN1_CMD)
        self.gain2.spin.valueChanged.connect(self.send_GAIN2_CMD)
        self.fb_on.spin.valueChanged.connect(self.send_FB_ON_CMD)
        self.dac_gain.spin.valueChanged.connect(self.send_DAC_GAIN_CMD)
        ''' slider '''
        self.dataRate_sd.sd.valueChanged.connect(self.send_DATA_RATE_CMD)
        ''' line edit '''
        self.sf_a.le.editingFinished.connect(self.SF_A_EDIT)
        self.sf_b.le.editingFinished.connect(self.SF_B_EDIT)

    def set_init_value(self, para):
        self.freq.spin.setValue(para["FREQ"])
        self.send_FREQ_CMD()
        self.wait_cnt.spin.setValue(para["WAIT_CNT"])
        self.send_WAIT_CNT_CMD()
        self.avg.spin.setValue(para["ERR_AVG"])
        self.send_AVG_CMD()
        self.mod_H.spin.setValue(para["MOD_H"])
        self.send_MOD_H_CMD()
        self.mod_L.spin.setValue(para["MOD_L"])
        self.send_MOD_L_CMD()
        self.err_th.spin.setValue(para["ERR_TH"])
        self.send_ERR_TH_CMD()
        self.err_offset.spin.setValue(para["ERR_OFFSET"])
        self.send_ERR_OFFSET_CMD()
        self.polarity.spin.setValue(para["POLARITY"])
        self.send_POLARITY_CMD()
        self.const_step.spin.setValue(para["CONST_STEP"])
        self.send_CONST_STEP_CMD()
        self.KF_Q.spin.setValue(para["KF_Q"])
        self.update_KF_Q()
        self.KF_R.spin.setValue(para["KF_R"])
        self.update_KF_R()
        self.gain1.spin.setValue(para["GAIN1"])
        self.send_GAIN1_CMD()
        self.gain2.spin.setValue(para["GAIN2"])
        self.send_GAIN2_CMD()
        self.fb_on.spin.setValue(para["FB_ON"])
        self.send_FB_ON_CMD()
        self.dac_gain.spin.setValue(para["DAC_GAIN"])
        self.send_DAC_GAIN_CMD()
        self.dataRate_sd.sd.setValue(para["DATA_RATE"])
        self.send_DATA_RATE_CMD()
        self.sf_a.le.setText(str(para["SF_A"]))
        self.SF_A_EDIT()
        self.sf_b.le.setText(str(para["SF_B"]))
        self.SF_B_EDIT()

    def writeImuCmd(self, cmd, value):
        self.__act.writeImuCmd(cmd, value)

    def send_FREQ_CMD(self):
        value = self.freq.spin.value()
        print('set freq: ', value)
        self.freq.lb.setText(str(round(1 / (2 * (value + 1) * 10e-6), 2)) + ' KHz')
        self.__act.writeImuCmd(CMD_FOG_MOD_FREQ, value)
        self.__par_manager.update_parameters("FREQ", value)

    def send_MOD_H_CMD(self):
        value = self.mod_H.spin.value()
        print('set mod_H: ', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_H, value)
        self.__par_manager.update_parameters("MOD_H", value)

    def send_MOD_L_CMD(self):
        value = self.mod_L.spin.value()
        print('set mod_L: ', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_L, value)
        self.__par_manager.update_parameters("MOD_L", value)

    def send_ERR_OFFSET_CMD(self):
        value = self.err_offset.spin.value()
        print('set err offset: ', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_OFFSET, value)
        self.__par_manager.update_parameters("ERR_OFFSET", value)

    def send_POLARITY_CMD(self):
        value = self.polarity.spin.value()
        print('set polarity: ', value)
        self.__act.writeImuCmd(CMD_FOG_POLARITY, value)
        self.__par_manager.update_parameters("POLARITY", value)

    def send_WAIT_CNT_CMD(self):
        value = self.wait_cnt.spin.value()
        print('set wait cnt: ', value)
        self.__act.writeImuCmd(CMD_FOG_WAIT_CNT, value)
        self.__par_manager.update_parameters("WAIT_CNT", value)

    def send_ERR_TH_CMD(self):
        value = self.err_th.spin.value()
        print('set err_th: ', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_TH, value)
        self.__par_manager.update_parameters("ERR_TH", value)

    def send_AVG_CMD(self):
        value = self.avg.spin.value()
        print('set err_avg: ', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_AVG, value)
        self.__par_manager.update_parameters("ERR_AVG", value)

    def send_GAIN1_CMD(self):
        value = self.gain1.spin.value()
        print('set gain1: ', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN1, value)
        self.__par_manager.update_parameters("GAIN1", value)

    def send_GAIN2_CMD(self):
        value = self.gain2.spin.value()
        print('set gain2: ', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN2, value)
        self.__par_manager.update_parameters("GAIN2", value)

    def send_FB_ON_CMD(self):
        value = self.fb_on.spin.value()
        print('set FB on: ', value)
        self.__act.writeImuCmd(CMD_FOG_FB_ON, value)
        self.__par_manager.update_parameters("FB_ON", value)

    def send_DAC_GAIN_CMD(self):
        value = self.dac_gain.spin.value()
        print('set DAC gain: ', value)
        self.__act.writeImuCmd(CMD_FOG_DAC_GAIN, value)
        self.__par_manager.update_parameters("DAC_GAIN", value)

    def send_CONST_STEP_CMD(self):
        value = self.const_step.spin.value()
        print('set constant step: ', value)
        self.__act.writeImuCmd(CMD_FOG_CONST_STEP, value)
        self.__par_manager.update_parameters("CONST_STEP", value)

    def update_KF_Q(self):
        value = self.KF_Q.spin.value()
        print('KF_Q: ', value)
        self.__par_manager.update_parameters("KF_Q", value)

    def update_KF_R(self):
        value = self.KF_R.spin.value()
        print('KF_R: ', value)
        self.__par_manager.update_parameters("KF_R", value)

    def send_DATA_RATE_CMD(self):
        value = self.dataRate_sd.sd.value()
        print('set dataRate: ', value)
        self.__act.writeImuCmd(CMD_FOG_INT_DELAY, value)
        self.__par_manager.update_parameters("DATA_RATE", value)

    def SF_A_EDIT(self):
        value = float(self.sf_a.le.text())
        print('sf_a: ', value)
        self.__par_manager.update_parameters("SF_A", value)

    def SF_B_EDIT(self):
        value = float(self.sf_b.le.text())
        print('sf_b: ', value)
        self.__par_manager.update_parameters("SF_B", value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pig_parameters_widget("act")
    w.show()
    app.exec_()
