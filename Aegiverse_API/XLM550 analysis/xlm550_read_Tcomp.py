import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

# file_name = r'H:\共用雲端硬碟\Aegiverse_RD\GP-1Z0 開發\GP-1Z0-00\D4 (filter-test)\allan\20240402_allan\20240402_allan_earthquake.txt'
file_name = 'XLM550_0830.txt'
# file_name = r'D:\github\adamShiau_Python\Aegiverse_API\XLM550_RD_PDf\XLM550_0830.txt'
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


SF_CODE = 2.048/2**23
SFA1 = 1.6646E-07
SFB1 = -0.6
plt.figure(1)

''' for SF temp comp.'''
SF_p0 = 0.742982
SF_p1 = 0.00001983288
SF_p2 = 0.000000156571
SF_p3 = -0.000000001536975

''' for BIAS temp comp.'''
BS_p0 = 1433.1
BS_p1 = 7.581278
BS_p2 = -0.06303523
BS_p3 = 0.0002968801
Tx2 = Tx-30
SF_comp = (SF_p0 + SF_p1*Tx2 + SF_p2*Tx2**2 + SF_p3*Tx2**3)
BS_comp = (BS_p0 + BS_p1*Tx2 + BS_p2*Tx2**2 + BS_p3*Tx2**3)/1000  # mg
# print(SF_comp)

SFA = SFA1*100/SF_comp
SFB = SFB1*100/SF_comp - BS_comp

# plt.plot(Tx, BS_comp, label='BS_comp')
# plt.legend()

# print(SF_comp)
# print(BS_comp)
# print(SFA)
# print(SFB)
ax = ax * SFA + SFB
# ax = ax * SF_CODE
# plt.plot(time, ax, label='ax')
# plt.legend()
print('std ax:', np.std(ax))

'''

plt.figure(2)
# SFA = 2.23992E-05
# SFB = -80.74025289
# ay = ay * SFA + SFB
ay = ay * SF_CODE
plt.plot(time, ay, label='ay')
plt.legend()
print('std ay:', np.std(ay))

plt.figure(3)
# SFA = 2.29606E-05
# SFB = -82.76352775
# az = az * SFA + SFB
az = az * SF_CODE
# az = az*2

plt.plot(time, az, label='az')
plt.legend()
print('std az:', np.std(az))

plt.figure(4)
plt.plot(time, Tx, label='Tx')
plt.legend()
plt.figure(5)
plt.plot(time, Ty, label='Ty')
plt.legend()
plt.figure(6)
plt.plot(time, Tz, label='Tz')
plt.legend()
'''


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

# with open('XLM550_0830_Tcomp.txt', 'w') as f:
#     # 写入变量名称
#     f.write("time,wx,wy,wz,ax,ay,az,Tx,Ty,Tz\n")
#
#     # 写入数据
#     for i in range(len(time)):
#         f.write(
#             f"{time[i]:.3f},{wx[i]:.5f},{wy[i]:.5f},{wz[i]:.5f},{ax[i]:.5f},{ay[i]:.5f},{az[i]:.5f},{Tx[i]:.2f},{Ty[i]:.2f},{Tz[i]:.2f}\n")

print("数据已成功写入 '.txt' 文件。")

plt.legend()
plt.show()
