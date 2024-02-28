import numpy as np
import matplotlib.pyplot as plt

# Define the sinc function
def sinc(x):
    return np.sinc(x/np.pi)

# Define the continuous signal
def x(t):
    return sinc(2*np.pi*t) + sinc(2*np.pi*(t-0.5))

# Define the sampling frequency
fs = 20  # Sampling frequency

# Time vector for the continuous signal
t_cont = np.linspace(-1, 2, 1000)

# Time vector for the discrete signal
t_disc = np.arange(-1, 2, 1/fs)

# Generate the continuous signal
x_cont = x(t_cont)

print('len(x_cont): ', len(x_cont))
# print(t_cont)
print('len(t_disc): ', len(t_disc))
# print(t_disc)

# Sample the continuous signal
x_disc = x(t_disc)

# Downsample by a factor of 2
x_downsampled = x_disc[::2]

print('len(x_downsampled): ', len(x_downsampled))

# Plot the continuous and downsampled signals
plt.figure(figsize=(10, 6))
plt.plot(t_cont, x_cont, label='Continuous Signal')
plt.stem(t_disc, x_disc, label='Sampled Signal', basefmt=" ")
plt.stem(t_disc[::2], x_downsampled, label='Downsampled Signal', markerfmt='ro', basefmt=" ", linefmt='r-')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title('Signal Downsampled by 2')
plt.legend()
plt.grid(True)
plt.show()
