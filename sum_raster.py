#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import sys
import numpy as np
import gdal

vrt_file = sys.argv[1]
out_file = sys.argv[2]
dataset = sys.argv[3]
ds = gdal.Open(vrt_file)

cols = ds.RasterXSize
rows = ds.RasterYSize

#write tiff file
driver = gdal.GetDriverByName('GTiff')
if dataset in ['CDR', 'PERSIANN']:
	outDataset = driver.Create(out_file, cols, rows, 1, gdal.GDT_Float32, ['COMPRESS=LZW'])
	type = np.float32
elif dataset == 'CCS':
	outDataset = driver.Create(out_file, cols, rows, 1, gdal.GDT_Int32, ['COMPRESS=LZW'])
	type = np.int32
#projection
geoTransform = ds.GetGeoTransform()
outDataset.SetGeoTransform(geoTransform )
proj = ds.GetProjection()
outDataset.SetProjection(proj)
#array
print 'reading array'
a = ds.ReadAsArray()
a = np.ma.masked_where(a == -99,a)
if len(a.shape) == 3:
#	maskArr = (a==-99).sum(0)
#	maskArr = np.ma.masked_where(maskArr>=1, maskArr)
	b = a.sum(axis=0)
#	b = np.ma.array(b, mask = maskArr.mask)
	b = b.filled(-99)
	b = b.astype(type)
elif len(a.shape) == 2:
	b = a
	b = b.filled(-99)
	b = b.astype(type)
	
#c = b/float(33)
#c[c==-3] = -99
print 'write raster'
#write band
outBand = outDataset.GetRasterBand(1)
outBand.WriteArray(b)
outBand.FlushCache()
outBand.SetNoDataValue(-99)