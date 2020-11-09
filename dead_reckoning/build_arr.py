import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


total_pnt = 1940
update_rate = 100
a0 = 2.778
dt = int(1/update_rate*1000) #ms
time = np.array(range(0, total_pnt*dt, dt))
time = time/1000 #s

acce = np.zeros(total_pnt)
acce[:10*update_rate] = a0


velocity = [0]
idx = 0
for i in acce : 
    velocity.append(velocity[idx]+i/update_rate)
    idx = idx + 1

velocity = velocity[:total_pnt]

w = np.full(total_pnt, 18.566)
idx = 0
theta = [0]
for i in w : 
    theta.append(theta[idx]+i/update_rate)
    idx = idx + 1
theta = theta[:total_pnt]
theta = np.array(theta)

phi = 90-theta

x = [0]
y = [0]
dl = [0]
idx = 0
dx = total_pnt*[0]
dy = total_pnt*[0]

for i in range(1,total_pnt) :
    
    dx[idx] = velocity[i]*0.01*math.cos(phi[i]*math.pi/180)
    dy[idx] = velocity[i]*0.01*math.sin(phi[i]*math.pi/180)
    dl.append(velocity[i]*0.01)
    x.append(x[idx] + dx[idx])
    y.append(y[idx] + dy[idx])
    print(x[idx], dx[idx])
    idx = idx + 1

# velocity = pd.Series(velocity)
# print(velocity)
# velocity = pd.Series(velocity.iloc[0:total_pnt], index = time)
# velocity = pd.Series(velocity.iloc[0:total_pnt])
# velocity = pd.Series(velocity, time)
# time = np.append(time, 30)

# time = pd.Series(time) #可轉換成time series
# time = time/1000 #s



# time.iloc[0:100] = acce


print(len(x))
print(len(y))
print(len(dl))
print(len(dx))
print(len(dy))

# print(math.cos(-180*math.pi/180))
# print(math.cos(-135*math.pi/180))

plt.figure(0)
plt.plot(phi)
# plt.figure(1)
# plt.plot(y)
plt.figure(1)
plt.plot(dl)
plt.figure(2)
plt.plot(dx)
plt.figure(3)
plt.plot(dy)
plt.show()

