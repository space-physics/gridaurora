import logging
import pathvalidate
from datetime import datetime
from pathlib import Path
from numpy import isscalar
from numpy.ma import masked_invalid #for pcolormesh, which doesn't like NaN
from matplotlib.pyplot import figure,draw,close,subplots
from matplotlib.colors import LogNorm
from matplotlib.ticker import MultipleLocator

#IEEE Transactions requires 600 dpi

dymaj=100
dymin=20

def writeplots(fg,plotprefix,tind=None,odir=None, fmt='.png', anno=None,dpi=None,facecolor=None,doclose=True):
    try:
        if fg is None or odir is None:
            return
    #%%
        draw() #Must have this here or plot doesn't update in animation multiplot mode!
        #TIF was not faster and was 100 times the file size!
        #PGF is slow and big file,
        #RAW crashes
        #JPG no faster than PNG

        suff = nametime(tind)

        if anno:
            fg.text(0.15,0.8,anno,fontsize='x-large')

        cn = Path(odir).expanduser() / pathvalidate.sanitize_filename(plotprefix + suff + fmt)
        print('write {}'.format(cn))

        if facecolor is None:
            facecolor=fg.get_facecolor()

        fg.savefig(str(cn),bbox_inches='tight',dpi=dpi, facecolor=facecolor, edgecolor='none')

        if doclose:
            close(fg)

    except Exception as e:
        logging.error('{}  when plotting {}'.format(e,plotprefix))

def nametime(tind):
    if isinstance(tind,int) and tind<1e6:
        return '{:03d}'.format(tind)
    elif isinstance(tind,datetime):
        return tind.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] #-3 truncates to millisecond digits only (arbitrary)
    elif tind is not None:
        return str(tind)
    else: #is None
        return ''
#%%
def plotflux(E,E0, arc, base=None,hi=None,low=None,mid=None,ttxt='Differential Number Flux'):
    FMAX = 1e6
    FMIN = 1e2

    lblstr = ['{:.0f}'.format(e0) for e0 in E0]

    ax = figure().gca()
    if isscalar(E0) and mid is not None:
        ax.loglog(E,hi,'k:')
        ax.loglog(E,low,'k:')
        ax.loglog(E,mid,'k:')
        ax.loglog(E,base,color='k')
    ax.loglog(E,arc,linewidth=2)

    ax.grid(True,which='both')
    ax.set_xlabel('Electron Energy [eV]')#,fontsize=afs,labelpad=-2)
    ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')#,fontsize=afs)
    ax.set_title(ttxt)
    #ax.tick_params(axis='both', which='both')
    ax.autoscale(True,tight=True)
    ax.set_ylim((1e2,FMAX))
    ax.legend(lblstr,loc='best')#,prop={'size':'large'})
    #ax.set_xlim((1e2,1e4))
   # sns.despine(ax=ax)

    if base is not None:
        ax = figure().gca()
        ax.loglog(E,base)
        ax.set_ylim((FMIN, FMAX))
        #ax.set_xlim((1e2,1e4))
        ax.set_title('arc Gaussian base function, E0=' + str(E0)+ '[eV]' +
                     '\n Wbc: width, Q0: height')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
        ax.legend(lblstr)

        ax = figure().gca()
        ax.loglog(E,low)
        ax.set_ylim((FMIN, FMAX))
        ax.set_title('arc low (E<E0).  Bl: height, bh: slope')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')

        ax = figure().gca()
        ax.loglog(E,mid)
        ax.set_ylim((FMIN, FMAX))
        ax.set_title('arc mid.  Bm:height, bm: slope')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')

        ax = figure().gca()
        ax.loglog(E,hi)
        ax.set_ylim((FMIN, FMAX))
        ax.set_title('arc hi (E>E0).  Bhf: height, bh: slope')
        ax.set_xlabel('Electron Energy [eV]')
        ax.set_ylabel('Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]')
#%%
def ploteigver(EKpcolor,zKM,eigenprofile,
               vlim=(None,)*6,sim=None,tInd=None,makeplot=None,prefix=None,progms=None):
    try:
        fg = figure(); ax = fg.gca()
        #pcolormesh canNOT handle nan at all
        pcm = ax.pcolormesh(EKpcolor, zKM, masked_invalid(eigenprofile),
                            edgecolors='none',#cmap=pcmcmap,
                            norm=LogNorm(),
                            vmin=vlim[4], vmax=vlim[5])
        ax.set_xlabel('Energy [eV]')
        ax.set_ylabel('$B_\parallel$ [km]')
        ax.autoscale(True,tight=True)
        ax.set_xscale('log')
        ax.yaxis.set_major_locator(MultipleLocator(dymaj))
        ax.yaxis.set_minor_locator(MultipleLocator(dymin))
#%% title
        if tInd is not None:
            mptitle = str(tInd)
        else:
            mptitle=''
        mptitle += '$P_{{eig}}$'
        if sim:
            mptitle += ', filter: {}'.format(sim.opticalfilter)
            mptitle += str(sim.reacreq)

        ax.set_title(mptitle)#,fontsize=tfs)
#%% colorbar
        cbar = fg.colorbar(pcm,ax=ax)
        cbar.set_label('[photons cm$^{-3}$s$^{-1}$]',labelpad=0)#,fontsize=afs)
       # cbar.ax.tick_params(labelsize=afs)
        #cbar.ax.yaxis.get_offset_text().set_size(afs)
#%% ticks,lim
        ax.tick_params(axis='both', which='both', direction='out')
        ax.set_ylim(vlim[2:4])
#%%
        writeplots(fg,prefix,tInd,makeplot,progms)
    except Exception as e:
        logging.error('tind {}   {}'.format(tInd,e))

def plotT(T,mmsl,name=''):

    ax1 = figure().gca()
    for c in ['filter','window','qe','atm']:
        ax1.plot(T.wavelength_nm, T.sel(filt=c),label=c)
    ax1.set_xlim(mmsl[:2])
    ax1.set_title('{}  Component transmittance'.format(name))
#
    ax2 = figure().gca()
    for s in ['sys','sysNObg3']:
        ax2.plot(T.wavelength_nm, T.sel(filt=s), label=s)

    ax2.set_title('{}  System Transmittance'.format(name))

    for a in (ax1,ax2):
        niceTax(a)


def niceTax(a):
    a.set_xlabel('wavelength (nm)')
    a.set_ylabel('Transmittance (unitless)')
 #   a.set_yscale('log')
    a.legend(loc='best')
#    a.set_ylim(1e-2,1)
    a.invert_xaxis()
    a.grid(True,which='both')

def comparefilters(Ts,names):

    fg, axs = subplots(len(Ts),1,sharex=True,sharey=True)

    for T,name,ax in zip(Ts,names,axs):
        try:
            ax.plot(T.wavelength_nm, T.sel(filt='filter'), label=name)
        except ValueError: # just a plain filter
            assert T.ndim==1
            ax.plot(T.wavelength_nm, T, label=name)

        forbidden = [630.,555.7,]
        permitted = [391.4,427.8,844.6,777.4]
        for l in forbidden:
            ax.axvline(l,linestyle='--',color='darkred',alpha=0.8)
        for l in permitted:
            ax.axvline(l,linestyle='--',color='darkgreen',alpha=0.8)

        ax.set_title('{}'.format(name))

    fg.suptitle('Transmittance')

    ax.set_ylim((0,1))
    ax.set_xlim(T.wavelength_nm[[-1,0]])
    ax.set_xlabel('wavelength [nm]')
