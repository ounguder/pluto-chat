from numpy import zeros
from scipy.signal import remez


def generate_filter(fs, filter_type, center_freq, bandwidth, transition_width,
                    number_of_taps):
    """
    Generate a filter tap array using the Remez algorithm for various filter types.

    This function generates a filter tap array using the Remez algorithm for either a low-pass
    or a band-pass filter. The filter type, center frequency, bandwidth, transition width,
    and number of taps are specified as inputs.

    Parameters:
    filter_type (str): Type of filter ('lp' for low-pass, 'bp' for band-pass).
    center_freq (float): Center frequency of the filter in Hz.
    bandwidth (float): Bandwidth of the filter in Hz.
    transition_width (float): Transition width of the filter in Hz.
    fs (float): Sampling frequency in Hz.
    number_of_taps (int): Number of taps for the filter.

    Returns:
        taps(numpy.ndarray): An array of filter tap coefficients generated using the Remez algorithm.

    Note:
        The function generates filter taps using the Remez algorithm from the SciPy 'signal' module.
        The tap array is calculated based on the specified filter type, center frequency, bandwidth,
        transition width, and number of taps.

    Example:
        samplingFrequency = 1000       # Sampling frequency of the filter
        filterType = 'lp'              # Filter type (low-pass)
        centerFrequency = 100          # Center frequency of the filter
        filterBandwidth = 50           # Bandwidth of the low-pass filter
        transitionWidth = 10           # Transition width of the filter
        numberOfTaps = 64              # Number of filter taps
        filterTaps = generateFilter(samplingFrequency, filterType, centerFrequency,
                                     filterBandwidth, transitionWidth, numberOfTaps)
        # Returns an array of filter tap coefficients for a low-pass filter.
    """
    filter_low = center_freq - (bandwidth / 2)
    filter_up = center_freq + (bandwidth / 2)
    sampling_freq = fs
    number_of_taps = number_of_taps
    taps = zeros(number_of_taps)
    trans_width = transition_width
    if filter_type == 'lp':
        cut_off_freq = bandwidth
        taps = remez(
            number_of_taps,
            [0, cut_off_freq, cut_off_freq + trans_width, 0.5 * sampling_freq],
            [1, 0],
            fs=sampling_freq)

    elif filter_type == 'bp':
        band = [filter_low, filter_up]  # Desired pass band, Hz
        edges = [
            0, band[0] - trans_width, band[0], band[1], band[1] + trans_width,
            0.5 * sampling_freq
        ]
        taps = remez(number_of_taps, edges, [0, 1, 0], fs=sampling_freq)
    return taps