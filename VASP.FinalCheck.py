#!/usr/bin/env python3

# V.2.0 - 4/1/2020

import os
from datetime import datetime
CWD = os.getcwd()
FileList = os.listdir(os.getcwd())

#### ---------------------------------------------------------------- Tools

def StartSection(NSEct,iStr):
	print(' '*4+'['+str(NSEct)+'] '+iStr)

def RaiseWarming(iStr):
	print('')
	print(' '*4+'*'*40)
	print(' '*4+' WARNING: '+iStr)
	print(' ' * 4 + '*' * 40+'\n')

def StrFix(iStr,le):
	if len(iStr)<le:
		return ' '*(le-len(iStr))+iStr
	else:	return iStr

def StrFixDot(iStr,le):
	if len(iStr)<le:
		return iStr+'.'*(le-len(iStr))
	else:	return iStr

def Status(iStr, **kwargs):
	print(' ' * 8 + '> '+iStr, end=kwargs.get('end', '\n'))

def Report(iStr, *args,  **kwargs):
	if not kwargs.get('NewLine'):
		print(' ' * 8 + StrFixDot('> '+iStr+' ', DotL) + ' : ', end='')
	else:
		print(' ' * (11+DotL)+iStr, end='')
	for i in args: print(i, end=' ')
	print('', end=kwargs.get('end','\n'))


print('\n'+' '*4+'General check at the end of a VASP run\n')

#### ---------------------------------------------------------------- Parameters

DotL = 35
SectNumber = iter(range(20))
neb = False


#### ---------------------------------------------------------------- Submit and Job INFO
StartSection(next(SectNumber), 'Submit job info')

#### Jobinfo
if 'JobInfo' in FileList:
	Report('Jobinfo file found', end='')
	with open('JobInfo','r') as f:
		Jobinfo = f.readlines()

	# Job ID
	print('Job ID='+str(Jobinfo[0].split()[0]), end='')

	# Time spent
	try:
		# Get dates
		INI_line = Jobinfo[1].split()
		END_line = Jobinfo[3].split()
		INI_time = INI_line[4].split(':')
		END_time = END_line[4].split(':')
		INI_datetime = datetime(int(INI_line[6]), int(INI_line[5][1:]), int(INI_line[3]), int(INI_time[0]), int(INI_time[1]), int(INI_time[2]))
		END_datetime = datetime(int(END_line[6]), int(END_line[5][1:]), int(END_line[3]), int(END_time[0]), int(END_time[1]), int(END_time[2]))

		print(', elapsed time:'+str(END_datetime-INI_datetime))

	except:
		try:
			# Get dates
			INI_line = Jobinfo[1].split()
			END_line = Jobinfo[2].split()
			INI_time = INI_line[4].split(':')
			END_time = END_line[4].split(':')
			INI_datetime = datetime(int(INI_line[6]), int(INI_line[5][1:]), int(INI_line[3]), int(INI_time[0]), int(INI_time[1]), int(INI_time[2]))
			END_datetime = datetime(int(END_line[6]), int(END_line[5][1:]), int(END_line[3]), int(END_time[0]), int(END_time[1]), int(END_time[2]))

			RaiseWarming('No node line in JobInfo file, better check that out.')
			Report('Elapsed time', end='')
			print(str(END_datetime-INI_datetime))
		except:
			print()
			RaiseWarming('Timming information incomplete, better check that out.')


else:
	print(' '*8+'> Jobfile not found')



#### submit
FoundSubmit = False
for iFile in FileList:
	if 'submit' in iFile:
		FoundSubmit = True
		print(' ' * 8 + StrFixDot('> Submit file found ', DotL) + ' : ' + iFile, end=' , ')

		with open(iFile, 'r') as f:
			SubmitLines = f.readlines()
			f.close()

		for iLine in SubmitLines:
			if '#SBATCH -p' in iLine: print('partition:' + str(iLine.split()[2]), end=' , ')
			if '#SBATCH -n' in iLine:
				cpus = int(iLine.split()[2])
				print('cpu:' + str(cpus), end=' ')
			if '#SBATCH --mem-per-cpu' in iLine: print('mem/cpu:' + str(iLine.split('=')[1].split()[0]), end=' ')
			if '#SBATCH --ntasks-per-node' in iLine:
				taskpernode = int(iLine.split('=')[1].split()[0])
				print('task/node:' + str(taskpernode), end=' ')

		print()

if not FoundSubmit:
	print(' ' * 8 + '> Submit file not found, look like a local run')




#### ---------------------------------------------------------------- INCAR check
StartSection(next(SectNumber), 'Looking for INCAR file')
if 'INCAR' in FileList:
	# try:
		# Open
	with open('INCAR') as f:
		INCARfile = f.readlines()
	INCAR = {iLine.split('=')[0].strip():iLine.split('=')[1] for iLine in INCARfile if '=' in iLine}

	# Check runtype
	if 'IBRION' in INCAR:
		IBRION = int(INCAR['IBRION'])
		Report('INCAR file found', end='')

	# Check optimizers
	Henk, POTIM = (False, False)
	if 'POTIM' in INCAR: POTIM = float(INCAR['POTIM'])
	if POTIM == 0. and 'IOPT' in INCAR:
		Henk = True
		IOPT = int(INCAR['IOPT'])

	# Check neb
	neb, nebclimb = (False, False)
	if IBRION in [1,2,3]:
		if 'IMAGES' in INCAR:
			neb = True
			IMAGES = int(INCAR['IMAGES'])
			if 'LCLIMB' in INCAR and INCAR['LCLIMB']:
				nebclimb = True

	# Report runtype
	if IBRION in [5,6,7,8]:
		print('IBRION='+str(IBRION)+', frequency calculation')
	elif IBRION == -1:
		print('Static run, IBRION='+str(IBRION))
	elif neb:
		print('neb path: IMAGES=' + str(IMAGES)+', climbing='+str(nebclimb), end='')
		if Henk:
			print(', Henkelman optimizer='+str(IOPT), end='')
		else:
			print(', optimizer='+str(IBRION), end='')
		print()

	elif IBRION in [1,2]:
			print('IBRION='+str(IBRION)+', geometry relaxation')
	elif Henk and IBRION == 3:
		print('Henkelman optimizer IOPT='+str(IOPT))

	else:
		# IBRION = 3 not henkelman
		print('IBRION=' + str(IBRION) + ', molecular dynamics evolution')



	# Parallelization
	Report('Parallelization', end='')
	NPAR, KPAR, NCORE = (False, False, False)
	if 'NPAR' in INCAR:
		NPAR= int(INCAR['NPAR'])
		print('NPAR=' + str(NPAR), end=' ')
	if 'KPAR' in INCAR:
		KPAR= int(INCAR['KPAR'])
		print('KPAR=' + str(KPAR), end=' ')
	if 'NCORE' in INCAR:
		NCORE = int(INCAR['NCORE'])
		print('NCORE=' + str(KPAR), end=' ')

	if not (KPAR or NPAR or NCORE):
		print('Not found, probably a serial run', end='')
	print()




	# except:
	# 	RaiseWarming('Something went wrong when looking for info in the INCAR file')


else:
	print("INCAR file not found. That is weird, better take a closer look!")






#### ---------------------------------------------------------------- log info
def CountSteps(iFile):
	scpCounter=0
	geomCounter=0
	with open(iFile) as f:
		loglines=f.readlines()
	for line in [iLine for iLine in loglines if len(iLine.split())>1]:
		if line.split()[0] in ['DAV:','RMM:']: scpCounter+=1
		if 'E0=' in line.split(): geomCounter+=1
	return scpCounter, geomCounter




StartSection(next(SectNumber), 'Looking for log/stdout/OSZICAR files')
if neb:
	ListCounter = []

	nebFolders = ["{:02d}".format(i)+'/' for i in range(1,IMAGES+1)]
	for iFolder in nebFolders:
		iscp, igeom = CountSteps(iFolder+'/OSZICAR')
		# print(iFolder+':'+str(iscp)+', '+str(igeom))
		ListCounter.append((igeom, iscp))

	# print(ListCounter)

	totalscp = sum([i[1] for i in ListCounter])

	Report('neb OSZCAR files', 'total scp='+str(totalscp)+', geom steps='+str(ListCounter[0][0]))

	Report('Detailed per (image)geo/scp',end='')
	for i in range(len(nebFolders)):
		print('('+nebFolders[i][:-1]+')'+str(ListCounter[i][0])+'/'+str(ListCounter[i][1]), end=' ')
	print()

else:
	for iFile in FileList:
		if 'logfile' in iFile or 'Logfile' in iFile:
			LogFile = iFile
			print(' '*8+StrFixDot('> Logfile found ',DotL)+' : '+LogFile, end =' , ')

			scpCounter, geomCounter = CountSteps(LogFile)

			print('scp count : '+str(scpCounter), end=' , ')
			print('geom count : ' + str(geomCounter))



	# else: print(' '*4+'>>>> Did not found a logfile of the run')





#### ---------------------------------------------------------------- OUTCAR info
if not neb:
	StartSection(next(SectNumber),'Looking for OUTCAR files')

	print(' '*8+StrFixDot('> Opening OUTCAR ',DotL), end=' : ')
	with open('OUTCAR', 'r') as f:
		OUTCARlines = f.readlines()
		f.close()
	print('Ok', end=', ')

	if 'Voluntary context switches:' in OUTCARlines[-1]:
		print('properly finished run')
	else:
		print()
		RaiseWarming('Interrupted run')



	# Check IBRION
	for iLine in OUTCARlines:
		if len(iLine.split()) > 3:
			if 'IBRION' in iLine.split():
				IBRION=int(iLine.split()[2])
				print(' '*8+StrFixDot('> Recognize run type ',DotL)+' : '+str(IBRION),end=', ')
				if IBRION in [1,2]:
					print('geometry relaxation')
				elif IBRION == -1:
					print('static')
				elif IBRION in [5,6,7,8]:
					print('frequency')
				elif Henk:
					print(', Henkelman optimizer=' + str(IOPT))
				else: print('')

	# Dispersion correction
	if IBRION in [-1,1,2,3]:
		GotD3 = False
		print(' '*8+StrFixDot('> Dispersion correction ',DotL),end=' : ')
		for iLine in range(len(OUTCARlines)):
			ThisLine = OUTCARlines[len(OUTCARlines) - iLine - 1]

			if GotD3 == False:
				if 'IVDW' in ThisLine:
					GotD3 = True
					# Dispersion type
					print('found IVDW='+ThisLine.split()[2],end=', ')
					for i in OUTCARlines[len(OUTCARlines) - iLine - 2].split(): print(i, end=' ')
					print()
					# Dispersion energy
					while ' Edisp' not in OUTCARlines[len(OUTCARlines) - iLine - 2]: iLine+=1
					print(' ' * (11+DotL) + 'correction @ last geometry = ' + OUTCARlines[len(OUTCARlines) - iLine - 2].split()[2] + ' eV')
					break
		if GotD3 == False: print('Not found')






	# Recorre hacia arriba
	if IBRION in [1,2,3]:
		print(' '*8+StrFixDot('> Checking ending ',DotL), end=' : ')
		Convergido = False; GotE = False
		for iLine in range(len(OUTCARlines)):
			ThisLine = OUTCARlines[len(OUTCARlines) - iLine - 1]

			if Convergido == False:
				if ThisLine == " reached required accuracy - stopping structural energy minimisation\n":
					Convergido = True
					print('reached geometric convergence, yay !!!!')
				continue
			else:
				if len(ThisLine.split())>4:
					if ThisLine.split()[4] == "energy(sigma->0)" :
						Report('Energy (sigma->0) = '+ThisLine.split()[6]+' eV', NewLine=True)
						GotE = True
					else:
						continue
				else:
					continue
			if GotE==True:
				print(' '*4+'Done!')
				quit()
		if not GotE:
			print(' '*7+'> Couldn\'t find geometric convergence')
			print(' ' * 4 + 'Done!')

	elif IBRION in [5,6,7,8]:
		print(' '*8+StrFixDot('> Frequencies found ',DotL), end=' : ')
		#TODO: Add list
		tmpFreqListR = []
		tmpFreqListI = []
		Separe	= True
		for iLine in OUTCARlines:
			if 'THz' in iLine.split():
				# Real freqs
				if iLine.split()[1] == 'f':
					tmpFreqListR.append(float(iLine.split()[7]))
					print(StrFix(iLine.split()[0],2),end=' ')
					print('f   = ', end='')
					print(StrFix(iLine.split()[7],12),end=' ')
					print(StrFix(iLine.split()[8], 4),end=' ')
					print(StrFix(iLine.split()[9],12), end=' ')
					print(StrFix(iLine.split()[10],4))
				elif iLine.split()[1] == 'f/i=':
					if Separe == True:
						print('-'*45+'\n'+' '*(11+DotL), end='')
						Separe = False

					tmpFreqListI.append(float(iLine.split()[6]))
					print(StrFix(iLine.split()[0],2),end=' ')
					print('f/i = ', end='')
					print(StrFix(iLine.split()[6],12),end=' ')
					print(StrFix(iLine.split()[7], 4),end=' ')
					print(StrFix(iLine.split()[8],12), end=' ')
					print(StrFix(iLine.split()[9],4))
				print(' '*(11+DotL),end='')
		# List
		print('\n'+' '*10+'Real Freqs (cm-1): '+str(tmpFreqListR))
		print(' ' * 10 + 'Img  Freqs       : ' + str(tmpFreqListI))



		print('\n'+' ' * 4 + 'Done!')




	else: print(' ' * 4 + 'Done!')

