#!/bin/sh

#
#
#   by DKB  150715  
#  revised 150803 to fix yrs:$yrs  glitch



ymdf=$1
ymdt=$2

dataset=$3

#unique user IP
userIP=$4

currentDateTime=$5  #should be A or V for accum or average

yf4=`echo $ymdf | cut -c1-4`

yf=`echo $ymdf | cut -c3-4`
mf=`echo $ymdf | cut -c5-6`
df=`echo $ymdf | cut -c7-8`

#YYYYmmdd

yt4=`echo $ymdt | cut -c1-4`
yt=`echo $ymdt | cut -c3-4`
mt=`echo $ymdt | cut -c5-6`
dt=`echo $ymdt | cut -c7-8`

size_ymdf=${#ymdf}
if [ $size_ymdf -eq 8 ]
then
	time_step='daily'
elif [ $size_ymdf -eq 6 ]
then
	time_step='monthly'
elif [ $size_ymdf -eq 4 ]
then
	time_step='yearly'
fi

dataset0=`echo $dataset | awk '{print $1 }'`
dataset01=`echo "${dataset0//\"}"`

if [ $dataset01 = 'CDR' ]
then
	dataset1='Persiann_CDR'
elif [ $dataset01 = 'CCS' ]
then
	dataset1='Persiann_CCS'
elif [ $dataset01 = 'PERSIANN' ]
then
	dataset1='Persiann'
fi

main_dir='/mnt/t/disk3/CHRSdata/'
h=`ls $main_dir$dataset1/$time_step/*$ymdf*.tif 2> /dev/null`
k=`ls $main_dir$dataset1/$time_step/*$ymdt*.tif 2> /dev/null`

if [ -z "$h" ] || [ -z "$k" ]
then
	echo "dataset is not available in the selected time range"
	exit
fi

# for calculations need what years what yymm and what ymd prior and ymd after
yrs=
mth=
dp=
da=

if [ $yf -eq $yt ]
then
	nd=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yf$mf`
	#ck full year
	if [ $mf$df = '0101' -a $mt$dt = '1231' ]
	then
		yrs=$yf
		#echo do da: mth: yrs: $yrs dp:
		#echo /mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
		/mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
		exit
	elif [ $mf -eq $mt ]
	then
		#ck full month
		if [ $df -eq 1 -a $dt -eq $nd ]
		then
			mth=$yf$mf
			#echo do mths: $mth
			#echo /mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
			/mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
			exit
		else  # less than month
			wkdf=$df
			while [ $wkdf -le $dt ]
			do
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
			done			
			#echo do da: $da
			#echo /mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
			/mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
			exit
		fi
	else
		if [ $df -eq 1 ]
		then
			mth="$mth $yf$mf"
		else
			wkdf=$df
			while [ $wkdf -le $nd ]
			do
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
			done
		fi
		wkmf=`expr $mf + 1`
		if [ $wkmf -lt 10 ]
		then
			wkmf=0$wkmf
		fi
		while [ $wkmf -lt $mt ]
		do
			mth="$mth $yf$wkmf"
			wkmf=`expr $wkmf + 1`
			if [ $wkmf -lt 10 ]
			then
				wkmf=0$wkmf
			fi
		done
		ndp=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yt$mt`
		if [ $dt -eq $ndp ]
		then
			mth="$mth $yt$mt"
		else
			wkdt=01
			while [ $wkdt -le $dt ]
			do
				dp="$dp $yt$mt$wkdt"
				wkdt=`expr $wkdt + 1`
				if [ $wkdt -lt 10 ]
				then
					wkdt=0$wkdt
				fi
			done
		fi
		#echo do da: $da mth: $mth  dp: $dp
		#echo /mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
		/mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
		exit
	fi
else
	#ck full year $yf
	if [ $mf$df = '0101' ]
	then
		yrs=$yf
	else
		if [ $df -eq 1 ]
		then
			mth=$yf$mf
		else
			nd=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yf$mf`
			wkdf=$df
			while [ $wkdf -le $nd ]
			do
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
			done
		fi

		wkmf=`expr $mf + 1`
		if [ $wkmf -lt 10 ]
		then
			wkmf=0$wkmf
		fi
			
		while [ $wkmf -le 12 ]
		do
			mth="$mth $yf$wkmf"
			wkmf=`expr $wkmf + 1`
			if [ $wkmf -lt 10 ]
			then
				wkmf=0$wkmf
			fi
		done
	fi
	wkyf=`expr $yf + 1`
	if [ $wkyf -lt 10 ]
	then
		wkyf=0$wkyf
	elif [ $wkyf -eq 100 ]
	then
		wkyf=00
	fi

	while [ $wkyf -ne $yt ]
	do
		yrs="$yrs $wkyf"
		wkyf=`expr $wkyf + 1`
		if [ $wkyf -lt 10 ]
		then
			wkyf=0$wkyf
		elif [ $wkyf -eq 100 ]
		then
			wkyf=00
		fi
	done
	if [ $mt$dt = "1231" ]
	then
		yrs="$yrs $yt"
		#echo do  da: $da yrs: $yrs mth: $mth
		#echo /mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
		/mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
		exit
	else
		ndp=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yt$mt`
		if [ $dt -eq $ndp ]
		then
			wkmt=01
			while [ $wkmt -le $mt ]
			do
				mth="$mth $yt$wkmt"
				wkmt=`expr $wkmt + 1`
				if [ $wkmt -lt 10 ]
				then
					wkmt=0$wkmt
				fi
			done
		else
			wkmt=01
			while [ $wkmt -lt $mt ]
			do
				mth="$mth $yt$wkmt"
				wkmt=`expr $wkmt + 1`
				if [ $wkmt -lt 10 ]
				then
					wkmt=0$wkmt
				fi
			done
			wkdt=01
			while [ $wkdt -le $dt ]
			do
				dp="$dp $yt$mt$wkdt"
				wkdt=`expr $wkdt + 1`
				if [ $wkdt -lt 10 ]
				then
					wkdt=0$wkdt
				fi
			done
		fi
	fi
fi

#echo do da: $da mth: $mth yrs: $yrs dp: $dp
#echo /mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
/mnt/t/disk2/pconnect/CHRSData/python/comparision/do_acc.py "$dataset" $userIP $currentDateTime "ha: da: $da mth: $mth yrs: $yrs dp: $dp hp: "
exit
