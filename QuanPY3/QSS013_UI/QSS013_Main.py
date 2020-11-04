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
import QSS013_Widget as UI
import QSS013_Action as ACT
import numpy as np
import datetime

CH_INDEX = 0
MODE_INDEX = 1
HEADER_INDEX = 2
TOTAL_INDEX = 3

SHOW_DATA_NUM = 3000
READOUT_FILENAME = "Signal_Read_Out.txt"

TITLE_TEXT = "QSS013"
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS013 V1.00 \n\n" + \
" Copyright @ 2020 Quantaser \n" + \
" Maintain by Quantaser Photonics Co. Ltd "


class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger
		self.top = UI.mainWidget()
		self.act = ACT.qss013Act(self.loggername)

		self.mainUI()
		self.mainMenu()
		self.mainInit()
		self.linkFunction()
		
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

	def mainInit(self):
		self.connectStatus = self.ConnectRun()
		self.getPreset()
		self.thread = QThread()
		self.act.moveToThread(self.thread)
		self.thread.started.connect(self.act.readData)
		self.act.update.connect(self.updatePlot)
		self.act.finished.connect(self.finished)
		self.all_data = np.empty(0)
		self.all_time = np.empty(0)
		self.emit_index = 0

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)

	def addAccesoryFlag(self, loggername):
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")
	
	def linkFunction(self):
		self.top.usb.btn.clicked.connect(self.ConnectRun)
		self.top.timeBtn.clicked.connect(self.callTimeDialog)
		self.top.run.clicked.connect(self.runCmd)
		self.top.stop.clicked.connect(self.stopCmd)
		self.top.save.clicked.connect(self.saveData)

	def ConnectRun(self):
		self.connectStatus = self.act.usbConnect()
		# print("main connect status = " + str(self.connectStatus) )
		if (self.connectStatus == 0):
			self.top.usb.SetConnectText(Qt.black,"Connection build", False)
			self.top.run.setEnabled(True)
		elif (self.connectStatus == 1):
			self.top.usb.SetConnectText(Qt.red,"Device not found", True)
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)

	def callTimeDialog(self):
		timeDialog = UI.timeDialog(self.act.timePreset)
		self.act.timePreset = timeDialog.getParameter(self.act.timePreset)
		self.act.savePreset(1)

	def getPreset(self):
		self.selectCh = int(self.act.preset[CH_INDEX])
		self.selectMode = int(self.act.preset[MODE_INDEX])
		fileheader = self.act.preset[HEADER_INDEX]

		if (self.selectCh == 4):
			self.top.ch.ch4.setChecked(True)
		elif (self.selectCh == 3):
			self.top.ch.ch3.setChecked(True)
		elif (self.selectCh == 2):
			self.top.ch.ch4.setChecked(True)
		else:
			self.top.ch.ch1.setChecked(True)

		if (self.selectMode == 3):
			self.top.mode.mode3.setChecked(True)
		elif (self.selectMode == 2):
			self.top.mode.mode2.setChecked(True)
		else:
			self.top.mode.mode1.setChecked(True)

		self.top.FHedit.edit.setText(fileheader)

	def runCmd(self):
		if self.top.ch.ch4.isChecked():
			self.selectCh = 4
		elif self.top.ch.ch3.isChecked():
			self.selectCh = 3
		elif self.top.ch.ch2.isChecked():
			self.selectCh = 2
		else:
			self.selectCh = 1
		self.act.preset[CH_INDEX] = self.selectCh

		if self.top.mode.mode3.isChecked():
			self.selectMode = 3
		elif self.top.mode.mode2.isChecked():
			self.selectMode = 2
		else:
			self.selectMode = 1
		self.act.preset[MODE_INDEX] = self.selectMode
		self.act.savePreset(0)

		self.top.run.setEnabled(False)
		self.top.stop.setEnabled(True)

		self.act.sendUsbCmd()
		self.all_data = np.empty(0)
		self.all_time = np.empty(0)
		self.emit_index = 0
		self.act.runFlag = True
		self.thread.start()

	def updatePlot(self, data, time_array):
		self.all_data = np.append(self.all_data, data)
		self.all_time = np.append(self.all_time, time_array)
		data_len = len(self.all_data)
		# print("data_len = " + str(data_len))
		time_len = len(self.all_time)
		# print("time_len = " + str(time_len))
		self.emit_index = self.emit_index + 1
		if (self.emit_index > 1):
			# print("draw plot")
			self.top.plot.ax.clear()
			self.top.plot.ax.set_ylabel("Vlotage(V)")
			self.top.plot.ax.set_xlabel("dT(ms)")
			# draw all data
			# self.top.plot.ax.plot(self.all_time, self.all_data, color = "blue", linestyle = '-')
			# draw only last show_num data
			self.top.plot.ax.plot(self.all_time[-SHOW_DATA_NUM:], self.all_data[-SHOW_DATA_NUM:], color = "blue", linestyle = '-')
			self.top.plot.figure.canvas.draw()
			self.emit_index = 0

	def stopCmd(self):
		self.act.runFlag = False
		self.top.run.setEnabled(True)
		self.top.stop.setEnabled(False)
		self.top.save.setEnabled(True)

	def finished(self):
		self.thread.quit()
		self.thread.wait()

	def saveData(self):
		fileheader = self.top.FHedit.edit.text()
		self.act.preset[HEADER_INDEX] = fileheader
		self.act.savePreset(0)

		SaveFileName,_ = QFileDialog.getSaveFileName(self,
						"Save Data",
						"./" + READOUT_FILENAME,
						"Text Files (*.txt)")
		if (SaveFileName != ''):
			curr_time = datetime.datetime.now()
			fileheader = self.top.FHedit.edit.text()+"\n"+str(curr_time)+"\n"+"dT(ms), Vlotage(V)"
			tempdata = np.array([self.all_time, self.all_data], np.float64)
			tempdata = np.transpose(tempdata)
			fil2a.list2DtoTextFile(SaveFileName,tempdata,",",self.loggername, fileheader)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

