#This python function reads NetCDF files downloaded from CHRS Data Portal (http://chrsdata.eng.uci.edu/)
#netCDF4 and collections libraries are required

from netCDF4 import Dataset
from collections import OrderedDict

def read_netcdf(netcdf_file):
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