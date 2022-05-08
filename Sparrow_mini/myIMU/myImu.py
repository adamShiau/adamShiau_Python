#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import time
import numpy as np
from imuLib.ImuReader import ImuReader
import matplotlib.pyplot as plt
import numpy

t_array = np.empty(0)
w_array = np.empty(0)
tt_array = np.empty(0)
ww_array = np.empty(0)


def getImuData(imudata):
    # global data
    # data = imudata

    t = imudata["TIME"]
    fog_wz = imudata["FOG_W"]
    wx, wy = imudata["MEMS_W"]
    ax, ay, az = imudata["MEMS_A"]
    # print("%.5f,  %d,  %.5f,  %.5f,  %.5f,  %.5f,  %.5f" % (t, fog_wz, wx, wy, ax, ay, az))
    checkImudata(t, fog_wz)


def checkImudata(t, w):
    global t_array, w_array, tt_array, ww_array

    if len(t_array) < 30:
        t_array = np.append(t_array, t)
        w_array = np.append(w_array, w)
    else:
        tt_array = np.append(tt_array, t_array)
        ww_array = np.append(ww_array, w_array)
        if len(tt_array) > 1000:
            tt_array = tt_array[30:]
            ww_array = ww_array[30:]

        print('step avg: ', np.round(np.average(ww_array), 4), end=', ')
        print('stdev: ', np.round(np.std(ww_array), 4))
        t_array = np.empty(0)
        w_array = np.empty(0)


if __name__ == "__main__":
    print("running myImu.py")
    # old_time = time.perf_counter()
    myImu = ImuReader()
    myImu.connectIMU()
    myImu.setCallback(getImuData)
    myImu.start()
    try:
        while True:
            time.sleep(.1)
            pass

    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.disconnectIMU()
        myImu.join()
        myImu.disconnectUSB()
        print('KeyboardInterrupt success')
