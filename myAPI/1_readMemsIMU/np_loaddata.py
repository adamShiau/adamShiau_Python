import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt

NAME = '0613_2' + '.txt'

Var = np.loadtxt(NAME, comments='#', delimiter=',', skiprows=0)

# wz = Var[:, 1]
# thetaz = wz.cumsum()
# print(len(wz), len(thetaz))
# print(wz, thetaz)

# t1 = time.perf_counter()
Var = pd.read_csv(NAME, comment='#')
Var.columns = ['time', 'wz', 'wx', 'wy', 'ax', 'ay', 'az']
wz = Var.wz
# print(Var)
# print(Var.cumsum())
x = [1,2,3,4,5,6]
# print(x)
# print(wz)
# print(wz.max())
# print(wz.min())
# print(wz.mean())
# print(wz.sum())
# print(wz.cumsum())

data = pd.date_range('20220614', periods=6)
d = pd.Series(x, index=data)
# print(d)

# Var.plot()
# plt.show()
# print(type(d))
# print(d.iloc[0])
# s = pd.Series(0, index=d)
# print(s)
# t2 = time.perf_counter()
# dt = (t2 - t1) * 1e3
#
# print(dt)
# times = Var.time
# t1 = time.perf_counter()
# for i in times:
#     d = i*i
# t2 = time.perf_counter()
# dt = (t2 - t1) * 1e3
# print('time3: ', dt)
# print(type(times))
# print(len(Var.time))

s = pd.Series([1,2,3,4,5])
d = pd.Series(6)
m = pd.concat([s, d])
print(s)
print(d)
print(m)