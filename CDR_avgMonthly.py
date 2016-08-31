#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import sys
import numpy as np
import gdal
import subprocess

for num in ['01','02','03','04','05','06','07','08','09','10','11','12']:
	command1 = "/usr/local/epd-7.2-2-rh5-x86_64/bin/gdalbuildvrt -separate tempdata/"+num+".vrt /mnt/t/disk3/CHRSdata/Persiann_CDR/monthly/CDR_*"+num+".tif"
	subprocess.Popen(command1, shell=True, executable="/bin/bash").communicate()
	ds = gdal.Open('tempdata/'+num+'.vrt')
	a = ds.ReadAsArray().astype('float')
	n_yr = a.shape[0]
	a[a == -99] = 'nan'
	b = np.nansum(a, axis = 0)
	b1 = b/float(n_yr)
	b1[np.isnan(b1)] = -99
	header = "ncols     %s\n" % 1440
	header += "nrows    %s\n" % 480
	header += "xllcorner %s\n" % -180
	header += "yllcorner %s\n" % -60
	header += "cellsize %.2f\n" % 0.25
	header += "NODATA_value -99\n"
	f = open('tempdata/'+num+'.asc', "w")
	f.write(header)
	np.savetxt(f, b1, fmt="%.2f")
	f.close()