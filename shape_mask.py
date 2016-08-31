#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import subprocess
import os
import sys
from PIL import Image
import numpy as np
import ogr

id = sys.argv[1]
if '_' in id:
	id = id.replace('_', ' ')
shapefile = sys.argv[2]
infile = sys.argv[3]
outfile = sys.argv[4]
outshape = sys.argv[5]
outfile1 = '../userFile/temp/temp.tif'

# load the shape file as a layer
shp_name = (shapefile.split('/'))[-1]
if shp_name == 'country_fusion.shp':
	prop = 'FIPS_CNTRY'
	filter = '{} = \'{}\''.format(prop, id)
	prior = "/usr/local/epd-7.3-2-rh5-x86_64/bin/"
elif shp_name == 'pol_divisions.shp':
	prop = 'NAM'
	filter = '{} = \'{}\''.format(prop, id)
	prior = "/usr/local/bin/"
elif shp_name[:6] == 'basins':
	prop = 'HYBAS_ID'
	filter = '{} = \'{}\''.format(prop, id)
	prior = "/usr/local/bin/"
else:
	print 'please select boundary, pol_division or basins shapefiles...'
	sys.exit()

# print filter
#select feature
# filter = '{} = \'{}\''.format(prop, id)

if ' ' in id:
	id = id.replace(' ', '_')

# Save extent to a new Shapefile
outShapefile = outshape

# Remove output shapefile if it already exists
try:
    os.remove(outShapefile)
except OSError:
    pass

command2 = prior+"ogr2ogr -f \"ESRI Shapefile\" -where \\ \""+filter+"\" "+outShapefile+" "+shapefile
# print command2
subprocess.Popen(command2, shell=True).communicate()
#get shapefile extents
vector = ogr.Open(outShapefile)
layer = vector.GetLayer()
shp_extents = layer.GetExtent()
[xmin1, xmax1, ymin1, ymax1] = np.floor(shp_extents) + np.floor((shp_extents - np.floor(shp_extents))/0.04) *0.04
p = [xmin1, ymin1, xmax1, ymax1]
p1 = map(str, p)

#subset raster:
cmd1 = "/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outshape+" -of GTiff -te "+' '.join(p1)+" "+infile+" "+outfile1+" -co COMPRESS=LZW"
subprocess.Popen(cmd1, shell=True).communicate()
cmd2 = '/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -of GTiff '+outfile1+' '+outfile
subprocess.Popen(cmd2, shell=True).communicate()

im = Image.open(outfile1)
array = np.array(im)
array = array[array != -99]
print "max: %.2f" % array.max()
print "min: %.2f" % array.min()
print "mean: %.2f" % array.mean()
print "median: %.2f" % np.median(array)