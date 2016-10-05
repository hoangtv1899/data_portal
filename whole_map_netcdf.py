#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import gdal
import shutil
import tarfile
from zipfile import ZipFile
from netCDF4 import Dataset
import numpy as np
import glob

curr_str = sys.argv[1]
date_start = sys.argv[2]
date_end = sys.argv[3]
time_step = sys.argv[4]
dataset = sys.argv[5]
outfile = sys.argv[6]
compression = sys.argv[7]
timestepAlt = sys.argv[8]

temp_folder0 = '../userFile/temp/'+curr_str+'/'

if dataset == 'CDR':
	dtype = 'f4'
	if len(date_start) == 8:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/daily/CDR_{"+date_start+".."+date_end+"}z.tif 2>/dev/null"
	elif len(date_start) == 6:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/monthly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"
	elif len(date_start) == 4:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/yearly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"
elif dataset in ['CCS', 'PERSIANN']:
	if dataset == 'CCS':
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
		dtype = 'i2'
	else:
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
		dtype = 'f4'
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"
print path_to_file
os.system("for b in `ls "+path_to_file+"`; do cp $b "+temp_folder0+"$(basename ${b%.*}).tif; done")
#convert to netcdf
file1 = sorted(glob.glob(temp_folder0+'*.*'))[0]

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
filenameo[:] = [os.path.basename(fi) for fi in sorted(glob.glob(temp_folder0+'*.tif'))]

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
   zlib=True,chunksizes=[chunk_time,chunk_lat,chunk_lon])
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
	tar = tarfile.open(zip_name, "w:gz")
	tar.add(outfile, os.path.basename(outfile))
	tar.add("../python/read_netcdf/read_netcdf.py", "read_netcdf.py")
	tar.add("../python/read_netcdf/read_netcdf.m", "read_netcdf.m")
	tar.add(temp_folder0+"info.txt", "info.txt")
	tar.close()
