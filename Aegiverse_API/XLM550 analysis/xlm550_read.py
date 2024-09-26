import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

# file_name = r'H:\共用雲端硬碟\Aegiverse_RD\GP-1Z0 開發\GP-1Z0-00\D4 (filter-test)\allan\20240402_allan\20240402_allan_earthquake.txt'
# file_name = 'XLM550_0830.txt'
file_name = r'D:\github\adamShiau_Python\Aegiverse_API\XLM550_RD_PDf\XLM550_0924_DiracADC_10kohm_100Hz-1.txt'
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
# time = time/3600
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
# plt.figure(1)
# SFA = 2.24042E-05
# SFB = -80.75709061
# ax = ax * SFA + SFB
ax = ax * SF_CODE
# plt.plot(time, ax, label='ax')
# plt.legend()
print('std ax:', np.std(ax))

# plt.figure(2)
# SFA = 2.23992E-05
# SFB = -80.74025289
# ay = ay * SFA + SFB
ay = ay * SF_CODE
# plt.plot(time, ay, label='ay')
# plt.legend()
print('std ay:', np.std(ay))

plt.figure(3)
# SFA = 3.36755E-07
# SFB = -0.0026240
# az = az * SFA + SFB
az = az * SF_CODE
SF_az = 0.72498 # mA/g
Rmeas = 10000 # ohm
az = 4*az/Rmeas*1000/SF_az

plt.plot(time, az, label='az')
plt.legend()
print('std az:', np.std(az))

# plt.figure(4)
# plt.plot(time, Tx, label='Tx')
# plt.legend()
# plt.figure(5)
# plt.plot(time, Ty, label='Ty')
# plt.legend()
plt.figure(6)
plt.plot(time, Tz, label='Tz')
plt.legend()



'''
# 设置窗口大小为 100 秒
window_size = 3000
# 将 az 数据转换为 pandas Series
az_series = pd.Series(az)

# 计算移动平均，窗口大小为 100 秒
# 假设数据采样率为 1Hz，即每秒采集一个数据点，窗口大小为 100 秒
sampling_rate = 1  # 1Hz
window_length = window_size * sampling_rate

az_moving_avg = az_series.rolling(window=window_length, min_periods=1).mean()

# 创建一个图形和轴对象
fig, ax1 = plt.subplots()
# 在第一个 y 轴上绘制 az 数据
ax1.plot(time, az_moving_avg, 'g-', label='az')  # 绿色线条表示 az 数据
ax1.set_xlabel('time(hrs)')          # 设置 x 轴标签
ax1.set_ylabel('volt', color='g')    # 设置左侧 y 轴标签和颜色
ax1.tick_params(axis='y', labelcolor='g')
# 设置 Tz 轴的 y 轴范围
ax1.set_ylim((1.642+5*1e-5)*2, (1.642+11*1e-5)*2)

# 创建第二个 y 轴
ax2 = ax1.twinx()
ax2.plot(time, Tz, 'b-', label='Tz')  # 蓝色线条表示 Tz 数据
ax2.set_ylabel('degree C', color='b')    # 设置右侧 y 轴标签和颜色
ax2.tick_params(axis='y', labelcolor='b')
# 设置 Tz 轴的 y 轴范围
ax2.set_ylim(38.16, 38.22)

plt.title('3.3V vs Tz')

# 添加图例（可选）
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
'''

with open('XLM550_0924_DiracADC_10kohm_100Hz-1_g.txt', 'w') as f:
    # 写入变量名称
    f.write("time,wx,wy,wz,ax,ay,az,Tx,Ty,Tz\n")

    # 写入数据
    for i in range(len(time)):
        f.write(
            f"{time[i]:.3f},{wx[i]:.5f},{wy[i]:.5f},{wz[i]:.5f},{ax[i]:.5f},{ay[i]:.5f},{az[i]:.5f},{Tx[i]:.2f},{Ty[i]:.2f},{Tz[i]:.2f}\n")

print("数据已成功写入 '.txt' 文件。")

plt.legend()
plt.show()
