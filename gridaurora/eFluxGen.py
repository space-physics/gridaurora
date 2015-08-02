#!/usr/bin/env python3
"""
 Michael Hirsch
 based on Strickland 1993
"""
from __future__ import division
from os.path import expanduser
from numpy import (pi,exp,logspace,arange,empty_like,isscalar, trapz,asfortranarray)
from pandas import DataFrame
import h5py
from warnings import warn
#
from histutils.findnearest import find_nearest

def maxwellian(E,E0,Q0,verbose=0):
    """
    Tanaka 2006 Eqn. 1
    http://odin.gi.alaska.edu/lumm/Papers/Tanaka_2006JA011744.pdf
    """
    Phi= Q0/(2*pi*E0**3) * E[:,None] * exp(-E[:,None]/E0)
    
    Q = trapz(Phi,E,axis=0)
    if verbose>0:
        print('total flux Q: ' + (' '.join('{:.1e}'.format(q) for q in Q)))
    return Phi,Q

def fluxgen(E,E0,Q0,Wbc,bl,bm,bh,Bm,Bhf,verbose=0):

    Wb=Wbc*E0

    isimE0 = find_nearest(E,E0)[0]

    base = gaussflux(E,Wb,E0,Q0)
    diffnumflux = base.copy()

    low = letail(E,E0,Q0,bl,verbose)
    diffnumflux += low #intermediate result

    mid = midtail(E,E0,bm,Bm)
    diffnumflux += mid #intermediate result

    hi = hitail(E,diffnumflux,isimE0,E0,Bhf,bh,verbose)
    diffnumflux += hi

    if verbose>0:
        diprat(E0,diffnumflux,isimE0)

    Q = trapz(diffnumflux,E,axis=0)
    if verbose>0:
        print('total flux Q: ' + (' '.join('{:.1e}'.format(q) for q in Q)))

    return asfortranarray(diffnumflux),low,mid,hi,base,Q

def letail(E,E0,Q0,bl,verbose):
    # for LET, 1<b<2
    #Bl = 8200.   #820 (typo?)
    Bl = 0.4*Q0/(2*pi*E0**2)*exp(-1)
    #bl = 1.0     #1
    low = Bl * (E[:,None]/E0)**-bl
    low[E[:,None] > E0] = 0.
    if verbose>0:
        print('Bl: ' + (' '.join('{:0.1f}'.format(b) for b in Bl)))
    return low

def midtail(E,E0,bm,Bm):
    #Bm = 1.8e4      #1.8e4
    #bm = 3.         #3
    mid = Bm*(E[:,None]/E0)**bm
    mid[E[:,None]>E0] = 0.
    return mid

def hitail(E,diffnumflux,isimE0,E0,Bhf,bh,verbose):
    # strickland 1993 said 0.2, but 0.145 gives better match to peak flux at 2500 = E0
    Bh = empty_like(E0)
    for iE0 in arange(E0.size):
        Bh[iE0] = Bhf[iE0]*diffnumflux[isimE0[iE0],iE0]      #4100.
    #bh = 4                   #2.9
    het = Bh*(E[:,None] / E0)**-bh
    het[E[:,None] < E0] = 0.
    if verbose>0:
        print('Bh: ' + (' '.join('{:0.1f}'.format(b) for b in Bh)))
    return het

def diprat(E0,arc,isimE0):
    dipratio = empty_like(E0)
    for iE0 in arange(E0.size):
        idip = arc[:isimE0[iE0],iE0].argmin(axis=0)
        dipratio[iE0] = arc[idip,iE0]/arc[isimE0[iE0],iE0]

    print('dipratio: ' + (' '.join('{:0.2f}'.format(d) for d in dipratio)))
    #if not all(0.2<dipratio<0.5):
    #    warn('dipratio outside of 0.2<dipratio<0.5')

def gaussflux(E,Wb,E0,Q0):
    Qc = Q0/(pi**(3/2) * Wb*E0)
    return Qc * exp(-((E[:,None]-E0) / Wb)**2)


def plotflux(E,E0, arc, base=None,hi=None,low=None,mid=None,dbglvl=0):
#    tfs = 'xx-large'
#    afs = 'x-large'
#    tkfs = 'large'
    lblstr = ['{:.0f}'.format(e0) for e0 in E0]
    ax = figure().gca()
    if isscalar(E0) and mid is not None:
        ax.loglog(E,hi,'k:')
        ax.loglog(E,low,'k:')
        ax.loglog(E,mid,'k:')
        ax.loglog(E,base,color='k')
    ax.loglog(E,arc,linewidth=2)

    #ax.grid(True,which='both')
    ax.set_xlabel('Electron Energy [eV]')#,fontsize=afs,labelpad=-2)
    ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')#,fontsize=afs)
    ax.set_title('Input differential number flux')#,fontsize=tfs)
    #ax.tick_params(axis='both', which='both')#,labelsize=tkfs)
    ax.autoscale(True,tight=True)
    ax.set_ylim((1e2,1e5))
    ax.legend(lblstr,loc='best')#,prop={'size':'large'})
    #ax.set_xlim((1e2,1e4))
   # sns.despine(ax=ax)

    if dbglvl>0 and base is not None:
        ax = figure().gca()
        ax.loglog(E,base)
        ax.set_ylim((1e2,1e6))
        #ax.set_xlim((1e2,1e4))
        ax.set_title('arc Gaussian base function, E0=' + str(E0)+ '[eV]' +
                     '\n Wbc: width, Q0: height')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
        ax.legend(lblstr)

        ax = figure().gca()
        ax.loglog(E,low)
        ax.set_ylim((1e2,1e6))
        ax.set_title('arc low (E<E0).  Bl: height, bh: slope')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')

        ax = figure().gca()
        ax.loglog(E,mid)
        ax.set_ylim((1e2,1e6))
        ax.set_title('arc mid.  Bm:height, bm: slope')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')

        ax = figure().gca()
        ax.loglog(E,hi)
        ax.set_ylim((1e2,1e6))
        ax.set_title('arc hi (E>E0).  Bhf: height, bh: slope')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')



def writeh5(h5fn,Phi,E,fp):
    if h5fn is not None:
        with h5py.File(h5fn,'w', libver='latest') as f:
            f.create_dataset('/diffnumflux',data=Phi)
            hE = f.create_dataset('/E',data=E); hE.attrs['Units'] = 'eV'
            f.create_dataset('/diffnumflux_params',data=fp)


if __name__ == '__main__':
    from matplotlib.pyplot import figure, show
    import seaborn as sns
    sns.set_context('talk')
    sns.set_style('whitegrid')

    from argparse import ArgumentParser
    p = ArgumentParser(description='generates diff. num flux based on Strickland 1993')
    p.add_argument('infn',help='HDF5 file with table dataset containing parameters')
    p.add_argument('-v','--verbose',help='set debugging verbosity',default=0,action='count')
    p.add_argument('-o','--save',help='filename output to HDF5',default=None)
    p = p.parse_args()

    #E = logspace(2,4.35,num=200,base=10) #like Strickland 1993
    E = logspace(1.7,4.3,num=33,base=10) #like matt's transcar sim

    try:
        with h5py.File(expanduser(p.infn),'r',libver='latest') as f:
            df = DataFrame(f['/diffnumflux_params'].value)
    except KeyError as e:
        warn('trouble accessing {} {}'.format(p.infn,e))
        raise


    df.dropna(axis=0,how='any',inplace=True)
#%% Maxwellian 
    Phimaxwell,Qmaxwell = maxwellian(E,df['E0'].values,df['Q0'].values, p.verbose)
    plotflux(E,df['E0'].values,Phimaxwell)
#%% Strickland
    Phi,low,mid,hi,base,Q = fluxgen(E,df['E0'].values,df['Q0'].values,df['Wbc'].values,
                                    df['bl'].values,df['bm'].values,df['bh'].values,
                                    df['Bm'].values,df['Bhf'].values, p.verbose)

    writeh5(p.save,Phi,E,df)

    plotflux(E,df['E0'].values,Phi, base, hi,low,mid,p.verbose)

    show()
