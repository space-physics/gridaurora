from pathlib import Path
from datetime import datetime, date, timedelta
from dateutil.parser import parse
import numpy as np
import xarray
import logging
from typing import Union, Tuple
import urllib.request
from sciencedates import yeardec2datetime

URLrecent = 'ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt'
URL45dayfcast = 'http://services.swpc.noaa.gov/text/45-day-ap-forecast.txt'
URL20yearfcast = 'https://sail.msfc.nasa.gov/solar_report_archives/May2016Rpt.pdf'

def getApF107(time: Union[str, datetime],
              forcedownload: bool=False) -> xarray.Dataset:
    """
    alternative going back to 1931:
    ftp://ftp.ngdc.noaa.gov/STP/GEOMAGNETIC_DATA/INDICES/KP_AP/

    20 year Forecast data from:
    https://sail.msfc.nasa.gov/solar_report_archives/May2016Rpt.pdf
    """
    time = totime(time).squeeze()[()]

    if isinstance(time, datetime):
        time = time.date()

    assert isinstance(time, date)

    fn,url = selectApfile(time)

    if not fn.is_file() or forcedownload:
        print(f'download {fn} from {url}')
        urllib.request.urlretrieve(url, fn)  # type: ignore
# %%
    fn = Path(fn).expanduser()
    if not fn.is_file():
        raise FileNotFoundError(f'{fn} not found.')


    if fn.name == URLrecent.split('/')[-1]:
        dat = readpast(fn)
    elif fn.name == URL45dayfcast.split('/')[-1]:
        dat = read45dayfcast(fn)
    elif fn.name == URL20yearfcast.split('/')[-1].split('.')[0] + '.txt':
        dat = read20yearfcast(fn)
    else:
        raise FileNotFoundError(f'could not determine if you have or which file to read for {time}')
# %% pull out the time we want
    Indices = dat.sel(time=time, method='nearest')

    return Indices


def read20yearfcast(fn: Path) -> xarray.Dataset:
    """
    uses 50th percentile of Ap and f10.7
    """
    dat = np.loadtxt(fn, usecols=(0,3,6), skiprows=11)

    time = yeardec2datetime(dat[:,0])

    date = [t.date() for t in time]

    data = xarray.Dataset({'Ap': ('time', dat[:,1]),
                           'f107': ('time', dat[:,2])},
                          coords={'time':date})

    return data


def readpast(fn: Path) -> xarray.Dataset:
    dat = np.loadtxt(fn, comments=('#', ':'), usecols=(0, 1, 7, 8, 9, 10))
    date = [parse(f'{ym[0]:.0f}-{ym[1]:02.0f}-01').date() for ym in dat[:, :2]]


    data = xarray.Dataset({'f107': ('time', dat[:, 2]),
                           'f107_smoothed': ('time', dat[:, 3]),
                           'Ap': ('time', dat[:, 4]),
                           'Ap_smoothed': ('time', dat[:, 5]), },
                          coords={'time': date})

    data = data.fillna(-1)  # by defn of NOAA

    return data

def read45dayfcast(fn: Path) -> xarray.Dataset:
    Ap = []
    time = []

    with fn.open('r') as f:
        for line in f:
            if line[0] in ('#', ':') or line.startswith('45-DAY AP FORECAST'):
                continue
            elif line.startswith('45-DAY F10.7 CM FLUX FORECAST'):
                break
# %% Ap
            ls = line.split()
            for t,a in zip(ls[::2], ls[1::2]):
                time.append(parse(t).date())
                Ap.append(int(a))

        dat = xarray.Dataset({'Ap': ('time',Ap)},
                            coords={'time':time})
# %% F10.7
        time = []
        f107 = []
        for line in f:
            if line.startswith('FORECASTER'):
                break

            ls = line.split()
            for t,a in zip(ls[::2], ls[1::2]):
                time.append(parse(t).date())
                f107.append(int(a))

        dat['f107'] = ('time',f107)


    return dat

def selectApfile(time: Union[datetime, date]) -> Tuple[Path, str]:
    path = Path(__file__).parent / 'data'
    path.mkdir(exist_ok=True)

    if isinstance(time, datetime):
        time = time.date()

    tnow = date.today()

    if time < tnow:  # past
        url = URLrecent
        fn = path / url.split('/')[-1]
    elif tnow <= time < tnow + timedelta(days=45):  # near future
        url = URL45dayfcast
        fn = path / url.split('/')[-1]
    else:  # future
        url = URL20yearfcast
        rawfn = path / url.split('/')[-1]
        fn = path / rawfn.with_suffix('.txt')

    return fn, url


def toyearmon(time: datetime) -> int:
    # %% date handle
    if isinstance(time, (tuple, list, np.ndarray)):
        logging.warning(f'taking only first time {time[0]}, would you like multiple times upgrade to code?')
        time = time[0]

    if isinstance(time, str):
        time = parse(time)
    elif isinstance(time, np.datetime64):
        time = time.astype(datetime)
    elif isinstance(time, (datetime,date)):
        pass
    else:
        raise TypeError(f'not sure what to do with type {type(time)}')

    ym = int(f'{time.year:d}{time.month:02d}')

    return ym


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
