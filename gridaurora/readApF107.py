"""
We should use:
ftp://ftp.ngdc.noaa.gov/STP/GEOMAGNETIC_DATA/INDICES/KP_AP/

but for now use:
ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt

Michael Hirsch
"""
from os.path import expanduser,isfile
from six import integer_types,PY2
from numpy import loadtxt,nan
from pandas import DataFrame
if PY2: FileNotFoundError = IOError

def readmonthlyApF107(yearmon,fn='RecentIndices.txt'):
    assert isinstance(yearmon,(integer_types))

    fn = expanduser(fn)

    if not isfile(fn):
        raise FileNotFoundError('download from ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt')

    d = loadtxt(fn,comments=('#',':'), usecols=(0,1,7,8,9,10))

    ind=[]
    for ym in d[:,:2]:
        ind.append(int(str(int(ym[0])) + '{:02d}'.format(int(ym[1]))))

    data = DataFrame(index=ind,data=d[:,2:],columns=['f107o','f107s','Apo','Aps'])

    data[data==-1] = nan #by defn of NOAA

    ApF107 = data.loc[yearmon,:]

    return ApF107

if __name__ == '__main__':
    data = readmonthlyApF107('RecentIndices.txt')