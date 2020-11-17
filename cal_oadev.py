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
		for j in range(0,dataLength-2*n):
			currentSum = (data[j+2*n]-2*data[j+n]+data[j])**2+currentSum #Cumulate the sum squared
		devAtThisTau = currentSum/(2*n**2*tau0**2*(dataLength-2*n)) #Divide by the coefficient
		dev = np.append(dev,np.sqrt(devAtThisTau))
		actualTau = np.append(actualTau,n*tau0)
	return actualTau, dev #Return the actual tau and overlapped Allan deviation