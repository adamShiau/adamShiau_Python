import pandas as pd
import numpy as np
from scipy.signal import find_peaks
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

# Perform FFT analysis
fft_adc1 = np.fft.fft(adc1)
fft_adc2 = np.fft.fft(adc2)

frequencies_adc1 = np.fft.fftfreq(len(adc1), d=sampling_interval)
frequencies_adc2 = np.fft.fftfreq(len(adc2), d=sampling_interval)

magnitude_adc1 = np.abs(fft_adc1) / len(adc1)
magnitude_adc2 = np.abs(fft_adc2) / len(adc2)

# Filter for positive frequencies
positive_freqs_adc1 = frequencies_adc1 > 0
positive_freqs_adc2 = frequencies_adc2 > 0

# Extract positive frequencies and magnitudes
frequencies_adc1_positive = frequencies_adc1[positive_freqs_adc1]
magnitudes_adc1_positive = magnitude_adc1[positive_freqs_adc1]

frequencies_adc2_positive = frequencies_adc2[positive_freqs_adc2]
magnitudes_adc2_positive = magnitude_adc2[positive_freqs_adc2]

# Define a threshold
threshold_value = 0.1 * max(magnitudes_adc1_positive)  # Example: 10% of max magnitude
print(threshold_value)

# Filter the data based on the threshold
filtered_freqs_adc1 = frequencies_adc1_positive[magnitudes_adc1_positive > threshold_value]
filtered_magnitudes_adc1 = magnitudes_adc1_positive[magnitudes_adc1_positive > threshold_value]

filtered_freqs_adc2 = frequencies_adc2_positive[magnitudes_adc2_positive > threshold_value]
filtered_magnitudes_adc2 = magnitudes_adc2_positive[magnitudes_adc2_positive > threshold_value]

# Find peaks for filtered ADC1 and ADC2 data
peaks_adc1, _ = find_peaks(filtered_magnitudes_adc1)
peaks_adc2, _ = find_peaks(filtered_magnitudes_adc2)

# Extract peak frequencies and magnitudes
peak_freqs_adc1 = filtered_freqs_adc1[peaks_adc1]
peak_magnitudes_adc1 = filtered_magnitudes_adc1[peaks_adc1]

peak_freqs_adc2 = filtered_freqs_adc2[peaks_adc2]
peak_magnitudes_adc2 = filtered_magnitudes_adc2[peaks_adc2]

# Prepare DataFrames for ADC1 and ADC2 peaks
peak_data_adc1 = pd.DataFrame({
    'Frequency (MHz)': peak_freqs_adc1 / 1e6,
    'Magnitude': peak_magnitudes_adc1
}).round(3)

peak_data_adc2 = pd.DataFrame({
    'Frequency (MHz)': peak_freqs_adc2 / 1e6,
    'Magnitude': peak_magnitudes_adc2
}).round(3)

# Print results for ADC1 and ADC2
print("Peak Noise Frequencies for ADC1:")
print(peak_data_adc1)

# print("\nPeak Noise Frequencies for ADC2:")
# print(peak_data_adc2)

# 繪製頻譜圖
plt.figure(figsize=(12, 6))
# plt.plot(frequencies_adc1[positive_freqs_adc1], magnitude_adc1[positive_freqs_adc1],
#          label='ADC1', color='red')
plt.plot(frequencies_adc1[positive_freqs_adc1], magnitude_adc1[positive_freqs_adc1],
         label='ADC1', color='red')
# plt.plot(frequencies_adc2[positive_freqs_adc2], magnitude_adc2[positive_freqs_adc2],
#          label='ADC2', color='blue')
plt.title('Frequency Spectrum of ADC Signals')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.legend()
plt.grid()
# plt.xlim(0, 10e6)  # 顯示 10 MHz 以下
plt.show()
