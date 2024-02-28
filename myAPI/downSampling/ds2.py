import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
__author__  = "Jan Wilczek"
__license__ = "GPL"
__version__ = "1.0.0"

# Plotting parameters
plt.rcParams.update({'font.size': 15})
xlim = [-15, 15]
stem_params = {'linefmt': 'C0-', 'markerfmt': 'C0o', 'basefmt': ' '}


def signal(A, f, t, phi=0.0):
    """
    :param A: amplitude
    :param f: frequency in Hz
    :param t: time in s
    :param phi: phase offset
    :return: sine with amplitude A at frequency f over time t
    """
    return A * np.sin(2 * np.pi * f * t + phi)

def normalized_dft(signal, n_fft, fs):
    """
    :param signal: signal to calculate DFT of
    :param n_fft: number of samples for Fast Fourier Transform
    :param fs: sample rate
    :return: discrete Fourier spectrum of the given signal normalized to the highest amplitude of frequency components
    """
    dft = np.abs(np.fft.fft(signal[:n_fft]))
    dft /= np.amax(dft)
    frequencies = np.fft.fftfreq(len(dft), d=1 / fs)

    amplitude_threshold = 0.01
    nonzero_frequencies = [frequency for i, frequency in enumerate(frequencies) if dft[i] > amplitude_threshold]
    nonzero_dft = [amplitude for amplitude in dft if amplitude > amplitude_threshold]

    return np.array(nonzero_dft), np.array(nonzero_frequencies)


if __name__ == '__main__':
    # Signal parameters
    fs = 48000                  # sample rate, Hz
    time_start = 0              # s
    signal_duration = 1         # s
    n_fft = int(0.01 * fs)      # number of samples for DFT
    t = np.arange(time_start, signal_duration, step=1/fs)

    # Hz to kHz conversion
    divisor = 1000.0
    fs_plot = fs / divisor

    frequencies = [100, 1000, 10000, 38000]
    for f in frequencies:
        # Generation
        s_t = signal(1.0, f, t)

        # Discrete Fourier transform
        dft, frequencies = normalized_dft(s_t, n_fft, fs)

        # Scaling
        frequencies_plot = frequencies / divisor

        # Playing
        attenuation = 0.3
        sd.play(attenuation * s_t, samplerate=fs)

        # Plotting
        plt.figure()
        plt.stem(frequencies_plot, dft, **stem_params)
        plt.hlines(xmin=xlim[0], xmax=xlim[1], y=0, colors='black')
        plt.vlines(0, 0, 1.0)
        plt.yticks([0, 1])
        plt.ylabel('Relative amplitude')
        plt.xlabel('f [kHz]')
        plt.show()