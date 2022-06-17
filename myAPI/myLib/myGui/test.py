import numpy as np
import pandas as pd

v = pd.read_csv('0616.txt', sep=r'\s*,\s*', engine='python', comment='#')
print(v.info())
print(v.shape)
print(v)
print(v['fog'])
# print(v.loc['0'])
# print(v)
# print(v.wz)