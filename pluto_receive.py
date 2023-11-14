import adi
import numpy as np
import matplotlib.pyplot as plt
from utils.visualization import plot_spectrum, sampling_visualize, constellation_plot_with_threshold
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

# System Parameters
tx_LO_frequency = int(900e6)
rx_LO_frequency = int(900e6)
tx_rx_difference = int(tx_LO_frequency - rx_LO_frequency)
band_pass_filter_bandwidth = int(0.8e6)
bandwidth = int(10e6)
sampling_rate = int(10e6)
number_of_samples = 2**16
Ts = 1 / sampling_rate
# SDR Parameters

sdr = adi.Pluto("ip:192.168.3.1")
sdr.gain_control_mode_chan0 = 'slow_attack'
# sdr.gain_control_mode_chan0 = 'manual'
# sdr.rx_hardwaregain_chan0 = 40
sdr.rx_lo = rx_LO_frequency
sdr.rx_rf_bandwidth = bandwidth
sdr.sample_rate = sampling_rate
sdr.rx_buffer_size = number_of_samples
sdr.tx_hardwaregain_chan0 = -10

#SRRC Generation
P = 16
nOfSL = 6
beta = 0.75
pulse = srrc(syms=nOfSL, beta=beta, P=P)

# ++++++++++++++++++++++ RX +++++++++++++++++++++++++++

for i in range(20):
    rx = sdr.rx()
rx = rx / 2**11
plot_spectrum(rx, Ts)
t = np.arange(0, len(rx) * Ts, Ts)

# # COARSE FREQUENCY CORRECTION
r4th = rx**4
coarse_frequency = (maximum_frequency(r4th, sampling_rate) / 4)
print(f'coarse1 = {coarse_frequency}')
coarse_demodulator = np.exp(-1j * 2 * np.pi * coarse_frequency * t)
coarse_demodulated_baseband_signal = rx * coarse_demodulator
plot_spectrum(coarse_demodulated_baseband_signal, Ts)
plot_spectrum(r4th, Ts)

# BAND SHIFTING BEFORE PHASE CORRECTION
fc = int(2e6)
shifted_before_CL = coarse_demodulated_baseband_signal * np.exp(
    1j * 2 * np.pi * fc * t)
plot_spectrum(shifted_before_CL, Ts)
carrier_est, theta, complex_exp_est = costas_loop_QAM(
    np.real(shifted_before_CL), sampling_rate, 0.2, fc, np.pi / 6, True)
baseband_signal = complex_exp_est * shifted_before_CL
# carrier_est, theta, complex_exp_est = costas_loop_QAM(
#     np.real(rx), sampling_rate, 0.2, fc, np.pi / 6, True)
# baseband_signal = complex_exp_est * rx

plot_spectrum(baseband_signal, Ts)

# MATCHED FILTERING
baseband_signal = signal.convolve(baseband_signal, pulse,
                                  'same') * np.max(pulse)
plot_spectrum(baseband_signal, Ts)

# CLOCK RECOVERY - WITH OUTPUT POWER MAXIMIZATION
tnow = 2 * nOfSL * P
tau1, downsampled_real = clock_recovery_OP_max(
    baseband_signal=np.real(baseband_signal),
    t_now=tnow,
    half_number_of_symbols=nOfSL,
    oversampling_factor=P,
    mu=0.6,
    delta=2,
    beta=beta)
tau2, downsampled_imag = clock_recovery_OP_max(
    baseband_signal=np.imag(baseband_signal),
    t_now=tnow,
    half_number_of_symbols=nOfSL,
    oversampling_factor=P,
    mu=0.6,
    delta=2,
    beta=beta)
downsampled_signal = downsampled_real + 1j * downsampled_imag
sampling_visualize(baseband_signal=baseband_signal,
                   downsampled_signal=downsampled_signal,
                   oversampling_factor=P,
                   half_number_of_symbols=nOfSL,
                   tau1=tau1,
                   tau2=tau2,
                   sampling_display=True,
                   constellation_display=True,
                   signal_and_samples=True)

# QUANTIZATION
quantized_symbols, threshold = quantalph_distance(downsampled_signal,
                                                  np.array([1, 3]))
constellation_plot_with_threshold(downsampled_signal, threshold)

# CORRELATION
correlation_indices, correlation_values = symbol_correlation(
    symbols=quantized_symbols,
    modulation_type="QAM4_2",
    trigger=80,
    header_length=13,
    visualize=True)

# MESSAGE GENERATION
received_message = frame_generator_RX(quantized_symbols=quantized_symbols,
                                      correlation_indices=correlation_indices,
                                      correlation_values=correlation_values,
                                      single_frame_length=365,
                                      header='barker13',
                                      modulation_type='QAM4_2')
print(f'Received Message is:\n{received_message}')
try:
    msg_output = message_handler(received_message, True)
    print(f'Message Output: \n {msg_output}')
except:
    print("From except block")
    plt.show()
else:

    plt.show()
