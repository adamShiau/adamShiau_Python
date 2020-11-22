import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt

print(sys.path)
Var = np.loadtxt('2.txt', comments='#', delimiter=',')
print(Var.shape)
print(Var[1,1])
t = Var[:,0]
ax = Var[:,1]
ay = Var[:,2]
az = Var[:,3]
wx = Var[:,4]
wy = Var[:,5]
wz = Var[:,6]

plt.plot(t, wz)
plt.show()