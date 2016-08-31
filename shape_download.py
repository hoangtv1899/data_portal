#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import subprocess
import os
import sys
import glob
import shutil
from osgeo import ogr, gdal
from datetime import datetime, timedelta
from dateutil import rrule
import calendar
import numpy as np

#inputs
curr_str = sys.argv[1]
id = sys.argv[2]
if '_' in id:
	id = id.replace('_', ' ')
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

#create temp folder
# if not os.path.exists('../userFile/temp/'):
    # os.makedirs('../userFile/temp/')
# if not os.path.exists('../userFile/temp/shapes/'):
    # os.makedirs('../userFile/temp/shapes/')

tmp_f = '../userFile/temp/'+curr_str+'/'
tmp_f1 = '../userFile/temp/199'+curr_str+'/'

#check dataset
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
		resolution = '0.04'
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
	else:
		resolution = '0.25'
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
	lat = 60
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"

#check shapefile

shp_name = (shapefile.split('/'))[-1]
if shp_name == 'country_fusion.shp':
	prop = 'FIPS_CNTRY'
	filter = '{} = \'{}\''.format(prop, id)
	prior = "/usr/local/epd-7.3-2-rh5-x86_64/bin/"
elif shp_name == 'pol_divisions.shp':
	prop = 'NAM'
	filter = '{} = \'{}\''.format(prop, id)
	prior = "/usr/local/bin/"
elif shp_name in ['basins_l1_new.shp', 'basins_l2_new.shp', 'basins_l3_new.shp', 'basins_l4_new.shp']:
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

# # Remove output shapefile if it already exists
# try:
    # os.remove(outShapefile)
# except OSError:
    # pass

command2 = prior+"ogr2ogr -f \"ESRI Shapefile\" -where \\ \""+filter+"\" "+outShapefile+" "+shapefile

# print command1
subprocess.Popen(command2, shell=True).communicate()
#get shapefile extents
vector = ogr.Open(outShapefile)
layer = vector.GetLayer()
shp_extents = layer.GetExtent()
[xmin1, xmax1, ymin1, ymax1] = np.floor(shp_extents) + np.floor((shp_extents - np.floor(shp_extents))/0.25) *0.25
p = [xmin1, ymin1, xmax1, ymax1]
p1 = map(str, p)

[xmin2, xmax2, ymin2, ymax2] = np.floor(shp_extents) + np.floor((shp_extents - np.floor(shp_extents))/0.04) *0.04
p_ = [xmin2, ymin2, xmax2, ymax2]
p2 = map(str, p_)

#clipping raster
if file_type == 'Tif':
	if dataset == 'CDR':
		command = "for b in `ls "+path_to_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+' '.join(p1)+" -of GTiff -ot Float64 $b "+tmp_f+"$(basename ${b%.*}).tif -co COMPRESS=LZW; "+os.path.dirname(os.path.abspath(__file__))+"/round_pixel_value.py "+tmp_f+"$(basename ${b%.*}).tif "+tmp_f1+"$(basename ${b%.*}).tif; done"
		print command
	elif dataset == 'CCS':
		command = "for b in `ls "+path_to_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+' '.join(p2)+" -of GTiff -ot Int32 $b "+tmp_f1+"$(basename ${b%.*}).tif -co COMPRESS=LZW; done"
 	else:
		command = "for b in `ls "+path_to_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+' '.join(p1)+" -of GTiff -ot Float64 $b "+tmp_f+"$(basename ${b%.*}).tif -co COMPRESS=LZW; "+os.path.dirname(os.path.abspath(__file__))+"/round_pixel_value.py "+tmp_f+"$(basename ${b%.*}).tif "+tmp_f1+"$(basename ${b%.*}).tif; done"
	subprocess.Popen(command, shell=True).communicate()
elif file_type == 'ArcGrid':
	if dataset == 'CDR':
		command = "for b in `ls "+path_to_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+' '.join(p1)+" -of GTiff -ot Float64 $b "+tmp_f+"$(basename ${b%.*}).tif; "+os.path.dirname(os.path.abspath(__file__))+"/asc_format.py "+tmp_f+"$(basename ${b%.*}).tif "+tmp_f1+"$(basename ${b%.*}).asc; done"
	elif dataset == 'CCS':
		command = "for b in `ls "+path_to_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+' '.join(p2)+" -of GTiff -ot Float64 $b "+tmp_f+"$(basename ${b%.*}).tif; "+os.path.dirname(os.path.abspath(__file__))+"/asc_format_ccs.py "+tmp_f+"$(basename ${b%.*}).tif "+tmp_f1+"$(basename ${b%.*}).asc; done"
		command1 = ""
	else:
		command = "for b in `ls "+path_to_file+"`; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr "+resolution+" "+resolution+" -te "+' '.join(p1)+" -of GTiff -ot Float64 $b "+tmp_f+"$(basename ${b%.*}).tif; "+os.path.dirname(os.path.abspath(__file__))+"/asc_format_ccs.py "+tmp_f+"$(basename ${b%.*}).tif "+tmp_f1+"$(basename ${b%.*}).asc; done"
		
	subprocess.Popen(command, shell=True, executable="/bin/bash").communicate()
	#subprocess.Popen(command1, shell=True, executable="/bin/bash").communicate()

for file in glob.iglob(outShapefile.split(".")[0]+".*"):
	shutil.copy(file, tmp_f1)


prjcmd = "cp /mnt/t/disk2/pconnect/CHRSData/projection/US.prj "+tmp_f1+id+".prj"
subprocess.Popen(prjcmd, shell=True, executable="/bin/bash").communicate()
shutil.make_archive(outfile, format=compression, root_dir=tmp_f1)
