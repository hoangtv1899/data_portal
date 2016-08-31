#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import numpy as np
from collections import OrderedDict

def ValidationFunction(sim, obs):
	result = OrderedDict()
	np.seterr(all='ignore')
	NoSimPoints = np.ma.count(sim)
	NoObsPoints = np.ma.count(obs)
	#flatten arrays
	simulated = (np.ma.masked_where(obs.mask==True, sim)).flatten('C')
	observed = (np.ma.masked_where(sim.mask==True, obs)).flatten('C')
	HitError = simulated[np.logical_and(simulated > 0, observed > 0)] - observed[np.logical_and(simulated > 0, observed > 0)]
	#hit bias
	hit_bias = np.sum(HitError)
	hit_bias = round(hit_bias, 4)
	#bias map
	biasmap = np.sum(simulated)/np.sum(observed)
	biasmap = round(biasmap, 4)
	#Number of correct negatives
	NoCorrNeg = np.sum(np.logical_and(simulated == 0, observed == 0))
	#Number of hit
	simhit = simulated[np.logical_and(simulated > 0, observed > 0)]
	NoHit = np.sum(np.logical_and(simulated > 0, observed > 0))
	#Total number of simulation hit
	SumSimhit = np.sum(simhit)
	SumSimhit = round(SumSimhit, 4)
	#Number of miss
	obsmiss = observed[np.logical_and(simulated == 0, observed > 0)]
	NoMiss = np.sum(np.logical_and(simulated == 0, observed > 0))
	#Total number of miss
	SumMiss = np.sum(obsmiss)
	if SumMiss.data == np.array(0.0):
		SumMiss = 0
	else:
		SumMiss = round(SumMiss, 4)
	#Number of false
	simfalse = simulated[np.logical_and(simulated > 0, observed == 0)]
	NoFalse = np.sum(np.logical_and(simulated > 0, observed == 0))
	#Total number of false
	SumFalse = np.sum(simfalse)
	if SumFalse.data == np.array(0.0):
		SumFalse = 0
	else:
		SumFalse = round(SumFalse, 4)
	#Total
	Tot = NoHit + NoFalse + NoMiss + NoCorrNeg
	#Probability of Detection
	POD = NoHit/float(NoHit + NoMiss)
	POD = round(POD, 4)
	#False Alarm Ratio
	FAR = NoFalse/float(NoHit + NoFalse)
	FAR = round(FAR, 4)
	#Bias score
	BIAS = (NoHit + NoFalse)/float(NoHit + NoMiss)
	BIAS = round(BIAS, 4)
	#Heidke skill score
	if (NoMiss ==0 and NoFalse == 0 and NoCorrNeg ==0):
		HSS = np.Inf
		HK = -np.Inf
		ETS = np.Inf
	else:
		exp_ect_corr = ((NoHit+NoMiss)*(NoHit+NoFalse)+(NoCorrNeg+NoMiss)*(NoCorrNeg+NoFalse))/float(Tot)
		HSS = (NoHit+NoCorrNeg - exp_ect_corr)/float(Tot - exp_ect_corr)
		HSS = round(HSS, 4)
		#Hanssen-Kuipers score
		HK = (NoHit/float(NoHit+NoMiss)) - (NoFalse/float(NoFalse + NoCorrNeg))
		HK = round(HK, 4)
		#Equitable threat score
		hits_rand = (NoHit+NoMiss)*(NoHit+NoFalse)/float(Tot)
		ETS = (NoHit - hits_rand)/float(NoHit+NoMiss+NoFalse-hits_rand)
		ETS = round(ETS, 4)
	#RMSE
	RMSE = np.sqrt(np.mean((simulated - observed)**2))
	RMSE = round(RMSE, 4)
	#RMSE normalize
	RMSE_norm = RMSE/float(np.max(simulated) - np.min(simulated))
	#Mean absolute error
	MAE = np.mean(np.absolute(simulated - observed))
	MAE = round(MAE, 4)
	#Correlation
	corr = np.corrcoef(simulated, observed)[-1,0]
	corr = round(corr, 4)
	result['NoSimPoints']=NoSimPoints; result['NoObsPoints']=NoObsPoints; result['biasmap']=biasmap; result['hit_bias']=hit_bias; result['NoHit']=NoHit; result['NoFalse']=NoFalse; result['NoMiss']=NoMiss; result['NoCorrNeg']=NoCorrNeg; result['SumMiss']=SumMiss; result['SumFalse']=SumFalse; result['SumSimhit']=SumSimhit; result['corr']=corr; result['MAE']=MAE; result['RMSE']=RMSE; result['POD']=POD; result['FAR']=FAR; result['BIAS']=BIAS; result['HSS']=HSS; result['HK']=HK; result['ETS']=ETS
	return result
	