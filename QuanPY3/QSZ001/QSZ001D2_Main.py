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
READOUT_FILENAME ="signal"
TITLE_TEXT = "Academia Sinica Growth Rate Measurement System"
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSZ001C V1.00 \n\n" + \
" Copyright @ 2020 TAIP \n" + \
" Maintain by Quantaser Photonics Co. Ltd "

STAGE_RANGE_X = 500000
STAGE_RANGE_Y = 500000

ERROR_TEXT = "Stage Displacement is 0"
MAX_PIXEL = 1024
RED = (255, 0, 0)

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
		self.gotoIndex = 0 
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.cameraStatus = False

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
		self.top.tab.preScan.setCam.clicked.connect(self.setCamera)
		self.top.tab.preScan.preScan.clicked.connect(self.startScan)
		self.top.tab.bacSampling.set.clicked.connect(self.plotSamPoints)
		self.top.control.analysis.clicked.connect(self.imgAnalysis)
		# self.top.control.test.clicked.connect(self.imageTest)
		# self.top.control.scan.clicked.connect(self.scanBtn)

	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")
		Qlogger.QuFilelogger("TEST", logging.DEBUG, "test.txt")

	def conCamera(self):
		result = self.act.connectCamera()
		if result:
			self.top.connectC.SetConnectText(Qt.black,"Connection build", False)
			self.top.tab.preScan.setCam.setEnabled(True)
		else:
			self.top.connectC.SetConnectText(Qt.red,"Connection failed", False)
	
	def conStage(self):
		result = self.act.connectStage()
		if result:
			self.top.connectS.SetConnectText(Qt.black,"Connection build", False)
		else:
			self.top.connectS.SetConnectText(Qt.red,"Connection failed", False)


#Hardware
	def setCamera(self):
		if (self.top.tab.preScan.gainAuto.isChecked() == True):
			self.act.setGain(0)	
		else:
			gain = self.top.tab.preScan.gain.spin.value()
			self.act.setGain(gain)

		if (self.top.tab.preScan.explorAuto.isChecked() == True):
			self.act.setExplosure(0)
		else:
			time = self.top.tab.preScan.explorgure.spin.value()
			self.act.setExplosure(time)	

		self.cameraStatus = True
		self.top.tab.preScan.setEnabled(self.cameraStatus)
		self.top.control.analysis.setEnabled(self.cameraStatus)
		
	def moveHome(self):
		self.act.stageHome()
		self.top.stage.yPos.setText(str(self.act.preY))
		self.top.stage.xPos.setText(str(self.act.preX))
		self.checkStageBtn()

	def moveBackward(self):
		movement = self.top.stage.delta.spin.value()
		if (movement == 0):
			self.errorBox()
			self.top.stage.delta.setFocus()
			return
		move = min(self.act.preY, movement)*(-1)
		self.act.stageMove(0, move)
		self.top.stage.yPos.setText(str(self.act.preY))
		self.checkStageBtn()

	def moveForward(self):
		movement = self.top.stage.delta.spin.value()
		if (movement == 0):
			self.errorBox()
			self.top.stage.delta.setFocus()
			return
		move = min(STAGE_RANGE_Y-self.act.preY, movement)
		self.act.stageMove(0, move)
		self.top.stage.yPos.setText(str(self.act.preY))
		self.checkStageBtn()
	
	def moveLeft(self):
		movement = self.top.stage.delta.spin.value()
		if (movement == 0):
			self.errorBox()
			self.top.stage.delta.setFocus()
			return
		move = min(self.act.preX, movement)*(-1)
		self.act.stageMove(move, 0)
		self.top.stage.xPos.setText(str(self.act.preX))
		self.checkStageBtn()

	def moveRight(self):
		movement = self.top.stage.delta.spin.value()
		if (movement == 0):
			self.errorBox()
			self.top.stage.delta.setFocus()
			return
		move = min(STAGE_RANGE_X-self.act.preX,movement)
		self.act.stageMove(move, 0)
		self.top.stage.xPos.setText(str(self.act.preX))
		self.checkStageBtn()
	
	def checkStageBtn(self):

		if (self.act.preX == 0) and (self.act.preY == 0):
			self.top.stage.home.setEnabled(False)
		else:
			self.top.stage.home.setEnabled(True)

		if (self.act.preX == 0):
			self.top.stage.left.setEnabled(False)
		else:
			self.top.stage.left.setEnabled(True)

		if (self.act.preX == STAGE_RANGE_X):
			self.top.stage.right.setEnabled(False)
		else:
			self.top.stage.right.setEnabled(True)

		if (self.act.preY == 0):
			self.top.stage.backward.setEnabled(False)
		else:
			self.top.stage.backward.setEnabled(True)

		if (self.act.preY == STAGE_RANGE_Y):
			self.top.stage.forward.setEnabled(False)
		else:
			self.top.stage.forward.setEnabled(True)

	def startScan(self):
		initx = self.top.tab.preScan.initXpos.spin.value()
		inity = self.top.tab.preScan.initYpos.spin.value()
		xSteps = self.top.tab.preScan.xSteps.spin.value()
		ySteps = self.top.tab.preScan.ySteps.spin.value()
		delta = self.top.tab.preScan.delta.spin.value()
		self.act.runFlag= True
		self.act.setScan(initx, xSteps, inity, ySteps, delta)
		# change the button to stop
		self.thread1.start()

	def updatePos(self):
		pass
		#get the postion from self.act.preX and self.axt.preY
		#display it in stageUI xpos and ypos

	def updatePlot(self, Img, xpos, ypos):
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
		print("xpos = "+str(self.bac_xpos))
		print("ypos = "+str(self.bac_ypos))
		if (self.bac_xpos*self.bac_ypos):
			self.top.plot.setImage(self.sampImg)
			self.updatePos()
			self.samplingTable()
			#for i in range (len(self.samTable)):
			#	print(self.samTable[i])
			self.plotSamPoints()
		else:
			print("no bac founded")
			#self.self.top.plot.setImage(self.sampImg)

	def samplingTable(self):
		# number = sampling number in UI
		# xstart = xtart in UI
		# delta = delta in UI
		number = 5
		xstart = 20
		delta = 40
		self.samTable = []
		for i in range(number):
			tempx = self.bac_xpos+xstart+delta*i
			if 0 < tempx < MAX_PIXEL:
				self.samTable.append([self.bac_xpos+xstart+delta*i, self.bac_ypos])

	def plotSamPoints(self):
		for i in range(len(self.samTable)):
			xpos = self.samTable[i][0]
			ypos = self.samTable[i][1]
			print("xpos = "+str(xpos))
			print("ypos = "+str(ypos))
			self.samImg = cv2.circle(self.sampImg, (xpos, ypos), 3, RED, -1)
		self.top.plot.setImage(self.sampImg)
		self.gotoIndex = 0
		# enable the go button
	
	def goSampling(self):
		coeff = self.top.control.pixelCoeff.spin.value
		gotoX= self.top.autoPos.xpos.spin.value()+self.samTable[self.gotoIndex][0]*coeff
		gotoY = self.top.autoPos.ypos.spin.value()+self.samTable[self.gotoIndex][1]*coeff
		self.gotoIndex = self.gotoIndex+1
		if self.gotoIndex == 1:
			pass
			#set the go button to next
		if self.gotoIndex == len(self.samTable):
			pass
			#disable the go button

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	def errorBox(self):
		msgBox = QMessageBox()
		msgBox.about(self, "Message", ERROR_TEXT)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

