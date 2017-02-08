"""
 Michael Hirsch
 based on Strickland 1993
"""
import logging
from numpy import (pi,exp,arange,empty_like, trapz, asfortranarray,atleast_1d)
import h5py
#
from sciencedates import find_nearest

def maxwellian(E,E0,Q0):
    """
    input:
    ------
    E: 1-D vector of energy bins [eV]
    E0: characteristic energy (scalar or vector) [eV]
    Q0: flux coefficient (scalar or vector) (to yield overall flux Q)

    output:
    -------
    Phi: differential number flux
    Q: total flux

    Tanaka 2006 Eqn. 1
    http://odin.gi.alaska.edu/lumm/Papers/Tanaka_2006JA011744.pdf
    """
    E0 = atleast_1d(E0)
    Q0 = atleast_1d(Q0)
    assert E0.ndim==Q0.ndim==1
    assert (Q0.size==1 or Q0.size==E0.size)

    Phi= Q0/(2*pi*E0**3) * E[:,None] * exp(-E[:,None]/E0)

    Q = trapz(Phi,E,axis=0)
    logging.info('total maxwellian flux Q: ' + (' '.join('{:.1e}'.format(q) for q in Q)))
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
    """
    strickland 1993 said 0.2, but 0.145 gives better match to peak flux at 2500 = E0
    """
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

def writeh5(h5fn,Phi,E,fp):
    if h5fn is not None:
        with h5py.File(h5fn,'w', libver='latest') as f:
            f.create_dataset('/diffnumflux',data=Phi)
            hE = f.create_dataset('/E',data=E); hE.attrs['Units'] = 'eV'
            f.create_dataset('/diffnumflux_params',data=fp)
