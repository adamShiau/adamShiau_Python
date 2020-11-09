import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


total_pnt = 10 #幾邊形
update_rate = 1
a0 = 1
w0 = 36 #degree/s

acce = np.zeros(total_pnt)
acce[:5] = a0


velocity = [0]
idx = 0
for i in acce : 
    velocity.append(velocity[idx]+i/update_rate)
    idx = idx + 1
    # print(velocity)

velocity = velocity[:total_pnt]
# print('velocity')
# print(velocity)

w = np.full(total_pnt, w0)
idx = 0
theta = [0]
for i in w : 
    theta.append(theta[idx]+i/update_rate)
    idx = idx + 1
    # print(theta)
theta = theta[:total_pnt]
theta = np.array(theta)
# print(theta)

phi = 90-theta
# print('phi')
# print(phi)

x = [0]
y = [0]
# dl = [0]
idx = 0
# dx = total_pnt*[0]
# dy = total_pnt*[0]

for i in range(0,total_pnt) :
    
    dx = velocity[i]*1*math.cos(phi[i]*math.pi/180)
    dy= velocity[i]*1*math.sin(phi[i]*math.pi/180)
    # dl.append(velocity[i]*0.01)
    x.append(x[i] + dx)
    y.append(y[i] + dy)
    # print(x[i], dx)
    # idx = idx + 1


# plt.figure(0)
# plt.plot(phi)
# plt.ylabel('phi')
plt.figure(1)
plt.ylabel('velocity')
plt.plot(velocity)
plt.figure(2)
plt.ylabel('acce')
plt.plot(acce)
plt.figure(4)
plt.plot(x,y)
plt.ylabel('track')
plt.figure(5)
plt.plot(theta,'-*')
plt.ylabel('theta')
plt.show()

