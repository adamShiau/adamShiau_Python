""" ####### log stuff creation, always on the top ########  """
import ast
import builtins
import datetime
import logging

import pandas

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """


import struct

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QDoubleValidator, Qt
from PySide6.QtWidgets import QGroupBox, QStackedWidget, QGridLayout, QApplication, QVBoxLayout, QWidget, QPushButton, \
    QSpacerItem, QSizePolicy, QHBoxLayout, QFileDialog, QMessageBox, QFrame

from myLib.myGui.mygui_serial import editBlock
from myLib import common as cmn


CMD_Gyro_G11 = 63
CMD_Gyro_G12 = 64
CMD_Gyro_G13 = 65
CMD_Gyro_G21 = 66
CMD_Gyro_G22 = 67
CMD_Gyro_G23 = 68
CMD_Gyro_G31 = 69
CMD_Gyro_G32 = 70
CMD_Gyro_G33 = 71
CMD_Gyro_GX = 60
CMD_Gyro_GY = 61
CMD_Gyro_GZ = 62
CMD_Accele_A11 = 51
CMD_Accele_A12 = 52
CMD_Accele_A13 = 53
CMD_Accele_A21 = 54
CMD_Accele_A22 = 55
CMD_Accele_A23 = 56
CMD_Accele_A31 = 57
CMD_Accele_A32 = 58
CMD_Accele_A33 = 59
CMD_Accele_AX = 48
CMD_Accele_AY = 49
CMD_Accele_AZ = 50

INIT_PARAMETERS = {
    "0": 0, "1": 0, "2": 0, "3": 9.8, "4": 0, "5": 0, "6": 0, "7": 9.8, "8": 0, "9": 0, "10": 0,
    "11": 9.8, "12": 0, "13": 0, "14": 0, "15": 1, "16": 0, "17": 0, "18": 0, "19": 1, "20": 0, "21": 0,
    "22": 0, "23": 1
}

class pig_calibration_widget(QGroupBox):
    def __init__(self, act, dataFile, dataFileName):
        super(pig_calibration_widget, self).__init__()
        self.setWindowTitle("IMU Misalignment Calibrtion")
        self.__act = act
        self.__file = dataFile
        self.filename = dataFileName
        self.dumpTrigerState = None
        self.keyIsNotExist = False
        self.__modifiedItem = set()
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
        self.Wx = editBlock("Bias WX")
        self.Wy = editBlock("Bias WY")
        self.Wz = editBlock("Bias WZ")

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
        Angular_velocity_Layout.addWidget(R_GroupBox)
        Angular_velocity_Layout.addWidget(b_GroupBox)
        Angular_velocity_Layout.addWidget(nextPage, alignment=QtCore.Qt.AlignRight)

        # self.dump_Btn = QPushButton("dump")
        # self.dump_Btn.setFixedWidth(150)
        # self.Update_Btn = QPushButton("Update")
        # self.Update_Btn.setFixedWidth(150)
        # self.loadMisalignmentFile = QPushButton("Load Misalignment File")
        # self.loadMisalignmentFile.setFixedWidth(150)
        #
        # BtnHorizontal = QHBoxLayout()
        # BtnHorizontal.addWidget(self.dump_Btn)
        # BtnHorizontal.addWidget(self.Update_Btn)
        # BtnHorizontal.addWidget(self.loadMisalignmentFile)

        spring = QSpacerItem(15, 35, QSizePolicy.Minimum, QSizePolicy.Expanding)
        Angular_velocity_Layout.addItem(spring)
        #Angular_velocity_Layout.insertLayout(4, BtnHorizontal)
        OneWidget.setLayout(Angular_velocity_Layout)

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
        acceleration_Layout.addWidget(acceleration_R_Group)
        acceleration_Layout.addWidget(acceleration_b_Group)
        acceleration_Layout.addWidget(PreviousPage)
        accelerationSpring = QSpacerItem(15, 35, QSizePolicy.Minimum, QSizePolicy.Expanding)
        acceleration_Layout.addItem(accelerationSpring)
        TwoWidget.setLayout(acceleration_Layout)

        setting_frame = QFrame()
        setting_frame.setStyleSheet('''QFrame {
                                               background-color: rgba(0, 0, 0, 192);
                                               border: 2px solid rgba(0, 0, 0, 32);
                                               border-radius: 10px;                                            
                                                }''')
        self.dump_Btn = QPushButton("Dump")
        self.dump_Btn.setFixedHeight(30)
        self.setBtnStyle(self.dump_Btn)
        self.init_para_btn = QPushButton("Init Para")
        self.init_para_btn.setFixedHeight(30)
        self.setBtnStyle(self.init_para_btn)
        self.Update_Btn = QPushButton("Update")
        self.Update_Btn.setFixedHeight(30)
        self.Update_Btn.setObjectName("UDBtn")
        self.setBtnStyle(self.Update_Btn)
        self.Update_Btn.setDisabled(True)
        self.loadMisalignmentFile_Gyro = QPushButton("Load Gyro File")
        self.loadMisalignmentFile_Gyro.setFixedHeight(30)
        self.setBtnStyle(self.loadMisalignmentFile_Gyro)
        self.loadMisalignmentFile_Acce = QPushButton("Load Acceleration File")
        self.loadMisalignmentFile_Acce.setFixedHeight(30)
        self.setBtnStyle(self.loadMisalignmentFile_Acce)
        self.export_Btn = QPushButton("Export")
        self.export_Btn.setFixedHeight(30)
        self.setBtnStyle(self.export_Btn)
        self.import_Btn = QPushButton("Import")
        self.import_Btn.setFixedHeight(30)
        self.setBtnStyle(self.import_Btn)

        BtnHorizontal = QVBoxLayout()
        BtnHorizontal.setAlignment(Qt.AlignTop)
        BtnHorizontal.setSpacing(5)
        BtnHorizontal.setContentsMargins(0, 0, 0, 0)
        BtnHorizontal.addWidget(self.dump_Btn)
        BtnHorizontal.addWidget(self.init_para_btn)
        BtnHorizontal.addWidget(self.Update_Btn)
        BtnHorizontal.addWidget(self.loadMisalignmentFile_Gyro)
        BtnHorizontal.addWidget(self.loadMisalignmentFile_Acce)
        BtnHorizontal.addWidget(self.export_Btn)
        BtnHorizontal.addWidget(self.import_Btn)
        setting_frame.setLayout(BtnHorizontal)

        self.stackView_one.addWidget(OneWidget)
        self.stackView_one.addWidget(TwoWidget)
        nextPage.clicked.connect(self.NextToTheSecondPG)
        PreviousPage.clicked.connect(self.PreviousToTheFirstPG)
        All_Layout.addWidget(setting_frame, 1)
        All_Layout.addWidget(self.stackView_one, 3)

        #All_Layout.addWidget(stackView_one)
        self.setLayout(All_Layout)

    def linkFunction(self):
        self.W1_1.le.textChanged.connect(self.Send_G11_CMD)
        self.W1_2.le.textChanged.connect(self.Send_G12_CMD)
        self.W1_3.le.textChanged.connect(self.Send_G13_CMD)
        self.W2_1.le.textChanged.connect(self.Send_G21_CMD)
        self.W2_2.le.textChanged.connect(self.Send_G22_CMD)
        self.W2_3.le.textChanged.connect(self.Send_G23_CMD)
        self.W3_1.le.textChanged.connect(self.Send_G31_CMD)
        self.W3_2.le.textChanged.connect(self.Send_G32_CMD)
        self.W3_3.le.textChanged.connect(self.Send_G33_CMD)
        self.Wx.le.textChanged.connect(self.Send_GX_CMD)
        self.Wy.le.textChanged.connect(self.Send_GY_CMD)
        self.Wz.le.textChanged.connect(self.Send_GZ_CMD)
        self.A1_1.le.textChanged.connect(self.Send_A11_CMD)
        self.A1_2.le.textChanged.connect(self.Send_A12_CMD)
        self.A1_3.le.textChanged.connect(self.Send_A13_CMD)
        self.A2_1.le.textChanged.connect(self.Send_A21_CMD)
        self.A2_2.le.textChanged.connect(self.Send_A22_CMD)
        self.A2_3.le.textChanged.connect(self.Send_A23_CMD)
        self.A3_1.le.textChanged.connect(self.Send_A31_CMD)
        self.A3_2.le.textChanged.connect(self.Send_A32_CMD)
        self.A3_3.le.textChanged.connect(self.Send_A33_CMD)
        self.Ax.le.textChanged.connect(self.Send_AX_CMD)
        self.Ay.le.textChanged.connect(self.Send_AY_CMD)
        self.Az.le.textChanged.connect(self.Send_AZ_CMD)

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
        self.init_para_btn.clicked.connect(self.init_para)
        # self.Update_Btn.clicked.connect(self.update_changevalue)
        self.loadMisalignmentFile_Gyro.clicked.connect(lambda: self.loadCSVandWriteMisalignment("G"))
        self.loadMisalignmentFile_Acce.clicked.connect(lambda: self.loadCSVandWriteMisalignment("A"))
        self.export_Btn.clicked.connect(self.exportTXTDump)
        self.import_Btn.clicked.connect(self.importTXT)

    def setBtnStyle(self, item):
        if item.objectName() == "UDBtn":
            item.setStyleSheet('''QPushButton {
                                               background-color: rgba(213, 216, 220, 68);
                                               border: 0px;
                                               border-radius: 10px;
                                               color: rgb(229, 231, 233);
                                               }''')
        else:
            item.setStyleSheet('''QPushButton {
                                               background-color: rgba(0, 0, 0, 32);
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

    def dump_cali_parameter(self):
        self.__act.flushInputBuffer("None")
        initVal = self.__act.dump_cali_parameters(2)
        # print(initVal)
        if isinstance(initVal, (list, dict)):
            self.set_init_val(initVal)
            self.dumpTrigerState = True
        elif type(initVal) == bool:
            self.mesboxProcess("warning", "Error occurred while in dump", "Please check if the device has power.")


    # 跳下一頁
    def NextToTheSecondPG(self):
        self.stackView_one.setCurrentIndex(1)

    # 回上一頁
    def PreviousToTheFirstPG(self):
        self.stackView_one.setCurrentIndex(0)

    def checkKeyExist(self, para, key):
        try:
            val = para.get(str(key))
        except TypeError:
            return 0
        except Exception:
            return 0

        # 用於load csv檔案的判斷
        if "Bias" in para:
            try:
                for idx, biasVal in val.items():
                    if not isinstance(biasVal, float):
                        return 0
            except Exception as e:
                logger.error(f"{e} ,檢查key是否存在的判斷出現錯誤。")
                self.keyIsNotExist = True
                return 0
        if not isinstance(val, pandas.Series):
            # 用於dump參數時的判斷
            if val == None:
                self.keyIsNotExist = True
                return 0
            # key值存在，但沒有值或是值為nan
            if val == "nan" or val == '':
                logger.info("參數值為空的狀況，故回傳數值0代替空值。")
                return 0
        return val

    def keyExistOrNotMes(self, name):
        if self.keyIsNotExist:
            if name == "misalignment參數值":
                self.mesboxProcess("warning", name+"有不存在的狀況", "在取misalignment參數值的狀況時，因設備版號為舊的部分\n"
                                                                                "，而GUI為最新版本未有撈取舊參數值，所以訊息通知使用\n"
                                                                                "者有些參數若為0或空值，代表該參數在舊版本的設備中未\n"
                                                                                "使用，因此撈取不到正確的參數。")
            elif name == "匯入參數值":
                self.mesboxProcess("warning", name+ "有不存在的狀況", "請確認匯入的參數，是否有key值設定錯誤，或是不存在的狀況發生。")
            else:
                self.mesboxProcess("warning", name+"有不存在的狀況", "請確認使用的CSV檔案內容與標題是否有問題。")

            self.keyIsNotExist = False


    # 點擊dump可以讀取儀器的數據
    def set_init_val(self, para):
        self.W1_1.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "15"))))
        self.W1_2.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "16"))))
        self.W1_3.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "17"))))
        self.W2_1.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "18"))))
        self.W2_2.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "19"))))
        self.W2_3.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "20"))))
        self.W3_1.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "21"))))
        self.W3_2.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "22"))))
        self.W3_3.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "23"))))
        self.Wx.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "12"))))
        self.Wy.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "13"))))
        self.Wz.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "14"))))
        self.A1_1.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "3"))))
        self.A1_2.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "4"))))
        self.A1_3.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "5"))))
        self.A2_1.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "6"))))
        self.A2_2.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "7"))))
        self.A2_3.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "8"))))
        self.A3_1.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "9"))))
        self.A3_2.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "10"))))
        self.A3_3.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "11"))))
        self.Ax.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "0"))))
        self.Ay.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "1"))))
        self.Az.le.setText(str(self.ieee754_int_to_float(self.checkKeyExist(para, "2"))))
        if not __name__ == "__main__":
            self.controlchangewhite()
            self.keyExistOrNotMes("misalignment參數值")
            self.__modifiedItem.clear()

    def selectcontrolchangecolor(self, control, send_item_func):
        control.setStyleSheet('background-color: yellow')

        clickBtnObj = self.sender()
        if not hasattr(clickBtnObj, 'text') or clickBtnObj.text() == "Load Misalignment File" or clickBtnObj.text() == "Import":
            if send_item_func not in self.__modifiedItem and send_item_func != None:
                self.__modifiedItem.add(send_item_func)


    def controlchangewhite(self):
        self.W1_1.le.setStyleSheet('background-color: white')
        self.W1_2.le.setStyleSheet('background-color: white')
        self.W1_3.le.setStyleSheet('background-color: white')
        self.W2_1.le.setStyleSheet('background-color: white')
        self.W2_2.le.setStyleSheet('background-color: white')
        self.W2_3.le.setStyleSheet('background-color: white')
        self.W3_1.le.setStyleSheet('background-color: white')
        self.W3_2.le.setStyleSheet('background-color: white')
        self.W3_3.le.setStyleSheet('background-color: white')
        self.Wx.le.setStyleSheet('background-color: white')
        self.Wy.le.setStyleSheet('background-color: white')
        self.Wz.le.setStyleSheet('background-color: white')
        self.A1_1.le.setStyleSheet('background-color: white')
        self.A1_2.le.setStyleSheet('background-color: white')
        self.A1_3.le.setStyleSheet('background-color: white')
        self.A2_1.le.setStyleSheet('background-color: white')
        self.A2_2.le.setStyleSheet('background-color: white')
        self.A2_3.le.setStyleSheet('background-color: white')
        self.A3_1.le.setStyleSheet('background-color: white')
        self.A3_2.le.setStyleSheet('background-color: white')
        self.A3_3.le.setStyleSheet('background-color: white')
        self.Ax.le.setStyleSheet('background-color: white')
        self.Ay.le.setStyleSheet('background-color: white')
        self.Az.le.setStyleSheet('background-color: white')

    def update_changevalue(self):
        mesbox = QtWidgets.QMessageBox()
        mesbox.setIcon(QMessageBox.Question)
        mesbox.setWindowTitle("確認是否要更新數值")
        mesbox.setText("請確認被選中的控制項都是要修改數值嗎?")
        mesbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mesbox.setDefaultButton(QtWidgets.QMessageBox.Yes)
        mes_result = mesbox.exec_()

        if mes_result == QMessageBox.Yes:
            self.updatelink()
            #print("Yes")
        elif mes_result == QMessageBox.No:
            pass


    def updatelink(self):
        if self.dumpTrigerState == True:
            for itemFunc in self.__modifiedItem:
                itemFunc()
            # self.Send_G11_CMD()
            # self.Send_G12_CMD()
            # self.Send_G13_CMD()
            # self.Send_G21_CMD()
            # self.Send_G22_CMD()
            # self.Send_G23_CMD()
            # self.Send_G31_CMD()
            # self.Send_G32_CMD()
            # self.Send_G33_CMD()
            # self.Send_GX_CMD()
            # self.Send_GY_CMD()
            # self.Send_GZ_CMD()
            # self.Send_A11_CMD()
            # self.Send_A12_CMD()
            # self.Send_A13_CMD()
            # self.Send_A21_CMD()
            # self.Send_A22_CMD()
            # self.Send_A23_CMD()
            # self.Send_A31_CMD()
            # self.Send_A32_CMD()
            # self.Send_A33_CMD()
            # self.Send_AX_CMD()
            # self.Send_AY_CMD()
            # self.Send_AZ_CMD()
            # 將背景顏色轉回白色
            self.controlchangewhite()
            self.__modifiedItem.clear()
            self.mesboxProcess("info", "更新完成資訊", "已更新完所有被修改的設備參數。")
            self.keyExistOrNotMes("misalignment參數值")
        else:
            self.mesboxProcess("warning", "update按鈕錯誤警告", "請確認是否已經點擊過dump按鈕，數據已經顯示於畫面中了。")


    # 讀取CSV的檔案，並填至控制項中
    def loadCSVandWriteMisalignment(self, load_mode):
        # 根據模式判斷是要將參數load到哪邊
        misalignment_list = {'G': [self.W1_1, self.W1_2, self.W1_3, self.W2_1, self.W2_2, self.W2_3, self.W3_1, self.W3_2, self.W3_3],
                'A': [self.A1_1, self.A1_2, self.A1_3, self.A2_1, self.A2_2, self.A2_3, self.A3_1, self.A3_2, self.A3_3]}

        if self.dumpTrigerState == True:
            options = QFileDialog.Option()
            filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", "All Files (*);;", options=options)
            if filename != "":
                misalignmentData = cmn.loadCSVFile(filename)
                # print(misalignmentData)
                biasVal = self.checkKeyExist(misalignmentData, "Bias")

                if isinstance(biasVal, pandas.Series):
                    try:
                        RVal = misalignmentData.iloc[0:5, 2:5]
                        #print(RVal.iloc[0,0])

                        misalignment_list[load_mode][0].le.setText(f'{RVal.iloc[0,0]:.10f}'.rstrip('0').rstrip('.'))
                        misalignment_list[load_mode][1].le.setText(f'{RVal.iloc[0,1]:.10f}'.rstrip('0').rstrip('.'))
                        misalignment_list[load_mode][2].le.setText(f'{RVal.iloc[0,2]:.10f}'.rstrip('0').rstrip('.'))
                        misalignment_list[load_mode][3].le.setText(f'{RVal.iloc[1, 0]:.10f}'.rstrip('0').rstrip('.'))
                        misalignment_list[load_mode][4].le.setText(f'{RVal.iloc[1, 1]:.10f}'.rstrip('0').rstrip('.'))
                        misalignment_list[load_mode][5].le.setText(f'{RVal.iloc[1, 2]:.10f}'.rstrip('0').rstrip('.'))
                        misalignment_list[load_mode][6].le.setText(f'{RVal.iloc[2, 0]:.10f}'.rstrip('0').rstrip('.'))
                        misalignment_list[load_mode][7].le.setText(f'{RVal.iloc[2, 1]:.10f}'.rstrip('0').rstrip('.'))
                        misalignment_list[load_mode][8].le.setText(f'{RVal.iloc[2, 2]:.10f}'.rstrip('0').rstrip('.'))

                        if load_mode == 'A':
                            self.Ax.le.setText(f'{biasVal[0]:.10f}'.rstrip('0').rstrip('.'))
                            self.Ay.le.setText(f'{biasVal[1]:.10f}'.rstrip('0').rstrip('.'))
                            self.Az.le.setText(f'{biasVal[2]:.10f}'.rstrip('0').rstrip('.'))
                    except Exception:
                        logger.error("載入CSV數據的功能出現錯誤。")
                        self.keyIsNotExist = True
                else:
                    self.keyIsNotExist = True
                self.keyExistOrNotMes("load Bias CSV")
                self.keyIsNotExist = False
        else:
            self.mesboxProcess("warning", "請確認是否已dump了", "請確認是否已經點擊過dump按鈕，或是已經將設備的\n參數回填至控制項中，且數據已經顯示於畫面。"
                                                                "\n若還沒執行dump，將無法執行此Load File功能。")


    def exportTXTDump(self):
        if self.dumpTrigerState == True:
            try:
                time_now = datetime.datetime.now()
                timeFormat = time_now.strftime("%Y%m%d%h%M")

                self.__act.flushInputBuffer("None")
                SN = self.__act.dump_SN_parameters(3)
                if "發生參數值為空的狀況" == SN:
                    dumpParaSN = "參數值為空，請確認設備是否以上電。"
                else:
                    dumpParaSN = SN
                # 移除\x00的相關字元，避免出現embedded null character錯誤
                SNPara = dumpParaSN.replace("\x00", "")

                # 先開啟要寫入的檔案
                self.__file.name = str(SNPara) + "_misalignment_" + timeFormat + "_" + self.filename + ".txt"
                self.__file.open(True)

                #參數key值的對照表
                self.__file.write_dump("參數key值對照表 ->")
                self.__file.write_dump(f"0= AX      , 1= AY      , 2= AZ        , 3= A11     , 4= A12     , 5= A13,\n"
                                       f"  6= A21     , 7= A22    , 8= A23      , 9= A31     , 10= A32   , 11= A33,\n"
                                       f"  12= GX     , 13= GY    , 14= GZ     , 15= G11   , 16= G12   , 17= G13,\n"
                                       f"  18= G21   , 19= G22   , 20= G23   , 21= G31   , 22= G32   , 23= G33")

                # 撈取設備中的misalignment參數
                self.__act.flushInputBuffer("None")
                initVal = self.__act.dump_cali_parameters(2)
                self.__file.write_dump("misalignment參數")
                if isinstance(initVal, dict):
                    self.__file.write_dump(initVal)
                else:
                    self.__file.write_dump("None")
                self.mesboxProcess("info", "匯出功能", "匯出功能正常執行，儲存misalignment的參數至txt檔案。")
            except Exception as e:
                logger.error(f"匯出參數的過程中發生錯誤 - {e}")
                self.mesboxProcess("warning", "匯出功能發生錯誤", "請確認匯出過程發生的錯誤，並進行修改。")
            if self.__file.isOpenFile:
                self.__file.close()
        else:
            self.mesboxProcess("warning", "請確認是否已dump了", "請確認是否已經點擊過dump按鈕，或是已經將設備的\n參數回填至控制項中，且數據已經顯示於畫面。"
                                                                "\n若還沒執行dump，將無法執行此匯出功能。")

    def importTXT(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", "All Files (*);;", options=options)

        misalignment_para = False
        if filename != "":
            if self.dumpTrigerState == True:
                try:
                    with open(filename, "r", encoding='utf-8') as f:
                        content = f.readline()
                        while content:
                            # 處理字串，使用取代功能將'#'與'\n'，取代為空值
                            content_replace = content.replace("#", "").replace("\n", "")
                            if misalignment_para and self.strCovertibleToDict(content_replace):
                                self.dumpTrigerState = True
                                self.set_init_val(ast.literal_eval(content_replace))
                                # self.updatelink()
                                misalignment_para = False

                            if content_replace == "misalignment參數":
                                misalignment_para = True
                            content = f.readline()
                            continue
                except Exception as e:
                    logger.error(f"匯入參數的過程中發生錯誤 - {e}")
                    self.mesboxProcess("warning", "匯入功能發生錯誤", "請確認匯入過程發生的錯誤，並進行修改。")
                finally:
                    self.keyExistOrNotMes("匯入參數值")
            else:
                self.mesboxProcess("warning", "請確認是否已dump了", "請確認是否已經點擊過dump按鈕，或是已經將設備的\n參數回填至控制項中，且數據已經顯示於畫面。"
                                                                    "\n若還沒執行dump，將無法執行此匯入功能。")

    def strCovertibleToDict(self, content):
        try:
            result = ast.literal_eval(content)
            return isinstance(result, dict)
        except (ValueError, SyntaxError):
            return False


    def init_para(self):
        """Apply INIT_PARAMETERS sequentially; each setText triggers Send_*_CMD."""
        if getattr(self, "_init_in_progress", False):
            return
        self._init_in_progress = True

        # Disable buttons during init
        self.init_para_btn.setEnabled(False)
        self.dump_Btn.setEnabled(False)
        self.export_Btn.setEnabled(False)
        self.import_Btn.setEnabled(False)
        self.loadMisalignmentFile_Gyro.setEnabled(False)
        self.loadMisalignmentFile_Acce.setEnabled(False)

        self._init_ops = self._build_init_ops_from_INIT_PARAMETERS()
        self._init_total = len(self._init_ops)
        self._init_idx = 0

        self._init_progress = QtWidgets.QProgressDialog("Updating calibration parameters…", None, 0, self._init_total, self)
        self._init_progress.setWindowTitle("Init Para")
        self._init_progress.setWindowModality(QtCore.Qt.WindowModal)
        self._init_progress.setAutoClose(True)
        self._init_progress.setAutoReset(True)
        self._init_progress.show()

        QtCore.QTimer.singleShot(0, self._init_para_step)

    def _init_para_step(self):
        if self._init_idx >= self._init_total:
            self._init_progress.setValue(self._init_total)
            self._init_progress.close()

            # Re-enable buttons
            self.init_para_btn.setEnabled(True)
            self.dump_Btn.setEnabled(True)
            self.export_Btn.setEnabled(True)
            self.import_Btn.setEnabled(True)
            self.loadMisalignmentFile_Gyro.setEnabled(True)
            self.loadMisalignmentFile_Acce.setEnabled(True)

            self._init_in_progress = False
            self.mesboxProcess("info", "Init Para", "Calibration parameters updated.")
            return

        setter, value = self._init_ops[self._init_idx]
        try:
            setter(value)
        except Exception as e:
            logger.error(f"init_para failed at idx={self._init_idx}: {e}")

        self._init_idx += 1
        self._init_progress.setValue(self._init_idx)

        # Wait 50ms between each parameter update
        QtCore.QTimer.singleShot(50, self._init_para_step)

    def _build_init_ops_from_INIT_PARAMETERS(self):
        """Build ordered setter ops based on the key table (see exportTXTDump)."""
        p = INIT_PARAMETERS

        def gv(k, default=0):
            return p.get(str(k), default)

        def fmt(x):
            try:
                return f"{float(x):.10f}".rstrip("0").rstrip(".")
            except Exception:
                return str(x)

        ops = []
        # Accelerometer b
        ops.append((self.Ax.le.setText, fmt(gv(0))))
        ops.append((self.Ay.le.setText, fmt(gv(1))))
        ops.append((self.Az.le.setText, fmt(gv(2))))

        # Accelerometer R
        ops.append((self.A1_1.le.setText, fmt(gv(3))))
        ops.append((self.A1_2.le.setText, fmt(gv(4))))
        ops.append((self.A1_3.le.setText, fmt(gv(5))))
        ops.append((self.A2_1.le.setText, fmt(gv(6))))
        ops.append((self.A2_2.le.setText, fmt(gv(7))))
        ops.append((self.A2_3.le.setText, fmt(gv(8))))
        ops.append((self.A3_1.le.setText, fmt(gv(9))))
        ops.append((self.A3_2.le.setText, fmt(gv(10))))
        ops.append((self.A3_3.le.setText, fmt(gv(11))))

        # Gyro b
        ops.append((self.Wx.le.setText, fmt(gv(12))))
        ops.append((self.Wy.le.setText, fmt(gv(13))))
        ops.append((self.Wz.le.setText, fmt(gv(14))))

        # Gyro R
        ops.append((self.W1_1.le.setText, fmt(gv(15))))
        ops.append((self.W1_2.le.setText, fmt(gv(16))))
        ops.append((self.W1_3.le.setText, fmt(gv(17))))
        ops.append((self.W2_1.le.setText, fmt(gv(18))))
        ops.append((self.W2_2.le.setText, fmt(gv(19))))
        ops.append((self.W2_3.le.setText, fmt(gv(20))))
        ops.append((self.W3_1.le.setText, fmt(gv(21))))
        ops.append((self.W3_2.le.setText, fmt(gv(22))))
        ops.append((self.W3_3.le.setText, fmt(gv(23))))

        return ops


    def mesboxProcess(self, status, title, content):
        mesbox = QMessageBox(self)
        if status == "warning":
            mesbox.warning(self, title, content)
        if status == "info":
            mesbox.information(self, title, content)

    def ieee754_int_to_float(self, int_value: int) -> float:
        """
        Convert a 32-bit IEEE-754 integer representation to a float.

        :param int_value: Integer representation of IEEE-754 float (32-bit)
        :return: Converted floating-point number
        """
        # Pack integer as 4 bytes, then unpack as a float
        # return round(struct.unpack('!f', struct.pack('!I', int_value))[0], 7)
        typeChange = 0
        buttonObj = self.sender()
        if buttonObj.text()  == "Import":
            if isinstance(int_value, float):
                typeChange = int_value
            elif isinstance(int_value, int):
                if len(str(abs(int_value))) == 10 or len(str(abs(int_value))) >= 8:
                    try:
                        typeChange = round(struct.unpack('!f', struct.pack('!i', int_value))[0], 7)
                    except Exception as e:
                        logger.error(f"{e} - 使用Import匯入數據，在數據型態轉換的過程發生錯誤。")
                        self.mesboxProcess('warning', '整數轉換單精度浮點數發生錯誤',
                                           '轉換過程中因帶入的整數，不符合此轉換的方法，所以發生錯誤。')
                else:
                    typeChange = int_value
            # if len(str(int_value)) == 10 or len(str(abs(int_value))) >= 8:
            #     try:
            #         typeChange = round(struct.unpack('!f', struct.pack('!i', int_value))[0], 7)
            #     except Exception as e:
            #         logger.error(f"{e} - 使用Import匯入數據，在數據型態轉換的過程發生錯誤。")
            #         self.mesboxProcess('warning', '整數轉換單精度浮點數發生錯誤', '轉換過程中因帶入的整數，不符合此轉換的方法，所以發生錯誤。')
            # else:
            #     typeChange = int_value
        else:
            try:
                typeChange = round(struct.unpack('!f', struct.pack('!i', int_value))[0], 7)
            except Exception as e:
                logger.error(f"{e} - 使用dump撈取數據，在數據型態轉換的過程發生錯誤。")
                self.mesboxProcess('warning', '整數轉換單精度浮點數發生錯誤',
                                   '轉換過程中因帶入的整數，不符合此轉換的方法，所以發生錯誤。')
        return typeChange


    # 將輸入至edit控制項中的數值轉為整數
    def Send_G11_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W1_1.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G11, value[0], 4)

    def Send_G12_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W1_2.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G12, value[0], 4)

    def Send_G13_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W1_3.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G13, value[0], 4)

    def Send_G21_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W2_1.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G21, value[0], 4)

    def Send_G22_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W2_2.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G22, value[0], 4)

    def Send_G23_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W2_3.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G23, value[0], 4)

    def Send_G31_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W3_1.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G31, value[0], 4)

    def Send_G32_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W3_2.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G32, value[0], 4)

    def Send_G33_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W3_3.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_G33, value[0], 4)

    def Send_GX_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Wx.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_GX, value[0], 4)
        print("Send_GX_CMD: ", value[0])

    def Send_GY_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Wy.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_GY, value[0], 4)

    def Send_GZ_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Wz.le.text()))))
        self.__act.writeImuCmd(CMD_Gyro_GZ, value[0], 4)
        print("Send_GZ_CMD: ", value[0])

    def Send_A11_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A1_1.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A11, value[0], 4)

    def Send_A12_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A1_2.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A12, value[0], 4)

    def Send_A13_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A1_3.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A13, value[0], 4)

    def Send_A21_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A2_1.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A21, value[0], 4)

    def Send_A22_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A2_2.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A22, value[0], 4)

    def Send_A23_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A2_3.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A23, value[0], 4)

    def Send_A31_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A3_1.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A31, value[0], 4)

    def Send_A32_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A3_2.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A32, value[0], 4)

    def Send_A33_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A3_3.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_A33, value[0], 4)

    def Send_AX_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Ax.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_AX, value[0], 4)

    def Send_AY_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Ay.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_AY, value[0], 4)

    def Send_AZ_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Az.le.text()))))
        self.__act.writeImuCmd(CMD_Accele_AZ, value[0], 4)
        print("send AZ")


# ==========================================
#   UI 預覽測試區塊 (Layout Preview Only)
# ==========================================
if __name__ == "__main__":
    import sys
    import os
    from PySide6.QtWidgets import QApplication

    # 1. 修正路徑 (讓 Python 找得到根目錄的 myLib)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))
    sys.path.append(root_dir)


    # 2. 定義 Dummy Reader (防止報錯)
    class DummyReader:
        def __getattr__(self, name):
            # 無論 UI 呼叫什麼方法 (如 flushInputBuffer)，都回傳這個空函式
            def method(*args, **kwargs):
                print(f"[UI Preview] Method called: {name}")
                return 0

            return method


    app = QApplication(sys.argv)

    # 3. 啟動視窗
    # 注意：這個 Widget 的 __init__ 通常是 (act, parent, filename)
    # 我們傳入 DummyReader, None, 和一個假檔名
    window = pig_calibration_widget(DummyReader(), None, "test_cali_config")

    window.show()
    sys.exit(app.exec())
