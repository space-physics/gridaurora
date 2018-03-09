#!/usr/bin/env python
install_requires = ['python-dateutil','pytz','numpy','scipy','xarray','h5py',
                    'sciencedates']
tests_require=['pytest','nose','coveralls']
# %%
from setuptools import setup,find_packages

setup(name='gridaurora',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      description='Gridding for auroral and ionospheric modeling',
      url='https://github.com/scivision/gridaurora',
      version='1.1.8',
      package_data={'gridaurora':['data/RecentIndices.txt'],
                    'gridaurora.precompute': ['*.h5']},
      classifiers=[
          'Intended Audience :: Science/Research',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
          'Programming Language :: Python :: 3',
          ],
      install_requires=install_requires,
      python_requires='>=3.6',
      extras_require={'plot':['matplotlib', 'seaborn', 'pathvalidate'],
                      'io':['lowtran','transcarread','astropy','pandas',],
                      'tests':tests_require},
      tests_require=tests_require,
	  )

