#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

from PIL import Image
import numpy as np
from osgeo import gdal
import zlib
import subprocess
import sys
import time
import os

#create temp asc file
curr1 = time.gmtime()
curr = time.mktime(curr1)
curr_str = str(curr)[:-2]
if not os.path.exists('../userFile/temp/'):
    os.makedirs('../userFile/temp/')

temp_file = '../userFile/'+curr_str+'.asc'

fileIn = sys.argv[1]
fileOut = sys.argv[2]

tempfile = ''
filename, file_extension = os.path.splitext(fileIn)
if file_extension == '.asc':
	b = open(fileIn).readlines()
	xllcor = float((b[2].split(' '))[-1])
	yllcor = float((b[3].split(' '))[-1])
	cell = float((b[4].split(' '))[-1])
	array = np.loadtxt(fileIn, skiprows = 6)
elif file_extension == '.tif':
	ds = gdal.Open(fileIn)
	im = ds.GetRasterBand(1)
	gt = ds.GetGeoTransform()
	width = ds.RasterXSize
	height = ds.RasterYSize
	cell = gt[1]
	xllcor = gt[0]
	yllcor = gt[3] + width*gt[4] + height*gt[5]
	#im = Image.open(fileIn)
	array = im.ReadAsArray()

header = "ncols     %s\n" % array.shape[1]
header += "nrows    %s\n" % array.shape[0]
header += "xllcorner %.3f\n" % xllcor
header += "yllcorner %.3f\n" % yllcor
header += "cellsize %.2f\n" % cell
header += "NODATA_value -99\n"

#Save the newly created asc file
f = open(fileOut, "w")
f.write(header)
np.savetxt(f, array, fmt="%.2f")
f.close()

zlib.compress(fileOut)