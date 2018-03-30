from pathlib import Path
from datetime import datetime
from dateutil.parser import parse
import numpy as np
import xarray
import logging
from typing import Union
import urllib.request

URL = 'ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt'

def readmonthlyApF107(yearmon:Union[str,datetime], fn:Union[str,Path]=None, forcedownload:bool=False) -> xarray.Dataset:
    """
    We should use:
    ftp://ftp.ngdc.noaa.gov/STP/GEOMAGNETIC_DATA/INDICES/KP_AP/

    but for now use:
    ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt

    Michael Hirsch, Ph.D.
    """
    if not fn:
        fn = Path(__file__).parent / 'data' / 'RecentIndices.txt'
        fn.parent.mkdir(exist_ok=True)

    fn = Path(fn).expanduser()
#%% date handle
    if isinstance(yearmon,(tuple,list,np.ndarray)):
        logging.warning(f'taking only first time {yearmon[0]}, would you like multiple times upgrade to code?')
        yearmon = yearmon[0]

    if isinstance(yearmon, str):
        yearmon = parse(yearmon)
    elif isinstance(yearmon,np.datetime64):
        yearmon = yearmon.astype(datetime)

    #not elif
    if isinstance(yearmon, datetime):
        yearmon = int(f'{yearmon.year:d}{yearmon.month:02d}')

    assert isinstance(yearmon,int)
#%% load data
    if not fn.is_file() or forcedownload:
        logging.warning(f'attemping download to {fn} from ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt')
        urllib.request.urlretrieve(URL,fn)

    dat = np.loadtxt(fn, comments=('#',':'), usecols=(0,1,7,8,9,10))
#  genfromtxt didn't eliminate missing values, unsure if bug
#    d = genfromtxt(fn,comments='#', usecols=(0,1,7,8,9,10), skip_header=2,dtype=float,
 #                missing_values={-1:-1},filling_values={-1:nan},invalid_raise=False)
#%% process and pack data
    yearmonth= [int(f'{ym[0]:.0f}{ym[1]:02.0f}') for ym in dat[:,:2]]

    data = xarray.Dataset({'f107o':('time',dat[:,2]),
                           'f107s':('time',dat[:,3]),
                           'Apo':('time',dat[:,4]),
                           'Aps':('time',dat[:,5]),},
                            coords={'time':yearmonth})

    data = data.fillna(-1) #by defn of NOAA
# %% pull out the time we want
    ApF107 = data.sel(time=yearmon)

    return ApF107
