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
import QSZ001D_Widget as UI
import QSZ001D_Action as ACT
import numpy as np
import datetime
import cv2

STAGE_RANGE_X = 500000
STAGE_RANGE_Y = 500000

# ERROR_TEXT = "Stage Displacement is 0"
MAX_PIXEL = 2048
RED = (255, 0, 0)

#Preset File Setting
IDX_CAM_GAIN = 0
IDX_CAM_TIME = 1
IDX_X_POS = 2
IDX_Y_POS = 3
IDX_X_STEP = 4
IDX_Y_STEP = 5
IDX_STAGE_DISP = 6
MAX_IDX = 7

SETTING_FILEPATH = "set"
PRESET_FILE_NAME = "set/setting.txt"

READOUT_FILENAME = "signal"
TITLE_TEXT = "Academia Sinica Growth Rate Measurement System"
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSZ001C V1.01 \n\n" + \
" Copyright @ 2020 TAIP \n" + \
" Maintain by Quantaser Photonics Co. Ltd "

class scanParam():
	def __init__(self):
		self.loggername = "Total"
		self.camGain = 1
		self.camTime = 20
		self.xPos = 1
		self.yPos = 1
		self.xStep = 2
		self.yStep = 2
		self.stageDisp = 5

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
				self.xPos = int(data[IDX_X_POS])
				self.yPos = int(data[IDX_Y_POS])
				self.xStep = int(data[IDX_X_STEP])
				self.yStep = int(data[IDX_Y_STEP])
				self.stageDisp = int(data[IDX_STAGE_DISP])

	def savePresetFile(self):
		data = [0]*MAX_IDX

		data[IDX_CAM_GAIN] = self.camGain
		data[IDX_CAM_TIME] = self.camTime
		data[IDX_X_POS] = self.xPos
		data[IDX_Y_POS] = self.yPos
		data[IDX_X_STEP] = self.xStep
		data[IDX_Y_STEP] = self.yStep
		data[IDX_STAGE_DISP] = self.stageDisp

		fil2a.array1DtoTextFile(PRESET_FILE_NAME, data, self.loggername)

class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger
		self.top = UI.mainWidget()

		self.act = ACT.qsz001D(self.loggername)
		self.thread1 = QThread()
		self.act.moveToThread(self.thread1)
		self.thread1.started.connect(self.act.startScan)
		self.act.update.connect(self.updatePlot)
		self.act.finished.connect(self.finished)

		self.mainUI()
		self.mainMenu()
		self.mainInit()
		self.linkFunction()

	def mainInit(self):
		self.gotoIndex = 0 
		self.cameraStatus = False
		self.stageStatus = False
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
		menu_about = QAction("&Version", self)
		menu_about.triggered.connect(self.aboutBox)
		aboutMenu = mainMenu.addMenu("&About")
		aboutMenu.addAction(menu_about)

	def linkFunction(self):
		self.top.connectC.btn.clicked.connect(self.conCamera)
		self.top.connectS.btn.clicked.connect(self.conStage)
		self.top.stage.home.clicked.connect(self.moveHome)
		self.top.stage.forward.clicked.connect(self.moveForward)
		self.top.stage.backward.clicked.connect(self.moveBackward)
		self.top.stage.left.clicked.connect(self.moveLeft)
		self.top.stage.right.clicked.connect(self.moveRight)
		# self.top.cam.gain.spin.valueChanged.connect(self.enableSetCam)
		# self.top.cam.gainAuto.stateChanged.connect(self.enableSetCam)
		# self.top.cam.exposure.spin.valueChanged.connect(self.enableSetCam)
		# self.top.cam.expAuto.stateChanged.connect(self.enableSetCam)
		self.top.cam.setCam.clicked.connect(self.setCamera)
		self.top.tab.preScan.preScan.clicked.connect(self.startScan)
		self.top.tab.preScan.preSave.clicked.connect(self.startScanSave)
		# self.top.tab.bacSampling.set.clicked.connect(self.plotSamPoints)
		self.top.control.analysis.clicked.connect(self.imgAnalysis)
		self.top.control.go.clicked.connect(self.goSampling)

	def LoadPreset(self):
		self.top.cam.gain.spin.setValue(self.scanParam.camGain)
		self.top.cam.exposure.spin.setValue(self.scanParam.camTime)
		self.top.tab.preScan.initXpos.spin.setValue(self.scanParam.xPos)
		self.top.tab.preScan.initYpos.spin.setValue(self.scanParam.yPos)
		self.top.tab.preScan.xSteps.spin.setValue(self.scanParam.xStep)
		self.top.tab.preScan.ySteps.spin.setValue(self.scanParam.yStep)
		self.top.tab.preScan.delta.spin.setValue(self.scanParam.stageDisp)

	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")
		Qlogger.QuFilelogger("TEST", logging.DEBUG, "test.txt")

	def conCamera(self):
		result = self.act.connectCamera()
		print(result)
		if result:
			self.top.connectC.SetConnectText(Qt.black,"Connection build", False)
			self.top.cam.setCam.setEnabled(True)
		else:
			self.top.connectC.SetConnectText(Qt.red,"Connection failed", False)
	
	def conStage(self):
		self.stageStatus = self.act.connectStage()
		if self.stageStatus:
			self.top.connectS.SetConnectText(Qt.black,"Connection build", False)
			self.act.stageHome()
		else:
			self.top.connectS.SetConnectText(Qt.red,"Connection failed", False)


#Hardware
	def setCamera(self):
		self.scanParam.camGain = self.top.cam.gain.spin.value()
		self.scanParam.camTime = self.top.cam.exposure.spin.value()

		if (self.top.cam.gainAuto.isChecked()):
			self.act.setGain(0)
			self.top.cam.gainValue.setText("Auto")
		else:
			self.act.setGain(self.scanParam.camGain)
			self.top.cam.gainValue.setText(str(self.scanParam.camGain))

		if (self.top.cam.expAuto.isChecked()):
			self.act.setExplosure(0)
			self.top.cam.timeValue.setText("Auto")
		else:
			self.act.setExplosure(self.scanParam.camTime)	
			self.top.cam.timeValue.setText(str(self.scanParam.camTime))

		self.scanParam.savePresetFile()
		self.cameraStatus = True
		# self.top.cam.setCam.setEnabled(False)
		self.top.tab.preScan.preScan.setEnabled(True)
		self.top.tab.preScan.preSave.setEnabled(True)

	# def enableSetCam(self):
	# 	self.top.cam.setCam.setEnabled(self.cameraStatus)

	def moveHome(self):
		self.act.stageHome()
		self.top.stage.yPos.setText(str(self.act.preY))
		self.top.stage.xPos.setText(str(self.act.preX))
		self.checkStageBtn()

	def moveBackward(self):
		movement = self.top.stage.delta.spin.value()
		move = min(self.act.preY, movement)*(-1)
		self.act.stageMove(0, move)
		self.top.stage.yPos.setText(str(self.act.preY))
		self.checkStageBtn()
		self.act.getImage()
		imgshow = cv2.flip(self.act.img1, 1)
		self.updatePlot(imgshow)

	def moveForward(self):
		movement = self.top.stage.delta.spin.value()
		move = min(STAGE_RANGE_Y-self.act.preY, movement)
		self.act.stageMove(0, move)
		self.top.stage.yPos.setText(str(self.act.preY))
		self.checkStageBtn()
		self.act.getImage()
		imgshow = cv2.flip(self.act.img1, 1)
		self.updatePlot(imgshow)
	
	def moveRight(self):
		movement = self.top.stage.delta.spin.value()
		move = min(self.act.preX, movement)*(-1)
		self.act.stageMove(move, 0)
		self.top.stage.xPos.setText(str(self.act.preX))
		self.checkStageBtn()
		self.act.getImage()
		imgshow = cv2.flip(self.act.img1, 1)
		self.updatePlot(imgshow)

	def moveLeft(self):
		movement = self.top.stage.delta.spin.value()
		move = min(STAGE_RANGE_X-self.act.preX, movement)
		self.act.stageMove(move, 0)
		self.top.stage.xPos.setText(str(self.act.preX))
		self.checkStageBtn()
		self.act.getImage()
		imgshow = cv2.flip(self.act.img1, 1)
		self.updatePlot(imgshow)
	
	def checkStageBtn(self):
		if (self.act.preX == 0) and (self.act.preY == 0):
			self.top.stage.home.setEnabled(False)
		else:
			self.top.stage.home.setEnabled(self.stageStatus)

		if (self.act.preX == 0):
			self.top.stage.right.setEnabled(False)
		else:
			self.top.stage.right.setEnabled(self.stageStatus)

		if (self.act.preX == STAGE_RANGE_X):
			self.top.stage.left.setEnabled(False)
		else:
			self.top.stage.left.setEnabled(self.stageStatus)

		if (self.act.preY == 0):
			self.top.stage.backward.setEnabled(False)
		else:
			self.top.stage.backward.setEnabled(self.stageStatus)

		if (self.act.preY == STAGE_RANGE_Y):
			self.top.stage.forward.setEnabled(False)
		else:
			self.top.stage.forward.setEnabled(self.stageStatus)

	def getPreScanData(self):
		self.scanParam.xPos = self.top.tab.preScan.initXpos.spin.value()
		self.scanParam.yPos = self.top.tab.preScan.initYpos.spin.value()
		self.scanParam.xStep = self.top.tab.preScan.xSteps.spin.value()
		self.scanParam.yStep = self.top.tab.preScan.ySteps.spin.value()
		self.scanParam.stageDisp = self.top.tab.preScan.delta.spin.value()
		self.scanParam.savePresetFile()
		self.top.control.analysis.setEnabled(self.cameraStatus)
		self.act.setScan(self.scanParam.xPos, self.scanParam.xStep, self.scanParam.yPos, self.scanParam.yStep, self.scanParam.stageDisp)

	def startScan(self):
		self.getPreScanData()
		self.act.saveFlag = False
		self.act.runFlag = True
		self.thread1.start()

	def startScanSave(self):
		SaveFileName,_ = QFileDialog.getSaveFileName(self,
						"Save Photo",
						"./" + "photo.jpg",
						"jpg Files (*.jpg)")
		if SaveFileName !="":
			self.getPreScanData()
			self.act.imgFile = SaveFileName
			self.act.saveFlag = True
			self.act.runFlag = True
			self.thread1.start()


	def updatePos(self):
		self.top.stage.xPos.setText(str(self.act.preX))
		self.top.stage.yPos.setText(str(self.act.preY))

	def updatePlot(self, Img):
		self.top.plot.setImage(Img)
		self.updatePos()

	def finished(self, indexout):
		self.top.control.pnameS.combo.clear()
		self.top.control.pnameS.combo.addItems(indexout)
		# change the stop button to scan
		self.thread1.quit()
		self.thread1.wait()

	def imgAnalysis(self):
		index = self.top.control.pnameS.combo.currentIndex()
		threshold = self.top.control.threshold.spin.value()
		self.act.stageIndexMove(index)
		self.sampImg, self.bac_xpos, self.bac_ypos = self.act.anaImage(threshold)
		# print("xpos = "+str(self.bac_xpos))
		# print("ypos = "+str(self.bac_ypos))
		if (self.bac_xpos*self.bac_ypos):
			self.top.control.go.setEnabled(self.cameraStatus)
			self.top.plot.setImage(self.sampImg)
			self.updatePos()
			self.samplingTable()
			#for i in range (len(self.samTable)):
			#	print(self.samTable[i])
			print("hello")
			print(len(self.samTable))
			self.plotSamPoints()
		else:
			print("no bac founded")
			#self.self.top.plot.setImage(self.sampImg)

	def samplingTable(self):
		number = self.top.tab.bacSampling.pts.spin.value()
		xstart = self.top.tab.bacSampling.startx.spin.value()
		delta = self.top.tab.bacSampling.deltax.spin.value()
		if (self.top.tab.bacSampling.left.isChecked()):
			delta = -delta
			xstart = -xstart
		self.samTable = []
		for i in range(number):
			tempx = self.bac_ypos+xstart+delta*i
			print(tempx)
			if 0 < tempx < MAX_PIXEL:
				print("inside"+str(tempx))
				self.samTable.append([self.bac_xpos, self.bac_ypos+xstart+delta*i])
		print("inside samTable"+str(len(self.samTable)))

	def plotSamPoints(self):
		#self.samplingTable()
		for i in range(len(self.samTable)):
			xpos = self.samTable[i][0]
			ypos = self.samTable[i][1]
			print("xpos = "+str(xpos))
			print("ypos = "+str(ypos))
			self.samImg = cv2.circle(self.sampImg, (xpos, ypos), 20,  RED, -1)
			print("i")
		self.top.plot.setImage(self.sampImg)
		self.gotoIndex = 0
		self.top.control.go.setEnabled(self.cameraStatus)
	
	def goSampling(self):
		coeff = self.top.control.pixelCoeff.spin.value
		gotoX = self.top.tab.autoPos.xpos.spin.value()+self.samTable[self.gotoIndex][0]*coeff
		gotoY = self.top.tab.autoPos.ypos.spin.value()+self.samTable[self.gotoIndex][1]*coeff
		self.gotoIndex = self.gotoIndex+1
		if self.gotoIndex == 1:
			self.top.control.go.setText("Next")
		if self.gotoIndex == len(self.samTable):
			self.top.control.go.setText("Go")
			self.top.control.go.setEnabled(False)

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	# def errorBox(self):
	# 	msgBox = QMessageBox()
	# 	msgBox.about(self, "Message", ERROR_TEXT)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

