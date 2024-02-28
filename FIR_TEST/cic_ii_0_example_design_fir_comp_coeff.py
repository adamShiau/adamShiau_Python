import numpy as np
from scipy.signal import firwin2, freqz
import matplotlib.pyplot as plt

def cic_ii_0_example_design_fir_comp_coeff(L=None, Fs=None, Fc=None, plot=False, is_fxp=True, B=16):
    try:
        # CIC filter parameters
        R = 32000  # Decimation factor
        M = 1  # Differential delay
        N = 12  # Number of stages

        # User Parameters
        if L is None:
            L = 31  # Default filter length
        if L % 2 == 0:
            print(f"FIR filter length must be an odd number. {L + 1} is used instead.")
            L += 1

        if Fs is None:
            Fs = 80e6  # Default sample rate before decimation
        if Fc is None:
            Fc = 4e6  # Default cutoff frequency

        if is_fxp and B is None:
            B = 16  # Default number of bits for fixed point coefficients

        # Normalized cutoff frequency
        Fo = R * Fc / Fs

        # CIC Compensator Design using firwin2
        p = 2e3
        s = 0.25 / p
        fp = np.arange(0, Fo + s, s)
        fs = np.arange(Fo + s, 0.5, s)
        f = np.concatenate((fp, fs)) * 2

        Mp = np.ones(len(fp))
        Mp[1:] = np.abs(M * R * np.sin(np.pi * fp[1:] / R) / np.sin(np.pi * M * fp[1:])) ** N
        Mf = np.concatenate((Mp, np.zeros(len(fs))))
        f[-1] = 1

        # Design FIR filter coefficients using firwin2
        h = firwin2(L, f, Mf)
        h /= np.max(h)  # Normalize coefficients

        # Output filter coefficients to a file
        filename = 'cic_ii_0_example_design_fir_comp_coeff.txt'
        with open(filename, 'wt') as f:
            if is_fxp:
                hz = np.round(h * (2 ** (B - 1) - 1))
                np.savetxt(f, hz, fmt='%d')
            else:
                np.savetxt(f, h, fmt='%.6f')

        print(f"The compensation filter coefficients have been saved to file '{filename}'.")

        # Plot filter responses if required
        if plot:
            plot_responses(R, M, N, h if is_fxp else f, Fs, is_fxp)

    except Exception as e:
        raise e

# Function for plotting filter responses
def plot_responses(R, M, N, res, Fs, is_fxp):
    try:
        # Full resolution CIC filter response
        hrec = np.ones(R * M)
        tmph = hrec
        for k in range(N - 1):
            tmph = np.convolve(hrec, tmph)
        hcic = tmph / np.max(tmph)

        # Total Response
        resp = np.repeat(res, R)
        ht = np.convolve(hcic, resp)

        # Frequency response
        no_data_points = 4096
        wt, Hcic = freqz(hcic, 1, no_data_points, fs=Fs)
        wt, Hciccomp = freqz(resp, 1, no_data_points, fs=Fs)
        wt, Ht = freqz(ht, 1, no_data_points, fs=Fs)

        # Check for complex values and discard imaginary parts
        # Hcic = np.real(Hcic)
        # Hciccomp = np.real(Hciccomp)
        # Ht = np.real(Ht)

        # Mcic = np.where(Hcic != 0, 20 * np.log10(np.abs(Hcic) / np.abs(Hcic[0])), 0)
        # Mciccomp = np.where(Hciccomp != 0, 20 * np.log10(np.abs(Hciccomp) / np.abs(Hciccomp[0])), 0)
        # Mt = np.where(Ht != 0, 20 * np.log10(np.abs(Ht) / np.abs(Ht[0])), 0)
        Mcic = 20 * np.log10(np.abs(Hcic) / np.abs(Hcic[0]))
        Mciccomp = 20 * np.log10(np.abs(Hciccomp) / np.abs(Hciccomp[0]))
        Mt = 20 * np.log10(np.abs(Ht) / np.abs(Ht[0]))
        print(wt)
        print(Mcic)
        print(Mciccomp)
        print(Mt)
        plt.figure()
        plt.plot(wt, Mcic, wt, Mciccomp, wt, Mt)
        if is_fxp:
            plt.legend(['CIC', 'CIC Comp', 'Total Response (Fixed Point)'])
        else:
            plt.legend(['CIC', 'CIC Comp', 'Total Response (Floating Point)'])
        plt.ylim([-100, 2])
        plt.title('CIC and its Compensation Filter Responses')
        plt.grid(True)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Filter Magnitude Response (dB)')
        plt.show()
    except Exception as e:
        raise e

if __name__ == '__main__':
    cic_ii_0_example_design_fir_comp_coeff(Fc=500 ,plot=True)
