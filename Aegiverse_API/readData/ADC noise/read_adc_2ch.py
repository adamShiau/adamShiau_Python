import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 讀取 CSV 檔案
file_path = r'C:\Users\ami73\Desktop\LGSM_FPGA\output_files'
file_name = 'adc_adcFir-2'
file_ext = '.csv'

# 組合完整檔案路徑
full_file_path = os.path.join(file_path, file_name + file_ext)
print(full_file_path)

if not os.path.exists(full_file_path):
    raise FileNotFoundError(f"File not found: {full_file_path}")

# 讀取特定範圍數據
cols_to_read = ["A", "B", "Q"]  # A: time, B: adc1, Q: adc2

data = pd.read_csv(full_file_path, usecols=[0, 1, 16], skiprows=7, nrows=8000, names=["time", "adc1", "adc2"])

# 轉換時間單位（假設 time 單位是 10ns）
time = data["time"] * 10e-9
adc1 = data["adc1"]
adc2 = data["adc2"]

print(len(time))
print('ADC1_std: ', round(np.std(adc1), 3))
print('ADC2_std: ', round(np.std(adc2), 3))

# 繪製 ADC1 圖表
plt.figure(figsize=(10, 6))
plt.plot(time, adc1, label='ADC1')
plt.title('ADC1 Values Over Time')
plt.xlabel('Time (s)')
plt.ylabel('ADC Values')
plt.legend()
plt.grid(True)

# 繪製 ADC2 圖表
plt.figure(figsize=(10, 6))
plt.plot(time, adc2, label='ADC2')
plt.title('ADC2 Values Over Time')
plt.xlabel('Time (s)')
plt.ylabel('ADC Values')
plt.legend()
plt.grid(True)

# 顯示圖形
plt.show()
