import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt


NAME = 'tt'
SF_A = 0.00295210451588764
SF_B = -0.00137052112589694

print(sys.path)
# Var = np.loadtxt(NAME+'.txt', comments='#', delimiter=',')
Var = np.loadtxt(NAME, comments='#', delimiter=',')
print(Var.shape)
print(Var[1,1])

t = Var[:,0]
t2 = t[1:]

diff_t = (t2-t[0:-1])*1e3
print('len(t):', len(t))
print('len(t2):', len(t2))
print('len(diff_t):', len(diff_t), end='\n\n')
err = Var[:,1]
step = Var[:,2]
PD_T = Var[:,3]
# Nano33_wx = Var[:,3]
# Nano33_wy = Var[:,4]
# Nano33_wz = Var[:,5]
# ax = Var[:,6]
# ay = Var[:,7]
# az = Var[:,8]
# lat = Var[:,12]
# lon = Var[:,13]
# vbox_az = Var[:,19]
# v = Var[:,9]
# vbox = Var[:,10]
# T = Var[:,11]

# x200 = Var2[:,0]
# y200 = Var2[:,1]
# xPP = Var2[:,2]
# yPP = Var2[:,3]
# xNano33 = Var2[:,4]
# yNano33 = Var2[:,5]

plt.figure(1)
plt.plot(diff_t,marker = '*')
plt.title("diff_t") # title
plt.xlabel("t(s)") # x label
plt.ylabel("difft(ms)") # y label
print('avg(diff_t), [ms]: ', np.average(diff_t))
print('std(diff_t), [ms]: ', np.std(diff_t))
print('update rate, [Hz]:', np.round(1e3/np.average(diff_t), 2), end='\n\n')

##### Err #######
err_mV = err*1e3
plt.figure(2)
plt.subplot(1,2,1)
plt.plot(t, err_mV, label='err signal')
plt.title("Err") # title
plt.xlabel("t(s)") # x label
plt.ylabel("mV") # y label
plt.legend()
print('avg(err), [mV]: ', np.average(err_mV))
print('std(err), [mV]: ', np.std(err_mV), end='\n\n')

plt.subplot(1,2,2)
plt.hist(err_mV, bins=100, range=None, density=False, color = 'lightblue', cumulative = False, label = "err Histogram")
plt.legend()
plt.xlabel('err')

##### Step #######
step_dph = 3600*(step*SF_A + SF_B)
# step_dph = step
plt.figure(3)
plt.subplot(1,2,1)
plt.plot(t, step_dph, label='step signal')
plt.title("step") # title
plt.xlabel("t(s)") # x label
plt.ylabel("dph") # y label
plt.legend()
print('avg(step), [dph]: ', np.average(step_dph))
print('std(step), [dph]: ', np.std(step_dph), end='\n\n')

plt.subplot(1,2,2)
plt.hist(step_dph, bins=100, range=None, density=False, color = 'lightblue', cumulative = False, label = "step Histogram")
plt.legend()
plt.xlabel('step')

#####double Y anix#######
# fig, ax1 = plt.subplots()

# color = 'tab:red'
# ax1.set_xlabel('time (s)')
# ax1.set_ylabel('mems gyro (dps)', color=color)
# ax1.plot(t, err, color=color)
# ax1.tick_params(axis='y', labelcolor=color)

# ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
# color = 'tab:blue'
# ax2.set_ylabel('PD temp. (degree C)', color=color)  # we already handled the x-label with ax1
# ax2.plot(t, PD_T, color=color)
# ax2.tick_params(axis='y', labelcolor=color)

# fig.tight_layout()  # otherwise the right y-label is slightly clipped

# print('avg(err): ', np.average(err))
# print('std(err): ', np.std(err))
#####






# plt.figure(3)
# plt.plot(t, Nano33_wx, label='Nano33_wx')
# plt.plot(t, Nano33_wy, label='Nano33_wy')
# plt.title("Nano33_w") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("DPS") # y label
# plt.legend()

# plt.figure(2)
# plt.plot(x200, y200, label='SRS200')
# plt.plot(xPP, yPP, label='Sparrow')
# plt.plot(xNano33, yNano33, label='Nano33')
# plt.title("track") # title
# plt.xlabel("m") # x label
# plt.ylabel("m") # y label
# plt.legend()

# plt.figure(2)
# plt.plot(t, SRS_wz)
# plt.title("SRS_wz") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("DPS") # y label

# plt.figure(11)
# temp = 0
# theta = np.empty(0)
# for i in range(len(SRS_wz)):
	# temp = temp - SRS_wz[i]
	
	# theta = np.append(theta, temp*0.01)
	# print(temp)
	# print(len(theta))
# print(len(SRS_wz))
# plt.plot(theta)
# plt.title("theta") # title
# plt.xlabel("pts") # x label
# plt.ylabel("degree") # y label

# plt.figure(4)
# plt.plot(t, ax)
# plt.title("ax") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("a(g)") # y label

# plt.figure(5)
# plt.plot(t, ay)
# plt.title("ay") # title
# plt.xlabel("t(s)") # x label
# plt.ylabel("a(g)") # y label

# plt.figure(6)
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