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
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/daily/CDR_{"+date_start+".."+date_end+"}z.tif 2>/dev/null"
	elif len(date_start) == 6:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/monthly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"
	elif len(date_start) == 4:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/yearly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"
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
	TypeName = 'GeoTiff'
	list_dest_file = [tmp_f+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
	if dataset in ['CDR', 'PERSIANN']:
		TypeArray = itertools.repeat('Float32', len(list_file))
		pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file, TypeArray))
	elif dataset == 'CCS':
		TypeArray = itertools.repeat('Int16', len(list_file))
		pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file, TypeArray))
elif file_type == 'ArcGrid':
	TypeName = 'ArcGrid'
	list_dest_file1 = [tmp_f1+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
	list_dest_file = [tmp_f+os.path.splitext(os.path.basename(file2))[0]+'.asc' for file2 in list_file]
	if dataset in ['CDR', 'PERSIANN']:
		TypeArray = itertools.repeat('Float32', len(list_file))
		pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file1, TypeArray))
	elif dataset =='CCS':
		TypeArray = itertools.repeat('Int16', len(list_file))
		pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file1, TypeArray))
	dataset_arr = itertools.repeat(dataset, len(list_dest_file))
	pool.map(AscFormat, itertools.izip(list_dest_file1, list_dest_file, dataset_arr))

file1 = sorted(glob.glob(tmp_f+'*.*'))[0]
ds = gdal.Open(file1)
try:
	a = ds.ReadAsArray()
except:
	print 'error: selected region is too small.'
	sys.exit()
nlat,nlon = a.shape
b = ds.GetGeoTransform() #bbox, interval
lon = np.arange(nlon)*b[1]+b[0]
lat = np.arange(nlat)*b[5]+b[3]
cell = b[1]
xllcor = b[0]
yllcor = b[3] + nlon*b[4] + nlat*b[5]

#create info file
file_info = open(tmp_f+'info.txt', 'w')
file_info.write("Satellite precipitation data in "+TypeName+" format downloaded from UCI CHRS's DataPortal(chrsdata.eng.uci.edu).\n")
file_info.write("Data domain:\n")
file_info.write("ncols     %s\n" % nlon)
file_info.write("nrows    %s\n" % nlat)
file_info.write("xllcorner %.3f\n" % xllcor)
file_info.write("yllcorner %.3f\n" % yllcor)
file_info.write("cellsize %.2f\n" % cell)
file_info.write("NODATA_value -99\n")
file_info.write("Unit: mm\n")
file_info.close()

for file in glob.iglob(outShapefile[:-4]+".*"):
	shutil.copy(file, tmp_f)

shutil.make_archive(outfile, format=compression, root_dir=tmp_f)
