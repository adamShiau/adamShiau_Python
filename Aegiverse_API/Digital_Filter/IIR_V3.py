import numpy as np
from scipy.signal import iirfilter, freqz
import matplotlib.pyplot as plt

# Filter specifications
fs = 100e6  # Sampling frequency in Hz
fc = 5e6      # Cutoff frequency in Hz
order = 2    # Filter order (2nd order IIR)

# Design a low-pass Butterworth filter
b, a = iirfilter(order, fc / (fs / 2), btype='low', ftype='butter')

# Convert coefficients to Q1.15 fixed-point format
q_format = 15
B = np.round(b * (2 ** q_format)).astype(int)
A = np.round(a * (2 ** q_format)).astype(int)

# Check for overflow
def check_overflow(coeff, name):
    for i, c in enumerate(coeff):
        if c < -32768 or c > 32767:
            print(f"Warning: {name}[{i}] = {c} exceeds signed 16-bit range!")

check_overflow(B, "B")
check_overflow(A, "A")

# Print coefficients in Verilog signed 16-bit format
print("// Verilog coefficients in signed 16-bit format")
print(f"parameter signed [15:0] COEFF_B0 = {B[0]};")
print(f"parameter signed [15:0] COEFF_B1 = {B[1]};")
print(f"parameter signed [15:0] COEFF_B2 = {B[2]};")
print(f"parameter signed [15:0] COEFF_A1 = {-A[1]};")  # Negate directly
print(f"parameter signed [15:0] COEFF_A2 = {-A[2]};")  # Negate directly

# Frequency response
w, h = freqz(b, a, worN=8000, fs=fs)

# Plot frequency response
plt.figure(figsize=(10, 6))
plt.plot(w, 20 * np.log10(abs(h)), label='Magnitude Response')
plt.title('Frequency Response of the IIR Filter')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (dB)')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.axvline(fc, color='red', linestyle='--', label=f'Cutoff Frequency = {fc} Hz')
plt.legend()
plt.show()
