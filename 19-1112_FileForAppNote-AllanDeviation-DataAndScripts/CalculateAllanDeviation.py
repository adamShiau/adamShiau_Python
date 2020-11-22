#Import the libraries
import numpy as np
from AllanFunc import cal_oadev
from pandas import read_excel
import matplotlib.pyplot as plt

#Read in the raw data from an excel file
raw = read_excel('data.xlsx',header=None);
data = raw.values
freq = data[:,0]
phase = data[:,1]


#Define tau array and sampling rate
t = np.array([8.19E-03, 1.64E-02, 3.28E-02, 6.55E-02, 1.31E-01, 2.62E-01, 
              5.24E-01, 1.05E+00, 2.10E+00, 4.19E+00, 8.39E+00, 1.68E+01, 
              3.36E+01, 6.71E+01, 1.34E+02, 2.68E+02])

r = 1.2207031250E+02
tau0 = 1/r
t = np.array([tau0, 5*tau0, 10*tau0, 50*tau0, 100*tau0, 500*tau0, 1e3*tau0, 5e3*tau0,
              1e4*tau0])


#Calculate the Allan Deviation
(t2phase, adphase) = cal_oadev(phase, r, t) 
 
#Plot the results
fig = plt.figure()
ax1 = fig.add_subplot()
ax1.set_label('Frequency (Hz)')
ax1.set_title('Phase Allan Deviations')
lin, = ax1.loglog(t2phase, adphase)

plt.show()