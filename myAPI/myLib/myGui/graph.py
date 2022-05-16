import matplotlib

matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget, plot
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class mplGraph_1(QWidget):
    def __init__(self, parent=None, width=10, height=10, dpi=100):
        super(mplGraph_1, self).__init__(parent)
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        canvas = FigureCanvas(self.fig)
        toolbar = NavigationToolbar(canvas=canvas, parent=self)
        self.ax = self.fig.add_subplot(111)
        layout = QGridLayout()
        layout.addWidget(canvas, 0, 0, 2, 2)
        layout.addWidget(toolbar, 2, 0, 1, 1)
        self.setLayout(layout)


class mplGraph_2(QWidget):
    def __init__(self, width=10, height=10, dpi=100):
        super(mplGraph_2, self).__init__()
        fig = Figure(figsize=(width, height), dpi=dpi)
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas=canvas, parent=None)
        self.ax1 = fig.add_subplot(121)
        self.ax2 = fig.add_subplot(122)
        layout = QGridLayout()
        layout.addWidget(canvas, 0, 0, 2, 2)
        layout.addWidget(toolbar, 2, 0, 1, 1)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication([])
    fig2 = mplGraph_2()
    fig2.ax1.plot([1, 2, 3])
    fig2.ax2.plot([1, 2, 5])
    fig2.show()
    app.exec_()
