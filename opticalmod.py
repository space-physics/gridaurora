#!/usr/bin/env python3
from __future__ import division,absolute_import
from os.path import join
import h5py
from numpy import arange
from warnings import warn
try:
    from matplotlib.pyplot import figure, subplots,show #must be here to allow plotOptMod to be called from hist-feasibility
    from matplotlib.ticker import MultipleLocator
    import seaborn as sns
    sns.color_palette(sns.color_palette("cubehelix"))
    sns.set(context='notebook', style='whitegrid',
        rc={'image.cmap': 'cubehelix_r'}) #for contour
except Exception as e:
    warn('problem with Matplotlib, plots won"t work   {}'.format(e))
#
try:
    from .filterload import getSystemT
except:
    from filterload import getSystemT

def opticalModel(sim,ver):
    #assert reqLambda.ndim == 1
    #assert z.ndim == 1
    #assert z.size == ver.shape[1]
    #assert reqLambda.size == ver.shape[0]

#%% get system optical transmission T
    optT = getSystemT(ver.index.values,sim.bg3fn, sim.windowfn,sim.qefn,sim.obsalt_km,sim.zenang)
#%% first multiply VER by T, THEN sum overall wavelengths
    if sim.opticalfilter == 'bg3':
        VERgray = ver.multiply(optT['sys'],axis=0).sum(axis=0)
    elif sim.opticalfilter == 'none':
        VERgray = ver.multiply(optT['sysNObg3'],axis=0).sum(axis=0)
    else:
        warn('unknown OpticalFilter type: {}'
             '   falling back to using no filter at all'.format(sim.opticalfilter))
        VERgray = ver.multiply(optT['sysNObg3'],axis=0).sum(axis=0)

    return VERgray

def plotOptMod(verNObg3gray,VERgray):
    """ called from either readTranscar.py or hist-feasibility/plotsnew.py """
    if VERgray is None and verNObg3gray is None: return

    ax2 = figure().gca() #summed (as camera would see)

    if VERgray is not None:
        z = VERgray.index.values
        Ek = VERgray.columns.values

#        ax1.semilogx(VERgray, z, marker='',label='filt', color='b')
        props = {'boxstyle':'round', 'facecolor':'wheat', 'alpha':0.5}
        fgs, axs = subplots(6, 6, sharex=True, sharey='row')
        axs=axs.ravel() #for convenient iteration
        fgs.subplots_adjust(hspace=0,wspace=0)
        fgs.suptitle('filtered VER/flux')
        fgs.text(0.04,0.5,'Altitude [km]',va='center', rotation='vertical')
        fgs.text(0.5, 0.04, 'Beam energy [eV]', ha='center')
        for i,e in enumerate(Ek):
            axs[i].semilogx(VERgray[e],z)
            axs[i].set_xlim((1e-3,1e4))

# place a text box in upper left in axes coords
            axs[i].text(0.95, 0.95, '{:0.0f}'.format(e)+'eV',
                                        transform=axs[i].transAxes, fontsize=12,
                                            va='top', ha='right',bbox=props)
        for i in range(33,36):
            axs[i].axis('off')

        ax2.semilogx(VERgray.sum(axis=1),z, label='filt',color='b')

        #specific to energies
        ax = figure().gca()
        for e in Ek:
            ax.semilogx(VERgray[e], z, marker='', label='{:0.0f}'.format(e)+'eV')
        ax.set_title('filtered VER/flux')
        ax.set_xlabel('VER/flux')
        ax.set_ylabel('altitude [km]')
        ax.legend(loc='best',fontsize=8)
        ax.set_xlim((1e-5, 1e5))
        ax.grid(True)

    if verNObg3gray is not None:
        ax1 = figure().gca() #overview
        z = verNObg3gray.index.values
        Ek = verNObg3gray.columns.values

        ax1.semilogx(verNObg3gray, z,marker='',label='unfilt', color='r')
        ax2.semilogx(verNObg3gray.sum(axis=1), z, label='unfilt', color='r')

        ax = figure().gca()
        for e in Ek:
            ax.semilogx(verNObg3gray[e], z, marker='', label='{:0.0f}'.format(e)+'eV')
        ax.set_title('UNfiltered VER/flux')
        ax.set_xlabel('VER/flux')
        ax.set_ylabel('altitude [km]')
        ax.legend(loc='best',fontsize=8)
        ax.set_xlim((1e-5, 1e5))
        ax.grid(True)

        ax1.set_title('VER/flux, one profile per beam')
        ax1.set_xlabel('VER/flux')
        ax1.set_ylabel('altitude [km]')
        ax1.grid(True)

    ax2.set_xlabel('VER/flux')
    ax2.set_ylabel('altitude [km]')
    ax2.set_title('VER/flux summed over all energy beams \n (as the camera would see)')
    ax2.legend(loc='best')
    ax2.grid(True)

def comparejgr2013(altkm,zenang):
    with h5py.File('precompute/trans_jgr2013a.h5','r',libver='latest') as fid:
        reqLambda = fid['/lambda'].value
        Tjgr2013 = fid['/T'].value

    optT = getSystemT(reqLambda, bg3fn, windfn, qefn,altkm,zenang)

    ax = figure().gca()
    ax.semilogy(reqLambda,optT['sys'],'b',label='HST')
    ax.semilogy(reqLambda,Tjgr2013,'r',label='JGR2013')
    ax.set_xlabel('wavelength [nm]')
    ax.set_ylabel('T')
    ax.set_title('Comparision of Transmission models: HST vs. JGR2013')
    ax.grid(True)
    ax.legend(loc='best')
    ax.set_title('System Transmission + Atmospheric Absorption')
    ax.set_ylim(1e-10,1)

def plotAllTrans(optT,log):
    mutwl = optT.index

    ax = figure().gca()
    ax.plot(mutwl,optT['sys'],label='optics')
    ax.plot(mutwl,optT['atm'],label='atmosphere')
    ax.plot(mutwl,optT[['sys','atm']].prod(axis=1),label='total',linewidth=2)
    if log:
        ax.set_yscale('log')
        ax.set_ylim(bottom=1e-5)
    ax.set_xlabel('wavelength [nm]')
    ax.set_ylabel('T')
    ax.set_title('Optical System Transmission and Atmospheric Absorption')
    ax.grid(True)
    ax.invert_xaxis()
    ax.xaxis.set_major_locator(MultipleLocator(100))
    ax.legend(loc='best')

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='computes optical transmission and compares (debug)')
    p.add_argument('--path',help='path to HDF5 data',default='precompute')
    p.add_argument('-a','--altkm',help='observer altitude (km)',type=float,default=0.)
    p.add_argument('--zenang',help='zenith angle (deg)',type=float,default=0.)
    p = p.parse_args()

    dpath = p.path
    bg3fn =  join(dpath,'BG3transmittance.h5')
    windfn =    join(dpath,'ixonWindowT.h5')
    qefn =      join(dpath,'emccdQE.h5')

    reqLambda = arange(200,1200,1)
    #reqLambda = linspace(200,1000,500) #so coarse it misses features

    optT = getSystemT(reqLambda, bg3fn, windfn, qefn,p.altkm,p.zenang)
#%%
    try:
        comparejgr2013(p.altkm,p.zenang)
#%% considering atmosphere
        plotAllTrans(optT,False)
        plotAllTrans(optT,True)
        #plotOptMod(ver,VERgray,tTC,Ek,Eki) #called in readTranscar.py
        show()

    except Exception as e:
        warn('problem plotting    {}'.format(e))
        print(optT)

