from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys

sys.path.append("../")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.pgplot = PlotWidget()
        self.setCentralWidget(self.pgplot)
        self.pgplot.setBackground("k")
        pen = pg.mkPen(color=(255, 0, 0), width=6, style=QtCore.Qt.SolidLine)

        self.pgplot.plot([1, 2, 3, 4, 5], pen=pen, symbol="+", symbolSize=30, symbolBrush="w")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
