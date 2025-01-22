import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# 設定參數
fs = 100e6  # 取樣頻率 100 MHz
fc = 250e3  # 截止頻率 250 kHz

# 設定濾波器階數
order = 4

# 計算規範化的截止頻率
f_norm = fc / (0.5 * fs)

# 使用 iirfilter 設計低通濾波器，輸出 SOS 格式
sos = signal.iirfilter(N=order, Wn=f_norm, btype='low', ftype='butter', output='sos')

# 輸出 SOS 係數
print("SOS coefficients:")
print(sos)

# 計算頻率響應
w, h = signal.sosfreqz(sos, worN=2000)

# 計算頻率 (Hz)
frequencies = w * fs / (2 * np.pi)

# 畫出頻率響應
plt.figure(figsize=(10, 6))
plt.plot(frequencies, abs(h), 'b')
plt.title(f'Lowpass Filter Frequency Response (Order = {order})')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.grid(True)
plt.xlim(0, fs / 2)
plt.ylim(0, 1.1)
plt.show()
