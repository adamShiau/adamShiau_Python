import os
import sys
import logging
sys.path.append("../")
import py3lib
from py3lib import *
from py3lib.AdamGUIclass import *
TITLE_TEXT = "NanoIMU"

class mainWidget(QWidget):
	def __init__(self, parent=None):
		super(mainWidget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.usb = connectBlock("USB Connection")
		self.read_btn = Read_btn()
		self.stop_btn = Stop_btn()
		# self.save_edit = Save_edit();
		self.updataCom = comportComboboxBlock(group_name='updata comport', btn_name='renew')
		# self.updataCom = Updata_COM_btn()
		# self.com_sel = Comport_sel()
		self.com_plot = output2Plot() 
		# self.com_plot = output4Plot()
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.com_plot, 0,0,5,1)
		mainLayout.addWidget(self.updataCom.layout(), 0,1,1,3)
		mainLayout.addWidget(self.usb.layout1(), 1,1,1,3)
		# mainLayout.addWidget(self.com_sel, 0,1,1,1)
		
		mainLayout.addWidget(self.read_btn, 2,1,1,1)
		mainLayout.addWidget(self.stop_btn, 2,2,1,1)
		# mainLayout.addWidget(self.save_edit, 2,0,1,1)
		
		# mainLayout.setRowStretch(0, 1)
		# mainLayout.setRowStretch(1, 1)
		# mainLayout.setColumnStretch(0, 1)
		# mainLayout.setColumnStretch(1, 1)
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

 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWidget()
	main.show()
	os._exit(app.exec_())