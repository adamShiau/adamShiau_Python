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
import QST006_Widget as UI
import QST006_Action as ACT
import numpy as np 

RUN_PRE_INTERVAL = 100
DRAW_LEN = 50
DEFAULT_FILENAME2 = "Photon_Statics.txt"

TITLE_TEXT = "Quantum Optics Experiment"
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QST006 V1.02 \n\n" + \
" Copyright @ 2020 Quantaser \n" + \
" Maintain by Quantaser Photonics Co. Ltd "


class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger
		self.act = ACT.qst006Action(self.loggername)
		self.top = UI.mainWidget()
		self.mainUI()
		self.mainMenu()

		self.thread1 = QThread()
		self.thread2 = QThread()
		self.obj = ACT.qst006Thread(self.act.usb, self.loggername)
		self.obj2 = ACT.qst006Thread(self.act.usb, self.loggername)
		self.obj.moveToThread(self.thread1)
		self.obj.update_count.connect(self.updatePhotonCount)
		self.obj.finished.connect(self.stopPre)
		self.thread1.started.connect(self.obj.readCount)
		self.obj2.moveToThread(self.thread2)
		self.obj2.update_histo.connect(self.updateHisto)
		self.obj2.finished.connect(self.stopExp1)
		self.thread2.started.connect(self.obj2.readMemory)
		self.linkFunction()
		self.conUsb()
		self.count_array = np.zeros(0)

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

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	def addAccesoryFlag(self, loggername):
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")
	
	def linkFunction(self):
		self.top.usbCon.btn.clicked.connect(self.conUsb)
		self.top.tabWidget.runPre.clicked.connect(self.runPre)
		self.top.tabWidget.stopPre.clicked.connect(self.stopPre)
		self.top.tabWidget.runExp1.clicked.connect(self.runExp1)
		self.top.tabWidget.stopExp1.clicked.connect(self.stopExp1)
		self.top.tabWidget.save.clicked.connect(self.saveExp1)

	def conUsb(self):
		conStatus = self.act.usbConnect(baudrate = 115200, timeout=0.4)
		if (conStatus):
			self.top.usbCon.SetConnectText(Qt.black, "connection build", False)
			self.top.tabWidget.runPre.setEnabled(True)
			self.top.tabWidget.runExp1.setEnabled(True)
		else:
			self.top.usbCon.SetConnectText(Qt.red, "connection failed", True)

	def runPre(self):
		conStatus = self.act.usb.checkCom()
		if self.top.tabWidget.radio1.chBtn2.isChecked():
			channel = 1
		else:
			channel = 0
		
		if conStatus == False:
			self.top.usbCon.connectStatus.setText("connection failed")
			self.logger.warning("runPre USB connection failed")
		else:
			self.top.tabWidget.runPre.setEnabled(False)
			self.top.tabWidget.runExp1.setEnabled(False)
			self.top.tabWidget.stopPre.setEnabled(True)
			self.obj.channel = channel
			self.obj.interval = RUN_PRE_INTERVAL	
			self.thread1.start()

	def updatePhotonCount(self, counting):
		if (len(self.count_array) >= DRAW_LEN):
			self.count_array = self.count_array[1:DRAW_LEN]
		self.count_array = np.append(self.count_array, counting)
		self.top.tabWidget.countLabel.setText(str(counting))
		self.top.plot.ax.clear()
		self.top.plot.ax.plot(self.count_array)
		self.top.plot.figure.canvas.draw()
		self.top.plot.figure.canvas.flush_events()

	def stopPre(self):
		self.obj.countingFlag = False
		self.thread1.quit()
		self.top.tabWidget.runPre.setEnabled(True)
		self.top.tabWidget.runExp1.setEnabled(True)
		self.top.tabWidget.stopPre.setEnabled(False)
		
	def runExp1(self):
		conStatus = self.act.usb.checkCom()
		if self.top.tabWidget.radio2.chBtn2.isChecked():
			channel = 1
		else:
			channel = 0
		self.maxIndex = self.top.tabWidget.maxIndex.spin.value()
		
		if conStatus == False:
			self.top.usbCon.connectStatus.setText("connection failed")
			self.logger.warning("runExp1 USB connection failed")
		else:
			self.top.tabWidget.runPre.setEnabled(False)
			self.top.tabWidget.runExp1.setEnabled(False)
			self.top.tabWidget.stopExp1.setEnabled(True)
			self.top.tabWidget.save.setEnabled(False)

			
			self.obj2.channel = channel
			self.obj2.interval = self.top.tabWidget.interval.spin.value()
			self.obj2.totalTime = float(self.top.tabWidget.totalTime.spin.value())/1000.0
			
			self.thread2.start()

	def updateHisto(self, data):
		self.data = data
		#print(self.maxIndex)
		drawData = data[0:self.maxIndex]
		self.top.plot.ax.clear()
		self.top.plot.ax.plot(drawData)
		self.top.plot.figure.canvas.draw()
		self.top.plot.figure.canvas.flush_events()

	def stopExp1(self):
		self.obj2.histoFlag = False
		self.thread2.quit()
		self.top.tabWidget.runPre.setEnabled(True)
		self.top.tabWidget.runExp1.setEnabled(True)
		self.top.tabWidget.stopExp1.setEnabled(False)
		self.top.tabWidget.save.setEnabled(True)

	def saveExp1(self):
		saveData = []
		binData = np.linspace(0, ACT.DATA_COUNT-1, ACT.DATA_COUNT)
		#print(binData)
		#print(len(self.data))
		for i in range(ACT.DATA_COUNT):
			saveData.append(str(binData[i]) + " , " + str(self.data[i]))
		#print(SaveData)
		SaveFileName = QFileDialog.getSaveFileName(self,
						"Save Data",
						"./" + DEFAULT_FILENAME2,
						"Text Files (*.txt)")
		if (SaveFileName[0] != ''):
			#print(SaveFileName[0])
			fil2a.array1DtoTextFile(SaveFileName[0], saveData, self.loggername)
			self.top.tabWidget.save.setEnabled(False)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

