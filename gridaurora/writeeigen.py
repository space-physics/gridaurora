from six import string_types
import h5py
from os.path import expanduser
from datetime import datetime
from pytz import UTC

epoch = datetime(1970,1,1,tzinfo=UTC)

def writeeigen(fn,ver,prates,lrates,tez,latlon):
    assert isinstance(fn,string_types)

    if fn.endswith('.h5'):
        h5fn = expanduser(fn)
        print('writing to '+ fn)
        ut1_unix = [(t-epoch).total_seconds() for t in ver.items.to_pydatetime()]
        with h5py.File(h5fn,'w',libver='latest') as f:
            f['/sensorloc'] = latlon
            #VER
            d=f.create_dataset('/eigenprofile',data=ver.values,compression='gzip')
            d=f.create_dataset('/altitude',data=ver.major_axis)
            d=f.create_dataset('/Ebins',data=ver.minor_axis)
            d=f.create_dataset('/ut1_unix',data=ut1_unix) #float
            #prod/loss
            f['/state'] = prates[0].columns.tolist()
            d=f.create_dataset('/production',data=prates.values,compression='gzip')
            d=f.create_dataset('/loss',data=lrates.values,compression='gzip')
            #energy deposition
            d=f.create_dataset('/energydeposition',data=tez.value,compression='gzip')