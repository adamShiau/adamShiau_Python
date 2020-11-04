import sys
sys.path.append("../")
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import QSS005_Action as Q5act


def testfunction(self):
	print "test"

class Ms1Dialog(QDialog):
	def __init__(self, parent =None):
		super(Ms1Dialog, self).__init__(parent)
		self.btn1 = QPushButton("OK")
		self.input = QLineEdit()
		self.paramlist=[]
		self.Ms1Layout()
		self.connectFunction()


	def Ms1Layout(self):
		ms1layout = QGridLayout()
		ms1layout.addWidget(self.btn1,0,0,1,1)
		ms1layout.addWidget(self.input,0,1,1,1)
		self.setLayout(ms1layout)

	def connectFunction(self):
		self.btn1.clicked.connect(self.okButtonPress)

	def okButtonPress(self):
		self.paramlist=[self.input.text(),10,1]
		print "hello"
		self.close()
	
	@staticmethod
	def getParameter(parent =None):
		dialog = Ms1Dialog(parent)
		result = dialog.exec_()
		return dialog.paramlist

class mainWidget(QWidget):
	def __init__(self, parent =None):
		super(QWidget, self).__init__(parent)
		
		self.mainWidgetLayout()
		self.connectFunction()

	def mainWidgetLayout(self):
		topLayout = QGridLayout()
		self.btn1 = QPushButton("connect")
		self.btn2 = QPushButton("BT2")
		self.btn3 = QPushButton("BT3")
		self.label1 = QLabel()
		self.label2 = QLabel()
		self.label1.setText("Label 1")
		self.label2.setText("Label 2")
		topLayout.addWidget(self.btn1, 0,0,1,1)
		topLayout.addWidget(self.btn2, 0,1,1,1)
		topLayout.addWidget(self.btn3, 0,2,1,1)
		topLayout.addWidget(self.label1, 1,0,1,3)
		topLayout.addWidget(self.label2, 2,0,3,3)
		self.setLayout(topLayout)

	
	def connectFunction(self): # define button function
		self.btn1.clicked.connect(testfunction)
		self.btn2.clicked.connect(testfunction)
		self.btn3.clicked.connect(testfunction)



	