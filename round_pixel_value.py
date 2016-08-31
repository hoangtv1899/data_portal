#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

#This code for rounding up pixel values of a raster
from osgeo import gdal
import numpy as np
import sys
from gdalconst import *

fileIn = sys.argv[1]
fileOut = sys.argv[2]

# register all of the GDAL drivers
gdal.AllRegister()

# open the image
inDs = gdal.Open(fileIn)
if inDs is None:
  print 'Could not open image file'
  sys.exit(1)

# read in the crop data and get info about it
band1 = inDs.GetRasterBand(1)
rows = inDs.RasterYSize
cols = inDs.RasterXSize
im_array = band1.ReadAsArray()

# create the output image
driver = inDs.GetDriver()
#print driver
outDs = driver.Create(fileOut, cols, rows, 1, GDT_Float32, ['COMPRESS=LZW'])
outBand = outDs.GetRasterBand(1)
outData = im_array.round(decimals = 2)

# write the data
outBand.WriteArray(outData)

# flush data to disk, set the NoData value and calculate stats
outBand.FlushCache()
outBand.SetNoDataValue(-99)

# georeference the image and set the projection
outDs.SetGeoTransform(inDs.GetGeoTransform())
#outDs.SetProjection(inDs.GetProjection())