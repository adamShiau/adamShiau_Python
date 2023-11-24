import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
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


if __name__ == "__main__":
    file_name = r'H:\我的雲端硬碟\工作相關\Common\GUI EXE\MP_12_RD\original.txt'
    file_name = os.path.normpath(file_name)
    print(file_name)
    Var = pd.read_csv(file_name, comment='#', skiprows=0, chunksize=None)
    time1 = np.array(Var['time'])
    wz1 = np.array(Var['wz'])*3600

    file_name = r'H:\我的雲端硬碟\工作相關\Common\GUI EXE\MP_12_RD\filter.txt'
    file_name = os.path.normpath(file_name)
    print(file_name)
    Var = pd.read_csv(file_name, comment='#', skiprows=0, chunksize=None)

    time2 = np.array(Var['time'])
    wz2 = np.array(Var['wz']) * 3600
    plt.subplot(2, 1, 1)
    plt.plot(time1, wz1, label='Original Signal')
    plt.plot(time2, wz2, label='Filter Signal')

    plt.legend()
    plt.grid()

    plt.subplot(2, 1, 2)

    # freq_filtered, spectrum_filtered = signal.periodogram(filtered_signal, fs=sampling_freq)
    freq_original, spectrum_original = signal.periodogram(wz1, fs=100)
    freq_filtered, spectrum_filtered = signal.periodogram(wz2, fs=100)
    # plt.semilogy(freq_original, spectrum_original, label='Original Spectrum')
    # plt.semilogy(freq_filtered, spectrum_filtered, label='Filtered Spectrum')
    plt.plot(freq_original, spectrum_original, label='Original Spectrum')
    plt.plot(freq_filtered, spectrum_filtered, label='Filtered Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid()

    plt.show()
