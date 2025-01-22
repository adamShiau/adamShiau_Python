from scipy.signal import firwin, freqz
import matplotlib.pyplot as plt
import numpy as np

# fs = 100e6  # ADC取樣頻率 (100 MHz)
fs = 500e3  # ADC取樣頻率 (500 KHz)
fc = 5e4  # 通帶截止頻率
n = 31  # 濾波器階數，給奇數
b = firwin(n + 1, fc / (fs / 2), pass_zero='lowpass')  # 設計低通濾波器
b_fixed = np.round(b * (2**15)).astype(int)  # 量化為16位（Q15格式）
print(", ".join(map(str, b_fixed)))  # 以Verilog格式輸出

# 檢查頻率響應
w, h = freqz(b, worN=8000)
plt.plot(0.5 * fs * w / np.pi, 20 * np.log10(abs(h)))
plt.title("FIR Filter Frequency Response")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Gain (dB)")
plt.grid()
plt.show()
