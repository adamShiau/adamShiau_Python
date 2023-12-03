# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


class kalman_1D:

    def __init__(self, x0=0, p0=0, Q=1, R=1):
        self.__x = x0
        self.__p = p0
        self.__kal_Q = Q
        self.__kal_R = R
        logger.debug("init Q = %d", self.kal_Q)
        logger.debug("init R = %d", self.kal_R)

    @property
    def kal_Q(self):
        return self.__kal_Q

    @kal_Q.setter
    def kal_Q(self, Q):
        self.__kal_Q = Q
        # print("set kal_Q = ", Q)

    @property
    def kal_R(self):
        return self.__kal_R

    @kal_R.setter
    def kal_R(self, R):
        self.__kal_R = R
        # print("set kal_R = ", R)

    def update(self, z):
        k = self.__p / (self.__p + self.__kal_R)
        x = self.__x + k * (z - self.__x)
        p = (1 - k) * self.__p
        self.predict(x, p)
        return x

    def predict(self, x, p):
        self.__x = x
        self.__p = p + self.__kal_Q


class moving_average:
    def __init__(self, size):
        self.__sum = 0
        self.__data_arr = np.zeros(size)
        self.__ptr = 0

    def update(self, z):
        self.__data_arr[self.__ptr] = z
        self.__sum = np.sum(self.__data_arr)
        self.__ptr += 1
        if self.__ptr == len(self.__data_arr):
            self.__ptr = 0
        mv = self.__sum / len(self.__data_arr)
        # print(self.__ptr-1, end=", ")
        # print(self.__data_arr, end=", ")
        # print(self.__sum)
        return mv


if __name__ == "__main__":
    # 產生測試訊號
    sampling_freq = 100
    t = np.linspace(0, 1, sampling_freq, endpoint=False)
    frequency_of_interest = 2.16  # 假設要測試的訊號頻率
    test_signal = np.sin(2 * np.pi * frequency_of_interest * t)

    # 設計濾波器
    # butter
    # cutoff_frequency = 100  # 假設設計的濾波器截止頻率
    # normalized_cutoff = cutoff_frequency / (0.5 * sampling_freq)
    # b, a = signal.butter(4, normalized_cutoff, btype='low')
    kal = kalman_1D()
    kal.kal_Q = 1
    kal.kal_R = 50

    # 濾波處理
    # filtered_signal = signal.filtfilt(b, a, test_signal)
    filtered_signal = np.empty(0)

    for i in test_signal:
        # filtered_signal = mv.update(test_signal)
        # filtered_signal = np.append(filtered_signal, mv.update(i))
        filtered_signal = np.append(filtered_signal, kal.update(i))

    # 計算濾波前後信號的能量
    energy_original = np.sum(np.square(test_signal))
    energy_filtered = np.sum(np.square(filtered_signal))

    # 計算衰減值
    attenuation = 10 * np.log10(energy_filtered / energy_original)

    print(f"Attenuation at cutoff frequency: {attenuation:.2f} dB")
    print(energy_filtered, energy_original, energy_filtered/energy_original)

    # 繪製波形
    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.plot(t, test_signal, label='Original Signal')
    plt.plot(t, filtered_signal, label='Filtered Signal')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid()

    # 繪製頻譜
    plt.subplot(2, 1, 2)
    freq_original, spectrum_original = signal.periodogram(test_signal, fs=sampling_freq)
    freq_filtered, spectrum_filtered = signal.periodogram(filtered_signal, fs=sampling_freq)

    # plt.semilogy(freq_original, spectrum_original, label='Original Spectrum')
    # plt.semilogy(freq_filtered, spectrum_filtered, label='Filtered Spectrum')
    plt.plot(freq_original, spectrum_original, label='Original Spectrum')
    plt.plot(freq_filtered, spectrum_filtered, label='Filtered Spectrum')
    # plt.axvline(x=cutoff_frequency, color='red', linestyle='--', label='Cutoff Frequency')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()

    pass
