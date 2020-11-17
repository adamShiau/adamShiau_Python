from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

PLOT_FONTSIZE = 14
PLOT_FONTSIZE_S = 10

class spinBlock(QGroupBox):
	def __init__(self, title, minValue, maxValue, double = False, step = 1, Decimals = 2, parent=None):
		super(spinBlock, self).__init__(parent)
		if (double):
			self.spin = QDoubleSpinBox()
			self.spin.setDecimals(Decimals)
		else:
			self.spin = QSpinBox()

		self.spin.setRange(minValue, maxValue)
		self.spin.setSingleStep(step)
		self.setTitle(title)

		layout = QHBoxLayout() 
		layout.addWidget(self.spin)     
		self.setLayout(layout)

class comportComboboxBlock():
	def __init__(self, btn_name="updata", group_name='updata comport'):
		# super(comportComboboxBlock, self).__init__(parent)
		self.groupBox = QGroupBox(group_name)
		self.updata = QPushButton(btn_name)
		self.cs = QComboBox()
		self.lb = QLabel("")
		
	def layout(self):   
		# layout = QVBoxLayout() 
		layout = QGridLayout()
		layout.addWidget(self.updata, 0,0,1,1)
		layout.addWidget(self.cs, 1,0,1,1)
		layout.addWidget(self.lb, 2,0,1,3)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox
		
		
		
class spinLabelBlock(QGroupBox):
	def __init__(self, title, labelname, labelvalue, minValue, maxValue, double = False, step = 1, Decimals = 2, parent=None):
		super(spinLabelBlock, self).__init__(parent)
		if double :
			self.spin = QDoubleSpinBox()
			self.spin.setDecimals(Decimals)
		else:
			self.spin = QSpinBox()

		self.spin.setRange(minValue, maxValue)
		self.spin.setSingleStep(step)
		self.labelname = QLabel(labelname)
		self.labelvalue = QLabel(labelvalue)
		self.setTitle(title)

		layout = QHBoxLayout()
		layout.addWidget(self.spin)
		layout.addWidget(self.labelname)
		layout.addWidget(self.labelvalue)
		self.setLayout(layout)


class checkEditBlock(QWidget):
	def __init__(self, name, min, max, parent=None):
		super(checkEditBlock, self).__init__(parent)
		self.name = name
		self.check = QCheckBox(name)
		self.value = QLineEdit()
		self.value.setValidator(QDoubleValidator(min, max, 4))

		layout = QHBoxLayout()
		layout.addWidget(self.check)
		layout.addWidget(self.value)
		self.setLayout(layout)


class editBlock(QGroupBox):
	def __init__(self, title, parent=None):
		super(editBlock, self).__init__(parent)
		self.edit = QLineEdit()
		self.setTitle(title)

		layout = QHBoxLayout() 
		layout.addWidget(self.edit)     
		self.setLayout(layout)


class comboBlock(QGroupBox):
	def __init__(self, title, comboList, parent=None):
		super(comboBlock, self).__init__(parent)
		self.comboList = comboList
		self.combo = QComboBox()
		self.combo.addItems(comboList)
		self.setTitle(title)

		layout = QHBoxLayout() 
		layout.addWidget(self.combo)     
		self.setLayout(layout)


class outputPlot(QWidget):
	def __init__(self, parent=None):
		super(outputPlot, self).__init__(parent)
		self.figure = Figure(figsize=(6,3))
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)
		plt.rcParams.update({'font.size': PLOT_FONTSIZE})

		layout = QGridLayout()
		layout.addWidget(self.canvas,0,0,1,2)
		layout.addWidget(self.toolbar,1,0,1,1)
		#layout.addWidget(self.button)
		self.setLayout(layout)
		self.ax = self.figure.add_subplot(111)


class outputPlotSize(QWidget):
	def __init__(self, fontsize, parent=None):
		super(outputPlotSize, self).__init__(parent)
		self.figure = Figure(figsize=(6,3))
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)
		plt.rcParams.update({'font.size': fontsize})

		layout = QGridLayout()
		layout.addWidget(self.canvas,0,0,1,2)
		layout.addWidget(self.toolbar,1,0,1,1)
		#layout.addWidget(self.button)
		self.setLayout(layout)
		self.ax = self.figure.add_subplot(111)


class output2Plot(QWidget):
	def __init__(self, parent=None):
		super(output2Plot, self).__init__(parent)
		self.figure = Figure(figsize=(3,6))
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)
		plt.rcParams.update({'font.size': PLOT_FONTSIZE})

		layout = QGridLayout()
		layout.addWidget(self.canvas,0,0,1,2)
		layout.addWidget(self.toolbar,1,0,1,1)
		#layout.addWidget(self.button)
		self.setLayout(layout)
		self.ax1 = self.figure.add_subplot(211)
		self.ax2 = self.figure.add_subplot(212)


class output2HPlot(QWidget):
	def __init__(self, parent=None):
		super(output2HPlot, self).__init__(parent)
		self.figure = Figure(figsize=(6,3))
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)
		plt.rcParams.update({'font.size': PLOT_FONTSIZE})

		layout = QGridLayout()
		layout.addWidget(self.canvas,0,0,1,2)
		layout.addWidget(self.toolbar,1,0,1,1)
		#layout.addWidget(self.button)
		self.setLayout(layout)
		self.ax1 = self.figure.add_subplot(121)
		self.ax2 = self.figure.add_subplot(122)


class output4Plot(QWidget):
	def __init__(self, parent=None):
		super(output4Plot, self).__init__(parent)
		self.figure = Figure(figsize=(6,3))
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)
		plt.rcParams.update({'font.size': PLOT_FONTSIZE})

		layout = QGridLayout()
		layout.addWidget(self.canvas,0,0,1,2)
		layout.addWidget(self.toolbar,1,0,1,1)
		#layout.addWidget(self.button)
		self.setLayout(layout)
		self.ax1 = self.figure.add_subplot(221)
		self.ax2 = self.figure.add_subplot(222)
		self.ax3 = self.figure.add_subplot(223)
		self.ax4 = self.figure.add_subplot(224)


class output3Plot(QWidget):
	def __init__(self, parent=None):
		super(output3Plot, self).__init__(parent)
		self.figure = Figure(figsize=(6,3))
		self.canvas = FigureCanvas(self.figure)
		self.toolbar = NavigationToolbar(self.canvas, self)
		plt.rcParams.update({'font.size': PLOT_FONTSIZE_S})

		layout = QGridLayout()
		layout.addWidget(self.canvas,0,0,1,2)
		layout.addWidget(self.toolbar,1,0,1,1)
		#layout.addWidget(self.button)
		self.setLayout(layout)
		self.ax1 = self.figure.add_subplot(311)
		self.ax2 = self.figure.add_subplot(312)
		self.ax3 = self.figure.add_subplot(313)


class connectBlock():
	def __init__(self, name):
		self.groupBox = QGroupBox(name)
		self.status = QLabel()
		self.btn = QPushButton("Connect")
		self.status.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		self.SetConnectText(Qt.red, "update comport first !", True)

	def layout1(self):   
		layout = QVBoxLayout()
		layout.addWidget(self.btn)
		layout.addWidget(self.status)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox

	def SetConnectText(self, color, text, flag):
		pe = QPalette()
		pe.setColor(QPalette.WindowText, color)
		self.status.setPalette(pe)
		self.status.setText(text)
		self.status.show()
		self.btn.setEnabled(flag)

	def layout2(self):   
		layout = QHBoxLayout()
		layout.addWidget(self.btn)
		layout.addWidget(self.status)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox

class IPconnectBlock():
	def __init__(self, name):
		self.groupBox = QGroupBox(name)
		self.IP = QLineEdit()
		self.status = QLabel()
		self.status.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		self.btn = QPushButton("Connect")
		self.SetConnectText(Qt.red, "Connect first !", True)

	def layout1(self):   
		layout = QVBoxLayout()
		layout.addWidget(self.IP)
		layout.addWidget(self.btn)
		layout.addWidget(self.status)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox

	def SetConnectText(self, color, text, flag):
		pe = QPalette()
		pe.setColor(QPalette.WindowText, color)
		self.status.setPalette(pe)
		self.status.setText(text)
		self.status.show()
		self.btn.setEnabled(flag)

	def layout2(self):   
		layout = QGridLayout()
		layout.addWidget(self.IP, 0, 0, 1, 1)
		layout.addWidget(self.btn, 0, 1, 1, 1)
		layout.addWidget(self.status, 1, 0, 1, 2)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox

