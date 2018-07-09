#!/usr/bin/env python
from datetime import datetime
import pytz
from numpy.testing import assert_allclose
from gridaurora.to_ut1 import to_ut1unix


def test_dt2ut1():
    ET = pytz.timezone('US/Eastern')

    tnaive = datetime(2015, 7, 1, tzinfo=None)
    tet = ET.localize(datetime(2015, 7, 1))  # don't use tzinfo, weird partial hour https://pypi.python.org/pypi/pytz/
    tstr = '2015-07-01T00:00:00-0800'

    assert_allclose(to_ut1unix(tnaive), 1435708800.)
    assert_allclose(to_ut1unix(tet),   1435723200.)
    assert_allclose(to_ut1unix(tstr),  1435737600.)
    assert_allclose(to_ut1unix(1435708800.), 1435708800.)
    assert_allclose(to_ut1unix([1435708800.]), 1435708800.)



if __name__ == '__main__':
    pytest.main()
