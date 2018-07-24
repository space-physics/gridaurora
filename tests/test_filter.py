#!/usr/bin/env python
from pathlib import Path
import pytest
from numpy.testing import assert_allclose
try:
    import gridaurora.filterload as gaf
except ImportError:
    gaf = None

R = Path(__file__).parents[1]
dpath = R / 'gridaurora/precompute'


@pytest.mark.skipif(gaf is None, reason='missing h5py')
def test_opticalfilter():
    bg3fn = dpath/'BG3transmittance.h5'
    windfn = dpath/'ixonWindowT.h5'
    qefn = dpath/'emccdQE.h5'

    testlambda = [250, 427.8, 555.7, 630.0, 777.4]
    obsalt_km = 0
    zenang_deg = 0

    T = gaf.getSystemT(testlambda, bg3fn, windfn, qefn, obsalt_km, zenang_deg)
    assert_allclose(T.wavelength_nm, testlambda)
    try:  # with lowtran
        assert_allclose(T['sys'],
                        [7.965214e-43, 4.411237e-01, 9.311972e-04, 1.016631e-05, 7.668004e-01],
                        rtol=1e-6)
    except AssertionError:
        assert_allclose(T['sys'],
                        [8.213363e-4, 5.790669e-1, 1.058124e-3, 1.133114e-5, 7.854393e-1],
                        rtol=1e-6)

    for f in T.data_vars:
        assert ((0 <= T[f]) & (T[f] <= 1)).all()


if __name__ == '__main__':
    pytest.main()
