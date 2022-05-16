import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT



class MyWidget():
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # self.setWindowTitle('hello world')
        # self.setGeometry(50, 50, 200, 150)
        self.window = QWidget()
        self.window.setGeometry(50, 50, 200, 150)

    def show(self):
        self.window.showMaximized()


# class myFIG(FigureCanvasQTAgg):
#     def __init__(self, width=10, height=4, dpi=100):
#         # super(myFIG, self).__init__()
#         self.fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = self.fig.add_subplot(111)
#         # canvas = FigureCanvasQTAgg(self.fig)
#         super(myFIG, self).__init__(self.fig)

class myFIG1(QWidget):
    def __init__(self, width=10, height=4, dpi=100):
        super(myFIG1, self).__init__()
        fig = Figure(figsize=(width, height), dpi=dpi)
        canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar2QT(canvas)
        self.axes = fig.add_subplot(111)

        layout = QGridLayout()
        layout.addWidget(canvas, 0, 0, 2, 2)
        layout.addWidget(toolbar, 2, 0, 1, 2)
        self.setLayout(layout)


class myFIG2(QWidget):
    def __init__(self, width=10, height=4, dpi=100):
        super(myFIG2, self).__init__()
        fig = Figure(figsize=(width, height), dpi=dpi)
        canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar2QT(canvas=canvas, parent=None)
        self.ax1 = fig.add_subplot(121)
        self.ax2 = fig.add_subplot(122)

        layout = QGridLayout()
        layout.addWidget(canvas, 0, 0, 2, 2)
        layout.addWidget(toolbar, 2, 0, 1, 2)
        self.setLayout(layout)


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

    # def show(self):
    #     self.ax.pl
    #     self.fig.show()


if __name__ == '__main__':
    # print(MyWidget.__base__)
    # print(QWidget.__base__)

    app = QApplication([])
    # lb = QLabel("Hello W")
    # lb.show()
    # sc = MplCanvas()
    sc = myFIG2()
    sc.ax1.plot([1, 2, 3])
    sc.ax2.plot([1, 8, 3])
    sc.show()

    app.exec_()

    # figure = myFIG()

    # figure.show()

    # w = MyWidget()
    # w.show()
    # app.exec_()
