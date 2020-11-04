from scipy.signal import butter, lfilter
from scipy.signal import freqs, medfilt
import numpy as np 
import matplotlib.pyplot as plt

t = np.linspace(0, 15, 1000)
sig = np.sin(2*np.pi*t)
noise = 0.1*np.cos(2*np.pi*t*10)
tot = sig+noise



if __name__ == '__main__':
	data = [float(line.rstrip('\n')) for line in open('data.txt')]
	b, a = butter(3, 0.9,'low', analog =True)
	w, h = freqs(b, a)
	y = lfilter(b,a,data)
	z = medfilt(data, 15)
	
		
	print b
	print a
	plt.subplot(211)
	plt.plot(data,'r')
	plt.plot(y,'b')
	plt.plot(z,'g')
	plt.subplot(212)
	plt.plot(w,20*np.log10(abs(h)),'r')
	plt.xscale('log')
	plt.grid (which ='both', axis ='both')
	#plt.plot(, 'b')

	plt.show()


