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
CMD_FOG_MOD_FREQ	= 0
CMD_FOG_MOD_AMP_H	= 1
CMD_FOG_MOD_AMP_L	= 2
CMD_FOG_ERR_OFFSET	= 3
CMD_FOG_POLARITY	= 4
CMD_FOG_WAIT_CNT	= 5
CMD_FOG_ERR_TH		= 6
CMD_FOG_ERR_AVG		= 7
CMD_FOG_TIMER_RST	= 8
CMD_FOG_GAIN1		= 9
CMD_FOG_GAIN2		= 10
CMD_FOG_FB_ON		= 11
CMD_FOG_CONST_STEP	= 12
CMD_FOG_FPGA_Q		= 13
CMD_FOG_FPGA_R		= 14
CMD_FOG_DAC_GAIN 	= 50
CMD_FOG_INT_DELAY	= 98
CMD_FOG_OUT_START	= 99


# STEP_MAX = 10
# V2PIN = 11
# OPENLOOP_START = 12
# STEP_TRIG_DLY = 13
# GAINPRE = '14 '
# FB_ON = '15 '
# FPGA_Q =14
# FPGA_R = 15
'''adc conversion '''
ADC_COEFFI = (4/8192) #PD attnuates 5 times befor enter ADC
# ADC_COEFFI = 1
TIME_COEFFI = 0.0001
# TIME_COEFFI = 1
''' define initial value'''

# MOD_H_INIT 			= 3400
# MOD_L_INIT 			= -3400
# FREQ_INIT 			= 135
# DAC_GAIN_INIT 		= 420

MOD_H_INIT 			= 3250
MOD_L_INIT 			= -3250
FREQ_INIT 			= 138
DAC_GAIN_INIT 		= 290

ERR_OFFSET_INIT 	= 0
POLARITY_INIT 		= 1
WAIT_CNT_INIT 		= 65
ERR_TH_INIT 		= 0
ERR_AVG_INIT 		= 6
GAIN1_SEL_INIT 		= 4
GAIN2_SEL_INIT 		= 4
FB_ON_INIT			= 1
CONST_STEP_INIT		= 0
FPGA_Q_INIT			= 1
FPGA_R_INIT			= 6
SW_Q_INIT			= 1
SW_R_INIT			= 6
SF_A_INIT = 0.00295210451588764
SF_B_INIT = -0.00137052112589694
DATA_RATE_INIT		= 1863

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
			self.send32BitCmd(FREQ_INIT)
			self.act.COM.writeBinary(CMD_FOG_MOD_AMP_H)
			self.send32BitCmd(MOD_H_INIT)
			self.act.COM.writeBinary(CMD_FOG_MOD_AMP_L)
			self.send32BitCmd(MOD_L_INIT)
			self.act.COM.writeBinary(CMD_FOG_ERR_OFFSET)
			self.send32BitCmd(ERR_OFFSET_INIT)
			self.act.COM.writeBinary(CMD_FOG_POLARITY)
			self.send32BitCmd(POLARITY_INIT)
			self.act.COM.writeBinary(CMD_FOG_WAIT_CNT)
			self.send32BitCmd(WAIT_CNT_INIT)
			self.act.COM.writeBinary(CMD_FOG_ERR_TH)
			self.send32BitCmd(ERR_TH_INIT)
			self.act.COM.writeBinary(CMD_FOG_ERR_AVG)
			self.send32BitCmd(ERR_AVG_INIT)
			self.act.COM.writeBinary(CMD_FOG_GAIN1)
			self.send32BitCmd(GAIN1_SEL_INIT)
			self.act.COM.writeBinary(CMD_FOG_GAIN2)
			self.send32BitCmd(GAIN2_SEL_INIT)
			self.act.COM.writeBinary(CMD_FOG_DAC_GAIN)
			self.send32BitCmd(DAC_GAIN_INIT)
			self.act.COM.writeBinary(CMD_FOG_FB_ON)
			self.send32BitCmd(FB_ON_INIT)
			self.act.COM.writeBinary(CMD_FOG_CONST_STEP)
			self.send32BitCmd(CONST_STEP_INIT)
			self.act.COM.writeBinary(CMD_FOG_INT_DELAY)
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
			self.top.sf_a.le.setText(str(SF_A_INIT)) 
			self.top.sf_b.le.setText(str(SF_B_INIT)) 
			self.sf_a_var = float(self.top.sf_a.le.text())
			self.sf_b_var = float(self.top.sf_b.le.text())
			# print('leave set init value')
			
	def SF_A_EDIT(self):
		self.sf_a_var = float(self.top.sf_a.le.text())
		print('sf_a_var: ', self.sf_a_var)
		
	def SF_B_EDIT(self):
		self.sf_b_var = float(self.top.sf_b.le.text())
		print('sf_b_var: ', self.sf_b_var)
	
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
		
	def send_MOD_H_CMD(self):
		value = self.top.mod_H.spin.value()	
		print('set mod_H: ', value)
		self.act.COM.writeBinary(CMD_FOG_MOD_AMP_H)
		self.send32BitCmd(value)
	
	def send_MOD_L_CMD(self):
		value = self.top.mod_L.spin.value()	
		print('set mod_L: ', value)
		self.act.COM.writeBinary(CMD_FOG_MOD_AMP_L)
		self.send32BitCmd(value)
	
	def send_ERR_OFFSET_CMD(self):
		value = self.top.err_offset.spin.value()	
		print('set err offset: ', value)
		self.act.COM.writeBinary(CMD_FOG_ERR_OFFSET)
		self.send32BitCmd(value)
		
	def send_POLARITY_CMD(self):
		value = self.top.polarity.spin.value()	
		print('set polarity: ', value)
		self.act.COM.writeBinary(CMD_FOG_POLARITY)
		self.send32BitCmd(value)
		
	def send_WAIT_CNT_CMD(self):
		value = self.top.wait_cnt.spin.value()
		print('set wait cnt: ', value)
		self.act.COM.writeBinary(CMD_FOG_WAIT_CNT)
		self.send32BitCmd(value)
		
	def send_ERR_TH_CMD(self):
		value = self.top.err_th.spin.value()	
		print('set err_th: ', value)
		self.act.COM.writeBinary(CMD_FOG_ERR_TH)
		self.send32BitCmd(value)
		
	def send_AVG_CMD(self):
		value = self.top.avg.spin.value()
		print('set err_avg: ', value)
		self.act.COM.writeBinary(CMD_FOG_ERR_AVG)
		self.send32BitCmd(value)

	def send_GAIN1_CMD(self):
		value = self.top.gain1.spin.value()	
		print('set gain1: ', value)
		self.act.COM.writeBinary(CMD_FOG_GAIN1)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
		
	def send_GAIN2_CMD(self):
		value = self.top.gain2.spin.value()	
		print('set gain2: ', value)
		self.act.COM.writeBinary(CMD_FOG_GAIN2)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
		
	def send_FB_ON_CMD(self):
		value = self.top.fb_on.spin.value()	
		print('set FB on: ', value)
		self.act.COM.writeBinary(CMD_FOG_FB_ON)
		time.sleep(DLY_CMD)
		self.send32BitCmd(value)
	
	def send_DAC_GAIN_CMD(self):
		value = self.top.dac_gain.spin.value()
		print('set DAC gain: ', value)
		self.act.COM.writeBinary(CMD_FOG_DAC_GAIN)
		self.send32BitCmd(value)
	
	def send_CONST_STEP_CMD(self):
		value = self.top.const_step.spin.value()	
		print('set constant step: ', value)
		self.act.COM.writeBinary(CMD_FOG_CONST_STEP)
		self.send32BitCmd(value)
		
	def send_HD_Q(self):
		value = self.top.HD_Q.spin.value()	
		print('set FPGA Q: ', value)
		self.act.COM.writeBinary(CMD_FOG_FPGA_Q)
		self.send32BitCmd(value)
				
	def send_HD_R(self):
		value = self.top.HD_R.spin.value()	
		print('set FPGA R: ', value)
		self.act.COM.writeBinary(CMD_FOG_FPGA_R)
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
		self.act.COM.writeBinary(CMD_FOG_INT_DELAY)
		self.send32BitCmd(value)
				
		

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
			usbConnStatus = self.act.COM.connect_comboBox(baudrate = BAUD_RATE_1, timeout = 1, port_name=self.cp)
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
				# self.act.COM.writeBinary(globals.OP_MODE)
				self.act.COM.writeBinary(CMD_FOG_OUT_START)
				self.send32BitCmd(1)
			else: 				#sync mode
				self.act.COM.writeBinary(CMD_FOG_OUT_START)
				self.send32BitCmd(2)
				
		self.start_time = time.time()
		
		self.act.startRun() # set self.act.runFlag = True
		self.act.start()
		pass

	def buttonStop(self):#set runFlag=0
		self.act.dt_init_flag = 1
		self.act.stopRun()
		
		
	def myThreadStop(self):
		if(globals.TEST_MODE==False): 
			self.act.COM.writeBinary(globals.OP_MODE)
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
		self.step = np.append(self.step, step_f*3600)
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.step = self.step[self.act.data_frame_update_point:]
			self.time = self.time[self.act.data_frame_update_point:]
		if(self.save_cb_flag == True):
			# if(len(data_f) != self.act.data_frame_update_point):
				# data_f = np.append(data_f, 999)
			np.savetxt(self.f, (np.vstack([time_f, data_f, step, PD_temperature])).T, fmt='%5.5f, %5.5f, %d, %3.1f')
		# print(time)
		# print('len(time):', len(time))
		# print('len(data):', len(data))
		# print('step avg: ', np.round(np.average(self.step), 4), end=', ')
		# print('stdev: ', np.round(np.std(self.step), 4))
		self.top.com_plot1.ax.plot(self.time, self.data, color = 'b', linestyle = '-', marker = '', label="err")
		# self.top.com_plot1.ax.plot(self.time, self.step, color = 'r', linestyle = '-', marker = '', label="step")
		# self.top.com_plot1.ax.plot(self.data, color = 'b', linestyle = '-', marker = '*', label="err")
		# self.top.com_plot1.ax.plot(self.step, color = 'r', linestyle = '-', marker = '*', label="err")
		self.top.com_plot1.figure.canvas.draw()		
		self.top.com_plot1.figure.canvas.flush_events()
		if(self.act.runFlag):
			# print('update rate: ', np.round(update_rate, 1), end=', ')
			# print(np.round(np.average(self.step), 3), end='\t')
			# print(np.round(np.std(self.step), 3))
			pass
		self.top.com_plot2.ax.plot(self.time, self.step, color = 'r', linestyle = '-', marker = '', label="step")
		# self.top.com_plot2.ax.plot(self.step, color = 'r', linestyle = '-', marker = '*', label="step")
		self.top.com_plot2.figure.canvas.draw()		
		self.top.com_plot2.figure.canvas.flush_events()
		
		

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
