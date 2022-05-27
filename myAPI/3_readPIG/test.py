from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import time
from PyQt5.QtCore import QThread
from threading import Thread

sys.path.append("../")


class test(Thread):
    def __init__(self):
        super(test, self).__init__()
        print("test")
        self.__isRun = False
        print("isRun: ", self.isRun)

    @property
    def isRun(self):
        return self.__isRun

    @isRun.setter
    def isRun(self, flag):
        self.__isRun = flag

    def run(self):
        print("Start Thread")
        while 1:
            if not self.isRun:
                break
            time.sleep(0.1)
            print("I am in run", self.isRun)
        print("Start Thread2")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = test()
    w.show()
    sys.exit(app.exec_())
