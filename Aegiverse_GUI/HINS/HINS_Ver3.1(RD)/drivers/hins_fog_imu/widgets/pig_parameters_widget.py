# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import ast
import builtins
import datetime
import decimal
import logging
import math
import re
import time

import numpy as np
import pandas as pd
from PySide6 import QtWidgets, QtCore

from myLib.myGui.myComboBox import comboGroup_1

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
'''AFI IMU '''
CMD_FOG_MOD_FREQ = 8
CMD_FOG_MOD_AMP_H = 9
CMD_FOG_MOD_AMP_L = 10
CMD_FOG_ERR_OFFSET = 18
CMD_FOG_POLARITY = 11
CMD_FOG_WAIT_CNT = 12
CMD_FOG_ERR_TH = 39
CMD_FOG_ERR_AVG = 13
CMD_FOG_TIMER_RST = 100
CMD_FOG_GAIN1 = 14
CMD_FOG_GAIN2 = 17
CMD_FOG_FB_ON = 16
CMD_FOG_CONST_STEP = 15
CMD_OUT_TH = 21
CMD_OUT_TH_EN = 22
CMD_FOG_FPGA_Q = 220
CMD_FOG_FPGA_R = 220
CMD_FOG_DAC_GAIN = 19
CMD_FOG_INT_DELAY = 240
CMD_FOG_OUT_START = 250
CMD_FOG_SF0 = 25
CMD_FOG_SF1 = 26
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
CMD_FOG_CUTOFF = 20

# Bias Temp
CMD_FOG_BIAS_T1 = 31
CMD_FOG_BIAS_T2 = 32
CMD_FOG_SFB_SLOPE_1 = 33
CMD_FOG_SFB_OFFSET_1 = 34
CMD_FOG_SFB_SLOPE_2 = 35
CMD_FOG_SFB_OFFSET_2 = 36
CMD_FOG_SFB_SLOPE_3 = 37
CMD_FOG_SFB_OFFSET_3 = 38

# ACCL Set
CMD_ACCL_SF0 = 39
CMD_ACCL_SF1 = 40
CMD_ACCL_SFB_SLOPE_1 = 41
CMD_ACCL_SFB_OFFSET_1 = 42

''' FOG PARAMETERS'''
INIT_PARAMETERS = {
    "0": 163, "1": 8192, "2": -8192, "3": 0, "4": 50, "5": 5, "6": 6, "7": 16384, "8": 1, "9": 5, "10": 0,
    "11": 72, "12": 650, "13":0, "14":0, "17": 0, "18": 1, "23": 50, "24": 10, "25": 0, "26": 0, "27": 0, "28": 0, "29": 0,
    "30": 0, "31": 0, "32": 10000, "33": 0, "34": 0
}

UPDate_Fucn = {
    "Func": np.array([])
}


class pig_parameters_widget(QGroupBox):
    def __init__(self, act, dataFileName, fileName="default_fog_parameters.json"):
        super(pig_parameters_widget, self).__init__()
        print("import pigParameters")
        self.__act = act
        self.imudata_file_Para = cmn.data_manager(fnum=0)
        self.filename = dataFileName
        self.dumpTrigerState = None
        self.__int_to_float_errorTimes = 0
        self.__modifiedItem = set()  # 用來儲存被修改的控制項。
        # self.__par_manager = cmn.parameters_manager(fileName, INIT_PARAMETERS, fnum=1)
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
        self.out_th_en = spinBlock(title='Att. Threshold EN', minValue=0, maxValue=1, double=False, step=1)

        # editline
        self.out_th = editBlock("Att. Threshold")
        self.dac_Vpi = editBlock(title='Vπ')
        self.dac_Vpi.setFixedWidth(100)
        self.rst_voltage = editBlock(title='RST Voltage')
        self.rst_voltage.setFixedWidth(100)
        # editline End

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
        self.dataRate_sd.setEnabled(False)
        ''' edit line '''
        self.sf0 = editBlock('STA')
        self.sf1 = editBlock('STB')
        self.sf2 = editBlock('SF2')
        self.sf3 = editBlock('SF3')
        self.sf4 = editBlock('SF4')
        self.sf5 = editBlock('SF5')
        self.sf6 = editBlock('SF6')
        self.sf7 = editBlock('SF7')
        self.sf8 = editBlock('SF8')
        self.sf9 = editBlock('SF9')
        self.sfb = editBlock('SFB')

        self.ACCLsta = editBlock('STA')
        self.ACCLstb = editBlock('STB')

        SFexplain = QLabel("Note: The values are displayed \nmultiplied by 10000.")
        self.SFTemp = QGroupBox("FOG SF Temp Cali")
        qvbox = QVBoxLayout()
        qvbox.addWidget(SFexplain)
        qvbox.addWidget(self.sf0)
        qvbox.addWidget(self.sf1)
        qvbox.addStretch(1)
        self.SFTemp.setLayout(qvbox)

        self.BiasTemp = QGroupBox("FOG Bias Temp Cali")
        BiasQvbox = QVBoxLayout()
        self.slope1 = editBlock("BTA1")
        self.slope2 = editBlock("BTA2")
        self.slope3 = editBlock("BTA3")
        self.offset1 = editBlock("BTB1")
        self.offset2 = editBlock("BTB2")
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

        # 第四欄的控制項
        self.ACCLSFTemp = QGroupBox("ACCL SF Temp Cali(g)")
        ACCLqvbox = QVBoxLayout()
        ACCLqvbox.addWidget(self.ACCLsta)
        ACCLqvbox.addWidget(self.ACCLstb)
        self.ACCLSFTemp.setLayout(ACCLqvbox)

        self.ACCLBiasTemp = QGroupBox("ACCL Bias Temp Cali(g)")
        ACCLBiasqvbox = QVBoxLayout()
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

        # 序號
        self.SNFrame = QGroupBox("Serial Number")
        self.startFunc_Box = QCheckBox("若確認要使用序號功能，請勾選此核取方塊。")
        nameStr = QLabel("SN(12字元)")
        self.SN_Str = QLineEdit()
        self.SN_Str.setMaxLength(12)
        SNRegex = QRegularExpression("^[A-Za-z0-9!@#$%&()_{};,.~]*$")
        SNValidator = QRegularExpressionValidator(SNRegex)
        self.SN_Str.setValidator(SNValidator)
        self.SN_Str.setDisabled(True)
        self.dumpTime_Btn = QPushButton("dump S/N")
        self.submit_Btn = QPushButton("Submit")
        self.submit_Btn.setDisabled(True)
        Spring = QSpacerItem(10, 25, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # 先將文字與輸入框綁成一個layout
        changeDateLayout = QVBoxLayout()
        changeDateLayout.addWidget(nameStr)
        changeDateLayout.addWidget(self.SN_Str)
        dateLayout = QGridLayout()
        dateLayout.addWidget(self.startFunc_Box, 0, 0, 1, 2)
        dateLayout.addLayout(changeDateLayout, 1, 0, 1, 2)
        dateLayout.addItem(Spring, 2, 0, 1, 1)
        dateLayout.addWidget(self.dumpTime_Btn, 3, 0, 1, 1)
        dateLayout.addWidget(self.submit_Btn, 3, 1, 1, 1)
        self.SNFrame.setLayout(dateLayout)

        self.dump_bt = QPushButton("Dump")
        self.Import_Btn = QPushButton("Import")
        self.Export_Btn = QPushButton("Export")
        self.init_para_btn = QPushButton("Init Para")
        # 用於status bar的功能建立
        self.progressBar_export = QProgressBar()
        self.progressBar_export.setRange(0, 100)
        self.progressBar_export.setValue(0)
        self.progressBar_export.setFixedWidth(200)
        self.progressBar_export.hide()
        self.progressBar_import = QProgressBar()
        self.progressBar_import.setRange(0, 100)
        self.progressBar_import.setFixedWidth(200)
        self.progressBar_import.setValue(0)
        self.progressBar_import.hide()

        # update 20240415 用來儲存要更新的function
        self.upFunc = UPDate_Fucn
        self.updateBtn = QPushButton("Update")
        self.BtnFrame = QVBoxLayout()
        self.BtnFrame.setContentsMargins(20, 1, 100, 1)
        self.BtnFrame.addWidget(self.dump_bt)
        self.BtnFrame.addWidget(self.init_para_btn)
        self.BtnFrame.addWidget(self.updateBtn)
        self.BtnFrame.addWidget(self.Import_Btn)
        self.BtnFrame.addWidget(self.progressBar_import)
        self.BtnFrame.addWidget(self.Export_Btn)
        self.BtnFrame.addWidget(self.progressBar_export)

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

        # 20240814 新增值接用檔案寫入控制項的button
        self.loadTempFile = QPushButton("Load Temp File")
        self.keyIsNotExist = False

        # channel
        self.dropdown_para = comboGroup_1("channel")
        self.dropdown_para.addItem(["X", "Y", "Z"])  # Z -> 1, X -> 3, Y -> 2
        # Only use Z channel for now: default to Z and lock the dropdown
        self.dropdown_para.cb.setCurrentText("Z")
        # self.dropdown_para.cb.setEnabled(False)
        self.__chVal = 1  # Z

        self.initUI()
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
        # mainLayout.addWidget(self.err_th, 5, 0, 1, 2)
        mainLayout.addWidget(self.fb_on, 5, 0, 1, 4)
        mainLayout.addWidget(self.freq, 6, 0, 1, 4)
        # mainLayout.addWidget(self.HD_Q, 7, 0, 1, 2)
        # mainLayout.addWidget(self.HD_R, 7, 2, 1, 2)
        # mainLayout.addWidget(self.KF_Q, 7, 0, 1, 2)
        # mainLayout.addWidget(self.KF_R, 7, 2, 1, 2)
        mainLayout.addWidget(self.cutoff, 7, 0, 1, 2)
        mainLayout.addWidget(self.out_th, 8, 0, 1, 2)
        mainLayout.addWidget(self.out_th_en, 9, 0, 1, 2)
        mainLayout.addWidget(self.dropdown_para, 7, 2, 1, 2)
        # mainLayout.addWidget(self.dump_bt, 9, 0, 1, 2)
        # mainLayout.addWidget(self.Firmware_Version_lb, 11, 0, 1, 4)
        # mainLayout.addWidget(self.GUI_Version_lb, 12, 0, 1, 4)
        mainLayout.addWidget(self.SFTemp, 0, 4, 2, 1)
        mainLayout.addWidget(self.BiasTemp, 2, 4, 8, 1)
        mainLayout.addWidget(self.ACCLSFTemp, 0, 5, 2, 1)
        mainLayout.addWidget(self.ACCLBiasTemp, 2, 5, 8, 1)
        mainLayout.addWidget(self.SNFrame, 0, 6, 2, 1)
        mainLayout.addWidget(self.loadTempFile, 10, 4, 1, 1)
        # mainLayout.addWidget(self.updateBtn, 11, 4, 1, 1)
        mainLayout.addLayout(self.BtnFrame, 2, 6, 2, 1)

        self.setLayout(mainLayout)

    def linkfunction(self):
        ''' spin box connect'''
        self.wait_cnt.spin.valueChanged.connect(self.send_WAIT_CNT_CMD)
        self.avg.spin.valueChanged.connect(self.send_AVG_CMD)
        self.mod_H.spin.valueChanged.connect(self.send_MOD_H_CMD)
        self.mod_L.spin.valueChanged.connect(self.send_MOD_L_CMD)
        self.freq.spin.valueChanged.connect(self.send_FREQ_CMD)
        self.err_offset.spin.valueChanged.connect(self.send_ERR_OFFSET_CMD)
        self.polarity.spin.valueChanged.connect(self.send_POLARITY_CMD)
        self.const_step.spin.valueChanged.connect(self.send_CONST_STEP_CMD)
        self.gain1.spin.valueChanged.connect(self.send_GAIN1_CMD)
        self.gain2.spin.valueChanged.connect(self.send_GAIN2_CMD)
        self.fb_on.spin.valueChanged.connect(self.send_FB_ON_CMD)
        self.dac_gain.spin.valueChanged.connect(self.send_DAC_GAIN_CMD)
        self.cutoff.spin.valueChanged.connect(self.send_CUTOFF_CMD)
        self.out_th_en.spin.valueChanged.connect(self.send_OUT_TH_EN_CMD)
        ''' line edit '''
        self.out_th.le.textChanged.connect(self.send_OUT_TH_CMD)
        self.sf0.le.textChanged.connect(self.send_SF0_CMD)
        self.sf1.le.textChanged.connect(self.send_SF1_CMD)
        self.T1.le.textChanged.connect(self.send_BIAS_T1_CMD)
        self.T2.le.textChanged.connect(self.send_BIAS_T2_CMD)
        self.slope1.le.textChanged.connect(self.send_SFB_SLOPE_1_CMD)
        self.slope2.le.textChanged.connect(self.send_SFB_SLOPE_2_CMD)
        self.slope3.le.textChanged.connect(self.send_SFB_SLOPE_3_CMD)
        self.offset1.le.textChanged.connect(self.send_SFB_OFFSET_1_CMD)
        self.offset2.le.textChanged.connect(self.send_SFB_OFFSET_2_CMD)
        self.offset3.le.textChanged.connect(self.send_SFB_OFFSET_3_CMD)
        self.ACCLsta.le.textChanged.connect(self.send_ACCL_SF0_CMD)
        self.ACCLstb.le.textChanged.connect(self.send_ACCL_SF1_CMD)
        self.ACCL_slope1.le.textChanged.connect(self.send_ACCL_SFB_SLOPE_1_CMD)
        self.ACCL_offset1.le.textChanged.connect(self.send_ACCL_SFB_OFFSET_1_CMD)

        self.SN_Str.textChanged.connect(lambda: self.selectcontrolchangecolor(self.SN_Str, None))

        ''' bt'''
        self.dump_bt.clicked.connect(self.dump_parameter)
        self.init_para_btn.clicked.connect(self.init_para)
        self.updateBtn.clicked.connect(self.update_changevalue)
        # 2025/05/28 先設置，要調整時比較好快速的調整，所以將更新按鈕改為禁止使用。
        self.updateBtn.setDisabled(True)
        self.loadTempFile.clicked.connect(self.loadCSVandWriteBias)
        self.startFunc_Box.stateChanged.connect(self.changeWidgetDisable)
        self.dumpTime_Btn.clicked.connect(self.dump_SN_parameter)
        self.submit_Btn.clicked.connect(self.submit_SN_parameter)
        self.Export_Btn.clicked.connect(self.exportTXTDump)
        self.Import_Btn.clicked.connect(self.importTXT)
        '''comboBox'''
        self.dropdown_para.cb.currentIndexChanged.connect(self.setChannel)

    def dump_parameter(self):
        self.__act.flushInputBuffer("None")
        initPara = self.__act.dump_fog_parameters(self.__chVal)
        # print(initPara)
        if isinstance(initPara, (list, dict)):
            self.set_init_value(initPara)
            self.dumpTrigerState = True
        # elif type(initPara) == bool:
        elif initPara == "無法取得值":
            self.mesboxProcess("warning", "Error occurred while in dump", "Please check if the device has power.")

    def init_para(self):
        """
        Apply INIT_PARAMETERS (GUI-style values) to widgets sequentially.
        Each change triggers existing valueChanged/textChanged callbacks -> auto send CMD.
        """
        # 防止重複按
        if hasattr(self, "_init_in_progress") and self._init_in_progress:
            return
        self._init_in_progress = True
        self.init_para_btn.setEnabled(False)

        # 準備進度視窗
        ops = self._build_init_ops_from_INIT_PARAMETERS()
        self._init_total = len(ops)
        self._init_idx = 0
        self._init_ops = ops

        self._init_progress = QtWidgets.QProgressDialog("Updating parameters…", None, 0, self._init_total, self)
        self._init_progress.setWindowTitle("Init Para")
        self._init_progress.setWindowModality(QtCore.Qt.WindowModal)
        self._init_progress.setAutoClose(True)
        self._init_progress.setAutoReset(True)
        self._init_progress.show()

        # 開始跑
        QtCore.QTimer.singleShot(0, self._init_para_step)

    def _init_para_step(self):
        if self._init_idx >= self._init_total:
            # done
            self._init_progress.setValue(self._init_total)
            self._init_progress.close()
            self.init_para_btn.setEnabled(True)
            self._init_in_progress = False
            self.mesboxProcess("info", "Init Para", "Parameters updated.")
            return

        (setter, value) = self._init_ops[self._init_idx]

        try:
            setter(value)  # 這裡會觸發 valueChanged/textChanged -> send cmd
        except Exception as e:
            logger.error(f"init_para step failed at idx={self._init_idx}: {e}")

        self._init_idx += 1
        self._init_progress.setValue(self._init_idx)

        # 50ms 後做下一個
        QtCore.QTimer.singleShot(50, self._init_para_step)

    def _build_init_ops_from_INIT_PARAMETERS(self):
        """
        Convert INIT_PARAMETERS (GUI-style values) to a list of (setter, value) operations in order.
        Important: do NOT call set_init_value() because that expects dump-format (IEEE ints, scaling, etc).
        """
        p = INIT_PARAMETERS

        def gv(k, default=0):
            return p.get(str(k), default)

        ops = []

        # spin boxes (direct int)
        ops.append((self.freq.spin.setValue, int(gv(0))))
        ops.append((self.mod_H.spin.setValue, int(gv(1))))
        ops.append((self.mod_L.spin.setValue, int(gv(2))))
        ops.append((self.polarity.spin.setValue, int(gv(3))))
        ops.append((self.wait_cnt.spin.setValue, int(gv(4))))
        ops.append((self.avg.spin.setValue, int(gv(5))))
        ops.append((self.gain1.spin.setValue, int(gv(6))))
        ops.append((self.const_step.spin.setValue, int(gv(7))))
        ops.append((self.fb_on.spin.setValue, int(gv(8))))
        ops.append((self.gain2.spin.setValue, int(gv(9))))
        ops.append((self.err_offset.spin.setValue, int(gv(10))))
        ops.append((self.dac_gain.spin.setValue, int(gv(11))))

        # cutoff: GUI-style (float shown in spin)
        ops.append((self.cutoff.spin.setValue, float(gv(12))))

        # line edits: treat INIT as GUI displayed string/number
        # SF (displayed multiplied by 10000 in your UI note)
        ops.append((self.sf0.le.setText, str(gv(17))))
        ops.append((self.sf1.le.setText, str(gv(18))))

        # Bias temp
        ops.append((self.T1.le.setText, str(gv(23))))
        ops.append((self.T2.le.setText, str(gv(24))))
        ops.append((self.slope1.le.setText, str(gv(25))))
        ops.append((self.offset1.le.setText, str(gv(26))))
        ops.append((self.slope2.le.setText, str(gv(27))))
        ops.append((self.offset2.le.setText, str(gv(28))))
        ops.append((self.slope3.le.setText, str(gv(29))))
        ops.append((self.offset3.le.setText, str(gv(30))))

        # ACCL SF temp (displayed *10000)
        ops.append((self.ACCLsta.le.setText, str(gv(31))))
        ops.append((self.ACCLstb.le.setText, str(gv(32))))

        # ACCL bias temp
        ops.append((self.ACCL_slope1.le.setText, str(gv(33))))
        ops.append((self.ACCL_offset1.le.setText, str(gv(34))))

        return ops

    def getVersion(self):
        self.__act.flushInputBuffer("None")
        self.Firmware_Version_lb.setText(self.__act.getVersion(self.__chVal))
        self.GUI_Version_lb.setText('IRIS-IMU-03-00-RD-RW')

    def setChannel(self):
        if self.dropdown_para.cb.currentText() == "X":
            self.__chVal = 3
        elif self.dropdown_para.cb.currentText() == "Z":
            self.__chVal = 1
        else:
            self.__chVal = int(self.dropdown_para.cb.currentIndex()) + 1
        # print("select channel")
        # print(str(self.__chVal))

    def changeWidgetDisable(self):
        self.submit_Btn.setDisabled(not self.startFunc_Box.isChecked())
        self.SN_Str.setDisabled(not self.startFunc_Box.isChecked())

    def dump_SN_parameter(self):
        self.__act.flushInputBuffer("None")
        SN = self.__act.dump_SN_parameters(3)
        if SN == "發生參數值為空的狀況":
            self.mesboxProcess("info", "參數值為空",
                               "1.請確認設備是否還未設定序號。\n2.請確認設備是否已上電。\n3.請斷開設備連接，並將設備重新上電，再連接設備取序號參數。\n謝謝")
        else:
            self.SN_Str.setText(str(SN))
            self.SN_Str.setStyleSheet('background-color: white')

    def submit_SN_parameter(self, importStatus=False):
        SNText = self.SN_Str.text()
        SNAscii = None
        Invalid_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for character in SNText:
            if character in Invalid_characters:
                raise invalidCharException(f'不允許在序號功能，匯入這些符號 -> \/:*?\"<>|')

        if SNText != "":
            try:
                SNText_split = SNText.split()
                for i in range(len(SNText_split)):
                    SNAscii = map(lambda x: hex(x), SNText_split[i].encode('utf-8'))

                SNAscii_list = list(SNAscii)
                if len(SNAscii_list) < 12:
                    k = len(SNAscii_list)
                    while k < 12:
                        SNAscii_list.append(hex(0))
                        k += 1
                # 將16進位的字串，依據基底為16轉為整數
                SNAscii_list_strToint = [int(j, 16) for j in SNAscii_list]
                self.__act.update_SN_parameters(SNAscii_list_strToint)
                self.SN_Str.setStyleSheet('bakcgorund-color: white')
                if not importStatus:
                    self.mesboxProcess("info", "輸入結果說明", "已將輸入內容寫入設備")

            except Exception as e:
                logger.error(f"於送出序號的格式轉換過程中發生錯誤 - {e}")
                self.mesboxProcess("warning", "序號功能發生錯誤", "請確認送出資料轉換的過程是否有錯誤。")

    def exportTXTDump(self):
        if self.dumpTrigerState == True:
            try:
                self.progressBar_export.setValue(0)
                self.progressBar_export.show()
                progressBarVal = 0
                # 取序號的參數
                self.__act.flushInputBuffer(None)
                SNPara = self.__act.dump_SN_parameters(3)
                if "發生參數值為空的狀況" == SNPara:
                    dumpParaSN = "參數值為空，請確認設備是否以上電。"
                else:
                    dumpParaSN = SNPara

                # 時間
                PCTimeNow = datetime.datetime.now()
                timeFormat = PCTimeNow.strftime("%Y%m%d%H%M")
                SNFile = SNPara.replace("\x00", "")  # 因儲存的檔案名稱不能含有此種特殊字元，需要使用取代的方式取代掉
                self.imudata_file_Para.name = str(SNFile) + "_" + timeFormat + "_" + self.filename + ".txt"
                self.imudata_file_Para.open(True)
                # 寫入參數key值的對應表
                self.imudata_file_Para.write_dump("參數key值對應表 ->")
                self.imudata_file_Para.write_dump(
                    f" 0= frequency            , 1= MOD_H                   , 2= MOD_L  ,\n"
                    f" 3=polarity                  , 4= Wait cnt                    , 5= avg,\n"
                    f" 6= GAIN1                   , 7= const_step                , 8= mode(0:OPEN),\n"
                    f" 9= GAIN2                   , 10= Err offset                 , 11= DAC_GAIN,\n"
                    f" 12= CutOff                 , 13= OUT_TH               , 14= OUT_EN,\n"
                    f" 17= FOG的STA               , 18= FOG的STB,\n"
                    f" 23= FOG Bias的T1      , 24= FOG Bias的T2          , 25= FOG Bias的BTA1,\n"
                    f" 26= FOG Bias的BTB1 , 27= FOG Bias的BTA2      , 28= FOG Bias的BTB2,\n"
                    f" 29= FOG Bias的BTA3 , 30= FOG Bias的BTB3      , 31= ACCL的STA,\n"
                    f" 32= ACCL的STB          , 33= ACCL Bias的BTA1    , 34= ACCL Bias的BTB1")
                # 寫入參數與序號
                self.imudata_file_Para.write_dump("SN")
                self.imudata_file_Para.write_dump(dumpParaSN)
                progressBarVal += 10
                self.progressBar_export.setValue(progressBarVal)

                i = 1
                while i < 4:
                    self.__act.flushInputBuffer(None)
                    result = self.__act.dump_fog_parameters(i)
                    if "無法取得值" in result:
                        dumpParaCh = "參數值無法取得"
                    else:
                        dumpParaCh = result
                    time.perf_counter()
                    self.imudata_file_Para.write_dump("Channel" + str(i))
                    self.imudata_file_Para.write_dump(dumpParaCh)
                    i += 1
                    progressBarVal += 30
                    self.progressBar_export.setValue(progressBarVal)
                self.mesboxProcess("info", "匯出功能", "匯出功能正常執行儲存完畢。")
            except Exception as e:
                logger.error(f"匯出參數的過程中發生錯誤 - {e}")
                self.mesboxProcess("warning", "匯出功能發生錯誤", "請確認匯出過程發生的錯誤，並進行修改。")
            if self.imudata_file_Para.isOpenFile:
                self.imudata_file_Para.close()
            self.progressBar_export.hide()
        else:
            self.mesboxProcess("warning", "請確認是否已dump了", "請確認是否已經點擊過dump按鈕，或是已經將設備的\n參數回填至控制項中，且數據已經顯示於畫面。"
                                                                "\n若還沒執行dump，將無法執行此匯出功能。")

    def importTXT(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", "All Files (*);;", options=options)

        # 判斷是否為channel變數
        itIsChannel = False
        # 判斷是否為序號變數
        itIsSN = False
        if filename != "":
            if self.dumpTrigerState == True:
                try:
                    with (open(filename, "r", encoding='utf-8') as f):
                        line_content = f.readline()
                        self.progressBar_import.setValue(0)
                        self.progressBar_import.show()
                        progressbar_Val = 0
                        while line_content != "":
                            # 移除#與\n字元的處理
                            content_replace = line_content.replace("#", "").replace("\n", "")
                            if itIsChannel == True and self.strCovertibleToDict(content_replace):
                                self.set_init_value(ast.literal_eval(content_replace))
                                itIsChannel = False
                                progressbar_Val += 30

                            if itIsSN == True and content_replace != "None":
                                # 先將\xe4\xbd\xa0 此種形式的字轉換為看得懂的文字
                                content_SN = bytearray(content_replace, "utf-8").decode("utf-8")
                                # content_SN = content_replace.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                                if 0 < len(content_SN) <= 12:
                                    self.SN_Str.setText(str(content_SN))
                                    self.SN_Str.setStyleSheet('background-color: white')
                                    self.submit_SN_parameter(True)
                                    progressbar_Val += 10
                                itIsSN = False

                            if "Channel" in content_replace:
                                num = content_replace.split("Channel")
                                self.__chVal = int(num[1].replace(" ", ""))
                                itIsChannel = True
                            if "SN" in content_replace:
                                itIsSN = True
                            time.sleep(0.5)
                            QApplication.processEvents()
                            self.progressBar_import.setValue(progressbar_Val)
                            line_content = f.readline()
                            continue
                except invalidCharException as e:
                    logger.error(f"錯誤 - {e}")
                except Exception as e:
                    logger.error(f"匯入參數的過程中發生錯誤 - {e}")
                finally:
                    if self.progressBar_import.value() != 100:
                        self.mesboxProcess("warning", "匯入功能發生錯誤",
                                           "匯入的過程中: \n(1)因檔案中沒有SN、Channel等標題或標題錯誤，無法匯入資訊。\n(2)因為檔案為空白狀態，所以無法匯入資訊。\n"
                                           "(3)資料類型有問題，導致無法匯入參數。\n(4)序號使用了不符合的符號命名檔案名稱。\n請檢查是否匯入功能有問題。")
                    self.progressBar_import.hide()
                    self.keyExistOrNotMes("匯入參數值")
            else:
                self.mesboxProcess("warning", "請確認是否已dump了", "請確認是否已經點擊過dump按鈕，或是已經將設備的\n參數回填至控制項中，且數據已經顯示於畫面。"
                                                                    "\n若還沒執行dump，將無法執行此匯入功能。")

    def strCovertibleToDict(self, content):
        try:
            result = ast.literal_eval(content)
            return isinstance(result, dict)
        except (ValueError, SyntaxError):
            return False

    def selectcontrolchangecolor(self, control, send_item_func):
        control.setStyleSheet('background-color: yellow;')

        clickBtnObj = self.sender()
        if not hasattr(clickBtnObj, 'text') or clickBtnObj.text() == "Load Temp File" or clickBtnObj.text() == "Import":
            if send_item_func not in self.__modifiedItem and send_item_func != None:
                self.__modifiedItem.add(send_item_func)
        # print(len(self.__modifiedItem))

    def controlchangewhite(self):
        self.wait_cnt.spin.setStyleSheet('background-color: white')
        self.avg.spin.setStyleSheet('background-color: white')
        self.mod_H.spin.setStyleSheet('background-color: white')
        self.mod_L.spin.setStyleSheet('background-color: white')
        self.freq.spin.setStyleSheet('background-color: white')
        # self.err_th.spin.setStyleSheet('background-color: white')
        self.err_offset.spin.setStyleSheet('background-color: white')
        self.polarity.spin.setStyleSheet('background-color: white')
        self.const_step.spin.setStyleSheet('background-color: white')
        # self.KF_Q.spin.setStyleSheet('background-color: white')
        # self.KF_R.spin.setStyleSheet('background-color: white')
        # self.HD_Q.spin.setStyleSheet('background-color: white')
        # self.HD_R.spin.setStyleSheet('background-color: white')
        self.gain1.spin.setStyleSheet('background-color: white')
        self.gain2.spin.setStyleSheet('background-color: white')
        self.fb_on.spin.setStyleSheet('background-color: white')
        self.dac_gain.spin.setStyleSheet('background-color: white')
        self.cutoff.spin.setStyleSheet('background-color: white')
        ''' slider '''
        # self.dataRate_sd.sd.setStyleSheet('background-color: white')
        ''' line edit '''
        self.sf0.le.setStyleSheet('background-color: white')
        self.sf1.le.setStyleSheet('background-color: white')
        self.T1.le.setStyleSheet('background-color: white')
        self.T2.le.setStyleSheet('background-color: white')
        self.slope1.le.setStyleSheet('background-color: white')
        self.slope2.le.setStyleSheet('background-color: white')
        self.slope3.le.setStyleSheet('background-color: white')
        self.offset1.le.setStyleSheet('background-color: white')
        self.offset2.le.setStyleSheet('background-color: white')
        self.offset3.le.setStyleSheet('background-color: white')
        self.ACCLsta.le.setStyleSheet('background-color: white')
        self.ACCLstb.le.setStyleSheet('background-color: white')
        self.ACCL_slope1.le.setStyleSheet('background-color: white')
        self.ACCL_offset1.le.setStyleSheet('background-color: white')

    def checkKeyExist(self, para, key):
        try:
            val = para.get(str(key))
        except TypeError:
            return 0
        except Exception:
            return 0

        # 用於load csv檔案的判斷
        try:
            if "TEMP Breakpoints" in para:
                if not isinstance(val.iloc[1], float) and not isinstance(val.iloc[3], float):
                    return 0
            if "slope" in para or "offset" in para:
                if not isinstance(val.iloc[0], float) and not isinstance(val.iloc[2], float) and not isinstance(
                        val.iloc[4], float):
                    return 0
        except Exception as e:
            logger.error(f"{e}, 檢查key是否存在與值的類型的判斷出現錯誤。")
            self.keyIsNotExist = True
            return 0

        if not isinstance(val, pd.Series):
            # 用於dump參數時的判斷
            if val == None:
                self.keyIsNotExist = True
                return 0
            if val == "nan" or val == '':
                logger.info("參數值為空的狀況，故回傳數值0代替空值。")
                return 0
        return val

    def loadCSVandWriteBias(self):
        if self.dumpTrigerState == True:
            options = QFileDialog.Options()
            filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", "All Files (*);;", options=options)
            if filename != "":
                biasData = cmn.loadCSVFile(filename)
                tempVal = self.checkKeyExist(biasData, "TEMP Breakpoints")
                slopeVal = self.checkKeyExist(biasData, "slope")
                offsetVal = self.checkKeyExist(biasData, "offset")

                if isinstance(tempVal, pd.Series) and isinstance(slopeVal, pd.Series) and isinstance(offsetVal,
                                                                                                     pd.Series):
                    try:
                        self.T1.le.setText(f'{tempVal[3]:.1f}')
                        self.T2.le.setText(f'{tempVal[1]:.1f}')

                        self.slope1.le.setText(f'{(float(slopeVal[4]) * -1):.10f}'.rstrip('0').rstrip('.'))
                        self.slope2.le.setText(f'{(float(slopeVal[2]) * -1):.10f}'.rstrip('0').rstrip('.'))
                        self.slope3.le.setText(f'{(float(slopeVal[0]) * -1):.10f}'.rstrip('0').rstrip('.'))
                        self.offset1.le.setText(f'{(float(offsetVal[4]) * -1):.10f}'.rstrip('0').rstrip('.'))
                        self.offset2.le.setText(f'{(float(offsetVal[2]) * -1):.10f}'.rstrip('0').rstrip('.'))
                        self.offset3.le.setText(f'{(float(offsetVal[0]) * -1):.10f}'.rstrip('0').rstrip('.'))
                    except Exception:
                        logger.error("載入CSV數據的功能出現錯誤。")
                        self.keyIsNotExist = True
                else:
                    self.keyIsNotExist = True

                self.keyExistOrNotMes("load Bias CSV")
                self.keyIsNotExist = False
        else:
            self.mesboxProcess("warning", "請確認是否已dump了", "請確認是否已經點擊過dump按鈕，或是已經將設備的\n參數回填至控制項中，且數據已經顯示於畫面。"
                                                                "\n若還沒執行dump，將無法執行此Load File功能。")

    def update_changevalue(self):
        mesbox = QtWidgets.QMessageBox()
        mesbox.setIcon(QMessageBox.Question)
        mesbox.setWindowTitle("確認是否要更新數值")
        mesbox.setText("請確認被選中的控制項都是要修改數值嗎?")
        mesbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mesbox.setDefaultButton(QtWidgets.QMessageBox.Yes)
        mes_result = mesbox.exec()

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
            # # self.update_FPGA_Q()
            # # self.update_FPGA_R()
            # self.send_GAIN1_CMD()
            # self.send_GAIN2_CMD()
            # self.send_FB_ON_CMD()
            # self.send_DAC_GAIN_CMD()
            # self.send_CUTOFF_CMD()
            # ''' slider '''
            # # self.send_DATA_RATE_CMD()
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
            # self.send_ACCL_SF0_CMD()
            # self.send_ACCL_SF1_CMD()
            # self.send_ACCL_SFB_SLOPE_1_CMD()
            # self.send_ACCL_SFB_OFFSET_1_CMD()

            time.perf_counter()
            # # 獲取按鈕的text文字
            # buttonObj = self.sender()
            # if buttonObj.text() == "Update":
            # 將背景顏色轉回白色
            self.controlchangewhite()
            self.__modifiedItem.clear()
            self.mesboxProcess("info", "更新完成資訊", "已更新完所有被修改的設備參數。")
            self.keyExistOrNotMes("parameter參數值")
            # func()
        else:
            self.mesboxProcess("warning", "update按鈕錯誤警告",
                               "請確認是否已經點擊過dump按鈕，或是已經將設備的\n參數回填至控制項中，且數據已經顯示於畫面。")

    def keyExistOrNotMes(self, name):
        if self.keyIsNotExist:
            if name == "parameter參數值":
                self.mesboxProcess("warning", name + "有不存在的狀況", "在取parameter參數值的狀況時，因設備版號為舊的部分，\n"
                                                                       "而GUI為最新版本未有撈取舊參數值，所以訊息通知使用者\n"
                                                                       "有些參數若為0或空值，代表該參數在舊版本的設備中未使\n"
                                                                       "用，因此撈取不到正確的參數。")
            elif name == "匯入參數值":
                self.mesboxProcess("warning", name + "有不存在的狀況",
                                   "請確認匯入的參數，是否有key值設定錯誤，或是不存在的狀況發生。")
            else:
                self.mesboxProcess("warning", name + "有不存在的狀況", "請確認使用的CSV檔案內容與標題是否有問題。")

            self.keyIsNotExist = False

    def set_init_value(self, para):
        self.freq.spin.setValue(self.checkKeyExist(para, "0"))
        self.mod_H.spin.setValue(self.checkKeyExist(para, "1"))
        self.mod_L.spin.setValue(self.checkKeyExist(para, "2"))
        self.polarity.spin.setValue(self.checkKeyExist(para, "3"))
        self.wait_cnt.spin.setValue(self.checkKeyExist(para, "4"))
        self.avg.spin.setValue(self.checkKeyExist(para, "5"))
        self.gain1.spin.setValue(self.checkKeyExist(para, "6"))
        self.const_step.spin.setValue(self.checkKeyExist(para, "7"))
        self.fb_on.spin.setValue(self.checkKeyExist(para, "8"))
        self.gain2.spin.setValue(self.checkKeyExist(para, "9"))
        self.err_offset.spin.setValue(self.checkKeyExist(para, "10"))
        self.dac_gain.spin.setValue(self.checkKeyExist(para, "11"))
        self.cutoff.spin.setValue(self.ieee754_int_to_float(self.checkKeyExist(para, "12")))
        self.out_th_en.spin.setValue(self.checkKeyExist(para, "14"))

        out_th = self.ieee754_int_to_float(self.checkKeyExist(para, "13"))
        self.out_th.le.setText(f'{out_th:.4f}'.rstrip('0').rstrip('.'))

        ### 20240417 修改
        # #將會有可能產生科學符號的部份，使用此方式將科學符號轉為標準表示法
        sf0_val = (self.ieee754_int_to_float(self.checkKeyExist(para, "17"), 17) * 10000)
        sf1_val = (self.ieee754_int_to_float(self.checkKeyExist(para, "18"), 18) * 10000)
        self.sf0.le.setText(f'{sf0_val:.6f}'.rstrip('0').rstrip('.'))
        self.sf1.le.setText(f'{sf1_val:.6f}'.rstrip('0').rstrip('.'))
        ## 20240417 修改
        # #將會有可能產生科學符號的部份，使用此方式將科學符號轉為標準表示法
        slope1_process = self.ieee754_int_to_float(self.checkKeyExist(para, "25"))
        slope2_process = self.ieee754_int_to_float(self.checkKeyExist(para, "27"))
        slope3_process = self.ieee754_int_to_float(self.checkKeyExist(para, "29"))
        offset1_process = self.ieee754_int_to_float(self.checkKeyExist(para, "26"))
        offset2_process = self.ieee754_int_to_float(self.checkKeyExist(para, "28"))
        offset3_process = self.ieee754_int_to_float(self.checkKeyExist(para, "30"))

        t1 = self.ieee754_int_to_float(self.checkKeyExist(para, "23"))
        t2 = self.ieee754_int_to_float(self.checkKeyExist(para, "24"))
        self.T1.le.setText(f'{t1:.1f}'.rstrip('0').rstrip('.'))
        self.T2.le.setText(f'{t2:.1f}'.rstrip('0').rstrip('.'))
        self.slope1.le.setText(f'{slope1_process:.10f}'.rstrip('0').rstrip('.'))
        self.slope2.le.setText(f'{slope2_process:.10f}'.rstrip('0').rstrip('.'))
        self.slope3.le.setText(f'{slope3_process:.10f}'.rstrip('0').rstrip('.'))
        self.offset1.le.setText(f'{offset1_process:.10f}'.rstrip('0').rstrip('.'))
        self.offset2.le.setText(f'{offset2_process:.10f}'.rstrip('0').rstrip('.'))
        self.offset3.le.setText(f'{offset3_process:.10f}'.rstrip('0').rstrip('.'))

        accl_sf0_val = self.ieee754_int_to_float(self.checkKeyExist(para, "31"), 31) * 10000
        accl_sf1_val = self.ieee754_int_to_float(self.checkKeyExist(para, "32"), 32) * 10000
        self.ACCLsta.le.setText(f'{accl_sf0_val:.6f}'.rstrip('0').rstrip('.'))
        self.ACCLstb.le.setText(f'{accl_sf1_val:.6f}'.rstrip('0').rstrip('.'))
        accl_slope_process = self.ieee754_int_to_float(self.checkKeyExist(para, "33"))
        accl_offset_process = self.ieee754_int_to_float(self.checkKeyExist(para, "34"))
        self.ACCL_slope1.le.setText(f'{accl_slope_process:.10f}'.rstrip('0').rstrip('.'))
        self.ACCL_offset1.le.setText(f'{accl_offset_process:.10f}'.rstrip('0').rstrip('.'))

        # pass
        if not __name__ == "__main__":
            self.controlchangewhite()

        if self.__int_to_float_errorTimes > 0:
            self.mesboxProcess('warning', '整數轉換單精度浮點數發生錯誤',
                               '轉換過程中因帶入的整數，不符合此轉換的方法，所以發生錯誤。')

    def mesboxProcess(self, status, title, content):
        mesbox = QMessageBox(self)
        if status == "warning":
            mesbox.warning(self, title, content)
        if status == "info":
            mesbox.information(self, title, content)

    def writeImuCmd(self, cmd, value, fog_ch):
        self.__act.writeImuCmd(cmd, value, fog_ch)

    def ieee754_int_to_float(self, int_value: int, valIdx=0) -> float:
        """
        Convert a 32-bit IEEE-754 integer representation to a float.

        :param int_value: Integer representation of IEEE-754 float (32-bit)
        :return: Converted floating-point number
        """
        # Pack integer as 4 bytes, then unpack as a float
        typeChange = 0
        try:
            valTruncated = int_value
            if int_value != "nan" or int_value != '':
                # # 若數值超出32位元的狀況，需要將多餘的位數截斷處理，避免發生錯誤
                # # 發生位元數過多的狀況，是因為SpinBox接收到nan值，產生的錯誤。
                # if (len(str(abs(int_value))) >= 11): # 先將整數的負號去除，在轉為字串進行截斷位數長度
                #     valStr = None
                #     if int_value > 0:
                #         valStr = str(int_value)[:10]
                #     else:
                #         valStr = str(int_value)[:11]
                #     if int(valStr) > 2147483647 or int(valStr) < -2147483648:
                #         valStr = valStr[:9]
                #     valTruncated = int(valStr)

                if isinstance(valTruncated, float):
                    typeChange = valTruncated * 0.0001
                elif isinstance(valTruncated, int):
                    if len(str(abs(valTruncated))) <= 10 or len(str(abs(valTruncated))) >= 8:
                        # 當參數為有號數的情況，需要做的處理
                        if str(valTruncated)[0] == "-":
                            valTruncated_unSign = int(valTruncated) & 0xFFFFFFFF
                            # print(int(valTruncated))
                            struct_pack = struct.pack('<I', valTruncated_unSign)
                            struct_unpack = struct.unpack('<f', struct_pack)[0]
                            typeChange = round(struct_unpack, 7)
                        else:
                            typeChange = round(struct.unpack('<f', struct.pack('<I', int(valTruncated)))[0], 7)
                    else:
                        typeChange = valTruncated
                        if valIdx != 0:
                            typeChange = typeChange * 0.0001

                # 轉換之後的值為nan的狀況，需要進行的判斷，避免一些控制項因為nan回填，導致發生OverflowError錯誤
                if math.isnan(typeChange):
                    return 0

            else:
                logger.error(f"撈取的資料等於nan，因此不轉換為浮點數，並回傳數值0填至控制項。")
                return 0
        except Exception as e:
            logger.error(f"{e} - 使用dump撈取數據，在數據型態轉換的過程發生錯誤。")
            self.__int_to_float_errorTimes += 1

        return typeChange

    def send_FREQ_CMD(self):
        # dt_fpga = 1e3 / 91e6  # for PLL set to 91MHz
        # dt_fpga = 1e3 / 90e6
        dt_fpga = 1e3 / 100e6
        # dt_fpga = 1e3/ 105e6 # for PLL set to 105MHz
        # dt_fpga = 1e3/ 107e6 # for PLL set to 107MHz
        # dt_fpga = 1e3/ 108.333333e6 # for PLL set to 109MHz
        value = self.freq.spin.value()
        # logger.info('set freq: %d', value)
        self.freq.lb.setText(str(round(1 / (2 * (value + 1) * dt_fpga), 2)) + ' KHz')
        self.__act.writeImuCmd(CMD_FOG_MOD_FREQ, value, self.__chVal)
        # print('send_FREQ_CMD:', self.__chVal)
        # self.__par_manager.update_parameters("FREQ", value)

    def send_MOD_H_CMD(self):
        value = self.mod_H.spin.value()
        # logger.info('set mod_H: %d', value)
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_H, value, self.__chVal)
        # self.__par_manager.update_parameters("MOD_H", value)

    def send_MOD_L_CMD(self):
        value = self.mod_L.spin.value()
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_L, value, self.__chVal)
        # logger.info('set mod_L: %d', value)
        # self.__par_manager.update_parameters("MOD_L", value)

    def send_ERR_OFFSET_CMD(self):
        value = self.err_offset.spin.value()
        # logger.info('set err offset: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_OFFSET, value, self.__chVal)
        # self.__par_manager.update_parameters("ERR_OFFSET", value)

    def send_POLARITY_CMD(self):
        value = self.polarity.spin.value()
        # logger.info('set polarity: %d', value)
        self.__act.writeImuCmd(CMD_FOG_POLARITY, value, self.__chVal)
        # self.__par_manager.update_parameters("POLARITY", value)

    def send_WAIT_CNT_CMD(self):
        value = self.wait_cnt.spin.value()
        # logger.info('set wait cnt: %d', value)
        self.__act.writeImuCmd(CMD_FOG_WAIT_CNT, value, self.__chVal)
        # self.__par_manager.update_parameters("WAIT_CNT", value)

    def send_ERR_TH_CMD(self):
        value = self.err_th.spin.value()
        # logger.info('set err_th: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_TH, value, self.__chVal)
        # self.__par_manager.update_parameters("ERR_TH", value)

    def send_AVG_CMD(self):
        value = self.avg.spin.value()
        # logger.info('set err_avg: %d', value)
        self.__act.writeImuCmd(CMD_FOG_ERR_AVG, value, self.__chVal)
        # self.__par_manager.update_parameters("ERR_AVG", value)

    def send_GAIN1_CMD(self):
        value = self.gain1.spin.value()
        # logger.info('set gain1: %d', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN1, value, self.__chVal)
        # self.__par_manager.update_parameters("GAIN1", value)

    def send_GAIN2_CMD(self):
        value = self.gain2.spin.value()
        # logger.info('set gain2: %d', value)
        self.__act.writeImuCmd(CMD_FOG_GAIN2, value, self.__chVal)
        # self.__par_manager.update_parameters("GAIN2", value)

    def send_FB_ON_CMD(self):
        value = self.fb_on.spin.value()
        # logger.info('set FB on: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FB_ON, value, self.__chVal)
        # self.__act.writeImuCmd(CMD_FOG_FB_ON, 0)
        # self.__act.writeImuCmd(CMD_FOG_FB_ON, value)
        # self.__par_manager.update_parameters("FB_ON", value)

    def send_DAC_GAIN_CMD(self):
        value = self.dac_gain.spin.value()
        # logger.info('set DAC gain: %d', value)
        self.__act.writeImuCmd(CMD_FOG_DAC_GAIN, value, self.__chVal)
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
        cutoff_Val = self.cutoff.spin.value()
        logger.info('set CUTOFF : %d', cutoff_Val)
        # value2 = struct.unpack('<I', struct.pack('<f', value))
        # logger.info('set DAC gain: %d', value)
        value = struct.unpack('<I', struct.pack('<f', float(cutoff_Val)))
        self.__act.writeImuCmd(CMD_FOG_CUTOFF, value[0], self.__chVal)
        # self.__par_manager.update_parameters("DAC_GAIN", value)
        # print("%d" % value)

    def send_OUT_TH_EN_CMD(self):
        value = self.out_th_en.spin.value()
        # logger.info('set FB on: %d', value)
        self.__act.writeImuCmd(CMD_OUT_TH_EN, value, self.__chVal)


    def send_OUT_TH_CMD(self):
        out_th = float(self.out_th.le.text())
        # logger.info('set SFA : %d', Re_sf0Val)
        value = struct.unpack('<I', struct.pack('<f', out_th))
        self.__act.writeImuCmd(CMD_OUT_TH, value[0], self.__chVal)

    def send_SF0_CMD(self):
        Re_sf0Val = float(self.sf0.le.text()) * 0.0001  # 與AA同方式
        # logger.info('set SFA : %d', Re_sf0Val)
        value = struct.unpack('<I', struct.pack('<f', Re_sf0Val))
        self.__act.writeImuCmd(CMD_FOG_SF0, value[0], self.__chVal)

    def send_SF1_CMD(self):
        Re_sf1Val = float(self.sf1.le.text()) * 0.0001  # 與AA同方式
        print(Re_sf1Val)
        # logger.info('set SFB : %d', Re_sf1Val)
        value = struct.unpack('<I', struct.pack('<f', Re_sf1Val))
        self.__act.writeImuCmd(CMD_FOG_SF1, value[0], self.__chVal)
        print("SF1: ")
        print(str(value[0]))

    # def send_SF_COMP_T1_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf_comp_T1.le.text())))
    #     print(value[0])
    #     self.__act.writeImuCmd(CMD_SF_COMP_T1, value[0])
    #
    # def send_SF_COMP_T2_CMD(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf_comp_T2.le.text())))
    #     print(value[0])
    #     self.__act.writeImuCmd(CMD_SF_COMP_T2, value[0])
    #
    # def send_SF_1_SLOPE(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf_1_slope.le.text())))
    #     print(value[0])
    #     self.__act.writeImuCmd(CMD_SF_1_SLOPE, value[0])
    #
    # def send_SF_1_OFFSET(self):
    #     value = struct.unpack('<I', struct.pack('<f', float(self.sf_1_offset.le.text())))
    #     print(value[0])
    #     self.__act.writeImuCmd(CMD_SF_1_OFFSET, value[0])

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
        # logger.info('set constant step: %d', value)
        self.__act.writeImuCmd(CMD_FOG_CONST_STEP, value, self.__chVal)
        # self.__par_manager.update_parameters("CONST_STEP", value)

    def update_KF_Q(self):
        value = self.KF_Q.spin.value()
        # logger.info('set KF_Q: %d', value)
        self.__act.kal_Q = value
        # self.__par_manager.update_parameters("KF_Q", value)

    def update_KF_R(self):
        value = self.KF_R.spin.value()
        # logger.info('set KF_R: %d', value)
        self.__act.kal_R = value
        # self.__par_manager.update_parameters("KF_R", value)

    def update_FPGA_Q(self):
        value = self.HD_Q.spin.value()
        # logger.info('set HD_Q: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FPGA_Q, value)
        # self.__par_manager.update_parameters("HD_Q", value)

    def update_FPGA_R(self):
        value = self.HD_R.spin.value()
        # logger.info('set HD_R: %d', value)
        self.__act.writeImuCmd(CMD_FOG_FPGA_R, value)
        # self.__par_manager.update_parameters("HD_R", value)

    def send_DATA_RATE_CMD(self):
        value = self.dataRate_sd.sd.value()
        # logger.info('set dataRate: %d', value)
        self.__act.writeImuCmd(CMD_FOG_INT_DELAY, value)
        # self.__par_manager.update_parameters("DATA_RATE", value)

    def SF_A_EDIT(self):
        value = float(self.sf_a.le.text())
        # logger.info('set sf_a: %f', value)
        self.__act.sf_a = value
        # self.__par_manager.update_parameters("SF_A", value)

    def SF_B_EDIT(self):
        value = float(self.sf_b.le.text())
        # logger.info('set sf_b: %f', value)
        self.__act.sf_b = value
        # self.__par_manager.update_parameters("SF_B", value)

    def send_BIAS_T1_CMD(self):
        logger.info('set BIAS T1 : %d', float(self.T1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.T1.le.text())))
        self.__act.writeImuCmd(CMD_FOG_BIAS_T1, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_BIAS_T2_CMD(self):
        logger.info('set BIAS T2 : %d', float(self.T2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.T2.le.text())))
        self.__act.writeImuCmd(CMD_FOG_BIAS_T2, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_SFB_SLOPE_1_CMD(self):
        logger.info('set BIAS SF SLOPE1 : %d', float(self.slope1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', (float(self.slope1.le.text()))))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_1, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_SFB_SLOPE_2_CMD(self):
        logger.info('set BIAS SF SLOPE2 : %d', float(self.slope2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', (float(self.slope2.le.text()))))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_2, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_SFB_SLOPE_3_CMD(self):
        logger.info('set BIAS SF SLOPE3 : %d', float(self.slope3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', (float(self.slope3.le.text()))))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_3, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_SFB_OFFSET_1_CMD(self):
        logger.info('set BIAS SF OFFSET1 : %d', float(self.offset1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', (float(self.offset1.le.text()))))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_1, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_SFB_OFFSET_2_CMD(self):
        logger.info('set BIAS SF OFFSET2 : %d', float(self.offset2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', (float(self.offset2.le.text()))))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_2, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_SFB_OFFSET_3_CMD(self):
        logger.info('set BIAS SF OFFSET3 : %d', float(self.offset3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', (float(self.offset3.le.text()))))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_3, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_ACCL_SF0_CMD(self):
        Re_sf0Val = float(self.ACCLsta.le.text()) * 0.0001  # 與AA同方式
        # logger.info('set ACC SFA : %d', Re_sf0Val)
        value = struct.unpack('<I', struct.pack('<f', Re_sf0Val))
        self.__act.writeImuCmd(CMD_ACCL_SF0, value[0], self.__chVal)

    def send_ACCL_SF1_CMD(self):
        Re_sf1Val = float(self.ACCLstb.le.text()) * 0.0001  # 與AA同方式
        # logger.info('set ACC SFB : %d', Re_sf1Val)
        value = struct.unpack('<I', struct.pack('<f', Re_sf1Val))
        self.__act.writeImuCmd(CMD_ACCL_SF1, value[0], self.__chVal)

    def send_ACCL_SFB_SLOPE_1_CMD(self):
        logger.info('set ACC SF SLOPE1 : %d', float(self.ACCL_slope1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', (float(self.ACCL_slope1.le.text()))))
        self.__act.writeImuCmd(CMD_ACCL_SFB_SLOPE_1, value[0], self.__chVal)
        # print("%x" % value[0])

    def send_ACCL_SFB_OFFSET_1_CMD(self):
        logger.info('set ACC SF OFFSET1 : %d', float(self.ACCL_offset1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', (float(self.ACCL_offset1.le.text()))))
        self.__act.writeImuCmd(CMD_ACCL_SFB_OFFSET_1, value[0], self.__chVal)
        # print("%x" % value[0])

    def InputIntforEdit(self):
        if self.dac_Vpi.le.text() != "" and self.rst_voltage.le.text() != "":
            if self.dac_Vpi_status and self.rst_voltage_status:
                self.CalDACGain()

    def isdoubleForDAC_Vpi(self):
        format_ = r'^[-+]?[0-9]*\.[0-9]+$'

        textVal_dac_Vpi = self.dac_Vpi.le.text()
        if bool(re.match(format_, textVal_dac_Vpi)) == True:
            self.dac_Vpi.le.setStyleSheet("color: black")
            self.dac_Vpi_status = True
        else:
            self.dac_Vpi.le.setStyleSheet("color: red")
            self.dac_Vpi_status = False

    def isdoubleForRST_voltage(self):
        format_ = r'^[-+]?[0-9]*\.[0-9]+$'

        textVal_rst_voltage = self.rst_voltage.le.text()
        if bool(re.match(format_, textVal_rst_voltage)) == True:
            self.rst_voltage.le.setStyleSheet("color: black")
            self.rst_voltage_status = True
        else:
            self.rst_voltage.le.setStyleSheet("color: red")
            self.rst_voltage_status = False

    def CalDACGain(self):
        y = float(self.dac_Vpi.le.text())
        b = float(self.rst_voltage.le.text())
        dac_gain_slope = 0.0087  # 斜率
        dac_gain_Val = np.round(((y - b) / dac_gain_slope))
        result = int(dac_gain_Val)
        self.dac_gain.spin.setValue(result)


class invalidCharException(Exception):
    def __init__(self, mes):
        super().__init__(mes)


# ==========================================
#   UI 預覽測試區塊 (Layout Preview Only)
# ==========================================
if __name__ == "__main__":
    import sys
    import os
    from PySide6.QtWidgets import QApplication

    # 1. 修正路徑：將專案根目錄加入 path，以便能 import myLib
    # 目前位置：drivers/hins_fog_imu/widgets/ (向上 4 層即為根目錄)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))
    sys.path.append(root_dir)


    # 2. 定義一個「啞巴」Reader (Dummy Reader)
    # 它的目的只是為了讓 Widget 初始化不報錯，不需要任何功能
    class DummyReader:
        def __getattr__(self, name):
            # 無論 UI 呼叫什麼方法 (writeImuCmd, flushInputBuffer...)
            # 都回傳一個「什麼都不做的函式」，並回傳空值
            def method(*args, **kwargs):
                print(f"[UI Preview] Method called: {name}")
                return 0  # 避免某些計算需要數值

            return method


    app = QApplication(sys.argv)

    # 3. 啟動視窗 (請依據檔案名稱修改對應的 Class)
    # ------------------------------------------------
    # 如果是 pig_parameters_widget.py:
    window = pig_parameters_widget(DummyReader(), "Preview_Mode")
    # ------------------------------------------------

    window.show()
    sys.exit(app.exec())
