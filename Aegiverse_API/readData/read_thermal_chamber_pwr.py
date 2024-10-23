import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

file_name = r'H:\我的雲端硬碟\工作相關\PUMP溫循量測\20241023_pump test_thermal_chamber.csv'
file_name = os.path.normpath(file_name)
print(file_name)
Var = pd.read_csv(file_name, comment='#', skiprows=0, chunksize=None, sep=',')
date = np.array(Var['data'])
chamber_T = np.array(Var['T1'])
# 將 chamber_T 陣列中的每個值重複 300 次
chamber_T = np.repeat(chamber_T, 300)
print('len(chamber_T): ', len(chamber_T))
# 平移 chamber_T
shift = 1  # 設定要平移的點數
# 在平移後，保留原始值的第一個值，並將 chamber_T 向右平移
# chamber_T_shifted = np.empty_like(chamber_T)  # 創建一個空陣列以儲存平移後的數據
chamber_T_shifted = np.empty(shift)
chamber_T_shifted[:shift] = chamber_T[0]  # 在起始位置補上第一個值
chamber_T = np.concatenate((chamber_T_shifted, chamber_T))
print('len(chamber_T_shifted): ', len(chamber_T))
# plt.figure(1)
# plt.plot( chamber_T, label='chamber_T')
#
# plt.figure(1)
# plt.plot( chamber_T, label='chamber_T')
# plt.show()


file_name_1 = r'H:\我的雲端硬碟\工作相關\PUMP溫循量測\PWR_241023_190059.txt'
file_name_1 = os.path.normpath(file_name_1)
# print(file_name_1)
Var = pd.read_csv(file_name_1, comment='#', skiprows=0, chunksize=None, sep='\t')
current = np.array(Var['Current(A)'])
power = np.array(Var['Power(W)'])

# print('len(power): ', len(power))
# plt.figure(1)
# plt.plot( power, label='power')

# 開始繪圖
fig, ax1 = plt.subplots(figsize=(10, 6))
# 繪製第一個 Y 軸 (Tact 和 Tset)
ax1.plot(power, color='b', label='power')
# ax1.plot(Tset, color='g', label='Tset', alpha=0.5)
ax1.set_xlabel('pts')
ax1.set_ylabel('Power supply current (A)')
ax1.tick_params(axis='y')
ax1.legend(loc='upper left')
# 創建第二個 Y 軸 (chamber_T)
ax2 = ax1.twinx()
ax2.plot(chamber_T, color='r', label='Chamber Temperature', linestyle='--')
ax2.set_ylabel('Chamber Temperature (°C)')
ax2.tick_params(axis='y', labelcolor='r')
ax2.legend(loc='upper right')
# ax2.set_ylim(-60, 100)
# 顯示圖表
plt.title('Power supply current and Chamber Temperature over Time')
plt.grid(True)
plt.tight_layout()




plt.show()