import numpy as np
import matplotlib.pyplot as plt

def generate_sine_wave(amp, freq, cycle, period_pts):
    t = [i for i in range(cycle * period_pts)]
    # print(len(t))
    x = amp * np.sin(2 * np.pi * np.array(t) / period_pts)
    return t, x

def SMA(idx, di, window):
    pow = 2**window
    data_reg = np.zeros(pow)
    do_arr = np.empty(0)
    i = 0;
    sum_reg = 0
    for xin in di:
        print('\ni, idx: ',i, idx)
        print('data_reg[idx]: ', data_reg[idx])
        print('xin, sum_reg: ', xin, sum_reg)
        sum_reg += xin - data_reg[idx]
        do = int(sum_reg) >> window
        print('sum_reg: ', sum_reg)
        print('do: ', do)
        data_reg[idx] = xin
        idx = (idx + 1)%pow;
        i+=1
        do_arr = np.append(do_arr, do)
    return do_arr



amp = 8191
cycle = 5
period_pts = 1000
freq = 10e3  # 弦波频率（Hz）

t, x = generate_sine_wave(amp, freq, cycle, period_pts)

idx = 0
window = 11
do = SMA(idx, x, window)
# print(len(x), len(do))

# plt.figure(figsize=(10, 6))
# plt.subplot(2, 1, 1)

plt.plot(t, x, label='1')
plt.plot(t, do, label='2')
# plt.title('Original Signal')
# plt.xlabel('Time (s)')
# plt.ylabel('Amplitude')
plt.legend()
plt.show()