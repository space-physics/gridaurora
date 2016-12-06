#!/usr/bin/env python
from pathlib import Path
import logging
from numpy import exp, log, ones_like, isfinite,spacing,column_stack,empty,asarray
from scipy.interpolate import interp1d
import h5py
from xarray import DataArray
# consider atmosphere
try:
    from lowtran import golowtran
except ImportError as e:
    logging.error('failure to load LOWTRAN, proceeding without atmospheric absorption model.  {}'.format(e))
    golowtran=None
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
    assert isinstance(bg3fn,(Path,str))
    bg3fn = Path(bg3fn).expanduser()

    windfn = Path(windfn).expanduser()
    qefn = Path(qefn).expanduser()

    newLambda = asarray(newLambda)
#%% atmospheric absorption
    if golowtran is not None:
        if dbglvl>0:
            print('loading LOWTRAN7 atmosphere model...')
        atmT = golowtran(obsalt_km,zenang_deg,
                         wlnm=(newLambda[0],newLambda[-1]),
                         c1={'model':5,'itype':3,'iemsct':0})
        try:
            atmTcleaned = atmT.values.squeeze()
            atmTcleaned[atmTcleaned==0] = spacing(1) # to avoid log10(0)
            fwl = interp1d(atmT.wavelength_nm,log(atmTcleaned),axis=0)
        except AttributeError: #problem with lowtran
            fwl = interp1d(newLambda,log(ones_like(newLambda)),kind='linear')
    else:
        fwl = interp1d(newLambda,log(ones_like(newLambda)),kind='linear')

    atmTinterp = exp(fwl(newLambda))
    if not isfinite(atmTinterp).all():
        logging.error('problem in computing LOWTRAN atmospheric attenuation, results are suspect!')
#%% BG3 filter
    with h5py.File(str(bg3fn),'r',libver='latest') as f:
        try:
            assert isinstance(f['/T'], h5py.Dataset),'we only allow one transmission curve per file' # simple legacy behavior
            fbg3  = interp1d(f['/wavelength'], log(f['/T']), kind='linear', bounds_error=False)
        except KeyError:
            raise KeyError('could not find /wavelength in {}'.format(f.filename))

        try:
            fname = f['T'].attrs['name'].item()
            if isinstance(fname,bytes):
                fname = fname.decode('utf8')
        except KeyError:
            fname =''
#%% camera window
    with h5py.File(str(windfn),'r',libver='latest') as f:
        fwind = interp1d(f['/lamb'], log(f['/T']), kind='linear')
#%% quantum efficiency
    with h5py.File(str(qefn),'r',libver='latest') as f:
        fqe =  interp1d(f['/lamb'], log(f['/QE']), kind='linear')
#%% collect results into DataArray

    T = DataArray(column_stack((exp(fbg3(newLambda)),
                                exp(fwind(newLambda)),
                                exp(fqe(newLambda)),
                                atmTinterp,
                                empty(newLambda.size),
                                empty(newLambda.size))),
                  coords=[('wavelength_nm',newLambda),
                          ('filt',['filter','window','qe','atm','sysNObg3','sys'])])
                                           #atm is ALREADY exp()

    T.loc[:,'sysNObg3'] = T.sel(filt=['window','qe','atm']).prod('filt')
    T.loc[:,'sys']      = T.sel(filt=['window','qe','filter','atm']).prod('filt')

    return T,fname