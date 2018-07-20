#!/usr/bin/env python
import pytest
import gridaurora
import urllib.error
from datetime import date, timedelta
from numpy.testing import assert_allclose


def test_past():

    t = date(2017, 8, 1)
    tstr = '2017-08-01'

    try:
        dat = gridaurora.getApF107(tstr, 81)
    except urllib.error.URLError as e:
        pytest.skip(f'possible timeout error {e}')

    assert dat.time.item() == t

    assert_allclose(dat['f107'], 77.9)
    assert_allclose(dat['f107s'], 82.533333)
    assert_allclose(dat['Ap'], 12.)
    assert_allclose(dat['Aps'], 13.333333)


def test_nearfuture():

    t = date.today() + timedelta(days=3)

    try:
        dat = gridaurora.getApF107(t)
    except urllib.error.URLError as e:
        pytest.skip(f'possible timeout error {e}')

    assert dat.time.item() == t

    assert 'Ap' in dat
    assert 'f107' in dat


def test_farfuture():

    t = date(2029, 12, 21)

    try:
        dat = gridaurora.getApF107(t, 81)
    except urllib.error.URLError as e:
        pytest.skip(f'possible timeout error {e}')

    assert t - timedelta(days=31) <= dat.time.item() <= t + timedelta(days=31)

    assert 'Ap' in dat
    assert 'f107' in dat


if __name__ == '__main__':
    pytest.main()
