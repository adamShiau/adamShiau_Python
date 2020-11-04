import sys
import time
sys.path.append("../")
import logging
import numpy as np 
import py3lib.COMPort as usb
import py3lib.Camera as cam 
import cv2
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
import QSZ001C_test as TEST

comportid = "067B:2303" 
DRAW_WIDTH = 4

GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

MOVE_TIME_INTERVAL = 1
MAX_PIXEL = 1024

CAMERA_TEST = True
STAGE_TEST = True

class qsz001D(QObject):
    update = pyqtSignal(object, int, int)
    finished = pyqtSignal(object)
    def __init__(self, loggername, parent = None):
        super(QObject,self).__init__(parent)
        self.loggername = loggername
        self.logger = logging.getLogger(loggername)
        self.stage = usb.FT232(loggername)
        self.stage_status = False
        self.camera = cam.FLIRcamera(loggername)
        self.preX = 0
        self.preY = 0
        #self.connectStage()
        #self.stageHome()
        self.a = TEST.TestImage("a.txt")
        self.imgTranspose = True
        self.runFlag = False
        # self.b = TEST.TestImage("b.txt")

    def connectStage(self):
        if not STAGE_TEST:
            result = self.stage.portConnect(comportid, baudrate = 19200)
        else:
            result = True
        return result

    def connectCamera(self):
        if not CAMERA_TEST:
            result = self.camera.camInit()
        else:
            result = True
        return result
    
    def stageHome(self):
        if not STAGE_TEST:
            self.stage.writeLine("H:W--", True)
        self.preX = 0
        self.preY = 0

    def stageMove(self, xmove, ymove):  
        if xmove > 0:
            xcmd = "+P"+str(xmove)
        else:
            xcmd = "-P"+str(abs(xmove))

        if ymove > 0:
            ycmd = "+P"+str(ymove)
        else:
            ycmd ="-P"+str(abs(ymove))

        if xmove*ymove:
            cmd1 = "M:W"
        elif xmove:
            cmd1 = "M:1"
            ycmd = ""
        else:
            cmd1 = "M:2"
            xcmd = ""

        time.sleep(MOVE_TIME_INTERVAL)
        self.preX = self.preX + xmove
        self.preY = self.preY + ymove
        if not STAGE_TEST:
            self.stage.writeLine(cmd, addR = True)
            self.stage.writeLine("G", addR = True)

    def getImage(self):
        if CAMERA_TEST:
            self.circletImg()
            #self.img1 = cv2.cvtColor(self.img1, cv2.COLOR_GRAY2RGB)
            self.imgC = cv2.cvtColor(self.img1, cv2.COLOR_GRAY2RGB)
        else:
            if (self.camera.status == False):
                self.camera.startAcquire()
            self.img1 = self.camera.getImage()
            self.imgC = cv2.cvtColor(self.img1, cv2.COLOR_GRAY2RGB)
            self.camera.endAcquire()

    def circletImg(self):
        numb = int(np.random.rand()*4.0)
        radius = int(np.random.rand()*100.0)
        xpos = int(np.random.rand()*(MAX_PIXEL-50))
        ypos = int(np.random.rand()*(MAX_PIXEL-50))
        self.img1 = np.zeros((MAX_PIXEL,MAX_PIXEL), np.uint8)
        for i in range(numb):
            cv2.circle(self.img1, (xpos, ypos), radius, 128, -1)

    def setScan(self, initx, xsteps, inity, ysteps, delta):
        self.initx = initx
        self.inity = inity
        self.xsteps = xsteps
        self.ysteps = ysteps
        self.delta = delta
        self.genScanTable(initx, inity, delta, xsteps, ysteps)

    def genScanTable(self, x0, y0, delta, stepx, stepy):
        deltas = delta
        ypos = 0
        self.scanTable=[]
        deltaindex =1
        for i in range(0,stepx):
            xpos = x0 + i*delta
            for j in range(0, stepy):
                photo_index = i*stepy+j
                if j == 0:
                    pass
                else :
                    ypos = ypos+deltas

                if photo_index == 0:
                    ypos = y0
                self.scanTable.append([xpos, ypos])
            deltas = deltas*(-1)
            deltaindex = deltaindex*(-1)
        print(self.scanTable)
    
    def stageIndexMove(self, photoindex):
        xpos = self.scanTable[photoindex][0]
        ypos = self.scanTable[photoindex][1]
        xmove = xpos-self.preX
        ymove = ypos-self.preY
        self.stageMove(xmove, ymove)

    def startScan(self):
        index = 0
        emptyImgSlot=np.zeros((MAX_PIXEL, self.ysteps*MAX_PIXEL, 3))
        imgOut = emptyImgSlot.copy()
        yindex = 0
        ydelta = 1
        indexout =[]
        for i in range(self.xsteps):
            innerImg = emptyImgSlot.copy() 
            for j in range(self.ysteps):
                if not self.runFlag:
                    break
                if j !=0:
                    yindex = yindex+ydelta 
                self.stageIndexMove(index)
                self.getImage()
                cv2.rectangle(self.imgC, (0,0),(MAX_PIXEL, MAX_PIXEL), RED, DRAW_WIDTH)
                cv2.putText(self.imgC, str(index), (int(MAX_PIXEL/2), int(MAX_PIXEL/2)), cv2.FONT_HERSHEY_DUPLEX,10, RED, 2, cv2.LINE_AA)
                if(self.imgTranspose):
                    self.imgC = cv2.transpose(self.imgC)
                innerImg[:,yindex*MAX_PIXEL:(yindex+1)*MAX_PIXEL,:] =self.imgC      
                imgOut[i*MAX_PIXEL:(i+1)*MAX_PIXEL,:,:]=innerImg
                indexout.append(str(index))
                index = index+1
                self.update.emit(imgOut, self.preX, self.preY)         
            ydelta = ydelta*(-1)
            if i != self.xsteps-1:
                imgOut = np.concatenate((imgOut, emptyImgSlot), axis = 0)
        self.finished.emit(indexout)
    
    def setGain(self, value=0): 
        if not CAMERA_TEST:
            if value == 0:
                self.camera.setGainAuto()
            else:
                self.camera.setGain(value)
    
    def setExplosure(self, time=0):
        if not CAMERA_TEST:
            if time == 0:  
                self.camera.setExplosureAuto()
            else:
                self.camera.setExplosure(time)

    def anaImage(self, threshold):
        self.getImage()
        ret, img2 = cv2.threshold(self.img1, threshold, 255, cv2.THRESH_BINARY)
        cntall, _ = cv2.findContours(img2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(cntall):
            areas = [cv2.contourArea(c) for c in cntall]
            max_index = np.argmax(areas)
            cnt = cntall[max_index]   
            self.imgC = cv2.drawContours(self.imgC, cnt, -1, YELLOW, DRAW_WIDTH)
            M = cv2.moments(cnt)
            if(M["m00"] !=0):
                xpos = int(M["m10"]/M["m00"])
                ypos = int(M["m01"]/M["m00"])
            else:
                xpos = 0
                ypos = 0
            print(str(xpos))
            print(str(ypos))
            cv2.circle(self.imgC, (xpos, ypos), 3, YELLOW, -1)
        else:
            self.imgC= np.zeros((MAX_PIXEL, MAX_PIXEL,3))
            xpos =0
            ypos =0
        return self.imgC, xpos, ypos
    

if __name__ == '__main__':
    pass

    






    
    
    


    


 
