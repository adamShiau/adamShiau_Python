#!/usr/bin/env python
#-*- coding:UTF-8 -*-
from __future__ import print_function
import os
import sys
import logging
from AdamGUIclass_ros import *
# import py3lib
# from py3lib import *
# from py3lib.AdamGUIclass import *
TITLE_TEXT = "Gyro"

class TabPlot(QTabWidget):
	def __init__(self, parent=None):
		super(TabPlot, self).__init__(parent)
		
		########Tab1 widget items##################
		''' Tab1  '''
		self.tab1 = QWidget()
		self.com_plot1 = outputPlotSize(16)
		self.com_plot2 = outputPlotSize(16)
		self.addTab(self.tab1,"Normal Mode")
		self.Tab1_UI()
		''' Tab2 '''
		self.tab2 = QWidget()
		self.sf_g = editBlock('g factor')
		self.ori_x = editBlock('ori. x')
		self.ori_y = editBlock('ori. y')
		self.ori_z = editBlock('ori. z')
		self.ori_w = editBlock('ori. w')
		self.ori_cov = edit9Block('orientation covariance')
		self.gyro_cov = edit9Block('gyro covariance')
		self.axlm_cov = edit9Block('accelerometer covariance')
		self.addTab(self.tab2,"ROS Mode")
		self.Tab2_UI()
		
	def Tab1_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.com_plot1, 0,0,5,10)
		layout.addWidget(self.com_plot2, 5,0,5,10)		
		self.tab1.setLayout(layout)
		
	def Tab2_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.sf_g, 0,0,1,1)
		layout.addWidget(self.ori_x, 1,0,1,1)
		layout.addWidget(self.ori_y, 1,1,1,1)
		layout.addWidget(self.ori_z, 1,2,1,1)
		layout.addWidget(self.ori_w, 1,3,1,1)
		layout.addWidget(self.ori_cov, 5,0,3,3)
		layout.addWidget(self.gyro_cov, 8,0,3,3)
		layout.addWidget(self.axlm_cov, 11,0,3,3)
		self.tab2.setLayout(layout)


class mainWidget(QWidget):
	def __init__(self, parent=None):
		super(mainWidget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.TabPlot = TabPlot()
		self.usb = usbConnect()
		self.read_btn = btn('read')
		self.stop_btn = btn('stop')
		''' spin box'''
		self.wait_cnt = spinBlock(title='Wait cnt', minValue=0, maxValue=100, double=False, step=1)
		self.avg = spinBlock(title='avg', minValue=0, maxValue=6, double=False, step=1)
		self.err_offset = spinBlock(title='Err offset', minValue=-10000, maxValue=10000, double=False, step=1)
		self.polarity = spinBlock(title='polarity', minValue=0, maxValue=1, double=False, step=1)
		self.mod_H = spinBlock(title='MOD_H', minValue=-32768, maxValue=32767, double=False, step=100)
		self.mod_L = spinBlock(title='MOD_L', minValue=-32768, maxValue=0, double=False, step=100)
		self.gain1 = spinBlock(title='GAIN1', minValue=0, maxValue=14, double=False, step=1)
		self.gain2 = spinBlock(title='GAIN2', minValue=0, maxValue=14, double=False, step=1)
		self.const_step = spinBlock(title='const_step', minValue=-32768, maxValue=32767, double=False, step=1)
		self.dac_gain = spinBlock(title='DAC_GAIN', minValue=0, maxValue=1023, double=False, step=10)
		# self.v2piN = spinBlock(title='V2PI_N', minValue=-32768, maxValue=-2000, double=False, step=1000)
		self.fb_on = spinBlock(title='mode(0:OPEN)', minValue=0, maxValue=2, double=False, step=1)
		self.err_th = spinBlock(title='ERR_TH', minValue=0, maxValue=16384, double=False, step=1)
		self.freq = spinBlockOneLabel(title='frequency', minValue=10, maxValue=1500, double=False, step=1)
		self.SW_Q = spinBlock(title='SW_Q', minValue=1, maxValue=100000, double=False, step=1)
		self.SW_R = spinBlock(title='SW_R', minValue=0, maxValue=100000, double=False, step=1)
		# self.trigDelay = spinBlock(title='trigDelay', minValue=0, maxValue=150, double=False, step=1)
		self.HD_Q = spinBlock(title='FPGA_Q', minValue=1, maxValue=100000, double=False, step=1)
		self.HD_R = spinBlock(title='FPGA_R', minValue=0, maxValue=100000, double=False, step=1)
		# self.dataRate = spinBlock(title='DATE RATE', minValue=1000, maxValue=3000, double=False, step=5)
		'''slider'''
		self.dataRate_sd = sliderBlock(title='DATE RATE', minValue=800, maxValue=2200, curValue=2135, interval=100)
		# self.dataRate_sd.setEnabled(False)
		'''radio btn'''
		self.Kal_rb = QRadioButton('Kalman filter')
		self.Kal_rb.setChecked(0)
		self.trig_mode_rb = radioBot_2(title='TRIG MODE', name1='INT', name2='EXT')
		self.trig_mode_rb.rb1.setChecked(1)
		''' plot '''
		self.com_plot1 = outputPlotSize(16)
		self.com_plot2 = outputPlotSize(16)
		''' label'''
		self.buffer_lb = displayOneBlock('Buffer size')
		self.temperature_lb = displayOneBlock('PD temp.')
		self.dataRate_lb = displayOneBlock('')
		''' edit line '''
		self.save_text = editBlockwChkBox('save file')
		self.sf_a = editBlock('SF_a')
		self.sf_b = editBlock('SF_b')
		
		
		self.main_UI()
		

	def main_UI(self):
		mainLayout = QGridLayout()
		###usb###
		mainLayout.addWidget(self.usb.layoutG(), 0,0,1,3)
		###Tab###
		mainLayout.addWidget(self.TabPlot, 2,0,10,10)
		###label###
		mainLayout.addWidget(self.buffer_lb, 0,3,1,2)		
		mainLayout.addWidget(self.temperature_lb, 0,5,1,2) 
		mainLayout.addWidget(self.dataRate_lb, 1,3,1,3)
		###btn###
		mainLayout.addWidget(self.read_btn, 0,7,1,1)
		mainLayout.addWidget(self.stop_btn, 0,8,1,1)
		
		### rb ###
		mainLayout.addWidget(self.Kal_rb, 0,12,1,1) 
		mainLayout.addWidget(self.trig_mode_rb.H_layout(),1,0,1,2 )
		### slider ###
		mainLayout.addWidget(self.dataRate_sd, 1,2,1,1) 
		### save Line Edit ###
		mainLayout.addWidget(self.save_text, 0,10,1,2)
		mainLayout.addWidget(self.sf_a, 10,10,1,2)
		mainLayout.addWidget(self.sf_b, 10,12,1,2)
		###spin Box###
		mainLayout.addWidget(self.wait_cnt, 1,10,1,2)
		mainLayout.addWidget(self.avg, 1,12,1,2)
		mainLayout.addWidget(self.mod_H, 2,10,1,2)
		mainLayout.addWidget(self.mod_L, 2,12,1,2)
		mainLayout.addWidget(self.err_offset, 3,10,1,2)
		mainLayout.addWidget(self.polarity, 3,12,1,2)
		mainLayout.addWidget(self.gain1, 4,10,1,2)
		mainLayout.addWidget(self.const_step, 5,12,1,2)
		mainLayout.addWidget(self.dac_gain, 5,10,1,2) 
		mainLayout.addWidget(self.gain2, 4,12,1,2)
		mainLayout.addWidget(self.fb_on, 6,12,1,2)
		mainLayout.addWidget(self.err_th, 6,10,1,2)
		mainLayout.addWidget(self.freq, 7,10,1,4) 
		
		mainLayout.addWidget(self.HD_Q, 8,10,1,2) 
		mainLayout.addWidget(self.HD_R, 8,12,1,2)  
		mainLayout.addWidget(self.SW_Q, 9,10,1,2) 
		mainLayout.addWidget(self.SW_R, 9,12,1,2) 
		
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