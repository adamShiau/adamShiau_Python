import os 
import sys 
sys.path.append("../") 
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
import gyro_Widget4 as UI 
import gyro_Action4 as ACT
import gyro_Globals as globals
TITLE_TEXT = "OPEN LOOP"
VERSION_TEXT = 'fog open loop 2020/12/25'
READOUT_FILENAME = "Signal_Read_Out.txt"
MAX_SAVE_INDEX = 3000
TEST_MODE = False
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
MOD_FREQ = '0 '
MOD_AMP_H = '1 '
MOD_AMP_L = '2 '
ERR_OFFSET = '3 '
POLARITY = '4 '
WAIT_CNT = '5 '
ERR_TH = '6 '
ERR_AVG = '7 '
GAIN1 = '8 '
STEP_MAX = '9 '
V2PI = '10 '
V2PIN = '11 '
OPENLOOP_START = '12 '
STEP_TRIG_DLY = '13 '
FB_ON = GAIN1
'''adc conversion '''
ADC_COEFFI = (1/8192)
TIME_COEFFI = 0.0001
''' define initial value'''
# MOD_H_INIT = 0
# MOD_L_INIT = -1000
MOD_H_INIT = 0
MOD_L_INIT = -2700
FREQ_INIT = 111
ERR_OFFSET_INIT = 0
POLARITY_INIT = 0
WAIT_CNT_INIT = 56
ERR_TH_INIT = 0
ERR_AVG_INIT = 5
GAIN_SEL_INIT = 11
STEP_MAX_INIT = 10000
V2PI_INIT = 30000
V2PIN_INIT = -30000
STEP_TRIG_DLY_INIT = 0

CMD_MOD_H_INIT = MOD_AMP_H + str(MOD_H_INIT) + '\n'
CMD_MOD_L_INIT = MOD_AMP_L + str(MOD_L_INIT) + '\n'
CMD_ERR_OFFSET_INIT = ERR_OFFSET + str(ERR_OFFSET_INIT) + '\n'
CMD_POLARITY_INIT = POLARITY + str(POLARITY_INIT) + '\n'
CMD_WAIT_CNT_INIT = WAIT_CNT + str(WAIT_CNT_INIT) + '\n'
CMD_ERR_TH_INIT = ERR_TH + str(ERR_TH_INIT) + '\n'
CMD_ERR_AVG_INIT = ERR_AVG + str(ERR_AVG_INIT) + '\n'
CMD_GAIN_SEL_INIT = GAIN1 + str(GAIN_SEL_INIT) + '\n'
CMD_OPENLOOP_INIT = GAIN1 + str(15) + '\n'
CMD_STEP_MAX_INIT = STEP_MAX + str(STEP_MAX_INIT) + '\n'
CMD_V2PI_INIT = V2PI + str(V2PI_INIT) + '\n'
CMD_V2PIN_INIT = V2PIN + str(V2PIN_INIT) + '\n'
CMD_FREQ_INIT = MOD_FREQ + str(FREQ_INIT) + '\n' 
CMD_STEP_TRIG_DLY_INIT = STEP_TRIG_DLY + str(STEP_TRIG_DLY_INIT) + '\n' 
# CMD_MODE_INIT = GAIN1 + str(15) + '\n' 
class mainWindow(QMainWindow):
	# Kal_status = 0
	
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
		self.thread1 = QThread() #開一個thread
		self.linkFunction()
		# self.disableBtn()
		self.get_rbVal()
		self.data = np.empty(0)
		self.step = np.empty(0)
		self.time = np.empty(0)
		self.setInitValue(False)
		self.setBtnStatus(False)
	
	# def send_initial_value(self):
		
	
	# def disableBtn(self):
		# self.top.usb.btn.setEnabled(False)
		# self.top.read_btn.read.setEnabled(False)
		# self.top.stop_btn.stop.setEnabled(False)
		
	# def enableBtn(self):
		# self.top.usb.btn.setEnabled(True)
		# self.top.read_btn.read.setEnabled(True)
		# self.top.stop_btn.stop.setEnabled(True)
	
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
		
		# openFile_Menu = mainMenu.addMenu("open file")
		# openFile = QAction("open", self)
		# openFile.triggered.connect(self.openFileBox)
		# openFile_Menu.addAction(openFile)
		

	def linkFunction(self):
		''' btn connect '''
		self.top.usb.bt_update.clicked.connect(self.update_comport)
		self.top.usb.cs.currentIndexChanged.connect(self.uadate_comport_label)
		self.top.usb.bt_connect.clicked.connect(self.usbConnect)
		self.top.read_btn.bt.clicked.connect(self.thread1Start) # set runFlag=1
		self.top.stop_btn.bt.clicked.connect(self.buttonStop) # set runFlag=0
		''' thread connect '''
		# self.thread1.started.connect(lambda:self.act.updateOpenLoop(Kal_status = self.Kal_status))
		self.thread1.started.connect(self.act.updateOpenLoop)

		''' emit connect '''
		self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		self.act.openLoop_updata3.connect(self.plotOpenLoop)
		#btn enable signal
		self.usbconnect_status.connect(self.setBtnStatus) #確定usb連接成功時才enable btn
		self.usbconnect_status.connect(self.setInitValue)
		
		''' radio btn'''
		self.top.Kal_rb.toggled.connect(lambda:self.rb_toggled(self.top.Kal_rb))
		
		''' spin box connect'''
		self.top.wait_cnt.spin.valueChanged.connect(self.send_WAIT_CNT_CMD)
		self.top.avg.spin.valueChanged.connect(self.send_AVG_CMD)
		self.top.mod_H.spin.valueChanged.connect(self.send_MOD_H_CMD)
		self.top.mod_L.spin.valueChanged.connect(self.send_MOD_L_CMD)
		self.top.freq.spin.valueChanged.connect(self.send_FREQ_CMD)
		self.top.err_th.spin.valueChanged.connect(self.send_ERR_TH_CMD)
		self.top.err_offset.spin.valueChanged.connect(self.send_ERR_OFFSET_CMD)
		self.top.polarity.spin.valueChanged.connect(self.send_POLARITY_CMD)
		
		self.top.gain1.spin.valueChanged.connect(self.send_GAIN1_CMD)
		self.top.step_max.spin.valueChanged.connect(self.send_STEP_MAX_CMD)
		self.top.v2pi.spin.valueChanged.connect(self.send_V2PI_CMD)
		self.top.v2piN.spin.valueChanged.connect(self.send_V2PIN_CMD)
		self.top.fb_on.spin.valueChanged.connect(self.send_FB_ON_CMD)
		
		self.top.Q.spin.valueChanged.connect(self.update_kal_Q)
		self.top.R.spin.valueChanged.connect(self.update_kal_R)
		self.top.trigDelay.spin.valueChanged.connect(self.send_trigDelay_CMD)
		
	def setInitValue(self, EN):
		if(EN):
			self.act.COM.writeLine(CMD_MOD_H_INIT)
			self.act.COM.writeLine(CMD_MOD_L_INIT)
			self.act.COM.writeLine(CMD_ERR_OFFSET_INIT)
			self.act.COM.writeLine(CMD_POLARITY_INIT)
			self.act.COM.writeLine(CMD_WAIT_CNT_INIT)
			self.act.COM.writeLine(CMD_ERR_TH_INIT)
			self.act.COM.writeLine(CMD_ERR_AVG_INIT)
			# self.act.COM.writeLine(CMD_GAIN_SEL_INIT)
			self.act.COM.writeLine(CMD_STEP_MAX_INIT)
			self.act.COM.writeLine(CMD_V2PI_INIT)
			self.act.COM.writeLine(CMD_V2PIN_INIT)
			self.act.COM.writeLine(CMD_FREQ_INIT)
			self.act.COM.writeLine(CMD_STEP_TRIG_DLY_INIT)
			# self.act.COM.writeLine(CMD_MODE_INIT)
			self.top.mod_H.spin.setValue(MOD_H_INIT)
			self.top.mod_L.spin.setValue(MOD_L_INIT)
			self.top.err_offset.spin.setValue(ERR_OFFSET_INIT)
			self.top.polarity.spin.setValue(POLARITY_INIT)
			self.top.wait_cnt.spin.setValue(WAIT_CNT_INIT)
			self.top.err_th.spin.setValue(ERR_TH_INIT)
			self.top.avg.spin.setValue(ERR_AVG_INIT)
			self.top.gain1.spin.setValue(GAIN_SEL_INIT)
			self.top.step_max.spin.setValue(STEP_MAX_INIT)
			self.top.v2pi.spin.setValue(V2PI_INIT)
			self.top.v2piN.spin.setValue(V2PIN_INIT)
			self.top.freq.spin.setValue(FREQ_INIT)
			self.top.fb_on.spin.setValue(0)
			self.act.COM.writeLine(CMD_OPENLOOP_INIT)
			self.top.Q.spin.setValue(globals.kal_Q)
			self.top.R.spin.setValue(globals.kal_R)
			self.top.trigDelay.spin.setValue(STEP_TRIG_DLY_INIT)

		
	def setBtnStatus(self, flag):
		self.top.read_btn.bt.setEnabled(flag)
		self.top.stop_btn.bt.setEnabled(flag)
		
	''' UART command '''
	def send_ERR_OFFSET_CMD(self):
		value = self.top.err_offset.spin.value()	
		cmd = ERR_OFFSET + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_POLARITY_CMD(self):
		value = self.top.polarity.spin.value()	
		cmd = POLARITY + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_WAIT_CNT_CMD(self):
		value = self.top.wait_cnt.spin.value()	
		cmd = WAIT_CNT + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_AVG_CMD(self):
		value = self.top.avg.spin.value()	
		cmd = ERR_AVG + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
	
	def send_MOD_H_CMD(self):
		value = self.top.mod_H.spin.value()	
		cmd = MOD_AMP_H + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
	
	def send_MOD_L_CMD(self):
		value = self.top.mod_L.spin.value()	
		cmd = MOD_AMP_L + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_GAIN1_CMD(self):
		value = self.top.gain1.spin.value()	
		cmd = GAIN1 + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_STEP_MAX_CMD(self):
		value = self.top.step_max.spin.value()	
		cmd = STEP_MAX + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_V2PI_CMD(self):
		value = self.top.v2pi.spin.value()	
		cmd = V2PI + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_V2PIN_CMD(self):
		value = self.top.v2piN.spin.value()	
		cmd = V2PIN + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_ERR_TH_CMD(self):
		value = self.top.err_th.spin.value()	
		cmd = ERR_TH + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	
	def send_FB_ON_CMD(self):
		value = self.top.fb_on.spin.value()	
		if(value==0):
			cmd = GAIN1 + str(15) + '\n'
		elif(value==1):
			cmd = GAIN1 + str(self.top.gain1.spin.value()) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
	
	def send_FREQ_CMD(self):
		value = self.top.freq.spin.value()	
		self.top.freq.lb.setText(str(round(1/(2*(value+1)*10e-6),2))+' KHz')
		cmd = MOD_FREQ + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def send_trigDelay_CMD(self):
		value = self.top.trigDelay.spin.value()	
		cmd = STEP_TRIG_DLY + str(value) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
	def update_kal_Q(self):
		value = self.top.Q.spin.value()
		globals.kal_Q = value
		print('kal_Q:', globals.kal_Q)
		
	def update_kal_R(self):
		value = self.top.R.spin.value()
		globals.kal_R = value
		print('kal_R:', globals.kal_R)
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
			
	def buttonStop(self):#set runFlag=0
		# self.act.setStop()
		cmd = OPENLOOP_START + str(0) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		
		self.act.runFlag = False
		self.act.dt_init_flag = 1
	
	def rb_toggled(self, rb):
		globals.kal_status = rb.isChecked()
		print('main:', globals.kal_status)
		
	def get_rbVal(self):
		globals.Kal_status = self.top.Kal_rb.isChecked()
		print('Kal:', globals.Kal_status)
	
	def open_file(self, filename):
		self.f=open(filename, 'w')
		start_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.f.writelines('#' + start_time_header + '\n')
	
	
	def thread1Start(self):
		self.save_status = self.openFileBox()
		cmd = OPENLOOP_START + str(1) + '\n'
		print(cmd)
		self.act.COM.writeLine(cmd)
		# file_name = self.top.save_edit.edit.text() 
		# self.f=open(file_name,'a')
		# self.f=open('er','a')
		self.act.runFlag = True
		self.thread1.start()
		self.act.COM.port.flushInput()
		
		# self.top.com_plot.ax1.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		
	def myThreadStop(self):
		self.thread1.quit() 
		self.thread1.wait()
		if(self.save_status):
			stop_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			self.f.writelines('#' + stop_time_header + '\n')
			self.f.close()
		self.data  = np.empty(0)
		self.time  = np.empty(0)
		self.step  = np.empty(0)
		
		
	def plotOpenLoop(self, time, data, step):
		if(self.act.runFlag):
			self.top.com_plot1.ax.clear()
			self.top.com_plot2.ax.clear()
		data_f = data*ADC_COEFFI 
		time_f = time*TIME_COEFFI
		# data_f = data 
		self.data  = np.append(self.data, data_f)
		self.time  = np.append(self.time, time_f)
		self.step = np.append(self.step, step)
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.step = self.step[self.act.data_frame_update_point:]
			self.time = self.time[self.act.data_frame_update_point:]
		
		if(self.save_status):
			np.savetxt(self.f, (np.vstack([time_f, data_f, step])).T, fmt='%5.5f, %5.5f, %5.5f')
		# print(time)
		# print('len(time):', len(time))
		# print('len(data):', len(data))
		self.top.com_plot1.ax.plot(self.time, self.data, color = 'r', linestyle = '-', marker = '*', label="err")
		self.top.com_plot1.figure.canvas.draw()		
		self.top.com_plot1.figure.canvas.flush_events()
		
		self.top.com_plot2.ax.plot(self.time, self.step, color = 'r', linestyle = '-', marker = '*', label="step")
		self.top.com_plot2.figure.canvas.draw()		
		self.top.com_plot2.figure.canvas.flush_events()
		
	def plotCloseLoop(self, time, data):
		if(self.act.runFlag):
			self.top.com_plot.ax.clear()
		# data_f = data*ADC_COEFFI 
		data_f = data*ADC_COEFFI 
		time_f = time*TIME_COEFFI
		self.data  = np.append(self.data, data_f)
		self.time  = np.append(self.time, time_f)
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.time = self.time[self.act.data_frame_update_point:]
		
		if(self.save_status):
			np.savetxt(self.f, (np.vstack([time_f, data_f])).T, fmt='%5.5f, %5.5f')
		# print(time)
		# print('len(time):', len(time))
		# print('len(data):', len(data))
		self.top.com_plot.ax.plot(self.time, self.data, color = 'r', linestyle = '-', marker = '*', label="open")
		self.top.com_plot.figure.canvas.draw()		
		self.top.com_plot.figure.canvas.flush_events()
		
	def plotOpenLoop_old(self, data):
		if(self.act.runFlag):
			self.top.com_plot.ax.clear()
		data_f = data*ADC_COEFFI
		self.data  = np.append(self.data, data_f)
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.time = self.time[self.act.data_frame_update_point:]
		
		if(self.save_status):
			np.savetxt(self.f, (np.vstack([data_f])).T, fmt='%5.5f')
		
		self.top.com_plot.ax.plot(self.data, color = 'r', linestyle = '-', marker = '*', label="open")
		self.top.com_plot.figure.canvas.draw()		
		self.top.com_plot.figure.canvas.flush_events()
		

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
