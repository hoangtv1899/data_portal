#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import sys
import os
import glob
import numpy as np
from ValidationFunction import ValidationFunction
from PlotMap import PlotMap, PlotColorMesh
from ShapeSelection import ShapeSelection
from osgeo import gdal, ogr
import json

fileIn1 = sys.argv[1]
fileIn2 = sys.argv[2]
time_step = sys.argv[3]

#file name
sim_name = os.path.splitext(os.path.basename(fileIn1))[0]
obs_name = os.path.splitext(os.path.basename(fileIn2))[0]
if 'CDR' in sim_name:
	sim_name = 'PERSIANN-CDR'
elif 'CCS' in sim_name:
	sim_name = 'PERSIANN-CCS'
elif 'PERSIANN' in sim_name:
	sim_name = 'PERSIANN'
elif 'mst2' in sim_name:
	sim_name = 'Radar Stage II'

if 'CDR' in obs_name:
	obs_name = 'PERSIANN-CDR'
elif 'CCS' in obs_name:
	obs_name = 'PERSIANN-CCS'
elif 'PERSIANN' in obs_name:
	obs_name = 'PERSIANN'
elif 'mst2' in obs_name:
	obs_name = 'Radar Stage II'

try:
	extend = sys.argv[4]
	extend = extend[1:-1].split(",")
	if len(extend) == 2: 
		shape = sys.argv[5]
		shape_in = ShapeSelection(extend, shape)
		shp_in = ogr.Open(shape_in)
		shp_layer = shp_in.GetLayer()
		shp_extents = shp_layer.GetExtent()
		if (sim_name == 'PERSIANN-CDR' or sim_name == 'PERSIANN'):
			[xmin1, xmax1, ymin1, ymax1] = np.ceil(shp_extents) + np.ceil((shp_extents - np.ceil(shp_extents))/0.25) *0.25 + [-0.25, 0.25, -0.25, 0.25]
			if ymin1 >= 60:
				sys.exit()
			elif ymax1 >= 60:
				ymax1 = 60
		p = [xmin1, ymin1, xmax1, ymax1]
		extend = [xmin1, xmax1, ymax1, ymin1]
		p1 = map(str, p)
		os.system('/usr/local/bin/gdalwarp -q -overwrite -dstnodata -99 -cutline '+shape_in+' -of GTiff -te '+' '.join(p1)+' '+fileIn1+' tempdata/'+os.path.basename(fileIn1))
		sim_im = gdal.Open('tempdata/'+os.path.basename(fileIn1))
		os.system('/usr/local/bin/gdalwarp -q -overwrite -dstnodata -99 -cutline '+shape_in+' -of GTiff -te '+' '.join(p1)+' '+fileIn2+' tempdata/'+os.path.basename(fileIn2))
		obs_im = gdal.Open('tempdata/'+os.path.basename(fileIn2))
	elif len(extend) == 4:
	#clip raster by extends
		extend = [float(x) for x in extend]
		os.system('gdal_translate -a_nodata -99 -projwin '+str(extend[0])+' '+str(extend[2])+' '+str(extend[1])+' '+str(extend[3])+' -of GTiff '+fileIn1+' tempdata/'+os.path.basename(fileIn1))
		sim_im = gdal.Open('tempdata/'+os.path.basename(fileIn1))
		os.system('gdal_translate -a_nodata -99 -projwin '+str(extend[0])+' '+str(extend[2])+' '+str(extend[1])+' '+str(extend[3])+' -of GTiff '+fileIn2+' tempdata/'+os.path.basename(fileIn2))
		obs_im = gdal.Open('tempdata/'+os.path.basename(fileIn2))
except:
	extend = [-180, 180, 60, -60]
	sim_im = gdal.Open(fileIn1)
	obs_im = gdal.Open(fileIn2)

#Masking data	
sim = sim_im.ReadAsArray()
obs = obs_im.ReadAsArray()
sim_mask = np.ma.masked_where(sim==-99, sim)
obs_mask = np.ma.masked_where(obs==-99, obs)
	
#get the statistics		
result = ValidationFunction(sim_mask, obs_mask)
with open('result.json', 'w') as fp:
	json.dump(result, fp)
#plot result images
steps = sim_im.GetGeoTransform()[1]
PlotMap(sim_mask, sim_name, obs_mask, obs_name, extend, steps, time_step)

#delete temp files
temp_files = glob.glob('tempdata/*')
for f in temp_files:
	os.remove(f)
temp_files1 = glob.glob('shapes/*')
for f in temp_files1:
	os.remove(f)