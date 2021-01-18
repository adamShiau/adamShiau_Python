import os
import sys
import logging
sys.path.append("../")
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import py3lib
from py3lib import *
from py3lib import AdamGUIclass
from py3lib.AdamGUIclass import *
# from py3lib.AdamGUIclass import *
TITLE_TEXT = "NanoIMU"

class TabPlot(QTabWidget):
	def __init__(self, parent=None):
		super(TabPlot, self).__init__(parent)
		self.tab1 = QWidget()
		self.tab2 = QWidget()
		self.tab3 = QWidget()
		''' tab1 GUI item'''
		###tab1 plot###
		self.tab1_plot1 = outputPlotSize(16)
		self.tab1_plot2 = outputPlotSize(16)
		self.tab1_plot3 = outputPlotSize(16)
		self.tab1_plot4 = outputPlotSize(16)
		###tab1 check box###
		self.tab1_gyro_cb = chkBoxBlock_2('wz','Nano33', 'PP')
		self.tab1_adxlXLM_cb = chkBoxBlock_2( 'ADXL355', 'ax', 'ay')
		self.tab1_nano33XLM_cb = chkBoxBlock_2('Nano33', 'ax', 'ay')
		self.tab1_speed_cb = chkBoxBlock_2( 'speed', 'ADXL355', 'Nano33')
		###tab1 btn###
		self.tab1_read_btn = AdamGUIclass.btn('read')
		self.tab1_stop_btn = AdamGUIclass.btn('stop')
		''' tab2 GUI item'''
		###tab2 label###
		self.tab2_SRS200 = AdamGUIclass.displayTwoBlock('SRS200_wz', 'offset', 'stdev')
		self.tab2_PP = AdamGUIclass.displayTwoBlock('PP_wz', 'offset', 'stdev')
		self.tab2_Nano33_gyro = AdamGUIclass.displayTwoBlock('Nano33_wz', 'offset', 'stdev')
		self.tab2_Nano33_xlm = AdamGUIclass.displaySixBlock('Nano33', 'ax', 'offset', 'stdev', 'ay', 'offset', 'stdev', 'az', 'offset', 'stdev')
		self.tab2_ADXL355_xlm = AdamGUIclass.displaySixBlock('ADXL355', 'ax', 'offset', 'stdev', 'ay', 'offset', 'stdev', 'az', 'offset', 'stdev')

		###tab2 btn###
		self.tab2_cali_start_btn = AdamGUIclass.btn('cali start')
		self.tab2_cali_stop_btn = AdamGUIclass.btn('cali stop')
		''' tab3 GUI item'''
		###tab3 plot###
		self.tab3_plot1 = outputPlotSize(16)
		###tab3 btn###
		self.tab3_xmax = AdamGUIclass.editBlockwBtn('xmax')
		self.tab3_ymax = AdamGUIclass.editBlockwBtn('ymax')
		
		# self.plot2 = output2Plot()
		# self.plot2.ax1.set_ylabel("Arbiary Uint")
		# self.plot2.ax2.set_xlabel("Time (s)")
		# self.plot2.ax2.set_ylabel("Arbiary Uint")
		self.addTab(self.tab1,"Meas.")
		self.addTab(self.tab2,"Cali.")
		self.addTab(self.tab3,"Track")
		self.Tab1_UI()
		self.Tab2_UI()
		self.Tab3_UI()
		
	def Tab1_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.tab1_plot1, 0, 0, 10, 10)
		layout.addWidget(self.tab1_plot2, 0, 11, 10, 10)
		layout.addWidget(self.tab1_plot3, 10, 0, 10, 10)
		layout.addWidget(self.tab1_plot4, 10, 11, 10, 10)
		layout.addWidget(self.tab1_gyro_cb.layout(), 5, 20, 1, 1)
		layout.addWidget(self.tab1_adxlXLM_cb.layout(), 14, 9, 1, 1)
		layout.addWidget(self.tab1_nano33XLM_cb.layout(), 15, 9, 1, 1)
		layout.addWidget(self.tab1_speed_cb.layout(), 14, 20, 1, 1)
		layout.addWidget(self.tab1_read_btn, 1, 30, 1, 1)
		layout.addWidget(self.tab1_stop_btn, 2, 30, 1, 1)
		self.tab1.setLayout(layout)

	def Tab2_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.tab2_SRS200, 0, 0, 3, 6)
		layout.addWidget(self.tab2_PP, 3, 0, 3, 6)
		layout.addWidget(self.tab2_Nano33_gyro, 6, 0, 3, 6)
		layout.addWidget(self.tab2_Nano33_xlm, 0, 6, 6, 6)
		layout.addWidget(self.tab2_ADXL355_xlm, 0, 12, 6, 6)
		layout.addWidget(self.tab2_cali_start_btn, 0, 18, 1, 1)
		layout.addWidget(self.tab2_cali_stop_btn, 1, 18, 1, 1)

		self.tab2.setLayout(layout)

	def Tab3_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.tab3_plot1, 0, 0, 10, 10) 
		layout.addWidget(self.tab3_xmax, 1, 10, 1, 1)
		layout.addWidget(self.tab3_ymax, 2, 10, 1, 1)
		self.tab3.setLayout(layout)

class mainWidget(QWidget):
	def __init__(self, parent=None):
		super(mainWidget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.usb = AdamGUIclass.usbConnect()
		self.TabPlot = TabPlot()
		self.buffer_lb = AdamGUIclass.displayOneBlock('Buffer size')
		###radio btn###
		self.mv_rb = QRadioButton('MV enable')
		self.mv_rb.setChecked(0)
		##guage###
		self.SRS200_gauge = gaugePlot()
		self.speed_gauge = gaugePlot()
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.usb.layoutG(), 0,0,1,3)
		mainLayout.addWidget(self.buffer_lb, 0,3,1,3)
		mainLayout.addWidget(self.mv_rb, 0,6,1,1)
		mainLayout.addWidget(self.TabPlot, 1,0,8,8)
		mainLayout.addWidget(self.SRS200_gauge, 2,9,3,3)
		mainLayout.addWidget(self.speed_gauge, 5,9,3,3)
		self.setLayout(mainLayout)
 
 
class Save_edit(QWidget):
	def __init__(self, parent=None):
		super(Save_edit, self).__init__(parent)
		self.edit = QLineEdit()
		self.Save_edit_UI()

	def Save_edit_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.edit, 0,0,1,1)
		self.setLayout(layout)
 
# class Read_btn(QWidget):
	# def __init__(self, parent=None):
		# super(Read_btn, self).__init__(parent)
		# self.bt = QPushButton("read")

		# self.Read_btn_UI()

	# def Read_btn_UI(self):
		# layout = QGridLayout()
		# layout.addWidget(self.read, 0,0,1,1)
		# self.setLayout(layout)
        
# class Stop_btn(QWidget):
	# def __init__(self, parent=None):
		# super(Stop_btn, self).__init__(parent)
		# self.bt = QPushButton("stop")

		# self.Stop_btn_UI()

	# def Stop_btn_UI(self):
		# layout = QGridLayout()
		# layout.addWidget(self.stop, 0,0,1,1)
		# self.setLayout(layout)
		
# class Cali_btn(QWidget):
	# def __init__(self, parent=None):
		# super(Cali_btn, self).__init__(parent)
		# self.btn = QPushButton("calibration start")
		# self.btn_UI()

	# def btn_UI(self):
		# layout = QGridLayout()
		# layout.addWidget(self.btn, 0,0,1,1)
		# self.setLayout(layout)
		
# class Cali_stop_btn(QWidget):
	# def __init__(self, parent=None):
		# super(Cali_stop_btn, self).__init__(parent)
		# self.btn = QPushButton("calibration stop")
		# self.btn_UI()

	# def btn_UI(self):
		# layout = QGridLayout()
		# layout.addWidget(self.btn, 0,0,1,1)
		# self.setLayout(layout)

 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWidget()
	# main = TabPlot()
	main.show()
	os._exit(app.exec_())