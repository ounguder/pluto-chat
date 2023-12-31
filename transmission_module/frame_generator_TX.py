import numpy as np
from utils.symbol_conversion import letters_to_pam, pam_to_qam4_2, pam_to_qam
from utils.barker_generator import barker_generator
"""
Function description:
        This function takes the arguments below so that it can generate symbol frames.data_length parameter defines the number of characters in a frame. According to that number
    text_message is subdivided into text strings except last frame. Last frame is generated by the remaning set of characters in the text_message after division.

        For each frame, in order to identify it on the receiver side, a prefix and a suffix is prepended and appended respectively. Those prefix and suffix are integer 
    number represented in hexadecimal string format with prefix `0X`.After that prefix and suffix is added to the text string, it is converted into symbols depending
    on the modulation_type. As first operation at this stage, characters are converted into binary format and then 4PAM symbols. For QAM4_2 and 4QAM, 4PAM symbols are mapped over related symbols.

        At the end, barker_code is prepended to each symbol frame and each individual frames appended together

        There are 3 cases check in the function. Those are
            First case; where text_message is longer than data_length. For this case, text is cut into strings with respect to the data_length variable
            Second case; where length of the message_text is equal to data_length variable
                For this case, prefix and suffix is added to the string and conversion into symbols is performed
            Last case; where message_text is shorter than data_length
                For this case, in addition to the prefix and suffix, empty positions in the frame is filled with a sequence such as `ABCDEF...67890` depending on the remained position quantity

Args:
        data_length (int): Length of each data frame.
        text_message (str): Text message to be transmitted.
        header_type (str): Type of header to be added to each frame.
        modulation_type (str): Modulation type for encoding symbols (e.g., "4QAM", "QAM4_2").
        info (bool): Flag indicating whether to display additional information.

    Returns:
        Tuple[np.ndarray, int, np.ndarray, int]: Tuple containing:
            symbol_frames (np.ndarray): Generated symbol frames for transmission.
            single_frame_length (int): Length of a single frame in symbols.
            header (np.ndarray): Header symbols used in the frames.
            data_length_with_id (int): Length of data frames with ID and header symbols.
    """


def frame_generator_TX(data_length, text_message, header_type, modulation_type,
                       info):
    mod_type = modulation_type
    data_length = data_length
    msg = text_message
    single_frame_length = 0
    header = barker_generator(header_type, modulation_type=mod_type)
    message_length = len(msg)
    number_of_data_frames, remainder = np.divmod(message_length, data_length)
    symbols_per_char = 4
    id_length_in_char = 4
    id_len_in_symbols = id_length_in_char * symbols_per_char
    data_length_with_id = id_length_in_char + data_length + id_length_in_char

    last_data_length_with_id = id_length_in_char + remainder + id_length_in_char
    symbol_frames = np.array([], dtype=complex)
    encoding = "ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890"

    if len(msg) > data_length:
        single_frame_length = len(
            header
        ) + id_len_in_symbols + data_length * symbols_per_char + id_len_in_symbols
        for i in range(number_of_data_frames + 1):
            if i == number_of_data_frames:
                data = f'{i:#04X}' + msg[i * data_length:(
                    (i) * data_length + remainder)] + f'{i:#04X}'
                for i in range(data_length_with_id - last_data_length_with_id):
                    data = data + encoding[i]
                # print(data)
                if mod_type == '4QAM':
                    data_symbols = pam_to_qam(letters_to_pam(data))
                elif mod_type == 'QAM4_2':
                    data_symbols = pam_to_qam4_2(letters_to_pam(data))
                else:
                    data_symbols = letters_to_pam(data)
                data_symbols_with_barker = np.append(header, data_symbols)
            else:
                data = f'{i:#04X}' + msg[i * data_length:(
                    (i + 1) * data_length)] + f'{i:#04X}'
                if mod_type == '4QAM':
                    data_symbols = pam_to_qam(letters_to_pam(data))
                elif mod_type == 'QAM4_2':
                    data_symbols = pam_to_qam4_2(letters_to_pam(data))
                else:
                    data_symbols = letters_to_pam(data)
                data_symbols_with_barker = np.append(header, data_symbols)

            if info:
                print(f'Data frame is generated: {data}')

            symbol_frames = np.append(symbol_frames, data_symbols_with_barker)

    elif len(msg) == data_length:
        single_frame_length = len(
            header
        ) + id_len_in_symbols + data_length * symbols_per_char + id_len_in_symbols
        data = f'{0:#04X}' + msg + f'{0:#04X}'
        if info:
            print(data)
        if mod_type == '4QAM':
            data_symbols = pam_to_qam(letters_to_pam(data))
        elif mod_type == 'QAM4_2':
            data_symbols = pam_to_qam4_2(letters_to_pam(data))
        else:
            data_symbols = letters_to_pam(data)
        data_symbols_with_barker = np.append(header, data_symbols)
        symbol_frames = data_symbols_with_barker

    else:
        single_frame_length = len(
            header
        ) + id_len_in_symbols + data_length * symbols_per_char + id_len_in_symbols
        data = f'{0:#04X}' + msg + f'{0:#04X}'
        for i in range(data_length - remainder):
            data = data + encoding[i]
        if info:
            print(data)
        if mod_type == '4QAM':
            data_symbols = pam_to_qam(letters_to_pam(data))
        elif mod_type == 'QAM4_2':
            data_symbols = pam_to_qam4_2(letters_to_pam(data))
        else:
            data_symbols = letters_to_pam(data)
        data_symbols_with_barker = np.append(header, data_symbols)
        symbol_frames = data_symbols_with_barker

    return symbol_frames, single_frame_length, header, data_length_with_id
