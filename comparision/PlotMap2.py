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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import traceback
import logging

def PlotMap2(obs, obs_name, sim1, sim_name1, extend, time_type, temp_folder, sim2=None, sim_name2=None):
	pool = multiprocessing.Pool(processes = 16)
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
		bounds1 = np.linspace(-15,15, 16)
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
	x = obs.flatten('C')
	y1 = sim1.flatten('C')
	if sim_name2:
		y2 = sim2.flatten('C')
		#array of difference
		c1 = sim1-obs
		c2 = sim2-obs
		c3 = sim2 -sim1
		v_maxC1 = math.ceil(np.max(c1)/sc2)*sc2
		v_minC1 = math.floor(np.min(c1)/sc2)*sc2
		v_maxC2 = math.ceil(np.max(c2)/sc2)*sc2
		v_minC2 = math.floor(np.min(c2)/sc2)*sc2
		v_maxC3 = math.ceil(np.max(c3)/sc2)*sc2
		v_minC3 = math.floor(np.min(c3)/sc2)*sc2
		masked_c1 = np.ma.masked_where(c1 == 0, c1)
		masked_c2 = np.ma.masked_where(c2 == 0, c2)
		masked_c3 = np.ma.masked_where(c3 == 0, c3)
		masked_sim1 = np.ma.masked_where(sim1.filled(-99) == 0, sim1.filled(-99))
		masked_obs = np.ma.masked_where(obs.filled(-99) == 0, obs.filled(-99))
		masked_sim2 = np.ma.masked_where(sim2.filled(-99) == 0, sim2.filled(-99))
	else:
		#array of difference
		c1 = sim1-obs
		v_maxC1 = math.ceil(np.max(c1)/sc2)*sc2
		v_minC1 = math.floor(np.min(c1)/sc2)*sc2
		masked_c1 = np.ma.masked_where(c1 == 0, c1)
		masked_sim1 = np.ma.masked_where(sim1.filled(-99) == 0, sim1.filled(-99))
		masked_obs = np.ma.masked_where(obs.filled(-99) == 0, obs.filled(-99))
	if sim_name2:
		#scatter plot
		if np.max(obs) > max(np.max(sim1), np.max(sim2)):
			v_max = math.ceil(np.max(obs)/sc1)*sc1
		else:
			obsMax = max(np.max(sim1), np.max(sim2))
			v_max = math.ceil(obsMax/sc1)*sc1
		if np.isinf(v_max):
			v_max = 800
		extend_arr = [extend]*6
		field_arr = [masked_obs, masked_sim1, masked_sim2, masked_c1, masked_c2, masked_c3]
		cmap_arr = [cmap0, cmap0, cmap0, cmap1, cmap1, cmap1]
		norm_arr = [norm, norm, norm, norm1, norm1, norm1]
		bound_arr = [bounds, bounds, bounds, bounds1, bounds1, bounds1]
		name1_arr = ['Data0', 'Data1', 'Data2', 'Image1', 'Image2', 'Image3']
		name2_arr = ['Data0', 'Data1', 'Data2', None, None, None]
		temp_arr = [temp_folder]*6
		arg_arr = itertools.izip(temp_arr, extend_arr, field_arr, cmap_arr, norm_arr, bound_arr, name1_arr, name2_arr)
		pool.map(PlotColorMesh1, arg_arr)
		#corr1
		fig = plt.figure()
		plt.plot(x, y1, '+', markersize=1, color='0.03' ,zorder = 4)
		plt.plot([0, v_max], [0, v_max], 'r-', zorder = 5)
		plt.axis([0, v_max, 0, v_max])
		plt.xlabel(obs_name, fontsize=11, fontweight='bold')
		plt.ylabel(sim_name1, fontsize=11, fontweight='bold', ha = 'left',labelpad=15)
		plt.tick_params(axis='y', which='both', top='off', left='off', right='off', bottom='off', labelsize=10, pad=0.25)
		plt.tick_params(axis='x', which='both', top='off', left='off', right='off', bottom='off', labelsize=10)
		plt.xticks(np.linspace(0, int(v_max), 3))
		plt.yticks(np.linspace(0, int(v_max), 3))
		fig.savefig(temp_folder+'Correlation1.png')
		plt.close()
		#corr2
		fig = plt.figure()
		plt.plot(x, y2, '+', markersize=1, color='0.03' ,zorder = 4)
		plt.plot([0, v_max], [0, v_max], 'r-', zorder = 5)
		plt.axis([0, v_max, 0, v_max])
		plt.xlabel(obs_name, fontsize=11, fontweight='bold')
		plt.ylabel(sim_name2, fontsize=11, fontweight='bold', ha = 'left',labelpad=15)
		plt.tick_params(axis='y', which='both', top='off', left='off', right='off', bottom='off', labelsize=10, pad=0.25)
		plt.tick_params(axis='x', which='both', top='off', left='off', right='off', bottom='off', labelsize=10)
		plt.xticks(np.linspace(0, int(v_max), 3))
		plt.yticks(np.linspace(0, int(v_max), 3))
		fig.savefig(temp_folder+'Correlation2.png')
		plt.close()
		#corr3
		fig = plt.figure()
		plt.plot(y2, y1, '+', markersize=1, color='0.03' ,zorder = 4)
		plt.plot([0, v_max], [0, v_max], 'r-', zorder = 5)
		plt.axis([0, v_max, 0, v_max])
		plt.xlabel(sim_name1, fontsize=11, fontweight='bold')
		plt.ylabel(sim_name2, fontsize=11, fontweight='bold', ha = 'left', labelpad=15)
		plt.tick_params(axis='y', which='both', top='off', left='off', right='off', bottom='off', labelsize=10, pad=0.25)
		plt.tick_params(axis='x', which='both', top='off', left='off', right='off', bottom='off', labelsize=10)
		plt.xticks(np.linspace(0, int(v_max), 3))
		plt.yticks(np.linspace(0, int(v_max), 3))
		fig.savefig(temp_folder+'Correlation3.png')
		plt.close()
	else:
		#scatter plot
		if np.max(obs) > np.max(sim1):
			v_max = math.ceil(np.max(obs)/sc1)*sc1
		else:
			obsMax = np.max(sim1)
			v_max = math.ceil(obsMax/sc1)*sc1
		if np.isinf(v_max):
			v_max = 800
		extend_arr = [extend]*3
		field_arr = [masked_obs, masked_sim1, masked_c1]
		cmap_arr = [cmap0, cmap0, cmap1]
		norm_arr = [norm, norm, norm1]
		bound_arr = [bounds, bounds, bounds1]
		name1_arr = ['Data0', 'Data1', 'Image1']
		name2_arr = ['Data0', 'Data1', None]
		temp_arr = [temp_folder]*3
		arg_arr = itertools.izip(temp_arr, extend_arr, field_arr, cmap_arr, norm_arr, bound_arr, name1_arr, name2_arr)
		#corr1
		fig = plt.figure()
		plt.plot(x, y1, '+', markersize=1, color='0.03' ,zorder = 4)
		plt.plot([0, v_max], [0, v_max], 'r-', zorder = 5)
		plt.axis([0, v_max, 0, v_max])
		plt.xlabel(obs_name, fontsize=11, fontweight='bold')
		plt.ylabel(sim_name1, fontsize=11, fontweight='bold', ha = 'left', labelpad=15)
		plt.tick_params(axis='y', which='both', top='off', left='off', right='off', bottom='off', labelsize=10, pad=0.25)
		plt.tick_params(axis='x', which='both', top='off', left='off', right='off', bottom='off', labelsize=10)
		plt.xticks(np.linspace(0, int(v_max), 3))
		plt.yticks(np.linspace(0, int(v_max), 3))
		fig.savefig(temp_folder+'Correlation1.png')
		plt.close()
		pool.map(PlotColorMesh1, arg_arr)

def PlotColorMesh1(args):
	PlotColorMesh(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])

def PlotColorMesh(temp_folder, extend, scalar_field, cmap, norm, bounds, xname, yname=None):
	fig = plt.figure()
	ax = plt.subplot(111)
	ticks_font = mpl.font_manager.FontProperties(family='Helvetica', style='normal', weight='light', stretch='normal', size='x-small')
	lons = np.arange(extend[0], extend[1], 0.25)
	lats = np.arange(extend[2], extend[3], -1*0.25)
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
	map.drawcoastlines(linewidth=1, color='yellow', zorder=2)
	map.drawcountries(linewidth=.8, color='yellow', zorder=3)
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
	fig.savefig(temp_folder+xname+'.png', transparent=True)
	plt.close()