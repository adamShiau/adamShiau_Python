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
import QSS005_QIT2_Widget as QIT_UI
import QSS005_QIT2_Action as ACT
import numpy as np 

HOST_NAME = "root"
HOST_PWD = "root"
HOST_PORT = 22

index_IP = 0
index_fileheader = 1
index_freq = 2
index_dataPts = 3
index_rolling = 4
index_delay = 5
index_dcOffset = 6
index_rfOffset = 7
index_polarity = 8
index_startMass = 9
index_stopMass = 10
index_massCenter = 11
index_massRange = 12
index_cdc = 13
index_crf = 14
index_optimize = 15
index_threshold = 16
index_width = 17
index_calib_offset = 18
index_total = 19

SETTING_FILEPATH = "set"
SETTING_FILENAME = "set/QIT2_setting.txt"
ENG_SETTING_FILENAME = "set/QIT2_eng_setting.txt"
MASS_FILENAME = "set/mass_setting.txt"
# OUTPUT_FILENAME = "output_data.txt"
TIC_FILENAME = "tic_data.txt"

CONNECT_BIT_CMD = "cat /root/GRC_v4.bit > /dev/xdevcfg"

Mass_Table_Max = 6

ERROR1_TEXT = "Mass table must have more than two records"
ERROR2_TEXT = "Mass table already have this data"
ERROR3_TEXT = "The same mass data has different parameter"

TITLE_TEXT = " Acdemic Sincica GRC Mass Spectrometer "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS005 QIT V3.03 \n\n" + \
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

		self.dc_act = ACT.DC_Action(self.act.ssh, self.loggername)
		self.thread1 = QThread()
		self.dc_act.moveToThread(self.thread1)
		self.thread1.started.connect(self.dc_act.readData)

		self.tic_act = ACT.TicAction(self.act.ssh, self.loggername)
		self.thread2 = QThread()
		self.tic_act.moveToThread(self.thread2)
		self.thread2.started.connect(self.tic_act.ticRun)

		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.LoadQITpreset()
		self.SSH_status = False

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
		self.top.hk.net.btn.clicked.connect(self.sshConnectRun)
		self.top.ms.dc.runBtn.clicked.connect(self.dc_RunBtn)
		self.top.ms.dc.stopBtn.clicked.connect(self.dc_StopBtn)
		self.top.ms.dc.addBtn.clicked.connect(self.dc_addMassTable)
		# self.top.ms.dc.freq.spin.valueChanged.connect(self.dc_sendCmd)
		# self.top.ms.dc.cdc.spin.valueChanged.connect(self.dc_sendCmd)
		# self.top.ms.dc.crf.spin.valueChanged.connect(self.dc_sendCmd)
		# self.top.ms.dc.mass.spin.valueChanged.connect(self.dc_sendCmd)

		self.top.ms.tic.run.clicked.connect(self.tic_RunBtn)
		self.top.ms.tic.stop.clicked.connect(self.tic_StopBtn)
		self.top.ms.tic.zeroBtn.clicked.connect(self.tic_ZeroBtn)
		self.top.ms.tic.save.clicked.connect(self.tic_SaveBtn)
		self.top.ms.tic.modify.clicked.connect(lambda:self.massDialog(True))

		self.dc_act.update_data.connect(self.dc_drawData)
		self.dc_act.finished.connect(self.dc_finish)
		self.tic_act.update_data.connect(self.tic_drawData)
		self.tic_act.finished.connect(self.tic_Finish)

	def LoadQITpreset(self):
		self.SettingData = ["hostname", "", 0.1, 10, 1, 50, 0, 0, 1, 30, 500, 0, 0.1, 0.0000001, 0.000001, 0, 0.01, 1, 0]
		self.engData = [141, 30, 29]
		if not os.path.isdir(SETTING_FILEPATH):
			print("dir NOT exist")
			os.mkdir(SETTING_FILEPATH)
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)
			fil2a.array1DtoTextFile(ENG_SETTING_FILENAME, self.engData, self.loggername)
		elif not os.path.exists(SETTING_FILENAME):
			print("setting file NOT exist")
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)
		elif not os.path.exists(ENG_SETTING_FILENAME):
			print("eng file NOT exist")
			fil2a.array1DtoTextFile(ENG_SETTING_FILENAME, self.engData, self.loggername)
		else:
			self.engData = fil2a.TexTFileto1DList(ENG_SETTING_FILENAME, self.loggername)
			self.SettingData = fil2a.TexTFileto1DList(SETTING_FILENAME, self.loggername)
			#print(self.SettingData)
			if (len(self.SettingData) != index_total):
				print("data len NOT the same")
				self.SettingData = ["hostname", "", 0.1, 10, 1, 50, 0, 0, 1, 30, 500, 0, 0.1, 0.0000001, 0.000001, 0, 0.01, 1, 0]
				fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)

		self.top.hk.net.IP.setText(self.SettingData[index_IP])
		self.top.hk.FHedit.edit.setText(self.SettingData[index_fileheader])

		self.top.ms.tic.freq.spin.setValue(float(self.SettingData[index_freq]))
		self.top.ms.tic.dataPts.spin.setValue(int(self.SettingData[index_dataPts]))
		self.top.ms.tic.rolling.spin.setValue(int(self.SettingData[index_rolling]))
		self.top.ms.tic.delay.spin.setValue(int(self.SettingData[index_delay]))
		self.top.ms.tic.dcOffset.spin.setValue(float(self.SettingData[index_dcOffset]))
		self.top.ms.tic.rfOffset.spin.setValue(float(self.SettingData[index_rfOffset]))
		if (int(self.SettingData[index_polarity]) == -1):
			self.top.ms.tic.poBtn2.setChecked(True)
		else:
			self.top.ms.tic.poBtn1.setChecked(True)

		self.top.ms.tic.startMass.spin.setValue(int(self.SettingData[index_startMass]))
		self.top.ms.tic.stopMass.spin.setValue(int(self.SettingData[index_stopMass]))
		self.top.ms.tic.massCenter.spin.setValue(int(self.SettingData[index_massCenter]))
		self.top.ms.tic.massRange.spin.setValue(float(self.SettingData[index_massRange]))
		self.top.ms.tic.cdc.spin.setValue(float(self.SettingData[index_cdc]))
		self.top.ms.tic.crf.spin.setValue(float(self.SettingData[index_crf]))
		if (int(self.SettingData[index_optimize]) == 1):
			self.top.ms.tic.cBtn2.setChecked(True)
		else:
			self.top.ms.tic.cBtn1.setChecked(True)

		self.top.ms.tic.threshold.spin.setValue(float(self.SettingData[index_threshold]))
		self.top.ms.tic.width.spin.setValue(int(self.SettingData[index_width]))
		self.tic_act.calib_offset = float(self.SettingData[index_calib_offset])

		self.all_mass_array = []
		if os.path.exists(MASS_FILENAME):
			temp_array = fil2a.TexTFileto2DList(MASS_FILENAME, ",", self.loggername)
			# print(temp_array)
			num = len(temp_array)
			# print(num)
			if (num > 0):
				self.top.ms.tic.modify.setEnabled(True)
				for i in range(0, num):
					if (temp_array[i][0] == "False"):
						check = False
					else:
						check = True
					self.all_mass_array.append( [ check, float(temp_array[i][1]), float(temp_array[i][2]), int(temp_array[i][3]) ] )
				# print(self.all_mass_array)
				self.top.ms.dc.cdc.spin.setValue(float(self.all_mass_array[num-1][1]))
				self.top.ms.dc.crf.spin.setValue(float(self.all_mass_array[num-1][2]))
				self.top.ms.dc.mass.spin.setValue(int(self.all_mass_array[num-1][3]))


	def SaveTICpreset(self, freq, dataPts, rolling, delay, dcOffset, rfOffset, 
						startMass, stopMass, massCenter, massRange, cdc, crf, threshold, width):
		self.SettingData[index_freq] = freq
		self.SettingData[index_dataPts] = dataPts
		self.SettingData[index_rolling] = rolling
		self.SettingData[index_delay] = delay
		self.SettingData[index_dcOffset] = dcOffset
		self.SettingData[index_rfOffset] = rfOffset
		if self.top.ms.tic.poBtn2.isChecked():
			self.SettingData[index_polarity] = -1
		else:
			self.SettingData[index_polarity] = 1

		self.SettingData[index_startMass] = startMass
		self.SettingData[index_stopMass] = stopMass
		self.SettingData[index_massCenter] = massCenter
		self.SettingData[index_massRange] = massRange
		self.SettingData[index_cdc] = cdc
		self.SettingData[index_crf] = crf
		if self.top.ms.tic.cBtn2.isChecked():
			self.SettingData[index_optimize] = 1
		else:
			self.SettingData[index_optimize] = 0

		self.SettingData[index_threshold] = threshold
		self.SettingData[index_width] = width

		fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)

	def addAccesoryFlag(self, loggername):
		#Qlogger.QuConsolelogger(loggername, logging.DEBUG)
		Qlogger.QuFilelogger(loggername, logging.WARNING, "log.txt")
		self.logger = logging.getLogger(loggername)

#Major Connection
	def sshConnectRun(self):
		ip = self.top.hk.net.IP.text()
		host = "rp-"+str(ip)+".local"
		self.SSH_status = self.act.sshConnect(1, host, HOST_PORT, HOST_NAME, HOST_PWD)
		if (self.SSH_status):
			self.act.ssh.sendCmd(CONNECT_BIT_CMD, False, 1)
			self.top.hk.net.SetConnectText(Qt.black, "Connection build", False)
			self.setEnableButton1()
			if not os.path.isdir(SETTING_FILEPATH):
				os.mkdir(SETTING_FILEPATH)
			self.SettingData[index_IP] = ip
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)
		else:
			self.top.hk.net.SetConnectText(Qt.red, "SSH connect failed", True)

	def setEnableButton1(self):
		# self.top.hk.net.connectBtn.setEnabled(False)
		self.top.ms.dc.runBtn.setEnabled(self.SSH_status)
		# self.top.ms.dc.zeroBtn.setEnabled(self.SSH_status)
		self.top.ms.tic.run.setEnabled(self.SSH_status)

#DC Parameter
	def dc_sendCmd(self):
		self.freq = self.top.ms.dc.freq.spin.value() 
		cdc = self.top.ms.dc.cdc.spin.value()
		crf = self.top.ms.dc.crf.spin.value()
		mass = self.top.ms.dc.mass.spin.value()

		self.dc_act.send_DC_Cmd(self.freq, cdc, crf, mass)

	def dc_RunBtn(self):
		self.top.pic.setCurrentIndex(0)
		sample_time = self.top.ms.dc.sample_time.spin.value()
		sample_time = float(sample_time/1000.0)

		if self.top.ms.dc.chBtn2.isChecked():
			channel = 1
		else:
			channel = 0

		# update by Adam request 2020.7.2, send ADC_MV before CH1 and DAC
		self.dc_act.setAdcCmd(sample_time, channel, self.engData)
		self.dc_sendCmd()
		self.dc_act.runFlag = True
		self.thread1.start()

		self.top.ms.dc.runBtn.setEnabled(False)
		self.top.ms.dc.stopBtn.setEnabled(True)
		# self.top.ms.dc.zeroBtn.setEnabled(False)

	def dc_drawData(self, data):
		self.data = data
		self.top.pic.plot.ax.clear()
		self.top.pic.plot.ax.plot(self.data, color = 'blue', linestyle = '-', marker = '')
		self.top.pic.plot.figure.canvas.draw()
		self.top.pic.plot.figure.canvas.flush_events()

	def dc_StopBtn(self):
		self.dc_act.runFlag = False
		# print("stop dc")
		self.dc_act.send_DC_Cmd(self.freq, 0, 0, 0)

	def dc_finish(self):
		self.thread1.quit()
		self.thread1.wait()
		self.top.ms.dc.runBtn.setEnabled(self.SSH_status)
		self.top.ms.dc.stopBtn.setEnabled(False)
		# self.top.ms.dc.zeroBtn.setEnabled(self.SSH_status)

	def dc_addMassTable(self):
		cdc = self.top.ms.dc.cdc.spin.value()
		crf = self.top.ms.dc.crf.spin.value()
		mass = self.top.ms.dc.mass.spin.value()
		num = len(self.all_mass_array)
		double_flag = False
		# print(num)
		if (num > 0):
			for i in range(0, num):
				if ( (cdc == self.all_mass_array[i][1])
				and (crf == self.all_mass_array[i][2])
				and (mass == self.all_mass_array[i][3]) ):
					double_flag = True
					break
			if (double_flag):
				self.errorBox(ERROR2_TEXT)
				return
			elif (num >= Mass_Table_Max):
				del self.all_mass_array[0]
		self.all_mass_array.append( [True, cdc, crf, mass] )
		# print(self.all_mass_array)
		self.top.ms.tic.modify.setEnabled(True)
		self.massDialog(False)

	def massDialog(self, can_select):
		MassDialog = QIT_UI.MassDialog(self.all_mass_array, can_select)
		self.all_mass_array = MassDialog.getParameter(self.all_mass_array, can_select)
		# print(self.all_mass_array)
		fil2a.list2DtoTextFile(MASS_FILENAME, self.all_mass_array, ",", self.loggername, header = "", double_float = True)
		# print("main call")

	def getOptData(self):
		self.doubleMass = False
		massData = []
		total = len(self.all_mass_array)
		for i in range(0, total):
			if (self.all_mass_array[i][0]):
				massLen = len(massData)
				for j in range(0, massLen):
					# print(self.all_mass_array[i][3])
					# print(self.optData[j][2])
					if (self.all_mass_array[i][3] == massData[j][2]):
						self.doubleMass = True
						break
				massData.append([self.all_mass_array[i][1], self.all_mass_array[i][2], self.all_mass_array[i][3]])
		return massData

	def tic_RunBtn(self):
		if (len(self.all_mass_array) < 2):
			self.errorBox(ERROR1_TEXT)
			return
		optData = self.getOptData()
		# print(optData)
		if (len(optData) < 2):
			self.errorBox(ERROR1_TEXT)
			return
		elif (self.doubleMass):
			self.errorBox(ERROR3_TEXT)
			return

		self.top.pic.setCurrentIndex(1)
		select_path = QFileDialog.getExistingDirectory(self, "Save Raw Data", "./")
		header = self.top.hk.FHedit.edit.text()

		freq_ui = self.top.ms.tic.freq.spin.value()
		freq = freq_ui*1000
		dataPts = self.top.ms.tic.dataPts.spin.value()
		rolling = self.top.ms.tic.rolling.spin.value()
		delay = self.top.ms.tic.delay.spin.value()
		dcOffset = self.top.ms.tic.dcOffset.spin.value()
		rfOffset = self.top.ms.tic.rfOffset.spin.value()
		if self.top.ms.tic.poBtn2.isChecked():
			polarity = -1
		else:
			polarity = 1

		startMass = self.top.ms.tic.startMass.spin.value()
		stopMass = self.top.ms.tic.stopMass.spin.value()
		massCenter = self.top.ms.tic.massCenter.spin.value()
		massRange = self.top.ms.tic.massRange.spin.value()
		minMass = massCenter - massRange
		maxMass = massCenter + massRange
		cdc = self.top.ms.tic.cdc.spin.value()
		crf = self.top.ms.tic.crf.spin.value()
		optimized = self.top.ms.tic.cBtn2.isChecked()

		threshold = self.top.ms.tic.threshold.spin.value()
		width = self.top.ms.tic.width.spin.value()
		if self.top.ms.dc.chBtn2.isChecked():
			channel = 1
		else:
			channel = 0

		self.SaveTICpreset(freq_ui, dataPts, rolling, delay, dcOffset, rfOffset, startMass, stopMass, massCenter, massRange, cdc, crf, threshold, width)
		self.tic_act.setParam(freq, dataPts, rolling, delay, threshold, width, polarity, startMass, stopMass, channel, self.engData, select_path, header)
		self.tic_act.ticInit(optData, minMass, maxMass, dcOffset, rfOffset, optimized, cdc, crf)

		self.top.ms.dc.runBtn.setEnabled(False)
		self.top.ms.tic.run.hide()
		self.top.ms.tic.run.setEnabled(False)
		self.top.ms.tic.stop.show()
		self.top.ms.tic.stop.setEnabled(True)

		self.tic_act.ticFlag = True
		if (1):
			self.thread2.start()
		else: # for check self.tic_act.ticInit generateMass
			self.top.pic.plot2.ax1.clear()
			self.top.pic.plot2.ax2.clear()
			self.top.pic.plot2.ax2.plot(self.tic_act.mass_array, self.tic_act.vdc_array, color = 'blue', linestyle = '-', marker = '')
			self.top.pic.plot2.ax2.set_xlabel("m/z")
			self.top.pic.plot2.ax3.clear()
			self.top.pic.plot2.ax3.plot(self.tic_act.mass_array, self.tic_act.vrf_array, color = 'green', linestyle = '-', marker = '')
			self.top.pic.plot2.ax3.set_xlabel("m/z")
			self.top.pic.plot2.figure.canvas.draw()
			self.top.pic.plot2.figure.canvas.flush_events()


	def tic_drawData(self, data, tic, xic, index):
		self.tic = tic
		self.xic = xic
		index_text = "Index = " + str(index)
		self.top.ms.tic.run_index1.setText(index_text)
		# self.top.ms.tic.run_index2.setText(str(index))
		self.top.pic.plot2.ax1.clear()
		self.top.pic.plot2.ax1.plot(tic, color = 'blue', linestyle = '-', label = 'tic')
		self.top.pic.plot2.ax1.plot(xic, color = 'red', linestyle = '-', label = 'xic')
		self.top.pic.plot2.ax1.set_xlabel("Time (s)")
		self.top.pic.plot2.ax1.legend()
		self.top.pic.plot2.ax2.clear()
		self.top.pic.plot2.ax2.plot(self.tic_act.mass_array, data[1], color = 'blue', linestyle = '-', marker = '')
		self.top.pic.plot2.ax2.set_xlabel("m/z")
		self.top.pic.plot2.ax3.clear()
		self.top.pic.plot2.ax3.plot(self.tic_act.mass_array, data[2], color = 'green', linestyle = '-', marker = '')
		self.top.pic.plot2.ax3.set_xlabel("m/z")
		self.top.pic.plot2.figure.canvas.draw()
		self.top.pic.plot2.figure.canvas.flush_events()

	def tic_StopBtn(self):
		self.tic_act.ticFlag = False
		# print("stop tic")

	def tic_Finish(self):
		self.thread2.quit()
		self.thread2.wait()
		self.top.ms.dc.runBtn.setEnabled(self.SSH_status)
		self.top.ms.tic.run.show()
		self.top.ms.tic.run.setEnabled(self.SSH_status)
		self.top.ms.tic.stop.hide()
		self.top.ms.tic.stop.setEnabled(False)
		self.top.ms.tic.zeroBtn.setEnabled(True)
		self.top.ms.tic.save.setEnabled(True)

	def tic_ZeroBtn(self):
		num = len(self.tic_act.singleData)
		new_calib_offset = sum(self.tic_act.singleData) / num * (-1)
		self.tic_act.calib_offset = self.tic_act.calib_offset + new_calib_offset
		self.dc_act.calib_offset = self.tic_act.calib_offset
		print("calib_offset = " + str(self.tic_act.calib_offset) )
		self.SettingData[index_calib_offset] = self.tic_act.calib_offset
		fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)

	def tic_SaveBtn(self):
		SaveFileName,_ = QFileDialog.getSaveFileName(self,
						"Save Data",
						"./" + TIC_FILENAME,
						"Text Files (*.txt)")
		if (SaveFileName != ''):
			header = self.top.hk.FHedit.edit.text()
			self.SettingData[index_fileheader] = header
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)

			curr_time = datetime.datetime.now()
			header = header + "\n" + str(curr_time) + "\n" + "time, tic, xic"
			tempdata = np.array([self.tic_act.time_array, self.tic, self.xic], np.float64)
			tempdata = np.transpose(tempdata)
			fil2a.list2DtoTextFile(SaveFileName, tempdata,",",self.loggername, header)

			self.top.ms.tic.save.setEnabled(False)

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	def errorBox(self, msg):
		msgBox = QMessageBox()
		msgBox.about(self, "Message", msg)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

