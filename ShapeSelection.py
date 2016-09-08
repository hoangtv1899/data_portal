#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import numpy as np
from osgeo import ogr
from shapely.wkt import loads
import sys
import itertools
import multiprocessing

def ShapeSelection(loc, shape, tmp_shp):
	pool = multiprocessing.Pool(processes = 4)
	#create a point
	point = ogr.Geometry(ogr.wkbPoint)
	point.AddPoint(float(loc[0]), float(loc[1]))
	p1 = loads(point.ExportToWkt())
	#open shapefile
	shp = ogr.Open(shape)
	layer = shp.GetLayer()
	shp_name = os.path.splitext(os.path.basename(shape))[0]
	if shp_name == 'country_fusion':
		prop = 'FIPS_CNTRY'
	elif shp_name == 'pol_divisions':
		prop = 'NAM'
	elif shp_name[:6] == 'basins':
		prop = 'HYBAS_ID'
	results = pool.map(FindFeature, itertools.izip(itertools.repeat(prop, len(layer)), itertools.repeat(p1, len(layer)),range(len(layer)), itertools.repeat(shape, len(layer)), itertools.repeat(tmp_shp, len(layer))))
	try:
		out_shape = [k1 for k1 in results if k1 is not None][0]
		if out_shape:
			return out_shape
		else:
			print 'no matching shapefile'
			quit()
	except:
		print 'not in domain'
		quit()

def FindFeature(args):
	prop = args[0]
	p1 = args[1]
	i = args[2]
	shape = args[3]
	tmp_shp = args[4]
	#create an output shapefile
	driver = ogr.GetDriverByName('ESRI Shapefile')
	# Add an ID field
	idField = ogr.FieldDefn("id", ogr.OFTInteger)
	shp = ogr.Open(shape)
	layer = shp.GetLayer()
	feat = layer.GetFeature(i)
	geom = feat.GetGeometryRef()
	p2 = loads(geom.ExportToWkt())
	if p1.intersects(p2):
		feat_name = feat.GetField(prop)
		if prop == 'HYBAS_ID':
			feat_name = str(int(feat_name))
		if ' ' in feat_name:
			feat_name = feat_name.replace(' ','_')
		out_shape = tmp_shp+feat_name+'.shp'
		if os.path.isfile(out_shape):
			os.system("rm -f "+tmp_shp+feat_name+".*")
		out_shp = driver.CreateDataSource(out_shape)
		out_layer = out_shp.CreateLayer(prop, geom_type=ogr.wkbPolygon)
		out_layer.CreateField(idField)
		out_feat = ogr.Feature(out_layer.GetLayerDefn())
		out_feat.SetGeometry(geom)
		out_feat.SetField('id',1)
		out_layer.CreateFeature(out_feat)
		out_shp.Destroy()
		return out_shape