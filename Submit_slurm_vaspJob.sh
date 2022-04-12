#!/bin/bash

echo "Preparando submit.job"

read -p '    Job Name : ' jobname
if ! [ -n "$jobname" ]; then echo "    Necesita esta variable"; exit; fi

read -p '    -p       : ' q
if ! [ -n "$q" ]; then echo "    Necesita esta variable"; exit; fi
if ! { [ "$q" = slims ] || [ "$q" = "general" ] || [ "$q" = "largemem" ]; }; then
	echo "Nombra bien la particion"
	exit
else
	if [ $q = "slims" ]; then mem=2400 ;fi
	if [ $q = "general" ]; then mem=4360 ;fi
	if [ $q = "largemem" ]; then mem=17450 ;fi
fi

read -p '    -N       : ' N
read -p '    -n       : ' nn
if ! [ -n "$nn" ]; then echo " Necesita esta variable"; exit; fi

read -p '    -task/nod: ' tpN

read -p '    -Mem/core: ' memCore
if [ -n "$memCore" ]; then
	mem=$memCore
fi

read -p '    -Mem/node: ' memNode
read -p '    -t       : ' hh

read -p '    Henkelman (y/n)  :' QyHenk

########## Inicializa archivos y direcciones
echo "    Inicializando direcciones y asignando numero de Job"

JobTrackDir=$HOME/JobTracker

jobnum=$(tail -1 $JobTrackDir/LaunchJob | awk '{print $1}')
jobnum=$((jobnum+1))



########## Generando archivo

echo "    Iniciando archivo submit.job.XXX"

echo "#!/bin/bash
#SBATCH -J "$jobname"."$jobnum"      # job name
#SBATCH -o logfile.%j."$jobnum"      # stdout file
#SBATCH -e errfile.%j."$jobnum"      # stderr file
#SBATCH -p "$q"            # queue" > submit.job.$jobnum

if [ -n "$N" ]; then 
	echo "#SBATCH -N "$N"           # Nodes" >> submit.job.$jobnum
fi

if [ -n "$hh" ]; then
	echo "#SBATCH -t "$hh":00       # run time duration" >> submit.job.$jobnum
fi

echo "#SBATCH -n "$nn" #nodes" >> submit.job.$jobnum

if [ -n "$memNode" ]; then
	echo "#SBATCH --mem="$memNode" #mem per node" >> submit.job.$jobnum
else
	echo "#SBATCH --mem-per-cpu="$mem" #mem" >> submit.job.$jobnum
fi

if [ -n "$tpN" ]; then
	echo "#SBATCH --ntasks-per-node="$tpN"         #n/N" >> submit.job.$jobnum
fi

echo "#SBATCH --mail-user=mymail@outlook.es
#SBATCH --mail-type=BEGIN,END,FAIL,TIME_LIMIT_80,TIME_LIMIT_90

touch JobInfo
echo INICIA \$(date) >>JobInfo
squeue -O name,jobid,nodelist| grep "$jobname" >>JobInfo" >> submit.job.$jobnum

if [ $QyHenk = y ]; then echo "ml intel/2018.04 VASP-VTST/5.4.4" >> submit.job.$jobnum;fi
if [ $QyHenk = n ]; then echo "ml intel/2018.04 VASP/5.4.4" >> submit.job.$jobnum;fi

echo "export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export MKL_DYNAMIC=FALSE

EXEC=vasp_std
BINVASP=\"\${EXEC}\"
export BINVASP

srun \$BINVASP

wait

echo TERMINA \$(date) >> JobInfo

exit" >> submit.job.$jobnum

########## Confirmación
echo "Revisando opciones
        #SBATCH -J "$jobname"
        #SBATCH -o logfile.%j
        #SBATCH -e errfile.%j
        #SBATCH -p "$q

if [ -n "$N" ]; then 
	echo "        #SBATCH -N "$N"           # Nodes"
fi

if [ -n "$hh" ]; then
	echo "        #SBATCH -t "$hh":00       # run time duration"
fi

echo "        #SBATCH -n "$nn"          # cores"

if [ -n "$memNode" ]; then
	echo "        #SBATCH --mem="$memNode" #mem/node"
else
	echo "        #SBATCH --mem-per-cpu="$mem" #mem"
fi

if [ -n "$tpN" ]; then
	echo "        #SBATCH --ntasks-per-node="$tpN"        #n/N"
fi

echo "        #SBATCH --mail-user=seba.god.gut@outlook.es
        #SBATCH --mail-type=BEGIN,END,FAIL,TIME_LIMIT_80,TIME_LIMIT_90"

echo 
echo

read -p 'Confirma (yes/*) : ' ConfirmRun
if [ "$ConfirmRun" = "yes" ]; then
	echo "Confirmado!, agregando a log y lanzando"
	echo "    JobID="$jobnum " / Subido el =" $(date)
	echo "    $jobnum $jobname $(date) $PWD"
	echo "$jobnum |n| $jobname |d| $(date) |dir| $PWD" >>  $JobTrackDir/LaunchJob
	sbatch submit.job.$jobnum

	cat ~/JobTracker/LaunchJob | tail -n 1 >> JobInfo

	sleep 2
	squeue
	echo

else
      	echo "No harm done"
	rm submit.job.$jobnum
fi

exit

