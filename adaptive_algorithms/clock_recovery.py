from utils.interpolation_with_sinc import interpolation_with_sinc
from numpy import zeros


def clock_recovery_OP_max(baseband_signal, t_now, half_number_of_symbols,
                          oversampling_factor, mu, delta, beta):
    """
    Perform clock recovery on sampled data.

    This function performs clock recovery on the given 'baseband_signal'.
    The clock recovery is achieved using the provided parameters and interpolation methods.

    Args:
        baseband_signal (numpy.ndarray): Array containing baseband signal data for clock recovery.
        t_now (float): Current time reference for clock recovery.
        half_number_of_symbols (int): Half of the number of symbols for srrc.
        oversampling_factor (int): Oversampling factor.
        mu (float): Step size coefficient for phase update.
        delta (float): Timing error detection window.
        beta (float): Roll-off factor for interpolation filter.

    

    Returns:
        tuple: A tuple containing:
            numpy.ndarray: Array of recovered timing errors at each iteration.
            numpy.ndarray: Array of recovered samples at each iteration.

    Note:
        This function utilizes the 'interpolation_with_sinc' function for interpolation.

    Resource:
        C. R. Johnson Jr, W. A. Sethares, and A. G. Klein, "Timing Recovery", in Software Receiver Design: Build
        your Own Digital Communication System in Five Easy Steps. Cambridge University
        Press, Aug. 2011,ch. 12, pp. 261-266.
    """
    m = oversampling_factor
    l = half_number_of_symbols
    if (t_now < m * l / 2):
        print('tnow is less than min, therefore m*l/2 is assigned')
        t_now = m * l / 2
    else:
        t_now = t_now
    n = round((len(baseband_signal) / oversampling_factor) - 2 * l)
    xs = zeros(n)
    tau_save = zeros(n)
    i = 0
    tau = 0.0
    while t_now < (
            len(baseband_signal) - l * m / 4
    ):  

        xs[i] = interpolation_with_sinc(sampledData=baseband_signal,
                                        t=t_now + tau,
                                        oneSidedLength=l,
                                        osFactor=m,
                                        beta=beta)
        x_deltap = interpolation_with_sinc(sampledData=baseband_signal,
                                           t=(t_now + tau + delta),
                                           oneSidedLength=l,
                                           osFactor=m,
                                           beta=beta)
        x_deltam = interpolation_with_sinc(sampledData=baseband_signal,
                                           t=(t_now + tau - delta),
                                           oneSidedLength=l,
                                           osFactor=m,
                                           beta=beta)
        dx = x_deltap - x_deltam
        tau = tau + mu * dx * xs[i]
        t_now = t_now + m
        tau_save[i] = tau
        i = i + 1

    return tau_save, xs
