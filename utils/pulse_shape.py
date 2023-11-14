from numpy import arange, sqrt, cos, sin, pi

"""
    Generate a Square-Root Raised Cosine (SRRC) pulse with specified parameters.

    This function generates an SRRC pulse with the given number of symbols 'syms', roll-off factor 'beta',
    and oversampling factor 'P'. The pulse is generated for a range of time values and can be optionally time-shifted.

    Args:
        syms (int): Half of Total Number of Symbols.
        beta (float): Roll-off factor.
        P (int): Oversampling factor.
        t_off (float, optional): Time offset. Default is 0.

    Returns:
        s(numpy.ndarray): SRRC pulse waveform.

    Example:
        symbols = 8           # Half of Total Number of Symbols
        roll_off = 0.5        # Roll-off factor
        oversampling = 4      # Oversampling factor
        time_offset = 1.0     # Time offset
        srrc_pulse = srrc(symbols, roll_off, oversampling, time_offset)
        # Returns the SRRC pulse waveform for the specified parameters

    Resource:
        C. R. Johnson Jr, W. A. Sethares, and A. G. Klein, "Pulse Shaping and Receive Filterin", in Software Receiver Design: Build your Own Digital Communication 
        System in Five Easy Steps. Cambridge University Press, Aug. 2011,ch. 11, pp. 247-249.
    """
def srrc(syms, beta, P, t_off=0):

    # s = (4*beta/np.sqrt(P)) scales SRRC
    # syms  = Half of Total Number of Symbols
    P = P
    beta = beta
    length_SRRC = P * syms * 2
    start = float((-length_SRRC / 2) + 1e-8 + t_off)
    stop = float((length_SRRC / 2) + 1e-8 + t_off)
    step = float(1)
    k = arange(start=start, stop=stop + 1, step=step, dtype=float)
    if beta == 0:
        beta = 1e-8
    denom = (pi * (1 - 16 * ((float(beta) * k / float(P))**2)))
    # s = (np.cos((1 + beta) * np.pi * k / P) + (np.sin(
    #     (1 - beta) * np.pi * k / P) / (4 * beta * k / P))) / denom
    s = (4 * beta / sqrt(P)) * (cos((1 + beta) * pi * k / P) + (sin(
        (1 - beta) * pi * k / P) / (4 * beta * k / P))) / denom
    return s