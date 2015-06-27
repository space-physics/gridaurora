#!/usr/bin/env python
from __future__ import division,absolute_import
from datetime import datetime
from numpy.testing import assert_allclose
from pytz import timezone
from six import integer_types
#%% ztanh
def test_ztanh():
    from .ztanh import setupz # . for nose
    zgrid = setupz(np=300, zmin=90, gridmin=1.5, gridmax=10.575)
    assert_allclose(zgrid[[0,99,-1]],[90., 701.93775845, 2999.04573563])
#%% fortrandates
def test_fortrandates():
    try: import fortrandates
    except: from . import fortrandates
    adatetime=datetime(2013,7,2,12,0,0)
    yeardec = fortrandates.datetime2yeardec(adatetime)
    assert_allclose(yeardec,2013.5)

    assert fortrandates.yeardec2datetime(yeardec) == adatetime

def test_utc():
    try: import fortrandates
    except: from . import fortrandates
    adatetime=datetime(2013,7,2,12,0,0)
    estdt = timezone('EST').localize(adatetime)
    utcdt = fortrandates.forceutc(estdt)
    assert utcdt==estdt
    assert utcdt.tzname()=='UTC'

def test_datetimefortran():
    try: import fortrandates
    except: from . import fortrandates
    adatetime=datetime(2013,7,2,12,0,0)
    iyd,utsec,stl= fortrandates.datetime2gtd(adatetime,glon=42)
    assert iyd[0]==183
    assert_allclose(utsec[0],43200)
    assert_allclose(stl[0],14.8)

def test_worldgrid():
    try: import worldgrid
    except: from . import worldgrid
    glat,glon = worldgrid.latlonworldgrid(latstep=10,lonstep=20)
    assert_allclose(glat[0,0],-90)
    assert (glat[0,0]==glat[0,:]).all()
    assert_allclose(glon[0,1],-160)
    assert (glon[0,0]==glon[:,0]).all()

