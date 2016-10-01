#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import numpy as np
#import scipy.io
from collections import OrderedDict

def ValidationFunction(obs, sim):
	result = OrderedDict()
	np.seterr(all='ignore')
	#NoSimPoints = np.ma.count(sim)
	#NoObsPoints = np.ma.count(obs)
	#flatten arrays
	try:
		simulated = (np.ma.masked_where(obs.mask==True, sim))
		observed = (np.ma.masked_where(sim.mask==True, obs))
	except:
		simulated = sim
		observed = obs
	simulated = np.delete(simulated, simulated.mask==True)
	observed = np.delete(observed, observed.mask==True)
	print simulated.shape
	print observed.shape
	#get condition rain
	#simulated = simulated[simulated>=0.1]
	#observed = observed[observed>=0.1]
	#begin calculation
	HitError = simulated[np.logical_and(simulated > 0, observed > 0)] - observed[np.logical_and(simulated > 0, observed > 0)]
	#hit bias
	hit_bias = np.sum(HitError)
	hit_bias = round(hit_bias, 3)
	#bias map
	biasmap = np.sum(simulated)/np.sum(observed)
	biasmap = round(biasmap, 3)
	#Number of correct negatives
	NoCorrNeg = np.sum(np.logical_and(simulated <= 0, observed <= 0))
	#Number of hit
	simhit = simulated[np.logical_and(simulated > 0, observed > 0)]
	NoHit = np.sum(np.logical_and(simulated > 0, observed > 0))
	#Total number of simulation hit
	SumSimhit = np.sum(simhit)
	SumSimhit = round(SumSimhit, 3)
	#Number of miss
	obsmiss = observed[np.logical_and(simulated <= 0, observed > 0)]
	NoMiss = np.sum(np.logical_and(simulated <= 0, observed > 0))
	#Total number of miss
	SumMiss = np.sum(obsmiss)
	if SumMiss.data == np.array(0.0):
		SumMiss = 0
	else:
		SumMiss = round(SumMiss, 3)
	#Number of false
	simfalse = simulated[np.logical_and(simulated > 0, observed == 0)]
	NoFalse = np.sum(np.logical_and(simulated > 0, observed == 0))
	#Total number of false
	SumFalse = np.sum(simfalse)
	if SumFalse.data == np.array(0.0):
		SumFalse = 0
	else:
		SumFalse = round(SumFalse, 3)
	#Total
	Tot = NoHit + NoFalse + NoMiss + NoCorrNeg
	#Probability of Detection
	POD = NoHit/float(NoHit + NoMiss)
	POD = round(POD, 3)
	#False Alarm Ratio
	FAR = NoFalse/float(NoHit + NoFalse)
	FAR = round(FAR, 3)
	#Bias score
	BIAS = (NoHit + NoFalse)/float(NoHit + NoMiss)
	BIAS = round(BIAS, 3)
	#Heidke skill score
	if (NoMiss ==0 and NoFalse == 0 and NoCorrNeg ==0):
		HSS = np.Inf
		HK = -np.Inf
		ETS = np.Inf
	else:
		exp_ect_corr = ((NoHit+NoMiss)*(NoHit+NoFalse)+(NoCorrNeg+NoMiss)*(NoCorrNeg+NoFalse))/float(Tot)
		HSS = (NoHit+NoCorrNeg - exp_ect_corr)/float(Tot - exp_ect_corr)
		HSS = round(HSS, 3)
		#Hanssen-Kuipers score
		HK = (NoHit/float(NoHit+NoMiss)) - (NoFalse/float(NoFalse + NoCorrNeg))
		HK = round(HK, 3)
		#Equitable threat score
		hits_rand = (NoHit+NoMiss)*(NoHit+NoFalse)/float(Tot)
		ETS = (NoHit - hits_rand)/float(NoHit+NoMiss+NoFalse-hits_rand)
		ETS = round(ETS, 3)
	#
	simulated1 = simulated[np.logical_and(simulated > 0, observed > 0)]
	observed1 = observed[np.logical_and(simulated > 0, observed > 0)]
	#RMSE
	RMSE = np.sqrt(np.mean((simulated1 - observed1)**2))
	RMSE = round(RMSE, 3)
	#RMSE normalize
	if simulated1.size !=0:
		if np.max(simulated1) == np.min(simulated1):
			RMSE_norm = np.Inf
		else:
			RMSE_norm = RMSE/float(np.max(simulated1) - np.min(simulated1))
		RMSE_norm = round(RMSE_norm, 3)
	else:
		RMSE_norm = np.nan
	#Mean absolute error
	MAE = np.mean(np.absolute(simulated1 - observed1))
	MAE = round(MAE, 3)
	#Correlation
	corr_ma = np.corrcoef(simulated1, observed1)
	#scipy.io.savemat('sim.mat', mdict={'sim':simulated.filled(-99)})
	#scipy.io.savemat('obs.mat', mdict={'obs':observed.filled(-99)})
	if corr_ma.size != 0:
		corr = corr_ma[0,1]
		corr = round(corr, 3)
	else:
		corr = np.nan
	#result['NoSimPoints']=NoSimPoints; result['NoObsPoints']=NoObsPoints; result['biasmap']=biasmap; result['hit_bias']=hit_bias; result['NoHit']=NoHit; result['NoFalse']=NoFalse; result['NoMiss']=NoMiss; result['NoCorrNeg']=NoCorrNeg; result['SumMiss']=SumMiss; result['SumFalse']=SumFalse; result['SumSimhit']=SumSimhit; result['corr']=corr; result['MAE']=MAE; result['RMSE']=RMSE; result['POD']=POD; result['FAR']=FAR; result['BIAS']=BIAS; result['HSS']=HSS; result['HK']=HK; result['ETS']=ETS
	#return np.array([biasmap, NoHit, NoFalse, NoMiss, SumMiss, SumFalse, SumSimhit, corr, RMSE, POD, FAR])
	result['corr']=corr; result['MAE']=MAE; result['RMSE']=RMSE; result['RMSE normalize']=RMSE_norm; result['POD']=POD; result['FAR']=FAR; result['BIAS']=BIAS; result['HSS']=HSS; result['HK']=HK; result['ETS']=ETS 
	return result
