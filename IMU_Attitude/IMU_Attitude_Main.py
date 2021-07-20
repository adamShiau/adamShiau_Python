import os 
import sys 
sys.path.append("../") 
import time 
import datetime
from scipy import signal
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
import numpy as np
import IMU_Attitude_Widget as UI  
import IMU_Attitude_Action as ACT
import IMU_Globals as globals

TITLE_TEXT = "IMU_PLOT"
VERSION_TEXT = 'Compare FOG with MEMS，2020/12/01'
READOUT_FILENAME = "Signal_Read_Out.txt"
MAX_SAVE_INDEX = 3000
ODR = 100
SAMPLING_TIME = 1/ODR
DEBUG = 0
DEBUG_COM = 0
track_max = 50
track_min = -50
w_factor = 0.01
TEST_MODE = 0
USE_FAKE_SPEED = 1
xlm_factor = 0.000122 #4g / 32768
ADxlm_factor = 0.0000156 #8g
gyro_factor = 0.00763 #250 / 32768 
# gyro_factor = 0.0090 #250 / 32768 
gyroPP_factor = -2.76
IMU_speed_factor = 0.001
gyro200_factor = 0.01
# gyro200_factor = 1.17122
adxl355_th = 0.0000 #acc g_th, 0.0005 = 0.0005*g
TRACK_UPDATE_CNT = 10
PRINT_DEGREE = 0
TRACK_X_MAX = 150
TRACK_X_MIN = -TRACK_X_MAX
TRACK_Y_MAX = 150
TRACK_Y_MIN = -TRACK_Y_MAX
''' VBOX conversion factor'''
latitude_factor = 0.0000001		#degree
longitude_factor = 0.0000001	#degree
velocity_factor = 0.001 		#km/h
altitude_factor = 0.01			#m
v_velocity_factor = 0.001		#m/s
pitch_factor = 0.01				#deg
roll_factor = 0.01				#deg
heading_factor = 0.01			#deg
accz_factor = 0.01				#m/s^2

class mainWindow(QMainWindow):
	''' define and initiate global variable '''
	old_dt = 0
	time_cnt = 0
	label_update_cnt = 0
	MV_status = 0
	offset_SRS200_wz = 0
	offset_T = 0
	offset_PP_wz = 0
	offset_IMU_speed = 0
	offset_Nano33_wx = 0
	offset_Nano33_wy = 0
	offset_Nano33_wz = 0
	offset_Nano33_ax = 0
	offset_Nano33_ay = 0
	offset_Nano33_az = 0
	offset_Adxl355_ax = 0
	offset_Adxl355_ay = 0
	offset_Adxl355_az = 0
	data_Adxl355_ax_f = 0
	data_Adxl355_ay_f = 0
	data_Adxl355_az_f = 0
	current_data_Adxl355_ax_f = 0
	current_data_Adxl355_ay_f = 0
	current_data_Adxl355_az_f = 0
	current_speedx_Adxl355 = 0
	current_speedy_Adxl355 = 0
	dt_old = 0
	''' pyqtSignal'''
	usbconnect_status = pyqtSignal(object) #to trigger the btn to enable state
	''' axis max for track'''
	x_max = 1
	y_max = 1
	clear_track_flag = False
	''' data save'''
	save_status = False
	track_cnt = 0
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		# self.COM = act.UART()
		self.setWindowTitle(TITLE_TEXT)
		self.resize(1100,800)
		self.move(0,0)
		self.loggername = "Total"
		self.top = UI.mainWidget()
		self.act = ACT.IMU_Action(self.loggername)
		'''inittialize thread '''
		# self.thread1 = QThread()
		# self.thread_cali = QThread()
		'''end of inittialize thread '''
		self.data_SRS200_wz = np.empty(0)
		self.data_Nano33_wx = np.empty(0)
		self.data_Nano33_wy = np.empty(0)
		self.data_Nano33_wz = np.empty(0)
		self.data_PP_wz = np.empty(0)
		self.data_IMU_speed = np.empty(0)
		self.data_Adxl355_ax = np.empty(0)
		self.data_Adxl355_ay = np.empty(0)
		self.data_Adxl355_az = np.empty(0)
		self.data_Nano33_ax = np.empty(0)
		self.data_Nano33_ay = np.empty(0)
		self.data_Nano33_az = np.empty(0)
		self.data_Update_rate = np.empty(0)
		self.data_time = np.empty(0)
		self.data_T = np.empty(0)
		self.thetaz_Nano33 = 0
		self.thetaz_PP = 0
		self.thetaz_SRS200 = 0
		# self.thetax = 0
		# self.thetay = 0
		self.data_velocity = np.empty(0)
		self.data_roll = np.empty(0)
		self.data_pitch = np.empty(0)
		self.data_heading = np.empty(0)
		self.data_accz = np.empty(0)
		self.speed_Nano33 = 0
		self.speedx_Nano33 = 0
		self.speedy_Nano33 = 0
		self.speed_Adxl355 = 0
		self.speedx_Adxl355 = 0
		self.current_speedx_Adxl355 = 0
		self.speedy_Adxl355 = 0
		self.current_speedy_Adxl355 = 0
		self.thetaz_Nano33_arr = np.empty(0)
		self.thetaz_PP_arr = np.empty(0)
		self.thetaz_SRS200_arr = np.empty(0)
		self.thetax_arr = np.empty(0)
		self.thetay_arr = np.empty(0)
		# self.dx_arr = np.zeros(0)
		# self.dy_arr = np.zeros(0)
		self.xNano33_arr = np.zeros(0)
		self.yNano33_arr = np.zeros(0)
		self.xNano33_sum = 0
		self.yNano33_sum = 0
		self.xPP_arr = np.zeros(0)
		self.yPP_arr = np.zeros(0)
		self.xPP_sum = 0
		self.yPP_sum = 0
		self.dx200_arr = np.zeros(0)
		self.dy200_arr = np.zeros(0)
		self.x200_arr = np.zeros(0)
		self.y200_arr = np.zeros(0)
		self.x200_sum = 0
		self.y200_sum = 0
		self.speed_Nano33_arr = np.empty(0)
		self.speed_Adxl355_arr = np.empty(0)
		# self.speedx_Nano33_arr = np.empty(0)
		# self.speedy_Nano33_arr = np.empty(0)
		self.dt = np.empty(0)
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.setCheckBox_init()
		self.setBtnStatus(False)
		self.get_cbVal()
		self.get_rbVal()
		# self.wz_offset = self.act.offset_wz
		
	
	
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
		''' thread btn connect '''
		self.top.TabPlot.tab1_read_btn.bt.clicked.connect(self.myThreadStart) # set runFlag=1
		self.top.TabPlot.tab1_stop_btn.bt.clicked.connect(self.buttonStop) # set runFlag=0
		self.top.TabPlot.tab2_cali_start_btn.bt.clicked.connect(self.caliThreadStart) # set runFlag_cali=1
		self.top.TabPlot.tab2_cali_stop_btn.bt.clicked.connect(self.buttonStop)# set runFlag_cali=0
		''' btn connect '''
		self.top.usb.bt_update.clicked.connect(self.update_comport)
		self.top.usb.cs.currentIndexChanged.connect(self.uadate_comport_label)
		self.top.usb.bt_connect.clicked.connect(self.usbConnect)
		self.top.TabPlot.tab3_xmax.bt.clicked.connect(self.updata_para)
		self.top.TabPlot.tab3_ymax.bt.clicked.connect(self.updata_para)
		''' thread connect '''
		# self.thread1.started.connect(lambda:self.act.updateADXL_IMUnGYRO(MV_MODE=self.MV_status)) 
		# self.thread_cali.started.connect(lambda:self.act.updateADXL_IMUnGYRO(MV_MODE=self.MV_status))

		''' emit connect '''
		#btn enable signal
		self.usbconnect_status.connect(self.setBtnStatus) #確定usb連接成功時才enable btn
		self.usbconnect_status.connect(self.setInitValue)
		#action emit connect
		# self.act.fog_update11.connect(self.plotADXLIMUnGYRO)
		self.act.fog_update10.connect(self.plotADXLIMUnGYRO)
		# self.act.fog_update13.connect(self.calibADXLIMUnGYRO)
		self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		
		''' text connect '''
		# self.top.wzOffset_le.textChanged.connect(self.updata_para)
		
		'''spinBlock '''
		self.top.Q.spin.valueChanged.connect(self.update_kal_Q)
		self.top.R.spin.valueChanged.connect(self.update_kal_R)
		
		''' check box '''
		self.top.TabPlot.tab1_gyro_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_gyro_cb.cb1))
		self.top.TabPlot.tab1_gyro_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_gyro_cb.cb2))
		self.top.TabPlot.tab1_gyro_cb.cb3.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_gyro_cb.cb3))
		self.top.TabPlot.tab1_gyro_cb.cb4.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_gyro_cb.cb4))
		self.top.TabPlot.tab1_gyro_cb.cb5.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_gyro_cb.cb5))
		self.top.TabPlot.tab1_adxlXLM_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_adxlXLM_cb.cb1))
		self.top.TabPlot.tab1_adxlXLM_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_adxlXLM_cb.cb2))
		self.top.TabPlot.tab1_adxlXLM_cb.cb3.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_adxlXLM_cb.cb3))
		# self.top.TabPlot.tab1_nano33XLM_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_nano33XLM_cb.cb1))
		# self.top.TabPlot.tab1_nano33XLM_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_nano33XLM_cb.cb2))
		self.top.TabPlot.tab1_speed_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_speed_cb.cb1))
		self.top.TabPlot.tab1_speed_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_speed_cb.cb2))
		self.top.TabPlot.tab1_attitude_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_attitude_cb.cb1))
		self.top.TabPlot.tab1_attitude_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_attitude_cb.cb2))
		self.top.TabPlot.tab1_attitude_cb.cb3.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_attitude_cb.cb3))
		self.top.TabPlot.tab3_track_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab3_track_cb.cb1))
		self.top.TabPlot.tab3_track_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab3_track_cb.cb2))
		self.top.TabPlot.tab3_track_cb.cb3.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab3_track_cb.cb3))

		''' radio btn'''
		self.top.kal_rb.toggled.connect(lambda:self.rb_toggled(self.top.kal_rb))
	
	def setCheckBox_init(self):
		self.top.TabPlot.tab1_gyro_cb.cb3.setChecked(True) #set gyro wz initial as PP
		self.top.TabPlot.tab1_adxlXLM_cb.cb3.setChecked(True) #set adxl355 XLM initial as az
		# self.top.TabPlot.tab1_nano33XLM_cb.cb1.setChecked(True) #set nano33 XLM initial as ax
		self.top.TabPlot.tab1_speed_cb.cb1.setChecked(True) #set speed_initial as VBOX
		self.top.TabPlot.tab1_attitude_cb.cb3.setChecked(True)#set attitude initial as heading
		
		self.top.TabPlot.tab3_track_cb.cb2.setChecked(True) #set track_SRS200 initially
		
	def setBtnStatus(self, flag):
		self.top.TabPlot.tab1_read_btn.bt.setEnabled(flag)
		self.top.TabPlot.tab1_stop_btn.bt.setEnabled(flag)
		self.top.TabPlot.tab2_cali_start_btn.bt.setEnabled(flag)
		self.top.TabPlot.tab2_cali_stop_btn.bt.setEnabled(flag)
		self.top.TabPlot.tab3_xmax.bt.setEnabled(flag)
		self.top.TabPlot.tab3_ymax.bt.setEnabled(flag)
		
	def setInitValue(self, EN):
		if(EN):
			self.top.Q.spin.setValue(globals.kal_Q)
			self.top.R.spin.setValue(globals.kal_R)
	
	def update_kal_Q(self):
		value = self.top.Q.spin.value()
		globals.kal_Q = value
		print('kal_Q:', globals.kal_Q)
		
	def update_kal_R(self): 
		value = self.top.R.spin.value()
		globals.kal_R = value
		print('kal_R:', globals.kal_R)
	
	def rb_toggled(self, rb):
		globals.kal_status = rb.isChecked()
		print('main:', globals.kal_status)
		
	def get_rbVal(self):
		globals.kal_status = self.top.kal_rb.isChecked()
		print('Kal:', globals.kal_status)
		
	def cb_toogled(self, cb):
		if(cb.text()==self.top.TabPlot.tab1_gyro_cb.cb1.text()):
			self.SRS200_wz_chk = cb.isChecked()
			print('SRS200_wz_chk:', self.SRS200_wz_chk)
		if(cb.text()==self.top.TabPlot.tab1_gyro_cb.cb2.text()):
			self.PP_wz_chk = cb.isChecked()
			print('PP_wz_chk:', self.PP_wz_chk)
		elif(cb.text()==self.top.TabPlot.tab1_gyro_cb.cb3.text()):
			self.Nano33_wx_chk = cb.isChecked()
			print('Nano33_wx_chk:', self.Nano33_wx_chk)
		elif(cb.text()==self.top.TabPlot.tab1_gyro_cb.cb4.text()):
			self.Nano33_wy_chk = cb.isChecked()
			print('Nano33_wy_chk:', self.Nano33_wy_chk)
		elif(cb.text()==self.top.TabPlot.tab1_gyro_cb.cb5.text()):
			self.Nano33_wz_chk = cb.isChecked()
			print('Nano33_wz_chk:', self.Nano33_wz_chk)
		elif(cb.text()==self.top.TabPlot.tab1_adxlXLM_cb.cb1.text()):
			self.Adxl355_ax_chk = cb.isChecked()
			print('Adxl355_ax_chk:', self.Adxl355_ax_chk)
		elif(cb.text()==self.top.TabPlot.tab1_adxlXLM_cb.cb2.text()):
			self.Adxl355_ay_chk = cb.isChecked()
			print('Adxl355_ay_chk:', self.Adxl355_ay_chk)
		elif(cb.text()==self.top.TabPlot.tab1_adxlXLM_cb.cb3.text()):
			self.Adxl355_az_chk = cb.isChecked()
			print('Adxl355_az_chk:', self.Adxl355_az_chk)
		# elif(cb.text()==self.top.TabPlot.tab1_adxlXLM_cb.cb4.text()):
			# self.Adxl355_T_chk = cb.isChecked()
			# print('Adxl355_T_chk:', self.Adxl355_T_chk)
		# elif(cb.text()==self.top.TabPlot.tab1_nano33XLM_cb.cb1.text()):
			# self.Nano33_ax_chk = cb.isChecked()
			# print('Nano33_ax_chk:', self.Nano33_ax_chk)
		# elif(cb.text()==self.top.TabPlot.tab1_nano33XLM_cb.cb2.text()):
			# self.Nano33_ay_chk = cb.isChecked()
			# print('Nano33_ay_chk:', self.Nano33_ay_chk)
		elif(cb.text()==self.top.TabPlot.tab1_speed_cb.cb1.text()):
			self.VBOX_v_chk = cb.isChecked()
			print('VBOX_v_chk:', self.VBOX_v_chk)
		elif(cb.text()==self.top.TabPlot.tab1_speed_cb.cb2.text()):
			self.IMU_v_chk = cb.isChecked()
			print('IMU_v_chk:', self.IMU_v_chk)
		elif(cb.text()==self.top.TabPlot.tab1_attitude_cb.cb1.text()):
			self.roll_chk = cb.isChecked()
			print('roll_chk:', self.roll_chk)
		elif(cb.text()==self.top.TabPlot.tab1_attitude_cb.cb2.text()):
			self.pitch_chk = cb.isChecked()
			print('pitch_chk:', self.pitch_chk)
		elif(cb.text()==self.top.TabPlot.tab1_attitude_cb.cb3.text()):
			self.heading_chk = cb.isChecked()
			print('heading_chk:', self.heading_chk)
		elif(cb.text()==self.top.TabPlot.tab3_track_cb.cb1.text()):
			self.Nano33_track_chk = cb.isChecked()
			print('Nano33_track_chk:', self.Nano33_track_chk)
		elif(cb.text()==self.top.TabPlot.tab3_track_cb.cb2.text()):
			self.SRS200_track_chk = cb.isChecked()
			print('SRS200_track_chk:', self.SRS200_track_chk)
		elif(cb.text()==self.top.TabPlot.tab3_track_cb.cb3.text()):
			self.PP_track_chk = cb.isChecked()
			print('PP_track_chk:', self.PP_track_chk)
			
	def get_cbVal(self):
		self.SRS200_wz_chk = self.top.TabPlot.tab1_gyro_cb.cb1.isChecked()
		print('SRS200_wz_chk:', self.SRS200_wz_chk)
		self.PP_wz_chk = self.top.TabPlot.tab1_gyro_cb.cb2.isChecked()
		print('PP_wz_chk:', self.PP_wz_chk)
		self.Nano33_wx_chk = self.top.TabPlot.tab1_gyro_cb.cb3.isChecked()
		print('Nano33_wx_chk:', self.Nano33_wx_chk)
		self.Nano33_wy_chk = self.top.TabPlot.tab1_gyro_cb.cb4.isChecked()
		print('Nano33_wy_chk:', self.Nano33_wy_chk)
		self.Nano33_wz_chk = self.top.TabPlot.tab1_gyro_cb.cb5.isChecked()
		print('Nano33_wz_chk:', self.Nano33_wz_chk)
		
		self.Adxl355_ax_chk = self.top.TabPlot.tab1_adxlXLM_cb.cb1.isChecked()
		print('Adxl355_ax_chk:', self.Adxl355_ax_chk)
		self.Adxl355_ay_chk = self.top.TabPlot.tab1_adxlXLM_cb.cb2.isChecked()
		print('Adxl355_ay_chk:', self.Adxl355_ay_chk)
		self.Adxl355_az_chk = self.top.TabPlot.tab1_adxlXLM_cb.cb3.isChecked()
		print('Adxl355_az_chk:', self.Adxl355_az_chk)
		# self.Adxl355_T_chk = self.top.TabPlot.tab1_adxlXLM_cb.cb4.isChecked()
		# print('Adxl355_T_chk:', self.Adxl355_T_chk)
		# self.Nano33_ax_chk = self.top.TabPlot.tab1_nano33XLM_cb.cb1.isChecked()
		# print('Nano33_ax_chk:', self.Nano33_ax_chk)
		# self.Nano33_ay_chk = self.top.TabPlot.tab1_nano33XLM_cb.cb2.isChecked()
		# print('Nano33_ay_chk:', self.Nano33_ay_chk)
		
		self.VBOX_v_chk = self.top.TabPlot.tab1_speed_cb.cb1.isChecked()
		print('VBOX_v_chk:', self.VBOX_v_chk)
		self.IMU_v_chk = self.top.TabPlot.tab1_speed_cb.cb2.isChecked()
		print('IMU_v_chk:', self.IMU_v_chk)
		
		self.roll_chk = self.top.TabPlot.tab1_attitude_cb.cb1.isChecked()
		print('roll_chk:', self.roll_chk)
		self.pitch_chk = self.top.TabPlot.tab1_attitude_cb.cb2.isChecked()
		print('pitch_chk:', self.pitch_chk)
		self.heading_chk = self.top.TabPlot.tab1_attitude_cb.cb3.isChecked()
		print('heading_chk:', self.heading_chk)
		
		self.Nano33_track_chk = self.top.TabPlot.tab3_track_cb.cb1.isChecked()
		print('Nano33_track_chk:', self.Nano33_track_chk)
		self.SRS200_track_chk = self.top.TabPlot.tab3_track_cb.cb2.isChecked()
		print('SRS200_track_chk:', self.SRS200_track_chk)
		self.PP_track_chk = self.top.TabPlot.tab3_track_cb.cb3.isChecked()
		print('PP_track_chk:', self.PP_track_chk)
		
	def updata_para(self):
		self.x_max = int(self.top.TabPlot.tab3_xmax.le.text())
		print(self.x_max)
		self.y_max = int(self.top.TabPlot.tab3_ymax.le.text())
		print(self.y_max)
		print('change')
	
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
		self.act.runFlag = False
		self.act.runFlag_cali = False
		print('self.act.runFlag: ', self.act.runFlag)
		print('self.act.runFlag_cali: ', self.act.runFlag_cali)
		self.act.dt_init_flag = 1
		self.thetax_arr = np.empty(0)
		self.thetay_arr = np.empty(0)
		self.thetaz_Nano33_arr = np.empty(0)
		self.thetaz_PP_arr = np.empty(0)
		self.thetaz_SRS200_arr = np.empty(0)
		self.old_dt = 0
		self.time_cnt = 0
		
	def open_file(self, filename):
		self.f=open(filename, 'w')
		# self.f2=open(filename[0:-4] + '_track.txt', 'w')
		start_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.f.writelines('#' + start_time_header + '\n')
		#dt, data_SRS200_wz_f, data_PP_wz_f, data_Adxl355_ax_f, data_Adxl355_ay_f, data_Adxl355_az_f
		#		,speedx_Adxl355_out, speedy_Adxl355_out, speed_Adxl355_out, data_IMU_speed_f, data_T
		self.f.writelines('#' + 'dt:s,  Adxl355_ax:g, Adxl355_ay:g, Adxl355_az:g, '
								+ 'Nano33_ax:g, Nano33_ay:g, Nano33_az:g, '
								+ 'Nano33_wx:DPS, Nano33_wy:DPS, Nano33_wz:DPS'+ '\n')
							
		#dt:s, SRS200:DPS, PP:DPS, Nano33_wx:DPS, Nano33_wy:DPS, Nano33_wz:DPS, Adxl355_ax:g, Adxl355_ay:g, Adxl355_az:g, adxl355_speed, VBOX_speed, T
		# self.f2.writelines('#' + 'SRS200_x, SRS200_y, PP_x, PP_y, Nano33_x, Nano33_y' + '\n')
	
	def caliThreadStart(self):
		self.act.runFlag_cali = True
		print('self.act.runFlag_cali:', self.act.runFlag_cali)
		# self.thread_cali.start()
		self.act.start()
		
	def caliThreadStop(self):
		self.act.runFlag_cali = False 
		# self.thread_cali.quit() 
		# self.thread_cali.wait()
		self.act.quit() 
		self.act.wait()
		
	def myThreadStart(self):
		# '''
		self.save_status = self.openFileBox()
		# '''
		# file_name = self.top.save_edit.edit.text() 
		# self.f=open(file_name,'a')
		# self.f=open('er','a')
		self.act.runFlag = True
		self.clear_track_flag = True
		self.act.start()
		self.act.MV_MODE = self.MV_status
		print('self.act.runFlag:', self.act.runFlag)
		# self.thread1.start()
		self.act.COM.port.flushInput()
		# self.top.com_plot.ax1.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		
	def myThreadStop(self):
		# self.thread1.quit() 
		# self.thread1.wait()
		# self.thread_cali.quit() 
		# self.thread_cali.wait()
		self.act.quit() 
		self.act.wait()
		# '''
		if(self.save_status):
			stop_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			self.f.writelines('#' + stop_time_header + '\n')
			self.f.close()
			# self.f2.close()
		# '''
		# self.data_SRS200_wz = np.empty(0)
		self.data_Nano33_wx = np.empty(0)
		self.data_Nano33_wy = np.empty(0)
		self.data_Nano33_wz = np.empty(0)
		# self.data_PP_wz = np.empty(0)
		# self.data_IMU_speed = np.empty(0)
		self.data_Adxl355_ax = np.empty(0)
		self.data_Adxl355_ay = np.empty(0)
		self.data_Adxl355_az = np.empty(0)
		self.data_Nano33_ax = np.empty(0)
		self.data_Nano33_ay = np.empty(0)
		self.data_Nano33_az = np.empty(0)
		self.data_Update_rate = np.empty(0)
		self.data_time = np.empty(0)
		self.dt = np.empty(0)
		
		

	def plotADXLIMUnGYRO(self, dt, data_Adxl355_ax, data_Adxl355_ay, data_Adxl355_az,
						data_Nano33_ax, data_Nano33_ay, data_Nano33_az,
						data_Nano33_wx, data_Nano33_wy, data_Nano33_wz):
		if(self.act.runFlag):
		
			# dt = dt*1e-3
			self.time_cnt = self.time_cnt + 1
			
			if(self.old_dt > 0):
				update_time = dt - self.old_dt
				update_rate = 1000/update_time
				# print('update_time: ', update_time)
				# print('update rate: ', update_rate)
			self.old_dt = dt
			
			if (len(self.dt) >= 600):
				self.dt = self.dt[1:]
				
				self.data_Adxl355_ax = self.data_Adxl355_ax[1:]
				self.data_Adxl355_ay = self.data_Adxl355_ay[1:]
				self.data_Adxl355_az = self.data_Adxl355_az[1:]
				
				self.data_Nano33_ax = self.data_Nano33_ax[1:]
				self.data_Nano33_ay = self.data_Nano33_ay[1:]
				self.data_Nano33_az = self.data_Nano33_az[1:]
				
				self.data_Nano33_wx = self.data_Nano33_wx[1:]
				self.data_Nano33_wy = self.data_Nano33_wy[1:]
				self.data_Nano33_wz = self.data_Nano33_wz[1:]
			
				self.data_Update_rate = self.data_Update_rate[1:]
				
				self.data_time = self.data_Update_rate[1:]
				
				self.data_time = self.data_time[1:]
			
		
			#print label
			self.label_update_cnt = self.label_update_cnt + 1
			if(self.label_update_cnt==20):
				self.label_update_cnt = 0
				self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
			
			self.dt = np.append(self.dt, dt)
			
			self.data_Adxl355_ax = np.append(self.data_Adxl355_ax, data_Adxl355_ax)
			self.data_Adxl355_ay = np.append(self.data_Adxl355_ay, data_Adxl355_ay)
			self.data_Adxl355_az = np.append(self.data_Adxl355_az, data_Adxl355_az)
			
			self.data_Nano33_ax = np.append(self.data_Nano33_ax, data_Nano33_ax)
			self.data_Nano33_ay = np.append(self.data_Nano33_ay, data_Nano33_ay)
			self.data_Nano33_az = np.append(self.data_Nano33_az, data_Nano33_az)
			
			self.data_Nano33_wx = np.append(self.data_Nano33_wx, data_Nano33_wx)
			self.data_Nano33_wy = np.append(self.data_Nano33_wy, data_Nano33_wy)
			self.data_Nano33_wz = np.append(self.data_Nano33_wz, data_Nano33_wz)
			
			self.data_Update_rate = np.append(self.data_Update_rate, update_time) 
			
			self.data_time = np.append(self.data_time, self.time_cnt) 
			print(self.data_time[-1])
			
			
			
			if(self.save_status):
				np.savetxt(self.f, (	np.vstack([dt, data_Adxl355_ax, data_Adxl355_ay, data_Adxl355_az,
										data_Nano33_ax, data_Nano33_ay, data_Nano33_az, 
										data_Nano33_wx, data_Nano33_wy, data_Nano33_wz])).T,
						fmt='%10d, %5.5f, %5.5f, %5.5f, %5.5f, %5.5f, %5.5f, %5.5f, %5.5f, %5.5f')
				
			# print('len(self.data_time): ', len(self.data_time))
			# print('len(self.data_Adxl355_ax):', len(self.data_Adxl355_ax[0:-1]))
			
			if(DEBUG) :
				print('len(dt): ', len(self.dt))
				print('len(self.data_SRS200_wz): ', len(self.data_SRS200_wz))
				print('len(self.x200_arr): ', len(self.x200_arr))
				print('len(self.thetaz_SRS200_arr): ', len(self.thetaz_SRS200_arr))
				pass
						
			''' ********Tab1 plot1**********'''
			if(self.SRS200_wz_chk):
				# self.top.TabPlot.tab1_plot2_1.setData(self.dt, self.data_PP_wz*3600)#dph
				# self.top.TabPlot.tab1_plot1_1.setData(self.data_time, self.data_Adxl355_ax[0:-1])
				self.top.TabPlot.tab1_plot1_1.setData(self.data_Adxl355_ax)
				
			else:
				self.top.TabPlot.tab1_plot1_1.setData()
				
			if(self.PP_wz_chk):
				# self.top.TabPlot.tab1_plot2_1.setData(self.dt, self.data_PP_wz*3600)#dph
				self.top.TabPlot.tab1_plot1_2.setData(self.data_Adxl355_ay)
				# self.top.TabPlot.tab1_plot1_2.setData(self.data_time, self.data_Adxl355_ay[0:-1])
			else:
				self.top.TabPlot.tab1_plot1_2.setData()
				
			if(self.Nano33_wx_chk):
				# self.top.TabPlot.tab1_plot2_2.setData(self.dt, self.data_Nano33_wx*3600)#dph
				self.top.TabPlot.tab1_plot1_3.setData(self.data_Adxl355_az)
				# self.top.TabPlot.tab1_plot1_3.setData(self.data_time, self.data_Adxl355_az[0:-1])
			else:
				self.top.TabPlot.tab1_plot1_3.setData()
			if(self.Nano33_wy_chk):
				# self.top.TabPlot.tab1_plot2_3.setData(self.dt, self.data_Nano33_wy*3600)
				self.top.TabPlot.tab1_plot1_4.setData()
			else:
				self.top.TabPlot.tab1_plot1_4.setData()
			if(self.Nano33_wz_chk):
				# self.top.TabPlot.tab1_plot2_4.setData(self.dt, self.data_Nano33_wz*3600)
				self.top.TabPlot.tab1_plot1_5.setData()
			else:
				self.top.TabPlot.tab1_plot1_5.setData()
				
			''' ********Tab1 plot2**********'''
			if(self.Adxl355_ax_chk):
				self.top.TabPlot.tab1_plot2_1.setData(self.data_Nano33_ax)
			else:
				self.top.TabPlot.tab1_plot2_1.setData()
				
			if(self.Adxl355_ay_chk):
				self.top.TabPlot.tab1_plot2_2.setData(self.data_Nano33_ay)
				# print(self.data_Adxl355_ay)
			else:
				self.top.TabPlot.tab1_plot2_2.setData()
				
			if(self.Adxl355_az_chk):
				self.top.TabPlot.tab1_plot2_3.setData(self.data_Nano33_az)
			else:
				self.top.TabPlot.tab1_plot2_3.setData()
				
				
				
			''' ********Tab1 plot3**********'''
			if(self.VBOX_v_chk):
				self.top.TabPlot.tab1_plot3_1.setData(self.data_Update_rate) #km/h
			else:
				self.top.TabPlot.tab1_plot3_1.setData()
			if(self.IMU_v_chk):
				# self.top.TabPlot.tab1_plot3_2.setData(self.dt, self.data_IMU_speed*3.6) #km/h
				self.top.TabPlot.tab1_plot3_2.setData()
			else:
				self.top.TabPlot.tab1_plot3_2.setData()
				
			''' ********Tab1 plot4**********'''
			if(self.roll_chk):
				self.top.TabPlot.tab1_plot4_1.setData(self.data_Nano33_wx)
			else:
				self.top.TabPlot.tab1_plot4_1.setData()
				
			if(self.pitch_chk):
				self.top.TabPlot.tab1_plot4_2.setData(self.data_Nano33_wy)
			else:
				self.top.TabPlot.tab1_plot4_2.setData()
			
			if(self.heading_chk):
				self.top.TabPlot.tab1_plot4_3.setData(self.data_Nano33_wz) 
			else:
				self.top.TabPlot.tab1_plot4_3.setData()
			

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
	

