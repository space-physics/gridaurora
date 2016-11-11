#!/usr/bin/env python
from numpy import logspace,array
from matplotlib.pyplot import  show
import seaborn as sns
sns.set_context('paper',font_scale=1.75)
sns.set_style('whitegrid')
#
from gridaurora.eFluxGen import maxwellian,fluxgen,writeh5
from gridaurora.plots import plotflux

E = logspace(2,4.35,num=200,base=10) #like Strickland 1993
#E = logspace(1.7,4.3,num=33,base=10) #like matt's transcar sim

E0 = array([1e4, 5250,3500,  2250,   1000, 750, 500])
#E0 = logspace(2.5,4,num=7,base=10)
Q0 = 1e12
#Q0 = array([1.1e12, 1e12, 7e11, 5e11, 2.25e11, 1.75e11,1.1e11])
Wbc= array([0.25, 0.375, 0.4, 0.5,  0.75, 0.9, 1.1])
bl = 0.8
bm = array([3,  2.5, 2.5, 2.5,    3.  ,   3.,   3.])
bh =  4.
Bm0= array([6500, 5500, 4750, 4000,3000, 2500, 2000])
Bhf= array([0.5, 0.3, 0.215, 0.15, 0.125, 0.125,  0.125]) # highest energy gaussian tail flux

if __name__ == '__main__':

    from argparse import ArgumentParser
    p = ArgumentParser(description='generates diff. num flux based on Strickland 1993')
    p.add_argument('-v','--verbose',help='set debugging verbosity',default=0,action='count')
    p.add_argument('-o','--save',help='filename output to HDF5',default=None)
    p = p.parse_args()

#%% Maxwellian
    Phimaxwell,Qmaxwell = maxwellian(E, E0, Q0)
    plotflux(E, E0, Phimaxwell,ttxt = 'Maxellian differential number flux')
#%% Strickland
    Phi,low,mid,hi,base,Q = fluxgen(E, E0, Q0, Wbc, bl, bm, bh, Bm0, Bhf, p.verbose)

#    writeh5(p.save,Phi,E,E0,Q0,Wbc,bl,bm,bh,Bm0,Bhf)

    #plotflux(E, E0,Phi, base, hi,low,mid,'Dispersive Alfvén wave flux vs $E_0$')
    plotflux(E, E0,Phi,ttxt='Dispersive Alfvén wave flux vs $E_0$')

    show()