#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

from netCDF4 import Dataset
from collections import OrderedDict

def read_cdf(netcdf_file):
	contents = OrderedDict()
	data = Dataset(netcdf_file, 'r')
	for var in data.variables:
		attrs = data.variables[var].ncattrs()
		if attrs:
			for attr in attrs:
				print '\t\t%s:' % attr,\
                      repr(data.variables[var].getncattr(attr))
		contents[var] = data.variables[var][:]
	return contents