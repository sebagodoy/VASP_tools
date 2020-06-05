#!/bin/bash

# How to use: myNEB.lineal.sh POSCAR1name POSCAR2name #Imagenes

############################################################################################
#Reconocer variables
if [ $# -gt 0 ]; then
	echo "Se reconocieron $# variables"
else
	echo "No se reconocen variables"
	echo "Uso: myNeb.Lineal <POSCAR_1> <POSCAR_2> <N imagenes>"
	exit
fi

echo "Asignando varibles"
if [ "$1" != "" ]; then
	POSCAR1=$1 
fi
if [ "$2" != "" ]; then
	POSCAR2=$2
fi
if [ "$3" != "" ]; then
	IMAGES=$3
	ImagesP1=$((IMAGES + 1))
	ImagesP2=$((IMAGES + 2))
fi
echo "        Ok"

############################################################################################
#Moviendo POSCARs
cp $POSCAR1 ./ImgInicial
cp $POSCAR2 ./ImgFinal



############################################################################################
#Creando Interpol.py
echo "Creando Interpol.py"
cat << IncludePy >> Interpol.py

# coding: utf-8

# HowToUse: $ python interpolate.py file_A file_B numOfPoints
# numOfPoints > 2

import sys

error = False
if len(sys.argv) == 4:
    file_A = sys.argv[1]
    file_B = sys.argv[2]
    numOfPoints = int(sys.argv[3])
    if(numOfPoints <= 2):
        error = True
else:
    error = True

if not error:
    def get_coordinates(filename):
        with open(filename) as f:
            content = f.readlines()
        f.close()
        header = content[0:9]
        coordinates = []
        SomeLetter = []
        num_coord = 0
        for tmp in content[6].split():
            num_coord += int(tmp)
        footer = content[(9+num_coord):]
        for i in range(9,9+num_coord):
            tmp = content[i].split()
            coordinates.append([float(tmp[0]),float(tmp[1]),float(tmp[2])])
            SomeLetter.append([tmp[3],tmp[4],tmp[5]])
        return coordinates, header, footer, SomeLetter

    def lerp(v0, v1, i):
        return v0 + i * (v1 - v0)

    def getEquidistantPoints(p1, p2, n):
        return [(lerp(p1[0],p2[0],1./n*i), lerp(p1[1],p2[1],1./n*i),  lerp(p1[2],p2[2],1./n*i)) for i in range(n+1)]

    def interpolate_coord(c1, c2, num = 1):
        # c1 = first coord.
        # c2 = second coord.
        # num = interpolated points
        num = int(num)
        output = []
        if num > 0:
            min_len = len(c1) if len(c1) <= len(c2) else len(c2)
            for i in range(0,min_len):
                output.append(getEquidistantPoints(c1[i],c2[i],num+1))
        return output

    def replaceSomeLetterwithF(SL1, SL2):
        output = []
        min_len = len(SL1) if len(SL1) <= len(SL2) else len(Sl2)
        for i in range(0,min_len):
            a = SL1[i][0] if SL1[i][0] == SL2[i][0] else "F"
            b = SL1[i][1] if SL1[i][1] == SL2[i][1] else "F"
            c = SL1[i][2] if SL1[i][2] == SL2[i][2] else "F"
            output.append([a,b,c])
        return output

    coord_1, header_1, footer_1, SomeLetter_1 = get_coordinates(file_A)
    coord_2, header_2, footer_2, SomeLetter_2 = get_coordinates(file_B)

    SomeLetter = replaceSomeLetterwithF(SomeLetter_1,SomeLetter_2)
    new_coord = interpolate_coord(coord_1, coord_2, numOfPoints-2)
    header = header_1
    footer = footer_1

    for i in range(1, numOfPoints + 1):
        with open("Img_N"+str(i),"w") as f:
            # write header
            for line in header:
                f.write(line)
            for j in range(len(new_coord)):
                line = " {0: .16f} {1: .16f} {2: .16f}   {3}   {4}   {5}\n".format(new_coord[j][i-1][0],new_coord[j][i-1][1],new_coord[j][i-1][2],SomeLetter[j][0],SomeLetter[j][1],SomeLetter[j][2])
                f.write(line)
            for line in footer:
                f.write(line)
        f.close()
else:
    sys.stdout.write("HowToUse: $ python interpolate.py file_A file_B numOfPoints" + '\n')
    sys.stdout.write("numOfPoints > 2 !!" + '\n')

IncludePy
echo "        Ok"

############################################################################################
# Creando NEB
echo "Creando imágenes NEB"
python Interpol.py ImgInicial ImgFinal $ImagesP2
echo "        Ok"

rm ImgInicial ImgFinal

echo "Reordenando imágenes"
for Img in $(seq 0 1 $ImagesP1)
do
	((ImgP1=$Img+1))

	ThisImg="Img_N"; ThisImg+=$ImgP1

	if (($Img < 10))
	then
		mkdir 0$Img
		mv $ThisImg 0$Img/POSCAR
	else
		mkdir $Img
		mv $ThisImg $Img/POSCAR
	fi
done
echo "        Ok"

echo "Todo Listo!"

rm Interpol.py
