#!/usr/bin/env python
from pathlib import Path
import logging
import numpy as np
from scipy.interpolate import interp1d
import h5py
import xarray

# consider atmosphere
try:
    import lowtran
except ImportError as e:
    logging.error(
        f"failure to load LOWTRAN, proceeding without atmospheric absorption model.  {e}"
    )
    lowtran = None
"""
gets optical System Transmittance from filter, sensor window, and QE spec.
Michael Hirsch 2014
references:
BG3 filter datasheet: http://www.howardglass.com/pdf/bg3_datasheet.pdf
QE: http://www.andor.com/pdfs/specifications/Andor_iXon_Ultra_897_Specifications.pdf
     http://occult.mit.edu/instrumentation/MORIS/Documents/DU-897_BI.pdf
window: http://www.andor.com/pdfs/specifications/Andor_Camera_Windows_Supplementary_Specifications.pdf
"""


def getSystemT(
    newLambda, bg3fn: Path, windfn: Path, qefn: Path, obsalt_km, zenang_deg, verbose: bool = False
) -> xarray.Dataset:

    bg3fn = Path(bg3fn).expanduser()
    windfn = Path(windfn).expanduser()
    qefn = Path(qefn).expanduser()

    newLambda = np.asarray(newLambda)
    # %% atmospheric absorption
    if lowtran is not None:
        c1 = {
            "model": 5,
            "h1": obsalt_km,
            "angle": zenang_deg,
            "wlshort": newLambda[0],
            "wllong": newLambda[-1],
        }
        if verbose:
            print("loading LOWTRAN7 atmosphere model...")
        atmT = lowtran.transmittance(c1)["transmission"].squeeze()
        try:
            atmTcleaned = atmT.values.squeeze()
            atmTcleaned[atmTcleaned == 0] = np.spacing(1)  # to avoid log10(0)
            fwl = interp1d(atmT.wavelength_nm, np.log(atmTcleaned), axis=0)
        except AttributeError:  # problem with lowtran
            fwl = interp1d(newLambda, np.log(np.ones_like(newLambda)), kind="linear")
    else:
        fwl = interp1d(newLambda, np.log(np.ones_like(newLambda)), kind="linear")

    atmTinterp = np.exp(fwl(newLambda))
    if not np.isfinite(atmTinterp).all():
        logging.error("problem in computing LOWTRAN atmospheric attenuation, results are suspect!")
    # %% BG3 filter
    with h5py.File(bg3fn, "r") as f:
        try:
            assert isinstance(
                f["/T"], h5py.Dataset
            ), "we only allow one transmission curve per file"  # simple legacy behavior
            fbg3 = interp1d(f["/wavelength"], np.log(f["/T"]), kind="linear", bounds_error=False)
        except KeyError:
            raise KeyError("could not find /wavelength in {}".format(f.filename))

        try:
            fname = f["T"].attrs["name"].item()
            if isinstance(fname, bytes):
                fname = fname.decode("utf8")
        except KeyError:
            fname = ""
    # %% camera window
    with h5py.File(windfn, "r") as f:
        fwind = interp1d(f["/lamb"], np.log(f["/T"]), kind="linear")
    # %% quantum efficiency
    with h5py.File(qefn, "r") as f:
        fqe = interp1d(f["/lamb"], np.log(f["/QE"]), kind="linear")
    # %% collect results into DataArray

    T = xarray.Dataset(
        {
            "filter": ("wavelength_nm", np.exp(fbg3(newLambda))),
            "window": ("wavelength_nm", np.exp(fwind(newLambda))),
            "qe": ("wavelength_nm", np.exp(fqe(newLambda))),
            "atm": ("wavelength_nm", atmTinterp),
        },
        coords={"wavelength_nm": newLambda},
        attrs={"filename": fname},
    )

    T["sysNObg3"] = T["window"] * T["qe"] * T["atm"]
    T["sys"] = T["sysNObg3"] * T["filter"]

    return T
