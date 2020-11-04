import os
import sys
sys.path.append("../")
import time
import logging
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import py3lib.QuLogger as Qlogger
import py3lib.FileToArray as fil2a
import QSS008_Widget as UI
import QSS008_Action as ACT
import numpy as np


HOST_NAME = "root"
HOST_PWD = "root"
HOST_PORT = 22
READOUT_FILENAME = "Signal_Read_Out.txt"

MAX_SAVE_INDEX = 3000

TITLE_TEXT = " NCU GyroScope"
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS008 V2.07 \n\n" + \
" Copyright @ 2019 Quantaser \n" + \
" Maintain by Quantaser Photonics Co. Ltd "


class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger
		self.act = ACT.qss008Act(self.loggername)
		self.top = UI.mainWidget()
		self.sshStatus = False
		self.usbConnect()

		self.thread1 = QThread()
		self.thread1.started.connect(self.act.runFog)
		self.act.fog_update.connect(self.plotFog)
		self.act.fog_finished.connect(self.fogFinished)
		self.data = np.empty(0)
		self.dt = np.empty(0)

		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.loadUIpreset()

	def mainUI(self):
		mainLayout = QGridLayout()
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.top,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)
	
	def mainMenu(self):
		mainMenu = self.menuBar()

		# fileMenu = mainMenu.addMenu("File")
		# menu_save = QAction("&Save",self)
		# fileMenu.addAction(menu_save)
		# menu_save.triggered.connect(self.fileBox)

		setMenu = mainMenu.addMenu("Setting")
		setSignal = QAction("&Signal Sampling", self)
		setKal = QAction("&Kalman filter", self)
		setMenu.addAction(setSignal)
		setMenu.addAction(setKal)
		setSignal.triggered.connect(self.callSetSignal)
		setKal.triggered.connect(self.callSetKal)

		aboutMenu = mainMenu.addMenu("&About")
		menu_about = QAction("&Version", self)
		aboutMenu.addAction(menu_about)
		menu_about.triggered.connect(self.aboutBox)

	def linkFunction(self):
		self.top.net.btn.clicked.connect(self.netConnect)
		self.top.usb.btn.clicked.connect(self.usbConnect)

		self.top.open.clicked.connect(self.set_BitFile)
		self.top.close.clicked.connect(self.set_BitFile)

		self.top.gain.gain1.valueChanged.connect(self.set_Gain1)
		self.top.gain.gain1pwr.currentIndexChanged.connect(self.set_Gain1pwr)
		self.top.gain.gain2pwr.currentIndexChanged.connect(self.set_Gain2pwr)

		self.top.fog.modH.spin.valueChanged.connect(self.set_modH)
		self.top.fog.modL.spin.valueChanged.connect(self.set_modL)
		self.top.fog.freq.spin.valueChanged.connect(self.set_freq)
		self.top.fog.twoPi.spin.valueChanged.connect(self.set_twoPi)

		self.top.fog.poBtn1.clicked.connect(self.set_Polarity)
		self.top.fog.poBtn2.clicked.connect(self.set_Polarity)

		self.top.start.clicked.connect(self.buttonStart)
		self.top.getData.clicked.connect(self.buttonGetData)
		self.top.stop.clicked.connect(self.buttonStop)

	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	# def fileBox(self):
	#     saveBox = QMessageBox()
	#     SaveFileName,_ = QFileDialog.getSaveFileName(self,
	#                     "Save Data",
	#                     "./" + READOUT_FILENAME,
	#                     "Text Files (*.txt)")
	#     if (SaveFileName != ''):
	#         fil2a.array1DtoTextFile(SaveFileName, self.data, self.loggername)
	#     saveBox.about(self, "Save File", "File saving completed")

	def loadUIpreset(self):
		self.top.net.IP.setText(self.act.host)

		if self.act.mode == "open":
			self.top.open.setChecked(True)
		elif self.act.mode == "close":
			self.top.close.setChecked(True)
		else:
			self.top.check.setChecked(True)
		self.pre_mode = self.act.mode

		self.top.gain.gain1.setValue(int(self.act.gain1))
		self.top.gain.gain1pwr.setCurrentIndex(int(self.act.gain1pwr))
		self.top.gain.gain2pwr.setCurrentIndex(int(self.act.gain2pwr))

		self.top.fog.modH.spin.setValue(int(self.act.modHigh))
		self.top.fog.modL.spin.setValue(int(self.act.modLow))
		self.top.fog.freq.spin.setValue(int(self.act.modFreq))
		self.top.fog.twoPi.spin.setValue(int(self.act.piVth))

		if (int(self.act.polarity) == 0):
			self.top.fog.poBtn2.setChecked(True)
		else:
			self.top.fog.poBtn1.setChecked(True)

		self.top.fog.coeff.setText(str(self.act.coeff))

#Connection
	def callSetKal(self):
		self.act.writePreset()
		dialog2 = UI.SetKalDialog(self.act.paralist[16:22])
		KalData = dialog2.getParameter(self.act.paralist[16:22])
		# print("callSetKal")
		# print(KalData)
		self.act.modQ = KalData[0]
		self.act.modR = KalData[1]
		self.act.modQ2 = KalData[2]
		self.act.modR2 = KalData[3]
		self.act.upperBand = KalData[4]
		self.act.lowerBand = KalData[5]

	def callSetSignal(self):
		self.act.writePreset()
		self.pre_mode_open = self.act.mode_open
		diaglog2 = UI.SetSignalDialog(self.act.paralist[5:10])
		signalData = diaglog2.getParameter(self.act.paralist[5:10])
		# print("callSetSignal")
		# print(signalData)
		self.act.ignor = signalData[0]
		self.act.offset = signalData[1]
		self.act.stepVth = signalData[2]
		self.act.inavg = signalData[3]
		self.act.mode_open = signalData[4]
		#if (self.act.mode == "open") and (self.pre_mode_open != self.act.mode_open):
		#	self.act.setBitFile()
			#print("mode_open = " + str(self.act.mode_open))

	def netConnect(self):
		ip = self.top.net.IP.text()
		host = "rp-"+str(ip)+".local"
		self.sshStatus = self.act.ssh.connectSSH(host, HOST_PORT, HOST_NAME, HOST_PWD)
		self.act.ssh.connectFTP()
		if self.sshStatus:
			self.top.net.SetConnectText(Qt.black, "Connection build", False)
			self.act.host = ip
			self.act.writePreset()
			self.set_BitFile(True)
			self.top.enableSSHsetting(True)
			if self.usbConnStatus:
				self.top.start.setEnabled(True)
		else:
			self.top.net.SetConnectText(Qt.red, "SSH connect failed", True)

	def usbConnect(self):
		self.usbConnStatus = self.act.usbConnect()
		if self.usbConnStatus:
			self.top.usb.SetConnectText(Qt.black,"Connection build", False)
			if self.sshStatus:
				self.top.start.setEnabled(True)
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)

	def set_BitFile(self, firstConnect = False):
		if self.act.runFlag:
			return
		if self.top.open.isChecked():
			self.act.mode = "open"
		elif self.top.close.isChecked():
			self.act.mode = "close"
		else:
			self.act.mode = "check"
		#if (firstConnect) or (self.pre_mode != self.act.mod):
		#	self.act.setBitFile()
			#print("mode = " + str(self.act.mode))

	def set_Gain1(self):
		if self.act.runFlag:
			return
		self.act.gain1 = self.top.gain.gain1.value()
		out = self.act.setGain1()
		self.top.gain.fst_gain_out.setText(str("%3.3f" % out))

	def set_Gain1pwr(self):
		if self.act.runFlag:
			return
		self.act.gain1pwr = self.top.gain.gain1pwr.currentIndex()
		out = self.act.setGain1()
		self.top.gain.fst_gain_out.setText(str("%3.3f" % out))

	def set_Gain2pwr(self):
		if self.act.runFlag:
			return
		self.act.gain2pwr = self.top.gain.gain2pwr.currentIndex()
		out = self.act.setGain2()
		self.top.gain.sec_gain_out.setText(str("%3.3f" % out))

	def set_Polarity(self):
		if self.act.runFlag:
			return
		if self.top.fog.poBtn2.isChecked():
			self.act.polarity = 0
		else:
			self.act.polarity = 1
		self.act.setPolarity()
		#print("polarity = " + str(self.act.polarity))

	def set_modH(self):
		if self.act.runFlag:
			return
		self.act.modHigh = self.top.fog.modH.spin.value()
		out = self.act.setModHigh()
		self.top.fog.modH.labelvalue.setText(str("%3.3f" % out))

	def set_modL(self):
		if self.act.runFlag:
			return
		self.act.modLow = self.top.fog.modL.spin.value()
		out = self.act.setModLow()
		self.top.fog.modL.labelvalue.setText(str("%3.3f" % out))

	def set_freq(self):
		if self.act.runFlag:
			return
		self.act.modFreq = self.top.fog.freq.spin.value()
		out = self.act.setModFreq()
		self.top.fog.freq.labelvalue.setText(str("%3.3f" % out))

	def set_twoPi(self):
		if self.act.runFlag:
			return
		self.act.piVth = self.top.fog.twoPi.spin.value()
		out = self.act.setPiVth()
		self.top.fog.twoPi.labelvalue.setText(str("%3.3f" % out))

	def buttonStart(self):
		if self.act.runFlag:
			return
		self.act.SaveFileName,_ = QFileDialog.getSaveFileName(self,
						"Save Data",
						"./" + READOUT_FILENAME,
						"Text Files (*.txt)")
		self.data = np.empty(0)
		self.dt = np.empty(0)
		self.act.writePreset()
		self.act.setIgnor()
		self.act.setOffset()
		self.act.setStepVth()
		self.act.setAVG()
		self.act.setModQ()
		self.act.setModR()
		self.act.setModQ2()
		self.act.setModR2()
		self.act.setUpperBand()
		self.act.setLowerBand()
		self.act.runFlag = True
		self.top.enableSSHsetting(False)
		self.top.start.setEnabled(False)

		self.top.stop.setEnabled(True)
		self.thread1.start()
		if self.top.close.isChecked():
			self.top.getData.setEnabled(True)
		else:
			self.top.getData.setEnabled(False)

	def buttonGetData(self):
		self.act.runFlag = False
		self.top.enableSSHsetting(True)
		self.top.start.setEnabled(False)
		result =self.act.getData()
		print (result)
		self.top.plot.ax2.clear()
		self.top.plot.ax2.plot(result)
		self.top.plot.figure.canvas.draw()
		self.top.plot.figure.canvas.flush_events()

	def buttonStop(self):
		self.act.setStop()
		self.act.runFlag = False
		self.top.enableSSHsetting(True)
		self.top.stop.setEnabled(False)
		self.top.getData.setEnabled(False)
		if self.sshStatus and self.usbConnStatus:
			self.top.start.setEnabled(True)

	def fogFinished(self):
		self.thread1.quit()
		self.thread1.wait()

	def plotFog(self, data, dt):
		temp = len(self.data)
		# self.logger.error("len = %d", temp)

		if (len(self.data) >= MAX_SAVE_INDEX):
			self.data = self.data[40:]
			self.dt = self.dt[40:]
			# self.logger.error("delete data")

		coeff = self.top.fog.coeff.text()
		if (coeff == ""):
			self.act.coeff = 1
		else:
			self.act.coeff = float(coeff)
		#print(f_coeff)

		self.data = np.append(self.data, data*self.act.coeff)
		self.dt = np.append(self.dt, dt)
		#print(self.data)

		# 2020.1.17 sherry, save file move to act.runFog()
		# if (self.act.SaveFileName != ''):
		# 	fil2a.array1DtoTextFile(self.act.SaveFileName, self.data, self.loggername)
		self.top.plot.ax1.clear()
		self.top.plot.ax1.set_ylabel("")
		self.top.plot.ax1.plot(self.dt, self.data, color = 'blue', linestyle = '-', marker = '*')
		self.top.plot.figure.canvas.draw()
		self.top.plot.figure.canvas.flush_events()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

