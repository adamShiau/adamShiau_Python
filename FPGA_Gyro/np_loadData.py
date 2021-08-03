import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt

print(sys.path)
Var = np.loadtxt('0802_H.txt', comments='#', delimiter=',')
print(Var.shape)
print(Var[1,1])
t = Var[:,0]
# t2 = t[1:]
# t = t[0:len(t2)]
# t3 = (t2-t)*1e3
open = Var[:,1]
close = Var[:,2]
open_max = round(np.max(open)*1000, 2)
open_min = round(np.min(open)*1000, 2)
open_avg = round(np.mean(open)*1000, 2)
open_std = round(np.std(open)*1000, 2)
close_max = round(np.max(close), 2)
close_min = round(np.min(close), 2)
close_avg = round(np.mean(close), 2)
close_std = round(np.std(close), 2)

print('t_end: ', t[-1])
print('open_max(mV): ', open_max)
print('open_min(mV): ', open_min)
print('open_avg(mV): ', open_avg)
print('open_std(mV): ', open_std, end='\n\n')
print('close_max(LSB): ', close_max)
print('close_min(LSB): ', close_min)
print('close_avg(LSB): ', close_avg)
print('close_std(LSB): ', close_std, end='\n\n')

# plt.plot(t,open = '*')
plt.figure(1)
plt.plot(t, open)
plt.figure(2)
plt.plot(t, close)
# plt.figure(3)
# plt.plot(t, SRS_wz)
# plt.figure(4)
# plt.plot(t, PP_wz)
# plt.show()

# print(t[-1])