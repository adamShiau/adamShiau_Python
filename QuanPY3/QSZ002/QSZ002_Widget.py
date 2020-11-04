import os
import sys
import logging
sys.path.append("../")
from py3lib.QuGUIclass import *
TITLE_TEXT = "GRC ElectroChemical Analysis"

class SpecPumpInput(QWidget):
	def __init__(self, parent = None):
		super(SpecPumpInput, self).__init__(parent)
		self.rate = spinBlock("Pump rate(ml/min)",0.01,100, True, 0.01, 2)
		self.intTime=spinBlock("Integration Time(us)", 5000, 10000000)
		self.avgNumber=spinBlock("Data Average Number", 1,50)
		self.filterLevel=spinBlock("Noise Filter Level", 0, 10)
		self.minWavelength=spinBlock("Minimum Wavelength", 200, 999)
		self.maxWavelength=spinBlock("Maximum Wavelength", 201, 1000)
		self.threshold = spinBlock("Threshold", 0, 1000000)
		self.filterLevel = spinBlock("Filter Level", 1, 10)
		self.useFilter = QCheckBox("Use Filtered Data")
		self.runSpectrum = QPushButton("Run Spectrum")
		self.control = QPushButton("Control")
		self.stop = QPushButton("stop")
		self.setUI()
	
	def setUI(self):
		layout =QVBoxLayout()
		layout.addWidget(self.rate)
		layout.addWidget(self.intTime)
		layout.addWidget(self.avgNumber)
		layout.addWidget(self.filterLevel)
		layout.addWidget(self.minWavelength)
		layout.addWidget(self.maxWavelength)
		layout.addWidget(self.threshold)
		layout.addWidget(self.filterLevel)
		layout.addWidget(self.useFilter)
		layout.addWidget(self.runSpectrum)
		layout.addWidget(self.control)
		layout.addWidget(self.stop)
		self.setLayout(layout)



class mainWidget(QWidget):
	def __init__(self, parent=None):
	    super (mainWidget, self).__init__(parent)
	    self.setWindowTitle(TITLE_TEXT)
	    self.open = connectBlock("Device Connect")
	    self.plot = output2Plot()
	    self.setting = SpecPumpInput()
	    self.main_UI()

	def main_UI(self):
	    mainLayout = QGridLayout()
	    mainLayout.addWidget(self.open, 0,1,1,1)
	    mainLayout.addWidget(self.setting, 1,1, 9, 1)
	    mainLayout.addWidget(self.plot, 0,0,10,1)
	    mainLayout.setRowStretch(0, 1)
	    mainLayout.setRowStretch(1, 8)
	    mainLayout.setColumnStretch(0, 4)
	    mainLayout.setColumnStretch(1, 1)
	    self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
