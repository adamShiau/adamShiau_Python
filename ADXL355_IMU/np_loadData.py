import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt

print(sys.path)
Var = np.loadtxt('t.txt', comments='#', delimiter=',')
print(Var.shape)
print(Var[1,1])
t = Var[:,0]
t2 = t[1:]
t = t[0:len(t2)]
t3 = (t2-t)*1e3
# SRS_wz = Var[:,1]
# PP_wz = Var[:,2]
# ax = Var[:,3]
# ay = Var[:,4]

plt.plot(t3,marker = '*')
# plt.figure(1)
# plt.plot(t, ax)
# plt.figure(2)
# plt.plot(t, ay)
# plt.figure(3)
# plt.plot(t, SRS_wz)
# plt.figure(4)
# plt.plot(t, PP_wz)
plt.show()

# print(t[-1])