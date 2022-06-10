#!/usr/bin/env python
# -*- coding:UTF-8 -*-
from __future__ import print_function
import time
import sys
import rosParameters as rosVar
import numpy as np
from pigImuReader import pigImuReader
from imuLib.Connector import Connector
from imuLib.fogParameters import pig_parameters_ros
import rospy
from sensor_msgs.msg import Imu

# gyro output unit selection
DPS = 1
DPH = 2
RPS = 3
unit = None
# t_array = np.empty(0)
# tt_array = np.empty(0)
# w1_array = np.empty(0)
# w2_array = np.empty(0)
# ww1_array = np.empty(0)
# ww2_array = np.empty(0)
# w_array = [np.empty(0), np.empty(0)]


def myCallBack(imudata):
    wx = imudata["NANO33_WX"]
    wy = imudata["NANO33_WY"]
    fog_wz = imudata["PIG_WZ"]
    ax = imudata["ADXL_AX"]
    ay = imudata["ADXL_AY"]
    az = imudata["ADXL_AZ"]
    ros_Imu_publish(wx, wy, fog_wz, ax, ay, az)
    # print(imudata["TIME"], imudata["NANO33_WZ"], imudata["ADXL_AZ"], imudata["PD_TEMP"])


def ros_Imu_publish(wx, wy, wz, ax, ay, az):
    global unit

    if unit == DPS:
        factor = 1
    elif unit == DPH:
        factor = 3600
    elif unit == RPS:
        factor = np.pi/180

    msg = Imu()
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = 'base_link'
    msg.orientation.x = rosVar.ORI_X
    msg.orientation.y = rosVar.ORI_Y
    msg.orientation.z = rosVar.ORI_Z
    msg.orientation.w = rosVar.ORI_W
    msg.orientation_covariance = [rosVar.COV_ORI_XX, rosVar.COV_ORI_XY, rosVar.COV_ORI_XZ,
                                  rosVar.COV_ORI_YX, rosVar.COV_ORI_YY, rosVar.COV_ORI_YZ,
                                  rosVar.COV_ORI_ZX, rosVar.COV_ORI_ZY, rosVar.COV_ORI_ZZ]
    msg.angular_velocity.x = wx * factor
    msg.angular_velocity.y = wy * factor
    msg.angular_velocity.z = wz * factor
    msg.angular_velocity_covariance = [rosVar.COV_W_XX, rosVar.COV_W_XY, rosVar.COV_W_XZ,
                                       rosVar.COV_W_YX, rosVar.COV_W_YY, rosVar.COV_W_YZ,
                                       rosVar.COV_W_ZX, rosVar.COV_W_ZY, rosVar.COV_W_ZZ]
    msg.linear_acceleration.x = ax * 9.8
    msg.linear_acceleration.y = ay * 9.8
    msg.linear_acceleration.z = az * 9.8
    msg.linear_acceleration_covariance = [rosVar.COV_A_XX, rosVar.COV_A_XY, rosVar.COV_A_XZ,
                                          rosVar.COV_A_YX, rosVar.COV_A_YY, rosVar.COV_A_YZ,
                                          rosVar.COV_A_ZX, rosVar.COV_A_ZY, rosVar.COV_A_ZZ]
    pub.publish(msg)


def checkImudata(t, w1, w2):
    global t_array, tt_array, w1_array, ww1_array, w2_array, ww2_array

    if len(t_array) < 30:
        t_array = np.append(t_array, t)
        w1_array = np.append(w1_array, w1)
        w2_array = np.append(w2_array, w2)
    else:
        tt_array = np.append(tt_array, t_array)
        ww1_array = np.append(ww1_array, w1_array)
        ww2_array = np.append(ww2_array, w2_array)
        if len(tt_array) > 1000:
            tt_array = tt_array[30:]
            ww1_array = ww1_array[30:]
            ww2_array = ww2_array[30:]

        print('fog_wz avg: ', np.round(np.average(ww1_array), 4), end=", ")
        print('std: ', np.round(np.std(ww1_array), 4), end=", ")
        print('mems_wz avg: ', np.round(np.average(ww2_array), 4), end=", ")
        print('std: ', np.round(np.std(ww2_array), 4))
        t_array = np.empty(0)
        w1_array = np.empty(0)
        w2_array = np.empty(0)


if __name__ == "__main__":
    global unit
    try:
        print("running myImu.py")
        ser = Connector()
        unit = DPH
        myImu = pigImuReader()
        myImu.isCali_w = sys.argv[2]
        myImu.isCali_a = sys.argv[3]
        myImu.arrayNum = 1
        myImu.setCallback(myCallBack)
        myImu.connect(ser, "/dev/" + sys.argv[1], 230400)
        pig_par = pig_parameters_ros(myImu)
        rospy.init_node('FOG_ROS', disable_signals=True)
        pub = rospy.Publisher('/imu_raw', Imu, queue_size=1)
        myImu.readIMU()
        myImu.start()

    except:
        print("Check if the arguments number are correct!")
        sys.exit()

    try:
        while True:
            time.sleep(.1)
            pass

    except KeyboardInterrupt:
        myImu.isRun = False
        myImu.stopIMU()
        myImu.disconnect()
        myImu.wait()
        # myImu.disconnectIMU()
        # myImu.join()
        print('KeyboardInterrupt success')
