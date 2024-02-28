import numpy as np
from scipy.signal import firwin
'''
# 截止频率为5MHz，采样频率为10MHz（示例采样频率，根据实际情况调整）
cutoff_freq = 1e2
sampling_freq = 5e6

# 设计滤波器
num_taps = 25
fir_coeff = firwin(num_taps, cutoff_freq / (sampling_freq / 2), window='hamming')

# 显示滤波器系数
print("FIR Filter Coefficients:")
print(*fir_coeff, sep=", ")
'''

from scipy.signal import firwin, freqz
import matplotlib.pyplot as plt
import numpy as np

# Sampling rate
fs = 10e3  # 500KSPS

# Cutoff frequency
cutoff = 100  # 100 Hz

# Filter length (number of taps)
num_taps = 25

# Design FIR filter using firwin
# coefficients = firwin(num_taps, cutoff/(fs / 2), fs=fs, pass_zero=True)
coefficients = firwin(num_taps, cutoff, fs=fs, pass_zero=True)
print("FIR Filter Coefficients:")
print(*coefficients, sep=", ")


# Compute frequency response
w, h = freqz(coefficients, worN=8000)
# print(h)
frequencies = w * fs / (2 * np.pi)

# Plot filter frequency response
plt.figure()
# plt.plot(coefficients)
# plt.title('FIR Filter Coefficients')
# plt.xlabel('Tap')
# plt.ylabel('Coefficient Value')


plt.plot(frequencies, 20 * np.log10(abs(h)), 'b')
plt.title('FIR Filter Frequency Response')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [dB]')

plt.grid(True)
plt.show()



