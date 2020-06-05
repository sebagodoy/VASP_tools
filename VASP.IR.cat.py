#!/usr/bin/env python3


print('    Agrega varios perfiles IR a una única serie  ')


# -------------------------------------------------------------------------------------------------
# Tools
# -------------------------------------------------------------------------------------------------
def print2file(fileObj, string):
	print(string)
	fileObj.write(string)

import os.path

# -------------------------------------------------------------------------------------------------
# Preparacion
# -------------------------------------------------------------------------------------------------
print("        > Iniciando archivo IR.log.cat")
Log = open('IR.log.cat', 'w')
Log.write(' Agrega varios perfiles IR a una única serie  \n')


# -------------------------------------------------------------------------------------------------
# Get data
# -------------------------------------------------------------------------------------------------

#Consistencia entre IR.log's
LockFreqIn=0.; LockFreqSec=0.; LockFreqFin=0.; MaxMainInt=0.

AddNew = True; LockSerial=False; InicialMainSerial = True; SerialCatalog=[]; ID=0
while AddNew == True:
	#------------------------------------------------------------------------------------------
	# Ubica archivo
	#------------------------------------------------------------------------------------------

	print("        -----------------------------------------------------------------------")
	Log.write(" -----------------------------------------------------------------------\n")

	ThisFile = "IR.log_"+input("        > Añadir IR.log_")
	ThisName = input("          > Identidad : ")

	if ThisName == "":
		ThisName = ID; ID+=1

	if os.path.isfile(ThisFile) == False:
		print("            Archivo no hallado, probemos de nuevo ..."); continue
	else: 
		print("          > Archivo hallado, abriendo", end=" ... ")

	#------------------------------------------------------------------------------------------
	# Get data
	#------------------------------------------------------------------------------------------
	tmpFreqBands=[]; tmpIntBands=[]; tmpLorBands=[]; tmpFreqSerial=[]; tmpIntSerial=[]
	tmpfreqIn=0.; tmpfreqSec=0.; tmpfreqFin=0.

	# Open file
	with open(ThisFile, 'r') as f:
		content=f.readlines()
		f.close()
	print("Ok")
	Log.write(" Añade "+ThisName+" desde "+ThisFile+'\n\n')

	# Agrega bandas de frecuencias
	print("          > Ingresando bandas de frecuencia", end=" ... ")
	iLine=2
	while iLine <= len(content) and 'cm⁻1' in content[iLine]:
		tmpFreqBands.append(float(content[iLine].split()[1]))
		tmpIntBands.append(float(content[iLine].split()[3]))
		tmpLorBands.append(float(content[iLine].split()[4]))
		iLine+=1
	print("Ok")

	# Reportando a Log
	print("          > Añadiendo a IR.log.cat", end=" ... ")
	Log.write("  #    Frecuencia       Intensidad    Lorentz Peak\n")
	for i in range(len(tmpFreqBands)):
		tmpLog="  "+str(i)
		while len(tmpLog)<7: tmpLog+=" "
		tmpLog+=str(tmpFreqBands[i])
		while len(tmpLog)<16: tmpLog+=" "
		tmpLog+="cm⁻1    "+str("{:.4E}".format(tmpIntBands[i]))+"    "+str("{:.8E}".format(tmpLorBands[i]))+"\n"
		Log.write(tmpLog)
	print("Ok")

				
	# Agrega serie de frecuencias
	print("          > Ingresando distribución de lawrents", end=" ... ")
	while not "Serie de absorbancia" in content[iLine]:
		iLine+=1
	iLine+=1
	while iLine < len(content):
		tmpFreqSerial.append(float(content[iLine].split()[0]))
		tmpIntSerial.append(float(content[iLine].split()[1]))
		iLine+=1
	print("Ok")

	# Lock rango serial
	tmpAcepta = True
	if LockSerial == False:
		print("          > Definiendo limites de serie aceptables")
		LockFreqIn=tmpFreqSerial[0]
		LockFreqSec=tmpFreqSerial[1]
		LockFreqFin=tmpFreqSerial[len(tmpFreqSerial)-1]
		LockSerial = True
	# Check concordancia con series anteriores
	else:
		print("          > Evaluando aceptación de serie", end=" ... ")
		if not LockFreqIn == tmpFreqSerial[0]: tmpAcepta = False
		if not LockFreqSec == tmpFreqSerial[1]: tmpAcepta = False
		if not LockFreqFin == tmpFreqSerial[len(tmpFreqSerial)-1]: tmpAcepta = False
		if tmpAcepta == False:
			print("Límites o paso de serial no coinciden. Revisar archivos!")
			continue
		else:
			print("Ok")

	# Prepara Main Serial
	if InicialMainSerial == True:
		print("          > Iniciando serie global", end=" ... ")
		MainSerial=[[],[]]
		for iFreq in tmpFreqSerial:
			MainSerial[0].append(iFreq)
			MainSerial[1].append(0.)
		InicialMainSerial = False
		print("Ok")
	
	# Añade sere a MainSerial
	print("          > Añadiendo a serie global", end=" ... ")
	for i in range(len(tmpIntSerial)):
		MainSerial[1][i]+=tmpIntSerial[i]
	print("Ok")

	# Añade a catálogo de series
	#    SerialCatalog[file N][X]
	#    X=0 : ID
	#    X=1 : freq bands
	#    X=2 : intensity bands
	#    X=3 : lorentz Int bands
	#    X=4 : intensity serial
	print("          > Añadiendo a catálogo", end="...")
	SerialCatalog.append([ThisName, tmpFreqBands, tmpIntBands, tmpLorBands, tmpIntSerial])
	print("Ok")

	#------------------------------------------------------------------------------------------
	# Añadir siguiente
	#------------------------------------------------------------------------------------------
	print("        -----------------------------------------------------------------------")
	if input("        > Seguir añadiendo? (def=y/n) ") == "n": AddNew = False


# -------------------------------------------------------------------------------------------------
# Traspasa Main Serial a Log
# -------------------------------------------------------------------------------------------------
Log.write(" -----------------------------------------------------------------------\n Serial compilado\n")
Log.write("  Frecuencia cm⁻1  Intensidad lorentz compilada\n")
for i in range(len(MainSerial[0])):
	tmpMainSerial="  "+str(MainSerial[0][i])
	while len(tmpMainSerial)<19:tmpMainSerial+=" "
	tmpMainSerial+=str("{:.10E}".format(MainSerial[1][i]))
	Log.write(tmpMainSerial+"\n")


# -------------------------------------------------------------------------------------------------
# Generando gráfico
# -------------------------------------------------------------------------------------------------
print("        -----------------------------------------------------------------------")
# General Plot
print("        > Iniciando gráfico\n          > Indentificando intensidad compilada máxima ... ", end="")
import matplotlib.pyplot as plt
ColorSerial=['red', 'indigo', 'lawngreen', 'aqua', 'deeppink', 'forestgreen','orangered', 'blue', 'yellow', 'brown', 'crimson', 'midnightblue', 'gray', 'lightgreen', 'darkgreen', 'darkslategray', 'springgreen', 'darkviolet', 'tan', 'chocolate', 'khaki', 'seagreen', 'slategray', 'mediummorchid', 'goldenrod', 'paleturquoise']
fig = plt.figure(figsize=(9.6, 4.8), dpi=100)

# Identifica máximo de Main Serial
for iIntMainSerial in MainSerial[1]:
	if iIntMainSerial > MaxMainInt: MaxMainInt = iIntMainSerial
print("Ok\n          > Añadiendo curva compilada", end=" ... ")

# Graficando Main Serial
plt.plot(MainSerial[0], MainSerial[1], 'k', linewidth=0.5)
print("end")

# Graficando bandas
print("          > Añadiendo bandas individuales")
for Item in range(len(SerialCatalog)):
	# Debug Serie
	#print('-----------------'+SerialCatalog[Item][0]+'-----------------')
	for iFreq in range(len(SerialCatalog[Item][1])):
		# Debug Freqs en serie
		#print(SerialCatalog[Item][1][iFreq])
		# Top Bands
		plt.plot( [SerialCatalog[Item][1][iFreq] , SerialCatalog[Item][1][iFreq]] , [MaxMainInt*(0.9/0.85),MaxMainInt*(0.95/0.85)], Color=ColorSerial[Item], linewidth=1.5)
		# Bottom curve
		plt.plot( [SerialCatalog[Item][1][iFreq] , SerialCatalog[Item][1][iFreq]] , [0.,SerialCatalog[Item][3][iFreq]], Color=ColorSerial[Item] , linewidth=1.2)

# Añadiendo nombres
print("          > Añadiendo nombres")
Item=0;	tmpX0=0.13; tmpX=tmpX0; dX=0.1; tmpY=0.033; MaxNames=7
while Item in range(len(SerialCatalog)):
	if tmpX > (tmpX0+MaxNames*dX):
		tmpX-=(MaxNames+1)*dX; tmpY-=0.045

	plt.gcf().text(tmpX, tmpY, SerialCatalog[Item][0], fontsize=7, backgroundcolor=ColorSerial[Item])
	tmpX+=dX
	Item+=1


# Graficando subcurvas
	
	
# Maquillaje final
plt.gca().invert_xaxis()
#plt.gca().get_yaxis().set_visible(False)
plt.gca().get_yaxis().set_ticks([])
if not input("          > Transmitancia / Absorbancia? (def=T/A) : ") == "A" :
	plt.gca().invert_yaxis()
	plt.ylabel("Transmitancia relativa")
else:
	plt.ylabel("Absorbancia relativa")
plt.gca().set_xlabel(r'$cm^{-1}$', fontsize=11.5)
plt.gca().xaxis.set_label_coords(1.012, -0.016)

# Guardando imágenes
plt.savefig('IR.cat.png', dpi=fig.dpi, bbox_inches='tight', pad_inches=0.5)
print("          > Gráfico guardado en IR.cat.png\n        > Mostrando gráfico", end=" ... ")
plt.show()
print("Ok")



# -------------------------------------------------------------------------------------------------
# File management - Inicia
# -------------------------------------------------------------------------------------------------
print("        > Finalizando IR.log.cat")
Log.close()

