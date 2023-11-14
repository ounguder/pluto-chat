from numpy import min, max, abs, zeros, exp, arange, sign, real, imag, pi,angle
"""
    The quantalph_distance function quantizes a set of symbols based on a given alphabet. It calculates the distance between the minimum and maximum 
    values in the alphabet and uses this distance to determine a threshold. Symbols within this threshold are quantized to the minimum values in the 
    alphabet, while symbols outside the threshold are quantized to the maximum values.

    Args:
        symbol_array (numpy.ndarray): Array of symbols to be quantized.
        alphabet (numpy.ndarray): Coded alphabet used for quantization.

    Returns:
        tuple: A tuple containing:
             numpy.ndarray: Quantized symbols.
             numpy.ndarray: Threshold array used for quantization.
    """


def quantalph_distance(symbol_array, alphabet):
    # symbolArray = downsampled symbols
    # alphabet = coded alphabet, it should be pass with symbols values which are greater than zero
    # distance = the distance on I and Q axis between the max and min QAM4_2 symbols
    # threshold = this is equal to the 1/4 of the total distance. This distance in the IQ axis is considered as a circle whose diameter is equal to the distance
    ## the radius of that circle is equal to distance/4. this radius is divided into 6 equal points and the distance of the third point to the origin is set as threshold
    min_alphabet = min(alphabet)
    max_alphabet = max(alphabet)
    min_point = min(symbol_array)
    max_point = max(symbol_array)
    distance = abs(min_point) + abs(max_point)
    threshold = 1 * distance / 4
    quantized_symbols = zeros(len(symbol_array), dtype=complex)
    threshold_array = threshold * exp(
        1j * 2 * pi * arange(0, 1, 1 / len(symbol_array)))
    for i in range(len(symbol_array)):
        if abs(symbol_array[i]) < threshold:
            quantized_symbols[i] = sign(real(
                symbol_array[i])) * min_alphabet + 1j * sign(
                    imag(symbol_array[i])) * min_alphabet
        else:
            quantized_symbols[i] = sign(real(
                symbol_array[i])) * max_alphabet + 1j * sign(
                    imag(symbol_array[i])) * max_alphabet
    return quantized_symbols, threshold_array
  
    
