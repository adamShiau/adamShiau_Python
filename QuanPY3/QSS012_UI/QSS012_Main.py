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
import QSS012_Widget as UI
import QSS012_Action as ACT
import numpy as np
import datetime
import cv2

IMG_FILENAME = "output"
DATA_FILENAME = "data"
TITLE_TEXT = "INTERFEROMETER"
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS012 V1.03 \n\n" + \
" Copyright @ 2020 \n" + \
" Maintain by Quantaser Photonics Co. Ltd "

STAGE_POS_MIN = 0000
STAGE_POS_MAX = 12000
STAGE_POS_STEP = 0.03

CAMTEST = False
MOTORTEST = False

PHOTO_TEXT = "Photo index = "

#Preset File Setting
IDX_CAM_GAIN = 0
IDX_CAM_TIME = 1
IDX_CAM_TEMP = 2
IDX_STAGE_SPEED = 3
IDX_SCAN_FROM = 4
IDX_SCAN_TO = 5
IDX_SCAN_DELTA = 6
IDX_SCAN_AVERAGE = 7
MAX_IDX = 8

SETTING_FILEPATH = "set"
PRESET_FILE_NAME = "set/setting.txt"

STAGE_MOVE_SPEED = 0.1

class scanParam():
	def __init__(self):
		self.loggername = "Total"
		self.camGain = 1
		self.camTime = 20
		self.camTemp = 20
		self.stageSpeed = STAGE_MOVE_SPEED
		self.scanFrom = 0
		self.scanTo = 0
		self.scanDelta = 0
		self.scanAvg = 1

	def loadPresetFile(self):
		if not os.path.isdir(SETTING_FILEPATH):
			os.mkdir(SETTING_FILEPATH)
			self.savePresetFile()
		elif not os.path.exists(PRESET_FILE_NAME):
			self.savePresetFile()
		else:
			data = fil2a.TexTFileto1DList(PRESET_FILE_NAME,self.loggername)
			# print(data)
			if (len(data) != MAX_IDX):
				self.savePresetFile()
			else:
				self.camGain = int(data[IDX_CAM_GAIN])
				self.camTime = int(data[IDX_CAM_TIME])
				self.camTemp = int(data[IDX_CAM_TEMP])
				self.stageSpeed = float(data[IDX_STAGE_SPEED])
				self.scanFrom = float(data[IDX_SCAN_FROM])
				self.scanTo = float(data[IDX_SCAN_TO])
				self.scanDelta = float(data[IDX_SCAN_DELTA])
				self.scanAvg = float(data[IDX_SCAN_AVERAGE])

	def savePresetFile(self):
		data = [0]*MAX_IDX

		data[IDX_CAM_GAIN] = self.camGain
		data[IDX_CAM_TIME] = self.camTime
		data[IDX_CAM_TEMP] = self.camTemp
		data[IDX_STAGE_SPEED] = self.stageSpeed
		data[IDX_SCAN_FROM] = self.scanFrom
		data[IDX_SCAN_TO] = self.scanTo
		data[IDX_SCAN_DELTA] = self.scanDelta
		data[IDX_SCAN_AVERAGE] = self.scanAvg

		fil2a.array1DtoTextFile(PRESET_FILE_NAME, data, self.loggername)

class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger
		self.top = UI.mainWidget()

		self.stageAct = ACT.stageAction(self.loggername, MOTORTEST)
		self.thread1 = QThread()
		self.stageAct.moveToThread(self.thread1)
		self.thread1.started.connect(self.stageAct.homeAndGoto)
		self.stageAct.finishedConn.connect(self.actFinishedConn)
		self.stageAct.finishedMove.connect(self.actFinishedMove)

		self.act = ACT.qss012(self.loggername, self.stageAct.motor, MOTORTEST, CAMTEST)
		self.thread = QThread()
		self.act.moveToThread(self.thread) 
		self.thread.started.connect(self.act.stageScan)
		# self.act.finishedConn.connect(self.actFinishedConn)
		# self.act.finishedMove.connect(self.actFinishedMove)
		self.act.updateScan.connect(self.updatePlot)
		self.act.finishedScan.connect(self.actFinishedScan)

		self.mainUI()
		self.mainMenu()
		self.mainInit()
		self.linkFunction()

	def mainInit(self):
		self.stage_pos = 0.0
		self.cameraStatus = False
		self.shutterStatus = False
		self.total = np.empty(0)
		self.posArray = np.empty(0)
		self.scanParam = scanParam()
		self.scanParam.loadPresetFile()
		self.LoadPreset()

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
		# menu_save.triggered.connect(self.saveFile)
		menu_about = QAction("&Version", self)
		menu_about.triggered.connect(self.aboutBox)
		aboutMenu = mainMenu.addMenu("&About")
		aboutMenu.addAction(menu_about)

	def linkFunction(self):
		self.top.hw.connectS.btn.clicked.connect(self.connectStage)
		self.top.hw.stage.forward.clicked.connect(lambda:self.stageMoveBtn("forward"))
		self.top.hw.stage.backward.clicked.connect(lambda:self.stageMoveBtn("backward"))
		self.top.hw.stage.home.clicked.connect(lambda:self.stageGotoBtn(True))
		self.top.hw.setSpeed.clicked.connect(self.setSpeedBtn)
		self.top.hw.gotoBtn.clicked.connect(lambda:self.stageGotoBtn(False))
		self.top.hw.connectC.btn.clicked.connect(self.connectCamera)
		self.top.hw.setCam.clicked.connect(self.setCamera)
		self.top.hw.getImg.clicked.connect(self.getImageBtn)
		self.top.hw.camOff.clicked.connect(self.camOffBtn)
		self.top.control.scan.clicked.connect(self.scanImage)
		self.top.control.stop.clicked.connect(self.stopScan)
		self.top.save1.clicked.connect(lambda:self.saveFile(1))
		self.top.save2.clicked.connect(lambda:self.saveFile(2))

	def LoadPreset(self):
		self.top.hw.gain.spin.setValue(self.scanParam.camGain)
		self.top.hw.time.spin.setValue(self.scanParam.camTime)
		self.top.hw.temp.spin.setValue(self.scanParam.camTemp)
		self.top.hw.speed.spin.setValue(self.scanParam.stageSpeed)
		self.top.control.scanFrom.spin.setValue(self.scanParam.scanFrom)
		self.top.control.scanTo.spin.setValue(self.scanParam.scanTo)
		self.top.control.delta.spin.setValue(self.scanParam.scanDelta)

	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")

#Stage
	def connectStage(self):
		self.top.hw.connectS.btn.setEnabled(False)
		self.top.hw.connectS.btn.update()
		self.stageAct.connect()

	def actFinishedConn(self, status):
		if status:
			self.act.motor = self.stageAct.motor
			self.top.hw.connectS.SetConnectText(Qt.black,"Connection build", False)
			self.stageCheckBtn(True)
			self.stageGotoBtn(True) # home
		else:
			self.top.hw.connectS.SetConnectText(Qt.red, "Connect Failed", True)
			self.stageCheckBtn(False)

	def setSpeedBtn(self):
		self.scanParam.stageSpeed = self.top.hw.speed.spin.value()
		self.scanParam.savePresetFile()
		if not MOTORTEST:
			self.stageAct.motor.set_velocity_parameters(0, self.scanParam.stageSpeed, self.scanParam.stageSpeed)

	def stageGotoBtn(self, home = False):
		if home:
			self.stageAct.goTo = 0
		else:
			self.stage_pos = self.top.hw.goPos.spin.value()
			self.stageAct.goTo = self.stage_pos / 1000.0
			self.stageAct.speed = self.scanParam.stageSpeed
		# print(self.stageAct.goTo)
		# self.stageAct.stageMove()
		self.thread1.start()

	def actFinishedMove(self, pos):
		self.thread1.quit()
		self.thread1.wait()
		self.stage_pos = pos * 1000
		pos_str = "%4.2f" % self.stage_pos + " um"
		self.top.hw.stage.pos.setText(pos_str)
		self.stageCheckBtn(True)

	def stageMoveBtn(self, type):
		# self.stageCheckBtn(False)
		old_pos = self.stage_pos
		move = 0.0

		if (type == "backward"):
			# print("backward")
			if ( (old_pos - STAGE_POS_STEP) < STAGE_POS_MIN):
				move = STAGE_POS_MIN - old_pos
			else:
				move = -STAGE_POS_STEP
			# print(move)
			if not MOTORTEST:
				self.stageAct.motor.set_velocity_parameters(0, STAGE_MOVE_SPEED, STAGE_MOVE_SPEED)
				self.stageAct.motor.move_by(move / 1000.0)
			self.stage_pos = self.stage_pos + move
			# print(self.stage_pos)
		elif (type == "forward"):
			# print("forward")
			if ( (old_pos + STAGE_POS_STEP) > STAGE_POS_MAX):
				move = STAGE_POS_MAX - old_pos
			else:
				move = STAGE_POS_STEP
			# print(move)
			if not MOTORTEST:
				self.stageAct.motor.set_velocity_parameters(0, STAGE_MOVE_SPEED, STAGE_MOVE_SPEED)
				self.stageAct.motor.move_by(move / 1000.0)
			self.stage_pos = self.stage_pos + move
			# print(self.stage_pos)

		pos_str = "%4.2f" % self.stage_pos + " um"
		self.top.hw.stage.pos.setText(pos_str)
		self.getImageBtn()
		self.stageCheckBtn(True)

	def stageCheckBtn(self, enable = True):
		status = self.stageAct.motorStatus and self.cameraStatus and self.shutterStatus
		self.top.hw.setSpeed.setEnabled(self.stageAct.motorStatus)
		self.top.control.scan.setEnabled(status)
		if (enable == False):
			self.top.hw.stage.home.setEnabled(False)
			self.top.hw.stage.backward.setEnabled(False)
			self.top.hw.stage.forward.setEnabled(False)
			self.top.hw.gotoBtn.setEnabled(False)
		else:
			self.top.hw.gotoBtn.setEnabled(self.stageAct.motorStatus)

			if (self.stage_pos == 0):
				self.top.hw.stage.home.setEnabled(False)
			else:
				self.top.hw.stage.home.setEnabled(self.stageAct.motorStatus)

			if (self.stage_pos == STAGE_POS_MIN):
				self.top.hw.stage.backward.setEnabled(False)
			else:
				self.top.hw.stage.backward.setEnabled(status)

			if (self.stage_pos == STAGE_POS_MAX):
				self.top.hw.stage.forward.setEnabled(False)
			else:
				self.top.hw.stage.forward.setEnabled(status)

#Camera
	def connectCamera(self):
		if not CAMTEST:
			r1 = self.act.camera.camInit()
			r2 = self.act.camera.setReadMode(4)
			r3 = self.act.camera.setAcquistionMode(1)
			r4 = self.act.camera.setTriggerMode(0)
			r5 = self.act.camera.setImage(1,1,1,self.act.camera.img_width,1,self.act.camera.img_height)
			r6 = self.act.camera.setShutter(1,1,0,0) # add shutter permanent open
			self.act.camera.setCoolerMode(0) 
			self.cameraStatus = r1 and r2 and r3 and r4 and r5 and r6
		else:
			self.cameraStatus = 1

		if (self.cameraStatus == 1):
			self.shutterStatus = True
			self.top.hw.connectC.SetConnectText(Qt.black,"Connection build", False)
			self.top.hw.setCam.setEnabled(True)
			self.top.hw.getImg.setEnabled(True)
			self.top.hw.camOff.setEnabled(True)
		else:
			self.top.hw.connectC.SetConnectText(Qt.red,"Conection Failed", True)

	def setCamera(self):
		self.scanParam.camGain = self.top.hw.gain.spin.value()
		self.scanParam.camTime = self.top.hw.time.spin.value()
		self.scanParam.camTemp = self.top.hw.temp.spin.value()
		self.scanParam.savePresetFile()
		eTime = self.scanParam.camTime / 1000.0
		if not CAMTEST:
			self.act.camera.setEMCCDGain(self.scanParam.camGain)
			self.act.camera.setExplosureTime(eTime)
			self.act.camera.CoolerOn()
			self.act.camera.setTemperature(self.scanParam.camTemp)
		self.top.hw.setCam.setEnabled(False)
		self.stageCheckBtn(True)

	def getImageBtn(self):
		self.act.getCamImg()
		tcam = self.act.camera.getTemperature()
		self.top.plot1.clear()
		self.top.plot2.clear()
		self.top.plot1.setImage(self.act.camera.img)
		self.top.hw.temp.labelvalue.setText(str(tcam))

	def camOffBtn(self):
		if (self.shutterStatus):
			if CAMTEST:
				print("Shutter Off")
			elif self.cameraStatus:
				self.act.camera.setShutter(1,2,0,0)	# set shutter off
			self.shutterStatus = False
			self.top.hw.camOff.setText("Shutter On")
			self.top.hw.getImg.setEnabled(False)
			self.top.control.scan.setEnabled(False)
		else:
			if CAMTEST:
				print("Shutter On")
			elif self.cameraStatus:
				self.act.camera.setShutter(1,1,0,0) # add shutter permanent open
			self.shutterStatus = True
			self.top.hw.camOff.setText("Shutter Off")
			statusC = self.cameraStatus and self.shutterStatus
			self.top.hw.getImg.setEnabled(statusC)
			status = self.stageAct.motorStatus and self.cameraStatus and self.shutterStatus
			self.top.control.scan.setEnabled(status)


#Control Scan
	def scanImage(self):
		self.scanParam.scanFrom = self.top.control.scanFrom.spin.value()
		self.scanParam.scanTo = self.top.control.scanTo.spin.value()
		self.scanParam.scanDelta = self.top.control.delta.spin.value()
		self.scanParam.scanAvg = self.top.control.average.spin.value()
		self.scanParam.savePresetFile()
		self.act.scanFrom = self.scanParam.scanFrom / 1000.0
		self.act.scanTo = self.scanParam.scanTo / 1000.0
		self.act.delta = self.scanParam.scanDelta / 1000.0
		self.act.average = self.scanParam.scanAvg

		self.total = np.empty(0)
		self.posArray = np.empty(0)
		self.top.plot1.clear()
		self.top.plot2.clear()

		self.top.control.scan.setEnabled(False)
		self.top.control.stop.setEnabled(True)
		self.act.scanFlag = True
		self.thread.start()

	def stopScan(self):
		self.act.scanFlag = False
		self.top.control.stop.setEnabled(False)

	def actFinishedScan(self):
		self.thread.quit()
		self.thread.wait()
		status = self.stageAct.motorStatus and self.cameraStatus and self.shutterStatus
		self.top.control.scan.setEnabled(status)
	
	def updatePlot(self, pos, img, tcam):
		self.stage_pos = pos * 1000
		self.posArray = np.append(self.posArray, self.stage_pos)
		pos_str = "%4.2f" % self.stage_pos + " um"
		self.top.hw.stage.pos.setText(pos_str)
		self.top.hw.temp.labelvalue.setText(str(tcam))
		self.top.plot1.setImage(img, autoRange = False)
		data, xdata = self.top.roi.getArrayRegion(img, self.top.plot1.imageItem, returnMappedCoords = True)
		num_sum = sum(sum(data))
		self.total = np.append(self.total, num_sum)
		self.top.plot2.plot(self.posArray, self.total)
		# print("%3.2f" % self.stage_pos + '\t' + str(num_sum))

	def plotROI(self,roicord):
		xarray = roicord[0]
		yarray = roicord[1]
		xlen = len(xarray)
		ylen = len(xarray[0])
		y1 = int(xarray[0][0])
		y2 = int(xarray[xlen-1][0])
		x1 = int(yarray[0][0])
		x2 = int(yarray[0][ylen-1])
		cordout = "x1="+str(x1)+", x2="+str(x2)+", y1="+str(y1)+(", y2=")+str(y2)
		return cordout

	def saveFile(self, type):
			if (type == 1):
				filename,_ = QFileDialog.getSaveFileName(self,"Save Image Data", "./" + IMG_FILENAME, "Text Files (*.txt)")
				if (filename != ""):
					data, xdata = self.top.roi.getArrayRegion(self.act.camera.img, self.top.plot1.imageItem, returnMappedCoords = True)
					#img1 = cv2.cvtColor(self.act.camera.img, cv2.COLOR_GRAY2RGB)

					cordout = self.plotROI(xdata)
					fil2a.list2DtoTextFile(filename, self.act.camera.img, ",", self.loggername)
					farray = filename.split('.')
					filename2 = farray[0] + "_ROI." + farray[1]
					fo = open(filename2,"w")
					fo.write(cordout)
					fo.close()
			else:
				filename,_ = QFileDialog.getSaveFileName(self,"Save Data", "./" + DATA_FILENAME, "Text Files (*.txt)")
				if (filename != ""):
					num = len(self.posArray)
					fo = open(filename, "w")
					for i in range(0, num):
						fo.write("%3.2f" % self.posArray[i] + '\t' + str(self.total[i]) + '\n')
					fo.close()

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	def closeEvent(self, event):
		if CAMTEST:
			print("window close")
		elif self.cameraStatus:
			self.act.camera.setShutter(1,2,0,0)	# set shutter off
			self.act.camera.shutDown()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())


