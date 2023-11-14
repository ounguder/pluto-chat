from numpy import real, imag, sign
from utils.symbol_conversion import pam_to_letters, qam_to_pam, qam4_2_to_pam
from utils.barker_generator import barker_generator

### FUNCTION DESCRIPTION
""" 
This function takes the arguments below so that it can detect where each frame starts by iterating over an array which holds indices of correlation output where it peaks.
Each individual frame is trimmed with respect to starting index and end index. end_index is calculated by substracting the header length from the next index value.
Phase Ambiguity reveals itself at the correlation output values. When a phase shift by 90 degrees occurs, value of the correlation negated. Therefore, sign of an individual
correlation value is used to eliminate phase ambiguity by multiplication of sign and following symbols.Depending on the modulation type, trimmed frames are converted into the characters. After
each iteration, generated strings are appended to an empty message variable called `my_msg`

Args:
        quantized_symbols (numpy.ndarray): Quantized symbols received from the communication channel.
        correlation_indices (numpy.ndarray): Indices of correlation peaks in the received signal.
        correlation_values (numpy.ndarray): Values of correlation peaks in the received signal.
        single_frame_length (int): Length of a single frame.
        header (str): Header used for frame synchronization.
        modulation_type (str): Modulation type used for transmission ('4QAM', 'QAM4_2', etc.).

    Returns:
        my_msg (str): A string representing the generated message after processing the input symbols
                    based on correlation indices, values, and modulation type.


"""


def frame_generator_RX(quantized_symbols, correlation_indices,
                       correlation_values, single_frame_length, header,
                       modulation_type):
    header_len = len(barker_generator(header, modulation_type))
    frame_len = single_frame_length
    mod_type = modulation_type
    my_msg = ""
    len_of_index_array = len(correlation_indices)
    for idx in range(len_of_index_array):
        index_real = int(real(correlation_indices[idx]))
        index_imag = int(imag(correlation_indices[idx]))
        value_real = sign(real(correlation_values[idx]))
        value_imag = sign(imag(correlation_values[idx]))
        starting_index_real = index_real + 1
        starting_index_imag = index_imag + 1
        if idx != len_of_index_array - 1:
            next_index_real = int(real(correlation_indices[idx + 1]))
            next_index_imag = int(imag(correlation_indices[idx + 1]))
            end_index_real = next_index_real - header_len + 1
            end_index_imag = next_index_imag - header_len + 1
        else:
            end_index_real = starting_index_real + frame_len - header_len
            end_index_imag = starting_index_imag + frame_len - header_len
        symbols_real = real(
            quantized_symbols[starting_index_real:end_index_real]) * value_real
        symbols_imag = imag(
            quantized_symbols[starting_index_imag:end_index_imag]) * value_imag
        symbols = symbols_real + 1j * symbols_imag
        if mod_type == '4QAM':
            msg = pam_to_letters(qam_to_pam(symbols))
        elif mod_type == 'QAM4_2':
            msg = pam_to_letters(qam4_2_to_pam(symbols))
        else:
            msg = pam_to_letters(symbols)
        my_msg += msg
    return my_msg
