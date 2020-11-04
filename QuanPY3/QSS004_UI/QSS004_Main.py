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
import QSS004_Widget as UI
import QSS004_Action as ACT
import numpy as np
#from screeninfo import get_monitors
import datetime

# monitor = get_monitors()
# monitor_string = str(monitor[0])
# monitor_info = monitor_string.split(', ')
# monitor_width = float(monitor_info[2][6:])
# monitor_height = float(monitor_info[3][7:])

monitor_width = 1920
monitor_height = 1080

MAIN_W = int(monitor_width*0.8)
MAIN_H = int(monitor_height*0.8)

HOST_NAME = "root"
HOST_PWD = "root"
HOST_PORT = 22

CONNECT_BIT_CMD = 'cat /root/int_GB.bit > /dev/xdevcfg'
LIB_PATH = 'LD_LIBRARY_PATH=/opt/redpitaya/lib '
SET_DAC = LIB_PATH + './DAC '
DAC_Constant_S5 = 6.0/5000.0

#Preset File Setting
IDX_IP = 0
IDX_HV_START = 1
IDX_HV_STEP = 2
IDX_HV_LOOPS = 3
IDX_HV_BKPTS = 4
IDX_HV_OFFSET = 13
IDX_ADC_LOOPS = 12

IDX_DC_FIX = 5
IDX_DC_ESI = 6
IDX_DC_FAN = 7
IDX_ADC_CH = 8
IDX_ADC_PO = 9
IDX_ADC_AVG = 10
IDX_ADC_TIMES = 11
IDX_INTEGRATOR = 14

#IDX_INT_TH1 = 13
#IDX_INT_TH2 = 14
#IDX_INT_TH3 = 15
#IDX_INT_TIME1 = 16
#IDX_INT_ITME2 = 17
#IDX_INT_TIME3 = 18
#IDX_INT_TIME4 = 19
#IDX_ANA_HEIGHT = 20
#IDX_ANA_WIDHTE = 21 

MAX_IDX = 15

SETTING_FILEPATH = "set"
PRESET_FILE_NAME = "set/setting.txt"
READOUT_FILENAME = "Signal_Read_Out.txt"
ANALYSIS_FILENAME = "Data_Analysis.txt"

TITLE_TEXT = " Acdemic Sincica GRC Mass Spectrometer "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS004 V2.02 \n\n" + \
" Copyright @ 2019 TAIP \n" + \
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

		self.dc_fixed = 0
		self.dc_esi = 0
		self.dc_fan = 0

		self.channel_str = '0 '
		self.adc_pority = 1
		self.mv_avg_num = 50
		self.avg_time = 1
		self.int_time = 1

		# self.integrator_time1 = 100
		# self.integrator_time2 = 100
		# self.integrator_time3 = 100
		# self.integrator_time4 = 100
		# self.integrator_th1 = 1000
		# self.integrator_th2 = 1000
		# self.integrator_th3 = 1000

		self.ana_height = 0
		self.ana_width = 1

	def loadPresetFile(self):
		if not os.path.isdir(SETTING_FILEPATH):
			os.mkdir(SETTING_FILEPATH)
			self.savePresetFile()
		elif not os.path.exists(PRESET_FILE_NAME):
			self.savePresetFile()
		else:
			data = fil2a.TexTFileto1DList(PRESET_FILE_NAME,self.loggername)
			#print(data)
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

				self.dc_fixed = int(data[IDX_DC_FIX])
				self.dc_esi = int(data[IDX_DC_ESI])
				self.dc_fan = int(data[IDX_DC_FAN])

				self.channel_str = data[IDX_ADC_CH]
				self.adc_pority = int(data[IDX_ADC_PO])
				self.mv_avg_num = int(data[IDX_ADC_AVG])
				self.avg_time = int(data[IDX_ADC_TIMES])
				self.int_time = int(data[IDX_INTEGRATOR])

				# self.integrator_time1 = float(data[IDX_INT_TIME1])
				# self.integrator_time2 = float(data[IDX_INT_ITME2])
				# self.integrator_time3 = float(data[IDX_INT_TIME3])
				# self.integrator_time4 = float(data[IDX_INT_TIME4])
				# self.integrator_th1 = int(data[IDX_INT_TH1])
				# self.integrator_th2 = int(data[IDX_INT_TH2])
				# self.integrator_th3 = int(data[IDX_INT_TH3])

				# self.ana_height = int(data[IDX_ANA_HEIGHT])
				# self.ana_width = int(data[IDX_ANA_WIDHTE])

	def savePresetFile(self):
		data = [0]*MAX_IDX
		data[IDX_IP] = self.ip

		data[IDX_HV_START] = self.start
		data[IDX_HV_STEP] = self.step
		data[IDX_HV_LOOPS] = self.loops
		data[IDX_HV_BKPTS] = self.scanBkWd
		data[IDX_HV_OFFSET] = self.offset
		data[IDX_ADC_LOOPS] = self.max_run_loops

		data[IDX_DC_FIX] = self.dc_fixed
		data[IDX_DC_ESI] = self.dc_esi
		data[IDX_DC_FAN] = self.dc_fan

		data[IDX_ADC_CH] = self.channel_str
		data[IDX_ADC_PO] = self.adc_pority
		data[IDX_ADC_AVG] = self.mv_avg_num
		data[IDX_ADC_TIMES] = self.avg_time
		data[IDX_INTEGRATOR] = self.int_time
	
		# data[IDX_INT_TIME1] = self.integrator_time1
		# data[IDX_INT_ITME2] = self.integrator_time2
		# data[IDX_INT_TIME3] = self.integrator_time3
		# data[IDX_INT_TIME4] = self.integrator_time4
		# data[IDX_INT_TH1] = self.integrator_th1
		# data[IDX_INT_TH2] = self.integrator_th2
		# data[IDX_INT_TH3] = self.integrator_th3

		# data[IDX_ANA_HEIGHT] = self.ana_height
		# data[IDX_ANA_WIDHTE] = self.ana_width

		#print(data)
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
		self.top = UI.mainWidget()
		#self.top.setMinimumSize(TOP_W, TOP_H)
		self.thread1 = QThread()
		self.thread1.started.connect(lambda:self.act.VoltageOut(self.scanFlag,self.scanParam))
		self.act.moveToThread(self.thread1)
		self.act.update_text.connect(self.updateText)
		self.act.update_array.connect(self.PlotData)
		self.act.update_index.connect(self.UpdateAccuIndex)
		self.act.finished.connect(self.CloseThread)
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
		self.SSHStatus = False
		self.scanFlag = False
		self.scanParam = scanParam()
		#print("in MainInit")
		self.scanParam.loadPresetFile()
		self.LoadPreset()
		# self.top.tabAll.VoltageChange()

	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")

	def linkFunction(self):
		self.top.net.btn.clicked.connect(self.sshConnectRun)
		# self.top.tabAll.DCset.V1_Btn.clicked.connect(self.setFixedVolt)
		self.top.tabAll.DCset.V2_Btn.clicked.connect(self.setESI)
		self.top.tabAll.Fan.FanBtn.clicked.connect(self.setFan)
		self.top.tabAll.HVscan.reset.clicked.connect(self.SetAllDacZero)
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
		self.top.net.IP.setText(self.scanParam.ip)

		self.top.tabAll.HVscan.StartVoltage.spin.setValue(int(self.scanParam.start))
		self.top.tabAll.HVscan.VoltageStep.spin.setValue(float(self.scanParam.step))
		self.top.tabAll.HVscan.Loop.spin.setValue(int(self.scanParam.loops))
		self.top.tabAll.HVscan.Back.spin.setValue(int(self.scanParam.scanBkWd))
		self.top.tabAll.HVscan.offset.spin.setValue(int(self.scanParam.offset))
		self.top.tabAll.HVscan.Run_loop.spin.setValue(int(self.scanParam.max_run_loops))

		self.top.tabAll.DCset.DC_Voltage1.spin.setValue(int(self.scanParam.dc_fixed))
		self.top.tabAll.DCset.DC_Voltage2.spin.setValue(int(self.scanParam.dc_esi))
		self.top.tabAll.Fan.Fan_Speed.spin.setValue(int(self.scanParam.dc_fan))

		if (self.scanParam.channel_str == '1 '):
			self.top.tabAll.DataSampling.chBtn2.setChecked(True)
		else:
			self.top.tabAll.DataSampling.chBtn1.setChecked(True)

		if (self.scanParam.adc_pority == -1):
			self.top.tabAll.DataSampling.poBtn2.setChecked(True)
		else:
			self.top.tabAll.DataSampling.poBtn1.setChecked(True)

		self.top.tabAll.DataSampling.MV_number.spin.setValue(int(self.scanParam.mv_avg_num))
		self.top.tabAll.DataSampling.AVG_time.spin.setValue(int(self.scanParam.avg_time))

# start Unique Function Define 
	def sshConnectRun(self):
		self.scanParam.ip = self.top.net.IP.text()
		host = "rp-" + str(self.scanParam.ip) + ".local"
		self.SSHStatus = self.act.sshConnect(host, HOST_PORT, HOST_NAME, HOST_PWD)
		if self.SSHStatus:
			self.act.ssh.sendCmd(CONNECT_BIT_CMD, False, 1)
			self.top.net.SetConnectText(Qt.black,"Connection build", False)
			self.SetAllDacZero()
			self.setEnableButton4conn()
			self.scanParam.savePresetFile()
		else:
			self.top.net.SetConnectText(Qt.red,"Connect Failed", True)

	def setEnableButton4conn(self):
		# self.top.net.connectBtn.setEnabled(False)
		self.setEnableButton4stop()

	def SetAllDacZero(self):
		for i in range(0, 10):
			ch = str(i) + ' 0'
			cmd = SET_DAC + ch
			self.act.ssh.sendCmd(cmd)
		self.top.tabAll.HVscan.text2.setText("0 (V)")
		# self.top.tabAll.DCset.fixed_label2.setText("0")
		self.top.tabAll.DCset.esi_label2.setText("0")
		self.top.tabAll.Fan.fanLabel2.setText("0")

#DC Voltage and Fan Control
	# def setFixedVolt(self):
	# 	self.scanParam.dc_fixed = self.top.tabAll.DCset.DC_Voltage1.spin.value()
	# 	out = self.scanParam.dc_fixed * DAC_Constant_S5
	# 	cmd = SET_DAC + '2 ' + str(out)
	# 	self.top.tabAll.DCset.fixed_label2.setText(str(self.scanParam.dc_fixed))
	# 	self.act.sendSSHCmd(cmd)
	# 	self.LoadScanValue()
	# 	self.scanParam.savePresetFile()

	def setESI(self):
		self.scanParam.dc_esi = self.top.tabAll.DCset.DC_Voltage2.spin.value()
		out = self.scanParam.dc_esi * DAC_Constant_S5
		cmd = SET_DAC + '3 ' + str(out)
		self.top.tabAll.DCset.esi_label2.setText(str(self.scanParam.dc_esi))
		self.act.ssh.sendCmd(cmd)
		self.LoadScanValue()
		self.scanParam.savePresetFile()

	def setFan(self):
		self.scanParam.dc_fan = self.top.tabAll.Fan.Fan_Speed.spin.value()
		out = float(self.scanParam.dc_fan) / 1000.0
		cmd = SET_DAC + '4 ' + str(out)
		self.top.tabAll.Fan.fanLabel2.setText(str(self.scanParam.dc_fan))
		self.act.ssh.sendCmd(cmd)
		self.LoadScanValue()
		self.scanParam.savePresetFile()

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
		self.thread1.start()

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
		self.thread1.start()

	def LoadScanValue(self):
		self.scanParam.start = self.top.tabAll.HVscan.StartVoltage.spin.value()
		self.scanParam.step = self.top.tabAll.HVscan.VoltageStep.spin.value()
		self.scanParam.loops = self.top.tabAll.HVscan.Loop.spin.value()
		self.scanParam.scanBkWd = self.top.tabAll.HVscan.Back.spin.value()
		self.scanParam.offset = self.top.tabAll.HVscan.offset.spin.value()
		self.scanParam.max_run_loops = self.top.tabAll.HVscan.Run_loop.spin.value()
		self.scanParam.dc_fixed = self.top.tabAll.DCset.DC_Voltage1.spin.value()

		if self.top.tabAll.DataSampling.chBtn2.isChecked():
			self.scanParam.channel_str = '1 '
		else:
			self.scanParam.channel_str = '0 '

		if self.top.tabAll.DataSampling.poBtn2.isChecked():
			self.scanParam.adc_pority = -1
		else:
			self.scanParam.adc_pority = 1

		self.scanParam.mv_avg_num = self.top.tabAll.DataSampling.MV_number.spin.value()
		self.scanParam.avg_time = self.top.tabAll.DataSampling.AVG_time.spin.value()
		self.scanParam.int_time = self.top.tabAll.DataSampling.int_time.spin.value()

	def LoadDcMode(self):
		self.LoadScanValue()
		self.scanParam.savePresetFile()

		self.scanParam.step = 0
		self.scanParam.loops = 10000000
		self.scanParam.max_run_loops = 1

		# self.scanParam.integrator_time2 = self.scanParam.integrator_time1
		# self.scanParam.integrator_time3 = self.scanParam.integrator_time1
		# self.scanParam.integrator_time4 = self.scanParam.integrator_time1

	def LoadScanMode(self):
		self.LoadScanValue()
		self.scanParam.savePresetFile()

		# self.scanParam.integrator_time1 = self.top.tabAll.Integrator.int_time1.value()
		# self.scanParam.integrator_time2 = self.top.tabAll.Integrator.int_time2.value()
		# self.scanParam.integrator_time3 = self.top.tabAll.Integrator.int_time3.value()
		# self.scanParam.integrator_time4 = self.top.tabAll.Integrator.int_time4.value()

		# self.scanParam.integrator_th1 = self.top.tabAll.Integrator.vth1.value()
		# self.scanParam.integrator_th2 = self.top.tabAll.Integrator.vth2.value()
		# self.scanParam.integrator_th3 = self.top.tabAll.Integrator.vth3.value()

	def setEnableButton4start(self):
		self.top.DCmode.setEnabled(False)
		self.top.startScan.setEnabled(False)
		self.top.stop.setEnabled(True)
		self.top.Signal.SaveDataBtn.setEnabled(False)
		self.top.tabAll.HVscan.reset.setEnabled(False)
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
		# if not self.scanFlag:
		# 	self.act.resetAlldata()
		self.setEnableButton4stop()
		self.top.Signal.SaveDataBtn.setEnabled(True)

	def setEnableButton4stop(self):
		self.top.DCmode.setEnabled(True)
		self.top.startScan.setEnabled(True)
		self.top.stop.setEnabled(False)
		self.top.tabAll.HVscan.reset.setEnabled(True)
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

	def PlotData(self, single_data, accu_data, x_data):
		single_len = len(single_data)
		self.x_data = x_data
		self.accu_data = accu_data
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
		self.top.tabPlot.plot1.figure.canvas.draw()
		self.top.tabPlot.plot1.figure.canvas.flush_events()

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
		self.top.tabPlot.plot2.ax.clear()
		self.top.tabPlot.plot2.ax.set_xlabel("dV (V)")
		self.top.tabPlot.plot2.ax.set_ylabel("Voltage Output (mV)")
		self.top.tabPlot.plot2.ax.plot(self.ana_x, self.ana_y)
		self.top.tabPlot.plot2.figure.canvas.draw()
		self.top.tabPlot.plot2.figure.canvas.flush_events()

	def FinkPeakBtn(self):
		th = self.top.tabAll.Analysis.Threshold.spin.value()
		width = self.top.tabAll.Analysis.Width.spin.value()

		self.analist = self.act.findPeak(self.ana_x, self.ana_y, th, width)
		self.DrawAnaPlot()
		self.top.tabAll.Analysis.AnaBtn.setEnabled(True)

		for i in range (0, len(self.analist)):
			self.top.tabPlot.plot2.ax.axvline(x=self.analist[i][0], color='k')
			self.top.tabPlot.plot2.ax.text(self.analist[i][0], self.analist[i][1], str("%2.3f" %self.analist[i][0]), fontsize=12)
		self.top.tabPlot.plot2.figure.canvas.draw()
		self.top.tabPlot.plot2.figure.canvas.flush_events()
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
		self.top.tabPlot.plot2.ax.clear()
		self.top.tabPlot.plot2.ax.set_xlabel("dV (V)")
		self.top.tabPlot.plot2.ax.set_ylabel("Voltage Output (mV)")
		self.top.tabPlot.plot2.ax.plot(self.ana_x, self.ana_y)
		self.top.tabPlot.plot2.ax.axhline(y=value, color='r')
		self.top.tabPlot.plot2.figure.canvas.draw()
		self.top.tabPlot.plot2.figure.canvas.flush_events()

		self.top.tabAll.Analysis.AnaBtn.setEnabled(True)

	def NoiseChange(self):
		self.top.tabAll.Analysis.AnaBtn.setEnabled(True)

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

