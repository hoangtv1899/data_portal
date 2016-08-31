#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7
#../python/rectangle_mask.py ulx uly lrx lry infile file_for_Web

import subprocess
import os
import sys
import time
from osgeo import gdal, osr
from PIL import Image
import math
import numpy as np

DEVNULL = open(os.devnull, 'wb')
curr1 = time.gmtime()
curr = time.mktime(curr1)
curr_str = str(curr)[:-2]

ulx = sys.argv[1]
uly = sys.argv[2]
lrx = sys.argv[3]
lry = sys.argv[4]
infile = sys.argv[5]
outfile = sys.argv[6]

imfile = gdal.Open(infile)
geoinformation = imfile.GetGeoTransform()
lat = geoinformation[3]

ulx1 = float(ulx)
uly1 = float(uly)
lrx1 = float(lrx)
lry1 = float(lry)
ulx = str(math.ceil(ulx1/geoinformation[1])*geoinformation[1])
uly = str(math.floor(uly1/geoinformation[1])*geoinformation[1])
lrx = str(math.floor(lrx1/geoinformation[1])*geoinformation[1])
lry = str(math.ceil(lry1/geoinformation[1])*geoinformation[1])

if float(ulx) <= float(lrx):
	uly = str(lat) if float(uly) > lat else uly
	lry = str(-lat) if float(lry) < -lat else lry
	command = '/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -projwin '+ulx+' '+uly+' '+lrx+' '+lry+' -of GTiff '+infile+' '+outfile+' -co COMPRESS=LZW'
	subprocess.Popen(command, shell=True, executable="/bin/bash", stdout=DEVNULL, stderr=DEVNULL).communicate()
else:
	lrx1 = float(lrx) + 360
	lrx1 = str(lrx1)
	ulx1 = float(ulx) - 360
	ulx1 = str(ulx1)
	uly = str(lat) if float(uly) > lat else uly
	lry = str(-lat) if float(lry) < -lat else lry
	temp_file1 = '../userFile/temp/1'+curr_str+'.tif'
	temp_file2 = '../userFile/temp/2'+curr_str+'.tif'
	temp_file3 = '../userFile/temp/3'+curr_str+'.tif'
	cmd1 = '/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -projwin -180 '+uly+' '+lrx+' '+lry+' -of GTiff '+infile+' "'+temp_file1+'" -co COMPRESS=LZW'
	subprocess.Popen(cmd1, shell=True, executable="/bin/bash", stdout=DEVNULL, stderr=DEVNULL).communicate()
	cmd2 = '/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -projwin '+ulx+' '+uly+' 180 '+lry+' -of GTiff '+infile+' "'+temp_file2+'" -co COMPRESS=LZW'	
	subprocess.Popen(cmd2, shell=True, executable="/bin/bash", stdout=DEVNULL, stderr=DEVNULL).communicate()
	cmd3 = '/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7 /root/gdal-1.11.2/swig/python/scripts/gdal_merge.py -o '+temp_file3+' '+temp_file1+' '+temp_file2
	subprocess.Popen(cmd3, shell=True, executable="/bin/bash", stdout=DEVNULL, stderr=DEVNULL).communicate()
	cmd4 = '/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -of GTiff '+temp_file3+' '+outfile+' -co COMPRESS=LZW'
	subprocess.Popen(cmd4, shell=True, executable="/bin/bash", stdout=DEVNULL, stderr=DEVNULL).communicate()

	os.remove(temp_file1)
	os.remove(temp_file2)
	os.remove(temp_file3)
im = Image.open(outfile)
array = np.array(im)
array = array[array != -99]
print "max: %.2f" % array.max()
print "min: %.2f" % array.min()
print "mean: %.2f" % array.mean()
print "median: %.2f" % np.median(array)