#!/usr/bin/env python
req = ['python-dateutil','pytz','nose','numpy','scipy','xarray','h5py','astropy','matplotlib','seaborn','pathlib2']
pipreq=['sciencedates','lowtran',
        'pathvalidate']
# %%
import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except Exception as e:
    pip.main(['install']+req)
pip.main(['install']+pipreq)
# %%
from setuptools import setup

setup(name='gridaurora',
      packages=['gridaurora'],
      author='Michael Hirsch, Ph.D.',
      description='Gridding for auroral and ionospheric modeling',
      url='https://github.com/scivision/gridaurora',
      version='1.1.4',
      package_data={'gridaurora':['data/RecentIndices.txt'],
                    'gridaurora.precompute': ['*.h5']},
      classifiers=[
          'Intended Audience :: Science/Research',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
          'Programming Language :: Python :: 3',
          ],
	  )

