#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import gdal
import numpy as np
from ShapeSelection import ShapeSelection
import ogr

user_IP = sys.argv[1]
loc = sys.argv[2]
loc = loc[1:-1].split(",")
shapefile = sys.argv[3]
infile = sys.argv[4]
outshape = sys.argv[5]

tmp_shp = '../userFile/'+user_IP+'/tempShape/'
#check shapefile
outshape = ShapeSelection(loc, shapefile, tmp_shp)
shp_in = ogr.Open(outshape)
shp_layer = shp_in.GetLayer()
shp_extents = shp_layer.GetExtent()
[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/0.04) *0.04 + [-0.04, 0.04, -0.04, 0.04]
if ymin1 >= 60:
	sys.exit()
elif ymax1 >= 60:
	ymax1 = 60

p = [xmin1, ymin1, xmax1, ymax1]
p1 = map(str, p)

outfile = tmp_shp+os.path.splitext(os.path.basename(shapefile))[0]+os.path.splitext(os.path.basename(outshape))[0]+'_'+os.path.splitext(os.path.basename(infile))[0]+".tif"

#subset raster:
os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outshape+" -of GTiff -ot Int16 -te "+' '.join(p1)+" "+infile+" "+outfile+" -co COMPRESS=LZW")

#print out file name to pass to JS

if os.path.splitext(os.path.basename(infile))[0][-1:] == "z":
	print "fileName:"+os.path.splitext(os.path.basename(shapefile))[0]+os.path.splitext(os.path.basename(outshape))[0]+'_'+os.path.splitext(os.path.basename(infile))[0][:-1]
else:
	print "fileName:"+os.path.splitext(os.path.basename(shapefile))[0]+os.path.splitext(os.path.basename(outshape))[0]+'_'+os.path.splitext(os.path.basename(infile))[0]
	
im = gdal.Open(outfile)
array = im.ReadAsArray()
array = array[array != -99]
print "max: %.2f" % array.max()
print "min: %.2f" % array.min()
print "mean: %.2f" % array.mean()
print "median: %.2f" % np.median(array)