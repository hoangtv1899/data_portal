#!/bin/sh

#
#
#   by DKB  150715  
#   revised 150803 to fix yrs:$yrs  glitch
#	modified by Hoang to use hour 160617



ymdhf=$1
ymdht=$2

dataset=$3

#unique user IP
userIP=$4

currentDateTime=$5


yf4=`echo $ymdhf | cut -c1-4`

yf=`echo $ymdhf | cut -c3-4`
mf=`echo $ymdhf | cut -c5-6`
df=`echo $ymdhf | cut -c7-8`
hf=`echo $ymdhf | cut -c9-10`
#YYYYmmdd

yt4=`echo $ymdht | cut -c1-4`
yt=`echo $ymdht | cut -c3-4`
mt=`echo $ymdht | cut -c5-6`
dt=`echo $ymdht | cut -c7-8`
ht=`echo $ymdht | cut -c9-10`

# for calculations need what years what yymm and what ymd prior and ymd after
yrs=
mth=
dp=
da=
ha=
hp=

if [ $yf -eq $yt ]
then
	nd=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yf$mf`
	#ck full year
	if [ $mf$df = '0101' -a $mt$dt = '1231' ]
	then
		if [ $hf = '00' -a $ht = '23' ]
		then
			yrs=$yf
			echo do ha: da: mth: yrs: $yrs dp: hp:
			echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
			./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
			exit
		elif [ $hf = '00' ]
		then
			#mth = 01 .. 11
			mth="$mth $yf$mf"
			wkmf=`expr $mf + 1`
			while [ $wkmf -lt $mt ]
			do
			if [ $wkmf -lt 10 ]
			then
				wkmf=0$wkmf
			fi
			mth="$mth $yf$wkmf"
			wkmf=`expr $wkmf + 1`
			done
			#dp = 01 .. 30
			dt1=$yt$mt'01'
			dp="$dp $dt1"
			wkdt=`expr 01 + 1`
			while [ $wkdt -lt $dt ]
			do
			if [ $wkdt -lt 10 ]
			then
				wkdt=0$wkdt
			fi
			dp="$dp $yt$mt$wkdt"
			wkdt=`expr $wkdt + 1`
			done
			if [ $ht = '00' ]
			then
				hp="$yt$mt$dt$ht"
				echo do ha: da: mth: $mth yrs: dp: $dp hp: $hp
				echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				exit
			else
				#hp = 00 .. $ht
				ht1=$yt$mt$dt'00'
				hp="$hp $ht1"
				wkht=`expr 00 + 1`
				while [ $wkht -le $ht ]
				do
				if [ $wkht -lt 10 ]
				then
					wkht=0$wkht
				fi
				hp="$hp $yt$mt$dt$wkht"
				wkht=`expr $wkht + 1`
				done
				echo do ha: da: mth: $mth yrs: dp: $dp hp: $hp
				echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				exit
			fi
		else
			#ha = $hf .. 23
			ha="$ha $yf$mf$df$hf"
			wkhf=`expr $hf + 1`
			while [ $wkhf -le 23 ]
			do
			if [ $wkhf -lt 10 ]
			then
				wkhf=0$wkhf
			fi
			ha="$ha $yf$mf$df$wkhf"
			wkhf=`expr $wkhf + 1`
			done
			#da = $df+1 .. 31
			wkdf=`expr $df + 1`
			while [ $wkdf -le 31 ]
			do
			if [ $wkdf -lt 10 ]
			then
				wkdf=0$wkdf
			fi
			da="$da $yf$mf$wkdf"
			wkdf=`expr $wkdf + 1`
			done
			if [ $ht = '23' ]
			then
				#mth = $mf+1 .. $mt
				wkmf=`expr $mf + 1`
				while [ $wkmf -le $mt ]
				do
				if [ $wkmf -lt 10 ]
				then
					wkmf=0$wkmf
				fi
				mth="$mth $yf$wkmf"
				wkmf=`expr $wkmf + 1`
				done
				echo do ha: $ha da: $da mth: $mth yrs: dp: hp:
				echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				exit
			else
			#mth = $mf+1 .. 11
				wkmf=`expr $mf + 1`
				while [ $wkmf -lt $mt ]
				do
				if [ $wkmf -lt 10 ]
				then
					wkmf=0$wkmf
				fi
				mth="$mth $yf$wkmf"
				wkmf=`expr $wkmf + 1`
				done
				#dp = 01 .. $dt
				dt1=$yt$mt'01'
				dp="$dp $dt1"
				wkdt=`expr 01 + 1`
				while [ $wkdt -lt $dt ]
				do
				if [ $wkdt -lt 10 ]
				then
					wkdt=0$wkdt
				fi
				dp="$dp $yt$mt$wkdt"
				wkdt=`expr $wkdt + 1`
				done
				if [ $ht = '00' ]
				then
					hp="$yt$mt$dt$ht"
					echo do ha: $ha da: $da mth: $mth yrs: dp: $dp hp: $hp
					echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					exit
				else
					#hp = 00 .. $ht
					ht1=$yt$mt$dt'00'
					hp="$hp $ht1"
					wkht=`expr 00 + 1`
					while [ $wkht -le $ht ]
					do
					if [ $wkht -lt 10 ]
					then
						wkht=0$wkht
					fi
					hp="$hp $yt$mt$dt$wkht"
					wkht=`expr $wkht + 1`
					done
					echo do ha: $ha da: $da mth: $mth yrs: dp: $dp hp: $hp
					echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					exit
				fi
			fi
		fi
	elif [ $mf -eq $mt ]
	then
		ndp=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yt$mt`
		#ck full month
		if [ $df -eq 1 -a $dt -eq $ndp ]
		then
			if [ $hf = '00' -a $ht = '23' ]
			then
				mth=$yf$mf
				echo do mth: $mth
				echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				exit
			elif [ $hf = '00' ]
			then
				#da = $df .. $dt-1
				da="$da $yf$mf$df"
				wkdf=`expr $df + 1`
				while [ $wkdf -lt $dt ]
				do
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				done
				if [ $ht = '00' ]
				then
					hp="$yt$mt$dt$ht"
					echo do ha: da: $da mth: yrs: dp: hp: $hp
					echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					exit
				else
					#hp = 00 .. $ht
					ht1=$yt$mt$dt'00'
					hp="$hp $ht1"
					wkht=`expr 00 + 1`
					while [ $wkht -le $ht ]
					do
					if [ $wkht -lt 10 ]
					then
						wkht=0$wkht
					fi
					hp="$hp $yt$mt$dt$wkht"
					wkht=`expr $wkht + 1`
					done
					echo do ha: da: $da mth: yrs: dp: hp: $hp
					echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					exit
				fi
			else
				#ha = $hf .. 23
				ha="$ha $yf$mf$df$hf"
				wkhf=`expr $hf + 1`
				while [ $wkhf -le 23 ]
				do
				if [ $wkhf -lt 10 ]
				then
					wkhf=0$wkhf
				fi
				ha="$ha $yf$mf$df$wkhf"
				wkhf=`expr $wkhf + 1`
				done
				if [ $ht = '23' ]
				then
					#da = $df+1 .. $dt
					wkdf=`expr $df + 1`
					while [ $wkdf -le $dt ]
					do
					if [ $wkdf -lt 10 ]
					then
						wkdf=0$wkdf
					fi
					da="$da $yf$mf$wkdf"
					wkdf=`expr $wkdf + 1`
					done
					echo do ha: $ha da: $da mth: yrs: dp: hp:
					echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					exit
				else
					#da = $df+1 .. $dt-1
					wkdf=`expr $df + 1`
					while [ $wkdf -lt $dt ]
					do
					if [ $wkdf -lt 10 ]
					then
						wkdf=0$wkdf
					fi
					da="$da $yf$mf$wkdf"
					wkdf=`expr $wkdf + 1`
					done
					if [ $ht = '00' ]
					then
						hp="$yt$mt$dt$ht"
						echo do ha: $ha da: $da mth: yrs: dp: hp: $hp
						echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
						./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
						exit
					else
					#hp = 00 .. $ht
						ht1=$yt$mt$dt'00'
						hp="$hp $ht1"
						wkht=`expr 00 + 1`
						while [ $wkht -le $ht ]
						do
						if [ $wkht -lt 10 ]
						then
							wkht=0$wkht
						fi
						hp="$hp $yt$mt$dt$wkht"
						wkht=`expr $wkht + 1`
						done
						echo do ha: $ha da: $da mth: yrs: dp: hp: $hp
						echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
						./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
						exit
					fi
				fi
				
			fi
		else  # less than month
			if [ $hf = '00' -a $ht = '23' ]
			then
				#da = $df .. $dt
				if [ $df -ne $dt ]
				then
					da="$da $yf$mf$df"
					wkdf=`expr $df + 1`
					while [ $wkdf -le $dt ]
					do
					if [ $wkdf -lt 10 ]
					then
						wkdf=0$wkdf
					fi
					da="$da $yf$mf$wkdf"
					wkdf=`expr $wkdf + 1`
					done
				else
					da=$yf$mf$df
				fi
				echo do da: $da
				echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				exit
			elif [ $hf = '00' ]
			then
				#da = $df .. $dt-1
				if [ $df -ne $dt ]
				then
					da="$da $yf$mf$df"
					wkdf=`expr $df + 1`
					while [ $wkdf -lt $dt ]
					do
					if [ $wkdf -lt 10 ]
					then
						wkdf=0$wkdf
					fi
					da="$da $yf$mf$wkdf"
					wkdf=`expr $wkdf + 1`
					done
				fi
				if [ $ht = '00' ]
				then
					hp="$yt$mt$dt$ht"
					echo do ha: da: $da mth: yrs: dp: hp: $hp
					echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					exit
				else
					#hp = 00 .. $ht
					ht1=$yt$mt$dt'00'
					hp="$hp $ht1"
					wkht=`expr 00 + 1`
					while [ $wkht -le $ht ]
					do
					if [ $wkht -lt 10 ]
					then
						wkht=0$wkht
					fi
					hp="$hp $yt$mt$dt$wkht"
					wkht=`expr $wkht + 1`
					done
					echo do ha: da: $da mth: yrs: dp: hp: $hp
					echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					exit
				fi
			else
				#ha = $hf .. 23
				ha="$ha $yf$mf$df$hf"
				wkhf=`expr $hf + 1`
				while [ $wkhf -le 23 ]
				do
				if [ $wkhf -lt 10 ]
				then
					wkhf=0$wkhf
				fi
				ha="$ha $yf$mf$df$wkhf"
				wkhf=`expr $wkhf + 1`
				done
				if [ $ht = '23' ]
				then
					#da = $df +1 .. $dt-1
					wkdf=`expr $df + 1`
					while [ $wkdf -le $dt ]
					do
					if [ $wkdf -lt 10 ]
					then
						wkdf=0$wkdf
					fi
					da="$da $yf$mf$wkdf"
					wkdf=`expr $wkdf + 1`
					done
					echo do ha: $ha da: $da mth: yrs: dp: hp:
					echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
					exit
				else
					#da = $df +1 .. $dt-1
					wkdf=`expr $df + 1`
					while [ $wkdf -lt $dt ]
					do
					if [ $wkdf -lt 10 ]
					then
						wkdf=0$wkdf
					fi
					da="$da $yf$mf$wkdf"
					wkdf=`expr $wkdf + 1`
					done
					if [ $ht = '00' ]
					then
						hp="$yt$mt$dt$ht"
						echo do ha: $ha da: $da mth: yrs: dp: hp: $hp
						echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
						./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
						exit
					else
					#hp = 00 .. $ht
						ht1=$yt$mt$dt'00'
						hp="$hp $ht1"
						wkht=`expr 00 + 1`
						while [ $wkht -le $ht ]
						do
						if [ $wkht -lt 10 ]
						then
							wkht=0$wkht
						fi
						hp="$hp $yt$mt$dt$wkht"
						wkht=`expr $wkht + 1`
						done
						echo do ha: $ha da: $da mth: yrs: dp: hp: $hp
						echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
						./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
						exit
					fi
				fi
			fi
		fi
	else
		if [ $df -eq 1 ]
		then
			if [ $hf = '00' ]
			then
				mth="$mth $yf$mf"
			else
				#ha = $hf .. 23
				ha="$ha $yf$mf$df$hf"
				wkhf=`expr $hf + 1`
				while [ $wkhf -le 23 ]
				do
				if [ $wkhf -lt 10 ]
				then
					wkhf=0$wkhf
				fi
				ha="$ha $yf$mf$df$wkhf"
				wkhf=`expr $wkhf + 1`
				done
				#da = $df+1 .. $nd
				wkdf=`expr $df + 1`
				while [ $wkdf -le $nd ]
				do
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				done
			fi
		else
			if [ $hf = '00' ]
			then
				#da = $df .. $nd
				da="$da $yf$mf$df"
				wkdf=`expr $df + 1`
				while [ $wkdf -le $nd ]
				do
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				done
			else
				#ha = $hf .. 23
				ha="$ha $yf$mf$df$hf"
				wkhf=`expr $hf + 1`
				while [ $wkhf -le 23 ]
				do
				if [ $wkhf -lt 10 ]
				then
					wkhf=0$wkhf
				fi
				ha="$ha $yf$mf$df$wkhf"
				wkhf=`expr $wkhf + 1`
				done
				#da = $df+1 .. $nd
				wkdf=`expr $df + 1`
				while [ $wkdf -le $nd ]
				do
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				done
			fi
		fi
		#mth $mf .. $mt
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
		#dp = 01 .. $dt
		ndp=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yt$mt`
		if [ $dt -eq $ndp ]
		then
			if [ $ht = '23' ]
			then
				mth="$mth $yt$mt"
			else
				#dp = 01..$dt-1
				dt1=$yt$mt'01'
				dp="$hp $dt1"
				wkdt=`expr 01 + 1`
				while [ $wkdt -lt $dt ]
				do
				if [ $wkdt -lt 10 ]
				then
					wkdt=0$wkdt
				fi
				dp="$dp $yt$mt$wkdt"
				wkdt=`expr $wkdt + 1`
				done
				if [ $ht = '00' ]
				then
					hp="$yt$mt$dt$ht"
				else
				#hp = 00 .. $ht
					ht1=$yt$mt$dt'00'
					hp="$hp $ht1"
					wkht=`expr 00 + 1`
					while [ $wkht -le $ht ]
					do
					if [ $wkht -lt 10 ]
					then
						wkht=0$wkht
					fi
					hp="$hp $yt$mt$dt$wkht"
					wkht=`expr $wkht + 1`
					done
				fi
				
			fi
		else
			if [ $ht = '23' ]
			then
				#dp = 01..$dt
				dt1=$yt$mt'01'
				dp="$hp $dt1"
				wkdt=`expr 01 + 1`
				while [ $wkdt -le $dt ]
				do
				if [ $wkdt -lt 10 ]
				then
					wkdt=0$wkdt
				fi
				dp="$dp $yt$mt$wkdt"
				wkdt=`expr $wkdt + 1`
				done
			else
				#dp = 01..$dt-1
				dt1=$yt$mt'01'
				dp="$hp $dt1"
				wkdt=`expr 01 + 1`
				while [ $wkdt -lt $dt ]
				do
				if [ $wkdt -lt 10 ]
				then
					wkdt=0$wkdt
				fi
				dp="$dp $yt$mt$wkdt"
				wkdt=`expr $wkdt + 1`
				done
				if [ $ht = '00' ]
				then
					hp="$yt$mt$dt$ht"
				else
				#hp = 00 .. $ht
					ht1=$yt$mt$dt'00'
					hp="$hp $ht1"
					wkht=`expr 00 + 1`
					while [ $wkht -le $ht ]
					do
					if [ $wkht -lt 10 ]
					then
						wkht=0$wkht
					fi
					hp="$hp $yt$mt$dt$wkht"
					wkht=`expr $wkht + 1`
					done
				fi
				
			fi
		fi
		echo do ha: $ha da: $da mth: $mth  dp: $dp hp: $hp
		echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
		./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
		exit
		fi
else
	nd=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yf$mf`
	#ck full year $yf
	if [ $mf$df = '0101' ]
	then
		if [ $hf = '00' ]
		then
			yrs=$yf
		else
			#ha = $hf .. 23
			ha="$ha $yf$mf$df$hf"
			wkhf=`expr $hf + 1`
			while [ $wkhf -le 23 ]
			do
			if [ $wkhf -lt 10 ]
			then
				wkhf=0$wkhf
			fi
			ha="$ha $yf$mf$df$wkhf"
			wkhf=`expr $wkhf + 1`
			done	
			#da = $df+1 .. $nd
			wkdf=`expr $df + 1`
			while [ $wkdf -le $nd ]
			do
			if [ $wkdf -lt 10 ]
			then
				wkdf=0$wkdf
			fi
			da="$da $yf$mf$wkdf"
			wkdf=`expr $wkdf + 1`
			done
			#mth = $mf+1 .. 12
			wkmf=`expr $mf + 1`
			while [ $wkmf -le 12 ]
			do
			if [ $wkmf -lt 10 ]
			then
				wkmf=0$wkmf
			fi
			mth="$mth $yf$wkmf"
			wkmf=`expr $wkmf + 1`
			done
		fi
	else
		if [ $df -eq 1 ]
		then
			if [ $hf = '00' ]
			then
				mth=$yf$mf
			else
				#ha = $hf .. 23
				ha="$ha $yf$mf$df$hf"
				wkhf=`expr $hf + 1`
				while [ $wkhf -le 23 ]
				do
				if [ $wkhf -lt 10 ]
				then
					wkhf=0$wkhf
				fi
				ha="$ha $yf$mf$df$wkhf"
				wkhf=`expr $wkhf + 1`
				done	
				#da = $df+1 .. nd
				nd=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yf$mf`
				wkdf=`expr $df + 1`
				while [ $wkdf -le $nd ]
				do
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				done
			fi
		else
			if [ $hf = '00' ]
			then
				#da = $df .. nd
				nd=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yf$mf`
				da="$da $yf$mf$df"
				wkdf=`expr $df + 1`
				while [ $wkdf -le $nd ]
				do
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				done
			else
				#ha = $hf .. 23
				ha="$ha $yf$mf$df$hf"
				wkhf=`expr $hf + 1`
				while [ $wkhf -le 23 ]
				do
				if [ $wkhf -lt 10 ]
				then
					wkhf=0$wkhf
				fi
				ha="$ha $yf$mf$df$wkhf"
				wkhf=`expr $wkhf + 1`
				done	
				#da = $df+1 .. nd
				nd=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yf$mf`
				wkdf=`expr $df + 1`
				while [ $wkdf -le $nd ]
				do
				if [ $wkdf -lt 10 ]
				then
					wkdf=0$wkdf
				fi
				da="$da $yf$mf$wkdf"
				wkdf=`expr $wkdf + 1`
				done
			fi
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
		if [ $ht = "23" ]
		then
			yrs="$yrs $yt"
			echo do  ha: $ha da: $da yrs: $yrs mth: $mth
			echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
			./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
			exit
		else
			#mth = 01 .. $mt-1
			mt1=$yt'01'
			mth="$mth $mt1"
			wkmt=`expr 01 + 1`
			while [ $wkmt -lt $mt ]
			do
			if [ $wkmt -lt 10 ]
			then
				wkmt=0$wkmt
			fi
			mth="$mth $yt$wkmt"
			wkmt=`expr $wkmt + 1`
			done
			#dp = 01..$dt-1
			dt1=$yt$mt'01'
			dp="$hp $dt1"
			wkdt=`expr 01 + 1`
			while [ $wkdt -lt $dt ]
			do
			if [ $wkdt -lt 10 ]
			then
				wkdt=0$wkdt
			fi
			dp="$dp $yt$mt$wkdt"
			wkdt=`expr $wkdt + 1`
			done
			if [ $ht = '00' ]
			then
				hp="$yt$mt$dt$ht"
			else
			#hp = 00 .. $ht
				ht1=$yt$mt$dt'00'
				hp="$hp $ht1"
				wkht=`expr 00 + 1`
				while [ $wkht -le $ht ]
				do
				if [ $wkht -lt 10 ]
				then
					wkht=0$wkht
				fi
				hp="$hp $yt$mt$dt$wkht"
				wkht=`expr $wkht + 1`
				done
			fi
		fi
	else
		ndp=`/mnt/t/disk2/pconnect/CHRSData/python/ndpm $yt$mt`
		if [ $dt -eq $ndp ]
		then
			if [ $ht = '23' ]
			then
				#mth = 01 .. $mt
				mt1=$yt'01'
				mth="$mth $mt1"
				wkmt=`expr 01 + 1`
				while [ $wkmt -le $mt ]
				do
				if [ $wkmt -lt 10 ]
				then
					wkmt=0$wkmt
				fi
				mth="$mth $yt$wkmt"
				wkmt=`expr $wkmt + 1`
				done
				echo do  ha: $ha da: $da yrs: $yrs mth: $mth
				echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				exit
			else
				#mth = 01 .. $mt-1
				mt1=$yt'01'
				mth="$mth $mt1"
				wkmt=`expr 01 + 1`
				while [ $wkmt -lt $mt ]
				do
				if [ $wkmt -lt 10 ]
				then
					wkmt=0$wkmt
				fi
				mth="$mth $yt$wkmt"
				wkmt=`expr $wkmt + 1`
				done
				#dp = 01..$dt-1
				dt1=$yt$mt'01'
				dp="$hp $dt1"
				wkdt=`expr 01 + 1`
				while [ $wkdt -lt $dt ]
				do
				if [ $wkdt -lt 10 ]
				then
					wkdt=0$wkdt
				fi
				dp="$dp $yt$mt$wkdt"
				wkdt=`expr $wkdt + 1`
				done	
				if [ $ht = '00' ]
				then
					hp="$yt$mt$dt$ht"
				else
				#hp = 00 .. $ht
					ht1=$yt$mt$dt'00'
					hp="$hp $ht1"
					wkht=`expr 00 + 1`
					while [ $wkht -le $ht ]
					do
					if [ $wkht -lt 10 ]
					then
						wkht=0$wkht
					fi
					hp="$hp $yt$mt$dt$wkht"
					wkht=`expr $wkht + 1`
					done
				fi				
			fi
		else
			if [ $ht = '23' ]
			then
				#mth = 01 .. $mt-1
				mt1=$yt'01'
				mth="$mth $mt1"
				wkmt=`expr 01 + 1`
				while [ $wkmt -lt $mt ]
				do
				if [ $wkmt -lt 10 ]
				then
					wkmt=0$wkmt
				fi
				mth="$mth $yt$wkmt"
				wkmt=`expr $wkmt + 1`
				done
				#dp = 01..$dt
				dt1=$yt$mt'01'
				dp="$hp $dt1"
				wkdt=`expr 01 + 1`
				while [ $wkdt -le $dt ]
				do
				if [ $wkdt -lt 10 ]
				then
					wkdt=0$wkdt
				fi
				dp="$dp $yt$mt$wkdt"
				wkdt=`expr $wkdt + 1`
				done
				echo do  ha: $ha da: $da yrs: $yrs mth: $mth dp: $dp
				echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
				exit
			else
				#mth = 01 .. $mt-1
				mt1=$yt'01'
				mth="$mth $mt1"
				wkmt=`expr 01 + 1`
				while [ $wkmt -lt $mt ]
				do
				if [ $wkmt -lt 10 ]
				then
					wkmt=0$wkmt
				fi
				mth="$mth $yt$wkmt"
				wkmt=`expr $wkmt + 1`
				done
				if [ $dt = '01' ]
				then
					dp=
				else
					#dp = 01..$dt-1
					dt1=$yt$mt'01'
					dp="$hp $dt1"
					wkdt=`expr 01 + 1`
					while [ $wkdt -lt $dt ]
					do
					if [ $wkdt -lt 10 ]
					then
						wkdt=0$wkdt
					fi
					dp="$dp $yt$mt$wkdt"
					wkdt=`expr $wkdt + 1`
					done	
				fi
				if [ $ht = '00' ]
				then
					hp="$yt$mt$dt$ht"
				else
				#hp = 00 .. $ht
					ht1=$yt$mt$dt'00'
					hp="$hp $ht1"
					wkht=`expr 00 + 1`
					while [ $wkht -le $ht ]
					do
					if [ $wkht -lt 10 ]
					then
						wkht=0$wkht
					fi
					hp="$hp $yt$mt$dt$wkht"
					wkht=`expr $wkht + 1`
					done
				fi
				
			fi
		fi
	fi
fi
echo do ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp
echo ./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
./do_acc.py "$dataset" $userIP $currentDateTime "ha: $ha da: $da mth: $mth yrs: $yrs dp: $dp hp: $hp"
exit
