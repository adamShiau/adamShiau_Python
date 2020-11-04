import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *
import pyqtgraph as pg 
#import cv2
import numpy as np 

TITLE_TEXT = "INTERFEROMETER"

POS_MIN = 0
POS_MAX = 25000
POS_STEP = 0.03

CAM_GAIN_MIN = 1
CAM_GAIN_MAX = 400

CAM_TIME_MIN = 20
CAM_TIME_MAX = 1000000

CAM_TEMP_MIN = -70
CAM_TEMP_MAX = 20

SPEED_MIN = 0.001
SPEED_MAX = 2
SPEED_STEP = 0.001

AVERAGE_MIN = 1
AVERAGE_MAX = 100

class stageBlock(QGroupBox):
	def __init__(self, parent=None):
		super(stageBlock, self).__init__(parent)
		self.setTitle("Adjust Postion")
		self.home = QPushButton("Home")
		self.forward = QPushButton("Forward")
		self.backward = QPushButton("Backward")
		self.home.setEnabled(False)
		self.poslabel = QLabel("POS = ")
		self.poslabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.pos = QLabel("0 um")
		self.forward.setEnabled(False)
		self.backward.setEnabled(False)
		self.home.setEnabled(False)
		self.stage_UI()

	def stage_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.forward, 0, 0, 1, 2)
		layout.addWidget(self.home, 1, 0, 1, 2)
		layout.addWidget(self.backward, 2, 0, 1, 2)
		layout.addWidget(self.poslabel, 3, 0, 1, 1)
		layout.addWidget(self.pos, 3, 1, 1, 1)
		self.setLayout(layout)


class HWSetting(QWidget):
	def __init__(self, parent=None):
		super(HWSetting, self).__init__(parent)

		self.connectS = connectBlock("Connect Stage")
		self.connectC = connectBlock("Connect Camera")
		self.stage = stageBlock()
		self.speed = spinBlock("Stage Velocity (mm/s)", SPEED_MIN, SPEED_MAX, True, SPEED_STEP, 3)
		self.setSpeed = QPushButton("Set Speed")
		self.goPos = spinBlock("Go To Pos (um)", POS_MIN, POS_MAX, True, POS_STEP, 2 )
		self.gotoBtn = QPushButton("Go")
		self.gain = spinBlock("Camera Gain", CAM_GAIN_MIN, CAM_GAIN_MAX)
		self.time = spinBlock("Camera Explorgure (ms)", CAM_TIME_MIN, CAM_TIME_MAX)
		self.temp = spinLabelBlock("Camera Temperaturep","Tcam=", "N/A" ,CAM_TEMP_MIN, CAM_TEMP_MAX)
		self.setCam = QPushButton("Camera Set")
		self.getImg = QPushButton("Get Image")
		self.camOff = QPushButton("Shutter Off")

		self.setSpeed.setEnabled(False)
		self.gotoBtn.setEnabled(False)
		self.setCam.setEnabled(False)
		self.getImg.setEnabled(False)
		self.camOff.setEnabled(False)

		self.gain.spin.valueChanged.connect(self.enableSetCam)
		self.time.spin.valueChanged.connect(self.enableSetCam)
		self.temp.spin.valueChanged.connect(self.enableSetCam)

		self.HW_UI()

	def HW_UI(self):
		layout = QVBoxLayout()
		layout.addWidget(self.connectS)
		layout.addWidget(self.connectC)
		layout.addWidget(self.gain)
		layout.addWidget(self.time)
		layout.addWidget(self.temp)
		layout.addWidget(self.setCam)
		layout.addWidget(self.getImg)
		layout.addWidget(self.camOff)
		layout.addWidget(self.stage)
		layout.addWidget(self.speed)
		layout.addWidget(self.setSpeed)
		layout.addWidget(self.goPos)
		layout.addWidget(self.gotoBtn)
		self.setLayout(layout)

	def enableSetCam(self):
		self.setCam.setEnabled(True)


class controlBlock(QWidget):
	def __init__(self, parent=None):
		super(controlBlock, self).__init__(parent)
		self.scanFrom = spinBlock("From Pos (um)", POS_MIN, POS_MAX, True, POS_STEP, 2 )
		self.scanTo = spinBlock("To Pos (um)", POS_MIN, POS_MAX, True, POS_STEP, 2 )
		self.delta = spinBlock("Delta (um)", POS_MIN, POS_MAX, True, POS_STEP, 2 )
		self.average = spinBlock("Average number", AVERAGE_MIN, AVERAGE_MAX)
		self.scan = QPushButton("Scan")
		self.stop = QPushButton("Stop")

		self.scan.setEnabled(False)
		self.stop.setEnabled(False)
		self.scanFrom.spin.valueChanged.connect(self.update_scanTo)
		# self.scanTo.spin.valueChanged.connect(self.update_scanFrom)

		self.Control_UI()

	def Control_UI(self):
		layout = QHBoxLayout()
		layout.addWidget(self.scanFrom)
		layout.addWidget(self.scanTo)
		layout.addWidget(self.delta)
		layout.addWidget(self.average)
		layout.addWidget(self.scan)
		layout.addWidget(self.stop)
		self.setLayout(layout)

	def update_scanTo(self):
		scanFrom = self.scanFrom.spin.value()
		self.scanTo.spin.setRange(scanFrom, POS_MAX)

	# def update_scanFrom(self):
	# 	scanTo = self.scanTo.spin.value()
	# 	self.scanFrom.spin.setRange(POS_MIN, scanTo)
	# 	self.delta.spin.setRange(POS_MIN, scanTo)

class mainWidget(QWidget):
	def __init__(self, parent=None):
		super (mainWidget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.hw = HWSetting()
		# self.otputText = QLabel("Size and Location Information")
		# self.otputText.setAlignment(Qt.AlignTop)
		self.control = controlBlock()
		self.plot1 = pg.ImageView()
		# self.plot1.disableAutoRange()
		self.roi = pg.ROI([0,0],[50,50], pen = pg.mkPen('r', width=3))
		self.roi.addScaleHandle((1,1),(0,0))
		self.plot1.addItem(self.roi)
		self.save1 = QPushButton("Save")
		self.plot2 = pg.PlotWidget()
		self.save2 = QPushButton("Save")
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.hw, 0, 0, 7, 1)
		# mainLayout.addWidget(self.otputText, 5, 0, 4, 3)
		mainLayout.addWidget(self.control, 0, 1, 1, 7)
		mainLayout.addWidget(self.plot1, 1, 1, 4, 6)
		mainLayout.addWidget(self.save1, 1, 7, 1, 1)
		mainLayout.addWidget(self.plot2, 5, 1, 5, 6)
		mainLayout.addWidget(self.save2, 5, 7, 1, 1)
		mainLayout.setRowStretch(0, 1)
		mainLayout.setRowStretch(1, 1)
		mainLayout.setRowStretch(2, 1)
		mainLayout.setRowStretch(3, 1)
		mainLayout.setRowStretch(4, 1)
		mainLayout.setRowStretch(5, 1)
		mainLayout.setRowStretch(6, 1)
		mainLayout.setRowStretch(7, 1)
		mainLayout.setRowStretch(8, 1)
		mainLayout.setRowStretch(9, 1)
		mainLayout.setColumnStretch(0, 1)
		mainLayout.setColumnStretch(1, 1)
		mainLayout.setColumnStretch(2, 1)
		mainLayout.setColumnStretch(3, 1)
		mainLayout.setColumnStretch(4, 1)
		mainLayout.setColumnStretch(5, 1)
		mainLayout.setColumnStretch(6, 1)
		mainLayout.setColumnStretch(7, 1)
		# mainLayout.setColumnStretch(8, 1)
		# mainLayout.setColumnStretch(9, 1)
		self.setLayout(mainLayout)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWidget()
	main.show()
	os._exit(app.exec_())
