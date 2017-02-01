from dateutil.parser import parse
from numpy import ndarray
import astropy.units as u
from astropy.coordinates import get_sun, EarthLocation, AltAz
from astropy.time import Time

def solarzenithangle(t,glat,glon,alt_m):
    """
    Input:

    t: scalar or array of datetime

    """
    if isinstance(t,(tuple,list,ndarray)):
        if isinstance(t[0],str):
            t=map(parse,t)
    elif isinstance(t,str):
        t=parse(t)

    obs = EarthLocation(lat=glat*u.deg, lon=glon*u.deg, height=alt_m*u.m)
    times = Time(t, scale='ut1')
    sun = get_sun(times)
    sunobs = sun.transform_to(AltAz(obstime=times,location=obs))
    return 90 - sunobs.alt.degree, sun,sunobs
