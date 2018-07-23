#!/usr/bin/env python
import pytest
from datetime import datetime
from numpy.testing import assert_allclose
try:
    import gridaurora.solarangle as gas
except ImportError:
    gas = None


@pytest.mark.skipif(gas is None, reason='CI prereq')
def test_solarangle():

    t = datetime(2015, 7, 1)
    tstr = '2015-07-01T00:00:00'
    glat = 65
    glon = -148
    alt_m = 200

    sza, sun, obs = gas.solarzenithangle(t, glat, glon, alt_m)
    assert_allclose(sza, 46.451623)

    sza, sun, obs = gas.solarzenithangle(tstr, glat, glon, alt_m)
    assert_allclose(sza, 46.451623)


if __name__ == '__main__':
    pytest.main()
