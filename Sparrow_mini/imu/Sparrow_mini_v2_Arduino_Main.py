import os 
import sys 
sys.path.append("../../") 
import time 
import datetime
from scipy import signal
# import logging
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
import numpy as np
import traceback
# import py3lib
# import py3lib.FileToArray as file
# import py3lib.QuLogger as Qlogger 
# import py3lib.FileToArray as fil2a 
import Sparrow_mini_v2_Widget as UI 
import Sparrow_mini_crc_v2_Action as ACT
import gyro_Globals as globals
TITLE_TEXT = "OPEN LOOP"
VERSION_TEXT = 'PIG V2'
READOUT_FILENAME = "Signal_Read_Out.txt"
MAX_SAVE_INDEX = 3000
DLY_CMD = 0.01 #delay between command
DEBUG = 1
track_max = 50
track_min = -50
w_factor = 0.01
xlm_factor = 0.000122 #4g / 32768
# gyro_factor = 0.00763 #250 / 32768 
gyro_factor = 0.0090 #250 / 32768 
gyro200_factor = 0.0121

BAUD_RATE_1 = 115200
BAUD_RATE_2 = 230400
# wx_offset = 107.065
# wy_offset = -513.717

'''-------define CMD address map-------'''
'''0~7 for output mode setting'''
'''8~255 for parameter setting'''
MODE_STOP 			= 0
MODE_FOG			= 1
MODE_IMU			= 2
MODE_EQ				= 3
MODE_IMU_FAKE		= 4
CMD_FOG_MOD_FREQ	= 8
CMD_FOG_MOD_AMP_H	= 9
CMD_FOG_MOD_AMP_L	= 10
CMD_FOG_ERR_OFFSET	= 11
CMD_FOG_POLARITY	= 12
CMD_FOG_WAIT_CNT	= 13
CMD_FOG_ERR_TH		= 14
CMD_FOG_ERR_AVG		= 15
CMD_FOG_TIMER_RST	= 16
CMD_FOG_GAIN1		= 17
CMD_FOG_GAIN2		= 18
CMD_FOG_FB_ON		= 19
CMD_FOG_CONST_STEP	= 20
CMD_FOG_FPGA_Q		= 21
CMD_FOG_FPGA_R		= 22
CMD_FOG_DAC_GAIN 	= 23
CMD_FOG_INT_DELAY	= 24
CMD_FOG_OUT_START	= 25

''' FOG paras position'''
POS_MOD_H_INIT 			= 0
POS_MOD_L_INIT 			= 1
POS_FREQ_INIT 			= 2
POS_DAC_GAIN_INIT 		= 3
POS_ERR_OFFSET_INIT 	= 4
POS_POLARITY_INIT 		= 5
POS_WAIT_CNT_INIT 		= 6
POS_ERR_TH_INIT 		= 7
POS_ERR_AVG_INIT 		= 8
POS_GAIN1_SEL_INIT 		= 9
POS_GAIN2_SEL_INIT 		= 10
POS_FB_ON_INIT			= 11
POS_CONST_STEP_INIT		= 12
POS_FPGA_Q_INIT			= 13
POS_FPGA_R_INIT			= 14
POS_SW_Q_INIT			= 15
POS_SW_R_INIT			= 16
POS_SF_A_INIT 	 		= 17
POS_SF_B_INIT 			= 18
POS_DATA_RATE_INIT		= 19

'''adc conversion '''
ADC_COEFFI = (4/8192) #PD attnuates 5 times befor enter ADC
# ADC_COEFFI = 1
TIME_COEFFI = 0.0001
# TIME_COEFFI = 1
''' define initial value'''

class mainWindow(QMainWindow):
	''' FOG PARAMETERS'''
	MOD_H_INIT 			= 3250
	MOD_L_INIT 			= -3250
	FREQ_INIT 			= 139
	DAC_GAIN_INIT 		= 290
	ERR_OFFSET_INIT 	= 0
	POLARITY_INIT 		= 1
	WAIT_CNT_INIT 		= 65
	ERR_TH_INIT 		= 0
	ERR_AVG_INIT 		= 6
	GAIN1_SEL_INIT 		= 6
	GAIN2_SEL_INIT 		= 5
	FB_ON_INIT			= 1
	CONST_STEP_INIT		= 0
	FPGA_Q_INIT			= 1
	FPGA_R_INIT			= 6
	SW_Q_INIT			= 1
	SW_R_INIT			= 6
	SF_A_INIT = 0.00295210451588764*1.02/2
	SF_B_INIT = -0.00137052112589694
	DATA_RATE_INIT		= 1863
	''' global var'''
	save_cb_flag = 0
	sf_a_var = 0
	sf_b_var = 0
	start_time = 0
	end_time = 0
	first_data_flag = 1
	time_offset = 0
	trig_mode = 0
	temp_time = 0
	# timer_rst_succeed = 0
	''' pyqtSignal'''
	usbconnect_status = pyqtSignal(object) #to trigger the btn to enable state
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.resize(1100,800)
		self.move(0,0)
		self.loggername = "Total"
		self.top = UI.mainWidget()
		self.act = ACT.gyro_Action(self.loggername)
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.data = np.empty(0)
		self.step = np.empty(0)
		self.time = np.empty(0)
		self.readParameters()
		self.setInitValue(False)
		self.setBtnStatus(False)
		self.get_rbVal()
			
	def mainUI(self):
		mainLayout = QGridLayout()
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.top,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)
		
	def mainMenu(self):
		mainMenu = self.menuBar() #放menu的地方，一定要有
		version_Menu = mainMenu.addMenu("version") #生成menu item
		version = QAction("Version", self) #生成menu item裡面的細項，名稱叫"Version"
		version.triggered.connect(self.versionBox)#把細項連接到要執行的動作
		version_Menu.addAction(version)#把連接好動作的細項加回menu item		


	def linkFunction(self):
		''' btn connect '''
		self.top.usb.bt_update.clicked.connect(self.update_comport)
		self.top.usb.cs.currentIndexChanged.connect(self.uadate_comport_label)
		self.top.usb.bt_connect.clicked.connect(self.usbConnect)

		''' thread connect '''
		self.top.read_btn.bt.clicked.connect(self.thread1Start) # set runFlag=1
		self.top.stop_btn.bt.clicked.connect(self.buttonStop) # set runFlag=0

		''' emit connect '''
		self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		
		if(globals.PRINT_MODE):
			self.act.data_update6.connect(self.printImu)
		else:
			self.act.data_update4.connect(self.plotData)
		
		#btn enable signal
		self.usbconnect_status.connect(self.setBtnStatus) #確定usb連接成功時才enable btn
		self.usbconnect_status.connect(self.setInitValue)
		
		''' radio btn'''
		self.top.Kal_rb.toggled.connect(lambda:self.rb_toggled(self.top.Kal_rb))
		self.top.trig_mode_rb.rb1.toggled.connect(self.trig_mode_rb_chk) 
		self.top.trig_mode_rb.rb1.toggled.connect(self.slider_en)
		''' line edit '''
		self.top.sf_a.le.editingFinished.connect(self.SF_A_EDIT)
		self.top.sf_b.le.editingFinished.connect(self.SF_B_EDIT)

		''' spin box connect'''
		self.top.wait_cnt.spin.valueChanged.connect(self.send_WAIT_CNT_CMD)
		self.top.avg.spin.valueChanged.connect(self.send_AVG_CMD)
		self.top.mod_H.spin.valueChanged.connect(self.send_MOD_H_CMD)
		self.top.mod_L.spin.valueChanged.connect(self.send_MOD_L_CMD)
		self.top.freq.spin.valueChanged.connect(self.send_FREQ_CMD)
		self.top.err_th.spin.valueChanged.connect(self.send_ERR_TH_CMD)
		self.top.err_offset.spin.valueChanged.connect(self.send_ERR_OFFSET_CMD)
		self.top.polarity.spin.valueChanged.connect(self.send_POLARITY_CMD)
		self.top.const_step.spin.valueChanged.connect(self.send_CONST_STEP_CMD)
		self.top.HD_Q.spin.valueChanged.connect(self.send_HD_Q)
		self.top.HD_R.spin.valueChanged.connect(self.send_HD_R)
		self.top.SW_Q.spin.valueChanged.connect(self.update_kal_Q)
		self.top.SW_R.spin.valueChanged.connect(self.update_kal_R)
		self.top.gain1.spin.valueChanged.connect(self.send_GAIN1_CMD)
		self.top.gain2.spin.valueChanged.connect(self.send_GAIN2_CMD)
		self.top.fb_on.spin.valueChanged.connect(self.send_FB_ON_CMD)
		self.top.dac_gain.spin.valueChanged.connect(self.send_DAC_GAIN_CMD) 
		''' slider '''
		self.top.dataRate_sd.sd.valueChanged.connect(self.send_DATA_RATE_CMD) 
		''' check box'''
		self.top.save_text.cb.toggled.connect(lambda:self.cb_toogled(self.top.save_text.cb))

	def checkBoxInit(self):
		self.top.save_text.cb.setChecked(0)
	
	def cb_toogled(self, cb):
		if(cb.text()==self.top.save_text.cb.text()):
			self.save_cb_flag = cb.isChecked()
			print('save_cb_flag:', self.save_cb_flag)

	def setInitValue(self, EN):
		if(EN and globals.TEST_MODE==False):
			# print('enter set init value')
			self.act.COM.writeBinary(CMD_FOG_MOD_FREQ)
			self.send32BitCmd(self.FREQ_INIT)
			self.act.COM.writeBinary(CMD_FOG_MOD_AMP_H)
			self.send32BitCmd(self.MOD_H_INIT)
			self.act.COM.writeBinary(CMD_FOG_MOD_AMP_L)
			self.send32BitCmd(self.MOD_L_INIT)
			self.act.COM.writeBinary(CMD_FOG_ERR_OFFSET)
			self.send32BitCmd(self.ERR_OFFSET_INIT)
			self.act.COM.writeBinary(CMD_FOG_POLARITY)
			self.send32BitCmd(self.POLARITY_INIT)
			self.act.COM.writeBinary(CMD_FOG_WAIT_CNT)
			self.send32BitCmd(self.WAIT_CNT_INIT)
			self.act.COM.writeBinary(CMD_FOG_ERR_TH)
			self.send32BitCmd(self.ERR_TH_INIT)
			self.act.COM.writeBinary(CMD_FOG_ERR_AVG)
			self.send32BitCmd(self.ERR_AVG_INIT)
			self.act.COM.writeBinary(CMD_FOG_GAIN1)
			self.send32BitCmd(self.GAIN1_SEL_INIT)
			self.act.COM.writeBinary(CMD_FOG_GAIN2)
			self.send32BitCmd(self.GAIN2_SEL_INIT)
			self.act.COM.writeBinary(CMD_FOG_DAC_GAIN)
			self.send32BitCmd(self.DAC_GAIN_INIT)
			self.act.COM.writeBinary(CMD_FOG_FB_ON)
			self.send32BitCmd(self.FB_ON_INIT)
			self.act.COM.writeBinary(CMD_FOG_CONST_STEP)
			self.send32BitCmd(self.CONST_STEP_INIT)
			self.act.COM.writeBinary(CMD_FOG_INT_DELAY)
			self.send32BitCmd(self.DATA_RATE_INIT)
			# globals.kal_Q = self.SW_Q_INIT
			# globals.kal_R = self.SW_R_INIT 
			
			
			self.top.freq.spin.setValue(self.FREQ_INIT)
			time.sleep(DLY_CMD)
			self.top.mod_H.spin.setValue(self.MOD_H_INIT)
			time.sleep(DLY_CMD)
			self.top.mod_L.spin.setValue(self.MOD_L_INIT)
			time.sleep(DLY_CMD)
			self.top.err_offset.spin.setValue(self.ERR_OFFSET_INIT)
			time.sleep(DLY_CMD)
			self.top.polarity.spin.setValue(self.POLARITY_INIT)
			time.sleep(DLY_CMD)
			self.top.wait_cnt.spin.setValue(self.WAIT_CNT_INIT)
			time.sleep(DLY_CMD)
			self.top.err_th.spin.setValue(self.ERR_TH_INIT)
			time.sleep(DLY_CMD)
			self.top.avg.spin.setValue(self.ERR_AVG_INIT)
			time.sleep(DLY_CMD)
			self.top.gain1.spin.setValue(self.GAIN1_SEL_INIT)
			time.sleep(DLY_CMD)
			self.top.gain2.spin.setValue(self.GAIN2_SEL_INIT)
			time.sleep(DLY_CMD)
			self.top.dac_gain.spin.setValue(self.DAC_GAIN_INIT)
			time.sleep(DLY_CMD)
			self.top.fb_on.spin.setValue(self.FB_ON_INIT)
			time.sleep(DLY_CMD)
			self.top.const_step.spin.setValue(self.CONST_STEP_INIT)
			time.sleep(DLY_CMD)
			self.top.HD_Q.spin.setValue(self.FPGA_Q_INIT)
			time.sleep(DLY_CMD)
			self.top.HD_R.spin.setValue(self.FPGA_R_INIT) 
			time.sleep(DLY_CMD)
			self.top.dataRate_sd.sd.setValue(self.DATA_RATE_INIT) 
			time.sleep(DLY_CMD)
			# self.top.SW_Q.spin.setValue(globals.kal_Q)
			# self.top.SW_R.spin.setValue(globals.kal_R)
			self.top.SW_Q.spin.setValue(self.SW_Q_INIT)
			self.top.SW_R.spin.setValue(self.SW_R_INIT)
			''' line editor'''
			self.top.sf_a.le.setText(str(self.SF_A_INIT)) 
			self.top.sf_b.le.setText(str(self.SF_B_INIT)) 
			self.sf_a_var = float(self.top.sf_a.le.text())
			self.sf_b_var = float(self.top.sf_b.le.text())
			# print('leave set init value')
			
	def SF_A_EDIT(self):
		self.sf_a_var = float(self.top.sf_a.le.text())
		print('sf_a_var: ', self.sf_a_var)
		self.SF_A_INIT = self.sf_a_var
		self.writeParameters()
		
	def SF_B_EDIT(self):
		self.sf_b_var = float(self.top.sf_b.le.text())
		print('sf_b_var: ', self.sf_b_var)
		self.SF_B_INIT = self.sf_b_var
		self.writeParameters()
	
	def resetTimer(self):
		self.act.COM.writeBinary(CMD_FOG_TIMER_RST)
		self.send32BitCmd(1)
		
	def send32BitCmd(self, value):
		if(value < 0):
			value = (1<<32) + value
		# time.sleep(DLY_CMD)
		self.act.COM.writeBinary(value>>24 & 0xFF)
		time.sleep(DLY_CMD)
		self.act.COM.writeBinary(value>>16 & 0xFF)
		time.sleep(DLY_CMD)
		self.act.COM.writeBinary(value>>8 & 0xFF)
		time.sleep(DLY_CMD)
		self.act.COM.writeBinary(value & 0xFF)
		time.sleep(DLY_CMD)
	
	def setBtnStatus(self, flag):
		# print('setBtnStatus')
		self.top.read_btn.bt.setEnabled(flag)
		self.top.stop_btn.bt.setEnabled(flag)
		
	''' UART command '''
	def send_FREQ_CMD(self):
		value = self.top.freq.spin.value()	
		print('set freq: ', value)
		self.top.freq.lb.setText(str(round(1/(2*(value+1)*10e-6),2))+' KHz')
		# print(hex(value))
		self.act.COM.writeBinary(CMD_FOG_MOD_FREQ)
		self.send32BitCmd(value)
		self.FREQ_INIT = value
		self.writeParameters()
		
	def send_MOD_H_CMD(self):
		value = self.top.mod_H.spin.value()	
		print('set mod_H: ', value)
		self.act.COM.writeBinary(CMD_FOG_MOD_AMP_H)
		self.send32BitCmd(value)
		self.MOD_H_INIT = value
		self.writeParameters()

	def send_MOD_L_CMD(self):
		value = self.top.mod_L.spin.value()	
		print('set mod_L: ', value)
		self.act.COM.writeBinary(CMD_FOG_MOD_AMP_L)
		self.send32BitCmd(value)
		self.MOD_L_INIT = value
		self.writeParameters()

	def send_ERR_OFFSET_CMD(self):
		value = self.top.err_offset.spin.value()	
		print('set err offset: ', value)
		self.act.COM.writeBinary(CMD_FOG_ERR_OFFSET)
		self.send32BitCmd(value)
		self.ERR_OFFSET_INIT = value
		self.writeParameters()

	def send_POLARITY_CMD(self):
		value = self.top.polarity.spin.value()	
		print('set polarity: ', value)
		self.act.COM.writeBinary(CMD_FOG_POLARITY)
		self.send32BitCmd(value)
		self.POLARITY_INIT = value
		self.writeParameters()

	def send_WAIT_CNT_CMD(self):
		value = self.top.wait_cnt.spin.value()
		print('set wait cnt: ', value)
		self.act.COM.writeBinary(CMD_FOG_WAIT_CNT)
		self.send32BitCmd(value)
		self.WAIT_CNT_INIT = value
		self.writeParameters()

	def send_ERR_TH_CMD(self):
		value = self.top.err_th.spin.value()	
		print('set err_th: ', value)
		self.act.COM.writeBinary(CMD_FOG_ERR_TH)
		self.send32BitCmd(value)
		self.ERR_TH_INIT = value
		self.writeParameters()

	def send_AVG_CMD(self):
		value = self.top.avg.spin.value()
		print('set err_avg: ', value)
		self.act.COM.writeBinary(CMD_FOG_ERR_AVG)
		self.send32BitCmd(value)
		self.ERR_AVG_INIT = value
		self.writeParameters()

	def send_GAIN1_CMD(self):
		value = self.top.gain1.spin.value()	
		print('set gain1: ', value)
		self.act.COM.writeBinary(CMD_FOG_GAIN1)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
		self.GAIN1_SEL_INIT = value
		self.writeParameters()

	def send_GAIN2_CMD(self):
		value = self.top.gain2.spin.value()	
		print('set gain2: ', value)
		self.act.COM.writeBinary(CMD_FOG_GAIN2)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
		self.GAIN2_SEL_INIT = value
		self.writeParameters()

	def send_FB_ON_CMD(self):
		value = self.top.fb_on.spin.value()	
		print('set FB on: ', value)
		self.act.COM.writeBinary(CMD_FOG_FB_ON)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
		self.FB_ON_INIT = value
		self.writeParameters()

	def send_DAC_GAIN_CMD(self):
		value = self.top.dac_gain.spin.value()
		print('set DAC gain: ', value)
		self.act.COM.writeBinary(CMD_FOG_DAC_GAIN)
		self.send32BitCmd(value)
		self.DAC_GAIN_INIT = value
		self.writeParameters()

	def send_CONST_STEP_CMD(self):
		value = self.top.const_step.spin.value()	
		print('set constant step: ', value)
		self.act.COM.writeBinary(CMD_FOG_CONST_STEP)
		self.send32BitCmd(value)
		self.CONST_STEP_INIT = value
		self.writeParameters()

	def send_HD_Q(self):
		value = self.top.HD_Q.spin.value()	
		print('set FPGA Q: ', value)
		self.act.COM.writeBinary(CMD_FOG_FPGA_Q)
		self.send32BitCmd(value)
		self.FPGA_Q_INIT = value
		self.writeParameters()

	def send_HD_R(self):
		value = self.top.HD_R.spin.value()	
		print('set FPGA R: ', value)
		self.act.COM.writeBinary(CMD_FOG_FPGA_R)
		self.send32BitCmd(value)
		self.FPGA_R_INIT = value
		self.writeParameters()

	def update_kal_Q(self):
		value = self.top.SW_Q.spin.value()
		print('kal_Q: ', value)
		self.act.kal_Q = value
		# globals.kal_Q = value
		# print(value);
		# print('kal_Q:', globals.kal_Q)
		self.SW_Q_INIT = value
		self.writeParameters()

		
	def update_kal_R(self):
		value = self.top.SW_R.spin.value()
		print('kal_R: ', value)
		self.act.kal_R = value
		# globals.kal_R = value
		# print(value);
		# print('kal_R:', globals.kal_R)
		self.SW_R_INIT = value
		self.writeParameters()
		
	def send_DATA_RATE_CMD(self):
		value = self.top.dataRate_sd.sd.value()	
		print('set dataRate: ', value)
		self.act.COM.writeBinary(CMD_FOG_INT_DELAY)
		self.send32BitCmd(value)
		self.DATA_RATE_INIT = value
		self.writeParameters()


	'''------------------------------------------------- '''
	
	def versionBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)
		
	def openFileBox(self):
		saveBox = QMessageBox()
		SaveFileName,_ = QFileDialog.getSaveFileName(self,
						"Save Data to", #視窗名稱
						"./", #起始路徑
						"Text Files (*.txt)") #存檔類型
		if (SaveFileName != ''):
			# saveBox.about(self, "Save File", "File saving on " + self.SaveFileName)
			self.open_file(SaveFileName)
			return 1
		else :
			saveBox.about(self, "Save File", "No file saving")
			return 0
	
	def showOP_Mode(self):
		if(globals.TEST_MODE == True):
			print('TEST_MODE')
		elif(globals.OP_MODE == MODE_FOG):
			print('MODE_FOG')
		elif(globals.OP_MODE == MODE_IMU):
			print('MODE_IMU')
		elif(globals.OP_MODE == MODE_EQ):
			print('MODE_EQ')
		elif(globals.OP_MODE == MODE_IMU_FAKE):
			print('MODE_IMU_FAKE')
	
# """ comport functin """
	def update_comport(self):
		self.act.COM.selectCom()
		self.top.usb.cs.clear()
		if(self.act.COM.portNum > 0):
			for i in range(self.act.COM.portNum):
				self.top.usb.cs.addItem(self.act.COM.comPort[i][0])
			idx = self.top.usb.cs.currentIndex()
			self.top.usb.lb.setText(self.act.COM.comPort[idx][1])
		# print('no comport')
	
	def uadate_comport_label(self):
		idx = self.top.usb.cs.currentIndex()
		self.top.usb.lb.setText(self.act.COM.comPort[idx][1])
		self.cp = self.act.COM.comPort[idx][0]
	
	def usbConnect(self):
		# self.usbconnect_status = pyqtSignal(object)
		
		if (globals.TEST_MODE):
			usbConnStatus = True
			self.cp = 'TEST MODE'
		else:
			usbConnStatus = self.act.COM.connect_comboBox(baudrate = BAUD_RATE_2, timeout = 1, port_name=self.cp)
		print(self.cp);
		print("status:" + str(usbConnStatus))
		self.showOP_Mode()
		if usbConnStatus:
			self.top.usb.SetConnectText(Qt.blue, self.cp + " Connect")
			self.usbconnect_status.emit(1)
			print("Connect build")
			
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)
			print("Connect failed")
			
# """ end of comport functin """
			
	def rb_toggled(self, rb):
		globals.kal_status = rb.isChecked()
		print('globals.kal_status:', globals.kal_status)
		
	def trig_mode_rb_chk(self):
		self.trig_mode = self.top.trig_mode_rb.rb1.isChecked()
		print('trig INT mode: ', self.trig_mode)
		
	def slider_en(self):
		if(self.trig_mode == True): #internal mode
			self.top.dataRate_sd.setEnabled(True)
		else:
			self.top.dataRate_sd.setEnabled(False)
		
	def get_rbVal(self):
		globals.Kal_status = self.top.Kal_rb.isChecked()
		print('Kal:', globals.Kal_status)
		self.trig_mode = self.top.trig_mode_rb.rb1.isChecked()
		print('trig INT mode: ', self.trig_mode)
	
	def open_file(self, filename):
		self.f=open(filename, 'w')
		start_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.f.writelines('#' + start_time_header + '\n')
	
	def thread1Start(self):
		if(self.save_cb_flag == True):
			self.open_file(self.top.save_text.le.text())
		
		if(globals.TEST_MODE==False): 
			self.resetTimer()
			if(self.trig_mode): 	#internal mode
				self.act.COM.writeBinary(globals.OP_MODE)
				self.send32BitCmd(1)
			else: 				#sync mode
				self.act.COM.writeBinary(globals.OP_MODE)
				self.send32BitCmd(2)
				
		self.start_time = time.time()
		
		self.act.startRun() # set self.act.runFlag = True
		self.act.start()
		pass

	def buttonStop(self):#set runFlag=0
		self.act.dt_init_flag = 1
		self.act.stopRun()
		# self.timer_rst_succeed = 0
		# self.act.COM.writeBinary(MODE_STOP)
		# self.send32BitCmd(1)
		
	def myThreadStop(self):
		if(globals.TEST_MODE==False): 
			self.act.COM.writeBinary(globals.OP_MODE)
			self.send32BitCmd(4)
		
		if(self.save_cb_flag == True):
			self.save_cb_flag == False
			self.top.save_text.cb.setChecked(0)
			stop_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			self.f.writelines('#' + stop_time_header + '\n')
			self.f.close()
			
		self.first_data_flag = 1
		self.data  = np.empty(0)
		self.time  = np.empty(0)
		self.step  = np.empty(0)
		self.resetTimer()
	def readParameters(self):
		try:
			f_par = np.loadtxt('para.txt', delimiter=',')
			self.MOD_H_INIT			= int(f_par[POS_MOD_H_INIT])
			self.MOD_L_INIT 		= int(f_par[POS_MOD_L_INIT])
			self.FREQ_INIT 			= int(f_par[POS_FREQ_INIT])
			self.DAC_GAIN_INIT 		= int(f_par[POS_DAC_GAIN_INIT])
			self.ERR_OFFSET_INIT 	= int(f_par[POS_ERR_OFFSET_INIT])
			self.POLARITY_INIT 		= int(f_par[POS_POLARITY_INIT])
			self.WAIT_CNT_INIT 		= int(f_par[POS_WAIT_CNT_INIT])
			self.ERR_TH_INIT 		= int(f_par[POS_ERR_TH_INIT])
			self.ERR_AVG_INIT 		= int(f_par[POS_ERR_AVG_INIT])
			self.GAIN1_SEL_INIT 	= int(f_par[POS_GAIN1_SEL_INIT])
			self.GAIN2_SEL_INIT 	= int(f_par[POS_GAIN2_SEL_INIT])
			self.FB_ON_INIT 		= int(f_par[POS_FB_ON_INIT])
			self.CONST_STEP_INIT 	= int(f_par[POS_CONST_STEP_INIT])
			self.FPGA_Q_INIT 		= int(f_par[POS_FPGA_Q_INIT])
			self.FPGA_R_INIT 		= int(f_par[POS_FPGA_R_INIT])
			self.SW_Q_INIT 			= int(f_par[POS_SW_Q_INIT])
			self.SW_R_INIT 			= int(f_par[POS_SW_R_INIT])
			self.SF_A_INIT			= (f_par[POS_SF_A_INIT])
			self.SF_B_INIT 			= (f_par[POS_SF_B_INIT])
			self.DATA_RATE_INIT 	= int(f_par[POS_DATA_RATE_INIT])
		except:
			traceback.print_exc()
			print('No para.txt file exist, uase default value and auto creat new!')
			self.writeParameters()
			
	def writeParameters(self):
		f_par=open('para.txt', 'w')
		np.savetxt(f_par, (np.vstack([self.MOD_H_INIT, self.MOD_L_INIT, self.FREQ_INIT, self.DAC_GAIN_INIT,
										self.ERR_OFFSET_INIT, self.POLARITY_INIT, self.WAIT_CNT_INIT,
										self.ERR_TH_INIT, self.ERR_AVG_INIT, self.GAIN1_SEL_INIT,
										self.GAIN2_SEL_INIT, self.FB_ON_INIT, self.CONST_STEP_INIT,
										self.FPGA_Q_INIT, self.FPGA_R_INIT, self.SW_Q_INIT, self.SW_R_INIT,
										self.SF_A_INIT, self.SF_B_INIT, self.DATA_RATE_INIT
		])).T, fmt='%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %1.20f, %1.17f, %d')
		f_par.close()
		
	def printData(self, time_in, data, step, PD_temperature):
		if(self.first_data_flag):
			self.first_data_flag = 0
			self.end_time = time.time()
			self.time_offset = 0.5*(self.end_time - self.start_time)
			print(self.time_offset)
		self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
		self.top.temperature_lb.lb.setText(str(PD_temperature[0]))
		data_f = data*ADC_COEFFI 
		time_f = time_in*TIME_COEFFI
		step_f = step*self.sf_a_var + self.sf_b_var
		
		print('time: ', time_f)
		print('err : ', data_f)
		print('step: ', step_f)
		
	def printImu(self, wx, wy, wz, ax, ay, az): 
		print(round(wx, 4), end='\t\t')
		print(round(wy, 4), end='\t\t')
		print(round(wz, 4), end='\t\t')
		print(round(ax, 4), end='\t\t')
		print(round(ay, 4), end='\t\t')
		print(round(az, 4))
		
		
	def plotData(self, time, data, step, PD_temperature):
		# print('main: \t', end='\t')
		# print(len(time), end='\t')
		# print(len(data), end='\t')
		# print(len(step), end='\t')
		# print(len(PD_temperature))
		if(self.act.runFlag):
			self.top.com_plot1.ax.clear()
			self.top.com_plot2.ax.clear()
		
		update_rate = 1/((time[1] - time[0])*TIME_COEFFI)
		self.top.dataRate_lb.lb.setText(str(np.round(update_rate, 1)))
		#update label#
		self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
		self.top.temperature_lb.lb.setText(str(PD_temperature[0]))
		
		if(globals.NANO33_WZ_MODE):
			data_f = data + 1.682
		else:
			data_f = data*ADC_COEFFI 
		time_f = time*TIME_COEFFI
		step_f = step*self.sf_a_var + self.sf_b_var

		if(globals.NANO33_WZ_MODE):
			self.data  = np.append(self.data, data_f*3600)
		else:
			self.data  = np.append(self.data, data_f)
		self.time  = np.append(self.time, time_f)
		self.step = np.append(self.step, step_f*3600)
		# self.step = np.append(self.step, step)
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.step = self.step[self.act.data_frame_update_point:]
			self.time = self.time[self.act.data_frame_update_point:]
		if(self.save_cb_flag == True):
			np.savetxt(self.f, (np.vstack([time_f, data_f, step, PD_temperature])).T, fmt='%5.5f, %5.9f, %d, %3.1f')
		# print('len(time):', len(time))
		# print('len(data):', len(data))
		print('step avg: ', np.round(np.average(self.step), 4), end=', ')
		print('stdev: ', np.round(np.std(self.step), 4))
		##### plot 1 ####
		self.top.com_plot1.ax.plot(self.time, self.data, color = 'b', linestyle = '-', marker = '', label="err")
		if(globals.NANO33_WZ_MODE):
			self.top.com_plot1.ax.plot(self.time, self.step, color = 'r', linestyle = '-', marker = '', label="step")
		self.top.com_plot1.figure.canvas.draw()		
		self.top.com_plot1.figure.canvas.flush_events()
		##### plot 2 ####
		self.top.com_plot2.ax.plot(self.time, self.step, color = 'r', linestyle = '-', marker = '', label="step")
		self.top.com_plot2.figure.canvas.draw()		
		self.top.com_plot2.figure.canvas.flush_events()
		
		

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
