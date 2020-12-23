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
		self.updataCom = comportComboboxBlock(group_name='updata comport', btn_name='renew')
		self.usb = connectBlock("USB Connection")
		self.read_btn = Read_btn()
		self.stop_btn = Stop_btn()
		''' spin box'''
		self.wait_cnt = spinBlock(title='Wait cnt', minValue=0, maxValue=50, double=False, step=1)
		self.avg = spinBlock(title='avg', minValue=0, maxValue=6, double=False, step=1)
		self.err_offset = spinBlock(title='Err offset', minValue=-50, maxValue=50, double=False, step=1)
		self.polarity = spinBlock(title='polarity', minValue=0, maxValue=1, double=False, step=1)
		self.mod_H = spinBlock(title='MOD_H', minValue=0, maxValue=32767, double=False, step=1)
		self.mod_L = spinBlock(title='MOD_L', minValue=-32768, maxValue=0, double=False, step=1)
		self.freq = spinBlockOneLabel(title='frequency', minValue=0, maxValue=150, double=False, step=1)
		
		self.com_plot = outputPlot()
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.com_plot, 0,0,7,1)
		mainLayout.addWidget(self.updataCom.layout(), 0,1,1,3)
		mainLayout.addWidget(self.usb.layout1(), 1,1,1,3)
				
		###btn###
		mainLayout.addWidget(self.read_btn, 2,1,1,1)
		mainLayout.addWidget(self.stop_btn, 2,2,1,1)
		
		###spin Box###
		mainLayout.addWidget(self.wait_cnt, 3,1,1,1)
		mainLayout.addWidget(self.avg, 3,2,1,1)
		mainLayout.addWidget(self.mod_H, 4,1,1,1)
		mainLayout.addWidget(self.mod_L, 4,2,1,1)
		mainLayout.addWidget(self.err_offset, 5,1,1,1)
		mainLayout.addWidget(self.polarity, 5,2,1,1)
		mainLayout.addWidget(self.freq, 6,1,1,2)
		
		###label and line editor###
		
		# mainLayout.addWidget(self.theta_lb, 16,1)
		# mainLayout.addWidget(self.theta200_lb, 16,2)
		# mainLayout.addWidget(self.buffer_lb, 16,3)
		
		# mainLayout.addWidget(self.wzOffset_lb, 12,1)
		# mainLayout.addWidget(self.wzStd_lb, 12,2)
		# mainLayout.addWidget(self.diffwzStd_lb, 12,3)
		# mainLayout.addWidget(self.wzOffset_le, 13,1,1,1)
		# mainLayout.addWidget(self.wzVth_le, 13,3,1,1)
		
		# mainLayout.addWidget(self.wz200Offset_lb, 14,1)
		# mainLayout.addWidget(self.wz200Std_lb, 14,2)
		# mainLayout.addWidget(self.wz200Offset_le, 15,1,1,1)
		
		# mainLayout.addWidget(self.wxOffset_lb, 8,1)
		# mainLayout.addWidget(self.wxStd_lb, 8,2)
		# mainLayout.addWidget(self.diffwxStd_lb, 8,3)
		# mainLayout.addWidget(self.wxOffset_le, 9,1,1,1)
		# mainLayout.addWidget(self.wxVth_le, 9,3,1,1)
		
		# mainLayout.addWidget(self.wyOffset_lb, 10,1)
		# mainLayout.addWidget(self.wyStd_lb, 10,2)
		# mainLayout.addWidget(self.diffwyStd_lb, 10,3)
		# mainLayout.addWidget(self.wyOffset_le, 11,1,1,1)
		# mainLayout.addWidget(self.wyVth_le, 11,3,1,1)
		
		# mainLayout.addWidget(self.axOffset_lb, 4,1)
		# mainLayout.addWidget(self.axStd_lb, 4,2)
		# mainLayout.addWidget(self.axOffset_le, 5,1,1,1)
		
		# mainLayout.addWidget(self.ayOffset_lb, 6,1)
		# mainLayout.addWidget(self.ayStd_lb, 6,2)
		# mainLayout.addWidget(self.ayOffset_le, 7,1,1,1)
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