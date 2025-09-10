""" ####### log stuff creation, always on the top ########  """
import os
import builtins
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

ExternalName_log = "main_logger"
""" ####### end of log stuff creation ########  """
# 寫入環境變數，只有執行這一個程式，才會寫入版號(是外部還是內部使用)
os.environ["verNum"] = str(True)
import sys

# current_directory = os.path.dirname(os.path.abspath(__file__))
# print(current_directory)
# myLib_path = os.path.join(current_directory, "myLib")
# sys.path.append(myLib_path)

# sys.path.append("../")

import time
import numpy as np
from myLib import common as cmn
from myLib.logProcess import logProcess
from myLib.myGui.mygui_serial import *
from myLib.mySerial.Connector import Connector
from myLib.myGui.pig_parameters_widget import pig_parameters_widget
from myLib.myGui.pig_parameters_widget import CMD_FOG_TIMER_RST
from myLib.myGui.pig_menu_manager import pig_menu_manager
from myLib.myGui import analysis_Allan, analysis_TimingPlot
from myLib.myGui import analysis_Allan, analysis_TimingPlot, myRadioButton
from myLib.myGui.pig_W_A_calibration_parameter_widget import pig_calibration_widget
from myLib.myGui.fog_select_command import Select_comMD
from PySide6.QtWidgets import *
from pigImu_Widget import pigImuWidget as TOP
from pigImuReader import pigImuReader as ACTION
from pigImuReader import IMU_DATA_STRUCTURE
from PySide6.QtCore import Signal
from myLib.myGui.pig_Kal_para_widget import pigKalParaWidget
from myLib.myGui.pig_events_view import pig_events_view
from myLib.myGui.AutoComp_widget import RectWidget


PRINT_DEBUG = 0


# for GP-1Z IMU
class mainWindow(QMainWindow):
    is_port_open_qt = Signal(bool)

    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()
        self.__first_run_flag = True
        self.press_stop = False
        self.resize(1600, 800)
        self.pig_parameter_widget = None
        self.cali_parameter_menu = None
        self.select_cmd = None
        self.__portName = None
        self.__baudRate = "BaudRate(預設)"
        self.__portNotErr = True # 用來判斷port的部分
        self.__versionNumber = "SG-AHRS-01-07-TTC-RW"
        self.setWindowTitle("Aegiverse GUI ("+self.__versionNumber+")")
        self.__connector = Connector()
        self.__isFileOpen = False
        self.top = TOP()
        self.act = ACTION()
        self.imudata_file = cmn.data_manager(fnum=0)
        self.pig_cali_menu = calibrationBlock()
        self.pig_initial_setting_menu = myRadioButton.radioButtonBlock_2('SYNC MODE', 'OFF', 'ON', False)  # True
        self.act.isCali = True
        self.menu = self.menuBar()
        self.pig_menu = pig_menu_manager(self.menu, self)
        self.analysis_allan = analysis_Allan.analysis_allan_widget(['fog'])
        self.analysis_timing_plot = analysis_TimingPlot.analysis_timing_plot_widget(
            ['fog', 'T'])
        self.AutoCompRect = RectWidget()
        self.pig_events_log_menu = pig_events_view()
        logProcess.setVariable(self.pig_events_log_menu)
        self.pig_Kal = None
        self.linkfunction()
        self.act.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()

        self.__debug = debug_en
        self.t_start = time.perf_counter()
        self.act.isKal = True
        # self.act.kal_R = 50
        # self.act.kal_Q = 1


    def mainUI(self):
        self.setCentralWidget(self.top)

    def linkfunction(self):
        # usb connection
        self.top.usb.bt_update.clicked.connect(self.updateComPort)
        self.top.usb.cb.currentIndexChanged.connect(self.selectComPort)
        self.top.usb.bt_connect.clicked.connect(self.connectMain)
        self.top.usb.bt_disconnect.clicked.connect(self.disconnectMain)
        self.top.usb.B_Rate.currentIndexChanged.connect(self.selectBaudRate)
        # bt connection
        self.top.read_bt.clicked.connect(self.start)
        self.top.stop_bt.clicked.connect(self.stop)
        # rb connection
        self.top.kal_filter_rb.toggled.connect(lambda: self.update_kalFilter_en(self.top.kal_filter_rb))
        # compensation button
        self.top.compensate_block.bt.clicked.connect(self.compensation_calcu_start)
        # pyqtSignal connection
        self.act.imudata_qt.connect(self.collectData)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)
        self.act.buffer_qt.connect(self.printBuffer)
        self.is_port_open_qt.connect(self.is_port_open_status_manager)
        # menu trigger connection
        self.pig_menu.action_trigger_connect([self.show_events_log_menu,
                                              self.show_parameters,
                                              self.show_calibration_menu,
                                              self.show_plot_data_menu,
                                              self.show_cal_allan_menu,
                                              self.show_initial_setting_menu,
                                              self.show_W_A_cali_parameter_menu,
                                              self.show_select_cmd_menu,
                                              self.show_Kal_menu
                                              ])
        # file name le
        self.top.save_block.le_filename.editingFinished.connect(
            lambda: self.file_name_le_connect(self.top.save_block.le_filename))

        # 設定使用Checkbox控制是否要顯示畫出的線
        self.top.plot1_lineName.cb1.clicked.connect(self.top.plotLineWXVisible)
        self.top.plot1_lineName.cb2.clicked.connect(self.top.plotLineWYVisible)
        self.top.plot1_lineName.cb3.clicked.connect(self.top.plotLineWZVisible)
        self.top.plot2_lineName.cb1.clicked.connect(self.top.plotLineAXVisible)
        self.top.plot2_lineName.cb2.clicked.connect(self.top.plotLineAYVisible)
        self.top.plot2_lineName.cb3.clicked.connect(self.top.plotLineAZVisible)
        # 切換角速度的單位功能
        self.top.plot1_unit_rb.rb1.clicked.connect(self.plotTitleChanged)
        self.top.plot1_unit_rb.rb2.clicked.connect(self.plotTitleChanged)
        # 設定姿態指示器的功能，讓圖顯示當下要呈現的姿態

        # 將計算的補償寫至設備並計算GX、GY、AX、AY
        self.act.AutoCompAvg_qt.connect(self.compensation_calcu_stop)


    def file_name_le_connect(self, obj):
        cmn.print_debug('file name: %s' % obj.text(), PRINT_DEBUG)
        filename = obj.text() + self.top.save_block.le_ext.text()
        self.analysis_timing_plot.pbar.set_filename_ext(filename)
        self.analysis_allan.pbar.set_filename_ext(filename)

    def show_events_log_menu(self):
        self.pig_events_log_menu.show()

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

    def show_select_cmd_menu(self):
        self.select_cmd.show()

    def show_Kal_menu(self):
        self.pig_Kal.show()

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()
        self.pig_menu.pig_kal_filter.setDisabled(not rb.isChecked())


    def printBuffer(self, val):
        self.top.buffer_lb.lb.setText(str(val))

    def printAtt(self, pitch, row, yaw):
        # self.top.pitch_lb.lb.setText(str(pitch))
        # self.top.row_lb.lb.setText(str(row))
        # self.top.yaw_lb.lb.setText(str(yaw))
        self.top.pitch_lb.lb.setText(f"{pitch:.5f}")
        self.top.row_lb.lb.setText(f"{row:.5f}")
        self.top.yaw_lb.lb.setText(f"{yaw:.5f}")

    def printPdTemperature(self, val):
        if (time.perf_counter() - self.t_start) > 0.5:
            self.top.pd_temp_lb.lb.setText(str(val))
            self.t_start = time.perf_counter()

    def printUpdateRate(self, t_list):  # 1000007
        try:
            update_rate = round(((t_list[-1] - t_list[0]) / (len(t_list) - 1)) ** -1, 1)
            self.top.data_rate_lb.lb.setText(str(update_rate))
        except IndexError as e:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f'1000007, IndexError — {e}.(An error occurred with the array index, line {__lineNum}.)')
            self.top.data_rate_lb.lb.setText(str(0))

    def updateComPort(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.addPortItems(portNum, portList)

    def selectComPort(self):
        self.__portName = self.top.usb.selectPort()

    def selectBaudRate(self):
        if self.top.usb.selectBRate() != "BaudRate(預設)":
            self.__baudRate = int(self.top.usb.selectBRate())

        if self.top.usb.selectBRate() == "BaudRate(預設)":
            self.__baudRate = "BaudRate(預設)"

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connectMain(self):  #　1000006
        self.__portNotErr= True
        if self.__baudRate != "BaudRate(預設)":
            try:
                is_port_open = self.act.connectRead(self.__connector, self.__portName, self.__baudRate)
                if is_port_open != False:
                    self.is_port_open_qt.emit(is_port_open)

                    # This line instantiate a parameter widget, load the parameter.json from LE block and send to FPGA
                    # self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
                    self.pig_parameter_widget = pig_parameters_widget(self.act, self.__versionNumber)
                    self.cali_parameter_menu = pig_calibration_widget(self.act)
                    self.select_cmd = Select_comMD(self.act)
                    self.pig_Kal = pigKalParaWidget(self.act)
                    self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
                    self.act.stopIMU()
                    self.imuThreadStopDetect()
                else:
                    self.__portNotErr = False
            except Exception as e:
                self.__portNotErr = False
                __excType, __excObj, __excTb = sys.exc_info()
                __lineNum = __excTb.tb_lineno
                logger.error(f'1000006, {type(e).__name__} — {e}.(An error occurred in the connect, line {__lineNum}.)')
            finally:
                if not self.__portNotErr:
                    __title = "Connect Error"
                    __errStr =  "An error occurred in the connect.\n"\
                                "1.Please confirm if the USB COM Port is correctly connected to the PC.\n" \
                                "2.Please ensure that the USB COM Port you want to connect is not being used by another application.\n"
                    self.WidgetMes(__title, __errStr)


    def disconnectMain(self): #　1000005
        try:
            is_port_open = self.act.disconnectRead()
            self.is_port_open_qt.emit(is_port_open)
            self.top.kal_filter_rb.setChecked(False)
        except RuntimeError as runErr:
            __excType, __excObj, __excTb = sys.exc_info()
            __lineNum = __excTb.tb_lineno
            logger.error(f"1000005, RuntimeError — {runErr}. (An error occurred while in disconnect, line {__lineNum}.)")


    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetFPGATimer(self, ch):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1, ch)

    def occurError(self, errStr: str):
        self.stop()
        self.disconnectMain()
        mesTitle = "Error occurred"
        self.WidgetMes(mesTitle, errStr)

    def WidgetMes(self, mestitle, errorMes):
        mesbox = QMessageBox(self.top)
        mesbox.critical(self.top, mestitle, errorMes)


    def start(self):
        self.top.setAutoCompBtnEnable(True)
        self.resetFPGATimer(3)
        self.act.readIMU()
        self.act.isRun = True
        self.press_stop = False
        self.act.start()
        if self.top.save_block.rb.isChecked():
            file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
            self.imudata_file.name = file_name
            self.imudata_file.open(self.top.save_block.rb.isChecked())
            self.imudata_file.write_line('time,wx,wy,wz,ax,ay,az,T,pitch,roll,yaw')

    def stop(self):
        # self.resetFPGATimer()
        self.top.setAutoCompBtnEnable(False)
        self.act.isRun = False
        self.act.stopIMU()
        if self.top.save_block.rb.isChecked():
            self.imudata_file.close()
        self.top.save_block.rb.setChecked(False)
        self.press_stop = True
        self.first_run_flag = True
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

    def compensation_calcu_start(self):
        self.top.setRunAutoCompBtnEnable(True)
        self.act.isRunAutoComp = True
        self.cali_parameter_menu.dump_Btn.click()
        self.AutoCompRect.show_message()
        self.AutoCompRect.raise_()
        widget_geom = self.geometry()
        x = widget_geom.x() + (widget_geom.width() - self.AutoCompRect.width()) // 2
        y = widget_geom.y() + (widget_geom.height() - self.AutoCompRect.height()) // 2
        self.AutoCompRect.move(x, y)
        # 執行取數據
        self.resetFPGATimer(3)
        self.act.readIMU()
        self.act.runAutoComp(self.top.compensate_block.le.text())


    def compensation_calcu_stop(self, avg):
        # 需要乘以負號
        WX_avg = avg[0] * -1
        WY_avg = avg[1] * -1
        AX_avg = avg[2] * -1
        AY_avg = avg[3] * -1

        self.cali_parameter_menu.GxC.le.setText(str(WX_avg))
        self.cali_parameter_menu.GyC.le.setText(str(WY_avg))
        self.cali_parameter_menu.AxC.le.setText(str(AX_avg))
        self.cali_parameter_menu.AyC.le.setText(str(AY_avg))

        self.cali_parameter_menu.Update_Btn.click()
        print("計算完成")
        self.AutoCompRect.hide_message()
        self.top.setRunAutoCompBtnEnable(False)
        self.act.isRunAutoComp = False
        mes = QMessageBox(self.top)
        mes.information(self.top, "自動補償功能執行完成", "自動補償功能已計算完成，並成功將misalignment參數值更新。")


    def collectData(self, imudata):  #　1000002
        if not self.press_stop:
            if self.act.isOccurrErr == True:
                self.act.isOccurrErr = False
                self.occurError(errStr="撈取數據功能出現錯誤。")
                return
            # Add self.first_run_flag to make sure that TIME data starts from nearing Zero after pressing Read button,
            # if the first element of imudata['TIME'] is greater than some arbitrary small value (two here), neglect
            # this imudata['TIME'] data!
            # if self.first_run_flag and (int(imudata['TIME'][0]) > 2):
            #     return
            self.first_run_flag = False
            input_buf = self.act.readInputBuffer()
            t0 = time.perf_counter()
            # imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
            try:
                self.printPdTemperature(imudata["PD_TEMP"][0])
                self.changYawLabel(imudata["YAW"][0])
                self.changePitchPos(imudata["PITCH"][0])
                self.changeRollImgAxis(imudata["ROLL"][0])
                self.printAtt(imudata["PITCH"][0], imudata["ROLL"][0], imudata["YAW"][0])
                # print(imudata['PIG_WZ'])
                # imudata['PIG_WZ'] = np.clip(imudata['PIG_WZ'], -900, 900)
                t1 = time.perf_counter()
                sample = 1000
                # print(imudata["TIME"])
                self.imudata["TIME"] = np.append(self.imudata["TIME"], imudata["TIME"])
                self.imudata["WX"] = np.append(self.imudata["WX"], imudata["WX"])
                self.imudata["WY"] = np.append(self.imudata["WY"], imudata["WY"])
                self.imudata["WZ"] = np.append(self.imudata["WZ"], imudata["WZ"])
                self.imudata["AX"] = np.append(self.imudata["AX"], imudata["AX"])
                self.imudata["AY"] = np.append(self.imudata["AY"], imudata["AY"])
                self.imudata["AZ"] = np.append(self.imudata["AZ"], imudata["AZ"])
                self.imudata["PD_TEMP"] = np.append(self.imudata["PD_TEMP"], imudata["PD_TEMP"])
                if len(self.imudata["TIME"]) > sample:
                    self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["WX"] = self.imudata["WX"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["WY"] = self.imudata["WY"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["WZ"] = self.imudata["WZ"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["AX"] = self.imudata["AX"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["AY"] = self.imudata["AY"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["AZ"] = self.imudata["AZ"][self.act.arrayNum:self.act.arrayNum + sample]
                    self.imudata["PD_TEMP"] = self.imudata["PD_TEMP"][self.act.arrayNum:self.act.arrayNum + sample]
                t2 = time.perf_counter()
                debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                             + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
                cmn.print_debug(debug_info, self.__debug)
                # print(imudata["PIG_WZ"])
                datalist = [imudata["TIME"], imudata["WX"], imudata["WY"], imudata["WZ"],
                            imudata["AX"], imudata["AY"], imudata["AZ"], imudata["PD_TEMP"],
                            imudata["PITCH"], imudata["ROLL"], imudata["YAW"]]
                data_fmt = "%.3f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f,%.5f,%.5f,%.5f"
                self.imudata_file.saveData(datalist, data_fmt)
                self.plotdata(self.imudata)
                self.printUpdateRate(self.imudata["TIME"])
                # print(len(self.imudata["TIME"]))
                # print('first_run_flag')
                self.changeRotatePoint()
            except Exception as e:
                __excType, __excObj, __excTb = sys.exc_info()
                __lineNum = __excTb.tb_lineno
                logger.error(f'1000002, {type(e).__name__} - An error occurred while collecting data, line {__lineNum}.')
                self.occurError(errStr="撈取數據功能出現錯誤。")


    def plotdata(self, imudata):
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
        # self.top.plot1.ax1.setData(imudata["TIME"], imudata["WZ"]*factor)
        # self.top.plot2.ax.setData(imudata["TIME"], imudata["AX"])
        # self.top.plot3.ax.setData(imudata["TIME"], imudata["AY"])
        # self.top.plot4.ax.setData(imudata["TIME"], imudata["AZ"])
        # self.top.plot5.ax.setData(imudata["TIME"], imudata["WX"])
        # self.top.plot6.ax.setData(imudata["TIME"], imudata["WY"])

    def plotTitleChanged(self):
        if self.top.plot1_unit_rb.btn_status == "dph":
            self.top.plot1.p.setTitle("FOG  [dph]")
        elif self.top.plot1_unit_rb.btn_status == "dps":
            self.top.plot1.p.setTitle("FOG  [dps]")


    def changYawLabel(self, yaw):
        self.top.Att_indicator.yaw_flight_update_move(yaw)

    def changeRollImgAxis(self, roll):
        self.top.Att_indicator.roll_flight_axis_update_rotation(roll)

    def changePitchPos(self, pitch):
        self.top.Att_indicator.pitch_flight_update_translate(pitch)

    def changeRotatePoint(self):
        self.top.Att_indicator.updateView()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
