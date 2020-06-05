#!/usr/bin/env python3


print('Anular movimiento de átomos en archivo MODECAR')

iFile = input('    Nombre de archivo : ')


# Get data
print('    Abre archivo coordenadas', end=' ... ')
with open(iFile, 'r') as f:
	content = f.readlines()
	f.close()
print('Ok')


################# Get frozen groups ####################
print('    Patron a anular: 1-24 26 32 ...')
AnulaPattern = input('                  >> ')

PatternNumbers=[]; MaxNumber=0

for iGroup in AnulaPattern.split():
	#Caso grupo
	if "-" in iGroup:
		for iElement in range(int(iGroup.split('-')[0]),int(iGroup.split('-')[1])+1):
			PatternNumbers.append(iElement)
			if iElement>MaxNumber: MaxNumber=iElement
	else:
		PatternNumbers.append(int(iGroup))
		if int(iGroup)>MaxNumber: MaxNumber=int(iGroup)

# Check límite
if MaxNumber>len(content):
	print("    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	print("    !! Excede cantidad de átomos en MODECAR !!")
	print("    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	quit()

# Lista de dimensiones
Dimens=[]
for i in content:
	for j in i.split():
		Dimens.append(float(j))
# Elimina
for i in PatternNumbers:
	Dimens[i*3-1]=0.
	Dimens[i*3-2]=0.
	Dimens[i*3-3]=0.

# Normaliza
Mag=0.
for i in Dimens:
	Mag+=i**2

Mag=Mag**(0.5)
print("    > Magnitud purgada : "+str(Mag))

for i in range(len(Dimens)):
	Dimens[i]=Dimens[i]/Mag

NewMag=0.
for i in Dimens:
	NewMag+=i**2
print("    > Magnitud normalizada : "+str(Mag))

# Sobreescribiendo
qyOver=input("    > Sobrescribir archivo? (def=n/y) : ")
if qyOver == 'y': NewName=iFile
else: NewName=iFile+'_Restricto'

with open(NewName,'w') as f:
	Count=0
	for iNum in Dimens:
		if iNum<0.: ThisNum='   '
		else: ThisNum='    '
		ThisNum+=str('{:.10E}'.format(iNum))+' '
		ThisNum.replace('e','E',1)

		f.write(ThisNum)
		Count+=1
		if Count==3:
			f.write('\n')
			Count=0
	f.close()
print('    Direcciones restrictas en nuevo archivo '+NewName)
		






