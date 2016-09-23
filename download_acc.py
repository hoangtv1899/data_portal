#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

from datetime import datetime
import os
import ogr
import gdal
import sys
import re
import shutil
import math
from netCDF4 import Dataset
import numpy as np
import multiprocessing
import itertools
import tarfile
from zipfile import ZipFile
from ShapeSelection import ShapeSelection
from asc_format_ccs1 import AscFormat

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        a = s[start:end]
        return [x for x in a.split(' ') if x]
    except ValueError:
        return ""

def ClipRaster(args):
	ulx = args[0]
	uly = args[1]
	lrx = args[2]
	lry = args[3]
	fileIn = args[4]
	dest_file = args[5]
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -ot Float32 -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of GTiff "+fileIn+" "+dest_file+" -co COMPRESS=LZW")

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
	
def ClipRasterShape(args):
	fileIn = args[0]
	outShapefile = args[1]
	resolution = args[2]
	p1 = args[3]
	dest_file = args[4]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+p1+" -of GTiff -ot Float32 "+fileIn+" "+dest_file)
	
def DownloadShape():
	myzip.write(outShapefile[:-4]+".shp", os.path.basename(outShapefile)[:-4]+".shp")
	myzip.write(outShapefile[:-4]+".shx", os.path.basename(outShapefile)[:-4]+".shx")
	myzip.write(outShapefile[:-4]+".dbf", os.path.basename(outShapefile)[:-4]+".dbf")

def DownloadShapeTar():
	tar.add(outShapefile[:-4]+".shp", os.path.basename(outShapefile)[:-4]+".shp")
	tar.add(outShapefile[:-4]+".shx", os.path.basename(outShapefile)[:-4]+".shx")
	tar.add(outShapefile[:-4]+".dbf", os.path.basename(outShapefile)[:-4]+".dbf")
	
out_file = sys.argv[1]
dataset = sys.argv[2]
userIP = sys.argv[3]
currentDateTime = sys.argv[4]
domain = sys.argv[5]
file_type = sys.argv[6]
compression = sys.argv[7]
input_string = sys.argv[8]

#input_string='ha: 08010122 da: 080102 mth: 0802 yrs: 09 10 11 dp: 120301 hp:'
date_cat = ['ha:', 'da:', 'mth:', 'yrs:', 'dp:', 'hp:']
year_list = []
month_list = []
day_list = []
hour_list = []
for index, list in enumerate(date_cat):
	if index == 5:
		x = input_string.split(list)[1]
		a = [y for y in x.split(' ') if y]
	else:
		a = find_between( input_string, list, date_cat[index + 1])
	if a:
		if list in ['ha:', 'hp:']:
			hour_list = hour_list + a
		elif list in ['da:', 'dp:']:
			day_list = day_list + a
		elif list == 'mth:':
			month_list = month_list + a
		elif list == 'yrs:':
			year_list = year_list + a

temp_folder0 = '../userFile/temp/'+currentDateTime+'/'
temp_folder01 = '../userFile/temp/199'+currentDateTime+'/'

date_list = []
if dataset == 'CDR':
	dtype = 'f4'
	dataset1 = dataset
	timestepH = ''
	timestepD = ''
	timestepM = ''
	timestepY = ''
	base_path = '/mnt/t/disk3/CHRSdata/Persiann_CDR/'
elif dataset in ['CCS', 'PERSIANN']:
	dataset1 = dataset
	timestepH = '1h'
	timestepD = '1d'
	timestepM = '1m'
	timestepY = '1y'
	if dataset == 'PERSIANN':
		dtype = 'f4'
		base_path = '/mnt/t/disk3/CHRSdata/Persiann/'
	elif dataset == 'CCS':
		dtype = 'i2'
		base_path = '/mnt/t/disk3/CHRSdata/Persiann_CCS/'
	#add hour to list from CCS and PERSIANN
	for i in hour_list:
		i_time = datetime.strptime(i, '%y%m%d%H')
		date_list.append(dataset+'_'+timestepH+i_time.strftime('%Y%m%d%H'))
else:	#shape and rectangle
	br_dwn = dataset.split(' ')
	dataset1 = br_dwn[0]
	if dataset1 == 'CDR':
		dtype = 'f4'
		resolution = '0.25'
		timestepH = ''
		timestepD = ''
		timestepM = ''
		timestepY = ''
		base_path = '/mnt/t/disk3/CHRSdata/Persiann_CDR/'
		if br_dwn[1] == 'rec':
			ulx = br_dwn[2]
			uly = br_dwn[3]
			lrx = br_dwn[4]
			lry = br_dwn[5]
			ulx = str(math.ceil(float(ulx)/float(resolution))*float(resolution))
			uly = str(math.floor(float(uly)/float(resolution))*float(resolution))
			lrx = str(math.floor(float(lrx)/float(resolution))*float(resolution))
			lry = str(math.ceil(float(lry)/float(resolution))*float(resolution))
		elif br_dwn[1] == 'shp':
			shapefile = br_dwn[2]
			loc = br_dwn[3]
			loc = loc[1:-1].split(",")
			outShapefile = ShapeSelection(loc, shapefile, temp_folder0)
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
	elif dataset1 in ['CCS', 'PERSIANN']:
		timestepH = '1h'
		timestepD = '1d'
		timestepM = '1m'
		timestepY = '1y'
		if dataset1 == 'PERSIANN':
			dtype = 'f4'
			resolution = '0.25'
			base_path = '/mnt/t/disk3/CHRSdata/Persiann/'
		elif dataset1 == 'CCS':
			dtype = 'i2'
			resolution = '0.04'
			base_path = '/mnt/t/disk3/CHRSdata/Persiann_CCS/'
		#add hour to list from CCS and PERSIANN
		for i in hour_list:
			i_time = datetime.strptime(i, '%y%m%d%H')
			date_list.append(br_dwn[0]+'_'+timestepH+i_time.strftime('%Y%m%d%H'))
		if br_dwn[1] == 'rec':
			ulx = br_dwn[2]
			uly = br_dwn[3]
			lrx = br_dwn[4]
			lry = br_dwn[5]
			ulx = str(math.ceil(float(ulx)/float(resolution))*float(resolution))
			uly = str(math.floor(float(uly)/float(resolution))*float(resolution))
			lrx = str(math.floor(float(lrx)/float(resolution))*float(resolution))
			lry = str(math.ceil(float(lry)/float(resolution))*float(resolution))
		elif br_dwn[1] == 'shp':
			shapefile = br_dwn[2]
			loc = br_dwn[3]
			loc = loc[1:-1].split(",")
			outShapefile = ShapeSelection(loc, shapefile, temp_folder0)
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
for j in day_list:
	j_time = datetime.strptime(j, '%y%m%d')
	date_list.append(dataset1+'_'+timestepD+j_time.strftime('%Y%m%d'))

for k in month_list:
	k_time = datetime.strptime(k, '%y%m')
	date_list.append(dataset1+'_'+timestepM+k_time.strftime('%Y%m'))

for l in year_list:
	l_time = datetime.strptime(l, '%y')
	date_list.append(dataset1+'_'+timestepY+l_time.strftime('%Y'))

file_list = []
for root, dirs, files in os.walk(base_path):
	for file in files:
		if any(dl in file for dl in date_list):
			file_list.append(os.path.join(root, file))

#print file_list
#DO THE ACCUMULATION
pool = multiprocessing.Pool(processes = 4)
if dataset in ['CCS', 'CDR', 'PERSIANN']:
	os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+os.path.splitext(os.path.basename(out_file))[0]+".tif'; /usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate $b "+' '.join(sorted(file_list))+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+"; rm $b 2>/dev/null")
	print 'done'
else:
	dataset1 = dataset.split(' ')[0]
	if br_dwn[1] == 'rec':
		uly = '60' if float(uly) > 60 else uly
		lry = '-60' if float(lry) < -60 else lry
		uly_arr = itertools.repeat(uly, len(file_list))
		ulx_arr = itertools.repeat(ulx, len(file_list))
		lry_arr = itertools.repeat(lry, len(file_list))
		lrx_arr = itertools.repeat(lrx, len(file_list))
		XE = ['180']* len(file_list)
		XW = ['-180']* len(file_list)
		list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in file_list]
		if float(ulx) <= float(lrx):
			pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, file_list, list_dest_file))
			os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+os.path.splitext(os.path.basename(out_file))[0]+".tif'; /usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate $b "+temp_folder0+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+"; rm $b 2>/dev/null")
			print 'done'
		else:
			lrx1 = float(lrx) + 360
			lrx1 = str(lrx1)
			ulx1 = float(ulx) - 360
			ulx1 = str(ulx1)
			ulx1_arr = [ulx1]* len(file_list)
			list_temp_file1 = [temp_folder01+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in file_list]
			list_temp_file2 = [temp_folder01+os.path.splitext(os.path.basename(file2))[0]+'_2.tif' for file2 in file_list]
			pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, XE, lry_arr, file_list,list_temp_file1))
			pool.map(ClipRaster, itertools.izip(XW, uly_arr, lrx_arr, lry_arr, file_list,list_temp_file2))
			pool.map(EditRaster, itertools.izip(ulx1_arr, uly_arr, XW, lry_arr,list_temp_file1))
			pool.map(MergeRaster, itertools.izip(list_temp_file1, list_temp_file2, list_dest_file))
			os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+os.path.splitext(os.path.basename(out_file))[0]+".tif'; /usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate $b "+temp_folder0+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+"; rm $b 2>/dev/null")
			print 'done'
	elif br_dwn[1] == 'shp':
		ShapeArray = itertools.repeat(outShapefile, len(file_list))
		ResArray = itertools.repeat(resolution, len(file_list))
		CoorArray = itertools.repeat(' '.join(p1), len(file_list))
		list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in file_list]
		pool.map(ClipRasterShape, itertools.izip(file_list, ShapeArray, ResArray, CoorArray,list_dest_file))
		os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+os.path.splitext(os.path.basename(out_file))[0]+".tif'; /usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate $b "+temp_folder0+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+"; rm $b 2>/dev/null")
		print 'done'
if file_type == 'Tif':
	os.system("cp "+temp_folder0+os.path.splitext(os.path.basename(out_file))[0]+".tif "+out_file)
	zip_name = out_file.split('_')[0]+"_"+currentDateTime+'.'+compression
	with ZipFile(zip_name, 'w') as myzip:
		myzip.write(out_file, os.path.basename(out_file))
		if br_dwn[1] == 'shp':
			DownloadShape()
elif file_type == 'ArcGrid':
	out_file = out_file[:-4]+".asc"
	AscFormat([temp_folder0+os.path.splitext(os.path.basename(out_file))[0]+".tif", out_file, dataset1])
	zip_name = out_file.split('_')[0]+"_"+currentDateTime+'.'+compression
	with ZipFile(zip_name, 'w') as myzip:
		myzip.write(out_file, os.path.basename(out_file))
		if br_dwn[1] == 'shp':
			DownloadShape()
elif file_type == 'NetCDF':
	out_file = out_file[:-4]+".nc"
	ds = gdal.Open(temp_folder0+os.path.splitext(os.path.basename(out_file))[0]+".tif")
	a = ds.ReadAsArray()
	nlat,nlon = np.shape(a)
	b = ds.GetGeoTransform() #bbox, interval
	lon = np.arange(nlon)*b[1]+b[0]
	lat = np.arange(nlat)*b[5]+b[3]
	cell = b[1]
	xllcor = b[0]
	yllcor = b[3] + nlon*b[4] + nlat*b[5]
	#create info file
	file_info = open(temp_folder0+'info.txt', 'w')
	file_info.write("Satellite precipitation data in NetCDF format downloaded from UCI CHRS's DataPortal(chrsdata.eng.uci.edu).\n")
	file_info.write("Data domain:\n")
	file_info.write("ncols     %s\n" % nlon)
	file_info.write("nrows    %s\n" % nlat)
	file_info.write("xllcorner %.3f\n" % xllcor)
	file_info.write("yllcorner %.3f\n" % yllcor)
	file_info.write("cellsize %.2f\n" % cell)
	file_info.write("NODATA_value -99\n")
	file_info.close()
	#create netCDF file
	nco = Dataset(out_file,'w',clobber=True)
	chunk_lon=16
	chunk_lat=16
	# create dimensions, variables and attributes:
	nco.createDimension('lon',nlon)
	nco.createDimension('lat',nlat)
	nco.createDimension('filename',None)
	lono = nco.createVariable('lon','f4',('lon'))
	lato = nco.createVariable('lat','f4',('lat'))
	# create container variable for CRS: lon/lat WGS84 datum
	crso = nco.createVariable('crs','i4')
	crso.long_name = 'Lon/Lat Coords in WGS84'
	crso.grid_mapping_name='latitude_longitude'
	crso.longitude_of_prime_meridian = 0.0
	crso.semi_major_axis = 6378137.0
	crso.inverse_flattening = 298.257223563
	# create short float variable for precipitation data, with chunking
	tmno = nco.createVariable('precip', dtype, ('lat', 'lon'), zlib=True,chunksizes=[chunk_lat,chunk_lon])
	tmno.grid_mapping = 'crs'
	tmno.set_auto_maskandscale(False)
	nco.Conventions='CF-1.6'
	#write lon,lat
	lono[:]=lon
	lato[:]=lat
	#write data
	tmno[:] = a
	nco.close()
	zip_name = out_file.split('_')[0]+"_"+currentDateTime+'.'+compression
	if compression == 'zip':
		with ZipFile(zip_name, 'w') as myzip:
			myzip.write("../python/read_netcdf/read_netcdf.py", "read_netcdf.py")
			myzip.write("../python/read_netcdf/read_netcdf.m", "read_netcdf.m")
			myzip.write(temp_folder0+"info.txt", "info.txt")
			myzip.write(out_file, os.path.basename(out_file))
			if br_dwn[1] == 'shp':
				DownloadShape()
	else:
		tar = tarfile.open(zip_name, "w:gz")
		tar.add(outfile, os.path.basename(outfile))
		tar.add("../python/read_netcdf/read_netcdf.py", "read_netcdf.py")
		tar.add("../python/read_netcdf/read_netcdf.m", "read_netcdf.m")
		tar.add(tmp_f+"info.txt", "info.txt")
		if br_dwn[1] == 'shp':
			DownloadShapeTar()
		tar.close()