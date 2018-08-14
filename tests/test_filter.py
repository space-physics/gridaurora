#!/usr/bin/env python
from pathlib import Path
import pytest
from pytest import approx

R = Path(__file__).resolve().parents[1]
dpath = R / 'gridaurora/precompute'


def test_opticalfilter():
    gaf = pytest.importorskip('gridaurora.filterload')

    bg3fn = dpath/'BG3transmittance.h5'
    windfn = dpath/'ixonWindowT.h5'
    qefn = dpath/'emccdQE.h5'

    testlambda = [250, 427.8, 555.7, 630.0, 777.4]
    obsalt_km = 0
    zenang_deg = 0

    T = gaf.getSystemT(testlambda, bg3fn, windfn, qefn, obsalt_km, zenang_deg)
    assert (T.wavelength_nm == approx(testlambda)).all()

    try:  # with lowtran
        assert T['sys'].values == approx([7.965214e-43, 4.411237e-01, 9.311972e-04, 1.016631e-05, 7.668004e-01],
                                         rel=0.001)
    except AssertionError:
        assert T['sys'].values == approx([8.213363e-4, 5.790669e-1, 1.058124e-3, 1.133114e-5, 7.854393e-1],
                                         rel=0.001)

    for f in T.data_vars:
        assert ((0 <= T[f]) & (T[f] <= 1)).all()


if __name__ == '__main__':
    pytest.main(['-x', __file__])
