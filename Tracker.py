#!/usr/bin/env python3

#######################################################################################################################
#
#	Fecha 		5/En/2021
#	Version		2.0 (incompatible con versiones anteriores por estructura del Logfile)
#	
#	Descripción: 	Script interpretado por python para crear, actualizar y revisar un registro (LogTracker, otro nombre
#					requiere modificación de este archivo).
#	Requiere: 		Binario de python3.algo en /usr/bin/env
#	Uso:		1) Inicializa LogTracker file con línea 000: 	$ Tracker.py -create
#				2) Añade nueva entrada al archivo LogTracker:	$ Tracker.py -add
#				3) Revisa últimas entradas de LogTracker:		$ Tracker.py -log
#				4) Remove last N entries:						$ Tracker.py -remove
#
#######################################################################################################################
#### Packages
import sys
import os



######################################################################################################################
print(' '*4+'Time Tracker for cluster usage')

DataFile = 'LogTracker'
DirDataFile = os.path.abspath(__file__)[:-10]+DataFile


def AddEntry(iDataFile):
	ID		= int(input(' ' * 8 + 'ID		: ') or 0.)
	Mj		= input(' ' * 8 + 'Description	: ') or 'X'
	nC 		= int(input(' ' * 8 + 'Cores		: '))
	nN		= int(input(' ' * 8 + 'Nodes		: '))
	tpN		= int(input(' ' * 8 + 'task/node	: '))
	NP 		= int(input(' ' * 8 + 'NPAR		: '))
	KP		= int(input(' ' * 8 + 'KPAR		: '))
	scp		= int(input(' ' * 8 + 'N scp		: ') or 0)

	# Time treatment: this one
	t	= str(input(' ' * 8 + 'Spend time	: ') or '0:00')
	tH	= int(t.split(':')[0])
	tm	= int(t.split(':')[1])
	if len(t.split(':')) == 3:
		ts = int(t.split(':')[2])
	else:
		ts=0

	# spent cpu time
	ct_h = tH * nC
	ct_m = tm * nC
	ct_s = ts * nC

	# time seg/scp
	rtpscp = (tH*3600+tm*60+ts)/scp		# runtime / scp (in seg)
	ctpscp = (tH*3600+tm*60+ts)*nC/scp	# cpu time / scp (in seg)


	# Time treatment: add to previous
	with open(iDataFile,'r') as f:
		PrevEntries = f.readlines()
		# Get previous summed hours
		Prt	= PrevEntries[-1].split(',')[8] # Previous accumulated runtime
		Pct = PrevEntries[-1].split(',')[10] # Previus accumulated Cpu time

		f.close()


	#### New runtime
	Nrt_s = int(Prt.split(':')[2])+ts
	Nrt_m = int(Prt.split(':')[1])+tm
	Nrt_h = int(Prt.split(':')[0])+tH

	#### New cpu time
	Nct_s = int(Pct.split(':')[2])+ct_s
	Nct_m = int(Pct.split(':')[1])+ct_m
	Nct_h = int(Pct.split(':')[0])+ct_h

	def FixTime(iHour, iMin, iSeg):
		while iSeg >= 60:
			iMin+=1
			iSeg-=60
		while iMin >= 60:
			iHour+=1
			iMin-=60
		return str(iHour)+':'+str('{:02d}'.format(iMin))+':'+str('{:02d}'.format(iSeg))

	def FixStr(StrIn, Xlen):
		if len(StrIn)<Xlen: return ' '*(Xlen-len(StrIn))+StrIn
		else: return StrIn


	if input(' '*4+'> Confirm addition (y/def=n):') == 'y':
		with open(iDataFile,'a') as f:
			f.write(FixStr(str(ID),4)+' , ')						# ID
			f.write(FixStr(str(nC), 3) + ' , ') 					# cpu
			for i in [nN, tpN]:	f.write(FixStr(str(i),5) + ' , ')	# nodes, task/node
			for i in [NP, KP]:	f.write(FixStr(str(i),4) + ' , ')	# NPAR, KPAR
			f.write(FixStr(str(scp), 5) + ' , ')					# scp
			f.write(FixStr(FixTime(tH, tm, ts),9)+' , ')

			f.write(FixStr(FixTime(Nrt_h, Nrt_m, Nrt_s),12)+' , ')		# Acc. runtime
			f.write(FixStr(FixTime(ct_h, ct_m, ct_s),14)+' , ')			# spent cpu time
			f.write(FixStr(FixTime(Nct_h, Nct_m, Nct_s), 13) + ' , ')	# Acc. cpu time

			f.write(FixStr('{:.1f}'.format(rtpscp), 7)+' , ')
			f.write(FixStr('{:.1f}'.format(ctpscp), 9) + ' , ')

			f.write(Mj)

			f.write('\n')
		print(' '*4+'> Entry added to log')
	else:
		print(' '*4+'='*30+'\n'+' '*5+'Entry not added\n'+' '*4+'='*30)



#### ---------------------------------------------------------------- Running
TableHeader	= '  ID | cpu | nodes | tsk/n | NPAR | KPAR | N scp |  run time |  Acc.runtime | spent cpu time | Acc. cpu time |   t/scp | t.cpu/scp | Message\n'
TableLine 	= '0000 ,  00 ,     0 ,     0 ,    0 ,    0 , 00000 , 000:00:00 , 000000:00:00 ,    00000:00:00 , 0000000:00:00 , 00000.0 ,   00000.0 , This is a brief message\n'

if len(sys.argv)>1:
	Action = sys.argv[1][1:]
	if Action == 'create':
		NewFilename = input(' ' * 4 + '>>>> New log file named (def='+DataFile+') : ') or DataFile
		DirNewFile	= os.path.abspath(__file__)[:-10] + NewFilename

		with open(DirNewFile, 'w') as f:
			f.write('  '+'#'*200+'\n  #'+'\n  #  Tracker log file: < Description> '+'\n  #\n  '+'#'*200+'\n\n')
			f.write(TableHeader)
			f.write(TableLine)
		print(' ' * 4 + '>>>> Created new log file named '+NewFilename+' on ')
		print(DirNewFile + '\n')


	elif Action == 'add':
		print(' ' * 4 + '>>>> Adding entry to registry')
		AddEntry(DirDataFile)


	elif Action == 'log':
		print(' ' * 4 + '>>>> Showing last log entries')
		with open(DirDataFile,'r') as f:
			Log = f.readlines()

			nLog = min(int(input(' ' * 4 + '>>>> How many lines to show? (def=5) : ') or 5), len(Log)-7)
			HeadLogCounterMax  = 25
			HeadLogCounter = 0
			print(TableHeader, end='')
			for i in range(nLog):
				print(Log[len(Log)-nLog+i], end='')
				if HeadLogCounter < HeadLogCounterMax:
					HeadLogCounter+=1
				else:
					print('\n'+TableHeader)
					HeadLogCounter = 0


		print('\n')


	elif Action == 'remove':
		n2remove = int(input(' '*4+'>'*4+' From the last one, how many entries to remove? (def=1) : ') or 1)
		if input(' '*4+'>'*4+' Are you sure to remove '+str(n2remove)+' lines?  (y/def=n) : ') == 'y':
			print(' '*4+'> Reading file')
			with open(DirDataFile, 'r') as f:
				PrevFullLog = f.readlines()
				# Check max to remove
				if len(PrevFullLog)-8 < n2remove:
					if not input(' '*4+'>'*4+' Log file is shorter than expected, this fully clean it. Are you sure? (y/def=n) : ') == 'y':
						print(' '*4+'> Relax, nothing was done.')
						quit()
					n2remove = min(n2remove, len(PrevFullLog)-8)


			print(' ' * 4 + '> Overwriting file')
			with open(DirDataFile, 'w') as f:
				for iLine in PrevFullLog[:-n2remove]:
					f.write(iLine)
			print(' '*4+'>'*4+' '+str(n2remove)+' lines were removed')
		else:
			print(' '*4+'> Relax, nothing was done.')


	else:
		print(' '*4+'Option not recognized, bye!')





