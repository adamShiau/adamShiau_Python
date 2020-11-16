import os 
import sys 
sys.path.append("../") 
import time 
import datetime
# import logging
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
import numpy as np
# import py3lib
# import py3lib.FileToArray as file
# import py3lib.QuLogger as Qlogger 
# import py3lib.FileToArray as fil2a 
import NanoIMU_Widget as UI 
import NanoIMU_Action as ACT
TITLE_TEXT = "COM_Read"
VERSION_TEXT = 'Hello Adam，2020/11/13'
READOUT_FILENAME = "Signal_Read_Out.txt"
MAX_SAVE_INDEX = 3000
DEBUG = 0
w_factor = 0.01
xlm_factor = 0.000122 #4g / 32768
gyro_factor = 0.00763 #250 / 32768 


class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.resize(1100,800)
		self.move(0,0)
		self.loggername = "Total"
		self.top = UI.mainWidget()
		self.act = ACT.COMRead_Action(self.loggername)
		self.thread1 = QThread() #開一個thread
		self.data = np.empty(0)
		self.data2 = np.empty(0)
		self.data3 = np.empty(0)
		self.data4 = np.empty(0)
		self.data5 = np.empty(0)
		self.data6 = np.empty(0)
		self.dt = np.empty(0)
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.disableBtn()
	
	def disableBtn(self):
		self.top.usb.btn.setEnabled(False)
		self.top.read_btn.read.setEnabled(False)
		self.top.stop_btn.stop.setEnabled(False)
		
	def enableBtn(self):
		self.top.usb.btn.setEnabled(True)
		self.top.read_btn.read.setEnabled(True)
		self.top.stop_btn.stop.setEnabled(True)
	
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
		self.top.usb.btn.clicked.connect(self.usbConnect)
		self.top.read_btn.read.clicked.connect(self.myThreadStart) # set runFlag=1
		self.top.stop_btn.stop.clicked.connect(self.buttonStop) # set runFlag=0
		self.top.updataCom.updata.clicked.connect(self.updata_comport)
		self.top.updataCom.cs.currentIndexChanged.connect(self.uadate_comport_label)
		self.top.updataCom.updata.clicked.connect(self.enableBtn)
		''' thread connect '''
		# self.thread1.started.connect(self.act.updateTwoData) #thread1啟動時會去trigger act.updateTwoData
		# self.thread1.started.connect(self.act.updateThreeData) #thread1啟動時會去trigger act.updateThreeData 
		# self.thread1.started.connect(self.act.updateFOG) #thread1啟動時會去trigger act.updateFOG 
		self.thread1.started.connect(self.act.updateXLMDnGYRO)
		''' emit connect '''
		self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		# self.act.fog_update.connect(self.plotFog) #fog_update emit 接收最新data and dt array
		# self.act.fog_update2.connect(self.plotFog2) 
		self.act.fog_update7.connect(self.plotXLMDnGYRO)
		
			
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
			
	def updata_comport(self):
		self.act.COM.selectCom()
		self.top.updataCom.cs.clear()
		''' combo box '''
		if(self.act.COM.portNum > 0):
			for i in range(self.act.COM.portNum):
				self.top.updataCom.cs.addItem(self.act.COM.comPort[i][0])
			idx = self.top.updataCom.cs.currentIndex()
			self.top.updataCom.lb.setText(self.act.COM.comPort[idx][1])
	
	def uadate_comport_label(self):
		idx = self.top.updataCom.cs.currentIndex()
		self.top.updataCom.lb.setText(self.act.COM.comPort[idx][1])
		self.cp = self.act.COM.comPort[idx][0]
	
	def usbConnect(self):
		# usbConnStatus = self.act.usbConnect() 
		print(self.cp);
		usbConnStatus = self.act.usbConnect_comboBox(self.cp)
		print("status:" + str(usbConnStatus))
		if usbConnStatus:
			self.top.usb.SetConnectText(Qt.black, self.act.COM.port.port + " Connection build", True)
			print("Connect build")
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)
			print("Connect failed")
			
	def buttonStop(self):#set runFlag=0
		# self.act.setStop()
		self.act.runFlag = False
		
	def open_file(self, filename):
		self.f=open(filename, 'w')
		start_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.f.writelines(start_time_header + '\n')
		
	def myThreadStart(self):
		self.save_status = self.openFileBox()
		# file_name = self.top.save_edit.edit.text() 
		# self.f=open(file_name,'a')
		# self.f=open('er','a')
		self.act.runFlag = True
		self.thread1.start()
		# self.top.com_plot.ax1.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		# self.top.com_plot.ax2.legend(bbox_to_anchor=(1.0, 1.0), loc='upper left', prop={'size': 10})
		
	def myThreadStop(self):
		self.thread1.quit() 
		self.thread1.wait()
		if(self.save_status):
			stop_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			self.f.writelines(stop_time_header + '\n')
			self.f.close()
		self.data  = np.empty(0)
		self.data2 = np.empty(0)
		self.data3 = np.empty(0)
		self.data4 = np.empty(0)
		self.data5 = np.empty(0)
		self.data6 = np.empty(0)
		self.dt = np.empty(0)
		
	def plotFog(self, data, dt):
		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.dt = self.dt[self.act.data_frame_update_point:]

		self.data = np.append(self.data, data*w_factor)
		self.dt = np.append(self.dt, dt)
		if(DEBUG) :
			print('len(data)', len(self.data))
			print('len(dt)', len(self.dt))
			# print(self.data)
		self.top.com_plot.ax.clear()
		self.top.com_plot.ax.set_ylabel("")
		self.top.com_plot.ax.plot(self.dt, self.data, color = 'blue', linestyle = '-', marker = '')
		self.top.com_plot.figure.canvas.draw()
		self.top.com_plot.figure.canvas.flush_events()
		
	def plotFog2(self, data1, data2, dt):

		if (len(self.data) >= 3000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.dt = self.dt[self.act.data_frame_update_point:]

		self.data = np.append(self.data, data1)
		self.data2 = np.append(self.data2, data2)
		self.dt = np.append(self.dt, dt)
		if(DEBUG) :
			print('len(data1)', len(self.data))
			print('len(data2)', len(self.data2))
			print('len(dt)', len(self.dt))
		# self.top.com_plot.ax1.set_ylabel("y1")
		# self.top.com_plot.ax1.plot(self.dt, self.data, color = 'blue', linestyle = '-', marker = '*')
		# self.top.com_plot.ax2.set_ylabel("y2")
		# self.top.com_plot.ax2.plot(self.dt, self.data2, color = 'red', linestyle = '-', marker = '*')
		
		# self.top.com_plot.figure.canvas.draw()
		# self.top.com_plot.ax1.clear()
		# self.top.com_plot.ax2.clear()
		# self.top.com_plot.figure.canvas.flush_events()
		
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
			np.savetxt(self.f, (np.vstack([dt,data_ax_f, data_ay_f, data_az_f, data_wx_f, data_wy_f, data_wz_f])).T, fmt='%.2f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f')
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

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
