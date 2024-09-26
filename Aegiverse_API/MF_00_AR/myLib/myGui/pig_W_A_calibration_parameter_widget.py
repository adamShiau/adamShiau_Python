import struct

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QGroupBox, QStackedWidget, QGridLayout, QApplication, QVBoxLayout, QWidget, QPushButton, \
    QSpacerItem, QSizePolicy, QHBoxLayout, QFileDialog, QMessageBox

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
        self.__act = act
        self.dumpTrigerState = None
        self.intiUI()
        self.linkFunction()

    def intiUI(self):
        All_Layout = QVBoxLayout()
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

        self.dumpBtn = QPushButton("dump")
        self.dumpBtn.setFixedWidth(150)
        self.UpdateBtn = QPushButton("Update")
        self.UpdateBtn.setFixedWidth(150)
        self.loadMisalignmentFile = QPushButton("Load Misalignment File")
        self.loadMisalignmentFile.setFixedWidth(150)

        BtnHorizontal = QHBoxLayout()
        BtnHorizontal.addWidget(self.dumpBtn)
        BtnHorizontal.addWidget(self.UpdateBtn)
        BtnHorizontal.addWidget(self.loadMisalignmentFile)

        spring = QSpacerItem(15, 35, QSizePolicy.Minimum, QSizePolicy.Expanding)
        Angular_velocity_Layout.addItem(spring)
        Angular_velocity_Layout.insertLayout(4, BtnHorizontal)
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

        self.stackView_one.addWidget(OneWidget)
        self.stackView_one.addWidget(TwoWidget)
        nextPage.clicked.connect(self.NextToTheSecondPG)
        PreviousPage.clicked.connect(self.PreviousToTheFirstPG)
        All_Layout.addWidget(self.stackView_one)

        #All_Layout.addWidget(stackView_one)
        self.setLayout(All_Layout)

    def linkFunction(self):
        self.W1_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W1_1.le))
        self.W1_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W1_2.le))
        self.W1_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W1_3.le))
        self.W2_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W2_1.le))
        self.W2_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W2_2.le))
        self.W2_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W2_3.le))
        self.W3_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W3_1.le))
        self.W3_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W3_2.le))
        self.W3_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.W3_3.le))
        self.Wx.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Wx.le))
        self.Wy.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Wy.le))
        self.Wz.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Wz.le))
        self.A1_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A1_1.le))
        self.A1_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A1_2.le))
        self.A1_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A1_3.le))
        self.A2_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A2_1.le))
        self.A2_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A2_2.le))
        self.A2_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A2_3.le))
        self.A3_1.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A3_1.le))
        self.A3_2.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A3_2.le))
        self.A3_3.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.A3_3.le))
        self.Ax.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Ax.le))
        self.Ay.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Ay.le))
        self.Az.le.textChanged.connect(lambda: self.selectcontrolchangecolor(self.Az.le))

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
        self.dumpBtn.clicked.connect(self.dump_cali_parameter)
        self.UpdateBtn.clicked.connect(self.update_changevalue)
        self.loadMisalignmentFile.clicked.connect(self.loadCSVandWriteMisalignment)

    def dump_cali_parameter(self):
        self.dumpTrigerState = True
        self.__act.flushInputBuffer("None")
        initVal = self.__act.dump_cali_parameters(2)
        print(initVal)
        self.set_init_val(initVal)

    # 跳下一頁
    def NextToTheSecondPG(self):
        self.stackView_one.setCurrentIndex(1)

    # 回上一頁
    def PreviousToTheFirstPG(self):
        self.stackView_one.setCurrentIndex(0)

    # 點擊dump可以讀取儀器的數據
    def set_init_val(self, para):
        self.W1_1.le.setText(str(float(para["G11"] * -1)))
        self.W1_2.le.setText(str(float(para["G12"] * -1)))
        self.W1_3.le.setText(str(float(para["G13"] * -1)))
        self.W2_1.le.setText(str(float(para["G21"] * -1)))
        self.W2_2.le.setText(str(float(para["G22"] * -1)))
        self.W2_3.le.setText(str(float(para["G23"] * -1)))
        self.W3_1.le.setText(str(float(para["G31"] * -1)))
        self.W3_2.le.setText(str(float(para["G32"] * -1)))
        self.W3_3.le.setText(str(float(para["G33"] * -1)))
        self.Wx.le.setText(str(float(para["GX"] * -1)))
        self.Wy.le.setText(str(float(para["GY"] * -1)))
        self.Wz.le.setText(str(float(para["GZ"] * -1)))
        self.A1_1.le.setText(str(float(para["A11"] * -1)))
        self.A1_2.le.setText(str(float(para["A12"] * -1)))
        self.A1_3.le.setText(str(float(para["A13"] * -1)))
        self.A2_1.le.setText(str(float(para["A21"] * -1)))
        self.A2_2.le.setText(str(float(para["A22"] * -1)))
        self.A2_3.le.setText(str(float(para["A23"] * -1)))
        self.A3_1.le.setText(str(float(para["A31"] * -1)))
        self.A3_2.le.setText(str(float(para["A32"] * -1)))
        self.A3_3.le.setText(str(float(para["A33"] * -1)))
        self.Ax.le.setText(str(float(para["AX"] * -1)))
        self.Ay.le.setText(str(float(para["AY"] * -1)))
        self.Az.le.setText(str(float(para["AZ"] * -1)))
        if not __name__ == "__main__":
            self.controlchangewhite()

    def selectcontrolchangecolor(self, control):
        control.setStyleSheet('background-color: yellow')

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
            print("Yes")
        elif mes_result == QMessageBox.No:
            pass


    def updatelink(self):
        if self.dumpTrigerState == True:
            self.Send_G11_CMD()
            self.Send_G12_CMD()
            self.Send_G13_CMD()
            self.Send_G21_CMD()
            self.Send_G22_CMD()
            self.Send_G23_CMD()
            self.Send_G31_CMD()
            self.Send_G32_CMD()
            self.Send_G33_CMD()
            self.Send_GX_CMD()
            self.Send_GY_CMD()
            self.Send_GZ_CMD()
            self.Send_A11_CMD()
            self.Send_A12_CMD()
            self.Send_A13_CMD()
            self.Send_A21_CMD()
            self.Send_A22_CMD()
            self.Send_A23_CMD()
            self.Send_A31_CMD()
            self.Send_A32_CMD()
            self.Send_A33_CMD()
            self.Send_AX_CMD()
            self.Send_AY_CMD()
            self.Send_AZ_CMD()
            # 將背景顏色轉回白色
            self.controlchangewhite()
        else:
            mesbox = QMessageBox(self)
            mesbox.warning(self, "update按鈕錯誤警告", "請確認是否已經點擊過dump按鈕，數據已經顯示於畫面中了。")


    # 讀取CSV的檔案，並填至控制項中
    def loadCSVandWriteMisalignment(self):
        options = QFileDialog.Option()
        filename, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", "All Files (*);;", options=options)
        if filename != "":
            misalignmentData = cmn.loadCSVFile(filename)
            # print(misalignmentData)
            biasVal = misalignmentData["Bias"]
            RVal = misalignmentData.iloc[0:5, 2:5]
            print(RVal.iloc[0,0])

            self.W1_1.le.setText(f'{RVal.iloc[0,0]:.10f}'.rstrip('0').rstrip('.'))
            self.W1_2.le.setText(f'{RVal.iloc[0,1]:.10f}'.rstrip('0').rstrip('.'))
            self.W1_3.le.setText(f'{RVal.iloc[0,2]:.10f}'.rstrip('0').rstrip('.'))
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


    # 將輸入至edit控制項中的數值轉為整數
    def Send_G11_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W1_1.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G11, value[0], 1)

    def Send_G12_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W1_2.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G12, value[0], 1)

    def Send_G13_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W1_3.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G13, value[0], 1)

    def Send_G21_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W2_1.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G21, value[0], 1)

    def Send_G22_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W2_2.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G22, value[0], 1)

    def Send_G23_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W2_3.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G23, value[0], 1)

    def Send_G31_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W3_1.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G31, value[0], 1)

    def Send_G32_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W3_2.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G32, value[0], 1)

    def Send_G33_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.W3_3.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_G33, value[0], 1)

    def Send_GX_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Wx.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_GX, value[0], 1)

    def Send_GY_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Wy.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_GY, value[0], 1)

    def Send_GZ_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Wz.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Gyro_GZ, value[0], 1)

    def Send_A11_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A1_1.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A11, value[0], 1)

    def Send_A12_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A1_2.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A12, value[0], 1)

    def Send_A13_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A1_3.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A13, value[0], 1)

    def Send_A21_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A2_1.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A21, value[0], 1)

    def Send_A22_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A2_2.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A22, value[0], 1)

    def Send_A23_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A2_3.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A23, value[0], 1)

    def Send_A31_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A3_1.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A31, value[0], 1)

    def Send_A32_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A3_2.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A32, value[0], 1)

    def Send_A33_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.A3_3.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_A33, value[0], 1)

    def Send_AX_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Ax.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_AX, value[0], 1)

    def Send_AY_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Ay.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_AY, value[0], 1)

    def Send_AZ_CMD(self):
        value = struct.unpack('<I', struct.pack('<f', (float(self.Az.le.text())*-1)))
        self.__act.writeImuCmd(CMD_Accele_AZ, value[0], 1)
        print("send AZ")


if __name__ == "__main__":
    app = QApplication([])
    win = pig_calibration_widget("act")
    win.show()
    app.exec_()
