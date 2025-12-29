# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import re
import os
from myLib.logProcess import logProcess

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__

ExternalName_log = __name__
if os.getenv('verNum') == str(True) :
    ExternalName_log = "pmeter_logger"

logger = logging.getLogger(logger_name + '.' + ExternalName_log)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys
import struct
import numpy as np
import pandas as pd

sys.path.append("../../")
print(__name__)
print(sys.path)
from myLib.myGui.mygui_serial import *
from myLib import common as cmn
from myLib.myGui.myLabel import *
from PySide6 import QtWidgets
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLabel, QGridLayout, QMessageBox, QApplication
from PySide6.QtGui import QDoubleValidator
from myLib.logProcess import logProcess


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
CMD_FOG_SF0 = 26
CMD_FOG_SF1 = 27
CMD_FOG_SF2 = 28
CMD_FOG_SF3 = 29
CMD_FOG_SF4 = 30
CMD_FOG_SF5 = 31
CMD_FOG_SF6 = 32
CMD_FOG_SF7 = 33
CMD_FOG_SF8 = 34
CMD_FOG_SF9 = 35
CMD_FOG_TMIN = 36
CMD_FOG_TMAX = 37
CMD_FOG_SFB = 38
CMD_FOG_CUTOFF = 39
CMD_FOG_STD_WX = 48
CMD_FOG_STD_WY = 49
CMD_FOG_STD_WZ = 50

# Bias Temp
CMD_FOG_BIAS_T1 = 40
CMD_FOG_BIAS_T2 = 41
CMD_FOG_SFB_SLOPE_1 = 42
CMD_FOG_SFB_OFFSET_1 = 43
CMD_FOG_SFB_SLOPE_2 = 44
CMD_FOG_SFB_OFFSET_2 = 45
CMD_FOG_SFB_SLOPE_3 = 46
CMD_FOG_SFB_OFFSET_3 = 47

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

UPDate_Func = {
    "Func": np.array([])
}

class pig_parameters_widget(QGroupBox):
    def __init__(self, act, ver, fileName="default_fog_parameters.json"):
        super(pig_parameters_widget, self).__init__()
        print("import pigParameters")
        self.__act = act
        self.__ver = ver
        self.__modifiedItem = set()
        # self.__par_manager = cmn.parameters_manager(fileName, INIT_PARAMETERS, fnum=1)
        self.setWindowTitle("PIG parameters")
        self.resize(750, 600)
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
        # Vpi與voltage設定
        self.dac_Vpi = editBlock(title='Vπ')
        self.dac_Vpi.setFixedWidth(100)
        self.rst_voltage = editBlock(title='RST Voltage')
        self.rst_voltage.setFixedWidth(100)

        self.fb_on = spinBlock(title='mode(0:OPEN)', minValue=0, maxValue=2, double=False, step=1)
        self.err_th = spinBlock(title='ERR_TH', minValue=0, maxValue=16384, double=False, step=1)
        self.freq = spinBlockOneLabel(title='frequency', minValue=10, maxValue=1500, double=False, step=1)
        self.KF_Q = spinBlock(title='SW_Q', minValue=1, maxValue=100000, double=False, step=1)
        self.KF_R = spinBlock(title='SW_R', minValue=0, maxValue=100000, double=False, step=1)
        self.HD_Q = spinBlock(title='FPGA_Q', minValue=1, maxValue=100000, double=False, step=1)
        # self.HD_Q.setEnabled(False)
        self.HD_R = spinBlock(title='FPGA_R', minValue=0, maxValue=100000, double=False, step=1)
        # self.HD_R.setEnabled(False)
        self.Tmin = spinBlock(title='Tmin', minValue=-30, maxValue=30, double=False, step=5)
        self.Tmax = spinBlock(title='Tmax', minValue=30, maxValue=150, double=False, step=5)
        self.cutoff = spinBlock(title='CutOff', minValue=50, maxValue=1500, double=False, step=5)
        '''slider'''
        self.dataRate_sd = sliderBlock(title='DATE RATE', minValue=1500, maxValue=5000, curValue=2500, interval=100)
        '''edit line in the left side'''
        self.std_wx = editBlock("STD_Wx")
        self.std_wy = editBlock("STD_Wy")
        self.std_wz = editBlock("STD_Wz")
        ''' edit line '''
        self.sf0 = editBlock('STA') #SF0
        self.sf1 = editBlock('STB') #SF1
        self.sf2 = editBlock('SF2')
        self.sf3 = editBlock('SF3')
        self.sf4 = editBlock('SF4')
        self.sf5 = editBlock('SF5')
        self.sf6 = editBlock('SF6')
        self.sf7 = editBlock('SF7')
        self.sf8 = editBlock('SF8')
        self.sf9 = editBlock('SF9')
        self.sfb = editBlock('SFB')

        SFexplain = QLabel("Note: The values are displayed \nmultiplied by 10000.")
        self.SFTemp = QGroupBox("SF Temp Cali")

        qvbox = QVBoxLayout()
        qvbox.addWidget(SFexplain)
        qvbox.addWidget(self.sf0)
        qvbox.addWidget(self.sf1)
        qvbox.addStretch(1)
        self.SFTemp.setLayout(qvbox)

        self.BiasTemp = QGroupBox("Bias Temp Cali")
        BiasQvbox = QVBoxLayout()
        self.slope1 = editBlock("BTA1")
        self.slope2 = editBlock("BTA2")
        self.slope3 = editBlock("BTA3")
        self.offset1 = editBlock("BTB1")
        self.offset2=editBlock("BTB2")
        self.offset3 = editBlock("BTB3")
        self.T1 = editBlock("T1")
        self.T2 = editBlock("T2")
        BiasQvbox.addWidget(self.slope3)
        BiasQvbox.addWidget(self.offset3)
        BiasQvbox.addWidget(self.T2)
        BiasQvbox.addWidget(self.slope2)
        BiasQvbox.addWidget(self.offset2)
        BiasQvbox.addWidget(self.T1)
        BiasQvbox.addWidget(self.slope1)
        BiasQvbox.addWidget(self.offset1)
        BiasQvbox.addStretch(1)
        self.BiasTemp.setLayout(BiasQvbox)

        self.ACCLsta = editBlock('STA')
        self.ACCLstb = editBlock('STB')

        # 第四欄的控制項
        self.ACCLSFTemp = QGroupBox("ACCL SF Temp Cali(g)")
        ACCLqvbox = QVBoxLayout()
        ACCLqvbox.setContentsMargins(10, 10, 10, 10)
        ACCLqvbox.addWidget(self.ACCLsta)
        ACCLqvbox.addWidget(self.ACCLstb)
        self.ACCLSFTemp.setLayout(ACCLqvbox)

        self.ACCLBiasTemp = QGroupBox("ACCL Bias Temp Cali(g)")
        ACCLBiasqvbox = QVBoxLayout()
        ACCLBiasqvbox.setContentsMargins(10, 10, 10, 10)
        self.ACCL_slope1 = editBlock("BTA1")
        self.ACCL_slope2 = editBlock("BTA2")
        self.ACCL_slope3 = editBlock("BTA3")
        self.ACCL_offset1 = editBlock("BTB1")
        self.ACCL_offset2 = editBlock("BTB2")
        self.ACCL_offset3 = editBlock("BTB3")
        self.ACCL_T1 = editBlock("T1")
        self.ACCL_T2 = editBlock("T2")
        ACCLBiasqvbox.addWidget(self.ACCL_slope3)
        ACCLBiasqvbox.addWidget(self.ACCL_offset3)
        ACCLBiasqvbox.addWidget(self.ACCL_T2)
        ACCLBiasqvbox.addWidget(self.ACCL_slope2)
        ACCLBiasqvbox.addWidget(self.ACCL_offset2)
        ACCLBiasqvbox.addWidget(self.ACCL_T1)
        ACCLBiasqvbox.addWidget(self.ACCL_slope1)
        ACCLBiasqvbox.addWidget(self.ACCL_offset1)
        self.ACCLBiasTemp.setLayout(ACCLBiasqvbox)

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

        # update 用來儲存要更新的function
        self.upFunc = UPDate_Func
        self.updateBtn = QPushButton("Update")
        self.loadTempFileBtn = QPushButton("Load Temp File")

        self.initUI()
        # initPara = self.__act.dump_fog_parameters(2)
        # print(initPara)
        # self.set_init_value(initPara)
        # self.KF_Q.spin.setValue(1)
        # self.KF_R.spin.setValue(50)
        self.linkfunction()
        self.dumpTrigerState = False
        self.keyIsNetExist = False

    def initUI(self):
        mainWid = QWidget() # 用於將整個控制項畫面套到滑軌工具的介面中
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
        mainLayout.addWidget(self.HD_Q, 7, 0, 1, 2)
        mainLayout.addWidget(self.HD_R, 7, 2, 1, 2)
        # mainLayout.addWidget(self.KF_Q, 7, 0, 1, 2)
        # mainLayout.addWidget(self.KF_R, 7, 2, 1, 2)
        mainLayout.addWidget(self.cutoff, 8, 0, 1, 2)
        mainLayout.addWidget(self.std_wx, 8, 2, 1, 2)
        mainLayout.addWidget(self.std_wy, 9, 0, 1, 2)
        mainLayout.addWidget(self.std_wz, 9, 2, 1, 2)
        mainLayout.addWidget(self.dump_bt, 10, 0, 1, 2)
        mainLayout.addWidget(self.Firmware_Version_lb, 11, 0, 1, 4)
        mainLayout.addWidget(self.GUI_Version_lb, 12, 0, 1, 4)

        mainLayout.addWidget(self.SFTemp, 0, 4, 2, 1)
        mainLayout.addWidget(self.BiasTemp, 2, 4, 8, 1)
        mainLayout.addWidget(self.ACCLSFTemp, 0, 5, 2, 1)
        mainLayout.addWidget(self.ACCLBiasTemp, 2, 5, 8, 1)
        mainLayout.addWidget(self.loadTempFileBtn, 10, 4, 1, 1)
        mainLayout.addWidget(self.updateBtn, 11, 4, 1, 1)

        mainWid.setLayout(mainLayout)
        paraScroll = QScrollArea()
        paraScroll.setWidget(mainWid)

        scrollLayout = QVBoxLayout()
        scrollLayout.setContentsMargins(10, 10, 10, 10)
        scrollLayout.addWidget(paraScroll)
        self.setLayout(scrollLayout)

    def linkfunction(self):
        """Connect UI signals directly to command functions."""

        # ---- spin boxes ----
        self.wait_cnt.spin.valueChanged.connect(lambda *_: self.send_WAIT_CNT_CMD())
        self.avg.spin.valueChanged.connect(lambda *_: self.send_AVG_CMD())
        self.mod_H.spin.valueChanged.connect(lambda *_: self.send_MOD_H_CMD())
        self.mod_L.spin.valueChanged.connect(lambda *_: self.send_MOD_L_CMD())
        self.freq.spin.valueChanged.connect(lambda *_: self.send_FREQ_CMD())
        self.err_th.spin.valueChanged.connect(lambda *_: self.send_ERR_TH_CMD())
        self.err_offset.spin.valueChanged.connect(lambda *_: self.send_ERR_OFFSET_CMD())
        self.polarity.spin.valueChanged.connect(lambda *_: self.send_POLARITY_CMD())
        self.const_step.spin.valueChanged.connect(lambda *_: self.send_CONST_STEP_CMD())
        # self.KF_Q.spin.valueChanged.connect(lambda *_: self.send_KF_Q_CMD())
        # self.KF_R.spin.valueChanged.connect(lambda *_: self.send_KF_R_CMD())
        self.HD_Q.spin.valueChanged.connect(lambda *_: self.update_FPGA_Q())
        self.HD_R.spin.valueChanged.connect(lambda *_: self.update_FPGA_R())
        self.gain1.spin.valueChanged.connect(lambda *_: self.send_GAIN1_CMD())
        self.gain2.spin.valueChanged.connect(lambda *_: self.send_GAIN2_CMD())
        self.fb_on.spin.valueChanged.connect(lambda *_: self.send_FB_ON_CMD())
        self.dac_gain.spin.valueChanged.connect(lambda *_: self.send_DAC_GAIN_CMD())
        self.cutoff.spin.valueChanged.connect(lambda *_: self.send_CUTOFF_CMD())

        # ---- line edits (editingFinished: 無參數；textChanged: 會帶 str) ----
        # 若希望在「離開輸入框」時送出，用 editingFinished：
        self.sf0.le.editingFinished.connect(lambda: self.send_SF0_CMD())
        self.sf1.le.editingFinished.connect(lambda: self.send_SF1_CMD())

        # 若希望「文字一改就送」，用 textChanged：
        self.T1.le.textChanged.connect(lambda *_: self.send_BIAS_T1_CMD())
        self.T2.le.textChanged.connect(lambda *_: self.send_BIAS_T2_CMD())
        self.slope1.le.textChanged.connect(lambda *_: self.send_SFB_SLOPE_1_CMD())
        self.slope2.le.textChanged.connect(lambda *_: self.send_SFB_SLOPE_2_CMD())
        self.slope3.le.textChanged.connect(lambda *_: self.send_SFB_SLOPE_3_CMD())
        self.offset1.le.textChanged.connect(lambda *_: self.send_SFB_OFFSET_1_CMD())
        self.offset2.le.textChanged.connect(lambda *_: self.send_SFB_OFFSET_2_CMD())
        self.offset3.le.textChanged.connect(lambda *_: self.send_SFB_OFFSET_3_CMD())

        self.std_wx.le.textChanged.connect(lambda *_: self.send_STD_Wx_CMD())
        self.std_wy.le.textChanged.connect(lambda *_: self.send_STD_Wy_CMD())
        self.std_wz.le.textChanged.connect(lambda *_: self.send_STD_Wz_CMD())

        # ---- buttons (clicked(bool)) ----
        self.dump_bt.clicked.connect(lambda *_: self.dump_parameter())
        self.updateBtn.clicked.connect(lambda *_: self.update_changevalue())
        self.loadTempFileBtn.clicked.connect(lambda *_: self.loadCSVandWriteBias())

    # def linkfunction(self):
    #     ''' spin box connect'''
    #     self.wait_cnt.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.wait_cnt.spin, self.send_WAIT_CNT_CMD))
    #     self.avg.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.avg.spin, self.send_AVG_CMD))
    #     self.mod_H.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.mod_H.spin, self.send_MOD_H_CMD))
    #     self.mod_L.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.mod_L.spin, self.send_MOD_L_CMD))
    #     self.freq.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.freq.spin, self.send_FREQ_CMD))
    #     self.err_th.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.err_th.spin, self.send_ERR_TH_CMD))
    #     self.err_offset.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.err_offset.spin, self.send_ERR_OFFSET_CMD))
    #     self.polarity.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.polarity.spin, self.send_POLARITY_CMD))
    #     self.const_step.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.const_step.spin, self.send_CONST_STEP_CMD))
    #     # self.KF_Q.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.KF_Q.spin))
    #     # self.KF_R.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.KF_R.spin))
    #     self.HD_Q.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.HD_Q.spin, self.update_FPGA_Q))
    #     self.HD_R.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.HD_R.spin, self.update_FPGA_R))
    #     self.gain1.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.gain1.spin, self.send_GAIN1_CMD))
    #     self.gain2.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.gain2.spin, self.send_GAIN2_CMD))
    #     self.fb_on.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.fb_on.spin, self.send_FB_ON_CMD))
    #     self.dac_gain.spin.valueChanged.connect(lambda:self.selectcontrolchangecolor(self.dac_gain.spin, self.send_DAC_GAIN_CMD))
    #     self.cutoff.spin.valueChanged.connect(lambda: self.selectcontrolchangecolor(self.cutoff.spin, self.send_CUTOFF_CMD))
    #     # ''' slider '''
    #     # self.dataRate_sd.sd.valueChanged.connect(self.send_DATA_RATE_CMD)
    #     ''' line edit '''
    #     # self.sf_a.le.editingFinished.connect(self.SF_A_EDIT)
    #     # self.sf_b.le.editingFinished.connect(self.SF_B_EDIT)
    #     # self.sf_all.le.editingFinished.connect(self.send_SF_ALL_CMD)
    #     self.sf0.le.editingFinished.connect(lambda: self.selectcontrolchangecolor(self.sf0.le, self.send_SF0_CMD))
    #     self.sf1.le.editingFinished.connect(lambda: self.selectcontrolchangecolor(self.sf1.le, self.send_SF1_CMD))
    #
    #     self.T1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.T1.le, self.send_BIAS_T1_CMD))
    #     self.T2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.T2.le, self.send_BIAS_T2_CMD))
    #     self.slope1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.slope1.le, self.send_SFB_SLOPE_1_CMD))
    #     self.slope2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.slope2.le, self.send_SFB_SLOPE_2_CMD))
    #     self.slope3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.slope3.le, self.send_SFB_SLOPE_3_CMD))
    #     self.offset1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.offset1.le, self.send_SFB_OFFSET_1_CMD))
    #     self.offset2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.offset2.le, self.send_SFB_OFFSET_2_CMD))
    #     self.offset3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.offset3.le, self.send_SFB_OFFSET_3_CMD))
    #
    #     self.std_wx.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.std_wx.le, self.send_STD_Wx_CMD))
    #     self.std_wy.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.std_wy.le, self.send_STD_Wy_CMD))
    #     self.std_wz.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.std_wz.le, self.send_STD_Wz_CMD))
    #
    #     ''' bt'''
    #     self.dump_bt.clicked.connect(self.dump_parameter)
    #     self.updateBtn.clicked.connect(self.update_changevalue)
    #     self.loadTempFileBtn.clicked.connect(self.loadCSVandWriteBias)


    def dump_parameter(self):
        self.cleanItemPropertyVal()
        self.__act.flushInputBuffer()
        initPara = self.__act.dump_fog_parameters(2)
        # print(initPara)
        if type(initPara) == dict:
            self.set_init_value(initPara)
            self.getVersion()
            self.dumpTrigerState = True
        elif type(initPara) == bool:
            self.mesboxProcess("warning", "Error occurred while in dump", "Please check if the device has power.")


    def getVersion(self):
        self.__act.flushInputBuffer()
        self.Firmware_Version_lb.setText(self.__act.getVersion(2))
        self.GUI_Version_lb.setText(self.__ver)

    def selectcontrolchangecolor(self, control, send_item_func):
        control.setStyleSheet('background-color:yellow')

        clickBtnObj = self.sender()
        if not hasattr(clickBtnObj, 'text') or clickBtnObj.text() == "Load Temp File":
            if send_item_func not in self.__modifiedItem and send_item_func != None:
                self.__modifiedItem.add(send_item_func)


    def controlchangewhite(self):
        if self.wait_cnt.spin.styleSheet() != "border: 1px solid red;": self.wait_cnt.spin.setStyleSheet('background-color:white')
        if self.avg.spin.styleSheet() != "border: 1px solid red;": self.avg.spin.setStyleSheet('background-color:white')
        if self.mod_H.spin.styleSheet() != "border: 1px solid red;": self.mod_H.spin.setStyleSheet('background-color: white')
        if self.mod_L.spin.styleSheet() != "border: 1px solid red;": self.mod_L.spin.setStyleSheet('background-color: white')
        if self.freq.spin.styleSheet() != "border: 1px solid red;": self.freq.spin.setStyleSheet('background-color:white')
        if self.err_th.spin.styleSheet() != "border: 1px solid red;": self.err_th.spin.setStyleSheet('background-color: white')
        if self.err_offset.spin.styleSheet() != "border: 1px solid red;": self.err_offset.spin.setStyleSheet('background-color: white')
        if self.polarity.spin.styleSheet() != "border: 1px solid red;": self.polarity.spin.setStyleSheet('background-color: white')
        if self.const_step.spin.styleSheet() != "border: 1px solid red;": self.const_step.spin.setStyleSheet('background-color: white')
        # if self.KF_Q.spin.styleSheet() != "border: 1px solid red;": self.KF_Q.spin.setStyleSheet('background-color: white')
        # if self.KF_R.spin.styleSheet() != "border: 1px solid red;": self.KF_R.spin.setStyleSheet('background-color: white')
        if self.HD_Q.spin.styleSheet() != "border: 1px solid red;": self.HD_Q.spin.setStyleSheet('background-color: white')
        if self.HD_R.spin.styleSheet() != "border: 1px solid red;": self.HD_R.spin.setStyleSheet('background-color: white')
        if self.gain1.spin.styleSheet() != "border: 1px solid red;": self.gain1.spin.setStyleSheet('background-color: white')
        if self.gain2.spin.styleSheet() != "border: 1px solid red;": self.gain2.spin.setStyleSheet('background-color: white')
        if self.fb_on.spin.styleSheet() != "border: 1px solid red;": self.fb_on.spin.setStyleSheet('background-color: white')
        if self.dac_gain.spin.styleSheet() != "border: 1px solid red;": self.dac_gain.spin.setStyleSheet('background-color: white')
        if self.cutoff.spin.styleSheet() != "border: 1px solid red;": self.cutoff.spin.setStyleSheet('background-color: white')
        if self.std_wx.le.styleSheet() != "border: 1px solid red;": self.std_wx.le.setStyleSheet('background-color: white')
        if self.std_wy.le.styleSheet() != "border: 1px solid red;": self.std_wy.le.setStyleSheet('background-color: white')
        if self.std_wz.le.styleSheet() != "border: 1px solid red;": self.std_wz.le.setStyleSheet('background-color: white')
        if self.sf0.le.styleSheet() != "border: 1px solid red;": self.sf0.le.setStyleSheet('background-color: white')
        if self.sf1.le.styleSheet() != "border: 1px solid red;": self.sf1.le.setStyleSheet('background-color: white')
        if self.T1.le.styleSheet() != "border: 1px solid red;": self.T1.le.setStyleSheet('background-color: white')
        if self.T2.le.styleSheet() != "border: 1px solid red;": self.T2.le.setStyleSheet('background-color: white')
        if self.slope1.le.styleSheet() != "border: 1px solid red;": self.slope1.le.setStyleSheet('background-color: white')
        if self.slope2.le.styleSheet() != "border: 1px solid red;": self.slope2.le.setStyleSheet('background-color: white')
        if self.slope3.le.styleSheet() != "border: 1px solid red;": self.slope3.le.setStyleSheet('background-color: white')
        if self.offset1.le.styleSheet() != "border: 1px solid red;": self.offset1.le.setStyleSheet('background-color: white')
        if self.offset2.le.styleSheet() != "border: 1px solid red;": self.offset2.le.setStyleSheet('background-color: white')
        if self.offset3.le.styleSheet() != "border: 1px solid red;": self.offset3.le.setStyleSheet('background-color: white')


    def update_changevalue(self):
        mesbox = QtWidgets.QMessageBox()
        mesbox.setIcon(QMessageBox.Question)
        mesbox.setWindowTitle("確認是否要更新數值")
        mesbox.setText("請確認被選中的控制項都是要修改數值嗎?")
        mesbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mesbox.setDefaultButton(QtWidgets.QMessageBox.Yes)
        mes_result = mesbox.exec_()

        if mes_result == QMessageBox.Yes:
            self.updatelink()
        elif mes_result == QMessageBox.No:
            pass

    def updatelink(self):
        if self.dumpTrigerState == True:
            for itemFunc in self.__modifiedItem:
                itemFunc()
            # self.send_WAIT_CNT_CMD()
            # self.send_AVG_CMD()
            # self.send_MOD_H_CMD()
            # self.send_MOD_L_CMD()
            # self.send_FREQ_CMD()
            # self.send_ERR_TH_CMD()
            # self.send_ERR_OFFSET_CMD()
            # self.send_POLARITY_CMD()
            # self.send_CONST_STEP_CMD()
            # self.update_KF_Q()
            # self.update_KF_R()
            # self.update_FPGA_Q()
            # self.update_FPGA_R()
            # self.send_GAIN1_CMD()
            # self.send_GAIN2_CMD()
            # self.send_FB_ON_CMD()
            # self.send_DAC_GAIN_CMD()
            # self.send_CUTOFF_CMD()
            # ''' slider '''
            # self.send_DATA_RATE_CMD()
            # self.send_SF0_CMD()
            # self.send_SF1_CMD()
            # self.send_BIAS_T1_CMD()
            # self.send_BIAS_T2_CMD()
            # self.send_SFB_SLOPE_1_CMD()
            # self.send_SFB_SLOPE_2_CMD()
            # self.send_SFB_SLOPE_3_CMD()
            # self.send_SFB_OFFSET_1_CMD()
            # self.send_SFB_OFFSET_2_CMD()
            # self.send_SFB_OFFSET_3_CMD()
            # 將背景顏色轉回白色
            self.controlchangewhite()
            self.__modifiedItem.clear()
            self.mesboxProcess("info", "更新完成資訊", "已更新完所有被修改的設備參數。")
            self.keyExistOrNotMes("parameter參數值")
            self.keyIsNetExist = False
        # func()
        else:
            self.mesboxProcess("warning", "update按鈕錯誤警告", "請確認是否已經點擊過dump按鈕，或是已經將設備的\n參數回填至控制項中，且數據已經顯示於畫面。")


    def checkKeyExist(self, para, key):
        # try:
        #     val = para.get(str(key))
        # except TypeError:
        #     return 0
        # except Exception:
        #     return 0
        #
        #
        try:
            # 使用dump或是load file，都會先由這邊取值，再做後續判斷與處理。
            val = para.get(str(key))
            # load csv檔案
            if "TEMP Breakpoints" in para:
                if not isinstance(val.iloc[1], float) and not isinstance(val.iloc[3], float):
                    return 0
            if "slope" in para or "offset" in para:
                if not isinstance(val.iloc[0], float) and not isinstance(val.iloc[2], float) and not isinstance(val.iloc[4], float):
                    return 0
        except Exception as e:
            # tb = e.__traceback__  # 錯誤軌跡資訊
            # logProcess.centrailzedError(num="", fileName=ExternalName_log, content=f"{type(e).__name__}--檢查'key是否存在'的判斷出現錯誤。", line=tb.tb_lineno)
            logger.error(f"{type(e).__name__}--檢查'key是否存在'的判斷出現錯誤。")
            self.keyIsNetExist = True
            return 0

        if not isinstance(val, pd.Series):
            if val == None:
                self.keyIsNetExist = True
                return None
            if val == "nan" or val == '':
                logger.info("參數值為空的狀況，故回傳數值0代替空值。")
                return 0  # 回傳0是因為有些控制項無法顯示文字或空值的狀況
        return val

    def loadCSVandWriteBias(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", "All Files (*);;", options=options)
        if filename != "":
            biasData = cmn.loadCSVFile(filename)
            tempVal = self.checkKeyExist(biasData, "TEMP Breakpoints")
            slopeVal = self.checkKeyExist(biasData, "slope")
            offsetVal = self.checkKeyExist(biasData, "offset")

            if isinstance(tempVal, pd.Series) and isinstance(slopeVal, pd.Series) and isinstance(offsetVal, pd.Series):
                try:
                    self.T1.le.setText(f'{tempVal[3]:.1f}')
                    self.T2.le.setText(f'{tempVal[1]:.1f}')

                    self.slope1.le.setText(f'{slopeVal[4]:.10f}'.rstrip('0').rstrip('.'))
                    self.slope2.le.setText(f'{slopeVal[4]:.10f}'.rstrip('0').rstrip('.'))
                    self.slope3.le.setText(f'{slopeVal[0]:.10f}'.rstrip('0').rstrip('.'))
                    self.offset1.le.setText(f'{offsetVal[4]:.10f}'.rstrip('0').rstrip('.'))
                    self.offset2.le.setText(f'{offsetVal[2]:.10f}'.rstrip('0').rstrip('.'))
                    self.offset3.le.setText(f'{offsetVal[0]:.10f}'.rstrip('0').rstrip('.'))
                except Exception as e:
                    self.keyIsNetExist = True
                    logger.error(f"{type(e).__name__}--載入CSV數據的功能出現錯誤。")
            else:
                self.keyIsNetExist = True
            self.keyExistOrNotMes("load Bias CSV")
            self.keyIsNetExist = False

    def keyExistOrNotMes(self, name):
        if self.keyIsNetExist:
            if name == "parameter參數值":
                self.mesboxProcess("warning", name+"有不存在的狀況", "在取parameter參數值的狀況時，因設備版號為舊的部分，\n"
                                                              "而GUI為最新版本未有撈取舊參數值，所以訊息通知使用者\n"
                                                              "有些參數若為0或空值，代表該參數在舊版本的設備中未使\n"
                                                              "用，因此撈取不到正確的參數。")
            else:
                self.mesboxProcess("warning", name+"有不存在的狀況", "請確認使用的CSV檔案內容標題是否有問題。")


    def updateControl(self, controlItem, para, keyVal):
        if not controlItem.property("called_once"):
            try:
                Val = self.checkKeyExist(para, keyVal)
                if isinstance(controlItem, QSpinBox):
                    controlItem.setValue(Val) if Val != None else controlItem.setStyleSheet("border: 1px solid red;")
                if isinstance(controlItem, QDoubleSpinBox):
                    controlItem.setValue(Val) if Val != None else controlItem.setStyleSheet("border: 1px solid red;")
                if isinstance(controlItem, QLineEdit):
                    if keyVal == "SF0" or keyVal == "SF1":
                        controlItem.setText(f'{(Val * 10000):.6f}'.rstrip('0').rstrip('.'))  if Val != None else controlItem.setStyleSheet("border: 1px solid red;")
                    elif "T1" in keyVal or "T2" in keyVal:
                        controlItem.setText(f'{Val:.1f}'.rstrip('0').rstrip('.')) if Val != None else controlItem.setStyleSheet("border: 1px solid red;")
                    else:
                        controlItem.setText(f'{Val:.10f}'.rstrip('0').rstrip('.')) if Val != None else controlItem.setStyleSheet("border: 1px solid red;")
                if isinstance(controlItem, QSlider):
                    if Val != None: controlItem.setValue(Val)

                controlItem.setProperty("called_once", True)
            except TypeError as e:
                logger.error(f"請確認計算使用的變數數值，是否型態是相同的。")
        else:
            logger.debug("重複使用控制項了，請確認程式碼是否有使用到重複的控制項。")

    def cleanItemPropertyVal(self):
        for item in self.findChildren(QSpinBox):
            if item.property("called_once"):
                item.setProperty("called_once", None)

    def set_init_value(self, para):
        self.updateControl(self.freq.spin, para, "FREQ")
        self.updateControl(self.wait_cnt.spin, para, "WAIT_CNT")
        self.updateControl(self.avg.spin, para, "ERR_AVG")
        self.updateControl(self.mod_H.spin, para, "MOD_H")
        self.updateControl(self.mod_L.spin, para, "MOD_L")
        self.updateControl(self.err_th.spin, para, "ERR_TH")
        self.updateControl(self.err_offset.spin, para, "ERR_OFFSET")
        self.updateControl(self.polarity.spin, para, "POLARITY")
        self.updateControl(self.const_step.spin, para, "CONST_STEP")
        self.updateControl(self.HD_Q.spin, para, "HD_Q")
        self.updateControl(self.HD_R.spin, para, "HD_R")
        self.updateControl(self.gain1.spin, para, "GAIN1")
        self.updateControl(self.gain2.spin, para, "GAIN2")
        self.updateControl(self.cutoff.spin, para, "CUTOFF")
        self.updateControl(self.fb_on.spin, para, "FB_ON")
        self.updateControl(self.dac_gain.spin, para, "DAC_GAIN")
        self.updateControl(self.std_wx.le, para, "STD_Wx")
        self.updateControl(self.std_wy.le, para, "STD_Wy")
        self.updateControl(self.std_wz.le, para, "STD_Wz")
        # self.updateControl(self.dataRate_sd.sd, para, "DATA_RATE")
        # freqVal = self.checkKeyExist(para, "FREQ")
        # if freqVal != "": self.freq.spin.setValue(freqVal)
        # waitCNT = self.checkKeyExist(para, "WAIT_CNT")
        # if waitCNT != "": self.wait_cnt.spin.setValue(waitCNT)
        # errAVG = self.checkKeyExist(para, "ERR_AVG")
        # if errAVG != "": self.avg.spin.setValue(errAVG)
        # modH = self.checkKeyExist(para, "MOD_H")
        # if modH != "": self.mod_H.spin.setValue(modH)
        # modL = self.checkKeyExist(para, "MOD_L")
        # if modL != "": self.mod_L.spin.setValue(modL)
        # errTH = self.checkKeyExist(para, "ERR_TH")
        # if errTH != "": self.err_th.spin.setValue(errTH)
        # errOFFSET = self.checkKeyExist(para, "ERR_OFFSET")
        # if errOFFSET != "": self.err_offset.spin.setValue(errOFFSET)
        # polarityVal = self.checkKeyExist(para, "POLARITY")
        # if polarityVal != "": self.polarity.spin.setValue(polarityVal)
        # constSTEP = self.checkKeyExist(para, "CONST_STEP")
        # if constSTEP != "": self.const_step.spin.setValue(constSTEP)
        # hdQ = self.checkKeyExist(para, "HD_Q")
        # if hdQ != "": self.HD_Q.spin.setValue(hdQ)
        # hdR = self.checkKeyExist(para, "HD_R")
        # if hdR != "": self.HD_R.spin.setValue(hdR)
        # gain1Val = self.checkKeyExist(para, "GAIN1")
        # if gain1Val != "": self.gain1.spin.setValue(gain1Val)
        # gain2Val = self.checkKeyExist(para, "GAIN2")
        # if gain2Val != "": self.gain2.spin.setValue(gain2Val)
        # cutOFF = self.checkKeyExist(para, "CUTOFF")
        # if cutOFF != "": self.cutoff.spin.setValue(cutOFF)
        # self.fb_on.spin.setValue(self.checkKeyExist(para, "FB_ON"))
        # self.dac_gain.spin.setValue(self.checkKeyExist(para, "DAC_GAIN"))
        # self.dataRate_sd.sd.setValue(self.checkKeyExist(para, "DATA_RATE"))
        # # self.Tmin.spin.setValue(para["TMIN"])
        # self.Tmax.spin.setValue(para["TMAX"])
        self.updateControl(self.sf0.le, para, "SF0")
        self.updateControl(self.sf1.le, para, "SF1")
        self.updateControl(self.T1.le, para, "BIAS_COMP_T1")
        self.updateControl(self.T2.le, para, "BIAS_COMP_T2")
        self.updateControl(self.slope1.le, para, "SFB_1_SLOPE")
        self.updateControl(self.slope2.le, para, "SFB_2_SLOPE")
        self.updateControl(self.slope3.le, para, "SFB_3_SLOPE")
        self.updateControl(self.offset1.le, para, "SFB_1_OFFSET")
        self.updateControl(self.offset2.le, para, "SFB_2_OFFSET")
        self.updateControl(self.offset3.le, para, "SFB_3_OFFSET")
        # sf0_val = self.checkKeyExist(para, "SF0")
        # if sf0_val != "": self.sf0.le.setText(f'{(sf0_val * 10000):.6f}'.rstrip('0').rstrip('.'))
        # sf1_val = self.checkKeyExist(para, "SF1")
        # # if sf1_val != "": self.sf1.le.setText(f'{(sf1_val * 10000):.6f}'.rstrip('0').rstrip('.'))
        # self.T1.le.setText(f'{self.checkKeyExist(para, "BIAS_COMP_T1"):.1f}'.rstrip('0').rstrip('.'))
        # self.T2.le.setText(f'{self.checkKeyExist(para, "BIAS_COMP_T2"):.1f}'.rstrip('0').rstrip('.'))
        # self.slope1.le.setText(f'{self.checkKeyExist(para, "SFB_1_SLOPE"):.10f}'.rstrip('0').rstrip('.'))
        # self.slope2.le.setText(f'{self.checkKeyExist(para, "SFB_2_SLOPE"):.10f}'.rstrip('0').rstrip('.'))
        # self.slope3.le.setText(f'{self.checkKeyExist(para, "SFB_3_SLOPE"):.10f}'.rstrip('0').rstrip('.'))
        # self.offset1.le.setText(f'{self.checkKeyExist(para, "SFB_1_OFFSET"):.10f}'.rstrip('0').rstrip('.'))
        # self.offset2.le.setText(f'{self.checkKeyExist(para, "SFB_2_OFFSET"):.10f}'.rstrip('0').rstrip('.'))
        # self.offset3.le.setText(f'{self.checkKeyExist(para, "SFB_3_OFFSET"):.10f}'.rstrip('0').rstrip('.'))

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
        # pass
        if not __name__ == "__main__":
            self.controlchangewhite()
            self.keyExistOrNotMes("parameter參數值")
            self.keyIsNetExist = False
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

    def mesboxProcess(self, status, title, content):
        mesbox = QMessageBox(self)
        if status == "warning":
            mesbox.warning(self, title, content)
        if status == "info":
            mesbox.information(self, title, content)

    def writeImuCmd(self, cmd, value, fog_ch):
        self.__act.writeImuCmd(cmd, value, fog_ch)

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
        # self.__par_manager.update_parameters("FREQ", value)

    def send_MOD_H_CMD(self):
        value = self.mod_H.spin.value()
        logger.info('set mod_H: %d', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_H, value)
        # self.__par_manager.update_parameters("MOD_H", value)

    def send_MOD_L_CMD(self):
        value = self.mod_L.spin.value()
        logger.info('set mod_L: %d', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_L, value)
        # self.__par_manager.update_parameters("MOD_L", value)

    def send_ERR_OFFSET_CMD(self):
        value = self.err_offset.spin.value()
        logger.info('set err offset: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_OFFSET, value)
        # self.__par_manager.update_parameters("ERR_OFFSET", value)

    def send_POLARITY_CMD(self):
        value = self.polarity.spin.value()
        logger.info('set polarity: %d', value)
        self.__act.writeImuCmd(CMD_FOG_POLARITY, value)
        # self.__par_manager.update_parameters("POLARITY", value)

    def send_WAIT_CNT_CMD(self):
        value = self.wait_cnt.spin.value()
        logger.info('set wait cnt: %d', value)
        self.__act.writeImuCmd(CMD_FOG_WAIT_CNT, value)
        # self.__par_manager.update_parameters("WAIT_CNT", value)

    def send_ERR_TH_CMD(self):
        value = self.err_th.spin.value()
        logger.info('set err_th: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_TH, value)
        # self.__par_manager.update_parameters("ERR_TH", value)

    def send_AVG_CMD(self):
        value = self.avg.spin.value()
        logger.info('set err_avg: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_AVG, value)
        # self.__par_manager.update_parameters("ERR_AVG", value)

    def send_GAIN1_CMD(self):
        value = self.gain1.spin.value()
        logger.info('set gain1: %d', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN1, value)
        # self.__par_manager.update_parameters("GAIN1", value)

    def send_GAIN2_CMD(self):
        value = self.gain2.spin.value()
        logger.info('set gain2: %d', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN2, value)
        # self.__par_manager.update_parameters("GAIN2", value)

    def send_FB_ON_CMD(self):
        value = self.fb_on.spin.value()
        logger.info('set FB on: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FB_ON, value)
        # self.__act.writeImuCmd(CMD_FOG_FB_ON, 0)
        # self.__act.writeImuCmd(CMD_FOG_FB_ON, value)
        # self.__par_manager.update_parameters("FB_ON", value)

    def send_DAC_GAIN_CMD(self):
        value = self.dac_gain.spin.value()
        logger.info('set DAC gain: %d', value)
        self.__act.writeImuCmd(CMD_FOG_DAC_GAIN, value)
        # self.__par_manager.update_parameters("DAC_GAIN", value)

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
        self.__act.writeImuCmd(CMD_FOG_CUTOFF, value)
        # self.__par_manager.update_parameters("DAC_GAIN", value)
        # print("%d" % value)

    def send_STD_Wx_CMD(self):
        logger.info(f'set STD_Wx : {float(self.std_wx.le.text())}')
        value = struct.unpack('<I', struct.pack('<f', float(self.std_wx.le.text())))
        self.__act.writeImuCmd(CMD_FOG_STD_WX, value[0])
        print("%x" % value[0])

    def send_STD_Wy_CMD(self):
        logger.info(f'set STD_Wy : {float(self.std_wy.le.text())}')
        value = struct.unpack('<I', struct.pack('<f', float(self.std_wy.le.text())))
        self.__act.writeImuCmd(CMD_FOG_STD_WY, value[0])

    def send_STD_Wz_CMD(self):
        logger.info(f'set STD_Wz : {float(self.std_wz.le.text())}')
        value = struct.unpack('<I', struct.pack('<f', float(self.std_wz.le.text())))
        self.__act.writeImuCmd(CMD_FOG_STD_WZ, value[0])

    def send_SF0_CMD(self):
        Re_sf0Val = float(self.sf0.le.text()) * 0.0001  # 與AA同方式
        logger.info('set SFA : %d', Re_sf0Val)
        value = struct.unpack('<I', struct.pack('<f', Re_sf0Val))
        self.__act.writeImuCmd(CMD_FOG_SF0, value[0])

    def send_SF1_CMD(self):
        Re_sf1Val = float(self.sf1.le.text()) * 0.0001  # 與AA同方式
        logger.info('set SFB : %d', Re_sf1Val)
        value = struct.unpack('<I', struct.pack('<f', Re_sf1Val))
        self.__act.writeImuCmd(CMD_FOG_SF1, value[0])

    # def send_SF2_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf2.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SF2, value[0])
    #
    # def send_SF3_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf3.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SF3, value[0])
    #
    # def send_SF4_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf4.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SF4, value[0])
    #
    # def send_SF5_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf5.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SF5, value[0])
    #
    # def send_SF6_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf6.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SF6, value[0])
    #
    # def send_SF7_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf7.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SF7, value[0])
    #
    # def send_SF8_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf8.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SF8, value[0])
    #
    # def send_SF9_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf9.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SF9, value[0])
    #
    # def send_SFB_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sfb.le.text())))
    #     self.__act.writeImuCmd(CMD_FOG_SFB, value[0])

    def send_BIAS_T1_CMD(self):
        logger.info('set BIAS T1 : %d', float(self.T1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.T1.le.text())))
        self.__act.writeImuCmd(CMD_FOG_BIAS_T1, value[0])

    def send_BIAS_T2_CMD(self):
        logger.info('set BIAS T2 : %d', float(self.T2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.T2.le.text())))
        self.__act.writeImuCmd(CMD_FOG_BIAS_T2, value[0])

    def send_SFB_SLOPE_1_CMD(self):
        logger.info('set BIAS SF SLOPE1 : %d', float(self.slope1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.slope1.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_1, value[0])

    def send_SFB_SLOPE_2_CMD(self):
        logger.info('set BIAS SF SLOPE2 : %d', float(self.slope2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.slope2.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_2, value[0])

    def send_SFB_SLOPE_3_CMD(self):
        logger.info('set BIAS SF SLOPE3 : %d', float(self.slope3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.slope3.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_3, value[0])

    def send_SFB_OFFSET_1_CMD(self):
        logger.info('set BIAS SF OFFSET1 : %d', float(self.offset1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.offset1.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_1, value[0])

    def send_SFB_OFFSET_2_CMD(self):
        logger.info('set BIAS SF OFFSET2 : %d', float(self.offset2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.offset2.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_2, value[0])

    def send_SFB_OFFSET_3_CMD(self):
        logger.info('set BIAS SF OFFSET3 : %d', float(self.offset3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.offset3.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_3, value[0])

    def send_CONST_STEP_CMD(self):
        value = self.const_step.spin.value()
        logger.info('set constant step: %d', value)
        self.__act.writeImuCmd(CMD_FOG_CONST_STEP, value)
        # self.__par_manager.update_parameters("CONST_STEP", value)

    def update_KF_Q(self):
        value = self.KF_Q.spin.value()
        logger.info('set KF_Q: %d', value)
        self.__act.kal_Q = value
        # self.__par_manager.update_parameters("KF_Q", value)

    def update_KF_R(self):
        value = self.KF_R.spin.value()
        logger.info('set KF_R: %d', value)
        self.__act.kal_R = value
        # self.__par_manager.update_parameters("KF_R", value)

    def update_FPGA_Q(self):
        value = self.HD_Q.spin.value()
        logger.info('set HD_Q: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FPGA_Q, value)
        # self.__par_manager.update_parameters("HD_Q", value)

    def update_FPGA_R(self):
        value = self.HD_R.spin.value()
        logger.info('set HD_R: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FPGA_R, value)
        # self.__par_manager.update_parameters("HD_R", value)

    def send_DATA_RATE_CMD(self):
        value = self.dataRate_sd.sd.value()
        logger.info('set dataRate: %d', value)
        self.__act.writeImuCmd(CMD_FOG_INT_DELAY, value)
        # self.__par_manager.update_parameters("DATA_RATE", value)

    def SF_A_EDIT(self):
        value = float(self.sf_a.le.text())
        logger.info('set sf_a: %f', value)
        self.__act.sf_a = value
        # self.__par_manager.update_parameters("SF_A", value)

    def SF_B_EDIT(self):
        value = float(self.sf_b.le.text())
        logger.info('set sf_b: %f', value)
        self.__act.sf_b = value
        # self.__par_manager.update_parameters("SF_B", value)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = pig_parameters_widget("act", "test-01")
    w.show()
    app.exec_()
