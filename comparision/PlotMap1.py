#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import numpy as np
import math
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import matplotlib as mpl
mpl.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import multiprocessing
import itertools

def PlotMap1(sim, sim_name, extend, temp_folder, Par, obs=None, obs_name=None):
	pool = multiprocessing.Pool(processes = 16)
	# define the bins and normalize
	if Par == 'BIAS':
		bounds = np.array([-99., 0., .2, .4, .6, .8, 1., 1.2, 1.4, 1.6, 1.8, 2.])
	else:
		bounds = np.array([-99., 0., .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.])
	# define the colormap
	cpool = [ '#7D7D7D', '#FFFFFF', '#90FF70', '#6DFF9C', '#3AFFC5', '#0BFFF8', '#00DCFF', '#0883FA', '#0156FE', '#0000FB', '#0001C2', '#00028A']
	cmap0 = mpl.colors.ListedColormap(cpool, 'indexed')
	mpl.cm.register_cmap(cmap=cmap0)
	# create the new map
	norm = mpl.colors.BoundaryNorm(bounds, cmap0.N)
	#flatten arrays
	masked_sim = np.ma.masked_where((np.isnan(sim)) | (sim == np.inf) | (sim == -np.inf), sim)
	masked_sim = masked_sim.filled(-99)
	if obs_name:
		masked_obs = np.ma.masked_where((np.isnan(obs)) | (obs == np.inf) | (obs == -np.inf), obs)
		masked_obs = masked_obs.filled(-99)
		if np.max(masked_sim) > np.max(masked_obs):
			v_max = math.ceil(np.max(masked_sim))
			extend_arr = [extend, extend]
			field_arr = [masked_sim, masked_obs]
			vmin_arr = [0., 0.]
			vmax_arr = [v_max, v_max]
			cmap_arr = [cmap0, cmap0]
			norm_arr = [norm, norm]
			bound_arr = [bounds, bounds]
			name1_arr = [sim_name, obs_name]
			temp_arr = [temp_folder, temp_folder]
			arg_arr = itertools.izip(extend_arr, field_arr, vmin_arr, vmax_arr, cmap_arr, norm_arr, bound_arr, name1_arr, temp_arr)
			pool.map(PlotColorMesh1, arg_arr)
		else:
			v_max = math.ceil(np.max(masked_obs))
			field_arr = [masked_obs, masked_sim]
			extend_arr = [extend, extend]
			vmin_arr = [0., 0.]
			vmax_arr = [v_max, v_max]
			cmap_arr = [cmap0, cmap0]
			norm_arr = [norm, norm]
			bound_arr = [bounds, bounds]
			name1_arr = [obs_name, sim_name]
			temp_arr = [temp_folder, temp_folder]
			arg_arr = itertools.izip(extend_arr, field_arr, vmin_arr, vmax_arr, cmap_arr, norm_arr, bound_arr, name1_arr, temp_arr)
			pool.map(PlotColorMesh1, arg_arr)
	else:
		v_max = math.ceil(np.max(masked_sim))
		PlotColorMesh(extend, masked_sim, 0., v_max, cmap0, norm, bounds, sim_name, temp_folder)

def PlotColorMesh1(args):
	PlotColorMesh(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8])

def PlotColorMesh(extend, scalar_field, v_min, v_max, cmap, norm, bounds, xname,temp_folder):
	fig = plt.figure(dpi=5000)
	ax = plt.subplot(111)
	ticks_font = mpl.font_manager.FontProperties(family='Helvetica', style='normal', weight='light', stretch='normal', size='x-small')
	lons = np.arange(extend[0], extend[1], 0.25)
	lats = np.arange(extend[2], extend[3], -1*0.25)
	lons, lats = np.meshgrid(lons,lats)
	map = Basemap(projection='mill',llcrnrlat=extend[3]-0.005,urcrnrlat=extend[2]+0.005,\
            llcrnrlon=extend[0]-0.005,urcrnrlon=extend[1]+0.005,resolution='c')
	parallels = np.arange(extend[3],extend[2]+1,math.ceil((extend[2]+1 - extend[3])/(60.))*10.)
	if len(parallels) < 3:
		parallels = np.array([extend[3], extend[2]])
	try:
		map.drawparallels(parallels,labels=[False,True,False,False], linewidth=.2, fontsize=10)
	except Exception as e:
		parallels = np.array([int(k) for k in parallels])
		map.drawparallels(parallels,labels=[False,True,False,False], linewidth=.2, fontsize=10)
	meridians = np.arange(extend[0],extend[1]+1,math.ceil((extend[1]+1 - extend[0])/(90.))*10.)
	if len(meridians) < 3:
		meridians = np.array([extend[0], extend[1]])
	map.drawmeridians(meridians,labels=[False,False,False,True], linewidth=.2, fontsize=10)
	map.drawcoastlines(linewidth=1, color='yellow', zorder=2)
	map.drawcountries(linewidth=.8, color='yellow', zorder=3)
	xx, yy = map(lons, lats)
	cs = map.pcolormesh(xx, yy, scalar_field, cmap=cmap, norm=norm, zorder = 1)
	if (extend[1] - extend[0]) > (extend[2] - extend[3]):
		cb = map.colorbar(cs, pad='15%', location='bottom', norm=norm, ticks=bounds)
		labels = [item.get_text() for item in cb.ax.get_xticklabels()]
		labels[0] = 'no data'
		cb.ax.set_xticklabels(labels, ticks_font, rotation = 30)
	else:
		cb = map.colorbar(cs, pad='15%', norm=norm, ticks=bounds)
		labels = [item.get_text() for item in cb.ax.get_yticklabels()]
		labels[0] = 'no data'
		cb.ax.set_yticklabels(labels, ticks_font)
	fig.savefig(temp_folder+xname+'.png', transparent=True)
	plt.close()