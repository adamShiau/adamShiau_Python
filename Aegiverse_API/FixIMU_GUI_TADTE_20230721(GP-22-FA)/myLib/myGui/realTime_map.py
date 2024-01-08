""" ####### log stuff creation, always on the top ########  """
import builtins
import logging
from datetime import datetime

import numpy as np
from PyQt5.QtWidgets import QApplication

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import gc
import os
import sys

from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QThread
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QPushButton, QLabel, QSlider, QLineEdit, QSpacerItem, \
    QSizePolicy, QApplication, QVBoxLayout


class realTime_MapUI(QWidget):
    iscloase_qt = pyqtSignal(bool)

    def __init__(self):
        super(realTime_MapUI, self).__init__()
        self.initUI()
        self.linkControl()
        self.mapWidget()
        self.stopTrackFuncVal = False
        self.TargetMarkerPosition = None
        self.setWindowTitle("即時軌跡")

    def closeEvent(self, *args, **kwargs):  # 當關閉視窗時，會被執行的函式
        #self.cancelMap()
        #self.RestartRealTrack()
        self.iscloase_qt.emit(True)

    def initUI(self):
        self.currentMapWidget = QWidget()
        self.currentMapWidget.resize(500, 600)
        self.currentMapWidget.setStyleSheet("background-color: white;")
        currentMapLayout = QHBoxLayout()
        self.currentMapView = QWidget()
        self.currentMapView.resize(400, 600)

        controlButtonLayout = QGridLayout()
        self.startTrack = QPushButton()
        self.startTrack.setText("Start Real-Time Tracking")
        self.startTrack.setFixedSize(220, 30)
        self.startTrack.setStyleSheet("background-color: black;\
                            color: white; border-radius: 5px; border-width: 2px; border-color: blue; border-style: solid;")
        self.stopTrack = QPushButton()
        self.stopTrack.setText("Stop Real-Time Tracking")
        self.stopTrack.setFixedSize(220, 30)
        self.stopTrack.setStyleSheet("background-color: black;\
                            color: white; border-radius: 5px;  border-width: 2px; border-color: blue; border-style: solid;")
        self.startUpAutoTracking = QPushButton()
        self.startUpAutoTracking.setText("Start Up Follow The Track Trail")
        self.startUpAutoTracking.setFixedSize(220, 30)
        self.startUpAutoTracking.setStyleSheet("background-color: black;\
                            color: white; border-radius: 5px;  border-width: 2px; border-color: blue; border-style: solid;")
        self.stopAutoTracking = QPushButton()
        self.stopAutoTracking.setText("Stop Follow The Track Trail")
        self.stopAutoTracking.setFixedSize(220, 30)
        self.stopAutoTracking.setStyleSheet("background-color: black;\
                            color: white; border-radius: 5px;  border-width: 2px; border-color: blue; border-style: solid;")

        self.SliderLabel = QLabel("軌跡點的速度調整： 50 km/hr")
        self.SliderLabel.setFont(QFont('Arial', 14))
        self.Slider = QSlider(Qt.Horizontal)
        self.Slider.setMinimum(0)
        self.Slider.setMaximum(100)
        self.Slider.setValue(50)

        SetLonLabel = QLabel("設定起始經度值：")
        SetLonLabel.setFont(QFont('Arial', 14))

        self.SetLonEdit = QLineEdit()
        self.SetLonEdit.setText("120.448338")
        self.SetLonEdit.setFont(QFont('Arial', 14))

        SetLatLabel = QLabel("設定起始緯度值：")
        SetLatLabel.setFont(QFont('Arial', 14))

        self.SetLatEdit = QLineEdit()
        self.SetLatEdit.setText("22.428453")
        self.SetLatEdit.setFont(QFont('Arial', 14))

        SetTargetLonLabel = QLabel("設定目標起始經度值：")
        SetTargetLonLabel.setFont(QFont('Arial', 14))

        self.SetTargetLonEdit = QLineEdit()
        self.SetTargetLonEdit.setText("120.308431")
        self.SetTargetLonEdit.setFont(QFont('Arial', 14))

        SetTargetLatLabel = QLabel("設定目標起始緯度值：")
        SetTargetLatLabel.setFont(QFont('Arial', 14))

        self.SetTargetLatEdit = QLineEdit()
        self.SetTargetLatEdit.setText("22.363809")
        self.SetTargetLatEdit.setFont(QFont('Arial', 14))
        self.InitValToTarget_Distance = QLabel("距離偏移訊號：")
        self.InitValToTarget_Distance.setFont(QFont('Arial', 14))
        self.InitValToTarget_Angle = QLabel("姿態偏移訊號：")
        self.InitValToTarget_Angle.setFont(QFont('Arial', 14))

        RealTimeButtonSpacer = QSpacerItem(100, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        controlButtonLayout.addWidget(self.startUpAutoTracking, 0, 0, 1, 1)
        controlButtonLayout.addWidget(self.stopAutoTracking, 1, 0, 1, 1)
        controlButtonLayout.addWidget(self.SliderLabel, 2, 0, 1, 1)
        controlButtonLayout.addWidget(self.Slider, 3, 0, 1, 1)
        ## controlButtonLayout.addWidget(SetLonLabel, 4, 0, 1, 1)
        ## controlButtonLayout.addWidget(self.SetLonEdit, 5, 0, 1, 1)
        # controlButtonLayout.addWidget(SetLatLabel, 6, 0, 1, 1)
        # controlButtonLayout.addWidget(self.SetLatEdit, 7, 0, 1, 1)
        # controlButtonLayout.addWidget(SetTargetLonLabel, 8, 0, 1, 1)
        # controlButtonLayout.addWidget(self.SetTargetLonEdit, 9, 0, 1 ,1)
        # controlButtonLayout.addWidget(SetTargetLatLabel, 10, 0, 1, 1)
        # controlButtonLayout.addWidget(self.SetTargetLatEdit, 11, 0, 1, 1)
        # controlButtonLayout.addWidget(self.InitValToTarget_Distance, 12, 0, 1, 1)
        # controlButtonLayout.addWidget(self.InitValToTarget_Angle, 13, 0, 1, 1)
        ### controlButtonLayout.addWidget(self.SliderVal, 4, 0, 1, 1)
        controlButtonLayout.addItem(RealTimeButtonSpacer, 14, 0, 5, 1)

        currentMapLayout.addWidget(self.currentMapView)
        currentMapLayout.addLayout(controlButtonLayout)
        self.currentMapWidget.setLayout(currentMapLayout)

        # 設定layout的大小
        currentMapLayout.setStretchFactor(self.currentMapView, 9)
        currentMapLayout.setStretchFactor(controlButtonLayout, 1)

        self.setLayout(currentMapLayout)

    def linkControl(self):
        self.stopAutoTracking.clicked.connect(self.stopTrackingControl)
        self.startUpAutoTracking.clicked.connect(self.startTrackingControl)


    def mapWidget(self):
    # 即時軌跡
        self.__current_view = QWebEngineView()
        # __current_map_Url = "./FixIMU_GUI_TADTE_20230721(GP-22-FA)/map_control.html"
        __current_map_Url = "./map_control.html"
        dir_Path = os.getcwd()
        # DirPath = os.path.dirname(os.getcwd())
        # DirPath2 = os.path.dirname(DirPath)
        # DirPath3 = os.path.dirname(DirPath2)
        absolutePath = os.path.join(dir_Path, __current_map_Url)   # 絕對位置
        # print(os.getcwd())
        # print(DirPath)
        # print(DirPath2)
        # print(DirPath3)

        settings = self.__current_view.settings()
        if hasattr(QWebEngineSettings, 'hardwareAccelerationEnabled'):
            settings.setAttribute(QWebEngineSettings.hardwareAccelerationEnabled, True)

        self.__current_view.setUrl(QUrl.fromLocalFile(absolutePath))

        realTimelayout = QVBoxLayout()
        realTimelayout.addWidget(self.__current_view)
        self.currentMapView.setLayout(realTimelayout)

    def RealDrawPath(self, point:object, mapAng: list, vbpoint: object):
        # 即時的定位位置
        self.__linepoint = point[-1]
        self.__vbox_linePoint = vbpoint[-1]
        self.InitAngle = 0
        for ang_val in mapAng:
            # js_script = f"newMarker.setLatLng({currentPoint}).update(); newMarker.setRotationAngle({mapAng}); poly_line_eaa3f4370a010685549681d73513088b.setLatLngs({point});"
            js_script = f"newMarker.setRotationAngle({ang_val});"
            self.__current_view.page().runJavaScript(js_script)
            self.InitAngle = ang_val

        # js_script = f"newMarker.setLatLng({self.__linepoint}).update(); poly_line_eaa3f4370a010685549681d73513088b.setLatLngs({point});"
        js_script = f"newMarker.setLatLng({self.__linepoint}).update();poly_line_eaa3f4370a010685549681d73513088b.setLatLngs({point});"
        self.__current_view.page().runJavaScript(js_script)
        if self.stopTrackFuncVal == False:
            jscmd = f"map_fcdcbcbcd8da196bbce0ca58bb6d3f39.setView({self.__linepoint});"
            self.__current_view.page().runJavaScript(jscmd)

            QApplication.processEvents()

        vbox_js = f"ployLine_for_vboxPointLine.setLatLngs({vbpoint});vboxMarker.setLatLng({self.__vbox_linePoint}).update();"
        self.__current_view.page().runJavaScript(vbox_js)

        # self.updateInitTargetLine()
        # self.CalDistance()
        # self.CalAngle()


    # 取消即時軌跡功能(顯示的軌跡資訊與自動追蹤功能)
    def CleanRealTrack(self):
        js_cmd = f"newMarker.setOpacity(0); poly_line_eaa3f4370a010685549681d73513088b.setLatLngs([]);"
        self.__current_view.page().runJavaScript(js_cmd)

    def Restartnewmarker(self):
        js_cmd = f"newMarker.setLatLng([22.428453, 120.448338]); poly_line_eaa3f4370a010685549681d73513088b.setLatLngs([]); vboxMarker.setLatLng([22.363809, 120.308431]);ployLine_for_vboxPointLine.setLatLngs([]);"
        self.__current_view.page().runJavaScript(js_cmd)
        jscmd = f"map_fcdcbcbcd8da196bbce0ca58bb6d3f39.setView([22.428453, 120.448338]);"
        self.__current_view.page().runJavaScript(jscmd)

    def RestartRealTrack(self):
        js_cmd = f"poly_line_initVal_TargetVal.setLatLngs([]);"
        self.__current_view.page().runJavaScript(js_cmd)
        self.SetLatEdit.setText("22.428453")
        self.SetLonEdit.setText("120.448338")
        self.SetTargetLatEdit.setText("22.363809")
        self.SetTargetLonEdit.setText("120.308431")
        self.InitValToTarget_Distance.setText("距離偏移訊號：")
        self.InitValToTarget_Angle.setText("姿態偏移訊號：")
        js_cmd_tar = f"targetMarker.setLatLng([22.363809, 120.308431]).update();"
        self.__current_view.page().runJavaScript(js_cmd_tar)
        self.Slider.setValue(50)

    # def SetTargetMarkerMap(self, lat, lon):
    #     self.TargetMarkerPosition = [lat, lon]
    #     JScmd = f"targetMarker.setOpacity(1);"
    #     self.__current_view.page().runJavaScript(JScmd)
    #     js_cmd = f"targetMarker.setLatLng({self.TargetMarkerPosition}).update();"
    #     self.__current_view.page().runJavaScript(js_cmd)

    def initTargetMarkerMap(self):
        js_cmd = 'targetMarker.setStyle({fillOpacity: 0});'
        self.__current_view.page().runJavaScript(js_cmd)

    def updateInitTargetLine(self):
        if self.TargetMarkerPosition != None:
            linePosition = [self.linepoint, self.TargetMarkerPosition]
            js_cmd = f"poly_line_initVal_TargetVal.setLatLngs([{linePosition}]);"
            self.__current_view.page().runJavaScript(js_cmd)

    def CalDistance(self):
        distance = (np.deg2rad(self.linepoint[0] - self.TargetMarkerPosition[0]) ** 2 + np.deg2rad(self.linepoint[1] - self.TargetMarkerPosition[1]) ** 2) ** 0.5 * 6371 * 1000
        lb = "距離偏移訊號： %.1f m" % distance
        self.InitValToTarget_Distance.setText(lb)

    def CalAngle(self):
        target_ang = -np.rad2deg(np.arctan2((self.TargetMarkerPosition[1] - self.linepoint[1]), (self.TargetMarkerPosition[0] - self.linepoint[0])))
        diff = self.InitAngle + target_ang
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        #print(diff)
        #print(self.InitAngle, target_ang)

        lb = "姿態偏移訊號： %.1f°" % diff
        self.InitValToTarget_Angle.setText(lb)

    def cancelMap(self):
        try:
            self.__current_view.deleteLater()
            #self.__current_view.close()
            self.__current_view = None
            gc.collect()
        except AttributeError:
            print("已經刪除了")

    def stopTrackingControl(self):
        self.stopTrackFuncVal = True

    def startTrackingControl(self):
        self.stopTrackFuncVal = False



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = realTime_MapUI()
    window.show()
    app.exec_()