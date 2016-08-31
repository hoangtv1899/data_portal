#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import subprocess
import os
import sys
import ogr

id = sys.argv[1]
shapefile = sys.argv[2]
infile = sys.argv[3]
outfile = sys.argv[4]
outfile1 = '/var/www/html/voxtests/CHRSData/userFile/temp/temp.tif'

#read old shapes
list_name = open('/var/www/html/voxtests/CHRSData/shapes/names.txt', "rb")
names_old = list_name.readlines()
names = []
for i in names_old:
	names.append(i[:-1])

list_name.close()

# load the shape file as a layer
drv = ogr.GetDriverByName('ESRI Shapefile')
shapes = drv.Open(shapefile)
layer = shapes.GetLayer(0)

shp_name = (shapefile.split('/'))[-1]
if shp_name == 'boundary.shp':
	prop = 'NA2'
elif shp_name == 'pol_divisions.shp':
	prop = 'NAM'
elif shp_name[:6] == 'basins':
	prop = 'HYBAS_ID'
else:
	print 'please select boundary, pol_division or basins shapefiles...'
	sys.exit()

#select feature
filter = prop + " = '"+ id+"'"
layer.SetAttributeFilter(filter)

for feat in layer:
	geom = feat.GetGeometryRef()

if ' ' in id:
	id = id.replace(' ', '_')


list_name = open('/var/www/html/voxtests/CHRSData/shapes/names.txt', "a")
list_name.write(id+'\n')
list_name.close()
# Save extent to a new Shapefile
outShapefile = '/var/www/html/voxtests/CHRSData/shapes/'+id+'.shp'
outDriver = ogr.GetDriverByName("ESRI Shapefile")

# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
	outDriver.DeleteDataSource(outShapefile)

	# Create the output shapefile
outDataSource = outDriver.CreateDataSource(outShapefile)
outLayer = outDataSource.CreateLayer("shape", geom_type=ogr.wkbPolygon)

	# Add an ID field
idField = ogr.FieldDefn("id", ogr.OFTInteger)
outLayer.CreateField(idField)

	# Create the feature and set values
featureDefn = outLayer.GetLayerDefn()
feature = ogr.Feature(featureDefn)
feature.SetGeometry(geom)
feature.SetField("id", 1)
outLayer.CreateFeature(feature)

	# Close DataSource
outDataSource.Destroy()


#subset raster:
cmd1 = "/usr/local/epd-7.3-2-rh5-x86_64/bin/gdalwarp -overwrite -dstnodata -99 -q -cutline /var/www/html/voxtests/CHRSData/shapes/"+id+".shp -crop_to_cutline -of GTiff "+infile+" "+outfile1+" -co COMPRESS=LZW"
subprocess.Popen(cmd1, shell=True).communicate()
cmd2 = '/usr/local/epd-7.2-2-rh5-x86_64/bin/gdal_translate -of AAIGrid '+outfile1+' '+outfile
subprocess.Popen("{}; {}".format(cmd1, cmd2), shell=True, executable="/bin/bash").communicate()
