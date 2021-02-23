#!/usr/bin/env python3

################################################################
################################ V.0

import sys
import numpy as np


def CodeStatus(inStr, **kwargs): print(' '*kwargs.get('l',4) + '> '+ inStr, end=kwargs.get('end','\n'))
def CodeError(inStr, **kwargs): print(' '*kwargs.get('l',2) + 'Error: >>>> '+ inStr)

def FolderFormat(iNum):
	return '{:02d}'.format(iNum)

def FixNumBlanck(ifloat, **kwargs):
	dec = '{:.'+str(kwargs.get('d',4))+'f}'
	length = kwargs.get('l', 10)
	strout = dec.format(ifloat)
	if len(strout)<length: strout = ' '*(length-len(strout))+strout
	return strout

def FixBlanck(iStr, **kwargs):
	length = kwargs.get('l', 10)
	strout = iStr
	if len(strout)<length: strout = ' '*(length-len(strout))+strout
	return strout

################################################################################################################################
################################################################################################################################

print(' '*4+'Generating XDATCAR5 reaction vmd movie from neb directory')

FileName = input(' '*4+'>> Filename of images (def=POSCAR) : ')
if FileName=='': FileName='POSCAR'


################ Collect folders
CodeStatus('Looking for images', end=' ')

ImagesCounter = 1
Head = None
Natoms = 0
AtomList = []
MovedAtoms = []
GeomFolder=[]
OutFile = 'POSCAR_nebPath'


#### Check initial file
try:
	f = open('./00/POSCAR','r')
	FileList = ['./00/POSCAR']
	print('.', end='')
	f.close()
except:
	print('')
	CodeError('No POSCAR on ./00/ folder was found. That\'s a must. Bye!')
	quit()

#### Get file list
while True:
	try:
		TestFile = './'+str(FolderFormat(ImagesCounter))+'/'+FileName
		f = open('./'+str(FolderFormat(ImagesCounter))+'/'+FileName,'r')
		FileList.append(TestFile)
		print('.', end='')
		ImagesCounter += 1
		f.close()
	except: break

#### Check final folder
if not FileList[-1].split('/')[-1] == 'POSCAR': #if the last is not POSCAR
	try:
		f = open('./'+str(FolderFormat(ImagesCounter))+'/POSCAR','r')
		FileList.append('./'+str(FolderFormat(ImagesCounter))+'/POSCAR')
		print('.', end='')
		ImagesCounter+=1
		f.close()
		print(' Ok')
	except:
		print()
		CodeError('Beware that the last tested folder (./'+FolderFormat(ImagesCounter)+') does not contain a POSCAR file')
else: print(' Ok')

CodeStatus('neb folder contained ' + str(ImagesCounter - 2) + ' images from folders 00/ to ' + str(FolderFormat(ImagesCounter - 1)) + '/')

#### Collect Head, review moved atoms
for iFile in FileList:
	#### Try to open
	with open(iFile, 'r') as f:
		iGeom = f.readlines()

	#### First image: Get head ? -> Create OutFile
	if Head == None:
		#### Get head
		Head = iGeom[0:7]
		#### Get number of atoms
		try:
			for iAt in iGeom[6].split(): Natoms+=int(iAt)
		except:
			CodeError('Atom type quantities not in 5th line. That POSCAR-type format is required. Bye!')
			break
		#### Construct AtomList
		try:
			for i in range(len(iGeom[6].split())):
				for j in range(int(iGeom[6].split()[i])):
					AtomList.append(iGeom[5].split()[i])
		except:
			CodeError('Could not  generate list of atoms, something is wrong on the atomic names (6th line) or their amounts (7th line). Bye!')
			break


		CodeStatus('Header properly retrieved, '+str(Natoms)+' atoms detected')

		#### Creating List of Moved Atoms
		for i in range(Natoms):
			MovedAtoms.append(False)
		#### Creating Output
		with open(OutFile,'w') as f:
			for iLine in Head[:6]:
				f.write(iLine)
		CodeStatus('Created file ' + OutFile+' to write neb path in POSCAR format')


	#### Check geometry format
	if not iGeom[7].split()[0][0] == 'S':
		CodeError('Selective dynamics (in 8th line) is assumed by this code. Image on '+str(FolderFormat(ImagesCounter))+'/'+FileName+' does not have that. Bye!')
		break
	if not iGeom[8].split()[0][0] == 'D':
		CodeError('All images need to define a \'Direct\' geometry on the 9th line. Image on '+str(FolderFormat(ImagesCounter))+'/'+FileName+' does not. Bye!')
		break

	#### Check atom movement
	for iAt in range(Natoms):
		if 'T' in iGeom[9+iAt].split()[3:]:
			MovedAtoms[iAt]=True
CodeStatus('Displaced atoms recognized. Only atoms with some T in selective dynamics are considered.')


#### Construct new atom numbers
CurrentAtom=AtomList[0]
AtomTypeCounter =  0
f = open(OutFile,'a')
for i in range(len(AtomList)):
	# Aglutinate if previous of the same type
	if AtomList[i] == CurrentAtom:
		if MovedAtoms[i]:
			AtomTypeCounter+=ImagesCounter
		else:
			AtomTypeCounter+=1
	else:
		f.write('   ' + str(AtomTypeCounter))
		# New type
		CurrentAtom  = AtomList[i]
		if MovedAtoms[i]:
			AtomTypeCounter = ImagesCounter
		else:
			AtomTypeCounter = 1
f.write('   '+str(AtomTypeCounter)+'\n')
f.write('Selective dynamics\nDirect\n')
f.close()
CodeStatus('Atomic list considering images was writted to '+OutFile)


#### Collect and write images
ImagesCounter = 0
G0 = open(FileList[0],'r')
of =  open(OutFile,'a')
Geom_0  = G0.readlines()
for iAt in range(Natoms):
	# Check if atom was moved
	if MovedAtoms[iAt]:
		for iFile in FileList:
			with open(iFile,'r') as Gi:
				Geom_i = Gi.readlines()
				Gi.close()
			of.write(Geom_i[9+iAt])
	else:
		of.write(Geom_0[9+iAt])
of.close()


CodeStatus('All images were properly included. POTCAR is also necesary for proper visualization in vmd. Bye!')


