import timeit
import time
import numpy as np

size = 10000

def pySum():
    a = list(range(size))
    b = list(range(size))
    c = []
    for i in range(len(a)):
        c.append(a[i]**2 + b[i]**2)
        # print('i=', i, end=' ')
        # print(c)

    return c
    
def npSum():
    a = np.arange(size)
    b = np.arange(size)
    for i in range(len(a)):
        c = a**2 + b**2
        # print('j=', i, end=' ')
        # print(c)
    return c
    
t = timeit.timeit(stmt="pySum()", setup="from  __main__ import pySum", number=10)
print('time/loop: ', t/10)
t = timeit.timeit(stmt="npSum()", setup="from  __main__ import npSum", number=10)
print('time/loop: ', t/10)