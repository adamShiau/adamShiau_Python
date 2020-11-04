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
import QST006B_Widget as UI
import QST006B_Action as ACT
import numpy as np 

DEFAULT_FILENAME2 = "Photon_Statics.txt"
Show_Num = 100

TEST_MODE = False

TITLE_TEXT = "Quantum Optics Experiment"
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QST006B V1.01 \n\n" + \
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

		self.mainInit()
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.conUsb()

	def mainInit(self):
		self.thread1 = QThread()
		self.obj = ACT.qst006Thread(self.act.usb, self.loggername)
		self.obj.moveToThread(self.thread1)
		self.thread1.started.connect(self.obj.readCount)
		self.obj.update_count.connect(self.updatePhotonCount)
		self.obj.finished.connect(self.finishExp)

		self.countA_array = np.zeros(0)
		self.countB_array = np.zeros(0)
		self.countAB_array = np.zeros(0)
		self.count_dt_array = np.zeros(0)

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
		self.logger = logging.getLogger(loggername)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")

	def linkFunction(self):
		self.top.usbCon.btn.clicked.connect(self.conUsb)
		self.top.start.clicked.connect(self.startExp)
		self.top.stop.clicked.connect(self.stopExp)
		self.top.save.clicked.connect(self.saveExp)

	def conUsb(self):
		conStatus = self.act.usbConnect(baudrate = 115200, timeout = 0.4)
		if (conStatus):
			self.top.usbCon.SetConnectText(Qt.black, "connection build", False)
			self.top.start.setEnabled(True)
		else:
			self.top.usbCon.SetConnectText(Qt.red, "connection failed", True)

	def startExp(self):
		if (TEST_MODE):
			conStatus = True
		else:
			conStatus = self.act.usb.checkCom()

		if (conStatus  == False):
			self.top.usbCon.SetConnectText(Qt.red, "connection failed", True)
			self.logger.warning("USB connection failed")
		else:
			self.countA_array = np.zeros(0)
			self.countB_array = np.zeros(0)
			self.countAB_array = np.zeros(0)
			self.count_dt_array = np.zeros(0)
			# print("conStatus = " + str(conStatus))
			self.top.start.setEnabled(False)
			self.top.stop.setEnabled(True)
			self.top.save.setEnabled(False)

			self.thread1.start()
			self.obj.countingFlag = True

	def updatePhotonCount(self, data1, data2, data3, dt):
		self.countA_array = np.append(self.countA_array, data1/10)
		self.countB_array = np.append(self.countB_array, data2/10)
		self.countAB_array = np.append(self.countAB_array, data3/10)
		self.count_dt_array = np.append(self.count_dt_array, dt)
		currnet_len = len(self.countA_array)
		if (currnet_len > Show_Num):
			diff = currnet_len - Show_Num
			showA_array = self.countA_array[diff:]
			showB_array = self.countB_array[diff:]
			showAB_array = self.countAB_array[diff:]
			show_dt_array = self.count_dt_array[diff:]
		else:
			showA_array = self.countA_array
			showB_array = self.countB_array
			showAB_array = self.countAB_array
			show_dt_array = self.count_dt_array

		self.top.plot.ax1.clear()
		self.top.plot.ax2.clear()
		self.top.plot.ax1.plot(show_dt_array, showA_array, color = 'blue', linestyle = '-', label = "A count")
		self.top.plot.ax1.plot(show_dt_array, showB_array, color = 'red', linestyle = '-', label = "B count")
		self.top.plot.ax1.legend()
		self.top.plot.ax2.plot(show_dt_array, showAB_array, color = 'green', linestyle = '-', label = "AB count")
		self.top.plot.ax2.legend()
		self.top.plot.ax2.set_xlabel("dT (S)")
		self.top.plot.figure.canvas.draw()
		self.top.plot.figure.canvas.flush_events()

	def stopExp(self):
		self.obj.countingFlag = False

	def finishExp(self):
		self.thread1.quit()
		self.thread1.wait()
		self.top.start.setEnabled(True)
		self.top.stop.setEnabled(False)
		self.top.save.setEnabled(True)

	def saveExp(self):
		saveData = []
		num = len(self.countA_array)
		binData = np.linspace(0, num-1, num)
		saveData.append("time , A count , B count , AB count")
		for i in range(num):
			saveData.append(str("%2.3f" % self.count_dt_array[i]) + " , " + str(self.countA_array[i]) + " , " + str(self.countB_array[i]) + " , " + str(self.countAB_array[i]))
		#print(SaveData)
		SaveFileName = QFileDialog.getSaveFileName(self,
						"Save Data",
						"./" + DEFAULT_FILENAME2,
						"Text Files (*.txt)")
		if (SaveFileName[0] != ''):
			#print(SaveFileName[0])
			fil2a.array1DtoTextFile(SaveFileName[0], saveData, self.loggername)
			self.top.save.setEnabled(False)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

