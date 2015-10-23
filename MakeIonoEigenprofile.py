#!/usr/bin/env python3
"""
Computes Eigenprofiles of Ionospheric response to flux tube input via the following steps:
1. Generate unit input differential number flux vs. energy
2. Compute ionospheric energy deposition and hence production/loss rates for the modeled kinetic chemistries (12 in total)

unverified for proper scaling, fitted exponential curve to extrapolate original
Zettergren grid from 50eV-18keV up to 100MeV

example:
python MakeIonoEigenprofile.py -i zettflux.csv -o ~/data/eigen.h5

Michael Hirsch
"""
from __future__ import division,absolute_import
from matplotlib.pyplot import show
from os.path import expanduser
import seaborn #optional pretty plots
#
from gridaurora.loadtranscargrid import loadregress,makebin,doplot

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='Makes unit flux eV^-1 as input to GLOW or Transcar to create ionospheric eigenprofiles')
    p.add_argument('-i','--inputgridfn',help='original Zettergren input flux grid to base off of',default='zettflux.csv')
    p.add_argument('-o','--outputeigenfluxfn',help='hdf5 file to write with ionospheric response (eigenprofiles)')
    p = p.parse_args()

    if not p.outputeigenfluxfn:
        print('you have not specified an output file with -o options, so I will only plot and not save result')
#%% input unit flux
    Egrid = loadregress(p.inputgridfn)
    bins = makebin(Egrid)

    doplot(p.inputgridfn,bins)
#%% ionospheric response
    ver,photIon,isr,phitop,zceta,sza,EKpcolor,prates,lrates = makeeigen(p.eigenprof,dtime,p.latlon,
                                                                        p.f107a,p.f107,p.f107p,p.ap,
                                                                        p.makeplot,p.odir,p.zlim)



    show()
