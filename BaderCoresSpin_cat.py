#!/usr/bin/env python3

# V.1.0 3/jun/2022 -SAGG

print("This python tool just recovers the atomic charges in an tot_ACF.dat and the\n"
      "atomic magnetization in a mag_ACF.dat file, both created from AECCAR* and CHGCAR\n"
      "from an spin polarized calculation, in a single file easy to read and copy paste.\n")

class baderpartition:
      def __init__(self, ifile):
            with open(ifile, 'r') as f:
                  self.text = f.readlines()
                  self.natoms = len(self.text)- 6
                  self.total = float(self.text[-1].split()[-1])
                  self.vac_total = float(self.text[-3].split()[-1])
                  self.vac_vol = float(self.text[-2].split()[-1])
                  # Separa cosas útiles
                  self.chargemag = [float(i.split()[4]) for i in self.text[2:-4]]
                  self.X = []
                  self.Y = []
                  self.Z = []
                  self.MinDist = []
                  self.AtomicVol = []
                  for iLine in self.text[2:-4]:
                        self.X.append(float(iLine.split()[1]))
                        self.Y.append(float(iLine.split()[2]))
                        self.Z.append(float(iLine.split()[3]))
                        self.MinDist.append(float(iLine.split()[5]))
                        self.AtomicVol.append(float(iLine.split()[6]))

def FixNum(entrada, ancho=12, format=True):
      if format:
            try:
                  entrada = "{:.6f}".format(entrada)
            except:
                  pass
      entrada = str(entrada)
      while len(entrada)<ancho:
            entrada = " " + entrada
      return entrada

# ----------------------------------------------------------------------------------
total = baderpartition("./tot_ACF.dat")
mag = baderpartition("./mag_ACF.dat")

if not (total.X == mag.X and total.Y == mag.Y and total.Z == mag.Z and total.MinDist == mag.MinDist and total.AtomicVol == mag.AtomicVol):
      quit("Files do not match. Check manually or regenerate carefully")

with open('Bader_Analysis_cat.dat','w') as f:
      f.write("    #           X           Y           Z    "
              "MIN DIST  ATOMIC VOL      CHARGE     MAGNET.    #\n")
      f.write(" "+"-"*93+"\n")
      for i, j in enumerate(total.X):
            f.write(FixNum(i+1, 5, format=False))
            f.write(FixNum(total.X[i]))
            f.write(FixNum(total.Y[i]))
            f.write(FixNum(total.Z[i]))
            f.write(FixNum(total.MinDist[i]))
            f.write(FixNum(total.AtomicVol[i]))
            # ---
            f.write(FixNum(total.chargemag[i]))
            f.write(FixNum(mag.chargemag[i]))
            # ----
            f.write(FixNum(i+1, 5, format=False))
            f.write("\n")
      f.write(" " + "-" * 93 + "\n")
      f.write(" " * 4 + " Charge density partition, vacuum: volume = " + FixNum(total.vac_vol, 10)
              +', total charge       = '+FixNum(total.vac_total, 10)+"\n")
      f.write(" " * 4 + " Spin density partition,   vacuum: volume = " + FixNum(mag.vac_vol, 10)
              +', total magetization = '+FixNum(mag.vac_total,10)+"\n")
      f.write(" " * 4 + " Number of electrons : " + str(total.total))
      f.write(" " * 4 + " Total magnetization : " + str(mag.total))


