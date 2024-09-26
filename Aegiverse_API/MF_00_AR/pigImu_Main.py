""" ####### log stuff creation, always on the top ########  """
import os
import builtins
from datetime import datetime, timedelta

import serial
import yaml
import logging.config

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

# current_directory = os.path.dirname(os.path.abspath(__file__))
# print(current_directory)
# myLib_path = os.path.join(current_directory, "myLib")
# sys.path.append(myLib_path)

# sys.path.append("../")
from myLib import common as cmn
from myLib.myGui.mygui_serial import *
import time
from myLib.mySerial.Connector import Connector
from myLib.myGui.pig_parameters_widget import pig_parameters_widget
from myLib.myGui.pig_parameters_widget import CMD_FOG_TIMER_RST
from myLib.myGui.pig_menu_manager import pig_menu_manager
from myLib.myGui import analysis_Allan, analysis_TimingPlot
from myLib.myGui import analysis_Allan, analysis_TimingPlot, myRadioButton

from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets

from pigImu_Widget import pigImuWidget as TOP
from pigImuReader import pigImuReader as ACTION
from pigImuReader import IMU_DATA_STRUCTURE
import numpy as np
from myLib.myGui.pig_W_A_calibration_parameter_widget import pig_calibration_widget


PRINT_DEBUG = 0


# for GP-1Z IMU
class mainWindow(QMainWindow):
    is_port_open_qt = pyqtSignal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()
        self.__first_run_flag = True
        self.press_stop = False
        self.resize(1450, 800)
        self.pig_parameter_widget = None
        self.cali_parameter_menu = None
        self.__portName = None
        self.setWindowTitle("Aegiverse FOG GUI")
        self.__connector = Connector()
        self.__isFileOpen = False
        self.top = TOP()
        self.act = ACTION()
        self.imudata_file = cmn.data_manager(fnum=0)
        self.imudata_file_Para = cmn.data_manager(fnum=1)
        self.pig_cali_menu = calibrationBlock()
        self.pig_initial_setting_menu = myRadioButton.radioButtonBlock_2('SYNC MODE', 'OFF', 'ON', False)  # True
        self.act.isCali = True
        self.menu = self.menuBar()
        self.pig_menu = pig_menu_manager(self.menu, self)
        self.analysis_allan = analysis_Allan.analysis_allan_widget(['fog'])
        self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
            ['fog', 'T'])
        self.linkfunction()
        self.act.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()

        self.__debug = debug_en
        self.t_start = time.perf_counter()
        # self.act.isKal = True
        # self.act.kal_R = 50
        # self.act.kal_Q = 1
        self.updateComPort()
        self.reset_flag = 0 # 若沒有被切斷，就不會等於1
        self.haveClickBtn = False  # 判斷已經按按鈕了
        # save dump 變數
        self.paraCh1 = None
        self.paraCh2 = None
        self.paraCh3 = None
        self.dumpMess = None  # 用於save時下dump使用的訊息視窗
        self.recordSelAxis = None
        self.hasConnect = None


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
        self.top.kal_filter_rb.clicked.connect(lambda: self.update_kalFilter_en(self.top.kal_filter_rb))
        # pyqtSignal connection
        self.act.imudata_qt.connect(self.collectData)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)
        self.act.buffer_qt.connect(self.printBuffer)
        self.is_port_open_qt.connect(self.is_port_open_status_manager)
        # menu trigger connection
        self.pig_menu.action_trigger_connect([self.show_parameters,
                                              self.show_calibration_menu,
                                              self.show_plot_data_menu,
                                              self.show_cal_allan_menu,
                                              self.show_initial_setting_menu,
                                              self.show_W_A_cali_parameter_menu
                                              ])
        # file name le
        self.top.save_block.le_filename.editingFinished.connect(
            lambda: self.file_name_le_connect(self.top.save_block.le_filename))

        # 設置當切換角速度的單位會執行觸發
        self.top.plot1_unit_rb.rb1.clicked.connect(self.plottitlechanged)
        self.top.plot1_unit_rb.rb2.clicked.connect(self.plottitlechanged)
        self.act.occur_err_qt.connect(self.occurError)
        # 點選checkBox可以顯示plot line chart，但取消勾選就會隱藏line chart
        self.top.plot1_lineName.cb1.clicked.connect(self.top.plot1LineNameOneVisible)
        self.top.plot1_lineName.cb2.clicked.connect(self.top.plot1LineNameTwoVisible)
        self.top.plot1_lineName.cb3.clicked.connect(self.top.plot1LineNameThreeVisible)
        self.top.plot7_lineName.cb1.clicked.connect(self.top.plot7LineNameOneVisible)
        self.top.plot7_lineName.cb2.clicked.connect(self.top.plot7LineNameTwoVisible)
        self.top.plot7_lineName.cb3.clicked.connect(self.top.plot7LineNameThreeVisible)
        # 當自動重連的狀態下，會執行的功能
        self.act.deviceReset_qt.connect(self.autoinstrumentReset)
        # 當勾選save的checkbox，會先執行dump取得參數
        self.top.save_block.rb.clicked.connect(self.saveTXTDump)
        # self.top.saveDumpCb.DumpCb_Z.stateChanged.connect(self.saveDumpCheckBoxChange)
        # self.top.saveDumpCb.DumpCb_X.stateChanged.connect(self.saveDumpCheckBoxChange)
        # self.top.saveDumpCb.DumpCb_Y.stateChanged.connect(self.saveDumpCheckBoxChange)
        self.act.stopRemind_qt.connect(self.closeStopMes)


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

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()

    def printBuffer(self, val):
        self.top.buffer_lb.lb.setText(str(val))

    # Z軸的溫度
    def printPdTemperature(self, val, X_val, Y_val):
        try:
            if (time.perf_counter() - self.t_start) > 0.5:
                self.top.pd_temp_lb.lb.setText(str(val))
                self.top.pdX_temp_lb.lb.setText(str(X_val))
                self.top.pdY_temp_lb.lb.setText(str(Y_val))
                self.t_start = time.perf_counter()
        except IndexError:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'IndexError — The index position has exceeded the range of the list.(An error occurred while the temperature is displayed, line {__lineNum}.)')
        except ValueError as ValError:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'ValueError — {ValError}.(An error occurred while the temperature is displayed, line {__lineNum}.)')
        finally:
            pass


    def printAtt(self, pitch, row, yaw):
        # self.top.pitch_lb.lb.setText(str(pitch))
        # self.top.row_lb.lb.setText(str(row))
        # self.top.yaw_lb.lb.setText(str(yaw))
        self.top.pitch_lb.lb.setText(f"{pitch:.5f}")
        self.top.row_lb.lb.setText(f"{row:.5f}")
        self.top.yaw_lb.lb.setText(f"{yaw:.5f}")


    def printUpdateRate(self, t_list):
        try:
            update_rate = round(((t_list[-1] - t_list[0]) / (len(t_list) - 1)) ** -1, 1)
            self.top.data_rate_lb.lb.setText(str(update_rate))
        except IndexError:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'IndexError — The index position has exceeded the range of the list.(An error occurred while the transmission rate is displayed, line {__lineNum}.)')
        except ValueError as ValError:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'ValueError — {ValError}.(An error occurred while the transmission rate is displayed, line {__lineNum}.)')
        finally:
            pass

    def updateComPort(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.addPortItems(portNum, portList)

    def selectComPort(self):
        self.__portName = self.top.usb.selectPort()

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connect(self):
        is_port_open = self.act.connect(self.__connector, self.__portName, 230400)
        if (is_port_open != False):
            self.is_port_open_qt.emit(is_port_open)

            # This line instantiate a parameter widget, load the parameter.json from LE block and send to FPGA
            self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
            self.cali_parameter_menu = pig_calibration_widget(self.act)
            self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
            #self.recordSelAxis = self.top.saveDumpCb.DumpCb.currentIndex()
            self.act.stopIMU()
        else:
            # 20231128
            self.act.stopIMU()
            __title = "Connect Error"
            __errStr = "An error occurred in the connect.\nPlease check the issue where the error occurred, thank you.\n" \
                        "1.Please confirm if the USB COM Port is correctly connected to the PC.\n" \
                        "2.Please ensure that the USB COM Port you want to connect is not being used by another application.\n" \
                        "And please take a screenshot of the error message for further troubleshooting by the responsible party.\nThank you for your cooperation."
            self.WidgetMes(__title, __errStr)
        self.hasConnect = True


    def disconnect(self):
        is_port_open = self.act.disconnect()
        self.is_port_open_qt.emit(is_port_open)
        self.hasConnect = False
        self.top.saveDumpCb.DumpCb_Z.setChecked(False)
        self.top.saveDumpCb.DumpCb_X.setChecked(False)
        self.top.saveDumpCb.DumpCb_Y.setChecked(False)


    def saveDumpCheckBoxChange(self):
        self.recordSelAxis = self.top.saveDumpCb.DumpCb.currentIndex()

    # save下dump需要處理的過程
    def saveTXTDump(self):
        if self.top.save_block.rb.isChecked() == True:
            self.widMesdump()
            # if self.recordSelAxis == 0:
            #     self.getAllDumpVal()
            if self.top.saveDumpCb.DumpCb_Z.isChecked() == True:
                self.getChannelOneVal()
            if self.top.saveDumpCb.DumpCb_X.isChecked() == True:
                self.getChannelTwoVal()
            if self.top.saveDumpCb.DumpCb_Y.isChecked() == True:
                self.getChannelThreeVal()
            self.dumpMess.close()

    def getAllDumpVal(self):
        # # channel 1
        self.act.flushInputBuffer("None")
        resultOne = self.act.dump_fog_parameters(1)
        if "無法取得值" in resultOne:
            self.paraCh1 = "參數值無法取得"
        else:
            self.paraCh1 = resultOne
        t1 = time.perf_counter()
        # print(self.paraCh1)
        # channel 2
        self.act.flushInputBuffer("None")
        resultTwo = self.act.dump_fog_parameters(2)
        if "無法取得值" in resultTwo:
            self.paraCh2 = "參數值無法取得"
        else:
            self.paraCh2 = resultTwo
        # print("channel 2的參數:")
        # print(self.paraCh2)
        t2 = time.perf_counter()
        # # channel 3
        self.act.flushInputBuffer("None")
        resultThree = self.act.dump_fog_parameters(3)
        if "無法取得值" in resultThree:
            self.paraCh3 = "參數值無法取得"
        else:
            self.paraCh3 = resultThree
        t3 = time.perf_counter()
        # print("All.........")
        # print(self.paraCh3)

    def getChannelOneVal(self):
        # # channel 1
        self.act.flushInputBuffer("None")
        resultOne = self.act.dump_fog_parameters(1)
        if "無法取得值" in resultOne:
            self.paraCh1 = "參數值無法取得"
        else:
            self.paraCh1 = resultOne
        t1 = time.perf_counter()
        # print("One..............")
        # print(self.paraCh1)

    def getChannelTwoVal(self):
        # channel 2
        self.act.flushInputBuffer("None")
        resultTwo = self.act.dump_fog_parameters(2)
        if "無法取得值" in resultTwo:
            self.paraCh2 = "參數值無法取得"
        else:
            self.paraCh2 = resultTwo
        # print("channel 2的參數:")
        # print(self.paraCh2)
        t2 = time.perf_counter()
        # print("Two...........")

    def getChannelThreeVal(self):
        # # channel 3
        self.act.flushInputBuffer("None")
        resultThree = self.act.dump_fog_parameters(3)
        if "無法取得值" in resultThree:
            self.paraCh3 = "參數值無法取得"
        else:
            self.paraCh3 = resultThree
        t3 = time.perf_counter()
        # print(self.paraCh3)
        # print("Three..........")

    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetFPGATimer(self, ch):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1, ch)

    # 20231128 自動重連使用
    def autoinstrumentReset(self, t):
        __errStr = ''
        try:
            logger.info("The device is reset. (設備重置)")
            date_now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            init_time = self.imudata_file.__openTime__
            timeoutAllTime = timedelta(hours=t[2], minutes=t[1], seconds=t[0])
            timeoutTime = init_time + timeoutAllTime
            strTimeoutTime = timeoutTime.strftime("%Y/%m/%d %H:%M:%S")
            self.imudata_file.write_line('#' + strTimeoutTime + '\n\n' +
                                         '#' + date_now)
        except Exception as e:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'Exception — {e}, line {__lineNum}.)')
            __errStr = '自動重連寫入重連時間的部分出現錯誤'
        finally:
            if __errStr != "":
                self.act.isRun = False
                self.occurError(__errStr)
            elif __errStr == "":
                pass

    def occurError(self, errStr:str):
        if self.reset_flag == 0:  # 只會出現一次
            self.reset_flag = 1
            self.top.save_block.rb.setChecked(False)
            self.imudata_file.close()
            self.press_stop = True
            self.first_run_flag = True
            mesTitle = "Error occurred while retrieving data"
            self.disconnect()  # 切斷連接
            self.WidgetMes(mesTitle, errStr)
            print(self.reset_flag)
            logger.error("Stop when timeout or error occurs.(發生Timeout且超時或是錯誤導致GUI的停止運行)")

    def WidgetMes(self, mestitle, errorMes):
        mesbox = QtWidgets.QMessageBox(self.top)
        mesbox.critical(self.top, mestitle, errorMes)

    def widMesdump(self, title = "正在取參數中...", content="取參數中，請勿進行任何動作。\n感謝配合~"):
        evenloop = QEventLoop()
        QTimer.singleShot(1000, evenloop.quit)
        self.dumpMess = QMessageBox()
        self.dumpMess.setWindowTitle(title)
        self.dumpMess.setIcon(QMessageBox.Information)
        self.dumpMess.setText(content)
        self.dumpMess.show()
        evenloop.exec()

    def closeStopMes(self, en):
        if en == True and self.hasConnect == True:
            self.dumpMess.close()

    def start(self):
        if self.haveClickBtn == False:
            self.resetFPGATimer(3)
            self.act.isRun = True
            self.press_stop = False
            self.act.readIMU()
            self.act.start()
            if self.reset_flag == 1:
                self.reset_flag = 0
                self.act.recording_device_reset_time = 0
                logger.info("The device is reset. (被切斷的重啟)")
            else:
                self.act.recording_device_reset_time = 0
                logger.info('The GUI is started to read the data.')
            file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
            filePara_name = self.top.save_block.le_filename.text() + "_Para" + self.top.save_block.le_ext.text()
            self.imudata_file_Para.name = filePara_name
            self.imudata_file_Para.open(self.top.save_block.rb.isChecked())
            if self.top.save_block.rb.isChecked():
                self.imudata_file_Para.write_dump("Channel 1")
                self.imudata_file_Para.write_dump(self.paraCh1)
                self.imudata_file_Para.write_dump("Channel 2")
                self.imudata_file_Para.write_dump(self.paraCh2)  # 寫入檔案中
                self.imudata_file_Para.write_dump("Channel 3")
                self.imudata_file_Para.write_dump(self.paraCh3)
            else:
                # print("沒有勾選save")
                logger.info("The save checkbox is not checked.")
            self.imudata_file_Para.close()

            self.imudata_file.name = file_name
            self.imudata_file.open(self.top.save_block.rb.isChecked())
            self.imudata_file.write_line('time,wx,wy,wz,ax,ay,az,Tx,Ty,Tz,Pitch,Roll,Yaw')
            self.haveClickBtn = True

    def stop(self):
        # self.resetFPGATimer()
        self.act.isRun = False
        self.top.save_block.rb.setChecked(False)
        self.top.saveDumpCb.DumpCb_Z.setChecked(False)
        self.top.saveDumpCb.DumpCb_X.setChecked(False)
        self.top.saveDumpCb.DumpCb_Y.setChecked(False)
        self.paraCh1 = None
        self.paraCh2 = None
        self.paraCh3 = None
        self.imudata_file.close()
        self.press_stop = True
        self.first_run_flag = True
        self.haveClickBtn = False
        logger.info('The GUI is stopped reading the data.')
        print('press stop')
        self.widMesdump("正在停止中......", "請勿執行任何動作，還在停止儀器中，請稍後~\n感謝配合")

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

    def collectData(self, imudata):
        if not self.press_stop:
            __errStr = ""
            # Add self.first_run_flag to make sure that TIME data starts from nearing Zero after pressing Read button,
            # if the first element of imudata['TIME'] is greater than some arbitrary small value (two here), neglect
            # this imudata['TIME'] data!
            # if self.first_run_flag and (int(imudata['TIME'][0]) > 2):
            #     return
            self.first_run_flag = False
            try:
                input_buf = self.act.readInputBuffer()
            except Exception as e:
                __excType, __excObj, __excTb = sys.exc_info()
                __lineNum = __excTb.tb_lineno
                logger.error(f'Get a PortNotOpenError, {e}.(An error occurred in the gathering data, line {__lineNum}.)')
                __errStr = f"An error occurred in the gathering data, PortNotOpenError.\nPlease check the issue where the error occurred, thank you.\n" \
                           "And please take a screenshot of the error message for further troubleshooting by the responsible party.\nThank you for your cooperation."
            except serial.serialutil.SerialException as e:  # 沒開電狀況下會出錯
                __excType, __excObj, __excTb = sys.exc_info()
                __lineNum = __excTb.tb_lineno
                logger.error(f'SerialException — {e}.(An error occurred in the gathering data, line {__lineNum}.)')
                __errStr = f"An error occurred in the gathering data.\nPlease check the issue where the error occurred, thank you.\n" \
                         "And please take a screenshot of the error message for further troubleshooting by the responsible party.\nThank you for your cooperation."
            finally:
                if __errStr != "":
                    self.act.isRun = False
                    self.occurError(__errStr)
                elif __errStr == "":
                    pass
            t0 = time.perf_counter()
            # imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
            self.printPdTemperature(imudata["PD_TEMP_Z"][0], imudata["PD_TEMP_X"][0],imudata["PD_TEMP_Y"][0] )
            # print(imudata)
            # print(imudata["PITCH"], imudata["PITCH"][0])
            # print(imudata["ROW"], imudata["ROW"][0])
            # print(imudata["YAM"], imudata["YAM"][0])
            self.printAtt(imudata["PITCH"][0], imudata["ROW"][0], imudata["YAM"][0])
            # print(imudata['PIG_WZ'])
            # imudata['PIG_WZ'] = np.clip(imudata['PIG_WZ'], -900, 900)
            t1 = time.perf_counter()

            try:
                sample = 1000
                # print(imudata["TIME"])
                self.imudata["TIME"] = np.append(self.imudata["TIME"], imudata["TIME"])
                self.imudata["WX"] = np.append(self.imudata["WX"], imudata["WX"])
                self.imudata["WY"] = np.append(self.imudata["WY"], imudata["WY"])
                self.imudata["WZ"] = np.append(self.imudata["WZ"], imudata["WZ"])
                self.imudata["AX"] = np.append(self.imudata["AX"], imudata["AX"])
                self.imudata["AY"] = np.append(self.imudata["AY"], imudata["AY"])
                self.imudata["AZ"] = np.append(self.imudata["AZ"], imudata["AZ"])
                self.imudata["PD_TEMP_X"] = np.append(self.imudata["PD_TEMP_X"], imudata["PD_TEMP_X"])
                self.imudata["PD_TEMP_Y"] = np.append(self.imudata["PD_TEMP_Y"], imudata["PD_TEMP_Y"])
                self.imudata["PD_TEMP_Z"] = np.append(self.imudata["PD_TEMP_Z"], imudata["PD_TEMP_Z"])
                self.imudata["PITCH"] = np.append(self.imudata["PITCH"], imudata["PITCH"])
                self.imudata["ROW"] = np.append(self.imudata["ROW"], imudata["ROW"])
                self.imudata["YAM"] = np.append(self.imudata["YAM"], imudata["YAM"])
                if len(self.imudata["TIME"]) > sample:
                    self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["WX"] = self.imudata["WX"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["WY"] = self.imudata["WY"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["WZ"] = self.imudata["WZ"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["AX"] = self.imudata["AX"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["AY"] = self.imudata["AY"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["AZ"] = self.imudata["AZ"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["PD_TEMP_X"] = self.imudata["PD_TEMP_X"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["PD_TEMP_Y"] = self.imudata["PD_TEMP_Y"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["PD_TEMP_Z"] = self.imudata["PD_TEMP_Z"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["PITCH"] = self.imudata["PITCH"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["ROW"] = self.imudata["ROW"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["YAM"] = self.imudata["YAM"][self.act.arrayNum:self.act.arrayNum + sample]
                t2 = time.perf_counter()
                debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                             + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)
                # print(imudata["PIG_WZ"])
                datalist = [imudata["TIME"], imudata["WX"], imudata["WY"], imudata["WZ"],
                            imudata["AX"], imudata["AY"], imudata["AZ"],
                            imudata["PD_TEMP_X"], imudata["PD_TEMP_Y"], imudata["PD_TEMP_Z"], imudata["PITCH"], imudata["ROW"], imudata["YAM"]]
                data_fmt = "%.3f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f,%.1f,%.1f,%.5f,%.5f,%.5f"
                self.imudata_file.saveData(datalist, data_fmt)
            except KeyError as e:
                __excType, __excObj, __excTb = sys.exc_info()
                __lineNum = __excTb.tb_lineno
                logger.error(
                    f'Get a KeyError.(An error occurred in the gathering data for plotting, line {__lineNum}.)')
                __errStr = "An error occurred in the gathering data for plotting, KeyError.\nPlease check the issue where the error occurred, thank you.\n" \
                         "And please take a screenshot of the error message for further troubleshooting by the responsible party.\nThank you for your cooperation."
            except ValueError as e:
                __excType, __excObj, __excTb = sys.exc_info()
                __lineNum = __excTb.tb_lineno
                logger.error(
                    f'ValueError: {e}.(An error occurred in the gathering data for plotting, line {__lineNum}.)')
                __errStr = "An error occurred in the gathering data for plotting, ValueError.\nPlease check the issue where the error occurred, thank you.\n" \
                         "And please take a screenshot of the error message for further troubleshooting by the responsible party.\nThank you for your cooperation."
            except IOError as IOerr:
                __excType, __excObj, __excTb = sys.exc_info()
                __lineNum = __excTb.tb_lineno
                logger.error(
                    f'IOError — {IOerr}.(An error occurred while the data storage portion, line {__lineNum} .)')
                __errStr = "An error occurred in the gathering data for plotting, IOError.\nPlease check the issue where the error occurred, thank you.\n" \
                         "And please take a screenshot of the error message for further troubleshooting by the responsible party.\nThank you for your cooperation."
            finally:
                if __errStr != "":
                    self.act.isRun = False
                    self.occurError(__errStr)
                elif __errStr == "":
                    pass

            self.plotdata(self.imudata)
            self.printUpdateRate(self.imudata["TIME"])
            # print(len(self.imudata["TIME"]))
            # print('first_run_flag')


    def plotdata(self, imudata):
        # print('plotdata: ', imudata['TIME'])
        if self.top.plot1_unit_rb.btn_status == 'dph':
            factor = 3600
        else:
            factor = 1
        # print(imudata["PIG_WZ"], end=', ')
        # print(factor)
        # if self.top.plot1_showWz_cb.cb_1.isChecked():
        #     self.top.plot1.ax1.setData(imudata["TIME"], imudata["WX"])
        # else:
        #     self.top.plot1.ax1.clear()
        # if self.top.plot1_showWz_cb.cb_2.isChecked():
        #     self.top.plot1.ax2.setData(imudata["TIME"], imudata["WY"])
        # else:
        #     self.top.plot1.ax2.clear()
        self.top.plot1.ax3.setData(imudata["TIME"], imudata["WZ"]*factor)
        self.top.plot1.ax1.setData(imudata["TIME"], imudata["WX"]*factor)
        self.top.plot1.ax2.setData(imudata["TIME"], imudata["WY"]*factor)

        self.top.plot7.ax1.setData(imudata["TIME"], imudata["AX"])
        self.top.plot7.ax2.setData(imudata["TIME"], imudata["AY"])
        self.top.plot7.ax3.setData(imudata["TIME"], imudata["AZ"])
        # self.top.plot2.ax.setData(imudata["TIME"], imudata["AX"])
        # self.top.plot3.ax.setData(imudata["TIME"], imudata["AY"])
        # self.top.plot4.ax.setData(imudata["TIME"], imudata["AZ"])
        # self.top.plot5.ax.setData(imudata["TIME"], imudata["WX"])
        # self.top.plot6.ax.setData(imudata["TIME"], imudata["WY"])


    # 當切換radiobutton時，plot的標題可以跟著改變
    def plottitlechanged(self):
        if self.top.plot1_unit_rb.btn_status == "dph":
            self.top.plot1.p.setTitle("FOG　　  [unit: dph]")
        elif self.top.plot1_unit_rb.btn_status == "dps":
            self.top.plot1.p.setTitle("FOG　　  [unit: dps]")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
