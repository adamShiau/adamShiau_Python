import os 
import sys 
sys.path.append("../") 
import time 
import logging
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
import py3lib.QuLogger as Qlogger 
import py3lib.FileToArray as fil2a 
import QSS014_Widget as UI 
import QSS014_Action as ACT


TITLE_TEXT = " QSS014 "
VERSION_TEXT = TITLE_TEXT + "\n" + \
" QSS014 V1.10 \n\n" + \
" Copyright @ 2020 TAIP \n" + \
" Maintain by Quantaser Photonics Co. Ltd "

ERROR_TEXT = "COM port return error, \n\n" + \
"please press START button again."

class MyThread(QThread): #此thread運行後每隔0.5s 送出trigger一次
    temp = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        # self.temp.emit(True)
        self.wait()

    def run(self):
        while(True):
            self.temp.emit()
            time.sleep(0.5)


class mainWindow(QMainWindow):
    def __init__(self, parent = None):
        super (mainWindow, self).__init__(parent)
        self.setWindowTitle(TITLE_TEXT)
        self.move(50,50)
        self.loggername = "Total"
        # self.addAccesoryFlag(self.loggername) # Add logger
        self.top = UI.mainWidget()
        self.act = ACT.qss014Action(self.loggername)
        self.adcThread = MyThread() #開一個thread
        self.mainUI()
        self.mainMenu()
        self.linkFunction()
        # self.loadUIpreset()
        
        self.usbConnect()

    def mainUI(self):
        mainLayout = QGridLayout()
        self.setCentralWidget(QWidget(self))
        mainLayout.addWidget(self.top,0,0,1,1)
        self.centralWidget().setLayout(mainLayout)

    def mainMenu(self):
        mainMenu = self.menuBar()
        menu_about = QAction("&Version", self)
        menu_about.triggered.connect(self.aboutBox)
        aboutMenu = mainMenu.addMenu("&About")
        aboutMenu.addAction(menu_about)

    def linkFunction(self):
        self.top.usb.btn.clicked.connect(self.usbConnect)

        #Btn connect
        self.top.test.timeBtn.clicked.connect(self.callTimeDialog)
        self.top.test.send.clicked.connect(self.sendButton)
        self.top.adc.start_rd.clicked.connect(self.adcThreadStart) #run thread
        self.top.adc.stop_rd.clicked.connect(self.adcThreadStop)
        
        #emit connect
        self.act.update_text.connect(self.print_ADC_value) #更新ADC讀到的值
        self.adcThread.temp.connect(self.rdButton_action) #讓thread 去觸發rdButton_action
        self.act.update_adcArray.connect(self.plotAdcArray) #更新作圖的ADC array

    def addAccesoryFlag(self, loggername):
        self.logger = logging.getLogger(loggername)
        #Qlogger.QuConsolelogger(loggername, logging.ERROR)
        Qlogger.QuFilelogger(loggername, logging.ERROR, "log.txt")

    def usbConnect(self):
        self.usbConnStatus = self.act.usbConnect()
        print("status:" + str(self.usbConnStatus))
        if self.usbConnStatus:
            # print(self.act.COM.port.port)
            self.top.usb.SetConnectText(Qt.black, self.act.COM.port.port + " Connection build", True)
            self.top.test.send.setEnabled(True)
            print("Connect build")
        else:
            self.top.usb.SetConnectText(Qt.red,"Connect failed", True)
            print("Connect failed")

    def loadUIpreset(self):
        self.top.test.freq.spin.setValue(self.act.freq)
        self.top.test.phase.spin.setValue(self.act.phase)

    def callTimeDialog(self):
        timeDialog = UI.timeDialog(self.act.timePreset)
        self.act.timePreset = timeDialog.getParameter(self.act.timePreset)
        self.act.writePreset(1)

    def sendButton(self):
        self.act.freq = self.top.test.freq.spin.value()
        self.act.phase = self.top.test.phase.spin.value()

        # self.act.writePreset()
        self.act.sendComCmd()

    def rdButton_action(self): 
        self.act.sendRdAdcCmd(False) #PC送出READ_ADC cmd, 然後讀回傳值，再把此值append到adc_array，然後把回傳值與adc_array emit出來
        
    def adcThreadStart(self):
        self.adcThread.start()
        
    def adcThreadStop(self):
        self.adcThread.terminate()
        self.act.sendRdAdcCmd(True)
        self.top.adc_plot.ax.clear()
        
    def print_ADC_value(self, value):
        self.top.adc.text.setText(str(value))
        
    def plotAdcArray(self, data):
        self.top.adc_plot.ax.plot(data, color = "blue", linestyle = '-', label= "real-time")
        self.top.adc_plot.figure.canvas.draw()

    def aboutBox(self):
        versionBox = QMessageBox()
        versionBox.about(self, "Version", VERSION_TEXT)

    def errorBox(self):
        msgBox = QMessageBox()
        msgBox.about(self, "Message", ERROR_TEXT)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = mainWindow()
    main.show()
    os._exit(app.exec_())

