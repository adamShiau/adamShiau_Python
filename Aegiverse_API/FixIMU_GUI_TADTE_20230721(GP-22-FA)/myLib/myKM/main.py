from time import sleep

import numpy as np
import myLib.myKM.transformation as tf

from myLib.myKM.KalmanFilter import EKF


class Driving:
    def __init__(self):
        std_imu = [0.001, 0.001, 0.001, 0.007, 0.007, 0.007]
        self.vrs = EKF()
        self.vrs.setInit(std_imu)
        self.time = 0
        self.vel_b = np.array([0, 10, 0])
        self.pos = np.deg2rad([25.013035, 121.2220388, 20.13])

    def SetPosLatLong(self, latitude, longitude):
        self.pos = np.deg2rad([latitude, longitude, 20.13])


    def run(self, t, omg, acc):
        if self.time > 0:
            dt = t - self.time
            rad_omg = np.deg2rad(omg)
            self.vrs.run(dt, rad_omg, np.array(acc))
            self.mechanization(dt)
        self.time = t

    def mechanization(self, dt):
        #print(dt)
        # 給定初始位置、速度、姿態
        my_lat0, my_lon0, my_hei0 = self.pos
        # 給定初始參數
        rm = tf.meridian_radius(my_lat0)
        rn = tf.normal_radius(my_lat0)
        inv_d = np.array([[0, 1 / (rm + my_hei0), 0],
                          [1 / (rn + my_hei0) / np.cos(my_lat0), 0, 0],
                          [0, 0, 1]])
        disp = inv_d @ (self.vrs.qut.R_b2l @ self.vel_b) * dt
        # 位移→位置
        self.pos = self.pos + disp
        #print(self.pos)

    def setVelocity(self, velocity):
        self.vel_b[1] = velocity/3.6

    def getPosition(self):
        return np.rad2deg(self.pos)

    def getAngle(self):
        return self.vrs.qut.ori[2] * 180 / 3.14159


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    my_drive = Driving()
    my_time = 0
    while True:
        my_time += 0.01
        my_omg = [0.5, 0.1, 0.2]
        my_acc = [0, 0, 1]
        my_drive.run(my_time, my_omg, my_acc)
        print(my_drive.getPosition())
        sleep(0.01)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
