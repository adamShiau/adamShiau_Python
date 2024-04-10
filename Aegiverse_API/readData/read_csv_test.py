import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

file_name = r'H:\共用雲端硬碟\Aegiverse_RD\GP-1Z0 開發\GP-1Z0-00\D4 (filter-test)\allan\20240402_allan\20240402_allan_earthquake.txt'
file_name = os.path.normpath(file_name)
print(file_name)
Var = pd.read_csv(file_name, comment='#', skiprows=0, chunksize=None)

time = np.array(Var['time'])
# wx = np.array(Var['wx'])
# wy = np.array(Var['wy'])
wz = np.array(Var['fog'])
# ax = np.array(Var['ax'])
# ay = np.array(Var['ay'])
# az = np.array(Var['az'])
pd_temp = np.array(Var['T'])
last = 4374000
# wz = wz[0:last]
# time = time[0:last]
# pd_temp = pd_temp[0:last]
# data = np.vstack([time, wz, pd_temp]).T
# np.savetxt('20240402_allan.txt', data, "%.3f,%.5f,%.1f")

# int_wz = np.cumsum(wz)
# mean_wz = np.mean(wz)
# print(mean_wz)
# wz2 = wz - mean_wz
# int_wz2 = np.cumsum(wz2)

# print(len(wz))
# print(len(int_wz))
plt.figure(1)
plt.plot(time, wz)
# plt.plot(wz)
# plt.figure(2)
# plt.plot(time, pd_temp)
# plt.figure(3)
# plt.plot(time, wz2)
# plt.figure(4)
# plt.plot(time, int_wz2)

'''
time2 = time[1:]
time3 = time[0:-1]
# fog = Var['fog']
size = len(time2)
dt = time2 - time3
mean = np.mean(dt)
std = np.std(dt)
print(mean)
print(std)

wz_size = len(wz)
print(wz_size)
print("1 min")
st = 0
stop = st + 60 * 100
mean_wz = np.mean(wz[st:stop])
print('mean_wz: ', mean_wz)

print("5 min")
st = 0
stop = st + 60 * 5 * 100
mean_wz = np.mean(wz[st:stop])
print('mean_wz: ', mean_wz)

print("10 min")
st = 0
stop = st + 60 * 10 * 100
mean_wz = np.mean(wz[st:stop])
print('mean_wz: ', mean_wz)
'''

# print(dt)
# plt.figure(1)
# plt.plot(time, wx)
# plt.figure(2)
# plt.plot(time, wy)
# plt.figure(3)
# plt.plot(time, wz)
# plt.figure(4)
# plt.plot(time, wz)
plt.show()
