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
import QSZ002_Widget as UI
import QSZ002_Action as ACT
import numpy as np
import datetime

READOUT_FILENAME ="signal"
TITLE_TEXT = "  "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSZ002 V1.00 \n\n" + \
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
		self.act = ACT.qsz002Spectrum(self.loggername)
		self.thread1 = QThread()
		self.act.moveToThread(self.thread1)
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		#self.setMinimumSize(1200,800)

	def mainUI(self):
		mainLayout = QGridLayout()
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.top,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)
	
	def mainMenu(self):
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu("File")
		menu_save = QAction("&Save",self)
		fileMenu.addAction(menu_save)
		menu_save.triggered.connect(self.saveFile)

		menu_about = QAction("&Version", self)
		menu_about.triggered.connect(self.aboutBox)
		aboutMenu = mainMenu.addMenu("&About")
		aboutMenu.addAction(menu_about)

	def linkFunction(self):
		self.top.open.btn.clicked.connect(self.Connect)
		self.thread1.started.connect(self.act.runSpectrum)
		self.top.setting.runSpectrum.clicked.connect(self.runSpectrum)
		self.top.setting.control.clicked.connect(self.runControl)
		self.top.setting.stop.clicked.connect(self.stop)
		self.act.update.connect(self.updatePlot)
		self.act.finished.connect(self.finished)
	
	def addAccesoryFlag(self, loggername):
		Qlogger.QuConsolelogger(loggername, logging.DEBUG)
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuFilelogger(loggername, logging.WARNING, "log.txt")

	def Connect(self):
		rate = self.top.setting.rate.spin.value()
		status =self.act.devOpen("1FE9:7101",rate)
		print (status)

	def setValue(self):
		self.act.minWave = self.top.setting.minWavelength.spin.value()
		self.act.maxWave = self.top.setting.maxWavelength.spin.value()
		self.act.intTime = self.top.setting.intTime.spin.value()
		self.act.avgNumber = self.top.setting.avgNumber.spin.value()
		self.act.threshold = self.top.setting.threshold.spin.value()
		self.act.filterLevel = self.top.setting.filterLevel.spin.value()
		self.act.filterOn = self.top.setting.useFilter.isChecked()
	
	def runSpectrum(self):
		self.setValue()
		self.act.enablePump = False
		self.act.runFlag = True
		self.data = np.empty(0)
		self.thread1.start()

	
	def runControl(self):
		self.setValue()
		self.act.enablePump = True
		self.act.runFlag = True
		self.data = np.empty(0)
		self.thread1.start()

	def stop(self):
		if self.act.enablePump:
			self.act.setPumpStop()
		self.act.runFlag = False

	def updatePlot(self,wavelenth, intensity, filtered, data):
		self.top.plot.ax1.clear()
		self.top.plot.ax2.clear()
		self.top.plot.ax1.plot(wavelenth, intensity)
		self.top.plot.ax1.plot(wavelenth, filtered)
		self.data = np.append(self.data, data)
		self.top.plot.ax2.plot(self.data)
		self.top.plot.figure.canvas.draw()
		self.top.plot.figure.canvas.flush_events()
	def finished(self):
		self.thread1.quit()
		self.thread1.wait()

	def saveFile(self):
		filename,_ =QFileDialog.getSaveFileName(self,"Save Data", "./" + READOUT_FILENAME, "Text Files (*.txt)")
		if (filename!=""):
			fil2a.array1DtoTextFile(filename, self.data, self.loggername)

	
	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

