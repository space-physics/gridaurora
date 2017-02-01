import h5py
from pathlib import Path
from datetime import datetime
from pytz import UTC
from xarray import DataArray
from .to_ut1 import to_ut1unix

epoch = datetime(1970,1,1,tzinfo=UTC)

def writeeigen(fn,Ebins,t,z,diffnumflux=None,ver=None,prates=None,lrates=None,
               tezs=None,latlon=None):
    if not isinstance(fn,str):
        return

    if fn.endswith('.h5'):
        fn = Path(fn).expanduser()
        print('writing to {}'.format(fn))

        ut1_unix = to_ut1unix(t)

        with h5py.File(fn,'w',libver='latest') as f:
            bdt = h5py.special_dtype(vlen=bytes)
            d=f.create_dataset('/sensorloc',data=latlon)
            d.attrs['unit']='degrees';d.attrs['description']='geographic coordinates'
#%% input precipitation flux
            d=f.create_dataset('/Ebins',   data=Ebins); d.attrs['unit']='eV'; d.attrs['description']='Energy bin edges'
            d=f.create_dataset('/altitude',data=z);     d.attrs['unit']='km'

            d=f.create_dataset('/ut1_unix',data=ut1_unix);
            d.attrs['unit']='sec. since Jan 1, 1970 midnight' #float

            if diffnumflux is not None:
                d=f.create_dataset('/diffnumflux',data=diffnumflux)
                d.attrs['unit']='cm^-2 s^-1 eV^-1'
                d.attrs['description'] = 'primary electron flux at "top" of modeled ionosphere'
#%% VER
            if isinstance(ver,DataArray):
                d=f.create_dataset('/ver/eigenprofile',data=ver.values,compression='gzip')
                d.attrs['unit']='photons cm^-3 sr^-1 s^-1'
                d.attrs['size']='Ntime x NEnergy x Nalt x Nwavelength'

                d=f.create_dataset('/ver/wavelength',data=ver.wavelength_nm)
                d.attrs['unit']='Angstrom'
#%% prod
            if isinstance(prates,DataArray):
                d=f.create_dataset('/prod/eigenprofile',data=prates.values,compression='gzip')
                d.attrs['unit']='particle cm^-3 sr^-1 s^-1'
                if prates.ndim==3:
                    d.attrs['size']='Ntime x NEnergy x Nalt'
                else: #ndim==4
                    d.attrs['size']='Ntime x NEnergy x Nalt x Nreaction'
                    d=f.create_dataset('/prod/reaction',data=prates.reaction,dtype=bdt)
                d.attrs['description']= 'reaction species state'
#%% loss
            if isinstance(lrates,DataArray):
                d=f.create_dataset('/loss/eigenprofiles',data=lrates.values,compression='gzip')
                d.attrs['unit']='particle cm^-3 sr^-1 s^-1'
                d.attrs['size']='Ntime x NEnergy x Nalt x Nreaction'
                d=f.create_dataset('/loss/reaction',data=lrates.reaction,dtype=bdt)
                d.attrs['description']= 'reaction species state'
#%% energy deposition
            if isinstance(tezs,DataArray):
                d=f.create_dataset('/energydeposition',data=tezs.values,compression='gzip')
                d.attrs['unit']='ergs cm^-3 s^-1'
                d.attrs['size']='Ntime x Nalt x NEnergies'
