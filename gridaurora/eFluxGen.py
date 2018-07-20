"""
 Michael Hirsch
 based on Strickland 1993
"""
import logging
from pathlib import Path
import numpy as np
import h5py
from typing import Tuple

pi = np.pi


def maxwellian(E: np.ndarray, E0: np.ndarray, Q0: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    input:
    ------
    E: 1-D vector of energy bins [eV]
    E0: characteristic energy (scalar or vector) [eV]
    Q0: flux coefficient (scalar or vector) (to yield overall flux Q)

    output:
    -------
    Phi: differential number flux
    Q: total flux

    Tanaka 2006 Eqn. 1
    http://odin.gi.alaska.edu/lumm/Papers/Tanaka_2006JA011744.pdf
    """
    E0 = np.atleast_1d(E0)
    Q0 = np.atleast_1d(Q0)
    assert E0.ndim == Q0.ndim == 1
    assert (Q0.size == 1 or Q0.size == E0.size)

    Phi = Q0/(2*pi*E0**3) * E[:, None] * np.exp(-E[:, None]/E0)

    Q = np.trapz(Phi, E, axis=0)
    logging.info('total maxwellian flux Q: ' + (' '.join('{:.1e}'.format(q) for q in Q)))
    return Phi, Q


def fluxgen(E, E0, Q0, Wbc, bl, bm, bh, Bm, Bhf, verbose: int=0) -> tuple:

    Wb = Wbc*E0

    isimE0 = abs(E - E0).argmin()

    base = gaussflux(E, Wb, E0, Q0)
    diffnumflux = base.copy()

    low = letail(E, E0, Q0, bl, verbose)
    diffnumflux += low  # intermediate result

    mid = midtail(E, E0, bm, Bm)
    diffnumflux += mid  # intermediate result

    hi = hitail(E, diffnumflux, isimE0, E0, Bhf, bh, verbose)
    diffnumflux += hi

    if verbose > 0:
        diprat(E0, diffnumflux, isimE0)

    Q = np.trapz(diffnumflux, E, axis=0)
    if verbose > 0:
        print('total flux Q: ' + (' '.join('{:.1e}'.format(q) for q in Q)))

    return np.asfortranarray(diffnumflux), low, mid, hi, base, Q


def letail(E: np.ndarray, E0: float, Q0: float, bl: float, verbose: int=0) -> np.ndarray:
    # for LET, 1<b<2
    # Bl = 8200.   #820 (typo?)
    Bl = 0.4*Q0/(2*pi*E0**2) * np.exp(-1)
    # bl = 1.0     #1
    low = Bl * (E[:, None]/E0)**-bl
    low[E[:, None] > E0] = 0.
    if verbose > 0:
        print('Bl: ' + (' '.join('{:0.1f}'.format(b) for b in Bl)))
    return low


def midtail(E: np.ndarray, E0: np.ndarray, bm: float, Bm: float):
    # Bm = 1.8e4      #1.8e4
    # bm = 3.         #3
    mid = Bm*(E[:, None]/E0)**bm
    mid[E[:, None] > E0] = 0.
    return mid


def hitail(E: np.ndarray, diffnumflux: np.ndarray, isimE0: np.ndarray, E0: np.ndarray,
           Bhf: np.ndarray, bh: float, verbose: int=0):
    """
    strickland 1993 said 0.2, but 0.145 gives better match to peak flux at 2500 = E0
    """
    Bh = np.empty_like(E0)
    for iE0 in np.arange(E0.size):
        Bh[iE0] = Bhf[iE0]*diffnumflux[isimE0[iE0], iE0]  # 4100.
    # bh = 4                   #2.9
    het = Bh*(E[:, None] / E0)**-bh
    het[E[:, None] < E0] = 0.
    if verbose > 0:
        print('Bh: ' + (' '.join('{:0.1f}'.format(b) for b in Bh)))
    return het


def diprat(E0: np.ndarray, arc: np.ndarray, isimE0: np.ndarray):
    dipratio = np.empty_like(E0)
    for iE0 in np.arange(E0.size):
        idip = arc[:isimE0[iE0], iE0].argmin(axis=0)
        dipratio[iE0] = arc[idip, iE0]/arc[isimE0[iE0], iE0]

    print('dipratio: ' + (' '.join(f'{d:0.2f}' for d in dipratio)))
    # if not all(0.2<dipratio<0.5):
    #    warn('dipratio outside of 0.2<dipratio<0.5')


def gaussflux(E, Wb, E0, Q0):
    Qc = Q0/(pi**(3/2) * Wb*E0)
    return Qc * np.exp(-((E[:, None]-E0) / Wb)**2)


def writeh5(h5fn: Path, Phi: np.ndarray, E, fp):
    if h5fn:
        with h5py.File(h5fn, 'w') as f:
            f.create_dataset('/diffnumflux', data=Phi)
            hE = f.create_dataset('/E', data=E)
            hE.attrs['Units'] = 'eV'
            f.create_dataset('/diffnumflux_params', data=fp)
