#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import sys
import os
import glob
import numpy as np
from datetime import datetime
from collections import OrderedDict
import multiprocessing as mp
from contextlib import closing
import itertools
import ctypes
from osgeo import gdal, ogr, osr
import json
import warnings
from ValidationFunction import ValidationFunction
from PlotMap2 import PlotMap2
from ShapeSelection import ShapeSelection

#turn off warnings
warnings.filterwarnings("ignore")

def ClipRaster(args):
	ulx = args[0]
	uly = args[1]
	lrx = args[2]
	lry = args[3]
	fileIn = args[4]
	dest_file = args[5]
	dest_vrt = args[6]
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of GTiff "+fileIn+" "+dest_file+" -co COMPRESS=LZW; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+dest_vrt+" "+dest_file)

def ClipRasterShape(args):
	fileIn = args[0]
	outShapefile = args[1]
	p1 = args[2]
	dest_file = args[3]
	dest_vrt = args[4]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -te "+p1+" -of GTiff "+fileIn+" "+dest_file+"; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+dest_vrt+" "+dest_file)

def SpaTempRes(dataset, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2):
	if dataset == 'CDR':
		start1 = '1983010100'
		TempResSet = ['customized', 'daily', 'monthly', 'yearly']
		if time_step == 'customized':
			if domain =='wholemap':
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" "+dataset+" "+userIP+" "+curr_str)
				bpath = temp_folder0+userIP+'.tif'
			elif domain.split(' ') == 'rec':
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" '\""+dataset+" "+domain+"\"' "+userIP+" "+curr_str)
				#bpath = temp_folder0+userIP+'.vrt'
				bpath = temp_folder0+userIP+'.tif'
			else:
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" '\""+dataset+" shp "+domain+"\"' "+userIP+" "+curr_str)
				#bpath = temp_folder0+userIP+'.vrt'
				bpath = temp_folder0+userIP+'.tif'
		else:
			bpath = '/mnt/t/disk3/CHRSdata/Persiann_CDR/'+time_step+'/'
	elif dataset == 'CCS':
		start1 = '2003010100'
		TempResSet = ['customized', '1hrly', '3hrly', '6hrly', 'daily', 'monthly', 'yearly']
		if time_step == 'customized':
			if domain =='wholemap':
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" "+dataset+" "+userIP+" "+curr_str)
				bpath = temp_folder1+userIP+'.tif'
			elif domain.split(' ') == 'rec':
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" '\""+dataset+" "+domain+"\"' "+userIP+" "+curr_str)
				#bpath = temp_folder1+userIP+'.vrt'
				bpath = temp_folder1+userIP+'.tif'
			else:
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" '\""+dataset+" shp "+domain+"\"' "+userIP+" "+curr_str)
				#bpath = temp_folder1+userIP+'.vrt'
				bpath = temp_folder1+userIP+'.tif'
		else:
			bpath = '/mnt/t/disk3/CHRSdata/Persiann_CCS/'+time_step+'/'
	elif dataset == 'PERSIANN':
		start1 = '2000030100'
		TempResSet = ['customized', '1hrly', '3hrly', '6hrly', 'daily', 'monthly', 'yearly']
		if time_step == 'customized':
			if domain =='wholemap':
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" "+dataset+" "+userIP+" "+curr_str)
				bpath = temp_folder2+userIP+'.tif'
			elif domain.split(' ') == 'rec':
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" '\""+dataset+" "+domain+"\"' "+userIP+" "+curr_str)
				#bpath = temp_folder2+userIP+'.vrt'
				bpath = temp_folder2+userIP+'.tif'
			else:
				os.system("../python/comparision/do_acc1.sh "+start_date+" "+end_date+" '\""+dataset+" shp "+domain+"\"' "+userIP+" "+curr_str)
				#bpath = temp_folder2+userIP+'.vrt'
				bpath = temp_folder2+userIP+'.tif'
		else:
			bpath = '/mnt/t/disk3/CHRSdata/Persiann/'+time_step+'/'
	return TempResSet, bpath, start1

curr_str = sys.argv[1]
userIP = sys.argv[2]
domain = sys.argv[3]
time_step = sys.argv[4]
start_date = sys.argv[5]

if (time_step != 'customized'):
	end_date = '0'
	DataRef = sys.argv[6]
	Data1 = sys.argv[7]
	try:
		Data2 = sys.argv[8]
	except:
		Data2 = ''
else:
	end_date = sys.argv[6]
	DataRef = sys.argv[7]
	Data1 = sys.argv[8]
	try:
		Data2 = sys.argv[9]
	except:
		Data2 = ''

#temp_folder0
temp_folder = '../userFile/temp/200'+curr_str+'/'
temp_folder0 = '../userFile/temp/'+curr_str+'/'
temp_folder1 = '../userFile/temp/199'+curr_str+'/'
temp_folder2 = '../userFile/temp/188'+curr_str+'/'
result_folder = '../userFile/'+userIP+'/comparison/'

#Spatial and temporal resolution of dataset
if Data2:
	[RefSet, RefPath, RefStart] = SpaTempRes(DataRef, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
	[FileSet1, FilePath1, FileStart1] = SpaTempRes(Data1, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
	[FileSet2, FilePath2, FileStart2] = SpaTempRes(Data2, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
else:
	Data2 = Data1
	[RefSet, RefPath, RefStart] = SpaTempRes(DataRef, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
	[FileSet1, FilePath1, FileStart1] = SpaTempRes(Data1, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
	[FileSet2, FilePath2, FileStart2] = [FileSet1, FilePath1, FileStart1]

if (len(start_date) < 10):
	start_date1 = start_date+'0'*(10-len(start_date))
	end_date1 = end_date+'0'*(10-len(end_date)-2)+'23'
else:
	start_date1 = start_date
	end_date1 = end_date

arr_len = 3
#compare time step
if time_step not in RefSet:
	print time_step+' is not in the dataset of '+DataRef+'. Skipping '+DataRef+'.'
	arr_len -= 1
	DataRef = Data1
	RefPath = FilePath1
	RefStart = FileStart1
elif time_step not in FileSet1:
	print time_step+' is not in the dataset of '+Data1+'. Skipping '+Data1+'.'
	arr_len -= 1
	Data1 = DataRef
	FilePath1 = RefPath
	FileStart1 = RefStart
elif time_step not in FileSet2:
	print time_step+' is not in the dataset of '+Data2+'. Skipping '+Data2+'.'
	arr_len -= 1
	Data2 = DataRef
	FilePath2 = RefPath
	FileStart2 = RefStart
	
#compare end date
if time_step == 'customized':
	if (int(end_date1) < int(RefStart)):
		print 'start date is smaller than time range of '+DataRef+'. Skipping '+DataRef+'.'
		arr_len -= 1
		DataRef = Data1
		RefPath = FilePath1
		if ((int(end_date1) < int(FileStart1)) or (int(end_date1) < int(FileStart2))):
			print 'error:Not enough dataset'
			sys.exit()
	elif int(end_date1) < int(FileStart1):
		print 'start date is smaller than time range of '+Data1+'. Skipping '+Data1+'.'
		arr_len -= 1
		Data1 = DataRef
		FilePath1 = RefPath
		if ((int(end_date1) < int(RefStart)) or (int(end_date1) < int(FileStart2))):
			print 'error:Not enough dataset'
			sys.exit()
	elif int(end_date1) < int(FileStart2):
		print 'start date is smaller than time range of '+Data2+'. Skipping '+Data2+'.'
		arr_len -= 1
		Data2 = DataRef
		FilePath2 = RefPath
		if ((int(end_date1) < int(RefStart)) or (int(end_date1) < int(FileStart1))):
			print 'error:Not enough dataset'
			sys.exit()

#compare start date
if (int(start_date1) < int(RefStart)):
	print 'start date is smaller than time range of '+DataRef+'. Skipping '+DataRef+'.'
	arr_len -= 1
	DataRef = Data1
	RefPath = FilePath1
	if ((int(start_date1) < int(FileStart1)) or (int(start_date1) < int(FileStart2))):
		print 'error:Not enough dataset'
		sys.exit()
elif int(start_date1) < int(FileStart1):
	print 'start date is smaller than time range of '+Data1+'. Skipping '+Data1+'.'
	arr_len -= 1
	Data1 = DataRef
	FilePath1 = RefPath
	if ((int(start_date1) < int(RefStart)) or (int(start_date1) < int(FileStart2))):
		print 'error:Not enough dataset'
		sys.exit()
elif int(start_date1) < int(FileStart2):
	print 'start date is smaller than time range of '+Data2+'. Skipping '+Data2+'.'
	arr_len -= 1
	Data2 = DataRef
	FilePath2 = RefPath
	if ((int(start_date1) < int(RefStart)) or (int(start_date1) < int(FileStart1))):
		print 'error:Not enough dataset'
		sys.exit()

print arr_len
if (arr_len < 2):
	print 'error:Not enough dataset'
	sys.exit()

pool = mp.Pool(processes = 16)
domain_split = domain.split(' ')
if (arr_len == 3):
	if domain_split[0] == 'wholemap':
		if time_step != 'customized':
			#list file from terminal
			RefFile = glob.glob(RefPath+'*'+start_date+'*.tif')[0]
			File1 = glob.glob(FilePath1+'*'+start_date+'*.tif')[0]
			File2 = glob.glob(FilePath2+'*'+start_date+'*.tif')[0]
			Refvrt = temp_folder0+'Ref.vrt'
			File1vrt = temp_folder1+'file1.vrt'
			File2vrt = temp_folder2+'file2.vrt'
			os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+Refvrt+" "+RefFile)
			os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File1vrt+" "+File1)
			os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File2vrt+" "+File2)
		else:
			Refvrt = RefPath
			File1vrt = FilePath1
			File2vrt = FilePath2
			time_step = 'monthly'
		extend = [-180, 180, 60, -60]
	elif domain_split[0] == 'rec':
		RawExtend = [float(x) for x in domain_split[1:]]
		extend = [RawExtend[0], RawExtend[2], RawExtend[1], RawExtend[3]]
		if time_step != 'customized':
			#list file from terminal
			RefFile = glob.glob(RefPath+'*'+start_date+'*.tif')[0]
			File1 = glob.glob(FilePath1+'*'+start_date+'*.tif')[0]
			File2 = glob.glob(FilePath2+'*'+start_date+'*.tif')[0]
			Refvrt = temp_folder0+'Ref.vrt'
			File1vrt = temp_folder1+'file1.vrt'
			File2vrt = temp_folder2+'file2.vrt'
			#steps to clip rectangle
			uly_arr = [str(extend[2])]*3
			ulx_arr = [str(extend[0])]*3
			lry_arr = [str(extend[3])]*3
			lrx_arr = [str(extend[1])]*3
			RefDestFile = temp_folder0+os.path.splitext(os.path.basename(RefFile))[0]+'.tif'
			DestFile1 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'.tif'
			DestFile2 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'.tif'
			pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, [RefFile, File1, File2], [RefDestFile, DestFile1, DestFile2], [Refvrt, File1vrt, File2vrt]))
		else:
			Refvrt = RefPath
			File1vrt = FilePath1
			File2vrt = FilePath2
			time_step = 'monthly'
	else:
		if time_step != 'customized':
			#list file from terminal
			RefFile = glob.glob(RefPath+'*'+start_date+'*.tif')[0]
			File1 = glob.glob(FilePath1+'*'+start_date+'*.tif')[0]
			File2 = glob.glob(FilePath2+'*'+start_date+'*.tif')[0]
			Refvrt = temp_folder0+'Ref.vrt'
			File1vrt = temp_folder1+'file1.vrt'
			File2vrt = temp_folder2+'file2.vrt'
			shape = domain_split[0]
			extend = domain_split[1:]
			shape_in = ShapeSelection(extend, shape, temp_folder0)
			shp_in = ogr.Open(shape_in)
			shp_layer = shp_in.GetLayer()
			shp_extents = shp_layer.GetExtent()
			[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/0.25) *0.25 + [-0.25, 0.25, -0.25, 0.25]
			if ymin1 >= 60:
				sys.exit()
			elif ymax1 >= 60:
				ymax1 = 60
			p = [xmin1, ymin1, xmax1, ymax1]
			extend = [xmin1, xmax1, ymax1, ymin1]
			p1 = map(str, p)
			#steps to clip shape
			RefDestFile = temp_folder0+os.path.splitext(os.path.basename(RefFile))[0]+'.tif'
			DestFile1 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'.tif'
			DestFile2 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'.tif'
			ShapeArray = [shape_in]*3
			CoorArray = [' '.join(p1)]*3
			pool.map(ClipRasterShape, itertools.izip([RefFile, File1, File2], ShapeArray, CoorArray,[RefDestFile, DestFile1, DestFile2], [Refvrt, File1vrt, File2vrt]))
		else:
			Refvrt = RefPath
			File1vrt = FilePath1
			File2vrt = FilePath2
			time_step = 'monthly'
			shape_in = glob.glob(temp_folder0+'*.shp')[0]
			shp_in = ogr.Open(shape_in)
			shp_layer = shp_in.GetLayer()
			shp_extents = shp_layer.GetExtent()
			[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/0.25) *0.25 + [-0.25, 0.25, -0.25, 0.25]
			if ymin1 >= 60:
				sys.exit()
			elif ymax1 >= 60:
				ymax1 = 60
			p = [xmin1, ymin1, xmax1, ymax1]
			extend = [xmin1, xmax1, ymax1, ymin1]
	ds = gdal.Open(Refvrt)
	Projection = osr.SpatialReference()
	Projection.ImportFromWkt(ds.GetProjectionRef())
	ref_arr = gdal.Open(Refvrt).ReadAsArray()
	obs_arr1 = gdal.Open(File1vrt).ReadAsArray()
	obs_arr2 = gdal.Open(File2vrt).ReadAsArray()
	#Masking data
	ref_arr_mask = np.ma.masked_where(ref_arr==-99, ref_arr)
	obs_arr1_mask = np.ma.masked_where(obs_arr1==-99, obs_arr1)
	obs_arr2_mask = np.ma.masked_where(obs_arr2==-99, obs_arr2)
	[nr, nc] = ref_arr_mask.shape
	#get results from ValidationFunction
	RefStat = OrderedDict()
	Obs1Stat = OrderedDict()
	Obs2Stat = OrderedDict()
	RefStat['Number of points']=nr*nc; RefStat['Number of points with rain']=np.ma.count(ref_arr_mask); RefStat['Mean rain rate']=round(np.ma.mean(ref_arr_mask),3); RefStat['Max rain rate']=round(np.ma.max(ref_arr_mask),3)
	Obs1Stat['Number of points']=nr*nc; Obs1Stat['Number of points with rain']=np.ma.count(obs_arr1_mask); Obs1Stat['Mean rain rate']=round(np.ma.mean(obs_arr1_mask),3); Obs1Stat['Max rain rate']=round(np.ma.max(obs_arr1_mask),3)
	Obs2Stat['Number of points']=nr*nc; Obs2Stat['Number of points with rain']=np.ma.count(obs_arr2_mask); Obs2Stat['Mean rain rate']=round(np.ma.mean(obs_arr2_mask),3); Obs2Stat['Max rain rate']=round(np.ma.max(obs_arr2_mask),3)
	result_1 = ValidationFunction(ref_arr_mask, obs_arr1_mask)
	result_2 = ValidationFunction(ref_arr_mask, obs_arr2_mask)
	result_3 = ValidationFunction(obs_arr1_mask, obs_arr2_mask)
	#print results
	print 'D0:'+','.join([str(x1) for x1 in RefStat.values()+result_1.values()])
	print 'D1:'+','.join([str(x1) for x1 in Obs1Stat.values()+result_2.values()])
	print 'D2:'+','.join([str(x1) for x1 in Obs2Stat.values()+result_3.values()])
	
else:
	if domain_split[0] == 'wholemap':
		extend = [-180, 180, 60, -60]
		if time_step != 'customized':
			#list file from terminal
			File1 = glob.glob(FilePath1+'*'+start_date+'*.tif')[0]
			File2 = glob.glob(FilePath2+'*'+start_date+'*.tif')[0]
			File1vrt = temp_folder1+'file1.vrt'
			File2vrt = temp_folder2+'file2.vrt'
			os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File1vrt+" "+File1)
			os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File2vrt+" "+File2)
		else:
			File1vrt = FilePath1
			File2vrt = FilePath2
			time_step = 'monthly'
	elif domain_split[0] == 'rec':
		RawExtend = [float(x) for x in domain_split[1:]]
		extend = [RawExtend[0], RawExtend[2], RawExtend[1], RawExtend[3]]
		if time_step != 'customized':
			#list file from terminal
			File1 = glob.glob(FilePath1+'*'+start_date+'*.tif')[0]
			File2 = glob.glob(FilePath2+'*'+start_date+'*.tif')[0]
			File1vrt = temp_folder1+'file1.vrt'
			File2vrt = temp_folder2+'file2.vrt'
			#steps to clip rectangle
			uly_arr = [str(extend[2])]*2
			ulx_arr = [str(extend[0])]*2
			lry_arr = [str(extend[3])]*2
			lrx_arr = [str(extend[1])]*2
			DestFile1 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'.tif'
			DestFile2 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'.tif'
			pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, [File1, File2], [DestFile1, DestFile2], [File1vrt, File2vrt]))
		else:
			File1vrt = FilePath1
			File2vrt = FilePath2
			time_step = 'monthly'
	else:
		if time_step != 'customized':
			#list file from terminal
			File1 = glob.glob(FilePath1+'*'+start_date+'*.tif')[0]
			File2 = glob.glob(FilePath2+'*'+start_date+'*.tif')[0]
			File1vrt = temp_folder1+'file1.vrt'
			File2vrt = temp_folder2+'file2.vrt'
			shape = domain_split[0]
			extend = domain_split[1:]
			shape_in = ShapeSelection(extend, shape, temp_folder0)
			shp_in = ogr.Open(shape_in)
			shp_layer = shp_in.GetLayer()
			shp_extents = shp_layer.GetExtent()
			[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/0.25) *0.25 + [-0.25, 0.25, -0.25, 0.25]
			if ymin1 >= 60:
				sys.exit()
			elif ymax1 >= 60:
				ymax1 = 60
			p = [xmin1, ymin1, xmax1, ymax1]
			extend = [xmin1, xmax1, ymax1, ymin1]
			p1 = map(str, p)
			#steps to clip shape
			DestFile1 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'.tif'
			DestFile2 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'.tif'
			ShapeArray = [shape_in]*2
			CoorArray = [' '.join(p1)]*2
			pool.map(ClipRasterShape, itertools.izip([File1, File2], ShapeArray, CoorArray,[DestFile1, DestFile2], [File1vrt, File2vrt]))
		else:
			File1vrt = FilePath1
			File2vrt = FilePath2
			time_step = 'monthly'
			shape_in = glob.glob(temp_folder0+'*.shp')[0]
			shp_in = ogr.Open(shape_in)
			shp_layer = shp_in.GetLayer()
			shp_extents = shp_layer.GetExtent()
			[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/0.25) *0.25 + [-0.25, 0.25, -0.25, 0.25]
			if ymin1 >= 60:
				sys.exit()
			elif ymax1 >= 60:
				ymax1 = 60
			p = [xmin1, ymin1, xmax1, ymax1]
			extend = [xmin1, xmax1, ymax1, ymin1]
	ds = gdal.Open(File1vrt)
	Projection = osr.SpatialReference()
	Projection.ImportFromWkt(ds.GetProjectionRef())
	obs_arr1 = gdal.Open(File1vrt).ReadAsArray()
	obs_arr2 = gdal.Open(File2vrt).ReadAsArray()
	#Masking data
	obs_arr1_mask = np.ma.masked_where(obs_arr1==-99, obs_arr1)
	obs_arr2_mask = np.ma.masked_where(obs_arr2==-99, obs_arr2)
	[nr, nc] = obs_arr1_mask.shape
	#get results from ValidationFunction
	Obs1Stat = OrderedDict()
	Obs2Stat = OrderedDict()
	Obs1Stat['Number of points']=nr*nc; Obs1Stat['Number of points with rain']=np.ma.count(obs_arr1_mask); Obs1Stat['Mean rain rate']=round(np.ma.mean(obs_arr1_mask),3); Obs1Stat['Max rain rate']=round(np.ma.max(obs_arr1_mask),3)
	Obs2Stat['Number of points']=nr*nc; Obs2Stat['Number of points with rain']=np.ma.count(obs_arr2_mask); Obs2Stat['Mean rain rate']=round(np.ma.mean(obs_arr2_mask),3); Obs2Stat['Max rain rate']=round(np.ma.max(obs_arr2_mask),3)
	result_1 = ValidationFunction(obs_arr1_mask, obs_arr2_mask)
	#print results
	print 'D0:'+','.join([str(x1) for x1 in Obs1Stat.values()+result_1.values()])
	print 'D1:'+','.join([str(x1) for x1 in Obs2Stat.values()])
	result_2 = np.array([])

#plot result images
driver = gdal.GetDriverByName('GTiff')
if len(result_2) != 0:
	PlotMap2(ref_arr_mask, DataRef, obs_arr1_mask, Data1, time_step, temp_folder, obs_arr2_mask, Data2)
	#export to rasters
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -of GTiff -ot Int16 -co COMPRESS=LZW "+Refvrt+" "+temp_folder+"Ref.tif")
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -of GTiff -ot Int16 -co COMPRESS=LZW "+File1vrt+" "+temp_folder+"File1.tif")
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -of GTiff -ot Int16 -co COMPRESS=LZW "+File2vrt+" "+temp_folder+"File2.tif")
	Diff1 = obs_arr1_mask-ref_arr_mask
	Diff1 = Diff1.filled(-99)
	Diff1name = temp_folder+"Diff1.tif"
	Diff1_raster = driver.Create(Diff1name, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Int16, ['COMPRESS=LZW'],)
	Diff1_raster.SetGeoTransform(ds.GetGeoTransform())
	Diff1_raster.SetProjection(Projection.ExportToWkt())
	Diff1_raster.GetRasterBand(1).WriteArray(Diff1)
	Diff1_raster.GetRasterBand(1).SetNoDataValue(-99)
	Diff1_raster.FlushCache()
	Diff2 = obs_arr2_mask-ref_arr_mask
	Diff2 = Diff2.filled(-99)
	Diff2name = temp_folder+"Diff2.tif"
	Diff2_raster = driver.Create(Diff2name, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Int16, ['COMPRESS=LZW'],)
	Diff2_raster.SetGeoTransform(ds.GetGeoTransform())
	Diff2_raster.SetProjection(Projection.ExportToWkt())
	Diff2_raster.GetRasterBand(1).WriteArray(Diff2)
	Diff2_raster.GetRasterBand(1).SetNoDataValue(-99)
	Diff2_raster.FlushCache()
	Diff3 = obs_arr2_mask-obs_arr1_mask
	Diff3 = Diff3.filled(-99)
	Diff3name = temp_folder+"Diff3.tif"
	Diff3_raster = driver.Create(Diff3name, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Int16, ['COMPRESS=LZW'],)
	Diff3_raster.SetGeoTransform(ds.GetGeoTransform())
	Diff3_raster.SetProjection(Projection.ExportToWkt())
	Diff3_raster.GetRasterBand(1).WriteArray(Diff3)
	Diff3_raster.GetRasterBand(1).SetNoDataValue(-99)
	Diff3_raster.FlushCache()
	os.system('cp '+temp_folder+'/* '+result_folder)
else:
	PlotMap2(obs_arr2_mask, Data2, obs_arr1_mask, Data1, time_step, temp_folder)
	#export to rasters
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -of GTiff -ot Int16 -co COMPRESS=LZW "+File1vrt+" "+temp_folder+"File1.tif")
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -of GTiff -ot Int16 -co COMPRESS=LZW "+File2vrt+" "+temp_folder+"File2.tif")
	Diff1 = obs_arr2_mask-obs_arr1_mask
	Diff1 = Diff1.filled(-99)
	Diff1name = temp_folder+"Diff3.tif"
	Diff1_raster = driver.Create(Diff1name, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Int16, ['COMPRESS=LZW'],)
	Diff1_raster.SetGeoTransform(ds.GetGeoTransform())
	Diff1_raster.SetProjection(Projection.ExportToWkt())
	Diff1_raster.GetRasterBand(1).WriteArray(Diff1)
	Diff1_raster.GetRasterBand(1).SetNoDataValue(-99)
	Diff1_raster.FlushCache()
	os.system('cp '+temp_folder+'/* '+result_folder)
