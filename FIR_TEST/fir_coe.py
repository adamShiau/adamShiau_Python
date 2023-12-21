import numpy as np
from scipy.signal import firwin

# 截止频率为5MHz，采样频率为10MHz（示例采样频率，根据实际情况调整）
cutoff_freq = 40e6
sampling_freq = 100e6

# 设计滤波器
num_taps = 32
fir_coeff = firwin(num_taps, cutoff_freq / (sampling_freq / 2), window='hamming')

# 显示滤波器系数
print("FIR Filter Coefficients:")
print(*fir_coeff, sep=", ")