#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import sys
import os
import glob
import numpy as np
from datetime import datetime
import multiprocessing as mp
from contextlib import closing
import itertools
import ctypes
from osgeo import gdal, ogr
import json
import warnings
from ValidationFunction import ValidationFunction
from PlotMap2 import PlotMap2
from PlotMap1 import PlotMap1
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
	os.system("/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -q -ot Int16 -a_nodata -99 -projwin "+ulx+" "+uly+" "+lrx+" "+lry+" -of GTiff "+fileIn+" "+dest_file+" -co COMPRESS=LZW")

def ClipRasterShape(args):
	fileIn = args[0]
	outShapefile = args[1]
	p1 = args[2]
	dest_file = args[3]
	os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline "+outShapefile+" -te "+p1+" -of GTiff -ot Int16 "+fileIn+" "+dest_file)

def SpaTempRes(dataset, time_step, domain, userIP, curr_str, start_date, end_date, temp_folder0, temp_folder1, temp_folder2):
	if dataset == 'CDR':
		TempResSet = ['daily', 'monthly', 'yearly']
		start1 = '1983010100'
		end1 = '2016033123'
		if time_step == 'acc':
			if domain =='wholemap':
				os.system("./do_acc.sh "+start_date+" "+end_date+" "+dataset+" "+userIP+" "+curr_str)
			elif domain.split(' ') == 'rec':
				os.system("./do_acc.sh "+start_date+" "+end_date+" '\""+dataset+" "+domain+"\"' "+userIP+" "+curr_str)
				bpath = temp_folder0+userIP+'.vrt'
				bpath1 = temp_folder0+userIP+'.tif'
			else:
				os.system("./do_acc.sh "+start_date+" "+end_date+" '\""+dataset+" shp "+domain+"\"' "+userIP+" "+curr_str)
				bpath = temp_folder0+userIP+'.vrt'
				bpath1 = temp_folder0+userIP+'.tif'
		elif time_step not in TempResSet:
			print time_step+' not avaiable for PERSIANN-CDR'
			sys.exit
		else:
			bpath = '/mnt/t/disk3/CHRSdata/Persiann_CDR/'+time_step+'/'
			bpath1 = ''
	elif dataset == 'CCS':
		TempResSet = ['1hrly', '3hrly', '6hrly', 'daily', 'monthly', 'yearly']
		start1 = '2003010100'
		end1 = '2016123100'
		if time_step == 'acc':
			if domain =='wholemap':
				os.system("./do_acc.sh "+start_date+" "+end_date+" "+dataset+" "+userIP+" "+curr_str)
			elif domain.split(' ') == 'rec':
				os.system("./do_acc.sh "+start_date+" "+end_date+" '\""+dataset+" "+domain+"\"' "+userIP+" "+curr_str)
				bpath = temp_folder1+userIP+'.vrt'
				bpath1 = temp_folder1+userIP+'.tif'
			else:
				os.system("./do_acc.sh "+start_date+" "+end_date+" '\""+dataset+" shp "+domain+"\"' "+userIP+" "+curr_str)
				bpath = temp_folder1+userIP+'.vrt'
				bpath1 = temp_folder1+userIP+'.tif'
		else:
			bpath = '/mnt/t/disk3/CHRSdata/Persiann_CCS/'+time_step+'/'
			bpath1 = ''
	elif dataset == 'PERSIANN':
		TempResSet = ['1hrly', '3hrly', '6hrly', 'daily', 'monthly', 'yearly']
		start1 = '2000030100'
		end1 = '2016123100'
		if time_step == 'acc':
			if domain =='wholemap':
				os.system("./do_acc.sh "+start_date+" "+end_date+" "+dataset+" "+userIP+" "+curr_str)
			elif domain.split(' ') == 'rec':
				os.system("./do_acc.sh "+start_date+" "+end_date+" '\""+dataset+" "+domain+"\"' "+userIP+" "+curr_str)
				bpath = temp_folder2+userIP+'.vrt'
				bpath1 = temp_folder2+userIP+'.tif'
			else:
				os.system("./do_acc.sh "+start_date+" "+end_date+" '\""+dataset+" shp "+domain+"\"' "+userIP+" "+curr_str)
				bpath = temp_folder2+userIP+'.vrt'
				bpath1 = temp_folder2+userIP+'.tif'
		else:
			bpath = '/mnt/t/disk3/CHRSdata/Persiann/'+time_step+'/'
			bpath1 = ''
	return TempResSet, start1, end1, bpath, bpath1	

def tonumpyarray(mp_arr):
    return np.frombuffer(mp_arr.get_obj())

def MultiValidationFunction(i):
	"""no synchronization."""
	arrRes1 = tonumpyarray(result1)
	arrRes2 = tonumpyarray(result2)
	arr0 = tonumpyarray(Ref)
	Ref0 = arr0[n*i:n*(i+1)]
	arr1 = tonumpyarray(Obs1)
	Obs01 = arr1[n*i:n*(i+1)]
	arr2 = tonumpyarray(Obs2)
	Obs02 = arr2[n*i:n*(i+1)]
	result01 = ValidationFunction(Ref0, Obs01)
	result02 = ValidationFunction(Ref0, Obs02)
	arrRes1[npar*i:npar*(i+1)] = result01
	arrRes2[npar*i:npar*(i+1)] = result02

def init(Ref_, Obs1_, Obs2_, result1_, result2_, n1, npar1):
	global Ref, Obs1, Obs2, result1, result2, n, npar
	Ref = Ref_ # must be inhereted, not passed as an argument
	result1 = result1_
	result2 = result2_
	Obs1 = Obs1_
	Obs2 = Obs2_
	n = n1
	npar = npar1
	
curr_str = sys.argv[1]
userIP = sys.argv[2]
domain = sys.argv[3]
time_step = sys.argv[4]
start_date = sys.argv[5]
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

if (len(start_date) < 10):
	start_date1 = start_date+'0'*(10-len(start_date))
	end_date1 = end_date+'0'*(10-len(end_date)-2)+'23'
else:
	start_date1 = start_date
	end_date1 = end_date

#Spatial and temporal resolution of dataset
if Data2:
	[RefSet, RefStart, RefEnd, RefPath, RefPath1] = SpaTempRes(DataRef, time_step, domain, userIP, curr_str, start_date1, end_date1, temp_folder0, temp_folder1, temp_folder2)
	[FileSet1, FileStart1, FileEnd1, FilePath1, FilePath01] = SpaTempRes(Data1, time_step, domain, userIP, curr_str, start_date1, end_date1, temp_folder0, temp_folder1, temp_folder2)
	[FileSet2, FileStart2, FileEnd2, FilePath2, FilePath02] = SpaTempRes(Data2, time_step, domain, userIP, curr_str, start_date1, end_date1, temp_folder0, temp_folder1, temp_folder2)
else:
	Data2 = Data1
	[RefSet, RefStart, RefEnd, RefPath, RefPath] = SpaTempRes(DataRef, time_step, domain, userIP, curr_str, start_date1, end_date1, temp_folder0, temp_folder1, temp_folder2)
	[FileSet1, FileStart1, FileEnd1, FilePath1, FilePath01] = SpaTempRes(Data1, time_step, domain, userIP, curr_str, start_date1, end_date1, temp_folder0, temp_folder1, temp_folder2)
	[FileSet2, FileStart2, FileEnd2, FilePath2, FilePath02] = [FileSet1, FileStart1, FileEnd1, FilePath1, FilePath01]

#Compare time frame

if any(int(start_date1) < np.array([int(x) for x in [RefStart, FileStart1, FileStart2]])):
	print 'start date is smaller than time range of dataset. Set start date equal to time range.'
	start_date1 = max(RefStart, FileStart1, FileStart2)
	start_date = start_date1[:len(start_date)]

if any(int(end_date1) > np.array([int(x) for x in [RefEnd, FileEnd1, FileEnd2]])):
	print 'end date is larger than time range of dataset. Set start end equal to time range.'
	end_date1 = min(RefEnd, FileEnd1, FileEnd2)
	end_date = end_date1[:len(endt_date)]
	
pool = mp.Pool(processes = 16)
domain_split = domain.split(' ')
if domain_split[0] == 'wholemap':
	extend = [-180, 180, 60, -60]
	if time_step != 'acc':
		#list file from terminal
		RefFiles = RefPath+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		Files1 = FilePath1+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		Files2 = FilePath2+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		#get list file into python
		RefList = [file1.replace('\n','') for file1 in os.popen('ls '+RefFiles).readlines()]
		FileList1 = [file1.replace('\n','') for file1 in os.popen('ls '+Files1).readlines()]
		FileList2 = [file1.replace('\n','') for file1 in os.popen('ls '+Files2).readlines()]
		#buil vrt, acc files
		Refvrt = temp_folder0+'Ref.vrt'
		Refacc = temp_folder0+'Ref.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+Refvrt+" "+' '.join(RefList)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+Refvrt+" "+Refacc+" "+DataRef)
		File1vrt = temp_folder1+'file1.vrt'
		File1acc = temp_folder1+'file1.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File1vrt+" "+' '.join(FileList1)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+File1vrt+" "+File1acc+" "+Data1)
		File2vrt = temp_folder2+'file2.vrt'
		File2acc = temp_folder2+'file2.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File2vrt+" "+' '.join(FileList2)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+File2vrt+" "+File2acc+" "+Data2)
	else:
		Refvrt = RefPath
		Refacc = RefPath1
		File1vrt = FilePath1
		File1acc = FilePath01
		File2vrt = FilePath2
		File2acc = FilePath02
		time_step = 'monthly'
elif domain_split[0] == 'rec':
	RawExtend = [float(x) for x in domain_split[1:]]
	extend = [RawExtend[0], RawExtend[2], RawExtend[1], RawExtend[3]]
	if time_step != 'acc':
		#steps to clip rectangle for ref
		RefFiles = RefPath+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		RefList = [file1.replace('\n','') for file1 in os.popen('ls '+RefFiles).readlines()]
		uly_arr = [str(extend[2])]*len(RefList)
		ulx_arr = [str(extend[0])]*len(RefList)
		lry_arr = [str(extend[3])]*len(RefList)
		lrx_arr = [str(extend[1])]*len(RefList)
		RefDestFile = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in RefList]
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, RefList, RefDestFile))
		#steps to clip rectangle for file1
		Files1 = FilePath1+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		FileList1 = [file1.replace('\n','') for file1 in os.popen('ls '+Files1).readlines()]
		ListDestFile1 = [temp_folder1+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in FileList1]
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, FileList1, ListDestFile1))
		#steps to clip rectangle for file1
		Files2 = FilePath2+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		FileList2 = [file2.replace('\n','') for file2 in os.popen('ls '+Files2).readlines()]
		ListDestFile2 = [temp_folder2+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in FileList2]
		pool.map(ClipRaster, itertools.izip(ulx_arr, uly_arr, lrx_arr, lry_arr, FileList2, ListDestFile2))
		#buil vrt, acc files
		Refvrt = temp_folder0+'Ref.vrt'
		Refacc = temp_folder0+'Ref.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+Refvrt+" "+' '.join(RefDestFile)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+Refvrt+" "+Refacc+" "+DataRef)
		File1vrt = temp_folder1+'file1.vrt'
		File1acc = temp_folder1+'file1.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File1vrt+" "+' '.join(ListDestFile1)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+File1vrt+" "+File1acc+" "+Data1)
		File2vrt = temp_folder2+'file2.vrt'
		File2acc = temp_folder2+'file2.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File2vrt+" "+' '.join(ListDestFile2)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+File2vrt+" "+File2acc+" "+Data2)
	else:
		Refvrt = RefPath
		Refacc = RefPath1
		File1vrt = FilePath1
		File1acc = FilePath01
		File2vrt = FilePath2
		File2acc = FilePath02
		time_step = 'monthly'
else:
	if time_step != 'acc':
		shape = domain_split[0]
		extend = domain_split[1:]
		shape_in = ShapeSelection(extend, shape, temp_folder)
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
		#steps to clip shape for ref
		RefFiles = RefPath+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		RefList = [file1.replace('\n','') for file1 in os.popen('ls '+RefFiles).readlines()]
		ShapeArray = [shape_in]*len(RefList)
		CoorArray = [' '.join(p1)]*len(RefList)
		RefDestFile = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in RefList]
		pool.map(ClipRasterShape, itertools.izip(RefList, ShapeArray, CoorArray,RefDestFile))
		#steps to clip shape for ref
		Files1 = FilePath1+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		FileList1 = [file1.replace('\n','') for file1 in os.popen('ls '+Files1).readlines()]
		ListDestFile1 = [temp_folder1+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in FileList1]
		pool.map(ClipRasterShape, itertools.izip(FileList1, ShapeArray, CoorArray,ListDestFile1))
		#steps to clip shape for ref
		Files2 = FilePath2+'*{'+start_date+'..'+end_date+'}*.tif 2>/dev/null'
		FileList2 = [file2.replace('\n','') for file2 in os.popen('ls '+Files2).readlines()]
		ListDestFile2 = [temp_folder2+os.path.splitext(os.path.basename(file2))[0]+'.tif' for file2 in FileList2]
		pool.map(ClipRasterShape, itertools.izip(FileList2, ShapeArray, CoorArray,ListDestFile2))
		#buil vrt, acc files
		Refvrt = temp_folder0+'Ref.vrt'
		Refacc = temp_folder0+'Ref.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+Refvrt+" "+' '.join(RefDestFile)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+Refvrt+" "+Refacc+" "+DataRef)
		File1vrt = temp_folder1+'file1.vrt'
		File1acc = temp_folder1+'file1.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File1vrt+" "+' '.join(ListDestFile1)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+File1vrt+" "+File1acc+" "+Data1)
		File2vrt = temp_folder2+'file2.vrt'
		File2acc = temp_folder2+'file2.tif'
		os.system("/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalbuildvrt -tr 0.25 0.25 -separate "+File2vrt+" "+' '.join(ListDestFile2)+"; /mnt/t/disk2/pconnect/CHRSData/python/sum_raster.py "+File2vrt+" "+File2acc+" "+Data2)
	else:
		Refvrt = RefPath
		Refacc = RefPath1
		File1vrt = FilePath1
		File1acc = FilePath01
		File2vrt = FilePath2
		File2acc = FilePath02
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
		time_step = 'monthly'
ref_arr = gdal.Open(Refvrt).ReadAsArray().swapaxes(2,0).swapaxes(1,0)
obs_arr1 = gdal.Open(File1vrt).ReadAsArray().swapaxes(2,0).swapaxes(1,0)
obs_arr2 = gdal.Open(File2vrt).ReadAsArray().swapaxes(2,0).swapaxes(1,0)
ref_acc= gdal.Open(Refacc).ReadAsArray()
obs_acc1= gdal.Open(File1acc).ReadAsArray()
obs_acc2= gdal.Open(File2acc).ReadAsArray()

#Masking data
ref_arr_mask = np.ma.masked_where(ref_arr==-99, ref_arr)
obs_arr1_mask = np.ma.masked_where(obs_arr1==-99, obs_arr1)
obs_arr2_mask = np.ma.masked_where(obs_arr2==-99, obs_arr2)
ref_acc_mask = np.ma.masked_where(ref_acc==-99, ref_acc)
obs_acc1_mask = np.ma.masked_where(obs_acc1==-99, obs_acc1)
obs_acc2_mask = np.ma.masked_where(obs_acc2==-99, obs_acc2)

#prepare data for multiprocessing
npar = 11
[nr, nc, n] = ref_arr_mask.shape
N = nr*nc*n
result1 = mp.Array(ctypes.c_long, nr*nc*npar)
result2 = mp.Array(ctypes.c_long, nr*nc*npar)
arrRes1 = tonumpyarray(result1)
arrRes1[:] = np.zeros((nr*nc, npar)).flatten('C')
arrRes2 = tonumpyarray(result2)
arrRes2[:] = np.zeros((nr*nc, npar)).flatten('C')
Ref = mp.Array(ctypes.c_long, N)
Obs1 = mp.Array(ctypes.c_long, N)
Obs2 = mp.Array(ctypes.c_long, N)
arr0 = tonumpyarray(Ref)
arr0[:] = ref_arr_mask.flatten('C')
arr1 = tonumpyarray(Obs1)
arr1[:] = obs_arr1_mask.flatten('C')
arr2 = tonumpyarray(Obs2)
arr2[:] = obs_arr2_mask.flatten('C')

with closing(mp.Pool(initializer=init, initargs=(Ref, Obs1, Obs2, result1, result2, n, npar, ))) as p:
    # many processes access different slices of the same array
	p.map_async(MultiValidationFunction, range(nr*nc))
p.join()
result_1 = tonumpyarray(result1).reshape(nr, nc, npar)
result_2 = tonumpyarray(result2).reshape(nr, nc, npar)
result_1 = np.ma.masked_where((np.isnan(result_1)) | (result_1 == np.inf) | (result_1 == -np.inf), result_1)
result_2 = np.ma.masked_where((np.isnan(result_2)) | (result_2 == np.inf) | (result_2 == -np.inf), result_2)

#plot parameters
ParList = ['BIAS', 'POD', 'VHI', 'FAR', 'VFAR', 'Categorical Miss', 'VMI', 'CSI', 'VCSI']
for Par in ParList:
	if Par == 'BIAS':
		Par_arr1 = result_1[:,:,0]
		Par_arr2 = result_2[:,:,0]
	elif Par == 'POD':
		Par_arr1 = result_1[:,:,9]
		Par_arr2 = result_2[:,:,9]
	elif Par == 'VHI':
		sumMiss1 = result_1[:,:,4]
		sumSimhit1 = result_1[:,:,6]
		Par_arr1 = np.divide(sumSimhit1, sumSimhit1+sumMiss1)
		sumMiss2 = result_2[:,:,4]
		sumSimhit2 = result_2[:,:,6]
		Par_arr2 = np.divide(sumSimhit2, sumSimhit2+sumMiss2)
	elif Par == 'FAR':
		Par_arr1 = result_1[:,:,10]
		Par_arr2 = result_2[:,:,10]
	elif Par == 'VFAR':
		sumFalse1 = result_1[:,:,5]
		sumSimhit1 = result_1[:,:,6]
		Par_arr1 = np.divide(sumFalse1, sumSimhit1+sumFalse1)
		sumFalse2 = result_2[:,:,5]
		sumSimhit2 = result_2[:,:,6]
		Par_arr2 = np.divide(sumFalse2, sumSimhit2+sumFalse2)
	elif Par == 'Categorical Miss':
		Par_arr1 = 1-result_1[:,:,9]
		Par_arr2 = 1-result_2[:,:,9]
	elif Par == 'VMI':
		sumMiss1 = result_1[:,:,4]
		sumSimhit1 = result_1[:,:,6]
		Par_arr1 = np.divide(sumMiss1, sumSimhit1+sumMiss1)
		sumMiss2 = result_2[:,:,4]
		sumSimhit2 = result_2[:,:,6]
		Par_arr2 = np.divide(sumMiss2, sumSimhit2+sumMiss2)
	elif Par == 'CSI':
		NoHit1 = result_1[:,:,1]
		NoMiss1 = result_1[:,:,3]
		NoFalse1 = result_1[:,:,2]
		Par_arr1 = np.divide(NoHit1, NoHit1+NoMiss1+NoFalse1)
		NoHit2 = result_2[:,:,1]
		NoMiss2 = result_2[:,:,3]
		NoFalse2 = result_2[:,:,2]
		Par_arr2 = np.divide(NoHit2, NoHit2+NoMiss2+NoFalse2)
	elif Par == 'VCSI':
		sumFalse1 = result_1[:,:,5]
		sumSimhit1 = result_1[:,:,6]
		sumMiss1 = result_1[:,:,4]
		Par_arr1 = np.divide(sumSimhit1, sumSimhit1+sumMiss1+sumFalse1)
		sumFalse2 = result_2[:,:,5]
		sumSimhit2 = result_2[:,:,6]
		sumMiss2 = result_2[:,:,4]
		Par_arr2 = np.divide(sumSimhit2, sumSimhit2+sumMiss2+sumFalse2)
	PlotMap1(Par_arr1, Par+'1', extend, temp_folder, Par, Par_arr2, Par+'2')

#plot result images
PlotMap2(ref_acc_mask, DataRef, obs_acc1_mask, Data1, extend, time_step, temp_folder, obs_acc2_mask, Data2)
os.system('cp '+temp_folder+'/* '+result_folder)