import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt

print(sys.path)
Var = np.loadtxt('filew.txt')
print(Var.shape)
print(Var[1,1])
a = Var[:,0]
b = Var[:,1]
c = Var[:,2]

plt.plot(b)
plt.show()