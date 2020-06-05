#!/bin/bash

############################################################################################
#Reconocer variables
echo "La serie NEB de archivos se mostrara en VESTA"
read -p '    N carpetas      : ' NImages
NImagesDown1=$((NImages - 1))

read -p '    Nombre archivos : ' Type2View

############################################################################################
# Creando NEB

echo "Creando lista de visualizacion"

ViewLine="00/POSCAR"; ViewLine+=" "

for Img in $(seq 1 1 $NImagesDown1)
do
	if (($Img < 10))
	then
		ViewLine+=0$Img/$Type2View		
	else
		ViewLine+=$Img/$Type2View
	fi
	
	ViewLine+=" "
done

if (($NImages < 10))
then
	ViewLine+=0$NImages/POSCAR;
else
	ViewLine+=$NImages/POSCAR;
fi

echo "Abriendo VESTA"

VESTA $ViewLine

echo "VESTA out!"
