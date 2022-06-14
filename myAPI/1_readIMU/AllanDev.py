import numpy as np
import math
import matplotlib.pyplot as plt
import time
import pandas as pd


def cal_oadev(data, rate, tauArray):
    tau0 = 1 / rate  # Calculate the sampling period
    dataLength = len(data)  # Calculate N, data length
    dev = np.array([])  # Create empty array to store the output.
    actualTau = np.array([])
    for i in tauArray:
        n = math.floor(i / tau0)  # Calculate n given a tau value.
        if n == 0:
            n = 1  # Use minimal n if tau is less than the sampling period.
        currentSum = 0  # Initialize the sum
        # print('n: ', n)
        tlp_s = time.perf_counter()
        for j in range(0, dataLength - 2 * n):
            currentSum = (data[j + 2 * n] - 2 * data[j + n] + data[j]) ** 2 + currentSum  # Cumulate the sum squared
            # currentSum += np.square((data[j + 2 * n] - 2 * data[j + n] + data[j]))
        tlp_e = time.perf_counter()
        # print('time_n= ', n, end=', ')
        # print((tlp_e-tlp_s)*1e3)
        devAtThisTau = currentSum / (2 * n ** 2 * tau0 ** 2 * (dataLength - 2 * n))  # Divide by the coefficient
        dev = np.append(dev, np.sqrt(devAtThisTau))
        actualTau = np.append(actualTau, n * tau0)
    return actualTau, dev  # Return the actual tau and overlapped Allan deviation


NAME = '0402_noKAL' + '.txt'
SF_A = 0.00295210451588764 * 1.02 / 2
SF_B = -0.00137052112589694
dataRate = 100

t1 = time.perf_counter()

Var = np.loadtxt(NAME, comments='#', delimiter=',', skiprows=0)
wz = Var[:, 1]

# Var = pd.read_csv(NAME, comment='#')
# Var.columns = ['time', 'wz', 'wx', 'wy', 'ax', 'ay', 'az']
# Var.columns = ['time', 'wz', 'wx', 'wy']
# wz = np.array(Var.wz)
# print(type(wz))
# print(wz)
t2 = time.perf_counter()

thetaz = (wz.cumsum() / dataRate)  # degree
# thetaz = tuple(wz.cumsum() / dataRate)  # degree
# print(type(thetaz))
# print(thetaz)
t3 = time.perf_counter()
dataLength = len(thetaz)

print('load done')
print('N =', dataLength)

tau0 = 1 / dataRate
'''
tau = m*tau0
m < (N-1)/2
for N = 17697570
m < 8848785 = 8e6
'''
tauArray = np.array([tau0, 3 * tau0, 5 * tau0, 10 * tau0, 30 * tau0, 50 * tau0,
                     100 * tau0, 300 * tau0, 500 * tau0, 1000 * tau0, 3e3 * tau0,
                     5000 * tau0, 10000 * tau0, 3e4 * tau0, 50000 * tau0, 100000 * tau0,
                     5e5 * tau0, 1e6 * tau0, 2e6 * tau0, 8e6 * tau0])

x, y = cal_oadev(thetaz, dataRate, tauArray)
t4 = time.perf_counter()

print('read: ', (t2 - t1) * 1e3)
print('cumsum: ', (t3 - t2) * 1e3)
print('allen: ', (t4 - t3) * 1e3)

y = y * 3600

plt.loglog(x, y, linestyle='-', marker='*')
plt.xlabel('s')
plt.ylabel('Degree/hour')
plt.grid()
plt.show()
