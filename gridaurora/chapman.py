from numpy import exp

def chapman_profile(Z0,zKM,H):
    """
    Z0: altitude [km] of intensity peak
    zKM: altitude grid [km]
    H: scale height [km]

    example:
    pz = chapman_profile(110,np.arange(90,200,1),20)
    """
    return exp(.5*(1-(zKM-Z0)/H - exp((Z0-zKM)/H)))