# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import ast
import builtins
import datetime
import logging
import struct
import time
import numpy as np
import pandas as pd
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QPushButton, QLineEdit, QCheckBox, QProgressBar, QFileDialog,
                               QMessageBox, QProgressDialog, QSpacerItem, QSizePolicy)

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys

sys.path.append("../../")
from myLib.myGui.mygui_serial import spinBlock, spinBlockOneLabel, sliderBlock, editBlock
from myLib import common as cmn
from myLib.myGui.myLabel import *
from myLib.myGui.myComboBox import comboGroup_1

'''-------define CMD address map-------'''
CMD_FOG_MOD_FREQ = 8
CMD_FOG_MOD_AMP_H = 9
CMD_FOG_MOD_AMP_L = 10
CMD_FOG_ERR_OFFSET = 18
CMD_FOG_POLARITY = 11
CMD_FOG_WAIT_CNT = 12
CMD_FOG_ERR_TH = 39
CMD_FOG_ERR_AVG = 13
CMD_FOG_GAIN1 = 14
CMD_FOG_GAIN2 = 17
CMD_FOG_FB_ON = 16
CMD_FOG_CONST_STEP = 15
CMD_OUT_TH = 21
CMD_OUT_TH_EN = 22
CMD_FOG_DAC_GAIN = 19
CMD_FOG_SF0 = 25
CMD_FOG_SF1 = 26
CMD_FOG_CUTOFF = 20
CMD_FOG_BIAS_T1 = 31
CMD_FOG_BIAS_T2 = 32
CMD_FOG_SFB_SLOPE_1 = 33
CMD_FOG_SFB_OFFSET_1 = 34
CMD_FOG_SFB_SLOPE_2 = 35
CMD_FOG_SFB_OFFSET_2 = 36
CMD_FOG_SFB_SLOPE_3 = 37
CMD_FOG_SFB_OFFSET_3 = 38
CMD_ACCL_SF0 = 39
CMD_ACCL_SF1 = 40
CMD_ACCL_SFB_SLOPE_1 = 41
CMD_ACCL_SFB_OFFSET_1 = 42

INIT_PARAMETERS = {
    "0": 163, "1": 8192, "2": -8192, "3": 0, "4": 50, "5": 5, "6": 6, "7": 16384, "8": 1, "9": 5, "10": 0,
    "11": 72, "12": 650, "13": 0, "14": 0, "17": 0, "18": 1, "23": 10, "24": 50, "25": 0, "26": 0, "27": 0, "28": 0,
    "29": 0,
    "30": 0, "31": 0, "32": 10000, "33": 0, "34": 0
}


class pig_parameters_widget(QGroupBox):
    def __init__(self, act, dataFileName, fileName="default_fog_parameters.json"):
        super(pig_parameters_widget, self).__init__()
        self.__act = act
        self._updating_ui = False
        self.imudata_file_Para = cmn.data_manager(fnum=0)
        self.filename = dataFileName
        self.dumpTrigerState = False
        self.__chVal = 1  # 預設 Z

        self.initUI_components()

        # --- 核心：配置管理表 (Table-Driven) ---
        self.config_table = {
            "0": {"type": "int", "widget": self.freq.spin, "comment": "frequency", "cmd_func": self.send_FREQ_CMD},
            "1": {"type": "int", "widget": self.mod_H.spin, "comment": "MOD_H", "cmd_func": self.send_MOD_H_CMD},
            "2": {"type": "int", "widget": self.mod_L.spin, "comment": "MOD_L", "cmd_func": self.send_MOD_L_CMD},
            "3": {"type": "int", "widget": self.polarity.spin, "comment": "polarity",
                  "cmd_func": self.send_POLARITY_CMD},
            "4": {"type": "int", "widget": self.wait_cnt.spin, "comment": "Wait cnt",
                  "cmd_func": self.send_WAIT_CNT_CMD},
            "5": {"type": "int", "widget": self.avg.spin, "comment": "avg", "cmd_func": self.send_AVG_CMD},
            "6": {"type": "int", "widget": self.gain1.spin, "comment": "GAIN1", "cmd_func": self.send_GAIN1_CMD},
            "7": {"type": "int", "widget": self.const_step.spin, "comment": "const_step",
                  "cmd_func": self.send_CONST_STEP_CMD},
            "8": {"type": "int", "widget": self.fb_on.spin, "comment": "mode(0:OPEN)", "cmd_func": self.send_FB_ON_CMD},
            "9": {"type": "int", "widget": self.gain2.spin, "comment": "GAIN2", "cmd_func": self.send_GAIN2_CMD},
            "10": {"type": "int", "widget": self.err_offset.spin, "comment": "Err offset",
                   "cmd_func": self.send_ERR_OFFSET_CMD},
            "11": {"type": "int", "widget": self.dac_gain.spin, "comment": "DAC_GAIN",
                   "cmd_func": self.send_DAC_GAIN_CMD},
            "12": {"type": "float", "widget": self.cutoff.spin, "comment": "CutOff", "cmd_func": self.send_CUTOFF_CMD},
            "13": {"type": "float", "widget": self.out_th.le, "comment": "Att. Threshold",
                   "cmd_func": self.send_OUT_TH_CMD},
            "14": {"type": "int", "widget": self.out_th_en.spin, "comment": "Threshold EN",
                   "cmd_func": self.send_OUT_TH_EN_CMD},
            "17": {"type": "sf", "widget": self.sf0.le, "comment": "FOG STA", "cmd_func": self.send_SF0_CMD},
            "18": {"type": "sf", "widget": self.sf1.le, "comment": "FOG STB", "cmd_func": self.send_SF1_CMD},
            "23": {"type": "float", "widget": self.T1.le, "comment": "FOG Bias T1", "cmd_func": self.send_BIAS_T1_CMD},
            "24": {"type": "float", "widget": self.T2.le, "comment": "FOG Bias T2", "cmd_func": self.send_BIAS_T2_CMD},
            "25": {"type": "float", "widget": self.slope1.le, "comment": "FOG Bias BTA1",
                   "cmd_func": self.send_SFB_SLOPE_1_CMD},
            "26": {"type": "float", "widget": self.offset1.le, "comment": "FOG Bias BTB1",
                   "cmd_func": self.send_SFB_OFFSET_1_CMD},
            "27": {"type": "float", "widget": self.slope2.le, "comment": "FOG Bias BTA2",
                   "cmd_func": self.send_SFB_SLOPE_2_CMD},
            "28": {"type": "float", "widget": self.offset2.le, "comment": "FOG Bias BTB2",
                   "cmd_func": self.send_SFB_OFFSET_2_CMD},
            "29": {"type": "float", "widget": self.slope3.le, "comment": "FOG Bias BTA3",
                   "cmd_func": self.send_SFB_SLOPE_3_CMD},
            "30": {"type": "float", "widget": self.offset3.le, "comment": "FOG Bias BTB3",
                   "cmd_func": self.send_SFB_OFFSET_3_CMD},
            "31": {"type": "sf", "widget": self.ACCLsta.le, "comment": "ACCL STA", "cmd_func": self.send_ACCL_SF0_CMD},
            "32": {"type": "sf", "widget": self.ACCLstb.le, "comment": "ACCL STB", "cmd_func": self.send_ACCL_SF1_CMD},
            "33": {"type": "float", "widget": self.ACCL_slope1.le, "comment": "ACCL Bias BTA1",
                   "cmd_func": self.send_ACCL_SFB_SLOPE_1_CMD},
            "34": {"type": "float", "widget": self.ACCL_offset1.le, "comment": "ACCL Bias BTB1",
                   "cmd_func": self.send_ACCL_SFB_OFFSET_1_CMD},
        }
        self.linkfunction()

    def initUI_components(self):
        """ 初始化所有 UI 元件 """
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
        self.out_th = editBlock("Att. Threshold")
        self.fb_on = spinBlock(title='mode(0:OPEN)', minValue=0, maxValue=2, double=False, step=1)
        self.freq = spinBlockOneLabel(title='frequency', minValue=10, maxValue=1500, double=False, step=1)
        self.cutoff = spinBlock(title='CutOff', minValue=50, maxValue=1500, double=False, step=5)

        self.sf0, self.sf1 = editBlock('STA'), editBlock('STB')
        self.slope1, self.slope2, self.slope3 = editBlock("BTA1"), editBlock("BTA2"), editBlock("BTA3")
        self.offset1, self.offset2, self.offset3 = editBlock("BTB1"), editBlock("BTB2"), editBlock("BTB3")
        self.T1, self.T2 = editBlock("T1"), editBlock("T2")
        self.ACCLsta, self.ACCLstb = editBlock('STA'), editBlock('STB')
        self.ACCL_slope1, self.ACCL_offset1 = editBlock("BTA1"), editBlock("BTB1")

        self.SFTemp = QGroupBox("FOG SF Temp Cali")
        v1 = QVBoxLayout();
        v1.addWidget(QLabel("Note: values x10000"));
        v1.addWidget(self.sf0);
        v1.addWidget(self.sf1);
        self.SFTemp.setLayout(v1)
        self.BiasTemp = QGroupBox("FOG Bias Temp Cali")
        v2 = QVBoxLayout();
        v2.addWidget(self.slope3);
        v2.addWidget(self.offset3);
        v2.addWidget(self.T2);
        v2.addWidget(self.slope2);
        v2.addWidget(self.offset2);
        v2.addWidget(self.T1);
        v2.addWidget(self.slope1);
        v2.addWidget(self.offset1);
        self.BiasTemp.setLayout(v2)
        self.ACCLSFTemp = QGroupBox("ACCL SF Temp Cali(g)")
        v3 = QVBoxLayout();
        v3.addWidget(self.ACCLsta);
        v3.addWidget(self.ACCLstb);
        self.ACCLSFTemp.setLayout(v3)
        self.ACCLBiasTemp = QGroupBox("ACCL Bias Temp Cali(g)")
        v4 = QVBoxLayout();
        v4.addWidget(self.ACCL_slope1);
        v4.addWidget(self.ACCL_offset1);
        self.ACCLBiasTemp.setLayout(v4)

        self.SNFrame = QGroupBox("Serial Number")
        self.startFunc_Box = QCheckBox("Enable SN")
        self.SN_Str = QLineEdit();
        self.SN_Str.setMaxLength(12);
        self.SN_Str.setDisabled(True)
        self.dumpTime_Btn = QPushButton("dump S/N");
        self.submit_Btn = QPushButton("Submit");
        self.submit_Btn.setDisabled(True)
        g1 = QGridLayout();
        g1.addWidget(self.startFunc_Box, 0, 0, 1, 2);
        g1.addWidget(QLabel("SN(12 chars)"), 1, 0);
        g1.addWidget(self.SN_Str, 1, 1);
        g1.addWidget(self.dumpTime_Btn, 2, 0);
        g1.addWidget(self.submit_Btn, 2, 1);
        self.SNFrame.setLayout(g1)

        self.dump_bt, self.init_para_btn, self.Import_Btn, self.Export_Btn = QPushButton("Dump"), QPushButton(
            "Init Para"), QPushButton("Import"), QPushButton("Export")
        self.progressBar_export = QProgressBar();
        self.progressBar_export.hide()
        self.loadTempFile = QPushButton("Load Temp File")
        self.dropdown_para = comboGroup_1("channel");
        self.dropdown_para.addItem(["X", "Y", "Z"]);
        self.dropdown_para.cb.setCurrentText("Z")

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.wait_cnt, 0, 0, 1, 2);
        mainLayout.addWidget(self.avg, 0, 2, 1, 2)
        mainLayout.addWidget(self.mod_H, 1, 0, 1, 2);
        mainLayout.addWidget(self.mod_L, 1, 2, 1, 2)
        mainLayout.addWidget(self.err_offset, 2, 0, 1, 2);
        mainLayout.addWidget(self.polarity, 2, 2, 1, 2)
        mainLayout.addWidget(self.gain1, 3, 0, 1, 2);
        mainLayout.addWidget(self.gain2, 3, 2, 1, 2)
        mainLayout.addWidget(self.const_step, 4, 2, 1, 2);
        mainLayout.addWidget(self.dac_gain, 4, 0, 1, 2)
        mainLayout.addWidget(self.fb_on, 5, 0, 1, 4);
        mainLayout.addWidget(self.freq, 6, 0, 1, 4)
        mainLayout.addWidget(self.cutoff, 7, 0, 1, 2);
        mainLayout.addWidget(self.dropdown_para, 7, 2, 1, 2)
        mainLayout.addWidget(self.out_th, 8, 0, 1, 2);
        mainLayout.addWidget(self.out_th_en, 9, 0, 1, 2)
        mainLayout.addWidget(self.SFTemp, 0, 4, 2, 1);
        mainLayout.addWidget(self.BiasTemp, 2, 4, 8, 1)
        mainLayout.addWidget(self.ACCLSFTemp, 0, 5, 2, 1);
        mainLayout.addWidget(self.ACCLBiasTemp, 2, 5, 8, 1)
        mainLayout.addWidget(self.SNFrame, 0, 6, 2, 1);
        mainLayout.addWidget(self.loadTempFile, 10, 4, 1, 1)
        b1 = QVBoxLayout();
        b1.addWidget(self.dump_bt);
        b1.addWidget(self.init_para_btn);
        b1.addWidget(self.Import_Btn);
        b1.addWidget(self.Export_Btn);
        b1.addWidget(self.progressBar_export);
        mainLayout.addLayout(b1, 2, 6, 2, 1)
        self.setLayout(mainLayout)

    def linkfunction(self):
        """ 綁定信號：根據 Table 內容自動連接監聽與發送 """
        self.dump_bt.clicked.connect(self.dump_parameter)
        self.init_para_btn.clicked.connect(self.init_para)
        self.Export_Btn.clicked.connect(self.exportTXTDump)
        self.Import_Btn.clicked.connect(self.importTXT)
        self.loadTempFile.clicked.connect(self.loadCSVandWriteBias)
        self.startFunc_Box.stateChanged.connect(self.changeWidgetDisable)
        self.dumpTime_Btn.clicked.connect(self.dump_SN_parameter)
        self.submit_Btn.clicked.connect(lambda: self.submit_SN_parameter(False))
        self.dropdown_para.cb.currentIndexChanged.connect(self.setChannel)

        for cid, info in self.config_table.items():
            w = info["widget"]
            if hasattr(w, "valueChanged"):
                w.valueChanged.connect(info["cmd_func"])
                w.valueChanged.connect(lambda _, w=w: w.setStyleSheet("background-color: yellow"))
            elif hasattr(w, "textChanged"):
                w.textChanged.connect(info["cmd_func"])
                w.textChanged.connect(lambda _, w=w: w.setStyleSheet("background-color: yellow"))

    def ieee754_int_to_float(self, int_val: int) -> float:
        """ 關鍵修正：解決負數顯示為 0 的問題 """
        try:
            packed = struct.pack('<I', int(int_val) & 0xFFFFFFFF)
            return round(struct.unpack('<f', packed)[0], 10)
        except:
            return 0.0

    def dump_parameter(self):
        """ 依據選定頻道 Dump 參數 """
        if not self.__act: return
        self.__act.flushInputBuffer("None");
        time.sleep(0.01)
        cfg = self.__act.dump_fog_parameters(self.__chVal)
        if isinstance(cfg, dict):
            self._updating_ui = True
            try:
                for cid, info in self.config_table.items():
                    raw = cfg.get(cid)
                    if raw is None: continue
                    f_val = self.ieee754_int_to_float(raw)
                    if info["type"] == "float":
                        val_s = f"{f_val:.10f}".rstrip('0').rstrip('.')
                    elif info["type"] == "sf":
                        val_s = f"{f_val * 10000:.6f}".rstrip('0').rstrip('.')
                    else:
                        val_s = str(int(raw))
                    w = info["widget"]
                    if hasattr(w, "setValue"):
                        w.setValue(float(val_s))
                    else:
                        w.setText(val_s)
                    w.setStyleSheet("background-color: white")
                self.dumpTrigerState = True
                QMessageBox.information(self, "Success", f"Channel {self.__chVal} dumped.")
            finally:
                self._updating_ui = False
        else:
            QMessageBox.warning(self, "Error", "Hardware not responding.")

    def exportTXTDump(self):
        """ 檔名規則：日期+_parameter.txt，遍歷 3 個頻道 """
        if not self.dumpTrigerState: QMessageBox.warning(self, "Warning", "Dump first."); return
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path, _ = QFileDialog.getSaveFileName(self, "Export", f"{now}_parameter.txt", "Text Files (*.txt)")
        if not path: return
        self.progressBar_export.show();
        self.progressBar_export.setValue(0)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# FOG Parameters Export - {now}\n\n")
                chs = {"Z": 1, "Y": 2, "X": 3}
                for name, ch_id in chs.items():
                    f.write(f"[{name} Channel]\n")
                    cfg = self.__act.dump_fog_parameters(ch_id)
                    if isinstance(cfg, dict):
                        for cid in sorted(self.config_table.keys(), key=int):
                            info = self.config_table[cid]
                            val = self.ieee754_int_to_float(cfg.get(cid, 0))
                            if info["type"] == "sf":
                                val *= 10000
                            elif info["type"] == "int":
                                val = int(cfg.get(cid, 0))
                            f.write(f"{cid}={val:<15} # {info['comment']}\n")
                    f.write("\n");
                    self.progressBar_export.setValue(self.progressBar_export.value() + 33)
            QMessageBox.information(self, "Success", "Export completed.");
            self.progressBar_export.setValue(100)
        finally:
            time.sleep(0.5); self.progressBar_export.hide()

    def importTXT(self):
        """ 依據選定頻道匯入 """
        path, _ = QFileDialog.getOpenFileName(self, "Import", "", "Text Files (*.txt)")
        if not path: return
        target = f"[{self.dropdown_para.cb.currentText()} Channel]"
        try:
            cfg_data, found = {}, False
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if target in line: found = True; continue
                    if found and line.startswith("["): break
                    if found and "=" in line:
                        k, v = line.split('#')[0].strip().split('=');
                        cfg_data[k.strip()] = v.strip()
            if not cfg_data: return
            self._updating_ui = False
            for cid, info in self.config_table.items():
                if cid in cfg_data:
                    w = info["widget"];
                    v = cfg_data[cid]
                    if hasattr(w, "setValue"):
                        w.setValue(float(v))
                    else:
                        w.setText(v)
            QMessageBox.information(self, "Success", f"Imported to {target}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import failed: {e}")

    def init_para(self):
        """ 帶進度條初始化 """
        if QMessageBox.question(self, "Init", "Reset parameters?") != QMessageBox.Yes: return
        prog = QProgressDialog("Initializing...", "Cancel", 0, len(INIT_PARAMETERS), self)
        prog.setWindowModality(Qt.WindowModal);
        prog.show()
        self._updating_ui = False
        for i, (cid, val) in enumerate(INIT_PARAMETERS.items()):
            if prog.wasCanceled(): break
            prog.setValue(i)
            if cid in self.config_table:
                info = self.config_table[cid]
                prog.setLabelText(f"Sending {info['comment']}...")
                w = info["widget"]
                if hasattr(w, "setValue"):
                    w.setValue(float(val))
                else:
                    w.setText(str(val))
                info["cmd_func"]()  # 使用表格中的 cmd_func 發送指令
                time.sleep(0.02);
                QtWidgets.QApplication.processEvents()
        prog.setValue(len(INIT_PARAMETERS))

    # --- 指令發送區域 (核心邏輯不變，僅加入更新鎖定) ---
    def send_FREQ_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_MOD_FREQ, self.freq.spin.value(), self.__chVal)

    def send_MOD_H_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_H, self.mod_H.spin.value(), self.__chVal)

    def send_MOD_L_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_MOD_AMP_L, self.mod_L.spin.value(), self.__chVal)

    def send_ERR_OFFSET_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_ERR_OFFSET, self.err_offset.spin.value(), self.__chVal)

    def send_POLARITY_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_POLARITY, self.polarity.spin.value(), self.__chVal)

    def send_WAIT_CNT_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_WAIT_CNT, self.wait_cnt.spin.value(), self.__chVal)

    def send_AVG_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_ERR_AVG, self.avg.spin.value(), self.__chVal)

    def send_GAIN1_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_GAIN1, self.gain1.spin.value(), self.__chVal)

    def send_GAIN2_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_GAIN2, self.gain2.spin.value(), self.__chVal)

    def send_FB_ON_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_FB_ON, self.fb_on.spin.value(), self.__chVal)

    def send_DAC_GAIN_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_DAC_GAIN, self.dac_gain.spin.value(), self.__chVal)

    def send_CONST_STEP_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_FOG_CONST_STEP, self.const_step.spin.value(), self.__chVal)

    def send_CUTOFF_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.cutoff.spin.value())))
        self.__act.writeImuCmd(CMD_FOG_CUTOFF, v[0], self.__chVal)

    def send_OUT_TH_EN_CMD(self):
        if getattr(self, '_updating_ui', False): return
        self.__act.writeImuCmd(CMD_OUT_TH_EN, self.out_th_en.spin.value(), self.__chVal)

    def send_OUT_TH_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.out_th.le.text())))
        self.__act.writeImuCmd(CMD_OUT_TH, v[0], self.__chVal)

    def send_SF0_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.sf0.le.text()) * 0.0001))
        self.__act.writeImuCmd(CMD_FOG_SF0, v[0], self.__chVal)

    def send_SF1_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.sf1.le.text()) * 0.0001))
        self.__act.writeImuCmd(CMD_FOG_SF1, v[0], self.__chVal)

    def send_BIAS_T1_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.T1.le.text())))
        self.__act.writeImuCmd(CMD_FOG_BIAS_T1, v[0], self.__chVal)

    def send_BIAS_T2_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.T2.le.text())))
        self.__act.writeImuCmd(CMD_FOG_BIAS_T2, v[0], self.__chVal)

    def send_SFB_SLOPE_1_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.slope1.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_1, v[0], self.__chVal)

    def send_SFB_SLOPE_2_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.slope2.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_2, v[0], self.__chVal)

    def send_SFB_SLOPE_3_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.slope3.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_SLOPE_3, v[0], self.__chVal)

    def send_SFB_OFFSET_1_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.offset1.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_1, v[0], self.__chVal)

    def send_SFB_OFFSET_2_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.offset2.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_2, v[0], self.__chVal)

    def send_SFB_OFFSET_3_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.offset3.le.text())))
        self.__act.writeImuCmd(CMD_FOG_SFB_OFFSET_3, v[0], self.__chVal)

    def send_ACCL_SF0_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.ACCLsta.le.text()) * 0.0001))
        self.__act.writeImuCmd(CMD_ACCL_SF0, v[0], self.__chVal)

    def send_ACCL_SF1_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.ACCLstb.le.text()) * 0.0001))
        self.__act.writeImuCmd(CMD_ACCL_SF1, v[0], self.__chVal)

    def send_ACCL_SFB_SLOPE_1_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.ACCL_slope1.le.text())))
        self.__act.writeImuCmd(CMD_ACCL_SFB_SLOPE_1, v[0], self.__chVal)

    def send_ACCL_SFB_OFFSET_1_CMD(self):
        if getattr(self, '_updating_ui', False): return
        v = struct.unpack('<I', struct.pack('<f', float(self.ACCL_offset1.le.text())))
        self.__act.writeImuCmd(CMD_ACCL_SFB_OFFSET_1, v[0], self.__chVal)

    def changeWidgetDisable(self):
        self.submit_Btn.setDisabled(not self.startFunc_Box.isChecked())
        self.SN_Str.setDisabled(not self.startFunc_Box.isChecked())

    def dump_SN_parameter(self):
        self.__act.flushInputBuffer("None");
        SN = self.__act.dump_SN_parameters(3)
        if SN != "發生參數值為空的狀況": self.SN_Str.setText(str(SN)); self.SN_Str.setStyleSheet(
            'background-color: white')

    def submit_SN_parameter(self, importStatus=False):
        txt = self.SN_Str.text()
        if txt:
            try:
                asciis = [int(hex(x), 16) for x in txt.encode('utf-8')]
                while len(asciis) < 12: asciis.append(0)
                self.__act.update_SN_parameters(asciis);
                self.SN_Str.setStyleSheet('background-color: white')
                if not importStatus: QMessageBox.information(self, "SN", "Written to device.")
            except Exception as e:
                logger.error(f"SN submit error: {e}")

    def setChannel(self):
        t = self.dropdown_para.cb.currentText()
        if t == "X":
            self.__chVal = 3
        elif t == "Z":
            self.__chVal = 1
        else:
            self.__chVal = 2

    def loadCSVandWriteBias(self):
        if not self.dumpTrigerState: QMessageBox.warning(self, "Warning", "Dump first."); return
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if path:
            data = cmn.loadCSVFile(path)
            try:
                t = data.get("TEMP Breakpoints");
                s = data.get("slope");
                o = data.get("offset")
                self.T1.le.setText(f'{t[3]:.1f}');
                self.T2.le.setText(f'{t[1]:.1f}')
                self.slope1.le.setText(f'{(float(s[4]) * -1):.10f}');
                self.slope2.le.setText(f'{(float(s[2]) * -1):.10f}');
                self.slope3.le.setText(f'{(float(s[0]) * -1):.10f}')
                self.offset1.le.setText(f'{(float(o[4]) * -1):.10f}');
                self.offset2.le.setText(f'{(float(o[2]) * -1):.10f}');
                self.offset3.le.setText(f'{(float(o[0]) * -1):.10f}')
            except:
                QMessageBox.warning(self, "CSV", "Data Error.")


if __name__ == "__main__":
    app = QApplication(sys.argv)


    class Dummy:
        def __getattr__(self, name):
            def m(*a, **k): return {"0": 163, "17": 0} if "dump" in name else 0

            return m


    win = pig_parameters_widget(Dummy(), "Preview")
    win.show();
    sys.exit(app.exec())