import logging
import sys
sys.path.append("../")
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import py3lib.QuLogger as Qlogger
import QSS005Widgettemp as Q5
import QSS005_Action as Q5act


VERSION_TEXT = "0.01"

class mainWindow(QMainWindow):
	def __init__(self, parent=None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle("QSS005")
		self.resize(500,500)
		self.move(50,50)
		self.top.setMinimumSize(600, 600)
		self.loggername ="Total"
		self.addAccesoryFlag(self.loggername) # Add logger 
		self.top = Q5.mainWidget()
		self.act = Q5act.qss005Action(self.loggername)		
		self.mainUI()
		self.mainToolBar()
		self.mainMenu()
		
		
	def mainToolBar(self):
		funcbar = self.addToolBar("Function")
		funcbar.setMovable(True)
		funcbar.setObjectName("Function")
		self.act1 = self.createAction("MS1", self.testAction2)
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
		act2 = self.createAction("MS2", self.testAction)
		aboutmenu.addAction(act2)

	def createAction(self, text, slot):
		action = QAction(text, self)
		self.connect(action, SIGNAL("triggered()"), slot)
		return action

	def addAccesoryFlag(self, loggername):
		Qlogger.QuConsolelogger(loggername, logging.DEBUG)
		self.datathread = Qthread()
		self.gaugethread = Qthread()
		self.plotxdata = np.zeros(10000)
		self.connectFlag = False
		self.ms1dataReady = False
		self.calibParamUpdate = True
		self.datathreadFlag = False

	def connectAction(self):
		ip ="rp-f05719.local"
		status = Q5.sshConnect(ip, 22, "root","root")
		if status:
			print "set Button status"
		else :



			print "print something in label and set False for all runable button"

	def ms1Run(self):
		self.act.moveToThread(self.datathread)

	def ms1Update(self, array):
		arrayLength = len(array)
		Q5.label1.setText("plot array plist")

	def calibUpdate(self, length):


	
	def testAction(self):
		logger = logging.getLogger("Total")
		logger.debug('tt')
		print 3
	def testAction2(self):
		a =Q5.Ms1Dialog.getParameter()
		print a



if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
