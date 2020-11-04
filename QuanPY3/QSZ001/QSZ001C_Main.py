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
import QSZ001C_Widget as UI
import QSZ001C_Action as ACT
import numpy as np
import datetime

READOUT_FILENAME ="signal"
TITLE_TEXT = "Academia Sinica Growth Rate Measurement System"
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSZ001C V1.00 \n\n" + \
" Copyright @ 2020 TAIP \n" + \
" Maintain by Quantaser Photonics Co. Ltd "

STAGE_STEP_X = 100
STAGE_STEP_Y = 100
STAGE_RANGE_X = 500
STAGE_RANGE_Y = 500

PHOTO_TEXT = "Photo index = "

class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger
		self.top = UI.mainWidget()
		self.act = ACT.qsz001C(self.loggername)
		self.thread1 = QThread()
		self.thread2 = QThread()
		# self.act.moveToThread(self.thread1)
		self.thread1.started.connect(lambda:self.act.scanCurrentPlate(0, 0, 0, False))
		self.thread2.started.connect(self.scanFuction)
		self.act.update.connect(self.updatePlot)
		self.act.finished.connect(self.finished)
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

		# fileMenu = mainMenu.addMenu("File")
		# menu_save = QAction("&Save",self)
		# fileMenu.addAction(menu_save)
		# menu_save.triggered.connect(self.saveFile)

		menu_about = QAction("&Version", self)
		menu_about.triggered.connect(self.aboutBox)
		aboutMenu = mainMenu.addMenu("&About")
		aboutMenu.addAction(menu_about)

	def linkFunction(self):
		self.top.tab.connectC.btn.clicked.connect(self.connectCamera)
		self.top.tab.stage.home.clicked.connect(lambda:self.stageMove("home"))
		self.top.tab.stage.up.clicked.connect(lambda:self.stageMove("up"))
		self.top.tab.stage.down.clicked.connect(lambda:self.stageMove("down"))
		self.top.tab.stage.left.clicked.connect(lambda:self.stageMove("left"))
		self.top.tab.stage.right.clicked.connect(lambda:self.stageMove("right"))
		self.top.tab.setCam.clicked.connect(self.setCamera)
		self.top.tab.fpathBtn.clicked.connect(self.filepathBtn)
		self.top.tab.preScan.clicked.connect(self.prescanBtn)
		self.top.tab.create.clicked.connect(self.createBtn)
		self.top.control.delete.clicked.connect(self.deleteBtn)
		self.top.control.test.clicked.connect(self.imageTest)
		self.top.control.scan.clicked.connect(self.scanBtn)

	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")
		Qlogger.QuFilelogger("TEST", logging.DEBUG, "test.txt")

#Hardware
	def connectCamera(self):
		# print("Camera Init in main")
		result = self.act.camera.camInit()
		if (result == 1):
			self.top.tab.connectC.SetConnectText(Qt.black,"Connection build", False)
			self.top.tab.setCam.setEnabled(True)

	def setCamera(self):
		if (self.top.tab.gainAuto.isChecked() == True):
			self.act.camera.setGainAuto()
			# print(1)
		else:
			gain = self.top.tab.gain.spin.value()
			self.act.camera.setGain(gain)
			# print(2)

		if (self.top.tab.explorAuto.isChecked() == True):
			self.act.camera.setExplosureAuto()
			# print(3)
		else:
			gain = self.top.tab.explorgure.spin.value()
			self.act.camera.setExplosure(gain)
			# print(4)
		self.cameraStatus = True
		# self.act.camera.startAcquire()
		self.top.tab.preScan.setEnabled(self.cameraStatus)
		self.top.control.test.setEnabled(self.cameraStatus)
		num = len(self.top.control.pname_list)
		# if (num > 0):
		# 	self.top.control.scan.setEnabled(self.cameraStatus)
		# else:
		# 	self.top.control.scan.setEnabled(False)

	def stageMove(self, type):
		old_x = self.act.preX
		old_y = self.act.preY
		move = 0

		if (type == "up"):
			# print("up")
			if (old_y < STAGE_STEP_Y):
				move = -old_y
			else:
				move = -STAGE_STEP_Y
			# print(move)
			self.act.stageMove(0, move)

		elif (type == "down"):
			# print("down")
			move = STAGE_RANGE_Y - old_y
			if ( move > STAGE_STEP_Y):
				move = STAGE_STEP_Y
			# print(move)
			self.act.stageMove(0, move)

		elif (type == "left"):
			# print("left")
			if (old_x < STAGE_STEP_X):
				move = -old_x
			else:
				move = -STAGE_STEP_X
			# print(move)
			self.act.stageMove(move, 0)

		elif (type == "right"):
			# print("right")
			move = STAGE_RANGE_X - old_x
			if ( move > STAGE_STEP_X):
				move = STAGE_STEP_X
			# print(move)
			self.act.stageMove(move, 0)

		else:	#if (type == "home"):
			# print("home")
			self.act.stageHome()

		self.top.tab.stage.xPos.setText(str(self.act.preX))
		self.top.tab.stage.yPos.setText(str(self.act.preY))

		if (self.act.preX == 0) and (self.act.preY == 0):
			self.top.tab.stage.home.setEnabled(False)
		else:
			self.top.tab.stage.home.setEnabled(True)

		if (self.act.preX == 0):
			self.top.tab.stage.left.setEnabled(False)
		else:
			self.top.tab.stage.left.setEnabled(True)

		if (self.act.preX == STAGE_RANGE_X):
			self.top.tab.stage.right.setEnabled(False)
		else:
			self.top.tab.stage.right.setEnabled(True)

		if (self.act.preY == 0):
			self.top.tab.stage.up.setEnabled(False)
		else:
			self.top.tab.stage.up.setEnabled(True)

		if (self.act.preY == STAGE_RANGE_Y):
			self.top.tab.stage.down.setEnabled(False)
		else:
			self.top.tab.stage.down.setEnabled(True)

#New Plate Setting
	def filepathBtn(self):
		filepath = QFileDialog.getExistingDirectory(self, "File Path", "./")
		if (filepath == ""):
			versionBox = QMessageBox()
			versionBox.about(self, "Error", "File Path is empty !     ")
		else:
			self.top.tab.fpath.setText(filepath)

	def getPhotoData(self):
		self.initXpos = self.top.tab.initXpos.spin.value()
		self.initYpos = self.top.tab.initYpos.spin.value()
		self.delta = self.top.tab.delta.spin.value()
		self.xSteps = self.top.tab.xSteps.spin.value()
		self.ySteps = self.top.tab.ySteps.spin.value()

	def prescanBtn(self):
		# self.top.tab.preScan.setEnabled(False)
		self.getPhotoData()
		self.act.CreateNewPlate("", "", self.initXpos, self.initYpos, self.delta, self.xSteps, self.ySteps, 0, 0, False)
		self.thread1.start()

	def updatePlot(self, i, img, topten):
		temp = PHOTO_TEXT + str(i)
		self.top.tab.fpath.setText(temp)
		self.top.tab.fpath.repaint()
		# print(img)
		# self.top.tabPlot.plot1.setImage(img)
		self.top.tabPlot.plot1.ax.imshow(img)
		self.top.tabPlot.plot1.canvas.draw()
		self.top.tabPlot.plot1.canvas.flush_events()
		show_text = "Petri Dish Name = " + self.act.currentPlate.name + '\n' + \
					"Scan index = " + str(self.act.currentPlate.scan_index) + '\n'
		num_topten = len(topten)
		# print("topten = " + str(num_topten))
		for i in range(0, num_topten):
			reverse = num_topten - i - 1
			show_text = show_text + "[ TOP " + str(i+1) + ' ] : ' + \
						"Photo index = " + str(topten[reverse]['photo_index']) + '\n' + \
						"X = " + str(topten[reverse]['xpos']) + " , " + \
						"Y = " + str(topten[reverse]['ypos']) + " , " + \
						"Area = " + str(topten[reverse]['area']) + " , " + \
						"Rate = " + str(round(topten[reverse]['rate'],4)) + '\n'
		self.top.otputText.setText(show_text)

	def finished(self, findarea):
		if (findarea):
			self.thread2.quit()
			self.thread2.wait()
			# self.top.control.scan.setEnabled(self.cameraStatus)
		else:
			self.thread1.quit()
			self.thread1.wait()
			# self.top.tab.preScan.setEnabled(self.cameraStatus)

	def createBtn(self):
		self.getPhotoData()
		pname = self.top.tab.pname.edit.text()
		filepath = self.top.tab.fpath.text()
		maxNum = self.top.tab.maxNum.spin.value()
		calFact = self.top.tab.calFact.spin.value()
		photoText = filepath.find(PHOTO_TEXT)

		if (filepath == "") or (photoText != -1):
			versionBox = QMessageBox()
			versionBox.about(self, "Error", "File Path is empty !     ")
		elif (pname == ""):
			versionBox = QMessageBox()
			versionBox.about(self, "Error", "Petri Dish Name is empty !     ")
		else:
			self.act.CreateNewPlate(pname, filepath, self.initXpos, self.initYpos, self.delta, self.xSteps, self.ySteps, maxNum, calFact, True)
			self.top.control.pname_list.append(pname)
			self.top.control.pnameS.combo.clear()
			self.top.control.pnameS.combo.addItems(self.top.control.pname_list)
			# print(self.top.control.pname_list)
			filepath = ""
			self.top.tab.fpath.setText(filepath)
			self.top.control.delete.setEnabled(True)
			# self.top.control.scan.setEnabled(self.cameraStatus)

#Control
	def deleteBtn(self):
		self.top.control.delete.setEnabled(False)
		# self.top.control.scan.setEnabled(False)
		num = len(self.top.control.pname_list)
		if (num > 0):
			index = self.top.control.pnameS.combo.currentIndex()
			del_name = self.top.control.pname_list[index]
			self.act.delPlate(del_name)
			self.top.control.pname_list.remove(del_name)
			self.top.control.pnameS.combo.clear()
			self.top.control.pnameS.combo.addItems(self.top.control.pname_list)
			# print(self.top.control.pname_list)

			num = len(self.top.control.pname_list)
			if (num > 0):
				self.top.control.delete.setEnabled(True)
				# self.top.control.scan.setEnabled(self.cameraStatus)

	def imageTest(self):
		threshold = self.top.control.threshold.spin.value()
		maxNum = self.top.tab.maxNum.spin.value()
		now = self.act.getImage()
		# self.top.tabPlot.plot1.ax.imshow(self.act.img1)
		# now = self.act.getImage2("test.png")	# for TEST
		_, img4 = self.act.findAreaNew2(0, maxNum, threshold, now)
		self.top.tabPlot.plot1.ax.imshow(img4)
		self.top.tabPlot.plot1.canvas.draw()
		self.top.tabPlot.plot1.canvas.flush_events()

	def scanBtn(self):
		# self.top.control.scan.setEnabled(False)
		index = self.top.control.pnameS.combo.currentIndex()
		pname = self.top.control.pname_list[index]
		print("===== " + pname + " =====")
		self.act.setPlate(pname)
		self.thread2.start()

	def scanFuction(self):
		maxNum = self.top.tab.maxNum.spin.value()
		threshold = self.top.control.threshold.spin.value()
		tolerance = self.top.control.tolerance.spin.value()
		self.act.scanCurrentPlate(maxNum, threshold, tolerance, True)

	def saveFile(self):
		filename,_ = QFileDialog.getSaveFileName(self,"Save Data", "./" + READOUT_FILENAME, "Text Files (*.txt)")
		if (filename != ""):
			fil2a.array1DtoTextFile(filename, self.data, self.loggername)
	
	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

