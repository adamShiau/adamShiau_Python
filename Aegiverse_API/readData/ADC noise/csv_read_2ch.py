import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 讀取 CSV 檔案
file_path = r'D:\github\myKicad\prj\IRIS\testing\IRIS ADC noise'
file_name = 'ADC_FIR_2CH_3'
file_ext = '.csv'

# 組合完整檔案路徑
full_file_path = os.path.join(file_path, file_name + file_ext)
print(full_file_path)

if not os.path.exists(full_file_path):
    raise FileNotFoundError(f"File not found: {full_file_path}")

# 檢查文件是否有標題行並正確讀取
data = pd.read_csv(full_file_path, header=0)  # 假設第一行是標題，跳過它

# 確保列名正確
data.columns = ["time", "adc1", "adc2"]
# print(data["time"] )

# 提取數據
time = data["time"] * 10e-9  # 時間，單位轉為 ns
adc1 = data["adc1"]
adc2 = data["adc2"]
print(len(time))
print('ADC1_std: ', round(np.std(adc1), 3))
print('ADC2_std: ', round(np.std(adc2), 3))


# Plot for ADC1
plt.figure(figsize=(10, 6))
plt.plot(time, adc1, label='ADC1')
# 添加標籤與圖例
plt.title('ADC Values Over Time')
plt.xlabel('Time (s)')
plt.ylabel('ADC Values')
plt.legend()
plt.grid(True)

# Plot for ADC1
plt.figure(figsize=(10, 6))
plt.plot(time, adc2, label='ADC2')
plt.title('ADC Values Over Time')
plt.xlabel('Time (s)')
plt.ylabel('ADC Values')
plt.legend()
plt.grid(True)



# 顯示圖形
plt.show()
