"""
converts date string, datetime, or array thereof to UT1 UNIX, seconds since Unix Epoch
"""
from pytz import UTC
from numpy import ndarray
from dateutil.parser import parse
from datetime import datetime
#
from sciencedates import forceutc

epoch = datetime(1970,1,1,tzinfo=UTC)

def to_ut1unix(t):
    """
    converts time inputs to UT1 seconds since Unix epoch
    """
    #keep this order
    if isinstance(t,datetime):
        t = [t]
    elif isinstance(t,str):
        t=[parse(t)]
    elif isinstance(t,(float,int)) or isinstance(t[0],(float,int)):
        return t

    assert isinstance(t,(tuple,list,ndarray))
    assert isinstance(t[0],datetime)

    return list(map(dt2ut1,t))


def dt2ut1(t):
    assert isinstance(t,datetime)

    return (forceutc(t)-epoch).total_seconds()
