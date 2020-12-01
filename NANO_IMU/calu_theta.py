# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 16:27:21 2020

@author: ami73
"""

import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt

dataRate = 100

print(sys.path)
Var = np.loadtxt('00.txt', comments='#', delimiter=',')
print(Var.shape)
print(Var[1,1])
t = Var[:,0]
ax = Var[:,1]
ay = Var[:,2]
az = Var[:,3]
wx = Var[:,4]
wy = Var[:,5]
wz = Var[:,6]
wz200 = Var[:,7]

thetaz = wz.cumsum()/dataRate #degree
thetaz200 = wz200.cumsum()/dataRate #degree
dataLength = t.size
print('length = ', dataLength)

plt.figure(1)
plt.plot(t, wz, t, wz200)
plt.figure(2)
plt.plot(t, thetaz, t, thetaz200)
plt.show()