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
import QSS008_TEST_Widget_tab as UI
import QSS008_TEST_Action as ACT
import numpy as np 

MAIN_W = 1280
MAIN_H = 720
TOP_W = 1280
TOP_H = 720
BAR_W = 60
BAR_H = 60

HOST_NAME = "root"
HOST_PWD = "root"
HOST_PORT = 22

RUN_CMD = "LD_LIBRARY_PATH=/opt/redpitaya/lib ./FOG_MONITOR "


TITLE_TEXT = " Gryo Test Program "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS008 TEST V1.00 \n\n" + \
" Copyright @ 2019 \n" + \
" Maintain by Quantaser Photonics Co. Ltd "


class mainWindow(QMainWindow):
	def __init__(self, parent = None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.resize(MAIN_W+BAR_W, MAIN_H+BAR_H)
		self.move(50,50)
		self.loggername = "Total"
		self.addAccesoryFlag(self.loggername) # Add logger 
		self.act = ACT.qss008Action(self.loggername)
		self.top = UI.mainWidget()
		self.top.setMinimumSize(TOP_W, TOP_H)
		self.thread = QThread()
		self.mainUI()
		self.mainMenu()
		self.linkFunction()


	def mainUI(self):
		mainLayout = QGridLayout()
		self.scorollerarea = QScrollArea()
		self.scorollerarea.setWidget(self.top)
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.scorollerarea,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)
	
	def mainMenu(self):
		mainMenu = self.menuBar()
		menu_about = QAction("&Version", self)
		menu_about.triggered.connect(self.aboutBox)
		aboutMenu = mainMenu.addMenu("&About")
		aboutMenu.addAction(menu_about)

	def addAccesoryFlag(self, loggername):
		Qlogger.QuConsolelogger(loggername, logging.INFO)
		self.logger = logging.getLogger(loggername)

	def linkFunction(self):
		self.top.net.connectBtn.clicked.connect(lambda:self.sshConnect())
		self.top.run.clicked.connect(lambda:self.runAct())

	def sshConnect(self):
		ip = self.top.net.connectIP.text()
		host = "rp-"+str(ip)+".local"
		status = self.act.sshCnt(host, HOST_PORT, HOST_NAME, HOST_PWD)
		if status:
			self.top.net.SetConnectText(Qt.black, "Connection build")
			self.top.net.connectBtn.setEnabled(False)
		else:
			self.top.net.SetConnectText(Qt.red, "SSH connection failed")

	def runAct(self):
		count = self.top.datacount.spin.value()
		delay = self.top.deltaT.spin.value()
		time = float(count * delay) / 1000000.0
		cmd = RUN_CMD + str(count) + " " + str(delay)
		#self.loggeer.debug(cmd)
		#print(cmd)
		self.act.sendSSHCmd(cmd, False, time)
		flist = ["addr1.bin","addr2.bin", "addr3.bin", "addr4.bin"]
		self.act.ssh.getFtpFilelist(flist)
		error = fil2a.BinFiletoArray("addr1.bin", 4, 'i', self.loggername)
		#print(error)
		int1st = fil2a.BinFiletoArray("addr2.bin", 4, 'i', self.loggername)
		#print(int1st)
		int1st_div = fil2a.BinFiletoArray("addr3.bin", 4, 'i', self.loggername)
		#print(int1st_div)
		int2nd_div = fil2a.BinFiletoArray("addr4.bin", 4, 'i', self.loggername)
		#print(int2nd_div)

		self.top.pic.plot.ax.clear()
		self.top.pic.plot.ax.plot(error, color = 'blue', linestyle = '-', marker = '*', label = 'ERROR')
		self.top.pic.plot.figure.canvas.draw()
		self.top.pic.plot.figure.canvas.flush_events()

		self.top.pic.plot2.ax.clear()
		self.top.pic.plot2.ax.plot(int1st, color = 'red', linestyle = '-', marker = '*', label = '1st INT')
		self.top.pic.plot2.figure.canvas.draw()
		self.top.pic.plot2.figure.canvas.flush_events()

		self.top.pic.plot3.ax.clear()
		self.top.pic.plot3.ax.plot(int1st_div, color = 'green', linestyle = '-', marker = '*', label = '1st INT_Div')
		self.top.pic.plot3.figure.canvas.draw()
		self.top.pic.plot3.figure.canvas.flush_events()

		self.top.pic.plot4.ax.clear()
		self.top.pic.plot4.ax.plot(int2nd_div, color = 'blue', linestyle = '-', marker = '*', label = '2nd INT_Div')
		self.top.pic.plot4.figure.canvas.draw()
		self.top.pic.plot4.figure.canvas.flush_events()

	def aboutBox(self):
		versionBox = QMessageBox()
		versionBox.about(self, "Version", VERSION_TEXT)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())

