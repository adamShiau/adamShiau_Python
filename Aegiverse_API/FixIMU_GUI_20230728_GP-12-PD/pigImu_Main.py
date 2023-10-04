""" ####### log stuff creation, always on the top ########  """
import os
import builtins
import pathlib
from datetime import datetime

import yaml
import logging.config

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

LOG_PATH = './logs/'
LOGGER_NAME = 'main'
builtins.LOGGER_NAME = LOGGER_NAME
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
f_log = open('log_config.yaml', 'r', encoding='utf-8')
config = yaml.safe_load(f_log)
logging.config.dictConfig(config)
logger = logging.getLogger(LOGGER_NAME)
f_log.close()
logger.info('create log stuff done, ')
logger.info('process start')
""" ####### end of log stuff creation ########  """

import sys

sys.path.append("../")
from myLib import common as cmn
from myLib.myGui.mygui_serial import *
import time
from myLib.mySerial.Connector import Connector
from myLib.myGui.pig_parameters_widget import pig_parameters_widget
from myLib.myGui.pig_parameters_widget import CMD_FOG_TIMER_RST
from myLib.myGui.pig_menu_manager import pig_menu_manager
from myLib.myGui import analysis_Allan, analysis_TimingPlot, myRadioButton, autoSave
from PyQt5.QtWidgets import *
from pigImu_Widget import pigImuWidget as TOP
from pigImuReader import pigImuReader as ACTION
from pigImuReader import IMU_DATA_STRUCTURE, IMU_Angle_STRUCTURE
from myLib.myGui.myTableWidget import VersionTable
import numpy as np


PRINT_DEBUG = 0
OUTPUT_ONE_AXIS = True


class mainWindow(QMainWindow):
    is_port_open_qt = pyqtSignal(bool)
    vers_open_qt = pyqtSignal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()
        self.press_stop = False
        self.resize(1450, 800)
        self.__portName = None
        self.GUIvers = "GP-12-PD\nstatus: active"
        self.setWindowTitle("Aegiverse IMU GUI")
        self.__connector = Connector()
        self.__isFileOpen = False
        self.top = TOP()
        self.act = ACTION()
        self.first_run_flag = True
        #self.imudata_file = cmn.data_manager(fnum=0)
        self.imudata_file_auto = autoSave.atSave_PC_v3(fnum=0)
        self.act.isCali = True
        self.menu = self.menuBar()
        self.pig_menu = pig_menu_manager(self.menu, self)
        # -------menu obj------#
        self.pig_parameter_widget = None
        self.pig_cali_menu = calibrationBlock()
        self.pig_initial_setting_menu = myRadioButton.radioButtonBlock_2('SYNC MODE', 'OFF', 'ON', False)  # True
        # means setting 'OFF' state value to True
        self.analysis_allan = analysis_Allan.analysis_allan_widget(['fog', 'wx', 'wy', 'wz', 'ax', 'ay', 'az'])
        self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
            ['fog', 'wx', 'wy', 'wz', 'ax', 'ay', 'az', 'T'])
        self.pig_ver = VersionTable()
        # -------end of menu obj------#
        self.linkfunction()
        self.act.arrayNum = 10
        self.mainUI()
        # self.imudata = self.resetDataContainer()
        #
        self.imudata = {k: np.empty(0) for k in set(IMU_Angle_STRUCTURE)}
        self.__debug = debug_en
        self.t_start = time.perf_counter()
        self.autoComPort_v2()  # 直接自動撈取COM Port，且撈取對應的儀器名稱
        self.reset_flag = 0  # 紀錄是否有reset 若有為1，若沒有為0
        self.DetectNum = 0  # 紀錄撈資料出現錯誤時，只能print一次
        self.first_draw = 0


    def closeEvent(self, *args, **kwargs):  # 當關閉視窗時，會被執行的函式
        if self.top.stop_bt.isEnabled() and self.__connector.portDoNotConnectStatus == False:
            self.stop()
        if self.top.usb.bt_disconnect.isEnabled():
            self.disconnect()
        # 判斷是用手動觸發為True，反之自動斷線為False
        self.act.Stop_NotTimeout = True

        sys.exit()

    def mainUI(self):
        self.setCentralWidget(self.top)

    def linkfunction(self):
        # usb connection
        self.top.usb.bt_update.clicked.connect(self.updateComPort)
        self.top.usb.cb.currentIndexChanged.connect(self.selectComPort)
        self.top.usb.bt_connect.clicked.connect(self.connect)
        self.top.usb.bt_disconnect.clicked.connect(self.disconnect)
        # bt connection
        self.top.read_bt.clicked.connect(self.start)
        self.top.stop_bt.clicked.connect(self.stop)
        # rb connection
        self.top.kal_filter_rb.toggled.connect(lambda: self.update_kalFilter_en(self.top.kal_filter_rb))
        # pyqtSignal connection
        self.act.imudata_qt.connect(self.collectData)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)
        self.act.buffer_qt.connect(self.printBuffer)
        self.is_port_open_qt.connect(self.is_port_open_status_manager)
        self.act.Portstatus_qt.connect(self.autoDetectComport)
        self.imudata_file_auto.createFile_Error_qt.connect(self.cannot_create_file_stop)
        self.act.deviceReset_qt.connect(self.autoinstrumentReset)
        self.act.oneHundred_data_qt.connect(self.collectData_two)
        self.act.hourChange_qt.connect(self.hourIsChange)
        # menu trigger connection
        self.pig_menu.action_trigger_connect([self.show_parameters,
                                              self.show_calibration_menu,
                                              self.show_plot_data_menu,
                                              self.show_cal_allan_menu,
                                              self.show_initial_setting_menu,
                                              self.show_version_menu
                                              ])
        # file name le
        self.top.save_block.le_filename.editingFinished.connect(
            lambda: self.file_name_le_connect(self.top.save_block.le_filename))
        self.vers_open_qt.connect(self.version_open_status_manager)
    def file_name_le_connect(self, obj):
        cmn.print_debug('file name: %s' % obj.text(), PRINT_DEBUG)
        filename = obj.text() + self.top.save_block.le_ext.text()
        self.analysis_timing_plot.pbar.set_filename_ext(filename)
        self.analysis_allan.pbar.set_filename_ext(filename)

    def show_parameters(self):
        self.pig_parameter_widget.show()

    def show_calibration_menu(self):
        self.pig_cali_menu.show()

    def show_initial_setting_menu(self):
        self.pig_initial_setting_menu.show()

    def show_plot_data_menu(self):
        self.analysis_timing_plot.show()

    def show_cal_allan_menu(self):
        self.analysis_allan.show()

    def show_version_menu(self):
        self.pig_ver.show()

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()

    def printBuffer(self, val):
        self.top.buffer_lb.lb.setText(str(val))

    def printGPS_Time(self, val):
        self.top.gpstime_lb.lb.setText(val)

    def printPdTemperature(self, val):
        if (time.perf_counter() - self.t_start) > 0.5:
            self.top.pd_temp_lb.lb.setText(str(val))
            self.t_start = time.perf_counter()

    def printUpdateRate(self, t_list):
        update_rate = round(((t_list[-1] - t_list[0]) / (len(t_list) - 1)) ** -1, 1)
        self.top.data_rate_lb.lb.setText(str(update_rate))

    def updateComPort(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.addPortItems(portNum, portList)
        if portNum != 0:
            if self.top.usb.bt_disconnect.isEnabled(): # 當GUI被連接的狀況下，點選更新COM Port時的防呆
                self.disconnect()
            self.top.usb.bt_connect.setEnabled(True) # 判斷是否已連接儀器，並顯示連接btn

    def selectComPort(self):
        self.__portName = self.top.usb.selectPort()

    def autoComPort_v2(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.autoComport_v2(portNum, portList)
        if portNum != 0:
            self.top.usb.bt_connect.setEnabled(True)  # 判斷是否已連接儀器，並顯示連接btn


    # 判斷COM Port是否有鬆脫或是沒電的狀況，並執行此功能
    def autoDetectComport(self, status):
        if not self.act.Stop_NotTimeout:  # 若不是手動的狀況下，才會執行自動斷線的部分
            self.imudata_file_auto.close_hour_folder()
            self.imudata_file_auto.reset_hh_reg()
            # self.top.save_block.rb.setChecked(False)
            # self.imudata_file.close()
            if (self.first_run_flag == False):  # 無法connect做判斷用的
                self.act.quit()
                self.act.wait()
            # self.__connector.portDoNotConnectStatus = False
            self.press_stop = True
            self.first_run_flag = True
            self.act.start_read = 0
            self.reset_flag = 1
            self.DetectNum += 1
            #self.act.InTheMoment_GUI_status = "STOP"  # 避免圖形看起來有問題
            self.disconnect()
            self.top.usb.autoDetectStatusLabel(False)  # 鎖connect & disconnect
            self.top.usb.showPortName_doesnot_connect()
            self.vers_open_qt.emit(False)
            if self.DetectNum == 1:
                logger.error('The GUI is auto-disconnect now. (原因:斷電、USB鬆脫)')
                mestitle = "儀器斷線的錯誤"  # 儀器斷線的錯誤
                Mes = "1.請檢查儀器的電源是否保持開啟。\n 2.請檢查USB是否已被拔除了。\n 3.請確認選擇的COM Port(USB)名稱是否為本公司的儀器。"
                self.WidgetMes(mestitle, Mes)
                # self.mesWindow(mestitle, Mes)

    def cannot_create_file_stop(self, status):  # 判斷資料夾無法建立時執行的部分
        self.act.isRun = False
        # self.__connector.portDoNotConnectStatus = True
        self.act.quit()
        self.act.wait()
        self.imudata_file_auto.reset_hh_reg()
        #self.top.save_block.rb.setChecked(False)
        self.press_stop = True
        self.first_run_flag = True
        self.act.start_read = 0
        self.reset_flag = 1
        self.top.setBtnEnable(True)
        logger.error('Error occurred while creating the file.')
        mesTitle = "建立檔案的過程出現錯誤"
        self.WidgetMes(mesTitle, self.imudata_file_auto.errorMes)
        # self.mesWindow(mesTitle, self.imudata_file_auto.errorMes)  # 建檔的部分出現錯誤

    def WidgetMes(self, mestitle, errorMes):
        mesbox = QtWidgets.QMessageBox(self.top)
        mesbox.critical(self.top, mestitle, errorMes)

    def version_open_status_manager(self, open):
        self.pig_menu.version_setEnable(open)

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connect(self):
        is_port_open = self.act.connect(self.__connector, self.__portName, 115200)
        if (is_port_open != False):
            self.is_port_open_qt.emit(is_port_open)
            self.vers_open_qt.emit(is_port_open)
            self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
            self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
            self.act.isExtMode = self.pig_initial_setting_menu.btn_status
            self.act.Stop_NotTimeout = False
            time.perf_counter()
            # 取得版號
            # VerText = self.act.getVersion()
            # self.pig_ver.createTable(VerText, self.GUIvers)
        # print(self.act.isExtMode)

    def disconnect(self, status=True):
        if self.top.stop_bt.isEnabled() == True:
            self.stop()
            time.sleep(1)
        else:
            if status:  # 判斷是用手動觸發為True，反之自動斷線為False
                self.act.Stop_NotTimeout = True
        is_port_open = self.act.disconnect()
        self.is_port_open_qt.emit(is_port_open)
        self.top.autoDetect_setBtnEnable(False)  # 鎖read & stop

    def imuThreadStopDetect(self):
        #self.imudata = self.resetDataContainer()
        # 230826
        self.imudata = {k: np.empty(0) for k in set(IMU_Angle_STRUCTURE)}

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetFPGATimer(self):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1)
        #print('main: reset FPGA time')

    def autoinstrumentReset(self):
        self.imudata_file_auto.close_hour_folder()
        self.imudata_file_auto.reset_hh_reg()
        self.reset_flag = 1
        logger.info("The device is reset. (儀器重置)")
        self.imudata_file_auto.create_data_folder(True)
        self.imudata_file_auto.auto_create_folder(True)

    def start(self):
        # self.resetFPGATimer()
        self.act.readIMU()
        self.act.isRun = True
        self.press_stop = False
        self.act.start()
        self.top.setBtnEnable(False)
        if self.reset_flag == 1:
            self.reset_flag = 0
            self.DetectNum = 0
            self.act.recording_divice_reset_time = 0
            logger.info("The device is reset. (被切斷的重啟)")
        else:
            self.act.recording_divice_reset_time = 0
            logger.info('The GUI is started to read the data.')
        #file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()

        file_name = str(pathlib.Path().absolute())
        self.imudata_file_auto.dirCreateStatus = True
        self.imudata_file_auto.data_path = file_name
        self.imudata_file_auto.start = True
        self.imudata_file_auto.create_data_folder(True)
        self.imudata_file_auto.auto_create_folder(True)
        # 禁用parameter
        self.top.startDisableControlElement(True)
        # 判斷是否為timeout，還是手動的方式斷線
        self.act.Stop_NotTimeout = False
        # 當斷線重新讀取檔案之後，reset的值需要重新歸零使用 20230816
        self.act.recording_device_reset_time = 0
        # 讀取資料之後，不能開啟版號
        self.vers_open_qt.emit(False)
        # file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
        # self.imudata_file.name = file_name
        # self.imudata_file.open(self.top.save_block.rb.isChecked())


    def stop(self):
        # self.resetFPGATimer()
        self.top.setBtnEnable(True)
        self.act.isRun = False
        self.top.startDisableControlElement(False)  # 啟用parameter
        self.act.Stop_NotTimeout = True
        #self.top.save_block.rb.setChecked(False)
        self.imudata_file_auto.close_hour_folder()
        self.imudata_file_auto.reset_hh_reg()
        #self.imudata_file.close()
        self.press_stop = True
        self.first_run_flag = True
        self.act.start_read = 0
        #self.act.InTheMoment_GUI_status = "STOP"
        self.vers_open_qt.emit(True)
        logger.info('The GUI is stopped to read the data.')
        #print('press stop')

    @property
    def press_stop(self):
        return self.__stop

    @press_stop.setter
    def press_stop(self, stop):
        self.__stop = stop

    @property
    def first_run_flag(self):
        return self.__first_run_flag

    @first_run_flag.setter
    def first_run_flag(self, flag):
        self.__first_run_flag = flag
        # self.act.first_run_flag = flag

    # def collectData(self, imudata):
    #     if not self.press_stop and (len(imudata["PD_TEMP"]) != 0) :
    #         # print('collectData pre: ', len(imudata['TIME']), end=', ')
    #         # print(imudata['TIME'])
    #         #
    #         # print('collectData after: ', len(imudata['TIME']), end=', ')
    #         # print(imudata['TIME'])
    #         # self.first_run_flag = False
    #         self.act.get_Port_connect_status()  # 判斷COM Port是否有被拔除
    #         #input_buf = self.act.readInputBuffer()
    #         t0 = time.perf_counter()
    #         # imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
    #         # print(len(imudata["PD_TEMP"]))
    #         self.printPdTemperature(imudata["PD_TEMP"][0])
    #         # self.printPdTemperature(0)
    #         t1 = time.perf_counter()
    #         # self.imudata = cmn.dictOperation(self.imudata, imudata, "APPEND", IMU_DATA_STRUCTURE)
    #         self.imudata["TIME"] = np.append(self.imudata["TIME"], imudata["TIME"])
    #         # self.imudata["ADXL_AX"] = np.append(self.imudata["ADXL_AX"], imudata["ADXL_AX"])
    #         # self.imudata["ADXL_AY"] = np.append(self.imudata["ADXL_AY"], imudata["ADXL_AY"])
    #         # self.imudata["ADXL_AZ"] = np.append(self.imudata["ADXL_AZ"], imudata["ADXL_AZ"])
    #         # self.imudata["NANO33_WX"] = np.append(self.imudata["NANO33_WX"], imudata["NANO33_WX"])
    #         # self.imudata["NANO33_WY"] = np.append(self.imudata["NANO33_WY"], imudata["NANO33_WY"])
    #         # self.imudata["NANO33_WZ"] = np.append(self.imudata["NANO33_WZ"], imudata["NANO33_WZ"])
    #         self.imudata["PIG_WZ"] = np.append(self.imudata["PIG_WZ"], imudata["PIG_WZ"])
    #         self.imudata["PIG_ERR"] = np.append(self.imudata["PIG_ERR"], imudata["PIG_ERR"])
    #         self.imudata["PD_TEMP"] = np.append(self.imudata["PD_TEMP"], imudata["PD_TEMP"])
    #         self.imudata["YEAR"] = np.append(self.imudata["YEAR"], imudata["YEAR"])
    #         self.imudata["MON"] = np.append(self.imudata["MON"], imudata["MON"])
    #         self.imudata["DAY"] = np.append(self.imudata["DAY"], imudata["DAY"])
    #         self.imudata["HOUR"] = np.append(self.imudata["HOUR"], imudata["HOUR"])
    #         self.imudata["MIN"] = np.append(self.imudata["MIN"], imudata["MIN"])
    #         self.imudata["SEC"] = np.append(self.imudata["SEC"], imudata["SEC"])
    #
    #         # print(len(self.imudata["TIME"]), end=", ")
    #         datanum = 1000
    #         if len(self.imudata["TIME"]) > datanum:
    #             self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             # self.imudata["ADXL_AX"] = self.imudata["ADXL_AX"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             # self.imudata["ADXL_AY"] = self.imudata["ADXL_AY"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             # self.imudata["ADXL_AZ"] = self.imudata["ADXL_AZ"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             # self.imudata["NANO33_WX"] = self.imudata["NANO33_WX"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             # self.imudata["NANO33_WY"] = self.imudata["NANO33_WY"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             # self.imudata["NANO33_WZ"] = self.imudata["NANO33_WZ"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["PIG_WZ"] = self.imudata["PIG_WZ"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["PIG_ERR"] = self.imudata["PIG_ERR"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["PD_TEMP"] = self.imudata["PD_TEMP"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["YEAR"] = self.imudata["YEAR"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["MON"] = self.imudata["MON"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["DAY"] = self.imudata["DAY"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["HOUR"] = self.imudata["HOUR"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["MIN"] = self.imudata["MIN"][self.act.arrayNum:self.act.arrayNum + datanum]
    #             self.imudata["SEC"] = self.imudata["SEC"][self.act.arrayNum:self.act.arrayNum + datanum]
    #         t2 = time.perf_counter()
    #         # debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
    #         #              + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
    #         # cmn.print_debug(debug_info, self.__debug)
    #         debug_info = "MAIN: ," + str(round((t2 - t0) * datanum, 5)) + ", " \
    #                      + str(round((t1 - t0) * datanum, 5)) + ", " + str(round((t2 - t1) * datanum, 5))
    #         cmn.print_debug(debug_info, self.__debug)
    #         # print(imudata["PIG_WZ"])
    #
    #         # if OUTPUT_ONE_AXIS:
    #         #     datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["PIG_WZ"]
    #         #     # datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["NANO33_WZ"]
    #         #         , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"], imudata["PD_TEMP"]]
    #         #     data_fmt = "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f"
    #         # else:
    #         #     datalist = [imudata["TIME"], imudata["PIG_WZ"], imudata["NANO33_WX"], imudata["NANO33_WY"],
    #         #                 imudata["NANO33_WZ"]
    #         #         , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"], imudata["PD_TEMP"]]
    #         #     data_fmt = "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f"
    #
    #         t2 = time.perf_counter()
    #         # debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
    #         #              + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
    #         debug_info = "MAIN: ," + str(round((t2 - t0) * datanum, 5)) + ", " \
    #                      + str(round((t1 - t0) * datanum, 5)) + ", " + str(round((t2 - t1) * datanum, 5))
    #         cmn.print_debug(debug_info, self.__debug)
    #         # print(imudata["PIG_WZ"])
    #
    #         # 將毫秒顯示兩位數
    #         ms_format_to_2 = (imudata['mSEC'][0] // 10) % 100
    #         ms_format_str = ''
    #         if ms_format_to_2 < 10:
    #             mes_str = str(ms_format_to_2)
    #             ms_format_str = '0%s' % mes_str[:-2]
    #         else:
    #             ms_format_str = str(ms_format_to_2)[:-2]
    #         # 撈取PC的時間
    #         gps_time = '%d/%d/%d %d:%d:%d' % (imudata['YEAR'][0], imudata['MON'][0], imudata['DAY'][0],
    #                                              imudata['HOUR'][0], imudata['MIN'][0], imudata['SEC'][0])
    #
    #         # datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["PIG_WZ"]
    #         #     , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]
    #         #     , imudata["YEAR"], imudata["MON"], imudata["DAY"], imudata["HOUR"]
    #         #     , imudata["MIN"], imudata["SEC"], imudata["mSEC"]]
    #         # data_fmt = "%.3f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%d,%d,%d,%d,%d,%d,%d"
    #         # datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["PIG_WZ"]
    #         #     , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"], imudata["PD_TEMP"]]
    #         # datalist = [imudata["TIME"], imudata["PIG_WZ"], imudata["PD_TEMP"], imudata["YEAR"], imudata["MON"], imudata["DAY"], imudata["HOUR"]
    #         #     , imudata["MIN"], imudata["SEC"], imudata["mSEC"]]
    #         #
    #         # data_fmt = "%.3f,% 3.5f,% 3.1f,%d,%02d,%02d,%02d,%02d,%02d,%03d"
    #
    #         self.printGPS_Time(gps_time)
    #         self.plotdata(self.imudata)
    #         self.printUpdateRate(self.imudata["TIME"])
    #         # print(len(self.imudata["TIME"]))
    def collectData(self, imudata):
        if not self.press_stop:
            # print('collectData pre: ', len(imudata['TIME']), end=', ')
            # print(imudata['TIME'])
            #
            # print('collectData after: ', len(imudata['TIME']), end=', ')
            # print(imudata['TIME'])
            # self.first_run_flag = False
            self.act.get_Port_connect_status()  # 判斷COM Port是否有被拔除
            #input_buf = self.act.readInputBuffer()
            t0 = time.perf_counter()

            t1 = time.perf_counter()
            # self.imudata = cmn.dictOperation(self.imudata, imudata, "APPEND", IMU_DATA_STRUCTURE)
            self.imudata["AngleZ"] = np.append(self.imudata["AngleZ"], imudata["AngleZ"])

            # print(len(self.imudata["TIME"]), end=", ")
            datanum = 1000
            if len(self.imudata["AngleZ"]) > datanum:
                self.imudata["AngleZ"] = self.imudata["AngleZ"][self.act.arrayNum:self.act.arrayNum + datanum]

            t2 = time.perf_counter()
            # debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
            #              + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
            # cmn.print_debug(debug_info, self.__debug)
            debug_info = "MAIN: ," + str(round((t2 - t0) * datanum, 5)) + ", " \
                         + str(round((t1 - t0) * datanum, 5)) + ", " + str(round((t2 - t1) * datanum, 5))
            cmn.print_debug(debug_info, self.__debug)
            # print(imudata["PIG_WZ"])

            # if OUTPUT_ONE_AXIS:
            #     datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["PIG_WZ"]
            #     # datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["NANO33_WZ"]
            #         , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"], imudata["PD_TEMP"]]
            #     data_fmt = "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f"
            # else:
            #     datalist = [imudata["TIME"], imudata["PIG_WZ"], imudata["NANO33_WX"], imudata["NANO33_WY"],
            #                 imudata["NANO33_WZ"]
            #         , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"], imudata["PD_TEMP"]]
            #     data_fmt = "%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f"

            t2 = time.perf_counter()
            # debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
            #              + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
            debug_info = "MAIN: ," + str(round((t2 - t0) * datanum, 5)) + ", " \
                         + str(round((t1 - t0) * datanum, 5)) + ", " + str(round((t2 - t1) * datanum, 5))
            cmn.print_debug(debug_info, self.__debug)
            # print(imudata["PIG_WZ"])

            # # 將毫秒顯示兩位數
            # ms_format_to_2 = (imudata['mSEC'][0] // 10) % 100
            # ms_format_str = ''
            # if ms_format_to_2 < 10:
            #     mes_str = str(ms_format_to_2)
            #     ms_format_str = '0%s' % mes_str[:-2]
            # else:
            #     ms_format_str = str(ms_format_to_2)[:-2]
            # # 撈取PC的時間
            # gps_time = '%d/%d/%d %d:%d:%d' % (imudata['YEAR'][0], imudata['MON'][0], imudata['DAY'][0],
            #                                      imudata['HOUR'][0], imudata['MIN'][0], imudata['SEC'][0])

            # datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["PIG_WZ"]
            #     , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]
            #     , imudata["YEAR"], imudata["MON"], imudata["DAY"], imudata["HOUR"]
            #     , imudata["MIN"], imudata["SEC"], imudata["mSEC"]]
            # data_fmt = "%.3f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%d,%d,%d,%d,%d,%d,%d"
            # datalist = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["PIG_WZ"]
            #     , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"], imudata["PD_TEMP"]]
            # datalist = [imudata["TIME"], imudata["PIG_WZ"], imudata["PD_TEMP"], imudata["YEAR"], imudata["MON"], imudata["DAY"], imudata["HOUR"]
            #     , imudata["MIN"], imudata["SEC"], imudata["mSEC"]]
            #
            # data_fmt = "%.3f,% 3.5f,% 3.1f,%d,%02d,%02d,%02d,%02d,%02d,%03d"

            #self.printGPS_Time(gps_time)
            self.plotdata(self.imudata)
            #self.printUpdateRate(self.imudata["TIME"])
            # print(len(self.imudata["TIME"]))

    ### def collectData_two(self, imudata):
    #     if not self.press_stop:
    #         self.act.get_Port_connect_status()  # 判斷COM Port是否有被拔除
    #         #input_buf = self.act.readInputBuffer()
    #
    #         # datalist = [imudata["time_accumulate"], imudata["TIME"], imudata["PIG_WZ"], imudata["PD_TEMP"], imudata["YEAR"], imudata["MON"],
    #         #             imudata["DAY"], imudata["HOUR"]
    #         #     , imudata["MIN"], imudata["SEC"], imudata["mSEC"]]
    #         datalist = [imudata["time_accumulate"], imudata["TIME"], imudata["PIG_WZ"], imudata["PD_TEMP"]]
    #
    #         # data_fmt = "%06d,%.3f,%3.5f,%3.1f,%d,%02d,%02d,%02d,%02d,%02d,%03d"
    #         data_fmt = "%06d,%.3f,%3.5f,%3.1f"
    #
    #         self.imudata_file_auto.saveData(datalist, data_fmt)
    #         self.imudata_file_auto.judgment_hh(True)
    #         #self.clearTimeAccumulate()
    #         # print(len(self.imudata["TIME"]))

    def collectData_two(self, imudata):
        if not self.press_stop:
            self.act.get_Port_connect_status()  # 判斷COM Port是否有被拔除
            #input_buf = self.act.readInputBuffer()

            # datalist = [imudata["time_accumulate"], imudata["TIME"], imudata["PIG_WZ"], imudata["PD_TEMP"], imudata["YEAR"], imudata["MON"],
            #             imudata["DAY"], imudata["HOUR"]
            #     , imudata["MIN"], imudata["SEC"], imudata["mSEC"]]
            datalist = [imudata["TXTVal"]]

            # data_fmt = "%06d,%.3f,%3.5f,%3.1f,%d,%02d,%02d,%02d,%02d,%02d,%03d"
            data_fmt = "%s"

            self.imudata_file_auto.saveData(datalist, data_fmt)
            self.imudata_file_auto.judgment_hh(True)
            #self.clearTimeAccumulate()
            # print(len(self.imudata["TIME"]))

    def hourIsChange(self, status):  # 20230712紀錄是否已經換小時的時間了
        self.imudata_file_auto.judgment_hh(status)

    def plotdata(self, imudata):

        self.top.plot1.ax1.setData(imudata["AngleZ"])
        self.top.plot1.p.hideAxis("bottom") # 不顯示底部(x軸)的方式
        #self.top.plot1.ax_time.setData(imudata["AngleZ"])
        # self.top.plot1.ax1.setData(imudata["TIME"], imudata["PIG_ERR"])

    # def plotdata(self, imudata):
    #     # print('plotdata: ', imudata['TIME'])
    #     if self.top.plot1_unit_rb.btn_status == 'dph':
    #         factor = 3600
    #     else:
    #         factor = 1
    #
    #     if self.top.plot1_showWz_cb.cb_1.isChecked():
    #         self.top.plot1.ax1.setData(imudata["PIG_WZ"] * factor)
    #         self.top.plot1.p.hideAxis("bottom") # 不顯示底部(x軸)的方式
    #         self.top.plot1.ax_time.setData(imudata["TIME"], imudata["PIG_WZ"] * factor)
    #         # self.top.plot1.ax1.setData(imudata["TIME"], imudata["PIG_ERR"])
    #     else:
    #         self.top.plot1.ax1.clear()
    #     if self.top.plot1_showWz_cb.cb_2.isChecked():
    #         self.top.plot1.ax2.setData(imudata["TIME"], imudata["NANO33_WZ"] * factor)
    #     else:
    #         self.top.plot1.ax2.clear()
    #
    #     # self.top.plot2.ax.setData(imudata["TIME"], imudata["ADXL_AX"])
    #     # self.top.plot3.ax.setData(imudata["TIME"], imudata["ADXL_AY"])
    #     # self.top.plot4.ax.setData(imudata["TIME"], imudata["ADXL_AZ"])
    #     # self.top.plot5.ax.setData(imudata["TIME"], imudata["NANO33_WX"])
    #     # self.top.plot6.ax.setData(imudata["TIME"], imudata["NANO33_WY"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
