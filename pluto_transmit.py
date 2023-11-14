import adi
import matplotlib.pyplot as plt
from  transmission_module.signal_generator_TX import signal_generator
from  transmission_module.frame_generator_TX import frame_generator_TX
from utils.visualization import plot_spectrum


# PLUTO SDR Setup
sdr = adi.Pluto('ip:192.168.3.1')
loFreq = int(900e6)
sampleRate = int(10e6)
bandwidth = int(10e6)
txGain = -5
sdr.tx_lo = loFreq
sdr.tx_rf_bandwidth = bandwidth
sdr.sample_rate = sampleRate
sdr.tx_hardwaregain_chan0 = txGain
sdr.tx_cyclic_buffer = True
Ts = 1 / sampleRate
tx_len = int(2**18)

#PULSE
N = 16
syms = 6
beta = 0.75
msg1 = "This is the end Hold your breath and count to ten Feel the Earth move and then Hear my heart burst again For this is the end I've drowned and dreamt this moment So overdue, I owe them Swept away, I'm stolen Let the sky fall When it crumbles We will stand tall Face it all together Let the sky fall When it crumbles We will stand tall Face it all together At Skyfall At Skyfall"
msg4 = "Gründlich durchgecheckt steht sie da Und wartet auf den Start, alles klar! Experten streiten sich Um ein paar Daten Die Crew hat da noch Ein paar Fragen doch Der Countdown läuft Effektivität bestimmt das Handeln Man verlässt sich blind Auf den ander'n Jeder weiß genau Was von ihm abhängt Jeder ist im Stress Doch Major Tom Macht einen Scherzaaaa"
msg5 = "Hello World!"
msg6 = "I'd sit alone and watch your light My only friend through teenage nights And everything I had to know I heard it on my radio So don't become some background noise A backdrop for the girls and boys Who just don't know, or just don't care And just complain when you're not there You had your time, you had the power You've yet to have your finest hour Radio (radio) All we hear is radio ga ga Radio goo goo Radio ga ga Radio, what's new? Radio, someone still loves you"
msg7 = "Hello from user1"
data_length = 80
msg = msg6
print(f'Message Character Length = {len(msg)}')

### FRAME GENERATION
my_frames, single_frame_length, my_header, data_length_with_id = frame_generator_TX(
    data_length=data_length,
    text_message=msg,
    header_type='barker13',
    modulation_type='QAM4_2',
    info=False)
print(f'Appended Symbol Frames Length = {len(my_frames)}')
print(f'Symbol Frames = {my_frames[:50]}')

### SIGNAL GENERATION
my_signal = signal_generator(symbol_frames=my_frames,
                             buffer_len_TX=tx_len,
                             oversampling_rate=N,
                             half_number_of_symbols=syms,
                             beta=beta,
                             signal_or_symbols=1,
                             visualize=True,
                             print_data=False)

plt.tight_layout()
my_signal = my_signal[:tx_len]
print(my_signal[:-100])
print(len(my_signal))
plot_spectrum(my_signal,Ts)

### SIGNAL SCALING, TRANSMISSION AND DISPLAY
my_signal = my_signal * 2**14

print(
    f'LO Freq = {loFreq}\nSample Rate = {sampleRate}\nGain = {txGain}\nPlutoSDR Tx Buffer Sample Size = {tx_len}\nNof SPS = {N}\nNof Sidelobes ={syms} \nbeta = {beta}\nData Length = {data_length}\nOne Frame Length ={single_frame_length}\nDataLenWithId = {data_length_with_id}\nHeader ={my_header}'
)
sdr.tx(my_signal)

plt.show()
