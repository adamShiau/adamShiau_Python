import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt

NAME = '2021-03-11'

print(sys.path)
Var = np.loadtxt(NAME+'.txt', comments='#', delimiter=',')
Var2 = np.loadtxt(NAME+'_track.txt', comments='#', delimiter=',')
print(Var.shape)
print(Var[1,1])

t = Var[:,0]
t2 = t[1:]

diff_t = (t2-t[0:-1])*1e3
print('len(t):', len(t))
print('len(t2):', len(t2))
print('len(diff_t):', len(diff_t))
SRS_wz = Var[:,1]
PP_wz = Var[:,2]
ax = Var[:,3]
ay = Var[:,4]
az = Var[:,5]
vx = Var[:,6]
vy = Var[:,7]
v = Var[:,8]
T = Var[:,9]
x = Var2[:,0]
y = Var2[:,1]

plt.figure(1)
plt.plot(diff_t,marker = '*')
plt.title("diff_t") # title
plt.xlabel("t(s)") # x label
plt.ylabel("difft(ms)") # y label


plt.figure(2)
plt.plot(t, SRS_wz)
plt.title("SRS_wz") # title
plt.xlabel("t(s)") # x label
plt.ylabel("DPS") # y label

plt.figure(11)
temp = 0
theta = np.empty(0)
for i in range(len(SRS_wz)):
	temp = temp - SRS_wz[i]
	
	theta = np.append(theta, temp*0.01)
	# print(temp)
	# print(len(theta))
# print(len(SRS_wz))
plt.plot(theta)
plt.title("theta") # title
plt.xlabel("pts") # x label
plt.ylabel("degree") # y label

# plt.figure(3)
# plt.plot(t, ax)
# plt.title("ax") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("a(g)") # y label

# plt.figure(4)
# plt.plot(t, ay)
# plt.title("ay") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("a(g)") # y label

# plt.figure(5)
# plt.plot(t, az)
# plt.title("az") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("a(g)") # y label


# plt.figure(6)
# plt.plot(t, vx)
# plt.title("vx") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("v(m/s)") # y label


# plt.figure(7)
# plt.plot(t, vy)
# plt.title("vy") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("v(m/s)") # y label

# plt.figure(8)
# plt.plot(t, v)
# plt.title("speed") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("v(m/s)") # y label

# plt.figure(9)
# plt.plot(x, y)
# plt.title("track") # title
# plt.xlabel("x(m)") # x label
# plt.ylabel("y(m)") # y label

# plt.figure(10)
# plt.plot(t, PP_wz)
# plt.title("PP_wz") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("w(dps)") # y label

# plt.figure(11)
# plt.plot(t, T)
# plt.title("temperature") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("T(code))") # y label

plt.show()

# print(t[-1])