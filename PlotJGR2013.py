#!/usr/bin/env python
"""
plots various data from Dahlgren et al 2013 JGR paper
"""
import h5py
#
from reesaurora.rees_model import plotA

def plotenerdep():
#%% load JGR2013 data
    with h5py.File('precompute/trans_jgr2013a.h5','r',libver='latest') as f:
        Ajgr = f['/Mp'].value; zjgr = f['/z'].value; Ejgr=f['/E'].value
    plotA(Ajgr.sum(axis=0),zjgr,Ejgr,'JGR2013 deposition matrix')

if __name__ == '__main__':
    plotenerdep()
