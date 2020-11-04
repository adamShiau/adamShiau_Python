import os
import time
import math
#import threading
import numpy as np 
import sys
sys.path.append("../")
from py3lib.COMPort import *
from py3lib.QuGUIclass import *
import py3lib.FileToArray as fil2a


TESTING_TIME_MIN = 1
TESTING_TIME_MAX = 8

Baudrate = 9600
Timeout = 0.5


class readSignal(QObject):
	update_data = pyqtSignal(float) # returned data or updated data
	finished = pyqtSignal()
	def __init__(self, dtc_num, runTime, usb, parent = None):
		super(QObject, self).__init__(parent)
		self.dtc_num = dtc_num
		self.runTime = runTime
		self.usb = usb
		self.runFlag = True

	def readVol(self):
		timePass = 0
		filename = self.dtc_num + ".txt"
		fo = open(filename, "w+")
		fo.write("Model : DTC03, S/N : " + self.dtc_num + '\n')
		fo.write("Date:" + time.strftime("%c") + '\n')
		fo.write("time" + '\t' + "volt" + '\t' + "temp" + '\n')
		#fo.close()

		while ( (timePass < self.runTime) and (self.runFlag) ):
			#self.writeData("MEAS:VOLT:DC?")
			self.usb.port.flushInput()
			try:
				self.usb.writeLine("MEAS:VOLT:DC?")
			except serial.SerialException:
				print("writeLine error")
				self.usb.find_com = False

			#outdata = self.readData()
			try:
				outdata = self.usb.readLine()
			except serial.SerialException:
				print("readLine error")
				self.usb.find_com = False
			else:
				#print(outdata)
				self.usb.port.flushInput()
			#print(outdata)

			if (outdata != ''):
				tempvol = float(outdata) #+ 2
				#print(tempvol)
				#tempact =(1/(math.log((float(y))/2.0)/3988+0.003354))-273.15
				tempact =(1/(math.log((float(tempvol))/2.0)/3988+0.003354))-273.15
				#print(tempact)
				fo.write(time.strftime("%T") + '\t')
				fo.write("%3.4f" % tempvol + '\t' + "%3.4f" % tempact + '\n')
				self.update_data.emit(tempact)

			timePass = timePass + 1
			time.sleep(1)
			# while end
		fo.close()
		self.finished.emit()


class inputGroup(QWidget):
	def __init__(self, parent=None):
		self.GroupBox = QGroupBox("Input")
		self.text0 = QLabel("")
		self.startTime = QLabel("")
		self.stopTime = QLabel("")
		self.text1 = QLabel("Filename = ")
		self.text1.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.filename = QLineEdit()
		self.text2 = QLabel(".txt")
		self.text3 = QLabel("Ex:")
		self.text3.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.text4 = QLabel("QI54350001_1B_24")
		self.runTime = spinBlock("Testing time (hr)", TESTING_TIME_MIN, TESTING_TIME_MAX)
		self.startBtn = QPushButton("Start")
		self.stopBtn = QPushButton("Stop")
		self.loadBtn = QPushButton("Load File")
		#self.testBtn = QPushButton("Test File")
		self.startBtn.setEnabled(False)
		self.stopBtn.setEnabled(False)

	def inputGroupUI(self):
		GroupLayout = QGridLayout()
		GroupLayout.addWidget(self.text0,0,1,1,1)
		GroupLayout.addWidget(self.startTime,0,5,1,1)
		GroupLayout.addWidget(self.stopTime,0,6,1,1)
		GroupLayout.addWidget(self.text1,1,0,1,1)
		GroupLayout.addWidget(self.filename,1,1,1,1)
		GroupLayout.addWidget(self.text2,1,2,1,1)
		GroupLayout.addWidget(self.runTime,1,3,1,2)
		GroupLayout.addWidget(self.startBtn,1,5,1,1)
		GroupLayout.addWidget(self.stopBtn,1,6,1,1)
		GroupLayout.addWidget(self.text3,2,0,1,1)
		GroupLayout.addWidget(self.text4,2,1,1,1)
		GroupLayout.addWidget(self.loadBtn,2,5,1,1)
		#GroupLayout.addWidget(self.testBtn,2,6,1,1)
		GroupLayout.setRowStretch(0, 1)
		GroupLayout.setRowStretch(1, 1)
		GroupLayout.setRowStretch(2, 1)
		GroupLayout.setColumnStretch(0, 1)
		GroupLayout.setColumnStretch(1, 1)
		GroupLayout.setColumnStretch(2, 1)
		GroupLayout.setColumnStretch(3, 1)
		GroupLayout.setColumnStretch(4, 1)
		GroupLayout.setColumnStretch(5, 1)
		GroupLayout.setColumnStretch(6, 1)
		#self.group.setLayout(GroupLayout)
		self.GroupBox.setLayout(GroupLayout)
		self.GroupBox.show()
		return self.GroupBox


class mainWindow(QMainWindow):
	def __init__(self, parent=None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle("DTC03 Testing")
		self.resize(960,640)
		self.move(50,50)
		self.com = connectBlock("USB Connection")
		self.input = inputGroup()
		self.plot = outputPlot()
		self.usb = FT232("")
		self.usb.connect(Baudrate, Timeout)
		#print(self.usb.find_com)
		#print(self.usb.port)
		self.setButtonStatus()
		if (self.usb.find_com):
			self.writeData("*CLS")
			self.writeData("SYST:REM")

		self.com.btn.clicked.connect(self.buildConnect)
		self.input.startBtn.clicked.connect(self.startBtn)
		self.input.stopBtn.clicked.connect(self.stopBtn)
		self.input.loadBtn.clicked.connect(self.loadBtn)
		#self.input.testBtn.clicked.connect(self.testBtn)

		self.data = np.empty(0)
		self.obj1 = readSignal("", 0, self.usb)
		self.thread1 = QThread()
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.input.inputGroupUI(),0,0,1,4)
		mainLayout.addWidget(self.com.layout1(),0,4,1,3)
		mainLayout.addWidget(self.plot,1,0,1,7)
		mainLayout.setColumnStretch(0, 1)
		mainLayout.setColumnStretch(1, 1)
		mainLayout.setRowStretch(0, 1)
		mainLayout.setRowStretch(1, 5)
		#self.setLayout(mainLayout)
		self.setCentralWidget(QWidget(self))
		self.centralWidget().setLayout(mainLayout)

	def setButtonStatus(self):
		#print( "setButtonStatus = " + str(self.usb.find_com) )
		pe = QPalette()
		if (self.usb.find_com):
			self.com.SetConnectText(Qt.black,"Connection build", False)
			self.input.startBtn.setEnabled(True)
		else:
			self.com.SetConnectText(Qt.red,"Connect failed", True)
			self.input.startBtn.setEnabled(False)

	def checkConnectStatus(self):
		if (self.usb.find_com == False):
			#print("com not find")
			self.setButtonStatus()

	def buildConnect(self):
		self.usb = FT232("")
		self.usb.connect(Baudrate, Timeout)
		#print(self.usb.find_com)
		#print(self.usb.port)
		self.setButtonStatus()
		if (self.usb.find_com):
			self.writeData("*CLS")
			self.writeData("SYST:REM")

	def writeData(self, indata):
		#print(indata)
		self.usb.port.flushInput()
		try:
			self.usb.writeLine(indata)
		except serial.SerialException:
			print("writeLine error")
			self.usb.find_com = False

	def readData(self):
		try:
			outdata = self.usb.readLine()
		except serial.SerialException:
			print("readLine error")
			self.usb.find_com = False
		else:
			#print(outdata)
			self.usb.port.flushInput()
			return outdata

	def startBtn(self):
		self.data = np.empty(0)
		dtc_num = self.input.filename.text()
		runTime = self.input.runTime.spin.value() * 60 * 60
		#print(runTime)
		self.obj1 = readSignal(dtc_num, runTime, self.usb)
		self.plot.ax.clear()

		if (dtc_num == ''):
			pe = QPalette()
			pe.setColor(QPalette.WindowText,Qt.red)
			self.input.text0.setPalette(pe)
			self.input.text0.setText("Please input filename")
		else:
			self.input.startTime.setText(time.strftime("%T"))
			self.input.stopTime.setText("")
			self.input.startBtn.setEnabled(False)
			self.input.stopBtn.setEnabled(True)

			if (self.usb.find_com):
				self.writeData("*CLS")
				self.obj1.moveToThread(self.thread1)
				self.obj1.update_data.connect(self.drawData)
				self.obj1.finished.connect(self.stopBtn)
				self.thread1.started.connect(self.obj1.readVol)
				self.thread1.start()

	def drawData(self, tempact):
		if (self.obj1.runFlag):
			self.data = np.append(self.data, tempact)
			self.plot.ax.clear()
			self.plot.ax.plot(self.data, '*-')
			#self.plot.canvas.draw()
			self.plot.figure.canvas.draw()
			self.plot.figure.canvas.flush_events()

	def stopBtn(self):
		self.thread1.quit()
		self.obj1.runFlag = False
		self.input.stopTime.setText(time.strftime("%T"))
		#self.data = np.empty(0)
		self.input.startBtn.setEnabled(True)
		self.input.stopBtn.setEnabled(False)

	def loadBtn(self):
		OpenFileName = QFileDialog.getOpenFileName(self, "Load Testing Data", "", "Text Files (*.txt)")
		if (OpenFileName[0] != ''):
			if os.path.exists(OpenFileName[0]):
				temp1, temp2, self.data = fil2a.TexTFileto3ColumeArray(OpenFileName[0], "\t", "DTC03", 3)
		#print(temp1)
		#print(temp2)
		#print(self.data)
		self.plot.ax.clear()
		self.plot.ax.plot(self.data, '*-')
		#self.plot.canvas.draw()
		self.plot.figure.canvas.draw()
		self.plot.figure.canvas.flush_events()

	# def testBtn(self):
	# 	temp1, temp2, data1 = fil2a.TexTFileto3ColumeArray("D:\\Quantaser_work\\DTC03\\Testing Report\\pic\\QI54350041_2B_26.txt", "\t", 3, "DTC03")
	# 	temp3, temp4, data2 = fil2a.TexTFileto3ColumeArray("D:\\Quantaser_work\\DTC03\\Testing Report\\pic\\QI54350042_2B_26.txt", "\t", 3, "DTC03")
	# 	#print(data1)
	# 	#print(data2)
	# 	self.data = (data1[1000:3600] + data2[0:2600])/2
	# 	#print(self.data)
	# 	self.plot.ax.clear()
	# 	self.plot.ax.plot(self.data, '*-')
	# 	#self.plot.canvas.draw()
	# 	self.plot.figure.canvas.draw()
	# 	self.plot.figure.canvas.flush_events()

	def beforeExit(self):
		self.BtnStop()
		app.exec_()
		return 0


if __name__ == '__main__':
	app = QApplication(sys.argv)

	main = mainWindow()
	main.show()
	os._exit(app.exec_())
	#os._exit(main.beforeExit())

