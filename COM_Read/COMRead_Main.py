import os 
import sys 
sys.path.append("../") 
import time 
# import logging
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
# import py3lib.QuLogger as Qlogger 
# import py3lib.FileToArray as fil2a 
import COMRead_Widget as UI 
import COMRead_Action as ACT
TITLE_TEXT = "COM_Read"

class MyThread(QThread): 
    temp = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        # self.temp.emit(True)
        # print('stop')
        self.wait()

    def run(self):
        while(True):
            self.temp.emit()
            time.sleep(0.01)

class mainWindow(QMainWindow):
    def __init__(self, parent = None):
        super (mainWindow, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.move(50,50)
        self.loggername = "Total"
        # self.addAccesoryFlag(self.loggername) # Add logger
        self.top = UI.mainWidget()
        self.act = ACT.COMRead_Action(self.loggername)
        self.myThread = MyThread() #開一個thread
        self.mainUI()
        # self.mainMenu()
        self.linkFunction()
        # self.loadUIpreset()
        
        # self.usbConnect()

    def mainUI(self):
        mainLayout = QGridLayout()
        self.setCentralWidget(QWidget(self))
        mainLayout.addWidget(self.top,0,0,1,1)
        self.centralWidget().setLayout(mainLayout)

    # def mainMenu(self):
        # mainMenu = self.menuBar()
        # menu_about = QAction("&Version", self)
        # menu_about.triggered.connect(self.aboutBox)
        # aboutMenu = mainMenu.addMenu("&About")
        # aboutMenu.addAction(menu_about)

    def linkFunction(self):
        self.top.usb.btn.clicked.connect(self.usbConnect)
        # self.top.read_btn.read.clicked.connect(self.readAscii)
        self.myThread.temp.connect(self.thread_action)
        self.top.read_btn.read.clicked.connect(self.myThreadStart)
        self.top.stop_btn.stop.clicked.connect(self.myThreadStop) 
        self.act.update_COMArray.connect(self.plotCOMArray) #更新作圖的ADC array
        # ''' Btn connect '''
        # self.top.test.timeBtn.clicked.connect(self.callTimeDialog)
        # self.top.test.send.clicked.connect(self.sendButton)
        # self.top.adc.start_rd.clicked.connect(self.adcThreadStart) #run thread
        # self.top.adc.stop_rd.clicked.connect(self.adcThreadStop)
        
        # ''' emit connect '''
        # self.act.update_text.connect(self.print_ADC_value) #更新ADC讀到的值
        # self.adcThread.temp.connect(self.rdButton_action) #讓thread 去觸發rdButton_action
        # self.act.update_adcArray.connect(self.plotAdcArray) #更新作圖的ADC array
        
    def usbConnect(self):
        self.usbConnStatus = self.act.usbConnect()
        print("status:" + str(self.usbConnStatus))
        if self.usbConnStatus:
            # print(self.act.COM.port.port)
            self.top.usb.SetConnectText(Qt.black, self.act.COM.port.port + " Connection build", True)
            # self.top.test.send.setEnabled(True)
            print("Connect build")
        else:
            self.top.usb.SetConnectText(Qt.red,"Connect failed", True)
            print("Connect failed")
            
    def readAscii(self):
        # print('hi')
        self.act.readAscii(False)
        
    def thread_action(self): 
        self.act.readAscii(False)
        
    def myThreadStart(self):
        self.myThread.start()
        
    def myThreadStop(self):
        self.act.readAscii(True)
        self.top.com_plot.ax.clear()
        self.myThread.terminate()
        
    def plotCOMArray(self, data):
        self.top.com_plot.ax.plot(data, color = "blue", linestyle = '-', label= "real-time")
        self.top.com_plot.figure.canvas.draw()

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWindow()
    main.show()
    os._exit(app.exec_())