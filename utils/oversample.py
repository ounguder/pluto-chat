from numpy import zeros

"""
    Oversample the input array by inserting M-1 zeros between each pair of elements.

    This function performs oversampling on the input 'my_array' by inserting M-1 zeros between
    each pair of adjacent elements, effectively increasing the sampling rate.

    Args:
        my_array (numpy.ndarray): Input array to be oversampled.
        M (int): Oversampling factor.

    Returns:
        numpy.ndarray: Oversampled array with M times the original length.

    Example:
        original_data = np.array([1, 2, 3, 4])   # Input array
        oversampling_factor = 3                   # Oversampling factor
        oversampled_data = oversample(original_data, oversampling_factor)
        # Returns [1, 0, 0, 2, 0, 0, 3, 0, 0, 4] for the given oversampling factor of 3
    """

def oversample(my_array, M):

    N = len(my_array)
    oversampled_array = zeros(N * M)
    oversampled_array[::M] = my_array
    return oversampled_array