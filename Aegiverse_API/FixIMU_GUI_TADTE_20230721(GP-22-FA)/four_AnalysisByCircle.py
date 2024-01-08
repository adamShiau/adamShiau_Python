import sys
# from Nano33 import Nano33
import numpy as np
# from PySide6 import QtWidgets
# #from WidgetsBox import Chart, DataReaderThread, Line
from transformation import Quaternion


# class DataTransfer:
#     def __init__(self, sensor):
#         self.pre_wz = 0
#         std_imu = [0.001, 0.001, 0.001, 0.007, 0.007, 0.007]
#         self.data_reader = DataReaderThread(sensor)
#         self.line1 = Line(max_length=500)
#         self.line2 = Line(max_length=500)
#         self.line3 = Line(max_length=1000)
#         self.line4 = Line(max_length=1000)
#
#         self.my_chart1 = Chart(self.line1.curve, self.line2.curve, self.line3.curve, self.line4.curve)
#         self.my_chart1.show()
#
#         self.wz_list = []
#         self.wz_filter_list = []
#
#         self.myNav = plane_nav()
#         self.myNav_filtered = plane_nav()
#
#     def begin(self):
#         self.data_reader.data_read.connect(self.transfer)
#         self.data_reader.start()
#
#     def transfer(self, data):
#         t = data['time']
#         wz = data['omg'][2]
#         if self.pre_wz == 0:
#             self.pre_wz = wz
#         wz_filtered = (wz * 0.1 + self.pre_wz * 0.9)
#
#         self.pre_wz = wz_filtered.copy()
#         self.wz_list.append(wz)
#         self.wz_filter_list.append(wz_filtered)
#
#         if len(self.wz_list) > 1000:
#             self.wz_list = self.wz_list[1:]
#             self.wz_filter_list = self.wz_filter_list[1:]
#
#         l, b = self.myNav.update(t, wz)
#         self.line1.updateValue(l, b)
#         l2, b2 = self.myNav_filtered.update(t, wz_filtered)
#         self.line2.updateValue(l2, b2)


class plane_nav:
    def __init__(self, vel=1, heading=0, wz_scale=1, deg=1, speed_up=16):
        self.vel = np.array([0, vel, 0])
        self.pos = np.zeros(3)
        self.qut = Quaternion(0, 0, heading)
        self.time = None
        self.sum = 0
        self.count = 0
        self.bias = 0
        self.const = deg
        self.wz_scale = wz_scale
        self.speed_up = speed_up

    def update(self, t, wz, counter=1):
        if self.count == counter:
            dt = (t - self.time) * self.speed_up
            self.qut.rotate(0, 0, np.deg2rad((wz - self.bias) * self.wz_scale + self.const), dt)
            self.pos += self.qut.R_b2l @ self.vel * dt
        elif self.count < counter:
            self.sum += wz
            self.count += 1
            self.bias = self.sum/counter
        self.time = t
        return self.pos[0], self.pos[1]

    def reset(self):
        self.vel = np.array([0, 1, 0])
        self.pos = np.zeros(3)
        self.qut = Quaternion(0, 0, 0)
        self.time = None
        self.sum = 0
        self.count = 0
        self.bias = 0

# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     nano33 = Nano33()
#     dtt = DataTransfer(nano33)
#     dtt.begin()
#
#     sys.exit(app.exec())
