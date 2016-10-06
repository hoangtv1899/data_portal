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

def AccPath(dataset):
	if dataset == 'PERSIANN':
		PathAcc = '/mnt/t/disk3/CHRSdata/Persiann/'
	else:
		PathAcc = '/mnt/t/disk3/CHRSdata/Persiann'+'_'+dataset+'/'
	return PathAcc

def ClipRasterPart(args):
	ulx = args[0]
	uly = args[1]
	lrx = args[2]
	lry = args[3]
	fileIn = args[4]
	dest_file = args[5]
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of GTiff "+fileIn+" "+dest_file+" -co COMPRESS=LZW")	

def EditRaster(args):
	ulx = args[0]
	uly = args[1]
	lrx = args[2]
	lry = args[3]
	fileIn = args[4]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7 /root/gdal-1.11.2/swig/python/scripts/gdal_edit.py -a_ullr "+ulx+" "+uly+" "+lrx+" "+lry+" "+fileIn)

def MergeRaster(args):
	dest_file_1 = args[0]
	dest_file_2 = args[1]
	dest_vrt = args[2]
	temp_file = args[3]
	os.system('/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7 /root/gdal-1.11.2/swig/python/scripts/gdal_merge.py -o '+temp_file+' '+dest_file_1+' '+dest_file_2+'; /usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate '+dest_vrt+' '+temp_file)

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

def CompareArray(Array1, Array2, Array3):
	if np.allclose(Array1.shape, Array2.shape):
		if np.allclose(Array2.shape, Array3.shape):
			return Array1, Array2, Array3
		else:
			if np.any(Array2.shape> Array3.shape):
				Array2 = Array2[:Array3.shape[0],:Array3.shape[1]]
				Array1 = Array1[:Array3.shape[0],:Array3.shape[1]]
				return Array1, Array2, Array3
			else:
				Array3 = Array3[:Array2.shape[0],:Array2.shape[1]]
				return Array1, Array2, Array3
	elif np.allclose(Array1.shape, Array3.shape):
		if np.any(Array3.shape> Array2.shape):
			Array3 = Array3[:Array2.shape[0],:Array2.shape[1]]
			Array1 = Array1[:Array2.shape[0],:Array2.shape[1]]
			return Array1, Array2, Array3
		else:
			Array2 = Array2[:Array3.shape[0],:Array3.shape[1]]
			return Array1, Array2, Array3
	elif np.allclose(Array2.shape, Array3.shape):
		if np.any(Array3.shape> Array1.shape):
			Array3 = Array3[:Array1.shape[0],:Array1.shape[1]]
			Array2 = Array2[:Array1.shape[0],:Array1.shape[1]]
			return Array1, Array2, Array3
		else:
			Array1 = Array1[:Array3.shape[0],:Array3.shape[1]]
			return Array1, Array2, Array3

def SpaTempRes(dataset, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2):
	if dataset == 'CDR':
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
	return TempResSet, bpath

def RasterCal(Ras1, Ras2, OutDiffFile, temp_folder0):
	Ras1_size=' '.join([str(xk) for xk in gdal.Open(Ras1).ReadAsArray().shape][::-1])
	Ras2_size=' '.join([str(xk) for xk in gdal.Open(Ras2).ReadAsArray().shape][::-1])
	if Ras1_size != Ras2_size:
		Ras2_temp = temp_folder0+'Ras2_temp.tif'
		os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdalwarp -q -overwrite -srcnodata -99 -ts "+Ras1_size+" "+Ras2+" "+Ras2_temp)
		Ras2 = Ras2_temp
	os.system("/mnt/t/disk2/pconnect/CHRSData/python/gdal_calc.py --overwrite -A "+Ras2+" -B "+Ras1+" --calc=\"numpy.around(100*(A-B)/B)\" --NoDataValue=-9999 --type='Int16' --outfile "+temp_folder0+"TempRas1.tif")
	os.system("/mnt/t/disk2/pconnect/CHRSData/python/gdal_calc.py --overwrite -A "+temp_folder0+"TempRas1.tif --calc=\"(A*([(A!=32767) & (A!=-32768)])-9999*(A==32767)-9999*(A==-32768))[0,:,:]\" --NoDataValue=-9999 --type='Int16' --outfile "+temp_folder0+"TempRas2.tif")
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -a_nodata -9999 -of GTiff -co COMPRESS=LZW "+temp_folder0+"TempRas2.tif "+OutDiffFile)

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
	[RefSet, RefPath] = SpaTempRes(DataRef, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
	[FileSet1, FilePath1] = SpaTempRes(Data1, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
	[FileSet2, FilePath2] = SpaTempRes(Data2, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
else:
	Data2 = Data1
	[RefSet, RefPath] = SpaTempRes(DataRef, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
	[FileSet1, FilePath1] = SpaTempRes(Data1, time_step, start_date, end_date, userIP, curr_str, domain, temp_folder0, temp_folder1, temp_folder2)
	[FileSet2, FilePath2] = [FileSet1, FilePath1]

arr_len = 3
#compare time step
if time_step not in RefSet:
	print time_step+' is not in the dataset of '+DataRef+'. Skipping '+DataRef+'.'
	arr_len -= 1
	DataRef = Data1
	RefPath = FilePath1
elif time_step not in FileSet1:
	print time_step+' is not in the dataset of '+Data1+'. Skipping '+Data1+'.'
	arr_len -= 1
	Data1 = DataRef
	FilePath1 = RefPath
elif time_step not in FileSet2:
	print time_step+' is not in the dataset of '+Data2+'. Skipping '+Data2+'.'
	arr_len -= 1
	Data2 = DataRef
	FilePath2 = RefPath

#check if input date is in data range
if time_step != 'customized':
	try:
		ref_file = glob.glob(RefPath+"*"+start_date+"*.tif")[0]
	except:
		print start_date+' is not in the data range of '+DataRef+'. Skipping '+DataRef+'.'
		ref_file = ''
		arr_len -= 1
	try:
		dat_file1 = glob.glob(FilePath1+"*"+start_date+"*.tif")[0]
	except:
		print start_date+' is not in the data range of '+Data1+'. Skipping '+Data1+'.'
		dat_file1 = ''
		arr_len -= 1
	try:
		dat_file2 = glob.glob(FilePath2+"*"+start_date+"*.tif")[0]
	except:
		print start_date+' is not in the data range of '+Data2+'. Skipping '+Data2+'.'
		dat_file2 = ''
		arr_len -= 1
else:
	if len(start_date) == 8:
		time_step1 = 'daily/'
	elif len(start_date) == 6:
		time_step1 = 'monthly/'
	elif len(start_date) == 4:
		time_step1 = 'yearly/'
	if DataRef == 'CDR':
		RefPath_acc = '/mnt/t/disk3/CHRSdata/Persiann_CDR'
	RefPath_acc = AccPath(DataRef)
	FilePath1_acc = AccPath(Data1)
	FilePath2_acc = AccPath(Data2)
	try:
		ref_file = glob.glob(RefPath_acc+time_step1+"*"+start_date+"*.tif")[0]
		ref_file1 = glob.glob(RefPath_acc+time_step1+"*"+end_date+"*.tif")[0]
	except:
		print start_date+' is not in the data range of '+DataRef+'. Skipping '+DataRef+'.'
		ref_file = ''
		arr_len -= 1
	try:
		dat_file1 = glob.glob(FilePath1_acc+time_step1+"*"+start_date+"*.tif")[0]
		dat_file01 = glob.glob(FilePath1_acc+time_step1+"*"+end_date+"*.tif")[0]
	except:
		print start_date+' is not in the data range of '+Data1+'. Skipping '+Data1+'.'
		dat_file1 = ''
		arr_len -= 1
	try:
		dat_file2 = glob.glob(FilePath2_acc+time_step1+"*"+start_date+"*.tif")[0]
		dat_file02 = glob.glob(FilePath2_acc+time_step1+"*"+end_date+"*.tif")[0]
	except:
		print start_date+' is not in the data range of '+Data2+'. Skipping '+Data2+'.'
		dat_file2 = ''
		arr_len -= 1

if arr_len == 2:
	if not dat_file1:
		Data1 = DataRef
		FilePath1 = RefPath
	if not dat_file2:
		Data2 = DataRef
		FilePath2 = RefPath
elif arr_len == 1:
	print 'error:Not enough dataset'
	sys.exit()

if arr_len < 2:
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
			uly = str(extend[2])
			ulx = str(extend[0])
			lry = str(extend[3])
			lrx = str(extend[1])
			#steps to clip rectangle
			if float(ulx) <= float(lrx):
				uly = str(60) if float(uly) > 60 else uly
				lry = str(-60) if float(lry) < -60 else lry
				uly_arr = [uly]*3
				ulx_arr = [ulx]*3
				lry_arr = [lry]*3
				lrx_arr = [lrx]*3
				RefDestFile = temp_folder0+os.path.splitext(os.path.basename(RefFile))[0]+'.tif'
				DestFile1 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'.tif'
				DestFile2 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'.tif'
				pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, [RefFile, File1, File2], [RefDestFile, DestFile1, DestFile2], [Refvrt, File1vrt, File2vrt]))
			else:
				RefDestFile_1 = temp_folder0+os.path.splitext(os.path.basename(RefFile))[0]+'_1.tif'
				DestFile1_1 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'_1.tif'
				DestFile2_1 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'_1.tif'
				RefDestFile_2 = temp_folder0+os.path.splitext(os.path.basename(RefFile))[0]+'_2.tif'
				DestFile1_2 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'_2.tif'
				DestFile2_2 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'_2.tif'
				ulx1 = float(ulx) - 360
				ulx1 = str(ulx1)
				uly = str(60) if float(uly) > 60 else uly
				lry = str(-60) if float(lry) < -60 else lry
				uly_arr = [uly]*3
				ulx_arr = [ulx]*3
				lry_arr = [lry]*3
				lrx_arr = [lrx]*3
				XE_arr = [ulx1]*3
				ulx_arr1 = ['-180']*3
				lrx_arr1 = ['180']*3
				pool.map(ClipRasterPart, itertools.izip(ulx_arr1, uly_arr, lrx_arr, lry_arr, [RefFile, File1, File2], [RefDestFile_1, DestFile1_1, DestFile2_1]))
				pool.map(ClipRasterPart, itertools.izip(ulx_arr, uly_arr, lrx_arr1, lry_arr, [RefFile, File1, File2], [RefDestFile_2, DestFile1_2, DestFile2_2]))
				pool.map(EditRaster, itertools.izip(XE_arr, uly_arr, ulx_arr1, lry_arr,[RefDestFile_2, DestFile1_2, DestFile2_2]))
				pool.map(MergeRaster, itertools.izip([RefDestFile_1, DestFile1_1, DestFile2_1], [RefDestFile_2, DestFile1_2, DestFile2_2], [Refvrt, File1vrt, File2vrt], [temp_folder0+os.path.splitext(os.path.basename(RefFile))[0]+'_sum.tif', temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'_sum.tif', temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'_sum.tif']))
				RefPath = Refvrt
				FilePath1 = File1vrt
				FilePath2 = File2vrt
		else:
			if DataRef == 'CCS':
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+Refvrt+" "+RefPath)
				File1vrt = FilePath1
				File2vrt = FilePath2
			elif Data1 == 'CCS':
				Refvrt = RefPath
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+File1vrt+" "+FilePath1)
				File2vrt = FilePath2
			elif Data2 == 'CCS':
				Refvrt = RefPath
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+File2vrt+" "+FilePath2)
				File1vrt = FilePath1
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
			if DataRef == 'CCS':
				Refvrt = temp_folder0+'Ref.vrt'
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+Refvrt+" "+RefPath)
				File1vrt = FilePath1
				File2vrt = FilePath2
			elif Data1 == 'CCS':
				File1vrt = temp_folder1+'file1.vrt'
				Refvrt = RefPath
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+File1vrt+" "+FilePath1)
				File2vrt = FilePath2
			elif Data2 == 'CCS':
				Refvrt = RefPath
				File2vrt = temp_folder2+'file2.vrt'
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+File2vrt+" "+FilePath2)
				File1vrt = FilePath1
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
	ds0 = gdal.Open(Refvrt)
	ds1 = gdal.Open(File1vrt)
	ds2 = gdal.Open(File2vrt)
	ref_arr = ds0.ReadAsArray()
	obs_arr1 = ds1.ReadAsArray()
	obs_arr2 = ds2.ReadAsArray()
	ref_arr, obs_arr1, obs_arr2 = CompareArray(ref_arr, obs_arr1, obs_arr2)
	#Masking data
	ref_arr_mask = np.ma.masked_where(ref_arr==-99, ref_arr)
	ref_arr_mask[ref_arr_mask <0.1] = 0
	obs_arr1_mask = np.ma.masked_where(obs_arr1==-99, obs_arr1)
	obs_arr1_mask[obs_arr1_mask <0.1] = 0
	obs_arr2_mask = np.ma.masked_where(obs_arr2==-99, obs_arr2)
	obs_arr2_mask[obs_arr2_mask <0.1] = 0
	[nr, nc] = ref_arr.shape
	#get results from ValidationFunction
	threshold = 0.1
	RefStat = OrderedDict()
	Obs1Stat = OrderedDict()
	Obs2Stat = OrderedDict()
	RefStat['Number of points']=nr*nc; RefStat['Number of points with rain']=np.sum((ref_arr_mask>0).astype(np.uint8)); RefStat['Mean rain rate']=round(np.ma.mean(ref_arr_mask),3); RefStat['Max rain rate']=round(np.ma.max(ref_arr_mask),3)
	Obs1Stat['Number of points']=nr*nc; Obs1Stat['Number of points with rain']=np.sum((obs_arr1_mask>0).astype(np.uint8)); Obs1Stat['Mean rain rate']=round(np.ma.mean(obs_arr1_mask),3); Obs1Stat['Max rain rate']=round(np.ma.max(obs_arr1_mask),3)
	Obs2Stat['Number of points']=nr*nc; Obs2Stat['Number of points with rain']=np.sum((obs_arr2_mask>0).astype(np.uint8)); Obs2Stat['Mean rain rate']=round(np.ma.mean(obs_arr2_mask),3); Obs2Stat['Max rain rate']=round(np.ma.max(obs_arr2_mask),3)
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
			uly = str(extend[2])
			ulx = str(extend[0])
			lry = str(extend[3])
			lrx = str(extend[1])
			#steps to clip rectangle
			if float(ulx) <= float(lrx):
				uly = str(60) if float(uly) > 60 else uly
				lry = str(-60) if float(lry) < -60 else lry
				uly_arr = [uly]*2
				ulx_arr = [ulx]*2
				lry_arr = [lry]*2
				lrx_arr = [lrx]*2
				DestFile1 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'.tif'
				DestFile2 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'.tif'
				pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, [File1, File2], [DestFile1, DestFile2], [File1vrt, File2vrt]))
			else:
				DestFile1_1 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'_1.tif'
				DestFile2_1 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'_1.tif'
				DestFile1_2 = temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'_2.tif'
				DestFile2_2 = temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'_2.tif'
				lrx1 = float(lrx) + 360
				lrx1 = str(lrx1)
				ulx1 = float(ulx) - 360
				ulx1 = str(ulx1)
				uly = str(60) if float(uly) > 60 else uly
				lry = str(-60) if float(lry) < -60 else lry
				uly_arr = [uly]*2
				ulx_arr = [ulx]*2
				lry_arr = [lry]*2
				lrx_arr = [lrx]*2
				XE_arr = [ulx1]*3
				ulx_arr1 = ['-180']*2
				lrx_arr1 = ['180']*2
				pool.map(ClipRasterPart, itertools.izip(ulx_arr1, uly_arr, lrx_arr, lry_arr, [File1, File2], [DestFile1_1, DestFile2_1]))
				pool.map(ClipRasterPart, itertools.izip(ulx_arr, uly_arr, lrx_arr1, lry_arr, [File1, File2], [DestFile1_2, DestFile2_2]))
				pool.map(EditRaster, itertools.izip(XE_arr, uly_arr, ulx_arr1, lry_arr,[DestFile1_2, DestFile2_2]))
				pool.map(MergeRaster, itertools.izip([DestFile1_1, DestFile2_1], [DestFile1_2, DestFile2_2], [File1vrt, File2vrt], [temp_folder1+os.path.splitext(os.path.basename(File1))[0]+'_sum.tif', temp_folder2+os.path.splitext(os.path.basename(File2))[0]+'_sum.tif']))
				FilePath1 = File1vrt
				FilePath2 = File2vrt
		else:
			if Data1 == 'CCS':
				File1vrt = temp_folder1+'file1.vrt'
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+File1vrt+" "+FilePath1)
				File2vrt = FilePath2
			elif Data2 == 'CCS':
				File2vrt = temp_folder2+'file2.vrt'
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+File2vrt+" "+FilePath2)
				File1vrt = FilePath1
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
			if Data1 == 'CCS':
				File1vrt = temp_folder1+'file1.vrt'
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+File1vrt+" "+FilePath1)
				File2vrt = FilePath2
			elif Data2 == 'CCS':
				File2vrt = temp_folder2+'file2.vrt'
				os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -overwrite -separate "+File2vrt+" "+FilePath2)
				File1vrt = FilePath1
			time_step = 'monthly'
			shape_in = glob.glob(temp_folder1+'*.shp')[0]
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
	obs_arr1 = gdal.Open(File1vrt).ReadAsArray()
	obs_arr2 = gdal.Open(File2vrt).ReadAsArray()
	if not np.allclose(obs_arr1.shape, obs_arr2.shape):
		if np.any(obs_arr1.shape > obs_arr2.shape):
			obs_arr1 = obs_arr1[:obs_arr2.shape[0],:obs_arr2.shape[1]]
		else:
			obs_arr2 = obs_arr2[:obs_arr1.shape[0],:obs_arr1.shape[1]]
	#Masking data
	obs_arr1_mask = np.ma.masked_where(obs_arr1==-99, obs_arr1)
	obs_arr1_mask[obs_arr1_mask <0.1] = 0
	obs_arr2_mask = np.ma.masked_where(obs_arr2==-99, obs_arr2)
	obs_arr2_mask[obs_arr2_mask <0.1] = 0
	[nr, nc] = obs_arr1.shape
	#get results from ValidationFunction
	threshold = 0.1
	Obs1Stat = OrderedDict()
	Obs2Stat = OrderedDict()
	Obs1Stat['Number of points']=nr*nc; Obs1Stat['Number of points with rain']=np.sum((obs_arr1_mask>0).astype(np.uint8)); Obs1Stat['Mean rain rate']=round(np.ma.mean(obs_arr1_mask),3); Obs1Stat['Max rain rate']=round(np.ma.max(obs_arr1_mask),3)
	Obs2Stat['Number of points']=nr*nc; Obs2Stat['Number of points with rain']=np.sum((obs_arr2_mask>0).astype(np.uint8)); Obs2Stat['Mean rain rate']=round(np.ma.mean(obs_arr2_mask),3); Obs2Stat['Max rain rate']=round(np.ma.max(obs_arr2_mask),3)
	result_1 = ValidationFunction(obs_arr1_mask, obs_arr2_mask)
	#print results
	print 'D0:'+','.join([str(x1) for x1 in Obs1Stat.values()+result_1.values()])
	print 'D1:'+','.join([str(x1) for x1 in Obs2Stat.values()])
	result_2 = np.array([])

#plot result images
if len(result_2) != 0:
	PlotMap2(ref_arr_mask, DataRef, obs_arr1_mask, Data1, time_step, temp_folder, obs_arr2_mask, Data2)
	#export to rasters
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -q -of GTiff -ot Int16 -co COMPRESS=LZW "+Refvrt+" "+temp_folder+"File1.tif")
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -q -of GTiff -ot Int16 -co COMPRESS=LZW "+File1vrt+" "+temp_folder+"File2.tif")
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -q -of GTiff -ot Int16 -co COMPRESS=LZW "+File2vrt+" "+temp_folder+"File3.tif")
	print 'RasterCal'
	RasterCal(temp_folder+"File1.tif", temp_folder+"File2.tif", temp_folder+"Diff1.tif", temp_folder0)
	RasterCal(temp_folder+"File1.tif", temp_folder+"File3.tif", temp_folder+"Diff2.tif", temp_folder0)
	RasterCal(temp_folder+"File2.tif", temp_folder+"File3.tif", temp_folder+"Diff3.tif", temp_folder0)
	if domain != 'wholemap':
		if DataRef == 'CCS':
			try:
				os.system("cp "+RefDestFile+" "+temp_folder+"File1.tif")
			except:
				os.system("cp "+RefPath+" "+temp_folder+"File1.tif")
		elif Data1 == 'CCS':
			try:
				os.system("cp "+DestFile1+" "+temp_folder+"File2.tif")
			except:
				os.system("cp "+FilePath1+" "+temp_folder+"File2.tif")
		elif Data2 == 'CCS':
			try:
				os.system("cp "+DestFile2+" "+temp_folder+"File3.tif")
			except:
				os.system("cp "+FilePath2+" "+temp_folder+"File3.tif")
	os.system('cp '+temp_folder+'/* '+result_folder)
	print 'datasetValue:'+DataRef+','+Data1+','+Data2
else:
	PlotMap2(obs_arr2_mask, Data2, obs_arr1_mask, Data1, time_step, temp_folder)
	#export to rasters
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -q -of GTiff -ot Int16 -co COMPRESS=LZW "+File1vrt+" "+temp_folder+"File1.tif")
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -a_nodata -99 -q -of GTiff -ot Int16 -co COMPRESS=LZW "+File2vrt+" "+temp_folder+"File2.tif")
	RasterCal(temp_folder+"File1.tif", temp_folder+"File2.tif", temp_folder+"Diff1.tif", temp_folder0)
	if domain != 'wholemap':
		#print 'DestFile1 '+DestFile1
		if Data1 == 'CCS':
			try:
				os.system("cp "+DestFile1+" "+temp_folder+"File1.tif")
			except:
				os.system("cp "+FilePath1+" "+temp_folder+"File1.tif")
		elif Data2 == 'CCS':
			try:
				os.system("cp "+DestFile2+" "+temp_folder+"File2.tif")
			except:
				os.system("cp "+FilePath2+" "+temp_folder+"File2.tif")
	os.system('cp '+temp_folder+'/* '+result_folder)
	print 'datasetValue:'+Data2+','+Data1
