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
# from py3lib.COMPort import UART 
import numpy as np
# import py3lib
# import py3lib.FileToArray as file
# import py3lib.QuLogger as Qlogger 
# import py3lib.FileToArray as fil2a 
import ADXL355_IMU_Widget2 as UI 
import ADXL355_IMU_Action2_BT as ACT
TITLE_TEXT = "IMU_PLOT"
VERSION_TEXT = 'Compare FOG with MEMS，2020/12/01'
READOUT_FILENAME = "Signal_Read_Out.txt"
MAX_SAVE_INDEX = 3000
DEBUG = 1
track_max = 50
track_min = -50
w_factor = 0.01
TEST_MODE = 0
xlm_factor = 0.000122 #4g / 32768
ADxlm_factor = 0.0000156 #8g
# gyro_factor = 0.00763 #250 / 32768 
gyro_factor = 0.0090 #250 / 32768 
gyro200_factor = 0.0121

# wx_offset = 107.065
# wy_offset = -513.717


class mainWindow(QMainWindow):
	wz_offset = 0
	wzVth = 0
	wz200_offset = 0
	wx_offset = 0
	wxVth = 0
	wy_offset = 0
	wyVth = 0
	ax_offset = 0
	axVth = 0
	ADax_offset = 0
	ay_offset = 0
	ADay_offset = 0
	ayVth = 0
	MV_status = 0
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		# self.COM = act.UART()
		self.setWindowTitle(TITLE_TEXT)
		self.resize(1100,800)
		self.move(0,0)
		self.loggername = "Total"
		self.top = UI.mainWidget()
		self.act = ACT.COMRead_Action(self.loggername)
		self.thread1 = QThread() #開一個thread
		self.thread_cali = QThread()
		self.data = np.empty(0)
		self.data2 = np.empty(0)
		self.data3 = np.empty(0)
		self.data4 = np.empty(0)
		self.data5 = np.empty(0)
		self.data6 = np.empty(0)
		self.data7 = np.empty(0)
		self.data8 = np.empty(0)
		self.data9 = np.empty(0)
		self.data10 = np.empty(0)
		self.diffdata1 = np.empty(0)
		self.diffdata2 = np.empty(0)
		self.diffdata3 = np.empty(0)
		self.diffdata4 = np.empty(0)
		self.diffdata5 = np.empty(0)
		self.diffdata6 = np.empty(0)
		self.thetaz = 0
		self.thetaz200 = 0
		self.thetax = 0
		self.thetay = 0
		self.speed = 0
		self.speedx = 0
		self.speedy = 0
		self.thetaz_arr = np.empty(0)
		self.thetaz200_arr = np.empty(0)
		self.thetax_arr = np.empty(0)
		self.thetay_arr = np.empty(0)
		self.dx_arr = np.zeros(0)
		self.dy_arr = np.zeros(0)
		self.x_arr = np.zeros(0)
		self.y_arr = np.zeros(0)
		self.x_sum = 0
		self.y_sum = 0
		self.dx200_arr = np.zeros(0)
		self.dy200_arr = np.zeros(0)
		self.x200_arr = np.zeros(0)
		self.y200_arr = np.zeros(0)
		self.x200_sum = 0
		self.y200_sum = 0
		self.speed_arr = np.empty(0)
		self.speedx_arr = np.empty(0)
		self.speedy_arr = np.empty(0)
		self.dt = np.empty(0)
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.disableBtn()
		self.get_cbVal()
		self.get_rbVal()
		# self.wz_offset = self.act.offset_wz
	
	def disableBtn(self):
		# self.top.usb.btn.setEnabled(False)
		self.top.read_btn.read.setEnabled(False)
		self.top.stop_btn.stop.setEnabled(False)
		self.top.cali_btn.btn.setEnabled(False)
		self.top.cali_stop_btn.btn.setEnabled(False)
		
	def enableBtn(self):
		# self.top.usb.btn.setEnabled(True)
		self.top.read_btn.read.setEnabled(True)
		self.top.stop_btn.stop.setEnabled(True)
		self.top.cali_btn.btn.setEnabled(True)
		self.top.cali_stop_btn.btn.setEnabled(True)
	
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
		
		self.top.cali_btn.btn.clicked.connect(self.caliThreadStart)
		self.top.cali_stop_btn.btn.clicked.connect(self.caliThreadStop)
		self.top.read_btn.read.clicked.connect(self.myThreadStart) # set runFlag=1
		self.top.stop_btn.stop.clicked.connect(self.buttonStop) # set runFlag=0
		#usb connect
		self.top.usb.bt_update.clicked.connect(self.update_comport)
		self.top.usb.cs.currentIndexChanged.connect(self.uadate_comport_label)
		self.top.usb.bt_connect.clicked.connect(self.usbConnect)
		self.top.usb.bt_connect.clicked.connect(self.enableBtn)
		''' thread connect '''
		self.thread1.started.connect(lambda:self.act.updateADXL_IMUnGYRO(MV_MODE=self.MV_status)) 
		# self.thread1.started.connect(lambda:self.act.updateIMUnGYRO(MV_MODE=self.MV_status))
		# self.thread_cali.started.connect(lambda:self.act.calibrationGYRO(MV_MODE=self.MV_status)) 
		# self.thread_cali.started.connect(lambda:self.act.calibrationIMUnGYRO(MV_MODE=self.MV_status))
		self.thread_cali.started.connect(lambda:self.act.calibrationADXL_IMUnGYRO(MV_MODE=self.MV_status))

		''' emit connect '''
		self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		# self.act.fog_update.connect(self.plotFog) #fog_update emit 接收最新data and dt array
		# self.act.fog_update2.connect(self.plotFog2)  
		# self.act.fog_update7.connect(self.plotXLMDnGYRO)
		# self.act.fog_update7.connect(self.plotGYRO)
		self.act.fog_update8.connect(self.plotIMUnGYRO)
		self.act.fog_update9.connect(self.plotADXLIMUnGYRO)
		self.act.fog_update12.connect(self.calibGYRO)
		# self.act.fog_update13.connect(self.calibIMUnGYRO)
		self.act.fog_update13.connect(self.calibADXLIMUnGYRO)
		
		''' text connect '''
		self.top.wzOffset_le.textChanged.connect(self.updata_para)
		self.top.wzVth_le.textChanged.connect(self.updata_para)
		self.top.wz200Offset_le.textChanged.connect(self.updata_para)
		self.top.wxOffset_le.textChanged.connect(self.updata_para)
		self.top.wxVth_le.textChanged.connect(self.updata_para)
		self.top.wyOffset_le.textChanged.connect(self.updata_para)
		self.top.wyVth_le.textChanged.connect(self.updata_para)
		self.top.axOffset_le.textChanged.connect(self.updata_para)
		self.top.axVth_le.textChanged.connect(self.updata_para)
		self.top.ayOffset_le.textChanged.connect(self.updata_para)
		self.top.ayVth_le.textChanged.connect(self.updata_para)
		self.top.axOffsetAD_le.textChanged.connect(self.updata_para)
		self.top.ayOffsetAD_le.textChanged.connect(self.updata_para)


		
		''' check box '''
		self.top.cb.ax_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.ax_cb))
		self.top.cb.ay_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.ay_cb))
		self.top.cb.wz_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.wz_cb))
		self.top.cb.wz200_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.wz200_cb))
		self.top.cb.v_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.v_cb))
		self.top.cb.vx_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.vx_cb))
		self.top.cb.vy_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.vy_cb))
		self.top.cb.thetaz_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.thetaz_cb))
		self.top.cb.thetaz200_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.thetaz200_cb))
		self.top.cb.x_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.x_cb))
		self.top.cb.y_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.y_cb))
		self.top.cb.track_cb.toggled.connect(lambda:self.cb_toogled(self.top.cb.track_cb))
		
		''' radio btn'''
		self.top.mv_rb.toggled.connect(lambda:self.rb_toggled(self.top.mv_rb))
	
	def rb_toggled(self, rb):
		self.MV_status = rb.isChecked()
		print('MV:', self.MV_status)
		
	def get_rbVal(self):
		self.MV_status = self.top.mv_rb.isChecked()
		print('MV:', self.MV_status)
		
	def cb_toogled(self, cb):
		if(cb.text()=='ax'):
			self.ax_chk = cb.isChecked()
			print('ax:', self.ax_chk)
		elif(cb.text()=='ay'):
			self.ay_chk = cb.isChecked()
			print('ay:', self.ay_chk)
		elif(cb.text()=='wz'):
			self.wz_chk = cb.isChecked()
			print('wz:', self.wz_chk)
		elif(cb.text()=='wz200'):
			self.wz200_chk = cb.isChecked()
			print('wz200:', self.wz200_chk)
		elif(cb.text()=='vx'):
			self.vx_chk = cb.isChecked()
			print('vx:', self.vx_chk)
		elif(cb.text()=='vy'):
			self.vy_chk = cb.isChecked()
			print('vy:', self.vy_chk)
		elif(cb.text()=='x'):
			self.x_chk = cb.isChecked()
			print('x:', self.x_chk)
		elif(cb.text()=='y'):
			self.y_chk = cb.isChecked()
			print('y:', self.y_chk)
		elif(cb.text()=='v'):
			self.v_chk = cb.isChecked()
			print('v:', self.v_chk)
		elif(cb.text()=='thetaz'):
			self.thetaz_chk = cb.isChecked()
			print('thetaz:', self.thetaz_chk)
		elif(cb.text()=='thetaz200'):
			self.thetaz200_chk = cb.isChecked()
			print('thetaz200:', self.thetaz200_chk)
		elif(cb.text()=='track'):
			self.track_chk = cb.isChecked()
			print('track:', self.track_chk)
			
	def get_cbVal(self):
		self.ax_chk = self.top.cb.ax_cb.isChecked()
		print('ax:', self.ax_chk)
		self.ay_chk = self.top.cb.ay_cb.isChecked()
		print('ay:', self.ay_chk)
		self.wz_chk = self.top.cb.wz_cb.isChecked()
		print('wz:', self.wz_chk)
		self.wz200_chk = self.top.cb.wz200_cb.isChecked()
		print('wz200:', self.wz200_chk)
		self.vx_chk = self.top.cb.vx_cb.isChecked()
		print('vx:', self.vx_chk)
		self.vy_chk = self.top.cb.vy_cb.isChecked()
		print('vy:', self.vy_chk)
		self.v_chk = self.top.cb.v_cb.isChecked()
		print('v:', self.v_chk)
		self.thetaz_chk = self.top.cb.thetaz_cb.isChecked()
		print('thetaz:', self.thetaz_chk)
		self.thetaz200_chk = self.top.cb.thetaz200_cb.isChecked()
		print('thetaz200:', self.thetaz200_chk)
		self.x_chk = self.top.cb.x_cb.isChecked()
		print('x:', self.x_chk)
		self.y_chk = self.top.cb.y_cb.isChecked()
		print('y:', self.y_chk)
		self.track_chk = self.top.cb.track_cb.isChecked()
		print('track:', self.track_chk)
	
	def updata_para(self):
		self.wz_offset = float(self.top.wzOffset_le.text())
		self.wzVth = float(self.top.wzVth_le.text())
		self.act.offset_wz = self.wz_offset  
		self.act.wzVth = self.wzVth
		
		self.wz200_offset = float(self.top.wz200Offset_le.text())
		self.act.offset_wz200 = self.wz200_offset  
		
		self.wx_offset = float(self.top.wxOffset_le.text())
		self.wxVth = float(self.top.wxVth_le.text())
		self.act.offset_wx = self.wx_offset  
		self.act.wxVth = self.wxVth
		
		self.wy_offset = float(self.top.wyOffset_le.text())
		self.wyVth = float(self.top.wyVth_le.text())
		self.act.offset_wy = self.wy_offset  
		self.act.wyVth = self.wyVth
		
		self.ax_offset = float(self.top.axOffset_le.text())
		self.axVth = float(self.top.axVth_le.text())
		self.act.offset_ax = self.ax_offset  
		# self.act.axVth = self.axVth
		self.act.axVth = 0
		
		self.ADax_offset = float(self.top.axOffsetAD_le.text())
		self.act.offset_ADax = self.ADax_offset 
		
		self.ay_offset = float(self.top.ayOffset_le.text())
		self.ayVth = float(self.top.wyVth_le.text())
		self.act.offset_ay = self.ay_offset  
		# self.act.ayVth = self.ayVth
		self.act.ayVth = 0
		
		self.ADay_offset = float(self.top.ayOffsetAD_le.text())
		self.act.offset_ADay = self.ADay_offset
		print('change')
		# print(type(self.wz_offset), end=', ')
		# print(self.wz_offset)
		# print(type(self.wzVth), end=', ')
		# print(self.wzVth)
	
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
		print(self.cp);
		if (TEST_MODE):
			usbConnStatus = True
		else:
			usbConnStatus = self.act.COM.connect_comboBox(baudrate = 115200, timeout = 1, port_name=self.cp)
		print("status:" + str(usbConnStatus))
		if usbConnStatus:
			self.top.usb.SetConnectText(Qt.blue, self.cp + " Connect")
			print("Connect build")
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)
			print("Connect failed")
			
# """ end of comport functin """

	def buttonStop(self):#set runFlag=0
		# self.act.setStop()
		self.act.runFlag = False
		self.act.dt_init_flag = 1
		self.thetax_arr = np.empty(0)
		self.thetay_arr = np.empty(0)
		self.thetaz_arr = np.empty(0)
		self.thetaz200_arr = np.empty(0)
		self.speedx_arr = np.empty(0)
		self.speedy_arr = np.empty(0)
		self.speed_arr = np.empty(0)
		self.x_arr = np.zeros(0)
		self.y_arr = np.zeros(0)
		self.x_sum = 0
		self.y_sum = 0
		self.dx_arr = np.zeros(0)
		self.dy_arr = np.zeros(0)
		self.x200_arr = np.zeros(0)
		self.y200_arr = np.zeros(0)
		self.x200_sum = 0
		self.y200_sum = 0
		self.dx200_arr = np.zeros(0)
		self.dy200_arr = np.zeros(0)
		self.top.com_plot.ax2.clear()
		
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
		ADaxOffset_cp = float(self.top.axOffsetAD_lb.val.text())
		axVth_cp = round(float(self.top.diffaxStd_lb.val.text())*3,3)
		ayOffset_cp = float(self.top.ayOffset_lb.val.text())
		ADayOffset_cp = float(self.top.ayOffsetAD_lb.val.text())
		ayVth_cp = round(float(self.top.diffayStd_lb.val.text())*3,3)
		# print("ADaxOffset_cp:", ADaxOffset_cp)
		# print("ADayOffset_cp:", ADayOffset_cp)
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
		
		self.top.axOffsetAD_le.setText(str(ADaxOffset_cp))
		self.ADax_offset = ADaxOffset_cp
		
		self.top.ayOffsetAD_le.setText(str(ADayOffset_cp))
		self.ADay_offset = ADayOffset_cp
		
		self.thread_cali.quit() 
		self.thread_cali.wait()
		self.data  = np.empty(0)
		self.data2 = np.empty(0)
		self.data3 = np.empty(0)
		self.data4 = np.empty(0)
		self.data5 = np.empty(0)
		self.data6 = np.empty(0)
		self.data7 = np.empty(0)
		self.data8 = np.empty(0)
		self.data9 = np.empty(0)
		self.data10 = np.empty(0)
		self.diffdata1 = np.empty(0)
		self.diffdata2 = np.empty(0)
		self.diffdata3 = np.empty(0)
		self.diffdata4 = np.empty(0)
		self.diffdata5 = np.empty(0)
		self.diffdata6 = np.empty(0)
	
	def myThreadStart(self):
		self.save_status = self.openFileBox()
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
		self.data2 = np.empty(0)
		self.data3 = np.empty(0)
		self.data4 = np.empty(0)
		self.data5 = np.empty(0)
		self.data6 = np.empty(0)
		self.data7 = np.empty(0)
		self.data8 = np.empty(0)
		self.data9 = np.empty(0)
		self.data10 = np.empty(0)
		self.dt = np.empty(0)
		self.thetaz = 0
		self.thetaz200 = 0
		self.thetax = 0
		self.thetay = 0
		self.speed = 0
		self.speedx = 0
		self.speedy = 0
		
		
	def plotFOGnXLMD(self, data_fog, data_ax, data_ay, data_az, dt):
		
		if(self.act.runFlag):
			self.top.com_plot.ax1.clear()
			self.top.com_plot.ax2.clear()
			
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.data3 = self.data3[self.act.data_frame_update_point:]
			self.data4 = self.data4[self.act.data_frame_update_point:]
			self.dt = self.dt[self.act.data_frame_update_point:]
		data_fog_f = data_fog*w_factor
		data_ax_f = data_ax*xlm_factor
		data_ay_f = data_ay*xlm_factor
		data_az_f = data_az*xlm_factor
		self.data = np.append(self.data, data_fog_f)
		self.data2 = np.append(self.data2, data_ax_f)
		self.data3 = np.append(self.data3, data_ay_f)
		self.data4 = np.append(self.data4, data_az_f)
		self.dt = np.append(self.dt, dt)
		if(self.save_status):
			np.savetxt(self.f, (np.vstack([dt,data_fog_f, data_ax_f, data_ay_f, data_az_f])).T, fmt='%.2f,%.5f,%.5f,%.5f,%.5f')
		if(DEBUG) :
			print('len(data_fog)', len(self.data))
			print('len(data_ax)', len(self.data2))
			print('len(data_ay)', len(self.data3))
			print('len(data_az)', len(self.data4))
			print('len(dt)', len(self.dt))
		colors = np.array(['r','g','b'])
		self.top.com_plot.ax1.set_ylabel("angular velocity(degree/hr)")
		self.top.com_plot.ax1.plot(self.dt, self.data, color = 'k', linestyle = '-', marker = '')
		self.top.com_plot.ax2.set_ylabel("acceleration(g)")
		self.top.com_plot.ax2.set_xlabel("time(s)")
		# self.top.com_plot.ax2.plot(self.dt, self.data2, self.dt, self.data3,  self.dt, self.data4, color = colors,linestyle = '-', marker = '')
		self.top.com_plot.ax2.plot(self.dt, self.data2, color = 'r', linestyle = '-', marker = '', label="ax")
		self.top.com_plot.ax2.plot(self.dt, self.data3, color = 'g', linestyle = '-', marker = '', label="ay")
		self.top.com_plot.ax2.plot(self.dt, self.data4, color = 'b', linestyle = '-', marker = '', label="az")
		self.top.com_plot.ax2.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.plot(self.dt, self.data2, color = 'red', linestyle = '-', marker = '')
		# self.top.com_plot.ax3.set_ylabel("ay")
		# self.top.com_plot.ax3.plot(self.dt, self.data3, color = 'red', linestyle = '-', marker = '')
		# self.top.com_plot.ax4.set_ylabel("az")
		# self.top.com_plot.ax4.plot(self.dt, self.data4, color = 'red', linestyle = '-', marker = '')
		
		self.top.com_plot.figure.canvas.draw()
		
		# self.top.com_plot.ax3.clear()
		# self.top.com_plot.ax4.clear()
		self.top.com_plot.figure.canvas.flush_events()
		
	def plotXLMDnGYRO(self, data_ax, data_ay, data_az, data_wx, data_wy, data_wz, dt):
		
		if(self.act.runFlag):
			self.top.com_plot.ax1.clear()
			self.top.com_plot.ax2.clear()
			
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.data3 = self.data3[self.act.data_frame_update_point:]
			self.data4 = self.data4[self.act.data_frame_update_point:]
			self.data5 = self.data5[self.act.data_frame_update_point:]
			self.data6 = self.data6[self.act.data_frame_update_point:]
			self.dt = self.dt[self.act.data_frame_update_point:]
		data_ax_f = data_ax*xlm_factor
		data_ay_f = data_ay*xlm_factor
		data_az_f = data_az*xlm_factor
		data_wx_f = data_wx*gyro_factor
		data_wy_f = data_wy*gyro_factor
		data_wz_f = data_wz*gyro_factor
		self.data  = np.append(self.data,  data_ax_f)
		self.data2 = np.append(self.data2, data_ay_f)
		self.data3 = np.append(self.data3, data_az_f)
		self.data4 = np.append(self.data4, data_wx_f)
		self.data5 = np.append(self.data5, data_wy_f)
		self.data6 = np.append(self.data6, data_wz_f)
		self.dt = np.append(self.dt, dt)
		if(self.save_status):
			np.savetxt(self.f, (np.vstack([dt,data_ax_f, data_ay_f, data_az_f, data_wx_f, data_wy_f, data_wz_f])).T, fmt='%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f')
		if(DEBUG) :
			print('len(data_ax)', len(self.data))
			print('len(data_ay)', len(self.data2))
			print('len(data_az)', len(self.data3))
			print('len(data_wx)', len(self.data4))
			print('len(data_wy)', len(self.data5))
			print('len(data_wz)', len(self.data6))
			print('len(dt)', len(self.dt))
		self.top.com_plot.ax1.set_ylabel("angular velocity(dps)")
		self.top.com_plot.ax1.plot(self.dt, self.data4, color = 'r', linestyle = '-', marker = '', label="wx")
		self.top.com_plot.ax1.plot(self.dt, self.data5, color = 'g', linestyle = '-', marker = '', label="wy")
		self.top.com_plot.ax1.plot(self.dt, self.data6, color = 'b', linestyle = '-', marker = '', label="wz")
		self.top.com_plot.ax1.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		
		self.top.com_plot.ax2.set_ylabel("acceleration(g)")
		self.top.com_plot.ax2.set_xlabel("time(s)")
		self.top.com_plot.ax2.plot(self.dt, self.data, color = 'r', linestyle = '-', marker = '' , label="ax")
		self.top.com_plot.ax2.plot(self.dt, self.data2, color = 'g', linestyle = '-', marker = '', label="ay")
		self.top.com_plot.ax2.plot(self.dt, self.data3, color = 'b', linestyle = '-', marker = '', label="az")
		self.top.com_plot.ax2.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.plot(self.dt, self.data2, color = 'red', linestyle = '-', marker = '')
		# self.top.com_plot.ax3.set_ylabel("ay")
		# self.top.com_plot.ax3.plot(self.dt, self.data3, color = 'red', linestyle = '-', marker = '')
		# self.top.com_plot.ax4.set_ylabel("az")
		# self.top.com_plot.ax4.plot(self.dt, self.data4, color = 'red', linestyle = '-', marker = '')
		
		self.top.com_plot.figure.canvas.draw()
		
		# self.top.com_plot.ax3.clear()
		# self.top.com_plot.ax4.clear()
		self.top.com_plot.figure.canvas.flush_events()
		
	def plotIMUnGYRO(self, data_ax, data_ay, data_az, data_wx, data_wy, data_wz, data_wz200, dt):
		if(self.act.runFlag):
			self.top.com_plot.ax1.clear()
			self.top.com_plot.ax2.clear()
			# if(not self.track_chk):
				# self.top.com_plot.ax2.clear()
		dt = dt*1e-6
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.data3 = self.data3[self.act.data_frame_update_point:]
			self.data4 = self.data4[self.act.data_frame_update_point:]
			self.data5 = self.data5[self.act.data_frame_update_point:]
			self.data6 = self.data6[self.act.data_frame_update_point:]
			self.data7 = self.data7[self.act.data_frame_update_point:]
			self.dt = self.dt[self.act.data_frame_update_point:]
		data_ax_f = (data_ax-self.ax_offset)*xlm_factor
		data_ay_f = (data_ay-self.ay_offset)*xlm_factor
		data_az_f = (data_az-0)*xlm_factor
		data_wx_f = (data_wx-self.wx_offset)*gyro_factor
		data_wy_f = (data_wy-self.wy_offset)*gyro_factor
		data_wz_f = (data_wz-self.wz_offset)*gyro_factor
		data_wz200_f = (data_wz200-self.wz200_offset)*gyro200_factor/3600 #convert to DPS
		
		self.thetaz = self.thetaz - np.sum(data_wz_f)*0.01 #負號是方向判斷的問題
		self.thetaz_arr = np.append(self.thetaz_arr, self.thetaz)
		self.thetaz200 = self.thetaz200 - np.sum(data_wz200_f)*0.01 #負號是方向判斷的問題
		self.thetaz200_arr = np.append(self.thetaz200_arr, self.thetaz200)
		self.thetax = self.thetax + np.sum(data_wx_f)*0.01
		self.thetax_arr = np.append(self.thetax_arr, self.thetax)
		self.thetay = self.thetay + np.sum(data_wy_f)*0.01
		self.thetay_arr = np.append(self.thetay_arr, self.thetay)
		self.speedx = self.speedx + np.sum(data_ax_f)*9.8*0.01
		self.speedx_arr = np.append(self.speedx_arr, self.speedx)
		self.speedy = self.speedy + np.sum(data_ay_f)*9.8*0.01
		self.speedy_arr = np.append(self.speedy_arr, self.speedy)
		self.speed = np.sqrt(np.square(self.speedx)+np.square(self.speedy))
		self.speed_arr = np.append(self.speed_arr, self.speed)
		
		''' for track plot'''
		theta = 90 - self.thetaz
		theta200 = 90 - self.thetaz200
		'''
		dx = dr*cos(theta), dr = vdt
		v = 1 m/s
		dt = data_frame_update_point*self.act.TIME_PERIOD 
		'''
		dx = np.cos(theta*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
		dy = np.sin(theta*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.x_sum = self.x_sum + dx
		self.y_sum = self.y_sum + dy
		
		dx200 = np.cos(theta200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
		dy200 = np.sin(theta200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.x200_sum = self.x200_sum + dx200
		self.y200_sum = self.y200_sum + dy200
		
		self.top.theta_lb.setText(str(round(self.thetaz,2)))
		self.top.theta_lb.setStyleSheet('color: blue')
		self.top.theta200_lb.setText(str(round(self.thetaz200,2)))
		self.top.theta200_lb.setStyleSheet('color: red')
		self.top.buffer_lb.setText(str(self.act.bufferSize))
		
		self.dx_arr = np.append(self.dx_arr, dx)
		self.dy_arr = np.append(self.dy_arr, dy)
		self.x_arr = np.append(self.x_arr, self.x_sum)
		self.y_arr = np.append(self.y_arr, self.y_sum)
		
		self.dx200_arr = np.append(self.dx200_arr, dx200)
		self.dy200_arr = np.append(self.dy200_arr, dy200)
		self.x200_arr = np.append(self.x200_arr, self.x200_sum)
		self.y200_arr = np.append(self.y200_arr, self.y200_sum)
		
		if (len(self.thetaz_arr) >= 10):
			self.thetaz_arr = self.thetaz_arr[1:]
			self.thetaz200_arr = self.thetaz200_arr[1:]
			self.thetax_arr = self.thetax_arr[1:]
			self.thetay_arr = self.thetay_arr[1:]
			self.speedx_arr = self.speedx_arr[1:]
			self.speedy_arr = self.speedy_arr[1:]
			self.speed_arr = self.speed_arr[1:]
			self.dx_arr = self.dx_arr[1:]
			self.dy_arr = self.dy_arr[1:]
			self.dx200_arr = self.dx200_arr[1:]
			self.dy200_arr = self.dy200_arr[1:]
			# self.x_arr = self.x_arr[1:]
			# self.y_arr = self.y_arr[1:]
		# print(np.sum(data_wz_f))
		
		self.data  = np.append(self.data,  data_ax_f)
		self.data2 = np.append(self.data2, data_ay_f)
		self.data3 = np.append(self.data3, data_az_f)
		self.data4 = np.append(self.data4, data_wx_f)
		self.data5 = np.append(self.data5, data_wy_f)
		self.data6 = np.append(self.data6, data_wz_f)
		self.data7 = np.append(self.data7, data_wz200_f)
		self.dt = np.append(self.dt, dt)
		if(self.save_status):
			np.savetxt(self.f, (np.vstack([dt,data_ax_f, data_ay_f, data_az_f, data_wx_f, data_wy_f, data_wz_f, data_wz200_f])).T, fmt='%5.5f,%.5f,%.5f,%.5f,%4.5f,%4.5f,%4.5f, %4.5f')
		if(DEBUG) :
			# print(np.average(self.data))
			# print(np.average(self.data2))
			# print(np.average(self.data3))
			# print('len(data_wx)', len(self.data4), end=', ')
			# print(np.average(self.data4))
			# print('len(data_wy)', len(self.data5), end=', ')
			# print(np.average(self.data5))
			# print('len(data_wz)', len(self.data6), end=', ')
			# print('len(data_wz200)', len(self.data7), end=', ')
			# print(np.round(np.average(self.data6), 3), end=', ')
			# print(np.round(np.std(self.data6), 3))
			# print(np.average(self.data6))
			# print('len(dt)', len(self.dt))
			
			# print("thez: ", end=', ')
			# print(self.thetaz, end=', ')
			# print(len(self.thetaz_arr))
			# print("thex: ", end=', ')
			# print(self.thetax, end=', ')
			# print(len(self.thetax_arr))
			# print("they: ", end=', ')
			# print(self.thetay, end=', ')
			# print(len(self.thetay_arr))
			
			# print("vx: ", end=', ')
			# print(self.speedx, end=', ')
			# print(len(self.speedx_arr))
			# print("vy: ", end=', ')
			# print(self.speedy, end=', ')
			# print(len(self.speedy_arr))
			# self.top.wzOffset_lb.setText(str(np.average(self.data6)))
			pass
					
		if(self.ax_chk):
			self.top.com_plot.ax1.plot(self.dt, self.data, color = 'r', linestyle = '-', marker = '', label="ax")
		if(self.ay_chk):
			self.top.com_plot.ax1.plot(self.dt, self.data2, color = 'g', linestyle = '-', marker = '', label="ay")
			
		if(self.wz_chk):
			self.top.com_plot.ax1.plot(self.dt, self.data6, color = 'b', linestyle = '-', marker = '', label="wz")
		if(self.wz200_chk):
			self.top.com_plot.ax1.plot(self.dt, self.data7, color = 'r', linestyle = '-', marker = '', label="wz200")
		if(self.x_chk):
			self.top.com_plot.ax1.plot(self.x_arr, color = 'r', linestyle = '-', marker = '', label="x")
		if(self.y_chk):
			self.top.com_plot.ax1.plot(self.y_arr, color = 'g', linestyle = '-', marker = '', label="y")
		if(self.vx_chk):
			self.top.com_plot.ax2.plot(self.speedx_arr, color = 'r', linestyle = '-', marker = '', label="vx")
			self.top.com_plot.ax2.set_ylim([-5, 5])
		if(self.vy_chk):
			self.top.com_plot.ax2.plot(self.speedy_arr, color = 'g', linestyle = '-', marker = '', label="vy")
			self.top.com_plot.ax2.set_ylim([-5, 5])
		if(self.thetaz_chk):
			self.top.com_plot.ax2.plot(self.thetaz_arr, color = 'b', linestyle = '-', marker = '', label="thetaz")
		if(self.thetaz200_chk):
			self.top.com_plot.ax2.plot(self.thetaz200_arr, color = 'r', linestyle = '-', marker = '', label="thetaz200")
		if(self.v_chk):
			self.top.com_plot.ax2.plot(self.speed_arr, color = 'k', linestyle = '-', marker = '', label="speed")
			self.top.com_plot.ax2.set_ylim([0, 5])
		if(self.track_chk):
			self.top.com_plot.ax2.plot(self.x_arr, self.y_arr, color = 'b', linestyle = '-', marker = '', label="track")
			self.top.com_plot.ax2.plot(self.x200_arr, self.y200_arr, color = 'r', linestyle = '-', marker = '', label="track200")
			self.top.com_plot.ax2.set_xlim([track_min, track_max])
			self.top.com_plot.ax2.set_ylim([track_min, track_max])
		
		self.top.com_plot.ax1.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		self.top.com_plot.ax2.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		self.top.com_plot.figure.canvas.draw()		
		self.top.com_plot.figure.canvas.flush_events()
		
	def plotADXLIMUnGYRO(self, data_ADax, data_ADay, data_ax, data_ay, data_wx, data_wy, data_wz, data_wz200, dt):
		if(self.act.runFlag):
			self.top.com_plot.ax1.clear()
			self.top.com_plot.ax2.clear()
			# if(not self.track_chk):
				# self.top.com_plot.ax2.clear()
		dt = dt*1e-6
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.data3 = self.data3[self.act.data_frame_update_point:]
			self.data4 = self.data4[self.act.data_frame_update_point:]
			self.data5 = self.data5[self.act.data_frame_update_point:]
			self.data6 = self.data6[self.act.data_frame_update_point:]
			self.data7 = self.data7[self.act.data_frame_update_point:]
			self.data8 = self.data8[self.act.data_frame_update_point:]
			self.dt = self.dt[self.act.data_frame_update_point:]
		data_ax_f = (data_ax-self.ax_offset)*xlm_factor
		data_ay_f = (data_ay-self.ay_offset)*xlm_factor
		data_ADax_f = (data_ADax-self.ADax_offset)*ADxlm_factor
		data_ADay_f = (data_ADay-self.ADay_offset)*ADxlm_factor
		# data_az_f = (data_az-0)*xlm_factor
		data_wx_f = (data_wx-self.wx_offset)*gyro_factor
		data_wy_f = (data_wy-self.wy_offset)*gyro_factor
		data_wz_f = (data_wz-self.wz_offset)*gyro_factor
		data_wz200_f = (data_wz200-self.wz200_offset)*gyro200_factor/3600 #convert to DPS
		
		self.thetaz = self.thetaz - np.sum(data_wz_f)*0.01 #負號是方向判斷的問題
		self.thetaz_arr = np.append(self.thetaz_arr, self.thetaz)
		self.thetaz200 = self.thetaz200 - np.sum(data_wz200_f)*0.01 #負號是方向判斷的問題
		self.thetaz200_arr = np.append(self.thetaz200_arr, self.thetaz200)
		self.thetax = self.thetax + np.sum(data_wx_f)*0.01
		self.thetax_arr = np.append(self.thetax_arr, self.thetax)
		self.thetay = self.thetay + np.sum(data_wy_f)*0.01
		self.thetay_arr = np.append(self.thetay_arr, self.thetay)
		self.speedx = self.speedx + np.sum(data_ax_f)*9.8*0.01
		self.speedx_arr = np.append(self.speedx_arr, self.speedx)
		self.speedy = self.speedy + np.sum(data_ay_f)*9.8*0.01
		self.speedy_arr = np.append(self.speedy_arr, self.speedy)
		self.speed = np.sqrt(np.square(self.speedx)+np.square(self.speedy))
		self.speed_arr = np.append(self.speed_arr, self.speed)
		
		''' for track plot'''
		theta = 90 - self.thetaz
		theta200 = 90 - self.thetaz200
		print('theta: ', self.thetaz)
		self.top.wz_gauge.item.setRotation(self.thetaz)
		'''
		dx = dr*cos(theta), dr = vdt
		v = 1 m/s
		dt = data_frame_update_point*self.act.TIME_PERIOD 
		'''
		dx = np.cos(theta*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
		dy = np.sin(theta*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.x_sum = self.x_sum + dx
		self.y_sum = self.y_sum + dy
		
		dx200 = np.cos(theta200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
		dy200 = np.sin(theta200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.x200_sum = self.x200_sum + dx200
		self.y200_sum = self.y200_sum + dy200
		
		self.top.theta_lb.setText(str(round(self.thetaz,2)))
		self.top.theta_lb.setStyleSheet('color: blue')
		self.top.theta200_lb.setText(str(round(self.thetaz200,2)))
		self.top.theta200_lb.setStyleSheet('color: red')
		self.top.buffer_lb.setText(str(self.act.bufferSize))
		
		self.dx_arr = np.append(self.dx_arr, dx)
		self.dy_arr = np.append(self.dy_arr, dy)
		self.x_arr = np.append(self.x_arr, self.x_sum)
		self.y_arr = np.append(self.y_arr, self.y_sum)
		
		self.dx200_arr = np.append(self.dx200_arr, dx200)
		self.dy200_arr = np.append(self.dy200_arr, dy200)
		self.x200_arr = np.append(self.x200_arr, self.x200_sum)
		self.y200_arr = np.append(self.y200_arr, self.y200_sum)
		
		if (len(self.thetaz_arr) >= 10):
			self.thetaz_arr = self.thetaz_arr[1:]
			self.thetaz200_arr = self.thetaz200_arr[1:]
			self.thetax_arr = self.thetax_arr[1:]
			self.thetay_arr = self.thetay_arr[1:]
			self.speedx_arr = self.speedx_arr[1:]
			self.speedy_arr = self.speedy_arr[1:]
			self.speed_arr = self.speed_arr[1:]
			self.dx_arr = self.dx_arr[1:]
			self.dy_arr = self.dy_arr[1:]
			self.dx200_arr = self.dx200_arr[1:]
			self.dy200_arr = self.dy200_arr[1:]
			# self.x_arr = self.x_arr[1:]
			# self.y_arr = self.y_arr[1:]
		# print(np.sum(data_wz_f))
		
		self.data  = np.append(self.data,  data_ax_f)
		self.data2 = np.append(self.data2, data_ay_f)
		self.data3 = np.append(self.data3, data_ADax_f)
		self.data4 = np.append(self.data4, data_ADay_f)
		self.data5 = np.append(self.data5, data_wx_f)
		self.data6 = np.append(self.data6, data_wy_f)
		self.data7 = np.append(self.data7, data_wz_f)
		self.data8 = np.append(self.data8, data_wz200_f)
		self.dt = np.append(self.dt, dt)
		if(self.save_status):
			np.savetxt(self.f, (np.vstack([dt,data_ax_f, data_ay_f, data_ADax_f, data_ADay_f, data_wx_f, data_wy_f, data_wz_f, data_wz200_f])).T, fmt='%5.5f,%.5f,%.5f,%.5f,%.5f,%4.5f,%4.5f,%4.5f, %4.5f')
		if(DEBUG) :
			# print(np.average(self.data))
			# print(np.average(self.data2))
			# print(np.average(self.data3))
			# print('len(data_wx)', len(self.data4), end=', ')
			# print(np.average(self.data4))
			# print('len(data_wy)', len(self.data5), end=', ')
			# print(np.average(self.data5))
			# print('len(data_wz)', len(self.data6), end=', ')
			# print('len(data_wz200)', len(self.data7), end=', ')
			# print(np.round(np.average(self.data6), 3), end=', ')
			# print(np.round(np.std(self.data6), 3))
			# print(np.average(self.data6))
			# print('len(dt)', len(self.dt))
			
			# print("thez: ", end=', ')
			# print(self.thetaz, end=', ')
			# print(len(self.thetaz_arr))
			# print("thex: ", end=', ')
			# print(self.thetax, end=', ')
			# print(len(self.thetax_arr))
			# print("they: ", end=', ')
			# print(self.thetay, end=', ')
			# print(len(self.thetay_arr))
			
			# print("vx: ", end=', ')
			# print(self.speedx, end=', ')
			# print(len(self.speedx_arr))
			# print("vy: ", end=', ')
			# print(self.speedy, end=', ')
			# print(len(self.speedy_arr))
			# self.top.wzOffset_lb.setText(str(np.average(self.data6)))
			
			# print('len(dt): ', len(self.dt))
			# print('len(ax_33): ', len(self.data))
			# print('len(ay_33): ', len(self.data2))
			# print('len(ADax): ', len(self.data3))
			# print('len(ADay): ', len(self.data4))
			# print('len(wz): ', len(self.data7))
			# print('len(wz200): ', len(self.data8))
			pass
					
		if(self.ax_chk):
			# self.top.com_plot.ax1.plot(self.dt, self.data, color = 'r', linestyle = '-', marker = '', label="ax")
			self.top.com_plot.ax1.plot(self.dt, self.data3, color = 'r', linestyle = '-', marker = '', label="ADax")
		if(self.ay_chk):
			# self.top.com_plot.ax1.plot(self.dt, self.data2, color = 'g', linestyle = '-', marker = '', label="ay")
			self.top.com_plot.ax1.plot(self.dt, self.data4, color = 'g', linestyle = '-', marker = '', label="ADay")
			
		if(self.wz_chk):
			self.top.com_plot.ax1.plot(self.dt, self.data7, color = 'b', linestyle = '-', marker = '', label="wz")
		if(self.wz200_chk):
			self.top.com_plot.ax1.plot(self.dt, self.data8, color = 'r', linestyle = '-', marker = '', label="wz200")
		if(self.x_chk):
			self.top.com_plot.ax1.plot(self.x_arr, color = 'r', linestyle = '-', marker = '', label="x")
		if(self.y_chk):
			self.top.com_plot.ax1.plot(self.y_arr, color = 'g', linestyle = '-', marker = '', label="y")
		if(self.vx_chk):
			self.top.com_plot.ax2.plot(self.speedx_arr, color = 'r', linestyle = '-', marker = '', label="vx")
			self.top.com_plot.ax2.set_ylim([-5, 5])
		if(self.vy_chk):
			self.top.com_plot.ax2.plot(self.speedy_arr, color = 'g', linestyle = '-', marker = '', label="vy")
			self.top.com_plot.ax2.set_ylim([-5, 5])
		if(self.thetaz_chk):
			self.top.com_plot.ax2.plot(self.thetaz_arr, color = 'b', linestyle = '-', marker = '', label="thetaz")
		if(self.thetaz200_chk):
			self.top.com_plot.ax2.plot(self.thetaz200_arr, color = 'r', linestyle = '-', marker = '', label="thetaz200")
		if(self.v_chk):
			self.top.com_plot.ax2.plot(self.speed_arr, color = 'k', linestyle = '-', marker = '', label="speed")
			self.top.com_plot.ax2.set_ylim([0, 5])
		if(self.track_chk):
			self.top.com_plot.ax2.plot(self.x_arr, self.y_arr, color = 'b', linestyle = '-', marker = '', label="track")
			self.top.com_plot.ax2.plot(self.x200_arr, self.y200_arr, color = 'r', linestyle = '-', marker = '', label="track200")
			self.top.com_plot.ax2.set_xlim([track_min, track_max])
			self.top.com_plot.ax2.set_ylim([track_min, track_max])
		
		self.top.com_plot.ax1.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		self.top.com_plot.ax2.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		self.top.com_plot.figure.canvas.draw()		
		self.top.com_plot.figure.canvas.flush_events()
	
	def calibGYRO(self, data_ax, data_ay, data_az, data_wx, data_wy, data_wz, 
					diff_ax, diff_ay, diff_az, diff_wx, diff_wy, diff_wz):
		if(self.act.runFlag):
			self.top.com_plot.ax1.clear()
			self.top.com_plot.ax2.clear()
			
		if (len(self.data) >= 300):
			self.data  = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.data3 = self.data3[self.act.data_frame_update_point:]
			self.data4 = self.data4[self.act.data_frame_update_point:]
			self.data5 = self.data5[self.act.data_frame_update_point:]
			self.data6 = self.data6[self.act.data_frame_update_point:]
			self.diffdata1 = self.diffdata1[self.act.data_frame_update_point:]
			self.diffdata2 = self.diffdata2[self.act.data_frame_update_point:]
			self.diffdata3 = self.diffdata3[self.act.data_frame_update_point:]
			self.diffdata4 = self.diffdata4[self.act.data_frame_update_point:]
			self.diffdata5 = self.diffdata5[self.act.data_frame_update_point:]
			self.diffdata6 = self.diffdata6[self.act.data_frame_update_point:]
		
		self.data  = np.append(self.data,  data_ax)
		self.data2 = np.append(self.data2, data_ay)
		self.data3 = np.append(self.data3, data_az)
		self.data4 = np.append(self.data4, data_wx)
		self.data5 = np.append(self.data5, data_wy)
		self.data6 = np.append(self.data6, data_wz)
		self.diffdata1 = np.append(self.diffdata1, diff_ax)
		self.diffdata2 = np.append(self.diffdata2, diff_ay)
		self.diffdata3 = np.append(self.diffdata3, diff_az)
		self.diffdata4 = np.append(self.diffdata4, diff_wx)
		self.diffdata5 = np.append(self.diffdata5, diff_wy)
		self.diffdata6 = np.append(self.diffdata6, diff_wz)
		
		wz_offset = np.round(np.average(self.data6),3)
		wz_std = np.round(np.std(self.data6), 3)
		diffwz_std = np.round(np.std(self.diffdata6), 3)
		self.top.wzOffset_lb.val.setText(str(wz_offset))
		self.top.wzStd_lb.val.setText(str(wz_std))
		self.top.diffwzStd_lb.val.setText(str(diffwz_std))
		
		wx_offset = np.round(np.average(self.data4),3)
		wx_std = np.round(np.std(self.data4), 3)
		diffwx_std = np.round(np.std(self.diffdata4), 3)
		self.top.wxOffset_lb.val.setText(str(wx_offset))
		self.top.wxStd_lb.val.setText(str(wx_std))
		self.top.diffwxStd_lb.val.setText(str(diffwx_std))
		
		wy_offset = np.round(np.average(self.data5),3)
		wy_std = np.round(np.std(self.data5), 3)
		diffwy_std = np.round(np.std(self.diffdata5), 3)
		self.top.wyOffset_lb.val.setText(str(wy_offset))
		self.top.wyStd_lb.val.setText(str(wy_std))
		self.top.diffwyStd_lb.val.setText(str(diffwy_std))
		
		ax_offset = np.round(np.average(self.data),3)
		ax_std = np.round(np.std(self.data), 3)
		diffax_std = np.round(np.std(self.diffdata1), 3)
		self.top.axOffset_lb.val.setText(str(ax_offset))
		self.top.axStd_lb.val.setText(str(ax_std))
		self.top.diffaxStd_lb.val.setText(str(diffax_std))
		
		ay_offset = np.round(np.average(self.data2),3)
		ay_std = np.round(np.std(self.data2), 3)
		diffay_std = np.round(np.std(self.diffdata2), 3)
		self.top.ayOffset_lb.val.setText(str(ay_offset))
		self.top.ayStd_lb.val.setText(str(ay_std))
		self.top.diffayStd_lb.val.setText(str(diffay_std))
		
		''' ax ay plot '''
		# self.top.com_plot.ax1.set_ylabel("acc(code)")
		# self.top.com_plot.ax1.plot(self.data, color = 'r', linestyle = '-', marker = '', label="ax")
		# self.top.com_plot.ax1.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.set_ylabel("w(code)")
		# self.top.com_plot.ax2.plot(self.data6, color = 'b', linestyle = '-', marker = '', label="wz")
		# self.top.com_plot.ax2.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		
		if(self.ax_chk):
			self.top.com_plot.ax1.plot(self.data, color = 'r', linestyle = '-', marker = '', label="ax")
		if(self.ay_chk):
			self.top.com_plot.ax1.plot(self.data2, color = 'g', linestyle = '-', marker = '', label="ay")
		if(self.wz_chk):
			self.top.com_plot.ax2.plot(self.data6, color = 'b', linestyle = '-', marker = '', label="wz")
		
		self.top.com_plot.ax1.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		self.top.com_plot.ax2.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		
		self.top.com_plot.figure.canvas.draw()		
		self.top.com_plot.figure.canvas.flush_events()
		
	def calibIMUnGYRO(self, data_ax, data_ay, data_az, data_wx, data_wy, data_wz, data_wz200,
					diff_ax, diff_ay, diff_az, diff_wx, diff_wy, diff_wz):
		if(self.act.runFlag):
			self.top.com_plot.ax1.clear()
			self.top.com_plot.ax2.clear()
			
		if (len(self.data) >= 300):
			self.data  = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.data3 = self.data3[self.act.data_frame_update_point:]
			self.data4 = self.data4[self.act.data_frame_update_point:]
			self.data5 = self.data5[self.act.data_frame_update_point:]
			self.data6 = self.data6[self.act.data_frame_update_point:]
			self.data7 = self.data7[self.act.data_frame_update_point:]
			self.diffdata1 = self.diffdata1[self.act.data_frame_update_point:]
			self.diffdata2 = self.diffdata2[self.act.data_frame_update_point:]
			self.diffdata3 = self.diffdata3[self.act.data_frame_update_point:]
			self.diffdata4 = self.diffdata4[self.act.data_frame_update_point:]
			self.diffdata5 = self.diffdata5[self.act.data_frame_update_point:]
			self.diffdata6 = self.diffdata6[self.act.data_frame_update_point:]
		
		self.data  = np.append(self.data,  data_ax)
		self.data2 = np.append(self.data2, data_ay)
		self.data3 = np.append(self.data3, data_az)
		self.data4 = np.append(self.data4, data_wx)
		self.data5 = np.append(self.data5, data_wy)
		self.data6 = np.append(self.data6, data_wz)
		self.data7 = np.append(self.data7, data_wz200)
		self.diffdata1 = np.append(self.diffdata1, diff_ax)
		self.diffdata2 = np.append(self.diffdata2, diff_ay)
		self.diffdata3 = np.append(self.diffdata3, diff_az)
		self.diffdata4 = np.append(self.diffdata4, diff_wx)
		self.diffdata5 = np.append(self.diffdata5, diff_wy)
		self.diffdata6 = np.append(self.diffdata6, diff_wz)
		
		wz_offset = np.round(np.average(self.data6),3)
		wz_std = np.round(np.std(self.data6), 3)
		diffwz_std = np.round(np.std(self.diffdata6), 3)
		self.top.wzOffset_lb.val.setText(str(wz_offset))
		self.top.wzStd_lb.val.setText(str(wz_std))
		self.top.diffwzStd_lb.val.setText(str(diffwz_std))
		
		wz200_offset = np.round(np.average(self.data7),3)
		wz200_std = np.round(np.std(self.data7), 3)
		self.top.wz200Offset_lb.val.setText(str(wz200_offset))
		self.top.wz200Std_lb.val.setText(str(wz200_std))
		
		wx_offset = np.round(np.average(self.data4),3)
		wx_std = np.round(np.std(self.data4), 3)
		diffwx_std = np.round(np.std(self.diffdata4), 3)
		self.top.wxOffset_lb.val.setText(str(wx_offset))
		self.top.wxStd_lb.val.setText(str(wx_std))
		self.top.diffwxStd_lb.val.setText(str(diffwx_std))
		
		wy_offset = np.round(np.average(self.data5),3)
		wy_std = np.round(np.std(self.data5), 3)
		diffwy_std = np.round(np.std(self.diffdata5), 3)
		self.top.wyOffset_lb.val.setText(str(wy_offset))
		self.top.wyStd_lb.val.setText(str(wy_std))
		self.top.diffwyStd_lb.val.setText(str(diffwy_std))
		
		ax_offset = np.round(np.average(self.data),3)
		ax_std = np.round(np.std(self.data), 3)
		diffax_std = np.round(np.std(self.diffdata1), 3)
		self.top.axOffset_lb.val.setText(str(ax_offset))
		self.top.axStd_lb.val.setText(str(ax_std))
		self.top.diffaxStd_lb.val.setText(str(diffax_std))
		
		ay_offset = np.round(np.average(self.data2),3)
		ay_std = np.round(np.std(self.data2), 3)
		diffay_std = np.round(np.std(self.diffdata2), 3)
		self.top.ayOffset_lb.val.setText(str(ay_offset))
		self.top.ayStd_lb.val.setText(str(ay_std))
		self.top.diffayStd_lb.val.setText(str(diffay_std))
		
		''' ax ay plot '''
		# self.top.com_plot.ax1.set_ylabel("acc(code)")
		# self.top.com_plot.ax1.plot(self.data, color = 'r', linestyle = '-', marker = '', label="ax")
		# self.top.com_plot.ax1.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.set_ylabel("w(code)")
		# self.top.com_plot.ax2.plot(self.data6, color = 'b', linestyle = '-', marker = '', label="wz")
		# self.top.com_plot.ax2.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		
		# if(self.ax_chk):
			# self.top.com_plot.ax1.plot(self.data, color = 'r', linestyle = '-', marker = '', label="ax")
		# if(self.ay_chk):
			# self.top.com_plot.ax1.plot(self.data2, color = 'g', linestyle = '-', marker = '', label="ay")
		if(self.wz200_chk):
			self.top.com_plot.ax1.plot(self.data7, color = 'r', linestyle = '-', marker = '', label="wz200")
		if(self.wz_chk):
			self.top.com_plot.ax2.plot(self.data6, color = 'b', linestyle = '-', marker = '', label="wz")
		
		self.top.com_plot.ax1.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		self.top.com_plot.ax2.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		
		self.top.com_plot.figure.canvas.draw()		
		self.top.com_plot.figure.canvas.flush_events()
		
	def calibADXLIMUnGYRO(self, data_ax, data_ay, data_az, data_ADax, data_ADay, data_ADaz, 
						data_wx, data_wy, data_wz, data_wz200, diff_wx, diff_wy, diff_wz):
		if(self.act.runFlag):
			self.top.com_plot.ax1.clear()
			self.top.com_plot.ax2.clear()
			
		if (len(self.data) >= 300):
			self.data  = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.data3 = self.data3[self.act.data_frame_update_point:]
			self.data4 = self.data4[self.act.data_frame_update_point:]
			self.data5 = self.data5[self.act.data_frame_update_point:]
			self.data6 = self.data6[self.act.data_frame_update_point:]
			self.data7 = self.data7[self.act.data_frame_update_point:]
			self.data8 = self.data8[self.act.data_frame_update_point:]
			self.data9 = self.data9[self.act.data_frame_update_point:]
			self.data10 = self.data10[self.act.data_frame_update_point:]
			# self.diffdata1 = self.diffdata1[self.act.data_frame_update_point:]
			# self.diffdata2 = self.diffdata2[self.act.data_frame_update_point:]
			# self.diffdata3 = self.diffdata3[self.act.data_frame_update_point:]
			self.diffdata4 = self.diffdata4[self.act.data_frame_update_point:]
			self.diffdata5 = self.diffdata5[self.act.data_frame_update_point:]
			self.diffdata6 = self.diffdata6[self.act.data_frame_update_point:]
		
		self.data  = np.append(self.data,  data_ax)
		self.data2 = np.append(self.data2, data_ay)
		self.data3 = np.append(self.data3, data_az)
		self.data4 = np.append(self.data4, data_wx)
		self.data5 = np.append(self.data5, data_wy)
		self.data6 = np.append(self.data6, data_wz)
		self.data7 = np.append(self.data7, data_wz200)
		self.data8  = np.append(self.data8,  data_ADax)
		self.data9  = np.append(self.data9,  data_ADay)
		self.data10  = np.append(self.data10,  data_ADaz)
		# self.diffdata1 = np.append(self.diffdata1, diff_ax)
		# self.diffdata2 = np.append(self.diffdata2, diff_ay)
		# self.diffdata3 = np.append(self.diffdata3, diff_az)
		self.diffdata4 = np.append(self.diffdata4, diff_wx)
		self.diffdata5 = np.append(self.diffdata5, diff_wy)
		self.diffdata6 = np.append(self.diffdata6, diff_wz)
		
		wz_offset = np.round(np.average(self.data6),3)
		wz_std = np.round(np.std(self.data6), 3)
		diffwz_std = np.round(np.std(self.diffdata6), 3)
		self.top.wzOffset_lb.val.setText(str(wz_offset))
		self.top.wzStd_lb.val.setText(str(wz_std))
		self.top.diffwzStd_lb.val.setText(str(diffwz_std))
		
		wz200_offset = np.round(np.average(self.data7),3)
		wz200_std = np.round(np.std(self.data7), 3)
		self.top.wz200Offset_lb.val.setText(str(wz200_offset))
		self.top.wz200Std_lb.val.setText(str(wz200_std))
		
		wx_offset = np.round(np.average(self.data4),3)
		wx_std = np.round(np.std(self.data4), 3)
		diffwx_std = np.round(np.std(self.diffdata4), 3)
		self.top.wxOffset_lb.val.setText(str(wx_offset))
		self.top.wxStd_lb.val.setText(str(wx_std))
		self.top.diffwxStd_lb.val.setText(str(diffwx_std))
		
		wy_offset = np.round(np.average(self.data5),3)
		wy_std = np.round(np.std(self.data5), 3)
		diffwy_std = np.round(np.std(self.diffdata5), 3)
		self.top.wyOffset_lb.val.setText(str(wy_offset))
		self.top.wyStd_lb.val.setText(str(wy_std))
		self.top.diffwyStd_lb.val.setText(str(diffwy_std))
		
		ax_offset = np.round(np.average(self.data),3)
		ax_std = np.round(np.std(self.data), 3)
		diffax_std = np.round(np.std(self.diffdata1), 3)
		self.top.axOffset_lb.val.setText(str(ax_offset))
		self.top.axStd_lb.val.setText(str(ax_std))
		self.top.diffaxStd_lb.val.setText(str(diffax_std))
		
		ay_offset = np.round(np.average(self.data2),3)
		ay_std = np.round(np.std(self.data2), 3)
		diffay_std = np.round(np.std(self.diffdata2), 3)
		self.top.ayOffset_lb.val.setText(str(ay_offset))
		self.top.ayStd_lb.val.setText(str(ay_std))
		self.top.diffayStd_lb.val.setText(str(diffay_std))
		
		ADax_offset = np.round(np.average(self.data8),3)
		ADax_std = np.round(np.std(self.data8), 3)
		self.top.axOffsetAD_lb.val.setText(str(ADax_offset))
		self.top.axStdAD_lb.val.setText(str(ADax_std))
		
		ADay_offset = np.round(np.average(self.data9),3)
		ADay_std = np.round(np.std(self.data9), 3)
		self.top.ayOffsetAD_lb.val.setText(str(ADay_offset))
		self.top.ayStdAD_lb.val.setText(str(ADay_std))
		
		''' ax ay plot '''
		# self.top.com_plot.ax1.set_ylabel("acc(code)")
		# self.top.com_plot.ax1.plot(self.data, color = 'r', linestyle = '-', marker = '', label="ax")
		# self.top.com_plot.ax1.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.set_ylabel("w(code)")
		# self.top.com_plot.ax2.plot(self.data6, color = 'b', linestyle = '-', marker = '', label="wz")
		# self.top.com_plot.ax2.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		
		# if(self.ax_chk):
			# self.top.com_plot.ax1.plot(self.data, color = 'r', linestyle = '-', marker = '', label="ax")
		# if(self.ay_chk):
			# self.top.com_plot.ax1.plot(self.data2, color = 'g', linestyle = '-', marker = '', label="ay")
		if(self.wz200_chk):
			self.top.com_plot.ax1.plot(self.data7, color = 'r', linestyle = '-', marker = '', label="wz200")
		if(self.wz_chk):
			self.top.com_plot.ax2.plot(self.data6, color = 'b', linestyle = '-', marker = '', label="wz")
		
		self.top.com_plot.ax1.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		self.top.com_plot.ax2.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		
		self.top.com_plot.figure.canvas.draw()		
		self.top.com_plot.figure.canvas.flush_events()
		

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
	

