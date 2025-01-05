import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 讀取 CSV 檔案
file_path = r'D:\github\myKicad\prj\EP\IRIS ADC noise'
file_name = 'ADC_2ch_ch1_PD_GND_2k'
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

# 提取數據
time = data["time"] * 10  # 時間，單位轉為 ns
adc1 = pd.to_numeric(data["adc1"], errors='coerce')  # 確保轉換為數字
adc2 = pd.to_numeric(data["adc2"], errors='coerce')  # 確保轉換為數字

# 去掉無效數據
adc1 = adc1.dropna()
adc2 = adc2.dropna()

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
# plt.xlim(0, 10e6)  # 顯示 10 MHz 以下
plt.show()
