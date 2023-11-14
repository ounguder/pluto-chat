from numpy import array, append, zeros, hstack, flipud, isin, max, any
from math import ceil
"""
    Process received messages, extract headers and messages, and reconstruct the complete message.

    Args:
        received_message (str): Received message as a string.
        display_outputs (bool): Flag to display intermediate outputs.

    Returns:
        str: Reconstructed complete message.
    """

FRAME_FILLER = "00ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890"


def message_handler(received_message, display_outputs: bool):

    split_array = received_message.split('0X')
    id_array = array([], dtype=int)
    frame_array = array([], dtype=str)
    id_and_substrings = array([], dtype=tuple)
    equal_flag = False

    for idx in range(len(split_array)):
        if (idx <= len(split_array) - 2) and (split_array[idx] != ''):
            if (split_array[idx][:2] == split_array[idx + 1][:2]) and (
                    not (split_array[idx] in FRAME_FILLER)):
                substring = split_array[idx]
                frame_array = append(frame_array, substring)
            else:
                pass
                

    for idx in range(len(frame_array)):
        if idx != len(frame_array) - 1:
            current_substring = frame_array[idx]
            next_substring = frame_array[idx + 1]
            try:
                current_id = int("0X" + current_substring[:2], 16)
            except:
                continue
            else:
                next_id = int("0X" + next_substring[:2], 16)
            if not equal_flag:
                if current_id != next_id:
                    id_array = append(id_array, current_id)
                    trimmed_string = current_substring[2:]
                    id_and_substrings = append(
                        id_and_substrings, tuple([current_id, trimmed_string]))
                else:
                    equal_flag = True
            else:
                previous_substring = frame_array[idx - 1]
                try:
                    previous_id = int("0X" + previous_substring[:2], 16)
                except:
                    continue
                else:
                    id_array = append(id_array, previous_id)
                    trimmed_prev_string = previous_substring[2:]
                    id_and_substrings = append(
                        id_and_substrings,
                        tuple([previous_id, trimmed_prev_string]))
                    equal_flag = False
        else:
            if not equal_flag:
                current_substring = frame_array[idx]
                try:
                    current_id = int("0X" + current_substring[:2], 16)
                except:
                    continue
                else:
                    id_array = append(id_array, current_id)
                    trimmed_string = current_substring[2:]
                    id_and_substrings = append(
                        id_and_substrings, tuple([current_id, trimmed_string]))
            else:
                current_substring = frame_array[idx - 1]
                try:
                    current_id = int("0X" + current_substring[:2], 16)
                except:
                    continue
                else:
                    id_array = append(id_array, current_id)
                    trimmed_string = current_substring[2:]
                    id_and_substrings = append(
                        id_and_substrings, tuple([current_id, trimmed_string]))

    max_id = max(id_array)
    id_and_substrings_len = len(id_and_substrings)
    storage_matrix_columns = max_id + 1
    storage_matrix_rows = ceil(
        id_and_substrings_len / 2 / storage_matrix_columns) + 1
    message_storage_matrix = zeros(
        (storage_matrix_rows, storage_matrix_columns), dtype=object)
    row_counter = 0
    for i in range(0, id_and_substrings_len - 1, 2):
        prefix = int(id_and_substrings[i])
        if i != id_and_substrings_len - 2:
            next_prefix = int(id_and_substrings[i + 2])
        else:
            next_prefix = prefix
        text_part = id_and_substrings[i + 1]

        if prefix <= max_id:
            message_storage_matrix[row_counter, prefix] = text_part
            if (prefix == max_id) or (abs(next_prefix - prefix) > 1):
                row_counter += 1

    final_message = zeros(max_id + 1, dtype=object)
    flipped_storage_matrix = flipud(message_storage_matrix)
    row_text_vector = hstack(flipped_storage_matrix)
    row_vector_len = len(row_text_vector)
    message_part_counter = 0
    for i in range(row_vector_len):
        message_partition = row_text_vector[i]
        if (not any(isin(final_message, message_partition))) and (
                message_part_counter <= max_id) and (
                    message_partition != '0') and (not (message_partition[:5]
                                                        in FRAME_FILLER)):
            final_message[message_part_counter] = str(message_partition)
            message_part_counter += 1
    if display_outputs:
        print(f'splitArray:\n {split_array}')
        print(f'frameArray:\n {frame_array}')
        print(f'idAndText Array: \n {id_and_substrings}')
        print(f'msgStorage Array: \n {message_storage_matrix}')
        print(f'flippedArray: \n {flipped_storage_matrix}')
        print(f'rowTextVector: \n {row_text_vector}')

    message_output = "".join(final_message)
    return message_output
