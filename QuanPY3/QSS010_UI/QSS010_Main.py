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
import QSS010_Widget as UI
import QSS010_Action as ACT
import numpy as np
import datetime

CV_FILENAME = "CV_data.txt"
IT_FILENAME = "IT_data.txt"


TITLE_TEXT = " Acdemic Sincica GRC ElectroChemical Analysis "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS010 V1.10 \n\n" + \
" Copyright @ 2019 TAIP \n" + \
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
		self.act = ACT.qss010Action(self.loggername)
		self.cvact = ACT.CVaction(self.act.COM, self.act.paralist, self.loggername)
		self.itact = ACT.ITaction(self.act.COM, self.act.paralist, self.loggername)
		self.thread1 = QThread()
		self.thread2 = QThread()
		self.cvact.moveToThread(self.thread1)
		self.itact.moveToThread(self.thread2)
		self.mainUI()
		self.mainMenu()
		self.linkFunction()
		self.loadUIpreset()
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

		#thread connect
		self.thread1.started.connect(self.cvact.CVstart)
		self.thread2.started.connect(self.itact.ITstart)

		#signal connect
		self.cvact.update_CV.connect(self.update_CV)
		self.cvact.stop_CV.connect(lambda:self.stop_CV(False))
		self.cvact.finished.connect(self.finished_CV)

		self.itact.update_IT.connect(self.update_IT)
		self.itact.stop_IT.connect(lambda:self.stop_IT(False))
		self.itact.finished.connect(self.finished_IV)

		#Btn connect
		self.top.taball.CV.start.clicked.connect(self.start_CV)
		self.top.taball.CV.stop.clicked.connect(lambda:self.stop_CV(True))
		self.top.taball.CV.save.clicked.connect(self.save_CV)

		self.top.taball.IT.start.clicked.connect(self.start_IT)
		self.top.taball.IT.stop.clicked.connect(lambda:self.stop_IT(True))
		self.top.taball.IT.save.clicked.connect(self.save_IT)

	def addAccesoryFlag(self, loggername):
		self.logger = logging.getLogger(loggername)
		#Qlogger.QuConsolelogger(loggername, logging.ERROR)
		Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")

	def usbConnect(self):
		self.usbConnStatus = self.act.usbConnect()
		if self.usbConnStatus:
			self.top.usb.SetConnectText(Qt.black,"Connection build", False)
			self.top.taball.CV.start.setEnabled(True)
			self.top.taball.IT.start.setEnabled(True)
		else:
			self.top.usb.SetConnectText(Qt.red,"Connect failed", True)

	def loadUIpreset(self):
		self.top.taball.CV.startV.spin.setValue(self.act.startV)
		self.top.taball.CV.dv.spin.setValue(self.act.dv)
		self.top.taball.CV.endV.spin.setValue(self.act.endV)
		self.top.taball.CV.dt.spin.setValue(self.act.CVdt)
		self.top.taball.CV.rate.spin.setValue(self.act.CVrate)
		self.top.taball.CV.quiet.spin.setValue(self.act.CVquiet)

		self.top.taball.IT.setV.spin.setValue(self.act.Vset)
		self.top.taball.IT.dt.spin.setValue(self.act.ITdt)
		self.top.taball.IT.rate.spin.setValue(self.act.ITrate)
		self.top.taball.IT.quiet.spin.setValue(self.act.ITquiet)

		self.top.header.edit.setText(self.act.header)

	def start_CV (self):
		self.act.startV = self.top.taball.CV.startV.spin.value()
		self.act.dv = self.top.taball.CV.dv.spin.value()
		self.act.endV = self.top.taball.CV.endV.spin.value()
		self.act.CVdt = self.top.taball.CV.dt.spin.value()
		self.act.CVrate = self.top.taball.CV.rate.spin.value()
		self.act.CVquiet = self.top.taball.CV.quiet.spin.value()
		self.top.taball.CV.start.setEnabled(False)
		self.top.taball.CV.stop.setEnabled(True)
		self.top.taball.IT.start.setEnabled(False)
		self.time_array = np.empty(0)
		self.vout = np.empty(0)
		self.iout = np.empty(0)
		self.act.writePreset()
		# self.cvact.setParam(startV, dv, endV, dt, rate)
		self.cvact.setParam()
		self.start_time = time.time()
		self.draw_begin = False
		self.cvact.CVrun = True
		self.thread1.start()
	
	def start_IT(self):
		self.act.Vset = self.top.taball.IT.setV.spin.value()
		self.act.ITdt = self.top.taball.IT.dt.spin.value()
		self.act.ITrate = self.top.taball.IT.rate.spin.value()
		self.act.ITquiet = self.top.taball.IT.quiet.spin.value()
		self.top.taball.CV.start.setEnabled(False)
		self.top.taball.IT.start.setEnabled(False)
		self.top.taball.IT.stop.setEnabled(True)
		self.time_array = np.empty(0)
		self.iout = np.empty(0)
		self.act.writePreset()
		#self.itact.setParam(vset, dt, rate)
		self.itact.setParam()
		self.start_time = time.time()
		self.draw_begin = False
		self.itact.ITrun = True
		self.thread2.start()
	
	def stop_CV(self, flag):
		self.cvact.CVrun = False
		self.act.COM.writeLine("1")
		self.top.taball.CV.start.setEnabled(self.usbConnStatus)
		self.top.taball.CV.stop.setEnabled(False)
		self.top.taball.CV.save.setEnabled(True)
		self.top.taball.IT.start.setEnabled(self.usbConnStatus)
		if (flag == False):
			self.errorBox()

	def stop_IT(self, flag):
		self.itact.ITrun = False
		self.act.COM.writeLine("1")
		self.top.taball.CV.start.setEnabled(self.usbConnStatus)
		self.top.taball.IT.start.setEnabled(self.usbConnStatus)
		self.top.taball.IT.stop.setEnabled(False)
		self.top.taball.IT.save.setEnabled(True)
		if (flag == False):
			self.errorBox()

	def update_CV(self, cv_time, vout, iout):
		# print(cv_time)
		# print(vout)
		# print(iout)
		self.top.plot.ax1.clear()
		self.top.plot.ax2.clear()
		self.top.plot.ax3.clear()

		run_time = time.time() - self.start_time
		if (run_time > self.act.CVquiet):
			if (self.draw_begin == False):
				quiet_left_str = "Quiet Time Left : 0"
				self.top.taball.CV.quiet_left.setText(quiet_left_str)
				self.draw_begin = True

			self.time_array = np.append(self.time_array, cv_time)
			self.vout = np.append(self.vout, vout)
			self.iout = np.append(self.iout, iout)

			self.top.plot.ax1.plot(self.vout, self.iout)
			self.top.plot.ax2.plot(self.time_array, self.vout)
			self.top.plot.ax3.plot(self.time_array, self.iout)

			self.top.plot.ax1.set_xlabel("Vwe (V)")
			self.top.plot.ax1.set_ylabel("I out")
			self.top.plot.ax2.set_xlabel("t (s)")
			self.top.plot.ax2.set_ylabel("Vwe (V)")
			self.top.plot.ax3.set_xlabel("t (s)")
			self.top.plot.ax3.set_ylabel("I out")
		else:
			quiet_left = self.act.CVquiet - int(run_time)
			quiet_left_str = "Quiet Time Left : " + str(quiet_left)
			self.top.taball.CV.quiet_left.setText(quiet_left_str)

		self.top.plot.figure.canvas.draw()
		self.top.plot.figure.canvas.flush_events()

	def update_IT(self, it_time, iout):
		# print(it_time)
		# print(iout)
		self.top.plot.ax1.clear()
		self.top.plot.ax2.clear()
		self.top.plot.ax3.clear()

		run_time = time.time() - self.start_time
		if (run_time > self.act.ITquiet):
			if (self.draw_begin == False):
				quiet_left_str = "Quiet Time Left : 0"
				self.top.taball.IT.quiet_left.setText(quiet_left_str)
				self.draw_begin = True

			self.time_array = np.append(self.time_array, it_time)
			self.iout = np.append(self.iout, iout)
			self.top.plot.ax1.plot(self.time_array, self.iout)

			self.top.plot.ax1.set_xlabel("t (s)")
			self.top.plot.ax3.set_ylabel("I out")
		else:
			quiet_left = self.act.ITquiet - int(run_time)
			quiet_left_str = "Quiet Time Left : " + str(quiet_left)
			self.top.taball.IT.quiet_left.setText(quiet_left_str)

		self.top.plot.figure.canvas.draw()
		self.top.plot.figure.canvas.flush_events()

	def finished_CV(self):
		self.thread1.quit()
		self.thread1.wait()

	def finished_IV(self):
		self.thread2.quit()
		self.thread2.wait()

	def save_CV(self):
		self.act.header = self.top.header.edit.text()
		self.act.writePreset()
		SaveFileName,_ = QFileDialog.getSaveFileName(self,"Save CV Data",CV_FILENAME,"Text Files (*.txt)")
		if (SaveFileName != ''):
			curr_time = datetime.datetime.now()
			fileheader = self.act.header+"\n"+str(curr_time)+"\n"+"time (ms), Vout (mV), Iout"
			temp = np.array(self.time_array)*1000
			self.time_array = temp.astype('int32')
			tempdata = np.array([self.time_array, self.vout, self.iout], np.int32)
			tempdata = np.transpose(tempdata)
			fil2a.list2DtoTextFile(SaveFileName,tempdata,",",self.loggername, fileheader)

	def save_IT(self):
		self.act.header = self.top.header.edit.text()
		self.act.writePreset()
		SaveFileName,_ = QFileDialog.getSaveFileName(self,"Save IT Data",IT_FILENAME,"Text Files (*.txt)")
		if (SaveFileName != ''):
			curr_time = datetime.datetime.now()
			fileheader = self.act.header+"\n"+str(curr_time)+"\n"+"time (ms), Iout"
			temp = np.array(self.time_array)*1000
			self.time_array = temp.astype('int32')
			tempdata = np.array([self.time_array, self.iout], np.int32)
			tempdata = np.transpose(tempdata)
			fil2a.list2DtoTextFile(SaveFileName,tempdata,",",self.loggername, fileheader)

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

