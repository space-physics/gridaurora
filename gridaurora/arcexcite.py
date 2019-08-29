#!/usr/bin/env python
"""
creates optical emissions from excitation rates
"""
from pathlib import Path
import logging
import xarray
import numpy as np
import h5py

#
from gridaurora.opticalmod import opticalModel
from gridaurora.calcemissions import calcemissions, sortelimlambda
from transcarread import calcVERtc


def getTranscar(sim, obsAlt_km: float, zenithang: float) -> tuple:
    zeroUnusedBeams = False

    if sim.loadver:  # from JGR2013, NOT used much
        Plambda, Ek = loadver(sim.loadverfn)

        EKpcolor = Ek  # TODO verify the energy centers for plotting (shifted 1/2 bin?)
        z = Plambda.major_axis.values

        lowestBeamUsedInd = getbeamsused(zeroUnusedBeams, Ek, sim.minbeamev)

        Plambda = Plambda.iloc[:, :, lowestBeamUsedInd:]
        nEnergy = Plambda.shape[2]

        Peigen = np.zeros((Plambda.shape[1], nEnergy), dtype=float, order="F")
        for iEn in range(nEnergy):
            # Transpose here because indexing Panel flips axes of Dataframe?
            Peigen[:, iEn] = opticalModel(sim, Plambda.iloc[:, :, iEn].T, obsAlt_km, zenithang)

        Peigenunfilt = Plambda.sum(axis=0)  # from matlab, which already did this
    else:  # read from transcar emissions.dat (TYPICALLY USED)
        # %% load transcar simulation outputs and modulate by optT
        Ek, EKpcolor = getBeamEnergies(sim.transcarev)
        # Peigen VERgray dimensions:  rows: altitudes  columns: the iEn^th energy beam
        # Plambda dims: rows: energy columns: altitude
        try:
            tReq = sim.transcarutc
        except (ValueError, AttributeError) as e:
            logging.warning(f"must specify a tReq in the spreadsheet for Transcar data.  {e}")
            tReq = None

        lowestBeamUsedInd = getbeamsused(zeroUnusedBeams, Ek, sim.minbeamev)
        nEnergy = Ek.size - lowestBeamUsedInd

        PlambdaAccum: np.ndarray = None  # for later testing
        for iEn in range(nEnergy):

            spec, tTC, tTCind = calcVERtc(sim.excratesfn, sim.transcarpath, Ek[iEn], tReq, sim)

            Plambda, _, _ = calcemissions(spec, sim)
            if Plambda is None:  # couldn't read this beam
                logging.info(f"skipped reading beam {Ek[iEn]}")
                continue
            z = Plambda.alt_km

            if iEn == lowestBeamUsedInd:
                PlambdaAccum = np.zeros((Plambda.shape[0], Plambda.shape[1], nEnergy), order="F")
                Peigen = np.zeros((z.size, nEnergy), dtype=float, order="F")

            PlambdaAccum[..., iEn] = Plambda  # Nalt x Nwavelength x Nenergy
            Peigen[:, iEn] = opticalModel(sim, Plambda, obsAlt_km, zenithang)

            if iEn != lowestBeamUsedInd:
                if all(Peigen[:, iEn] == Peigen[:, lowestBeamUsedInd]):
                    logging.error(
                        f"all Peigen for beam {Ek[iEn]} equal Peigen: beam {Ek[lowestBeamUsedInd]}"
                    )

        if PlambdaAccum is None:  # no beams at all were read
            raise ValueError("No beams were usable")

        Peigenunfilt = xarray.DataArray(
            data=PlambdaAccum.sum(axis=1),  # sum over wavelength axis=1
            coords=[("alt_km", z), ("energy_ev", Ek)],
        )

    Peigen = xarray.DataArray(data=Peigen, coords=[("alt_km", z), ("energy_ev", Ek)])

    return Peigen, EKpcolor, Peigenunfilt


def getbeamsused(zeroUnusedBeams, Ek: float, minbeamenergy: float) -> int:
    if zeroUnusedBeams:
        try:
            return np.where(Ek >= minbeamenergy)[0][0]  # first index
        except IndexError:
            logging.warning(
                "minimum energy outside the simulation energy range, falling back to using all beams"
            )

    return 0


def loadver(verfn):
    with h5py.File(verfn, "r") as fid:
        plambda = fid["/Mp"].value
        zTC = fid["/z"].value
        Ek = fid["/E"].value
        lamb = fid["/lambda"].value

    lamb, plambdasorted = sortelimlambda(lamb, plambda)

    pdatf = xarray.DataArray(
        data=plambdasorted,
        coords={"wavelength_nm": lamb, "alt_km": zTC, "energy": Ek},
        dims=["wavelength_nm", "alt_km", "energy"],
    )
    return pdatf, Ek


def getBeamEnergies(beamEnergyCSV):
    beamCSV = Path(beamEnergyCSV).expanduser()
    logging.info("Transcar sim. data dir: {}".format(beamCSV))

    try:
        beamEnergies = np.loadtxt(beamCSV, usecols=[0, 1], delimiter=",")
    except OSError as e:
        raise OSError("could not find file. {}".format(e))

    Ek = beamEnergies[:, 0]  # TODO should this value be in the log middle of these values?
    # Ek = Ek[Ek>minBeamEnergy] #nope, let's leave it to be zeroed later
    EKpcolor = np.append(
        Ek, beamEnergies[-1, 1]
    )  # the next higher energy is in the next right column

    return Ek, EKpcolor
