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
# import py3lib
# import py3lib.FileToArray as file
# import py3lib.QuLogger as Qlogger 
# import py3lib.FileToArray as fil2a 
import Sparrow_mini_v2_Widget as UI 
import Sparrow_mini_v2_Action as ACT
import gyro_Globals as globals
TITLE_TEXT = "OPEN LOOP"
VERSION_TEXT = 'fog open loop 2020/12/25'
READOUT_FILENAME = "Signal_Read_Out.txt"
MAX_SAVE_INDEX = 3000
TEST_MODE = False
DLY_CMD = 0.01 #delay between command
DEBUG = 1
track_max = 50
track_min = -50
w_factor = 0.01
xlm_factor = 0.000122 #4g / 32768
# gyro_factor = 0.00763 #250 / 32768 
gyro_factor = 0.0090 #250 / 32768 
gyro200_factor = 0.0121

# wx_offset = 107.065
# wy_offset = -513.717

'''define uart address '''
MOD_FREQ_ADDR = 	0
MOD_AMP_H_ADDR = 	1
MOD_AMP_L_ADDR = 	2
ERR_OFFSET_ADDR =	3
POLARITY_ADDR = 	4
WAIT_CNT_ADDR = 	5
ERR_TH_ADDR = 		6
ERR_AVG_ADDR = 		7
TIMER_RST_ADDR = 	8
GAIN1_ADDR = 		9
GAIN2_ADDR = 		10
FB_ON_ADDR = 		11
CONST_STEP_ADDR = 	12
FPGA_Q_ADDR	=		13
FPGA_R_ADDR = 		14

DAC_GAIN_ADDR = 	50
DATA_RATE_ADDR =	98
DATA_OUT_START_ADDR =	99

STEP_MAX = 10
V2PIN = 11
OPENLOOP_START = 12
STEP_TRIG_DLY = 13
# GAINPRE = '14 '
# FB_ON = '15 '
FPGA_Q =14
FPGA_R = 15
'''adc conversion '''
ADC_COEFFI = (4/8192) #PD attnuates 5 times befor enter ADC
# ADC_COEFFI = 1
TIME_COEFFI = 0.0001
''' define initial value'''

MOD_H_INIT 			= 3300
MOD_L_INIT 			= -3300
FREQ_INIT 			= 138
ERR_OFFSET_INIT 	= 0
POLARITY_INIT 		= 1
WAIT_CNT_INIT 		= 69
ERR_TH_INIT 		= 0
ERR_AVG_INIT 		= 6
GAIN1_SEL_INIT 		= 7
GAIN2_SEL_INIT 		= 0
DAC_GAIN_INIT 		= 300
FB_ON_INIT			= 0
CONST_STEP_INIT		= 0
FPGA_Q_INIT			= 1
FPGA_R_INIT			= 6
SW_Q_INIT			= 1
SW_R_INIT			= 10
SF_A = 1
SF_B = 0
DATA_RATE_INIT		= 2135

# STEP_MAX_INIT = 10000
# V2PI_INIT = 30000
# V2PIN_INIT = -30000
# STEP_TRIG_DLY_INIT = 0
# MODE_INIT = 0
# FPGA_Q_INIT = 10
# FPGA_R_INIT = 5

class mainWindow(QMainWindow):
	# Kal_status = 0
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
			self.act.openLoop_updata4.connect(self.printData)
		else:
			self.act.openLoop_updata4.connect(self.plotData)
		
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

	# """ comport functin """
	def update_comport(self):
		self.act.COM.selectCom()
		self.top.usb.cs.clear()
		if(self.act.COM.portNum > 0):
			for i in range(self.act.COM.portNum):
				self.top.usb.cs.addItem(self.act.COM.comPort[i][0])
			idx = self.top.usb.cs.currentIndex()
			self.top.usb.lb.setText(self.act.COM.comPort[idx][1])
	
	def uadate_comport_label(self):
		idx = self.top.usb.cs.currentIndex()
		self.top.usb.lb.setText(self.act.COM.comPort[idx][1])
		self.cp = self.act.COM.comPort[idx][0]
	
	def usbConnect(self):
		# self.usbconnect_status = pyqtSignal(object)
		print(self.cp);
		if (TEST_MODE):
			usbConnStatus = True
		else:
			usbConnStatus = self.act.COM.connect_comboBox(baudrate = 115200, timeout = 1, port_name=self.cp)
		print("status:" + str(usbConnStatus))
		if usbConnStatus:
			self.top.usb.SetConnectText(Qt.blue, self.cp + " Connect")
			self.usbconnect_status.emit(1)
			print("Connect build")
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)
			print("Connect failed")
			
# """ end of comport functin """
	
	def checkBoxInit(self):
		self.top.save_text.cb.setChecked(0)
	
	def cb_toogled(self, cb):
		if(cb.text()==self.top.save_text.cb.text()):
			self.save_cb_flag = cb.isChecked()
			print('save_cb_flag:', self.save_cb_flag)

	def setInitValue(self, EN):
		if(EN):
			self.act.COM.writeBinary(MOD_FREQ_ADDR)
			self.send32BitCmd(FREQ_INIT)
			self.act.COM.writeBinary(MOD_AMP_H_ADDR)
			self.send32BitCmd(MOD_H_INIT)
			self.act.COM.writeBinary(MOD_AMP_L_ADDR)
			self.send32BitCmd(MOD_L_INIT)
			self.act.COM.writeBinary(ERR_OFFSET_ADDR)
			self.send32BitCmd(ERR_OFFSET_INIT)
			self.act.COM.writeBinary(POLARITY_ADDR)
			self.send32BitCmd(POLARITY_INIT)
			self.act.COM.writeBinary(WAIT_CNT_ADDR)
			self.send32BitCmd(WAIT_CNT_INIT)
			self.act.COM.writeBinary(ERR_TH_ADDR)
			self.send32BitCmd(ERR_TH_INIT)
			self.act.COM.writeBinary(ERR_AVG_ADDR)
			self.send32BitCmd(ERR_AVG_INIT)
			self.act.COM.writeBinary(GAIN1_ADDR)
			self.send32BitCmd(GAIN1_SEL_INIT)
			self.act.COM.writeBinary(GAIN2_ADDR)
			self.send32BitCmd(GAIN2_SEL_INIT)
			self.act.COM.writeBinary(DAC_GAIN_ADDR)
			self.send32BitCmd(DAC_GAIN_INIT)
			self.act.COM.writeBinary(FB_ON_ADDR)
			self.send32BitCmd(FB_ON_INIT)
			self.act.COM.writeBinary(CONST_STEP_ADDR)
			self.send32BitCmd(CONST_STEP_INIT)
			self.act.COM.writeBinary(DATA_RATE_ADDR)
			self.send32BitCmd(DATA_RATE_INIT)
			globals.kal_Q = SW_Q_INIT
			globals.kal_R = SW_R_INIT 
			
			
			self.top.freq.spin.setValue(FREQ_INIT)
			time.sleep(DLY_CMD)
			self.top.mod_H.spin.setValue(MOD_H_INIT)
			time.sleep(DLY_CMD)
			self.top.mod_L.spin.setValue(MOD_L_INIT)
			time.sleep(DLY_CMD)
			self.top.err_offset.spin.setValue(ERR_OFFSET_INIT)
			time.sleep(DLY_CMD)
			self.top.polarity.spin.setValue(POLARITY_INIT)
			time.sleep(DLY_CMD)
			self.top.wait_cnt.spin.setValue(WAIT_CNT_INIT)
			time.sleep(DLY_CMD)
			self.top.err_th.spin.setValue(ERR_TH_INIT)
			time.sleep(DLY_CMD)
			self.top.avg.spin.setValue(ERR_AVG_INIT)
			time.sleep(DLY_CMD)
			self.top.gain1.spin.setValue(GAIN1_SEL_INIT)
			time.sleep(DLY_CMD)
			self.top.gain2.spin.setValue(GAIN2_SEL_INIT)
			time.sleep(DLY_CMD)
			self.top.dac_gain.spin.setValue(DAC_GAIN_INIT)
			time.sleep(DLY_CMD)
			self.top.fb_on.spin.setValue(FB_ON_INIT)
			time.sleep(DLY_CMD)
			self.top.const_step.spin.setValue(CONST_STEP_INIT)
			time.sleep(DLY_CMD)
			self.top.HD_Q.spin.setValue(FPGA_Q_INIT)
			time.sleep(DLY_CMD)
			self.top.HD_R.spin.setValue(FPGA_R_INIT) 
			time.sleep(DLY_CMD)
			self.top.dataRate_sd.sd.setValue(DATA_RATE_INIT) 
			time.sleep(DLY_CMD)
			self.top.SW_Q.spin.setValue(globals.kal_Q)
			self.top.SW_R.spin.setValue(globals.kal_R)
			''' line editor'''
			self.top.sf_a.le.setText('1') 
			self.top.sf_b.le.setText('0') 
			self.sf_a_var = float(self.top.sf_a.le.text())
			self.sf_b_var = float(self.top.sf_b.le.text())

	def SF_A_EDIT(self):
		self.sf_a_var = float(self.top.sf_a.le.text())
		print('sf_a_var: ', self.sf_a_var)
		
	def SF_B_EDIT(self):
		self.sf_b_var = float(self.top.sf_b.le.text())
		print('sf_b_var: ', self.sf_b_var)
	
	def resetTimer(self):
		self.act.COM.writeBinary(TIMER_RST_ADDR)
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
		self.top.read_btn.bt.setEnabled(flag)
		self.top.stop_btn.bt.setEnabled(flag)
		
	''' UART command '''
	def send_FREQ_CMD(self):
		value = self.top.freq.spin.value()	
		print('set freq: ', value)
		self.top.freq.lb.setText(str(round(1/(2*(value+1)*10e-6),2))+' KHz')
		# print(hex(value))
		self.act.COM.writeBinary(MOD_FREQ_ADDR)
		self.send32BitCmd(value)
		
	def send_MOD_H_CMD(self):
		value = self.top.mod_H.spin.value()	
		print('set mod_H: ', value)
		self.act.COM.writeBinary(MOD_AMP_H_ADDR)
		self.send32BitCmd(value)
	
	def send_MOD_L_CMD(self):
		value = self.top.mod_L.spin.value()	
		print('set mod_L: ', value)
		self.act.COM.writeBinary(MOD_AMP_L_ADDR)
		self.send32BitCmd(value)
	
	def send_ERR_OFFSET_CMD(self):
		value = self.top.err_offset.spin.value()	
		print('set err offset: ', value)
		self.act.COM.writeBinary(ERR_OFFSET_ADDR)
		self.send32BitCmd(value)
		
	def send_POLARITY_CMD(self):
		value = self.top.polarity.spin.value()	
		print('set polarity: ', value)
		self.act.COM.writeBinary(POLARITY_ADDR)
		self.send32BitCmd(value)
		
	def send_WAIT_CNT_CMD(self):
		value = self.top.wait_cnt.spin.value()
		print('set wait cnt: ', value)
		self.act.COM.writeBinary(WAIT_CNT_ADDR)
		self.send32BitCmd(value)
		
	def send_ERR_TH_CMD(self):
		value = self.top.err_th.spin.value()	
		print('set err_th: ', value)
		self.act.COM.writeBinary(ERR_TH_ADDR)
		self.send32BitCmd(value)
		
	def send_AVG_CMD(self):
		value = self.top.avg.spin.value()
		print('set err_avg: ', value)
		self.act.COM.writeBinary(ERR_AVG_ADDR)
		self.send32BitCmd(value)

	def send_GAIN1_CMD(self):
		value = self.top.gain1.spin.value()	
		print('set gain1: ', value)
		self.act.COM.writeBinary(GAIN1_ADDR)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
		
	def send_GAIN2_CMD(self):
		value = self.top.gain2.spin.value()	
		print('set gain2: ', value)
		self.act.COM.writeBinary(GAIN2_ADDR)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
		
	def send_FB_ON_CMD(self):
		value = self.top.fb_on.spin.value()	
		print('set FB on: ', value)
		self.act.COM.writeBinary(FB_ON_ADDR)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
	
	def send_DAC_GAIN_CMD(self):
		value = self.top.dac_gain.spin.value()
		print('set DAC gain: ', value)
		self.act.COM.writeBinary(DAC_GAIN_ADDR)
		self.send32BitCmd(value)
	
	def send_CONST_STEP_CMD(self):
		value = self.top.const_step.spin.value()	
		print('set constant step: ', value)
		self.act.COM.writeBinary(CONST_STEP_ADDR)
		self.send32BitCmd(value)
		
	def send_HD_Q(self):
		value = self.top.HD_Q.spin.value()	
		print('set FPGA Q: ', value)
		self.act.COM.writeBinary(FPGA_Q_ADDR)
		self.send32BitCmd(value)
				
	def send_HD_R(self):
		value = self.top.HD_R.spin.value()	
		print('set FPGA R: ', value)
		self.act.COM.writeBinary(FPGA_R_ADDR)
		self.send32BitCmd(value)
	
	def update_kal_Q(self):
		value = self.top.SW_Q.spin.value()
		globals.kal_Q = value
		print(value);
		print('kal_Q:', globals.kal_Q)
		
	def update_kal_R(self):
		value = self.top.SW_R.spin.value()
		globals.kal_R = value
		print(value);
		print('kal_R:', globals.kal_R)
		
	def send_DATA_RATE_CMD(self):
		value = self.top.dataRate_sd.sd.value()	
		print('set dataRate: ', value)
		self.act.COM.writeBinary(DATA_RATE_ADDR)
		self.send32BitCmd(value)
				
	# def send_V2PIN_CMD(self):
		# value = self.top.v2piN.spin.value()	
		# cmd = V2PIN + str(value) + '\n'
		# print(cmd)
		# self.act.COM.writeLine(cmd)
		
	
		
	# def send_trigDelay_CMD(self):
		# value = self.top.trigDelay.spin.value()	
		# cmd = STEP_TRIG_DLY + str(value) + '\n'
		# print(cmd)
		# self.act.COM.writeLine(cmd)
		

		

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
			
# """ comport functin """
	def update_comport(self):
		self.act.COM.selectCom()
		self.top.usb.cs.clear()
		if(self.act.COM.portNum > 0):
			for i in range(self.act.COM.portNum):
				self.top.usb.cs.addItem(self.act.COM.comPort[i][0])
			idx = self.top.usb.cs.currentIndex()
			self.top.usb.lb.setText(self.act.COM.comPort[idx][1])
	
	def uadate_comport_label(self):
		idx = self.top.usb.cs.currentIndex()
		self.top.usb.lb.setText(self.act.COM.comPort[idx][1])
		self.cp = self.act.COM.comPort[idx][0]
	
	def usbConnect(self):
		# self.usbconnect_status = pyqtSignal(object)
		print(self.cp);
		if (TEST_MODE):
			usbConnStatus = True
		else:
			usbConnStatus = self.act.COM.connect_comboBox(baudrate = 115200, timeout = 1, port_name=self.cp)
		print("status:" + str(usbConnStatus))
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
		# self.save_status = 1
		if(self.save_cb_flag == True):
			self.open_file(self.top.save_text.le.text())
		
		self.resetTimer()
		if(self.trig_mode): 	#internal mode
			self.act.COM.writeBinary(DATA_OUT_START_ADDR)
			self.send32BitCmd(1)
		else: 				#sync mode
			self.act.COM.writeBinary(DATA_OUT_START_ADDR)
			self.send32BitCmd(2)
		self.start_time = time.time()
		
		self.act.startRun() # set self.act.runFlag = True
		self.act.start()
		

	def buttonStop(self):#set runFlag=0
		# self.act.runFlag = False
		self.act.dt_init_flag = 1
		self.act.stopRun()
		
		# self.act.terminate() 
		
	def myThreadStop(self):
		self.act.COM.writeBinary(DATA_OUT_START_ADDR)
		self.send32BitCmd(0)
		
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
		
	def plotData(self, time, data, step, PD_temperature):
		if(self.act.runFlag):
			self.top.com_plot1.ax.clear()
			self.top.com_plot2.ax.clear()
		update_rate = 1/((time[1] - time[0])*TIME_COEFFI)
		#update label#
		self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
		self.top.temperature_lb.lb.setText(str(PD_temperature[0]))
		self.top.dataRate_lb.lb.setText(str(np.round(update_rate, 1)))
		
		data_f = data*ADC_COEFFI 
		time_f = time*TIME_COEFFI
		step_f = step*self.sf_a_var + self.sf_b_var
		# data_f = data 
		self.data  = np.append(self.data, data_f)
		self.time  = np.append(self.time, time_f)
		self.step = np.append(self.step, step_f)
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.step = self.step[self.act.data_frame_update_point:]
			self.time = self.time[self.act.data_frame_update_point:]
		
		if(self.save_cb_flag == True):
			np.savetxt(self.f, (np.vstack([time_f, data_f, step, PD_temperature])).T, fmt='%5.5f, %5.5f, %d, %3.1f')
		# print(time)
		# print('len(time):', len(time))
		# print('len(data):', len(data))
		self.top.com_plot1.ax.plot(self.time, self.data, color = 'r', linestyle = '-', marker = '*', label="err")
		# self.top.com_plot1.ax.plot(self.data, color = 'r', linestyle = '-', marker = '*', label="err")
		self.top.com_plot1.figure.canvas.draw()		
		self.top.com_plot1.figure.canvas.flush_events()
		if(self.act.runFlag):
			# print('update rate: ', np.round(update_rate, 1), end=', ')
			print('step avg: ', np.round(np.average(self.step), 3))
		self.top.com_plot2.ax.plot(self.time, self.step, color = 'r', linestyle = '-', marker = '*', label="step")
		# self.top.com_plot2.ax.plot(self.step, color = 'r', linestyle = '-', marker = '*', label="step")
		self.top.com_plot2.figure.canvas.draw()		
		self.top.com_plot2.figure.canvas.flush_events()
		
		

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
