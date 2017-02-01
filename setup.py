#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)


setup(name='gridaurora',
      packages=['gridaurora'],
      data_files=[('gridaurora/data',['gridaurora/data/RecentIndices.txt'])],
	  install_requires=['histutils','pathvalidate'],
      extras_require={'lowtran':'lowtran'}, #optional
      dependency_links = ['https://github.com/scienceopen/lowtran/tarball/master#egg=lowtran',
                     'https://github.com/scienceopen/histutils/tarball/master#egg=histutils'],
      package_data={'gridaurora.precompute': ['*.h5']},
	  )
