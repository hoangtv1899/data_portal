#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

from datetime import datetime
import os
import ogr
import sys
import math
import numpy as np
import glob
import multiprocessing
import itertools
from ShapeSelection import ShapeSelection

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
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -q -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of GTiff "+fileIn+" "+dest_file+" -co COMPRESS=LZW")

def ClipRasterShape(args):
	fileIn = args[0]
	outShapefile = args[1]
	resolution = args[2]
	p1 = args[3]
	dest_file = args[4]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -tr 0.25 0.25 -te "+p1+" -of GTiff "+fileIn+" "+dest_file)

dataset = sys.argv[1]
userIP = sys.argv[2]
currentDateTime = sys.argv[3]
input_string = sys.argv[4]

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
temp_folder1 = '../userFile/temp/199'+currentDateTime+'/'
temp_folder2 = '../userFile/temp/188'+currentDateTime+'/'

date_list = []
if dataset == 'CDR':
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
		base_path = '/mnt/t/disk3/CHRSdata/Persiann/'
		temp_folder0 = temp_folder2
	elif dataset == 'CCS':
		base_path = '/mnt/t/disk3/CHRSdata/Persiann_CCS/'
		temp_folder0 = temp_folder1
	#add hour to list from CCS and PERSIANN
	for i in hour_list:
		i_time = datetime.strptime(i, '%y%m%d%H')
		date_list.append(dataset+'_'+timestepH+i_time.strftime('%Y%m%d%H'))
else:	#shape and rectangle
	dataset = dataset[1:-1]
	br_dwn = dataset.split(' ')
	dataset1 = br_dwn[0]
	if dataset1 == 'CDR':
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
			ulx = str(math.ceil(float(ulx)/0.25)*0.25)
			uly = str(math.floor(float(uly)/0.25)*0.25)
			lrx = str(math.floor(float(lrx)/0.25)*0.25)
			lry = str(math.ceil(float(lry)/0.25)*0.25)
		elif br_dwn[1] == 'shp':
			shapefile = br_dwn[2]
			loc1 = br_dwn[3]
			loc2 = br_dwn[4]
			loc = [loc1, loc2]
			outShapefile = ShapeSelection(loc, shapefile, temp_folder0)
			shp_in = ogr.Open(outShapefile)
			shp_layer = shp_in.GetLayer()
			shp_extents = shp_layer.GetExtent()
			[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/0.25) *0.25 + [-0.25, 0.25, -0.25, 0.25]
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
			resolution = '0.25'
			temp_folder0 = temp_folder2
			base_path = '/mnt/t/disk3/CHRSdata/Persiann/'
		elif dataset1 == 'CCS':
			resolution = '0.04'
			temp_folder0 = temp_folder1
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
			ulx = str(math.ceil(float(ulx)/0.25)*0.25)
			uly = str(math.floor(float(uly)/0.25)*0.25)
			lrx = str(math.floor(float(lrx)/0.25)*0.25)
			lry = str(math.ceil(float(lry)/0.25)*0.25)
		elif br_dwn[1] == 'shp':
			shapefile = br_dwn[2]
			loc1 = br_dwn[3]
			loc2 = br_dwn[4]
			loc = [loc1, loc2]
			outShapefile = ShapeSelection(loc, shapefile, temp_folder0)
			shp_in = ogr.Open(outShapefile)
			shp_layer = shp_in.GetLayer()
			shp_extents = shp_layer.GetExtent()
			[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/0.25) *0.25 + [-0.25, 0.25, -0.25, 0.25]
			if ymin1 >= 60:
				sys.exit()
			elif ymax1 >= 60:
				ymax1 = 60
			p = [xmin1, ymin1, xmax1, ymax1]
			p1 = map(str, p)

file_list = []
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
pool = multiprocessing.Pool(processes = 4)
if dataset in ['CCS', 'CDR', 'PERSIANN']:
	os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+userIP+".tif'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate $b "+' '.join(sorted(file_list))+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+" 2>/dev/null")
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
		list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in file_list]
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, file_list, list_dest_file))
		if dataset1 == 'CCS':
			os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+userIP+".tif'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -overwrite -separate $b "+temp_folder0+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+" 2>/dev/null")
		else:
			os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+userIP+".tif'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate $b "+temp_folder0+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+" 2>/dev/null")
		print 'done'
	elif br_dwn[1] == 'shp':
		ShapeArray = itertools.repeat(outShapefile, len(file_list))
		ResArray = itertools.repeat(resolution, len(file_list))
		CoorArray = itertools.repeat(' '.join(p1), len(file_list))
		list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in file_list]
		pool.map(ClipRasterShape, itertools.izip(file_list, ShapeArray, ResArray, CoorArray,list_dest_file))
		if dataset1 == 'CCS':
			os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+userIP+".tif'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -overwrite -separate $b "+temp_folder0+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+" 2>/dev/null")
		else:
			os.system("b='"+temp_folder0+userIP+".vrt'; h='"+temp_folder0+userIP+".tif'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate $b "+temp_folder0+"*.tif; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py $b $h "+dataset1+" 2>/dev/null")
		print 'done'

