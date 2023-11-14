import numpy as np
import matplotlib.pyplot as plt
from utils.visualization import plot_spectrum, constellation_plot_with_threshold, sampling_visualize
from utils.pulse_shape import srrc
from scipy import signal
from receiver_module.frame_generator_RX import frame_generator_RX
from receiver_module.symbol_correlation import symbol_correlation
from receiver_module.quantization import quantalph_distance
from adaptive_algorithms.costas_loop import costas_loop_QAM
from receiver_module.message_handler import message_handler
from utils.maximum_frequency import maximum_frequency
from adaptive_algorithms.costas_loop import costas_loop_QAM
from adaptive_algorithms.clock_recovery import clock_recovery_OP_max
from utils.my_radio import MyRadio
"""
    Perform signal processing operations on received samples and extract messages.

    Args:
        my_SDR (MyRadio): Custom software-defined radio object.
        plot_graphs (bool): Flag to indicate whether to plot intermediate graphs.

    Returns:
        str: Extracted and reconstructed message.
    """


def operation_RX(my_SDR: MyRadio, plot_graphs: bool):

    #Correlation
    TRIGGER = 80
    HEADER_LENGTH = 13
    FRAME_LENGTH_SYMBOLS = 365

    #SRRC Generation
    OVERSAMPLING_RATE = 16
    HALF_NO_OF_SYMBOLS = 6
    ROLLOFF_FACTOR = 0.75
    Ts = 1 / my_SDR.sample_rate
    sampling_rate = my_SDR.sample_rate
    pulse = srrc(syms=HALF_NO_OF_SYMBOLS,
                 beta=ROLLOFF_FACTOR,
                 P=OVERSAMPLING_RATE)

    # ++++++++++++++++++++++ RX +++++++++++++++++++++++++++

    rx = my_SDR.receive_samples()
    t = np.arange(0, len(rx) * Ts, Ts)

    # COARSE FREQUENCY CORRECTION
    r4th = rx**4
    coarse_frequency = (maximum_frequency(r4th, sampling_rate) / 4)
    # print(f'coarse1 = {coarseF}')
    coarse_demodulated = np.exp(-1j * 2 * np.pi * coarse_frequency * t)
    coarse_baseband = rx * coarse_demodulated

    # BAND SHIFTING BEFORE PHASE CORRECTION
    fc = int(2e6)
    shifted_before_CL = coarse_baseband * np.exp(1j * 2 * np.pi * fc * t)

    carrier_est, theta, complex_exp_est = costas_loop_QAM(
        np.real(shifted_before_CL), sampling_rate, 0.2, fc, np.pi / 6,
        plot_graphs)
    baseband_signal = complex_exp_est * shifted_before_CL

    # MATCHED FILTERING
    matched_filtered_baseband = signal.convolve(baseband_signal, pulse,
                                                'same') * np.max(pulse)

    # CLOCK RECOVERY - WITH OUTPUT POWER MAXIMIZATION
    tnow = 2 * HALF_NO_OF_SYMBOLS * OVERSAMPLING_RATE
    tau1, downsampled_real = clock_recovery_OP_max(
        baseband_signal=np.real(matched_filtered_baseband),
        t_now=tnow,
        half_number_of_symbols=HALF_NO_OF_SYMBOLS,
        oversampling_factor=OVERSAMPLING_RATE,
        mu=0.6,
        delta=2,
        beta=ROLLOFF_FACTOR)
    tau2, downsampled_imag = clock_recovery_OP_max(
        baseband_signal=np.imag(matched_filtered_baseband),
        t_now=tnow,
        half_number_of_symbols=HALF_NO_OF_SYMBOLS,
        oversampling_factor=OVERSAMPLING_RATE,
        mu=0.6,
        delta=2,
        beta=ROLLOFF_FACTOR)
    downsampled_signal = downsampled_real + 1j * downsampled_imag

    # QUANTIZATION
    quantized_symbols, threshold = quantalph_distance(downsampled_signal,
                                                      np.array([1, 3]))

    # CORRELATION
    correlation_indices, correlation_values = symbol_correlation(
        symbols=quantized_symbols,
        modulation_type="QAM4_2",
        trigger=TRIGGER,
        header_length=HEADER_LENGTH,
        visualize=plot_graphs)
    if plot_graphs:
        plot_spectrum(rx, Ts)
        plot_spectrum(coarse_baseband, Ts)
        plot_spectrum(r4th, Ts)
        plot_spectrum(shifted_before_CL, Ts)
        plot_spectrum(baseband_signal, Ts)
        plot_spectrum(matched_filtered_baseband, Ts)
        sampling_visualize(baseband_signal=matched_filtered_baseband,
                           downsampled_signal=downsampled_signal,
                           oversampling_factor=OVERSAMPLING_RATE,
                           half_number_of_symbols=HALF_NO_OF_SYMBOLS,
                           tau1=tau1,
                           tau2=tau2,
                           sampling_display=True,
                           constellation_display=False,
                           signal_and_samples=True)
        constellation_plot_with_threshold(downsampled_signal, threshold)
    # MESSAGE GENERATION
    try:
        received_message = frame_generator_RX(
            quantized_symbols=quantized_symbols,
            correlation_indices=correlation_indices,
            correlation_values=correlation_values,
            single_frame_length=FRAME_LENGTH_SYMBOLS,
            header='barker13',
            modulation_type='QAM4_2')
        message_output = message_handler(received_message,
                                         display_outputs=False)
        return message_output
    except:
        pass
