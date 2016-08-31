#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import gdal
import shutil
import ogr
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
	
def ClipRaster(args):
	fileIn = args[0]
	outShapefile = args[1]
	resolution = args[2]
	p1 = args[3]
	dest_file = args[4]
	dtype = args[5]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+p1+" -of GTiff -ot "+dtype+" "+fileIn+" "+dest_file)

####Create tif files###
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
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
		resolution = "0.04"
	else:
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
		resolution = "0.25"
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"

#Shapefile

#check shapefile
outShapefile = ShapeSelection(loc, shapefile)
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
if dataset == 'CDR':
	dtype = 'Float32'
	TypeArray = itertools.repeat('Float32', len(list_file))
	pool.map(ClipRaster, itertools.izip(list_file, ShapeArray, ResArray, CoorArray,list_dest_file, TypeArray))
elif dataset in ['PERSIANN', 'CCS']:
	dtype = 'Int16'
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

#convert to netcdf
file1 = sorted(glob.glob(tmp_f+'*.*'))[0]

ds = gdal.Open(file1)
a = ds.ReadAsArray()
nlat,nlon = np.shape(a)
b = ds.GetGeoTransform() #bbox, interval
lon = np.arange(nlon)*b[1]+b[0]
lat = np.arange(nlat)*b[5]+b[3]


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
filenameo = nco.createVariable('filename','i4',('filename'))
filenameo[:] = [int(re.findall('\d+', os.path.basename(fi))[-1]) for fi in sorted(glob.glob(tmp_f+'*.*'))]

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
tmno = nco.createVariable('precip', dtype,  ('filename', 'lat', 'lon'), 
   zlib=True,chunksizes=[chunk_time,chunk_lat,chunk_lon],fill_value=-99, least_significant_digit=3)
tmno.grid_mapping = 'crs'
tmno.set_auto_maskandscale(False)

nco.Conventions='CF-1.6'

#write lon,lat
lono[:]=lon
lato[:]=lat

#Read files
temp_file = '../userFile/temp/'+curr_str+'/temp.vrt'
os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate "+temp_file+" "+' '.join(list_dest_file))
ds = gdal.Open(temp_file)
tmno[:,:,:] = ds.ReadAsArray()

os.remove(temp_file)
    	
shutil.rmtree(tmp_f)