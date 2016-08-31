#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7
#../python/rectangle_mask.py ulx uly lrx lry tif date_start date_end file_type dataset outfolder

import subprocess
import os
import sys
import gdal
import time
import shutil
import ogr
from netCDF4 import Dataset
import numpy as np
import datetime as dt
import glob

curr1 = time.gmtime()
curr = time.mktime(curr1)
curr_str = str(curr)[:-2]

if not os.path.exists('../userFile/temp/'):
    os.makedirs('../userFile/temp/', 0777)
if not os.path.exists('../userFile/temp/shapes/'):
    os.makedirs('../userFile/temp/shapes/')
temp_folder0 = '../userFile/temp/'+curr_str+'/'
os.makedirs(temp_folder0, 0777)

id = sys.argv[1]
shapefile = sys.argv[2]
date_start = sys.argv[3]
date_end = sys.argv[4]
dataset = sys.argv[5]
outfile = sys.argv[6]
timestepAlt = sys.argv[8]
time_step = sys.argv[9]

####Create tif files###
if dataset == 'CDR':
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
	lat = 60
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"

# shapefile = '/var/www/html/voxtests/CHRSData/shapes/basins_l1_new.shp'
# ogr2ogr -f "ESRI Shapefile" -where \ "HYBAS_ID = '4020015090'" /var/www/html/voxtests/CHRSData/userFile/hoang2.shp /var/www/html/voxtests/CHRSData/shapes/basins_l1_new.shp

#check shapefile
shp_name = (shapefile.split('/'))[-1]
if shp_name == 'country_fusion.shp':
	prop = 'FIPS_CNTRY'
	filter = '{} = \'{}\''.format(prop, id)
	prior = "/usr/local/epd-7.3-2-rh5-x86_64/bin/"
elif shp_name == 'pol_divisions.shp':
	prop = 'NAM'
	filter = '{} = \'{}\''.format(prop, id)
	prior = "/usr/local/epd-7.3-2-rh5-x86_64/bin/"
elif shp_name[:6] == 'basins':
	prop = 'HYBAS_ID'
	filter = '{} = \'{}\''.format(prop, id)
	prior = "/usr/local/bin/"
else:
	print 'please select boundary, pol_division or basins shapefiles...'
	sys.exit()

#select feature
# filter = '{} = \'{}\''.format(prop, id)

if ' ' in id:
	id = id.replace(' ', '_')

# Save extent to a new Shapefile
outShapefile = '/mnt/t/disk2/pconnect/CHRSData/userFile/temp/shapes/'+id+'.shp'

# Keep shapefile if it already exists
if not os.path.isfile(outShapefile):
	command2 = prior+"ogr2ogr -f \"ESRI Shapefile\" -where \\ \""+filter+"\" "+outShapefile+" "+shapefile
	# print command1
	subprocess.Popen(command2, shell=True).communicate()

command = "for b in `ls "+path_to_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -crop_to_cutline -of GTiff $b  "+temp_folder0+"$(basename ${b%.*}).tif -co COMPRESS=LZW; done"
subprocess.Popen(command, shell=True).communicate()

####convert to netcdf
file1 = sorted(glob.glob(temp_folder0+'*.tif'))[0]

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

#create netCDF file
nco.createDimension('lon',nlon)
nco.createDimension('lat',nlat)
nco.createDimension('time',None)
timeo = nco.createVariable('time','f4',('time'))
timeo.units = 'days since '+date_start[:4]+'-'+date_start[4:6]+'-'+date_start[6:8]
timeo.standard_name = 'time'
timeo[:] = np.arange(int(date_start[-2:]),int(date_start[-2:])+ len(glob.glob(temp_folder0+'*')))

lono = nco.createVariable('lon','f4',('lon'))
lono.units = 'degrees_east'
lono.standard_name = 'longitude'

lato = nco.createVariable('lat','f4',('lat'))
lato.units = 'degrees_north'
lato.standard_name = 'latitude'

# create container variable for CRS: lon/lat WGS84 datum
crso = nco.createVariable('crs','i4')
crso.long_name = 'Lon/Lat Coords in WGS84'
crso.grid_mapping_name='latitude_longitude'
crso.longitude_of_prime_meridian = 0.0
crso.semi_major_axis = 6378137.0
crso.inverse_flattening = 298.257223563

# create short float variable for precipitation data, with chunking
tmno = nco.createVariable('precip', 'f4',  ('time', 'lat', 'lon'), 
   zlib=True,chunksizes=[chunk_time,chunk_lat,chunk_lon],fill_value=-99, least_significant_digit=3)
if dataset == 'CDR':
	tmno.units = 'mm/day'
	tmno.long_name = 'daily precipitation'
	tmno.standard_name = 'daily_precip'
elif dataset == 'CCS':
	tmno.units = 'mm/h'
	tmno.long_name = 'hourly precipitation'
	tmno.standard_name = 'hourly_precip'
tmno.grid_mapping = 'crs'
tmno.set_auto_maskandscale(False)

nco.Conventions='CF-1.6'

#write lon,lat
lono[:]=lon
lato[:]=lat
# itime=0
#Read files
temp_file = '../userFile/temp/'+curr_str+'/temp.vrt'
command1 = "/usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate "+temp_file+" "+temp_folder0+"*.tif"
subprocess.Popen(command1, shell=True, executable="/bin/bash").communicate()
ds = gdal.Open(temp_file)
tmno[:,:,:] = ds.ReadAsArray()
os.remove(temp_file)

# for root, dirs, files in os.walk(temp_folder0):
#     files.sort()
#     for f in files:
# 		if dataset == 'CDR':
# 			year=int(f[4:8])
# 			mon=int(f[8:10])
# 			day=int(f[10:12])
# 			hour=0
# 			date=dt.datetime(year,mon,day,hour,0,0)
# 			basedate = dt.datetime(int(date_start[:4]), int(date_start[4:6]), int(date_start[-2:]),0,0,0)
# 			dtime=(date-basedate).total_seconds()/86400
# 		elif dataset == 'CCS':
# 			start = f.find(pre_name)+len(pre_name)
# 			end = f.find('.tif', start)
# 			date_time_ccs = f[start:end]
# 			date = time.strptime(date_time_ccs, "%y%j%H")
# 			dtime=(time.mktime(date)-time.mktime(date_start1))/3600
# 			#hour=(f[12:13])
# 		
# 		timeo[itime]=dtime
# 		# min temp
# 		tmn_path = os.path.join(root,f)
# 		print(tmn_path)
# 		tmn=Image.open(tmn_path)
# 		a1=np.array(tmn)  #data
# 		tmno[itime,:,:]=a1
# 		itime=itime+1
    	
shutil.rmtree(temp_folder0)