import os
import sys
sys.path.append("../")
import time
import datetime
import logging
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import py3lib.QuLogger as Qlogger
import py3lib.FileToArray as fil2a
import QSS005_TEST_Widget as QIT_UI
import QSS005_TEST_Action as ACT
import numpy as np 

HOST_NAME = "root"
HOST_PWD = "root"
HOST_PORT = 22

index_IP1 = 0
index_total = 1

SETTING_FILEPATH = "set"
SETTING_FILENAME = "set/TEST_setting.txt"

CONNECT_BIT_CMD = "cat /root/GRC_v3.bit > /dev/xdevcfg"
#CONNECT_BIT_CMD = "cat /root/GRC_MST.bit > /dev/xdevcfg"
WF_OUTPUT_CMD = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./CH1 "
LIB_PATH = "LD_LIBRARY_PATH=/opt/redpitaya/lib "

TITLE_TEXT = " Acdemic Sincica GRC Mass Spectrometer "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS005 QIT TEST V1.00 \n\n" + \
" Copyright @ 2020 TAIP \n" + \
" Maintain by Quantaser Photonics Co. Ltd "


class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)		
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger 
		self.act = ACT.qss005Action(self.loggername)
		self.top = QIT_UI.mainWidget()
		
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.LoadQITpreset()
		self.SSH1_status = False

	def mainUI(self):
		mainLayout = QGridLayout()
		#self.scorollerarea = QScrollArea()
		#self.scorollerarea.setWidget(self.top)
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.top,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)
	
	def mainMenu(self):
		mainMenu = self.menuBar()
		menu_about = QAction("&Version", self)
		menu_about.triggered.connect(self.aboutBox)
		aboutMenu = mainMenu.addMenu("&About")
		aboutMenu.addAction(menu_about)

	def linkFunction(self):
		self.top.hk.net1.btn.clicked.connect(self.sshConnectRun1)
		self.top.ms.wf_out.run1_btn.clicked.connect(self.WFO_Ch1Run)

	def LoadQITpreset(self):
		self.SettingData = ["hostname"]
		if not os.path.isdir(SETTING_FILEPATH):
			print("dir NOT exist")
			os.mkdir(SETTING_FILEPATH)
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)
		elif not os.path.exists(SETTING_FILENAME):
			print("file NOT exist")
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)
		else:
			self.SettingData = fil2a.TexTFileto1DList(SETTING_FILENAME, self.loggername)
			#print(self.SettingData)
			if (len(self.SettingData) != index_total):
				print("data len NOT the same")
				self.SettingData = ["hostname"]
				fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)

		self.top.hk.net1.IP.setText(self.SettingData[index_IP1])

	def addAccesoryFlag(self, loggername):
		#Qlogger.QuConsolelogger(loggername, logging.DEBUG)
		Qlogger.QuFilelogger(loggername, logging.WARNING, "log.txt")
		self.logger = logging.getLogger(loggername)

#Major Connection
	def sshConnectRun1(self):
		ip = self.top.hk.net1.IP.text()
		host = "rp-"+str(ip)+".local"
		self.SSH1_status = self.act.sshConnect(1, host, HOST_PORT, HOST_NAME, HOST_PWD)
		if (self.SSH1_status):
			self.act.ssh1.sendCmd(CONNECT_BIT_CMD, False, 1)
			self.top.hk.net1.SetConnectText(Qt.black, "Connection build", False)
			self.setEnableButton1()
			if not os.path.isdir(SETTING_FILEPATH):
				os.mkdir(SETTING_FILEPATH)
			self.SettingData[index_IP1] = ip
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)
		else:
			self.top.hk.net1.SetConnectText(Qt.red, "SSH connect failed", True)

	def setEnableButton1(self):
		# self.top.hk.net1.connectBtn.setEnabled(False)
		self.top.ms.wf_out.run1_btn.setEnabled(self.SSH1_status)

#Waveform Output
	def WFO_Ch1Run(self):
		freq = self.top.ms.wf_out.freq.spin.value() 
		rfamp = self.top.ms.wf_out.rfamp.spin.value() 
		dcamp = float(self.top.ms.wf_out.dcamp.spin.value()/1000)

		cmd2 = LIB_PATH + "./DAC 8 " + str(dcamp)
		# print(cmd2)
		self.act.ssh1.sendCmd(cmd2, True)
		time.sleep(0.1)

		cmd1 = WF_OUTPUT_CMD + str(freq) + " " + str(rfamp) + " 0"
		# print(cmd1)
		self.act.ssh1.sendCmd(cmd1, True)
		# stdout = self.act.sendSSHQuerry(1, cmd, True)
		# output = stdout.readline()
		# print(output)

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

