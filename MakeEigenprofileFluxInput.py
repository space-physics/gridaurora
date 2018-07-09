#!/usr/bin/env python
"""
creates energy grid of unit flux eV^-1
unverified for proper scaling, fitted exponential curve to extrapolate original
Zettergren grid from 50eV-18keV up to 100MeV

example:
python MakeEigenprofileFluxInput.py -i zettflux.csv -o ~/data/100MeVtop.h5

Michael Hirsch
"""
from matplotlib.pyplot import show
import seaborn
from pathlib import Path
from argparse import ArgumentParser
from gridaurora.loadtranscargrid import loadregress,makebin,doplot

def main():
    
    p = ArgumentParser(description='Makes unit flux eV^-1 as input to GLOW or Transcar to create ionospheric eigenprofiles')
    p.add_argument('-i','--inputgridfn',help='original Zettergren grid to base off of',default='zettflux.csv')
    p.add_argument('-o','--outputeigenfluxfn',help='hdf5 file to write with eigenflux')
    p = p.parse_args()

    Egrid = loadregress(p.inputgridfn)
    bins = makebin(Egrid)

    if p.outputeigenfluxfn:
        bins.to_hdf(Path(p.outputeigenfluxfn).expanduser(),'top')

    doplot(p.inputgridfn,bins)
    show()


if __name__ == '__main__':
    main()
