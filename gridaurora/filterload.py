#!/usr/bin/env python3
from __future__ import absolute_import,division
import logging
from matplotlib.pyplot import figure
from numpy import exp, log, ones_like, isfinite,spacing
from scipy.interpolate import interp1d
import h5py
from os.path import expanduser
from pandas import DataFrame
# consider atmosphere
try:
    from lowtran.pylowtran7 import golowtran
    useatm = True
except ImportError as e:
    logging.error('failure to load LOWTRAN, proceeding without atmospheric absorption model.  {}'.format(e))
    useatm=False
'''
gets optical System Transmittance from filter, sensor window, and QE spec.
Michael Hirsch 2014
references:
BG3 filter datasheet: http://www.howardglass.com/pdf/bg3_datasheet.pdf
QE: http://www.andor.com/pdfs/specifications/Andor_iXon_Ultra_897_Specifications.pdf
     http://occult.mit.edu/instrumentation/MORIS/Documents/DU-897_BI.pdf
window: http://www.andor.com/pdfs/specifications/Andor_Camera_Windows_Supplementary_Specifications.pdf
'''

def getSystemT(newLambda, bg3fn,windfn,qefn,obsalt_km,zenang_deg,dbglvl=0):
#%% atmospheric absorption
    if useatm:
        if dbglvl>0: print('loading LOWTRAN7 atmosphere model...')
        atmT = golowtran(obsalt_km,zenang_deg,
                         wlnm=(newLambda[0],newLambda[-1]),
                         c1={'model':5,'itype':3,'iemsct':0})
        try:
            atmTcleaned = atmT.values.squeeze()
            atmTcleaned[atmTcleaned==0] = spacing(1) # to avoid log10(0)
            fwl = interp1d(atmT.index,log(atmTcleaned),axis=0)
        except AttributeError: #problem with lowtran
            fwl = interp1d(newLambda,log(ones_like(newLambda)),kind='linear')
    else:
        fwl = interp1d(newLambda,log(ones_like(newLambda)),kind='linear')
    atmTinterp = exp(fwl(newLambda))
    if not isfinite(atmTinterp).all():
        logging.error('problem in computing LOWTRAN atmospheric attenuation, results are suspect!')
#%% BG3 filter
    with h5py.File(expanduser(bg3fn),'r',libver='latest') as f:
        fbg3  = interp1d(f['/lamb'], log(f['/T']), kind='linear')
#%% camera window
    with h5py.File(expanduser(windfn),'r',libver='latest') as f:
        fwind = interp1d(f['/lamb'], log(f['/T']), kind='linear')
#%% quantum efficiency
    with h5py.File(expanduser(qefn),'r',libver='latest') as f:
        fqe =  interp1d(f['/lamb'], log(f['/QE']), kind='linear')


    T = DataFrame(index=newLambda, data = {'bg3':   exp(fbg3(newLambda)),
                                           'window':exp(fwind(newLambda)),
                                           'qe':    exp(fqe(newLambda)),
                                           'atm':   atmTinterp}) #atm is ALREADY exp()

    T['sysNObg3'] = T[['window','qe','atm']].prod(axis=1)
    T['sys']      = T[['window','qe','bg3','atm']].prod(axis=1)

    return T
#%% ploting
def plotT(T,mmsl):
    ax = figure().gca()
    T[['bg3','window','qe','atm']].plot(ax=ax)
    ax.set_xlim(mmsl[:2])
    ax.set_title('Component transmittance')
    ax.set_xlabel('wavelength (nm)')
    ax.set_ylabel('Transmittance (unitless)')
    ax.set_yscale('log')
    ax.legend(loc='best')
    ax.set_ylim(1e-6,1)
    ax.invert_xaxis()
#
    ax = figure().gca()
    T[['sys','sysNObg3']].plot(ax=ax)
    ax.set_title('System Transmittance')
    ax.set_ylabel('Transmittance (unitless)')
    ax.set_xlabel('wavelength (nm)')
    ax.set_yscale('log')
    ax.set_ylim(1e-6,1)
    ax.legend(loc='best')
    ax.invert_xaxis()
