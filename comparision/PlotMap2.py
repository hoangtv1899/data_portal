#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import os
import numpy as np
import math
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import matplotlib as mpl
mpl.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt

def StandardName(name):
	if name == 'CDR':
		xname = 'PERSIANN-CDR'+' (mm)'
	elif name == 'CCS':
		xname = 'PERSIANN-CCS'+' (mm)'
	elif name == 'PERSIANN':
		xname = name+' (mm)'
	return xname

def PlotMap2(obs, obs_name, sim1, sim_name1, time_step, temp_folder, sim2=None, sim_name2=None):
	obs_name = StandardName(obs_name)
	sim_name1 = StandardName(sim_name1)
	if time_step == 'yearly':
		sc1 = 1000.
	elif time_step == 'monthly':
		sc1 = 300.
	elif time_step in ['daily', '1hrly', '3hrly', '6hrly']:
		sc1 = 10.
	#flatten arrays
	x = obs.flatten('C')
	y1 = sim1.flatten('C')
	if sim_name2:
		sim_name2 = StandardName(sim_name2)
		if np.max(obs) > max(np.max(sim1), np.max(sim2)):
			v_max = math.ceil(np.max(obs)/sc1)*sc1
		else:
			obsMax = max(np.max(sim1), np.max(sim2))
			v_max = math.ceil(obsMax/sc1)*sc1
		if np.isinf(v_max):
			v_max = 800
		y2 = sim2.flatten('C')
		#corr1
		fig = plt.figure()
		plt.gca().set_aspect('equal', adjustable='box')
		plt.plot(x, y1, '+', markersize=1, color='0.03' ,zorder = 1)
		plt.plot([0, v_max], [0, v_max], 'r-', zorder = 2)
		plt.axis([0, v_max, 0, v_max])
		plt.xlabel(obs_name, fontsize=15, fontweight='bold',labelpad=12)
		plt.ylabel(sim_name1, fontsize=15, fontweight='bold', ha = 'left',labelpad=18)
		plt.tick_params(axis='y', which='both', top='off', right='off', bottom='off', labelsize=15, pad=5)
		plt.tick_params(axis='x', which='both', top='off', left='off', right='off', labelsize=15, pad=5)
		plt.xticks(np.linspace(0, int(v_max), 5))
		plt.yticks(np.linspace(0, int(v_max), 5)[1:])
		fig.savefig(temp_folder+'Scatter1.png')
		plt.close()
		#corr2
		fig = plt.figure()
		plt.gca().set_aspect('equal', adjustable='box')
		plt.plot(x, y2, '+', markersize=1, color='0.03' ,zorder = 1)
		plt.plot([0, v_max], [0, v_max], 'r-', zorder = 2)
		plt.axis([0, v_max, 0, v_max])
		plt.xlabel(obs_name, fontsize=15, fontweight='bold',labelpad=12)
		plt.ylabel(sim_name2, fontsize=15, fontweight='bold', ha = 'left',labelpad=18)
		plt.tick_params(axis='y', which='both', top='off', right='off', bottom='off', labelsize=15, pad=5)
		plt.tick_params(axis='x', which='both', top='off', left='off', right='off', labelsize=15, pad=5)
		plt.xticks(np.linspace(0, int(v_max), 5))
		plt.yticks(np.linspace(0, int(v_max), 5)[1:])
		fig.savefig(temp_folder+'Scatter2.png')
		plt.close()
		#corr3
		fig = plt.figure()
		plt.gca().set_aspect('equal', adjustable='box')
		plt.plot(y2, y1, '+', markersize=1, color='0.03' ,zorder = 1)
		plt.plot([0, v_max], [0, v_max], 'r-', zorder = 2)
		plt.axis([0, v_max, 0, v_max])
		plt.xlabel(sim_name1, fontsize=15, fontweight='bold',labelpad=12)
		plt.ylabel(sim_name2, fontsize=15, fontweight='bold', ha = 'left', labelpad=18)
		plt.tick_params(axis='y', which='both', top='off', right='off', bottom='off', labelsize=15, pad=5)
		plt.tick_params(axis='x', which='both', top='off', left='off', right='off', labelsize=15, pad=5)
		plt.xticks(np.linspace(0, int(v_max), 5))
		plt.yticks(np.linspace(0, int(v_max), 5)[1:])
		fig.savefig(temp_folder+'Scatter3.png')
		plt.close()
	else:
		if np.max(obs) > np.max(sim1):
			v_max = math.ceil(np.max(obs)/sc1)*sc1
		else:
			v_max = math.ceil(np.max(sim1)/sc1)*sc1
		if np.isinf(v_max):
			v_max = 800
		#corr1
		fig = plt.figure()
		plt.gca().set_aspect('equal', adjustable='box')
		plt.plot(x, y1, '+', markersize=1, color='0.03' ,zorder = 1)
		plt.plot([0, v_max], [0, v_max], 'r-', zorder = 2)
		plt.axis([0, v_max, 0, v_max])
		plt.xlabel(obs_name, fontsize=15, fontweight='bold',labelpad=12)
		plt.ylabel(sim_name1, fontsize=15, fontweight='bold', ha = 'left', labelpad=18)
		plt.tick_params(axis='y', which='both', top='off', right='off', bottom='off', labelsize=15, pad=5)
		plt.tick_params(axis='x', which='both', top='off', left='off', right='off', labelsize=15, pad=5)
		plt.xticks(np.linspace(0, int(v_max), 5))
		plt.yticks(np.linspace(0, int(v_max), 5)[1:])
		fig.savefig(temp_folder+'Scatter1.png')
		plt.close()
