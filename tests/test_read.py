#!/usr/bin/env python
import pytest
import gridaurora
import urllib.error


def test_f107apread():
    try:
        f107ap = gridaurora.readmonthlyApF107(201708)
    except urllib.error.URLError as e:
        pytest.skip(f'possible timeout error {e}')

    assert f107ap['f107o'] == 77.9
    assert f107ap['f107s'] == 76.3
    assert f107ap['Apo'] == 12.
    assert f107ap['Aps'] == 10.7


if __name__ == '__main__':
    pytest.main()
