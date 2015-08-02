#!/usr/bin/env python3
from __future__ import print_function,absolute_import,division
from numpy import exp, arange, log, ones_like, isfinite,spacing
from scipy.interpolate import interp1d
import h5py
from os.path import join,expanduser
from pandas import DataFrame
from warnings import warn
# consider atmosphere
try:
    from lowtran.pylowtran7 import golowtran
    useatm = True
except ImportError as e:
    warn('failure to load LOWTRAN atmosphere model, proceeding without '
         'atmospheric absorption model.  {}'.format(e))
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
def selftest(bg3fn,windfn,qefn, mmsLambda,obsalt_km,zenang_deg):

    newLambda = arange(mmsLambda[0],mmsLambda[1]+mmsLambda[2],mmsLambda[2], dtype=float)
    return getSystemT(newLambda,bg3fn,windfn,qefn,obsalt_km,zenang_deg)

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
        warn('problem in computing LOWTRAN atmospheric attenuation, results are suspect!')
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
#%%
if __name__=="__main__":
    from argparse import ArgumentParser
    p = ArgumentParser(description='mogrifies spectral transmission data from datasheets as manually converted into HDF5 data')
    p.add_argument('--h5',help='write HDF5 output to this file',type=str,default='')
    p.add_argument('--noplot',help='do not show plots',action='store_false')
    p.add_argument('--wlnm',help='START STOP STEP wavelength in nm',nargs=3,default=(200.,1000.,0.1),type=float)
    p.add_argument('--path',help='path to HDF5 data',default='precompute',type=str)
    p.add_argument('-a','--altkm',help='observer altitude (km)',type=float,default=0.)
    p.add_argument('--zenang',help='zenith angle (deg)',type=float,default=0.)
    p = p.parse_args()

    dpath = p.path
    filterfn =  join(dpath,'BG3transmittance.h5')
    windFN =    join(dpath,'ixonWindowT.h5')
    qeFN =      join(dpath,'emccdQE.h5')

    T = selftest(filterfn, windFN, qeFN, p.wlnm,p.altkm,p.zenang)

        #write to disk
    if p.h5:
        #come up with a unique filename
        print('writing ' + p.h5)
        with h5py.File(p.h5,'w',libver='latest') as f:
            f["T"]=T

    if p.noplot:
        from matplotlib.pyplot import show,figure
        plotT(T, p.wlnm)
        show()
