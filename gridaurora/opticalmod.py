#!/usr/bin/env python
import logging
import xarray
from .filterload import getSystemT


def opticalModel(sim, ver: xarray.DataArray, obsAlt_km: float, zenithang: float):
    """
    ver: Nalt x Nwavelength

    """
    assert isinstance(ver, xarray.DataArray)
    # %% get system optical transmission T
    optT = getSystemT(ver.wavelength_nm, sim.bg3fn, sim.windowfn, sim.qefn, obsAlt_km, zenithang)
    # %% first multiply VER by T, THEN sum overall wavelengths
    if sim.opticalfilter == "bg3":
        VERgray = (ver * optT["sys"].values[None, :]).sum("wavelength_nm")
    elif sim.opticalfilter == "none":
        VERgray = (ver * optT["sysNObg3"].values[None, :]).sum("wavelength_nm")
    else:
        logging.warning(
            f"unknown OpticalFilter type: {sim.opticalfilter}"
            "   falling back to using no filter at all"
        )
        VERgray = (ver * optT["sysNObg3"].values[None, :]).sum("wavelength_nm")

    return VERgray
