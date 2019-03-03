"""
load and plot transcar energy grid
Egrid is not what's used externally by other programs, but rather variable "bins"
"""
from pathlib import Path
import xarray
import numpy as np
from scipy.stats import linregress
from matplotlib.pyplot import figure

flux0 = 70114000000.0
Nold = 33
Nnew = 81  # 100MeV


def loadregress(fn: Path):
    # %%
    Egrid = np.loadtxt(Path(fn).expanduser(), delimiter=',')
#    Ematt = asarray([logspace(1.7220248253079387,4.2082263059355824,num=Nold,base=10),
#                    #[logspace(3.9651086925197356,9.689799159992674,num=33,base=exp(1)),
#                     logspace(1.8031633895706722,4.2851520785250914,num=Nold,base=10)]).T
# %% log-lin regression
    Enew = np.empty((Nnew, 4))
    Enew[:Nold, :] = Egrid
    for k in range(4):
        s, i = linregress(range(Nold), np.log10(Egrid[:, k]))[:2]
        Enew[Nold:, k] = 10**(np.arange(Nold, Nnew)*s+i)

    return Enew


def doplot(fn: Path, bins: xarray.DataArray, Egrid: np.ndarray = None, debug: bool = False):
    # %% main plot
    ax = figure().gca()
    ax.bar(left=bins.loc[:, 'low'],
           height=bins.loc[:, 'flux'],
           width=bins.loc[:, 'high']-bins.loc[:, 'low'])
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylabel('flux [s$^{-1}$ sr$^{-1}$ cm$^{-2}$ eV$^{-1}$]')
    ax.set_xlabel('bin energy [eV]')
    ax.set_title(f'Input flux used to generate eigenprofiles, based on {fn}')

# %% debug plots
    if debug:
        ax = figure().gca()
        bins[['low', 'high']].plot(logy=True, ax=ax, marker='.')
        ax.set_xlabel('bin number')
        ax.set_ylabel('bin energy [eV]')

        ax = figure().gca()
        bins['flux'].plot(logy=True, ax=ax, marker='.')
        ax.set_xlabel('bin number')
        ax.set_ylabel('flux [s$^{-1}$ sr$^{-1}$ cm$^{-2}$ eV$^{-1}$]')

        if Egrid is not None:
            ax = figure().gca()
            ax.plot(Egrid, marker='.')
            # ax.plot(Ematt,marker='.',color='k')
            ax.set_yscale('log')
            ax.set_ylabel('eV')
            ax.legend(['E1', 'E2', 'pr1', 'pr2'], loc='best')


def makebin(Egrid: np.ndarray):
    E1 = Egrid[:, 0]
    E2 = Egrid[:, 1]
    pr1 = Egrid[:, 2]
    pr2 = Egrid[:, 3]

    dE = E2-E1
    Esum = E2+E1
    flux = flux0 / 0.5 / Esum / dE
    Elow = E1 - 0.5*(E1 - pr1)
    Ehigh = E2 - 0.5*(E2 - pr2)

    E = np.column_stack((Elow, Ehigh, flux))

    Ed = xarray.DataArray(data=E, dims=['energy', 'type'])
    Ed['type'] = ['low', 'high', 'flux']

    return Ed
