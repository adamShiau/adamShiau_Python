import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import os

# 讀取 CSV 檔案
file_path = r'D:\github\myKicad\prj\EP\IRIS ADC noise'
file_name = 'ADC_2ch_ch1_PD_GND'
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
adc1 = pd.to_numeric(data["adc1"], errors='coerce').dropna()
adc2 = pd.to_numeric(data["adc2"], errors='coerce').dropna()

# 取樣頻率
sampling_interval = 10e-9  # 10 ns
sampling_rate = 1 / sampling_interval

# Perform FFT analysis for ADC1 and ADC2
fft_adc1 = np.fft.fft(adc1)
frequencies_adc1 = np.fft.fftfreq(len(adc1), d=sampling_interval)
magnitude_adc1 = np.abs(fft_adc1) / len(adc1)

fft_adc2 = np.fft.fft(adc2)
frequencies_adc2 = np.fft.fftfreq(len(adc2), d=sampling_interval)
magnitude_adc2 = np.abs(fft_adc2) / len(adc2)

# Filter for positive frequencies
positive_freqs_adc1 = frequencies_adc1 > 0
positive_freqs_adc2 = frequencies_adc2 > 0

frequencies_adc1_positive = frequencies_adc1[positive_freqs_adc1]
magnitudes_adc1_positive = magnitude_adc1[positive_freqs_adc1]

frequencies_adc2_positive = frequencies_adc2[positive_freqs_adc2]
magnitudes_adc2_positive = magnitude_adc2[positive_freqs_adc2]

# Define threshold values
threshold_value_adc1 = 0.2 * max(magnitudes_adc1_positive)
threshold_value_adc2 = 0.5 * max(magnitudes_adc2_positive)

# Filter frequencies above threshold
filtered_freqs_adc1 = frequencies_adc1_positive[magnitudes_adc1_positive > threshold_value_adc1]
filtered_magnitudes_adc1 = magnitudes_adc1_positive[magnitudes_adc1_positive > threshold_value_adc1]

filtered_freqs_adc2 = frequencies_adc2_positive[magnitudes_adc2_positive > threshold_value_adc2]
filtered_magnitudes_adc2 = magnitudes_adc2_positive[magnitudes_adc2_positive > threshold_value_adc2]

# Find peaks for ADC1 and ADC2
peaks_adc1, _ = find_peaks(filtered_magnitudes_adc1)
peak_freqs_adc1 = filtered_freqs_adc1[peaks_adc1]
peak_magnitudes_adc1 = filtered_magnitudes_adc1[peaks_adc1]

peaks_adc2, _ = find_peaks(filtered_magnitudes_adc2)
peak_freqs_adc2 = filtered_freqs_adc2[peaks_adc2]
peak_magnitudes_adc2 = filtered_magnitudes_adc2[peaks_adc2]

# Calculate base multiples
def calculate_base_multiples(peak_freqs, peak_magnitudes):
    if len(peak_freqs) > 0:
        base_frequency = peak_freqs.min()  # Find the fundamental frequency
        multiples = peak_freqs / base_frequency  # Calculate harmonics
        peak_data = pd.DataFrame({
            'Frequency (MHz)': peak_freqs / 1e6,
            'Magnitude': peak_magnitudes,
            'Base Multiple': multiples.round(3)
        }).round({'Frequency (MHz)': 3, 'Magnitude': 3})
    else:
        peak_data = pd.DataFrame(columns=['Frequency (MHz)', 'Magnitude', 'Base Multiple'])
    return peak_data

# Prepare DataFrames for peaks with base multiples
peak_data_adc1 = calculate_base_multiples(peak_freqs_adc1, peak_magnitudes_adc1)
peak_data_adc2 = calculate_base_multiples(peak_freqs_adc2, peak_magnitudes_adc2)

# Print peak data with base multiples
print("Peak Noise Frequencies for ADC1 (with Base Multiples):")
print(peak_data_adc1)

print("\nPeak Noise Frequencies for ADC2 (with Base Multiples):")
print(peak_data_adc2)

# Combine ADC1 and ADC2 data into a single DataFrame
combined_data = pd.concat([
    peak_data_adc1.add_prefix('ADC1 '),
    peak_data_adc2.add_prefix('ADC2 ')
], axis=1)

# Save the combined data to a single CSV file
output_combined_path = os.path.join(file_path, "FFT_Peak_Data_ADC1_ADC2.csv")
combined_data.to_csv(output_combined_path, index=False)

print(f"Combined peak data for ADC1 and ADC2 saved to: {output_combined_path}")

# Plot for ADC1
plt.figure(figsize=(12, 6))
plt.plot(frequencies_adc1_positive / 1e6, magnitudes_adc1_positive,
         label='Full Spectrum (ADC1)', color='blue', alpha=0.7)
plt.scatter(filtered_freqs_adc1 / 1e6, filtered_magnitudes_adc1,
            label='Filtered Frequencies (ADC1)', color='red', zorder=5)
plt.scatter(peak_freqs_adc1 / 1e6, peak_magnitudes_adc1,
            label='Peaks in Filtered Data (ADC1)', color='green', zorder=10, marker='x')
plt.title('Comparison of Full Spectrum and Filtered Frequencies (ADC1)')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Magnitude')
plt.legend()
plt.grid()

# Plot for ADC2
plt.figure(figsize=(12, 6))
plt.plot(frequencies_adc2_positive / 1e6, magnitudes_adc2_positive,
         label='Full Spectrum (ADC2)', color='blue', alpha=0.7)
plt.scatter(filtered_freqs_adc2 / 1e6, filtered_magnitudes_adc2,
            label='Filtered Frequencies (ADC2)', color='red', zorder=5)
plt.scatter(peak_freqs_adc2 / 1e6, peak_magnitudes_adc2,
            label='Peaks in Filtered Data (ADC2)', color='green', zorder=10, marker='x')
plt.title('Comparison of Full Spectrum and Filtered Frequencies (ADC2)')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Magnitude')
plt.legend()
plt.grid()

plt.show()
