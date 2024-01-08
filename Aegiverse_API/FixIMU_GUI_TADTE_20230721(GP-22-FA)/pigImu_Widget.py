""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

from PyQt5.QtWidgets import *
import sys
from myLib.myGui.graph import *
from myLib.myGui.mygui_serial import *
from myLib.myGui.myLabel import *
from myLib.myGui.myLineEdit import *
from myLib.myGui.myCheckBox import *
from myLib.myGui.myRadioButton import *
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from myLib.myGui.pig_menu_manager import pig_menu_manager


class pigImuWidget(QWidget):

    def __init__(self):
        super(pigImuWidget, self).__init__()
        self.initUI()

    def initUI(self):
        #self.usb = usbConnect()
        self.usb = usbConnect_auto_v2()
        self.read_bt = QPushButton("read")
        self.read_bt.setEnabled(False)
        self.stop_bt = QPushButton("stop")
        self.stop_bt.setEnabled(False)
        self.save_block = dataSaveBlock("save data")
        self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_SP10")
        self.buffer_lb = displayOneBlock('Buffer Size')
        self.pd_temp_lb = displayOneBlock('PD Temp.')
        self.data_rate_lb = displayOneBlock('Data Rate')
        self.logo_lb = logo('./aegiverse_logo_bk.jpg')
        self.kal_filter_rb = QRadioButton('Kalman Filter')
        self.plot1_showWz_cb = checkBoxBlock_2('Wz', 'pig', 'mems')
        self.gpstime_lb = displayOneBlock('Date (GPS Date in UTC)', label_size=8)
        self.plot1_unit_rb = radioButtonBlock_2('Unit', 'dph', 'dps')
        self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG_WZ VS MEMS_WZ")
        self.plot2 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [g]")
        self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [g]")
        self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_WX [DPS]")
        self.plot6 = pgGraph_1(color=(255, 0, 0), title="MEMS_WY [DPS]")

        layout = QGridLayout()
        layout.addWidget(self.usb.layout(), 0, 0, 1, 4)
        layout.addWidget(self.read_bt, 0, 5, 1, 1)
        layout.addWidget(self.stop_bt, 0, 6, 1, 1)
        #layout.addWidget(self.save_block, 0, 10, 1, 3)
        layout.addWidget(self.para_block, 1, 10, 1, 3)
        layout.addWidget(self.buffer_lb, 1, 4, 1, 1)
        layout.addWidget(self.pd_temp_lb, 1, 5, 1, 1)
        layout.addWidget(self.data_rate_lb, 1, 6, 1, 2)
        layout.addWidget(self.logo_lb, 0, 13, 2, 7)
        layout.addWidget(self.kal_filter_rb, 0, 4, 1, 1)
        layout.addWidget(self.plot1, 2, 0, 10, 10)
        layout.addWidget(self.plot1_showWz_cb, 1, 2, 1, 2)
        layout.addWidget(self.plot1_unit_rb, 1, 0, 1, 2)
        layout.addWidget(self.plot2, 2, 10, 2, 10)
        layout.addWidget(self.plot3, 4, 10, 2, 10)
        layout.addWidget(self.plot4, 6, 10, 2, 10)
        layout.addWidget(self.plot5, 8, 10, 2, 10)
        layout.addWidget(self.plot6, 10, 10, 2, 10)
        layout.addWidget(self.gpstime_lb, 0, 10, 1, 3)

        self.setLayout(layout)

    def setBtnEnable(self, en):
        self.read_bt.setEnabled(en)
        self.stop_bt.setEnabled(not en)  # 20230712 修改

from myLib.myGui.myTabWidget import *

class pigImuWidget_v2(QWidget):

    def __init__(self):
        super(pigImuWidget_v2, self).__init__()
        self.initUI()

    def initUI(self):
        #self.usb = usbConnect()
        self.usb = usbConnect_auto_v2()
        self.read_bt = QPushButton("read")
        self.read_bt.setEnabled(False)
        self.stop_bt = QPushButton("stop")
        self.stop_bt.setEnabled(False)
        self.save_block = dataSaveBlock("save data")
        self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_SP10")
        self.buffer_lb = displayOneBlock('Buffer Size')
        self.pd_temp_lb = displayOneBlock('PD Temp.')
        self.data_rate_lb = displayOneBlock('Data Rate')
        self.logo_lb = logo('./aegiverse_logo_bk.jpg')
        self.kal_filter_rb = QRadioButton('Kalman Filter')
        self.plot1_showWz_cb = checkBoxBlock_2('Wz', 'pig', 'mems')
        self.gpstime_lb = displayOneBlock('Date (GPS Date in UTC)', label_size=8)
        self.plot1_unit_rb = radioButtonBlock_2('Unit', 'dph', 'dps')

        # TabWidget
        self.tabwidget_show = tabwidget_v1()
        self.tabwidget_show_posture = self.tabwidget_show.tabwidget_posture("姿態展示")
        # self.tabwidget_show.initUI()
        self.tabwidget_show.tabwidget_plot("六軸線性圖", self.plot_put_on_the_tabwidget())
        # self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG_WZ VS MEMS_WZ")
        # self.plot2 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        # self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [g]")
        # self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [g]")
        # self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_WX [DPS]")
        # self.plot6 = pgGraph_1(color=(255, 0, 0), title="MEMS_WY [DPS]")

        layout = QGridLayout()
        layout.addWidget(self.usb.layout(), 0, 0, 1, 4)
        layout.addWidget(self.read_bt, 0, 5, 1, 1)
        layout.addWidget(self.stop_bt, 0, 6, 1, 1)
        #layout.addWidget(self.save_block, 0, 10, 1, 3)
        layout.addWidget(self.para_block, 1, 10, 1, 3)
        layout.addWidget(self.buffer_lb, 1, 4, 1, 1)
        layout.addWidget(self.pd_temp_lb, 1, 5, 1, 1)
        layout.addWidget(self.data_rate_lb, 1, 6, 1, 2)
        layout.addWidget(self.logo_lb, 0, 13, 2, 7)
        layout.addWidget(self.kal_filter_rb, 0, 4, 1, 1)
        # layout.addWidget(self.plot1, 2, 0, 10, 10)
        layout.addWidget(self.tabwidget_show, 2, 0, 10, 20)
        layout.addWidget(self.plot1_showWz_cb, 1, 2, 1, 2)
        layout.addWidget(self.plot1_unit_rb, 1, 0, 1, 2)
        # layout.addWidget(self.plot2, 2, 10, 2, 10)
        # layout.addWidget(self.plot3, 4, 10, 2, 10)
        # layout.addWidget(self.plot4, 6, 10, 2, 10)
        # layout.addWidget(self.plot5, 8, 10, 2, 10)
        # layout.addWidget(self.plot6, 10, 10, 2, 10)
        layout.addWidget(self.gpstime_lb, 0, 10, 1, 3)

        self.setLayout(layout)

    def plot_put_on_the_tabwidget(self):
        self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG_WZ VS MEMS_WZ") #0605修改
        self.plot1 = pgGraph_1_2(color1="w", color2="r", title="MEMS_WZ")
        self.plot2 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [g]")
        self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [g]")
        self.plot5 = pgGraph_1(color=(255, 0, 0), title="FOG_WX [DPS]")
        self.plot6 = pgGraph_1(color=(255, 0, 0), title="FOG_WY [DPS]")

        plot_layout = QGridLayout()
        plot_layout.addWidget(self.plot1, 0, 0, 10, 10)
        plot_layout.addWidget(self.plot2, 0, 10, 2, 10)
        plot_layout.addWidget(self.plot3, 2, 10, 2, 10)
        plot_layout.addWidget(self.plot4, 4, 10, 2, 10)
        plot_layout.addWidget(self.plot5, 6, 10, 2, 10)
        plot_layout.addWidget(self.plot6, 8, 10, 2, 10)
        return plot_layout

    def setBtnEnable(self, en):
        self.read_bt.setEnabled(en)
        self.stop_bt.setEnabled(not en)  # 20230712 修改


class pigImuWidget_Tab(QWidget):

    def __init__(self):
        super(pigImuWidget_Tab, self).__init__()
        self.initUI()

    def initUI(self):
        #self.usb = usbConnect()
        self.usb = usbConnect_auto_v2()
        self.read_bt = QPushButton("read")
        self.read_bt.setEnabled(False)
        self.read_bt.setMinimumSize(80, 50)
        self.read_bt.setFont(QFont('Arial', 10))
        self.stop_bt = QPushButton("stop")
        self.stop_bt.setEnabled(False)
        self.stop_bt.setMinimumSize(80, 50)
        self.stop_bt.setFont(QFont('Arial', 10))
        self.save_block = dataSaveBlock("save data")
        self.para_block = lineEditBlock(name='parameter configuration file', le_name="parameters_G03") # 之前設置的parameters_SP10
        self.buffer_lb = displayOneBlock('Buffer Size')
        self.pd_temp_lb = displayOneBlock('PD Temp Z-Axis.')
        self.pdX_temp_lb = displayOneBlock('PD Temp X-Axis.')
        self.pdY_temp_lb = displayOneBlock('PD Temp Y-Axis.')
        self.data_rate_lb = displayOneBlock('Data Rate')
        self.logo_lb = logo('./aegiverse_logo_bk_2.png')
        self.kal_filter_rb = QRadioButton('Kalman Filter')
        self.kal_filter_rb.setChecked(True)
        self.plot1_showWz_cb = checkBoxBlock_2('Wz', 'pig', 'mems')
        self.gpstime_lb = displayOneBlock('Date (GPS Date in UTC)', label_size=8)
        self.plot1_unit_rb = radioButtonBlock_2('Unit', 'dph', 'dps')

        self.satellite = displayOneBlock("GPS and GLONASS and BeiDou")
        self.vbox_kf_status = displayOneBlock("KF Status")
        self.vbox_pos_quality = displayOneBlock("Pos Quality")
        self.vbox_vel_quality = displayOneBlock("Vel Quality")
        self.vbox_Velocity = displayOneBlock("Velocity")
        self.vbox_Vertical_Vel = displayOneBlock("Vertical_Vel")
        self.vbox_Heading_KF = displayOneBlock("Heading_KF")

        # TabWidget
        self.tabwidget_show = tabwidget_v1()
        self.tabwidget_show.tabwidget_plot("六軸線性圖", self.plot_put_on_the_tabwidget())
        #self.tabwidget_show_posture = self.tabwidget_show.tabwidget_posture("姿態展示")
        # self.tabwidget_show.initUI()
        # self.plot1 = pgGraph_1_2(color1="w", color2="r", title="FOG_WZ VS MEMS_WZ")
        # self.plot2 = pgGraph_1(color=(255, 0, 0), title="MEMS_AX [g]")
        # self.plot3 = pgGraph_1(color=(255, 0, 0), title="MEMS_AY [g]")
        # self.plot4 = pgGraph_1(color=(255, 0, 0), title="MEMS_AZ [g]")
        # self.plot5 = pgGraph_1(color=(255, 0, 0), title="MEMS_WX [DPS]")
        # self.plot6 = pgGraph_1(color=(255, 0, 0), title="MEMS_WY [DPS]")

        layout = QGridLayout()
        layout.addWidget(self.usb.layout(), 0, 0, 1, 5)
        layout.addWidget(self.read_bt, 0, 7, 1, 1)
        layout.addWidget(self.stop_bt, 0, 8, 1, 1)
        layout.addWidget(self.save_block, 0, 10, 1, 3)
        layout.addWidget(self.para_block, 0, 13, 1, 4)
        layout.addWidget(self.buffer_lb, 1, 0, 1, 2)
        # layout.addWidget(self.pd_temp_lb, 1, 5, 1, 1)
        layout.addWidget(self.data_rate_lb, 1, 2, 1, 2)
        layout.addWidget(self.logo_lb, 0, 17, 1, 3)
        layout.addWidget(self.kal_filter_rb, 0, 5, 1, 2)
        layout.addWidget(self.pd_temp_lb, 1, 4, 1, 1)
        layout.addWidget(self.pdX_temp_lb, 1, 5, 1, 1)
        layout.addWidget(self.pdY_temp_lb, 1, 6, 1, 1)
        layout.addWidget(self.satellite, 1, 7, 1, 3)
        layout.addWidget(self.vbox_kf_status, 1, 10, 1, 1)
        layout.addWidget(self.vbox_pos_quality, 1, 11, 1, 1)
        layout.addWidget(self.vbox_vel_quality, 1, 12, 1, 1)
        layout.addWidget(self.vbox_Velocity, 1, 13, 1, 1)
        layout.addWidget(self.vbox_Vertical_Vel, 1, 14, 1, 1)
        layout.addWidget(self.vbox_Heading_KF, 1, 15, 1, 1)
        # layout.addWidget(self.plot1, 2, 0, 10, 10)
        layout.addWidget(self.tabwidget_show, 2, 0, 10, 20)
        # layout.addWidget(self.plot1_showWz_cb, 1, 2, 1, 2)
        # layout.addWidget(self.plot1_unit_rb, 1, 0, 1, 2)

        self.setLayout(layout)

    def plot_put_on_the_tabwidget(self):
        #self.plot1 = pgGraph_1_2(color1="w", color2="r") #0605修改
        #self.plot1 = pgGraph_1_2(color1="w", color2="r", title="MEMS_WZ")
        self.plot_AFI_W = pgGraph_1_3(color1 = "w", color2 = "r", color3 = "y", linename1 = "WX", linename2 = "WY", linename3 = "WZ", title = "AFI___WX:white, WY:red, WZ:yellow, unit: DPS")
        self.plot_AFI_A = pgGraph_1_3(color1 = "w", color2 = "r", color3 = "y", linename1 = "AX", linename2 = "AY", linename3 = "AZ", title = "AFI___AX:white, AY:red, AZ:yellow, unit: m/s\u00B2")

        self.plot_KVH_W = pgGraph_1_3(color1 = "w", color2 = "r", color3 = "y", linename1 = "WX", linename2 = "WY", linename3 = "WZ", title = "KVH___WX:white, WY:red, WZ:yellow")
        self.plot_KVH_A = pgGraph_1_3(color1 = "w", color2 = "r", color3 = "y", linename1 = "AX", linename2 = "AY", linename3 = "AZ", title = "KVH___AX:white, AY:red, AZ:yellow")

        # self.plot_vbox_vel = pgGraph_vbox_2(color1="w", color2="r", title="white：，red：Vertical_Ver")
        # self.plot_vbox_vel = pgGraph_1_W(color=(255, 0, 0), title="Velocity")
        # self.plot_vbox_ver = pgGraph_1_W(color=(255, 0, 0), title="Vertical_Ver")

        self.plot_vbox_latLong = pgGraph_1_W(color='w', title="VBOX Track")

        # 畫圖會顯示的資訊
        # Info_Item = QHBoxLayout()
        # Info_Item.addWidget(self.plot1_showWz_cb)
        # Info_Item.addWidget(self.plot1_unit_rb)
        # Info_Item.addWidget(self.buffer_lb)
        # Info_Item.addWidget(self.pd_temp_lb)
        # Info_Item.addWidget(self.data_rate_lb)

        plot_layout = QGridLayout()

        plot_layout.addWidget(self.plot_AFI_W, 0, 0, 6, 6)
        plot_layout.addWidget(self.plot_AFI_A, 6, 0, 6, 6)
        # plot_layout.addWidget(self.plot1_showWz_cb, 0, 0, 1, 5)
        # plot_layout.addWidget(self.plot1_unit_rb, 0, 5, 1, 5)

        plot_layout.addWidget(self.plot_KVH_W, 0, 6, 6, 6)
        plot_layout.addWidget(self.plot_KVH_A, 6, 6, 6, 6)

        # plot_layout.addWidget(self.plot_vbox_vel, 0, 12, 12, 10)
        # plot_layout.addWidget(self.plot_vbox_vel, 0, 12, 3, 10)
        # plot_layout.addWidget(self.plot_vbox_ver, 3, 12, 3, 10)
        plot_layout.addWidget(self.plot_vbox_latLong, 0, 12, 12, 10)
        # plot_layout.addWidget(self.pd_temp_lb, 0, 12, 1, 1)
        # plot_layout.addWidget(self.pdX_temp_lb, 0, 13, 1, 1)
        # plot_layout.addWidget(self.pdY_temp_lb, 0, 14, 1, 1)
        # plot_layout.addWidget(self.data_rate_lb, 0, 16, 1, 4)
        return plot_layout

    def setBtnEnable(self, en):
        self.read_bt.setEnabled(en)
        self.stop_bt.setEnabled(not en)  # 20230712 修改

    def autoDetect_setBtnEnable(self, en):
        self.read_bt.setEnabled(en)
        self.stop_bt.setEnabled(en)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #w = pigImuWidget()
    w = pigImuWidget_Tab()

    w.show()
    app.exec_()
