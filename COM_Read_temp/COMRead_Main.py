import os 
import sys 
import time as timer
sys.path.append("../") 
import datetime
from scipy import signal
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
import numpy as np
import COMRead_Widget as UI 
import COMRead_Action as ACT

TEST_MODE = 0
DEBUG = 0
gyro200_factor = 0.0121
SAMPLING_TIME = 0.01
NUM = 400
class mainWindow(QMainWindow):
	''' global vars'''
	data1 = np.empty(0)
	time = np.empty(0)
	save_status = False
	''' pyqtSignal'''
	usbconnect_status = pyqtSignal(object) #to trigger the btn to enable state
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle('com port read')
		self.resize(1100,800)
		self.move(0,0)
		self.top = UI.COMRead_Widget()
		self.act = ACT.COMRead_Action()
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
	
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
		''' thread btn connect '''
		self.top.read_btn.bt.clicked.connect(self.myThreadStart) # set runFlag=1
		self.top.stop_btn.bt.clicked.connect(self.buttonStop) # set runFlag=0
		''' btn connect '''
		self.top.usb.bt_update.clicked.connect(self.update_comport)
		self.top.usb.cs.currentIndexChanged.connect(self.uadate_comport_label)
		self.top.usb.bt_connect.clicked.connect(self.usbConnect)

		''' emit connect '''
		#action emit connect
		self.act.update2.connect(self.plotCOM)
		self.act.finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
		
	def myThreadStart(self):
		self.save_status = self.openFileBox()
		self.act.runFlag = True
		self.act.start()
		print('Main, self.act.runFlag:', self.act.runFlag)
		print('act.test_mode_flag: ', self.act.test_mode_flag)
		if(self.act.test_mode_flag == 0):
			self.act.COM.port.flushInput()
		
	def buttonStop(self):#set runFlag=0
		self.act.runFlag = False
		print('self.act.runFlag: ', self.act.runFlag)
		
	
		
	def myThreadStop(self):
		# print('finish')
		self.act.quit() 
		self.act.wait()
		self.initializeDate()
		# if(self.save_status):
			# stop_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			# self.f.writelines('#' + stop_time_header + '\n')
			# self.f.close()
	
	def initializeDate(self):
		self.data1 = np.empty(0)
		self.time = np.empty(0)
	
	""" comport functin """
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
			usbConnStatus = self.act.COM.connect_comboBox(baudrate = 230400, timeout = 1, port_name=self.cp)
		print("status:" + str(usbConnStatus))
		if usbConnStatus:
			self.top.usb.SetConnectText(Qt.blue, self.cp + " Connect")
			self.usbconnect_status.emit(1)
			print("Connect build")
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)
			print("Connect failed")
			
	""" end of comport functin """
	
	def plotCOM(self, time, data1):
		# time = time*1e-6
		t1 = float(datetime.datetime.now().strftime('%S.%f'))
		print('Main: t1= (s)', t1)
		if (len(self.time) >= 200000):
			self.data1 = self.data1[NUM:]
			self.time = self.time[NUM:]
		self.top.buffer_lb.lb.setText(str(self.act.bufferSize))
		self.data1 = np.append(self.data1, data1)
		self.time = np.append(self.time, time)
		print('len(self.time): ', len(self.time), end='\t')
		# print(time)
		print(self.time[0], end='\t')
		print(self.time[-1])
		# self.top.plot1.setData(self.time, self.data1)
		self.top.plot1.setData(self.data1)
		# self.data1 = np.empty(0)
		# self.time = np.empty(0)
		t2 = float(datetime.datetime.now().strftime('%S.%f'))
		print('Main dt= (ms)', (t2 - t1)*1000)
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
		self.f=open(filename, 'w')
		start_time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.f.writelines('#' + start_time_header + '\n')
		
	def versionBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)
        
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
