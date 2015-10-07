import logging
from os.path import join
from numpy import arange
from gridaurora.filterload import getSystemT,plotT
from matplotlib.pyplot import show

def selftest(bg3fn,windfn,qefn, mmsLambda,obsalt_km,zenang_deg):

    newLambda = arange(mmsLambda[0],mmsLambda[1]+mmsLambda[2],mmsLambda[2], dtype=float)
    return getSystemT(newLambda,bg3fn,windfn,qefn,obsalt_km,zenang_deg)

if __name__=="__main__":
    from argparse import ArgumentParser
    p = ArgumentParser(description='mogrifies spectral transmission data from datasheets as manually converted into HDF5 data')
    p.add_argument('--wlnm',help='START STOP STEP wavelength in nm',nargs=3,default=(200.,1000.,0.1),type=float)
    p.add_argument('--path',help='path to HDF5 data',default='precompute')
    p.add_argument('-a','--altkm',help='observer altitude (km)',type=float,default=0.)
    p.add_argument('--zenang',help='zenith angle (deg)',type=float,default=0.)
    p = p.parse_args()


    filterfn =  join(p.path,'BG3transmittance.h5')
    windFN =    join(p.path,'ixonWindowT.h5')
    qeFN =      join(p.path,'emccdQE.h5')

    T = selftest(filterfn, windFN, qeFN, p.wlnm,p.altkm,p.zenang)

    plotT(T, p.wlnm)
    show()