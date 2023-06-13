import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

filename = '5.txt'

Var = pd.read_csv(filename, comment='#', skiprows=0, chunksize=None)
time = np.array(Var['time'])
fog = np.array(Var['fog'][0:-1]) * 1
fog = fog.astype(int)
fog2 = np.empty(0)
# for x in fog:
#     byte0 = (x >> 24) & 0xFF
#     byte1 = (x >> 16) & 0xFF
#     byte2 = (x >> 8) & 0xFF
#     byte3 = (x >> 0) & 0xFF
    # if x != -2147483648:
    #     fog2 = np.append(fog2, x)
    # if x == -2147483648:
    #     x = 0
    # fog2 = np.append(fog2, x)
    # print(hex(byte0), end=', ')
    # print(hex(byte1), end=', ')
    # print(hex(byte2), end=', ')
    # print(hex(byte3), end=', ')
    # print(byte0 << 24 | byte1 << 16 | byte2 << 8 | byte3, end=', ')
    # print(x)

# for x in fog[0:60000]:
#     byte0 = (x >> 24) & 0xFF
#     byte1 = (x >> 16) & 0xFF
#     byte2 = (x >> 8) & 0xFF
#     byte3 = (x >> 0) & 0xFF
#     fog2 = np.append(fog2, x)
    # print(hex(byte0), end=', ')
    # print(hex(byte1), end=', ')
    # print(hex(byte2), end=', ')
    # print(hex(byte3), end=', ')
    # print(byte0 << 24 | byte1 << 16 | byte2 << 8 | byte3, end=', ')
    # print(x)
# fog2 = np.append(fog2, byte2 << 8 | byte3)

# byte0 = ~byte0
# byte1 = ~byte1
# byte2 = ~byte2
# byte3 = ~byte3
#
# print(hex(byte0), end=', ')
# print(hex(byte1), end=', ')
# print(hex(byte2), end=', ')
# print(hex(byte3), end=', ')
# print(byte0 << 24 | byte1 << 16 | byte2 << 8 | byte3, end=', ')
# print(x)
# print('\n')

# print(len(fog))
T = np.array(Var['T'])
size = len(time)

plt.figure(1)
plt.plot(time)
plt.xlabel('number', fontsize=10)
plt.ylabel('time [s]', fontsize=10)
plt.figure(2)
plt.plot(fog, '-+')
plt.xlabel('number', fontsize=10)
plt.ylabel('dps', fontsize=10)
# plt.figure(3)
# plt.plot(fog2)
# plt.xlabel('number', fontsize=10)
# plt.ylabel('dps', fontsize=10)
plt.figure(3)
plt.plot(T)
plt.xlabel('number', fontsize=10)
plt.ylabel('degree C', fontsize=10)

# plt.legend(['ext trigger', 'delay'])
# plt.legend(['ext trigger'])
plt.show()
