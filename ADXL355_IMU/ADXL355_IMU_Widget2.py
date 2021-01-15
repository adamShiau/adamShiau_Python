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
		###tab1 plot###
		self.tab1_plot1 = outputPlotSize(16)
		self.tab1_plot2 = outputPlotSize(16)
		self.tab1_plot3 = outputPlotSize(16)
		self.tab1_plot4 = outputPlotSize(16)
		###tab1 check box###
		self.tab1_gyro_cb = chkBoxBlock_2('','Nano33', 'PP')
		self.tab1_adxlXLM_cb = chkBoxBlock_2( 'ADXL355', 'ax', 'ay')
		self.tab1_nano33XLM_cb = chkBoxBlock_2('Nano33', 'ax', 'ay')
		self.tab1_speed_cb = chkBoxBlock_2( '', 'ADXL355', 'Nano33')
		###tab1 btn###
		self.tab1_read_btn = Read_btn()
		self.tab1_stop_btn = Stop_btn()
		
		###tab2 label###
		self.tab2_SRS200 = AdamGUIclass.displayTwoBlock('SRS200_wz', 'offset', 'stdev')
		self.tab2_PP = AdamGUIclass.displayTwoBlock('PP_wz', 'offset', 'stdev')
		self.tab2_Nano33_gyro = AdamGUIclass.displayTwoBlock('Nano33_wz', 'offset', 'stdev')
		self.tab2_Nano33_xlm = AdamGUIclass.displaySixBlock('Nano33', 'ax', 'offset', 'stdev', 'ay', 'offset', 'stdev', 'az', 'offset', 'stdev')
		self.tab2_ADXL355_xlm = AdamGUIclass.displaySixBlock('ADXL355', 'ax', 'offset', 'stdev', 'ay', 'offset', 'stdev', 'az', 'offset', 'stdev')

		###tab2 btn###
		self.tab2_cali_start_btn = AdamGUIclass.btn('cali start')
		self.tab2_cali_stop_btn = AdamGUIclass.btn('cali stop')

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
		# self.SRS200 = displayTwoBlock()
		### btn ###
		# self.read_btn = Read_btn()
		# self.stop_btn = Stop_btn()
		# self.cali_btn = Cali_btn()
		# self.cali_stop_btn = Cali_stop_btn()
		
		# self.save_edit = Save_edit();
		# self.updataCom = comportComboboxBlock(group_name='updata comport', btn_name='renew')
		# self.updataCom = Updata_COM_btn()
		# self.com_sel = Comport_sel()
		
		###guage###
		# self.wz_gauge = gaugePlot()
		
		###label###
		# self.wzOffset_lb = labelBlock('wz offset')
		# self.wzStd_lb = labelBlock('wz stdev')
		# self.diffwzStd_lb = labelBlock('diffWz stdev')
		
		# self.wz200Offset_lb = labelBlock('wz200 offset')
		# self.wz200Std_lb = labelBlock('wz200 stdev')
		
		# self.wxOffset_lb = labelBlock('wx offset')
		# self.wxStd_lb = labelBlock('wx stdev')
		# self.diffwxStd_lb = labelBlock('diffWx stdev')
		
		# self.wyOffset_lb = labelBlock('wy offset')
		# self.wyStd_lb = labelBlock('wy stdev')
		# self.diffwyStd_lb = labelBlock('diffWy stdev')
		
		# self.axOffset_lb = labelBlock('ax offset_nano')
		# self.axStd_lb = labelBlock('ax stdev_nano')
		# self.diffaxStd_lb = labelBlock('diffax stdev')
		
		# self.ayOffset_lb = labelBlock('ay offset_nano')
		# self.ayStd_lb = labelBlock('ay stdev_nano')
		# self.diffayStd_lb = labelBlock('diffay stdev')
		
		# self.axOffsetAD_lb = labelBlock('ax offset_355')
		# self.axStdAD_lb = labelBlock('ax stdev_355')
		
		# self.ayOffsetAD_lb = labelBlock('ay offset_355')
		# self.ayStdAD_lb = labelBlock('ay stdev_355')
		
		# pe = QPalette()
		# pe.setColor(QPalette.WindowText, Qt.blue)
		
		# self.theta_lb = QLabel();
		# self.theta_lb.setPalette(pe)
		# self.theta_lb.setFont(QFont('Arial', 20)) 
		# self.theta_lb.setText('theta')
		
		# self.theta200_lb = QLabel();
		# self.theta200_lb.setPalette(pe)
		# self.theta200_lb.setFont(QFont('Arial', 20)) 
		# self.theta200_lb.setText('theta200')
		
		# self.buffer_lb = QLabel();
		# self.buffer_lb.setPalette(pe)
		# self.buffer_lb.setFont(QFont('Arial', 20)) 
		# self.buffer_lb.setText('buffer')
		
		
		###check box###
		# self.cb = chkBoxBlock('ax','ay','wz','vx','vy','thetaz')
		# self.cb.wz_cb.setChecked(1)
		# self.cb.wz200_cb.setChecked(1)
		# self.cb.thetaz_cb.setChecked(1)
		
		###radio btn###
		# self.mv_rb = QRadioButton('MV')
		# self.mv_rb.setChecked(0)
		
		###line editor###
		# self.wzOffset_le = QLineEdit()
		# self.wzOffset_le.setFixedWidth(100)
		# self.wzOffset_le.setText('0')
		# self.wzVth_le = QLineEdit()
		# self.wzVth_le.setFixedWidth(100)
		# self.wzVth_le.setText('0')
		
		# self.wz200Offset_le = QLineEdit()
		# self.wz200Offset_le.setFixedWidth(100)
		# self.wz200Offset_le.setText('0')
		
		# self.wxOffset_le = QLineEdit()
		# self.wxOffset_le.setFixedWidth(100)
		# self.wxOffset_le.setText('0')
		# self.wxVth_le = QLineEdit()
		# self.wxVth_le.setFixedWidth(100)
		# self.wxVth_le.setText('0')
		
		# self.wyOffset_le = QLineEdit()
		# self.wyOffset_le.setFixedWidth(100)
		# self.wyOffset_le.setText('0')
		# self.wyVth_le = QLineEdit()
		# self.wyVth_le.setFixedWidth(100)
		# self.wyVth_le.setText('0')
		
		# self.axOffset_le = QLineEdit()
		# self.axOffset_le.setFixedWidth(100)
		# self.axOffset_le.setText('0')
		# self.axVth_le = QLineEdit()
		# self.axVth_le.setFixedWidth(100)
		# self.axVth_le.setText('0')
		
		# self.axOffsetAD_le = QLineEdit()
		# self.axOffsetAD_le.setFixedWidth(100)
		# self.axOffsetAD_le.setText('0')
		
		# self.ayOffset_le = QLineEdit()
		# self.ayOffset_le.setFixedWidth(100)
		# self.ayOffset_le.setText('0')
		# self.ayVth_le = QLineEdit()
		# self.ayVth_le.setFixedWidth(100)
		# self.ayVth_le.setText('0')
		
		# self.ayOffsetAD_le = QLineEdit()
		# self.ayOffsetAD_le.setFixedWidth(100)
		# self.ayOffsetAD_le.setText('0')
		
		# self.com_plot = output2Plot() 
		# self.com_plot = output3Plot() 
		# self.com_plot = output4Plot()
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.usb.layoutG(), 0,0,1,2)
		mainLayout.addWidget(self.buffer_lb, 0,2,1,2)
		mainLayout.addWidget(self.TabPlot, 1,0,10,10)
		
		
		# mainLayout.addWidget(self.updataCom.layout(), 0,1,1,3)
		
		# mainLayout.addWidget(self.com_sel, 0,1,1,1) ax_rb
		
		###gauge###
		# mainLayout.addWidget(self.wz_gauge, 0,4,3,3)
		
		###check box###
		# mainLayout.addWidget(self.cb.layout(), 15,0)
		
		###btn###
		# mainLayout.addWidget(self.read_btn, 2,1,1,1)
		# mainLayout.addWidget(self.stop_btn, 2,2,1,1)
		# mainLayout.addWidget(self.cali_btn, 3,1,1,1)
		# mainLayout.addWidget(self.cali_stop_btn, 3,2,1,1) 
		# mainLayout.addWidget(self.mv_rb, 3,3)
		
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
		
		# mainLayout.addWidget(self.axOffsetAD_lb, 4,3)
		# mainLayout.addWidget(self.axStdAD_lb, 4,4)
		# mainLayout.addWidget(self.axOffsetAD_le, 5,3,1,1)
		
		# mainLayout.addWidget(self.ayOffset_lb, 6,1)
		# mainLayout.addWidget(self.ayStd_lb, 6,2)
		# mainLayout.addWidget(self.ayOffset_le, 7,1,1,1)
		
		# mainLayout.addWidget(self.ayOffsetAD_lb, 6,3)
		# mainLayout.addWidget(self.ayStdAD_lb, 6,4)
		# mainLayout.addWidget(self.ayOffsetAD_le, 7,3,1,1)
		
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
	# main = TabPlot()
	main.show()
	os._exit(app.exec_())