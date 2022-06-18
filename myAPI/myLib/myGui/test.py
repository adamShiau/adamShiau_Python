import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import os, sys
from tqdm import tqdm

path = '0618.txt'
# size = os.path.getsize(path)
# print('%s = %d bytes' % (path, size))


t1 = time.perf_counter()
# data = pd.read_csv('0402.txt', sep=r'\s*,\s*', engine='python', nrows=2, skiprows=2)
# data = pd.read_csv(path, sep=r'\s*,\s*', engine='python')
# size = os.path.getsize(path)
# data = pd.read_csv('0616_mems.txt', sep=r'\s*,\s*', engine='python', usecols=['time'], comment='#')
# chunks = []
# for chunk in pd.read_csv('0616_mems.txt', sep=r'\s*,\s*', engine='python', comment='#', usecols=['time', 'wx'], chunksize=1000):
#     chunks.append(chunk)
# #
# data = pd.concat((f for f in chunks), axis=0)
# data.columns = ['time', 'ax', 'ay', 'az', 'wx', 'wy', 'wz']

temp = pd.read_csv(path, sep=r'\s*,\s*', engine='python', skiprows=2, nrows=19)
temp.to_csv('tt2.txt', index=False)
N = len(temp.to_csv(index=False))
print(temp)
print('N= ', N)
# print(temp.iloc[0])
# print('AA\n', temp[0:0])
# print('BB', temp[:1])
df = [temp[:0]]

t = int(os.path.getsize(path) / N * 20 / 10 ** 4) + 1
for i, chunk in enumerate(pd.read_csv(path, chunksize=10 ** 4, low_memory=False)):
    df.append(chunk)

# print(df)
# data = temp[:0].append(df)
# data = pd.concat([temp[:0]])
# del df

t2 = time.perf_counter()
print(t2 - t1)
# print(data)
# print(data[:0]) # colum
# print('%s = %d bytes' % (path, size))
print(len(data.to_csv(index=False)))

# wz = data['wz']
# wz.plot()
# plt.show()
# print(chunks[0])
# print(v.info())
# print(v.shape)
# print(v)
# print(v['wz'])
# print(v.loc['0'])
# print(v)
# print(v.wz)
