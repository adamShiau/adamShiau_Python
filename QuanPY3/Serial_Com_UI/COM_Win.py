import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
sys.path.append("../")
from py3lib.COMPort import *

Timeout = 2

class connectBlock():
	def __init__(self):
		self.connectGroupBox = QGroupBox("USB Connection")
		self.connectStatus = QLabel()
		self.connectBtn = QPushButton("Connect")
		self.connectStatus.setAlignment(Qt.AlignLeft)

		self.baudrate = QComboBox()
		self.baudrate_list = ["9600" , "115200"]
		self.baudrate.addItems(self.baudrate_list)
		self.baudrate.setCurrentIndex(0)

	def connectBlockWidget(self):   
		connectLayout = QVBoxLayout()
		connectLayout.addWidget(self.baudrate)
		connectLayout.addWidget(self.connectStatus)
		connectLayout.addWidget(self.connectBtn)
		self.connectGroupBox.setLayout(connectLayout)
		self.connectGroupBox.show()
		return self.connectGroupBox
	
class inputGroup(QWidget):
	def __init__(self, parent=None):
		self.GroupBox = QGroupBox("input")
		self.text = QLabel("Send data = ")
		self.input = QLineEdit()
		self.radioBtnA = QRadioButton("ASCII", self.GroupBox)
		self.radioBtnA.setChecked(True)  # select by default
		self.radioBtnH = QRadioButton("HEX", self.GroupBox)

	def inputGroupUI(self):
		GroupLayout = QGridLayout()
		GroupLayout.addWidget(self.radioBtnA,0,1,1,1)
		GroupLayout.addWidget(self.radioBtnH,0,2,1,1)
		GroupLayout.addWidget(self.text,1,0,1,1)
		GroupLayout.addWidget(self.input,1,1,1,2)
		GroupLayout.setRowStretch(0, 1)
		GroupLayout.setRowStretch(1, 1)
		GroupLayout.setColumnStretch(0, 1)
		GroupLayout.setColumnStretch(1, 1)
		GroupLayout.setColumnStretch(2, 1)
		#self.group.setLayout(GroupLayout)
		self.GroupBox.setLayout(GroupLayout)
		self.GroupBox.show()
		return self.GroupBox

class outputGroup(QWidget):
	def __init__(self, parent=None):
		self.GroupBox = QGroupBox("output")
		self.output = QTextEdit()
		#self.radioBtnA = QRadioButton("ASCII", self.GroupBox)
		#self.radioBtnA.setChecked(True)  # select by default
		#self.radioBtnH = QRadioButton("HEX", self.GroupBox)

	def outputGroupUI(self):
		GroupLayout = QGridLayout()
		#GroupLayout.addWidget(self.radioBtnA,0,0,1,1)
		#GroupLayout.addWidget(self.radioBtnH,0,1,1,1)
		GroupLayout.addWidget(self.output,0,0,1,1)
		GroupLayout.setRowStretch(0, 1)
		#GroupLayout.setRowStretch(1, 1)
		GroupLayout.setColumnStretch(0, 1)
		#GroupLayout.setColumnStretch(1, 1)
		#self.group.setLayout(GroupLayout)
		self.GroupBox.setLayout(GroupLayout)
		self.GroupBox.show()
		return self.GroupBox

class mainWindow(QMainWindow):
	def __init__(self, parent=None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle("Serial Read Write")
		self.resize(960,640)
		self.move(50,50)
		self.com = connectBlock()
		self.inputGroup = inputGroup()
		self.outputGroup = outputGroup()
		#self.usb = COMPort.FT232(9600, 2)
		#self.usb = FT232(9600, 2)
		self.usb = FT232("Total")
		#self.setButtonStatus()
		self.flushBtn = QPushButton("Flush")
		self.sendBtn = QPushButton("Send")
		self.sendReadBtn = QPushButton("Send / Read Line")
		self.readLineBtn = QPushButton("Read Line")
		self.readBtn = QPushButton("Read")
		self.byte = QLineEdit()
		self.label = QLabel("bytes")

		self.com.connectBtn.clicked.connect(lambda:self.buildConnect())
		self.flushBtn.clicked.connect(lambda:self.flushBtnRun())
		self.sendBtn.clicked.connect(lambda:self.sendBtnRun())
		self.sendReadBtn.clicked.connect(lambda:self.sendReadBtnRun())
		self.readLineBtn.clicked.connect(lambda:self.readLineBtnRun())
		self.readBtn.clicked.connect(lambda:self.readBtnRun())

		self.flushBtn.setEnabled(False)
		self.sendBtn.setEnabled(False)
		self.sendReadBtn.setEnabled(False)
		self.readLineBtn.setEnabled(False)
		self.readBtn.setEnabled(False)

		self.main_UI()


	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.inputGroup.inputGroupUI(),0,0,1,4)
		mainLayout.addWidget(self.com.connectBlockWidget(),0,4,1,3)
		mainLayout.addWidget(self.flushBtn,1,0,1,1)
		mainLayout.addWidget(self.sendBtn,1,1,1,1)
		mainLayout.addWidget(self.sendReadBtn,1,2,1,1)
		mainLayout.addWidget(self.readLineBtn,1,3,1,1)
		mainLayout.addWidget(self.readBtn,1,4,1,1)
		mainLayout.addWidget(self.byte,1,5,1,1)
		mainLayout.addWidget(self.label,1,6,1,1)
		mainLayout.addWidget(self.outputGroup.outputGroupUI(),2,0,1,7)
		mainLayout.setColumnStretch(0, 2)
		mainLayout.setColumnStretch(1, 2)
		mainLayout.setColumnStretch(2, 2)
		mainLayout.setColumnStretch(3, 2)
		mainLayout.setColumnStretch(4, 1)
		mainLayout.setColumnStretch(5, 1)
		mainLayout.setColumnStretch(6, 1)
		mainLayout.setRowStretch(0, 1)
		mainLayout.setRowStretch(1, 1)
		mainLayout.setRowStretch(2, 5)
		#self.setLayout(mainLayout)
		self.setCentralWidget(QWidget(self))
		self.centralWidget().setLayout(mainLayout)


	def setButtonStatus(self):
		#print( "setButtonStatus = " + str(self.usb.find_com) )
		pe = QPalette()
		if (self.usb.find_com):
			pe.setColor(QPalette.WindowText,Qt.black)
			self.com.connectStatus.setPalette(pe)
			self.com.connectStatus.setText("Device connected")
			self.com.connectBtn.setEnabled(False)
			self.flushBtn.setEnabled(True)
			self.sendBtn.setEnabled(True)
			self.sendReadBtn.setEnabled(True)
			self.readLineBtn.setEnabled(True)
			self.readBtn.setEnabled(True)
		else:
			pe.setColor(QPalette.WindowText,Qt.red)
			self.com.connectStatus.setPalette(pe)
			self.com.connectStatus.setText("Can't find correct COM port")
			self.com.connectBtn.setEnabled(True)
			self.flushBtn.setEnabled(False)
			self.sendBtn.setEnabled(False)
			self.sendReadBtn.setEnabled(False)
			self.readLineBtn.setEnabled(False)
			self.readBtn.setEnabled(False)


	def checkConnectStatus(self):
		if (self.usb.find_com == False):
			#print "com not find"
			self.setButtonStatus()

	def buildConnect(self):
		br_index = self.com.baudrate.currentIndex()
		baudrate = int(self.com.baudrate_list[br_index])
		#print(baudrate)
		#self.usb = COMPort.FT232(9600, 2)
		#self.usb = FT232(9600, 2)
		self.usb.connect(baudrate, Timeout)
		#print(self.usb.find_com)
		#print(self.usb.port)
		self.setButtonStatus()

	def writeData(self):
		self.usb.port.flushInput()
		indata = str(self.inputGroup.input.text())
		if self.inputGroup.radioBtnH.isChecked():
			if indata.isdigit():
				outdata = int(indata)
				try:
					self.usb.writeBinary(outdata)
				except serial.SerialException:
					self.usb.find_com = False
			else:
				self.inputGroup.input.setText("Enter number")
		else:
			outdata = indata
			try:
				self.usb.writeLine(outdata)
			except serial.SerialException:
				self.usb.find_com = False


	def readData(self):
		try:
			outdata = self.usb.readLine()
		except serial.SerialException:
			self.usb.find_com = False
		else:
			self.outputGroup.output.setText(str(outdata))
			self.usb.port.flushInput()


	def flushBtnRun(self):
		self.usb.port.flushInput()
		self.outputGroup.output.setText("")

	def sendBtnRun(self):
		self.writeData()
		self.checkConnectStatus()
		self.outputGroup.output.setText("")

	def sendReadBtnRun(self):
		self.writeData()
		self.checkConnectStatus()
		#self.usb.port.flush()
		self.readData()
		self.checkConnectStatus()

	def readLineBtnRun(self):
		self.readData()
		self.checkConnectStatus()

	def readBtnRun(self):
		byteText = str(self.byte.text())
		outdata = []
		if byteText.isdigit():
			byte = int(byteText)
			#print byte
			try:
				for i in range(0, byte):
					temp = self.usb.readBinary()
					#print temp
					outdata.append(temp)
				#print outdata
			except serial.SerialException:
				self.usb.find_com = False
			else:
				outstr = ""
				for i in range(0, byte):
					outstr = outstr + str(outdata[i]) + ", "			
				self.outputGroup.output.setText(outstr)
		else:
			self.byte.setText("Number")
		self.checkConnectStatus()


if __name__ == '__main__':
	app = QApplication(sys.argv)

	main = mainWindow()
	main.show()
	os._exit(app.exec_())

