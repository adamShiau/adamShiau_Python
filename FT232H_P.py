import ftd2xx as ft
import numpy as np 
import time
import matplotlib.pyplot as plt

def checkDeviceConnect():
    devNum = ft.createDeviceInfoList() #num of connected dev
    if(devNum == 0):
        err = 1
    elif(devNum > 0):
        for i in range(0, devNum):
            d = ft.getDeviceInfoDetail(i)
            err = 2
            if (d['description'] == b'FT232H'): err = 0
    return err


d = ft.getDeviceInfoDetail()
print()
print()
print()
print()
print()
print(d)

ERR = checkDeviceConnect()
if(ERR == 1):
    print('connect device first')
elif(ERR == 2):
    print('connect FT232H first')
elif(ERR == 0):
    print('connect success!')
    print('dev information: ')
    d2 = ft.openEx(b'FT232H', 2)
    print(d2.getDeviceInfo())


''' host write '''
CMD1 = chr(53)
CMD2 = chr(54)
CMD3 = chr(55)
CMD4 = chr(56)

READ_ADC1_ch0_START = chr(48)
READ_ADC1_ch0_STOP = chr(49)
READ_ADC1_ch1_START = chr(50)
READ_ADC1_ch1_STOP = chr(51)
READ_ADC2_ch0_START = chr(57)
READ_ADC2_ch0_STOP = chr(58)
READ_ADC2_ch1_START = chr(59)
READ_ADC2_ch1_STOP = chr(60)
INTEGRATOR_1_START = chr(61)
INTEGRATOR_1_STOP = chr(62)
MODE1 = chr(1)
MODE2 = chr(2)
MODE3 = chr(3)
SET_T1 = chr(4)
SET_T2 = chr(5)
SET_T3 = chr(6)
SET_T4 = chr(7)
  
TIME_WAIT = 0.1


# d2.write(CMD1)
# d2.write(DUMMY1)
# d2.write(DUMMY2)
# d2.write(DUMMY3)
# d2.write(DUMMY4)
# print("cmd: " + CMD1)
# time.sleep(TIME_WAIT)

# d2.write(CMD2)
# d2.write(DUMMY1)
# d2.write(DUMMY2)
# d2.write(DUMMY3)
# d2.write(DUMMY4)
# print("cmd: " + CMD2)
# time.sleep(TIME_WAIT)

# d2.write(CMD3)
# d2.write(DUMMY1)
# d2.write(DUMMY2)
# d2.write(DUMMY3)
# d2.write(DUMMY4)
# print("cmd: " + CMD3)
# time.sleep(TIME_WAIT)

# d2.write(CMD4)
# d2.write(DUMMY1)
# d2.write(DUMMY2)
# d2.write(DUMMY3)
# d2.write(DUMMY4)
# print("cmd: " + CMD4)
# time.sleep(TIME_WAIT)

# while(1):
    # d2.write(CMD1)
    # d2.write(DUMMY1)
    # d2.write(DUMMY2)
    # d2.write(DUMMY3)
    # d2.write(DUMMY4)
    # print("cmd: " + CMD1)
    # time.sleep(TIME_WAIT)

    # d2.write(CMD2)
    # d2.write(DUMMY1)
    # d2.write(DUMMY2)
    # d2.write(DUMMY3)
    # d2.write(DUMMY4)
    # print("cmd: " + CMD2)
    # time.sleep(TIME_WAIT)

    # d2.write(CMD3)
    # d2.write(DUMMY1)
    # d2.write(DUMMY2)
    # d2.write(DUMMY3)
    # d2.write(DUMMY4)
    # print("cmd: " + CMD3)
    # time.sleep(TIME_WAIT)
    
    # d2.write(CMD4)
    # d2.write(DUMMY1)
    # d2.write(DUMMY2)
    # d2.write(DUMMY3)
    # d2.write(DUMMY4)
    # print("cmd: " + CMD4)
    # time.sleep(TIME_WAIT)
    
    # d2.write(READ_ADC1_ch0_START)
    # print("cmd: " + READ_ch0_START)
    # time.sleep(TIME_WAIT)
    
    # d2.write(READ_ADC1_ch0_STOP)
    # print("cmd: " + READ_ch0_STOP)
    # time.sleep(TIME_WAIT)
    
    # d2.write(READ_ADC1_ch1_START)
    # print("cmd: " + READ_ch1_START)
    # time.sleep(TIME_WAIT)
    
    # d2.write(READ_ADC1_ch1_STOP)
    # print("cmd: " + READ_ch1_STOP)
    # time.sleep(TIME_WAIT)
def setValue(value):
    value1 = value >> 24
    value2 = (value >> 16) & 255
    value3 = (value >> 8) & 255
    value4 = value & 255
    if(value1 == 0):
        value1 = 256
    if(value2 == 0):
        value2 = 256
    if(value3 == 0):
        value3 = 256
    if(value4 == 0):
        value4 = 256
    d2.write(chr(value1))
    d2.write(chr(value2))
    d2.write(chr(value3))
    d2.write(chr(value4))
    

''' '''
# d2.write(MODE1)
# setValue(0)
# d2.write(SET_T3)
# setValue(250)
# d2.write(SET_T4)
# setValue(100)
# d2.write(INTEGRATOR_1_START)
# setValue(0)
# time.sleep(1)
# d2.write(INTEGRATOR_1_STOP)
# setValue(0)
''' host w/R '''
SPI_NEXT_VALID_NUM = 8165
NUM = 1000 
size = int(NUM/2)-1
dt = 20e-3*SPI_NEXT_VALID_NUM
t = size*[0]
data1 = size*[0]
data2 = size*[0]
data3 = size*[0]
data4 = size*[0]
for i in range(1,size):
    t[i] = i
idx = 0
############ADC1 ch0######################
# d2.write(READ_ADC1_ch0_START)
# print("cmd: " + READ_ADC1_ch0_START)  

# d2.purge() 
# val = d2.read(NUM)

# for i in range(0,NUM, 2):
    # if i >= 2:
        
        # data1[idx] = (val[i]*256 + val[i+1])*5/65535
        # print(idx, data1[idx]);
        # idx = idx + 1
        

# idx = 0 
# d2.write(READ_ADC1_ch0_STOP)
# print("cmd: " + READ_ADC1_ch0_STOP)
# print('')
# plt.figure(1)
# plt.plot(data1)
# time.sleep(TIME_WAIT)
############ADC1 ch1######################

# d2.write(READ_ADC1_ch1_START)
# print("cmd: " + READ_ADC1_ch1_START)  

# d2.purge() 
# val = d2.read(NUM)

# for i in range(0,NUM, 2):
    # if i >= 2:
        # data2[idx] = (val[i]*256 + val[i+1])*5/65535
        # print(idx, data2[idx]);
        # idx = idx + 1
    
# idx = 0   
# d2.write(READ_ADC1_ch1_STOP)
# print("cmd: " + READ_ADC1_ch1_STOP)
# print('')
# plt.figure(1)
# plt.plot(t, data2)
# time.sleep(TIME_WAIT)
############ADC2 ch0######################
# d2.write(READ_ADC2_ch0_START)
# print("cmd: " + READ_ADC2_ch0_START)  

# d2.purge() 
# val = d2.read(NUM)

# for i in range(0,NUM, 2):
    # if i >= 2:
        # data3[idx] = (val[i]*256 + val[i+1])*3.3/65535
        # print(data3[idx]);
        # idx = idx + 1
    
    
# idx = 0     
# d2.write(READ_ADC2_ch0_STOP)
# print("cmd: " + READ_ADC2_ch0_STOP)
# print('')
# plt.figure(1)
# plt.plot(t, data3)
# time.sleep(TIME_WAIT)
############ADC2 ch1######################
# d2.write(READ_ADC2_ch1_START)
# print("cmd: " + READ_ADC2_ch1_START)  

# d2.purge() 
# val = d2.read(NUM)

# for i in range(0,NUM, 2):
    # if i >= 2:
        # data4[idx] = (val[i]*256 + val[i+1])*3.3/65535
        # print(data4[idx]);
        # idx = idx + 1
    
# idx = 0     
# d2.write(READ_ADC2_ch1_STOP)

# print("cmd: " + READ_ADC2_ch1_STOP)
# print('')
# plt.figure(1)
# plt.plot(t, data4)

# plt.show()
''' '''
#########################################
# while(1):
    # d2.write(CMD1)
    # print("cmd: " + CMD1)
    # time.sleep(TIME_WAIT)

    # d2.write(CMD2)
    # print("cmd: " + CMD2)
    # time.sleep(TIME_WAIT)

    # d2.write(CMD3)
    # print("cmd: " + CMD3)
    # time.sleep(TIME_WAIT)
    
    # d2.write(CMD4)
    # print("cmd: " + CMD4)
    # time.sleep(TIME_WAIT)
    
    # d2.write(READ_START)
    # print("cmd: " + READ_START)
    # val = d2.read(2);
    # print(val[0])
    # print(val[1])
    
    # print(d2.read(1)[0])
    # print(d2.read(1)[0])
    # for i in range(0, 20):
        # print(d2.read(TIME_WAIT)[0])
        
    # d2.write(READ_STOP)
    # print("cmd: " + READ_STOP)
    
    # d2.write(READ_STOP)
    # print("cmd: " + READ_STOP)

# while(1):
# ''' '''
    # d2.write(READ_START)
    # val = d2.read(2);
    # print(val[0])
    # print(val[1])
    # print((val[0]*256+val[1])*3.3/65535)
    # d2.write(READ_STOP)
    # time.sleep(0.5)
# ''' '''
    # d2.purge();
    # for i in range(0,100):
# '''
        # d2.write(READ_START)
        # val = d2.read(2);
        # d2.write(READ_STOP)
        # print(val[0])
        # print(val[1])
# '''
        # val = d2.read(1);
        # print(val[0])
 

# while(1):
    
    # rq = d2.getQueueStatus()
    # if rq > 0 :
        # val = d2.read(rq)
        # for i in range(0, rq):
            # print(i, val[i])
        # d2.purge()
        
# d2.purge()      
# while(1):
    # val = d2.read(4)
    # print(val[0], end=', ')
    # print(val[1], end=', ')
    # print(val[2], end=', ')
    # print(val[3])
    # d2.purge() 
    
# d2.purge() 
# idx = 1
# val = d2.read(300)
# while(1):
    # for i in range(0,300, 10):
        # print(i, val[i], end=', ')
        # print(val[i+1], end=', ')
        # print(val[i+2], end=', ')
        # print(val[i+3], end=', ')
        # print(val[i+4])
        # print(i, val[i+5], end=', ')
        # print(val[i+6], end=', ')
        # print(val[i+7], end=', ')
        # print(val[i+8], end=', ')
        # print(val[i+9])
        # if(val[i]==0 and val[i+1]==1): 
            # vH = val[i+2]
            # if(val[i+5]==4 and val[i+6]==5):
                # vL = val[i+7]
                # print(vH, end=', ')
                # print(vL, end=', ')
                # print((vH*255+vL)*5/65535)
        # print('****************')
        # idx = idx + 1
    # idx = 1
    # d2.purge() 
    # d2.resetDevice()
    # time.sleep(0.5)
    # val = d2.read(300)
    # print("")
    

    
    
    
# d2.purge() 
# idx = 1
# val = d2.read(200)
# while(1):
    # for i in range(0,200, 2):
        # print('i= ', i, end=', ')
        # print(val[i], end=', ')
        # print(val[i+1], end=', ')
        # print((val[i]*256+val[i+1])*5.0/65535)
    # d2.purge() 
    # val = d2.read(200)
    # print('')
    
# rq = d2.getQueueStatus()
# print('rq1= ', rq)
# val = d2.read(100)
# for i in range(0,100, 1):
        # print(i, val[i])
# rq2 = d2.getQueueStatus()
# print('rq2= ', rq2)   

''' lt1865 read'''   
# NUM = 1000   
# d2.purge() 
# val = d2.read(NUM)
# while(1):
    # for i in range(0,NUM, 2):
        # print(i, val[i], end=', ')
        # print(val[i+1], end=', ')
        # print((val[i]*256 + val[i+1])*5/65535)
    # d2.purge()
    # val = d2.read(NUM)
    # print('')
''' '''    
    
# d2.purge() 
# val = d2.read(2)
# while(1):
    # val = d2.read(2)
    # print(val[0], end=', ')
    # print(val[1], end=', ')
    # print((val[0]*256 + val[1])*5/65535)
    # d2.purge() 
   
''' test tx queue'''
# rq = d2.getQueueStatus()
# print('rq1= ', rq)

# if rq > 0 :
    # d2.purge()
    # print(d2.getQueueStatus())
    # val = d2.read(rq)
    # print('val= ', val[0])
    # print('val= ', val[1])
    # print('val= ', val[2])
    # print(d2.getQueueStatus())

# print((val[0]*256+val[1])*5.0/65535)
# d2.write(READ_STOP)
''' '''