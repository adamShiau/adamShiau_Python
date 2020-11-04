import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *
import pyqtgraph as pg 
#import cv2
import numpy as np 

CAM_GAIN_MIN = 1
CAM_GAIN_MAX = 100

CAM_TIME_MIN = 20
CAM_TIME_MAX = 1000000

POS_MIN = 1
POS_MAX = 1000000

STEP_MIN = 2
STEP_MAX = 100

DISP_MIN = 5
DISP_MAX = 1000000

TITLE_TEXT = "Academia Sinica Growth Rate Measurement System"

class bacteriaSampling(QGroupBox):
	def __init__(self, parent = None):
		super(bacteriaSampling, self).__init__(parent)
		self.setTitle("Bacteria Sampling")
		self.startx = spinBlock("Start postion", 0, 300)
		self.deltax = spinBlock("Steps", 0, 200)
		self.direction = QGroupBox("Dirction")
		self.right = QRadioButton("Right")
		self.left = QRadioButton("Left")
		self.pts = spinBlock("Sampling points", 1, 10)
		# self.set = QPushButton("Set")
		self.left.setChecked(True)
		self.bacUI()

	def bacUI(self):
		dirlayout = QHBoxLayout()
		dirlayout.addWidget(self.left)
		dirlayout.addWidget(self.right)
		self.direction.setLayout(dirlayout)
		layout = QGridLayout()
		layout.addWidget(self.startx, 0,0,1,1)
		layout.addWidget(self.deltax, 0,1,1,1)
		layout.addWidget(self.direction,1,0,1,1)
		layout.addWidget(self.pts,1,1,1,1)
		# layout.addWidget(self.set,2,1,1,1)
		self.setLayout(layout)

class autoSampler(QGroupBox):
	def __init__(self, parent=None):
		super (autoSampler, self).__init__(parent)
		self.setTitle("AutoSampler Postion")
		self.xpos = spinBlock("AutoSampler XPOS", 0, 500000)
		self.ypos = spinBlock("AutoSampler YPOS", 0, 500000)

		layout = QHBoxLayout()
		layout.addWidget(self.xpos)
		layout.addWidget(self.ypos)
		self.setLayout(layout)

class stageBlock(QGroupBox):
	def __init__(self, parent=None):
		super(stageBlock, self).__init__(parent)
		self.setTitle("Stage Postion")
		self.home = QPushButton("Home")
		self.forward = QPushButton("Forward")
		self.backward = QPushButton("Backward")
		self.left = QPushButton("Left")
		self.right = QPushButton("Right")
		self.xlabel = QLabel("X = ")
		self.xlabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.xPos = QLabel("0")
		self.ylabel = QLabel("Y = ")
		self.ylabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.yPos = QLabel("0")
		self.delta = spinBlock("Displacement", DISP_MIN, DISP_MAX)

		self.home.setEnabled(False)
		self.backward.setEnabled(False)
		self.right.setEnabled(False)

		self.stage_UI()

	def stage_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.forward, 0, 1, 1, 2)
		layout.addWidget(self.left, 1, 0, 2, 1)
		layout.addWidget(self.right, 1, 3, 2, 1)
		layout.addWidget(self.backward, 3, 1, 1, 2)
		layout.addWidget(self.home, 3, 3, 1, 1)
		layout.addWidget(self.xlabel, 1, 1, 1, 1)
		layout.addWidget(self.xPos, 1, 2, 1, 1)
		layout.addWidget(self.ylabel, 2, 1, 1, 1)
		layout.addWidget(self.yPos, 2, 2, 1, 1)
		layout.addWidget(self.delta, 4, 0, 1, 2)
		self.setLayout(layout)

class cameraBlock(QGroupBox):
	def __init__(self, parent=None):
		super(cameraBlock, self).__init__(parent)
		self.gain = spinBlock("Camera Gain", CAM_GAIN_MIN, CAM_GAIN_MAX)
		self.gainAuto = QCheckBox("Auto")
		self.exposure = spinBlock("Camera Exposure (us)", CAM_TIME_MIN, CAM_TIME_MAX)
		self.expAuto = QCheckBox("Auto")
		self.setCam = QPushButton("Camera Set")
		self.setCam.setEnabled(False)
		self.gainText = QLabel("Gain = ")
		self.gainText.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.gainValue = QLabel("( Not set )")
		self.timeText = QLabel("Exposure = ")
		self.timeText.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.timeValue = QLabel("( Not set )")
		self.camera_UI()

	def camera_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.gain, 0, 0, 1, 2)
		layout.addWidget(self.gainAuto, 0, 2, 1, 1)
		layout.addWidget(self.exposure, 1, 0, 1, 2)
		layout.addWidget(self.expAuto, 1, 2, 1, 1)
		layout.addWidget(self.setCam, 0, 3, 2, 1)
		layout.addWidget(self.gainText, 2, 0, 1, 1)
		layout.addWidget(self.gainValue, 2, 1, 1, 1)
		layout.addWidget(self.timeText, 2, 2, 1, 1)
		layout.addWidget(self.timeValue, 2, 3, 1, 1)
		self.setLayout(layout)

class preScanBlock(QGroupBox):
	def __init__(self, parent=None):
		super(preScanBlock, self).__init__(parent)
		#tab2 block items
		self.initXpos = spinBlock("Init X Postion", POS_MIN, POS_MAX)
		self.xSteps = spinBlock("X Steps", STEP_MIN, STEP_MAX)
		self.initYpos = spinBlock("Init Y Postion", POS_MIN, POS_MAX)
		self.ySteps = spinBlock("Y Steps", STEP_MIN, STEP_MAX)
		self.delta = spinBlock("Displacement", 5, 1000000)
		self.preScan = QPushButton("Prescan")
		self.preSave = QPushButton("PreScan for Save")
		self.preScan.setEnabled(False)
		self.preSave.setEnabled(False)

		self.preScan_UI()

	def preScan_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.initXpos, 0, 0, 1, 1)
		layout.addWidget(self.xSteps, 0, 1, 1, 1)
		layout.addWidget(self.initYpos, 1, 0, 1, 1)
		layout.addWidget(self.ySteps, 1, 1, 1, 1)
		layout.addWidget(self.delta, 2, 0, 1, 1)
		layout.addWidget(self.preScan, 3, 0, 1, 1)
		layout.addWidget(self.preSave, 3, 1, 1, 1)
		self.setLayout(layout)

class tabSetting(QTabWidget):
	def __init__(self, parent=None):
		super(tabSetting, self).__init__(parent)
		self.tab1 = QWidget()
		self.tab2 = QWidget()
		self.addTab(self.tab1,"Pre Scan")
		self.addTab(self.tab2,"Auto Sampler")

		self.preScan = preScanBlock()
		self.autoPos = autoSampler()
		self.bacSampling = bacteriaSampling()

		self.Tab1_UI()
		self.Tab2_UI()

	def Tab1_UI(self):
		layout = QHBoxLayout()
		layout.addWidget(self.preScan)
		self.tab1.setLayout(layout)

	def Tab2_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.autoPos)
		layout.addWidget(self.bacSampling)
		self.tab2.setLayout(layout)

class controlBlock(QWidget):
	def __init__(self, parent=None):
		super(controlBlock, self).__init__(parent)
		self.photos = []
		self.pnameS = comboBlock("Select Photo", self.photos)
		self.threshold = spinBlock("Threshold", 0, 255)
		self.analysis = QPushButton("Image Analysis")
		self.pixelCoeff = spinBlock("Pixel to length", 1, 1000, True, 0.01, 2)
		self.go = QPushButton("Go")

		self.analysis.setEnabled(False)
		self.go.setEnabled(False)
		self.Control_UI()

	def Control_UI(self):
		layout = QHBoxLayout()
		layout.addWidget(self.pnameS)
		layout.addWidget(self.threshold)
		layout.addWidget(self.analysis)
		layout.addWidget(self.pixelCoeff)
		layout.addWidget(self.go)
		self.setLayout(layout)


class mainWidget(QWidget):
	def __init__(self, parent=None):
		super (mainWidget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.connectS = connectBlock("Connect Stage")
		self.connectC = connectBlock("Connect Camera")
		self.stage = stageBlock()
		self.cam = cameraBlock()
		self.tab = tabSetting()
		self.control = controlBlock()
		self.plot = pg.ImageView()
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.connectS, 0, 0, 1, 1)
		mainLayout.addWidget(self.connectC, 0, 1, 1, 1)
		mainLayout.addWidget(self.stage, 1, 0, 3, 2)
		mainLayout.addWidget(self.cam, 4, 0, 2, 2)
		mainLayout.addWidget(self.tab, 6, 0, 3, 2)
		mainLayout.addWidget(self.control, 0, 2, 1, 7)
		mainLayout.addWidget(self.plot, 1, 2, 8, 7)

		mainLayout.setRowStretch(0, 1)
		mainLayout.setRowStretch(1, 1)
		mainLayout.setRowStretch(2, 1)
		mainLayout.setRowStretch(3, 1)
		mainLayout.setRowStretch(4, 1)
		mainLayout.setRowStretch(5, 1)
		mainLayout.setRowStretch(6, 1)
		mainLayout.setRowStretch(7, 1)
		mainLayout.setRowStretch(8, 1)
		mainLayout.setColumnStretch(0, 1)
		mainLayout.setColumnStretch(1, 1)
		mainLayout.setColumnStretch(2, 1)
		mainLayout.setColumnStretch(3, 1)
		mainLayout.setColumnStretch(4, 1)
		mainLayout.setColumnStretch(5, 1)
		mainLayout.setColumnStretch(6, 1)
		mainLayout.setColumnStretch(7, 1)
		mainLayout.setColumnStretch(8, 1)
		self.setLayout(mainLayout)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWidget()
	main.show()
	os._exit(app.exec_())
