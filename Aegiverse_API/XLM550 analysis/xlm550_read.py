import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# file_name = r'H:\共用雲端硬碟\Aegiverse_RD\GP-1Z0 開發\GP-1Z0-00\D4 (filter-test)\allan\20240402_allan\20240402_allan_earthquake.txt'
file_name = 'XLM550_0830.txt'
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
Tx = np.array(Var['Tx'])
Ty = np.array(Var['Ty'])
Tz = np.array(Var['Tz'])
# last = 4374000
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
SF_CODE = 2.048/2**23
plt.figure(1)
SFA = 2.24042E-07
SFB = -80.75709061
ax = ax * SFA + SFB
# ax = ax * SF_CODE
plt.plot(time, ax, label='ax')
plt.legend()
print('std ax:', np.std(ax))

plt.figure(2)
SFA = 2.23992E-07
SFB = -80.74025289
ay = ay * SFA + SFB
# ay = ay * SF_CODE
plt.plot(time, ay, label='ay')
plt.legend()
print('std ay:', np.std(ay))

plt.figure(3)
SFA = 2.29606E-07
SFB = -82.76352775
az = az * SFA + SFB
# az = az * SF_CODE
plt.plot(time, az, label='az')
plt.legend()
print('std az:', np.std(az))


plt.legend()
# plt.show()

with open('xlm550_0830_fix_0.001-on-X.txt', 'w') as f:
    # 写入变量名称
    f.write("time,wx,wy,wz,ax,ay,az,Tx,Ty,Tz\n")

    # 写入数据
    for i in range(len(time)):
        f.write(
            f"{time[i]:.3f},{wx[i]:.5f},{wy[i]:.5f},{wz[i]:.5f},{ax[i]:.5f},{ay[i]:.5f},{az[i]:.5f},{Tx[i]:.2f},{Ty[i]:.2f},{Tz[i]:.2f}\n")

print("数据已成功写入 '.txt' 文件。")
