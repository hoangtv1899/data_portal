#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import gdal
import shutil
from netCDF4 import Dataset
import numpy as np
import glob

curr_str = sys.argv[1]
date_start = sys.argv[2]
date_end = sys.argv[3]
time_step = sys.argv[4]
dataset = sys.argv[5]
outfile = sys.argv[6]
timestepAlt = sys.argv[7]

temp_folder0 = '../userFile/temp/'+curr_str+'/'

if dataset == 'CDR':
	dtype = 'f4'
	if len(date_start) == 8:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/daily_asc/CDR_{"+date_start+".."+date_end+"}z.asc 2>/dev/null"
	elif len(date_start) == 6:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/monthly_asc/CDR_{"+date_start+".."+date_end+"}.asc 2>/dev/null"
	elif len(date_start) == 4:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/yearly_asc/CDR_{"+date_start+".."+date_end+"}.asc 2>/dev/null"
elif dataset in ['CCS', 'PERSIANN']:
	if dataset == 'CCS':
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
	else:
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
	dtype = 'i4'
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"

os.system("for b in `ls "+path_to_file+"`; do cp $b "+temp_folder0+"$(basename ${b%.*}).asc; done")
#convert to netcdf
file1 = sorted(glob.glob(temp_folder0+'*.*'))[0]

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
filenameo = nco.createVariable('filename','S1',('filename'))
filenameo[:] = [os.path.basename(fi) for fi in sorted(glob.glob(temp_folder0+'*.*'))]

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

# itime=0
#Read files
temp_file = '../userFile/temp/'+curr_str+'/temp.vrt'
os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate "+temp_file+" `ls "+path_to_file+"`")
ds = gdal.Open(temp_file)
tmno[:,:,:] = ds.ReadAsArray()
