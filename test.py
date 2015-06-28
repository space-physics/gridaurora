#!/usr/bin/env python
from __future__ import division,absolute_import
from datetime import datetime
from numpy.testing import assert_allclose
from pytz import timezone
from os.path import join
from warnings import warn
#%% ztanh
def test_ztanh():
    try: from .ztanh import setupz # . for nose
    except: from ztanh import setupz
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

def test_opticalfilter():
    try: import filterload
    except: from . import filterload

    dpath = 'precompute'
    bg3fn =  join(dpath,'BG3transmittance.h5')
    windfn = join(dpath,'ixonWindowT.h5')
    qefn =   join(dpath,'emccdQE.h5')

    testlambda = [250, 427.8, 555.7, 630.0, 777.4]
    obsalt_km = 0
    zenang_deg= 0

    T = filterload.getSystemT(testlambda,bg3fn,windfn,qefn,obsalt_km,zenang_deg)
    assert_allclose(T.index,testlambda)
    try: #with lowtran
        assert_allclose(T['sys'].values,
                    [7.965214e-43, 4.411237e-01,9.311972e-04,1.016631e-05, 7.668004e-01],
                    rtol=1e-6)
    except:
        assert_allclose(T['sys'].values,
                    [8.213363e-4, 5.790669e-1, 1.058124e-3, 1.133114e-5, 7.854393e-1],
                    rtol=1e-6)

    assert ((0 <= T.values) & (T.values <= 1)).all()

if __name__ == '__main__':
    test_ztanh()
    test_datetimefortran()
    test_fortrandates()
    test_opticalfilter()
    test_utc()
    test_worldgrid()

