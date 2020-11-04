import os
import sys
sys.path.append("../")
from py3lib.QuGUIclass import *

# SETTING_FILEPATH = "set"
# SETTING_FILENAME = "set/setting.txt"
TITLE_TEXT = "Quantum Optics Experiment"


class mainWidget(QWidget):
    def __init__(self, parent=None):
        super (mainWidget, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.start = QPushButton("Start")
        self.stop = QPushButton("Stop")
        self.save = QPushButton("Save")
        self.usbCon = connectBlock("USB Connection")
        self.plot = output2Plot()
        self.plot.ax2.set_xlabel("dT (S)")
        self.main_UI()

    def main_UI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.start,0,0,1,1)
        mainLayout.addWidget(self.stop,0,1,1,1)
        mainLayout.addWidget(self.save,0,2,1,1)
        mainLayout.addWidget(self.usbCon.layout1(), 0,5,1,1)
        mainLayout.addWidget(self.plot, 1,0,1,6)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        mainLayout.setColumnStretch(4, 1)
        mainLayout.setColumnStretch(5, 1)
        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(1, 5)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWidget()
    main.show()
    os._exit(app.exec_())
