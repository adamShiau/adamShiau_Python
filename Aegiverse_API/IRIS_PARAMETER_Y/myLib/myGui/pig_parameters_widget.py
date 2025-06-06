# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys
import struct

sys.path.append("../../")
print(__name__)
print(sys.path)
from myLib.myGui.mygui_serial import *
from myLib import common as cmn
from myLib.myGui.myLabel import *

'''-------define CMD address map-------'''
'''0~7 for output mode setting'''
'''8~255 for parameter setting'''
MODE_STOP = 0
MODE_FOG = 1
MODE_IMU = 2
MODE_EQ = 3
MODE_IMU_FAKE = 4
''' FOG PARAMETER'''
CMD_FOG_MOD_FREQ = 8
CMD_FOG_MOD_AMP_H = 9
CMD_FOG_MOD_AMP_L = 10
CMD_FOG_POLARITY = 11
CMD_FOG_WAIT_CNT = 12
CMD_FOG_ERR_AVG = 13
CMD_FOG_GAIN1 = 14
CMD_FOG_CONST_STEP = 15
CMD_FOG_FB_ON = 16
CMD_FOG_GAIN2 = 17
CMD_FOG_ERR_OFFSET = 18
CMD_FOG_DAC_GAIN = 19
CMD_FOG_CUTOFF = 20

CMD_SF_COMP_T1 = 23
CMD_SF_COMP_T2 = 24
CMD_SF_1_SLOPE = 25
CMD_SF_1_OFFSET = 26

CMD_FOG_ERR_TH = 39
CMD_FOG_TIMER_RST = 100

CMD_FOG_FPGA_Q = 220
CMD_FOG_FPGA_R = 220

CMD_FOG_INT_DELAY = 240
CMD_FOG_OUT_START = 250
CMD_FOG_SF0 = 260
CMD_FOG_SF1 = 270
CMD_FOG_SF2 = 280
CMD_FOG_SF3 = 290
CMD_FOG_SF4 = 300
CMD_FOG_SF5 = 310
CMD_FOG_SF6 = 320
CMD_FOG_SF7 = 330
CMD_FOG_SF8 = 340
CMD_FOG_SF9 = 350
CMD_FOG_TMIN = 360
CMD_FOG_TMAX = 370
CMD_FOG_SFB = 380

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
                   "HD_Q": 1,
                   "HD_R": 1,
                   "SF_A": 0.00295210451588764 * 1.02 / 2,
                   "SF_B": -0.00137052112589694,
                   "DATA_RATE": 2000
                   }


class pig_parameters_widget(QGroupBox):
    def __init__(self, act, fileName="default_fog_parameters.json"):
        super(pig_parameters_widget, self).__init__()
        print("import pigParameters")
        self.__act = act
        self.__par_manager = cmn.parameters_manager(fileName, INIT_PARAMETERS, fnum=1)
        self.setWindowTitle("PIG parameters")
        # self.setTitle("PIG parameters")
        self.wait_cnt = spinBlock(title='Wait cnt', minValue=0, maxValue=300, double=False, step=1)
        self.avg = spinBlock(title='avg', minValue=0, maxValue=9, double=False, step=1)
        self.err_offset = spinBlock(title='Err offset', minValue=-10000, maxValue=10000, double=False, step=1)
        self.polarity = spinBlock(title='polarity', minValue=0, maxValue=1, double=False, step=1)
        self.mod_H = spinBlock(title='MOD_H', minValue=-32768, maxValue=32767, double=False, step=100)
        self.mod_L = spinBlock(title='MOD_L', minValue=-32768, maxValue=0, double=False, step=100)
        self.gain1 = spinBlock(title='GAIN1', minValue=0, maxValue=14, double=False, step=1)
        self.gain2 = spinBlock(title='GAIN2', minValue=0, maxValue=20, double=False, step=1)
        self.const_step = spinBlock(title='const_step', minValue=-32768, maxValue=65000, double=False, step=100)
        self.dac_gain = spinBlock(title='DAC_GAIN', minValue=0, maxValue=1023, double=False, step=1)
        self.fb_on = spinBlock(title='mode(0:OPEN)', minValue=0, maxValue=2, double=False, step=1)
        self.err_th = spinBlock(title='ERR_TH', minValue=0, maxValue=16384, double=False, step=1)
        self.freq = spinBlockOneLabel(title='frequency', minValue=10, maxValue=1500, double=False, step=1)
        # self.KF_Q = spinBlock(title='SW_Q', minValue=1, maxValue=100000, double=False, step=1)
        # self.KF_R = spinBlock(title='SW_R', minValue=0, maxValue=100000, double=False, step=1)
        # self.HD_Q = spinBlock(title='FPGA_Q', minValue=1, maxValue=100000, double=False, step=1)
        # self.HD_Q.setEnabled(False)
        # self.HD_R = spinBlock(title='FPGA_R', minValue=0, maxValue=100000, double=False, step=1)
        # self.HD_R.setEnabled(False)
        self.Tmin = spinBlock(title='Tmin', minValue=-30, maxValue=30, double=False, step=5)
        self.Tmax = spinBlock(title='Tmax', minValue=30, maxValue=150, double=False, step=5)
        self.cutoff = spinBlock(title='CutOff', minValue=50, maxValue=1500, double=False, step=5)
        '''slider'''
        self.dataRate_sd = sliderBlock(title='DATE RATE', minValue=1500, maxValue=5000, curValue=2500, interval=100)
        ''' edit line '''
        self.sf_comp_T1 = editBlock('sf_comp_T1')
        self.sf_comp_T2 = editBlock('sf_comp_T2')
        self.sf_1_slope = editBlock('sf_1_slope')
        self.sf_1_offset = editBlock('sf_1_offset')
        self.sf3 = editBlock('SF3')
        self.sf4 = editBlock('SF4')
        self.sf5 = editBlock('SF5')
        self.sf6 = editBlock('SF6')
        self.sf7 = editBlock('SF7')
        self.sf8 = editBlock('SF8')
        self.sf9 = editBlock('SF9')
        self.sfb = editBlock('SFB')

        self.dump_bt = QPushButton("dump")
        # self.sf_all = editBlock('SF_all')
        ''' label '''
        self.Tmin_lb = QLabel()
        self.Tmax_lb = QLabel()
        self.T1r_lb = QLabel()
        self.T1l_lb = QLabel()
        self.T2r_lb = QLabel()
        self.T2l_lb = QLabel()
        self.T3r_lb = QLabel()
        self.T3l_lb = QLabel()
        self.T4r_lb = QLabel()
        self.T4l_lb = QLabel()
        self.T5r_lb = QLabel()
        self.T5l_lb = QLabel()
        self.T6r_lb = QLabel()
        self.T6l_lb = QLabel()
        self.T7r_lb = QLabel()
        self.T7l_lb = QLabel()
        self.Firmware_Version_lb = QLabel()
        self.GUI_Version_lb = QLabel()

        self.initUI()
        # initPara = self.__act.dump_fog_parameters(2)
        # print(initPara)
        # self.set_init_value(initPara)
        self.linkfunction()

    def initUI(self):
        mainLayout = QGridLayout()

        mainLayout.addWidget(self.wait_cnt, 0, 0, 1, 2)
        mainLayout.addWidget(self.avg, 0, 2, 1, 2)
        mainLayout.addWidget(self.mod_H, 1, 0, 1, 2)
        mainLayout.addWidget(self.mod_L, 1, 2, 1, 2)
        mainLayout.addWidget(self.err_offset, 2, 0, 1, 2)
        mainLayout.addWidget(self.polarity, 2, 2, 1, 2)
        mainLayout.addWidget(self.gain1, 3, 0, 1, 2)
        mainLayout.addWidget(self.gain2, 3, 2, 1, 2)
        mainLayout.addWidget(self.const_step, 4, 2, 1, 2)
        mainLayout.addWidget(self.dac_gain, 4, 0, 1, 2)
        mainLayout.addWidget(self.err_th, 5, 0, 1, 2)
        mainLayout.addWidget(self.fb_on, 5, 2, 1, 2)
        mainLayout.addWidget(self.freq, 6, 0, 1, 4)
        # mainLayout.addWidget(self.HD_Q, 7, 0, 1, 2)
        # mainLayout.addWidget(self.HD_R, 7, 2, 1, 2)
        # mainLayout.addWidget(self.KF_Q, 8, 0, 1, 2)
        # mainLayout.addWidget(self.KF_R, 8, 2, 1, 2)
        mainLayout.addWidget(self.dataRate_sd, 9, 0, 1, 4)
        mainLayout.addWidget(self.sfb, 10, 6, 1, 2)
        mainLayout.addWidget(self.cutoff, 10, 0, 1, 2)
        mainLayout.addWidget(self.dump_bt, 11, 0, 1, 2)
        mainLayout.addWidget(self.Firmware_Version_lb, 12, 0, 1, 4)
        mainLayout.addWidget(self.GUI_Version_lb, 13, 0, 1, 4)
        mainLayout.addWidget(self.Tmin, 9, 4, 1, 2)
        mainLayout.addWidget(self.Tmax, 0, 4, 1, 2)
        mainLayout.addWidget(self.sf_comp_T1, 9, 6, 1, 2)
        mainLayout.addWidget(self.sf_comp_T2, 8, 6, 1, 2)
        mainLayout.addWidget(self.sf_1_slope, 7, 6, 1, 2)
        mainLayout.addWidget(self.sf_1_offset, 6, 6, 1, 2)
        mainLayout.addWidget(self.sf4, 5, 6, 1, 2)
        mainLayout.addWidget(self.sf5, 4, 6, 1, 2)
        mainLayout.addWidget(self.sf6, 3, 6, 1, 2)
        mainLayout.addWidget(self.sf7, 2, 6, 1, 2)
        mainLayout.addWidget(self.sf8, 1, 6, 1, 2)
        mainLayout.addWidget(self.sf9, 0, 6, 1, 2)
        mainLayout.addWidget(self.Tmin_lb, 8, 4, 1, 2)
        mainLayout.addWidget(self.Tmax_lb, 1, 8, 1, 2)
        mainLayout.addWidget(self.T1r_lb, 8, 8, 1, 2)
        mainLayout.addWidget(self.T1l_lb, 7, 4, 1, 2)
        mainLayout.addWidget(self.T2r_lb, 7, 8, 1, 2)
        mainLayout.addWidget(self.T2l_lb, 6, 4, 1, 2)
        mainLayout.addWidget(self.T3r_lb, 6, 8, 1, 2)
        mainLayout.addWidget(self.T3l_lb, 5, 4, 1, 2)
        mainLayout.addWidget(self.T4r_lb, 5, 8, 1, 2)
        mainLayout.addWidget(self.T4l_lb, 4, 4, 1, 2)
        mainLayout.addWidget(self.T5r_lb, 4, 8, 1, 2)
        mainLayout.addWidget(self.T5l_lb, 3, 4, 1, 2)
        mainLayout.addWidget(self.T6r_lb, 3, 8, 1, 2)
        mainLayout.addWidget(self.T6l_lb, 2, 4, 1, 2)
        mainLayout.addWidget(self.T7r_lb, 2, 8, 1, 2)
        mainLayout.addWidget(self.T7l_lb, 1, 4, 1, 2)
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
        # self.KF_Q.spin.valueChanged.connect(self.update_KF_Q)
        # self.KF_R.spin.valueChanged.connect(self.update_KF_R)
        # self.HD_Q.spin.valueChanged.connect(self.update_FPGA_Q)
        # self.HD_R.spin.valueChanged.connect(self.update_FPGA_R)
        self.gain1.spin.valueChanged.connect(self.send_GAIN1_CMD)
        self.gain2.spin.valueChanged.connect(self.send_GAIN2_CMD)
        self.fb_on.spin.valueChanged.connect(self.send_FB_ON_CMD)
        self.dac_gain.spin.valueChanged.connect(self.send_DAC_GAIN_CMD)
        self.Tmin.spin.valueChanged.connect(self.send_TMIN_CMD)
        self.Tmax.spin.valueChanged.connect(self.send_TMAX_CMD)
        self.cutoff.spin.valueChanged.connect(self.send_CUTOFF_CMD)
        ''' slider '''
        self.dataRate_sd.sd.valueChanged.connect(self.send_DATA_RATE_CMD)
        ''' line edit '''
        # self.sf_a.le.editingFinished.connect(self.SF_A_EDIT)
        # self.sf_b.le.editingFinished.connect(self.SF_B_EDIT)
        # self.sf_all.le.editingFinished.connect(self.send_SF_ALL_CMD)
        self.sf_comp_T1.le.editingFinished.connect(self.send_SF_COMP_T1_CMD)
        self.sf_comp_T2.le.editingFinished.connect(self.send_SF_COMP_T2_CMD)
        self.sf_1_slope.le.editingFinished.connect(self.send_SF_1_SLOPE)
        self.sf_1_offset.le.editingFinished.connect(self.send_SF_1_OFFSET)
        self.sf4.le.editingFinished.connect(self.send_SF4_CMD)
        self.sf5.le.editingFinished.connect(self.send_SF5_CMD)
        self.sf6.le.editingFinished.connect(self.send_SF6_CMD)
        self.sf7.le.editingFinished.connect(self.send_SF7_CMD)
        self.sf8.le.editingFinished.connect(self.send_SF8_CMD)
        self.sf9.le.editingFinished.connect(self.send_SF9_CMD)
        self.sfb.le.editingFinished.connect(self.send_SFB_CMD)
        ''' bt'''
        self.dump_bt.clicked.connect(self.getVersion)
        self.dump_bt.clicked.connect(self.dump_parameter)

    def dump_parameter(self):
        self.__act.flushInputBuffer()
        initPara = self.__act.dump_fog_parameters(2)
        print(initPara)
        self.set_init_value(initPara)

    def getVersion(self):
        self.__act.flushInputBuffer()
        # self.Firmware_Version_lb.setText(self.__act.getVersion(2))
        self.Firmware_Version_lb.setText('not yet done')
        self.GUI_Version_lb.setText('GP-13-PD')

    def set_init_value(self, para):
        self.freq.spin.setValue(para["0"])
        self.mod_H.spin.setValue(para["1"])
        self.mod_L.spin.setValue(para["2"])
        self.polarity.spin.setValue(para["3"])
        self.wait_cnt.spin.setValue(para["4"])
        self.avg.spin.setValue(para["5"])
        self.gain1.spin.setValue(para["6"])
        self.const_step.spin.setValue(para["7"])
        self.fb_on.spin.setValue(para["8"])
        self.gain2.spin.setValue(para["9"])
        self.err_offset.spin.setValue(para["10"])
        self.dac_gain.spin.setValue(para["11"])
        self.cutoff.spin.setValue(para["12"])
        self.sf_comp_T1.le.setText(str(self.ieee754_int_to_float(para["15"])))
        self.sf_comp_T2.le.setText(str(self.ieee754_int_to_float(para["16"])))
        self.sf_1_slope.le.setText(str(self.ieee754_int_to_float(para["17"])))
        self.sf_1_offset.le.setText(str(self.ieee754_int_to_float(para["18"])))

        # self.err_th.spin.setValue(para["ERR_TH"])
        # self.HD_Q.spin.setValue(para["HD_Q"])
        # self.HD_R.spin.setValue(para["HD_R"])

        # self.dataRate_sd.sd.setValue(para["DATA_RATE"])
        # self.Tmin.spin.setValue(para["TMIN"])
        # self.Tmax.spin.setValue(para["TMAX"])
        # self.sf0.le.setText(str(para["SF0"]))
        # self.sf1.le.setText(str(para["SF1"]))
        # self.sf2.le.setText(str(para["SF2"]))
        # self.sf3.le.setText(str(para["SF3"]))
        # self.sf4.le.setText(str(para["SF4"]))
        # self.sf5.le.setText(str(para["SF5"]))
        # self.sf6.le.setText(str(para["SF6"]))
        # self.sf7.le.setText(str(para["SF7"]))
        # self.sf8.le.setText(str(para["SF8"]))
        # self.sf9.le.setText(str(para["SF9"]))
        # self.sfb.le.setText(str(para["SFB"]))
        # self.Tmin_lb.setText(str(para["TMIN"]))
        # self.Tmax_lb.setText(str(para["TMAX"]))
        # self.T1r_lb.setText(str(para["T1"]))
        # self.T1l_lb.setText(str(para["T1"]))
        # self.T2r_lb.setText(str(para["T2"]))
        # self.T2l_lb.setText(str(para["T2"]))
        # self.T3r_lb.setText(str(para["T3"]))
        # self.T3l_lb.setText(str(para["T3"]))
        # self.T4r_lb.setText(str(para["T4"]))
        # self.T4l_lb.setText(str(para["T4"]))
        # self.T5r_lb.setText(str(para["T5"]))
        # self.T5l_lb.setText(str(para["T5"]))
        # self.T6r_lb.setText(str(para["T6"]))
        # self.T6l_lb.setText(str(para["T6"]))
        # self.T7r_lb.setText(str(para["T7"]))
        # self.T7l_lb.setText(str(para["T7"]))
        pass

        # if not __name__ == "__main__":
        #     self.send_FREQ_CMD()
        #     self.send_WAIT_CNT_CMD()
        #     self.send_AVG_CMD()
        #     self.send_MOD_H_CMD()
        #     self.send_MOD_L_CMD()
        #     self.send_ERR_TH_CMD()
        #     self.send_ERR_OFFSET_CMD()
        #     self.send_POLARITY_CMD()
        #     self.send_CONST_STEP_CMD()
        #     # """
        #     self.update_FPGA_Q()
        #     self.update_FPGA_R()
        #     # """
        #     self.send_GAIN1_CMD()
        #     self.send_GAIN2_CMD()
        #     self.send_FB_ON_CMD()
        #     self.send_DAC_GAIN_CMD()
        #     self.send_DATA_RATE_CMD()
        #
        #     self.update_KF_Q()
        #     self.update_KF_R()
        #     self.SF_A_EDIT()
        #     self.SF_B_EDIT()

    def writeImuCmd(self, cmd, value, fog_ch):
        self.__act.writeImuCmd(cmd, value, fog_ch)

    def ieee754_int_to_float(self, int_value: int) -> float:
        """
        Convert a 32-bit IEEE-754 integer representation to a float.

        :param int_value: Integer representation of IEEE-754 float (32-bit)
        :return: Converted floating-point number
        """
        # Pack integer as 4 bytes, then unpack as a float
        return round(struct.unpack('!f', struct.pack('!I', int_value))[0], 7)

    def send_FREQ_CMD(self):
        # dt_fpga = 1e3 / 91e6  # for PLL set to 91MHz
        # dt_fpga = 1e3 / 90e6
        dt_fpga = 1e3 / 100e6
        # dt_fpga = 1e3/ 105e6 # for PLL set to 105MHz
        # dt_fpga = 1e3/ 107e6 # for PLL set to 107MHz
        # dt_fpga = 1e3/ 108.333333e6 # for PLL set to 109MHz
        value = self.freq.spin.value()
        logger.info('set freq: %d', value)
        self.freq.lb.setText(str(round(1 / (2 * (value + 1) * dt_fpga), 2)) + ' KHz')
        self.__act.writeImuCmd(CMD_FOG_MOD_FREQ, value)
        self.__par_manager.update_parameters("FREQ", value)

    def send_MOD_H_CMD(self):
        value = self.mod_H.spin.value()
        logger.info('set mod_H: %d', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_H, value)
        self.__par_manager.update_parameters("MOD_H", value)

    def send_MOD_L_CMD(self):
        value = self.mod_L.spin.value()
        logger.info('set mod_L: %d', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_L, value)
        self.__par_manager.update_parameters("MOD_L", value)

    def send_ERR_OFFSET_CMD(self):
        value = self.err_offset.spin.value()
        logger.info('set err offset: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_OFFSET, value)
        self.__par_manager.update_parameters("ERR_OFFSET", value)

    def send_POLARITY_CMD(self):
        value = self.polarity.spin.value()
        logger.info('set polarity: %d', value)
        self.__act.writeImuCmd(CMD_FOG_POLARITY, value)
        self.__par_manager.update_parameters("POLARITY", value)

    def send_WAIT_CNT_CMD(self):
        value = self.wait_cnt.spin.value()
        logger.info('set wait cnt: %d', value)
        self.__act.writeImuCmd(CMD_FOG_WAIT_CNT, value)
        self.__par_manager.update_parameters("WAIT_CNT", value)

    def send_ERR_TH_CMD(self):
        value = self.err_th.spin.value()
        logger.info('set err_th: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_TH, value)
        self.__par_manager.update_parameters("ERR_TH", value)

    def send_AVG_CMD(self):
        value = self.avg.spin.value()
        logger.info('set err_avg: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_AVG, value)
        self.__par_manager.update_parameters("ERR_AVG", value)

    def send_GAIN1_CMD(self):
        value = self.gain1.spin.value()
        logger.info('set gain1: %d', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN1, value)
        self.__par_manager.update_parameters("GAIN1", value)

    def send_GAIN2_CMD(self):
        value = self.gain2.spin.value()
        logger.info('set gain2: %d', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN2, value)
        self.__par_manager.update_parameters("GAIN2", value)

    def send_FB_ON_CMD(self):
        value = self.fb_on.spin.value()
        logger.info('set FB on: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FB_ON, value)
        # self.__act.writeImuCmd(CMD_FOG_FB_ON, 0)
        # self.__act.writeImuCmd(CMD_FOG_FB_ON, value)
        self.__par_manager.update_parameters("FB_ON", value)

    def send_DAC_GAIN_CMD(self):
        value = self.dac_gain.spin.value()
        logger.info('set DAC gain: %d', value)
        self.__act.writeImuCmd(CMD_FOG_DAC_GAIN, value)
        self.__par_manager.update_parameters("DAC_GAIN", value)

    def send_TMIN_CMD(self):
        value = self.Tmin.spin.value()
        value2 = struct.unpack('<I', struct.pack('<f', value))
        # logger.info('set DAC gain: %d', value)
        self.__act.writeImuCmd(CMD_FOG_TMIN, value2[0])
        # self.__par_manager.update_parameters("DAC_GAIN", value)
        print("%x" % value2[0])

    def send_TMAX_CMD(self):
        value = self.Tmax.spin.value()
        value2 = struct.unpack('<I', struct.pack('<f', value))
        # logger.info('set DAC gain: %d', value)
        self.__act.writeImuCmd(CMD_FOG_TMAX, value2[0])
        # self.__par_manager.update_parameters("DAC_GAIN", value)
        print("%x" % value2[0])

    def send_CUTOFF_CMD(self):
        value = self.cutoff.spin.value()
        logger.info('set CUTOFF : %d', value)
        # value2 = struct.unpack('<I', struct.pack('<f', value))
        # logger.info('set DAC gain: %d', value)
        self.__act.writeImuCmd(CMD_FOG_CUTOFF, value)
        # self.__par_manager.update_parameters("DAC_GAIN", value)
        # print("%d" % value)

    def send_SF_COMP_T1_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf_comp_T1.le.text())))
        print(value[0])
        self.__act.writeImuCmd(CMD_SF_COMP_T1, value[0])

    def send_SF_COMP_T2_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf_comp_T2.le.text())))
        print(value[0])
        self.__act.writeImuCmd(CMD_SF_COMP_T2, value[0])

    def send_SF_1_SLOPE(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf_1_slope.le.text())))
        print(value[0])
        self.__act.writeImuCmd(CMD_SF_1_SLOPE, value[0])

    def send_SF_1_OFFSET(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf_1_offset.le.text())))
        print(value[0])
        self.__act.writeImuCmd(CMD_SF_1_OFFSET, value[0])

    def send_SF3_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf3.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SF3, value[0])

    def send_SF4_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf4.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SF4, value[0])

    def send_SF5_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf5.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SF5, value[0])

    def send_SF6_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf6.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SF6, value[0])

    def send_SF7_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf7.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SF7, value[0])

    def send_SF8_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf8.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SF8, value[0])

    def send_SF9_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sf9.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SF9, value[0])

    def send_SFB_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.sfb.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB, value[0])

    def send_CONST_STEP_CMD(self):
        value = self.const_step.spin.value()
        logger.info('set constant step: %d', value)
        self.__act.writeImuCmd(CMD_FOG_CONST_STEP, value)
        self.__par_manager.update_parameters("CONST_STEP", value)

    def update_KF_Q(self):
        value = self.KF_Q.spin.value()
        logger.info('set KF_Q: %d', value)
        self.__act.kal_Q = value
        self.__par_manager.update_parameters("KF_Q", value)

    def update_KF_R(self):
        value = self.KF_R.spin.value()
        logger.info('set KF_R: %d', value)
        self.__act.kal_R = value
        self.__par_manager.update_parameters("KF_R", value)

    def update_FPGA_Q(self):
        value = self.HD_Q.spin.value()
        logger.info('set HD_Q: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FPGA_Q, value)
        self.__par_manager.update_parameters("HD_Q", value)

    def update_FPGA_R(self):
        value = self.HD_R.spin.value()
        logger.info('set HD_R: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FPGA_R, value)
        self.__par_manager.update_parameters("HD_R", value)

    def send_DATA_RATE_CMD(self):
        value = self.dataRate_sd.sd.value()
        logger.info('set dataRate: %d', value)
        self.__act.writeImuCmd(CMD_FOG_INT_DELAY, value)
        self.__par_manager.update_parameters("DATA_RATE", value)

    def SF_A_EDIT(self):
        value = float(self.sf_a.le.text())
        logger.info('set sf_a: %f', value)
        self.__act.sf_a = value
        self.__par_manager.update_parameters("SF_A", value)

    def SF_B_EDIT(self):
        value = float(self.sf_b.le.text())
        logger.info('set sf_b: %f', value)
        self.__act.sf_b = value
        self.__par_manager.update_parameters("SF_B", value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pig_parameters_widget("act")
    w.show()
    app.exec_()
