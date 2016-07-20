#!/usr/bin/env python
import os,sys
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--file','requirements.txt'])
except Exception as e:
    pass

setup(name='gridaurora',
      packages=['gridaurora'],
	  description='utilities for ionospheric gridding, particularly for the aurora',
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/gridaurora',
      data_files=[('gridaurora/data',['gridaurora/data/RecentIndices.txt'])],
	  install_requires=['histutils'],
      extras_require={'lowtran':'lowtran'}, #optional
      dependency_links = ['https://github.com/scienceopen/lowtran/tarball/master#egg=lowtran',
                     'https://github.com/scienceopen/histutils/tarball/master#egg=histutils'],
      package_data={'gridaurora.precompute': ['*.h5']},
	  )
