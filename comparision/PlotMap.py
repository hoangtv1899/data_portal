#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import numpy as np
import math
import matplotlib as mpl
mpl.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import multiprocessing
import itertools
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import traceback
import logging

def PlotMap(sim, sim_name, obs, obs_name, extend, steps, time_type):
	pool = multiprocessing.Pool(processes = 4)
	# define the bins and normalize
	if time_type == 'yearly':
		bounds = np.array([-99., 0., 30., 60., 90., 120., 150., 210., 300., 375., 450., 600., 750., 900., 1050., 1200., 1500., 2250., 3000., 3750., 4500., 6000., 9000., 12000., 15000., 18000., 20000.])
		bounds1 = np.linspace(-2000,2000, 21)
		sc1 = 1000.
		sc2 = 200.
	elif time_type == 'monthly':
		bounds = np.array([-99., 0., 15., 30., 45., 60., 75., 105., 150., 195., 225., 300., 375., 450., 525., 600., 750., 1125., 1500., 1875., 2250., 3000., 4500., 6000., 7500., 9000., 11000.])
		bounds1 = np.linspace(-300,300, 21)
		sc1 = 300.
		sc2 = 100.
	elif time_type in ['daily', 'hourly']:
		bounds = np.array([-99., 0., 1., 2., 3., 4., 5., 7., 10., 13., 15., 20., 25., 30., 35., 40., 50., 75., 100., 125., 150., 200., 300., 400., 500., 600., 800])
		bounds1 = np.linspace(-20,20, 21)
		sc1 = 10.
		sc2 = 10.
	# define the colormap
	cpool = [ '#7D7D7D', '#FFFFFF', '#00028A', '#0001C2', '#0000FB', '#0156FE',
		'#0883FA', '#00DCFF', '#0BFFF8', '#3AFFC5', '#6DFF9C',
		'#90FF70', '#C0FF4A', '#F2FF11', '#FFE400', '#FFB400', 
		'#F89400', '#FC6100', '#FF2D05', '#E60000', '#C80000', 
		'#A00028', '#6E0028', '#460019', '#320014', '#0A0002', '#F7AAED']
	cmap0 = mpl.colors.ListedColormap(cpool, 'indexed')
	mpl.cm.register_cmap(cmap=cmap0)
	cmap1 = plt.cm.BrBG
	# create the new map
	norm = mpl.colors.BoundaryNorm(bounds, cmap0.N)
	norm1 = mpl.colors.BoundaryNorm(bounds1, cmap1.N)
	#flatten arrays
	x = sim.flatten('C')
	y = obs.flatten('C')
	#array of difference
	c = sim-obs
	v_maxC = math.ceil(np.max(c)/sc2)*sc2
	v_minC = math.floor(np.min(c)/sc2)*sc2
	masked_c = np.ma.masked_where(c == 0, c)
	masked_sim = np.ma.masked_where(sim.filled(-99) == 0, sim.filled(-99))
	masked_obs = np.ma.masked_where(obs.filled(-99) == 0, obs.filled(-99))
	#scatter plot
	if np.max(sim) > np.max(obs):
		v_max = math.ceil(np.max(sim)/sc1)*sc1
		extend_arr = [extend, extend, extend]
		step_arr = [steps, steps, steps]
		field_arr = [masked_sim, masked_obs, masked_c]
		vmin_arr = [0., 0., v_minC]
		vmax_arr = [v_max, v_max, v_maxC]
		cmap_arr = [cmap0, cmap0, cmap1]
		norm_arr = [norm, norm, norm1]
		bound_arr = [bounds, bounds, bounds1]
		name1_arr = [sim_name, obs_name, sim_name+' vs '+obs_name]
		name2_arr = [obs_name, sim_name, None]
		x_arr = [x, y, None]
		y_arr = [y, x, None]
		arg_arr = itertools.izip(extend_arr, step_arr, field_arr, vmin_arr, vmax_arr, cmap_arr, norm_arr, bound_arr, name1_arr, name2_arr, x_arr, y_arr)
		pool.map(PlotColorMesh1, arg_arr)
	else:
		v_max = math.ceil(np.max(obs)/sc1)*sc1
		extend_arr = [extend, extend, extend]
		step_arr = [steps, steps, steps]
		field_arr = [masked_obs, masked_sim, masked_c]
		vmin_arr = [0., 0., v_minC]
		vmax_arr = [v_max, v_max, v_maxC]
		cmap_arr = [cmap0, cmap0, cmap1]
		norm_arr = [norm, norm, norm1]
		bound_arr = [bounds, bounds, bounds1]
		name1_arr = [obs_name, sim_name, obs_name+' vs '+sim_name]
		name2_arr = [sim_name, obs_name, None]
		x_arr = [y, x, None]
		y_arr = [x, y, None]
		arg_arr = itertools.izip(extend_arr, step_arr, field_arr, vmin_arr, vmax_arr, cmap_arr, norm_arr, bound_arr, name1_arr, name2_arr, x_arr, y_arr)
		pool.map(PlotColorMesh1, arg_arr)


def PlotColorMesh1(args):
	PlotColorMesh(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], args[10], args[11])

def PlotColorMesh(extend, steps, scalar_field, v_min, v_max, cmap, norm, bounds, xname, yname=None, x=None, y=None):
	fig = plt.figure(dpi=5000)
	ax = plt.subplot(111)
	ticks_font = mpl.font_manager.FontProperties(family='Helvetica', style='normal', weight='light', stretch='normal', size='x-small')
	plt.title(xname.upper(), fontsize = 20, fontweight = 'bold')
	lons = np.arange(extend[0], extend[1], steps)
	lats = np.arange(extend[2], extend[3], -1*steps)
	lons, lats = np.meshgrid(lons,lats)
	map = Basemap(projection='mill',llcrnrlat=extend[3]-0.005,urcrnrlat=extend[2]+0.005,\
            llcrnrlon=extend[0]-0.005,urcrnrlon=extend[1]+0.005,resolution='c')
	parallels = np.arange(extend[3],extend[2]+1,math.ceil((extend[2] - extend[3])/(60.))*10.)
	if len(parallels) < 3:
		parallels = np.array([extend[3], extend[2]])
	try:
		map.drawparallels(parallels,labels=[False,True,False,False], linewidth=.2, fontsize=10)
	except Exception as e:
		parallels = np.array([int(k) for k in parallels])
		map.drawparallels(parallels,labels=[False,True,False,False], linewidth=.2, fontsize=10)
	meridians = np.arange(extend[0],extend[1]+1,math.ceil((extend[1] - extend[0])/(90.))*10.)
	if len(meridians) < 3:
		meridians = np.array([extend[0], extend[1]])
	map.drawmeridians(meridians,labels=[False,False,False,True], linewidth=.2, fontsize=10)
	map.drawcoastlines(linewidth=.5, color='yellow', zorder=2)
	map.drawcountries(linewidth=.5, color='yellow', zorder=3)
	xx, yy = map(lons, lats)
	cs = map.pcolormesh(xx, yy, scalar_field, cmap=cmap, norm=norm, zorder = 1)
	if yname is not None:
		if (extend[1] - extend[0]) > (extend[2] - extend[3]):
			cb = map.colorbar(cs, pad='15%', location='bottom', norm=norm, ticks=bounds)
			labels = [item.get_text() for item in cb.ax.get_xticklabels()]
			labels[0] = 'no data'
			labels[1] = ' '
			labels[-1] = '>'+labels[-2]
			cb.ax.set_xticklabels(labels, ticks_font, rotation=30)
			cb.ax.set_xlabel('Rain (mm)', va='bottom', fontweight='bold')
		else:
			cb = map.colorbar(cs, pad='15%', norm=norm, ticks=bounds)
			labels = [item.get_text() for item in cb.ax.get_yticklabels()]
			labels[0] = ' '
			labels[1] = 'no data'
			labels[-1] = '>'+labels[-2]
			cb.ax.set_yticklabels(labels, ticks_font)
			cb.ax.set_ylabel('Rain (mm)', ha = 'right', fontweight='bold')
		axin = inset_axes(ax,width="40%",height="40%", loc=3, borderpad = 1.9)
		axin.plot(x, y, '+', markersize=1, color='0.03' ,zorder = 4)
		axin.plot([v_min, v_max], [v_min, v_max], 'r-', zorder = 5)
		axin.axis([v_min, v_max, v_min, v_max])
		axin.set_title('RAIN (mm)', fontweight='bold', fontsize=8, x=0.5, y=0.82)
		axin.set_xlabel(xname, fontsize=7, fontweight='bold')
		axin.set_ylabel(yname, fontsize=7, fontweight='bold', ha = 'left')
		#axin.yaxis.set_label_coords(0, 1.08)
		#axin.xaxis.set_label_coords(0.5, -0.154)
		axin.tick_params(axis='y', which='both', top='off', left='off', right='off', bottom='off', labelsize=8, pad=0.25)
		axin.tick_params(axis='x', which='both', top='off', left='off', right='off', bottom='off', labelsize=8)
		axin.set_xticks(np.arange(0, int(v_max)+1, int(v_max)/2))
		axin.set_yticks(np.arange(0, int(v_max)+1, int(v_max)/2))
		axin.set_aspect('equal', adjustable='box', anchor='SW')
	else:
		if (extend[1] - extend[0]) > (extend[2] - extend[3]):
			cb = map.colorbar(cs, pad='15%', location='bottom', norm=norm, ticks=bounds)
			labels = [item.get_text() for item in cb.ax.get_xticklabels()]
			cb.ax.set_xticklabels(labels, ticks_font, rotation = 30)
			cb.ax.set_xlabel('Rain (mm)', va='bottom', fontweight='bold')
		else:
			cb = map.colorbar(cs, pad='15%', norm=norm, ticks=bounds)
			labels = [item.get_text() for item in cb.ax.get_yticklabels()]
			cb.ax.set_yticklabels(labels, ticks_font)
			cb.ax.set_ylabel('Rain (mm)', ha = 'right', fontweight='bold')
	fig.savefig(xname+'.png', transparent=True)
	plt.close()