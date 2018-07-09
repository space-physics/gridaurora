#!/usr/bin/env python
import pytest
from numpy.testing import assert_allclose
from gridaurora.ztanh import setupz
from gridaurora.worldgrid import latlonworldgrid


def test_ztanh():
    zgrid = setupz(np=300, zmin=90, gridmin=1.5, gridmax=10.575)
    assert_allclose(zgrid[[0, 99, -1]], [90., 701.93775845, 2999.04573563])


def test_worldgrid():
    glat, glon = latlonworldgrid(latstep=10, lonstep=20)
    assert_allclose(glat[0, 0], -90)
    assert (glat[0, 0] == glat[0, :]).all()
    assert_allclose(glon[0, 1], -160)
    assert (glon[0, 0] == glon[:, 0]).all()


if __name__ == '__main__':
    pytest.main()
