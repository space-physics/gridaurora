#!/usr/bin/env python
""" loads VER profiles (ver vs. altitude, and optionally vs. energy,reaction type)
Initially, we use eigenprofiles precomputed by Transcar.
Please contact me with any questions.

Michael Hirsch
Sept 2015
"""
from pathlib import Path
import h5py
from argparse import ArgumentParser
from gridaurora.arcexcite import getTranscar
from transcarread import SimpleSim
from gridaurora.plots import plotOptMod
try:
    from histfeas.plotsnew import ploteigver, ploteig1d
except ImportError as e:
    print(e)  # only used for plots


def main():
    p = ArgumentParser(
        description='Loads and Plots Auroral Eigenprofiles (VER vs. altitude) for monoeenergtic electron beam of precipitation')
    p.add_argument('path', help='root path to simulation output')
    p.add_argument('-p', '--doplot', help='make plots of data', action='store_true')
    p.add_argument('-o', '--outfn', help='hdf5 filename to write output to')
    p.add_argument('--zenithang', help='angle from local vertical', type=float, default=12.5)
    p.add_argument('--alt', help='kilometers', type=float, default=0.)
    p = p.parse_args()

    # set some default parameters bundled up as a Class
    sim = SimpleSim(filt='bg3', inpath=p.path, transcarutc='2013-03-31T09:00:21Z')

    Peigen, EKpcolor, Peigenunfilt = getTranscar(sim, p.alt, p.zenithang)
# %% write output (overwrites existing  HDF5 file)
    if p.outfn:
        h5fn = Path(p.outfn).expanduser()
        print('writing', h5fn)
        with h5py.File(h5fn, 'w') as f:
            d = f.create_dataset('/eigenprofile', data=Peigen.values)
            d.attrs['units'] = 'photons cm^-3 sr^-1 s^-1 eV^-1'
            d = f.create_dataset('/altitude', data=Peigen.index)
            d.attrs['units'] = 'km'
            d = f.create_dataset('/EbinEdges', data=EKpcolor)
            d.attrs['units'] = 'eV'
            d = f.create_dataset('/Ebins', data=Peigen.columns)
            d.attrs['units'] = 'eV'
# %% plotting
    if p.doplot:
        ploteigver(EKpcolor, Peigen.alt_km, Peigen.values, (None,)*6, sim)

        plotOptMod(Peigenunfilt, Peigen)

        ploteig1d(EKpcolor[:-1], Peigen.alt_km, Peigen.values, (None,)*6, sim)


if __name__ == '__main__':
    main()
