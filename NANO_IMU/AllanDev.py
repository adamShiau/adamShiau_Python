'''
The function cal_oadev takes the time series, sampling rate and an array of observation time τ as the input. 
It calculates the overlapped Allan deviation using equation (2) and returns 
the nτ0 and σy (nτ0 ) as arrays. Required Libraries: NumPy, math

note:τ = nτ0
https://liquidinstruments.com/blog/2019/11/12/measuring-allan-deviation-a-guide-to-allan-deviation-with-mokulabs-phasemeter/
'''

#Import libraries
import numpy as np
import math
import matplotlib.pyplot as plt


def cal_oadev(data,rate,tauArray):
	tau0 = 1/rate #Calculate the sampling period
	dataLength = data.size #Calculate N, data length
	dev = np.array([]) #Create empty array to store the output.
	actualTau = np.array([])	
	for i in tauArray:
		n = math.floor(i/tau0) #Calculate n given a tau value.
		if n == 0:
			n = 1 #Use minimal n if tau is less than the sampling period.
		currentSum = 0 #Initialize the sum
		print('n: ', n)
		for j in range(0,dataLength-2*n):
			currentSum = (data[j+2*n]-2*data[j+n]+data[j])**2+currentSum #Cumulate the sum squared
		devAtThisTau = currentSum/(2*n**2*tau0**2*(dataLength-2*n)) #Divide by the coefficient
		dev = np.append(dev,np.sqrt(devAtThisTau))
		actualTau = np.append(actualTau,n*tau0)
	return actualTau, dev #Return the actual tau and overlapped Allan deviation


dataRate = 100

Var = np.loadtxt('20201111_SRS200.txt', comments='#', delimiter=None, skiprows=6)
# Var = np.loadtxt('data2.txt', comments='#', delimiter=',', skiprows=0)
t = Var[:,0]
# ax = Var[:,1]
# ay = Var[:,2]
# az = Var[:,3]
# wx = Var[:,4]
# wy = Var[:,5]
# wz = Var[:,6]
wz = Var[:,1] #dps
thetaz = wz.cumsum()/dataRate #degree
dataLength = t.size

print('load done')
print('N =', dataLength, end=', ')
print(thetaz.size)


tau0 = 1/dataRate

tauArray = np.array([tau0, 3*tau0, 5*tau0, 10*tau0, 30*tau0, 50*tau0, 
                     100*tau0, 300*tau0, 500*tau0, 1000*tau0, 3e3*tau0,
                     5000*tau0, 10000*tau0, 3e4*tau0, 50000*tau0, 100000*tau0,
					 5e5*tau0, 1e6*tau0, 2e6*tau0])
# tauArray = np.array([tau0, 3*tau0, 5*tau0, 10*tau0, 30*tau0, 50*tau0, 
					# 100*tau0, 300*tau0, 500*tau0, 1000*tau0, 3e3*tau0,
					# 5000*tau0, 10000*tau0, 3e4*tau0, 50000*tau0, 100000*tau0,
					# 5e5*tau0])

x, y = cal_oadev(thetaz, dataRate, tauArray)
y = y*3600

plt.loglog(x,y, linestyle = '-', marker = '*')
plt.xlabel('s')
plt.ylabel('Degree/hour')
plt.show()

