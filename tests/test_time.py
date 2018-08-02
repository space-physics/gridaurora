#!/usr/bin/env python
import pytest
from datetime import datetime
from pytest import approx
from gridaurora import to_ut1unix


def test_dt2ut1():

    t = datetime(2015, 7, 1)
    tstr = '2015-07-01T00:00:00'

    assert to_ut1unix(t) == approx(1435708800.)
    assert to_ut1unix(tstr) == approx(1435708800.)
    assert to_ut1unix(1435708800.) == approx(1435708800.)
    assert to_ut1unix([1435708800.]) == approx(1435708800.)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
