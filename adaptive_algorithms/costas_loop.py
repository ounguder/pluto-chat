from scipy.signal import remez, freqz
from numpy import append, fliplr, matmul, pi, zeros, arange, cos, exp
from utils.visualization import plot_response
from matplotlib.pyplot import subplots
"""
    Perform carrier frequency and phase offset estimation using Costas loop for QAM signals.

    Args:
        rx (numpy.ndarray): Received signal.
        fs (float): Sampling frequency of the received signal.
        mu (float): Step size for phase update in the Costas loop.
        estimated_frequency (float): Estimated carrier frequency of the received signal.
        theta_init (float): Initial phase offset estimation.
        display_output (bool): Flag to display intermediate plots and outputs.

    Returns:
        tuple: A tuple containing:
        carrier_estimation (numpy.ndarray):     Estimated carrier signal.
        theta (numpy.ndarray):                  Estimated phase offset.
        complex_exp_estimation (numpy.ndarray): Estimated complex exponential signal.

    Note:
        This function utilizes a Costas loop for carrier frequency and phase offset estimation in QAM signals.
    
    Resource:
        C. R. Johnson Jr, W. A. Sethares, and A. G. Klein, "A Digital Quadrature Amplitude
        Modulation Radio", in Software Receiver Design: Build your Own Digital Communication 
        System in Five Easy Steps. Cambridge University Press, Aug. 2011,ch. 16, pp. 367-371.
    """


def costas_loop_QAM(rx, fs, mu, estimated_frequency, theta_init,
                    display_output):
    r = rx
    f0 = estimated_frequency
    Ts = 1 / fs
    nyquist_freq = fs / 2
    N = len(rx)
    time = N * Ts
    t = arange(0, time, Ts)
    fl = 201
    cut_off_freq = 0.4 * nyquist_freq
    start_freq = 0.3 * nyquist_freq
    ff = [0, start_freq, cut_off_freq, nyquist_freq]
    fa = [1, 0]
    taps = remez(fl, ff, fa, fs=fs)
    wBP, hBP = freqz(taps, [1], worN=1048, fs=fs)

    taps = taps.reshape((1, len(taps)))
    theta = zeros(len(t))
    theta[0] = theta_init
    q = fl
    z1 = zeros(q)
    z2 = zeros(q)
    z3 = zeros(q)
    z4 = zeros(q)
    carrier_estimation = zeros(N)
    complex_exp_estimation = zeros(N, dtype=complex)

    for k in range(len(t) - 1):
        s = 2 * r[k]
        z1 = append(z1[1:len(z1) + 1], s * cos(2 * pi * f0 * t[k] + theta[k]))
        z2 = append(z2[1:len(z2) + 1],
                    s * cos(2 * pi * f0 * t[k] + pi / 4 + theta[k]))
        z3 = append(z3[1:len(z3) + 1],
                    s * cos(2 * pi * f0 * t[k] + pi / 2 + theta[k]))
        z4 = append(z4[1:len(z4) + 1],
                    s * cos(2 * pi * f0 * t[k] + 3 * pi / 4 + theta[k]))
        lpf1 = matmul(fliplr(taps), z1.reshape((len(z1), 1)))
        lpf2 = matmul(fliplr(taps), z2.reshape((len(z2), 1)))
        lpf3 = matmul(fliplr(taps), z3.reshape((len(z3), 1)))
        lpf4 = matmul(fliplr(taps), z4.reshape((len(z4), 1)))
        theta[k + 1] = (theta[k] +
                        mu * lpf1[0, 0] * lpf2[0, 0] * lpf3[0, 0] * lpf4[0, 0])

        carrier_estimation[k] = cos((2 * pi * f0 * t[k] + theta[k]))
        complex_exp_estimation[k] = exp(
            -1j * (2 * pi * estimated_frequency * t[k] + theta[k]))
    if display_output:
        plot_response(wBP, hBP, "LP Filter for Costas Loop")

        fig5, axs = subplots(2, 1, figsize=(12.8, 9.6))
        fig5.suptitle("Costas Loop Phase Recovery", fontsize=20)
        axs[0].plot(t, theta)
        axs[0].set_title("Theta", fontsize=18)
        axs[0].set_ylabel("Phase Offset", fontsize=16)
        axs[0].set_xlabel("t (s)", fontsize=16)
        axs[1].plot(t, carrier_estimation)
        axs[1].set_title('Estimated Carrier', fontsize=18)
        axs[1].set_ylabel("Amplitude", fontsize=16)
        axs[1].set_xlabel("t (s)", fontsize=16)
        fig5.tight_layout()
    return carrier_estimation, theta, complex_exp_estimation
