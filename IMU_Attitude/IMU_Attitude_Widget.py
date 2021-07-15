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
# import ADXL355_Globals as globals
TITLE_TEXT = "NanoIMU"

class TabPlot(QTabWidget):
	def __init__(self, parent=None):
		super(TabPlot, self).__init__(parent)
		pg.setConfigOption('background', 'w')
		pg.setConfigOption('foreground', 'k')
		self.win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
		self.win.resize(1000,600)
		self.win.setWindowTitle('pyqtgraph example: Plotting')
		self.win2 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
		self.win2.resize(1000,600)
		self.win2.setWindowTitle('pyqtgraph example: Plotting')
		pg.setConfigOptions(antialias=True)
		self.tab1 = QWidget()
		self.tab2 = QWidget()
		self.tab3 = QWidget()
		''' tab1 GUI item'''
		###tab1 plot###
		tab1_plot1 = self.win.addPlot(title="accelerometer(g)")
		self.tab1_plot1_1 = tab1_plot1.plot(pen='r')
		self.tab1_plot1_2 = tab1_plot1.plot(pen='b')
		self.tab1_plot1_3 = tab1_plot1.plot(pen='k')
		self.tab1_plot1_4 = tab1_plot1.plot(pen='g')
		self.tab1_plot1_5 = tab1_plot1.plot(pen='y')
		tab1_plot2 = self.win.addPlot(title="accelerometer(g)")
		self.tab1_plot2_1 = tab1_plot2.plot(pen='r')
		self.tab1_plot2_2 = tab1_plot2.plot(pen='b')
		self.tab1_plot2_3 = tab1_plot2.plot(pen='k')
		self.win.nextRow()
		tab1_plot3 = self.win.addPlot(title="sampling")
		self.tab1_plot3_1 = tab1_plot3.plot(pen='r')
		self.tab1_plot3_2 = tab1_plot3.plot(pen='b')
		tab1_plot4= self.win.addPlot(title="gyro(dps)")
		self.tab1_plot4_1 = tab1_plot4.plot(pen='r')
		self.tab1_plot4_2 = tab1_plot4.plot(pen='b')
		self.tab1_plot4_3 = tab1_plot4.plot(pen='k')
		###tab1 check box###
		self.tab1_gyro_cb = chkBoxBlock_5('ADXL','ax','ay', 'az', '', '')
		self.tab1_adxlXLM_cb = chkBoxBlock_3( 'NANO33', 'ax', 'ay', 'az')
		# self.tab1_nano33XLM_cb = chkBoxBlock_2('Nano33', 'ax', 'ay')
		self.tab1_speed_cb = chkBoxBlock_2('dt', 'ms', '')
		self.tab1_attitude_cb = chkBoxBlock_3( 'NANO33', 'wx', 'wy', 'wz')
		###tab1 btn###
		self.tab1_read_btn = AdamGUIclass.btn('read')
		self.tab1_stop_btn = AdamGUIclass.btn('stop')
		''' tab2 GUI item'''
		###tab2 label###
		self.tab2_SRS200 = AdamGUIclass.displayTwoBlock('SRS200_wz', 'offset', 'stdev')
		self.tab2_PP = AdamGUIclass.displayTwoBlock('PP_wz', 'offset', 'stdev')
		self.tab2_IMU_speed = AdamGUIclass.displayTwoBlock('IMU_speed', 'offset', 'stdev')
		self.tab2_Nano33_gyro = AdamGUIclass.displayTwoBlock('Nano33_wz', 'offset', 'stdev')
		self.tab2_Nano33_xlm = AdamGUIclass.displaySixBlock('Nano33', 'ax', 'offset', 'stdev', 'ay', 'offset', 'stdev', 'az', 'offset', 'stdev')
		self.tab2_ADXL355_xlm = AdamGUIclass.displaySixBlock('ADXL355', 'ax', 'offset', 'stdev', 'ay', 'offset', 'stdev', 'az', 'offset', 'stdev')

		###tab2 btn###
		self.tab2_cali_start_btn = AdamGUIclass.btn('cali start')
		self.tab2_cali_stop_btn = AdamGUIclass.btn('cali stop')
		''' tab3 GUI item'''
		###tab3 plot###
		self.tab3_plot1 = self.win2.addPlot(title="plot5")
		self.tab3_plot1_1 = self.tab3_plot1.plot(pen='r')
		self.tab3_plot1_2 = self.tab3_plot1.plot(pen='b')
		self.tab3_plot1_3 = self.tab3_plot1.plot(pen='k')
		###tab3 btn###
		self.tab3_xmax = AdamGUIclass.editBlockwBtn('xmax')
		self.tab3_ymax = AdamGUIclass.editBlockwBtn('ymax')
		###tab3 check box###
		self.tab3_track_cb = chkBoxBlock_3('track','Nano33', 'SRS200', 'PP')
		self.addTab(self.tab1,"Meas.")
		self.addTab(self.tab2,"Cali.")
		self.addTab(self.tab3,"Track")
		self.Tab1_UI()
		self.Tab2_UI()
		self.Tab3_UI()
		
	def Tab1_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.win, 0, 0, 20, 20)
		# layout.addWidget(self.tab1_adxlXLM_cb.layout(), 11, 7, 1, 1)
		# layout.addWidget(self.tab1_nano33XLM_cb.layout(), 12, 7, 1, 1)
		layout.addWidget(self.tab1_gyro_cb.layout(), 1, 9, 1, 1)
		layout.addWidget(self.tab1_adxlXLM_cb.layout(), 1, 19, 1, 1)
		layout.addWidget(self.tab1_speed_cb.layout(), 11, 9, 1, 1)
		layout.addWidget(self.tab1_attitude_cb.layout(), 11, 19, 1, 1)
		layout.addWidget(self.tab1_read_btn, 1, 30, 1, 1)
		layout.addWidget(self.tab1_stop_btn, 2, 30, 1, 1)
		self.tab1.setLayout(layout)

	def Tab2_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.tab2_SRS200, 0, 0, 2, 3)
		layout.addWidget(self.tab2_PP, 2, 0, 2, 3)
		layout.addWidget(self.tab2_IMU_speed, 0, 3, 2, 3)
		# layout.addWidget(self.tab2_Nano33_gyro, 6, 0, 3, 6)
		# layout.addWidget(self.tab2_Nano33_xlm, 0, 6, 6, 6)
		layout.addWidget(self.tab2_ADXL355_xlm, 0, 12, 3, 6)
		layout.addWidget(self.tab2_cali_start_btn, 0, 18, 1, 1)
		layout.addWidget(self.tab2_cali_stop_btn, 1, 18, 1, 1)

		self.tab2.setLayout(layout)

	def Tab3_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.win2, 0, 0, 10, 10)  
		layout.addWidget(self.tab3_track_cb.layout(), 1, 10, 1, 1)
		# layout.addWidget(self.tab3_xmax, 2, 10, 1, 1)
		# layout.addWidget(self.tab3_ymax, 3, 10, 1, 1)
		self.tab3.setLayout(layout)

class mainWidget(QWidget):
	def __init__(self, parent=None):
		super(mainWidget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.usb = AdamGUIclass.usbConnect()
		self.TabPlot = TabPlot()
		### label ###
		self.buffer_lb = AdamGUIclass.displayOneBlock('Buffer size')
		self.VBOX_sat_lb = AdamGUIclass.displayOneBlock('Sat#')
		self.VBOX_latitude_lb = AdamGUIclass.displayOneBlock('latitude(deg)')
		self.VBOX_longitude_lb = AdamGUIclass.displayOneBlock('longitude(deg)')
		self.VBOX_v_velocity_lb = AdamGUIclass.displayOneBlock('v_velocity(m/s)')
		self.VBOX_altitude_lb = AdamGUIclass.displayOneBlock('height(m)')
		self.VBOX_accz_lb = AdamGUIclass.displayOneBlock('accz(m/s^2)')
		###radio btn###
		self.kal_rb = QRadioButton('Kalman filter')
		self.kal_rb.setChecked(0)
		##gauge###
		self.SRS200_gauge = gaugePlotwLabel('     theta', 'theta (degree)')
		self.speed_gauge = gaugePlotwLabel('ADXL speed', 'speed (km/hr)')
		self.IMU_speed_gauge = gaugePlotwLabel('IMU speed', 'speed (km/hr)')
		##spinBlock##
		self.Q = spinBlock(title='Q', minValue=0, maxValue=100000, double=False, step=10)
		self.R = spinBlock(title='R', minValue=0, maxValue=100000, double=False, step=10)
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.usb.layoutG(), 0,0,1,3)
		mainLayout.addWidget(self.buffer_lb, 0,3,1,1)
		mainLayout.addWidget(self.kal_rb, 0,4,1,1)
		mainLayout.addWidget(self.Q, 0,5,1,1)
		mainLayout.addWidget(self.R, 0,6,1,1)
		mainLayout.addWidget(self.TabPlot, 1,0,8,8)
		# mainLayout.addWidget(self.SRS200_gauge, 0,9,3,3)
		# mainLayout.addWidget(self.speed_gauge, 3,9,3,3)
		# mainLayout.addWidget(self.IMU_speed_gauge, 6,9,3,3)		
		mainLayout.addWidget(self.VBOX_sat_lb, 1,9,1,3)
		mainLayout.addWidget(self.VBOX_latitude_lb, 2,9,1,3)
		mainLayout.addWidget(self.VBOX_longitude_lb, 3,9,1,3)
		mainLayout.addWidget(self.VBOX_v_velocity_lb, 4,9,1,3)
		mainLayout.addWidget(self.VBOX_altitude_lb, 5,9,1,3) 
		mainLayout.addWidget(self.VBOX_accz_lb, 6,9,1,3)
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
 

 
if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWidget()
	# main = TabPlot()
	main.show()
	os._exit(app.exec_())