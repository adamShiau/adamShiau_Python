import numpy as np
import matplotlib.pyplot as plt

# 生成弦波
# def generate_sine_wave(freq, duration, sampling_rate):
#     t = np.linspace(0, duration, int(duration * sampling_rate), endpoint=False)
#     x = np.sin(2 * np.pi * freq * t)
#     return t, x

def generate_sine_wave(amp, freq, cycle, period_pts):
    t = [i for i in range(cycle * period_pts)]
    # print(len(t))
    x = amp * np.sin(2 * np.pi * np.array(t) / period_pts)
    return t, x

# 简单移动平均滤波器
def simple_moving_average(data, window_size):
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[window_size:] - cumsum[:-window_size]) / window_size

# 参数设置
# sampling_rate = 1000  # 采样率
# duration = 2  # 信号持续时间（秒）
# frequency = 5  # 弦波频率（Hz）
# window_sizes = [5, 10, 20]  # 不同的窗口大小

amp = 8191
cycle = 5
period_pts = 1000
freq = 10e3  # 弦波频率（Hz）
window_size = 1024

# 生成弦波信号
# t, x = generate_sine_wave(frequency, duration, sampling_rate)

t, x = generate_sine_wave(amp, freq, cycle, period_pts)

# 绘制原始信号
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(t, x)
plt.title('Original Signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')

# 应用不同窗口大小的简单移动平均滤波器并绘制
plt.subplot(2, 1, 2)
plt.plot(t, x, label='Original Signal')

# for window_size in window_sizes:
#     smoothed_signal = simple_moving_average(x, window_size)
#     plt.plot(t[window_size - 1:], smoothed_signal, label=f'SMA (Window Size={window_size})')

smoothed_signal = simple_moving_average(x, window_size)
plt.plot(t[window_size - 1:], smoothed_signal, label=f'SMA (Window Size={window_size})')

plt.title('Smoothed Signal with Simple Moving Average')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.tight_layout()
plt.show()
