import logging
import os
from datetime import datetime


def setup_global_logging(log_level=logging.INFO):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename = datetime.now().strftime("app_%Y%m%d.log")
    log_path = os.path.join(log_dir, log_filename)

    # 建立格式：[時間] [層級] [模組名] 訊息
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. 檔案 Handler
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # 2. 控制台 Handler (開發用)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 配置 Root Logger
    root_logger = logging.getLogger("main")
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    root_logger.info("Logging system initialized.")


# 在程式一啟動時呼叫
setup_global_logging()



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
from myLib.myGui.pig_W_A_calibration_parameter_widget import pig_calibration_widget
from myLib.myGui.pig_configuration_widget import pig_configuration_widget
from myLib.myGui.hins_cmd_widget import hins_cmd_widget
from pigImu_Widget import pigImuWidget as TOP
from pigImuReader import pigImuReader as ACTION
from pigImuReader import IMU_DATA_STRUCTURE
import numpy as np

from PySide6.QtWidgets import *
from PySide6 import QtWidgets
from PySide6.QtCore import Signal

PRINT_DEBUG = 0

# for GP-1Z
class mainWindow(QMainWindow):
    is_port_open_qt = Signal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()
        self.__first_run_flag = True
        self.press_stop = False
        self.resize(1450, 800)
        self.pig_parameter_widget = None
        self.cali_parameter_menu = None
        self.pig_configuration_menu = None
        self.hins_cmd_menu = None
        self.pig_version_menu = None
        self.__portName = None
        self.GUI_vers = "HINS-INS-01-00-RD-RW"
        self.setWindowTitle("Aegiverse G-HINS GUI")
        self.__connector = Connector()
        self.__isFileOpen = False
        self.top = TOP()
        self.act = ACTION()
        self.imudata_file = cmn.data_manager(fnum=0)
        self.imudata_file_Misa = cmn.data_manager(fnum=2)
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

        self.updateComPort()
        self.reset_flag = 0  # 若沒有被切斷，就不會等於1
        self.haveClickBtn = False  # 判斷已經按按鈕了
        # # save dump 變數
        # self.paraCh1 = None
        # self.paraCh2 = None
        # self.paraCh3 = None
        self.dumpMess = None  # 用於save時下dump使用的訊息視窗
        self.recordSelAxis = None
        self.hasConnect = None

        ''' HINS ENU'''
        # Rcs = [0, -1, 0,
        #        -1, 0, 0,
        #        0, 0, -1]

        ''' HINS NED'''
        Rcs = [0, -1, 0,
               1, 0, 0,
               0, 0, 1]

        self.act.R_CS = Rcs


    def mainUI(self):
        self.setCentralWidget(self.top)

    def linkfunction(self):
        # usb connection
        self.top.usb.bt_update.clicked.connect(self.updateComPort)
        self.top.usb.cb.currentIndexChanged.connect(self.selectComPort)
        self.top.usb.bt_connect.clicked.connect(self.connectMain)
        self.top.usb.bt_disconnect.clicked.connect(self.disconnectMain)
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
        # menu trigger connection
        self.pig_menu.action_trigger_connect([self.show_parameters,
                                              self.show_W_A_cali_parameter_menu,
                                              self.show_version_menu,
                                              self.show_configuration_menu,
                                              self.show_hins_cmd_menu
                                              # self.show_calibration_menu,
                                              # self.show_plot_data_menu,
                                              # self.show_cal_allan_menu,
                                              # self.show_initial_setting_menu,

                                              ])
        # file name le
        self.top.save_block.le_filename.editingFinished.connect(
            lambda: self.file_name_le_connect(self.top.save_block.le_filename))
        # Clicking the checkbox will display the plot line chart
        self.top.plot1_lineName.cb1.clicked.connect(self.top.plot1LineNameOneVisible)
        self.top.plot1_lineName.cb2.clicked.connect(self.top.plot1LineNameTwoVisible)
        self.top.plot1_lineName.cb3.clicked.connect(self.top.plot1LineNameThreeVisible)
        self.top.plot2_lineName.cb1.clicked.connect(self.top.plot2LineNameOneVisible)
        self.top.plot2_lineName.cb2.clicked.connect(self.top.plot2LineNameTwoVisible)
        self.top.plot2_lineName.cb3.clicked.connect(self.top.plot2LineNameThreeVisible)
        # Switching the unit will trigger the function
        self.top.plot1_unit_rb.rb1.clicked.connect(self.plotTitleChanged)
        self.top.plot1_unit_rb.rb2.clicked.connect(self.plotTitleChanged)
        self.act.occur_err_qt.connect(self.occurError)
        # 當自動重連的狀態下，會執行的功能
        self.act.deviceReset_qt.connect(self.autoinstrumentReset)
        # 當勾選save的checkbox，會先執行dump取得參數
        # self.top.save_block.rb.clicked.connect(self.saveTXTDump)
        self.act.stopRemind_qt.connect(self.closeStopMes)

        # 是否使用RCS做資料frame旋轉至sensor frame
        self.top.save_block.rcs_cb.toggled.connect(
            lambda checked: setattr(self.act, "use_rcs", checked)
        )


    def file_name_le_connect(self, obj):
        cmn.print_debug('file name: %s' % obj.text(), PRINT_DEBUG)
        filename = obj.text() + self.top.save_block.le_ext.text()
        self.analysis_timing_plot.pbar.set_filename_ext(filename)
        self.analysis_allan.pbar.set_filename_ext(filename)

    def show_parameters(self):
        self.pig_parameter_widget.show()

    def show_hins_cmd_menu(self):
        if self.hins_cmd_menu:
            self.hins_cmd_menu.show()

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

    def show_configuration_menu(self):
        self.pig_configuration_menu.show()

    def show_version_menu(self):
        self.act.flushInputBuffer("None")
        self.pig_version_menu.ViewVersion(self.act.getVersion(2), self.GUI_vers)
        self.pig_version_menu.show()

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()

    def printBuffer(self, val):
        self.top.buffer_lb.lb.setText(str(val))

    def printPdTemperature(self, X_val, Y_val, Z_val):
        try:
            if (time.perf_counter() - self.t_start) > 0.5:
                self.top.pdX_temp_lb.lb.setText(f'{X_val:.4f}')
                self.top.pdY_temp_lb.lb.setText(f'{Y_val:.4f}')
                self.top.pdZ_temp_lb.lb.setText(f'{Z_val:.4f}')
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

    def printUpdateRate(self, t_list, window=100):
        """
        以最後 window 筆時間戳計算平均資料率 (Hz)，更新到 data_rate_lb。
        t_list: list / numpy array 等可迭代序列（秒）
        """
        try:
            # 轉成 list
            ts = t_list.tolist() if hasattr(t_list, "tolist") else list(t_list)
            if not ts:
                self.top.data_rate_lb.lb.setText("N/A")
                return

            # 只取最後 window 筆
            ts = ts[-window:]

            # 清理資料：移除 None / NaN
            clean = []
            for x in ts:
                try:
                    fx = float(x)
                    if fx == fx:  # 過濾 NaN
                        clean.append(fx)
                except (TypeError, ValueError):
                    continue

            if len(clean) < 2:
                self.top.data_rate_lb.lb.setText("N/A")
                return

            # 計算相鄰時間差（只保留正的）
            deltas = [b - a for a, b in zip(clean[:-1], clean[1:]) if (b - a) > 0]
            if not deltas:
                self.top.data_rate_lb.lb.setText("N/A")
                return

            avg_dt = sum(deltas) / len(deltas)
            update_rate = round(1.0 / avg_dt, 1)
            self.top.data_rate_lb.lb.setText(str(update_rate))

        except IndexError:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(
                f'IndexError — The index position has exceeded the range of the list.(An error occurred while the transmission rate is displayed, line {__lineNum}.)')
        except ValueError as ValError:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(
                f'ValueError — {ValError}.(An error occurred while the transmission rate is displayed, line {__lineNum}.)')
        except Exception as e:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(
                f'Unexpected — {e}.(An error occurred while the transmission rate is displayed, line {__lineNum}.)')
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

    def connectMain(self):
        is_port_open = self.act.connectRead(self.__connector, self.__portName, 230400)
        if (is_port_open != False):
            self.is_port_open_qt.emit(is_port_open)

            # This line instantiate a parameter widget, load the parameter.json from LE block and send to FPGA
            self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.save_block.le_filename.text())
            self.cali_parameter_menu = pig_calibration_widget(self.act, self.imudata_file_Misa, self.top.save_block.le_filename.text())
            self.pig_configuration_menu = pig_configuration_widget(self.act)
            self.pig_version_menu = VersionTable()
            self.hins_cmd_menu = hins_cmd_widget(self.act)
            self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
            self.act.stopIMU()
            self.act.raw_hins_ack_qt.connect(self.hins_cmd_menu.update_rx_display)
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

    def disconnectMain(self):
        is_port_open = self.act.disconnectRead()
        self.is_port_open_qt.emit(is_port_open)
        self.hasConnect = False
        # self.top.saveDumpCb.DumpCb_Z.setChecked(False)
        # self.top.saveDumpCb.DumpCb_X.setChecked(False)
        # self.top.saveDumpCb.DumpCb_Y.setChecked(False)


    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetFPGATimer(self, ch):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1, ch)
        time.sleep(0.001)
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 0, ch)

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
            #self.disconnectMain()  # 切斷連接
            self.stop()
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
            # self.resetFPGATimer(3)
            self.act.readIMU()
            self.act.isRun = True
            self.press_stop = False
            self.act.start()
            if self.reset_flag == 1:
                self.reset_flag = 0
                self.act.recording_device_reset_time = 0
                logger.info("The device is reset. (被切斷的重啟)")
            else:
                self.act.recording_device_reset_time = 0
                logger.info('The GUI is started to read the data.')
            filePara_name = self.top.save_block.le_filename.text() + "_Para" + self.top.save_block.le_ext.text()

            if self.top.save_block.rb.isChecked():
                print('save_block.rb.isChecked')
                # 若 RCS checkbox 有被勾選，file name 多一個 _Rcs
                if self.top.save_block.rcs_cb.isChecked():
                    file_name = self.top.save_block.le_filename.text() + '_Rcs' + self.top.save_block.le_ext.text()
                else:
                    file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
                self.imudata_file.name = file_name
                self.imudata_file.open(self.top.save_block.rb.isChecked())
                # 若 RCS checkbox 有被勾選，先寫一行提示
                if self.top.save_block.rcs_cb.isChecked():
                    print('top.save_block.rcs_cb.isChecked')
                    self.imudata_file.write_line("# data rotate to sensor frame")
                self.imudata_file.write_line('time,wx,wy,wz,ax,ay,az,Tx,Ty,Tz,Tacc,pitch,roll,yaw')

            self.haveClickBtn = True


    def stop(self):
        # self.resetFPGATimer()
        self.act.isRun = False
        self.top.save_block.rb.setChecked(False)
        # self.top.saveDumpCb.DumpCb_Z.setChecked(False)
        # self.top.saveDumpCb.DumpCb_X.setChecked(False)
        # self.top.saveDumpCb.DumpCb_Y.setChecked(False)
        # self.paraCh1 = None
        # self.paraCh2 = None
        # self.paraCh3 = None
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
            self.printPdTemperature(imudata["PD_TEMP_X"][0], imudata["PD_TEMP_Y"][0],imudata["PD_TEMP_Z"][0])
            self.changYawLabel(imudata["YAW"][0])
            self.changePitchPos(imudata["PITCH"][0])
            self.changeRollImgAxis(imudata["ROLL"][0])
            self.printAtt(imudata["PITCH"][0], imudata["ROLL"][0], imudata["YAW"][0])

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
                self.imudata["ACC_TEMP"] = np.append(self.imudata["ACC_TEMP"], imudata["ACC_TEMP"])
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
                    self.imudata["ACC_TEMP"] = self.imudata["ACC_TEMP"][self.act.arrayNum:self.act.arrayNum + sample]
                t2 = time.perf_counter()
                debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                             + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)
                # print(imudata["PIG_WZ"])
                datalist = [imudata["TIME"], imudata["WX"], imudata["WY"], imudata["WZ"],
                         imudata["AX"], imudata["AY"], imudata["AZ"]
                        , imudata["PD_TEMP_X"], imudata["PD_TEMP_Y"], imudata["PD_TEMP_Z"], imudata["ACC_TEMP"]
                        , imudata["PITCH"], imudata["ROLL"], imudata["YAW"]]
                data_fmt = "%.3f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.3f,%.3f,%.3f,%.3f,%.5f,%.5f,%.5f"
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

            self.plotData(self.imudata)
            self.printUpdateRate(self.imudata["TIME"])
            self.changeRotatePoint()
            # print(len(self.imudata["TIME"]))
            # print('first_run_flag')


    def plotData(self, imudata):
        # print('plotdata: ', imudata['TIME'])
        if self.top.plot1_unit_rb.btn_status == 'dph':
            factor = 3600
        else:
            factor = 1

        self.top.plot1.ax1.setData(imudata["TIME"], imudata["WX"]*factor)
        self.top.plot1.ax2.setData(imudata["TIME"], imudata["WY"]*factor)
        self.top.plot1.ax3.setData(imudata["TIME"], imudata["WZ"]*factor)
        self.top.plot2.ax1.setData(imudata["TIME"], imudata["AX"])
        self.top.plot2.ax2.setData(imudata["TIME"], imudata["AY"])
        self.top.plot2.ax3.setData(imudata["TIME"], imudata["AZ"])
        self.top.plot2.ax4.setData(imudata["TIME"], imudata["ACC_TEMP"])

    def plotTitleChanged(self):
        if self.top.plot1_unit_rb.btn_status == "dph":
            self.top.plot1.p.setTitle('FOG　　  [unit: dph]')
        elif self.top.plot1_unit_rb.btn_status == "dps":
            self.top.plot1.p.setTitle('FOG　　  [unit: dps]')

    def changYawLabel(self, yaw):
        self.top.Att_indicator.yaw_flight_update_move(yaw)

    def changeRollImgAxis(self, roll):
        self.top.Att_indicator.roll_flight_axis_update_rotation(roll)

    def changePitchPos(self, pitch):
        self.top.Att_indicator.pitch_flight_update_translate(pitch)

    def changeRotatePoint(self):
        self.top.Att_indicator.updateView()

    def printAtt(self, pitch, row, yaw):
        # self.top.pitch_lb.lb.setText(str(pitch))
        # self.top.row_lb.lb.setText(str(row))
        # self.top.yaw_lb.lb.setText(str(yaw))
        self.top.pitch_lb.lb.setText(f"{pitch:.5f}")
        self.top.row_lb.lb.setText(f"{row:.5f}")
        self.top.yaw_lb.lb.setText(f"{yaw:.5f}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
