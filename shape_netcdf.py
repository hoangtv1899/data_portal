#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import gdal
import shutil
import ogr
import tarfile
from zipfile import ZipFile
from netCDF4 import Dataset
import numpy as np
import multiprocessing
import itertools
from ShapeSelection import ShapeSelection
import glob
import re

#inputs
curr_str = sys.argv[1]
loc = sys.argv[2]
loc = loc[1:-1].split(",")
shapefile = sys.argv[3]
date_start = sys.argv[4]
date_end = sys.argv[5]
dataset = sys.argv[6]
outfile = sys.argv[7]
compression = sys.argv[8]
timestepAlt = sys.argv[9]
try:
	time_step = sys.argv[10]
except IndexError:
	time_step = 'null'

tmp_f = '../userFile/temp/'+curr_str+'/'
tmp_shp = '../userFile/temp/shp_'+curr_str+'/'
	
def ClipRaster(args):
	fileIn = args[0]
	outShapefile = args[1]
	resolution = args[2]
	p1 = args[3]
	dest_file = args[4]
	dtype = args[5]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+p1+" -of GTiff -ot "+dtype+" "+fileIn+" "+dest_file)

def DownloadShape():
	myzip.write(outShapefile[:-4]+".shp", os.path.basename(outShapefile)[:-4]+".shp")
	myzip.write(outShapefile[:-4]+".shx", os.path.basename(outShapefile)[:-4]+".shx")
	myzip.write(outShapefile[:-4]+".dbf", os.path.basename(outShapefile)[:-4]+".dbf")

def DownloadShapeTar():
	tar.add(outShapefile[:-4]+".shp", os.path.basename(outShapefile)[:-4]+".shp")
	tar.add(outShapefile[:-4]+".shx", os.path.basename(outShapefile)[:-4]+".shx")
	tar.add(outShapefile[:-4]+".dbf", os.path.basename(outShapefile)[:-4]+".dbf")
	
####Create tif files###
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
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
		resolution = "0.04"
	else:
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
		resolution = "0.25"
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"

#Shapefile

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

#Clip raster
pool = multiprocessing.Pool(processes = 4)
list_file = [file1.replace('\n','') for file1 in os.popen('ls '+path_to_file).readlines()]
ShapeArray = itertools.repeat(outShapefile, len(list_file))
ResArray = itertools.repeat(resolution, len(list_file))
CoorArray = itertools.repeat(' '.join(p1), len(list_file))
list_dest_file = [tmp_f+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in list_file]
if dataset in ['CDR', 'PERSIANN']:
	dtype = 'f4'
	TypeArray = itertools.repeat('Float32', len(list_file))
	pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file, TypeArray))
elif dataset =='CCS':
	dtype = 'i2'
	TypeArray = itertools.repeat('Int16', len(list_file))
	pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file, TypeArray))

####convert to netcdf
file1 = sorted(glob.glob(tmp_f+'*.tif'))[0]

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
file_info = open(tmp_f+'info.txt', 'w')
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
if 'basins_l4_new.shp' in shapefile.split('/'):
	chunk_lon=8
	chunk_lat=8
	chunk_time=12
else:
	chunk_lon=16
	chunk_lat=16
	chunk_time=12

# create dimensions, variables and attributes:
nco.createDimension('lon',nlon)
nco.createDimension('lat',nlat)
nco.createDimension('filename',None)
filenameo = nco.createVariable('filename','S1',('filename'))
filenameo[:] = [int(re.findall('\d+', os.path.basename(fi))[-1]) for fi in sorted(glob.glob(tmp_f+'*.tif'))]

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
zip_name = outfile[:-3]+'.'+compression
if compression == 'zip':
	with ZipFile(zip_name, 'w') as myzip:
		myzip.write("../python/read_netcdf/read_netcdf.py", "read_netcdf.py")
		myzip.write("../python/read_netcdf/read_netcdf.m", "read_netcdf.m")
		myzip.write(tmp_f+"info.txt", "info.txt")
		myzip.write(outfile, os.path.basename(outfile))
		DownloadShape()
else:
	tar = tarfile.open(zip_name, "w:gz")
	tar.add(outfile, os.path.basename(outfile))
	tar.add("../python/read_netcdf/read_netcdf.py", "read_netcdf.py")
	tar.add("../python/read_netcdf/read_netcdf.m", "read_netcdf.m")
	tar.add(tmp_f+"info.txt", "info.txt")
	DownloadShapeTar()
	tar.close()