from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import (QGraphicsView,QGraphicsScene,QApplication)

PLOT_FONTSIZE = 14
PLOT_FONTSIZE_S = 10
GAUGE_LINE_X1 = 40
GAUGE_LINE_Y1 = 160
GAUGE_LINE_X2 = 101
GAUGE_LINE_Y2 = 101

class btn(QWidget):
	def __init__(self, name='name', parent=None):
		super(btn, self).__init__(parent)
		self.bt = QPushButton(name)
		layout = QGridLayout()
		layout.addWidget(self.bt, 0,0,1,1)
		self.setLayout(layout)

class displayOneBlock(QGroupBox):
	def __init__(self, name='name', parent=None):
		super(displayOneBlock, self).__init__(parent)
		self.setTitle(name)
		self.setFont(QFont('',10)) 
		pe = QPalette()
		pe.setColor(QPalette.WindowText,Qt.yellow)
		pe.setColor(QPalette.Window,Qt.black)
		self.lb = QLabel();
		self.lb.setPalette(pe)
		self.lb.setFont(QFont('Arial', 20)) 
		self.lb.setAutoFillBackground(True)
		self.lb.setText('buffer')
		
		layout = QVBoxLayout()
		layout.addWidget(self.lb)
		self.setLayout(layout)
		
class displayTwoBlock(QGroupBox):
	def __init__(self, title='title', name1='name1', name2='name2', parent=None):
		super(displayTwoBlock, self).__init__(parent)
		# self.groupBox = QGroupBox(title)
		self.setTitle(title)
		self.setFont(QFont('',20)) 
		pe = QPalette()
		pe.setColor(QPalette.WindowText,Qt.yellow)
		pe.setColor(QPalette.Window,Qt.black)
		self.lb1 = QLabel();
		self.lb1.setPalette(pe)
		self.lb1.setFont(QFont('Arial', 30)) 
		self.lb1.setAutoFillBackground(True)
		self.lb1.setText('label1')
		self.lb1name = QLabel();
		self.lb1name.setText(name1)
		
		self.lb2 = QLabel(name2);
		self.lb2.setPalette(pe)
		self.lb2.setFont(QFont('Arial', 30)) 
		self.lb2.setAutoFillBackground(True)
		self.lb2.setText('lab1l2')
		self.lb2name = QLabel();
		self.lb2name.setText(name2)
		
		layout = QGridLayout()
		layout.addWidget(self.lb1name, 0, 0, 1, 1)
		layout.addWidget(self.lb1, 1, 0, 3, 5)
		layout.addWidget(self.lb2name, 4, 0, 1, 1)
		layout.addWidget(self.lb2, 5, 0, 3, 5)
		self.setLayout(layout)
		
class displaySixBlock(QGroupBox):
	def __init__(self, groupName='groupName', title1='title1', name1_1='name1_1', name1_2='name1_2',
											  title2='title2', name2_1='name2_1', name2_2='name2_2', 
											  title3='title3', name3_1='name3_1', name3_2='name3_2', parent=None):
		super(displaySixBlock, self).__init__(parent)
		self.setTitle(groupName)
		self.setFont(QFont('',20)) 
		pe = QPalette()
		pe.setColor(QPalette.WindowText,Qt.yellow)
		pe.setColor(QPalette.Window,Qt.black)
		
		self.lb1_title = QLabel();
		self.lb1_title.setText(title1)
		self.lb1_1 = QLabel();
		self.lb1_1.setPalette(pe)
		self.lb1_1.setFont(QFont('Arial', 30)) 
		self.lb1_1.setAutoFillBackground(True)
		self.lb1_1.setText('label1_1')
		self.lb1_1name = QLabel();
		self.lb1_1name.setText(name1_1)		
		self.lb1_2 = QLabel();
		self.lb1_2.setPalette(pe)
		self.lb1_2.setFont(QFont('Arial', 30)) 
		self.lb1_2.setAutoFillBackground(True)
		self.lb1_2.setText('label1_2')
		self.lb1_2name = QLabel();
		self.lb1_2name.setText(name1_2)
		
		self.lb2_title = QLabel();
		self.lb2_title.setText(title2)
		self.lb2_1 = QLabel();
		self.lb2_1.setPalette(pe)
		self.lb2_1.setFont(QFont('Arial', 30)) 
		self.lb2_1.setAutoFillBackground(True)
		self.lb2_1.setText('label2_1')
		self.lb2_1name = QLabel();
		self.lb2_1name.setText(name2_1)		
		self.lb2_2 = QLabel();
		self.lb2_2.setPalette(pe)
		self.lb2_2.setFont(QFont('Arial', 30)) 
		self.lb2_2.setAutoFillBackground(True)
		self.lb2_2.setText('label2_2')
		self.lb2_2name = QLabel();
		self.lb2_2name.setText(name2_2)
		
		self.lb3_title = QLabel();
		self.lb3_title.setText(title3)
		self.lb3_1 = QLabel();
		self.lb3_1.setPalette(pe)
		self.lb3_1.setFont(QFont('Arial', 30)) 
		self.lb3_1.setAutoFillBackground(True)
		self.lb3_1.setText('label3_1')
		self.lb3_1name = QLabel();
		self.lb3_1name.setText(name3_1)		
		self.lb3_2 = QLabel();
		self.lb3_2.setPalette(pe)
		self.lb3_2.setFont(QFont('Arial', 30)) 
		self.lb3_2.setAutoFillBackground(True)
		self.lb3_2.setText('label3_2')
		self.lb3_2name = QLabel();
		self.lb3_2name.setText(name3_2)
		
		# layout1 = QGridLayout()
		# layout1.addWidget(self.lb1_title, 2, 0, 1, 1)
		# layout1.addWidget(self.lb1_1name, 1, 1, 1, 2)
		# layout1.addWidget(self.lb1_1, 2, 1, 2, 2)
		# layout1.addWidget(self.lb1_2name, 1, 3, 1, 1)
		# layout1.addWidget(self.lb1_2, 2, 3, 2, 2)
		# layout1.setRowStretch(1, 1)
		# layout1.setRowStretch(2, 5)
		# layout1.setRowStretch(3, 5) 
		# layout1.setColumnStretch(0, 2)
		# layout1.setColumnStretch(1, 5)
		# layout1.setColumnStretch(2, 5)
		# layout1.setColumnStretch(3, 5)
		# layout1.setColumnStretch(4, 5)
		
		# layout2 = QGridLayout()
		# layout2.addWidget(self.lb2_title, 2, 0, 1, 1)
		# layout2.addWidget(self.lb2_1name, 1, 1, 1, 2)
		# layout2.addWidget(self.lb2_1, 2, 1, 2, 2)
		# layout2.addWidget(self.lb2_2name, 1, 3, 1, 1)
		# layout2.addWidget(self.lb2_2, 2, 3, 2, 2)
		# layout2.setRowStretch(1, 1)
		# layout2.setRowStretch(2, 5)
		# layout2.setRowStretch(3, 5) 
		# layout2.setColumnStretch(0, 2)
		# layout2.setColumnStretch(1, 5)
		# layout2.setColumnStretch(2, 5)
		# layout2.setColumnStretch(3, 5)
		# layout2.setColumnStretch(4, 5)
		
		# layout3 = QGridLayout()
		# layout3.addWidget(self.lb3_title, 2, 0, 1, 1)
		# layout3.addWidget(self.lb3_1name, 1, 1, 1, 2)
		# layout3.addWidget(self.lb3_1, 2, 1, 2, 2)
		# layout3.addWidget(self.lb3_2name, 1, 3, 1, 1)
		# layout3.addWidget(self.lb3_2, 2, 3, 2, 2)
		# layout3.setRowStretch(1, 1)
		# layout3.setRowStretch(2, 5)
		# layout3.setRowStretch(3, 5) 
		# layout3.setColumnStretch(0, 2)
		# layout3.setColumnStretch(1, 5)
		# layout3.setColumnStretch(2, 5)
		# layout3.setColumnStretch(3, 5)
		# layout3.setColumnStretch(4, 5)
		
		# layout = QVBoxLayout()
		layout = QGridLayout()
		layout.addWidget(self.lb1_title, 2, 0, 2, 1)
		layout.addWidget(self.lb1_1name, 1, 2, 1, 2)
		layout.addWidget(self.lb1_1, 2, 1, 2, 4)
		layout.addWidget(self.lb1_2name, 1, 8, 1, 2)
		layout.addWidget(self.lb1_2, 2, 7, 2, 4)
		
		layout.addWidget(self.lb2_title, 7, 0, 2, 1)
		layout.addWidget(self.lb2_1name, 6, 2, 1, 2)
		layout.addWidget(self.lb2_1, 7, 1, 2, 4)
		layout.addWidget(self.lb2_2name, 6, 8, 1, 2)
		layout.addWidget(self.lb2_2, 7, 7, 2, 4)
		
		layout.addWidget(self.lb3_title, 12, 0, 2, 1)
		layout.addWidget(self.lb3_1name, 11, 2, 1, 2)
		layout.addWidget(self.lb3_1, 12, 1, 2, 4)
		layout.addWidget(self.lb3_2name, 11, 8, 1, 2)
		layout.addWidget(self.lb3_2, 12, 7, 2, 4)
		# layout.addLayout(layout1)
		# layout.addLayout(layout2)
		# layout.addLayout(layout3)
		self.setLayout(layout)

class gaugePlot(QGraphicsView):
	def __init__(self, parent=None):
		super(gaugePlot, self).__init__(parent)
		pen = QPen(Qt.red)
		pen.setWidth(3) #改變指針寬度
		pen.setCapStyle(Qt.RoundCap)   #指針末端的形狀, Qt.RoundCap, Qt.SquareCap, Qt.RoundCap
		scene = QGraphicsScene() #https://my.oschina.net/golang/blog/209554
								#https://www.itread01.com/content/1548416194.html

		pen.setCosmetic(True)  
		scene.addPixmap(QPixmap('DPS_guage.png'))
		self.item = scene.addLine(GAUGE_LINE_X1, GAUGE_LINE_Y1, GAUGE_LINE_X2, GAUGE_LINE_Y2, pen) 
		pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.gray))
		brush = QtGui.QBrush(pen.color().darker(100))
		scene.addEllipse(87, 87, 20, 20, pen, brush)
		self.item.setTransformOriginPoint(GAUGE_LINE_X2, GAUGE_LINE_Y2)
		self.setScene(scene)
		
class gaugePlotwLabel(QGraphicsView):
	def __init__(self, text='', title='123',  parent=None):
		super(gaugePlotwLabel, self).__init__(parent)
		
		pe = QPalette()
		pe.setColor(QPalette.WindowText,Qt.yellow)
		pe.setColor(QPalette.Window,Qt.black)
		self.lb = QLabel();
		self.lb.setPalette(pe)
		self.lb.setFont(QFont('Arial', 10)) 
		self.lb.setAutoFillBackground(True)
		self.lb.setText(text)
		
		self.title = QLabel();
		self.title.setText(title)
		
		self.gauge = gaugePlot()
		layout = QGridLayout()
		
		layout.addWidget(self.gauge, 0, 0, 40, 40)
		layout.addWidget(self.lb, 22, 19, 1, 1)
		layout.addWidget(self.title, 2, 19, 1, 1)
		self.setLayout(layout)
		
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
		
class spinBlockOneLabel(QGroupBox):
	def __init__(self, title, minValue, maxValue, double = False, step = 1, Decimals = 2, parent=None):
		super(spinBlockOneLabel, self).__init__(parent)
		if (double):
			self.spin = QDoubleSpinBox()
			self.spin.setDecimals(Decimals)
		else:
			self.spin = QSpinBox()

		self.spin.setRange(minValue, maxValue)
		self.spin.setSingleStep(step)
		self.lb = QLabel('freq')
		self.setTitle(title)

		layout = QHBoxLayout() 
		layout.addWidget(self.spin)    
		layout.addWidget(self.lb)  		
		self.setLayout(layout)
	
class chkBoxBlock_1(QWidget):
	def __init__(self, title='', name='', parent=None):
		super(chkBoxBlock_1, self).__init__(parent)
		self.groupBox = QGroupBox(title)
		self.cb = QCheckBox(name)
		
	def layout(self):
		layout = QVBoxLayout()
		layout.addWidget(self.cb)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox
	
class chkBoxBlock_2(QWidget):
	def __init__(self, title='', name1='', name2='', parent=None):
		super(chkBoxBlock_2, self).__init__(parent)
		self.groupBox = QGroupBox(title)
		self.cb1 = QCheckBox(title+'_'+name1)
		self.cb2 = QCheckBox(title+'_'+name2)
		
	def layout(self):
		layout = QVBoxLayout()
		layout.addWidget(self.cb1)
		layout.addWidget(self.cb2)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox
		
class chkBoxBlock_3(QWidget):
	def __init__(self, title='', name1='', name2='', name3='', parent=None):
		super(chkBoxBlock_3, self).__init__(parent)
		self.groupBox = QGroupBox(title)
		self.cb1 = QCheckBox(title+'_'+name1)
		self.cb2 = QCheckBox(title+'_'+name2)
		self.cb3 = QCheckBox(title+'_'+name3)
	def layout(self):
		layout = QVBoxLayout()
		layout.addWidget(self.cb1)
		layout.addWidget(self.cb2)
		layout.addWidget(self.cb3)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox
		
class chkBoxBlock_4(QWidget):
	def __init__(self, title='', name1='', name2='', name3='', name4='', parent=None):
		super(chkBoxBlock_4, self).__init__(parent)
		self.groupBox = QGroupBox(title)
		self.cb1 = QCheckBox(title+'_'+name1)
		self.cb2 = QCheckBox(title+'_'+name2)
		self.cb3 = QCheckBox(title+'_'+name3)
		self.cb4 = QCheckBox(title+'_'+name4)
	def layout(self):
		layout = QVBoxLayout()
		layout.addWidget(self.cb1)
		layout.addWidget(self.cb2)
		layout.addWidget(self.cb3)
		layout.addWidget(self.cb4)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox
		
class chkBoxBlock(QWidget):
	def __init__(self, name1='', name2='', name3='', name4='', name5='', name6='', parent=None):
		super(chkBoxBlock, self).__init__(parent)
		self.groupBox = QGroupBox('show graph')
		self.ax_cb = QCheckBox(name1)
		self.ay_cb = QCheckBox(name2)
		self.wz_cb = QCheckBox(name3)
		self.wz200_cb = QCheckBox('wz200')
		self.vx_cb = QCheckBox(name4)
		self.vy_cb = QCheckBox(name5)
		self.v_cb = QCheckBox('v')
		self.x_cb = QCheckBox('x')
		self.y_cb = QCheckBox('y')
		self.track_cb = QCheckBox('track')
		
		self.thetaz_cb = QCheckBox(name6)
		self.thetaz200_cb = QCheckBox(name6+'200')
		
	def layout(self):
		layout = QGridLayout()
		layout.addWidget(self.ax_cb, 0,0)
		layout.addWidget(self.ay_cb, 0,1)
		layout.addWidget(self.wz_cb, 0,2)
		# layout.addWidget(self.x_cb, 0,3)
		# layout.addWidget(self.y_cb, 0,4)
		# layout.addWidget(self.vx_cb, 1,0)
		# layout.addWidget(self.vy_cb, 1,1)
		layout.addWidget(self.v_cb, 1,0)
		layout.addWidget(self.thetaz_cb, 1,2)
		layout.addWidget(self.thetaz200_cb, 1,1)
		layout.addWidget(self.wz200_cb, 0,3)
		layout.addWidget(self.track_cb, 1,3)
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

class labelBlock(QWidget):
	def __init__(self, title='title', parent=None):
		super(labelBlock, self).__init__(parent)
		self.title = QLabel(title)
		self.val = QLabel()
		
		layout = QVBoxLayout()
		layout.addWidget(self.title)
		layout.addWidget(self.val)
		self.setLayout(layout)

class editBlock(QGroupBox):
	def __init__(self, title, parent=None):
		super(editBlock, self).__init__(parent)
		self.edit = QLineEdit()
		self.setTitle(title)

		layout = QHBoxLayout() 
		layout.addWidget(self.edit)     
		self.setLayout(layout)
		
class editBlockwBtn(QGroupBox):
	def __init__(self, title='', val='10', parent=None):
		super(editBlockwBtn, self).__init__(parent)
		self.setTitle(title)
		self.bt = QPushButton('set')
		self.le = QLineEdit(val)

		layout = QGridLayout() 
		layout.addWidget(self.bt, 0, 0, 1, 1)  
		layout.addWidget(self.le, 1, 0, 2, 2)  		
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
	def __init__(self, fontsize, title='', parent=None):
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
		self.ax.set_title(title)


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

class usbConnect():
	def __init__(self, btn_name="COM update", group_name='Connect COM port'):
		self.groupBox = QGroupBox(group_name)
		self.bt_update = QPushButton(btn_name)
		self.bt_connect = QPushButton('connect')
		self.cs = QComboBox()
		self.lb = QLabel(" ")
		self.lb_com = QLabel(" ")
			
		
	def layoutG(self):
		layout = QGridLayout()
		layout.addWidget(self.bt_update, 0,0,1,1)
		layout.addWidget(self.cs, 0,1,1,1)
		layout.addWidget(self.bt_connect, 0,2,1,1)
		layout.addWidget(self.lb, 1,0,1,2)
		layout.addWidget(self.lb_com, 1,2,1,1)
		self.groupBox.setLayout(layout)
		self.groupBox.show()
		return self.groupBox
		
	def SetConnectText(self, color, text):
		pe = QPalette()
		pe.setColor(QPalette.WindowText, color)
		self.lb_com.setPalette(pe)
		self.lb_com.setText(text)
		self.lb_com.show()
		# self.btn.setEnabled(flag)

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

