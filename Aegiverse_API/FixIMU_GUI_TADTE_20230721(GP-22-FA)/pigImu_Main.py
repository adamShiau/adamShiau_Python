""" ####### log stuff creation, always on the top ########  """
import json
import os
import builtins
import pathlib
import threading
from datetime import datetime, timedelta

import yaml
import logging.config

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from MySerial.KVHReader import KVHReader, KVHReaderQthread

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
from pigImu_Widget import pigImuWidget_Tab as TOP
from pigImuReader import pigImuReader as ACTION, KVH_DATA_STRUCTURE_MANI, VBOX_Time_DATA_STRUCTURE_MAIN
from pigImuReader import IMU_DATA_STRUCTURE, Posture_DATA_STRUCTURE, ChangeVersion_DATA_STRUCTURE, VBOX_DATA_STRUCTURE_MAIN, Integration_DATA_STRUCTURE
import numpy as np
from four_AnalysisByCircle import plane_nav
from myLib.myKM.main import Driving
from myLib.myGui.realTime_map import realTime_MapUI
from pigImuMapReader import pigImuMapReader

from MySerial.VBOXReader import VBOXReader, ReaderQthread
from myLib.myGui.pig_W_A_calibration_parameter_widget import pig_calibration_widget

PRINT_DEBUG = 0
OUTPUT_ONE_AXIS = True


class mainWindow(QMainWindow):
    is_port_open_qt = pyqtSignal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()
        self.press_stop = False
        self.resize(1450, 800)
        self.__portName = None
        self.setWindowTitle("Aegiverse IMU GUI  (version: GP-23-FA  status: active)")
        self.__connector = Connector()
        self.__isFileOpen = False
        self.top = TOP()
        self.act = ACTION()
        self.first_run_flag = True
        self.imudata_file = cmn.data_manager(fnum=0)
        nowFileP = os.getcwd()
        jsonP = nowFileP + "//DrawDa//ImuData.json"
        self.imuJason_file = cmn.json_manager("C:\\github\\TADT\\FixIMU_GUI_TADTE_20240102(GP-23-FA)\\DrawDa\\ImuData.json")
        #self.imudata_file_auto = autoSave.atSave_PC_v3(fnum=0)
        self.act.isCali = True
        self.menu = self.menuBar()
        self.pig_menu = pig_menu_manager(self.menu, self)
        # -------menu obj------#
        self.pig_parameter_widget = None
        self.cali_parameter_menu = None
        self.pig_cali_menu = calibrationBlock()
        self.pig_initial_setting_menu = myRadioButton.radioButtonBlock_2('SYNC MODE', 'OFF', 'ON', False)  # True
        # means setting 'OFF' state value to True
        self.analysis_allan = analysis_Allan.analysis_allan_widget(['fog', 'wx', 'wy', 'wz', 'ax', 'ay', 'az'])
        self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
            ['fog', 'wx', 'wy', 'wz', 'ax', 'ay', 'az', 'T'])
        self.mapUI = realTime_MapUI() # 地圖視窗
        self.mapRead = pigImuMapReader()
        # -------end of menu obj------#
        self.linkfunction()
        self.act.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()
        self.__debug = debug_en
        self.t_start = time.perf_counter()
        self.autoComPort_v2()  # 直接自動撈取COM Port，且撈取對應的儀器名稱
        self.reset_flag = 0  # 紀錄是否有reset 若有為1，若沒有為0
        self.DetectNum = 0  # 紀錄撈資料出現錯誤時，只能print一次
        self.recordPDTemp_min = 65
        self.first_draw = 0
        self.posture_thread = None
        self.postureData = {k: np.empty(0) for k in set(Posture_DATA_STRUCTURE)}
        # self.mapRead = pigImuMapReader()
        self.map_isopen = False

        # 20231229
        self.myImu = None
        self.VB_GPS = None
        self.VB_GLONASS = None
        self.VB_BeiDou = None
        self.VB_Time = None
        self.VB_Latitude = None
        self.VB_Longitude = None
        self.VB_Velocity = None
        self.VB_Heading = None
        self.VB_Altitude = None
        self.VB_Vertical_Vel = None
        self.VB_Pitch_KF = None
        self.VB_Roll_KF = None
        self.VB_Heading_KF = None
        self.VB_Pitch_rate = None
        self.VB_Roll_rate = None
        self.VB_Yaw_rate = None
        self.VB_Acc_X = None
        self.VB_Acc_Y = None
        self.VB_Acc_Z = None
        self.VB_Date = None
        self.VB_KF_Status = None
        self.VB_Pos_Quality = None
        self.VB_Vel_Quality = None
        self.VB_Heading2_KF = None
        self.KVHStruck = {k: np.empty(0) for k in set(KVH_DATA_STRUCTURE_MANI)}

        self.VBOXDraw = {k: np.empty(0) for k in set(VBOX_Time_DATA_STRUCTURE_MAIN)}
        self.KVHStruck_Time = {k: np.empty(0) for k in set(KVH_DATA_STRUCTURE_MANI)}

        self.savaDataNum = 0


    def closeEvent(self, *args, **kwargs):  # 當關閉視窗時，會被執行的函式
        if self.act.isRun == True and self.__connector.portDoNotConnectStatus == False:
            self.stop()
        if self.top.usb.bt_disconnect.isEnabled() == True:
            self.disconnect()

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
        # self.act.Portstatus_qt.connect(self.autoDetectComport)
        #self.imudata_file_auto.createFile_Error_qt.connect(self.cannot_create_file_stop)
        self.act.deviceReset_qt.connect(self.autoinstrumentReset)
        self.act.imuPosture_qt.connect(self.posturedata)
        # menu trigger connection
        self.pig_menu.action_trigger_connect([self.show_parameters,
                                              self.show_calibration_menu,
                                              self.show_plot_data_menu,
                                              self.show_cal_allan_menu,
                                              self.show_initial_setting_menu,
                                              self.show_map_ui_menu,
                                              self.show_W_A_cali_parameter_menu
                                              ])
        # file name le
        self.top.save_block.le_filename.editingFinished.connect(
            lambda: self.file_name_le_connect(self.top.save_block.le_filename))

        # 姿態展示使用的按鈕
        #self.top.tabwidget_show.reset_degree.clicked.connect(self.resetPosture)

        # 即時軌跡
        self.mapUI.iscloase_qt.connect(self.closeWinMapSet)
        self.mapRead.realTImePointqt_signal.connect(self.mapUI.RealDrawPath)
        self.mapUI.Slider.valueChanged.connect(self.sliderChangeVal)
        self.mapRead.timePointData_signal.connect(self.save_Data)


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

    def show_W_A_cali_parameter_menu(self):
        self.cali_parameter_menu.show()

    def show_map_ui_menu(self):
        #self.mapUI.initTargetMarkerMap()
        self.mapUI.Restartnewmarker()
        self.sliderChangeVal()
        self.mapUI.show()
        self.map_isopen = True

    def closeWinMapSet(self, result):
        self.map_isopen = False

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()

    def printBuffer(self, val):
        self.top.buffer_lb.lb.setText(str(val))

    def printGPS_Time(self, val):
        self.top.gpstime_lb.lb.setText(val)

    def printPdTemperature(self, val, X_val, Y_val):
        if (time.perf_counter() - self.t_start) > 0.5:
            self.top.pd_temp_lb.lb.setText(str(val))
            self.top.pdX_temp_lb.lb.setText(str(X_val))
            self.top.pdY_temp_lb.lb.setText(str(Y_val))
            self.t_start = time.perf_counter()

    def printUpdateRate(self, t_list):
        update_rate = round(((t_list[-1] - t_list[0]) / (len(t_list) - 1)) ** -1, 1)
        self.top.data_rate_lb.lb.setText(str(update_rate))

    def printVBOX(self):
        satellite_num = int(self.VB["GPS"][0]) + int(self.VB["GLONASS"][0]) + int(self.VB["BeiDou"][0])
        kfStatus = int(self.VB["KF_Status"][0])
        posQuality = int(self.VB["Pos_Quality"][0] * 100) / 100
        velQuality = int(self.VB["Vel_Quality"][0] * 100) / 100
        velocity = int(self.VB["Velocity"][0] * 100) / 100
        vertical_vel = int(self.VB["Vertical_Vel"][0] * 100) / 100
        heading_kf = int(self.VB["Heading_KF"][0] * 100) / 100

        self.top.satellite.lb.setText(str(satellite_num))
        self.top.vbox_kf_status.lb.setText(str(kfStatus))
        self.top.vbox_pos_quality.lb.setText(str(posQuality))
        self.top.vbox_vel_quality.lb.setText(str(velQuality))
        self.top.vbox_Velocity.lb.setText(str(velocity))
        self.top.vbox_Vertical_Vel.lb.setText(str(vertical_vel))
        self.top.vbox_Heading_KF.lb.setText(str(heading_kf))

    def updateComPort(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.addPortItems(portNum, portList)
        if portNum != 0:
            self.top.usb.bt_connect.setEnabled(True) # 判斷是否已連接儀器，並顯示連接btn
            if self.top.usb.bt_disconnect.isEnabled():
                self.disconnect()


    def selectComPort(self):
        self.__portName = self.top.usb.selectPort()

    def autoComPort_v2(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.autoComport_v2(portNum, portList)
        if portNum != 0:
            self.top.usb.bt_connect.setEnabled(True) # 判斷是否已連接儀器，並顯示連接btn

    # 判斷COM Port是否有鬆脫或是沒電的狀況，並執行此功能
    # def autoDetectComport(self, status):
    #     self.top.save_block.rb.setChecked(False)
    #     # self.imudata_file.close()
    #     if self.top.tabwidget_show.QTab.currentIndex() == 1 and self.top.tabwidget_show.threadStatus:
    #         # self.posture_thread.join()
    #         self.top.tabwidget_show.time_update.stop()
    #         self.top.tabwidget_show.threadStatus = False
    #     else:
    #         self.imudata_file_auto.close_hour_folder()
    #         self.imudata_file_auto.reset_hh_reg()
    #     if (self.first_run_flag == False):  # 無法connect做判斷用的
    #         self.act.quit()
    #         self.act.wait()
    #     # self.__connector.portDoNotConnectStatus = False
    #     self.press_stop = True
    #     self.first_run_flag = True
    #     self.act.start_read = 0
    #     self.reset_flag = 1
    #     self.DetectNum += 1
    #     self.disconnect()
    #     self.top.usb.showPortName_doesnot_connect()
    #     if self.DetectNum == 1:
    #         logger.error('The GUI is auto-disconnect now. (原因:斷電、USB鬆脫)')
    #         mestitle = "儀器斷線的錯誤"  # 儀器斷線的錯誤
    #         Mes = "1.請檢查儀器的電源是否保持開啟。\n 2.請檢查USB是否已被拔除了。\n 3.請確認選擇的COM Port(USB)名稱是否為本公司的儀器。"
    #         self.WidgetMes(mestitle, Mes)
    #         # self.mesWindow(mestitle, Mes)

    # def cannot_create_file_stop(self, status):  # 判斷資料夾無法建立時執行的部分
    #     self.act.isRun = False
    #     # self.__connector.portDoNotConnectStatus = True
    #     self.act.quit()
    #     self.act.wait()
    #     self.imudata_file_auto.reset_hh_reg()
    #     self.top.save_block.rb.setChecked(False)
    #     self.press_stop = True
    #     self.first_run_flag = True
    #     self.act.start_read = 0
    #     self.reset_flag = 1
    #     self.top.setBtnEnable(True)
    #     logger.error('Error occurred while creating the file.')
    #     mesTitle = "建立檔案的過程出現錯誤"
    #     self.WidgetMes(mesTitle, self.imudata_file_auto.errorMes)
    #     # self.mesWindow(mesTitle, self.imudata_file_auto.errorMes)  # 建檔的部分出現錯誤

    def WidgetMes(self, mestitle, errorMes):
        mesbox = QtWidgets.QMessageBox(self.top)
        mesbox.critical(self.top, mestitle, errorMes)

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connect(self):
        is_port_open = self.act.connect(self.__connector, self.__portName, 230400)
        if (is_port_open != False):
            self.is_port_open_qt.emit(is_port_open)
            self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
            self.cali_parameter_menu = pig_calibration_widget(self.act)
            self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
            self.act.isExtMode = self.pig_initial_setting_menu.btn_status
            self.act.stopIMU()
        # print(self.act.isExtMode)

    def disconnect(self):
        if self.act.isRun == True:
            self.stop()
            time.sleep(1)
        is_port_open = self.act.disconnect()
        self.is_port_open_qt.emit(is_port_open)
        self.top.autoDetect_setBtnEnable(False)

    def imuThreadStopDetect(self):
        self.VB = {k: np.empty(0) for k in set(VBOX_DATA_STRUCTURE_MAIN)}
        self.VBOXDraw = {k: np.empty(0) for k in set(VBOX_Time_DATA_STRUCTURE_MAIN)}
        self.KVHStruck_Time = {k: np.empty(0) for k in set(KVH_DATA_STRUCTURE_MANI)}
        self.imudata = self.resetDataContainer()
        #self.imudata_two = self.resetDataContainer()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(ChangeVersion_DATA_STRUCTURE)}

    def resetFPGATimer(self, ch):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1, ch)
        print('main: reset FPGA time')

    def autoinstrumentReset(self, t):
        logger.info("The device is reset. (設備重置)")
        date_now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        init_time = self.imudata_file.__openTime__
        timeoutAllTime = timedelta(hours=t[2], minutes=t[1], seconds=t[0])
        timeoutTime = init_time + timeoutAllTime
        strTimeoutTime = timeoutTime.strftime("%Y/%m/%d %H:%M:%S")
        self.imudata_file.write_line('#' + strTimeoutTime + '\n\n' +
                                     '#' + date_now)
        # self.imudata_file_auto.close_hour_folder()
        # self.imudata_file_auto.reset_hh_reg()
        # self.reset_flag = 1
        # logger.info("The device is reset. (儀器重置)")
        # self.imudata_file_auto.create_data_folder(True)
        # self.imudata_file_auto.auto_create_folder(True)

    def VBOX_Get_Data(self):
        received_data = []
        vbox = VBOXReader("COM14", baudRate=115200, debug_en=False)
        self.myImu = ReaderQthread(vbox, debug_en=False)
        self.myImu.data_qt.connect(self.VBOX_collect)
        # myImu.data_qt.connect(lambda mydata: received_data.append(mydata))

        self.myImu.connectSerial()
        self.myImu.isRun = True
        start_time = time.time()
        self.myImu.start()

    def VBOXStop(self):
        self.myImu.isRun = False
        self.myImu.disconnectSerial()
        self.myImu.wait()

    def KVH_Get_Data(self):
        received_data = []
        p1750 = KVHReader("COM16", baudRate=115200, debug_en=True)
        self.KVH_myImu = KVHReaderQthread(p1750, debug_en=True)
        self.KVH_myImu.KVHdata_qt.connect(self.KVHcollect)

        self.KVH_myImu.connectSerial()
        self.KVH_myImu.isRun = True
        start_time = time.time()
        self.KVH_myImu.start()

    def KVHStop(self):
        self.KVH_myImu.isRun = False
        self.KVH_myImu.disconnectSerial()
        self.KVH_myImu.wait()

    def start(self):
        #self.resetFPGATimer()
        # self.top.tabwidget_show.cancelLayout()
        if self.map_isopen:
            self.mapUI.stopTrackFuncVal = False  # 停止自動追蹤功能
            self.mapRead.cleanArray()
            self.mapRead.realTImePointqt_signal.connect(self.mapUI.RealDrawPath)
            self.initKM = Driving()
            #self.SetMapMarkerPosition() # 起始經緯度
            #self.SetTargetMarkerPosition()  # 目標經緯

        self.KVH_Get_Data()  # 20231229 新增
        self.VBOX_Get_Data()  # 20231228 新增
        self.act.readIMU()

        self.act.isRun = True
        self.press_stop = False
        self.planeList()
        self.__connector.cleanVal()
        self.act.TabNum = self.top.tabwidget_show.QTab.currentIndex()
        if self.top.tabwidget_show.QTab.currentIndex() == 1:
            self.top.tabwidget_show.initUI()
            self.resetPosture()  # 角度歸零
            # self.posture_thread = threading.Thread(target=self.act.postureStart)
            # self.posture_thread.start()
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
        # file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
        # if self.top.tabwidget_show.QTab.currentIndex() != 1:
        #     file_name = str(pathlib.Path().absolute())
        #     self.imudata_file_auto.dirCreateStatus = True
        #     self.imudata_file_auto.data_path = file_name
        #     self.imudata_file_auto.start = True
        #     self.imudata_file_auto.create_data_folder(True)
        #     self.imudata_file_auto.auto_create_folder(True)
        file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
        self.imudata_file.name = file_name
        self.imudata_file.open(self.top.save_block.rb.isChecked())
        self.imudata_file.write_line('AFI_TIME, AFI_WX, AFI_WY, AFI_WZ, AFI_AX, AFI_AY, AFI_AZ, AFI_PD_TEMP_X, AFI_PD_TEMP_Y, AFI_PD_TEMP_Z, GPS'
                                     ',GLONASS, BeiDou, VBOXTime, Latitude,  Longitude,  Velocity,  Heading,  Altitude,  Vertical_Vel,  Pitch_KF,  Roll_KF,  Heading_KF'
                                     ', Pitch_rate,  Roll_rate,  Yaw_rate,  Acc_X,  Acc_Y,  Acc_Z,  Date,  KF_Status,  Pos_Quality,  Vel_Quality,  Heading2_KF'
                                     ',kvh_wx, kvh_wy,  kvh_wz,  kvh_ax,  kvh_ay,  kvh_az,  kvh_status,  kvh_seq_num,  kvh_Temperature')
        # if OUTPUT_ONE_AXIS:
        #     self.imudata_file.write_line('time,wx,wy,fog,ax,ay,az,T')
        # else:
        #     self.imudata_file.write_line('time,fog,wx,wy,wz,ax,ay,az,T')

    def planeList(self):
        self.xMEMS_list = []
        self.yMEMS_list = []
        self.xFOG_list = []
        self.yFOG_list = []
        self.xTrue_list = []
        self.yTrue_list = []
        self.plane_calcu_MEMS = plane_nav()
        self.plane_calcu_FOG = plane_nav()
        self.plane_calcu_True = plane_nav()

    def stop(self):
        self.resetFPGATimer(3)
        self.KVHStop()  # 20231229
        self.VBOXStop() # 20231229
        self.act.isRun = False
        if self.top.tabwidget_show.QTab.currentIndex() == 1 and self.top.tabwidget_show.threadStatus:
            #self.posture_thread.join()
            self.top.tabwidget_show.time_update.stop()
            self.top.tabwidget_show.threadStatus = False
            self.resetPosture()
        # else:
        #     self.imudata_file_auto.close_hour_folder()
        #     self.imudata_file_auto.reset_hh_reg()
        self.top.save_block.rb.setChecked(False)
        self.imudata_file.close()
        self.top.setBtnEnable(True)
        self.press_stop = True
        self.first_run_flag = True
        self.act.start_read = 0
        #self.top.tabwidget_show.resetCircle()
        logger.info('The GUI is stopped to read the data.')
        print('press stop')

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

    def VBOX_collect(self, VB_date):
        self.VB_GPS = VB_date["GPS"]
        self.VB_GLONASS = VB_date["GLONASS"]
        self.VB_BeiDou = VB_date["BeiDou"]
        self.VB_Time = VB_date["VBOXTime"]
        self.VB_Latitude = VB_date["Latitude"]
        self.VB_Longitude = VB_date["Longitude"]
        self.VB_Velocity = VB_date["Velocity"]
        self.VB_Heading = VB_date["Heading"]
        self.VB_Altitude = VB_date["Altitude"]
        self.VB_Vertical_Vel = VB_date["Vertical_Vel"]
        self.VB_Pitch_KF = VB_date["Pitch_KF"]
        self.VB_Roll_KF = VB_date["Roll_KF"]
        self.VB_Heading_KF = VB_date["Heading_KF"]
        self.VB_Pitch_rate = VB_date["Pitch_rate"]
        self.VB_Roll_rate = VB_date["Roll_rate"]
        self.VB_Yaw_rate = VB_date["Yaw_rate"]
        self.VB_Acc_X = VB_date["Acc_X"]
        self.VB_Acc_Y = VB_date["Acc_Y"]
        self.VB_Acc_Z = VB_date["Acc_Z"]
        self.VB_Date = VB_date["Date"]
        self.VB_KF_Status = VB_date["KF_Status"]
        self.VB_Pos_Quality = VB_date["Pos_Quality"]
        self.VB_Vel_Quality = VB_date["Vel_Quality"]
        self.VB_Heading2_KF = VB_date["Heading2_KF"]

    def KVHcollect(self, KVH_data):
        kvh_list = ['kvh_wx', 'kvh_wy', 'kvh_wz', 'kvh_ax', 'kvh_ay', 'kvh_az', 'kvh_status',
                    'kvh_seq_num', 'kvh_Temperature']
        self.KVHStruck = {k: np.empty(0) for k in set(KVH_DATA_STRUCTURE_MANI)}
        self.KVHStruck[kvh_list[0]] = np.append(self.KVHStruck[kvh_list[0]], KVH_data[kvh_list[0]])
        self.KVHStruck[kvh_list[1]] = np.append(self.KVHStruck[kvh_list[1]], KVH_data[kvh_list[1]])
        self.KVHStruck[kvh_list[2]] = np.append(self.KVHStruck[kvh_list[2]], KVH_data[kvh_list[2]])
        self.KVHStruck[kvh_list[3]] = np.append(self.KVHStruck[kvh_list[3]], KVH_data[kvh_list[3]])
        self.KVHStruck[kvh_list[4]] = np.append(self.KVHStruck[kvh_list[4]], KVH_data[kvh_list[4]])
        self.KVHStruck[kvh_list[5]] = np.append(self.KVHStruck[kvh_list[5]], KVH_data[kvh_list[5]])
        self.KVHStruck[kvh_list[6]] = np.append(self.KVHStruck[kvh_list[6]], KVH_data[kvh_list[6]])
        self.KVHStruck[kvh_list[7]] = np.append(self.KVHStruck[kvh_list[7]], KVH_data[kvh_list[7]])
        self.KVHStruck[kvh_list[8]] = np.append(self.KVHStruck[kvh_list[8]], KVH_data[kvh_list[8]])

    def collectData(self, imudata):
        kvh_list = ['kvh_wx', 'kvh_wy', 'kvh_wz', 'kvh_ax', 'kvh_ay', 'kvh_az', 'kvh_status',
                    'kvh_seq_num', 'kvh_Temperature']
        if not self.press_stop:
            try:
                time_val = np.array([])
                self.savaDataNum += 1
                # print('collectData pre: ', len(imudata['TIME']), end=', ')
                # print(imudata['TIME'])
                #
                # print('collectData after: ', len(imudata['TIME']), end=', ')
                # print(imudata['TIME'])
                # self.first_run_flag = False
                #self.act.get_Port_connect_status()  # 判斷COM Port是否有被拔除
                # input_buf = self.act.readInputBuffer()
                t0 = time.perf_counter()
                # imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
                self.printPdTemperature(imudata["PD_TEMP_Z"][0], imudata["PD_TEMP_X"][0],imudata["PD_TEMP_Y"][0])
                t1 = time.perf_counter()
                # self.imudata = cmn.dictOperation(self.imudata, imudata, "APPEND", IMU_DATA_STRUCTURE)

                self.VB = {k: np.empty(0) for k in set(VBOX_DATA_STRUCTURE_MAIN)}
                for i in range(10):
                    self.VB["GPS"] = np.append(self.VB["GPS"], self.VB_GPS)
                    self.VB["GLONASS"] = np.append(self.VB["GLONASS"], self.VB_GLONASS)
                    self.VB["BeiDou"] = np.append(self.VB["BeiDou"], self.VB_BeiDou)
                    self.VB["VBOXTime"] = np.append(self.VB["VBOXTime"], self.VB_Time)
                    self.VB["Latitude"] = np.append(self.VB["Latitude"], self.VB_Latitude)
                    self.VB["Longitude"] = np.append(self.VB["Longitude"], self.VB_Longitude)
                    self.VB["Velocity"] = np.append(self.VB["Velocity"], self.VB_Velocity)
                    self.VB["Heading"] = np.append(self.VB["Heading"], self.VB_Heading)
                    self.VB["Altitude"] = np.append(self.VB["Altitude"], self.VB_Altitude)
                    self.VB["Vertical_Vel"] = np.append(self.VB["Vertical_Vel"], self.VB_Vertical_Vel)
                    self.VB["Pitch_KF"] = np.append(self.VB["Pitch_KF"], self.VB_Pitch_KF)
                    self.VB["Roll_KF"] = np.append(self.VB["Roll_KF"], self.VB_Roll_KF)
                    self.VB["Heading_KF"] = np.append(self.VB["Heading_KF"], self.VB_Heading_KF)
                    self.VB["Pitch_rate"] = np.append(self.VB["Pitch_rate"], self.VB_Pitch_rate)
                    self.VB["Roll_rate"] = np.append(self.VB["Roll_rate"], self.VB_Roll_rate)
                    self.VB["Yaw_rate"] = np.append(self.VB["Yaw_rate"], self.VB_Yaw_rate)
                    self.VB["Acc_X"] = np.append(self.VB["Acc_X"], self.VB_Acc_X)
                    self.VB["Acc_Y"] = np.append(self.VB["Acc_Y"], self.VB_Acc_Y)
                    self.VB["Acc_Z"] = np.append(self.VB["Acc_Z"], self.VB_Acc_Z)
                    self.VB["Date"] = np.append(self.VB["Date"], self.VB_Date)
                    self.VB["KF_Status"] = np.append(self.VB["KF_Status"], self.VB_KF_Status)
                    self.VB["Pos_Quality"] = np.append(self.VB["Pos_Quality"], self.VB_Pos_Quality)
                    self.VB["Vel_Quality"] = np.append(self.VB["Vel_Quality"], self.VB_Vel_Quality)
                    self.VB["Heading2_KF"] = np.append(self.VB["Heading2_KF"], self.VB_Heading2_KF)

                self.printVBOX()

                if self.savaDataNum == 10:
                    self.imudata["TIME"] = np.append(self.imudata["TIME"], imudata["TIME"][-1])
                    self.imudata["WX"] = np.append(self.imudata["WX"], imudata["WX"][-1])
                    self.imudata["WY"] = np.append(self.imudata["WY"], imudata["WY"][-1])
                    self.imudata["WZ"] = np.append(self.imudata["WZ"], imudata["WZ"][-1])
                    self.imudata["AX"] = np.append(self.imudata["AX"], imudata["AX"][-1])
                    self.imudata["AY"] = np.append(self.imudata["AY"], imudata["AY"][-1])
                    self.imudata["AZ"] = np.append(self.imudata["AZ"], imudata["AZ"][-1])
                    self.imudata["PD_TEMP_X"] = np.append(self.imudata["PD_TEMP_X"], imudata["PD_TEMP_X"][-1])
                    self.imudata["PD_TEMP_Y"] = np.append(self.imudata["PD_TEMP_Y"], imudata["PD_TEMP_Y"][-1])
                    self.imudata["PD_TEMP_Z"] = np.append(self.imudata["PD_TEMP_Z"], imudata["PD_TEMP_Z"][-1])

                    self.KVHStruck_Time[kvh_list[0]] = np.append(self.KVHStruck_Time[kvh_list[0]], self.KVHStruck[kvh_list[0]][-1])
                    self.KVHStruck_Time[kvh_list[1]] = np.append(self.KVHStruck_Time[kvh_list[1]], self.KVHStruck[kvh_list[1]][-1])
                    self.KVHStruck_Time[kvh_list[2]] = np.append(self.KVHStruck_Time[kvh_list[2]], self.KVHStruck[kvh_list[2]][-1])
                    self.KVHStruck_Time[kvh_list[3]] = np.append(self.KVHStruck_Time[kvh_list[3]], self.KVHStruck[kvh_list[3]][-1])
                    self.KVHStruck_Time[kvh_list[4]] = np.append(self.KVHStruck_Time[kvh_list[4]], self.KVHStruck[kvh_list[4]][-1])
                    self.KVHStruck_Time[kvh_list[5]] = np.append(self.KVHStruck_Time[kvh_list[5]], self.KVHStruck[kvh_list[5]][-1])
                    self.savaDataNum = 0
                    #
                    # self.VBOXDraw["Velocity"] = np.append(self.VBOXDraw["Velocity"], self.VB["Velocity"])
                    # self.VBOXDraw["Vertical_Vel"] = np.append(self.VBOXDraw["Vertical_Vel"], self.VB["Vertical_Vel"])
                    #
                    self.VBOXDraw["Latitude"] = np.append(self.VBOXDraw["Latitude"], self.VB["Latitude"][-1])
                    self.VBOXDraw["Longitude"] = np.append(self.VBOXDraw["Longitude"], self.VB["Longitude"][-1])
                    # print(self.VBOXDraw)
                    # print(self.KVHStruck_Time)


                # print(len(self.imudata["TIME"]), end=", ")
                datanum = 100
                if len(self.imudata["TIME"]) > datanum:  # 20230626
                    self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["WX"] = self.imudata["WX"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["WY"] = self.imudata["WY"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["WZ"] = self.imudata["WZ"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["AX"] = self.imudata["AX"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["AY"] = self.imudata["AY"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["AZ"] = self.imudata["AZ"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["PD_TEMP_X"] = self.imudata["PD_TEMP_X"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["PD_TEMP_Y"] = self.imudata["PD_TEMP_Y"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.imudata["PD_TEMP_Z"] = self.imudata["PD_TEMP_Z"][self.act.arrayNum:self.act.arrayNum + datanum]

                    # self.VBOXDraw["Velocity"] = self.VBOXDraw["Velocity"][self.act.arrayNum:self.act.arrayNum + datanum]
                    # self.VBOXDraw["Vertical_Vel"] = self.VBOXDraw["Vertical_Vel"][self.act.arrayNum:self.act.arrayNum + datanum]
                    #
                    self.VBOXDraw["Latitude"] = self.VBOXDraw["Latitude"][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.VBOXDraw["Longitude"] = self.VBOXDraw["Longitude"][self.act.arrayNum:self.act.arrayNum + datanum]
                    #
                    self.KVHStruck_Time[kvh_list[0]] = self.KVHStruck_Time[kvh_list[0]][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.KVHStruck_Time[kvh_list[1]] = self.KVHStruck_Time[kvh_list[1]][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.KVHStruck_Time[kvh_list[2]] = self.KVHStruck_Time[kvh_list[2]][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.KVHStruck_Time[kvh_list[3]] = self.KVHStruck_Time[kvh_list[3]][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.KVHStruck_Time[kvh_list[4]] = self.KVHStruck_Time[kvh_list[4]][self.act.arrayNum:self.act.arrayNum + datanum]
                    self.KVHStruck_Time[kvh_list[5]] = self.KVHStruck_Time[kvh_list[5]][self.act.arrayNum:self.act.arrayNum + datanum]

                    # ["DataTime"] = self.data_time["DataTime"][self.act.arrayNum: self.act.arrayNum + 1000]

                # if (self.recordPDTemp_min != imudata["MIN"][-1]) == True:  # 20230627 每一分鐘記錄一次三軸的溫度
                #     PD_Time = '%d/%d/%d %d:%d:%d' % (
                #     imudata["YEAR"][-1], imudata["MON"][-1], imudata["DAY"][-1], imudata["HOUR"][-1]
                #     , imudata["MIN"][-1], imudata["SEC"][-1])
                #     # print(imudata["PD_TEMPERATURE_SP9"])
                #     Temp_mems = imudata["PD_TEMP"][-1]
                #     tempdata = PD_Time + ", " + str(Temp_mems)
                #     self.imudata_file_auto.saveData(1, tempdata, "")
                #     self.recordPDTemp_min = imudata["MIN"][-1]

                t2 = time.perf_counter()
                # debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                #              + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
                debug_info = "MAIN: ," + str(round((t2 - t0) * datanum, 5)) + ", " \
                             + str(round((t1 - t0) * datanum, 5)) + ", " + str(round((t2 - t1) * datanum, 5))
                cmn.print_debug(debug_info, self.__debug)
                # print(imudata["PIG_WZ"])

                # 將毫秒顯示兩位數
                # ms_format_to_2 = (imudata['mSEC'][0] // 10) % 100
                # ms_format_str = ''
                # if ms_format_to_2 < 10:
                #     mes_str = str(ms_format_to_2)
                #     ms_format_str = '0%s' % mes_str[:-2]
                # else:
                #     ms_format_str = str(ms_format_to_2)[:-2]
                # # 撈取PC的時間
                # gps_time = '%d/%d/%d %d:%d:%d.%s' % (imudata['YEAR'][0], imudata['MON'][0], imudata['DAY'][0],
                #                                      imudata['HOUR'][0], imudata['MIN'][0], imudata['SEC'][0],
                #                                      ms_format_str)
                # self.judgment_Reset()  # 判斷是否有reset
                ##########
                # print(imudata)
                # print(imudata["TIME"].tolist())
                # ImuData ={
                #     "TIME" : imudata["TIME"].tolist(),
                #     "WX" : imudata["WX"].tolist(),
                #     "WY" : imudata["WY"].tolist(),
                #     "WZ" : imudata["WZ"].tolist(),
                #     "AX" : imudata["AX"].tolist(),
                #     "AY" : imudata["AY"].tolist(),
                #     "AZ" : imudata["AZ"].tolist()
                # }
                # json_str = json.dumps(ImuData)
                # print(json_str)
                # self.imuJason_file.writeJson(json_str)
                ##############
                # if self.map_isopen:
                #     self.mapRead.RealTimeTrackStart(imudata, self.VB, self.KVHStruck)
                # else:
                self.mapRead.Integration_Data(imudata, self.VB, self.KVHStruck)
                self.plotdata(self.imudata, self.KVHStruck_Time, self.VBOXDraw)
                self.printUpdateRate(self.imudata["TIME"])
                # print(len(self.imudata["TIME"]))
            except Exception as e:
                print(e)


    def save_Data(self, imudata):
        # print(imudata)
        DataNameList = ["One_TIME", "One_WX", "One_WY", "One_WZ", "One_AX", "One_AY", "One_AZ", "One_PD_TEMP_X", "One_PD_TEMP_Y", "One_PD_TEMP_Z",
                        "One_latitude(deg)", "One_longitude(deg)","GPS",
                        "GLONASS", "BeiDou", "VBOXTime", "Latitude", "Longitude", "Velocity", 'Heading', 'Altitude',
                        'Vertical_Vel', "Pitch_KF", "Roll_KF", "Heading_KF",
                        "Pitch_rate", "Roll_rate", "Yaw_rate", "Acc_X", "Acc_Y", "Acc_Z", "Date", "KF_Status",
                        "Pos_Quality", 'Vel_Quality', "Heading2_KF",
                        "kvh_wx", "kvh_wy", "kvh_wz", "kvh_ax", "kvh_ay", "kvh_az", "kvh_status", 'kvh_seq_num',
                        'kvh_Temperature']
        datalist = [imudata[DataNameList[0]], imudata[DataNameList[1]], imudata[DataNameList[2]], imudata[DataNameList[3]],
                    imudata[DataNameList[4]], imudata[DataNameList[5]], imudata[DataNameList[6]], imudata[DataNameList[7]], imudata[DataNameList[8]], imudata[DataNameList[9]],
                    imudata[DataNameList[12]], imudata[DataNameList[13]], imudata[DataNameList[14]], imudata[DataNameList[15]], imudata[DataNameList[16]],
                    imudata[DataNameList[17]], imudata[DataNameList[18]], imudata[DataNameList[19]], imudata[DataNameList[20]], imudata[DataNameList[21]], imudata[DataNameList[22]], imudata[DataNameList[23]],
                    imudata[DataNameList[24]], imudata[DataNameList[25]], imudata[DataNameList[26]], imudata[DataNameList[27]], imudata[DataNameList[28]], imudata[DataNameList[29]], imudata[DataNameList[30]], imudata[DataNameList[31]],
                    imudata[DataNameList[32]], imudata[DataNameList[33]], imudata[DataNameList[34]], imudata[DataNameList[35]], imudata[DataNameList[36]], imudata[DataNameList[37]], imudata[DataNameList[38]], imudata[DataNameList[38]],
                    imudata[DataNameList[40]], imudata[DataNameList[41]], imudata[DataNameList[42]], imudata[DataNameList[43]], imudata[DataNameList[44]]]
        data_fmt = "%.3f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f,%.1f,%.1f, %d,%d,%d,%.6f,%.7f,%.7f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f" \
                   ",%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f"

        try:
            self.imudata_file.saveData(datalist, data_fmt)
        except Exception as e:
            print(Exception)
            pass

    def posturedata(self, imudata):
        if not self.press_stop:
            x_Axis = imudata["WX"][0]
            z_Axis = imudata["WZ"][0]
            y_Axis = imudata["WY"][0]
            x_acc = imudata["AX"][0] * 9.8
            y_acc = imudata["AY"][0] * 9.8
            z_acc = imudata["AZ"][0] * 9.8

            self.top.tabwidget_show.widget_win.x_Axis = x_Axis
            self.top.tabwidget_show.widget_win.y_Axis = y_Axis
            self.top.tabwidget_show.widget_win.z_Axis = z_Axis
            # 加速度
            self.top.tabwidget_show.widget_win.x_acc = x_acc
            self.top.tabwidget_show.widget_win.y_acc = y_acc
            self.top.tabwidget_show.widget_win.z_acc = z_acc

            mems_Z = imudata["WZ"][0] #* 100
            FOG_Z = imudata["WZ"][0] #* 100
            self.top.tabwidget_show.widget_circle.input(imudata["TIME"][0], mems_Z, FOG_Z)

            xMEMS, yMEMS = self.plane_calcu_MEMS.update(imudata["TIME"][0], mems_Z)
            xFOG, yFOG = self.plane_calcu_FOG.update(imudata["TIME"][0], FOG_Z)
            xTrue, yTrue = self.plane_calcu_True.update(imudata["TIME"][0], 0)


            self.postureData["xMEMS"] = np.append(self.postureData["xMEMS"], xMEMS)
            self.postureData["yMEMS"] = np.append(self.postureData["yMEMS"], yMEMS)
            self.postureData["xFOG"] = np.append(self.postureData["xFOG"], xFOG)
            self.postureData["yFOG"] = np.append(self.postureData["yFOG"], yFOG)
            self.postureData["xTrue"] = np.append(self.postureData["xTrue"], xTrue)
            self.postureData["yTrue"] = np.append(self.postureData["yTrue"], yTrue)

            if len(self.postureData["xMEMS"]) == 10:
                # 畫圈
                self.xMEMS_list.append(self.postureData["xMEMS"][-1])
                self.yMEMS_list.append(self.postureData["yMEMS"][-1])
                self.xFOG_list.append(self.postureData["xFOG"][-1])
                self.yFOG_list.append(self.postureData["yFOG"][-1])
                self.xTrue_list.append(self.postureData["xTrue"][-1])
                self.yTrue_list.append(self.postureData["yTrue"][-1])
                self.postureData = {k: np.empty(0) for k in set(Posture_DATA_STRUCTURE)}

            if len(self.xMEMS_list) > 600:
                self.plane_calcu_MEMS.reset()
                self.plane_calcu_FOG.reset()
                self.plane_calcu_True.reset()
                self.planeList()

            self.top.tabwidget_show.plot_cir.ax1.setData(
                np.array(self.xMEMS_list) - self.xTrue_list, np.array(self.yMEMS_list) - self.yTrue_list)
            self.top.tabwidget_show.plot_cir.ax2.setData(
                np.array(self.xFOG_list) - self.xTrue_list, np.array(self.yFOG_list) - self.yTrue_list)


            self.top.tabwidget_show.widget_win.time = imudata["TIME"][0]

            __three_Asix = np.rad2deg(self.top.tabwidget_show.widget_win.AR.me.qut.ori)
            # self.top.tabwidget_show.set_x_degree.setText("{:.2f}".format(__three_Asix[0]))
            # self.top.tabwidget_show.set_y_degree.setText("{:.2f}".format(__three_Asix[1]))
            # self.top.tabwidget_show.set_z_degree.setText("{:.2f}".format(__three_Asix[2]))
            # self.top.tabwidget_show.set_z_mems_rotationalSpeed.setText(str(mems_Z))
            self.top.tabwidget_show.set_z_mems_integralAngle.setText(str(self.top.tabwidget_show.widget_circle.ang_MEMS))
            self.top.tabwidget_show.set_z_FOG_rotationalSpeed.setText(str(FOG_Z))
            self.top.tabwidget_show.set_z_FOG_integralAngle.setText(str(self.top.tabwidget_show.widget_circle.ang_FOG))


    def resetPosture(self):
        self.top.tabwidget_show.widget_win.resetDraw()
        self.top.tabwidget_show.resetCircle()
        self.plane_calcu_MEMS.reset()
        self.plane_calcu_FOG.reset()
        self.plane_calcu_True.reset()
        self.planeList()
        self.top.tabwidget_show.set_z_mems_rotationalSpeed.setText("0.0")
        self.top.tabwidget_show.set_z_mems_integralAngle.setText("0.0")
        self.top.tabwidget_show.set_z_FOG_rotationalSpeed.setText("0.0")
        self.top.tabwidget_show.set_z_FOG_integralAngle.setText("0.0")
        # time.sleep(2)
        #print('歸零')

    def plotdata(self, imudata, kvhData, vboxData):
        # print('plotdata: ', imudata['TIME'])
        QApplication.processEvents()
        if self.top.plot1_unit_rb.btn_status == 'dph':
            factor = 3600
        else:
            factor = 1

        # self.top.plot7.ax.setData(imudata["TIME"], imudata["WZ"])
        # if self.top.plot1_showWz_cb.cb_1.isChecked():
        #     self.top.plot1.ax1.setData(imudata["TIME"], imudata["WZ"] * factor)
        #     # self.top.plot1.ax1.setData(imudata["TIME"], imudata["PIG_ERR"])
        # else:
        #     self.top.plot1.ax1.clear()
        # if self.top.plot1_showWz_cb.cb_2.isChecked():
        #     self.top.plot1.ax2.setData(imudata["TIME"], imudata["NANO33_WZ"] * factor)
        # else:
        #     self.top.plot1.ax2.clear()

        # self.top.plot2.ax.setData(imudata["TIME"], imudata["AX"])
        # self.top.plot3.ax.setData(imudata["TIME"], imudata["AY"])
        # self.top.plot4.ax.setData(imudata["TIME"], imudata["AZ"])
        # self.top.plot5.ax.setData(imudata["TIME"], imudata["WX"])
        # self.top.plot6.ax.setData(imudata["TIME"], imudata["WY"])

        self.top.plot_AFI_W.ax1.setData(imudata["TIME"], imudata["WX"])
        self.top.plot_AFI_W.ax2.setData(imudata["TIME"], imudata["WY"])
        self.top.plot_AFI_W.ax3.setData(imudata["TIME"], imudata["WZ"])
        self.top.plot_AFI_A.ax1.setData(imudata["TIME"], imudata["AX"])
        self.top.plot_AFI_A.ax2.setData(imudata["TIME"], imudata["AY"])
        self.top.plot_AFI_A.ax3.setData(imudata["TIME"], imudata["AZ"])

        self.top.plot_KVH_W.ax1.setData(imudata["TIME"], kvhData["kvh_wx"])
        self.top.plot_KVH_W.ax2.setData(imudata["TIME"], kvhData["kvh_wy"])
        self.top.plot_KVH_W.ax3.setData(imudata["TIME"], kvhData["kvh_wz"])
        self.top.plot_KVH_A.ax1.setData(imudata["TIME"], kvhData["kvh_ax"] * 9.8)
        self.top.plot_KVH_A.ax2.setData(imudata["TIME"], kvhData["kvh_ay"] * 9.8)
        self.top.plot_KVH_A.ax3.setData(imudata["TIME"], kvhData["kvh_az"] * 9.8)
        #
        # self.top.plot_vbox_vel.ax.setData(imudata["TIME"], vboxData["Velocity"])
        # self.top.plot_vbox_ver.ax.setData(imudata["TIME"], vboxData["Vertical_Vel"])
        #
        self.top.plot_vbox_latLong.ax.setData(vboxData["Longitude"], vboxData["Latitude"])
        # print(imudata)
        # print(kvhData)
        #print(vboxData["Vertical_Vel"])
        QApplication.processEvents()

    # 調整速度
    def sliderChangeVal(self):
        val = self.mapUI.Slider.value()
        lb = "軌跡點的速度調整至： " + str(val) + " km/hr"
        self.mapUI.SliderLabel.setText(lb)
        self.mapRead.initKM.setVelocity(val)

    # 修改起始經緯度
    # def SetMapMarkerPosition(self):
        # if self.mapUI.SetLatEdit.text() != "" and self.mapUI.SetLonEdit.text() != "":
        #     latVal = float(self.mapUI.SetLatEdit.text())
        #     lonVal = float(self.mapUI.SetLonEdit.text())
        #self.mapRead.initKM.SetPosLatLong(latVal, lonVal)

    # def SetTargetMarkerPosition(self):
    #     if self.mapUI.SetTargetLatEdit.text() != "" and self.mapUI.SetTargetLonEdit.text() != "":
    #         targetLatVal = float(self.mapUI.SetTargetLatEdit.text())
    #         targetLonVal = float(self.mapUI.SetTargetLonEdit.text())
    #         self.mapUI.SetTargetMarkerMap(targetLatVal, targetLonVal)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
