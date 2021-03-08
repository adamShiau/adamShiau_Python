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
import ADXL355_IMU_Widget4 as UI 
import ADXL355_IMU_Action4_BT as ACT
# import ADXL355_Globals as globals
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
xlm_factor = 0.000122 #4g / 32768
ADxlm_factor = 0.0000156 #8g
# gyro_factor = 0.00763 #250 / 32768 
gyro_factor = 0.0090 #250 / 32768 
gyroPP_factor = 1
gyro200_factor = 0.0121

# wx_offset = 107.065
# wy_offset = -513.717


class mainWindow(QMainWindow):
	''' define and initiate global variable '''
	MV_status = 0
	offset_SRS200_wz = 0
	offset_PP_wz = 0
	offset_Nano33_wz = 0
	offset_Nano33_ax = 0
	offset_Nano33_ay = 0
	offset_Nano33_az = 0
	offset_Adxl355_ax = 0
	offset_Adxl355_ay = 0
	offset_Adxl355_az = 0
	
	''' pyqtSignal'''
	usbconnect_status = pyqtSignal(object) #to trigger the btn to enable state
	''' axis max for track'''
	x_max = 1
	y_max = 1
	clear_track_flag = False
	''' data save'''
	save_status = False
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
		self.data_Adxl355_ax = np.empty(0)
		self.data_Adxl355_ay = np.empty(0)
		self.data_Adxl355_az = np.empty(0)
		self.data_Nano33_ax = np.empty(0)
		self.data_Nano33_ay = np.empty(0)
		self.data_Nano33_az = np.empty(0)
		self.thetaz_nano33 = 0
		self.thetaz_SRS200 = 0
		# self.thetax = 0
		# self.thetay = 0
		self.speed_Nano33 = 0
		self.speedx_Nano33 = 0
		self.speedy_Nano33 = 0
		self.speed_Adxl355 = 0
		self.speedx_Adxl355 = 0
		self.speedy_Adxl355 = 0
		self.thetaz_nano33_arr = np.empty(0)
		self.thetaz_SRS200_arr = np.empty(0)
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
		#action emit connect
		self.act.fog_update8.connect(self.plotADXLIMUnGYRO)
		self.act.fog_update11.connect(self.calibADXLIMUnGYRO)
		self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		
		''' text connect '''
		# self.top.wzOffset_le.textChanged.connect(self.updata_para)

		''' check box '''
		self.top.TabPlot.tab1_gyro_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_gyro_cb.cb1))
		self.top.TabPlot.tab1_gyro_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_gyro_cb.cb2))
		self.top.TabPlot.tab1_adxlXLM_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_adxlXLM_cb.cb1))
		self.top.TabPlot.tab1_adxlXLM_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_adxlXLM_cb.cb2))
		self.top.TabPlot.tab1_nano33XLM_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_nano33XLM_cb.cb1))
		self.top.TabPlot.tab1_nano33XLM_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_nano33XLM_cb.cb2))
		self.top.TabPlot.tab1_speed_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_speed_cb.cb1))
		self.top.TabPlot.tab1_speed_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab1_speed_cb.cb2))
		self.top.TabPlot.tab3_track_cb.cb1.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab3_track_cb.cb1))
		self.top.TabPlot.tab3_track_cb.cb2.toggled.connect(lambda:self.cb_toogled(self.top.TabPlot.tab3_track_cb.cb2))

		''' radio btn'''
		self.top.mv_rb.toggled.connect(lambda:self.rb_toggled(self.top.mv_rb))
	
	def setCheckBox_init(self):
		self.top.TabPlot.tab1_gyro_cb.cb2.setChecked(True) #set gyro wz initial as PP
		self.top.TabPlot.tab1_adxlXLM_cb.cb1.setChecked(True) #set adxl355 XLM initial as ax
		# self.top.TabPlot.tab1_nano33XLM_cb.cb1.setChecked(True) #set nano33 XLM initial as ax
		self.top.TabPlot.tab1_speed_cb.cb1.setChecked(True) #set speed_Nano33 initial as adxl355
		self.top.TabPlot.tab3_track_cb.cb2.setChecked(True) #set track_SRS200 initially
		
	def setBtnStatus(self, flag):
		self.top.TabPlot.tab1_read_btn.bt.setEnabled(flag)
		self.top.TabPlot.tab1_stop_btn.bt.setEnabled(flag)
		self.top.TabPlot.tab2_cali_start_btn.bt.setEnabled(flag)
		self.top.TabPlot.tab2_cali_stop_btn.bt.setEnabled(flag)
		self.top.TabPlot.tab3_xmax.bt.setEnabled(flag)
		self.top.TabPlot.tab3_ymax.bt.setEnabled(flag)
		
	
	def rb_toggled(self, rb):
		self.MV_status = rb.isChecked()
		print('MV:', self.MV_status)
		
	def get_rbVal(self):
		self.MV_status = self.top.mv_rb.isChecked()
		print('MV:', self.MV_status)
		
	def cb_toogled(self, cb):
		if(cb.text()==self.top.TabPlot.tab1_gyro_cb.cb1.text()):
			self.Nano33_wz_chk = cb.isChecked()
			print('Nano33_wz_chk:', self.Nano33_wz_chk)
		elif(cb.text()==self.top.TabPlot.tab1_gyro_cb.cb2.text()):
			self.PP_wz_chk = cb.isChecked()
			print('PP_wz_chk:', self.PP_wz_chk)
		elif(cb.text()==self.top.TabPlot.tab1_adxlXLM_cb.cb1.text()):
			self.Adxl355_ax_chk = cb.isChecked()
			print('Adxl355_ax_chk:', self.Adxl355_ax_chk)
		elif(cb.text()==self.top.TabPlot.tab1_adxlXLM_cb.cb2.text()):
			self.Adxl355_ay_chk = cb.isChecked()
			print('Adxl355_ay_chk:', self.Adxl355_ay_chk)
		elif(cb.text()==self.top.TabPlot.tab1_nano33XLM_cb.cb1.text()):
			self.Nano33_ax_chk = cb.isChecked()
			print('Nano33_ax_chk:', self.Nano33_ax_chk)
		elif(cb.text()==self.top.TabPlot.tab1_nano33XLM_cb.cb2.text()):
			self.Nano33_ay_chk = cb.isChecked()
			print('Nano33_ay_chk:', self.Nano33_ay_chk)
		elif(cb.text()==self.top.TabPlot.tab1_speed_cb.cb1.text()):
			self.Adxl355_v_chk = cb.isChecked()
			print('Adxl355_v_chk:', self.Adxl355_v_chk)
		elif(cb.text()==self.top.TabPlot.tab1_speed_cb.cb2.text()):
			self.Nano33_v_chk = cb.isChecked()
			print('Nano33_v_chk:', self.Nano33_v_chk)
		elif(cb.text()==self.top.TabPlot.tab3_track_cb.cb1.text()):
			self.Nano33_track_chk = cb.isChecked()
			print('Nano33_track_chk:', self.Nano33_track_chk)
		elif(cb.text()==self.top.TabPlot.tab3_track_cb.cb2.text()):
			self.SRS200_track_chk = cb.isChecked()
			print('SRS200_track_chk:', self.SRS200_track_chk)
			
	def get_cbVal(self):
		self.Nano33_wz_chk = self.top.TabPlot.tab1_gyro_cb.cb1.isChecked()
		print('Nano33_wz_chk:', self.Nano33_wz_chk)
		self.PP_wz_chk = self.top.TabPlot.tab1_gyro_cb.cb2.isChecked()
		print('PP_wz_chk:', self.PP_wz_chk)
		self.Adxl355_ax_chk = self.top.TabPlot.tab1_adxlXLM_cb.cb1.isChecked()
		print('Adxl355_ax_chk:', self.Adxl355_ax_chk)
		self.Adxl355_ay_chk = self.top.TabPlot.tab1_adxlXLM_cb.cb2.isChecked()
		print('Adxl355_ay_chk:', self.Adxl355_ay_chk)
		self.Nano33_ax_chk = self.top.TabPlot.tab1_nano33XLM_cb.cb1.isChecked()
		print('Nano33_ax_chk:', self.Nano33_ax_chk)
		self.Nano33_ay_chk = self.top.TabPlot.tab1_nano33XLM_cb.cb2.isChecked()
		print('Nano33_ay_chk:', self.Nano33_ay_chk)
		self.Adxl355_v_chk = self.top.TabPlot.tab1_speed_cb.cb1.isChecked()
		print('Adxl355_v_chk:', self.Adxl355_v_chk)
		self.Nano33_v_chk = self.top.TabPlot.tab1_speed_cb.cb2.isChecked()
		print('Nano33_v_chk:', self.Nano33_v_chk)
		self.Nano33_track_chk = self.top.TabPlot.tab3_track_cb.cb1.isChecked()
		print('Nano33_track_chk:', self.Nano33_track_chk)
		self.SRS200_track_chk = self.top.TabPlot.tab3_track_cb.cb2.isChecked()
		print('SRS200_track_chk:', self.SRS200_track_chk)
		
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
		self.thetaz_nano33_arr = np.empty(0)
		self.thetaz_SRS200_arr = np.empty(0)
		# self.speedx_Nano33_arr = np.empty(0)
		# self.speedy_Nano33_arr = np.empty(0)
		# self.speed_Nano33_arr = np.empty(0)
		self.x_arr = np.zeros(0)
		self.y_arr = np.zeros(0)
		self.x_sum = 0
		self.y_sum = 0
		self.dx_arr = np.zeros(0)
		self.dy_arr = np.zeros(0)
		# self.x200_arr = np.zeros(0)
		# self.y200_arr = np.zeros(0)
		self.x200_sum = 0
		self.y200_sum = 0
		self.dx200_arr = np.zeros(0)
		self.dy200_arr = np.zeros(0)
		# self.top.com_plot.ax2.clear()
		
	def open_file(self, filename):
		self.f=open(filename, 'w')
		start_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.f.writelines('#' + start_time_header + '\n')
	
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
		offset_Nano33_wz = 0
		offset_Nano33_ax = 0
		offset_Nano33_ay = 0
		offset_Nano33_az = 0
		offset_Adxl355_ax = 0
		offset_Adxl355_ay = 0
		offset_Adxl355_az = 0
		
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
		# '''
		self.data_SRS200_wz = np.empty(0)
		self.data_Nano33_wx = np.empty(0)
		self.data_Nano33_wy = np.empty(0)
		self.data_Nano33_wz = np.empty(0)
		self.data_PP_wz = np.empty(0)
		self.data_Adxl355_ax = np.empty(0)
		self.data_Adxl355_ay = np.empty(0)
		self.data_Adxl355_az = np.empty(0)
		self.data_Nano33_ax = np.empty(0)
		self.data_Nano33_ay = np.empty(0)
		self.data_Nano33_az = np.empty(0)
		self.dt = np.empty(0)
		
		self.speed_Nano33_arr = np.empty(0)
		self.speed_Adxl355_arr = np.empty(0)
		self.thetaz_nano33 = 0
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
		
	def plotADXLIMUnGYRO(self, dt, data_SRS200_wz, data_Nano33_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay, data_Nano33_ax, data_Nano33_ay):
		# print('plotADXLIMUnGYRO')
		if(self.act.runFlag):
		
			if(DEBUG_COM):
				print('data_SRS200_wz: ', end=', ');
				print(data_SRS200_wz)
			
			# self.top.TabPlot.tab1_plot1.ax.clear()
			# self.top.TabPlot.tab1_plot2.ax.clear()
			# self.top.TabPlot.tab1_plot3.ax.clear()
			# self.top.TabPlot.tab1_plot4.ax.clear()
			# self.top.TabPlot.tab3_plot1.ax.clear()
			
			
			# if(self.Nano33_wz_chk or self.PP_wz_chk):
				# self.top.TabPlot.tab1_plot2.ax.clear()
			# if(self.Adxl355_ax_chk or self.Adxl355_ay_chk or self.Nano33_ax_chk or self.Nano33_ay_chk):
				# self.top.TabPlot.tab1_plot3.ax.clear()
			# if(self.Nano33_v_chk or self.Adxl355_v_chk):
				# self.top.TabPlot.tab1_plot4.ax.clear()
			# if((self.Nano33_track_chk or self.SRS200_track_chk) and self.clear_track_flag):
				# self.clear_track_flag = False
				# self.top.TabPlot.tab3_plot1.ax.clear()
				
			# if((self.Nano33_track_chk or self.SRS200_track_chk)):
				# self.clear_track_flag = False
				# self.top.TabPlot.tab3_plot1.ax.clear()
			
			pass
		dt = dt*1e-6
		if (len(self.dt) >= 3000):
			self.dt = self.dt[self.act.data_frame_update_point:]
			self.data_SRS200_wz = self.data_SRS200_wz[self.act.data_frame_update_point:]
			self.data_Nano33_wz = self.data_Nano33_wz[self.act.data_frame_update_point:]
			self.data_PP_wz = self.data_PP_wz[self.act.data_frame_update_point:]
			self.data_Adxl355_ax = self.data_Adxl355_ax[self.act.data_frame_update_point:]
			self.data_Adxl355_ay = self.data_Adxl355_ay[self.act.data_frame_update_point:]
			self.data_Nano33_ax = self.data_Nano33_ax[self.act.data_frame_update_point:]
			self.data_Nano33_ay = self.data_Nano33_ay[self.act.data_frame_update_point:]
			
		data_SRS200_wz_f = (data_SRS200_wz - self.offset_SRS200_wz)*gyro200_factor/3600 #convert to DPS
		data_Nano33_wz_f = (data_Nano33_wz - self.offset_Nano33_wz)*gyro_factor
		data_PP_wz_f = (data_PP_wz - self.offset_PP_wz)*gyroPP_factor
		data_Adxl355_ax_f = (data_Adxl355_ax - self.offset_Adxl355_ax)*ADxlm_factor
		data_Adxl355_ay_f = (data_Adxl355_ay - self.offset_Adxl355_ay)*ADxlm_factor
		data_Nano33_ax_f = (data_Nano33_ax - self.offset_Nano33_ax)*xlm_factor
		data_Nano33_ay_f = (data_Nano33_ay - self.offset_Nano33_ay)*xlm_factor
		

		'''由角速率積分計算角度，積分時間為data_frame_update_point*(1/ODR), ODR=100Hz'''
		self.thetaz_nano33 = self.thetaz_nano33 - np.sum(data_Nano33_wz_f)*SAMPLING_TIME #負號是方向判斷的問題, 0.01是1/ODR
		self.thetaz_nano33_arr = np.append(self.thetaz_nano33_arr, self.thetaz_nano33)
		self.thetaz_SRS200 = self.thetaz_SRS200 - np.sum(data_SRS200_wz_f)*SAMPLING_TIME #負號是方向判斷的問題
		self.thetaz_SRS200_arr = np.append(self.thetaz_SRS200_arr, self.thetaz_SRS200)
		# print('self.thetaz_nano33: ', self.thetaz_nano33)
		print('self.thetaz_SRS200: ', self.thetaz_SRS200)
		self.top.SRS200_gauge.lb.setText(str(round(self.thetaz_SRS200, 2)))
		
		'''由加速度積分計算速度'''
		#Nano33
		self.speedx_Nano33 = self.speedx_Nano33 + np.sum(data_Nano33_ax_f)*9.8*SAMPLING_TIME
		# self.speedx_Nano33_arr = np.append(self.speedx_Nano33_arr, self.speedx_Nano33)
		self.speedy_Nano33 = self.speedy_Nano33 + np.sum(data_Nano33_ay_f)*9.8*SAMPLING_TIME
		# self.speedy_Nano33_arr = np.append(self.speedy_Nano33_arr, self.speedy_Nano33)
		self.speed_Nano33 = np.sqrt(np.square(self.speedx_Nano33)+np.square(self.speedy_Nano33))
		self.speed_Nano33_arr = np.append(self.speed_Nano33_arr, self.speed_Nano33)
		#ADXL355
		self.speedx_Adxl355 = self.speedx_Adxl355 + np.sum(data_Adxl355_ax_f)*9.8*SAMPLING_TIME
		self.speedy_Adxl355 = self.speedy_Adxl355 + np.sum(data_Adxl355_ay_f)*9.8*SAMPLING_TIME
		self.speed_Adxl355 = np.sqrt(np.square(self.speedx_Adxl355)+np.square(self.speedy_Adxl355))
		self.speed_Adxl355_arr = np.append(self.speed_Adxl355_arr, self.speed_Adxl355)
		self.top.speed_gauge.lb.setText(str(round(self.speed_Adxl355, 2)))
		#guage plot
		self.top.SRS200_gauge.gauge.item.setRotation(self.thetaz_SRS200)
		self.top.speed_gauge.gauge.item.setRotation(np.average(data_SRS200_wz_f))
		
		''' for track plot'''
		thetaz_nano33 = 90 - self.thetaz_nano33
		thetaz_SRS200 = 90 - self.thetaz_SRS200
		'''
		dx = dr*cos(theta), dr = vdt
		v = 1 m/s
		dt = data_frame_update_point*self.act.TIME_PERIOD 
		'''
		dx = np.cos(thetaz_nano33*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
		dy = np.sin(thetaz_nano33*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.x_sum = self.x_sum + dx
		self.y_sum = self.y_sum + dy
		
		dx200 = np.cos(thetaz_SRS200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD 
		dy200 = np.sin(thetaz_SRS200*np.pi/180)*self.act.data_frame_update_point*self.act.TIME_PERIOD
		self.x200_sum = self.x200_sum + dx200
		self.y200_sum = self.y200_sum + dy200
		
		#print buffer to label
		self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
		
		self.dx_arr = np.append(self.dx_arr, dx)
		self.dy_arr = np.append(self.dy_arr, dy)
		self.x_arr = np.append(self.x_arr, self.x_sum)
		self.y_arr = np.append(self.y_arr, self.y_sum)
		
		self.dx200_arr = np.append(self.dx200_arr, dx200)
		self.dy200_arr = np.append(self.dy200_arr, dy200)
		self.x200_arr = np.append(self.x200_arr, self.x200_sum)
		self.y200_arr = np.append(self.y200_arr, self.y200_sum)
		
		if (len(self.thetaz_nano33_arr) >= 1000):
			self.thetaz_nano33_arr = self.thetaz_nano33_arr[1:]
			self.thetaz_SRS200_arr = self.thetaz_SRS200_arr[1:]
			# self.thetax_arr = self.thetax_arr[1:]
			# self.thetay_arr = self.thetay_arr[1:]
			# self.speedx_Nano33_arr = self.speedx_Nano33_arr[1:]
			# self.speedy_Nano33_arr = self.speedy_Nano33_arr[1:]
			self.speed_Nano33_arr = self.speed_Nano33_arr[1:]
			self.speed_Adxl355_arr = self.speed_Adxl355_arr[1:]
			self.dx_arr = self.dx_arr[1:]
			self.dy_arr = self.dy_arr[1:]
			self.dx200_arr = self.dx200_arr[1:]
			self.dy200_arr = self.dy200_arr[1:]
			self.x_arr = self.x_arr[1:]
			self.y_arr = self.y_arr[1:]
			self.x200_arr = self.x200_arr[1:]
			self.y200_arr = self.y200_arr[1:]
		
		self.data_SRS200_wz  = np.append(self.data_SRS200_wz,  data_SRS200_wz_f)
		self.data_Nano33_wz = np.append(self.data_Nano33_wz, data_Nano33_wz_f)
		self.data_PP_wz = np.append(self.data_PP_wz, data_PP_wz_f)
		self.data_Adxl355_ax = np.append(self.data_Adxl355_ax, data_Adxl355_ax_f)
		self.data_Adxl355_ay = np.append(self.data_Adxl355_ay, data_Adxl355_ay_f)
		self.data_Nano33_ax = np.append(self.data_Nano33_ax, data_Nano33_ax_f)
		self.data_Nano33_ay = np.append(self.data_Nano33_ay, data_Nano33_ay_f)
		self.dt = np.append(self.dt, dt)
		
		if(self.save_status):
			# np.savetxt(self.f, (np.vstack([dt, data_SRS200_wz_f, data_Nano33_wz_f, data_PP_wz_f, data_Adxl355_ax_f, data_Adxl355_ay_f, 
			# data_Nano33_ax_f, data_Nano33_ay_f])).T, fmt='%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f')
			np.savetxt(self.f, (np.vstack([dt, data_SRS200_wz_f, data_PP_wz_f, data_Adxl355_ax_f, data_Adxl355_ay_f, 
			])).T, fmt='%5.5f,%5.5f,%5.5f,%5.5f,%5.5f')
		if(DEBUG) :
			print('len(dt): ', len(self.dt))
			print('len(self.data_SRS200_wz): ', len(self.data_SRS200_wz))
			print('len(self.x200_arr): ', len(self.x200_arr))
			print('self.x200_arr[-1]: ', self.x200_arr[-1])
			print('dt: ', self.dt[0])
			print('SRS200_wz: ', self.data_SRS200_wz[0])
			print('Nano33_wz: ', self.data_Nano33_wz[0])
			print('PP_wz: ', self.data_PP_wz[0])
			print('Adxl355_ax: ', self.data_Adxl355_ax[0])
			print('Adxl355_ay: ', self.data_Adxl355_ay[0])
			print('Nano33_ax: ', self.data_Nano33_ax[0])
			print('Nano33_ay: ', self.data_Nano33_ay[0])
			
			pass
					
		
		self.top.TabPlot.tab1_plot1.setData(self.dt, self.data_SRS200_wz)
		
		
		# self.top.com_plot.ax1.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.legend(bbox_to_anchor=(0.9, 1.0), loc='upper left', prop={'size': 10})
		if(self.Nano33_wz_chk ):
			self.top.TabPlot.tab1_plot2_1.setData(self.dt, self.data_Nano33_wz)
		else:
			self.top.TabPlot.tab1_plot2_1.setData()
			
		if(self.PP_wz_chk):
			self.top.TabPlot.tab1_plot2_2.setData(self.dt, self.data_PP_wz)
		else:
			self.top.TabPlot.tab1_plot2_2.setData()
		# if(self.Nano33_wz_chk or self.PP_wz_chk):
			# self.top.TabPlot.tab1_plot2.figure.canvas.draw()		
			# self.top.TabPlot.tab1_plot2.figure.canvas.flush_events()
		
		if(self.Adxl355_ax_chk):
			self.top.TabPlot.tab1_plot3_1.setData(self.dt, self.data_Adxl355_ax)
		else:
			self.top.TabPlot.tab1_plot3_1.setData()
		if(self.Adxl355_ay_chk):
			self.top.TabPlot.tab1_plot3_2.setData(self.dt, self.data_Adxl355_ay)
		else:
			self.top.TabPlot.tab1_plot3_2.setData()
		if(self.Nano33_ax_chk):
			self.top.TabPlot.tab1_plot3_3.setData(self.dt, self.data_Nano33_ax)
		else:
			self.top.TabPlot.tab1_plot3_3.setData()
		if(self.Nano33_ay_chk):
			self.top.TabPlot.tab1_plot3_4.setData(self.dt, self.data_Nano33_ay)
		else:
			self.top.TabPlot.tab1_plot3_4.setData()
		# if(self.Adxl355_ax_chk or self.Adxl355_ay_chk or self.Nano33_ax_chk or self.Nano33_ay_chk):
			# self.top.TabPlot.tab1_plot3.figure.canvas.draw()		
			# self.top.TabPlot.tab1_plot3.figure.canvas.flush_events()
		
		if(self.Adxl355_v_chk):
			self.top.TabPlot.tab1_plot4_1.setData(self.speed_Adxl355_arr)
		else:
			self.top.TabPlot.tab1_plot4_1.setData()
		if(self.Nano33_v_chk):
			self.top.TabPlot.tab1_plot4_2.setData(self.speed_Nano33_arr)
		else:
			self.top.TabPlot.tab1_plot4_2.setData()
		# if(self.Nano33_v_chk or self.Adxl355_v_chk):
			# self.top.TabPlot.tab1_plot4.figure.canvas.draw()		
			# self.top.TabPlot.tab1_plot4.figure.canvas.flush_events()
		
		if(self.Nano33_track_chk):
			self.top.TabPlot.tab3_plot1_1.setData(self.x_arr, self.y_arr)
		else:
			self.top.TabPlot.tab3_plot1_1.setData()
		if(self.SRS200_track_chk):
			self.top.TabPlot.tab3_plot1_2.setData(self.x200_arr, self.y200_arr) 
			x_max = self.x200_arr[-1] + 50
			x_min = self.x200_arr[-1] - 50
			y_max = self.y200_arr[-1] + 50
			y_min = self.y200_arr[-1] - 50
			self.top.TabPlot.tab3_plot1.setXRange(x_min, x_max, padding=0)
			self.top.TabPlot.tab3_plot1.setYRange(y_min, y_max, padding=0)
		else:
			self.top.TabPlot.tab3_plot1_2.setData()
		# if(self.Nano33_track_chk or self.SRS200_track_chk):
			# self.top.TabPlot.tab3_plot1.ax.set_xlim([-self.x_max, self.x_max])
			# self.top.TabPlot.tab3_plot1.ax.set_ylim([-self.y_max, self.y_max])
			# self.top.TabPlot.tab3_plot1.ax.set_xlim([x_min, x_max])
			# self.top.TabPlot.tab3_plot1.ax.set_ylim([y_min, y_max])
			# self.top.TabPlot.tab3_plot1.figure.canvas.draw()		
			# self.top.TabPlot.tab3_plot1.figure.canvas.flush_events()
			
		'''
		if(self.Nano33_wz_chk ):
			self.top.TabPlot.tab1_plot2.ax.plot(self.dt, self.data_Nano33_wz, color = 'b', linestyle = '-', marker = '', label="Nano33_wz")
		if(self.PP_wz_chk):
			self.top.TabPlot.tab1_plot2.ax.plot(self.dt, self.data_PP_wz, color = 'k', linestyle = '-', marker = '', label="PP_wz")			
		if(self.Nano33_wz_chk or self.PP_wz_chk):
			self.top.TabPlot.tab1_plot2.figure.canvas.draw()		
			self.top.TabPlot.tab1_plot2.figure.canvas.flush_events()
			
		if(self.Adxl355_ax_chk):
			self.top.TabPlot.tab1_plot3.ax.plot(self.dt, self.data_Adxl355_ax, color = 'b', linestyle = '-', marker = '', label="Adxl355_ax")
		if(self.Adxl355_ay_chk):
			self.top.TabPlot.tab1_plot3.ax.plot(self.dt, self.data_Adxl355_ay, color = 'k', linestyle = '-', marker = '', label="Adxl355_ay")
		if(self.Nano33_ax_chk):
			self.top.TabPlot.tab1_plot3.ax.plot(self.dt, self.data_Nano33_ax, color = 'r', linestyle = '-', marker = '', label="Nano33_ax")
		if(self.Nano33_ay_chk):
			self.top.TabPlot.tab1_plot3.ax.plot(self.dt, self.data_Nano33_ay, color = 'g', linestyle = '-', marker = '', label="Nano33_ay")
		if(self.Adxl355_ax_chk or self.Adxl355_ay_chk or self.Nano33_ax_chk or self.Nano33_ay_chk):
			self.top.TabPlot.tab1_plot3.figure.canvas.draw()		
			self.top.TabPlot.tab1_plot3.figure.canvas.flush_events()
		
		if(self.Adxl355_v_chk):
			self.top.TabPlot.tab1_plot4.ax.plot(self.speed_Adxl355_arr, color = 'b', linestyle = '-', marker = '', label="Adxl355_v")
		if(self.Nano33_v_chk):
			self.top.TabPlot.tab1_plot4.ax.plot(self.speed_Nano33_arr, color = 'k', linestyle = '-', marker = '', label="Nano33_v")
		if(self.Nano33_v_chk or self.Adxl355_v_chk):
			self.top.TabPlot.tab1_plot4.figure.canvas.draw()		
			self.top.TabPlot.tab1_plot4.figure.canvas.flush_events()
			
		if(self.Nano33_track_chk):
			self.top.TabPlot.tab3_plot1.ax.plot(self.x_arr, self.y_arr, color = 'b', linestyle = '-', marker = '', label="Nano33_track")
		if(self.SRS200_track_chk):
			self.top.TabPlot.tab3_plot1.ax.plot(self.x200_arr, self.y200_arr, color = 'k', linestyle = '-', marker = '', label="SRS200_track")
			# print('len(x200_arr): ', len(self.x200_arr))
			
		if(self.Nano33_track_chk or self.SRS200_track_chk):
			self.top.TabPlot.tab3_plot1.ax.set_xlim([-self.x_max, self.x_max])
			self.top.TabPlot.tab3_plot1.ax.set_ylim([-self.y_max, self.y_max])
			self.top.TabPlot.tab3_plot1.figure.canvas.draw()		
			self.top.TabPlot.tab3_plot1.figure.canvas.flush_events()
		# '''
		# time.sleep(0.01)
			
	def calibADXLIMUnGYRO(self, data_SRS200_wz, data_Nano33_wx, data_Nano33_wy, data_Nano33_wz, data_PP_wz, data_Adxl355_ax, data_Adxl355_ay,
									data_Adxl355_az, data_Nano33_ax, data_Nano33_ay, data_Nano33_az):
		# print('calibADXLIMUnGYRO')
		if (len(self.data_SRS200_wz) >= 300):
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
		
		self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
		
		self.offset_SRS200_wz = np.round(np.average(self.data_SRS200_wz),3)
		self.std_SRS200_wz = np.round(np.std(self.data_SRS200_wz), 3)
		self.top.TabPlot.tab2_SRS200.lb1.setText(str(self.offset_SRS200_wz))
		self.top.TabPlot.tab2_SRS200.lb2.setText(str(self.std_SRS200_wz))
		
		self.offset_PP_wz = np.round(np.average(self.data_PP_wz),3)
		self.std_PP_wz = np.round(np.std(self.data_PP_wz), 3)
		self.top.TabPlot.tab2_PP.lb1.setText(str(self.offset_PP_wz))
		self.top.TabPlot.tab2_PP.lb2.setText(str(self.std_PP_wz))
		
		
		self.offset_Nano33_wz = np.round(np.average(self.data_Nano33_wz),3)
		self.std_Nano33_wz = np.round(np.std(self.data_Nano33_wz), 3)
		self.top.TabPlot.tab2_Nano33_gyro.lb1.setText(str(self.offset_Nano33_wz))
		self.top.TabPlot.tab2_Nano33_gyro.lb2.setText(str(self.std_Nano33_wz))
		
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
		

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
	

