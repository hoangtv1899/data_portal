#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import gdal
import re
import shutil
from zipfile import ZipFile
import tarfile
from netCDF4 import Dataset
import numpy as np
import multiprocessing
import itertools
import glob

curr_str = sys.argv[1]
ulx = sys.argv[2]
uly = sys.argv[3]
lrx = sys.argv[4]
lry = sys.argv[5]
date_start = sys.argv[6]
date_end = sys.argv[7]
dataset = sys.argv[8]
outfile = sys.argv[9]
compression = sys.argv[10]
timestepAlt = sys.argv[11]
try:
	time_step = sys.argv[12]
except IndexError:
	time_step = 'null'

temp_folder0 = '../userFile/temp/'+curr_str+'/'

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

####Create tif files###
if dataset == 'CDR':
	resolution = '0.25'
	lat = 60
	dtype = 'f4'
	if len(date_start) == 8:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/daily/CDR_{"+date_start+".."+date_end+"}z.tif 2>/dev/null"
	elif len(date_start) == 6:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/monthly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"
	elif len(date_start) == 4:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/yearly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"	
elif dataset in ['CCS', 'PERSIANN']:
	lat = 60
	if dataset == 'CCS':
		dtype = 'i2'
		resolution = '0.04'
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
	else:
		dtype = 'f4'
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
	list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
	if dataset in ['CDR', 'PERSIANN']:
		TypeArray = ['Float32']* len(list_file)
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, list_file, list_dest_file, TypeArray))
	elif dataset=='CCS':
		TypeArray = ['Int16']* len(list_file)
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, list_file, list_dest_file, TypeArray))
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
	list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
	pool.map(MergeRaster, itertools.izip(list_temp_file1, list_temp_file2, list_dest_file))

#convert to netcdf
file1 = sorted(glob.glob(temp_folder0+'*.tif'))[0]

ds = gdal.Open(file1)
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
file_info.write("Unit mm\n")
file_info.close()

#create netCDF file
nco = Dataset(outfile,'w',clobber=True)

# chunking is optional, but can improve access a lot: 
# (see: http://www.unidata.ucar.edu/blogs/developer/entry/chunking_data_choosing_shapes)
chunk_lon=16
chunk_lat=16
chunk_time=12

# create dimensions, variables and attributes:
nco.createDimension('lon',nlon)
nco.createDimension('lat',nlat)
nco.createDimension('filename',None)
filenameo = nco.createVariable('filename','S1',('filename'))
filenameo[:] = [int(re.findall('\d+', os.path.basename(fi))[-1]) for fi in sorted(glob.glob(temp_folder0+'*.tif'))]

lono = nco.createVariable('lon','f4',('lon'))
lato = nco.createVariable('lat','f4',('lat'))

# create container variable for CRS: lon/lat WGS84 datum
crso = nco.createVariable('crs','i4')
crso.long_name = 'Lon/Lat Coords in WGS84'
crso.grid_mapping_name='latitude_longitude'
crso.longitude_of_prime_meridian = 0.0
crso.semi_major_axis = 6378137.0
crso.inverse_flattening = 298.257223563

nco.Conventions='CF-1.6'

#write lon,lat
lono[:]=lon
lato[:]=lat

#Read files
temp_file = '../userFile/temp/'+curr_str+'/temp.vrt'
os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate "+temp_file+" "+' '.join(list_dest_file))
ds = gdal.Open(temp_file)
if (len(ds.ReadAsArray().shape) == 3):
	# create short float variable for precipitation data, with chunking
	tmno = nco.createVariable('precip', dtype,  ('filename', 'lat', 'lon'), 
		zlib=True,chunksizes=[chunk_time,chunk_lat,chunk_lon])
	tmno.grid_mapping = 'crs'
	tmno.set_auto_maskandscale(False)
	tmno[:] = ds.ReadAsArray()
elif (len(ds.ReadAsArray().shape) == 2):
	# create short float variable for precipitation data, with chunking
	tmno = nco.createVariable('precip', dtype,  ('lat', 'lon'), 
		zlib=True,chunksizes=[chunk_lat,chunk_lon])
	tmno.grid_mapping = 'crs'
	tmno.set_auto_maskandscale(False)
	tmno[:] = ds.ReadAsArray()

nco.close()
zip_name = outfile.split('_')[0]+"_"+curr_str+'.'+compression
if compression == 'zip':
	with ZipFile(zip_name, 'w') as myzip:
		myzip.write("../python/read_netcdf/read_netcdf.py", "read_netcdf.py")
		myzip.write("../python/read_netcdf/read_netcdf.m", "read_netcdf.m")
		myzip.write(temp_folder0+"info.txt", "info.txt")
		myzip.write(outfile, os.path.basename(outfile))
else:
	tar = tarfile.open(zip_name, "w")
	tar.add(outfile, os.path.basename(outfile))
	tar.add("../python/read_netcdf/read_netcdf.py", "read_netcdf.py")
	tar.add("../python/read_netcdf/read_netcdf.m", "read_netcdf.m")
	tar.add(temp_folder0+"info.txt", "info.txt")
	tar.close()