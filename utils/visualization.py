from numpy import linspace, real, imag, log10, absolute
import matplotlib.pyplot as plt
from utils.oversample import oversample
from sk_dsp_comm.sigsys import my_psd


def plot_spectrum(x, Ts):
    """
    Plot the time-domain signal and its power spectral density (PSD).

    This function takes a complex input signal 'x' and its sampling period 'Ts' and plots
    both the time-domain representation of the signal (real and imaginary parts) and its
    power spectral density (PSD).

    Args:
        x (numpy.ndarray): Input complex signal.
        Ts (float): Sampling period of the signal.

    Returns:
        None

    Note:
        This function utilizes the 'my_psd' function from the 'ss' module to compute the
        power spectral density (PSD) of the input signal 'x'. Make sure the 'ss' module
        is available and the 'my_psd' function is defined before using this function.


    """
    N = len(x)
    fs = 1 / Ts
    t = Ts * linspace(0, N, N, endpoint=False)
    P_r, f = my_psd(x, 2**12, fs)

    fig10, [axx0, axx1] = plt.subplots(2, 1, figsize=(12.8, 9.6))
    fig10.suptitle("Frequency and Time Domain Representation", fontsize=20)

    axx0.plot(t, real(x), label='Real', color='r')
    axx0.plot(t, imag(x), label='Imag', color='b')
    axx0.legend()
    axx0.set_xlabel('t (sec)', fontsize=16)
    axx0.set_ylabel('Amplitude', fontsize=16)
    axx1.plot(f, 10 * log10(P_r))
    axx1.set_xlabel('Frequency (Hz)', fontsize=16)
    axx1.set_ylabel('Magnitude', fontsize=16)
    axx1.set_ylim([-150, 0])
    axx1.grid(True)
    axx0.grid(True)
    fig10.tight_layout()


def plot_response(w, h, title):
    "Utility function to plot response functions"
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(w, 20 * log10(absolute(h)))
    ax.set_ylim(-150, 30)
    ax.grid(True)
    ax.set_xlabel('Frequency (Hz)', fontsize=16)
    ax.set_ylabel('Gain (dB)', fontsize=16)
    ax.set_title(title, fontsize=20)


def constellation_plot(rx):
    """
    Generate a constellation plot for a given set of complex symbols.

    This function generates a constellation plot for a given set of complex symbols 'rx'. The plot
    displays the real part of symbols on the x-axis and the imaginary part on the y-axis.

    Args:
        rx (numpy.ndarray): Array of complex symbols to be plotted.

    Returns:
        None

    Note:
        The function generates a scatter plot of the complex symbols, showing their distribution
        in the complex plane.


    """
    symbols_real = real(rx)
    symbols_imag = imag(rx)
    fig, axs = plt.subplots(1, 1)
    axs.plot(symbols_real, symbols_imag, '.')
    axs.set_title('Constellation Diagram')
    axs.set_ylabel('Q Symbols')
    axs.set_xlabel('I Symbols')
    axs.grid(True)


def constellation_plot_with_threshold(rx, threshold_array):
    """
    Generate a constellation plot with threshold markers for a given set of complex symbols.

    This function generates a constellation plot for a given set of complex symbols 'rx', along with
    threshold markers represented by 'threshold_array'. The plot displays the real part of symbols on
    the x-axis and the imaginary part on the y-axis.

    Args:
        rx (numpy.ndarray): Array of complex symbols to be plotted.
        threshold_array (numpy.ndarray): Array of complex threshold values for reference.

    Returns:
        None

    Note:
        The function generates a scatter plot of the complex symbols and the threshold markers,
        showing their distribution in the complex plane.


    """
    symbols_real = real(rx)
    symbols_imag = imag(rx)
    threshold_real = real(threshold_array)
    threshold_imag = imag(threshold_array)
    fig, axs = plt.subplots(1, 1, figsize=(12.8, 9.6))
    axs.plot(symbols_real, symbols_imag, '.', label='Symbols')
    axs.plot(threshold_real,
             threshold_imag,
             '.r',
             markersize=1,
             label='Threshold')
    axs.legend()
    axs.set_title('Constellation Diagram', fontsize=18)
    axs.set_ylabel('Q Symbols', fontsize=16)
    axs.set_xlabel('I Symbols', fontsize=16)
    axs.grid(True)
    fig.tight_layout()


def sampling_visualize(baseband_signal, downsampled_signal,
                       oversampling_factor, half_number_of_symbols, tau1, tau2,
                       sampling_display, constellation_display,
                       signal_and_samples):

    if sampling_display:
        dsR = real(downsampled_signal)
        dsI = imag(downsampled_signal)

        fig2, axs = plt.subplots(4, 1, figsize=(12.8, 9.6))
        fig2.suptitle("Clock Recovery Algorithm Ouput and Symbols",
                      fontsize=20)

        axs[0].plot(dsR, '.r')
        axs[0].set_title('Real Symbols', fontsize=18)
        axs[0].set_ylabel("Amplitude", fontsize=16)
        axs[0].set_xlabel("Number Of Symbols", fontsize=16)
        axs[0].grid(True)
        axs[1].plot(dsI, '.b')
        axs[1].set_title('Imaginary Symbols', fontsize=18)
        axs[1].set_ylabel("Amplitude", fontsize=16)
        axs[1].set_xlabel("Number Of Symbols", fontsize=16)
        axs[1].grid(True)
        axs[2].plot(tau1)
        axs[2].set_title(' Tau for Real Symbols', fontsize=18)
        axs[2].set_ylabel("Offset estimates", fontsize=16)
        axs[2].set_xlabel("Number Of Symbols", fontsize=16)
        axs[3].plot(tau2)
        axs[3].set_title(' Tau for Imaginary Symbols', fontsize=18)
        axs[3].set_ylabel("Offset estimates", fontsize=16)
        axs[3].set_xlabel("Number Of Symbols", fontsize=16)
        fig2.tight_layout()
        if constellation_display:
            before_quantization = dsR + 1j * dsI
            constellation_plot(before_quantization)
        if signal_and_samples:
            fig4, axs = plt.subplots(2, 1, figsize=(12.8, 9.6))

            fig4.suptitle("Baseband Signal Before and After Sampling",
                          fontsize=20)
            dsRZeroPadded = oversample(dsR, oversampling_factor)
            dsIZeroPadded = oversample(dsI, oversampling_factor)
            axs[0].plot(dsRZeroPadded,
                        'k',
                        marker='.',
                        markersize=3,
                        linestyle='none')
            axs[0].plot(
                real(baseband_signal[2 * half_number_of_symbols *
                                     oversampling_factor + 1::]), 'r')
            axs[0].set_title('Real Signal and Symbols', fontsize=18)
            axs[0].set_ylabel("Amplitude", fontsize=16)
            axs[0].set_xlabel("Number Of Samples", fontsize=16)
            axs[1].plot(dsIZeroPadded,
                        'k',
                        marker='.',
                        markersize=3,
                        linestyle='none')
            axs[1].plot(
                imag(baseband_signal[2 * half_number_of_symbols *
                                     oversampling_factor + 1::]), 'b')
            axs[1].set_title('Imaginary Signal and Symbols', fontsize=18)
            axs[1].set_ylabel("Amplitude", fontsize=16)
            axs[1].set_xlabel("Number Of Samples", fontsize=16)
            fig4.tight_layout()
