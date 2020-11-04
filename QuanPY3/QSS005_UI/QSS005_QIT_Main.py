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
import QSS005_QIT_Widget as QIT_UI
import QSS005_QIT_Action as ACT
import numpy as np 

HOST_NAME = "root"
HOST_PWD = "root"
HOST_PORT = 22

index_IP1 = 0
index_IP2 = 1
index_fileheader = 2
index_scanMode = 3
index_startMass = 4
index_stopMass = 5
index_massMin = 6
index_massMax = 7
index_radius = 8
index_freq = 9
index_rolling = 10
index_dataPts = 11
index_threshold = 12
index_width = 13
index_cdc = 14
index_crf = 15
index_total = 16

SETTING_FILEPATH = "set"
SETTING_FILENAME = "set/QIT_setting.txt"
OUTPUT_FILENAME = "output_data.txt"
TIC_FILENAME = "tic_data.txt"

#CONNECT_BIT_CMD = "cat /root/GRC_v3.bit > /dev/xdevcfg"
CONNECT_BIT_CMD = "cat /root/GRC_MST.bit > /dev/xdevcfg"
WF_OUTPUT_CMD = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./CH1 "

ADC_MV_SCAN_READ = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./ADC_MV "
MV_Numver_MIN = 50
ADC_SCAN_READ_gain = ' 1'

ADC_SCAN_READ = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./ADC "

TITLE_TEXT = " Acdemic Sincica GRC Mass Spectrometer "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS005 QIT V2.033 \n\n" + \
" Copyright @ 2019 TAIP \n" + \
" Maintain by Quantaser Photonics Co. Ltd "


class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)		
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger 
		self.act = ACT.qss005Action(self.loggername)
		self.wfo_act = ACT.wfoAction(self.act.ssh1, self.loggername)
		self.wfm_act = ACT.wfmAction(self.act.ssh2, self.loggername)
		self.tic_act = ACT.ticAction(self.act.ssh1, self.loggername)
		self.top = QIT_UI.mainWidget()
		self.thread1 = QThread()
		self.thread2 = QThread()
		self.thread3 = QThread()
		self.wfo_act.moveToThread(self.thread1)
		self.wfm_act.moveToThread(self.thread2)
		self.tic_act.moveToThread(self.thread3)
		
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.LoadQITpreset()
		self.SSH1_status = False
		self.SSH2_status = False

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
		self.top.hk.net2.btn.clicked.connect(self.sshConnectRun2)

		self.top.ms.wf_out.run1_btn.clicked.connect(self.WFO_Ch1Run)
		self.top.ms.wf_out.ch1_freq.spin.valueChanged.connect(self.WFO_Ch1Run)
		self.top.ms.wf_out.ch1_amp.spin.valueChanged.connect(self.WFO_Ch1Run)
		self.top.ms.wf_out.ch1_offset.spin.valueChanged.connect(self.WFO_Ch1Run)
		self.top.ms.wf_out.start_btn.clicked.connect(self.WFO_StartBtn)
		self.top.ms.wf_out.stop_btn.clicked.connect(self.WFO_StopBtn)
		self.top.ms.wf_out.save_btn.clicked.connect(self.WFO_SaveBtn)

		self.top.ms.wf_mon.mon_btn.clicked.connect(self.WFM_RunBtn)
		self.top.ms.wf_mon.stop_btn.clicked.connect(self.WFM_StopBtn)

		self.top.ms.tic.run.clicked.connect(self.tic_RunBtn)
		self.top.ms.tic.stop.clicked.connect(self.tic_StopBtn)
		self.top.ms.tic.save.clicked.connect(self.tic_SaveBtn)

		self.wfo_act.update_data.connect(self.WFO_drawData)
		self.wfo_act.finished.connect(self.WFO_Finish)

		self.wfm_act.update_data.connect(self.WFM_drawData)
		self.wfm_act.finished.connect(self.WFM_Finish)

		self.tic_act.update_data.connect(self.tic_drawData)
		self.tic_act.finished.connect(self.tic_Finish)

	def LoadQITpreset(self):
		self.SettingData = ["hostname", "hostname", "", 1, 30, 500, 31, 500, 1, 0, 1, 10, 0, 1, 0.0001, 0.01]
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
				self.SettingData = ["hostname", "hostname", "", 1, 30, 500, 31, 500, 1, 0, 1, 10, 0, 1, 0.0001, 0.01]
				fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)

		self.top.hk.net1.IP.setText(self.SettingData[index_IP1])
		self.top.hk.net2.IP.setText(self.SettingData[index_IP2])
		self.top.hk.FHedit.edit.setText(self.SettingData[index_fileheader])
		self.top.ms.tic.startMass.spin.setValue(int(self.SettingData[index_startMass]))
		self.top.ms.tic.stopMass.spin.setValue(int(self.SettingData[index_stopMass]))
		self.top.ms.tic.massMin.spin.setValue(int(self.SettingData[index_massMin]))
		self.top.ms.tic.massMax.spin.setValue(int(self.SettingData[index_massMax]))
		self.top.ms.tic.radius.spin.setValue(float(self.SettingData[index_radius]))
		self.top.ms.tic.freq.spin.setValue(float(self.SettingData[index_freq]))
		self.top.ms.tic.rolling.spin.setValue(int(self.SettingData[index_rolling]))
		self.top.ms.tic.dataPts.spin.setValue(int(self.SettingData[index_dataPts]))
		self.top.ms.tic.threshold.spin.setValue(float(self.SettingData[index_threshold]))
		self.top.ms.tic.width.spin.setValue(int(self.SettingData[index_width]))
		self.top.ms.tic.cdc.spin.setValue(float(self.SettingData[index_cdc]))
		self.top.ms.tic.crf.spin.setValue(float(self.SettingData[index_crf]))
		#print("0 min = "+str(self.top.ms.tic.massMin.spin.value()))
		#print("0 max = "+str(self.top.ms.tic.massMax.spin.value()))
		# MUST set massMin after massMax again , 2019-12-4 fix massMin can NOT set value issue
		self.top.ms.tic.massMin.spin.setValue(int(self.SettingData[index_massMin]))

	def SaveTICpreset(self, startMass, stopMass, massMin, massMax, radius, freq, rolling, dataPts, threshold, width, cdc, crf):
		self.SettingData[index_startMass] = startMass
		self.SettingData[index_stopMass] = stopMass
		self.SettingData[index_massMin] = massMin
		self.SettingData[index_massMax] = massMax
		self.SettingData[index_radius] = radius
		self.SettingData[index_freq] = freq
		self.SettingData[index_rolling] = rolling
		self.SettingData[index_dataPts] = dataPts
		self.SettingData[index_threshold] = threshold
		self.SettingData[index_width] = width
		self.SettingData[index_cdc] = cdc
		self.SettingData[index_crf] = crf
		fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)

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
		self.top.ms.wf_out.start_btn.setEnabled(self.SSH1_status)
		self.top.ms.tic.run.setEnabled(self.SSH1_status)

#AUX Connection
	def sshConnectRun2(self):
		ip = self.top.hk.net2.IP.text()
		host = "rp-"+str(ip)+".local"
		self.SSH2_status = self.act.sshConnect(2, host, HOST_PORT, HOST_NAME, HOST_PWD)
		if (self.SSH2_status):
			self.act.ssh2.sendCmd(CONNECT_BIT_CMD, False, 1)
			self.top.hk.net2.SetConnectText(Qt.black, "Connection build", False)
			self.setEnableButton2()
			if not os.path.isdir(SETTING_FILEPATH):
				os.mkdir(SETTING_FILEPATH)
			self.SettingData[index_IP2] = ip
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)
		else:
			self.top.hk.net2.SetConnectText(Qt.red, "SSH connect failed", True)

	def setEnableButton2(self):
		# self.top.hk.net2.connectBtn.setEnabled(False)
		self.top.ms.wf_mon.mon_btn.setEnabled(self.SSH2_status)

#Waveform Output
	def WFO_Ch1Run(self):
		freq = self.top.ms.wf_out.ch1_freq.spin.value() 
		amp = self.top.ms.wf_out.ch1_amp.spin.value()
		offset = self.top.ms.wf_out.ch1_offset.spin.value()

		cmd = WF_OUTPUT_CMD + str(freq) + " " + str(amp) + " " + str(offset)
		self.act.ssh1.sendCmd(cmd, True)
		# stdout = self.act.sendSSHQuerry(1, cmd, True)
		# output = stdout.readline()
		# print(output)

	def WFO_StartBtn(self):
		#print("WFO start")
		self.top.pic.setCurrentIndex(0)
		sample_time = self.top.ms.wf_out.sample_time.spin.value()
		sample_time = float(sample_time/1000.0)
		acqu_time = self.top.ms.wf_out.acqu_time.spin.value()

		if self.top.ms.wf_out.chBtn2.isChecked():
			Channel_str = '1 '
		else:
			Channel_str = '0 '
		MV_Number_str = str(MV_Numver_MIN)
		wfo_cmd = ADC_MV_SCAN_READ + Channel_str + MV_Number_str + ADC_SCAN_READ_gain
		self.wfo_act.WFO_setCmdAndValue(wfo_cmd, sample_time, acqu_time)

		self.wfo_act.WFO_runFlag = True
		self.thread1.started.connect(self.wfo_act.WFO_readData)
		self.thread1.start()

		self.top.ms.wf_out.start_btn.setEnabled(False)
		self.top.ms.wf_out.stop_btn.setEnabled(True)
		self.top.ms.wf_mon.mon_btn.setEnabled(False)
		self.top.ms.tic.run.setEnabled(False)

	def WFO_drawData(self, data):
		if self.top.ms.wf_out.poBtn2.isChecked():
			self.data = data * (-1)
		else:
			self.data = data

		self.top.pic.plot.ax.clear()
		self.top.pic.plot.ax.plot(self.data, color = 'blue', linestyle = '-', marker = '*')
		self.top.pic.plot.figure.canvas.draw()
		self.top.pic.plot.figure.canvas.flush_events()

	def WFO_StopBtn(self):
		#print("WFO stop")
		self.wfo_act.WFO_runFlag = False

	def WFO_Finish(self):
		self.thread1.quit()
		self.top.ms.wf_out.start_btn.setEnabled(self.SSH1_status)
		self.top.ms.wf_out.stop_btn.setEnabled(False)
		self.top.ms.wf_out.save_btn.setEnabled(True)
		self.top.ms.wf_mon.mon_btn.setEnabled(self.SSH2_status)
		self.top.ms.tic.run.setEnabled(self.SSH1_status)

	def WFO_SaveBtn(self):
		SaveFileName,_ = QFileDialog.getSaveFileName(self,
						"Save Data",
						"./" + OUTPUT_FILENAME,
						"Text Files (*.txt)")
		if (SaveFileName != ''):
			header = self.top.hk.FHedit.edit.text()
			self.SettingData[index_fileheader] = header
			fil2a.array1DtoTextFile(SETTING_FILENAME, self.SettingData, self.loggername)
			fil2a.array1DtoTextFile(SaveFileName, self.data, self.loggername, header)
			self.top.ms.wf_out.save_btn.setEnabled(False)

#Waveform Monitor
	def WFM_RunBtn(self):
		#print("WFM start")
		self.top.pic.setCurrentIndex(1)
		if self.top.ms.wf_mon.chBtn2.isChecked():
			trig_src_str = '1 '
		else:
			trig_src_str = '0 '

		sam_num = self.top.ms.wf_mon.sam_num.combo.currentIndex()
		sam_num_str = str(self.top.ms.wf_mon.sam_num_list[sam_num]) + ' '
		trig_level = float(self.top.ms.wf_mon.trig_level.spin.value()) / 1000.0
		gain = self.top.ms.wf_mon.gain.combo.currentIndex()
		wfm_cmd = ADC_SCAN_READ + trig_src_str + sam_num_str + str(trig_level) + " " + str(gain)
		self.wfm_act.WFM_setCmd(wfm_cmd)

		self.wfm_act.WFM_runFlag = True
		self.thread2.started.connect(self.wfm_act.WFM_readBinData)
		self.thread2.start()

		self.top.ms.wf_out.start_btn.setEnabled(False)
		self.top.ms.wf_mon.mon_btn.setEnabled(False)
		self.top.ms.wf_mon.stop_btn.setEnabled(True)
		self.top.ms.tic.run.setEnabled(False)

	def WFM_drawData(self, WFM_Bin_Data1, WFM_Bin_Data2):
		self.top.pic.plot2.ax.clear()
		self.top.pic.plot2.ax.plot(WFM_Bin_Data1, color = 'blue', linestyle = '-', marker = '*', label = 'CH1')
		self.top.pic.plot2.ax.plot(WFM_Bin_Data2, color = 'red', linestyle = '-', marker = '*', label = 'CH2')
		self.top.pic.plot2.ax.legend()
		self.top.pic.plot2.figure.canvas.draw()
		self.top.pic.plot2.figure.canvas.flush_events()

	def WFM_StopBtn(self):
		#print("WFM stop")
		self.wfm_act.WFM_runFlag = False

	def WFM_Finish(self):
		self.thread2.quit()
		self.top.ms.wf_out.start_btn.setEnabled(self.SSH1_status)
		self.top.ms.wf_mon.mon_btn.setEnabled(self.SSH2_status)
		self.top.ms.wf_mon.stop_btn.setEnabled(False)
		self.top.ms.tic.run.setEnabled(self.SSH1_status)

#Quadrupole Mass Filter
	def tic_RunBtn(self):
		self.top.pic.setCurrentIndex(2)
		select_path = QFileDialog.getExistingDirectory(self, "Save Raw Data", "./")
		header = self.top.hk.FHedit.edit.text()

		rolling = self.top.ms.tic.rolling.spin.value()
		dataPts = self.top.ms.tic.dataPts.spin.value()
		threshold = self.top.ms.tic.threshold.spin.value()
		width = self.top.ms.tic.width.spin.value()
		startMass = self.top.ms.tic.startMass.spin.value()
		stopMass = self.top.ms.tic.stopMass.spin.value()
		self.tic_act.setParam(rolling, dataPts, threshold, width, startMass, stopMass, select_path, header)

		radius = self.top.ms.tic.radius.spin.value()*0.01
		freq = self.top.ms.tic.freq.spin.value()*1000
		# self.tic_act.calVolt(radius, freq)
		cdc = self.top.ms.tic.cdc.spin.value()
		crf = self.top.ms.tic.crf.spin.value()
		self.tic_act.calVolt2(freq, cdc, crf)

		massMin = self.top.ms.tic.massMin.spin.value()
		massMax = self.top.ms.tic.massMax.spin.value()
		self.tic_act.genrateMass(massMin, massMax)

		self.SaveTICpreset(startMass, stopMass, massMin, massMax, radius, freq, rolling, dataPts, threshold, width, cdc, crf)

		self.tic_act.ticFlag = True
		self.thread3.started.connect(self.tic_act.ticRun)
		self.thread3.start()

		self.top.ms.wf_out.start_btn.setEnabled(False)
		self.top.ms.wf_mon.mon_btn.setEnabled(False)
		self.top.ms.tic.run.setEnabled(False)
		self.top.ms.tic.stop.setEnabled(True)

	def tic_drawData(self, data, tic, xic, index):
		self.tic = tic
		self.xic = xic
		# index_text = "Index = " + str(index)
		# self.top.ms.tic.run_index2.setText(index_text)
		self.top.ms.tic.run_index2.setText(str(index))
		self.top.pic.plot3.ax1.clear()
		self.top.pic.plot3.ax1.plot(tic, color = 'blue', linestyle = '-', label = 'tic')
		self.top.pic.plot3.ax1.plot(xic, color = 'red', linestyle = '-', label = 'xic')
		self.top.pic.plot3.ax1.set_xlabel("Time (s)")
		self.top.pic.plot3.ax1.legend()
		self.top.pic.plot3.ax2.clear()
		self.top.pic.plot3.ax2.plot(self.tic_act.mass_array, data[1], color = 'blue', linestyle = '-', marker = '*')
		self.top.pic.plot3.ax2.set_xlabel("m/z")
		self.top.pic.plot3.ax3.clear()
		self.top.pic.plot3.ax3.plot(self.tic_act.mass_array, data[2], color = 'green', linestyle = '-', marker = '*')
		self.top.pic.plot3.ax3.set_xlabel("m/z")
		self.top.pic.plot3.figure.canvas.draw()
		self.top.pic.plot3.figure.canvas.flush_events()

	def tic_StopBtn(self):
		self.tic_act.ticFlag = False

	def tic_Finish(self):
		self.thread3.quit()
		self.thread3.wait()
		self.top.ms.wf_out.start_btn.setEnabled(self.SSH1_status)
		self.top.ms.wf_mon.mon_btn.setEnabled(self.SSH2_status)
		self.top.ms.tic.run.setEnabled(self.SSH1_status)
		self.top.ms.tic.stop.setEnabled(False)
		self.top.ms.tic.save.setEnabled(True)

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


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

