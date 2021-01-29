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
import gyro_Widget as UI 
import gyro_Action as ACT
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
OPENLOOP_START = '12 '
FB_ON = GAIN1
'''adc conversion '''
ADC_COEFFI = (2.5/8192)
TIME_COEFFI = 0.0001

class mainWindow(QMainWindow):
	# wz_offset = 0
	# wzVth = 0
	# wz200_offset = 0
	# wx_offset = 0
	# wxVth = 0
	# wy_offset = 0
	# wyVth = 0
	# ax_offset = 0
	# axVth = 0
	# ay_offset = 0
	# ayVth = 0
	# MV_status = 0
	wait_cnt = 10
	avg = 0
	mod_H = 10000
	mod_L = -10000
	freq = 100
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
		self.data = np.empty(0)
		self.time = np.empty(0)
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
		self.thread1.started.connect(self.act.updateOpenLoop)

		''' emit connect '''
		self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		self.act.openLoop_updata2.connect(self.plotOpenLoop)
		#btn enable signal
		self.usbconnect_status.connect(self.setBtnStatus) #確定usb連接成功時才enable btn
		
		''' spin box connect'''
		self.top.wait_cnt.spin.valueChanged.connect(self.send_WIT_CNT_CMD)
		self.top.avg.spin.valueChanged.connect(self.send_AVG_CMD)
		self.top.mod_H.spin.valueChanged.connect(self.send_MOD_H_CMD)
		self.top.mod_L.spin.valueChanged.connect(self.send_MOD_L_CMD)
		self.top.freq.spin.valueChanged.connect(self.send_FREQ_CMD)
		self.top.err_offset.spin.valueChanged.connect(self.send_ERR_OFFSET_CMD)
		self.top.polarity.spin.valueChanged.connect(self.send_POLARITY_CMD)
		
		self.top.gain1.spin.valueChanged.connect(self.send_GAIN1_CMD)
		self.top.step_max.spin.valueChanged.connect(self.send_STEP_MAX_CMD)
		self.top.v2pi.spin.valueChanged.connect(self.send_V2PI_CMD)
		self.top.fb_on.spin.valueChanged.connect(self.send_FB_ON_CMD)
		
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
		
	def send_WIT_CNT_CMD(self):
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
		
	def open_file(self, filename):
		self.f=open(filename, 'w')
		start_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.f.writelines('#' + start_time_header + '\n')
	
	def caliThreadStart(self):
		self.act.runFlag = True
		self.thread_cali.start()
		
	def caliThreadStop(self):
		self.act.runFlag = False 
		wzOffset_cp = float(self.top.wzOffset_lb.val.text())
		wzVth_cp = round(float(self.top.diffwzStd_lb.val.text())*3,3)
		wz200Offset_cp = float(self.top.wz200Offset_lb.val.text())
		wxOffset_cp = float(self.top.wxOffset_lb.val.text())
		wxVth_cp = round(float(self.top.diffwxStd_lb.val.text())*3,3)
		wyOffset_cp = float(self.top.wyOffset_lb.val.text())
		wyVth_cp = round(float(self.top.diffwyStd_lb.val.text())*3,3)
		
		axOffset_cp = float(self.top.axOffset_lb.val.text())
		axVth_cp = round(float(self.top.diffaxStd_lb.val.text())*3,3)
		ayOffset_cp = float(self.top.ayOffset_lb.val.text())
		ayVth_cp = round(float(self.top.diffayStd_lb.val.text())*3,3)
		if(wzVth_cp < 1):
			wzVth_cp = 1
		if(wxVth_cp < 1):
			wxVth_cp = 1
		if(wyVth_cp < 1):
			wyVth_cp = 1
		if(axVth_cp < 1):
			axVth_cp = 1
		if(ayVth_cp < 1):
			ayVth_cp = 1
			
		self.top.wzOffset_le.setText(str(wzOffset_cp))
		self.top.wzVth_le.setText(str(wzVth_cp))
		self.wz_offset = wzOffset_cp
		self.wzVth = wzVth_cp
		
		self.top.wz200Offset_le.setText(str(wz200Offset_cp))
		self.wz200_offset = wz200Offset_cp
		
		self.top.wxOffset_le.setText(str(wxOffset_cp))
		self.top.wxVth_le.setText(str(wxVth_cp))
		self.wx_offset = wxOffset_cp
		self.wxVth = wxVth_cp
		
		self.top.wyOffset_le.setText(str(wyOffset_cp))
		self.top.wyVth_le.setText(str(wyVth_cp))
		self.wy_offset = wyOffset_cp
		self.wyVth = wyVth_cp
		
		self.top.axOffset_le.setText(str(axOffset_cp))
		self.top.axVth_le.setText(str(axVth_cp))
		self.ax_offset = axOffset_cp
		self.axVth = axVth_cp
		
		self.top.ayOffset_le.setText(str(ayOffset_cp))
		self.top.ayVth_le.setText(str(ayVth_cp))
		self.ay_offset = ayOffset_cp
		self.ayVth = ayVth_cp
		
		self.thread_cali.quit() 
		self.thread_cali.wait()
		self.data  = np.empty(0)
		self.data2 = np.empty(0)
		self.data3 = np.empty(0)
		self.data4 = np.empty(0)
		self.data5 = np.empty(0)
		self.data6 = np.empty(0)
		self.data7 = np.empty(0)
		self.diffdata1 = np.empty(0)
		self.diffdata2 = np.empty(0)
		self.diffdata3 = np.empty(0)
		self.diffdata4 = np.empty(0)
		self.diffdata5 = np.empty(0)
		self.diffdata6 = np.empty(0)
	
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
		# self.data2 = np.empty(0)
		# self.data3 = np.empty(0)
		# self.data4 = np.empty(0)
		# self.data5 = np.empty(0)
		# self.data6 = np.empty(0)
		# self.data7 = np.empty(0)
		# self.dt = np.empty(0)
		# self.thetaz = 0
		# self.thetaz200 = 0
		# self.thetax = 0
		# self.thetay = 0
		# self.speed = 0
		# self.speedx = 0
		# self.speedy = 0
		
		
		
	def plotOpenLoop(self, time, data):
		if(self.act.runFlag):
			self.top.com_plot.ax.clear()
		# data_f = data*ADC_COEFFI 
		data_f = data 
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
		
	def plotCloseLoop(self, time, data):
		if(self.act.runFlag):
			self.top.com_plot.ax.clear()
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
