#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import subprocess
import os
import sys
import time
import shutil
import zipfile
from datetime import datetime, timedelta
from dateutil import rrule
import calendar

curr1 = time.gmtime()
curr = time.mktime(curr1)
curr_str = str(curr)[:-2]

date_start = sys.argv[1]
date_end = sys.argv[2]
time_step = sys.argv[3]
file_type = sys.argv[4]
dataset = sys.argv[5]
outfile = sys.argv[6]
compression = sys.argv[7]
lat = sys.argv[8]
lon = sys.argv[9]

if not os.path.exists('../userFile/temp/'):
    os.makedirs('../userFile/temp/')
if not os.path.exists('../userFile/temp/shapes/'):
    os.makedirs('../userFile/temp/shapes/')
temp_folder0 = '../userFile/temp/'+curr_str+'/'
#
os.makedirs(temp_folder0)
temp_file = '/mnt/t/disk2/pconnect/CHRSData/userFile/temp.vrt'
if dataset == 'CDR':
	if len(date_start) == 8:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/"+time_step+"_asc/CDR_{"+date_start+".."+date_end+"}z.asc 2>/dev/null"
	elif len(date_start) == 6:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/"+time_step+"_asc/CDR_{"+date_start+".."+date_end+"}.asc 2>/dev/null"
	elif len(date_start) == 4:
		path_to_file = "/mnt/p/diske/rainsphere/cdr/"+time_step+"_asc/CDR_{"+date_start+".."+date_end+"}.asc 2>/dev/null"

elif dataset in ['CCS', 'PERSIANN']:
	timestepAlt = sys.argv[10]
	if dataset == 'CCS':
		bpath = "/mnt/t/disk3/CHRSdata/Persiann_CCS/"
	else:
		bpath = "/mnt/t/disk3/CHRSdata/Persiann/"
	path_to_file = bpath+time_step+"/"+dataset+"_"+timestepAlt+"{"+date_start+".."+date_end+"}.tif 2>/dev/null"

if dataset == 'CDR':
	command = "echo 'Time, Rain(mm), Latitude, "+lat+", Longitude, "+lon+",' >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv"
	#command1 = "for b in `ls "+path_to_file+"`; do t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");echo ${t%.*},$v, >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv; done"
	if len(date_start) == 8:
		#command1 = "current=$(date -d \""+date_start+"\" +%Y%m%d); end=$(date -d \""+date_end+" +1 days\" +%Y%m%d); while [ \"$end\" != \"$current\" ]; do b=/mnt/p/diske/rainsphere/cdr/daily_asc/CDR_${current}z.asc; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");echo ${t%.*},$v, >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv;  current=$(date -d \"$current +1 days\" +%Y%m%d); done 2>/dev/null"
		command1 = "current=$(date -d \""+date_start+"\" +%Y%m%d); end=$(date -d \""+date_end+" +1 days\" +%Y%m%d); while [ \"$end\" != \"$current\" ]; do b=/mnt/p/diske/rainsphere/cdr/daily_asc/CDR_${current}z.asc; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");printf \"%s, %.3f\n\" ${t%.*} $v >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv;  current=$(date -d \"$current +1 days\" +%Y%m%d); done 2>/dev/null"
	elif len(date_start) == 6:
		date_start1 = date_start+"01"
		date_end1 = date_end+"01"
		command1 = "current=$(date -d \""+date_start1+"\" +%Y%m%d); end=$(date -d \""+date_end1+" +1 months\" +%Y%m%d); while [ \"$end\" != \"$current\" ]; do b=/mnt/p/diske/rainsphere/cdr/monthly_asc/CDR_${current:0:6}.asc; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");printf \"%s, %.3f\n\" ${t%.*} $v >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv;  current=$(date -d \"$current +1 months\" +%Y%m%d); done 2>/dev/null"
	elif len(date_start) == 4:
		date_start1 = date_start+"0101"
		date_end1 = date_end+"0101"
		command1 = "current=$(date -d \""+date_start1+"\" +%Y%m%d); end=$(date -d \""+date_end1+" +1 years\" +%Y%m%d); while [ \"$end\" != \"$current\" ]; do b=/mnt/p/diske/rainsphere/cdr/yearly_asc/CDR_${current:0:4}.asc; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");printf \"%s, %.3f\n\" ${t%.*} $v >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv;  current=$(date -d \"$current +1 years\" +%Y%m%d); done 2>/dev/null"
	#command = "echo $(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+") >> "+temp_folder0+date_start+"_"+date_end+".csv"

elif dataset == 'CCS':
	command = "echo 'Time, Rain(mm), Latitude, "+lat+", Longitude, "+lon+",' >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv"
	#command1 = "for b in `ls "+path_to_file+"`; do t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");echo ${t%.*},$v, >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv; done"
	if len(date_start) == 10:
		if timestepAlt == '1h':
			addedHour = "1"
		elif timestepAlt == '3h':
			addedHour = "3"
		elif timestepAlt == '6h':
			addedHour = "6"
		command1 = "current=$(date -d \""+date_start[:-2]+" "+date_start[-2:]+"\" +%Y%m%d%H); end=$(date -d \""+date_end[:-2]+" "+date_end[-2:]+" +"+addedHour+" hour\" +%Y%m%d%H); while [ \"$end\" != \"$current\" ]; do b=/mnt/t/disk3/CHRSdata/Persiann_CCS/"+timestepAlt+"rly/CCS_"+timestepAlt+"${current}.tif; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");echo ${t%.*},$v, >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv; t=${current:0:8}; s=${current:8:10}; current=$(date -d \"$t $s +"+addedHour+" hour\" +%Y%m%d%H); done 2>/dev/null"
	elif len(date_start) == 8:
		command1 = "current=$(date -d \""+date_start+"\" +%Y%m%d); end=$(date -d \""+date_end+" +1 days\" +%Y%m%d); while [ \"$end\" != \"$current\" ]; do b=/mnt/t/disk3/CHRSdata/Persiann_CCS/daily/CCS_1d${current}.tif; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");printf \"%s, %.3f\n\" ${t%.*} $v >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv; current=$(date -d \"$current +1 days\" +%Y%m%d); done 2>/dev/null"

elif dataset == 'PERSIANN':
	command = "echo 'Time, Rain(mm), Latitude, "+lat+", Longitude, "+lon+",' >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv"
	#command1 = "for b in `ls "+path_to_file+"`; do t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");echo ${t%.*},$v, >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv; done"
	if len(date_start) == 10:
		if timestepAlt == '1h':
			addedHour = "1"
		elif timestepAlt == '3h':
			addedHour = "3"
		elif timestepAlt == '6h':
			addedHour = "6"
		command1 = "current=$(date -d \""+date_start[:-2]+" "+date_start[-2:]+"\" +%Y%m%d%H); end=$(date -d \""+date_end[:-2]+" "+date_end[-2:]+" +"+addedHour+" hour\" +%Y%m%d%H); while [ \"$end\" != \"$current\" ]; do b=/mnt/t/disk3/CHRSdata/Persiann/"+timestepAlt+"rly/PERSIANN_"+timestepAlt+"${current}.tif; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");printf \"%s, %.3f\n\" ${t%.*} $v >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv; t=${current:0:8}; s=${current:8:10}; current=$(date -d \"$t $s +"+addedHour+" hour\" +%Y%m%d%H); done 2>/dev/null"
	elif len(date_start) == 8:
		command1 = "current=$(date -d \""+date_start+"\" +%Y%m%d); end=$(date -d \""+date_end+" +1 days\" +%Y%m%d); while [ \"$end\" != \"$current\" ]; do b=/mnt/t/disk3/CHRSdata/Persiann/daily/PERSIANN_"+timestepAlt+"${current}.tif; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");printf \"%s, %.3f\n\" ${t%.*} $v >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv;  current=$(date -d \"$current +1 days\" +%Y%m%d); done 2>/dev/null"
	elif len(date_start) == 6:
		date_start1 = date_start+"01"
		date_end1 = date_end+"01"
		command1 = "current=$(date -d \""+date_start1+"\" +%Y%m%d); end=$(date -d \""+date_end1+" +1 months\" +%Y%m%d); while [ \"$end\" != \"$current\" ]; do b=/mnt/t/disk3/CHRSdata/Persiann/monthly/PERSIANN_"+timestepAlt+"${current:0:6}.tif; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");printf \"%s, %.3f\n\" ${t%.*} $v >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv;  current=$(date -d \"$current +1 months\" +%Y%m%d); done 2>/dev/null"
	elif len(date_start) == 4:
		date_start1 = date_start+"0101"
		date_end1 = date_end+"0101"
		command1 = "current=$(date -d \""+date_start1+"\" +%Y%m%d); end=$(date -d \""+date_end1+" +1 years\" +%Y%m%d); while [ \"$end\" != \"$current\" ]; do b=/mnt/t/disk3/CHRSdata/Persiann/yearly/PERSIANN_"+timestepAlt+"${current:0:4}.tif; t=$(basename ${b##*_}); v=$(/usr/local/bin/gdallocationinfo -geoloc -valonly $b "+str(lon)+" "+str(lat)+");printf \"%s, %.3f\n\" ${t%.*} $v >> "+temp_folder0+dataset+"_"+date_start+"_"+date_end+".csv;  current=$(date -d \"$current +1 years\" +%Y%m%d); done 2>/dev/null"

subprocess.Popen("{}; {}".format(command, command1), shell=True, executable="/bin/bash").communicate()
#subprocess.Popen(command1, shell=True, executable="/bin/bash").communicate()
shutil.make_archive(outfile, format=compression, root_dir=temp_folder0)

shutil.rmtree(temp_folder0)
