from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import os 
import sys 

WRITE_DATA = 1
rotation_angle = -25
rt_theta = rotation_angle*np.pi/180
divider = 1

NAME = '04-20-2021_start5'
filename = NAME+'_mod'+'.txt'

app = QtGui.QApplication([])
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
win = pg.GraphicsLayoutWidget(show=True, title="track plot")
win.resize(490,520)
win.setWindowTitle('pyqtgraph example: Plotting')
pg.setConfigOptions(antialias=True)





Var = np.loadtxt(NAME+'.txt', comments='#', delimiter=',')
# Var2 = np.loadtxt(NAME+'_track.txt', comments='#', delimiter=',')
print('Var.shape: ', Var.shape)

t = Var[:,0]
t2 = t[1:]

diff_t = (t2-t[0:-1])*1
print('len(t):', len(t))
print('len(t2):', len(t2))
print('len(diff_t):', len(diff_t))
SRS_wz = Var[:,1]
Sparrow_wz = Var[:,2]
Nano33_wx = Var[:,3]
Nano33_wy = Var[:,4]
Nano33_wz = Var[:,5]
ax = Var[:,6]
ay = Var[:,7]
az = Var[:,8]
v = Var[:,9]
# vbox = Var[:,10]
T = Var[:,12]



length = round(len(t)/divider)
print('plot length: ', length)

temp_theta_SRS = 0
temp_theta_Sparrow = 0
temp_theta_Nano33 = 0
tempx_SRS = 0
tempy_SRS = 0
tempx_Sparrow = 0
tempy_Sparrow = 0
tempx_Nano33 = 0
tempy_Nano33 = 0
theta_SRS = np.empty(0)
theta_Sparrow = np.empty(0)
theta_Nano33 = np.empty(0)
x_SRS = np.empty(0)
y_SRS = np.empty(0)
xp_SRS = np.empty(0)
yp_SRS = np.empty(0)
x_Sparrow = np.empty(0)
y_Sparrow = np.empty(0)
xp_Sparrow = np.empty(0)
yp_Sparrow = np.empty(0)
x_Nano33 = np.empty(0)
y_Nano33 = np.empty(0)
xp_Nano33 = np.empty(0)
yp_Nano33 = np.empty(0)
for i in range(length-1):
	dt = t[i+1]-t[i]
	''' theta'''
	temp_theta_SRS = temp_theta_SRS - SRS_wz[i]*dt
	theta_SRS = np.append(theta_SRS, temp_theta_SRS)
	temp_theta_Sparrow = temp_theta_Sparrow - Sparrow_wz[i]*dt
	theta_Sparrow = np.append(theta_Sparrow, temp_theta_Sparrow)
	temp_theta_Nano33 = temp_theta_Nano33 - Nano33_wz[i]*dt
	theta_Nano33 = np.append(theta_Nano33, temp_theta_Nano33)
	''' x'''
	tempx_SRS = tempx_SRS + v[i]*np.cos((90-temp_theta_SRS)*np.pi/180)*dt
	x_SRS = np.append(x_SRS, tempx_SRS)
	tempx_Sparrow = tempx_Sparrow + v[i]*np.cos((90-temp_theta_Sparrow)*np.pi/180)*dt
	x_Sparrow = np.append(x_Sparrow, tempx_Sparrow)
	tempx_Nano33 = tempx_Nano33 + v[i]*np.cos((90-temp_theta_Nano33)*np.pi/180)*dt
	x_Nano33 = np.append(x_Nano33, tempx_Nano33)
	''' y'''
	tempy_SRS = tempy_SRS + v[i]*np.sin((90-temp_theta_SRS)*np.pi/180)*dt
	y_SRS = np.append(y_SRS, tempy_SRS)
	tempy_Sparrow = tempy_Sparrow + v[i]*np.sin((90-temp_theta_Sparrow)*np.pi/180)*dt
	y_Sparrow = np.append(y_Sparrow, tempy_Sparrow)
	tempy_Nano33 = tempy_Nano33 + v[i]*np.sin((90-temp_theta_Nano33)*np.pi/180)*dt
	y_Nano33 = np.append(y_Nano33, tempy_Nano33)
	''' rotation axis'''
	xp_SRS = np.append(xp_SRS, tempx_SRS*np.cos(rt_theta)-tempy_SRS*np.sin(rt_theta))
	yp_SRS = np.append(yp_SRS, tempx_SRS*np.sin(rt_theta)+tempy_SRS*np.cos(rt_theta))
	xp_Sparrow = np.append(xp_Sparrow, tempx_Sparrow*np.cos(rt_theta)-tempy_Sparrow*np.sin(rt_theta))
	yp_Sparrow = np.append(yp_Sparrow, tempx_Sparrow*np.sin(rt_theta)+tempy_Sparrow*np.cos(rt_theta))
	xp_Nano33 = np.append(xp_Nano33, tempx_Nano33*np.cos(rt_theta)-tempy_Nano33*np.sin(rt_theta))
	yp_Nano33 = np.append(yp_Nano33, tempx_Nano33*np.sin(rt_theta)+tempy_Nano33*np.cos(rt_theta))

min_xSRS = np.min(xp_SRS); max_xSRS = np.max(xp_SRS)
min_ySRS = np.min(yp_SRS); max_ySRS = np.max(yp_SRS)
range_xSRS = np.abs(max_xSRS-min_xSRS)
range_ySRS = np.abs(max_ySRS-min_ySRS)
# print('range_xSRS: ', range_xSRS)
# print('range_ySRS: ', range_ySRS)
# print('min_xSRS: ', min_xSRS)
# print('max_xSRS: ', max_xSRS)

min_xSparrow = np.min(xp_Sparrow); max_xSparrow = np.max(xp_Sparrow)
min_ySparrow = np.min(yp_Sparrow); max_ySparrow = np.max(yp_Sparrow)
range_xSparrow = np.abs(max_xSparrow-min_xSparrow)
range_ySparrow = np.abs(max_ySparrow-min_ySparrow)
# print('range_xSparrow: ', range_xSparrow)
# print('range_ySparrow: ', range_ySparrow)
# print('min_xSparrow: ', min_xSparrow)
# print('max_xSparrow: ', max_xSparrow)

min_xNano33 = np.min(xp_Nano33); max_xNano33 = np.max(xp_Nano33)
min_yNano33 = np.min(yp_Nano33); max_yNano33 = np.max(yp_Nano33)
range_xNano33 = np.abs(max_xNano33-min_xNano33)
range_yNano33 = np.abs(max_yNano33-min_yNano33)
# print('range_xNano33: ', range_xNano33)
# print('range_yNano33: ', range_yNano33)
# print('min_xNano33: ', min_xNano33)
# print('max_xNano33: ', max_xNano33)


axis_range = np.max([range_xSRS, range_ySRS, range_xSparrow, range_ySparrow, range_xNano33, range_yNano33])
x_min = np.min([min_xSRS, min_xSparrow, min_xNano33])
x_max = np.max([max_xSRS, max_xSparrow, max_xNano33])
y_min = np.min([min_ySRS, min_ySparrow, min_yNano33])
y_max = np.max([max_ySRS, max_ySparrow, max_yNano33])

print('axis_range: ', axis_range)

print(len(x_SRS), end=', ')
print(len(y_SRS))


p1 = win.addPlot()
p1.addLegend()
# p1.plot(x_SRS, y_SRS, pen='r', name="SRS200")
p1.plot(xp_SRS, yp_SRS, pen='r', name="SRS200p")
# p1.plot(x_Sparrow, y_Sparrow, pen='r', name="Sparrow")
p1.plot(xp_Sparrow, yp_Sparrow, pen='b', name="Sparrowp")
# p1.plot(x_Nano33, y_Nano33, pen='k', name="Nano33")
p1.plot(xp_Nano33, yp_Nano33, pen='k', name="Nano33p")
p1.setXRange(x_min, x_min + axis_range, padding=0)
p1.setYRange(y_min, y_min + axis_range, padding=0)


if(WRITE_DATA):
	# f=open(filename, 'w')
	f2=open(filename[0:-4] + '_track.txt', 'w')
	# f.writelines('#' + 'dt, SRS200_wz, PP_wz, Nano33_wx, Nano33_wy, Nano33_wz, Adxl355_ax, Adxl355_ay, '
	# +'Adxl355_az, speed, VBOX, data_T' + '\n')
	# f.writelines('#' + 's, DPS, DPS, DPS, DPS, DPS, g, g, g, m/s, km/h,code' + '\n')
	f2.writelines('#' + 'SRS200_x, SRS200_y, PP_x, PP_y, Nano33_x, Nano33_y' + '\n')
	# np.savetxt(f, (np.vstack([t, SRS_wz, Sparrow_wz, Nano33_wx, Nano33_wy, Nano33_wz, 
		# ax, ay, az, v, vbox, T])).T, 
			# fmt='%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.0f')
	np.savetxt(f2, (np.vstack([x_SRS, y_SRS, x_Sparrow, y_Sparrow, x_Nano33, y_Nano33]	)).T, 
		fmt='%5.5f,%5.5f,%5.5f,%5.5f,%5.5f,%5.5f')
	# f.close()
	f2.close()


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()






