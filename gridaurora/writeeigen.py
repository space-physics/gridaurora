from __future__ import division,absolute_import
from six import string_types
import h5py
from os.path import expanduser
from datetime import datetime
from pytz import UTC
#
from histutils.fortrandates import forceutc

epoch = datetime(1970,1,1,tzinfo=UTC)

def writeeigen(fn,ver,prates,lrates,tez,latlon):
    if not isinstance(fn,string_types):
        return

    if fn.endswith('.h5'):
        fn = expanduser(fn)
        print('writing to '+ fn)

        ut1_unix = [(forceutc(t)-epoch).total_seconds() for t in ver.labels.to_pydatetime()]

        with h5py.File(fn,'w',libver='latest') as f:
            bdt = h5py.special_dtype(vlen=bytes)
            f['/sensorloc'] = latlon
            #VER
            d=f.create_dataset('/ver/eigenprofile',data=ver.values,compression='gzip')
            d=f.create_dataset('/altitude',data=ver.major_axis)
            d=f.create_dataset('/Ebins',data=ver.items)
            d=f.create_dataset('/ut1_unix',data=ut1_unix) #float
            d=f.create_dataset('/ver/wavelength',data=ver.minor_axis)
            #prod
            d=f.create_dataset('/prod/eigenprofile',data=prates.values,compression='gzip')
            d=f.create_dataset('/prod/reaction',data=prates.minor_axis,dtype=bdt)
            #loss
            d=f.create_dataset('/loss/eigenprofiles',data=lrates.values,compression='gzip')
            d=f.create_dataset('/loss/reaction',data=lrates.minor_axis,dtype=bdt)
            #energy deposition
            d=f.create_dataset('/energydeposition',data=tez.values,compression='gzip')