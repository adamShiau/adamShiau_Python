from scipy.optimize import newton
from scipy.signal import freqz, dimpulse, dstep
from math import sin, cos, sqrt, pi
import numpy as np
import matplotlib.pyplot as plt

'''
reference web:
https://tttapa.github.io/Pages/Mathematics/Systems-and-Control-Theory/Digital-filters/Simple%20Moving%20Average/Simple-Moving-Average.html
'''
# Function for calculating the cut-off frequency of a moving average filter
def get_sma_cutoff(N, **kwargs):
    func = lambda w: sin(N*w/2) - N/sqrt(2) * sin(w/2)  # |H(e^jω)| = √2/2
    deriv = lambda w: cos(N*w/2) * N/2 - N/sqrt(2) * cos(w/2) / 2  # dfunc/dx
    omega_0 = pi/N  # Starting condition: halfway the first period of sin(Nω/2)
    return newton(func, omega_0, deriv, **kwargs)

# Simple moving average design parameters

f_s = 300e3
N = 16384

# Find the cut-off frequency of the SMA
w_c = get_sma_cutoff(N)
f_c = w_c * f_s / (2 * pi)
print('sampling rate(MHz): ',f_s/1e6 );
print('MV points: ',N );
print('cut off freq(KHz) : ', f_c/1e3, end='\n\n')

# SMA coefficients
b = np.ones(N)
a = np.array([N] + [0]*(N-1))

# Calculate the frequency response
w, h = freqz(b, a, worN=4096)
w *= f_s / (2 * pi)                    # Convert from rad/sample to Hz

# f_marker1 = 24.4e3
f_marker2 = 389e3
# f_marker3 = 775e3

# Plot the amplitude response
plt.subplot(2, 1, 1)
plt.suptitle('Bode Plot')
plt.plot(w, 20 * np.log10(abs(h)))       # Convert modulus to dB
plt.ylabel('Magnitude [dB]')
plt.xlim(0, f_s / 2 /1)
plt.ylim(-60, 1)
# plt.axvline(f_c, color='red')
# plt.axvline(f_marker1, color='blue')
plt.axvline(f_marker2, color='blue')
# plt.axvline(f_marker3, color='blue')
# plt.axhline(-3.01, linewidth=0.8, color='black', linestyle=':')
plt.grid()

# Plot the phase response
plt.subplot(2, 1, 2)
plt.plot(w, 180 * np.angle(h) / pi)      # Convert argument to degrees
plt.xlabel('Frequency [Hz]')
plt.ylabel('Phase [°]')
plt.xlim(0, f_s / 2/50)
plt.ylim(-180, 90)
plt.yticks([-180, -135, -90, -45, 0, 45, 90])
# plt.axvline(f_marker1, color='blue')
plt.axvline(f_marker2, color='blue')
# plt.axvline(f_marker3, color='blue')
# plt.axvline(f_c, color='red')
plt.grid()
plt.show()
''' 
# Plot the impulse response
t, y = dimpulse((b, a, 1/f_s), n=2*N)
plt.suptitle('Impulse Response')
_, _, baseline = plt.stem(t, y[0], basefmt='k:')
plt.setp(baseline, 'linewidth', 1)
baseline.set_xdata([0,1])
baseline.set_transform(plt.gca().get_yaxis_transform())
plt.xlabel('Time [seconds]')
plt.ylabel('Output')
plt.xlim(-1/f_s, 2*N/f_s)
plt.yticks([0, 0.5/N, 1.0/N])
plt.show()

# Plot the step response
t, y = dstep((b, a, 1/f_s), n=2*N)
plt.suptitle('Step Response')
_, _, baseline = plt.stem(t, y[0], basefmt='k:')
plt.setp(baseline, 'linewidth', 1)
baseline.set_xdata([0,1])
baseline.set_transform(plt.gca().get_yaxis_transform())
plt.xlabel('Time [seconds]')
plt.ylabel('Output')
plt.xlim(-1/f_s, 2*N/f_s)
plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])

plt.show()
''' 