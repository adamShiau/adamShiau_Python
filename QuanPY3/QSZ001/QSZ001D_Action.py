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

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

MOVE_TIME_INTERVAL = 1
MAX_PIXEL = 2048

CAMERA_TEST = False
STAGE_TEST = False

class qsz001D(QObject):
    update = pyqtSignal(object)
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
        self.imgTranspose = False
        self.runFlag = False
        self.imgFile = ""
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
        sleep_time_x = MOVE_TIME_INTERVAL * (abs(xmove) / 2500)
        # print(sleep_time_x)

        if ymove > 0:
            ycmd = "+P"+str(ymove)
        else:
            ycmd ="-P"+str(abs(ymove))
        sleep_time_y = MOVE_TIME_INTERVAL * (abs(ymove) / 2500)
        # print(sleep_time_y)

        if xmove*ymove:
            cmd1 = "M:W"
        elif xmove:
            cmd1 = "M:1"
            ycmd = ""
        else:
            cmd1 = "M:2"
            xcmd = ""

        cmd = cmd1 + xcmd + ycmd
        # print(cmd)
        self.preX = self.preX + xmove
        self.preY = self.preY + ymove
        if not STAGE_TEST:
            print(cmd)
            self.stage.writeLine(cmd, addR = True)
            self.stage.writeLine("G", addR = True)
            sleep_time = max(sleep_time_x, sleep_time_y)
            # print(sleep_time)
            time.sleep(sleep_time)

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
    def rotateText(self, index, RotateM):
        emptyImg = np.zeros((MAX_PIXEL, MAX_PIXEL, 3))
        imgout= cv2.putText(emptyImg, str(index), (int(MAX_PIXEL/2), int(MAX_PIXEL/2)),cv2.FONT_HERSHEY_DUPLEX,10, RED, 2, cv2.LINE_AA)
        imgout = cv2.rectangle(imgout, (0,0),(MAX_PIXEL, MAX_PIXEL), RED, DRAW_WIDTH)
        imgout = cv2.warpAffine(imgout, RotateM, (MAX_PIXEL, MAX_PIXEL))
        return imgout



    
    def startScan2(self):
        index = 0
        emptyImgSlot=np.zeros((MAX_PIXEL, self.ysteps*MAX_PIXEL))
        imgOut = emptyImgSlot.copy()
        yindex = 0
        ydelta = 1
        indexout =[]
        #R90 = cv2.getRotationMatrix2D((MAX_PIXEL/2,MAX_PIXEL/2), 90, 1.0)
        #R270 = cv2.getRotationMatrix2D((MAX_PIXEL/2,MAX_PIXEL/2), 270, 1.0)
        for i in range(self.xsteps):
            innerImg = emptyImgSlot.copy() 
            for j in range(self.ysteps):
                if not self.runFlag:
                    break
                if j !=0:
                    yindex = yindex+ydelta 
                self.stageIndexMove(index)
                self.getImage()
                #rotateTextImg = self.rotateText(index, R270)
                #self.imgC = rotateTextImg+self.imgC
                self.img1 = cv2.flip(self.img1, 1)
                innerImg[:,yindex*MAX_PIXEL:(yindex+1)*MAX_PIXEL] =self.img1      
                imgOut[i*MAX_PIXEL:(i+1)*MAX_PIXEL,:]=innerImg
                indexout.append(str(index))
                index = index+1
                self.update.emit(imgOut)         
            ydelta = ydelta*(-1)
            if i != self.xsteps-1:
                imgOut = np.concatenate((imgOut, emptyImgSlot), axis = 0)
        self.finished.emit(indexout)

    def startScan(self):
        R90 = cv2.getRotationMatrix2D((MAX_PIXEL/2,MAX_PIXEL/2), 90, 1.0)
        R270 = cv2.getRotationMatrix2D((MAX_PIXEL/2,MAX_PIXEL/2), 270, 1.0)
        if self.saveFlag:
            emptyImgSlot=np.zeros((MAX_PIXEL, self.ysteps*MAX_PIXEL))
        else:
            emptyImgSlot=np.zeros((MAX_PIXEL, self.ysteps*MAX_PIXEL, 3))
        
        index = 0
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
                if not self.saveFlag:
                    rotateTextImg = self.rotateText(index, R270)
                    self.imgC = rotateTextImg+self.imgC
                    cv2.rectangle(self.imgC, (0,0),(MAX_PIXEL, MAX_PIXEL), RED, DRAW_WIDTH)
                    #cv2.putText(self.imgC, str(index), (int(MAX_PIXEL/2), int(MAX_PIXEL/2)), cv2.FONT_HERSHEY_DUPLEX,10, RED, 2, cv2.LINE_AA)
                
                if(self.imgTranspose):
                    if self.saveFlag:
                        self.img1 = cv2.transpose(self.img1)
                    else:
                        self.imgC = cv2.transpose(self.imgC)
                
                if self.saveFlag:
                    self.img1 = cv2.flip(self.img1, 1)
                    innerImg[:,yindex*MAX_PIXEL:(yindex+1)*MAX_PIXEL] =self.img1      
                    imgOut[i*MAX_PIXEL:(i+1)*MAX_PIXEL,:]=innerImg
                else:
                    self.imgC = cv2.flip(self.imgC, 1)
                    innerImg[:,yindex*MAX_PIXEL:(yindex+1)*MAX_PIXEL,:] =self.imgC      
                    imgOut[i*MAX_PIXEL:(i+1)*MAX_PIXEL,:,:]=innerImg
                indexout.append(str(index))
                index = index+1
                self.update.emit(imgOut)         
            ydelta = ydelta*(-1)
            if i != self.xsteps-1:
                imgOut = np.concatenate((imgOut, emptyImgSlot), axis = 0)
        if self.saveFlag:
            imgOut = cv2.transpose(imgOut)
            cv2.imwrite(self.imgFile, imgOut)
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
        img1 = cv2.flip(self.img1, 1)
        imgC = cv2.flip(self.imgC, 1)
        ret, img2 = cv2.threshold(img1, threshold, 255, cv2.THRESH_BINARY)
        cntall, _ = cv2.findContours(img2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(cntall):
            areas = [cv2.contourArea(c) for c in cntall]
            max_index = np.argmax(areas)
            cnt = cntall[max_index]   
            imgC = cv2.drawContours(imgC, cnt, -1, YELLOW, DRAW_WIDTH)
            M = cv2.moments(cnt)
            if(M["m00"] !=0):
                xpos = int(M["m10"]/M["m00"])
                ypos = int(M["m01"]/M["m00"])
            else:
                xpos = 0
                ypos = 0
            print(str(xpos))
            print(str(ypos))
            imgC=cv2.circle(imgC, (xpos, ypos), 20, YELLOW, -1)
        else:
            imgC= np.zeros((MAX_PIXEL, MAX_PIXEL,3))
            xpos =0
            ypos =0
        return imgC, xpos, ypos

if __name__ == '__main__':
    pass

    






    
    
    


    


 
