#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

from datetime import date, timedelta, datetime
import os
import sys
import subprocess
import shutil

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        a = s[start:end]
        return [x for x in a.split(' ') if x]
    except ValueError:
        return ""

out_file = sys.argv[1]
dataset = sys.argv[2]
userIP = sys.argv[3]
currentDateTime = sys.argv[4]
domain = sys.argv[5]
file_type = sys.argv[6]
compression = sys.argv[7]
id = sys.argv[8]
shapefile = sys.argv[9]

shp_name = (shapefile.split('/'))[-1]
if shp_name == 'country_fusion.shp':
	prop = 'FIPS_CNTRY'
elif shp_name == 'pol_divisions.shp':
	prop = 'NAM'
elif shp_name[:6] == 'basins':
	prop = 'HYBAS_ID'
else:
	print 'please select boundary, pol_division or basins shapefiles...'
	sys.exit()
filter = '{} = \'{}\''.format(prop, id)
#select feature
if ' ' in id:
	id = id.replace(' ', '_')
# Save extent to a new Shapefile
outShapefile = '/mnt/t/disk2/pconnect/CHRSData/userFile/temp/shapes/'+id+'.shp'
# Remove output shapefile if it already exists
try:
	os.remove(outShapefile)
	os.remove('/mnt/t/disk2/pconnect/CHRSData/userFile/temp/shapes/'+id+'.dbf')
	os.remove('/mnt/t/disk2/pconnect/CHRSData/userFile/temp/shapes/'+id+'.shx')
except OSError:
	pass
cmdshape = "/usr/local/bin/ogr2ogr -f \"ESRI Shapefile\" -where \\ \""+filter+"\" "+outShapefile+" "+shapefile
# print cmdshape
subprocess.Popen(cmdshape, shell=True).communicate()

temp_folder1 = '../userFile/temp/'+userIP+'/'
if not os.path.exists(temp_folder1):
	os.makedirs(temp_folder1)

#temp folder use for creating asc file while not keeping tif file
temp_folder0 = '../userFile/temp/0'+userIP+'/'
if not os.path.exists(temp_folder0):
	os.makedirs(temp_folder0)

if file_type == 'ArcGrid':
	if dataset == 'CDR':
		resolution = '0.25'
		if domain == '0':
			command = "for b in `ls "+out_file+"`; do "+os.path.dirname(__file__)+"/asc_format.py $b "+temp_folder1+"$(basename ${b%.*}).asc; done"
			subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
		elif domain == '1':
			lat = 60
			if float(ulx) <= float(lrx):
				uly = str(lat) if float(uly) > lat else uly
				lry = str(-lat) if float(lry) < -lat else lry
				command = "for b in "+out_file+"; do /usr/local/bin/gdal_translate -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of AAIGrid "+out_file+" "+temp_folder0+"$(basename ${b%.*}).asc; "+os.path.dirname(__file__)+"/asc_format_ccs.py "+temp_folder0+"$(basename ${b%.*}).asc "+temp_folder1+"$(basename ${b%.*}).asc; done"
				subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
			elif float(ulx) > float(lrx):
				lrx1 = float(lrx) + 360
				lrx1 = str(lrx1)
				ulx1 = float(ulx) - 360
				ulx1 = str(ulx1)
				cmd4 = "for b in "+out_file+"; do /usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7 /root/gdal-1.11.2/swig/python/scripts/gdal_merge.py -o "+temp_folder0+"$(basename ${b%.*}).tif $b "+temp_folder0+"$(basename ${b%.*}).tif -co COMPRESS=LZW >& /dev/null; done"
				cmd5 = "for b in "+temp_folder0+"*.tif; do /usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -of AAIGrid $b "+temp_folder0+"$(basename ${b%.*}).asc >& /dev/null; "+os.path.dirname(__file__)+"/asc_format_ccs.py "+temp_folder0+"$(basename ${b%.*}).asc "+temp_folder1+"$(basename ${b%.*}).asc; done"
				subprocess.Popen("{}; {}".format(cmd4, cmd5), shell=True, executable="/bin/bash").communicate()
		else:
			command = "for b in `ls "+out_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -crop_to_cutline -of GTiff $b "+temp_folder0+"$(basename ${b%.*}).tif; done"
			print command
			command1 = "for file in "+temp_folder0+"*.tif; do /usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -of AAIGrid $file "+temp_folder0+"$(basename ${file%.*}).asc; "+os.path.dirname(__file__)+"/asc_format.py "+temp_folder0+"$(basename ${file%.*}).asc "+temp_folder1+"$(basename ${file%.*}).asc; done"
			command2 = "cp /mnt/t/disk2/pconnect/CHRSData/userFile/temp/shapes/"+id+".* "+temp_folder1
			subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
			subprocess.Popen(command1, shell=True, executable="/bin/bash").communicate()
			subprocess.Popen(command2, shell=True, executable="/bin/bash").communicate()
	else:
		if dataset == 'PERSIANN':
			resolution = '0.25'
		else:
			resolution = '0.04'
		if domain == '0':
			command = "for b in `ls "+out_file+"`; do "+os.path.dirname(__file__)+"/asc_format_ccs.py $b "+temp_folder1+"$(basename ${b%.*}).asc; done"
			subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
		elif domain == '1':
			lat = 60
			if float(ulx) <= float(lrx):
				uly = str(lat) if float(uly) > lat else uly
				lry = str(-lat) if float(lry) < -lat else lry
				command = "for b in "+out_file+"; do /usr/local/bin/gdal_translate -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of AAIGrid "+out_file+" "+temp_folder0+"$(basename ${b%.*}).asc; "+os.path.dirname(__file__)+"/asc_format_ccs.py "+temp_folder0+"$(basename ${b%.*}).asc "+temp_folder1+"$(basename ${b%.*}).asc; done"
				subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
			elif float(ulx) > float(lrx):
				lrx1 = float(lrx) + 360
				lrx1 = str(lrx1)
				ulx1 = float(ulx) - 360
				ulx1 = str(ulx1)
				cmd4 = "for b in "+out_file+"; do /usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7 /root/gdal-1.11.2/swig/python/scripts/gdal_merge.py -o "+temp_folder0+"$(basename ${b%.*}).tif $b "+temp_folder0+"$(basename ${b%.*}).tif -co COMPRESS=LZW >& /dev/null; done"
				cmd5 = "for b in "+temp_folder0+"*.tif; do /usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -of AAIGrid $b "+temp_folder0+"$(basename ${b%.*}).asc >& /dev/null; "+os.path.dirname(__file__)+"/asc_format_ccs.py "+temp_folder0+"$(basename ${b%.*}).asc "+temp_folder1+"$(basename ${b%.*}).asc; done"
				subprocess.Popen("{}; {}".format(cmd4, cmd5), shell=True, executable="/bin/bash").communicate()
		else:
			command = "for b in `ls "+out_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -crop_to_cutline -of GTiff $b "+temp_folder0+"$(basename ${b%.*}).tif; done"
			command1 = "for file in "+temp_folder0+"*.tif; do /usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -of AAIGrid $file "+temp_folder0+"$(basename ${file%.*}).asc; "+os.path.dirname(__file__)+"/asc_format_ccs.py "+temp_folder0+"$(basename ${file%.*}).asc "+temp_folder1+"$(basename ${file%.*}).asc; done"
			command2 = "cp /mnt/t/disk2/pconnect/CHRSData/userFile/temp/shapes/"+id+".* "+temp_folder1
			subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
			subprocess.Popen(command1, shell=True, executable="/bin/bash").communicate()
			subprocess.Popen(command2, shell=True, executable="/bin/bash").communicate()

	zip_name = out_file.split('_')[0]+"_"+currentDateTime
	#zip_name = dataset+"_"+currentDateTime
	shutil.make_archive(zip_name, format=compression, root_dir=temp_folder1)

elif file_type == 'Tif':
	if dataset == 'CDR':
		resolution = '0.25'
		if domain in ['0', '1']:
			command = "for b in `ls "+out_file+"`; do cp "+out_file+" "+temp_folder1+" >& /dev/null; done"
		else:
			command = "for b in `ls "+out_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -crop_to_cutline -of GTiff $b "+temp_folder1+"$(basename ${b%.*}).tif; done"
			command1 = "cp /mnt/t/disk2/pconnect/CHRSData/userFile/temp/shapes/"+id+".* "+temp_folder1
			subprocess.Popen(command1, shell=True, executable="/bin/bash").communicate()
	else:
		resolution = '0.04'
		if domain in ['0', '1']:
			command = "for b in `ls "+out_file+"`; do cp "+out_file+" "+temp_folder1+" >& /dev/null; done"
		else:
			command = "for b in `ls "+out_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -crop_to_cutline -of GTiff $b "+temp_folder1+"$(basename ${b%.*}).tif; done"
			command1 = "cp /mnt/t/disk2/pconnect/CHRSData/userFile/temp/shapes/"+id+".* "+temp_folder1
			subprocess.Popen(command1, shell=True, executable="/bin/bash").communicate()
	subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
	zip_name = out_file.split('_')[0]+"_"+currentDateTime
	shutil.make_archive(zip_name, format=compression, root_dir=temp_folder1)
else:
	command = "for b in `ls "+out_file+"`; do /usr/local/bin/gdal_translate -of netCDF -co FORMAT=NC4 "+out_file+" "+temp_folder1+"$(basename ${b%.*}).nc; done"
	command1 = "cp /mnt/t/disk2/pconnect/CHRSData/python/read_netcdf/read_netcdf.py "+temp_folder1
	subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
	zip_name = out_file.split('_')[0]+"_"+currentDateTime
	shutil.make_archive(zip_name, format=compression, root_dir=temp_folder1)

shutil.rmtree(temp_folder0)
shutil.rmtree(temp_folder1)