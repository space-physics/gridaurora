from pathlib import Path
from datetime import datetime
from dateutil.parser import parse
import numpy as np
import xarray
import logging
from typing import Union
import urllib.request

URL = 'ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt'


def readmonthlyApF107(yearmon: Union[int, str, datetime], fn: Union[str, Path]=None,
                      forcedownload: bool=False) -> xarray.Dataset:
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
# %% date handle
    if isinstance(yearmon, (tuple, list, np.ndarray)):
        logging.warning(f'taking only first time {yearmon[0]}, would you like multiple times upgrade to code?')
        yearmon = yearmon[0]

    if isinstance(yearmon, str):
        yearmon = parse(yearmon)
    elif isinstance(yearmon, np.datetime64):
        yearmon = yearmon.astype(datetime)

    # not elif
    if isinstance(yearmon, datetime):
        yearmon = int(f'{yearmon.year:d}{yearmon.month:02d}')

    assert isinstance(yearmon, int)
# %% load data
    if not fn.is_file() or forcedownload:
        logging.warning(f'attemping download to {fn} from ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt')
        urllib.request.urlretrieve(URL, fn)  # type: ignore

    dat = np.loadtxt(fn, comments=('#', ':'), usecols=(0, 1, 7, 8, 9, 10))
#  genfromtxt didn't eliminate missing values, unsure if bug
#    d = genfromtxt(fn,comments='#', usecols=(0,1,7,8,9,10), skip_header=2,dtype=float,
#                missing_values={-1:-1},filling_values={-1:nan},invalid_raise=False)
# %% process and pack data
    yearmonth = [int(f'{ym[0]:.0f}{ym[1]:02.0f}') for ym in dat[:, :2]]

    data = xarray.Dataset({'f107o': ('time', dat[:, 2]),
                           'f107s': ('time', dat[:, 3]),
                           'Apo': ('time', dat[:, 4]),
                           'Aps': ('time', dat[:, 5]), },
                          coords={'time': yearmonth})

    data = data.fillna(-1)  # by defn of NOAA
# %% pull out the time we want
    try:
        ApF107 = data.sel(time=yearmon)
    except KeyError as e:
        logging.error(f'{yearmon} is not in the Indices file. Using last available time {data.time[-1].item()}.  {e}')
        ApF107 = data.sel(time=data.time[-1])

    return ApF107


def to_ut1unix(time: Union[str, datetime, float, np.ndarray]) -> np.ndarray:
    """
    converts time inputs to UT1 seconds since Unix epoch
    """
    # keep this order
    time = totime(time)

    if isinstance(time[0], (float, int)):
        return time

    assert isinstance(time, (tuple, list, np.ndarray))
    assert isinstance(time[0], datetime), f'expected datetime, not {type(time[0])}'

    return np.array(list(map(dt2ut1, time)))


def dt2ut1(t: datetime) -> float:
    epoch = datetime(1970, 1, 1)
    assert isinstance(t, datetime)

    return (t-epoch).total_seconds()


def totime(time: Union[str, datetime, np.datetime64]) -> np.ndarray:
    time = np.atleast_1d(time)

    if isinstance(time[0], (datetime, np.datetime64)):
        pass
    elif isinstance(time[0], str):
        time = np.atleast_1d(list(map(parse, time)))

    return time


def chapman_profile(Z0: float, zKM: np.ndarray, H: float):
    """
    Z0: altitude [km] of intensity peak
    zKM: altitude grid [km]
    H: scale height [km]

    example:
    pz = chapman_profile(110,np.arange(90,200,1),20)
    """
    return np.exp(.5*(1-(zKM-Z0)/H - np.exp((Z0-zKM)/H)))
