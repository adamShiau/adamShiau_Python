import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_name = '1012_MP1Z.txt'
Var = pd.read_csv(file_name, comment='#', skiprows=0, chunksize=None)

time = np.array(Var['time'])
wx = np.array(Var['wx'])
wy = np.array(Var['wy'])
wz = np.array(Var['wz'])
ax = np.array(Var['ax'])
ay = np.array(Var['ay'])
az = np.array(Var['az'])
time2 = time[1:]
time3 = time[0:-1]
# fog = Var['fog']
size = len(time2)
dt = time2 - time3
mean = np.mean(dt)
std = np.std(dt)
print(mean)
print(std)
# print(dt)
plt.figure(1)
plt.plot(time, wx)
plt.figure(2)
plt.plot(time, wy)
plt.figure(3)
plt.plot(time, wz)
plt.show()

