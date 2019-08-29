import numpy as np

"""
these are altitudes hard-coded into the old version of NCAR GLOW.
"""


def glowalt() -> np.ndarray:
    # z = range(80,110+1,1)
    z = np.arange(30.0, 110 + 1.0, 1.0)
    z = np.append(z, [111.5, 113.0, 114.5, 116.0])
    z = np.append(z, np.arange(118, 150 + 2, 2.0))
    z = np.append(z, np.arange(153, 168 + 3, 3.0))
    z = np.append(z, np.arange(172, 180 + 4, 4.0))
    z = np.append(z, np.arange(185, 205 + 5, 5))
    z = np.append(z, np.arange(211, 223 + 6, 6))
    z = np.append(z, np.arange(230, 244 + 7, 7))
    z = np.append(z, np.arange(252, 300 + 8, 8))
    z = np.append(z, np.arange(309, 345 + 9, 9))
    z = np.append(z, np.arange(355, 395 + 10, 10))
    z = np.append(z, np.arange(406, 428 + 11, 11))
    z = np.append(z, [440.0, 453, 467, 482, 498, 515, 533, 551])
    z = np.append(z, np.arange(570, 950 + 20, 20))

    return z
