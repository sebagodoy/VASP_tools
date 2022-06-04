#!/bin/bash

echo "Given AECCAR files and CHGCAR for a spin polarized calculation\n the bader charges and magnetism will be computed"

echo "0) Preparing folder and files"
mkdir Bader_analysis_charges_magnetism
mv AECCAR0 ./Bader_analysis_charges_magnetism/AECCAR0
mv AECCAR1 ./Bader_analysis_charges_magnetism/AECCAR1
mv AECCAR2 ./Bader_analysis_charges_magnetism/AECCAR2
mv CHGCAR ./Bader_analysis_charges_magnetism/CHGCAR
cd ./Bader_analysis_charges_magnetism

echo "1) Sum initial cores (AECCAR0) and final valence e (AECCAR2) to CHGCAR_sum"
chgsum.pl AECCAR0 AECCAR2

echo "2) Split spin-polarized CHGCAR to total charges (CHGCAR_tot) and spin polarized charge (CHGCAR_mag)"
chgsplit.pl CHGCAR

echo "3) Get total bader charges (bader CHGCAR_tot -ref CHGCAR_sum)"
# It would be the same to use bader CHGCAR -ref CHGCAR_sum
bader CHGCAR_tot -ref CHGCAR_sum

echo "4) Remane bader files for total charge"
mv ACF.dat tot_ACF.dat
mv AVF.dat tot_AVF.dat
mv BCF.dat tot_BCF.dat

echo "5) Get spin polarized charges (bader CHGCAR_mag -ref CHGCAR_sum)"
bader CHGCAR_mag -ref CHGCAR_sum

echo "6) Remane bader files for magnetism"
mv ACF.dat mag_ACF.dat
mv AVF.dat mag_AVF.dat
mv BCF.dat mag_BCF.dat


echo ""
echo "Correctly done. Check ./Bader_analysis_charges_magnetism for charge in file tot_ACF.dat and for magnatization in file mag_ACF.dat"

echo ""
echo "Compilig charge density partition and integrated spin polarization"
BaderCoresSpin_cat.py

echo "Done. Check the Bader_analysis_charges_magnetism/Bader_Analysis_cat.dat file"
