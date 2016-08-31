#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import sys
import numpy as np
import gdal

vrt_file = sys.argv[1]
out_file = sys.argv[2]
ds = gdal.Open(vrt_file)
#
cols = ds.RasterXSize
rows = ds.RasterYSize

#write tiff file
driver = gdal.GetDriverByName('GTiff')
outDataset = driver.Create(out_file, cols, rows, 1, gdal.GDT_Float32)
#projection
geoTransform = ds.GetGeoTransform()
outDataset.SetGeoTransform(geoTransform )
proj = ds.GetProjection()
outDataset.SetProjection(proj)
#array
print 'reading array'
a = ds.ReadAsArray().astype('float')
if len(a.shape) == 3:
	a[a == -99.] = np.nan
	b = np.nansum(a, axis = 0)
	b[np.isnan(b)] = -99.
	b = b.astype('int')
elif len(a.shape) == 2:
	b = a

#c = b/float(33)
#c[c==-3] = -99
print 'write raster'
#write band
outBand = outDataset.GetRasterBand(1)
outBand.WriteArray(b)
outBand.FlushCache()
outBand.SetNoDataValue(-99)