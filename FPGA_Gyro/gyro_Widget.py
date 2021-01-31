import os
import sys
import logging
sys.path.append("../")
import py3lib
from py3lib import *
from py3lib.AdamGUIclass import *
TITLE_TEXT = "Gyro"

class mainWidget(QWidget):
	def __init__(self, parent=None):
		super(mainWidget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		# self.updataCom = comportComboboxBlock(group_name='updata comport', btn_name='renew')
		# self.usb = connectBlock("USB Connection")
		self.usb = usbConnect()
		self.read_btn = btn('read')
		self.stop_btn = btn('stop')
		''' spin box'''
		self.wait_cnt = spinBlock(title='Wait cnt', minValue=0, maxValue=100, double=False, step=1)
		self.avg = spinBlock(title='avg', minValue=0, maxValue=6, double=False, step=1)
		self.err_offset = spinBlock(title='Err offset', minValue=-50, maxValue=50, double=False, step=1)
		self.polarity = spinBlock(title='polarity', minValue=0, maxValue=1, double=False, step=1)
		self.mod_H = spinBlock(title='MOD_H', minValue=0, maxValue=32767, double=False, step=1)
		self.mod_L = spinBlock(title='MOD_L', minValue=-32768, maxValue=0, double=False, step=1)
		self.gain1 = spinBlock(title='GAIN', minValue=0, maxValue=14, double=False, step=1)
		self.step_max = spinBlock(title='step_max', minValue=0, maxValue=16384, double=False, step=1)
		self.v2pi = spinBlock(title='V2PI', minValue=0, maxValue=32767, double=False, step=1)
		self.fb_on = spinBlock(title='mode(0:OPEN)', minValue=0, maxValue=1, double=False, step=1)
		self.err_th = spinBlock(title='ERR_TH', minValue=0, maxValue=16384, double=False, step=1)
		self.freq = spinBlockOneLabel(title='frequency', minValue=0, maxValue=150, double=False, step=1)
		
		
		self.com_plot = outputPlotSize(16)
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.usb.layoutG(), 0,0,1,3)
		mainLayout.addWidget(self.com_plot, 1,0,10,10)
				
		###btn###
		mainLayout.addWidget(self.read_btn, 0,5,1,1)
		mainLayout.addWidget(self.stop_btn, 0,6,1,1)
		
		###spin Box###
		mainLayout.addWidget(self.wait_cnt, 1,10,1,2)
		mainLayout.addWidget(self.avg, 1,12,1,2)
		mainLayout.addWidget(self.mod_H, 2,10,1,2)
		mainLayout.addWidget(self.mod_L, 2,12,1,2)
		mainLayout.addWidget(self.err_offset, 3,10,1,2)
		mainLayout.addWidget(self.polarity, 3,12,1,2)
		mainLayout.addWidget(self.gain1, 4,10,1,2)
		mainLayout.addWidget(self.step_max, 4,12,1,2)
		mainLayout.addWidget(self.v2pi, 5,10,1,2)
		mainLayout.addWidget(self.fb_on, 5,12,1,2)
		mainLayout.addWidget(self.err_th, 6,10,1,2)
		mainLayout.addWidget(self.freq, 7,10,1,4)
		
		self.setLayout(mainLayout)
 
class Comport_sel(QWidget):
	def __init__(self, parent=None):
		super(Comport_sel, self).__init__(parent)
		self.cs = QComboBox()
		self.Comport_sel_UI()

	def Comport_sel_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.cs, 0,0,1,1)
		self.setLayout(layout) 
 
class Updata_COM_btn(QWidget):
	def __init__(self, parent=None):
		super(Updata_COM_btn, self).__init__(parent)
		self.updata = QPushButton("updata comport")

		self.Updata_COM_btn_UI()

	def Updata_COM_btn_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.updata, 0,0,1,1)
		self.setLayout(layout)
 
class Save_edit(QWidget):
	def __init__(self, parent=None):
		super(Save_edit, self).__init__(parent)
		self.edit = QLineEdit()
		self.Save_edit_UI()

	def Save_edit_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.edit, 0,0,1,1)
		self.setLayout(layout)
 
class Read_btn(QWidget):
	def __init__(self, parent=None):
		super(Read_btn, self).__init__(parent)
		self.read = QPushButton("read")

		self.Read_btn_UI()

	def Read_btn_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.read, 0,0,1,1)
		self.setLayout(layout)
        
class Stop_btn(QWidget):
	def __init__(self, parent=None):
		super(Stop_btn, self).__init__(parent)
		self.stop = QPushButton("stop")

		self.Stop_btn_UI()

	def Stop_btn_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.stop, 0,0,1,1)
		self.setLayout(layout)
		
class Cali_btn(QWidget):
	def __init__(self, parent=None):
		super(Cali_btn, self).__init__(parent)
		self.btn = QPushButton("calibration start")
		self.btn_UI()

	def btn_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.btn, 0,0,1,1)
		self.setLayout(layout)
		
class Cali_stop_btn(QWidget):
	def __init__(self, parent=None):
		super(Cali_stop_btn, self).__init__(parent)
		self.btn = QPushButton("calibration stop")
		self.btn_UI()

	def btn_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.btn, 0,0,1,1)
		self.setLayout(layout)

 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWidget()
	main.show()
	os._exit(app.exec_())