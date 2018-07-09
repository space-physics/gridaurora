#!/usr/bin/env python
"""
A collection of models and parameterizations for differential number flux,
typically taken in the collisonless region "above the top of the ionosphere"
as is commonly stated.
"""
from numpy import gradient, exp, logspace, asarray, atleast_1d
from matplotlib.pyplot import figure,show
from argparse import ArgumentParser


def EllisonRamaty(E: np.ndarray, E0: np.ndarray, gamma: np.ndarray, kappa: np.ndarra, C0: np.ndarray):
    E,E0,gamma,kappa,C0 = dimhandler(E,E0,gamma,kappa,C0)
#%% do work
    return C0 * E[:,None]**(-gamma) * exp(-((E[:,None]-E0)/gradient(E)[:,None])**kappa)

def dimhandler(E,E0,gamma,kappa,C0=None):
#%% lite input validation
    E = asarray(E); E0 = atleast_1d(E0); gamma = atleast_1d(gamma); kappa = atleast_1d(kappa)
    C0 = atleast_1d(C0)
    assert E.ndim == 1 and E0.ndim == 1 and gamma.ndim ==1 and kappa.ndim ==1 and C0.ndim==1,'E0, gamma, kappa, C0 must be scalar or vector. E must be vector'

    return E,E0,gamma,kappa,C0

def plotdnf(E,phi,E0,gamma,kappa):
    E,E0,gamma,kappa = dimhandler(E,E0,gamma,kappa)[:4]

    if gamma.size>1:
        labels = map(str,gamma)
    elif kappa.size>1:
        labels = map(str,kappa)
    else:
        labels = map(str,E0)

    ax = figure().gca()
    lines = ax.loglog(E,phi,marker='*')
    ax.set_xlabel("Particle beam energy [eV]")
    ax.set_ylabel("Flux [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]")
    ax.tick_params(axis='both', which='major', labelsize='large')
    ax.grid(True)
    ax.legend(lines,labels,loc='best')
    

def main():
    p = ArgumentParser(description="differential number flux parameterizations")
    p.add_argument('E0',help='characteristic energy [eV]',nargs='+',type=float)
    p.add_argument('-g','--gamma',help='gamma parameter',nargs='+',type=float,default=-1)
    p.add_argument('-k','--kappa',help='kappa parameter',nargs='+',type=float,default=1)
    p.add_argument('-c','--C0',help='scaling constant',type=float,default=1)
    p = p.parse_args()

    E = logspace(1.7,4.5,num=33,base=10)

    phi =  EllisonRamaty(E,p.E0,p.gamma,p.kappa,p.C0)

    plotdnf(E,phi,p.E0,p.gamma,p.kappa)
    show()


if __name__ == '__main__':
    main()
