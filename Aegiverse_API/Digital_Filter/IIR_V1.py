from scipy.signal import iirfilter, sosfreqz
import matplotlib.pyplot as plt
import numpy as np

# IIR 濾波器設計參數
fs = 100e6  # 採樣頻率
fc = 250e3  # 截止頻率
f_norm = fc / (fs / 2)  # 規範化頻率

# 設計 IIR 濾波器（Butterworth 為例）
sos = iirfilter(N=4, Wn=f_norm, btype='low', ftype='butter', output='sos')

# 輸出 SOS 係數
print("SOS coefficients:")
print(sos)

# 頻率響應
w, h = sosfreqz(sos, fs=fs)
plt.semilogx(w, 20 * np.log10(abs(h)))
plt.title('IIR Filter Frequency Response')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [dB]')
plt.grid(which='both', linestyle='--', linewidth=0.5)
plt.axvline(fc, color='red')  # 截止頻率
plt.show()
