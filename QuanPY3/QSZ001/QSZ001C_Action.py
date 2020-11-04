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
areadtp = np.dtype([('id',int),('area', float),('photo_index', int),('xpos',int),('ypos',int),('time', float), ('rate', float)])

DRAW_WIDTH = 5
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

MOVE_TIME_INTERVAL = 2

texti = 10

class BacteriaData(object):
    def __init__ (self):
        self.photo_index = -1
        self.xpos = None
        self.ypos = None
        self.id = None
        self.arealist = []
        self.timelist = []
        self.rate = 0
    
    def calRate(self):
        x = np.array(self.timelist)
        print("===== timelist =====")
        print(x)
        y = np.array(np.log(self.arealist))
        print("===== arealist =====")
        print(y)
        temp = np.polyfit(x,y,1)
        self.rate = temp[0]  

class PlateData(object):
    def __init__(self, loggername):    
        self.scan_index = 0
        self.calib = 1
        self.name = "empty"
        self.fpath = ""
        self.photolist = []
        self.topten = np.empty(0)
        self.loggername = loggername
        self.logger = logging.getLogger(loggername)
        self.bacteriaList = []
        self.timeBegin = 0

    def createNew(self, filepath, name, x0, y0, delta, stepx, stepy, calib):
        self.scan_index = 0
        self.calib = calib
        self.name = name
        self.fpath = filepath
        # Create photolist for scan
        # print("name = " + self.name)
        # print("filepath = " + self.fpath)
        # print("calib = " + str(self.calib) )
        self.generatePhotoTable( x0, y0, delta, stepx, stepy)

    def generatePhotoTable(self, x0, y0, delta, stepx, stepy):
        deltas = delta
        ypos = 0
        for i in range(0,stepx):
            xpos = x0 + i*delta
            for j in range(0, stepy):
                photo_index = i*stepy+j
                if j == 0:
                    ypos = ypos
                else :
                    ypos = ypos+deltas

                if photo_index == 0:
                    ypos = y0

                self.photolist.append([photo_index, xpos, ypos])
            deltas = deltas*(-1)
        # print("photolist")
        # print(self.photolist)

    def reducePhotoList(self):
        num = len(self.topten)
        newphotolist = []
        if num:
            temp = self.topten
            temp.sort(order = 'photo_index')
            pre_index = -1
            for i in range(0, num):
                if temp[i]['photo_index'] == pre_index:
                    pass
                else: 
                    newphotolist.append(self.photolist[temp[i]['photo_index']])
                    pre_index = temp[i]['photo_index']
            self.photolist = newphotolist 

        else:
            self.logger.error("topten empty")

    def newBacteria(self, maxarea, t0):
        for topten_index in range (0, maxarea):
            bacData = BacteriaData() 
            bacData.photo_index = self.topten[topten_index]['photo_index']
            bacData.id = self.topten[topten_index]['id']
            bacData.xpos = self.topten[topten_index]['xpos']
            bacData.ypos = self.topten[topten_index]['ypos']
            bacData.rate = self.topten[topten_index]['rate']
            bacData.timelist.append(self.topten[topten_index]['time']-t0)
            bacData.arealist.append(self.topten[topten_index]['area'])
            # print("===== newBacteria =====")
            # print(bacData.timelist)
            self.bacteriaList.append(bacData)

    def checkPhoto(self, photo_index, outarea, tolerance, t0):
        self.topten.sort(order = 'area')
        num = len(outarea)
        for i in range(0, len(self.topten)):
            if self.topten[i]['photo_index'] == photo_index:  # if photo_index in topten is equal to analysis photo_index
                matched = 0
                for j in range(0, num):
                    #print("scan for outarea"+str(outarea[j]))
                    deltax = abs(self.topten[i]['xpos'] - outarea[j][3]) # check if the postion is correct or not
                    deltay = abs(self.topten[i]['ypos'] - outarea[j][4]) # check if the postion is correct or not
                    lengthcheck = len(self.bacteriaList[self.topten[i]['id']].arealist) < (self.scan_index+1)
                    if (deltax < tolerance) and (deltay < tolerance) and lengthcheck:
                        matched = 1
                        self.topten[i]['area'] = outarea[j][1]
                        self.topten[i]['xpos'] = outarea[j][3]
                        self.topten[i]['ypos'] = outarea[j][4]
                        self.topten[i]['time'] = outarea[j][5]
                        self.bacteriaList[self.topten[i]['id']].arealist.append(outarea[j][1])
                        self.bacteriaList[self.topten[i]['id']].timelist.append(outarea[j][5]-t0)
                        self.bacteriaList[self.topten[i]['id']].xpos = outarea[j][3]
                        self.bacteriaList[self.topten[i]['id']].ypos = outarea[j][4]
                        # print("===== checkPhoto =====")
                        # print(self.bacteriaList[self.topten[i]['id']].timelist)

                    if not matched:
                        self.topten[i]['area'] = 0.1
                        self.topten[i]['time'] = outarea[j][5]
                        self.bacteriaList[self.topten[i]['id']].arealist.append(0.1)
                        self.bacteriaList[self.topten[i]['id']].timelist.append(outarea[j][5]-t0)
                        # print("===== not matched =====")
                        # print(self.bacteriaList[self.topten[i]['id']].timelist)

    def updateRate(self, maxarea):
        self.topten.sort(order = 'id')
        for i in range(0, maxarea):
            if (self.scan_index > 0): # and (self.topten[i]['area'] != 0.1):
                self.bacteriaList[i].calRate()
                self.topten[i]['rate'] = self.bacteriaList[i].rate 
            else:
                self.topten[i]['rate'] = self.bacteriaList[i].arealist[0]
        # print("[updateRate]")
        # print(self.topten)

class qsz001C(QObject):
    update = pyqtSignal(int, object, object)
    finished = pyqtSignal(bool)
    def __init__(self, loggername, parent = None):
        super(QObject,self).__init__(parent)
        self.loggername = loggername
        self.logger = logging.getLogger(loggername)
        self.stage = usb.FT232(loggername)
        self.plateList = []
        self.currentPlate = PlateData(loggername)
        self.stage_status = False
        self.camera = cam.FLIRcamera(loggername)
        self.preX = 0
        self.preY = 0
        self.connectStage()
        self.stageHome()
        self.a = TEST.TestImage("a.txt")
        # self.b = TEST.TestImage("b.txt")

    def connectStage(self):
        self.stage.portConnect(comportid, baudrate = 19200)

    def stageHome(self):
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

        cmd = cmd1 + xcmd + ycmd
        # print(cmd)
        time.sleep(MOVE_TIME_INTERVAL)
        # print("take photo")
        self.preX = self.preX + xmove
        self.preY = self.preY + ymove

        #self.stage.writeLinern(cmd)
        #self.stage.writeLinern("G")

    def getImage(self):
        if (self.camera.status == False):
            self.camera.startAcquire()
        self.img1 = self.camera.getImage()
        self.camera.endAcquire()
        # print(self.img1)
        #self.img1 = self.img1[0:10, 0:10]
        #self.img1 = cv2.circle(self.img1, (texti,texti), 50, YELLOW ,-1)
        timestamp = time.time()
        return timestamp

    def getImage2(self, fname):
        self.img1 = cv2.imread(fname)
        self.img1 = cv2.cvtColor(self.img1, cv2.COLOR_BGR2GRAY)
        timestamp = time.time()
        return timestamp

    # def findAreaNew(self, photo_index, maxarea):
    #     info = []
    #     for i in range(0,maxarea):
    #         t = time.time()
    #         area = int(np.random.random()*100)
    #         x = int(np.random.random()*1024)
    #         y = int(np.random.random()*1024)
    #         info.append((i, area, photo_index, x, y, t,0))
        
    #     #outarea = np.array(info)
    #     outarea = np.array(info, dtype = areadtp)
    #     return outarea

    # def findArea(self, photo_index, maxarea):
    #     info = []
    #     tempid = -1
    #     prob1 = np.random.random()
    #     prob2 = np.random.random()
    #     prob3 = np.random.random()-0.5
    #     prob4 = np.random.random()-0.5

    #     num = len(self.currentPlate.topten)
    #     for i in range(0, num):
    #         t = time.time()
    #         if self.currentPlate.topten[i]['photo_index'] == photo_index:
    #             if prob1 < 0.98:
    #                 area = self.currentPlate.topten[i]['area']*(1+prob2/2)
    #                 xpos = self.currentPlate.topten[i]['xpos']*(1+prob3/100)
    #                 ypos = self.currentPlate.topten[i]['ypos']*(1+prob4/100)
    #             else:
    #                 area = int(np.random.random()*100)
    #                 xpos = int(np.random.rand()*1024)
    #                 ypos = int(np.random.random()*1024)
    #         else:
    #             area = int(np.random.random()*100)
    #             xpos = int(np.random.random()*1024)
    #             ypos = int(np.random.random()*1024)

    #         info.append((tempid, area, photo_index, xpos, ypos, t, 0 ))

    #     outarea = np.array(info, dtype = areadtp)
    #     return outarea

    def saveImageFile(self, img, photo_index, now, contour):
        tt = time.localtime(now)
        dateStr = str(tt.tm_year)+"_"+str(tt.tm_mon)+"_"+str(tt.tm_mday)+"_"
        timeStr = str(tt.tm_hour)+"_"+str(tt.tm_min)+"_"+str(tt.tm_sec)
        if contour:
            final = "M.jpg"
        else:
            final = ".jpg"
        fname = self.currentPlate.fpath + '\\' + dateStr + timeStr + final
        cv2.imwrite(fname, img)

    def sortContour(self, cntall, maxarea, photo_index, timestamp):
        area1 = []
        info = []
        for i, cnt in enumerate(cntall):
            area1.append((i, cv2.contourArea(cnt)))
        area2 = sorted(area1, key = lambda d: d[1], reverse = True)
        img4 = self.img1.copy()
        for i in range(0, min(len(cntall), maxarea)):
            img4 = cv2.drawContours(img4, cntall[area2[i][0]],-1,BLUE,DRAW_WIDTH)
            area = area2[i][1]*self.currentPlate.calib
            M = cv2.moments(cntall[area2[i][0]])
            if (M["m00"] != 0):
                xpos = int(M["m10"]/M["m00"])
                ypos = int(M["m01"]/M["m00"])
            else:
                xpos = 0
                ypos = 0
                self.logger.error("Center not find: index="+str(photo_index)+",name="+self.currentPlate.name)
            img4 = cv2.circle(img4, (xpos,ypos), 10, (255, 255, 0),-1)
            info.append((i, area, photo_index, xpos, ypos, timestamp, 0 ))

        outarea = np.array(info, dtype = areadtp)
        return outarea, img4

    def findAreaNew2(self, photo_index, maxarea, threshold, timestamp):
        ret, img2 = cv2.threshold(self.img1, threshold, 255, cv2.THRESH_BINARY)
        cntall, hierarchy = cv2.findContours(img2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        outarea, img4 = self.sortContour(cntall, maxarea, photo_index, timestamp) 
        return outarea, img4

    # def scanNewPlate(self, photolist, maxarea):
    #     for i in range(0, len(photolist)):
    #         #print("corrd:"+str(arealist[i][1])+", "+str(arealist[i][2]))
    #         temp = self.findAreaNew(i, maxarea)
    #         if i == 0:
    #             topten = temp
    #         else:
    #             topten = np.append(topten, temp)
    #             topten.sort(order ='area')
    #             topten = topten[-maxarea:]
        
    #     for j in range(0,maxarea):
    #         topten[j]['id'] = j
    #     return topten

    def CreateNewPlate(self, filepath, name, x0, y0, delta, stepx, stepy, maxarea, calib, type = False):
        newPlate = PlateData(self.loggername)
        newPlate.createNew(name, filepath, x0, y0, delta, stepx, stepy, calib)
        # newPlate.topten = self.scanNewPlate(newPlate.photolist, maxarea)
        if (type == True):
            # newPlate.reducePhotoList()
            # newPlate.topten.sort(order = 'id')
            # newPlate.newBacteria(maxarea)
            self.plateList.append(newPlate)
        else:
            self.currentPlate = newPlate

    def setPlate(self, platename):
        notmatched = 1
        num = len(self.plateList)
        i = 0
        while (i < num) and notmatched:
            if self.plateList[i].name == platename:
                notmatched = 0
                self.currentPlate = self.plateList[i]
            i = i + 1

        if notmatched:
            self.logger.error("no matched platename")

    def delPlate(self, Platename):
        notmatched = 1
        num = len(self.plateList)
        i = 0
        while (i < num) and notmatched:
            if self.plateList[i].name == Platename:
                notmatched = 0
                del self.plateList[i]
            i = i + 1

        if notmatched:
            self.logger.error("wrong delte Platename")

    def calculatePos(self, index):
        # print("photo lens =")
        # print(len(self.currentPlate.photolist))
        photo_index = self.currentPlate.photolist[index][0]
        target_xpos = self.currentPlate.photolist[index][1]
        target_ypos = self.currentPlate.photolist[index][2]
        xpos = target_xpos - self.preX
        ypos = target_ypos - self.preY
        return photo_index, xpos, ypos

    def newPlateTopten(self, index, outarea, maxarea):
        if index == 0:
            self.currentPlate.topten = outarea
        else:
            self.currentPlate.topten = np.append(self.currentPlate.topten, outarea)
            self.currentPlate.topten.sort(order = 'area')
            self.currentPlate.topten = self.currentPlate.topten[-maxarea:]
        num = len(outarea)
        if (num > 0):
            for j in range(0, min(num, maxarea) ):
                self.currentPlate.topten[j]['id'] = j
        # print("[newPlateTopten]")
        # print(self.currentPlate.topten)
        return num

    def scanCurrentPlate(self, maxarea, threshold, tolerance, findarea): 
        num_photo = len(self.currentPlate.photolist)
        self.stageHome()
        self.preX = 0
        self.preY = 0
        i = 0
        topten = 0
        while (i < num_photo):
            print("===== scan_index = " + str(self.currentPlate.scan_index))
            print("===== photo index = " + str(i))
            photo_index, xpos, ypos = self.calculatePos(i)
            self.stageMove(xpos, ypos)
            # now = self.getImage() # need to open if NOT TEST
            # TEST begin
            variation = 0
            rate = 0.3
            # maxarea = 3
            now = time.time()
            if (self.currentPlate.scan_index == 0):
                self.img1 = self.a.generateImage(photo_index, 0, variation, rate, maxarea, True, True)
            else:
                self.img1 = self.a.generateImage(photo_index, self.currentPlate.scan_index, variation, rate, maxarea, False, True)
            # TEST end

            if findarea:
                outarea, self.img4 = self.findAreaNew2(photo_index, maxarea, threshold, now)
                self.saveImageFile(self.img1, photo_index, now, False)
                self.saveImageFile(self.img4, photo_index, now, True)
                if self.currentPlate.scan_index == 0:
                    self.num_topten = self.newPlateTopten(i, outarea, maxarea)
                    # self.currentPlate.reducePhotoList()
                    self.currentPlate.topten.sort(order = 'id')
                    self.currentPlate.timeBegin = self.currentPlate.topten[0]['time']
                    self.currentPlate.newBacteria(self.num_topten, self.currentPlate.timeBegin)
                else:
                    self.currentPlate.checkPhoto(photo_index, outarea, tolerance, self.currentPlate.timeBegin)
                    self.currentPlate.updateRate(self.num_topten)
                self.update.emit(i, self.img4, self.currentPlate.topten)
            else:
                self.update.emit(i, self.img1, self.currentPlate.topten)
            i = i + 1
            # while end
        self.currentPlate.scan_index = self.currentPlate.scan_index + 1
        self.finished.emit(findarea)


if __name__ == '__main__':
    pass

    






    
    
    


    


 
