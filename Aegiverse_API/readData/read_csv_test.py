import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_name = '20231006_Allan.txt'
Var = pd.read_csv(file_name, comment='#', skiprows=0, chunksize=None)

time = np.array(Var['time'])
time2 = time[1:]
time = time[0:-1]
fog = Var['fog']
size = len(time)
dt = time2 - time
mean = np.mean(dt)
std = np.std(dt)
print(mean)
print(std)
# print(dt)
# plt.plot(dt)
# plt.show()

