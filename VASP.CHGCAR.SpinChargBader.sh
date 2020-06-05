#!/bin/bash

#Separa CHGCAR en density part/ magnetic part
#cf1 charge density part, cf2 magnetism part spin difference charges
# chgsplit.sh CHGCAR

#Magnetismo por átomo según división por charge density
# bader cf2 -ref cf1

if [ $# -gt 0 ]; then
	while [ "$1" != "" ]; do
		case $1 in 
			-see)
				echo "Generando archivos"
				chgsplit.sh CHGCAR
				bader cf2 -ref cf1
				echo "Mostrando"
				vi ACF.dat
				echo "Limpiando"
				rm ACF.dat
				rm AVF.dat BCF.dat
				rm cf1 cf2
				echo ""
			;;
			-keep)
				echo "Generando archivos"
				chgsplit.sh CHGCAR
				bader cf2 -ref cf1
				echo "Renombrando archivo"
				mv ACF.dat SpinBader.Out
				echo "Limpiando"
				rm AVF.dat BCF.dat
				rm cf1 cf2
				echo ""
			;;
			-keepSplit)
				echo "Generando archivos"
				chgsplit.sh CHGCAR
				bader cf2 -ref cf1
				echo "Renombrando archivos"
				mv cf1 CHGCAR_Charge_Dens
				mv cf2 CHGCAR_Spin_Dens
				mv ACF.dat SpinBader.Out
				echo "Limpiando"
				rm AVF.dat BCF.dat
				echo ""
			;;
			-Clear)
				echo "Borrando archivos previos *.dat , cf* , CHGCAR_* y SpinBader.Out"
				rm -f ACF.dat AVF.dat BCF.dat
				rm -f cf1 cf2
				rm -f SpinBader.O*
				rm -f CHGCAR_Charge_Dens
				rm -f CHGCAR_Spin_Dens
			;;
			-h | *)
				echo "Opciones:"
				echo "        -see            : sólo muestra separación Bader, elimina todo archivo después"
				echo "        -keep (default) : guarda archivo bader de separación de magnetismo"
				echo "        -keepSplit      : guarda separación de CHGCAR y SpinBader"
				echo "        -Clear          : borra archivos previos *.dat , cf* , CHGCAR_* y SpinBader.Out"
				echo ""
			;;
		esac
		shift
	done
else
	echo ".....................................Organizando"
	mkdir Spin-Charg-Bader
	mv CHGCAR Spin-Charg-Bader
	cd Spin-Charg-Bader

	#Genera Spin
	echo ".....................................Generando archivos Spin"
	chgsplit.sh CHGCAR
	bader cf2 -ref cf1
	echo ".....................................Renombrando archivos Spin"
	mv ACF.dat SpinBader.Out
	echo ".....................................Limpiando archivos Spin"
	rm AVF.dat BCF.dat
	rm cf1 cf2
	echo ""

	#Genera Charg
	echo ".....................................Generando archivos Charg"
	bader CHGCAR
	echo ".....................................Renombrando archivos Charg"
	mv ACF.dat ChargBader.Out
	echo ".....................................Limpiando archivos Charg"
	rm AVF.dat BCF.dat

	#Concatenando resultados
	echo ".....................................Generando python compilador de resultados"
	
	cat << IncludePy >> CompileSpinCharge.py	

# coding: utf-8

# HowToUse: $ python interpolate.py file_A file_B numOfPoints
# numOfPoints > 2

import sys

error = False
if len(sys.argv) == 3:
    file_Charge = sys.argv[1]
    file_Spin = sys.argv[2]
else:
    error = True

if not error:
    NLines=sum(1 for line in open(file_Charge))
    
    def getTotal(filename):
        with open(filename) as f:
            content = f.readlines()
        f.close
        tmp =content [(NLines-1)].split()
        Total = tmp[3]
        return Total

    def getQuantity(filename,Col):
        with open(filename) as f:
            content = f.readlines()
        f.close()
        Quant = []
        for i in range(2,NLines-4):
            tmp = content[i].split()
            Quant.append([tmp[(Col-1)]])
        return Quant

    
    TotalCharg = getTotal(file_Charge)
    TotalMag = getTotal(file_Spin)
    AtomList = getQuantity(file_Charge,1)
    ChargeList = getQuantity(file_Charge,5)
    MagList = getQuantity(file_Spin,5)


    with open("Spin-Charge.out","w") as f:
        #Header
        f.write("  #   MAG   CHARGE" + "\n")
        f.write("------------------" + "\n")

        #Compilado
        for j in range(len(AtomList)):
            f.write(" " + str(AtomList[j][0]) + " | " + str(MagList[j][0]) + " | " + str(ChargeList[j][0]) + "\n")

        #Finalizando
        f.write("------------------" + "\n")
        f.write("Total Spin = " + str(TotalMag) + "\n")
        f.write("Total Charg = " + str(TotalCharg) + "\n")

    f.close()

else:
    sys.stdout.write("HowToUse: $ python interpolate.py file_A file_B numOfPoints" + '\n')
    sys.stdout.write("numOfPoints > 2 !!" + '\n')

IncludePy





	echo "..................................... . . . generado"

	echo ".....................................Compilando"
	ml Python/3.7.2
	python CompileSpinCharge.py ChargBader.Out SpinBader.Out

	echo ".....................................Limpiando"
	rm CompileSpinCharge.py

	echo "Listo!"
	tail -n 500 Spin-Charge.out

fi
