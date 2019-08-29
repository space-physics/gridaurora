from datetime import datetime
import astropy.units as u
from astropy.coordinates import get_sun, EarthLocation, AltAz
from astropy.time import Time
from . import totime


def solarzenithangle(time: datetime, glat: float, glon: float, alt_m: float) -> tuple:
    """
    Input:

    t: scalar or array of datetime
    """
    time = totime(time)

    obs = EarthLocation(lat=glat * u.deg, lon=glon * u.deg, height=alt_m * u.m)
    times = Time(time, scale="ut1")
    sun = get_sun(times)
    sunobs = sun.transform_to(AltAz(obstime=times, location=obs))

    return 90 - sunobs.alt.degree, sun, sunobs
