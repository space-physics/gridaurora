#!/usr/bin/env python3
""" loads VER profiles (ver vs. altitude, and optionally vs. energy,reaction type)
Initially, we use eigenprofiles precomputed by Transcar.
Please contact me with any questions.

Michael Hirsch
Sept 2015
"""
from __future__ import division,absolute_import
import logging
import h5py
from os.path import expanduser
#
from gridaurora.arcexcite import getTranscar
from transcarread.readTranscar import SimpleSim
from gridaurora.opticalmod import plotOptMod
try:
    from histfeas.plotsnew import ploteig,ploteig1d
except:
    pass #only used for plots

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='Loads and Plots Auroral Eigenprofiles (VER vs. altitude for a given monoeenergtic electron beam of precipitation')
    p.add_argument('path',help='root path to simulation output')
    p.add_argument('-p','--doplot',help='make plots of data',action='store_true')
    p.add_argument('-o','--outfn',help='hdf5 filename to write output to')
    p = p.parse_args()

    sim = SimpleSim(filt='bg3',inpath=p.path,transcarutc='2013-03-31T09:00:21Z') #set some default parameters bundled up as a Class

    Peigen, EKpcolor, Peigenunfilt = getTranscar(sim)
#%% write output
    if p.outfn:
        h5fn = expanduser(p.outfn)
        with h5py.File(h5fn,'w',libver='latest') as f:
            d=f.create_dataset('/eigenprofile',data=Peigen.values)
            d.attrs['units']='photons cm^-3 sr^-1 s^-1 eV^-1'
            d=f.create_dataset('/altitude',data=Peigen.index)
            d.attrs['units']='km'
            d=f.create_dataset('/EbinEdges',data=EKpcolor)
            d.attrs['units']='eV'
            d=f.create_dataset('/Ebins',data=Peigen.columns)
            d.attrs['units']='eV'
#%% plotting
    if p.doplot:
        ploteig(EKpcolor,Peigen.index.values,Peigen.values,(None,)*6,sim)

        plotOptMod(Peigenunfilt,Peigen)

        ploteig1d(EKpcolor[:-1],Peigen.index,Peigen.values,(None,)*6,sim)