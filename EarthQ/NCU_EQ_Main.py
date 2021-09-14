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
import NCU_EQ_Widget as UI 
import NCU_EQ_Action as ACT
import NCU_EQ_Globals as globals

PRINT_VBOX_MAIN = 0
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

MAX_DATA_NUM = 1_000_000
DIRNAME = os.path.dirname(__file__) #get path of current file 
# print(dirname)
DATAPATH = os.path.join(DIRNAME, 'data') #enter the directory name to save data
# print(dataPath)

''' VBOX conversion factor'''
# https://reurl.cc/rgOZzy
latitude_factor = 0.0000001		#degree
longitude_factor = 0.0000001	#degree
velocity_factor = 0.001/3.6 	#m/s
altitude_factor = 0.01			#m
v_velocity_factor = 0.001		#m/s
pitch_factor = 0.01				#deg
roll_factor = 0.01				#deg
heading_factor = 0.01			#deg
accz_factor = 0.01				#m/s^2

class mainWindow(QMainWindow):
	''' define and initiate global variable '''
	# EQ_idx = 0
	# EQ_cnt = SAVE_DATA_NUM 
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
	''' auto save global variable'''
	g_busy = 0
	g_data_ptr = MAX_DATA_NUM
	g_idx = 1
	old_dirName_year = datetime.datetime.now().year
	old_dirName_month = datetime.datetime.now().month
	test_data = 0
	g_stop = 0
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
		self.act.fog_update20.connect(self.plotADXLIMUnGYRO)
		self.act.fog_update13.connect(self.calibADXLIMUnGYRO)
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
		self.top.TabPlot.tab1_gyro_cb.cb1.setChecked(True) #set gyro wz initial as PP
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
		# self.wz_offset = float(self.top.wzOffset_le.text())
		# self.wzVth = float(self.top.wzVth_le.text())
		# self.act.offset_wz = self.wz_offset  
		# self.act.wzVth = self.wzVth
		
		# self.wz200_offset = float(self.top.wz200Offset_le.text())
		# self.act.offset_wz200 = self.wz200_offset  
		
		# self.wx_offset = float(self.top.wxOffset_le.text())
		# self.wxVth = float(self.top.wxVth_le.text())
		# self.act.offset_wx = self.wx_offset  
		# self.act.wxVth = self.wxVth
		
		# self.wy_offset = float(self.top.wyOffset_le.text())
		# self.wyVth = float(self.top.wyVth_le.text())
		# self.act.offset_wy = self.wy_offset  
		# self.act.wyVth = self.wyVth
		
		# self.ax_offset = float(self.top.axOffset_le.text())
		# self.axVth = float(self.top.axVth_le.text())
		# self.act.offset_ax = self.ax_offset  
		# self.act.axVth = 0
		
		# self.ADax_offset = float(self.top.axOffsetAD_le.text())
		# self.act.offset_ADax = self.ADax_offset 
		
		# self.ay_offset = float(self.top.ayOffset_le.text())
		# self.ayVth = float(self.top.wyVth_le.text())
		# self.act.offset_ay = self.ay_offset  
		# self.act.ayVth = 0
		
		# self.ADay_offset = float(self.top.ayOffsetAD_le.text())
		# self.act.offset_ADay = self.ADay_offset
		print('change')
	
	def versionBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)
	
			
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
		# self.speedx_Nano33_arr = np.empty(0)
		# self.speedy_Nano33_arr = np.empty(0)
		# self.speed_Nano33_arr = np.empty(0)
		# self.x_arr = np.zeros(0)
		# self.y_arr = np.zeros(0)
		self.xNano33_sum = 0
		self.yNano33_sum = 0
		self.xPP_sum = 0
		self.yPP_sum = 0
		self.x200_sum = 0
		self.y200_sum = 0
		# self.dx_arr = np.zeros(0)
		# self.dy_arr = np.zeros(0)
		self.x200_arr = np.zeros(0)
		self.y200_arr = np.zeros(0)
		self.xNano33_arr = np.zeros(0)
		self.yNano33_arr = np.zeros(0)
		self.xPP_arr = np.zeros(0)
		self.yPP_arr = np.zeros(0)
		
	def autoCreateDir(self, dataPath, dirName, busy, rst_n):
		filepath = os.path.join(dataPath, str(dirName))
		if (not busy and rst_n):
			folder_exist = os.path.exists(filepath)
			if not folder_exist:
				print('\ncreate folder: ', filepath)
				os.mkdir(filepath)
				status = 0
			else:
				print('folder exist!')
				status = 1
		else:
			status = 2
		return status, filepath
	
	def open_and_save_data(self, data_ptr, max_dataNum, rst_n, filePath, idx, data1, data2, data3, data4, data5, data6, data7, data8, data9):
		
		if(data_ptr == max_dataNum): 
			print('create txt')
			self.fauto=open(os.path.join(filePath, str(datetime.datetime.now().day) + '-' + str(idx)) +'.txt', 'w')
			self.fauto.writelines('#' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + '\n')
			np.savetxt(self.fauto, np.vstack([data1, data2, data3, data4, data5, data6, data7, data8, data9]).T, 
				fmt='%5.3f,\t\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f')
					#   dt, srs200,   pp,    nano33_wx, nano33_wy, nano33_wz,  adxl_ax,       adxl_ay,    adxl_az
			busy = 1
			status = 0
			
		elif(data_ptr == 1 or rst_n == 0):
			print('close txt')
			np.savetxt(self.fauto, np.vstack([data1, data2, data3, data4, data5, data6, data7, data8, data9]).T, 
				fmt='%5.3f,\t\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f')
			self.fauto.writelines('#' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + '\n')
			self.fauto.close()
			busy = 0
			status = 1
		else:
			# print('save txt')
			np.savetxt(self.fauto, np.vstack([data1, data2, data3, data4, data5, data6, data7, data8, data9]).T, 
				fmt='%5.3f,\t\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f,\t%5.5f')
			busy = 1
			status = 2
		return status, busy
	
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
	
	def open_file(self, filename):
		print('in open_file')
		self.f=open(filename, 'w')
		# self.f2=open(filename[0:-4] + '_track.txt', 'w')
		start_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.f.writelines('#' + start_time_header + '\n')
		#dt, data_SRS200_wz_f, data_PP_wz_f, data_Adxl355_ax_f, data_Adxl355_ay_f, data_Adxl355_az_f
		#		,speedx_Adxl355_out, speedy_Adxl355_out, speed_Adxl355_out, data_IMU_speed_f, data_T
		# self.f.writelines('#' + 'dt:s, SRS200:DPS, PP:DPS, Nano33_wx:DPS, Nano33_wy:DPS, Nano33_wz:DPS, Adxl355_ax:g, '
		# +'Adxl355_ay:g, Adxl355_az:g, VBOX_speed(m/s), v_speed(m/s), T, latitude(deg), longitude(deg) altitude(m), gpssat, pitch(deg), roll(deg), heading(deg)' + '\n')
		#dt:s, SRS200:DPS, PP:DPS, Nano33_wx:DPS, Nano33_wy:DPS, Nano33_wz:DPS, Adxl355_ax:g, Adxl355_ay:g, Adxl355_az:g, adxl355_speed, VBOX_speed, T
		self.f.writelines('#' + 'dt:s, SRS200:DPS, PP:DPS, Nano33_wx:DPS, Nano33_wy:DPS, Nano33_wz:DPS, Adxl355_ax:g, '
		+'Adxl355_ay:g, Adxl355_az:g' + '\n')
		#   dt, srs200,   pp,    nano33_wx, nano33_wy, nano33_wz,  adxl_ax, adxl_ay,  adxl_az,  vbox_v,  lat,    lon,    gps,    h,   v_velo
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
		
		# self.top.TabPlot.lb.setText(str(self.act.bufferSize))
		offset_SRS200_wz = 0
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
		offset_T = 0
		
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
			print('in close_file')
			stop_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			self.f.writelines('#' + stop_time_header + '\n')
			self.f.close()
			# self.f2.close()
			
		''' ********auto save function************'''
		dummy, self.g_busy = self.open_and_save_data(self.g_data_ptr, MAX_DATA_NUM, self.act.runFlag, self.temp_filepath, self.g_idx, 
			self.dt[-1],self.data_SRS200_wz[-1]/3600,self.data_PP_wz[-1]/3600,self.data_Nano33_wx[-1],self.data_Nano33_wy[-1],
			self.data_Nano33_wz[-1],self.data_Adxl355_ax[-1],self.data_Adxl355_ay[-1],self.data_Adxl355_az[-1])
		
		self.g_idx = self.g_idx + 1
		self.g_data_ptr = MAX_DATA_NUM
		self.g_stop = 1	 #用於stop後再read遇到換年/月情況
		''' ********end of auto save function************'''
			
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
		self.dt = np.empty(0)
		self.data_T = np.empty(0)
		self.data_velocity = np.empty(0)
		self.data_roll = np.empty(0)
		self.data_pitch = np.empty(0)
		self.data_heading = np.empty(0)
		self.data_accz = np.empty(0)
		
		self.speed_Nano33_arr = np.empty(0)
		self.speed_Adxl355_arr = np.empty(0)
		self.thetaz_Nano33 = 0
		self.thetaz_PP = 0
		self.thetaz_SRS200 = 0
		self.thetax = 0
		self.thetay = 0
		self.speed_Nano33 = 0
		self.speedx_Nano33 = 0
		self.speedy_Nano33 = 0
		self.speed_Adxl355 = 0
		self.speedx_Adxl355 = 0
		self.speedy_Adxl355 = 0
		self.x200_arr = np.zeros(0)
		self.y200_arr = np.zeros(0)
		self.data_Adxl355_ax_f = 0
		self.data_Adxl355_ay_f = 0
		self.data_Adxl355_az_f = 0
		self.old_speedx_Adxl355 = 0
		self.old_speedy_Adxl355 = 0
		self.dt_old = 0
		self.data_SRS200_wz_f_old = 0
		self.data_Nano33_wx_f_old = 0
		self.data_Nano33_wy_f_old = 0
		self.data_Nano33_wz_f_old = 0
		self.data_PP_wz_f_old = 0
		
		
	def plotADXLIMUnGYRO(self, dt, data_SRS200_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay, data_Adxl355_az, data_T, 
						data_Nano33_wx, data_Nano33_wy, data_Nano33_wz, gpssat, latitude, longitude, velocity, altitude, v_velocity, 
							pitch, roll, heading, accz):
		if(PRINT_VBOX_MAIN):
			print('gpssat: ', gpssat)
			print('latitude: ', latitude)
			print('longitude: ', longitude)
			print('velocity: ', velocity)
			print('altitude: ', altitude)
			print('v_velocity: ', v_velocity)
			# print('pitch: ', pitch)
			# print('roll: ', roll)
			# print('heading: ', heading)
			print('accz: ', accz)
				
			if(DEBUG_COM):
				print('2. data_SRS200_wz: ', end='\t');
				print(data_SRS200_wz)
			pass
		dt = dt*1e-3
		if (len(self.dt) >= 300):
			self.dt = self.dt[self.act.data_frame_update_point:]
			self.data_T = self.data_T[self.act.data_frame_update_point:]
			self.data_SRS200_wz = self.data_SRS200_wz[self.act.data_frame_update_point:]
			self.data_Nano33_wx = self.data_Nano33_wx[self.act.data_frame_update_point:]
			self.data_Nano33_wy = self.data_Nano33_wy[self.act.data_frame_update_point:]
			self.data_Nano33_wz = self.data_Nano33_wz[self.act.data_frame_update_point:]
			self.data_PP_wz = self.data_PP_wz[self.act.data_frame_update_point:]
			self.data_IMU_speed = self.data_IMU_speed[self.act.data_frame_update_point:]
			self.data_Adxl355_ax = self.data_Adxl355_ax[self.act.data_frame_update_point:]
			self.data_Adxl355_ay = self.data_Adxl355_ay[self.act.data_frame_update_point:]
			self.data_Adxl355_az = self.data_Adxl355_az[self.act.data_frame_update_point:]
			
			self.data_velocity = self.data_velocity[self.act.data_frame_update_point:]
			self.data_roll = self.data_roll[self.act.data_frame_update_point:]
			self.data_pitch = self.data_pitch[self.act.data_frame_update_point:]
			self.data_heading = self.data_heading[self.act.data_frame_update_point:]
			self.data_accz = self.data_accz[self.act.data_frame_update_point:]
		
		
		data_SRS200_wz_f = (data_SRS200_wz-self.offset_SRS200_wz)*gyro200_factor*1.17122 #DPH
		data_Nano33_wx_f = (data_Nano33_wx-self.offset_Nano33_wx)*gyro_factor
		data_Nano33_wy_f = (data_Nano33_wy-self.offset_Nano33_wy)*gyro_factor
		data_Nano33_wz_f = (data_Nano33_wz-self.offset_Nano33_wz)*gyro_factor
		# data_PP_wz_f = (1.97-(data_PP_wz)*gyroPP_factor)/3600*1.11098 + 0.01714
		data_PP_wz_f = (1.97-(data_PP_wz-self.offset_PP_wz)*gyroPP_factor)*1.11098 #DPH
		# data_PP_wz_f = (data_PP_wz)*gyro200_factor*1.17122/3600 + 0.01528#convert to DPS
		# data_IMU_speed_f = (0)*IMU_speed_factor/3.6 #convert to m/s
		# data_IMU_speed_f = (data_IMU_speed - 0)*IMU_speed_factor/3.6 #convert to m/s
		data_Adxl355_ax_f = (data_Adxl355_ax-self.offset_Adxl355_ax)*ADxlm_factor
		data_Adxl355_ay_f = (data_Adxl355_ay-self.offset_Adxl355_ay)*ADxlm_factor
		data_Adxl355_az_f = (data_Adxl355_az-self.offset_Adxl355_az)*ADxlm_factor
		
		'''***************auto save data ************************** '''
		if(not self.save_status and self.act.runFlag): #若使用手動輸入檔名，則disable自動存檔功能
			dirName_year = datetime.datetime.now().year
			dirName_month = datetime.datetime.now().month
			if(dirName_year != self.old_dirName_year or dirName_month != self.old_dirName_month): #當年分或月份改變時(換年or換日)，reset idx。會比busy=0還早發生
				if(self.g_stop):
					self.g_idx = 1
				else:
					self.g_idx = 0 
			self.g_stop = 0
			status, filepath1 = self.autoCreateDir(DATAPATH,  dirName_year,  self.g_busy, self.act.runFlag)
			status, filepath2 = self.autoCreateDir(filepath1, dirName_month, self.g_busy, self.act.runFlag)
			self.temp_filepath = filepath2
			if(self.g_data_ptr == 0):#資料數量指標=1時代表關閉檔案了，此時reset至MAX_DATA_NUM
				self.g_data_ptr = MAX_DATA_NUM
			# print('bbbbbbbb')
			dummy, self.g_busy = self.open_and_save_data(self.g_data_ptr, MAX_DATA_NUM, self.act.runFlag, filepath2, self.g_idx, 
				dt, data_SRS200_wz_f/3600, data_PP_wz_f/3600, data_Nano33_wx_f, data_Nano33_wy_f, data_Nano33_wz_f,
				data_Adxl355_ax_f, data_Adxl355_ay_f, data_Adxl355_az_f) 
			
			self.g_data_ptr = self.g_data_ptr - 1
			if(self.g_busy==0): #寫完數據，若發生換年or換日則g_idx此時=0
				self.g_idx += 1
			self.old_dirName_year =  dirName_year
			self.old_dirName_month = dirName_month
		'''***************end of auto save data ************************** '''
		
		''' VBOX data convert to float'''
		data_latitude_f = 	latitude*latitude_factor
		data_longitude_f = 	longitude*longitude_factor
		data_velocity_f = 	velocity*velocity_factor
		data_altitude_f = 	altitude*altitude_factor
		data_v_velocity_f = v_velocity*v_velocity_factor
		data_pitch_f = 		pitch*pitch_factor
		data_roll_f = 		roll*roll_factor
		data_heading_f = 	heading*heading_factor
		data_accz_f = 		accz*accz_factor
		data_gpssat_f = gpssat
			

		'''由角速率積分計算角度，積分時間為data_frame_update_point*(1/ODR), ODR=100Hz'''
		self.thetaz_Nano33 = self.thetaz_Nano33 - np.sum(data_Nano33_wz_f)*SAMPLING_TIME #負號是方向判斷的問題, 0.01是1/ODR
		self.thetaz_Nano33_arr = np.append(self.thetaz_Nano33_arr, self.thetaz_Nano33)
		
		self.thetaz_SRS200 = self.thetaz_SRS200 - np.sum(data_SRS200_wz_f)*SAMPLING_TIME #負號是方向判斷的問題
		self.thetaz_SRS200_arr = np.append(self.thetaz_SRS200_arr, self.thetaz_SRS200)
		
		self.thetaz_PP = self.thetaz_PP - np.sum(data_PP_wz_f)*SAMPLING_TIME #負號是方向判斷的問題
		self.thetaz_PP_arr = np.append(self.thetaz_PP_arr, self.thetaz_PP)
		
		if(PRINT_DEGREE):
			print(np.round(self.thetaz_SRS200, 2), end=', ')
			print(np.round(self.thetaz_PP, 2), end=', ')
			print(np.round(self.thetaz_Nano33, 2))
		
		
		
		''' for track plot'''
		thetaz_Nano33 = 90 - self.thetaz_Nano33
		thetaz_PP = 90 - self.thetaz_PP
		thetaz_SRS200 = 90 - self.thetaz_SRS200
		'''
		dx = dr*cos(theta), dr = vdt
		v = 1 m/s
		dt = data_frame_update_point*self.act.TIME_PERIOD 
		'''
		if(USE_FAKE_SPEED):
			dxNano33 = np.cos(thetaz_Nano33*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			dyNano33 = np.sin(thetaz_Nano33*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		else:
			# dxNano33 = self.speed_Adxl355*np.cos(thetaz_Nano33*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			# dyNano33 = self.speed_Adxl355*np.sin(thetaz_Nano33*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
			dxNano33 = data_IMU_speed_f*np.cos(thetaz_Nano33*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			dyNano33 = data_IMU_speed_f*np.sin(thetaz_Nano33*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.xNano33_sum = self.xNano33_sum + dxNano33
		self.yNano33_sum = self.yNano33_sum + dyNano33
		
		if(USE_FAKE_SPEED):
			dxPP = np.cos(thetaz_PP*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			dyPP = np.sin(thetaz_PP*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		else: 
			# dxPP = self.speed_Adxl355*np.cos(thetaz_PP*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			# dyPP = self.speed_Adxl355*np.sin(thetaz_PP*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
			dxPP = data_IMU_speed_f*np.cos(thetaz_PP*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			dyPP = data_IMU_speed_f*np.sin(thetaz_PP*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.xPP_sum = self.xPP_sum + dxPP
		self.yPP_sum = self.yPP_sum + dyPP
		
		if(USE_FAKE_SPEED):
			dx200 = np.cos(thetaz_SRS200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			dy200 = np.sin(thetaz_SRS200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		else:
			# dx200 = self.speed_Adxl355*np.cos(thetaz_SRS200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			# dy200 = self.speed_Adxl355*np.sin(thetaz_SRS200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
			dx200 = data_IMU_speed_f*np.cos(thetaz_SRS200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
			dy200 = data_IMU_speed_f*np.sin(thetaz_SRS200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.x200_sum = self.x200_sum + dx200
		self.y200_sum = self.y200_sum + dy200
		
		#print label
		self.label_update_cnt = self.label_update_cnt + 1
		if(self.label_update_cnt==20):
			self.label_update_cnt = 0
			self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
			self.top.VBOX_latitude_lb.lb.setText(str(np.round(data_latitude_f,7)))
			self.top.VBOX_longitude_lb.lb.setText(str(np.round(data_longitude_f,7)))
			# self.top.VBOX_v_velocity_lb.lb.setText(str(np.round(data_v_velocity_f,3))) 
			self.top.VBOX_v_velocity_lb.lb.setText(str(np.round(data_velocity_f*3.6,3)))
			self.top.VBOX_sat_lb.lb.setText(str(data_gpssat_f))
			self.top.VBOX_altitude_lb.lb.setText(str(np.round(data_altitude_f, 2)))
			self.top.VBOX_accz_lb.lb.setText(str(round(data_accz_f, 2)))
		
		# self.dx_arr = np.append(self.dx_arr, dx)
		# self.dy_arr = np.append(self.dy_arr, dy)
		# self.x_arr = np.append(self.x_arr, self.x_sum)
		# self.y_arr = np.append(self.y_arr, self.y_sum)
		
		# self.dx200_arr = np.append(self.dx200_arr, dx200)
		# self.dy200_arr = np.append(self.dy200_arr, dy200)
		
		self.track_cnt = self.track_cnt + 1
		if(self.track_cnt == TRACK_UPDATE_CNT):
			self.track_cnt = 0
			self.x200_arr = np.append(self.x200_arr, self.x200_sum)
			self.y200_arr = np.append(self.y200_arr, self.y200_sum)
			self.xPP_arr = np.append(self.xPP_arr, self.xPP_sum)
			self.yPP_arr = np.append(self.yPP_arr, self.yPP_sum)
			self.xNano33_arr = np.append(self.xNano33_arr, self.xNano33_sum)
			self.yNano33_arr = np.append(self.yNano33_arr, self.yNano33_sum)
			# if(self.save_status):
				# np.savetxt(self.f2, (np.vstack([self.x200_arr[-1], self.y200_arr[-1],self.xPP_arr[-1], self.yPP_arr[-1],self.xNano33_arr[-1], self.yNano33_arr[-1]])).T, fmt='%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f')
			# print(self.x200_sum, end=', ')
			# print(self.y200_sum, end=', ')
			# print(self.xNano33_sum, end=', ')
			# print(self.yNano33_sum)
			
			
		if (len(self.thetaz_SRS200_arr) >= 3000):
			self.thetaz_Nano33_arr = self.thetaz_Nano33_arr[1:]
			self.thetaz_PP_arr = self.thetaz_PP_arr[1:]
			self.thetaz_SRS200_arr = self.thetaz_SRS200_arr[1:]
			# self.thetax_arr = self.thetax_arr[1:]
			# self.thetay_arr = self.thetay_arr[1:]
			# self.speedx_Nano33_arr = self.speedx_Nano33_arr[1:]
			# self.speedy_Nano33_arr = self.speedy_Nano33_arr[1:]
			# self.speed_Nano33_arr = self.speed_Nano33_arr[1:]
			self.speed_Adxl355_arr = self.speed_Adxl355_arr[1:]
			# self.dx_arr = self.dx_arr[1:]
			# self.dy_arr = self.dy_arr[1:]
			# self.dx200_arr = self.dx200_arr[1:]
			# self.dy200_arr = self.dy200_arr[1:]
			# self.x_arr = self.x_arr[1:]
			# self.y_arr = self.y_arr[1:]
			
		if (len(self.x200_arr) >= 3000):
			self.x200_arr = self.x200_arr[1:]
			self.y200_arr = self.y200_arr[1:]
			self.xNano33_arr = self.xNano33_arr[1:]
			self.yNano33_arr = self.yNano33_arr[1:]
			self.xPP_arr = self.xPP_arr[1:]
			self.yPP_arr = self.yPP_arr[1:]
			
		
		self.data_SRS200_wz  = np.append(self.data_SRS200_wz,  data_SRS200_wz_f)
		self.data_Nano33_wx = np.append(self.data_Nano33_wx, data_Nano33_wx_f)
		self.data_Nano33_wy = np.append(self.data_Nano33_wy, data_Nano33_wy_f)
		self.data_Nano33_wz = np.append(self.data_Nano33_wz, data_Nano33_wz_f)
		# print('np:', float(self.data_Nano33_wz[-1]))
		# print(data_Nano33_wz_f)
		self.data_PP_wz = np.append(self.data_PP_wz, data_PP_wz_f)
		self.data_velocity = np.append(self.data_velocity, data_velocity_f)
		# print('data_velocity_f: ', data_velocity_f)
		self.data_roll = np.append(self.data_roll, data_roll_f)
		self.data_pitch = np.append(self.data_pitch, data_pitch_f)
		self.data_heading = np.append(self.data_heading, data_heading_f)
		self.data_accz = np.append(self.data_accz, data_accz_f)
		# self.data_IMU_speed = np.append(self.data_IMU_speed, data_IMU_speed_f)
		self.data_Adxl355_ax = np.append(self.data_Adxl355_ax, data_Adxl355_ax_f)
		self.data_Adxl355_ay = np.append(self.data_Adxl355_ay, data_Adxl355_ay_f)
		self.data_Adxl355_az = np.append(self.data_Adxl355_az, data_Adxl355_az_f)
		# self.data_Nano33_ax = np.append(self.data_Nano33_ax, data_Nano33_ax_f)
		# self.data_Nano33_ay = np.append(self.data_Nano33_ay, data_Nano33_ay_f)
		self.dt = np.append(self.dt, dt)
		self.data_T = np.append(self.data_T, (data_T-self.offset_T)*1e-3)
		
		if(self.save_status):
			np.savetxt(self.f, (np.vstack([dt, data_SRS200_wz_f/3600, data_PP_wz_f/3600, data_Nano33_wx_f, data_Nano33_wy_f, data_Nano33_wz_f, 
				data_Adxl355_ax_f, data_Adxl355_ay_f, data_Adxl355_az_f])).T, 
					fmt='%5.3f,  %5.5f,  %5.5f,   %5.5f,    %5.5f,       %5.5f,     %5.5f,        %5.5f,     %5.5f')
						#   dt, srs200,   pp,    nano33_wx, nano33_wy, nano33_wz,  adxl_ax,       adxl_ay,    adxl_az
		if(DEBUG) :
			print('len(dt): ', len(self.dt))
			print('len(self.data_SRS200_wz): ', len(self.data_SRS200_wz))
			print('len(self.x200_arr): ', len(self.x200_arr))
			print('len(self.thetaz_SRS200_arr): ', len(self.thetaz_SRS200_arr))
			# print('dt: ', self.dt[0])
			# print('SRS200_wz: ', self.data_SRS200_wz[0])
			# print('Nano33_wz: ', self.data_Nano33_wz[0])
			# print('PP_wz: ', self.data_PP_wz[0])
			# print('Adxl355_ax: ', self.data_Adxl355_ax[0])
			# print('Adxl355_ay: ', self.data_Adxl355_ay[0])
			# print('Nano33_ax: ', self.data_Nano33_ax[0])
			# print('Nano33_ay: ', self.data_Nano33_ay[0])
			
			pass
					
		''' save old data'''
		# self.dt_old = dt
		# self.data_SRS200_wz_f_old = data_SRS200_wz_f
		# self.data_Nano33_wx_f_old = data_Nano33_wx_f
		# self.data_Nano33_wy_f_old = data_Nano33_wy_f
		# self.data_Nano33_wz_f_old = data_Nano33_wz_f
		# self.data_PP_wz_f_old = data_PP_wz_f
		
		#data_SRS200_wz 
		# self.top.TabPlot.tab1_plot1.setData(self.dt, self.data_SRS200_wz*3600) #dph
		# self.top.TabPlot.tab1_plot1.setData(self.dt, self.data_SRS200_wz) #dps
		# self.top.TabPlot.tab1_plot1_2.setData(self.dt, self.data_PP_wz)
			
		''' ********Tab1 plot1**********'''
		# if(self.SRS200_wz_chk):
			# self.top.TabPlot.tab1_plot1_1.setData(self.dt, self.data_SRS200_wz)#dph
		# else:
			# self.top.TabPlot.tab1_plot1_1.setData()
			
		self.top.TabPlot.tab1_plot_w1.setData(self.dt, self.data_SRS200_wz)#dph
			
		# if(self.PP_wz_chk):
			# self.top.TabPlot.tab1_plot1_2.setData(self.dt, self.data_PP_wz)#dph
		# else:
			# self.top.TabPlot.tab1_plot1_2.setData()
		self.top.TabPlot.tab1_plot_w2.setData(self.dt, self.data_PP_wz)#dph
			
		'''
		if(self.Nano33_wx_chk):
			self.top.TabPlot.tab1_plot1_3.setData(self.dt, self.data_Nano33_wx*3600)#dph
			# self.top.TabPlot.tab1_plot1_3.setData(self.dt, self.data_Nano33_wx)#dps
		else:
			self.top.TabPlot.tab1_plot1_3.setData()
		'''
		self.top.TabPlot.tab1_plot_w3.setData(self.dt, self.data_Nano33_wx*3600)#dph
			
		'''
		if(self.Nano33_wy_chk):
			self.top.TabPlot.tab1_plot1_4.setData(self.dt, self.data_Nano33_wy*3600)#dph
			# self.top.TabPlot.tab1_plot1_4.setData(self.dt, self.data_Nano33_wy)
		else:
			self.top.TabPlot.tab1_plot1_4.setData()
		'''
		self.top.TabPlot.tab1_plot_w4.setData(self.dt, self.data_Nano33_wy*3600)#dph
			
		'''
		if(self.Nano33_wz_chk):
			self.top.TabPlot.tab1_plot1_5.setData(self.dt, self.data_Nano33_wz*3600)
			# self.top.TabPlot.tab1_plot1_5.setData(self.dt, self.data_Nano33_wz)
		else:
			self.top.TabPlot.tab1_plot1_5.setData()
		'''
		self.top.TabPlot.tab1_plot_w5.setData(self.dt, self.data_Nano33_wz*3600)#dph
		
		
		''' ********Tab1 plot2**********'''
		# if(self.Adxl355_ax_chk):
			# self.top.TabPlot.tab1_plot2_1.setData(self.dt, self.data_Adxl355_ax)
		# else:
			# self.top.TabPlot.tab1_plot2_1.setData()
		self.top.TabPlot.tab1_plot_a1.setData(self.dt, self.data_Adxl355_ax)#g
		
		# if(self.Adxl355_ay_chk):
			# self.top.TabPlot.tab1_plot2_2.setData(self.dt, self.data_Adxl355_ay)
		# else:
			# self.top.TabPlot.tab1_plot2_2.setData()
		self.top.TabPlot.tab1_plot_a2.setData(self.dt, self.data_Adxl355_ay)#g
		
		# if(self.Adxl355_az_chk):
			# self.top.TabPlot.tab1_plot2_3.setData(self.dt, self.data_Adxl355_az)
		# else:
			# self.top.TabPlot.tab1_plot2_3.setData()
		self.top.TabPlot.tab1_plot_a3.setData(self.dt, self.data_Adxl355_az)#g
		
		# if(self.Adxl355_T_chk):
			# self.top.TabPlot.tab1_plot3_4.setData(self.dt, self.data_T)
		# else:
			# self.top.TabPlot.tab1_plot3_4.setData()
			
		# if(self.Nano33_ax_chk):
			# self.top.TabPlot.tab1_plot3_3.setData(self.dt, self.data_Nano33_ax)
		# else:
			# self.top.TabPlot.tab1_plot3_3.setData()
		# if(self.Nano33_ay_chk):
			# self.top.TabPlot.tab1_plot3_4.setData(self.dt, self.data_Nano33_ay)
		# else:
			# self.top.TabPlot.tab1_plot3_4.setData()
		# if(self.Adxl355_ax_chk or self.Adxl355_ay_chk or self.Nano33_ax_chk or self.Nano33_ay_chk):
			# self.top.TabPlot.tab1_plot3.figure.canvas.draw()		
			# self.top.TabPlot.tab1_plot3.figure.canvas.flush_events()
			
			
		
			
	def calibADXLIMUnGYRO(self, data_SRS200_wz, data_Nano33_wx, data_Nano33_wy, data_Nano33_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay,
									data_Adxl355_az, data_Nano33_ax, data_Nano33_ay, data_Nano33_az, data_T, data_IMU_speed):
		# print('calibADXLIMUnGYRO')
		if (len(self.data_SRS200_wz) >= 100):
			self.data_SRS200_wz = self.data_SRS200_wz[self.act.data_frame_update_point:]
			self.data_Nano33_wx = self.data_Nano33_wx[self.act.data_frame_update_point:]
			self.data_Nano33_wy = self.data_Nano33_wy[self.act.data_frame_update_point:]
			self.data_Nano33_wz = self.data_Nano33_wz[self.act.data_frame_update_point:]
			self.data_PP_wz = self.data_PP_wz[self.act.data_frame_update_point:]
			self.data_Adxl355_ax = self.data_Adxl355_ax[self.act.data_frame_update_point:]
			self.data_Adxl355_ay = self.data_Adxl355_ay[self.act.data_frame_update_point:]
			self.data_Adxl355_az = self.data_Adxl355_az[self.act.data_frame_update_point:]
			self.data_Nano33_ax = self.data_Nano33_ax[self.act.data_frame_update_point:]
			self.data_Nano33_ay = self.data_Nano33_ay[self.act.data_frame_update_point:]
			self.data_Nano33_az = self.data_Nano33_az[self.act.data_frame_update_point:]
			self.data_T = self.data_T[self.act.data_frame_update_point:]
			self.data_IMU_speed = self.data_IMU_speed[self.act.data_frame_update_point:]
			
		self.data_SRS200_wz  = np.append(self.data_SRS200_wz,  data_SRS200_wz)
		self.data_Nano33_wx = np.append(self.data_Nano33_wx, data_Nano33_wx)
		self.data_Nano33_wy = np.append(self.data_Nano33_wy, data_Nano33_wy)
		self.data_Nano33_wz = np.append(self.data_Nano33_wz, data_Nano33_wz)
		self.data_PP_wz = np.append(self.data_PP_wz, data_PP_wz)
		self.data_Adxl355_ax = np.append(self.data_Adxl355_ax, data_Adxl355_ax)
		self.data_Adxl355_ay = np.append(self.data_Adxl355_ay, data_Adxl355_ay)
		self.data_Adxl355_az = np.append(self.data_Adxl355_az, data_Adxl355_az)
		self.data_Nano33_ax = np.append(self.data_Nano33_ax, data_Nano33_ax)
		self.data_Nano33_ay  = np.append(self.data_Nano33_ay,  data_Nano33_ay)
		self.data_Nano33_az  = np.append(self.data_Nano33_az,  data_Nano33_az)
		self.data_T  = np.append(self.data_T,  data_T)
		self.data_IMU_speed = np.append(self.data_IMU_speed, data_IMU_speed)
		
		self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
		
		self.offset_T = np.round(np.average(self.data_T),3)
		# print('self.offset_T: ', self.offset_T)
		
		self.offset_SRS200_wz = np.round(np.average(self.data_SRS200_wz),3)
		self.std_SRS200_wz = np.round(np.std(self.data_SRS200_wz), 3)
		self.top.TabPlot.tab2_SRS200.lb1.setText(str(self.offset_SRS200_wz))
		self.top.TabPlot.tab2_SRS200.lb2.setText(str(self.std_SRS200_wz))
		
		self.offset_PP_wz = np.round(np.average(self.data_PP_wz),3)
		self.std_PP_wz = np.round(np.std(self.data_PP_wz), 3)
		self.top.TabPlot.tab2_PP.lb1.setText(str(self.offset_PP_wz))
		self.top.TabPlot.tab2_PP.lb2.setText(str(self.std_PP_wz))
		
		self.offset_IMU_speed = np.round(np.average(self.data_IMU_speed),3)
		self.std_IMU_speed = np.round(np.std(self.data_IMU_speed), 3)
		self.top.TabPlot.tab2_IMU_speed.lb1.setText(str(self.offset_IMU_speed))
		self.top.TabPlot.tab2_IMU_speed.lb2.setText(str(self.std_IMU_speed))
		
		self.offset_Nano33_wx = np.round(np.average(self.data_Nano33_wx),3)
		self.std_Nano33_wx = np.round(np.std(self.data_Nano33_wx), 3)
		self.offset_Nano33_wy = np.round(np.average(self.data_Nano33_wy),3)
		self.std_Nano33_wy = np.round(np.std(self.data_Nano33_wy), 3)
		self.offset_Nano33_wz = np.round(np.average(self.data_Nano33_wz),3)
		self.std_Nano33_wz = np.round(np.std(self.data_Nano33_wz), 3)
		# self.top.TabPlot.tab2_Nano33_gyro.lb1.setText(str(self.offset_Nano33_wz))
		# self.top.TabPlot.tab2_Nano33_gyro.lb2.setText(str(self.std_Nano33_wz))
		
		self.offset_Nano33_ax = np.round(np.average(self.data_Nano33_ax),3)
		self.std_Nano33_ax = np.round(np.std(self.data_Nano33_ax), 3)
		self.top.TabPlot.tab2_Nano33_xlm.lb1_1.setText(str(self.offset_Nano33_ax))
		self.top.TabPlot.tab2_Nano33_xlm.lb1_2.setText(str(self.std_Nano33_ax))
		
		self.offset_Nano33_ay = np.round(np.average(self.data_Nano33_ay),3)
		self.std_Nano33_ay = np.round(np.std(self.data_Nano33_ay), 3)
		self.top.TabPlot.tab2_Nano33_xlm.lb2_1.setText(str(self.offset_Nano33_ay))
		self.top.TabPlot.tab2_Nano33_xlm.lb2_2.setText(str(self.std_Nano33_ay))
		
		self.offset_Nano33_az = np.round(np.average(self.data_Nano33_az),3)
		self.std_Nano33_az = np.round(np.std(self.data_Nano33_az), 3)
		self.top.TabPlot.tab2_Nano33_xlm.lb3_1.setText(str(self.offset_Nano33_az))
		self.top.TabPlot.tab2_Nano33_xlm.lb3_2.setText(str(self.std_Nano33_az))
		
		self.offset_Adxl355_ax = np.round(np.average(self.data_Adxl355_ax),3)
		self.std_Adxl355_ax = np.round(np.std(self.data_Adxl355_ax), 3)
		self.top.TabPlot.tab2_ADXL355_xlm.lb1_1.setText(str(self.offset_Adxl355_ax))
		self.top.TabPlot.tab2_ADXL355_xlm.lb1_2.setText(str(self.std_Adxl355_ax))
		
		self.offset_Adxl355_ay = np.round(np.average(self.data_Adxl355_ay),3)
		self.std_Adxl355_ay = np.round(np.std(self.data_Adxl355_ay), 3)
		self.top.TabPlot.tab2_ADXL355_xlm.lb2_1.setText(str(self.offset_Adxl355_ay))
		self.top.TabPlot.tab2_ADXL355_xlm.lb2_2.setText(str(self.std_Adxl355_ay))
		
		self.offset_Adxl355_az = np.round(np.average(self.data_Adxl355_az),3)
		self.std_Adxl355_az = np.round(np.std(self.data_Adxl355_az), 3)
		self.top.TabPlot.tab2_ADXL355_xlm.lb3_1.setText(str(self.offset_Adxl355_az))
		self.top.TabPlot.tab2_ADXL355_xlm.lb3_2.setText(str(self.std_Adxl355_az))
		
		# if(self.act.runFlag_cali == False):
			# print('self.offset_SRS200_wz: ', self.offset_SRS200_wz)
			# print('self.offset_PP_wz: ', self.offset_PP_wz)
			# print('self.offset_Nano33_wx: ', self.offset_Nano33_wx)
			# print('self.offset_Nano33_wy: ', self.offset_Nano33_wy)
			# print('self.offset_Nano33_wz: ', self.offset_Nano33_wz)
			# print('self.offset_Adxl355_ax: ', self.offset_Adxl355_ax)
			# print('self.offset_Adxl355_ay: ', self.offset_Adxl355_ay)
			# print('self.offset_Adxl355_az: ', self.offset_Adxl355_az)
			# print('self.offset_IMU_speed: ', self.offset_IMU_speed)

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
	

