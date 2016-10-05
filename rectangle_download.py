#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import shutil
import gdal
import glob
import numpy as np
import multiprocessing
import itertools
from asc_format_ccs1 import AscFormat

curr_str = sys.argv[1]
ulx = sys.argv[2]
uly = sys.argv[3]
lrx = sys.argv[4]
lry = sys.argv[5]
date_start = sys.argv[6]
date_end = sys.argv[7]
file_type = sys.argv[8]
dataset = sys.argv[9]
outfile = sys.argv[10]
compression = sys.argv[11]
timestepAlt = sys.argv[12]
try:
	time_step = sys.argv[13]
except IndexError:
	time_step = 'null'

temp_folder0 = '../userFile/temp/'+curr_str+'/'
temp_folder01 = '../userFile/temp/199'+curr_str+'/'

def ClipRaster(args):
	ulx = args[0]
	uly = args[1]
	lrx = args[2]
	lry = args[3]
	fileIn = args[4]
	dest_file = args[5]
	dtype = args[6]
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -ot "+dtype+" -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of GTiff "+fileIn+" "+dest_file+" -co COMPRESS=LZW")

def EditRaster(args):
	ulx = args[0]
	uly = args[1]
	lrx = args[2]
	lry = args[3]
	fileIn = args[4]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7 /root/gdal-1.11.2/swig/python/scripts/gdal_edit.py -a_ullr "+ulx+" "+uly+" "+lrx+" "+lry+" "+fileIn)
	
def MergeRaster(args):
	fileIn1 = args[0]
	fileIn2 = args[1]
	fileOut = args[2]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7 /root/gdal-1.11.2/swig/python/scripts/gdal_merge.py -q -o "+fileOut+" "+fileIn1+" "+fileIn2+" -co COMPRESS=LZW")

if dataset == 'CDR':
	resolution = '0.25'
	lat = 60
	if len(date_start) == 8:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/daily/CDR_{"+date_start+".."+date_end+"}z.tif 2>/dev/null"
	elif len(date_start) == 6:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/monthly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"
	elif len(date_start) == 4:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/yearly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"	
elif dataset in ['CCS', 'PERSIANN']:
	lat = 60
	if dataset == 'CCS':
		resolution = '0.04'
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
	else:
		resolution = '0.25'
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"

pool = multiprocessing.Pool(processes = 4)
list_file = [file1.replace('\n','') for file1 in os.popen('ls '+path_to_file).readlines()]
if float(ulx) <= float(lrx):
	uly = str(lat) if float(uly) > lat else uly
	lry = str(-lat) if float(lry) < -lat else lry
	uly_arr = itertools.repeat(uly, len(list_file))
	ulx_arr = itertools.repeat(ulx, len(list_file))
	lry_arr = itertools.repeat(lry, len(list_file))
	lrx_arr = itertools.repeat(lrx, len(list_file))
	if file_type == 'Tif':
		TypeName = 'GeoTiff'
		list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
		if dataset in ['CDR', 'PERSIANN']:
			TypeArray = ['Float32']* len(list_file)
		elif dataset == 'CCS':
			TypeArray = ['Int16']* len(list_file)
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, list_file, list_dest_file, TypeArray))
	elif file_type == 'ArcGrid':
		TypeName = 'ArcGrid'
		list_dest_file1 = [temp_folder01+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
		list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.asc' for file2 in list_file]
		dataset_arr = itertools.repeat(dataset, len(list_dest_file))
		if dataset in ['CDR', 'PERSIANN']:
			TypeArray = ['Float32']* len(list_file)
			pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, list_file,list_dest_file1, TypeArray))
			pool.map(AscFormat, itertools.izip(list_dest_file1, list_dest_file, dataset_arr))
		elif dataset == 'CCS':
			TypeArray = ['Int16']* len(list_file)
			pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, list_file,list_dest_file1, TypeArray))
			pool.map(AscFormat, itertools.izip(list_dest_file1, list_dest_file, dataset_arr))
else:
	lrx1 = float(lrx) + 360
	lrx1 = str(lrx1)
	ulx1 = float(ulx) - 360
	ulx1 = str(ulx1)
	uly = str(lat) if float(uly) > lat else uly
	lry = str(-lat) if float(lry) < -lat else lry
	uly_arr = [uly]* len(list_file)
	ulx_arr = [ulx]* len(list_file)
	lry_arr = [lry]* len(list_file)
	lrx_arr = [lrx]* len(list_file)
	ulx1_arr = [ulx1]* len(list_file)
	XE = ['180']* len(list_file)
	XW = ['-180']* len(list_file)
	temp_folder1 = '../userFile/temp/188'+curr_str+'/'
	if dataset in ['CDR', 'PERSIANN']:
		TypeArray = ['Float32']* len(list_file)
		list_temp_file1 = [temp_folder1+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
		list_temp_file2 = [temp_folder1+os.path.splitext(os.path.basename(file2))[0]+'_2.tif' for file2 in list_file]
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, XE, lry_arr, list_file,list_temp_file1, TypeArray))
		pool.map(ClipRaster, itertools.izip(XW, uly_arr, lrx_arr, lry_arr, list_file,list_temp_file2, TypeArray))
	elif dataset == 'CCS':
		TypeArray = ['Int16']* len(list_file)
		list_temp_file1 = [temp_folder1+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
		list_temp_file2 = [temp_folder1+os.path.splitext(os.path.basename(file2))[0]+'_2.tif' for file2 in list_file]
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, XE, lry_arr, list_file,list_temp_file1, TypeArray))
		pool.map(ClipRaster, itertools.izip(XW, uly_arr, lrx_arr, lry_arr, list_file,list_temp_file2, TypeArray))
	pool.map(EditRaster, itertools.izip(ulx1_arr, uly_arr, XW, lry_arr,list_temp_file1))
	if file_type == 'Tif':
		TypeName = 'GeoTiff'
		list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
		pool.map(MergeRaster, itertools.izip(list_temp_file1, list_temp_file2, list_dest_file))
	elif file_type == 'ArcGrid':
		TypeName = 'ArcGrid'
		list_dest_file1 = [temp_folder01+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
		list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.asc' for file2 in list_file]
		pool.map(MergeRaster, itertools.izip(list_temp_file1, list_temp_file2, list_dest_file1))
		dataset_arr = itertools.repeat(dataset, len(list_dest_file))
		pool.map(AscFormat, itertools.izip(list_dest_file1, list_dest_file, dataset_arr))

file1 = sorted(glob.glob(temp_folder0+'*.*'))[0]
ds = gdal.Open(file1)
a = ds.ReadAsArray()
nlat,nlon = a.shape
b = ds.GetGeoTransform() #bbox, interval
lon = np.arange(nlon)*b[1]+b[0]
lat = np.arange(nlat)*b[5]+b[3]
cell = b[1]
xllcor = b[0]
yllcor = b[3] + nlon*b[4] + nlat*b[5]

#create info file
file_info = open(temp_folder0+'info.txt', 'w')
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
shutil.make_archive(outfile, format=compression, root_dir=temp_folder0)	

