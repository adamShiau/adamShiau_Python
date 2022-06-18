import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import os, sys

path = '0619.txt'
row_len = 20
temp = pd.read_csv(path, sep=r'\s*,\s*', engine='python', comment='#', skiprows=2, nrows=row_len - 1)
size = os.path.getsize(path)
N = len(temp.to_csv(index=False))*1
print(temp)
print('N: ', N)
print('size: ', size)
print('total len: ', int(size / N)*row_len)
total_length = int(size / N)*row_len

df = []
chunksize = 6000
for chunk in pd.read_csv(path, sep=r'\s*,\s*', engine='python', comment='#', skiprows=0, chunksize=chunksize):
    # N = len(chunk.to_csv(index=False))
    df.append(chunk)
    current_len = len(df)*chunksize
    # print( len(df)*chunksize )
    # print('progress: ', round(current_len*100/total_length, 2))

df = pd.concat((f for f in df))
wz = df['wz']
wz.index = df['time']
# wz.plot()
# df[['wz']].plot()
# plt.show()
# print(df)
    # print('N: ', N)

# N = len(temp.to_csv(index=False))
# size = os.path.getsize(path)
# print(temp)
# print('N: ', N)
# print('size: ', size)
# print(size / N)
