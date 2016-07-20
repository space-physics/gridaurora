#!/usr/bin/env python
"""
inspired by Matt Zettergren
Michael Hirsch
"""
from numpy import tanh, linspace, cumsum, insert, gradient, median

def setupz(np,zmin,gridmin,gridmax):
    """
    np: number of grid points
    zmin: minimum STEP SIZE at minimum grid altitude [km]
    gridmin: minimum altitude of grid [km]
    gridmax: maximum altitude of grid [km]
    """

    dz = _ztanh(np,gridmin,gridmax)

    return insert(cumsum(dz)+zmin, 0, zmin)[:-1]

def _ztanh(np,gridmin,gridmax):
    """
    typically call via setupz instead
    """
    x0 = linspace(0, 3.14, np) #arbitrarily picking 3.14 as where tanh gets to 99% of asymptote
    return tanh(x0)*gridmax+gridmin

#def zexp(np,gridmin):
#    x0 = linspace(0, 1, np)
#    return exp(x0)**2+(gridmin-1)

def plotz(z):
    dz = gradient(z,edge_order=2) #numpy>=1.9.1
    dzmed = median(dz)

    ax = figure().gca()
    ax.plot(dz,z)
    ax.axvline(dzmed,color='r',linestyle='--', label='median')
    ax.set_xlabel('grid spacing [km]')
    ax.set_ylabel('altitude [km]')
    ax.set_title('$N_p=$'+str(z.shape[0]))
    ax.grid(True)
    ax.legend(loc='best')

if __name__ == '__main__':
    from matplotlib.pyplot import figure, show
    from argparse import ArgumentParser
    p = ArgumentParser(description='create continuously step sized grid')
    p.add_argument('-n','--np',help='number of points in grid',type=int,default=300)
    p.add_argument('--zmin',help='bottom of grid',type=float,default=90)
    p.add_argument('--gmin',help='minimum grid spacing',type=float,default=1.5)
    p.add_argument('--gmax',help='max grid spacing',type=float,default=10.575)
    a = p.parse_args()

    zgrid = setupz(a.np,a.zmin,a.gmin,a.gmax)
    plotz(zgrid)
    print(zgrid[-1])

    show()
