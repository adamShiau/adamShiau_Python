import os 
import sys 
sys.path.append("../") 
import time 
# import logging
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
import numpy as np
# import py3lib.QuLogger as Qlogger 
# import py3lib.FileToArray as fil2a 
import COMRead_Widget as UI 
import COMRead_Action as ACT
TITLE_TEXT = "COM_Read"
MAX_SAVE_INDEX = 3000
DEBUG = 0
w_factor = 0.01
xlm_factor = 0.00012207031 #4g / 32768code


class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.move(50,50)
		self.loggername = "Total"
		self.top = UI.mainWidget()
		self.act = ACT.COMRead_Action(self.loggername)
		self.thread1 = QThread() #開一個thread
		self.data = np.empty(0)
		self.data2 = np.empty(0)
		self.data3 = np.empty(0)
		self.data4 = np.empty(0)
		self.dt = np.empty(0)
		self.mainUI()
		self.linkFunction()

	def mainUI(self):
		mainLayout = QGridLayout()
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.top,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)

	def linkFunction(self):
		''' btn connect '''
		self.top.usb.btn.clicked.connect(self.usbConnect)
		self.top.read_btn.read.clicked.connect(self.myThreadStart) # set runFlag=1
		self.top.stop_btn.stop.clicked.connect(self.buttonStop) # set runFlag=0
		''' thread connect '''
		# self.thread1.started.connect(self.act.updateTwoData) #thread1啟動時會去trigger act.updateTwoData
		# self.thread1.started.connect(self.act.updateThreeData) #thread1啟動時會去trigger act.updateThreeData 
		# self.thread1.started.connect(self.act.updateFOG) #thread1啟動時會去trigger act.updateFOG 
		self.thread1.started.connect(self.act.updateFOGnXLMD)
		''' emit connect '''
		self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		self.act.fog_update.connect(self.plotFog) #fog_update emit 接收最新data and dt array
		self.act.fog_update2.connect(self.plotFog2) 
		self.act.fog_update4.connect(self.plotFog4)
			
		
	def usbConnect(self):
		usbConnStatus = self.act.usbConnect()
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
		
	def myThreadStart(self):
		self.act.runFlag = True
		self.thread1.start()
		
	def myThreadStop(self):
		self.thread1.quit()
		self.thread1.wait()
		self.data  = np.empty(0)
		self.data2 = np.empty(0)
		self.data3 = np.empty(0)
		self.data4 = np.empty(0)
		self.dt = np.empty(0)
		# self.top.com_plot.ax1.clear()
		# self.top.com_plot.ax2.clear()
		
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
		
	def plotFog4(self, data_fog, data_ax, data_ay, data_az, dt):

		if (len(self.data) >= 1000):
			self.data = self.data[self.act.data_frame_update_point:]
			self.data2 = self.data2[self.act.data_frame_update_point:]
			self.data3 = self.data3[self.act.data_frame_update_point:]
			self.data4 = self.data4[self.act.data_frame_update_point:]
			self.dt = self.dt[self.act.data_frame_update_point:]

		self.data = np.append(self.data, data_fog*w_factor)
		self.data2 = np.append(self.data2, data_ax*xlm_factor)
		self.data3 = np.append(self.data3, data_ay*xlm_factor)
		self.data4 = np.append(self.data4, data_az*xlm_factor)
		self.dt = np.append(self.dt, dt)
		if(DEBUG) :
			print('len(data_fog)', len(self.data))
			print('len(data_ax)', len(self.data2))
			print('len(data_ay)', len(self.data3))
			print('len(data_az)', len(self.data4))
			print('len(dt)', len(self.dt))
		self.top.com_plot.ax1.set_ylabel("fog")
		self.top.com_plot.ax1.plot(self.dt, self.data, color = 'blue', linestyle = '-', marker = '')
		self.top.com_plot.ax2.set_ylabel("ax")
		# self.top.com_plot.ax2.plot(self.dt, self.data2, self.dt, self.data3,  self.dt, self.data4, color = 'red', linestyle = '-', marker = '')
		self.top.com_plot.ax2.plot(self.dt, self.data2, color = 'red', linestyle = '-', marker = '')
		self.top.com_plot.ax3.set_ylabel("ay")
		self.top.com_plot.ax3.plot(self.dt, self.data3, color = 'red', linestyle = '-', marker = '')
		self.top.com_plot.ax4.set_ylabel("az")
		self.top.com_plot.ax4.plot(self.dt, self.data4, color = 'red', linestyle = '-', marker = '')
		
		self.top.com_plot.figure.canvas.draw()
		self.top.com_plot.ax1.clear()
		self.top.com_plot.ax2.clear()
		self.top.com_plot.ax3.clear()
		self.top.com_plot.ax4.clear()
		self.top.com_plot.figure.canvas.flush_events()

        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
