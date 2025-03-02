import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 讀取 CSV 檔案
file_path = r'C:\Users\ami73\Desktop\IRIS_FPGA'
file_name = 'ADC_3 comp reg_adc3_sync_0227-2'
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
time = data["time"]
adc1 = data["adc1"]
adc2 = data["adc2"]

print(len(time))
print('ADC1_std: ', round(np.std(adc1), 3))
print('ADC2_std: ', round(np.std(adc2), 3))

# 繪製 ADC1 圖表
plt.figure(figsize=(10, 6))
plt.plot(time * 10e-9, adc1, label='ADC1')
plt.title('ADC1 Values Over Time')
plt.xlabel('Time (s)')
plt.ylabel('ADC Values')
plt.legend()
plt.grid(True)

# 繪製 ADC2 圖表
plt.figure(figsize=(10, 6))
plt.plot(time * 10e-9, adc2, label='ADC2')
plt.title('ADC2 Values Over Time')
plt.xlabel('Time (s)')
plt.ylabel('ADC Values')
plt.legend()
plt.grid(True)

# 取樣頻率
sampling_interval = 10e-9  # 10 ns
sampling_rate = 1 / sampling_interval

# FFT 分析
fft_adc1 = np.fft.fft(adc1)
fft_adc2 = np.fft.fft(adc2)

frequencies_adc1 = np.fft.fftfreq(len(adc1), d=sampling_interval)
frequencies_adc2 = np.fft.fftfreq(len(adc2), d=sampling_interval)

magnitude_adc1 = np.abs(fft_adc1) / len(adc1)
magnitude_adc2 = np.abs(fft_adc2) / len(adc2)

# 過濾正頻率
positive_freqs_adc1 = frequencies_adc1 > 0
positive_freqs_adc2 = frequencies_adc2 > 0

# 繪製頻譜圖
plt.figure(figsize=(12, 6))
plt.plot(frequencies_adc1[positive_freqs_adc1], magnitude_adc1[positive_freqs_adc1],
         label='ADC1', color='red')
plt.plot(frequencies_adc2[positive_freqs_adc2], magnitude_adc2[positive_freqs_adc2],
         label='ADC2', color='blue')
plt.title('Frequency Spectrum of ADC Signals')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.legend()
plt.grid()

# 顯示圖形
plt.show()
