#!/bin/bash

echo 
echo "    Secuencia de revisión previo a lanzamiento individual"
echo
echo "=============================================================="
echo "    Revisión de INCAR"
echo "=============================================================="
cat INCAR
read -p '    > Ok?' Cont
echo "=============================================================="
echo "    Revisión de KPOINTS "
echo "=============================================================="
cat KPOINTS
read -p '    > Ok?' Cont
echo "=============================================================="
echo "    Elementos en POTCAR"
echo "=============================================================="
grep TITEL POTCAR
read -p '    > Ok?' Cont
echo "=============================================================="
echo "    Revisión de POSCAR"
echo "=============================================================="
cat POSCAR
read -p '    > Ok?' Cont
echo
echo ">>>> Todos los archivos en orden"
echo ">>>> Revisando disponibilidad de recursos"
echo 
sinfo
