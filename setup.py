#!/usr/bin/env python3

from setuptools import setup

with open('README.rst','r') as f:
	long_description = f.read()

setup(name='gridaurora',
      version='0.1.1',
	  description='utilities for ionospheric gridding, particularly for the aurora',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/gridaurora',
	  install_requires=['histutils',
                        'pathlib2>=2.1.0'],
      extras_require={'lowtran':'lowtran'}, #optional
          dependency_links = ['https://github.com/scienceopen/lowtran/tarball/master#egg=lowtran',
                             'https://github.com/scienceopen/histutils/tarball/master#egg=histutils'],
          packages=['gridaurora'],
          package_data={'gridaurora.precompute': ['*.h5']},
	  )


