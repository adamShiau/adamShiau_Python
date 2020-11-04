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
import QSS005_Widget2 as UI
import QSS005_Action2 as ACT
import numpy as np
#from screeninfo import get_monitors
import datetime

# monitor = get_monitors()
# monitor_string = str(monitor[0])
# monitor_info = monitor_string.split(', ')
# monitor_width = float(monitor_info[2][6:])
# monitor_height = float(monitor_info[3][7:])

HOST_NAME = "root"
HOST_PWD = "root"
HOST_PORT = 22

READOUT_FILENAME = "Signal_Read_Out.txt"

CONNECT_BIT_CMD = "cat /root/GRC_v4.bit > /dev/xdevcfg"

RESET_CYCLE_CMD = 	"/opt/redpitaya/bin/monitor 0x40200048 "
HOLD_CYCLE_CMD = 	"/opt/redpitaya/bin/monitor 0x4020004C "
INT_CYCLE_CMD = 	"/opt/redpitaya/bin/monitor 0x40200050 "

LIB_PATH = "LD_LIBRARY_PATH=/opt/quantaser/lib "
MOS_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./MOS "
WF_OUTPUT_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./CH1 "

MS1_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./MS1 "
ISO_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./ISOLATION "
MSMS_CMD = "LD_LIBRARY_PATH=/opt/quantaser/lib ./MSMS "

DAC_RATIO = 6.0/5000.0 #high voltage amplifier conversion Ratio
DAC_MAX = 5000

INIT_DATACOUNT = 10000

SCAN_SAMPLING_RATE = 33 # 1/ms

SAVE_FILE_CMD = " 1 "
ISO_OUT_FILE_CMD = "chirp_out.bin "
MSMS_OUT_FILE_CMD = "msms_out.bin "

XIC_ERROR_MSG1 = "The mass should be between "
XIC_ERROR_MSG2 = "\nPlease modify Xic Mass"

TEST_MODE = False

TITLE_TEXT = " Acdemic Sincica GRC Mass Spectrometer "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS005 V3.04 \n\n" + \
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
		self.actHK = ACT.qss005ActionHK(self.act.ssh, self.loggername)
		self.top = UI.mainWidget()

		self.gaugeTurnState = False

		self.ms1AccuSingle = np.empty(0)
		self.ms1AccuAll = np.empty(0)
		self.ms1AccuTime = np.empty(0)

		self.peak_num = 0
		self.mass = np.zeros(INIT_DATACOUNT)
		self.SSHstatus = False
		self.Timeoffset = 0

		self.mainUI()
		self.mainMenu()
		self.mainInit()
		self.linkFunction()
		self.setHKpreset()

	def mainUI(self):
		mainLayout = QGridLayout()
		#self.scorollerarea = QScrollArea()
		#self.scorollerarea.setWidget(self.top)
		self.setCentralWidget(QWidget(self))
		#mainLayout.addWidget(self.scorollerarea,0,0,1,1)
		mainLayout.addWidget(self.top,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)
	
	def mainMenu(self):
		mainMenu = self.menuBar()
		menu_about = QAction("&Version", self)
		menu_about.triggered.connect(self.aboutBox)
		aboutMenu = mainMenu.addMenu("&About")
		aboutMenu.addAction(menu_about)

	def mainInit(self):
		self.thread1 = QThread()
		self.thread1.started.connect(self.actHK.gauge_readData)
		self.actHK.moveToThread(self.thread1)
		self.actHK.gauge_update_text.connect(self.gaugeUpdateText)
		self.actHK.gauge_finished.connect(self.measClose)

		self.thread2 = QThread()
		self.thread2.started.connect(self.act.ms1single)
		self.thread3 = QThread()
		self.thread3.started.connect(self.act.ms1multiRun)
		self.act.moveToThread(self.thread2)
		self.act.ms1_update_array.connect(self.ms1_drawData)
		self.act.ms1_single_finished.connect(self.ms1Close)
		self.act.ms1_update_total_array.connect(self.ms1_drawTotalData)
		self.act.ms1_finished.connect(self.ms1BtnClose)

	def linkFunction(self):
		self.top.hk.net.btn.clicked.connect(self.sshConnectRun)
		self.top.hk.uart.gaugeTurn.clicked.connect(self.turnClick)
		self.top.hk.uart.gaugeMeas.clicked.connect(self.measClick)
		self.top.hk.dac.dac_combo.currentIndexChanged.connect(self.dacChange)
		self.top.hk.dac.setBtn.clicked.connect(self.dacOut)
		self.top.ms.run1_btn.clicked.connect(self.WFO_Ch1Run)
		self.top.ms.ch1_freq.spin.valueChanged.connect(self.WFO_Ch1Run)
		self.top.ms.ch1_amp.spin.valueChanged.connect(self.WFO_Ch1Run)
		self.top.ms.ch1_offset.spin.valueChanged.connect(self.WFO_Ch1Run)

		self.top.ms.scanSetBtn.clicked.connect(self.callScanDialog)
		self.top.ms.sysSetBtn.clicked.connect(self.callSysDialog)
		self.top.ms.ms1RunBtn.clicked.connect(lambda:self.ms1BtnRun(True))
		self.top.ms.ms1RunAllBtn.clicked.connect(self.ms1BtnRunAll)
		self.top.ms.ms1StopBtn.clicked.connect(self.ms1BtnStop)
		self.top.ms.ms1SaveBtn.clicked.connect(self.ms1BtnSave)
		self.top.ms.ms1ResetBtn.clicked.connect(self.ms1BtnReset)

		self.top.ms.currDataBtn.clicked.connect(self.setCurrData)
		self.top.ms.loadDataBtn.clicked.connect(self.loadData)
		self.top.ms.threshold.spin.valueChanged.connect(self.ShowThreshold)
		self.top.ms.noise_width.spin.valueChanged.connect(self.NoiseChange)
		self.top.ms.caFindBtn.clicked.connect(lambda:self.caFindPeak(True))
		self.top.ms.caSetBtn.clicked.connect(self.calibrCallDialog)
		self.top.ms.fitBtn.clicked.connect(self.fitting)

		self.top.ms.isoSetBtn.clicked.connect(self.isoCallDialog)

	def setHKpreset(self):
		self.top.hk.net.IP.setText(self.act.hkPreset[0])
		self.top.hk.dac.setVolt.setText(str(self.act.hkPreset[1]))

	def addAccesoryFlag(self, loggername):
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.WARNING, "log.txt")

#Connection
	def sshConnectRun(self):
		ip = self.top.hk.net.IP.text()
		host = "rp-"+str(ip)+".local"
		self.SSHstatus = self.act.sshConnect(host, HOST_PORT, HOST_NAME, HOST_PWD)
		if self.SSHstatus:
			self.act.ssh.sendCmd(CONNECT_BIT_CMD, False, 1)

			for i in range(0, 10):
				dac_cmd = LIB_PATH + "./" + str(self.top.hk.dac.dac_list[i]) + ' 0'
				self.act.ssh.sendCmd(dac_cmd)

			self.top.hk.net.SetConnectText(Qt.black, "Connection build", False)
			self.setEnableButton()
			self.act.hkPreset[0] = ip
			self.act.savePreset(0)
		else:
			self.top.hk.net.SetConnectText(Qt.red, "SSH connect failed", True)

	def setEnableButton(self):
		# self.top.hk.net.connectBtn.setEnabled(False)
		self.top.hk.uart.gaugeTurn.setEnabled(self.SSHstatus)
		self.top.hk.dac.setBtn.setEnabled(self.SSHstatus)
		self.top.ms.run1_btn.setEnabled(self.SSHstatus)
		self.top.ms.ms1RunBtn.setEnabled(self.SSHstatus)
		self.top.ms.ms1RunAllBtn.setEnabled(self.SSHstatus)

#uartBlock
	def turnClick(self):
		if self.gaugeTurnState == False:
			self.gaugeTurnState = True
			self.top.hk.uart.gaugeTurn.setText("Turn Off")
			self.top.hk.uart.gaugeMeas.setEnabled(self.SSHstatus)
			cmd = MOS_CMD + "1 0 0 0"
			print("Turn On gauge")
		else:
			self.gaugeTurnState = False
			self.top.hk.uart.gaugeTurn.setText("Turn On")
			self.top.hk.uart.gaugeMeas.setEnabled(False)
			cmd = MOS_CMD + "0 0 0 0"
			print("Turn Off gauge")
		self.act.ssh.sendCmd(cmd)
		self.top.hk.uart.gaugeTurn.show()

	def gaugeUpdateText(self, output):
		if (self.actHK.gauge_runFlag):
			self.top.hk.uart.gaugeOut.setText(output)
			self.top.hk.uart.gaugeOut.show()

	def measClick(self):
		if (self.actHK.gauge_runFlag == False):
			#print("meas start")
			self.actHK.gauge_runFlag = True
			self.measStart()
		else:
			#print("meas stop")
			self.actHK.gauge_runFlag = False

	def measStart(self):
		self.top.hk.uart.gaugeMeas.setText("Stop")
		self.top.hk.uart.gaugeMeas.show()
		self.top.hk.uart.gaugeTurn.setEnabled(False)
		# self.thread1.started.connect(self.actHK.gauge_readData)
		self.thread1.start()
		print("Start Measure")

	def measClose(self):
		self.thread1.quit()
		self.thread1.wait()
		self.top.hk.uart.gaugeMeas.setText("Measure")
		self.top.hk.uart.gaugeMeas.show()
		self.top.hk.uart.gaugeTurn.setEnabled(self.SSHstatus)
		print("Stop Measure")

#dacSubBlock
	def dacChange(self):
		dac_index = self.top.hk.dac.dac_combo.currentIndex()
		self.top.hk.dac.setVolt.setText(str(self.act.hkPreset[dac_index+1]))

	def dacOut(self):
		dac_index = self.top.hk.dac.dac_combo.currentIndex()
		dac_channel = self.top.hk.dac.dac_combo.currentText()
		dac_value = self.top.hk.dac.setVolt.text()

		if (float(dac_value) > DAC_MAX):
			self.top.hk.dac.setVolt.setText(str(DAC_MAX))
			dac_value = DAC_MAX
		dac_out = float(dac_value) * DAC_RATIO * 1000
		#LD_LIBRARY_PATH=/opt/quantaser/lib ./DAC 1 6.7
		cmd = LIB_PATH + "./" + str(dac_channel) + " " + str(dac_out)
		# print(cmd)
		self.act.ssh.sendCmd(cmd)
		self.top.hk.dac.text2.setText(str(dac_out))
		self.act.hkPreset[dac_index+1] = float(dac_value)
		self.act.savePreset(0)

#Preparation
	def WFO_Ch1Run(self):
		freq = self.top.ms.ch1_freq.spin.value() 
		amp = self.top.ms.ch1_amp.spin.value()
		offset = self.top.ms.ch1_offset.spin.value()

		cmd = WF_OUTPUT_CMD + str(freq) + " " + str(amp) + " " + str(offset)
		self.act.ssh.sendCmd(cmd, True)
		#output = stdout.readline()
		# print(output)

#ms1
	def callScanDialog(self):
		# print(self.act.scanPreset)
		scanDialog = UI.scanDialog(self.act.scanPreset)
		self.act.scanPreset = scanDialog.getParameter(self.act.scanPreset)
		self.act.savePreset(1)

	def callSysDialog(self):
		# print(self.act.sysPreset)
		sysDialog = UI.sysDialog(self.act.sysPreset)
		self.act.sysPreset = sysDialog.getParameter(self.act.sysPreset)
		self.act.savePreset(2)

	def getScanPreset(self):
		self.ch1_freq = int(self.act.scanPreset[0])
		self.scan_period = int(self.act.scanPreset[1])
		self.ch1_trapping_amp = int(self.act.scanPreset[2])
		self.ch1_ramp = int(self.act.scanPreset[3])
		self.ch1_final_amp = int(self.act.scanPreset[4])
		self.ch1_offset = int(self.act.scanPreset[5])

		self.ttl_duration = int(self.act.scanPreset[6])
		self.damp_duration = int(self.act.scanPreset[7])

		self.ms1_chirp_amp = int(self.act.scanPreset[8])
		self.iso_chirp_amp = int(self.act.scanPreset[15])/10
		self.ch2_freq_factor = float(self.act.scanPreset[9])
		self.ch2_final_freq = int(self.act.scanPreset[10])

		self.MSMS_t1 = int(self.act.scanPreset[11])-30
		# self.MSMS_time = int(self.act.scanPreset[12])
		self.MSMS_t2 = int(self.act.scanPreset[12])-50
		self.msms_amp = int(self.act.scanPreset[13])/10
		self.delay_time = int(self.act.scanPreset[14])

		self.ramp_pts = self.scan_period * SCAN_SAMPLING_RATE
		self.ramp_step = (self.ch1_ramp - self.ch1_trapping_amp) / (self.ramp_pts - 1)

	def getSysPreset(self):
		self.level = int(self.act.sysPreset[0])
		self.threshold = float(self.act.sysPreset[1])
		self.noise_width = int(self.act.sysPreset[2])
		self.xicMassCenter = int(self.act.sysPreset[3])
		self.xicMassRange = float(self.act.sysPreset[4])
		self.isoMassCenter = int(self.act.sysPreset[5])
		self.isoMassRange = float(self.act.sysPreset[6])
		self.rfVolGain = int(self.act.sysPreset[7])
		self.r0 = float(self.act.sysPreset[8])
		self.z0 = float(self.act.sysPreset[9])
		self.minMass = self.xicMassCenter - self.xicMassRange
		self.maxMass = self.xicMassCenter + self.xicMassRange

	def getPreset(self):
		self.getScanPreset()
		self.getSysPreset()

		self.adc_offset = int(self.act.engSet[0])
		self.adc_gain_p = int(self.act.engSet[1])
		self.adc_gain_n = int(self.act.engSet[2])

		if (not self.top.ms.ms1.isChecked()):
			self.act.checkParamChanged(self.ch2_freq_factor, self.ch2_final_freq, self.isoMassCenter, self.isoMassRange, \
			self.ch1_trapping_amp, self.rfVolGain, self.ch1_freq, self.r0, self.z0, self.iso_chirp_amp, self.msms_amp)

	def ms1Cmd(self):
		command = MS1_CMD \
					+ str(self.ch1_freq * 1000) + ' '\
					+ str(self.ramp_pts) + ' '\
					+ str(self.ramp_step)+ ' '\
					+ str(self.ch1_trapping_amp) + ' '\
					+ str(self.ch1_final_amp) + ' '\
					+ str(self.ms1_chirp_amp) + ' '\
					+ str(self.ch2_freq_factor) + ' '\
					+ str(self.ch2_final_freq) \
					+ SAVE_FILE_CMD \
					+ str(self.ttl_duration) + ' '\
					+ str(self.damp_duration) + ' '\
					+ str(self.adc_offset) + ' '\
					+ str(self.ch1_offset) + ' '\
					+ str(self.adc_gain_p) + ' '\
					+ str(self.adc_gain_n) + ' '\
					+ str(self.delay_time)
		print("ms1 cmd = " + command)
		return command

	def isoCmd(self):
		command = ISO_CMD \
					+ str(self.ch1_freq * 1000) + ' '\
					+ str(self.ttl_duration) + ' '\
					+ str(self.damp_duration) + ' '\
					+ str(self.ch1_trapping_amp) + ' '\
					+ str(self.ramp_step)+ ' '\
					+ str(self.ramp_pts) + ' '\
					+ str(self.ch1_final_amp) + ' '\
					+ str(self.ch1_offset) + ' '\
					+ str(self.adc_offset) + ' '\
					+ str(self.adc_gain_p) + ' '\
					+ str(self.adc_gain_n) \
					+ SAVE_FILE_CMD \
					+ ISO_OUT_FILE_CMD \
					+ str(self.ch2_freq_factor) + ' '\
					+ str(self.delay_time)
		print("iso cmd = " + command)
		return command

	def msmsCmd(self):
		command = MSMS_CMD \
					+ str(self.ch1_freq * 1000) + ' '\
					+ str(self.ttl_duration) + ' '\
					+ str(self.damp_duration) + ' '\
					+ str(self.ch1_trapping_amp) + ' '\
					+ MSMS_OUT_FILE_CMD \
					+ str(self.MSMS_t1) + ' '\
					+ str(self.MSMS_t2) + ' '\
					+ str(self.ramp_step) + ' '\
					+ str(self.ramp_pts) + ' '\
					+ str(self.ch1_final_amp) + ' '\
					+ str(self.ch1_offset) + ' '\
					+ str(self.adc_offset) + ' '\
					+ str(self.adc_gain_p) + ' '\
					+ str(self.adc_gain_n) \
					+ SAVE_FILE_CMD \
					+ ISO_OUT_FILE_CMD \
					+ str(self.ch2_freq_factor) + ' '\
					+ str(self.delay_time)
		print("msms cmd = " + command)
		return command

	def singleCmd(self):
		self.getPreset()
		# self.act.chirp_amp = self.ch2_chirp_amp/1000

		if self.top.ms.msms.isChecked():
			command = self.msmsCmd()
		elif self.top.ms.isolation.isChecked():
			command = self.isoCmd()
		else: # default ms1
			command = self.ms1Cmd()

		cmd_delay_time = float(self.scan_period + self.ttl_duration + 32) / 1000 * 1.5
		# cmd_delay_time = float(self.ttl_duration + 38 + self.MSMS_t1 + 38 + self.MSMS_t2 + 50 + self.scan_period + self.delay_time) / 1000
		# print(delay_time)
		# getFile_delay_time = float(self.scan_period) / 1000
		getFile_delay_time = cmd_delay_time

		noise_filter = False
		if (self.top.ms.checkNoise.isChecked()):
			noise_filter = True

		# print("main : " + str(self.ramp_pts))
		self.act.pts = self.ramp_pts
		self.act.ms1_setCmdAndValue(command, cmd_delay_time, self.top.ms.ms1.isChecked(), getFile_delay_time)
		self.act.ms1_setNoiseAndLevel(noise_filter, self.level)
		self.act.setQss005header(self.top.hk.FHedit.edit.text())
		self.act.setPolarity(self.top.ms.checkNegative.isChecked())

	def checkXicMass(self):
		num = len(self.act.xplotdata)
		minMass = self.act.xplotdata[0]
		maxMass = self.act.xplotdata[num-1]

		if (self.minMass < minMass) or (self.maxMass >  maxMass):
			maxMass_str = "%2.2f" % maxMass
			minMass_str = "%2.2f" % minMass
			msg = XIC_ERROR_MSG1 + minMass_str + " and " + maxMass_str + XIC_ERROR_MSG2
			msg = "Error!\n" + msg
			return False, msg
		else:
			msg = "No Error"
			return True, msg

	def ms1BtnRun(self, single = True):
		self.singleCmd()

		result1, msg1 = self.checkXicMass()
		if (result1 == False):
			self.errorBox(msg1)
			return

		if (not self.top.ms.ms1.isChecked()):
			result, msg = self.act.checkISOinit()
			if (result == False):
				self.errorBox(msg)
				return

		self.top.ms.ms1RunBtn.setEnabled(False)
		self.top.ms.ms1RunAllBtn.setEnabled(False)
		self.top.ms.ms1SaveBtn.setEnabled(False)
		self.top.ms.ms1ResetBtn.setEnabled(False)

		self.act.ms1singleRunFlag = True
		self.thread2.start()
		# print("ms1 start")

	def ms1_drawData(self, data):
		self.act.currData = data
		self.mass = self.act.xplotdata[0:len(self.act.currData)]
		self.top.tabPlot.plot1.ax1.clear()
		self.top.tabPlot.plot1.ax1.set_ylabel("Voltage (V)")

		if (not TEST_MODE):	# real data output
			self.top.tabPlot.plot1.ax1.plot(self.mass, self.act.currData, color = 'blue', linestyle = '-', marker = '*')
		elif (self.top.ms.ms1.isChecked()):
			self.top.tabPlot.plot1.ax1.plot(self.act.currData, color = 'blue', linestyle = '-', marker = '*')
		else:	# test data output
			self.top.tabPlot.plot1.ax1.plot(self.act.msmsOut, color = 'blue')
			self.top.tabPlot.plot1.ax1.plot(self.act.isoChirpOut, color ='green')
			self.top.tabPlot.plot1.ax2.plot(np.abs(np.fft.fft(self.act.msmsOut)), color = 'blue')
			self.top.tabPlot.plot1.ax2.plot(np.abs(np.fft.fft(self.act.isoChirpOut)), color = 'green')

		self.top.tabPlot.plot1.figure.canvas.draw()
		self.top.tabPlot.plot1.figure.canvas.flush_events()

	def ms1Stop(self):
		self.act.ms1singleRunFlag = False

	def ms1Close(self):
		self.thread2.quit()
		self.thread2.wait()
		self.top.ms.ms1RunBtn.setEnabled(self.SSHstatus)
		self.top.ms.ms1RunAllBtn.setEnabled(self.SSHstatus)
		self.top.ms.ms1StopBtn.setEnabled(False)
		self.top.ms.ms1SaveBtn.setEnabled(self.SSHstatus)
		self.top.ms.ms1ResetBtn.setEnabled(self.SSHstatus)
		self.top.ms.currDataBtn.setEnabled(self.SSHstatus)
		# print("ms1 Close")

	def ms1BtnRunAll(self):
		#if (self.top.ms.checkSaveRaw.isChecked()):
		select_path = QFileDialog.getExistingDirectory(self, "Save Raw Data", "./")
		if (self.top.ms.checkTic.isChecked()):
			self.ms1BtnReset()
		self.singleCmd()
		self.act.ms1_setRowAndPath(select_path)
		self.act.runLoop = self.top.ms.runLoop.spin.value()

		result1, msg1 = self.checkXicMass()
		if (result1 == False):
			self.errorBox(msg1)
			return

		if (not self.top.ms.ms1.isChecked()):
			result, msg = self.act.checkISOinit()
			if (result == False):
				self.errorBox(msg)
				return

		self.top.ms.ms1RunBtn.setEnabled(False)
		self.top.ms.ms1RunAllBtn.setEnabled(False)
		self.top.ms.ms1StopBtn.setEnabled(True)
		self.top.ms.ms1SaveBtn.setEnabled(False)
		self.top.ms.ms1ResetBtn.setEnabled(False)

		self.act.ms1runFlag = True
		self.Timeoffset = time.time()
		# self.thread2.finished.connect(self.ms1BtnStop)
		self.thread3.start()
		# print("all start")

	def ms1_drawTotalData(self, single, data):
		# num = len(single)
		# print("num = " + str(num))
		self.ms1_drawData(single)
		self.act.currData = data
		self.mass = self.act.xplotdata[0:len(self.act.currData)]
		# indexStr = "Run Index = " + str(self.act.rawfileindex)
		indexStr = str(self.act.rawfileindex)
		self.top.ms.ms1Index.setText(indexStr)
		self.top.tabPlot.plot1.ax2.clear()
		self.top.tabPlot.plot1.ax2.set_xlabel("Mass")
		self.top.tabPlot.plot1.ax2.set_ylabel("Voltage (V)")
		self.top.tabPlot.plot1.ax2.plot(self.mass, self.act.currData, color = 'red', linestyle = '-', marker = '*')
		self.top.tabPlot.plot1.figure.canvas.draw()
		self.top.tabPlot.plot1.figure.canvas.flush_events()

		# new added accu fuction
		if self.top.ms.checkTic.isChecked():
			self.caFindPeak(False)

			if (self.peak_num > 0):	
				# print(self.act.rawfileindex)
				t_diff = time.time()-self.Timeoffset
				# print("t_diff = " + str(t_diff))
				self.ms1AccuTime = np.append(self.ms1AccuTime,t_diff)

				temp = np.array(self.analist).transpose()
				
				self.top.tabPlot.plot2.ax1.clear()
				self.top.tabPlot.plot2.ax1.set_ylabel("Arbiary Uint")
				self.top.tabPlot.plot2.ax2.clear()
				self.top.tabPlot.plot2.ax2.set_xlabel("Time (s)")
				self.top.tabPlot.plot2.ax2.set_ylabel("Arbiary Uint")
				self.ms1AccuAll = np.append(self.ms1AccuAll,sum(temp[1]))
				singletemp = 0
				for i in range(0, self.peak_num):
					if (temp[0][i] > self.minMass) and (temp[0][i] < self.maxMass):
						singletemp = singletemp + temp[1][i]
				self.ms1AccuSingle = np.append(self.ms1AccuSingle, singletemp)
				self.top.tabPlot.plot2.ax1.plot(self.ms1AccuTime, self.ms1AccuAll, color ='blue')
				self.top.tabPlot.plot2.ax2.plot(self.ms1AccuTime, self.ms1AccuSingle, color ='green')
				self.top.tabPlot.plot2.figure.canvas.draw()
				self.top.tabPlot.plot2.figure.canvas.flush_events()

	def ms1BtnStop(self):
		self.act.ms1runFlag = False

	def ms1BtnClose(self):
		self.thread3.quit()
		self.thread3.wait()
		self.top.ms.ms1RunBtn.setEnabled(self.SSHstatus)
		self.top.ms.ms1RunAllBtn.setEnabled(self.SSHstatus)
		self.top.ms.ms1StopBtn.setEnabled(False)
		self.top.ms.ms1SaveBtn.setEnabled(self.SSHstatus)
		self.top.ms.ms1ResetBtn.setEnabled(self.SSHstatus)
		self.top.ms.currDataBtn.setEnabled(self.SSHstatus)
		# print("all close")

	def ms1BtnSave(self):
		SaveFileName,_ = QFileDialog.getSaveFileName(self, "Save Signal Data", READOUT_FILENAME, "Text Files (*.txt)")
		if (SaveFileName != ''):
			curr_time = datetime.datetime.now()
			fileheader1 = self.top.hk.FHedit.edit.text()+"\n"+str(curr_time)+ "\n" +"mass, signal"
			fileheader2 = self.top.hk.FHedit.edit.text()+"\n"+str(curr_time)+ "\n" +"time, signal"
			tempdata = np.array([self.mass, self.act.currData], np.float64)
			tempdata = np.transpose(tempdata)
			fil2a.list2DtoTextFile(SaveFileName, tempdata,",",self.loggername, fileheader1)
			if self.top.ms.checkTic.isChecked():
				tempdata = np.array([self.ms1AccuTime, self.ms1AccuAll], np.float64)
				tempdata = np.transpose(tempdata)
				fil2a.list2DtoTextFile(SaveFileName[0:-4]+"_TIC_All.txt", tempdata,",", self.loggername, fileheader2)
				tempdata = np.array([self.ms1AccuTime, self.ms1AccuSingle], np.float64)
				tempdata = np.transpose(tempdata)
				fil2a.list2DtoTextFile(SaveFileName[0:-4]+"_TIC_Sing.txt", tempdata,",", self.loggername, fileheader2)
			
	def ms1BtnReset(self):
		self.act.resetIndex()
		self.ms1AccuSingle = np.empty(0)
		self.ms1AccuAll = np.empty(0)
		self.ms1AccuTime = np.empty(0)
		# self.top.ms.ms1Index.setText("Run Index = 0")
		self.top.ms.ms1Index.setText("0")

#Calibration
	def setCurrData(self):
		currlen = len(self.act.currData)
		self.mass = self.act.xplotdata[0:currlen]
		self.top.ms.caFindBtn.setEnabled(True)

		data2max = max(self.act.currData)
		data2min = min(self.act.currData)
		self.top.ms.threshold.spin.setRange(data2min, data2max)
		self.DrawAnaPlot()

	def loadData(self):
		OpenFileName,_ = QFileDialog.getOpenFileName(self,"Load Signal Data","","Text Files (*.txt)")
		if (OpenFileName != ''):
			self.mass, self.act.currData = fil2a.TexTFileto2ColumeArray(OpenFileName, ",", self.loggername, 3)
		self.act.updateCalMass()
		self.setCurrData()

	def DrawAnaPlot(self):
		self.top.tabPlot.plot1.ax2.clear()
		self.top.tabPlot.plot1.ax2.set_xlabel("Mass")
		self.top.tabPlot.plot1.ax2.set_ylabel("Voltage (V)")
		#self.top.tabPlot.plot1.ax2.plot(self.act.currData, color = 'g', linestyle = '-', marker = '*')
		self.top.tabPlot.plot1.ax2.plot(self.mass, self.act.currData, color = 'g', linestyle = '-', marker = '*')
		self.top.tabPlot.plot1.figure.canvas.draw()
		self.top.tabPlot.plot1.figure.canvas.flush_events()

	def ShowThreshold(self):
		value = float(self.top.ms.threshold.spin.value())
		self.top.tabPlot.plot1.ax2.clear()
		self.top.tabPlot.plot1.ax2.set_xlabel("Mass")
		self.top.tabPlot.plot1.ax2.set_ylabel("Voltage (V)")
		#self.top.tabPlot.plot1.ax2.plot(self.act.currData, color = 'g', linestyle = '-', marker = '*')
		self.top.tabPlot.plot1.ax2.plot(self.mass, self.act.currData, color = 'g', linestyle = '-', marker = '*')
		self.top.tabPlot.plot1.ax2.axhline(y = value, color = 'r')
		self.top.tabPlot.plot1.figure.canvas.draw()
		self.top.tabPlot.plot1.figure.canvas.flush_events()
		self.top.ms.caFindBtn.setEnabled(True)

	def NoiseChange(self):
		self.top.ms.caFindBtn.setEnabled(True)

	def caFindPeak(self,calib):
		if calib:
			value1 = float(self.top.ms.threshold.spin.value())
			value2 = int(self.top.ms.noise_width.spin.value())
		else:
			value1 = self.threshold
			value2 = self.noise_width
		peaks = self.act.calibra_findPeak(value1, value2, calib)
		self.peak_num = len(peaks)
		# print(peaks)
		# print("self.peak_num = " + str(self.peak_num))

		self.analist = []
		for index in peaks:
			#if index <=len(self.mass):
			xvalue = self.act.xplotdata[index]
			if calib:
				yvalue = self.act.currData[index]
			else:
				yvalue = self.act.singleData[index]
			self.analist.append([xvalue, yvalue])

		for i in range(0, self.peak_num):
			xvalue = self.analist[i][0]
			yvalue = self.analist[i][1]
			if calib:
				self.top.tabPlot.plot1.ax2.text(xvalue, yvalue, "Peak" + str(i+1), fontsize = 12, color = 'r')
				self.top.ms.caFindBtn.setEnabled(False)
				self.top.ms.caSetBtn.setEnabled(True)
			else:
				self.top.tabPlot.plot1.ax1.text(xvalue, yvalue, str(i+1)+":"+str(yvalue), fontsize = 7, color ='k')
		
		self.top.tabPlot.plot1.figure.canvas.draw()
		self.top.tabPlot.plot1.figure.canvas.flush_events()

	def calibrCallDialog(self):
		setPeaks = UI.SetPeakDialog(self.peak_num, self.loggername)
		self.calbIndexData = []
		self.calbIndexData = setPeaks.getParameter(self.peak_num, self.loggername)
		if (len(self.calbIndexData) > 0):
			self.top.ms.fitBtn.setEnabled(True)

	def fitting(self):
		self.act.calibra_curveFit(self.calbIndexData)
		self.act.updateCalMass()
		self.act.savePreset(3)
		currlen = len(self.act.currData)
		self.mass = self.act.xplotdata[0:currlen]
		self.DrawAnaPlot()


#Isolation
	def isoCallDialog(self):
		a = self.SetPeakDialog.getParameter()
		print(a)

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	def errorBox(self, msg):
		msgBox = QMessageBox()
		msgBox.about(self, "Message", msg)

	def closeEvent(self, event):
		# print("window close")
		self.actHK.gauge_runFlag = False
		self.ms1BtnStop()
		self.ms1Stop()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

