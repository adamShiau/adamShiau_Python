import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, \
    QGraphicsEllipseItem, QGraphicsLineItem, QSlider, QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor
import math


class CircularGauge(QWidget):
    def __init__(self):
        super().__init__()
        self.pre_time = None
        self.ang_MEMS = 0
        self.ang_FOG = 0
        self.count = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.circle = QGraphicsEllipseItem(-150, -150, 300, 300)
        pen = QPen(QColor(Qt.black))
        pen.setWidth(5)
        self.circle.setPen(pen)
        self.scene.addItem(self.circle)

        self.pointer_mems = QGraphicsLineItem(0, 0, 0, -140)
        pen = QPen(QColor(Qt.red))
        pen.setWidth(2)
        self.pointer_mems.setPen(pen)
        self.scene.addItem(self.pointer_mems)
        self.label_mems = QGraphicsTextItem("MEMS Z", self.pointer_mems) #角速度
        self.label_mems.setDefaultTextColor(Qt.red)
        self.label_mems.setPos(0, -140)


        self.pointer_fog = QGraphicsLineItem(0, 0, 0, -140)
        pen = QPen(QColor(Qt.blue))
        pen.setWidth(2)
        self.pointer_fog.setPen(pen)
        self.scene.addItem(self.pointer_fog)
        self.label_fog = QGraphicsTextItem("FOG Z", self.pointer_fog)  # 角速度
        self.label_fog.setDefaultTextColor(Qt.blue)
        self.label_fog.setPos(0, -140)

        # self.slider = QSlider(Qt.Horizontal)
        # self.slider.setRange(0, 360)
        # self.slider.valueChanged.connect(self.rotatePointer)
        # layout.addWidget(self.slider)

        layout.addWidget(self.view)
        self.setLayout(layout)

    def input(self, time, w_mems, w_fog):
        if self.count == 300:
            if self.pre_time is not None:
                self.ang_MEMS += w_mems * (time - self.pre_time)
                self.ang_FOG += w_fog * (time - self.pre_time)
            self.pre_time = time

            if self.ang_MEMS > 360:
                self.ang_MEMS -= 360
            elif self.ang_MEMS < 0:
                self.ang_MEMS += 360
            if self.ang_FOG > 360:
                self.ang_FOG -= 360
            elif self.ang_FOG < 0:
                self.ang_FOG += 360
        else:
            self.count += 1



        # self.rotatePointer(self.ang_FOG, self.pointer_fog, "F")
        # self.rotatePointer(self.ang_MEMS, self.pointer_mems, "M")

    #@staticmethod
    def rotatePointer(self,value, pointer, name):
        angle = math.radians(value - 90)
        x = 140 * math.cos(angle)
        y = 140 * math.sin(angle)
        pointer.setLine(0, 0, x, y)

        if name == "M":
            self.label_mems.setPos(x, y)
        elif name == "F":
            self.label_fog.setPos(x, y)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Circular Gauge')
        self.setGeometry(100, 100, 400, 400)

        self.central_widget = CircularGauge()
        self.setCentralWidget(self.central_widget)

        self.central_widget.rotatePointer(20, self.central_widget.pointer_mems)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
