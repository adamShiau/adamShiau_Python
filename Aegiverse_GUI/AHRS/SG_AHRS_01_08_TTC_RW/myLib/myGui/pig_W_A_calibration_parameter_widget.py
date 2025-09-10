""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import os
import pandas
from pyqtgraph.colors import palette

from myLib.logProcess import logProcess

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
# logger = logging.getLogger(logger_name + '.' + __name__)
ExternalName_log = __name__
if os.getenv('verNum') == str(True) :
    ExternalName_log = "misa_logger"

logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import struct
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QDoubleValidator, Qt
from PySide6.QtWidgets import QGroupBox, QStackedWidget, QGridLayout, QApplication, QVBoxLayout, QWidget, QPushButton, \
    QSpacerItem, QSizePolicy, QMessageBox, QFrame, QHBoxLayout, QFileDialog, QLineEdit

from myLib.myGui.mygui_serial import editBlock
from myLib import common as cmn

CMD_Gyro_G11 = 120
CMD_Gyro_G12 = 121
CMD_Gyro_G13 = 122
CMD_Gyro_G21 = 123
CMD_Gyro_G22 = 124
CMD_Gyro_G23 = 125
CMD_Gyro_G31 = 126
CMD_Gyro_G32 = 127
CMD_Gyro_G33 = 128
CMD_Gyro_GX = 117
CMD_Gyro_GY = 118
CMD_Gyro_GZ = 119
CMD_Accele_A11 = 108
CMD_Accele_A12 = 109
CMD_Accele_A13 = 110
CMD_Accele_A21 = 111
CMD_Accele_A22 = 112
CMD_Accele_A23 = 113
CMD_Accele_A31 = 114
CMD_Accele_A32 = 115
CMD_Accele_A33 = 116
CMD_Accele_AX = 105
CMD_Accele_AY = 106
CMD_Accele_AZ = 107

class pig_calibration_widget(QGroupBox):
    def __init__(self, act):
        super(pig_calibration_widget, self).__init__()
        self.setWindowTitle("IMU Misalignment Calibrtion")
        #self.resize(520, 430)
        self.__act = act
        self.keyIsNotExist = False
        self.dumpTrigerState = None
        self.__modifiedItem = set()

        # 紀錄offsset的設備內部值
        self.__device_GXC = None
        self.__device_GYC = None
        self.__device_GZC = None
        self.__device_AXC = None
        self.__device_AYC = None
        self.__device_AZC = None

        self.intiUI()
        self.linkFunction()


    def intiUI(self):
        All_Layout = QHBoxLayout()
        self.stackView_one = QStackedWidget()
        Angular_velocity_Layout = QVBoxLayout()
        acceleration_Layout = QVBoxLayout()
        OneWidget = QWidget()
        TwoWidget = QWidget()

        # first Page
        R_GroupBox = QGroupBox("Gyro R")
        R_GroupBox_layout = QGridLayout()
        R_GroupBox.setLayout(R_GroupBox_layout)
        self.W1_1 = editBlock("G11")
        self.W1_2 = editBlock("G12")
        self.W1_3 = editBlock("G13")
        self.W2_1 = editBlock("G21")
        self.W2_2 = editBlock("G22")
        self.W2_3 = editBlock("G23")
        self.W3_1 = editBlock("G31")
        self.W3_2 = editBlock("G32")
        self.W3_3 = editBlock("G33")
        self.W1_1.setFixedWidth(150)
        self.W1_2.setFixedWidth(150)
        self.W1_3.setFixedWidth(150)
        nextPage = QPushButton("next page -->")
        nextPage.setFixedSize(120, 25)

        b_GroupBox = QGroupBox("Gyro b")
        b_GroupBox_layout = QGridLayout()
        b_GroupBox.setLayout(b_GroupBox_layout)
        self.Wx = editBlock("GX")
        self.Wy = editBlock("GY")
        self.Wz = editBlock("GZ")

        self.GxC = editBlock("GXC")
        self.GyC = editBlock("GYC")
        self.GzC = editBlock("GZC")

        R_GroupBox_layout.addWidget(self.W1_1, 0, 0, 1, 2)
        R_GroupBox_layout.addWidget(self.W1_2, 0, 2, 1, 2)
        R_GroupBox_layout.addWidget(self.W1_3, 0, 4, 1, 2)
        R_GroupBox_layout.addWidget(self.W2_1, 1, 0, 1, 2)
        R_GroupBox_layout.addWidget(self.W2_2, 1, 2, 1, 2)
        R_GroupBox_layout.addWidget(self.W2_3, 1, 4, 1, 2)
        R_GroupBox_layout.addWidget(self.W3_1, 2, 0, 1, 2)
        R_GroupBox_layout.addWidget(self.W3_2, 2, 2, 1, 2)
        R_GroupBox_layout.addWidget(self.W3_3, 2, 4, 1, 2)
        b_GroupBox_layout.addWidget(self.Wx, 0, 0, 1, 2)
        b_GroupBox_layout.addWidget(self.Wy, 0, 2, 1, 2)
        b_GroupBox_layout.addWidget(self.Wz, 0, 4, 1, 2)
        b_GroupBox_layout.addWidget(self.GxC, 1, 0, 1, 2)
        b_GroupBox_layout.addWidget(self.GyC, 1, 2, 1, 2)
        b_GroupBox_layout.addWidget(self.GzC, 1, 4, 1, 2)
        Angular_velocity_Layout.addWidget(R_GroupBox)
        Angular_velocity_Layout.addWidget(b_GroupBox)
        Angular_velocity_Layout.addWidget(nextPage, alignment=QtCore.Qt.AlignRight)

        spring = QSpacerItem(15, 35, QSizePolicy.Minimum, QSizePolicy.Expanding)
        Angular_velocity_Layout.addItem(spring)
        OneWidget.setLayout(Angular_velocity_Layout)

        self.dump_Btn = QPushButton("Dump")
        self.dump_Btn.setFixedHeight(30)
        self.setBtnStyle(self.dump_Btn)
        self.Update_Btn = QPushButton("Update")
        self.Update_Btn.setFixedHeight(30)
        self.setBtnStyle(self.Update_Btn)
        self.loadMisalignmentFile_Btn = QPushButton("Load Misalignment File")
        self.loadMisalignmentFile_Btn.setFixedHeight(30)
        self.setBtnStyle(self.loadMisalignmentFile_Btn)

        setting_frame = QFrame()
        setting_frame.setStyleSheet('''QFrame {
                                            background-color: rgba(0, 0, 0, 255);
                                            border: 2px solid rgba(0, 0, 0, 32);
                                            border-radius: 10px;
                                        }''')
        BtnHorizontal = QVBoxLayout()
        BtnHorizontal.setAlignment(Qt.AlignTop)
        BtnHorizontal.setSpacing(5)
        BtnHorizontal.setContentsMargins(0, 0, 0, 0)
        BtnHorizontal.addWidget(self.dump_Btn)
        BtnHorizontal.addWidget(self.Update_Btn)
        BtnHorizontal.addWidget(self.loadMisalignmentFile_Btn)
        setting_frame.setLayout(BtnHorizontal)

        # Second Page
        acceleration_R_Group = QGroupBox("Accelerometer R")
        acceleration_R_GroupBox_layout = QGridLayout()
        acceleration_R_Group.setLayout(acceleration_R_GroupBox_layout)
        self.A1_1 = editBlock("A11")
        self.A1_2 = editBlock("A12")
        self.A1_3 = editBlock("A13")
        self.A2_1 = editBlock("A21")
        self.A2_2 = editBlock("A22")
        self.A2_3 = editBlock("A23")
        self.A3_1 = editBlock("A31")
        self.A3_2 = editBlock("A32")
        self.A3_3 = editBlock("A33")
        self.A1_1.setFixedWidth(150)
        self.A1_2.setFixedWidth(150)
        self.A1_3.setFixedWidth(150)
        PreviousPage = QPushButton("<-- previous page")
        PreviousPage.setFixedSize(120, 25)

        acceleration_b_Group = QGroupBox("Accelerometer b")
        acceleration_b_Group_layout = QGridLayout()
        acceleration_b_Group.setLayout(acceleration_b_Group_layout)
        self.Ax = editBlock("AX")
        self.Ay = editBlock("AY")
        self.Az = editBlock("AZ")

        self.AxC = editBlock("AXC")
        self.AyC = editBlock("AYC")
        self.AzC = editBlock("AZC")

        acceleration_R_GroupBox_layout.addWidget(self.A1_1, 0, 0, 1, 2)
        acceleration_R_GroupBox_layout.addWidget(self.A1_2, 0, 2, 1, 2)
        acceleration_R_GroupBox_layout.addWidget(self.A1_3, 0, 4, 1, 2)
        acceleration_R_GroupBox_layout.addWidget(self.A2_1, 1, 0, 1, 2)
        acceleration_R_GroupBox_layout.addWidget(self.A2_2, 1, 2, 1, 2)
        acceleration_R_GroupBox_layout.addWidget(self.A2_3, 1, 4, 1, 2)
        acceleration_R_GroupBox_layout.addWidget(self.A3_1, 2, 0, 1, 2)
        acceleration_R_GroupBox_layout.addWidget(self.A3_2, 2, 2, 1, 2)
        acceleration_R_GroupBox_layout.addWidget(self.A3_3, 2, 4, 1, 2)
        acceleration_b_Group_layout.addWidget(self.Ax, 0, 0, 1, 2)
        acceleration_b_Group_layout.addWidget(self.Ay, 0, 2, 1, 2)
        acceleration_b_Group_layout.addWidget(self.Az, 0, 4, 1, 2)
        acceleration_b_Group_layout.addWidget(self.AxC, 1, 0, 1, 2)
        acceleration_b_Group_layout.addWidget(self.AyC, 1, 2, 1, 2)
        acceleration_b_Group_layout.addWidget(self.AzC, 1, 4, 1, 2)
        acceleration_Layout.addWidget(acceleration_R_Group)
        acceleration_Layout.addWidget(acceleration_b_Group)
        acceleration_Layout.addWidget(PreviousPage)
        accelerationSpring = QSpacerItem(15, 35, QSizePolicy.Minimum, QSizePolicy.Expanding)
        acceleration_Layout.addItem(accelerationSpring)
        TwoWidget.setLayout(acceleration_Layout)

        self.stackView_one.addWidget(OneWidget)
        self.stackView_one.addWidget(TwoWidget)
        nextPage.clicked.connect(self.NextToTheSecondPG)
        PreviousPage.clicked.connect(self.PreviousToTheFirstPG)
        All_Layout.addWidget(setting_frame, 1)
        All_Layout.addWidget(self.stackView_one, 3)

        #All_Layout.addWidget(stackView_one)
        self.setLayout(All_Layout)

    def setBtnStyle(self, item):
        item.setStyleSheet('''QPushButton {
                                            background-color: rgba(0, 0, 0, 192);
                                            border: 0px;
                                            border-radius: 10px;
                                            color: rgb(255, 255, 255);
                                            }
                            QPushButton::hover {
                                                background-color: rgb(255, 255, 255);
                                                color: rgb(0, 0, 0);
                                                border: 0px;
                                                border-radius: 10px;
                                                }''')


    def linkFunction(self):
        # self.W1_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W1_1.le, self.Send_G11_CMD))
        # self.W1_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W1_2.le, self.Send_G12_CMD))
        # self.W1_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W1_3.le, self.Send_G13_CMD))
        # self.W2_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W2_1.le, self.Send_G21_CMD))
        # self.W2_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W2_2.le, self.Send_G22_CMD))
        # self.W2_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W2_3.le, self.Send_G23_CMD))
        # self.W3_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W3_1.le, self.Send_G31_CMD))
        # self.W3_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W3_2.le, self.Send_G32_CMD))
        # self.W3_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W3_3.le, self.Send_G33_CMD))
        # self.Wx.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Wx.le, self.Send_GX_CMD))
        # self.Wy.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Wy.le, self.Send_GY_CMD))
        # self.Wz.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Wz.le, self.Send_GZ_CMD))
        # self.GxC.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.GxC.le, self.Send_GXC_CMD))
        # self.GyC.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.GyC.le, self.Send_GYC_CMD))
        # self.GzC.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.GzC.le, self.Send_GZC_CMD))
        # self.A1_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A1_1.le, self.Send_A11_CMD))
        # self.A1_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A1_2.le, self.Send_A12_CMD))
        # self.A1_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A1_3.le, self.Send_A13_CMD))
        # self.A2_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A2_1.le, self.Send_A21_CMD))
        # self.A2_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A2_2.le, self.Send_A22_CMD))
        # self.A2_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A2_3.le, self.Send_A23_CMD))
        # self.A3_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A3_1.le, self.Send_A31_CMD))
        # self.A3_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A3_2.le, self.Send_A32_CMD))
        # self.A3_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A3_3.le, self.Send_A33_CMD))
        # self.Ax.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Ax.le, self.Send_AX_CMD))
        # self.Ay.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Ay.le, self.Send_AY_CMD))
        # self.Az.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Az.le, self.Send_AZ_CMD))
        # self.AxC.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.AxC.le, self.Send_AXC_CMD))
        # self.AyC.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.AyC.le, self.Send_AYC_CMD))
        # self.AzC.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.AzC.le, self.Send_AZC_CMD))
        # ---- W group ----
        self.W1_1.le.textChanged.connect(lambda *_: self.Send_G11_CMD())
        self.W1_2.le.textChanged.connect(lambda *_: self.Send_G12_CMD())
        self.W1_3.le.textChanged.connect(lambda *_: self.Send_G13_CMD())
        self.W2_1.le.textChanged.connect(lambda *_: self.Send_G21_CMD())
        self.W2_2.le.textChanged.connect(lambda *_: self.Send_G22_CMD())
        self.W2_3.le.textChanged.connect(lambda *_: self.Send_G23_CMD())
        self.W3_1.le.textChanged.connect(lambda *_: self.Send_G31_CMD())
        self.W3_2.le.textChanged.connect(lambda *_: self.Send_G32_CMD())
        self.W3_3.le.textChanged.connect(lambda *_: self.Send_G33_CMD())
        self.Wx.le.textChanged.connect(lambda *_: self.Send_GX_CMD())
        self.Wy.le.textChanged.connect(lambda *_: self.Send_GY_CMD())
        self.Wz.le.textChanged.connect(lambda *_: self.Send_GZ_CMD())
        self.GxC.le.textChanged.connect(lambda *_: self.Send_GXC_CMD())
        self.GyC.le.textChanged.connect(lambda *_: self.Send_GYC_CMD())
        self.GzC.le.textChanged.connect(lambda *_: self.Send_GZC_CMD())

        # ---- A group ----
        self.A1_1.le.textChanged.connect(lambda *_: self.Send_A11_CMD())
        self.A1_2.le.textChanged.connect(lambda *_: self.Send_A12_CMD())
        self.A1_3.le.textChanged.connect(lambda *_: self.Send_A13_CMD())
        self.A2_1.le.textChanged.connect(lambda *_: self.Send_A21_CMD())
        self.A2_2.le.textChanged.connect(lambda *_: self.Send_A22_CMD())
        self.A2_3.le.textChanged.connect(lambda *_: self.Send_A23_CMD())
        self.A3_1.le.textChanged.connect(lambda *_: self.Send_A31_CMD())
        self.A3_2.le.textChanged.connect(lambda *_: self.Send_A32_CMD())
        self.A3_3.le.textChanged.connect(lambda *_: self.Send_A33_CMD())
        self.Ax.le.textChanged.connect(lambda *_: self.Send_AX_CMD())
        self.Ay.le.textChanged.connect(lambda *_: self.Send_AY_CMD())
        self.Az.le.textChanged.connect(lambda *_: self.Send_AZ_CMD())
        self.AxC.le.textChanged.connect(lambda *_: self.Send_AXC_CMD())
        self.AyC.le.textChanged.connect(lambda *_: self.Send_AYC_CMD())
        self.AzC.le.textChanged.connect(lambda *_: self.Send_AZC_CMD())
        # limite_doublevalidator = QDoubleValidator()
        # limite_doublevalidator.setNotation(QDoubleValidator.StandardNotation)
        # limite_doublevalidator.setRange(-100000, 100000, 7)
        #
        # # 設定輸入值的限制
        # self.W1_1.le.setValidator(limite_doublevalidator)
        # self.W1_2.le.setValidator(limite_doublevalidator)
        # self.W1_3.le.setValidator(limite_doublevalidator)
        # self.W2_1.le.setValidator(limite_doublevalidator)
        # self.W2_2.le.setValidator(limite_doublevalidator)
        # self.W2_3.le.setValidator(limite_doublevalidator)
        # self.W3_1.le.setValidator(limite_doublevalidator)
        # self.W3_2.le.setValidator(limite_doublevalidator)
        # self.W3_3.le.setValidator(limite_doublevalidator)
        # self.Wx.le.setValidator(limite_doublevalidator)
        # self.Wy.le.setValidator(limite_doublevalidator)
        # self.Wz.le.setValidator(limite_doublevalidator)
        # # 設定輸入值的限制
        # self.A1_1.le.setValidator(limite_doublevalidator)
        # self.A1_2.le.setValidator(limite_doublevalidator)
        # self.A1_3.le.setValidator(limite_doublevalidator)
        # self.A2_1.le.setValidator(limite_doublevalidator)
        # self.A2_2.le.setValidator(limite_doublevalidator)
        # self.A2_3.le.setValidator(limite_doublevalidator)
        # self.A3_1.le.setValidator(limite_doublevalidator)
        # self.A3_2.le.setValidator(limite_doublevalidator)
        # self.A3_3.le.setValidator(limite_doublevalidator)
        # self.Ax.le.setValidator(limite_doublevalidator)
        # self.Ay.le.setValidator(limite_doublevalidator)
        # self.Az.le.setValidator(limite_doublevalidator)
        self.dump_Btn.clicked.connect(self.dump_cali_parameter)
        self.Update_Btn.clicked.connect(self.update_changevalue)
        self.loadMisalignmentFile_Btn.clicked.connect(self.loadCSVandWriteMisalignment)


    def dump_cali_parameter(self):
        self.__act.flushInputBuffer()
        initVal = self.__act.dump_cali_parameters(2)
        if isinstance(initVal, (list, dict)):
            self.dumpTrigerState = True
            self.set_init_val(initVal)
        elif type(initVal) == bool:
            self.mesboxProcess("warning", "Error occurred while in dump", "Please check if the device has power.")


    # 跳下一頁
    def NextToTheSecondPG(self):
        self.stackView_one.setCurrentIndex(1)

    # 回上一頁
    def PreviousToTheFirstPG(self):
        self.stackView_one.setCurrentIndex(0)

    def checkKeyExist(self, para, key):
        # try:
        #     val = para.get(str(key))
        # except TypeError:
        #     return 0
        # except Exception:
        #     return 0
        try:
            # 使用dump或是load file，都會先由這邊取值，再做後續判斷與處理。
            val = para.get(str(key))

            # 用於load cav檔案的判斷
            if "Bias" in para:
                for idx, biasVal in val.items():
                    if not isinstance(biasVal, float):
                        return 0
        except Exception as e:
            self.keyIsNotExist = True
            logger.error(f"{e} ,檢查key是否存在的判斷出現錯誤。")
            return 0

        if not isinstance(val, pandas.Series):
            # 用於dump參數時的判斷
            if val == None:  # 會出現None，代表該Key值找不到。
                self.keyIsNotExist = True
                return None
            if val == "nan" or val == '':
                logger.info("參數值為空的狀況，故回傳數值0代替空值。")
                return 0  # 回傳0是因為有些控制項無法顯示文字或空值的狀況
        return val

    def keyExistOrNotMes(self, name):
        if not self.__act.isRunAutoComp:
            if self.keyIsNotExist:
                if name == "misalignment參數值":
                    self.mesboxProcess("warning", name+"有不存在的狀況", "在取misalignment參數值的狀況時，因設備版號為舊的部分，\n"
                                                                                    "而GUI為最新版本未有撈取舊參數值，所以訊息通知使用者\n"
                                                                                    "有些參數若為0或空值，代表該參數在舊版本的設備中未使\n"
                                                                                    "用，因此撈取不到正確的參數。")
                else:
                    self.mesboxProcess("warning", name+"有不存在的狀況", "請確認使用的CSV檔案內容標題是否有問題。")


    # 點擊dump可以讀取儀器的數據
    def set_init_val(self, para):
        self.W1_1.le.setText(str(self.checkKeyExist(para, "G11")))
        self.W1_2.le.setText(str(self.checkKeyExist(para, "G12")))
        self.W1_3.le.setText(str(self.checkKeyExist(para, "G13")))
        self.W2_1.le.setText(str(self.checkKeyExist(para, "G21")))
        self.W2_2.le.setText(str(self.checkKeyExist(para, "G22")))
        self.W2_3.le.setText(str(self.checkKeyExist(para, "G23")))
        self.W3_1.le.setText(str(self.checkKeyExist(para, "G31")))
        self.W3_2.le.setText(str(self.checkKeyExist(para, "G32")))
        self.W3_3.le.setText(str(self.checkKeyExist(para, "G33")))
        self.Wx.le.setText(str(self.checkKeyExist(para, "GX")))
        self.Wy.le.setText(str(self.checkKeyExist(para, "GY")))
        self.Wz.le.setText(str(self.checkKeyExist(para, "GZ")))
        # 回填至介面的輸入框中
        self.GxC.le.setText("0")
        self.GyC.le.setText("0")
        self.GzC.le.setText("0")
        # 紀錄設備中的offset值
        if self.checkKeyExist(para, "GXC") == None:
            self.__device_GXC = 0
        else:
            self.__device_GXC = float(self.checkKeyExist(para, "GXC"))
        if self.checkKeyExist(para, "GYC") == None:
            self.__device_GYC = 0
        else:
            self.__device_GYC = float(self.checkKeyExist(para, "GYC"))
        if self.checkKeyExist(para, "GZC") == None:
            self.__device_GZC = 0
        else:
            self.__device_GZC = float(self.checkKeyExist(para, "GZC"))

        self.A1_1.le.setText(str(self.checkKeyExist(para, "A11")))
        self.A1_2.le.setText(str(self.checkKeyExist(para, "A12")))
        self.A1_3.le.setText(str(self.checkKeyExist(para, "A13")))
        self.A2_1.le.setText(str(self.checkKeyExist(para, "A21")))
        self.A2_2.le.setText(str(self.checkKeyExist(para, "A22")))
        self.A2_3.le.setText(str(self.checkKeyExist(para, "A23")))
        self.A3_1.le.setText(str(self.checkKeyExist(para, "A31")))
        self.A3_2.le.setText(str(self.checkKeyExist(para, "A32")))
        self.A3_3.le.setText(str(self.checkKeyExist(para, "A33")))
        self.Ax.le.setText(str(self.checkKeyExist(para, "AX")))
        self.Ay.le.setText(str(self.checkKeyExist(para, "AY")))
        self.Az.le.setText(str(self.checkKeyExist(para, "AZ")))
        # 回填至介面的輸入框中
        self.AxC.le.setText("0")
        self.AyC.le.setText("0")
        self.AzC.le.setText("0")
        # 紀錄設備中的offset值
        if self.checkKeyExist(para, "AXC") == None:
            self.__device_AXC = 0
        else:
            self.__device_AXC = float(self.checkKeyExist(para, "AXC"))
        if self.checkKeyExist(para, "AYC") == None:
            self.__device_AYC = 0
        else:
            self.__device_AYC = float(self.checkKeyExist(para, "AYC"))
        if self.checkKeyExist(para, "AZC") == None:
            self.__device_AZC = 0
        else:
            self.__device_AZC = float(self.checkKeyExist(para, "AZC"))

        if not __name__ == "__main__":
            self.controlChangeBackgorundColor()
            self.keyExistOrNotMes("misalignment參數值")
            self.keyIsNotExist = False

    def selectcontrolchangecolor(self, control, send_item_func):
        control.setStyleSheet('background-color: yellow')

        # 用於當為手動修改控制項，會執行儲存被修改的控制項，之後在更新參數只會執行有被儲存的控制項
        clickBtnObj = self.sender()
        if not hasattr(clickBtnObj, 'text') or clickBtnObj.text() == "Load Misalignment File":
            if send_item_func not in self.__modifiedItem and send_item_func != None:
                self.__modifiedItem.add(send_item_func)

                # 當有設定新的offset值，就需要更新GXC、GYC、GZC、AXC、AYC與AZC的參數值
                if control is self.GxC.le and self.Send_GX_CMD not in self.__modifiedItem:
                    self.__modifiedItem.add(self.Send_GX_CMD)
                if control == self.GyC.le and self.Send_GY_CMD not in self.__modifiedItem:
                    self.__modifiedItem.add(self.Send_GY_CMD)
                if control == self.GzC.le and self.Send_GZ_CMD not in self.__modifiedItem:
                    self.__modifiedItem.add(self.Send_GZ_CMD)
                if control == self.AxC.le and self.Send_AX_CMD not in self.__modifiedItem:
                    self.__modifiedItem.add(self.Send_AX_CMD)
                if control == self.AyC.le and self.Send_AY_CMD not in self.__modifiedItem:
                    self.__modifiedItem.add(self.Send_AY_CMD)
                if control == self.AzC.le and self.Send_AZ_CMD not in self.__modifiedItem:
                    self.__modifiedItem.add(self.Send_AZ_CMD)


    def controlChangeBackgorundColor(self):
        for control_item in self.findChildren(QWidget):
            # 如果是輸入框，會將外觀重置
            if isinstance(control_item, QLineEdit):
                control_item.setStyleSheet("")

    def update_changevalue(self):
        if not self.__act.isRunAutoComp:
            mesbox = QtWidgets.QMessageBox()
            mesbox.setIcon(QMessageBox.Question)
            mesbox.setWindowTitle("確認是否要更新數據")
            mesbox.setText("請確認被選中的控制項都是要修改數值嗎?")
            mesbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            mesbox.setDefaultButton(QtWidgets.QMessageBox.Yes)
            mes_result = mesbox.exec_()

            if mes_result == QMessageBox.Yes:
                self.updatelink()
            elif mes_result == QMessageBox.No:
                pass
        else:
            self.updatelink()

    def updatelink(self):
        if self.dumpTrigerState == True:
            for itemFunc in self.__modifiedItem:
                itemFunc()

            self.controlChangeBackgorundColor()
            self.__modifiedItem.clear()
            if not self.__act.isRunAutoComp:
                self.mesboxProcess("info", "更新完成資訊", "已更新完所有被修改的設備參數。")
            self.keyExistOrNotMes("misalignment參數值")
            self.keyIsNotExist = False
        else:
            self.mesboxProcess("warning", "update按鈕錯誤警告", "請確認是否已經點擊過dump按鈕，且數據已經顯示於畫面中了。")


    def loadCSVandWriteMisalignment(self):
        options= QFileDialog.Option()
        filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", "All Files (*);;", options=options)
        if filename != "":
            misalignmentData = cmn.loadCSVFile(filename)
            biasVal = self.checkKeyExist(misalignmentData, "Bias")

            if isinstance(biasVal, pandas.Series):
                try:
                    RVal = misalignmentData.iloc[0:5, 2:5]

                    self.W1_1.le.setText(f'{RVal.iloc[0, 0]:.10f}'.rstrip('0').rstrip('.'))
                    self.W1_2.le.setText(f'{RVal.iloc[0, 1]:.10f}'.rstrip('0').rstrip('.'))
                    self.W1_3.le.setText(f'{RVal.iloc[0, 2]:.10f}'.rstrip('0').rstrip('.'))
                    self.W2_1.le.setText(f'{RVal.iloc[1, 0]:.10f}'.rstrip('0').rstrip('.'))
                    self.W2_2.le.setText(f'{RVal.iloc[1, 1]:.10f}'.rstrip('0').rstrip('.'))
                    self.W2_3.le.setText(f'{RVal.iloc[1, 2]:.10f}'.rstrip('0').rstrip('.'))
                    self.W3_1.le.setText(f'{RVal.iloc[2, 0]:.10f}'.rstrip('0').rstrip('.'))
                    self.W3_2.le.setText(f'{RVal.iloc[2, 1]:.10f}'.rstrip('0').rstrip('.'))
                    self.W3_3.le.setText(f'{RVal.iloc[2, 2]:.10f}'.rstrip('0').rstrip('.'))

                    self.A1_1.le.setText(f'{RVal.iloc[0, 0]:.10f}'.rstrip('0').rstrip('.'))
                    self.A1_2.le.setText(f'{RVal.iloc[0, 1]:.10f}'.rstrip('0').rstrip('.'))
                    self.A1_3.le.setText(f'{RVal.iloc[0, 2]:.10f}'.rstrip('0').rstrip('.'))
                    self.A2_1.le.setText(f'{RVal.iloc[1, 0]:.10f}'.rstrip('0').rstrip('.'))
                    self.A2_2.le.setText(f'{RVal.iloc[1, 1]:.10f}'.rstrip('0').rstrip('.'))
                    self.A2_3.le.setText(f'{RVal.iloc[1, 2]:.10f}'.rstrip('0').rstrip('.'))
                    self.A3_1.le.setText(f'{RVal.iloc[2, 0]:.10f}'.rstrip('0').rstrip('.'))
                    self.A3_2.le.setText(f'{RVal.iloc[2, 1]:.10f}'.rstrip('0').rstrip('.'))
                    self.A3_3.le.setText(f'{RVal.iloc[2, 2]:.10f}'.rstrip('0').rstrip('.'))
                    self.Ax.le.setText(f'{biasVal[0]:.10f}'.rstrip('0').rstrip('.'))
                    self.Ay.le.setText(f'{biasVal[1]:.10f}'.rstrip('0').rstrip('.'))
                    self.Az.le.setText(f'{biasVal[2]:.10f}'.rstrip('0').rstrip('.'))
                except Exception as e:
                    self.keyIsNotExist = True
                    logger.error(f"{type(e).__name__}--載入CSV數據的功能出現錯誤。")
            else:
                self.keyIsNotExist = True
            self.keyExistOrNotMes("load Bias CSV")
            self.keyIsNotExist = False

    def mesboxProcess(self, status, title, content):
        mesbox = QMessageBox(self)
        if status == "warning":
            mesbox.warning(self, title, content)
        if status == "info":
            mesbox.information(self, title, content)

    # 將輸入至edit控制項中的數值轉為整數
    def Send_G11_CMD(self):
        logger.info('set G11 : %d', float(self.W1_1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W1_1.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G11, value[0], 1)

    def Send_G12_CMD(self):
        logger.info('set G12 : %d', float(self.W1_2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W1_2.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G12, value[0], 1)

    def Send_G13_CMD(self):
        logger.info('set G13 : %d', float(self.W1_3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W1_3.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G13, value[0], 1)

    def Send_G21_CMD(self):
        logger.info('set G21 : %d', float(self.W2_1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W2_1.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G21, value[0], 1)

    def Send_G22_CMD(self):
        logger.info('set G22 : %d', float(self.W2_2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W2_2.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G22, value[0], 1)

    def Send_G23_CMD(self):
        logger.info('set G23 : %d', float(self.W2_3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W2_3.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G23, value[0], 1)

    def Send_G31_CMD(self):
        logger.info('set G31 : %d', float(self.W3_1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W3_1.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G31, value[0], 1)

    def Send_G32_CMD(self):
        logger.info('set G32 : %d', float(self.W3_2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W3_2.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G32, value[0], 1)

    def Send_G33_CMD(self):
        logger.info('set G33 : %d', float(self.W3_3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.W3_3.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G33, value[0], 1)

    def Send_GX_CMD(self):
        # 最終寫入的值為輸入的值與offset相加，但offset是負號值
        GX_value = float(self.Wx.le.text()) + float(self.GxC.le.text())
        logger.info(f'set GX : {GX_value}')
        value = struct.unpack('<I', struct.pack('<f', GX_value))
        print("Send_GX_CMD: ");
        print("Gx: ", float(self.Wx.le.text()))
        print("GxC: ", float(self.GxC.le.text()))
        print("All: ", GX_value)
        self.__act.writeImuCmd(CMD_Gyro_GX, value[0], 1)

    def Send_GY_CMD(self):
        # logger.info('set GY : %d', float(self.Wy.le.text()))
        # 最終寫入的值為輸入的值與offset相加，但offset是負號值
        GY_value = float(self.Wy.le.text()) + float(self.GyC.le.text())
        logger.info(f'set GY : {GY_value}')
        value = struct.unpack('<I', struct.pack('<f', GY_value))
        self.__act.writeImuCmd(CMD_Gyro_GY, value[0], 1)

    def Send_GZ_CMD(self):
        # logger.info('set GZ : %d', float(self.Wz.le.text()))
        # 最終寫入的值為輸入的值與offset相加，但offset是負號值
        GZ_value = float(self.Wz.le.text()) + float(self.GzC.le.text())
        logger.info(f'set GZ : {GZ_value}')
        value = struct.unpack('<I', struct.pack('<f', GZ_value))
        self.__act.writeImuCmd(CMD_Gyro_GZ, value[0], 1)

    def Send_GXC_CMD(self):
        GX_offset = float(self.__device_GXC) + float(self.GxC.le.text())
        logger.info(f'set GXC : {GX_offset}')
        value = struct.unpack('<I', struct.pack('<f', GX_offset))
        # self.__act.writeImuCmd(, value[0], 1)

    def Send_GYC_CMD(self):
        GY_offset = float(self.__device_GYC) + float(self.GyC.le.text())
        logger.info(f'set GYC : {GY_offset}')
        value = struct.unpack('<I', struct.pack('<f', GY_offset))
        # self.__act.writeImuCmd(, value[0], 1)

    def Send_GZC_CMD(self):
        GZ_offset = float(self.__device_GZC) + float(self.GzC.le.text())
        logger.info(f'set GZC : {GZ_offset}')
        value = struct.unpack('<I', struct.pack('<f', GZ_offset))
        # self.__act.writeImuCmd(, value[0], 1)

    def Send_A11_CMD(self):
        logger.info('set A11 : %d', float(self.A1_1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A1_1.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A11, value[0], 1)

    def Send_A12_CMD(self):
        logger.info('set A12 : %d', float(self.A1_2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A1_2.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A12, value[0], 1)

    def Send_A13_CMD(self):
        logger.info('set A13 : %d', float(self.A1_3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A1_3.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A13, value[0], 1)

    def Send_A21_CMD(self):
        logger.info('set A21 : %d', float(self.A2_1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A2_1.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A21, value[0], 1)

    def Send_A22_CMD(self):
        logger.info('set A22 : %d', float(self.A2_2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A2_2.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A22, value[0], 1)

    def Send_A23_CMD(self):
        logger.info('set A23 : %d', float(self.A2_3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A2_3.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A23, value[0], 1)

    def Send_A31_CMD(self):
        logger.info('set A31 : %d', float(self.A3_1.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A3_1.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A31, value[0], 1)

    def Send_A32_CMD(self):
        logger.info('set A32 : %d', float(self.A3_2.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A3_2.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A32, value[0], 1)

    def Send_A33_CMD(self):
        logger.info('set A33 : %d', float(self.A3_3.le.text()))
        value = struct.unpack('<I', struct.pack('<f', float(self.A3_3.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A33, value[0], 1)

    def Send_AX_CMD(self):
        # logger.info('set AX : %d', float(self.Ax.le.text()))
        # 將AX輸入的值與offset值相加(offset為負號值，因此使用相加的方式)
        AX_value = float(self.Ax.le.text()) + float(self.AxC.le.text())
        logger.info(f'set AX : {AX_value}')
        value = struct.unpack('<I', struct.pack('<f', AX_value))
        self.__act.writeImuCmd(CMD_Accele_AX, value[0], 1)

    def Send_AY_CMD(self):
        # logger.info('set AY : %d', float(self.Ay.le.text()))
        # 將AY輸入的值與offset值相加(offset為負號值，因此使用相加的方式)
        AY_value = float(self.Ay.le.text()) + float(self.AyC.le.text())
        logger.info(f'set AY : {AY_value}')
        value = struct.unpack('<I', struct.pack('<f', AY_value))
        self.__act.writeImuCmd(CMD_Accele_AY, value[0], 1)

    def Send_AZ_CMD(self):
        # logger.info('set AZ : %d', float(self.Az.le.text()))
        # 將AZ輸入的值與offset值相加(offset為負號值，因此使用相加的方式)
        AZ_value = float(self.Az.le.text()) + float(self.AzC.le.text())
        logger.info(f'set AZ : {AZ_value}')
        value = struct.unpack('<I', struct.pack('<f', AZ_value))
        self.__act.writeImuCmd(CMD_Accele_AZ, value[0], 1)
        # print("send AZ")

    def Send_AXC_CMD(self):
        AX_offset = float(self.__device_AXC) + float(self.AxC.le.text())
        logger.info(f'set AXC : {AX_offset}')
        value = struct.unpack('<I', struct.pack('<f', float(AX_offset)))
        # self.__act.writeImuCmd(, value[0], 1)

    def Send_AYC_CMD(self):
        AY_offset = float(self.__device_AYC) + float(self.AyC.le.text())
        logger.info(f'set AYC : {AY_offset}')
        value = struct.unpack('<I', struct.pack('<f', float(AY_offset)))
        # self.__act.writeImuCmd(, value[0], 1)

    def Send_AZC_CMD(self):
        AZ_offset = float(self.__device_AZC) + float(self.AzC.le.text())
        logger.info(f'set AZC : {AZ_offset}')
        value = struct.unpack('<I', struct.pack('<f', float(AZ_offset)))
        # self.__act.writeImuCmd(, value[0], 1)


if __name__ == "__main__":
    app = QApplication([])
    win = pig_calibration_widget("act")
    win.show()
    app.exec_()
