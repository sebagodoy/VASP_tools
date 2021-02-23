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
OutFile = 'nebMovie_XDATCAR5'


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
if not FileList[-1].split('/')[-1] == 'POSCAR':
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

#### Collect and write images
ImagesCounter = 0
for iFile in FileList:
	#### Try to open
	with open(iFile,'r') as f:
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
		CodeStatus('Header properly retrieved, '+str(Natoms)+' atoms detected')
		#### Creating Output
		with open(OutFile,'w') as f:
			for iLine in Head:
				f.write(iLine)
		CodeStatus('Created file ' + OutFile+' to write movie un XDATCAR-vmd format')


	#### Check geometry format
	if not iGeom[8].split()[0][0] == 'D':
		CodeError('All images need to define a \'Direct\' geometry on the 9th line. Image on '+str(FolderFormat(ImagesCounter))+'/'+FileName+' does not. Bye!')
		break

	#### Collect geometry
	with open(OutFile,'a') as f:
		f.write('Direct configuration='+FixBlanck(str(ImagesCounter+1),l=6)+'\n')
		for iAt in iGeom[9:9+Natoms]:
			f.write(' ')
			for i in range(3): f.write('  '+iAt.split()[i])
			f.write('\n')


	# Prepare for enxt image
	ImagesCounter+=1

#### Line for final geom
with open(OutFile,'a') as f: f.write('Direct configuration='+FixBlanck(str(ImagesCounter+1),l=6)+'\n')

CodeStatus('All images were properly included. POTCAR is also necesary for proper visualization in vmd. Bye!')


