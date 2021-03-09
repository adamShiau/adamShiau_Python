import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt

print(sys.path)
Var = np.loadtxt('t.txt', comments='#', delimiter=',')
print(Var.shape)
print(Var[1,1])
t = Var[:,0]
# ax = Var[:,1]
# ay = Var[:,2]
# az = Var[:,3]
# wx = Var[:,4]
# wy = Var[:,5]
wz = Var[:,1]

t2 = t[1:]
print(len(t))
print(len(t2))
delta_t = t2 - t[0:-1]
plt.plot(delta_t*1e3)
plt.show()