#!/usr/bin/env python3

# This script reads POSCAR/CONTCAR type files and computes center of mass and inertia moments.
# It allows selecting a subset of atoms

# v2.0 - 4/may/2023 - SAGG (sebagodoy.at.udec.cl)

# packages
import numpy as np

# Data
AtomMases = {
    'H':1.0079,'He':4.0026,
    'Li':6.941,'Be':9.0122,'B':10.811,'C':12.0107,'N':14.0067,'O':15.9994,'F':18.9984,'Ne':20.1797,
    'Na':22.9897,'Mg':24.305,'Al':26.9815,'Si':28.0855,'P':30.9738,
    'S':32.065,'Cl':35.453,'K':39.0983,'Ar':39.948,
    'Ca':40.078,'Sc':44.9559,'Ti':47.867,'V':50.9415,'Cr':51.9961,
    'Mn':54.938,'Fe':55.845,'Ni':58.6934,'Co':58.9332,
    'Cu':63.546,'Zn':65.39,'Ga':69.723,'Ge':72.64,'As':74.9216,'Se':78.96,
    'Br':79.904,'Kr':83.8, 'Rb':85.4678,'Sr':87.62, 'Y':88.9059,'Zr':91.224,'Nb':92.9064,
    'Mo':95.94,'Tc':98,'Ru':101.07,'Rh':102.9055,'Pd':106.42,'Ag':107.8682,'Cd':112.411,
    'In':114.818,'Sn':118.71,'Sb':121.76,'I':126.9045,'Te':127.6,'Xe':131.293,'Cs':132.9055,
    'Ba':137.327,'La':138.9055,'Ce':140.116,'Pr':140.9077,'Nd':144.24,'Pm':145,'Sm':150.36,
    'Eu':151.964,'Gd':157.25,'Tb':158.9253,'Dy':162.5,'Ho':164.9303,'Er':167.259,'Tm':168.9342,
    'Yb':173.04,'Lu':174.967,'Hf':178.49,'Ta':180.9479,'W':183.84,'Re':186.207,'Os':190.23,
    'Ir':192.217,'Pt':195.078,'Au':196.9665,'Hg':200.59,'Tl':204.3833,'Pb':207.2,'Bi':208.9804,
    'Po':209,'At':210,'Rn':222,'Fr':223,'Ra':226,'Ac':227,'Pa':231.0359,'Th':232.0381,'Np':237,
    'U':238.0289,'Am':243,'Pu':244,'Cm':247,'Bk':247,'Cf':251,'Es':252,'Fm':257,'Md':258,
    'No':259,'Rf':261,'Lr':262,'Db':262,'Bh':264,'Sg':266,'Mt':268,'Rg':272,'Hs':277
}

# Custom functions
def Report(istr, end='\n', start=' '*4+'> '):
    print(start+str(istr), end=end)
def FixNum(iNum, **kwargs):
    myformat = "{:"+str(kwargs.get('tot',12))+"."+str(kwargs.get('dec',4))+"f}"
    return myformat.format(iNum)
def FixNumE(iNum, **kwargs):
    myformat = "{:"+str(kwargs.get('tot',12))+"."+str(kwargs.get('dec',4))+"e}"
    return myformat.format(iNum)


# Open file
filedir = input('  > File (def=./CONTCAR) : ') or './CONTCAR'
with open(filedir, 'r') as f:
    content = f.readlines()

# Get box
latfactor = float(content[1])  # lattice factor
cellbox = [[float(j)*latfactor for j in content[i].split()] for i in range(2,5)]
# print("Cell box :"); [print(i) for i in cellbox] # debug print

# Get atom types
try:
    atomtype_names = content[5].split()
    atomtype_numbers = [int(i) for i in content[6].split()]
    if not len(atomtype_names) == len(atomtype_numbers):
        raise ValueError
    natoms = sum(atomtype_numbers)
    Report('Detected '+str(natoms)+' atoms including : '+', '.join(atomtype_names))
except ValueError:
    quit("File must contain line with atom names in line 6 and amount per type in line 7.")

# Check format
if not len(content[8].split()) == 1:
    quit('Check the file format, atom coordinates are expected start in line 10, (line 8: Selective dynamics '
         '\r\nand line 9:Direct or Cartesian or C, c, K, c')

# Get coords n mass, check Selective dynamics
AtomData = [] # format: [x, y, z, 'atom name', atom mass (float)]
atomcounter = 0
for i, k in zip(atomtype_names, atomtype_numbers):
    for iatom in range(k):
        AtomData.append([float(coor) for coor in content[9 + atomcounter].split()[:3]]+[i] + [AtomMases[i]])
        atomcounter += 1

# Select subset
subset = input('  > Select subset of atoms (e.g. 3,5,6-9,13) or use all (def.) :')
if not subset:
    Report('Using all atoms')
    Atoms = [i for i in AtomData]
else:
    Atoms = []
    for k in subset.split(','):
        if '-' in k:
            for j in range(int(k.split('-')[0]) -1 , int(k.split('-')[1])):
                Atoms.append(AtomData[j])
        else:
            Atoms.append(AtomData[int(k)-1])
    Report('Chosen a subset of the available atoms.')

# Ask about mases
# TODO: add modify masses option
ThisMases = {}
for i in Atoms:
    ThisMases[i[3]]=i[4]
Report('Selection includes : '+', '.join(list(ThisMases.keys())))


# --------------------------------------------------------------------------------
# Compute mass center
TotalMass = sum([i[4] for i in Atoms])
MassCenter = [sum([i[j]*i[4]/TotalMass for i in Atoms]) for j in range(3)]

if content[8][:-1].rstrip() in 'Direct':
    MassCenterDirect = MassCenter
    # transform to cartesian coordinates
    MassCenterCart = [sum([cellbox[i][j] * MassCenter[i] for i in range(3)]) for j in range(3)]

else:
    MassCenterCart = MassCenter
    # -- Transform cartesian to cell coordinate system
    New2OldBasis = np.array([[i, j, k] for i, j, k in zip(cellbox[0], cellbox[1], cellbox[2])])
    New2OldBasis = np.linalg.inv(New2OldBasis)
    MassCenterDirect = [sum([New2OldBasis[j][i] * MassCenterCart[i] for i in range(len(MassCenterCart))]) for j in range(len(MassCenterCart))]

Report('Total mass of the selected subset is : '+FixNum(TotalMass))
Report('Mass center is : [' +
       ' , '.join([FixNum(i, tot=8) for i in MassCenterCart]) +
       '] ( Cartesian )', start = ' '*6)
Report('                 [' +
       ' , '.join([FixNum(i, tot=8) for i in MassCenterDirect]) +
       '] ( Direct )', start = ' '*6)
# ----------------------------------------------------------------------------------------------------------------------
# Correct direct coordinates to cartessian
if content[8][:-1].rstrip() in 'Direct':
    Report('Scaling direct coordinates to cartesian for the atoms considered')
    # scalate coordinates to the box
    for iatom in Atoms:
        iatom[:3] = [ sum([cellbox[i][j]*iatom[i] for i in range(3)]) for j in range(3)]

# Correct coordinates to mass center
for iatom in Atoms:
    iatom[0:3] = [iatom[j]-MassCenterCart[j] for j in range(3)]

# Inertia tensor
Itens = [[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]]
for iatom in Atoms:
    mag2 = sum([i**2 for i in iatom[:3]])
    for i in range(3):
        for j in range(3):
            Itens[i][j] -= iatom[i]*iatom[j]*iatom[4]
        Itens[i][i] += mag2*iatom[4]

Report('Inertia tensor : ')
for i in Itens:
    print(' '*16, end='')
    for j in i:
        print(FixNum(j), end=' , ')
    print()

# Ineria moments around principal axis
ITensArray = np.array(Itens)
w, v = np.linalg.eig(ITensArray)
Report('Inertia moments and principal rotation axis : ')
for i, j in zip(w,v):
    print(' '*16, end='')
    print('['+' , '.join([FixNum(k, tot=8) for k in j])+']', end=' -> ')
    print(FixNum(i, tot=8) + ' (g/mol)*A2')

# Rotational temperatures
#### Constants
kb			= 1.3806488E-23		# Boltzmann's constant [m2 kg / s2 K]
hh			= 6.62606957E-34	# Plack's constant [m2 kG/s]
Nav			= 6.02214129E23		# Avogadro's Number [particles/mol]

Report('Inertia moments (I) and rotational temperatures')
print('                I : (g/mol)*A2    kg*m2       ;    rot. temp  [K] ')
for i in w:
    iunits = i/(1000*Nav*1e20)
    rotT = (hh**2)/(8*(np.pi**2)*iunits*kb)
    print(' '*20 + FixNum(i, tot=8) + ' '*4 + FixNumE(iunits, tot=8) + ' '*10+ FixNum(rotT, tot=8))
