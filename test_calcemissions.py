#!/usr/bin/env python3
"""
using excitation rates and other factors, creates volume emission rate profiles.
"""
from __future__ import division,absolute_import
import logging
import h5py
from os.path import join,expanduser
from matplotlib.pyplot import show

from gridaurora.calcemissions import calcemissions,plotspectra,showIncrVER
from gridaurora.filterload import getSystemT
# github.com/scienceopen/transcarread
from transcarread.readExcrates import readexcrates
from transcarread.parseTranscar import readTranscarInput
from transcarread.readTranscar import SimpleSim

if __name__ == '__main__':
    import cProfile,pstats

    #
    from argparse import ArgumentParser
    p = ArgumentParser(description = 'using excitation rates and other factors, creates volume emission rate profiles.')
    p.add_argument('path',help='root path where simulation inputs/outputs are')
    p.add_argument('beamenergy',help='beam energy [eV] to plot',type=float)
    p.add_argument('-r','--reacreq',help='reactions to include e.g. metastable atomic',nargs='+',default=['metastable','atomic','n21ng','n2meinel','n22pg','n21pg'])
    p.add_argument('-m','--makeplot',help='specify plots to make e.g. vjinc vjinc1d',nargs='+',default=['eigtime','eigtime1d','spectra'])
    p.add_argument('--datcarfn',help='path to dir.input/DATCAR',default='dir.input/DATCAR')
    p.add_argument('--profile',help='profile performance',action='store_true')
    p.add_argument('-p','--doplot',help='show plots of data',action='store_true')
    p.add_argument('-o','--outfile',help='HDF5 filename to write')
    p=p.parse_args()

    tReqInd = 40 #arbitrary,
    #NOTE: make sure tReqInd after precipitation starts or you're looking at airglow instead of aurora!

    simpath = join(p.path,'beam'+str(p.beamenergy))

    excrpath = join(simpath,'dir.output')
    excrates = readexcrates(excrpath,'emissions.dat')[0]
    sim = SimpleSim(filt=None,inpath=simpath,reacreq=p.reacreq)
#%% testing code timing only
    if p.profile:
        proffn = 'calcemissions.pstats'
        cProfile.run('calcemissions(excrates,tReqInd,sim)',proffn)
        pstats.Stats(proffn).sort_stats('time','cumulative').print_stats(50)
        exit()
#%% normal usage, continue processing data
    tctime = readTranscarInput(join(simpath,p.datcarfn))

    t=excrates.minor_axis.to_datetime().to_pydatetime()

    if t[tReqInd]<tctime['tstartPrecip']:
        logging.warning('you picked a time before precipitation started, so youre looking at AIRGLOW instead of AURORA!')

    tver,ver,br=calcemissions(excrates, tReqInd, sim)
    optT = getSystemT(tver.index,sim.bg3fn, sim.windowfn,sim.qefn,sim.obsalt_km,sim.zenang)
#%% write as hdf5
    if p.outfile:
        h5fn = expanduser(p.outfile)
        print('writing output to '+h5fn)
        with h5py.File(expanduser(h5fn),'w',libver='latest') as f:
            d=f.create_dataset('/ver',data=tver.values) #volume emission rate per beam vs. altitude and wavelength
            d.attrs['units'] = 'photons cm^-3 sr^-1 s^-1 eV^-1'
            d=f.create_dataset('/wavelength',data=tver.index)
            d.attrs['units'] = 'nm'
            d=f.create_dataset('/altitude',data=tver.columns)
            d.attrs['units'] = 'km'
#%% plots
    if p.doplot:
        #spectra overall
        plotspectra(br,optT,p.beamenergy,sim.lambminmax)

        #details of individual reactions
        for r in p.reacreq:
            sim.reacreq = r
            ver, tver,br = calcemissions(excrates, tReqInd, sim)
            showIncrVER(t, tReqInd, tctime, ver,tver, str(r),p.makeplot)

        show()