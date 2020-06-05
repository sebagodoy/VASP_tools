#! /bin/bash

################## Initialize variables ####################
fcutoff="0"
rottr="no"
userT=""
userP=""

################## Define Constants ####################
pi="3.14159265359"
m_e="1.66053892*10^-27"
q_e="1.60217657*10^-19"
kB="1.3806488*10^-23"
R="8.3144621"
h="6.62606957*10^-34"
c="299792458"
NA="6.02214129*10^23"
eVperh="27.211396132"
kjpmpereV="96.4853367607"

################## Help text ####################
help(){
echo '-------------------------------------------------------------------------------------------------'
echo '|  This script uses the output of a VASP frequency calculation to derive enthalpy and free   '
echo '|  energy values at user specified T, P, low frequency cutoff value. It  excludes all      '
echo '|  rotational and translational contribution to these values '
echo '-------------------------------------------------------------------------------------------------'
echo  'Format:'
echo  '    gvib.sh [options [arguments]] <Gaussian_output_file> '
echo  'Options:'
echo  '   -h'
echo  '     Display help'
echo  '   -f <frequency_value>'
echo  '     Set low frequency cutoff in cm-1; default value is 0'
echo  '   -T <temperature_value>'
echo  '     Specify temperature in K; by default 298.15 K is used'
echo  '   -P <pressure_value>'
echo  '     Specify pressure in atm; by default 1 atm is used'
echo  '   -x'
echo  '     Exclude rotation and translation; recommended for surface species'
exit 0
}

################## Process options ####################
while getopts "hxf:T:P:" arg; do
        case $arg in
                h) help  ;;
                x) rottr="no"  ;;
                f) fcutoff=$OPTARG  ;;
                T) userT=$OPTARG   ;;
                P) userP=$OPTARG   ;;
               \?) help ;;
        esac
done
shift $((OPTIND -1))

##### Read Gaussian output, write frequencies to FREQfile ###############
vibfile=$1
FREQfile="FREQ"
#m=$(grep 'Molecular mass' $vibfile | tr -s ' ' | cut -d' ' -f4 | sed '/\./ s/\.\{0,1\}0\{1,\}$//')
T="553.15" #$(grep Temperature $vibfile | tr -s ' ' | cut -d' ' -f3 | sed '/\./ s/\.\{0,1\}0\{1,\}$//')
P="1.0" #$(grep Temperature $vibfile | tr -s ' ' | cut -d' ' -f6 | sed '/\./ s/\.\{0,1\}0\{1,\}$//') 
#rtemp=$(grep 'Rotational temperature' $vibfile)
#rt1=$(echo $rtemp | tr -s ' ' | cut -d' ' -f 4)
#rt2=$(echo $rtemp | tr -s ' ' | cut -d' ' -f 5)
#rt3=$(echo $rtemp | tr -s ' ' | cut -d' ' -f 6)
#sigma=$(grep 'Rotational symmetry number' $vibfile | tr -s ' ' | cut -d' ' -f 5)
#linear="0"
#if [ "$rt2" == "" ]; then 
#linear="1"   ## molecule is linear
#fi

nline=$(grep 'cm-1' $vibfile | awk '{print $3}' | wc -l)

f1=($(grep 'cm-1' $vibfile | awk '{print $8}'))
f2=($(grep 'cm-1' $vibfile | awk '{print $7}'))

# Borra anterior
if [ -s $FREQfile ]; then
rm $FREQfile
fi

for ((i=0; i<$nline; i++))
do

if [ "${f1[$i]}" != "cm-1" ]; then
freq[$(($i))]="${f1[$i]}"
echo ${f1[$i]} >> $FREQfile
else # negativos
freq[$(($i))]="-${f2[$i]}"
echo "-${f2[$i]}" >> $FREQfile
fi
done

nfreq=$nline

###########Electronic Energy##########################
#eel=$(tac $vibfile | grep -m 1 "E(" | tr -s ' ' | cut -d' ' -f6)
#eel=$(echo "scale=70; $eel * $eVperh * $kjpmpereV " | bc -l)

##### Set T and P, if supplied by user ###############
if [ "$userT" != "" ]; then
T=$userT
fi

if [ "$userP" != "" ]; then
P=$userP
fi

analfile=${vibfile%%"."*}"_vibT"$T"P"$P"f"$fcutoff
patm=$P
P=$(echo "scale=70; $P * 101325.0" | bc -l )

##### Calculate trans-rot H, S components ###############
#htr=0
#hrot=0
#str=0
#srot=0
#if [ "$rottr" == "yes" ] ; then
#  htr=$(echo "scale=70; 2.5 * $R * $T / 1000.0 " | bc -l)
#  str=$(echo "scale=70; $R * (2.5 + l($kB * $T / $P * sqrt((2.0 * $pi * $m * $m_e * $kB * $T / ($h) / ($h)  )^3) ) )" | bc -l)
#  if [ "$linear" == "1" ]; then
#   hrot=$(echo "scale=70; 1.0 * $R * $T / 1000.0 " | bc -l)
#   srot=$(echo "scale=70; $R * (1.0 + l( $T / $rt1 / $sigma) ) " | bc -l)
#  else
#   hrot=$(echo "scale=70; 1.5 * $R * $T / 1000.0 " | bc -l)
#   srot=$(echo "scale=70; $R * (1.5 + l( sqrt($pi * $T^3 / $rt1 / $rt2 / $rt3) / $sigma ) ) " | bc -l)
#  fi
#else
#analfile=$analfile"_x"
#fi

##### Calculate vib components ###############
zpve="0"
hvib="0"
svib="0"
for el in ${freq[@]} ; do
if (( $(echo "$el > $fcutoff" | bc -l) )); then  # $el is higher than the cutoff
hnu=$(echo "scale=70; $h * $c * $el * 100.0" | bc -l)
hnukbt=$(echo "scale=70; $hnu / ($kB) / $T" | bc -l)
zpve=$(echo "scale=70; $zpve + $NA * $hnu / 2.0 / 1000.0 " | bc -l)
hvib=$(echo "scale=70; $hvib + $NA * $hnu /(e($hnukbt) - 1.0) / 1000.0 " | bc -l)
svib=$(echo "scale=70; $svib + $R * ( $hnukbt /(e($hnukbt) - 1.0) - l(1.0 - e(-$hnukbt) ))" | bc -l)
fi
done

################## Add components #######################
htot=$(echo "scale=70; $eel + $zpve + $htr + $hrot + $hvib" | bc -l)
stot=$(echo "scale=70; $str + $srot + $svib" | bc -l)
gtot=$(echo "scale=70; $htot - $stot * $T / 1000.0" | bc -l)

################## Print results #######################
eel=$(echo $eel | cut -c1-15 )
zpve=$(echo $zpve | cut -c1-15 )
htr=$(echo $htr | cut -c1-15 )
hrot=$(echo $hrot | cut -c1-15 )
hvib=$(echo $hvib | cut -c1-15 )
htot=$(echo $htot | cut -c1-15 )
str=$(echo $str | cut -c1-15 )
srot=$(echo $srot | cut -c1-15 )
svib=$(echo $svib | cut -c1-15 )
stot=$(echo $stot | cut -c1-15 )
gtot=$(echo $gtot | cut -c1-15 )

echo "T = "$T" K
P = "$patm" atm
Cutoff freq. = "$fcutoff" cm-1
Include rotation and translation? "$rottr"
-----------------------------
E(0)  = "$eel" kJ/mol
ZPVE  = "$zpve"  kJ/mol
-----------------------------
H(tr) = "$htr" kJ/mol
S(tr) = "$str" J/(mol K)
H(rot) = "$hrot" kJ/mol
S(rot) = "$srot" J/(mol K)
H(vib) = "$hvib" kJ/mol
S(vib) = "$svib" J/(mol K)
----------------------------
H(tot) = "$htot" kJ/mol
S(tot) = "$stot" J/(mol K) 
G(tot) = "$gtot" kJ/mol" > $analfile

cat $analfile

