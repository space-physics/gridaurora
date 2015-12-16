from __future__ import division,absolute_import,unicode_literals
from six import integer_types
import logging
from datetime import datetime
from pathlib2 import Path
from numpy import in1d,array
from numpy.ma import masked_invalid #for pcolormesh, which doesn't like NaN
from matplotlib.pyplot import figure,draw
from matplotlib.colors import LogNorm
from matplotlib.ticker import MultipleLocator

dpi=100 #IEEE Transactions requires 600 dpi

dymaj=100
dymin=20

def writeplots(fg,plotprefix,tind,method,odir,overridefmt=None,anno=None):
    draw() #Must have this here or plot doesn't update in animation multiplot mode!
    #TIF was not faster and was 100 times the file size!
    #PGF is slow and big file,
    #RAW crashes
    #JPG no faster than PNG
    tmpl = ('eps','jpg','png','pdf')
    used = in1d(tmpl,method)
    if used.any():
        if overridefmt is not None:
            fmt = overridefmt
        else:
            fmt = array(tmpl)[used][0]

        suff = nametime(tind)

        if anno:
            fg.text(0.15,0.8,anno,fontsize='x-large')

        cn = (Path(odir) / (plotprefix + suff + '.{}'.format(fmt))).expanduser()
        print('write {}'.format(cn))
        fg.savefig(str(cn),bbox_inches='tight',dpi=dpi)  # this is slow and async

def nametime(tind):
    if isinstance(tind,integer_types) and tind<1e6:
        return '{:03d}'.format(tind)
    elif isinstance(tind,datetime):
        return tind.strftime('%Y-%m-%dT%H:%M:%S') 
    elif tind is not None:
        return str(tind)
    else: #is None
        return ''
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
