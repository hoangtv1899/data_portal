#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

from datetime import date, timedelta, datetime
import os
import sys
import glob
import subprocess
import math
import shutil
from osgeo import gdal
from ShapeSelection import ShapeSelection
import numpy as np

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
curr_str = sys.argv[4]
input_string = sys.argv[5]

temp_folder0 = '../userFile/temp/'+curr_str+'/'
temp_folder1 = '../userFile/temp/199'+curr_str+'/'
temp_folder2 = '../userFile/temp/188'+curr_str+'/'
temp_folder3 = '../userFile/temp/200'+curr_str+'/'

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

file_list = []
if dataset == 'CDR':
	timestepH = ''
	timestepD = ''
	timestepM = ''
	timestepY = ''
	base_path = '/mnt/t/disk3/CHRSdata/Persiann_CDR/'
	dataset1 = dataset
elif dataset in ['CCS', 'PERSIANN']:
	timestepH = '1h'
	timestepD = '1d'
	timestepM = '1m'
	timestepY = '1y'
	if dataset == 'PERSIANN':
		base_path = '/mnt/t/disk3/CHRSdata/Persiann/'
	elif dataset == 'CCS':
		base_path = '/mnt/t/disk3/CHRSdata/Persiann_CCS/'
	#add hour to list from CCS and PERSIANN
	for i in hour_list:
		i_time = datetime.strptime(i, '%y%m%d%H')
		file_list = file_list + glob.glob(base_path+'1hrly/'+dataset+'_'+timestepH+i_time.strftime('%Y%m%d%H')+'*.tif')
#		date_list.append(dataset+'_'+timestepH+i_time.strftime('%Y%m%d%H'))
	dataset1 = dataset
else:	#shape and rectangle
	br_dwn = dataset.split(' ')
	if br_dwn[0] == 'CDR':
		timestepH = ''
		timestepD = ''
		timestepM = ''
		timestepY = ''
		base_path = '/mnt/t/disk3/CHRSdata/Persiann_CDR/'
		resolution = '0.25'
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
			# Save extent to a new Shapefile
			outShapefile = ShapeSelection(loc, shapefile, '/mnt/t/disk2/pconnect/CHRSData/userFile/'+userIP+'/tempShapeAcc/')
	elif br_dwn[0] in ['CCS', 'PERSIANN']:
		timestepH = '1h'
		timestepD = '1d'
		timestepM = '1m'
		timestepY = '1y'
		if br_dwn[0] == 'PERSIANN':
			base_path = '/mnt/t/disk3/CHRSdata/Persiann/'
			resolution = '0.25'
		elif br_dwn[0] == 'CCS':
			base_path = '/mnt/t/disk3/CHRSdata/Persiann_CCS/'
			resolution = '0.04'
		#add hour to list from CCS and PERSIANN
		for i in hour_list:
			i_time = datetime.strptime(i, '%y%m%d%H')
			file_list = file_list + glob.glob(base_path+'1hrly/'+br_dwn[0]+'_'+timestepH+i_time.strftime('%Y%m%d%H')+'*.tif')
#			date_list.append(br_dwn[0]+'_'+timestepH+i_time.strftime('%Y%m%d%H'))
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
			# Save extent to a new Shapefile
			outShapefile = ShapeSelection(loc, shapefile, '/mnt/t/disk2/pconnect/CHRSData/userFile/'+userIP+'/tempShapeAcc/')
	dataset1 = br_dwn[0]

#date_list = []
for j in day_list:
	j_time = datetime.strptime(j, '%y%m%d')
	file_list = file_list+glob.glob(base_path+'daily/'+dataset1+'_'+timestepD+j_time.strftime('%Y%m%d')+'*.tif')
#	date_list.append(dataset1+'_'+timestepD+j_time.strftime('%Y%m%d'))

for k in month_list:
	k_time = datetime.strptime(k, '%y%m')
	file_list = file_list+glob.glob(base_path+'monthly/'+dataset1+'_'+timestepM+k_time.strftime('%Y%m')+'*.tif')
#	date_list.append(dataset1+'_'+timestepM+k_time.strftime('%Y%m'))

for l in year_list:
	l_time = datetime.strptime(l, '%y')
	file_list = file_list+glob.glob(base_path+'yearly/'+dataset1+'_'+timestepY+l_time.strftime('%Y')+'*.tif')
#	date_list.append(dataset1+'_'+timestepY+l_time.strftime('%Y'))

#file_list = []
#for root, dirs, files in os.walk(base_path):
#	for file in files:
#		if any(dl in file for dl in date_list) and os.path.splitext(file)[-1] == '.tif':
#			file_list.append(os.path.join(root, file))

#print file_list
#DO THE ACCUMULATION
if dataset in ['CDR', 'CCS', 'PERSIANN']:
	cmd = "b='"+temp_folder0+userIP+".vrt'; k='"+temp_folder0+userIP+".tif'; h='"+out_file+"'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -separate $b "+' '.join(sorted(file_list))+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $k "+dataset+"; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -of GTiff -co COMPRESS=LZW $k $h 2>/dev/null"
	subprocess.call(cmd, shell=True, executable="/bin/bash" )
	print 'done'
else:
	if br_dwn[1] == 'rec':
		if float(ulx) <= float(lrx):
			uly = '60' if float(uly) > 60 else uly
			lry = '-60' if float(lry) < -60 else lry
			cmd0 = "for b in "+' '.join(sorted(file_list))+"; do echo 'processing '$b; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of GTiff $b "+temp_folder1+"$(basename ${b%.*}).tif -co COMPRESS=LZW; done"
			subprocess.call(cmd0, shell=True, executable="/bin/bash" )
			cmd = "b='"+temp_folder0+userIP+".vrt'; k='"+temp_folder0+userIP+".tif'; h='"+out_file+"'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -separate $b "+temp_folder1+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $k "+br_dwn[0]+"; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -of GTiff -co COMPRESS=LZW $k $h; rm $b $k 2>/dev/null"
			subprocess.call(cmd, shell=True, executable="/bin/bash" )
			print 'done'
		else:
			uly = '60' if float(uly) > 60 else uly
			lry = '-60' if float(lry) < -60 else lry
			cmd1 = "for b in "+' '.join(sorted(file_list))+"; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -projwin "+ulx+" "+uly+" 180 "+lry+" -of GTiff $b "+temp_folder1+"$(basename ${b%.*}).tif -co COMPRESS=LZW >& /dev/null; done"
			cmd2 = "for b in "+' '.join(sorted(file_list))+"; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -projwin -180 "+uly+" "+lrx+" "+lry+" -of GTiff $b "+temp_folder2+"$(basename ${b%.*}).tif -co COMPRESS=LZW >& /dev/null; done"
			cmd3 = "for b in "+temp_folder1+"*.tif; do /usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7 /root/gdal-1.11.2/swig/python/scripts/gdal_merge.py -o "+temp_folder3+"$(basename ${b%.*}).tif $b "+temp_folder2+"$(basename ${b%.*}).tif -co COMPRESS=LZW -a_nodata -99 >& /dev/null; done"
			subprocess.Popen("{}; {}; {}".format(cmd1, cmd2, cmd3), shell=True, executable="/bin/bash").communicate()
			shutil.rmtree(temp_folder1)
			shutil.rmtree(temp_folder2)
			cmd = "b='"+temp_folder0+userIP+".vrt'; k='"+temp_folder0+userIP+".tif'; h='"+out_file+"'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -separate $b "+temp_folder0+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $k; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -of GTiff -co COMPRESS=LZW $k $h; rm $b $k 2>/dev/null"
			subprocess.call(cmd, shell=True, executable="/bin/bash" )
			print 'done'
	elif br_dwn[1] == 'shp':
		cmd0 = "for b in "+' '.join(sorted(file_list))+"; do /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -of GTiff $b "+temp_folder1+"$(basename ${b%.*}).tif -co COMPRESS=LZW; done"
		subprocess.call(cmd0, shell=True, executable="/bin/bash" )
		cmd = "b='"+temp_folder0+userIP+".vrt'; k='"+temp_folder0+userIP+".tif'; h='"+out_file+"'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -separate $b "+temp_folder1+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $k "+br_dwn[0]+"; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -of GTiff -co COMPRESS=LZW $k $h; rm $b $k 2>/dev/null"
		subprocess.call(cmd, shell=True, executable="/bin/bash" )
		print 'done'

im = gdal.Open(out_file)
array = im.ReadAsArray()
#array = np.ma.masked_where(array == -99, array) #this will show median as nan
array = array[array != -99]
print "max: %.2f" % array.max()
print "min: %.2f" % array.min()
print "mean: %.2f" % array.mean()
print "median: %.2f" % np.median(array)