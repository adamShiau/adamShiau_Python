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
import QSS011_TEST_Widget as UI
import QSS011_TEST_Action as ACT


TITLE_TEXT = " QSS011 "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS011 TEST V1.10 \n\n" + \
" Copyright @ 2020 TAIP \n" + \
" Maintain by Quantaser Photonics Co. Ltd "

ERROR_TEXT = "COM port return error, \n\n" + \
"please press START button again."

class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger
		self.top = UI.mainWidget()
		self.act = ACT.qss011Action(self.loggername)
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		#self.loadUIpreset()
		self.usbConnect()

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
		self.top.usb.btn.clicked.connect(self.usbConnect)

		#Btn connect
		self.top.getadc.clicked.connect(self.getADCButton)

	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")

	def usbConnect(self):
		self.usbConnStatus = self.act.usbConnect()
		if self.usbConnStatus:
			self.top.usb.SetConnectText(Qt.black,"Connection build", False)
			self.top.getadc.setEnabled(True)
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)

	def loadUIpreset(self):
		self.top.test.freq.spin.setValue(self.act.freq)
		self.top.test.phase.spin.setValue(self.act.phase)

	def getADCButton(self):
		data = self.act.getADC()
		self.top.plot.clear()
		self.top.plot.plot(data)

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

