import os
import sys
import logging
sys.path.append("../")
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import py3lib
import pyqtgraph as pg
from py3lib import *
from py3lib import AdamGUIclass
from py3lib.AdamGUIclass import *
TITLE_TEXT = "NanoIMU"

class COMRead_Widget(QWidget):
	def __init__(self, parent=None):
		super(COMRead_Widget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		''' plot '''
		self.win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
		self.win.resize(1000,600)
		self.win.setWindowTitle('pyqtgraph example: Plotting')
		plot1 = self.win.addPlot(title="p1")
		self.plot1 = plot1.plot(pen='r')
		''' usb '''
		self.usb = AdamGUIclass.usbConnect()
		''' lb '''
		self.buffer_lb = AdamGUIclass.displayOneBlock('Buffer size')
		''' bt '''
		self.read_btn = AdamGUIclass.btn('read')
		self.stop_btn = AdamGUIclass.btn('stop')
		''' gauge'''
		self.SRS200_gauge = gaugePlotwLabel('theta', 'theta (degree)')
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.usb.layoutG(), 0,0,1,3)
		mainLayout.addWidget(self.buffer_lb, 0,3,1,1)
		mainLayout.addWidget(self.win, 1,0,40,40)
		mainLayout.addWidget(self.read_btn, 1,41,1,1)
		mainLayout.addWidget(self.stop_btn, 2,41,1,1)
		mainLayout.addWidget(self.SRS200_gauge, 5,41,15,15)
		self.setLayout(mainLayout)
 

 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = COMRead_Widget()
	main.show()
	os._exit(app.exec_())