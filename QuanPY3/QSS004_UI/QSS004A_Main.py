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
import QSS004A_Widget as UI
import QSS004A_Action as ACT
import numpy as np
import datetime

monitor_width = 1920
monitor_height = 1080

MAIN_W = int(monitor_width*0.8)
MAIN_H = int(monitor_height*0.8)


#Preset File Setting
IDX_IP = 0
IDX_HV_START = 1
IDX_HV_STEP = 2
IDX_HV_LOOPS = 3
IDX_HV_BKPTS = 4
IDX_HV_OFFSET = 5
IDX_ADC_LOOPS = 6
IDX_HV_DELAY = 7
IDX_HV_FILTER = 8

IDX_DC_FIX = 9
IDX_DC_ESI = 10
IDX_DC_FAN = 11
IDX_ADC_CH = 12
IDX_ADC_PO = 13
IDX_ADC_AVG = 14
IDX_ADC_TIMES = 15
IDX_MASS_CENTER = 16
IDX_MASS_RANGE = 17
IDX_THRESHOLD = 18
IDX_WIDTH = 19
MAX_IDX = 20

SETTING_FILEPATH = "set"
PRESET_FILE_NAME = "set/settingA.txt"
READOUT_FILENAME = "Signal_Read_Out.txt"
ANALYSIS_FILENAME = "Data_Analysis.txt"

TITLE_TEXT = " Acdemic Sincica GRC Mass Spectrometer "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS004A V3.04 \n\n" + \
" Copyright @ 2020 TAIP \n" + \
" Maintain by Quantaser Photonics Co. Ltd "

class scanParam():
	def __init__(self):
		self.loggername = "Total"
		self.ip = "hostname"

		self.start = 1000
		self.step = 200
		self.loops = 1
		self.scanBkWd = 0
		self.offset = 0
		self.max_run_loops = 1
		self.delay = 100
		self.filterFreq = 1

		self.dc_fixed = 0
		self.dc_esi = 0
		self.dc_fan = 0

		self.channel_str = '0 '
		self.adc_pority = 1
		self.mv_avg_num = 50
		self.avg_time = 1

		self.xic_center = 100
		self.xic_delta = 1
		self.ana_height = 0
		self.ana_width = 1

		self.xicMode = False
		self.cutFreq = 0.7
		self.filter = False

	def loadPresetFile(self):
		if not os.path.isdir(SETTING_FILEPATH):
			os.mkdir(SETTING_FILEPATH)
			self.savePresetFile()
		elif not os.path.exists(PRESET_FILE_NAME):
			self.savePresetFile()
		else:
			data = fil2a.TexTFileto1DList(PRESET_FILE_NAME,self.loggername)
			if (len(data) != MAX_IDX):
				self.savePresetFile()
			else:
				self.ip = data[IDX_IP]

				self.start = int(data[IDX_HV_START])
				self.step = float(data[IDX_HV_STEP])
				self.loops = int(data[IDX_HV_LOOPS])
				self.scanBkWd = int(data[IDX_HV_BKPTS])
				self.offset = int(data[IDX_HV_OFFSET])
				self.max_run_loops = int(data[IDX_ADC_LOOPS])
				self.delay = int(data[IDX_HV_DELAY])
				self.filterFreq = int(data[IDX_HV_FILTER])

				self.dc_fixed = int(data[IDX_DC_FIX])
				self.dc_esi = int(data[IDX_DC_ESI])
				self.dc_fan = int(data[IDX_DC_FAN])

				self.channel_str = data[IDX_ADC_CH]
				self.adc_pority = int(data[IDX_ADC_PO])
				self.mv_avg_num = int(data[IDX_ADC_AVG])
				self.avg_time = int(data[IDX_ADC_TIMES])

				self.xic_center = int(data[IDX_MASS_CENTER])
				self.xic_delta = float(data[IDX_MASS_RANGE])
				self.ana_height = int(data[IDX_THRESHOLD])
				self.ana_width = int(data[IDX_WIDTH])

	def savePresetFile(self):
		data = [0]*MAX_IDX
		data[IDX_IP] = self.ip

		data[IDX_HV_START] = self.start
		data[IDX_HV_STEP] = self.step
		data[IDX_HV_LOOPS] = self.loops
		data[IDX_HV_BKPTS] = self.scanBkWd
		data[IDX_HV_OFFSET] = self.offset
		data[IDX_ADC_LOOPS] = self.max_run_loops
		data[IDX_HV_DELAY] = self.delay
		data[IDX_HV_FILTER] = self.filterFreq

		data[IDX_DC_FIX] = self.dc_fixed
		data[IDX_DC_ESI] = self.dc_esi
		data[IDX_DC_FAN] = self.dc_fan

		data[IDX_ADC_CH] = self.channel_str
		data[IDX_ADC_PO] = self.adc_pority
		data[IDX_ADC_AVG] = self.mv_avg_num
		data[IDX_ADC_TIMES] = self.avg_time

		data[IDX_MASS_CENTER] = self.xic_center
		data[IDX_MASS_RANGE] = self.xic_delta
		data[IDX_THRESHOLD] = self.ana_height
		data[IDX_WIDTH] = self.ana_width

		fil2a.array1DtoTextFile(PRESET_FILE_NAME, data, self.loggername)

class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.resize(MAIN_W, MAIN_H)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger
		self.act = ACT.qss004Action(self.loggername)
		self.fanact = ACT.qss004Action2(self.act.COM, self.loggername)
		self.top = UI.mainWidget()
		#self.top.setMinimumSize(TOP_W, TOP_H)
		self.thread1 = QThread()
		self.thread2 = QThread()
		self.act.moveToThread(self.thread1)
		self.fanact.moveToThread(self.thread2)
		self.thread1.started.connect(lambda:self.act.VoltageOut(self.scanFlag,self.scanParam))
		self.thread2.started.connect(self.fanact.fanQuerry)
		self.act.update_text.connect(self.updateText)
		# self.act.update_array.connect(self.PlotData)
		self.act.update_array_filter.connect(self.PlotData)
		self.act.update_xic.connect(self.PlotXicData)
		self.act.update_index.connect(self.UpdateAccuIndex)
		self.act.finished.connect(self.CloseThread)
		self.fanact.update_fan.connect(self.updateFan)
		self.fanact.finished.connect(self.CloseThread2)

		self.mainUI()
		self.mainMenu()
		self.mainInit()
		self.linkFunction()

	def mainUI(self):
		mainLayout = QGridLayout()
		#self.scorollerarea = QScrollArea()
		#self.scorollerarea.setWidget(self.top)
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.top)
		self.centralWidget().setLayout(mainLayout)
	
	def mainMenu(self):
		mainMenu = self.menuBar()
		menu_about = QAction("&Version", self)
		menu_about.triggered.connect(self.aboutBox)
		aboutMenu = mainMenu.addMenu("&About")
		aboutMenu.addAction(menu_about)

	def mainInit(self):
		self.ConnectRun()
		self.scanFlag = False
		self.scanParam = scanParam()
		self.scanParam.loadPresetFile()
		self.LoadPreset()
		self.preFanFlag = False
	
	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")

	def linkFunction(self):
		self.top.comport.btn.clicked.connect(self.ConnectRun)
		# self.top.tabAll.DCset.V1_Btn.clicked.connect(self.setFixedVolt)
		self.top.tabAll.DCset.V2_Btn.clicked.connect(self.setESI)  
		self.top.tabAll.Fan.FanBtn.clicked.connect(self.setFan)
		self.top.tabAll.HVscan.turnoff.clicked.connect(self.SetAllDacZero)
		self.top.tabAll.Analysis.LoadBtn.clicked.connect(self.LoadAnaData)
		self.top.tabAll.Analysis.CurrBtn.clicked.connect(self.UseCurrData)
		self.top.tabAll.Analysis.AnaBtn.clicked.connect(self.FinkPeakBtn)
		self.top.tabAll.Analysis.SaveBtn.clicked.connect(self.SaveAnaData)
		self.top.tabAll.Analysis.Threshold.spin.valueChanged.connect(self.ShowThreshold)
		self.top.tabAll.Analysis.Width.spin.valueChanged.connect(self.NoiseChange)
		#self.top.resetBtn.clicked.connect(self.resetBtn)
		self.top.DCmode.clicked.connect(self.DCmodeBtn)
		self.top.startScan.clicked.connect(self.ScanBtn)
		self.top.stop.clicked.connect(self.StopBtn)
		self.top.Signal.SaveDataBtn.clicked.connect(self.SaveAvgData)

	def LoadPreset(self):
		self.top.tabAll.HVscan.StartVoltage.spin.setValue(int(self.scanParam.start))
		self.top.tabAll.HVscan.VoltageStep.spin.setValue(float(self.scanParam.step))
		self.top.tabAll.HVscan.Loop.spin.setValue(int(self.scanParam.loops))
		self.top.tabAll.HVscan.Back.spin.setValue(int(self.scanParam.scanBkWd))
		self.top.tabAll.HVscan.offset.spin.setValue(int(self.scanParam.offset))
		self.top.tabAll.HVscan.Run_loop.spin.setValue(int(self.scanParam.max_run_loops))
		self.top.tabAll.HVscan.delay.spin.setValue(int(self.scanParam.delay))
		self.top.tabAll.HVscan.filterFreq.spin.setValue(int(self.scanParam.filterFreq))

		self.top.tabAll.DCset.DC_Voltage1.spin.setValue(int(self.scanParam.dc_fixed))
		self.top.tabAll.DCset.DC_Voltage2.spin.setValue(int(self.scanParam.dc_esi))
		self.top.tabAll.Fan.Fan_Speed.spin.setValue(int(self.scanParam.dc_fan))

		if (self.scanParam.adc_pority == -1):
			self.top.tabAll.DataSampling.poBtn2.setChecked(True)
		else:
			self.top.tabAll.DataSampling.poBtn1.setChecked(True)

		self.top.tabAll.DataSampling.AVG_time.spin.setValue(int(self.scanParam.avg_time))

		self.top.tabAll.TicXic.xicMassCenter.spin.setValue(int(self.scanParam.xic_center))
		self.top.tabAll.TicXic.xicMassRange.spin.setValue(float(self.scanParam.xic_delta))
		self.top.tabAll.TicXic.xicThreshold.spin.setValue(int(self.scanParam.ana_height))
		self.top.tabAll.TicXic.xicWidth.spin.setValue(int(self.scanParam.ana_width))

# start Unique Function Define 
	def ConnectRun(self):
		self.connectStatus = self.act.usbConnect()
		if self.connectStatus:
			self.top.comport.SetConnectText(Qt.black,"Connection build", False)
			self.SetAllDacZero()
			self.setEnableButton4conn()
		else:
			self.top.comport.SetConnectText(Qt.red,"Connect failed", True)

	def setEnableButton4conn(self):
		# self.top.comport.connectBtn.setEnabled(False)
		self.setEnableButton4stop()

	def SetAllDacZero(self):
		for i in range(1, 6):
			self.act.setVoltage(i, 0)
		# self.top.tabAll.DCset.fixed_label2.setText("0")
		self.top.tabAll.DCset.esi_label2.setText("0")
		self.top.tabAll.Fan.fanLabel2.setText("0")
		self.top.tabAll.HVscan.text2.setText("0")
		self.act.Vdcout = 0
		self.act.Vscanout = 0

#DC Voltage and Fan Control
	# def setFixedVolt(self):
	# 	self.scanParam.dc_fixed = self.top.tabAll.DCset.DC_Voltage1.spin.value()
	# 	self.top.tabAll.DCset.fixed_label2.setText(str(self.scanParam.dc_fixed))
	# 	self.act.setVoltage(4, self.scanParam.dc_fixed)
	# 	self.LoadScanValue()
	# 	self.scanParam.savePresetFile()

	def setESI(self):
		self.scanParam.dc_esi = self.top.tabAll.DCset.DC_Voltage2.spin.value()
		self.top.tabAll.DCset.esi_label2.setText(str(self.scanParam.dc_esi))
		self.act.setVoltage(1, self.scanParam.dc_esi)
		self.LoadScanValue()
		self.scanParam.savePresetFile()

	def setFan(self):
		self.scanParam.dc_fan = self.top.tabAll.Fan.Fan_Speed.spin.value()
		out = float(self.scanParam.dc_fan) / 1000.0
		self.top.tabAll.Fan.fanLabel2.setText(str(self.scanParam.dc_fan))
		self.act.setVoltage(5, out)
		self.LoadScanValue()
		self.scanParam.savePresetFile()
		if (out == 0):
			self.fanact.fanFlag = False
			updateFan(self, 0)
		elif (self.fanact.fanFlag == False):
			self.fanact.fanFlag = True
			self.thread2.start()
			self.thread2.setPriority(QThread.LowPriority)
			# print("start 2")

#	def resetBtn(self):
#		self.act.resetAlldata()

	def DCmodeBtn(self):
		self.scanFlag = False
		self.LoadDcMode()
		self.raw_path = ""
		self.setEnableButton4start()
		self.act.resetAlldata()
		self.top.runIndex.setText("0")
		self.act.run_flag = True
		if self.fanact.fanFlag:	# fix 2 Qthread writeLine will conflict
			self.preFanFlag = True
			self.fanact.fanFlag = False
		self.thread1.start()
		self.thread1.setPriority(QThread.HighPriority)
		# print("start 1")

	def ScanBtn(self):
		self.scanFlag = True
		self.LoadScanMode()
		# if self.top.Signal.checkbox.isChecked():
		self.raw_path = QFileDialog.getExistingDirectory(self,"Save Raw Data", "./")
		# if self.raw_path == "":
			# return 
		self.setEnableButton4start()
		self.act.resetAlldata()
		self.top.runIndex.setText("0")
		self.act.run_flag = True
		if self.fanact.fanFlag:	# fix 2 Qthread writeLine will conflict
			self.preFanFlag = True
			self.fanact.fanFlag = False
		self.thread1.start()
		self.thread1.setPriority(QThread.HighPriority)
		# print("start 1")

	def LoadScanValue(self):
		self.scanParam.start = self.top.tabAll.HVscan.StartVoltage.spin.value()
		self.scanParam.step = self.top.tabAll.HVscan.VoltageStep.spin.value()
		self.scanParam.loops = self.top.tabAll.HVscan.Loop.spin.value()
		self.scanParam.scanBkWd = self.top.tabAll.HVscan.Back.spin.value()
		self.scanParam.offset = self.top.tabAll.HVscan.offset.spin.value()
		self.scanParam.max_run_loops = self.top.tabAll.HVscan.Run_loop.spin.value()
		self.scanParam.delay = self.top.tabAll.HVscan.delay.spin.value()
		self.scanParam.filterFreq = self.top.tabAll.HVscan.filterFreq.spin.value()
		self.scanParam.dc_fixed = self.top.tabAll.DCset.DC_Voltage1.spin.value()
		self.scanParam.xicMode = self.top.tabAll.HVscan.checkTic.isChecked()
		self.scanParam.filter = self.top.tabAll.HVscan.checkFilter.isChecked()

		if self.top.tabAll.DataSampling.poBtn2.isChecked():
			self.scanParam.adc_pority = -1
		else:
			self.scanParam.adc_pority = 1

		self.scanParam.avg_time = self.top.tabAll.DataSampling.AVG_time.spin.value()

		self.scanParam.xic_center = self.top.tabAll.TicXic.xicMassCenter.spin.value()
		self.scanParam.xic_delta = self.top.tabAll.TicXic.xicMassRange.spin.value()
		self.scanParam.ana_height = self.top.tabAll.TicXic.xicThreshold.spin.value()
		self.scanParam.ana_width = self.top.tabAll.TicXic.xicWidth.spin.value()

	def LoadDcMode(self):
		self.LoadScanValue()
		self.scanParam.savePresetFile()
		self.scanParam.step = 0
		self.scanParam.loops = 10000000
		self.scanParam.max_run_loops = 1

	def LoadScanMode(self):
		self.LoadScanValue()
		self.scanParam.savePresetFile()

	def setEnableButton4start(self):
		self.top.DCmode.setEnabled(False)
		self.top.startScan.setEnabled(False)
		self.top.stop.setEnabled(True)
		self.top.Signal.SaveDataBtn.setEnabled(False)
		# self.top.tabAll.HVscan.reset.setEnabled(False)
		# self.top.tabAll.DCset.V1_Btn.setEnabled(False)
		self.top.tabAll.DCset.V2_Btn.setEnabled(False)
		self.top.tabAll.Fan.FanBtn.setEnabled(False)
		self.top.tabAll.Analysis.CurrBtn.setEnabled(True)

	def StopBtn(self):
		if self.scanFlag:
			self.scanParam.max_run_loops = 0
		else:
			self.scanParam.loops = 0
		self.act.run_flag = False

	def CloseThread(self):
		self.act.run_flag = False
		self.thread1.quit()
		self.thread1.wait()
		# print("quit 1")
		# if not self.scanFlag:
		# 	self.act.resetAlldata()
		self.setEnableButton4stop()
		self.top.Signal.SaveDataBtn.setEnabled(True)
		# fix 2 Qthread writeLine will conflict
		if (self.preFanFlag):
			self.fanact.fanFlag = True
			self.thread2.start()
			self.thread2.setPriority(QThread.LowPriority)
			# print("start 2")

	def updateFan(self, freq):
		self.top.tabAll.Fan.fanLabel2.setText(str(freq))

	def CloseThread2(self):
		self.thread2.quit()
		self.thread2.wait()
		# print("quit 2")

	def setEnableButton4stop(self):
		self.top.DCmode.setEnabled(True)
		self.top.startScan.setEnabled(True)
		self.top.stop.setEnabled(False)
		self.top.tabAll.HVscan.turnoff.setEnabled(True)
		# self.top.tabAll.DCset.V1_Btn.setEnabled(True)
		self.top.tabAll.DCset.V2_Btn.setEnabled(True)
		self.top.tabAll.Fan.FanBtn.setEnabled(True)

	def UpdateAccuIndex(self, index, single_data):
		self.top.runIndex.setText(str(index))
		# if self.top.Signal.checkbox.isChecked() and self.scanFlag:
		if (self.raw_path != "" ) and self.scanFlag:
			tempdata = np.array([self.x_data, single_data], np.float64)
			tempdata = np.transpose(tempdata)
			curr_time = datetime.datetime.now()
			fileheader = self.top.FHedit.edit.text()+"\n"+str(curr_time)+"\n"+"dV(mV), Signal(mV)"
			fname = self.raw_path+"/"+curr_time.strftime("%Y_%m_%d_%H_%M")+".txt"
			#print(fname)
			fil2a.list2DtoTextFile(fname,tempdata,",",self.loggername, fileheader)

	def updateText(self, vol, signal):
		volStr = str(vol) + " (V)"
		self.top.tabAll.HVscan.text2.setText(volStr)
		self.top.Signal.text.setText(str("%3.1f" %signal))

	# def PlotData(self, single_data, accu_data, x_data):
	def PlotData(self, single_data, accu_data, x_data, filter, filter_data):
		single_len = len(single_data)
		self.x_data = x_data
		self.accu_data = accu_data
		if (filter):
			self.filter_data = filter_data
		else:
			self.filter_data = None
		self.top.tabPlot.plot1.ax.clear()
		self.top.tabPlot.plot1.ax.plot(x_data[0:single_len], single_data, color = "blue", linestyle = '-', label= "real-time")
		if self.scanFlag:
			self.top.tabPlot.plot1.ax.set_xlabel("dV (V)")
		else:
			self.top.tabPlot.plot1.ax.set_xlabel("index (V)")
		self.top.tabPlot.plot1.ax.set_ylabel("Output Voltage (mV)")

		if self.act.run_index != 0:
			self.top.tabPlot.plot1.ax.plot(x_data, accu_data, color = "green", linestyle = '-', label ="accumulated")
			self.top.tabPlot.plot1.ax.legend()

		if (filter):
			self.top.tabPlot.plot1.ax.plot(x_data[0:single_len], filter_data, color = "orange", linestyle = '-', label ="filtered")
			self.top.tabPlot.plot1.ax.legend()

		self.top.tabPlot.plot1.figure.canvas.draw()
		self.top.tabPlot.plot1.figure.canvas.flush_events()

	def PlotXicData(self, t_data, tic_data, xic_data):
		self.top.tabPlot.plot2.ax1.clear()
		self.top.tabPlot.plot2.ax1.set_ylabel("TIC Voltage (V)")
		self.top.tabPlot.plot2.ax1.plot(t_data, tic_data, color = 'blue', linestyle = '-', marker = '*')
		self.top.tabPlot.plot2.ax2.clear()
		self.top.tabPlot.plot2.ax2.set_xlabel("Mass")
		self.top.tabPlot.plot2.ax2.set_ylabel("XIC Voltage (V)")
		self.top.tabPlot.plot2.ax2.plot(t_data, xic_data, color = 'red', linestyle = '-', marker = '*')
		self.top.tabPlot.plot2.figure.canvas.draw()
		self.top.tabPlot.plot2.figure.canvas.flush_events()

	def SaveAvgData(self):
		SaveFileName,_ = QFileDialog.getSaveFileName(self,"Save Analysis Data",READOUT_FILENAME,"Text Files (*.txt)")
		if (SaveFileName != ''):
			curr_time = datetime.datetime.now()
			fileheader = self.top.FHedit.edit.text()+"\n"+str(curr_time)+"\n"+"dV(mV), Signal(mV)"
			tempdata = np.array([self.x_data, self.accu_data], np.float64)
			tempdata = np.transpose(tempdata)
			fil2a.list2DtoTextFile(SaveFileName,tempdata,",",self.loggername, fileheader)

#Data Analysis
	def LoadAnaData(self):
		fname,_ = QFileDialog.getOpenFileName(self,"Load Signal Data","","Text Files (*.txt)")
		if (fname != ''):
			self.ana_x, self.ana_y = fil2a.TexTFileto2ColumeArray(fname, ",", self.loggername, 3)
			self.DrawAnaPlot()

	def UseCurrData(self):
		self.ana_x = self.x_data
		self.ana_y = self.accu_data
		self.DrawAnaPlot()

	def DrawAnaPlot(self):
		self.top.tabPlot.plot3.ax.clear()
		self.top.tabPlot.plot3.ax.set_xlabel("dV (V)")
		self.top.tabPlot.plot3.ax.set_ylabel("Voltage Output (mV)")
		self.top.tabPlot.plot3.ax.plot(self.ana_x, self.ana_y)
		self.top.tabPlot.plot3.figure.canvas.draw()
		self.top.tabPlot.plot3.figure.canvas.flush_events()

	def FinkPeakBtn(self):
		th = self.top.tabAll.Analysis.Threshold.spin.value()
		width = self.top.tabAll.Analysis.Width.spin.value()

		self.analist = self.act.findPeak(self.ana_x, self.ana_y, th, width)
		self.DrawAnaPlot()
		self.top.tabAll.Analysis.AnaBtn.setEnabled(True)

		for i in range (0, len(self.analist)):
			self.top.tabPlot.plot3.ax.axvline(x=self.analist[i][0], color='k')
			self.top.tabPlot.plot3.ax.text(self.analist[i][0], self.analist[i][1], str("%2.3f" %self.analist[i][0]), fontsize=12)
		self.top.tabPlot.plot3.figure.canvas.draw()
		self.top.tabPlot.plot3.figure.canvas.flush_events()
		self.top.tabAll.Analysis.AnaBtn.setEnabled(False)
		self.top.tabAll.Analysis.SaveBtn.setEnabled(True)

	def SaveAnaData(self):
		SaveFileName,_ = QFileDialog.getSaveFileName(self,"Save Analysis Data",ANALYSIS_FILENAME,"Text Files (*.txt)")
		if (SaveFileName != ''):
			curr_time = datetime.datetime.now()
			fileheader = self.top.FHedit.edit.text()+"\n"+"dV(mV) , peak_height (mV), peak_width(mV)"
			fil2a.list2DtoTextFile(SaveFileName, self.analist,",",self.loggername, fileheader)
			self.top.tabAll.Analysis.SaveBtn.setEnabled(False)
	
	def ShowThreshold(self):
		value = float(self.top.tabAll.Analysis.Threshold.spin.value())
		self.top.tabPlot.plot3.ax.clear()
		self.top.tabPlot.plot3.ax.set_xlabel("dV (V)")
		self.top.tabPlot.plot3.ax.set_ylabel("Voltage Output (mV)")
		self.top.tabPlot.plot3.ax.plot(self.ana_x, self.ana_y)
		self.top.tabPlot.plot3.ax.axhline(y=value, color='r')
		self.top.tabPlot.plot3.figure.canvas.draw()
		self.top.tabPlot.plot3.figure.canvas.flush_events()

		self.top.tabAll.Analysis.AnaBtn.setEnabled(True)

	def NoiseChange(self):
		self.top.tabAll.Analysis.AnaBtn.setEnabled(True)

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	def closeEvent(self, event):
		self.StopBtn()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

