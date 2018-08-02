#!/usr/bin/env python
import pytest
from datetime import datetime
from pytest import approx


def test_solarangle():

    gas = pytest.importorskip('gridaurora.solarangle')

    t = datetime(2015, 7, 1)
    tstr = '2015-07-01T00:00:00'
    glat = 65
    glon = -148
    alt_m = 200

    sza, sun, obs = gas.solarzenithangle(t, glat, glon, alt_m)
    assert sza == approx(46.451623)

    sza, sun, obs = gas.solarzenithangle(tstr, glat, glon, alt_m)
    assert sza == approx(46.451623)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
