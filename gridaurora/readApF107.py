"""
We should use:
ftp://ftp.ngdc.noaa.gov/STP/GEOMAGNETIC_DATA/INDICES/KP_AP/

but for now use:
ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt

Michael Hirsch
"""
from os.path import expanduser,isfile
from numpy import loadtxt,nan
from pandas import DataFrame

def readmonthly(fn):
    fn = expanduser(fn)

    if not isfile(fn):
        raise FileNotFoundError('download from ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt')

    d = loadtxt(fn,comments=('#',':'), usecols=(0,1,7,8,9,10))

    ind=[]
    for ym in d[:,:2]:
        ind.append(int(str(int(ym[0])) + '{:02d}'.format(int(ym[1]))))

    data = DataFrame(index=ind,data=d[:,2:],columns=['f107o','f107s','Apo','Aps'])

    data[data==-1] = nan #by defn of NOAA

    return data

if __name__ == '__main__':
    data = readmonthly('RecentIndices.txt')