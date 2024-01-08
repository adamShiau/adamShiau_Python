# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
import time

from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """


from PyQt5.QtWidgets import QGroupBox, QTabWidget, QSizePolicy, QTabBar, QVBoxLayout, QWidget, QMainWindow, QGridLayout, \
    QLineEdit, QHBoxLayout, QPushButton, QLabel, QSpacerItem
from myLib.myGui.Draw_3DImg import openGL_Widget_Cube
from myLib.myGui.CircularGauge import *
from myLib.myGui.graph import *



class tabwidget_v1(QMainWindow):
    def __init__(self):
        super(tabwidget_v1, self).__init__()
        self.QTab = QTabWidget()
        self.setCentralWidget(self.QTab)
        self.QTab.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.QTab.setMinimumSize(650, 500)
        self.resetDegree = False
        self.threadStatus = False

        self.remove = False

    def tabwidget_plot(self, tab_title='', plot_object: object = None):
        TabBar_plot = QTabBar()
        TabBar_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        TabBar_plot.setMinimumSize(500, 500)
        TabBar_plot.setLayout(plot_object)
        self.QTab.addTab(TabBar_plot, tab_title)

    def tabwidget_posture(self, tab_title=''):
        TabBar_posture = QTabBar()
        TabBar_posture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        TabBar_posture.setMinimumSize(500, 600)

        self.layout_openGL = QGridLayout()
        self.widget_win = openGL_Widget_Cube()
        #self.widget_win.setMinimumSize(300, 300)

        self.widget_circle = CircularGauge()
        #self.widget_circle.setMinimumSize(200, 350)

        self.plot_cir = pgGraph_circle_1_2(color1="w", color2="r", title="The Impact of Headings on Plane Coordinates Speed 15x")
        #self.plot_cir.setMinimumSize(200, 350)


        self.widget_degree = QWidget()
        self.widget_degree_layout = QVBoxLayout()

        self.set_z_mems_rotationalSpeed = QLineEdit("0.0")
        self.set_z_mems_rotationalSpeed.setDisabled(True)
        self.set_z_mems_rotationalSpeed.setFont(QFont('Arial', 14))
        self.set_z_mems_integralAngle = QLineEdit("0.0")
        self.set_z_mems_integralAngle.setDisabled(True)
        self.set_z_mems_integralAngle.setFont(QFont('Arial', 14))
        self.set_z_FOG_rotationalSpeed = QLineEdit("0.0")
        self.set_z_FOG_rotationalSpeed.setDisabled(True)
        self.set_z_FOG_rotationalSpeed.setFont(QFont('Arial', 14))
        self.set_z_FOG_integralAngle = QLineEdit("0.0")
        self.set_z_FOG_integralAngle.setDisabled(True)
        self.set_z_FOG_integralAngle.setFont(QFont('Arial', 14))
        self.z_la_mems_rotationalSpeed = QLabel("MEMS Z-Axis of Rotational Speed：")
        self.z_la_mems_rotationalSpeed.setFont(QFont('Arial', 14))
        self.z_la_mems_integralAngle = QLabel("Integral Angle of the MEMS Z-Axis：")
        self.z_la_mems_integralAngle.setFont(QFont('Arial', 14))
        self.z_la_FOG_rotationalSpeed = QLabel("FOG Z-Axis of Rotational Speed：")
        self.z_la_FOG_rotationalSpeed.setFont(QFont('Arial', 14))
        self.z_la_FOG_integralAngle = QLabel("Integral Angle of the FOG Z-Axis：")
        self.z_la_FOG_integralAngle.setFont(QFont('Arial', 14))
        self.reset_degree = QPushButton('Resetting The Angle To Zero')
        self.reset_degree.setFont(QFont('Arial', 14))

        SpacerItem_1 = QSpacerItem(120, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        SpacerItem_2 = QSpacerItem(120, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        SpacerItem_3 = QSpacerItem(120, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        SpacerItem_4 = QSpacerItem(120, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        SpacerItem_5 = QSpacerItem(10, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.widget_degree_layout.addWidget(self.z_la_mems_rotationalSpeed)
        self.widget_degree_layout.addWidget(self.set_z_mems_rotationalSpeed)
        self.widget_degree_layout.addItem(SpacerItem_1)
        self.widget_degree_layout.addWidget(self.z_la_mems_integralAngle)
        self.widget_degree_layout.addWidget(self.set_z_mems_integralAngle)
        self.widget_degree_layout.addItem(SpacerItem_2)
        self.widget_degree_layout.addWidget(self.z_la_FOG_rotationalSpeed)
        self.widget_degree_layout.addWidget(self.set_z_FOG_rotationalSpeed)
        self.widget_degree_layout.addItem(SpacerItem_3)
        self.widget_degree_layout.addWidget(self.z_la_FOG_integralAngle)
        self.widget_degree_layout.addWidget(self.set_z_FOG_integralAngle)
        self.widget_degree_layout.addItem(SpacerItem_4)
        self.widget_degree_layout.addWidget(self.reset_degree)
        #self.widget_degree_layout.addItem(SpacerItem_5, 4, 1, 1, 1)


        #self.widget_degree.setMinimumSize(100, 50)
        #self.layout_openGL.addWidget(self.widget_win, 0, 7, 23, 9)  # 0, 0, 20, 11
        self.layout_openGL.addWidget(self.widget_degree, 0, 20, 2, 5)
        self.layout_openGL.addLayout(self.widget_degree_layout, 2, 20, 5, 5)
        #self.layout_openGL.addWidget(self.widget_circle, 0, 7, 13, 7)  # 0, 11, 10, 8
        self.layout_openGL.addWidget(self.plot_cir, 0, 0, 23, 16)  # 10, 11, 10, 8
        TabBar_posture.setLayout(self.layout_openGL)
        self.QTab.addTab(TabBar_posture, tab_title)


    def initUI(self):
        self.threadStatus = True
        drawLayout = QGridLayout()
        self.setLayout(drawLayout)

        self.time_update = QTimer(self)
        self.time_update.timeout.connect(self.updateImg)
        self.time_update.start(10)


    def resetCircle(self):
        self.widget_circle.rotatePointer(0, self.widget_circle.pointer_mems, "M")
        self.widget_circle.rotatePointer(0, self.widget_circle.pointer_fog, "F")

    def updateImg(self):
        # if self.resetDegree:
        #     self.widget_win.resetDraw()
        #     self.resetDegree = False
        #     time.sleep(1)
        #     print("歸零")
        # else:
        self.widget_win.update_GL()
