#!/usr/bin/env python
from pathlib import Path
import numpy as np
import h5py
from typing import Tuple
import xarray

"""
inputs:
spec: excitation rates, 3-D , dimensions time x altitude x reaction

output:
ver: a pandas DataFrame, wavelength x altitude
br: flux-tube integrated intensity, dimension lamb

See Eqn 9 of Appendix C of Zettergren PhD thesis 2007 to get a better insight on what this set of functions do.
"""


def calcemissions(rates: xarray.DataArray, sim) -> Tuple[xarray.DataArray, np.ndarray, np.ndarray]:
    if not sim.reacreq:
        return 0., 0., 0.

    ver = None
    lamb = None
    br = None
    """
    Franck-Condon factor
    http://chemistry.illinoisstate.edu/standard/che460/handouts/460-Feb28lec-S13.pdf
    http://assign3.chem.usyd.edu.au/spectroscopy/index.php
    """
# %% METASTABLE
    if 'metastable' in sim.reacreq:
        ver, lamb, br = getMetastable(rates, ver, lamb, br, sim.reactionfn)
# %% PROMPT ATOMIC OXYGEN EMISSIONS
    if 'atomic' in sim.reacreq:
        ver, lamb, br = getAtomic(rates, ver, lamb, br, sim.reactionfn)
# %% N2 1N EMISSIONS
    if 'n21ng' in sim.reacreq:
        ver, lamb, br = getN21NG(rates, ver, lamb, br, sim.reactionfn)
# %% N2+ Meinel band
    if 'n2meinel' in sim.reacreq:
        ver, lamb, br = getN2meinel(rates, ver, lamb, br, sim.reactionfn)
# %% N2 2P (after Vallance Jones, 1974)
    if 'n22pg' in sim.reacreq:
        ver, lamb, br = getN22PG(rates, ver, lamb, br, sim.reactionfn)
# %% N2 1P
    if 'n21pg' in sim.reacreq:
        ver, lamb, br = getN21PG(rates, ver, lamb, br, sim.reactionfn)
# %% Remove NaN wavelength entries
    if ver is None:
        raise ValueError('you have not selected any reactions to generate VER')
# %% sort by wavelength, eliminate NaN
    lamb, ver, br = sortelimlambda(lamb, ver, br)
# %% assemble output
    dfver = xarray.DataArray(data=ver, coords=[('alt_km', rates.alt_km),
                                               ('wavelength_nm', lamb)])

    return dfver, ver, br


def getMetastable(rates, ver: np.ndarray, lamb, br, reactfn: Path):
    with h5py.File(reactfn, 'r') as f:
        A = f['/metastable/A'][:]
        lambnew = f['/metastable/lambda'].value.ravel(order='F')  # some are not 1-D!

    """
    concatenate along the reaction dimension, axis=-1
    """
    vnew = np.concatenate((A[:2] * rates.loc[..., 'no1s'].values[:, None],
                           A[2:4] * rates.loc[..., 'no1d'].values[:, None],
                           A[4:] * rates.loc[..., 'noii2p'].values[:, None]), axis=-1)

    assert vnew.shape == (rates.shape[0], A.size)

    return catvl(rates.alt_km, ver, vnew, lamb, lambnew, br)


def getAtomic(rates, ver, lamb, br, reactfn):
    """ prompt atomic emissions (nm)
    844.6 777.4
    """
    with h5py.File(reactfn, 'r') as f:
        lambnew = f['/atomic/lambda'].value.ravel(order='F')  # some are not 1-D!

    vnew = np.concatenate((rates.loc[..., 'po3p3p'].values[..., None],
                           rates.loc[..., 'po3p5p'].values[..., None]), axis=-1)

    return catvl(rates.alt_km, ver, vnew, lamb, lambnew, br)


def getN21NG(rates, ver, lamb, br, reactfn):
    """
    excitation Franck-Condon factors (derived from Vallance Jones, 1974)
    """
    with h5py.File(str(reactfn), 'r', libver='latest') as f:
        A = f['/N2+1NG/A'].value
        lambdaA = f['/N2+1NG/lambda'].value.ravel(order='F')
        franckcondon = f['/N2+1NG/fc'].value

    return doBandTrapz(A, lambdaA, franckcondon, rates.loc[..., 'p1ng'], lamb, ver, rates.alt_km, br)


def getN2meinel(rates, ver, lamb, br, reactfn):
    with h5py.File(str(reactfn), 'r', libver='latest') as f:
        A = f['/N2+Meinel/A'].value
        lambdaA = f['/N2+Meinel/lambda'].value.ravel(order='F')
        franckcondon = f['/N2+Meinel/fc'].value
    # normalize
    franckcondon = franckcondon/franckcondon.sum()  # special to this case

    return doBandTrapz(A, lambdaA, franckcondon, rates.loc[..., 'pmein'], lamb, ver, rates.alt_km, br)


def getN22PG(rates, ver, lamb, br, reactfn):
    """ from Benesch et al, 1966a """
    with h5py.File(str(reactfn), 'r', libver='latest') as f:
        A = f['/N2_2PG/A'].value
        lambdaA = f['/N2_2PG/lambda'].value.ravel(order='F')
        franckcondon = f['/N2_2PG/fc'].value

    return doBandTrapz(A, lambdaA, franckcondon, rates.loc[..., 'p2pg'], lamb, ver, rates.alt_km, br)


def getN21PG(rates, ver, lamb, br, reactfn):

    with h5py.File(str(reactfn), 'r', libver='latest') as fid:
        A = fid['/N2_1PG/A'].value
        lambnew = fid['/N2_1PG/lambda'].value.ravel(order='F')
        franckcondon = fid['/N2_1PG/fc'].value

    tau1PG = 1 / np.nansum(A, axis=1)
    """
    solve for base concentration
    confac=[1.66;1.56;1.31;1.07;.77;.5;.33;.17;.08;.04;.02;.004;.001];  %Cartwright, 1973b, stop at nuprime==12
    Gattinger and Vallance Jones 1974
    confac=array([1.66,1.86,1.57,1.07,.76,.45,.25,.14,.07,.03,.01,.004,.001])
    """

    consfac = franckcondon/franckcondon.sum()  # normalize
    losscoef = (consfac / tau1PG).sum()
    N01pg = rates.loc[..., 'p1pg'] / losscoef

    scalevec = (A * consfac[:, None]).ravel(order='F')  # for clarity (verified with matlab)

    vnew = scalevec[None, None, :] * N01pg.values[..., None]

    return catvl(rates.alt_km, ver, vnew, lamb, lambnew, br)


def doBandTrapz(Aein, lambnew, fc, kin, lamb, ver, z, br):
    """
    ver dimensions: wavelength, altitude, time

     A and lambda dimensions:
    axis 0 is upper state vib. level (nu')
    axis 1 is bottom state vib level (nu'')
    there is a Franck-Condon parameter (variable fc) for each upper state nu'
    """
    tau = 1/np.nansum(Aein, axis=1)

    scalevec = (Aein * tau[:, None] * fc[:, None]).ravel(order='F')

    vnew = scalevec[None, None, :]*kin.values[..., None]

    return catvl(z, ver, vnew, lamb, lambnew, br)


def catvl(z, ver, vnew, lamb, lambnew, br):
    """
    trapz integrates over altitude axis, axis = -2
    concatenate over reaction dimension, axis = -1

    br: column integrated brightness
    lamb: wavelength [nm]
    ver: volume emission rate  [photons / cm^-3 s^-3 ...]
    """
    if ver is not None:
        br = np.concatenate((br, np.trapz(vnew, z, axis=-2)), axis=-1)  # must come first!
        ver = np.concatenate((ver, vnew), axis=-1)
        lamb = np.concatenate((lamb, lambnew))
    else:
        ver = vnew.copy(order='F')
        lamb = lambnew.copy()
        br = np.trapz(ver, z, axis=-2)

    return ver, lamb, br


def sortelimlambda(lamb, ver, br):
    assert lamb.ndim == 1
    assert lamb.size == ver.shape[-1]
# %% eliminate unused wavelengths and Einstein coeff
    mask = np.isfinite(lamb)
    ver = ver[..., mask]
    lamb = lamb[mask]
    br = br[:, mask]
# %% sort by lambda
    lambSortInd = lamb.argsort()  # lamb is made piecemeal and is overall non-monotonic

    return lamb[lambSortInd], ver[..., lambSortInd], br[:, lambSortInd]  # sort by wavelength ascending order
