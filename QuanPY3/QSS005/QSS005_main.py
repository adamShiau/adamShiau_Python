import logging
import sys
import numpy as np 
sys.path.append("../")
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import py3lib.QuLogger as Qlogger
import QSS005_Widget as Q5
import QSS005_Action as Q5act


VERSION_TEXT = "0.01"

class mainWindow(QMainWindow):
	def __init__(self, parent=None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle("QSS005")
		self.resize(500,500)
		self.move(50,50)
		
		self.loggername ="Total"
		self.addAccesoryFlag(self.loggername) # Add logger 
		self.top = Q5.mainWidget()
		self.top.setMinimumSize(600, 600)
		self.act = Q5act.qss005Action(self.loggername)		
		self.mainUI()
		self.mainToolBar()
		self.mainMenu()
		self.connectFunction()
		
		
	def mainToolBar(self):
		funcbar = self.addToolBar("Function")
		funcbar.setMovable(True)
		funcbar.setObjectName("Function")
		self.act1 = self.createAction("MS1", self.sshConnectRun)
		funcbar.addAction(self.act1)

	def mainUI(self):
		mainLayout = QGridLayout()
		self.scorollerarea = QScrollArea()
		self.scorollerarea.setWidget(self.top)
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.scorollerarea,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)
	
	def mainMenu(self):
		Menu = self.menuBar()
		aboutmenu=Menu.addMenu("&About")
		act2 = self.createAction("MS2", self.sshConnectRun)
		aboutmenu.addAction(act2)

	def createAction(self, text, slot):
		action = QAction(text, self)
		self.connect(action, SIGNAL("triggered()"), slot)
		return action

	def addAccesoryFlag(self, loggername):
		Qlogger.QuConsolelogger(loggername, logging.DEBUG)
		self.datathread = QThread()
		self.gaugethread = QThread()
		self.plotxdata = np.zeros(10000)
		self.connectFlag = False
		self.ms1dataReady = False
		self.datathreadFlag = False

	def connectFunction(self):
		self.top.btn1.clicked.connect(self.sshConnectRun)
	
	def sshConnectRun(self):
		print "set Button status"
		ip ="rp-f05719.local"
		status = self.act.sshConnect(ip, 22, "root","root")
		if status:
			print "set Button status"
		else :
			print "print something in label and set False for all runable button"

	def ms1Run(self):
		self.act.moveToThread(self.datathread)
		self.act.update_array.connect(self.ms1Update)
		self.act.finished.connect(self.ms1Finished)
		self.act.started.connect(self.act.ms1Single)
		self.act.start()

	def ms1Update(self, array):
		Q5.label1.setText("plot array plist")
	
	def ms1Finished(self):
		self.act.quit()

	def ms1MultiRun(self):
		self.act.moveToThread(self.datathread)
		self.act.update_array.connect(self.ms1Update)
		self.act.finished.connect(self.ms1Finished)
		self.act.started.connect(self.act.ms1multiRun)
		self.act.start()

	def calibFindPeak(self):
		width = 3 # get some value for UI
		height =3 # get some value for UI
		peaks =self.act.calibra_findPeak(width, height)






	


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())