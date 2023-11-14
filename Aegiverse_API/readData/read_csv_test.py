import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

file_name = r'H:\我的雲端硬碟\工作相關\Projects\1_IMU\MP_IMU\data\10-17-2023\MP-1Z-10162023.txt'
file_name = os.path.normpath(file_name)
print(file_name)
Var = pd.read_csv(file_name, comment='#', skiprows=0, chunksize=None)

time = np.array(Var['time'])
wx = np.array(Var['wx'])
wy = np.array(Var['wy'])
wz = np.array(Var['wz'])
ax = np.array(Var['ax'])
ay = np.array(Var['ay'])
az = np.array(Var['az'])
pd_temp = np.array(Var['T'])
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
# print(dt)
# plt.figure(1)
# plt.plot(time, wx)
# plt.figure(2)
# plt.plot(time, wy)
# plt.figure(3)
# plt.plot(time, wz)
# plt.figure(4)
plt.plot(time, wz)
plt.show()
