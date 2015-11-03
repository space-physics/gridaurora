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
from collections import namedtuple
from matplotlib.pyplot import show
from os.path import expanduser
from dateutil import rrule
from dateutil.parser import parse
import seaborn #optional pretty plots
#
from gridaurora.loadtranscargrid import loadregress,makebin,doplot
from gridaurora.writeeigen import writeeigen
from glowaurora.eigenprof import makeeigen,ekpcolor
from glowaurora.runglow import plotprodloss,plotenerdep
from gridaurora.plots import ploteigver

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='Makes unit flux eV^-1 as input to GLOW or Transcar to create ionospheric eigenprofiles')
    p.add_argument('-i','--inputgridfn',help='original Zettergren input flux grid to base off of',default='zettflux.csv')
    p.add_argument('-o','--outfn',help='hdf5 file to write with ionospheric response (eigenprofiles)')
    p.add_argument('-t','--simtime',help='yyyy-mm-ddTHH:MM:SSZ time of sim',nargs='+',required=True)#,default='1999-12-21T00:00:00Z')
    p.add_argument('-c','--latlon',help='geodetic latitude/longitude (deg)',type=float,nargs=2,required=True)
    p.add_argument('-m','--makeplot',help='show to show plots, png to save pngs of plots',nargs='+',default=['show'])
    p.add_argument('-z','--zlim',help='minimum,maximum altitude [km] to plot',nargs=2,default=(None,None),type=float)

    p = p.parse_args()

    if not p.outfn:
        print('you have not specified an output file with -o options, so I will only plot and not save result')

    makeplot=p.makeplot

    if len(p.simtime) == 1:
        T = [parse(p.simtime[0])]
    elif len(p.simtime) == 2:
        T = list(rrule.rrule(rrule.HOURLY,
                                 dtstart=parse(p.simtime[0]),
                                 until =parse(p.simtime[1])))
#%% input unit flux
    Egrid = loadregress(expanduser(p.inputgridfn))
    Ebins = makebin(Egrid)
    EKpcolor,EK,diffnumflux = ekpcolor(Ebins)
#%% ionospheric response
    """ three output eigenprofiles
    1) ver (optical emissions) 4-D array: time x energy x altitude x wavelength
    2) prates (production) 4-D array:     time x energy x altitude x reaction
    3) lrates (loss) 4-D array:           time x energy x altitude x reaction
    """
    ver,photIon,isr,phitop,zceta,sza,prates,lrates,tezs = makeeigen(EK,diffnumflux,T,p.latlon,
                                                                        p.makeplot,p.outfn,p.zlim)
#%% plots
    #input
    doplot(p.inputgridfn,Ebins)

    #output
    glat,glon = p.latlon
    z=ver.major_axis.values
    sim = namedtuple('sim',['reacreq','opticalfilter']); sim.reacreq=sim.opticalfilter=''

    writeeigen(p.outfn,EKpcolor,ver.labels.to_pydatetime(),ver.major_axis(),
               diffnumflux,ver,prates,lrates,tezs,p.latlon)

    for t in ver: #for each time
        #VER eigenprofiles, summed over wavelength
        ploteigver(EKpcolor,z,ver[t].sum(axis=2),(None,)*6,sim,'{} Vol. Emis. Rate '.format(t))
        #volume production rate, summed over reaction
        plotprodloss(EKpcolor,z,
                     prates[t].sum(axis=2).values,lrates[t].sum(axis=2).values,
                     t,glat,glon,p.zlim)
        #energy deposition
        plotenerdep(EKpcolor,z,tezs[t],t,glat,glon,p.zlim)

    show()
