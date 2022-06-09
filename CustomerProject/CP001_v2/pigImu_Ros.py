#!/usr/bin/env python
# -*- coding:UTF-8 -*-
from __future__ import print_function
import time
import sys
import rosParameters as rosVar
import numpy as np
from pigImuReader import pigImuReader, IMU_DATA_STRUCTURE
from imuLib.Connector import Connector
from imuLib import common as cmn
from imuLib.fogParameters import pig_parameters_ros
import rospy
from sensor_msgs.msg import Imu

t_array = np.empty(0)
tt_array = np.empty(0)
w1_array = np.empty(0)
w2_array = np.empty(0)
ww1_array = np.empty(0)
ww2_array = np.empty(0)
w_array = [np.empty(0), np.empty(0)]


def myCallBack(imudata, imuoffset):
    imuoffset["TIME"] = [0]
    imudata = cmn.dictOperation(imudata, imuoffset, "SUB", IMU_DATA_STRUCTURE)
    print(imudata["TIME"], imudata["PIG_WZ"], imudata["ADXL_AZ"], imudata["PD_TEMP"])


'''
def myCallBack(imudata, offset):
    t = imudata["TIME"]
    fog_wz = imudata["FOG_W"] - offset["FOG_OS"]
    wx, wy, wz = [imudata["MEMS_W"][i] - offset["MEMS_W_OS"][i] for i in range(3)]
    ax, ay, az = [imudata["MEMS_A"][i] - offset["MEMS_A_OS"][i] for i in range(3)]
    fog_wz_dph = fog_wz * 3600
    mems_wz_dph = wz * 3600
    # print("%.5f,  %.5f,  %.5f,  %.5f,  %.5f,  %.5f,  %.5f" % (t, fog_wz_dph, wx, wy, ax, ay, az))
    checkImudata(t, fog_wz_dph, mems_wz_dph)
    ros_Imu_publish(wx, wy, fog_wz, ax, ay, az)
'''


def ros_Imu_publish(wx, wy, wz, ax, ay, az):
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
    msg.angular_velocity.x = wx * np.pi / 180
    msg.angular_velocity.y = wy * np.pi / 180
    msg.angular_velocity.z = wz * np.pi / 180
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


"""
def checkImudata(t, w1, w2):
    global w_array

    w_array[0] = np.append(w_array[0], w1)
    w_array[1] = np.append(w_array[1], w2)
    if len(w_array[0]) > 100:
        w_array[0] = w_array[0][1:]
        w_array[1] = w_array[1][1:]

    print(len(w_array[0]), end=", ")
    print('fog_wz avg: ', np.round(np.average(w_array[0]), 4), end=", ")
    print('std: ', np.round(np.std(w_array[0]), 4), end=", ")
    print('mems_wz avg: ', np.round(np.average(w_array[1]), 4), end=", ")
    print('std: ', np.round(np.std(w_array[1]), 4))
"""

if __name__ == "__main__":
    try:
        print("running myImu.py")
        ser = Connector()

        # par_manager = cmn.parameters_manager("parameters_SP9.json", INIT_PARAMETERS, 1)
        # initPara = par_manager.check_file_exist()
        myImu = pigImuReader(boolCalia=sys.argv[2], boolCaliw=sys.argv[3])
        pig_par = pig_parameters_ros(myImu)
        myImu.arrayNum = 1
        myImu.setCallback(myCallBack)
        myImu.connect(ser, "/dev/" + sys.argv[1], 230400)

        rospy.init_node('FOG_ROS', disable_signals=True)
        pub = rospy.Publisher('/imu_raw', Imu, queue_size=1)
        myImu.readIMU()
        myImu.start()

        # myImu = pigImuReader("/dev/" + sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
        # myImu.setCallback(myCallBack)
        # myImu.connectIMU()
        # rospy.init_node('FOG_ROS', disable_signals=True)
        # pub = rospy.Publisher('/imu_raw', Imu, queue_size=1)
        # myImu.start()
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
