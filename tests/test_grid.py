#!/usr/bin/env python
import pytest
from pytest import approx
from gridaurora.ztanh import setupz
from gridaurora.worldgrid import latlonworldgrid


def test_ztanh():
    zgrid = setupz(Np=300, zmin=90, gridmin=1.5, gridmax=10.575)
    assert (zgrid[[0, 99, -1]] == approx([90., 701.93775845, 2999.04573563]))


def test_worldgrid():
    glat, glon = latlonworldgrid(latstep=10, lonstep=20)
    assert glat[0, 0] == approx(-90.)
    assert glat[0, 0] == approx(glat[0, :])
    assert glon[0, 1] == approx(-160.)
    assert glon[0, 0] == approx(glon[:, 0])


if __name__ == '__main__':
    pytest.main(['-x', __file__])
