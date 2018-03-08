#!/usr/bin/env python
import logging
from pathlib import Path
from numpy import arange
from matplotlib.pyplot import show
#
import seaborn as sns
sns.color_palette("cubehelix")
sns.set(context='paper', style='whitegrid',font_scale=2,
        rc={'image.cmap': 'cubehelix_r'})
#
from gridaurora.filterload import getSystemT
from gridaurora.opticalmod import comparejgr2013,plotAllTrans

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='computes optical transmission and compares (debug)')
    p.add_argument('--path',help='path to HDF5 data',default='precompute')
    p.add_argument('-a','--altkm',help='observer altitude (km)',type=float,default=0.)
    p.add_argument('--zenang',help='zenith angle (deg)',type=float,default=0.)
    p.add_argument('-m','--makeplot',help='[eps png]',nargs='+')
    p = p.parse_args()

    dpath = Path(p.path).expanduser()
    bg3fn =  dpath/'BG3transmittance.h5'
    windfn = dpath/'ixonWindowT.h5'
    qefn =   dpath/'emccdQE.h5'

    reqLambda = arange(200,1200,1)
    #reqLambda = linspace(200,1000,500) #so coarse it misses features

    optT = getSystemT(reqLambda, bg3fn, windfn, qefn,p.altkm,p.zenang)
#%%
    try:
        comparejgr2013(p.altkm,p.zenang,bg3fn,windfn,qefn)
#%% considering atmosphere
        plotAllTrans(optT,False)
        fg=plotAllTrans(optT,True)

        #plotOptMod(ver,VERgray,tTC,Ek,Eki) #called in readTranscar.py
        show()

    except Exception as e:
        logging.warning(f'problem plotting    {e}')
        print(optT)
