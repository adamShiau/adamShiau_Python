import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *
import pyqtgraph as pg 
#import cv2
import numpy as np 

TITLE_TEXT = "Academia Sinica Growth Rate Measurement System"

class stageBlock(QGroupBox):
	def __init__(self, parent=None):
		super(stageBlock, self).__init__(parent)
		self.setTitle("Stage Postion")
		self.home = QPushButton("Home")
		self.up = QPushButton("Forward")
		self.down = QPushButton("Backward")
		self.left = QPushButton("Left")
		self.right = QPushButton("Right")
		self.xlabel = QLabel("X = ")
		self.xlabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.xPos = QLabel("0")
		self.ylabel = QLabel("Y = ")
		self.ylabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.yPos = QLabel("0")

		self.home.setEnabled(False)
		self.up.setEnabled(False)
		self.left.setEnabled(False)

		self.stage_UI()

	def stage_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.home, 0, 0, 1, 1)
		layout.addWidget(self.up, 0, 1, 1, 2)
		layout.addWidget(self.down, 3, 1, 1, 2)
		layout.addWidget(self.left, 1, 0, 2, 1)
		layout.addWidget(self.right, 1, 3, 2, 1)
		layout.addWidget(self.xlabel, 1, 1, 1, 1)
		layout.addWidget(self.xPos, 1, 2, 1, 1)
		layout.addWidget(self.ylabel, 2, 1, 1, 1)
		layout.addWidget(self.yPos, 2, 2, 1, 1)
		self.setLayout(layout)


class TabSetting(QTabWidget):
	def __init__(self, parent=None):
		super(TabSetting, self).__init__(parent)
		self.tab1 = QWidget()
		self.tab2 = QWidget()
		self.addTab(self.tab1,"Hardware")
		self.addTab(self.tab2,"New Plate Setting")

		#tab1 block items
		self.connectS = connectBlock("Connect Stage")
		self.connectC = connectBlock("Connect Camera")
		self.stage = stageBlock()
		self.gain = spinBlock("Camera Gain", 1, 100)
		self.gainAuto = QCheckBox("Auto")
		self.explorgure = spinBlock("Camera Explorgure (us)", 20, 1000000)
		self.explorAuto = QCheckBox("Auto")
		self.setCam = QPushButton("Camera Set")

		self.setCam.setEnabled(False)

		#tab2 block items
		self.initXpos = spinBlock("Init X Postion", 1, 100)
		self.xSteps = spinBlock("X Steps", 2, 100)
		self.initYpos = spinBlock("Init Y Postion", 3, 100)
		self.ySteps = spinBlock("Y Steps", 2, 100)
		self.delta = spinBlock("Displacement", 5, 100)
		self.pname = editBlock("Petri Dish Name")
		self.maxNum = spinBlock("Analysis Quanty", 2, 100)
		self.calFact = spinBlock("Calibration Factor", 7, 100)
		self.fpathBtn = QPushButton("File Path")
		self.fpath = QLabel("")
		self.preScan = QPushButton("Prescan")
		self.create = QPushButton("Create")

		self.preScan.setEnabled(False)

		self.Tab1_UI()
		self.Tab2_UI()

	def Tab1_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.connectS, 0, 0, 1, 2)
		layout.addWidget(self.connectC, 0, 2, 1, 2)
		layout.addWidget(self.stage, 1, 0, 2, 4)
		layout.addWidget(self.gain, 3, 0, 1, 2)
		layout.addWidget(self.gainAuto, 3, 2, 1, 1)
		layout.addWidget(self.explorgure, 4, 0, 1, 2)
		layout.addWidget(self.explorAuto, 4, 2, 1, 1)
		layout.addWidget(self.setCam, 3, 3, 2, 1)
		self.tab1.setLayout(layout)

	def Tab2_UI(self):
		layout = QGridLayout()
		layout.addWidget(self.initXpos, 0, 0, 1, 2)
		layout.addWidget(self.xSteps, 0, 2, 1, 2)
		layout.addWidget(self.initYpos, 1, 0, 1, 2)
		layout.addWidget(self.ySteps, 1, 2, 1, 2)
		layout.addWidget(self.delta, 2, 0, 1, 2)
		layout.addWidget(self.pname, 2, 2, 1, 2)
		layout.addWidget(self.maxNum, 3, 0, 1, 2)
		layout.addWidget(self.calFact, 3, 2, 1, 2)
		layout.addWidget(self.fpathBtn, 4, 0, 1, 1)
		layout.addWidget(self.fpath, 4, 1, 1, 3)
		layout.addWidget(self.preScan, 5, 0, 1, 2)
		layout.addWidget(self.create, 5, 2, 1, 2)

		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 1)
		layout.setColumnStretch(2, 1)
		layout.setColumnStretch(3, 1)
		self.tab2.setLayout(layout)

	# def Tab4_UI(self):
	# 	layout = QGridLayout()
	# 	layout.addWidget(self.connectC, 0, 0, 1, 3)
		
	# 	layout.setColumnStretch(0, 1)
	# 	layout.setColumnStretch(1, 1)
	# 	layout.setColumnStretch(2, 1)
	# 	self.tab4.setLayout(layout)

class controlBlock(QWidget):
	def __init__(self, parent=None):
		super(controlBlock, self).__init__(parent)
		self.pname_list = []
		self.pnameS = comboBlock("Petri Dish Name", self.pname_list)
		self.delete = QPushButton("Delete")
		self.threshold = spinBlock("Threshold",90, 255)
		self.test = QPushButton("Image Test")
		self.tolerance = spinBlock("Tolerance",10, 105)
		self.scan = QPushButton("Scan")
		self.delete.setEnabled(False)
		self.test.setEnabled(False)
		# self.scan.setEnabled(False)

		self.Control_UI()

	def Control_UI(self):
		layout = QHBoxLayout()
		layout.addWidget(self.pnameS)
		layout.addWidget(self.delete)
		layout.addWidget(self.threshold)
		layout.addWidget(self.test)
		layout.addWidget(self.tolerance)
		layout.addWidget(self.scan)
		self.setLayout(layout)


class TabPlot(QTabWidget):
	def __init__(self, parent=None):
		super(TabPlot, self).__init__(parent)
		self.tab1 = QWidget()
		self.tab2 = QWidget()
		# self.plot1 = pg.ImageView()
		self.plot1 = outputPlot()
		self.plot2 = pg.PlotWidget()
		a = np.linspace(100, 1, 100)
		self.plot2.plot(a)
		self.addTab(self.tab1,"Image")
		self.addTab(self.tab2,"Rate")
		self.Tab1_UI()
		self.Tab2_UI()

	def Tab1_UI(self):
		layout = QVBoxLayout()
		layout.addWidget(self.plot1)
		self.tab1.setLayout(layout)

	def Tab2_UI(self):
		layout = QVBoxLayout()
		layout.addWidget(self.plot2)
		self.tab2.setLayout(layout)


class mainWidget(QWidget):
	def __init__(self, parent=None):
		super (mainWidget, self).__init__(parent)
		self.setWindowTitle(TITLE_TEXT)
		self.tab = TabSetting()
		self.otputText = QLabel("Size and Location Information")
		self.otputText.setAlignment(Qt.AlignTop)
		self.control = controlBlock()
		self.tabPlot = TabPlot()
		self.main_UI()

	def main_UI(self):
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.tab, 0, 0, 5, 1)
		mainLayout.addWidget(self.otputText, 5, 0, 1, 1)
		mainLayout.addWidget(self.control, 0, 1, 1, 1)
		mainLayout.addWidget(self.tabPlot, 1, 1, 5, 1)
		mainLayout.setRowStretch(0, 1)
		mainLayout.setRowStretch(1, 1)
		mainLayout.setRowStretch(2, 1)
		mainLayout.setRowStretch(3, 1)
		mainLayout.setRowStretch(4, 1)
		mainLayout.setRowStretch(5, 5)
		mainLayout.setColumnStretch(0, 2)
		mainLayout.setColumnStretch(1, 5)
		self.setLayout(mainLayout)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = mainWidget()
	main.show()
	os._exit(app.exec_())
