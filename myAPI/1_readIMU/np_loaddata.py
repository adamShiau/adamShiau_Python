import numpy as np
import time
import pandas as pd

NAME = '0613_2' + '.txt'
t1 = time.perf_counter()
Var = np.loadtxt(NAME, comments='#', delimiter=',', skiprows=0)
t2 = time.perf_counter()
dt = (t2 - t1) * 1e3
shape = np.shape(Var)
print(dt)
print(shape)
# print(Var[:, 0])
# print(Var[-1])

t1 = time.perf_counter()
Var = pd.read_csv(NAME, comment='#')
Var.columns = ['time', 'wx', 'wy', 'wz', 'ax', 'ay', 'az']
# df = pd.DataFrame(Var, columns=['a', 'b', 'c', 'd', 'e', 'f', 'g'])
t2 = time.perf_counter()
dt = (t2 - t1) * 1e3

print(dt)
# print(Var)
print(Var.time[53848])
# print(len(Var.time))
