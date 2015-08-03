#!/usr/bin/env python3

from setuptools import setup 

with open('README.rst') as f:
	long_description = f.read()
	
setup(name='gridaurora',
      version='0.1',
	  description='utilities for ionospheric gridding, particularly for the aurora',
	  long_description=long_description,
	  author='Michael Hirsch',
	  author_email='hirsch617@gmail.com',
	  url='https://github.com/scienceopen/gridaurora',
	  package_data={'gridaurora.precompute', ['*.h5']},
	  install_requires=['lowtran','histutils','pandas','six','pytz','numpy','scipy','h5py'],
          dependency_links = ['https://github.com/scienceopen/lowtran/tarball/master#egg=lowtran',
                             'https://github.com/scienceopen/histutils/tarball/master#egg=histutils'],
          packages=['gridaurora'],
	  )


