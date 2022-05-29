import sys

sys.path.append("../")
from myLib import common as cmn
from myLib.myGui.mygui_serial import *
import time
from myLib.mySerial.Connector import Connector
from myLib.myGui.pig_parameters_widget import pigParameters
from PyQt5.QtWidgets import *
from memsImu_Widget import memsImuWidget as TOP
from memsImuReader import memsImuReader as ACTION
from memsImuReader import IMU_DATA_STRUCTURE
import numpy as np


class mainWindow(QWidget):
    def __init__(self, debug_en: bool = False):
        super(mainWindow, self).__init__()
        self.__portName = None
        self.setWindowTitle("memsImuPlot")
        self.__connector = Connector()
        self.__isFileOpen = False
        self.top = TOP()
        self.act = ACTION()
        self.pig_parameter = pigParameters()
        self.act.isCali = True
        self.linkfunciton()
        self.act.arrayNum = 10
        self.mainUI()
        self.imudata = self.resetDataContainer()
        # self.file_data = None

        self.__debug = debug_en

    def mainUI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.top, 0, 0, 1, 1)
        self.setLayout(mainLayout)

    def linkfunciton(self):
        # usb connection
        self.top.usb.bt_update.clicked.connect(self.updateComPort)
        self.top.usb.cb.currentIndexChanged.connect(self.selectComPort)
        self.top.usb.bt_connect.clicked.connect(self.connect)
        self.top.usb.bt_disconnect.clicked.connect(self.disconnect)
        # bt connection
        self.top.start_bt.clicked.connect(self.start)
        self.top.stop_bt.clicked.connect(self.stop)
        self.top.pig_parameter_bt.clicked.connect(self.show_parameters)
        # bt pyqtSignal connection
        self.act.imudata_qt.connect(self.collectData)
        self.act.imuThreadStop_qt.connect(self.imuThreadStopDetect)
        # rb connection
        # self.top.save_rb.toggled.connect(self.save_data_ctrl)

    def show_parameters(self):
        self.pig_parameter.show()

    def updateComPort(self):
        portNum, portList = self.__connector.portList()
        self.top.usb.addPortItems(portNum, portList)

    def selectComPort(self):
        self.__portName = self.top.usb.selectPort()

    def connect(self):
        is_open = self.act.connect(self.__connector, self.__portName, 230400)
        self.top.usb.updateStatusLabel(is_open)

    def disconnect(self):
        is_open = self.act.disconnect()
        self.top.usb.updateStatusLabel(is_open)

    def imuThreadStopDetect(self):
        self.imudata = self.resetDataContainer()

    def resetDataContainer(self):
        # return {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
        #         for k in set(IMU_DATA_STRUCTURE)}
        return {k: np.empty(0) for k in set(IMU_DATA_STRUCTURE)}

    def start(self):
        self.act.readIMU()
        self.act.isRun = True
        self.act.start()
        self.__isFileImuOpen, self.__FileImu_fd = cmn.file_manager(self.top.save_block.rb.isChecked(),
                                    self.top.save_block.le_filename.text()+self.top.save_block.le_ext.text())


    def stop(self):
        self.act.isRun = False
        self.top.save_block.rb.setChecked(False)
        self.__isFileImuOpen, self.__FileImu_fd = cmn.file_manager(self.top.save_block.rb.isChecked(),
                                   self.top.save_block.le_filename.text()+self.top.save_block.le_ext.text())

    def collectData(self, imudata, imuoffset):
        input_buf = self.act.readInputBuffer()
        t0 = time.perf_counter()
        imuoffset["TIME"] = [0]
        imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
        t1 = time.perf_counter()
        # self.imudata = cmn.dictOperation(self.imudata, imudata, "APPEND", IMU_DATA_STRUCTURE)
        self.imudata["TIME"] = np.append(self.imudata["TIME"], imudata["TIME"])
        self.imudata["ADXL_AX"] = np.append(self.imudata["ADXL_AX"], imudata["ADXL_AX"])
        self.imudata["ADXL_AY"] = np.append(self.imudata["ADXL_AY"], imudata["ADXL_AY"])
        self.imudata["ADXL_AZ"] = np.append(self.imudata["ADXL_AZ"], imudata["ADXL_AZ"])
        self.imudata["NANO33_WX"] = np.append(self.imudata["NANO33_WX"], imudata["NANO33_WX"])
        self.imudata["NANO33_WY"] = np.append(self.imudata["NANO33_WY"], imudata["NANO33_WY"])
        self.imudata["NANO33_WZ"] = np.append(self.imudata["NANO33_WZ"], imudata["NANO33_WZ"])
        # print( self.imudata["TIME"])
        if len(self.imudata["TIME"]) > 1000:
            self.imudata["TIME"] = self.imudata["TIME"][self.act.arrayNum:-1]
            self.imudata["ADXL_AX"] = self.imudata["ADXL_AX"][self.act.arrayNum:-1]
            self.imudata["ADXL_AY"] = self.imudata["ADXL_AY"][self.act.arrayNum:-1]
            self.imudata["ADXL_AZ"] = self.imudata["ADXL_AZ"][self.act.arrayNum:-1]
            self.imudata["NANO33_WX"] = self.imudata["NANO33_WX"][self.act.arrayNum:-1]
            self.imudata["NANO33_WY"] = self.imudata["NANO33_WY"][self.act.arrayNum:-1]
            self.imudata["NANO33_WZ"] = self.imudata["NANO33_WZ"][self.act.arrayNum:-1]
        t2 = time.perf_counter()
        debug_info = "MAIN: ," + str(input_buf) + ", " + str(round((t2 - t0) * 1000, 5)) + ", " \
                     + str(round((t1 - t0) * 1000, 5)) + ", " + str(round((t2 - t1) * 1000, 5))
        cmn.print_debug(debug_info, self.__debug)

        data = [imudata["TIME"], imudata["NANO33_WX"], imudata["NANO33_WY"], imudata["NANO33_WZ"]
            , imudata["ADXL_AX"], imudata["ADXL_AY"], imudata["ADXL_AZ"]]
        data_fmt = "%.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f"
        cmn.saveData2File(self.__isFileImuOpen, data, data_fmt, self.__FileImu_fd)
        self.plotdata(self.imudata)
        # print(len(self.imudata["TIME"]))

    def plotdata(self, imudata):
        self.top.plot1.ax2.setData(imudata["TIME"], imudata["NANO33_WZ"])
        self.top.plot2.ax.setData(imudata["ADXL_AX"])
        self.top.plot3.ax.setData(imudata["ADXL_AY"])
        self.top.plot4.ax.setData(imudata["ADXL_AZ"])
        self.top.plot5.ax.setData(imudata["NANO33_WX"])
        self.top.plot6.ax.setData(imudata["NANO33_WY"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = mainWindow(debug_en=False)
    main.show()
    app.exec_()
