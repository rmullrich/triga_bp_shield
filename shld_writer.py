'''
This code will write mcnp input files for shields of different materials while varying lengths

User desired parameters can be altered near the bottom of the code.
'''

import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os

#create output folder
#try:
#os.mkdir('output')
#except OSError,e:
#    print e

#numbering
#  0 Void
#  1 Air      2 Borated Polyethylene
#  3 Aluminum 4 Lead
#  5 Tungsten 6 Cadmium
#  n neutron  p photon

density = [0.0, 0.001293, 1.000, 2.699, 11.34, 19.3, 8.65, 7.874]
label = ['VOID', 'Air', 'Borated Polyethylene', 'Aluminum', 'Lead', 'Tungsten', 'Cadmium', 'Iron']
abrev = ['VOID', 'air', 'bp', 'al', 'pb', 'w', 'cd', 'fe']

def Block1(blocks):
    '''
    This function creates the cell cards for the shielding problem
    The only parameters that this program changes are for cell 21, where the material
    and the material density are changed.
    
    Inputs:
        material: the material number corresponding to the material cards in block 3
        density: the density of that material
        label: the english name of that material
    
    Output:
        H: the string containing the text for the cell cards
    '''    
    H = ''
    H += 'c  *********************************************************\n'
    H += 'c                           BLOCK 1\n'
    H += 'c  *********************************************************\n'
    H += '11 1 -0.001239  11 -12     -21            $ NEBP Cavity\n'
    H += '12 2 -1.0       11 -12  21 -22            $ Borated Poly Collimator\n'
    H += '13 3 -2.699     11 -12  22 -23            $ NEBP Aluminum Case\n'
    H += 'c \n'
    for i, mat in enumerate(blocks):
        H += '{} {} -{} 120 -121 122 -123 {} -{}  $ Brick of {}\n'.format(200 + i, mat, density[mat], 12 if i == 0 else 130 + i, 131 + i, abrev[mat])
    H += 'c \n'
    H += '31 1 -0.001239  41 -32     -21        $ Detector Cell\n'
    H += 'c Define Problem space cell\n'
    H += '90 1 -0.001239 -32 #11 #12 #13 (-12:-120:121:-122:123:{}) #31\n'.format(130 + len(blocks))
    H += '99 0            32                        $ Graveyard (RIP IN PEACE)\n'
    H += '\n'
    return H

def Block2(blocks, width):
    H = ''
    H += 'c  *********************************************************\n'
    H += 'c                           BLOCK 2\n'
    H += 'c  *********************************************************\n'
    H += 'c  _____Problem Planes\n'
    H += '11  PX  -36.015          $ Collimator Front Plane\n'
    H += '12  PX   0               $ Collimator Back Plane\n'
    H += 'c  _____Cylinders\n'
    H += '21  CX   1.27            $ Cavity Cylinder\n'
    H += '22  CX   7.62            $ Borated Poly Cylinder\n'
    H += '23  CX   8.255           $ Aluminum Case Cylinder\n'
    H += 'c  _____Rectangular Parallelepiped\n'
    H += '120 PZ -10\n'
    H += '121 PZ 10\n'
    H += '122 PY -10\n'
    H += '123 PY 10\n'
    for i, mat in enumerate(blocks):
        H += '{} PX {} $ Brick of {}\n'.format(131 + i, width + i+.0001, abrev[mat]) 
    H += '32  RPP    -40 101             -11   11      -11  11    $ Problem Space\n'
    H += 'c  _____Detector Planes\n'
    H += '41 PX {}\n'.format(len(blocks)*width + .0002)
    H += '\n'
    return H

def Block3(particle, blocks):
    nps = 100000
    H = ''
    H += 'c  *********************************************************\n'
    H += 'c                           BLOCK 3\n'
    H += 'c  *********************************************************\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c                   PROBLEM SPECIFICATIONS\n'
    H += 'c  ---------------------------------------------------------\n'
    if particle == 'n': H += 'MODE n p\n'
    if particle == 'p': H += 'MODE p\n'
    H += 'NPS {}\n'.format(nps)
    H += 'PRINT 110\n'
    #H += 'phys:p J J J 1 \n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c                        IMPORTANCES\n'
    H += 'c  ---------------------------------------------------------\n'
    if particle == 'n': 
        H += 'IMP:n 1 {}r 0\n'.format(4 + len(blocks))
    H += 'IMP:p 1 {}r 0\n'.format(4 + len(blocks))
    H += 'c  ---------------------------------------------------------\n'
    H += 'c                      MATERIAL CARDS\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c \n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c  MATERIAL 1:      AIR  \n'
    H += 'c  ------------------------(density 0.001293 g/cm^3)--------\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'M1    7014 -0.7558\n'
    H += '      8016 -0.2314\n'
    H += '     18040 -0.0128\n'
    H += 'c \n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c  MATERIAL 2:      BORATED POLYETHYLENE\n'
    H += 'c  ---------------------------(density 1.000 g/cm^3)--------\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'M2     1001     -0.125355\n'
    H += '       5010.70c -0.100000\n'
    H += '       6000     -0.774645\n'
    H += 'c \n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c  MATERIAL 3:      ALUMINUM \n'
    H += 'c  ---------------------------(density 2.699 g/cm^3)--------\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'M3    13027.70c -1.0\n'
    H += 'c \n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c  MATERIAL 4:      LEAD  \n'
    H += 'c  ---------------------------(density 11.34 g/cm^3)--------\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'M4   82207.70c   -1.0\n'
    H += 'c \n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c  MATERIAL 5:      TUNGSTEN   \n'
    H += 'c  ---------------------------(density 19.3 g/cm^3)---------\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'M5   074184   -1.0\n'
    H += 'c \n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c  MATERIAL 6:      CADMIUM\n'
    H += 'c  ---------------------------(density 8.65 g/cm^3)---------\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'M6   048112   -1.0\n'
    H += 'c \n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'c  MATERIAL 7:      Iron\n'
    H += 'c  ---------------------------(density 7.874 g/cm^3)---------\n'
    H += 'c  ---------------------------------------------------------\n'
    H += 'M7   026000   -1.0\n'
    H += 'c \n'
    return H

def Source(particle):
    H = ''
    if particle == 'n':
        H = open('nsource.txt', 'r').read()
    if particle == 'p':
        H = open('psource.txt', 'r').read()
    return H

def Tally(particle):
    H = ''
    H += 'c  ---------------------------------------------------------\n'
    H += 'c                       TALLY CARDS\n'
    H += 'c  ---------------------------------------------------------\n'
    if particle == 'n':
        H += 'F11:n 41\n'
        H += 'FS11  21\n'
        H += 'E11   0.0 0.5 20\n'
    H += 'F21:p 41\n'
    H += 'FS21  21\n'
    H += 'E21   0.0 0.1 20\n'
    H += '\n'
    return H

def remove(fname):
    print fname
    names = ['output/{}'.format(fname), 'output/{}o'.format(fname), 'output/{}r'.format(fname)]
    for name in names:
        try:
            os.remove(name)
        except OSError:
            pass
        
def readGamma(filename):
    f = open(filename).readlines()
    for i, line in enumerate(f):
        if '1tally       21' in line:
            nFastG = float(f[i+17].split()[1])
            totalGamma = float(f[i+18].split()[1])
    return nFastG, totalGamma

def readNeutron(filename):
    f = open(filename).readlines()
    
    for i, line in enumerate(f):
        if '1tally       11' in line:
            nFastN = float(f[i+17].split()[1])
            totalNeutrons = float(f[i+18].split()[1])
        if '1tally       21' in line:
            nFastG = float(f[i+17].split()[1])
            totalGamma = float(f[i+18].split()[1])
    return nFastN, totalNeutrons, nFastG, totalGamma
    
    

def name(blocks):
    s = ''
    for b in blocks:
        s += '{}'.format(b)
    return s

def dec2hex(num):
    if num == 0:
        return 0
    ans = ""
    while num > 0:
        ans = str(num%7) + ans
        num /= 7
    return int(ans)
    
def makeList(num):
    n = dec2hex(num)
    L = [0] * (10 - len(str(n)))
    L += [int(d) for d in str(n)]
    return [l + 1 for l in L]
   
def run(blocks, width):
    for par in ['n', 'p']:
        #the next line will title the mcnp input file
        s = 'TRIGA BEAMPORT {} Shield, Thickness {}\n'.format(name(blocks), len(blocks))
        #calls the Block1 function to produce cell cards for input file            
        s += Block1(blocks)
        #write surface cards            
        s += Block2(blocks, width)
        #write information in Block 3            
        s += Block3(par, blocks)
        s += Source(par)
        s += Tally(par)
        #give the file a name
        fname = 'mat{}{}.i'.format(name(blocks), par) 
        # Remove any files already present with the same name
        remove(fname)
        #create file in output folder and write to file
        with open('output/{}'.format(fname), 'w') as H:
            H.write(s)
        subprocess.call('mcnp6 name=output/{}'.format(fname), shell=True)
        
        if par == 'p':
            fastG, totG = readGamma('output/{}o'.format(fname))
        else:
            fastN, totN, fastG2, totG2 = readNeutron('output/{}o'.format(fname))
            
        # Remove any files already present with the same name
        remove(fname)
    return fastN, totN, fastG+fastG2, totG+totG2

#here you'll input all of the parameter you want to create the input files you need
#particle types
task = os.environ['SGE_TASK_ID']
task = int(task) - 1

allBlocks = [makeList(task)]
            # 2244222445
width = 2.0
#this will loop through the above lists to create the desired mcnp input files
for blocks in allBlocks:
    output = run(blocks, width)
    with open('output/{}'.format(name(blocks)), 'w') as f:
        f.write('{} {} {} {}'.format(*output))
         
        
        
        
        
