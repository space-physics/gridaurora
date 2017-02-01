#!/usr/bin/env python
"""
creates optical emissions from excitation rates
"""
from pathlib import Path
import logging
from xarray import  DataArray
from numpy import zeros,append,where, loadtxt
import h5py
from pytz import UTC
#
from gridaurora.opticalmod import opticalModel
from gridaurora.calcemissions import calcemissions, sortelimlambda
from transcarread.readTranscar import calcVERtc

def getTranscar(sim,obsAlt_km,zenithang):
    zeroUnusedBeams = False

    if sim.loadver: #from JGR2013, NOT used much
        Plambda,Ek = loadver(sim.loadverfn)

        EKpcolor = Ek #TODO verify the energy centers for plotting (shifted 1/2 bin?)
        z = Plambda.major_axis.values

        lowestBeamUsedInd = getbeamsused(zeroUnusedBeams, Ek, sim.minbeamev)
        nEnergy = Ek.size - lowestBeamUsedInd
        Plambda = Plambda.iloc[:,:,lowestBeamUsedInd:]

        Peigen = zeros((Plambda.shape[1], nEnergy), dtype=float, order='F')
        for iEn in range(nEnergy):
            Peigen[:,iEn] = opticalModel(sim, Plambda.iloc[:,:,iEn].T,obsAlt_km,zenithang) #Transpose here because indexing Panel flips axes of Dataframe?

        Peigenunfilt = Plambda.sum(axis=0) #from matlab, which already did this
    else: #read from transcar emissions.dat (TYPICALLY USED)
#%% load transcar simulation outputs and modulate by optT
        Ek,EKpcolor = getBeamEnergies(sim.transcarev)
        # Peigen VERgray dimensions:  rows: altitudes  columns: the iEn^th energy beam
        # Plambda dims: rows: energy columns: altitude
        try:
            tReq = sim.transcarutc
            if tReq.tzinfo == None:
                tReq = tReq.replace(tzinfo = UTC)
            else:
                tReq = tReq.astimezone(UTC)
        except (ValueError,AttributeError) as e:
            logging.warning('You must specify a tReq in the spreadsheet for when you want to use transcar data' + str(e))
            tReq = None

        lowestBeamUsedInd = getbeamsused(zeroUnusedBeams,Ek,sim.minbeamev)
        nEnergy = Ek.size - lowestBeamUsedInd

        PlambdaAccum=None #for later testing
        for iEn in range(nEnergy):

            spec,tTC,tTCind = calcVERtc(sim.excratesfn, sim.transcarpath, Ek[iEn], tReq, sim)

            Plambda = calcemissions(spec,tTCind,sim)[0]
            if Plambda is None: #couldn't read this beam
                logging.info('skipped reading beam {}'.format(Ek[iEn]))
                continue
            z = Plambda.alt_km


            if iEn == lowestBeamUsedInd:
                PlambdaAccum = zeros((Plambda.shape[0],Plambda.shape[1],nEnergy),order='F')
                Peigen= zeros((z.size, nEnergy), dtype=float, order='F')

            PlambdaAccum[...,iEn] = Plambda  # Nalt x Nwavelength x Nenergy
            Peigen[:,iEn] = opticalModel(sim,Plambda,obsAlt_km,zenithang)

            if iEn != lowestBeamUsedInd:
                 if all( Peigen[:,iEn] == Peigen[:,lowestBeamUsedInd]):
                    logging.error('all Peigen for beam {} are equal to Peigen for beam {}'.format(Ek[iEn],Ek[lowestBeamUsedInd]))

        if PlambdaAccum is None: #no beams at all were read
            return ValueError('No beams were usable')

        Peigenunfilt = DataArray(data=PlambdaAccum.sum(axis=1), #sum over wavelength axis=1
                                 coords=[('alt_km',z),('energy_ev',Ek)])

    Peigen = DataArray(data=Peigen,
                       coords=[('alt_km',z),('energy_ev',Ek)])

    return Peigen, EKpcolor, Peigenunfilt

def getbeamsused(zeroUnusedBeams,Ek,minbeamenergy):
    if zeroUnusedBeams:
        try:
            return where(Ek>=minbeamenergy)[0][0]
        except IndexError:
            logging.warning('** You have picked a minimum energy outside the simulation energy range, falling back to using all beams')

    return 0

def loadver(verfn):
    with h5py.File(verfn,'r',libver='latest') as fid:
        plambda = fid['/Mp'].value
        zTC = fid['/z'].value
        Ek = fid['/E'].value
        lamb = fid['/lambda'].value

    lamb, plambdasorted = sortelimlambda(lamb,plambda)

    pdatf = Panel(plambdasorted,lamb,zTC,Ek)
    return pdatf,Ek

def getBeamEnergies(beamEnergyCSV):
    beamCSV = Path(beamEnergyCSV).expanduser()
    logging.info('Transcar sim. data dir: {}'.format(beamCSV) )

    try:
        beamEnergies= loadtxt(str(beamCSV),usecols=[0,1],delimiter=',')
    except OSError as e:
        raise OSError('could not find file. {}'.format(e))

    Ek = beamEnergies[:,0] #TODO should this value be in the log middle of these values?
    #Ek = Ek[Ek>minBeamEnergy] #nope, let's leave it to be zeroed later
    EKpcolor = append(Ek,beamEnergies[-1,1]) # the next higher energy is in the next right column

    return Ek,EKpcolor
