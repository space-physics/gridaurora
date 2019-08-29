#!/usr/bin/env python
"""
inspired by Matt Zettergren
Michael Hirsch
"""
import numpy as np


def setupz(Np: int, zmin: float, gridmin: float, gridmax: float) -> np.ndarray:
    """
    np: number of grid points
    zmin: minimum STEP SIZE at minimum grid altitude [km]
    gridmin: minimum altitude of grid [km]
    gridmax: maximum altitude of grid [km]
    """

    dz = _ztanh(Np, gridmin, gridmax)

    return np.insert(np.cumsum(dz) + zmin, 0, zmin)[:-1]


def _ztanh(Np: int, gridmin: float, gridmax: float) -> np.ndarray:
    """
    typically call via setupz instead
    """
    x0 = np.linspace(
        0, 3.14, Np
    )  # arbitrarily picking 3.14 as where tanh gets to 99% of asymptote
    return np.tanh(x0) * gridmax + gridmin


# def zexp(np,gridmin):
#    x0 = linspace(0, 1, np)
#    return exp(x0)**2+(gridmin-1)
