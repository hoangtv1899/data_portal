#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import shutil
import multiprocessing
import itertools
from asc_format_ccs1 import AscFormat

curr_str = sys.argv[1]
date_start = sys.argv[2]
date_end = sys.argv[3]
time_step = sys.argv[4]
file_type = sys.argv[5]
dataset = sys.argv[6]
outfile = sys.argv[7]
compression = sys.argv[8]
timestepAlt = sys.argv[9]

temp_folder0 = '../userFile/temp/'+curr_str+'/'

temp_file = '/mnt/t/disk2/pconnect/CHRSData/userFile/temp.vrt'

if dataset == 'CDR':
	if len(date_start) == 8:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/daily/CDR_{"+date_start+".."+date_end+"}z.tif 2>/dev/null"
	elif len(date_start) == 6:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/monthly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"
	elif len(date_start) == 4:
		path_to_file = "/mnt/t/disk3/CHRSdata/Persiann_CDR/yearly/CDR_{"+date_start+".."+date_end+"}.tif 2>/dev/null"
elif dataset in ['CCS', 'PERSIANN']:
	if dataset == 'CCS':
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
	else:
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"
	
pool = multiprocessing.Pool(processes = 4)
if file_type == 'ArcGrid':
	list_file = [file1.replace('\n','') for file1 in os.popen('ls '+path_to_file).readlines()]
	dataset_arr = itertools.repeat(dataset, len(list_file))
	list_dest_file = [temp_folder0+os.path.splitext(os.path.basename(file2))[0]+'.asc' for file2 in list_file]
	pool.map(AscFormat, itertools.izip(list_file, list_dest_file, dataset_arr))
	shutil.make_archive(outfile, format=compression, root_dir=temp_folder0)
elif file_type == 'Tif':
	os.system("for b in `ls "+path_to_file+"`; do cp $b "+temp_folder0+"$(basename ${b%.*}).tif; done")
	shutil.make_archive(outfile, format=compression, root_dir=temp_folder0)
 