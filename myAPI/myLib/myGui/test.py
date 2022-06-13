import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class WindowDemo(QMainWindow):
    def __init__(self):
        super(WindowDemo, self).__init__()
        self.resize(200, 200)
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setPixmap(QPixmap('./aegiverse_logo.jpg'))
        self.setCentralWidget(self.logo)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = WindowDemo()
    win.show()
    sys.exit(app.exec_())
