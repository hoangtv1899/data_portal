#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import glob
import shutil
from osgeo import ogr, gdal
import numpy as np
import multiprocessing
import itertools
from ShapeSelection import ShapeSelection
from asc_format1 import AscFormatFloat
from asc_format_ccs1 import AscFormat

def ClipRaster(args):
	fileIn = args[0]
	outShapefile = args[1]
	resolution = args[2]
	p1 = args[3]
	dest_file = args[4]
	dtype = args[5]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+p1+" -of GTiff -ot "+dtype+" "+fileIn+" "+dest_file)
	
#inputs
curr_str = sys.argv[1]
loc = sys.argv[2]
loc = loc[1:-1].split(",")
shapefile = sys.argv[3]
date_start = sys.argv[4]
date_end = sys.argv[5]
file_type = sys.argv[6]
dataset = sys.argv[7]
outfile = sys.argv[8]
compression = sys.argv[9]
timestepAlt = sys.argv[10]
try:
	time_step = sys.argv[11]
except IndexError:
	time_step = 'null'

tmp_f = '../userFile/temp/'+curr_str+'/'
tmp_f1 = '../userFile/temp/199'+curr_str+'/'
tmp_shp = '../userFile/temp/shp_'+curr_str+'/'
#check dataset
if dataset == 'CDR':
	resolution = '0.25'
	if len(date_start) == 8:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/daily_asc/CDR_{"+date_start+".."+date_end+"}z.asc 2>/dev/null"
	elif len(date_start) == 6:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/monthly_asc/CDR_{"+date_start+".."+date_end+"}.asc 2>/dev/null"
	elif len(date_start) == 4:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/yearly_asc/CDR_{"+date_start+".."+date_end+"}.asc 2>/dev/null"
elif dataset in ['CCS', 'PERSIANN']:
	if dataset == 'CCS':
		resolution = '0.04'
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
	else:
		resolution = '0.25'
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"

#check shapefile
outShapefile = ShapeSelection(loc, shapefile, tmp_shp)
shp_in = ogr.Open(outShapefile)
shp_layer = shp_in.GetLayer()
shp_extents = shp_layer.GetExtent()
[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/float(resolution)) *float(resolution) + [-float(resolution), float(resolution), -float(resolution), float(resolution)]
if ymin1 >= 60:
	sys.exit()
elif ymax1 >= 60:
	ymax1 = 60

p = [xmin1, ymin1, xmax1, ymax1]
p1 = map(str, p)

#clipping raster
pool = multiprocessing.Pool(processes = 4)
list_file = [file1.replace('\n','') for file1 in os.popen('ls '+path_to_file).readlines()]
ShapeArray = itertools.repeat(outShapefile, len(list_file))
ResArray = itertools.repeat(resolution, len(list_file))
CoorArray = itertools.repeat(' '.join(p1), len(list_file))
if file_type == 'Tif':
	list_dest_file = [tmp_f+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
	if dataset == 'CDR':
		TypeArray = itertools.repeat('Float32', len(list_file))
		pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file, TypeArray))
	elif dataset in ['PERSIANN', 'CCS']:
		TypeArray = itertools.repeat('Int16', len(list_file))
		pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file, TypeArray))
elif file_type == 'ArcGrid':
	list_dest_file1 = [tmp_f1+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
	list_dest_file = [tmp_f+os.path.splitext(os.path.basename(file2))[0]+'.asc' for file2 in list_file]
	if dataset == 'CDR':
		TypeArray = itertools.repeat('Float32', len(list_file))
		pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file1, TypeArray))
		pool.map(AscFormatFloat, itertools.izip(list_dest_file1, list_dest_file))
	elif dataset in ['PERSIANN', 'CCS']:
		TypeArray = itertools.repeat('Int16', len(list_file))
		pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file1, TypeArray))
		pool.map(AscFormat, itertools.izip(list_dest_file1, list_dest_file))
	shutil.rmtree(tmp_f1)

for file in glob.iglob(outShapefile.split(".")[0]+".*"):
	shutil.copy(file, tmp_f)

shutil.make_archive(outfile, format=compression, root_dir=tmp_f)
