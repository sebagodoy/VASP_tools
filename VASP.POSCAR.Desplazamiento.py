#!/usr/bin/env python3


print(' Compara átomos selectos de dos archivos formato POSCAR devolviendo\n un vector promedio de desplazamiento\n')


######################### Tools:ini #########################
def SumLine(strline):
	nSum = 0.
	for iElement in strline.split():
		nSum+=float(iElement)
	return nSum

def GetList(StrAction):
	################# Get displacement groups ####################
	print('    Array a '+StrAction+': 1-24 26 32 ...')
	ArrayPattern = input('        >> ')

	PatternNumbers=[];

	for iGroup in ArrayPattern.split():
		#Caso grupo
		if "-" in iGroup:
			for iElement in range(int(iGroup.split('-')[0]),int(iGroup.split('-')[1])+1):
				PatternNumbers.append(iElement)
		else:
			PatternNumbers.append(int(iGroup))
	return PatternNumbers

def GetAtomNameList(conjuntos):
	strline = input('    Lista de nombres atomicos: ')
	if not len(strline.split())==len(conjuntos.split()):
		print('        Nombres y # grupos de atomos no coinciden')		
		print('        . . . adios!')
		quit()
	NameList = ''
	for iName in strline.split():
		NameList+=iName+' '
	NameList+='\n'
	return NameList

######################### Tools:fin #########################


Compare=[]
iFile1 = input('    Nombre de geometría de referencia : ')
Compare.append(GetList('comparar'))

iFile2 = input('    Nombre de geometría a modificar   : ')
if input('    Compara misma secuencia (y/def=n) :')=='y': Compare.append(Compare[0])
else: Compare.append(GetList('comparar'))


# Secuencias comparables?
if not len(Compare[0])==len(Compare[1]):
	print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	print('    !! Secuencias no tienen la misma cantidad     !!')
	print('    !! necesito eso para vivir, adios mundo cruel !!')
	print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
	quit()
print('    Secuencias comparables, abriendo archivos\n')




Files=[iFile1, iFile2]; CoordSystem = [[],[]];
for FileIndex in range(len(Files)):
	iFile=Files[FileIndex]
	
	# Get data
	print("    > Abriendo "+iFile)
	with open(iFile, 'r') as f:
		content = f.readlines()
		f.close()

	iLine = 5
	# Cantidad de átomos
	if len(content[iLine].split()) == len(content[iLine+1].split()) and not content[iLine+1][0]=='S':
		print('    > Detecta formato con nombres')
		nAtoms = int(SumLine(content[iLine+1]))
		iLine+=2
	else:
		print('    > Detecta formato sin nombres')
		# get atoms names
		nAtoms = int(SumLine(content[iLine]))
		iLine+=1
	print('    > Detecta '+str(nAtoms)+' átomos en el sistema')
	
	# Máximo de átomos
	if max(Compare[FileIndex])>nAtoms:
		print('    Un momento, eso no me calza con los que hay que comparar')
		quit()

	#Selective dynamics Line
	if 'S' in content[iLine]:
		print('    > Detecta Selective dynamics previo')
		iLine+=2
	else:
		print('    > No detecta Selective dynamics nuevo')
		iLine+=1

	#Check tipo de coordenadas
	if not 'D' in content[iLine-1]:
		print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
		print('    !! No detecta sistema de coordenadas directo  !!')
		print('    !! necesito eso para vivir, adios mundo cruel !!')
		print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
		quit()

	#Añade coordenadas
	print('    > Obteniendo coordenadas rel. relevantes', end=' ... ')
	for i in Compare[FileIndex]:
		print(i)
		ThisLine=content[iLine+i-1].split()
		CoordSystem[FileIndex].append([float(ThisLine[0]), float(ThisLine[1]), float(ThisLine[2])])
	print('Ok\n')



# Compara cantidad de átomos
if not len(CoordSystem[0])==len(CoordSystem[1]):
	print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	print('    !! La referencia tiene '+str(len(CoordSystem[0]))+' átomos.             !!')
	print('    !! El objetivo tiene '+str(len(CoordSystem[0]))+' átomos.               !!')
	print('    !! Y quieres que los compare? not today       !!')
	print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
	quit()
else:
	print('    > Los modelos son apropiadamente comparables')

# Check sistemas de coordenadas a comparar
for i in CoordSystem:
	for j in i:
		print(j)
	print('----')
print('-----------------------------------')

########################## Desplazamientos
print('    > Generando vectores de desplazamiento atómicos', end=' ... ')
Desplz=[[],[],[]]
for iAtom in range(len(CoordSystem[0])):
	for iCoord in range(3):
		Desplz[iCoord].append(CoordSystem[1][iAtom][iCoord]-CoordSystem[0][iAtom][iCoord])
print('Ok')

#Check sistema de desplazamientos generados
for i in range(len(Desplz[0])):
	print(str(Desplz[0][i])+'    '+str(Desplz[1][i])+'    '+str(Desplz[2][i]))


# Vector de desplazamiento promedio
print('    > Promediando vectores de desplazamiento', end='...')
DesplVector=[]
for iCoord in Desplz:
	tmpSum=0.; tmpCount=0
	for iElem in iCoord:
		tmpSum+=iElem
		tmpCount+=1
	DesplVector.append(tmpSum/tmpCount)
print('Ok\n')

# Check vector desplazamiento
print('vector')
print(DesplVector)
print('-----')


############################# Aplicar desplazamientp
print('    Vector aplicable a archivos POSCAR\n')

ApplyAgain=True

while ApplyAgain == True:

	# Nuevo POSCAR
	iFile = input('    Aplicar desplazamiento a archivo : ')

##  ------------------------------------------------------
	# Get data
	print('    > Abriendo', end=' ... ')
	with open(iFile, 'r') as f:
		content = f.readlines()
		f.close()
	print('Ok')

	# Top Box
	TopBox = content[0:5]
	print('    > Almacena Top Box')

	iLine = 5
	# Cantidad de átomos
	if len(content[iLine].split()) == len(content[iLine+1].split()) and not content[iLine+1][0]=='S':
		print('    > Detecta formato con nombres')
		nAtoms = int(SumLine(content[iLine+1]))
		iLine+=2
	else:
		print('    > Detecta formato sin nombres')
		nAtoms = int(SumLine(content[iLine]))
		iLine+=1
	print('    > Detecta '+str(nAtoms)+' átomos en el sistema')

	#Selective dynamics Line
	if 'S' in content[iLine]:
		print('    > Detecta Selective dynamics previo')
		iLine+=2
	else:
		print('    > No detecta Selective dynamics nuevo')
		iLine+=1

	#Check tipo de coordenadas
	if not 'D' in content[iLine-1]:
		print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
		print('    !! No detecta sistema de coordenadas directo  !!')
		print('    !! necesito eso para vivir, adios mundo cruel !!')
		print('    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
		quit()

	# Mid Box
	MidBox = content[5:iLine]
	print('    > Almacena Mid Box')
	print(MidBox)
	print('------>'+str(iLine))

	# Array a desplazar
	ModifyArray = GetList('desplazar')

	# Máximo de átomos
	if max(ModifyArray)>nAtoms:
		print('    Un momento, eso no me calza con los que hay que comparar')
		quit()

	# Añade coordenadas
	print('    > Obteniendo coordenadas relativas', end=' ... ')
	CoordsModify=[]; DynamicsModify=[]
	for i in range(nAtoms):
		ThisLine=content[iLine+i].split()
		CoordsModify.append([float(ThisLine[0]), float(ThisLine[1]), float(ThisLine[2])])
		DynamicsModify.append([ThisLine[3], ThisLine[4], ThisLine[5]])
	print('Ok\n')

	# Check
	print(len(CoordsModify))
	print(len(DynamicsModify))
	
	# Tail Box
	TailBox=content[iLine+nAtoms+1:]
	print('    > Almacena Tail Box')

	# Traslada coordenadas
	print('    > Desplazando coordenadas selectas', end=' ... ')
	for iAtom in ModifyArray:
		print(iAtom)
		for jCoord in range(3):
			CoordsModify[iAtom-1][jCoord]+=DesplVector[jCoord]
	print('Ok')


	################# Reescribe archivo ####################
	print('    > Sobrescribiendo archivo', end=' ... ')
	with open(iFile, 'w') as f:
		for i in TopBox:
			f.write(i)
		for j in MidBox:
			f.write(j)

		for iAt in range(nAtoms):
			for jCoor in range(3):
				f.write('  '+str('{:.16f}'.format(CoordsModify[iAt][jCoor])))
			for jDyn in range(3):
				f.write('   '+DynamicsModify[iAt][jDyn])
			f.write('\n')

		for k in TailBox:
			f.write(k)
	print('Ok\n')


	if not input('    Agregar a otro? (y/def=n) : ')=='y': ApplyAgain=False


print('end')















	


