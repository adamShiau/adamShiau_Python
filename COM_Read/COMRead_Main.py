import os 
import sys 
sys.path.append("../") 
import time 
# import logging
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
import numpy as np
# import py3lib.QuLogger as Qlogger 
# import py3lib.FileToArray as fil2a 
import COMRead_Widget as UI 
import COMRead_Action as ACT
TITLE_TEXT = "COM_Read"
MAX_SAVE_INDEX = 3000

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
            # self.myThread = MyThread() #開一個thread
            self.thread1 = QThread()
            self.data = np.empty(0)
            self.dt = np.empty(0)
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
            self.thread1.started.connect(self.act.runFog) #thread1啟動時會去trigger act.runfog
            self.act.fog_finished.connect(self.myThreadStop) #runFlag=0時fog_finished會emit，之後關掉thread1
            self.act.fog_update.connect(self.plotFog) #fog_update emit 最新40筆data and dt array
            # self.top.read_btn.read.clicked.connect(self.readAscii)
            # self.myThread.temp.connect(self.thread_action)
            self.top.read_btn.read.clicked.connect(self.myThreadStart) # runFlag=1
            self.top.stop_btn.stop.clicked.connect(self.buttonStop) # runFlag=0
            # self.act.update_COMArray.connect(self.plotCOMArray) #更新作圖的ADC array
        
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
        
    def buttonStop(self):#set runFlag=0
            # self.act.setStop()
            self.act.runFlag = False
        
    def thread_action(self): 
            self.act.readAscii(False)
        
    def myThreadStart(self):
            # self.myThread.start()
            self.act.runFlag = True
            self.thread1.start()
        
    def myThreadStop(self):
            # self.act.readAscii(True)
            self.top.com_plot.ax.clear()
            # self.myThread.terminate()
            self.thread1.quit()
            self.thread1.wait()
        
    def plotCOMArray(self, data):
            self.top.com_plot.ax.plot(data, color = "blue", linestyle = '-', label= "real-time")
            self.top.com_plot.figure.canvas.draw()
        
    def plotFog(self, data, dt):
        temp = len(self.data)
        # self.logger.error("len = %d", temp)

        if (len(self.data) >= 3000):
                self.data = self.data[5:]
                self.dt = self.dt[5:]
                # self.logger.error("delete data")

        # coeff = self.top.fog.coeff.text()
        # if (coeff == ""):
                # self.act.coeff = 1
        # else:
                # self.act.coeff = float(coeff)
        #print(f_coeff)

        self.data = np.append(self.data, data)
        self.dt = np.append(self.dt, dt)
        print('len(data)', len(self.data))
        print('len(dt)', len(self.dt))
        # print(self.dt, end=', ')
        # print(self.data)
        #print(self.data)

        # 2020.1.17 sherry, save file move to act.runFog()
        # if (self.act.SaveFileName != ''):
        # 	fil2a.array1DtoTextFile(self.act.SaveFileName, self.data, self.loggername)
        self.top.com_plot.ax.clear()
		
        self.top.com_plot.ax.set_ylabel("")
        self.top.com_plot.ax.plot(self.dt, self.data, color = 'blue', linestyle = '-', marker = '*')
        self.top.com_plot.figure.canvas.draw()
        self.top.com_plot.figure.canvas.flush_events()

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWindow()
    main.show()
    os._exit(app.exec_())
