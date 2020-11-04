
import time
import logging
import sys
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import numpy as np



class doSomthing1(QObject):
	update_text = pyqtSignal(str) # returned data or updated data
	finished = pyqtSignal()
	def __init__(self, loops, parent = None):
		super(QObject,self).__init__(parent)
		self.loops = loops

	def running1(self):  # run action for the tread, must use "run"
		print "loops ="+str(self.loops)
		for i in xrange (0, self.loops):
			time.sleep(1)
			output = "I am function1 in loop "+str(i)+"."
			logging.error( output)
			self.update_text.emit(output)
		logging.info( "thread doSomthing1 finished!")
		self.finished.emit()


class doSomthing3(QObject):
	
	update_array = pyqtSignal(object)
	finished = pyqtSignal()

	def __init__(self, loops, parent =None):
		super(QObject, self).__init__(parent)
		self.loops = loops

	def running2(self):
		a = np.zeros((0))
		logging.debug("th2 loops =" +str(self.loops))
		for i in xrange (0, self.loops):
			a =np.append(a, i)
			time.sleep(1.5)
			logging.debug(a)
			self.update_array.emit(a)

		self.finished.emit()


class mainWidget(QWidget):
	def __init__(self, parent =None):
		super(QWidget, self).__init__(parent)
		self.btn1 = QPushButton("BT1")
		self.btn2 = QPushButton("BT2")
		self.btn3 = QPushButton("BT3")
		self.label1 = QLabel()
		self.label2 = QLabel()
		self.label1.setText("Label 1")
		self.label2.setText("Label 2")
		topLayout = QGridLayout()
		topLayout.addWidget(self.btn1, 0,0,1,1)
		topLayout.addWidget(self.btn2, 0,1,1,1)
		topLayout.addWidget(self.btn3, 0,2,1,1)
		topLayout.addWidget(self.label1, 1,0,1,3)
		topLayout.addWidget(self.label2, 2,0,3,3)
		self.setLayout(topLayout)
		self.connectButton()

	def btn1Run(self): # define connection
		self.thread1 = QThread()
		self.obj1 = doSomthing1(5)
		self.obj1.moveToThread(self.thread1)
		self.obj1.update_text.connect(self.th1update)
		self.thread1.started.connect(self.obj1.running1)
		self.obj1.finished.connect(self.th1stop)
		self.thread1.start()

	def th1stop(self):
		logging.debug("I am stop")
		self.thread1.quit()

	def th1update(self, text): # get the data from thread
		self.label1.setText(text)

	def btn3Run(self):
		self.thread2 = QThread()
		self.obj2 = doSomthing3(5)
		self.obj2.moveToThread(self.thread2)
		self.obj2.update_array.connect(self.th2update)
		self.thread2.started.connect(self.obj2.running2)
		self.obj2.finished.connect(self.th2stop)
		self.thread2.start()

	def th2update(self,array): 
		outtext = ""
		for i in array:
			outtext= outtext + str(i)+","
		self.label1.setText(outtext)

	def th2stop(self):
		self.thread2.quit()


	def connectButton(self): # define button function
		self.btn1.clicked.connect(self.btn1Run)
		self.btn2.clicked.connect(self.btn2Run)
		self.btn3.clicked.connect(self.btn3Run)

	def btn2Run(self):
		ans = self.thread1.isRunning()
		ans2 = self.thread2.isRunning()
		self.label2.setText("Thread runing status:"+str(ans)+","+str(ans2))

		
class mainWindow(QMainWindow):
	def __init__(self, parent=None):
		super (mainWindow, self).__init__(parent)
		self.setWindowTitle("ThreadingTest")
		self.resize(500,500)
		self.move(50,50)
		self.top = mainWidget()
		self.top.setMinimumSize(600, 600)
		self.mainUI()
		logging.basicConfig(level=logging.DEBUG, filename="log.txt", format='%(levelname)s : %(module)s ,%(threadName)s, %(message)s')

	def mainUI(self):
		mainLayout = QGridLayout()
		self.scorollerarea = QScrollArea()
		self.scorollerarea.setWidget(self.top)
		self.setCentralWidget(QWidget(self))
		mainLayout.addWidget(self.scorollerarea,0,0,1,1)
		self.centralWidget().setLayout(mainLayout)
		

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	main.show()
	os._exit(app.exec_())
