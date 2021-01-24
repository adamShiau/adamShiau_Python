import os 
import sys 
sys.path.append("../") 
import time 
import datetime
from scipy import signal
# import logging
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
import numpy as np
import action as ACT

class mainWindow(QWidget):
	def __init__(self, parent=None):
		super(mainWindow, self).__init__(parent)
		self.start = QPushButton('start')
		self.stop = QPushButton('stop')
		self.thread1 = QThread()
		self.setupUI()
		self.act = ACT.action2()
		self.link()
	
	def setupUI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.start, 0,0,1,1)
		mainLayout.addWidget(self.stop, 1,0,1,1)
		self.setLayout(mainLayout)
		
		
	def link(self):
		# '''
		# self.thread1.started.connect(self.act.doLoop)
		# self.act.act_signal.connect(self.print_thread)
		# '''
		self.start.clicked.connect(self.start_action)
		self.stop.clicked.connect(self.stop_action)
		self.act.act_signal.connect(self.print_thread)
		
	def start_action(self):
		self.act.run_flag = 1
		# self.act.act_signal.connect(self.print_thread)
		# '''
		# self.thread1.start()
		# '''
		self.act.start()
		
	def stop_action(self):
		self.act.run_flag = 0
		self.thread1.quit() 
		self.thread1.wait()
		
	def print_thread(self, data):
		print('data = ', data)
		
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWindow()
	# main = TabPlot()
	main.show()
	os._exit(app.exec_())