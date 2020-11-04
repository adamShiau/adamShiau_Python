from PyQt4.QtGui import *
from PyQt4.QtCore import *

class mainWidget(QWidget):
	def __init__(self, parent =None):
		super(QWidget, self).__init__(parent)
		self.btn1 = QPushButton("Connect")
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
		

	def btn1Run(self): # define connection
		a=3
		#self.thread1 = QThread()
		#self.obj1 = doSomthing1(5)
		#self.obj1.moveToThread(self.thread1)
		#self.obj1.update_text.connect(self.th1update)
		#self.thread1.started.connect(self.obj1.running1)
		#self.obj1.finished.connect(self.th1stop)
		#self.thread1.start()

	def th1stop(self):
		logging.debug("I am stop")
		self.thread1.quit()

	def th1update(self, text): # get the data from thread
		self.label1.setText(text)

	def btn3Run(self):
		a=3
		#self.thread2 = QThread()
		#self.obj2 = doSomthing3(5)
		#self.obj2.moveToThread(self.thread2)
		#self.obj2.update_array.connect(self.th2update)
		#self.thread2.started.connect(self.obj2.running2)
		#self.obj2.finished.connect(self.th2stop)
		#self.thread2.start()

	def th2update(self,array): 
		outtext = ""
		for i in array:
			outtext= outtext + str(i)+","
		self.label1.setText(outtext)

	def th2stop(self):
		self.thread2.quit()




	def btn2Run(self):
		ans = self.thread1.isRunning()
		ans2 = self.thread2.isRunning()
		self.label2.setText("Thread runing status:"+str(ans)+","+str(ans2))
