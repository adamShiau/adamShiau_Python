# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 21:10:55 2020

@author: adam
"""


import numpy as np
import time
f=open('filew.txt','a')

cnt1 = 0
cnt2 = 0

data = np.empty(0)
# data2 = np.empty(0)
temp1 = np.empty(0)
temp2 = np.empty(0)
temp3 = np.empty(0)
while(1):
    temp1 = np.empty(0)
    temp2 = np.empty(0)
    temp3 = np.empty(0)
    for i in range(5):
        temp1 = np.append(temp1, cnt1)
        temp2 = np.append(temp2, cnt2)
        temp3 = np.append(temp3, cnt2+cnt1)
        cnt1 = cnt1 + 1
        cnt2 = cnt2 - 1
        time.sleep(0.2)
    # print(temp1)
    # print(temp2)
    data = (np.vstack([temp1,temp2, temp3])).T
    print(data)
    np.savetxt(f, data, fmt='%.5f')
f.close()
    