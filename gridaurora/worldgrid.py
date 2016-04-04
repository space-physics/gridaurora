from numpy import arange,meshgrid

def latlonworldgrid(latstep=5,lonstep=5):
    lat = arange(-90.,90+latstep,latstep)
    lon = arange(-180.,180+lonstep,lonstep)
    glon,glat = meshgrid(lon,lat)
    return glat,glon
