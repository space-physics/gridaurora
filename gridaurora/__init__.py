from datetime import datetime, date
from dateutil.parser import parse
import numpy as np
import logging
from typing import Union


def toyearmon(time: datetime) -> int:
    # %% date handle
    if isinstance(time, (tuple, list, np.ndarray)):
        logging.warning(f'taking only first time {time[0]}, would you like multiple times upgrade to code?')
        time = time[0]

    if isinstance(time, str):
        time = parse(time)
    elif isinstance(time, np.datetime64):
        time = time.astype(datetime)
    elif isinstance(time, (datetime, date)):
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

    if isinstance(time, (float, int)):
        return time

    if isinstance(time, (tuple, list, np.ndarray)):
        assert isinstance(time[0], datetime), f'expected datetime, not {type(time[0])}'
        return np.array(list(map(dt2ut1, time)))
    else:
        assert isinstance(time, datetime)
        return dt2ut1(time)


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

    return time.squeeze()[()]


def chapman_profile(Z0: float, zKM: np.ndarray, H: float):
    """
    Z0: altitude [km] of intensity peak
    zKM: altitude grid [km]
    H: scale height [km]

    example:
    pz = chapman_profile(110,np.arange(90,200,1),20)
    """
    return np.exp(.5*(1-(zKM-Z0)/H - np.exp((Z0-zKM)/H)))
