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
from pigImu_Widget import pigImuWidget as TOP
from pigImuReader import pigImuReader as ACTION
from pigImuReader import IMU_DATA_STRUCTURE
import numpy as np

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
        self.__portName = None
        self.setWindowTitle("Aegiverse FOG GUI")
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
        self.linkfunction()
        self.act.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()

        self.__debug = debug_en
        self.t_start = time.perf_counter()

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
        # menu trigger connection
        self.pig_menu.action_trigger_connect([self.show_parameters,
                                              self.show_calibration_menu,
                                              self.show_plot_data_menu,
                                              self.show_cal_allan_menu,
                                              self.show_initial_setting_menu
                                              ])
        # file name le
        self.top.save_block.le_filename.editingFinished.connect(
            lambda: self.file_name_le_connect(self.top.save_block.le_filename))

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

    def update_kalFilter_en(self, rb):
        self.act.isKal = rb.isChecked()

    def printBuffer(self, val):
        self.top.buffer_lb.lb.setText(str(val))

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

    def selectComPort(self):
        self.__portName = self.top.usb.selectPort()

    def is_port_open_status_manager(self, open):
        # print("port open: ", open)
        self.top.usb.updateStatusLabel(open)
        self.pig_menu.setEnable(open)
        self.top.setBtnEnable(open)

    def connect(self):
        is_port_open = self.act.connect(self.__connector, self.__portName, 230400)
        self.is_port_open_qt.emit(is_port_open)

        # This line instantiate a parameter widget, load the parameter.json from LE block and send to FPGA
        self.pig_parameter_widget = pig_parameters_widget(self.act, self.top.para_block.le_filename.text() + '.json')
        self.act.isCali_w, self.act.isCali_a = self.pig_cali_menu.cali_status()  # update calibration flag to act
        self.act.stopIMU()

    def disconnect(self):
        is_port_open = self.act.disconnect()
        self.is_port_open_qt.emit(is_port_open)

    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def resetDataContainer(self):
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def resetFPGATimer(self, ch):
        self.act.writeImuCmd(CMD_FOG_TIMER_RST, 1, ch)

    def start(self):
        self.resetFPGATimer(3)
        self.act.readIMU()
        self.act.isRun = True
        self.press_stop = False
        self.act.start()
        file_name = self.top.save_block.le_filename.text() + self.top.save_block.le_ext.text()
        self.imudata_file.name = file_name
        self.imudata_file.open(self.top.save_block.rb.isChecked())
        self.imudata_file.write_line('time,wx,wy,wz,ax,ay,az,T')

    def stop(self):
        # self.resetFPGATimer()
        self.act.isRun = False
        self.top.save_block.rb.setChecked(False)
        self.imudata_file.close()
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

    def collectData(self, imudata):
        if not self.press_stop:
            # Add self.first_run_flag to make sure that TIME data starts from nearing Zero after pressing Read button,
            # if the first element of imudata['TIME'] is greater than some arbitrary small value (two here), neglect
            # this imudata['TIME'] data!
            # if self.first_run_flag and (int(imudata['TIME'][0]) > 2):
            #     return
            self.first_run_flag = False
            input_buf = self.act.readInputBuffer()
            t0 = time.perf_counter()
            # imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
            self.printPdTemperature(imudata["PD_TEMP"][0])
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
                        imudata["AX"], imudata["AY"], imudata["AZ"], imudata["PD_TEMP"]]
            data_fmt = "%.3f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f"
            self.imudata_file.saveData(datalist, data_fmt)
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
        self.top.plot1.ax1.setData(imudata["TIME"], imudata["WZ"]*factor)
        self.top.plot2.ax.setData(imudata["TIME"], imudata["AX"])
        self.top.plot3.ax.setData(imudata["TIME"], imudata["AY"])
        self.top.plot4.ax.setData(imudata["TIME"], imudata["AZ"])
        self.top.plot5.ax.setData(imudata["TIME"], imudata["WX"])
        self.top.plot6.ax.setData(imudata["TIME"], imudata["WY"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
