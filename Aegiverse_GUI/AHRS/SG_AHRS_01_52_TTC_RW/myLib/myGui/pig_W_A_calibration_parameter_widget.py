import struct

from PySide6 import QtCore
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
        self.intiUI()
        self.linkFunction()
        self.keyIsNotExist = False

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

        spring = QSpacerItem(15, 35, QSizePolicy.Minimum, QSizePolicy.Expanding)
        Angular_velocity_Layout.addItem(spring)
        OneWidget.setLayout(Angular_velocity_Layout)

        self.dump_Btn = QPushButton("dump")
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
        self.W1_1.le.editingFinished.connect(self.Send_G11_CMD)
        self.W1_2.le.editingFinished.connect(self.Send_G12_CMD)
        self.W1_3.le.editingFinished.connect(self.Send_G13_CMD)
        self.W2_1.le.editingFinished.connect(self.Send_G21_CMD)
        self.W2_2.le.editingFinished.connect(self.Send_G22_CMD)
        self.W2_3.le.editingFinished.connect(self.Send_G23_CMD)
        self.W3_1.le.editingFinished.connect(self.Send_G31_CMD)
        self.W3_2.le.editingFinished.connect(self.Send_G32_CMD)
        self.W3_3.le.editingFinished.connect(self.Send_G33_CMD)
        self.Wx.le.editingFinished.connect(self.Send_GX_CMD)
        self.Wy.le.editingFinished.connect(self.Send_GY_CMD)
        self.Wz.le.editingFinished.connect(self.Send_GZ_CMD)
        self.A1_1.le.editingFinished.connect(self.Send_A11_CMD)
        self.A1_2.le.editingFinished.connect(self.Send_A12_CMD)
        self.A1_3.le.editingFinished.connect(self.Send_A13_CMD)
        self.A2_1.le.editingFinished.connect(self.Send_A21_CMD)
        self.A2_2.le.editingFinished.connect(self.Send_A22_CMD)
        self.A2_3.le.editingFinished.connect(self.Send_A23_CMD)
        self.A3_1.le.editingFinished.connect(self.Send_A31_CMD)
        self.A3_2.le.editingFinished.connect(self.Send_A32_CMD)
        self.A3_3.le.editingFinished.connect(self.Send_A33_CMD)
        self.Ax.le.editingFinished.connect(self.Send_AX_CMD)
        self.Ay.le.editingFinished.connect(self.Send_AY_CMD)
        self.Az.le.editingFinished.connect(self.Send_AZ_CMD)

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
        self.loadMisalignmentFile_Btn.clicked.connect(self.loadCSVandWriteMisalignment)

    def dump_cali_parameter(self):
        self.__act.flushInputBuffer()
        initVal = self.__act.dump_cali_parameters(2)
        print(initVal)
        self.set_init_val(initVal)

    # 跳下一頁
    def NextToTheSecondPG(self):
        self.stackView_one.setCurrentIndex(1)

    # 回上一頁
    def PreviousToTheFirstPG(self):
        self.stackView_one.setCurrentIndex(0)

    def selectcontrolchangecolor(self, control):
        control.setStyleSheet('background-color: yellow')

    def controlChangeBackgorundColor(self):
        for control_item in self.findChildren(QWidget):
            # 如果是輸入框，會將外觀重置
            if isinstance(control_item, QLineEdit):
                control_item.setStyleSheet("")

    def checkKeyExist(self, para, key):
        val = para.get(str(key))
        if val == None:
            self.keyIsNotExist= True
            return None
        return val

    def keyExistOrNotMes(self):
        if self.keyIsNotExist:
            mesbox = QMessageBox(self)
            mesbox.warning(self, "load CSV數據有不存在的狀況", "請確認使用的CSV檔案內容標題是否有問題。")

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
        self.keyExistOrNotMes()
        self.keyIsNotExist=False

    def loadCSVandWriteMisalignment(self):
        options= QFileDialog.Option()
        filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", "All Files (*);;", options=options)
        if filename != "":
            misalignmentData = cmn.loadCSVFile(filename)
            biasVal = misalignmentData["Bias"]
            RVal = misalignmentData.iloc[0:5, 2:5]

            self.W1_1.le.setText(f'{RVal.iloc[0, 0]:.10f}'.rstrip('0').rstrip('.'))
            self.W1_2.le.setText(f'{RVal.iloc[0, 1]:.10f}'.rstrip('0').rstrip('.'))
            self.W1_3.le.setText(f'{RVal.iloc[0, 2]:.10f}'.rstrip('0').rstrip('.'))
            self.W2_1.le.setText(f'{RVal.iloc[1, 0]:.10f}'.rstrip('0').rstrip('.'))
            self.W2_2.le.setText(f'{RVal.iloc[1, 1]:.10f}'.rstrip('0').rstrip('.'))
            self.W2_3.le.setText(f'{RVal.iloc[1, 2]:.10f}'.rstrip('0').rstrip('.'))
            self.W3_1.le.setText(f'{RVal.iloc[2, 0]:.10f}'.rstrip('0').rstrip('.'))

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

    # 將輸入至edit控制項中的數值轉為整數
    def Send_G11_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W1_1.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G11, value[0], 1)

    def Send_G12_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W1_2.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G12, value[0], 1)

    def Send_G13_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W1_3.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G13, value[0], 1)

    def Send_G21_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W2_1.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G21, value[0], 1)

    def Send_G22_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W2_2.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G22, value[0], 1)

    def Send_G23_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W2_3.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G23, value[0], 1)

    def Send_G31_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W3_1.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G31, value[0], 1)

    def Send_G32_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W3_2.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G32, value[0], 1)

    def Send_G33_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.W3_3.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_G33, value[0], 1)

    def Send_GX_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.Wx.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_GX, value[0], 1)

    def Send_GY_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.Wy.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_GY, value[0], 1)

    def Send_GZ_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.Wz.le.text())))
        self.__act.writeImuCmd(CMD_Gyro_GZ, value[0], 1)

    def Send_A11_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A1_1.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A11, value[0], 1)

    def Send_A12_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A1_2.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A12, value[0], 1)

    def Send_A13_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A1_3.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A13, value[0], 1)

    def Send_A21_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A2_1.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A21, value[0], 1)

    def Send_A22_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A2_2.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A22, value[0], 1)

    def Send_A23_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A2_3.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A23, value[0], 1)

    def Send_A31_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A3_1.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A31, value[0], 1)

    def Send_A32_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A3_2.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A32, value[0], 1)

    def Send_A33_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.A3_3.le.text())))
        self.__act.writeImuCmd(CMD_Accele_A33, value[0], 1)

    def Send_AX_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.Ax.le.text())))
        self.__act.writeImuCmd(CMD_Accele_AX, value[0], 1)

    def Send_AY_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.Ay.le.text())))
        self.__act.writeImuCmd(CMD_Accele_AY, value[0], 1)

    def Send_AZ_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', float(self.Az.le.text())))
        self.__act.writeImuCmd(CMD_Accele_AZ, value[0], 1)
        print("send AZ")


if __name__ == "__main__":
    app = QApplication([])
    win = pig_calibration_widget("act")
    win.show()
    app.exec_()
