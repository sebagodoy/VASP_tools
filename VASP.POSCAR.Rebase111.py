#! /usr/bin/env python3

################################################################

print('Rebase p(AxA) (111) to sqared cell')

#### Tools
def CodeStatus(iStr, **kwargs):
	print(' '*8+'> '+str(iStr), **kwargs)

def FixNum(iNum, Ndec=14):
	formatstr = '{:.'+str(Ndec)+'f}'
	return str(formatstr.format(iNum))
def FixStrLead(iStr, Length):
	return ' '*(Length-len(iStr))+iStr


######## Get file
iFileName = str(input('    Base geometry (def=CONTCAR) : '))
if iFileName == '': iFileName = 'CONTCAR'

try:
	# Opening
	CodeStatus('Opening file ...', end='')
	with open(iFileName, 'r') as f:
		iFile = f.readlines()
		f.close()
	print('Ok')

	# Get Head
	CodeStatus('Get Head, Name, Factor and Base vectors', end=' ... ')
	Head = iFile[:9]
	iName = iFile[0].strip()
	AtomLine = iFile[6].split()
	BaseFactor = float(iFile[1])
	# Test
	# print('Head:')
	# for i in Head: print((i))
	# print('Name:'+iName)
	# print('Atom line:'+str(AtomLine))
	# print('Base factor:'+str(BaseFactor))

	# BaseVect
	BaseVect =[]
	for i in range(3):
		BaseVect.append([float(j) for j in Head[2+i].split()])
	print('Ok')
	# Test
	# for i in BaseVect: print(i)

	# Get Atom numbers
	NAtoms = sum([int(i) for i in AtomLine])
	CodeStatus('Found '+str(NAtoms)+' atoms, retrieving coordinates', end=' ... ')

	# Get Atom Coordinates
	AtomCoords = []
	AtomFreedom = []
	for i in range(NAtoms):
		AtomCoords.append([float(j) for j in iFile[9+i].split()[:3]])
		AtomFreedom.append([k for k in iFile[9+i].split()[3:]])
	# Test
	# print()
	# for i,j in zip(AtomCoords, AtomFreedom):
	# 	print(str(i)+' ---- '+str(j))
	print('Ok')

	# Get Tail
	CodeStatus('Checking file tail', end=' ... ')
	FileTail = []
	if len(iFile) > 8+NAtoms:
		print('properly retrieved, Ok')
		FileTail = iFile[9+NAtoms:]
	else:
		print('tail empty, Ok')

except:
	quit(' '*8+'!'*30+'\n'+' '*8+'!! Sometjing went wrong \n'+' '*8+'!'*30)



######## Adapt base vectos and coordinates
CodeStatus('Adapting to real base and atom coordinates', end=' ... ')
# Real Base = Base Vectors * Base Factor
RealBase = []
for i in range(3):
	RealBase.append([j*BaseFactor for j in BaseVect[i]])
# Test
# print('\nReal Base:')
# for i in RealBase: print(i)

# Real Coordinates
RealAtomCoords = []
for iAt in AtomCoords:
	RealAtomCoords.append([sum([iAt[j]*RealBase[j][i] for j in range(3)]) for i in range(3)])
# Test
# for i in RealAtomCoords:
# 	print(i)

print('Ok')

######## Apply traslations for rebasing X coordinate

# New Base
NewBase = [RealBase[0],[0.,RealBase[1][1], 0.], RealBase[2]]
MaxPos = [NewBase[i][i] for i in range(3)]
# Test
# print('New base:')
# for i in NewBase: print(i)
# print('MaxPos:'+str(MaxPos))

# ask for traslation
DefTras = '.42 .025 .0'
NewBaseTranslation = input('    New base translation (fractional \'.x .x .x\', def='+DefTras+') : ')
# Defaul Traslation
if NewBaseTranslation == '':
	NewBaseTranslation = DefTras

if not NewBaseTranslation == '':
	try:
		# Get vector
		CustomTras = [float(i) for i in NewBaseTranslation.split()]
		CustomTrasStr = str([FixNum(CustomTras[k], 2) for k in range(3)])
		CodeStatus('Applying translation '+CustomTrasStr, end=' ... ')
		# Apply to RealAtomCoords
		for i in range(len(RealAtomCoords)):
			for j in range(3):
				RealAtomCoords[i][j]-=CustomTras[j]*MaxPos[j]
		print('Ok')
	except:
		quit(' '*8+'!'*30+'\n'+' '*8+'!! Sometjing went wrong \n'+' '*8+'!'*30)


CodeStatus('Adapting to rectangular base, applying symmetry translations', end= ' ... ')
## Apply 3D traslation symmetry
for i in range(len(RealAtomCoords)):
	for j in range(3):
		while RealAtomCoords[i][j] >= MaxPos[j]:
			RealAtomCoords[i][j]-= MaxPos[j]
		while RealAtomCoords[i][j] <0:
			RealAtomCoords[i][j]+= MaxPos[j]
## Direct Coordinates
DirectAtomCoords = []
for iRAC in RealAtomCoords:
	DirectAtomCoords.append([iRAC[i]/MaxPos[i] for i in range(3)])
print('Ok')



# Writting
FileName = str(input(' '*4+'Saving in new file. Filename (deafult=POSCAR) : '))
if FileName == '': FileName='POSCAR'
Name = str(input(' '*4+'Current name: '+iName+', wish to modify? (def=no) : '))
if Name == '': Name=iName

AddPrevName = input(' '*4+'Add info about base file? (def=y) :')
if not AddPrevName == 'n':
	Name += '__from__'+iName
	if not NewBaseTranslation == '':
		Name+='__traslated_by_'+CustomTrasStr


with open(FileName, 'w') as f:
	# Name
	f.write(Name+' '*4+'\n')

	# Factor
	f.write(' '*3+FixNum(1.))
	# Base vectors
	for iVect in NewBase:
		f.write('\n ')
		for j in iVect:
			f.write(FixStrLead(FixNum(j,16), 22))
	# Atom types and numbers
	f.write('\n'+Head[5])
	f.write(Head[6])
	# Selectivity
	f.write('Selective dynamics')
	f.write('\nDirect')
	# New atom coordinates
	for iAt in range(len(DirectAtomCoords)):
		f.write('\n')
		for j in range(3):
			f.write(FixStrLead(FixNum(DirectAtomCoords[iAt][j], 16), 20))
		for k in range(3):
			f.write(FixStrLead(AtomFreedom[iAt][k], 4))
	# Tail
	if len(FileTail) >0:
		f.write('\n')
		for iTailLine in FileTail:
			f.write(iTailLine)




