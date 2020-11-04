import ftd2xx as ft
import time
import matplotlib.pyplot as plt

'''command definition '''
PATTERN1 = chr(53)
PATTERN2 = chr(54)
PATTERN3 = chr(55)
PATTERN4 = chr(56)
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
INTEGRATOR_2_START = chr(63)
INTEGRATOR_2_STOP = chr(64)
INTEGRATOR_3_START = chr(65)
INTEGRATOR_3_STOP = chr(66)
INTEGRATOR_4_START = chr(67)
INTEGRATOR_4_STOP = chr(68)

MODE1 = chr(1)
MODE2 = chr(2)
MODE3 = chr(3)
SET_T1 = chr(4)
SET_T2 = chr(5)
SET_T3 = chr(6)
SET_T4 = chr(7)
'''-----------------------------------'''

'''adc read'''
NUM = 1000 
SPI_NEXT_VALID_NUM = 8165
dt = 20e-3*SPI_NEXT_VALID_NUM #us
size = int(NUM/2)-1
TIME_WAIT = 0.1
idx = 0
data1 = size*[0]
data2 = size*[0]
data3 = size*[0]
data4 = size*[0]
t = size*[0]
for i in range(1,size):
    t[i] = i*dt
ADC_REF_1 = 3.3
ADC_REF_2 = 3.3

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
    
    ''' LED test pattern 
        each pattern blinks different pattern of four LEDs
        PATTERN1 : {0,0,1,1}
        PATTERN1 : {1,1,0,0}
        PATTERN1 : {1,0,1,0}
        PATTERN1 : {0,0,1,0}
    '''
    d2.write(PATTERN1)
    setValue(0)
    time.sleep(0.1)
    d2.write(PATTERN2)
    setValue(0)
    time.sleep(0.1)
    d2.write(PATTERN3)
    setValue(0)
    time.sleep(0.1)
    d2.write(PATTERN4)
    setValue(0)
    time.sleep(0.1)
    
    '''set {mode}, 
        mode: MODE1, MODE2, MODE3
        set once untill mode changed
    '''
    d2.write(MODE1)
    setValue(0)
    
    '''set {Tn value},
        Tn: T1~T4
        the time period = value * 20ns
        *T1 must > T4 otherwise occur weird result
    '''
    d2.write(SET_T1)
    setValue(750) #10us
    d2.write(SET_T2) 
    setValue(2500) #40us
    d2.write(SET_T3)
    setValue(700) #5us
    d2.write(SET_T4)
    setValue(350) #2us
    d2.write(INTEGRATOR_4_START)
    setValue(0)
    time.sleep(0.1)
    d2.write(INTEGRATOR_4_STOP)
    setValue(0)

    '''read ADC1 ch0'''
    # d2.write(READ_ADC1_ch0_START)
    # setValue(0)

    # d2.purge() 
    # val = d2.read(NUM)
    # for i in range(0,NUM, 2):
        # if i >= 2: #remove the first data
            
            # data1[idx] = (val[i]*256 + val[i+1])*ADC_REF_1/65535
            # print(idx, data1[idx])
            # idx = idx + 1
            
    # idx = 0 
    # d2.write(READ_ADC1_ch0_STOP)
    # setValue(0)
    # plt.figure(1)
    # plt.plot(t, data1)
    # time.sleep(TIME_WAIT)
    
    # '''read ADC1 ch1'''
    # d2.write(READ_ADC1_ch1_START)
    # setValue(0)

    # d2.purge() 
    # val = d2.read(NUM)
    # for i in range(0,NUM, 2):
        # if i >= 2: #remove the first data
            
            # data2[idx] = (val[i]*256 + val[i+1])*ADC_REF_1/65535
            # print(idx, data2[idx])
            # idx = idx + 1
            
    # idx = 0 
    # d2.write(READ_ADC1_ch1_STOP)
    # setValue(0)
    # plt.figure(2)
    # plt.plot(t, data2)
    # time.sleep(TIME_WAIT)
    
    # '''read ADC2 ch0'''
    # d2.write(READ_ADC2_ch0_START)
    # setValue(0)

    # d2.purge() 
    # val = d2.read(NUM)
    # for i in range(0,NUM, 2):
        # if i >= 2: #remove the first data
            
            # data3[idx] = (val[i]*256 + val[i+1])*ADC_REF_2/65535
            # print(idx, data3[idx])
            # idx = idx + 1
            
    # idx = 0 
    # d2.write(READ_ADC2_ch0_STOP)
    # setValue(0)
    # plt.figure(3)
    # plt.plot(t, data3)
    # time.sleep(TIME_WAIT)
    
    # '''read ADC2 ch1'''
    
    # d2.write(READ_ADC2_ch1_START)
    # setValue(0)

    # d2.purge() 
    # val = d2.read(NUM)
    # for i in range(0,NUM, 2):
        # if i >= 2: #remove the first data
            
            # data4[idx] = (val[i]*256 + val[i+1])*ADC_REF_2/65535
            # print(idx, data4[idx])
            # idx = idx + 1
            
    # idx = 0 
    # d2.write(READ_ADC2_ch1_STOP)
    # setValue(0)
    # plt.figure(4)
    # plt.plot(t, data4)
    # time.sleep(TIME_WAIT)    
    # plt.show()




