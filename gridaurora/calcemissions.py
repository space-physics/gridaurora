#!/usr/bin/env python3
import logging
from numpy import trapz, isfinite, concatenate, nansum
import h5py
from xarray import DataArray
from matplotlib.pyplot import figure,close,subplots
#from matplotlib.colors import LogNorm
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import SecondLocator, DateFormatter, MinuteLocator
"""
inputs:
spec: excitation rates, 3-D , dimensions time x altitude x reaction

output:
ver: a pandas DataFrame, wavelength x altitude
br: flux-tube integrated intensity, dimension lamb

See Eqn 9 of Appendix C of Zettergren PhD thesis 2007 to get a better insight on what this set of functions do.
"""
spectraAminmax = (1e-1,8e5) #for plotting
spectrallines=(391.44, 427.81, 557.7, 630.0, 777.4, 844.6) #297.2, 636.4,762.0, #for plotting

def calcemissions(spec,tReqInd,sim):
    if not sim.reacreq:
        return

    assert isinstance(spec,DataArray), 'I expect an xarray DataArray as input'

    ver = None; lamb = None; br=None
    """
    Franck-Condon factor
    http://chemistry.illinoisstate.edu/standard/che460/handouts/460-Feb28lec-S13.pdf
    http://assign3.chem.usyd.edu.au/spectroscopy/index.php
    """
#%% METASTABLE
    if 'metastable' in sim.reacreq:
        ver, lamb,br = getMetastable(spec,ver,lamb,br, sim.reactionfn)
#%% PROMPT ATOMIC OXYGEN EMISSIONS
    if 'atomic' in sim.reacreq:
        ver, lamb,br = getAtomic(spec, ver, lamb, br, sim.reactionfn)
#%% N2 1N EMISSIONS
    if 'n21ng' in sim.reacreq:
        ver, lamb,br = getN21NG(spec,ver,lamb, br, sim.reactionfn)
#%% N2+ Meinel band
    if 'n2meinel' in sim.reacreq:
        ver, lamb,br = getN2meinel(spec,ver,lamb, br, sim.reactionfn)
#%% N2 2P (after Vallance Jones, 1974)
    if 'n22pg' in sim.reacreq:
        ver, lamb,br = getN22PG(spec,ver,lamb, br, sim.reactionfn)
#%% N2 1P
    if 'n21pg' in sim.reacreq:
        ver, lamb,br = getN21PG(spec,ver,lamb, br, sim.reactionfn)
#%% Remove NaN wavelength entries
    if ver is None:
        raise ValueError('you have not selected any reactions to generate VER')
#%% sort by wavelength, eliminate NaN
    lamb, ver, br = sortelimlambda(lamb,ver,br)
    try:
        tver = ver[tReqInd,...]
        br = br[tReqInd,:]
    except IndexError as e:
        logging.error('error in time index, falling back to last time value')
        print(str(e))
        tver = ver[-1,...]
        br = br[-1,:]
#%% assemble output
    dfver = DataArray(data=tver, coords=[('alt_km',spec.alt_km),('wavelength_nm',lamb)])

    return dfver, ver,br

def getMetastable(spec,ver,lamb,br,reactfn):
    with h5py.File(str(reactfn),'r',libver='latest') as f:
        A = f['/metastable/A'].value
        lambnew = f['/metastable/lambda'].value.ravel(order='F') #some are not 1-D!

    """
    concatenate along the reaction dimension, axis=-1
    """
    vnew = concatenate((A[None,None,:2] * spec.loc[...,'no1s'].values[...,None],
                        A[None,None,2:4]* spec.loc[...,'no1d'].values[...,None],
                        A[None,None,4:] * spec.loc[...,'noii2p'].values[...,None]), axis=-1)

    return catvl(spec.alt_km,ver,vnew,lamb,lambnew,br)

def getAtomic(spec,ver,lamb, br,reactfn):
    """ prompt atomic emissions (nm)
    844.6 777.4
    """
    with h5py.File(str(reactfn),'r',libver='latest') as f:
        lambnew = f['/atomic/lambda'].value.ravel(order='F') #some are not 1-D!

    vnew = concatenate((spec.loc[...,'po3p3p'].values[...,None],
                        spec.loc[...,'po3p5p'].values[...,None]),axis=-1)

    return catvl(spec.alt_km,ver,vnew,lamb,lambnew,br)

def getN21NG(spec,ver,lamb,br, reactfn):
    """
    excitation Franck-Condon factors (derived from Vallance Jones, 1974)
    """
    with h5py.File(str(reactfn),'r',libver='latest') as f:
        A = f['/N2+1NG/A'].value
        lambdaA = f['/N2+1NG/lambda'].value.ravel(order='F')
        franckcondon = f['/N2+1NG/fc'].value

    return doBandTrapz(A,lambdaA,franckcondon, spec.loc[...,'p1ng'],lamb,ver,spec.alt_km,br)

def getN2meinel(spec,ver,lamb,br,reactfn):
    with h5py.File(str(reactfn),'r',libver='latest') as f:
        A = f['/N2+Meinel/A'].value
        lambdaA = f['/N2+Meinel/lambda'].value.ravel(order='F')
        franckcondon = f['/N2+Meinel/fc'].value
    #normalize
    franckcondon = franckcondon/franckcondon.sum() #special to this case

    return doBandTrapz(A,lambdaA,franckcondon, spec.loc[...,'pmein'],lamb,ver,spec.alt_km,br)

def getN22PG(spec,ver,lamb,br,reactfn):
    """ from Benesch et al, 1966a """
    with h5py.File(str(reactfn),'r',libver='latest') as f:
        A = f['/N2_2PG/A'].value
        lambdaA = f['/N2_2PG/lambda'].value.ravel(order='F')
        franckcondon = f['/N2_2PG/fc'].value

    return doBandTrapz(A,lambdaA,franckcondon,spec.loc[...,'p2pg'],lamb,ver,spec.alt_km,br)

def getN21PG(spec,ver,lamb,br,reactfn):

    with h5py.File(str(reactfn),'r',libver='latest') as fid:
        A = fid['/N2_1PG/A'].value
        lambnew = fid['/N2_1PG/lambda'].value.ravel(order='F')
        franckcondon = fid['/N2_1PG/fc'].value

    tau1PG = 1 / nansum(A,axis=1)
    """
    solve for base concentration
    confac=[1.66;1.56;1.31;1.07;.77;.5;.33;.17;.08;.04;.02;.004;.001];  %Cartwright, 1973b, stop at nuprime==12
    Gattinger and Vallance Jones 1974
    confac=array([1.66,1.86,1.57,1.07,.76,.45,.25,.14,.07,.03,.01,.004,.001])
    """

    consfac = franckcondon/franckcondon.sum() #normalize
    losscoef = (consfac / tau1PG).sum()
    N01pg=spec.loc[...,'p1pg'] / losscoef

    scalevec = (A * consfac[:,None]).ravel(order='F') #for clarity (verified with matlab)

    vnew = scalevec[None,None,:] * N01pg.values[...,None]

    return catvl(spec.alt_km,ver,vnew,lamb,lambnew,br)

def doBandTrapz(Aein,lambnew,fc,kin,lamb,ver,z,br):
    """
    ver dimensions: wavelength, altitude, time

     A and lambda dimensions:
    axis 0 is upper state vib. level (nu')
    axis 1 is bottom state vib level (nu'')
    there is a Franck-Condon parameter (variable fc) for each upper state nu'
    """
    tau=1/nansum(Aein,axis=1)

    scalevec = (Aein * tau[:,None] * fc[:,None]).ravel(order='F')

    vnew = scalevec[None,None,:]*kin.values[...,None]

    return catvl(z,ver,vnew,lamb,lambnew,br)

def catvl(z,ver,vnew,lamb,lambnew,br):
    """
    trapz integrates over axis=1, the altitude dimension
    concatenate over reaction dimension, axis=-1
    """
    if ver is not None:
        br = concatenate((br,trapz(vnew,z,axis=1)), axis=-1) #must come first!
        ver=concatenate((ver,vnew), axis=-1)
        lamb=concatenate((lamb,lambnew))
    else:
        ver = vnew.copy(order='F')
        lamb = lambnew.copy()
        br = trapz(ver,z,axis=1)

    return ver, lamb, br

def sortelimlambda(lamb,ver,br):
    assert lamb.ndim == 1
    assert lamb.size == ver.shape[-1]
#%% eliminate unused wavelengths and Einstein coeff
    mask = isfinite(lamb)
    ver = ver[...,mask]
    lamb = lamb[mask]
    br = br[:,mask]
#%% sort by lambda
    lambSortInd = lamb.argsort() #lamb is made piecemeal and is overall non-monotonic

    return lamb[lambSortInd], ver[...,lambSortInd],br[:,lambSortInd] #sort by wavelength ascending order

#%% plots

def showIncrVER(tTC,tReqInd,tctime,ver,tver,titxt,makePlots):
    saveplot = False
    z = ver.columns.values
    lamb = ver.index.values

    if 'spectra1d' in makePlots:
        b = trapz(ver,z,axis=1) #integrate along z, looking up magnetic zenith
        plotspectra(b,lamb)

    if 'eigtime' in makePlots:
        fg = figure(figsize=(11,8),dpi=100,tight_layout=True); ax = fg.gca()

        pcm = ax.pcolormesh(tTC, z, tver.sum(axis=0), #sum over wavelength
                            edgecolors='none',cmap=None,norm=None,
                            vmin=0,vmax=1e3)

        ax.axvline(tTC[tReqInd], color='white', linestyle='--',label='Req. Time')
        ax.axvline(tctime['tstartPrecip'], color='red', linestyle='--', label='Precip. Start')
        ax.axvline(tctime['tendPrecip'], color='red', linestyle='--',label='Precip. End')


        titlemean = titxt + ('\n VER/flux: $\lambda \in$' +
                             str(lamb) + ' [nm]' +
                             '\n geodetic lat:' +str(tctime['latgeo_ini'])
                             + ' lon:' + str(tctime['longeo_ini']) +
                             ' date: ' + tctime['dayofsim'].strftime('%Y-%m-%d') )
#make room for long title
        fg.subplots_adjust(top=0.8)

        ax.set_title(titlemean,fontsize=9)

        ax.yaxis.set_major_locator(MultipleLocator(100))
        ax.yaxis.set_minor_locator(MultipleLocator(20))

        #ax.xaxis.set_major_locator(MinuteLocator(interval=10))
        ax.xaxis.set_major_locator(MinuteLocator(interval=1))
        ax.xaxis.set_minor_locator(SecondLocator(interval=10))
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

        ax.tick_params(axis='both', which='both', direction='out',labelsize=12)

        ax.autoscale(True,tight=True)
        cbar = fg.colorbar(pcm)
        cbar.set_label('VER/flux',labelpad=0)
        ax.set_xlabel('Time [UTC]')
        ax.set_ylabel('altitude [km]')
        if saveplot:
            sfn = ''.join(e for e in titxt if e.isalnum() or e=='.') #remove special characters
            fg.savefig('out/VER' + sfn + '.png',dpi=150,bbox_inches='tight')
            close(fg)

    if 'eigtime1d' in makePlots:
        fg = figure(figsize=(11,8),dpi=100); ax = fg.gca()
        #fg.subplots_adjust(top=0.85)
        thistitle = titxt + ': {:d} emission lines\n VER/flux:  geodetic lat: {} lon: {}  {}'.format(ver.shape[0],tctime['latgeo_ini'],tctime['longeo_ini'],tTC[tReqInd])
        ax.set_title(thistitle, fontsize=12)
        ax.set_xlabel('VER/flux')
        ax.set_ylabel('altitude [km]')

        for ifg,clamb in enumerate(lamb):
            ax.semilogx(ver.iloc[ifg,:],z,label=str(clamb))

        ax.yaxis.set_major_locator(MultipleLocator(100))
        ax.yaxis.set_minor_locator(MultipleLocator(20))
        ax.grid(True)
        if ver.shape[0]<20:
            ax.legend(loc='upper center', bbox_to_anchor=(1.05, .95),
                                 ncol=1, fancybox=True, shadow=True,fontsize=9)

        ax.tick_params(axis='both', which='both', direction='in', labelsize=12)

        ax.set_xlim(1e-9,1e3)
        ax.set_ylim((z[0],z[-1]))

        if saveplot:
            sfn = ''.join(e for e in titxt if e.isalnum()) #remove special characters
            fg.savefig('out/VER' + sfn + '.png', dpi=150, bbox_inches='tight')
            close(fg)

def plotspectra(br,optT,E,lambminmax):

    lamb = optT.wavelength_nm

    def _plotspectrasub(ax,bf,txt):
        ax.set_yscale('log')
        ax.set_title('Auroral spectrum, ' +  txt +
                     ',integrated along flux tube: $E_0$ = {:.0f} eV'.format(E))
        ax.set_ylabel('optical intensity')
        ax.set_xlim(lambminmax)
        ax.set_ylim(spectraAminmax)
        ax.xaxis.set_major_locator(MultipleLocator(100))
        #ax.invert_xaxis()

        for l in spectrallines:
            ax.text(l,bf[l]*1.7, '{:.1f}'.format(l),
                    ha='center',va='bottom',fontsize='medium',rotation=60)

#%%
    fg,((ax1,ax2)) = subplots(2,1,sharex=True,figsize=(10,8))
    bf=br*optT['sysNObg3']
    ax1.stem(lamb,bf)
    _plotspectrasub(ax1,bf,'no filter')


    bf=br*optT['sys']
    ax2.stem(lamb,bf)
    _plotspectrasub(ax2,bf,'BG3 filter')
    ax2.set_xlabel('wavelength [nm]')

    return fg
