#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import sys
import glob

loc = sys.argv[1]
time_range = sys.argv[2]
dataset = sys.argv[3]
time_step = sys.argv[4]


if time_step == 'daily':
	timestepAlt = '1d'
elif time_step == 'monthly':
	timestepAlt = '1m'
elif time_step == 'yearly':
	timestepAlt = '1y'

loc1 = loc[1:-1].replace(',', ' ')
date_start, date_end = [x.replace(' ','') for x in time_range[1:-1].split(',')]
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

command = "for b in `ls "+path_to_file+"`; do echo `gdallocationinfo -geoloc $b "+loc1+" | grep \"Value:\" | cut -d ':' -f 2` mm; done"

os.system(command)