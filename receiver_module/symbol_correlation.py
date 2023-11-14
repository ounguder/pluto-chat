from numpy import real, imag, correlate, zeros, ndenumerate, abs, trim_zeros
import matplotlib.pyplot as plt
from utils.barker_generator import barker_generator
"""
    The symbol_correlation function calculates the correlation between received symbols and a specified header sequence for both
    the real and imaginary parts. If the correlation values exceed a specified trigger threshold, they are considered for further 
    processing. The function returns the indices and corresponding correlation values for further analysis.

    Args:
        symbols (numpy.ndarray): Received symbols to be correlated.
        modulation_type (str): Modulation type ('QAM', 'QAM4_2', etc.).
        trigger (float): Threshold for considering correlation values.
        header_length (int): Length of the header sequence.
        visualize (bool): Flag to indicate whether to display correlation plots.

    Returns:
        tuple: A tuple containing:
            numpy.ndarray: Correlation indices (complex numbers representing positions in the array).
            numpy.ndarray: Correlation values (complex numbers representing correlation strengths).
    """


def symbol_correlation(symbols, modulation_type, trigger, header_length,
                       visualize):

    header = barker_generator(barker_type=f'barker{header_length}',
                              modulation_type=modulation_type)

    real_symbols = real(symbols)
    imag_symbols = imag(symbols)
    header_real = real(header)
    header_imag = imag(header)
    correlation_real = correlate(real_symbols, header_real, 'full')
    correlation_imag = correlate(imag_symbols, header_imag, 'full')
    imag_correlation_indices = zeros(80)
    imag_correlation_values = zeros(80)
    real_correlation_indices = zeros(80)
    real_correlation_values = zeros(80)
    i = 0
    k = 0

    for index, value in ndenumerate(correlation_real):

        if abs(value) >= trigger:
            real_correlation_indices[i] = index[0]
            real_correlation_values[i] = value
            i += 1

    for index, value in ndenumerate(correlation_imag):

        if abs(value) >= trigger:
            imag_correlation_indices[k] = index[0]
            imag_correlation_values[k] = value
            k += 1

    if visualize:
        print(f'Header = {header}')
        fig2, axs = plt.subplots(2, 1, figsize=(12.8, 9.6))
        fig2.suptitle('Correlation Output of Real and Imaginary Symbols',
                      fontsize=20)
        axs[0].stem(correlation_real, 'r')
        axs[0].set_title("Real Part Correlation Output", fontsize=18)
        axs[0].grid(True)
        axs[0].set_ylabel("Correlation Value", fontsize=16)
        axs[0].set_xlabel("Number Of Symbols", fontsize=16)
        axs[1].stem(correlation_imag, 'b')
        axs[1].grid(True)
        axs[1].set_title("Imaginary Part Correlation Output", fontsize=18)
        axs[1].set_ylabel("Correlation Value", fontsize=16)
        axs[1].set_xlabel("Number Of Symbols", fontsize=16)
        fig2.tight_layout()
    correlation_indices = trim_zeros(
        real_correlation_indices + 1j * imag_correlation_indices, 'b')
    correlation_values = trim_zeros(
        real_correlation_values + 1j * imag_correlation_values, 'b')

    return correlation_indices, correlation_values
