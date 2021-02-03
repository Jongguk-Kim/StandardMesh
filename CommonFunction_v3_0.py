import matplotlib as mpl
mpl.use('Agg')
import math, time
import os, glob, sys, json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
# from matplotlib.cm import cm
from matplotlib.patches import PathPatch
from mpl_toolkits.axes_grid1 import make_axes_locatable
import _islm
import multiprocessing as mp
from multiprocessing import Pool

TireRubberComponents = [
    # 'BEAD_R', 'BEAD_L', # 'BD1' ,  Bead
    'BD1', 
    'BEAD_R', 'BEAD_L', 
    'BEC' , # Belt Edge Cushion
    'BSW' , # Black SideWall Component
    'BTT' , # Belt rubber component (associated with BT components)
    'CCT' , # Carcass rubber component (associated with C components)
    'SCT' , 
    'NCT' ,
    'CHS' ,
    'CTB' , 'CTR', 'CTB1' , 'CTR1',# Tread Componet
    'ET'  , # Edge Tape
    'FIL' , 'BDF', # Bead Filler
    'HUS' , # Hump Strip
    'JBT' , # Rubber associated with JFC, JEC components
    'L11' , 'IL1', # Inner liner component
    'L12' , 'IL2', # #2 Innerliner
    'LBF' , # Lower Bead Filler
    'UBF' , # Upper Bead Filler
    'RIC' , # Rim Cushion
    'SIR' , # Sidewall Insert Rubber
    'SHW' , # Shoulder Wedge
    'SRTT', # Associated with PK1, PK2, RFM and FLI components
    'SUT' , 'UTR', 'SUT1' , 'UTR1',# SubTread
    'TRW' , # Tread Wing
    
    'WSW'  # While Sidewall
]
TireTreadComponents = [
    'CTB' , 'CTR',
    'SUT' , 'UTR',
    'TRW'
]
TireCordComponents = [
    'C01'  , 'CC1', # Carcass Cord 1 
    'C02'  , 'CC2', # Carcass Cord 2
    'C03'  , 'CC3', # Carcass Cord 3 
    'C04'  , 'CC4', # Carcass Cord 4
    'BT1'  , # Belt 1 
    'BT2'  , # Belt 2
    'BT3'  , # Belt 3
    'BT4'  , # Belt 4
    'JFC1' , 'JFC', # Jointless Full Cap 1
    'JFC2' , # Jointless Full Cap 2
    'JEC1' , 'JEC', # Jointless Edge Cap 1
    'OJEC1', # Overlapped Jointless Edge Cap
    'OJFC1', # Overlapped Jointless Full Cap
    'PK1'  , # Half Bead Packing
    'PK2'  , # Full Bead Packing
    'RFM'  , # Bead S(RFM)
    'FLI'  , # Bead Flipper
    'CH1'  , 'CH1_R', 'CH1_L',  # Steel Chafer 
    'CH2'  , 'CH2_R', 'CH2_L',  # 1st Nylon Chafer
    'CH3'  , 'CH3_R', 'CH3_L',  # 2nd Nylon Chafer
    'NCF'  , 'SCF'  , 'NF1'  , 'NF2',
    'BDC'  , # bead cover 
    'SPC'    ## spiral coil
    #'SWS'    # temporary component for Endurance simulation 
]

def GET_TIRE_COMPONENT(): 
    return TireRubberComponents, TireCordComponents

class RIMFORCE:
    def __init__(self, rpt_file):
        self.FX = 0.0
        self.FY = 0.0
        self.FZ = 0.0
        self.MX = 0.0
        self.MY = 0.0
        self.MZ = 0.0

        self.GetForce(rpt_file)

    def GetForce(self, rpt_file):
        with open(rpt_file) as IN:
            lines = IN.readlines()

        for line in lines:
            if 'FX_AVE' in line:
                data = list(line.split(':'))
                self.FX = float(data[1].strip())
            if 'FY_AVE' in line:
                data = list(line.split(':'))
                self.FY = float(data[1].strip())
            if 'FZ_AVE' in line:
                data = list(line.split(':'))
                self.FZ = float(data[1].strip())
            if 'MX_AVE' in line:
                data = list(line.split(':'))
                self.MX = float(data[1].strip())
            if 'MY_AVE' in line:
                data = list(line.split(':'))
                self.MY = float(data[1].strip())
            if 'MZ_AVE' in line:
                data = list(line.split(':'))
                self.MZ = float(data[1].strip())

    def Help(self):
        print ('class RIMFORCE(rpt_file)')
        print ('- self.FX / FY / FZ / MX / MY / MZ')
        print (' From : /REPORT/*.rpt')

class SIMTIME:
    def __init__(self, SMART_INP):
        self.SimulationTime = 0.0
        self.DelTime = 0.0001
        self.LastStep = 0
        self.AveragingTime = 0.001

        self.GetTime(SMART_INP)

    def GetTime(self, inpFile):
        with open(inpFile) as IN:
            lines = IN.readlines()

        for line in lines:
            if 'SIMULATION_TIME' in line:
                word = list(line.split('='))
                data = list(word[1].split(','))
                self.SimulationTime = float(data[0].strip())

            if 'OUTPUT_CONTROL' in line:
                word = list(line.split('='))
                data = list(word[1].split(','))
                self.DelTime = float(data[0].strip())
                AvgTime = list(data[1].split('('))
                self.AveragingTime = float(AvgTime[0].strip())
        PCI_Time = 0.06
        if self.SimulationTime == 0.0:
            self.LastStep = int(PCI_Time / self.DelTime)
        else:
            self.LastStep = int(self.SimulationTime / self.DelTime)

    def Help(self):
        print ('class SIMTIME(SMART_Inp_File)')
        print ('- self.SimulationTime / DelTime / LastStep / AveragingTime')

class CONDITION:
    def __init__(self, SMART_INP):
        self.Pressure = 0.0
        self.Load = 0.0
        self.Speed = 0.0
        self.Camber = 0.0
        self.LateralID = 0
        self.LateralValue = 0.0
        self.SlipAngle = 0.0
        self.TractionID = 0
        self.TractionValue = 0.0
        self.FreeSpin = 0.0
        self.Road = 0.0
        self.Drum = 0.0
        self.RimWidth = 0.0
        self.RimDiameter = 0.0

        self.GetConditions(SMART_INP)

    def GetConditions(self, SMART_INP):
        with open(SMART_INP) as IN:
            lines = IN.readlines()
        for line in lines:
            if 'CONDITION_LOAD' in line:
                word = list(line.split('='))
                data = list(word[1].split(','))
                self.Pressure = float(data[1].strip())
                self.Load = float(data[2].strip())
                self.Speed = float(data[3].strip())

            if 'CAMBER_ANGLE' in line:
                word = list(line.split('='))
                data = list(word[1].split(','))
                self.Camber = float(data[0].strip())

            if 'LATERAL_CONTROL' in line:
                word = list(line.split('='))
                data = list(word[1].split(','))
                self.LateralID = int(data[0].strip())
                self.LateralValue = float(data[1].strip())
                self.SlipAngle = float(data[1].strip())

            if 'ROTATION_CONTROL' in line:
                word = list(line.split('='))
                data = list(word[1].split(','))
                self.TractionID = int(data[0].strip())
                self.TractionValue = float(data[1].strip())

            if 'INFLATION_TIME' in line:
                word = list(line.split('='))
                Wd = list(word[1].split(','))
                data = list(Wd[2].split('('))
                # print 'free spin', data
                self.FreeSpin = float(data[0].strip())

            if 'ROAD_GEOM' in line:
                word = list(line.split('='))
                Wd = list(word[1].split(','))
                data = list(Wd[0].split('('))
                self.Road = float(data[0].strip())
                self.Drum = float(data[0].strip())

            if 'RIM_GEOM' in line:
                word = list(line.split('='))
                data = list(word[1].split(','))
                self.RimDiameter = float(data[0].strip()) * 2.0
                self.RimWidth = float(data[1].strip()) * 2.0

    def Help(self):
        print (" class CONDITION (SMART_Inp_File)")
        print (" self.Pressure/Load/Camber/LateralID/LateralValue/TractionID/TractionValue/FreeSpin")
        print (' self.Road/RimWidth/RimDiameter')

class STATIC:
    def __init__(self, value):
        self.value = value

    def Print(self):
        print (self.value)

class EDGE:
    def __init__(self):
        self.Edge = []

    def Help(self):
        print ("*********************************************************************************")
        print ("EDGE : Node1, Node2, Elset_Name, FacdID, Element_No, D")
        print (" D : -1= Edge, 0 = Free Edge, -2 = not Free Edge, 1= outer edges, Above 1(2~) = Tie No")
        print ("***************************************************************************")
        print ("** Related Function *******************************************************")
        print ("** - self.Add([]) -> Add a component")
        print ("** - self.Print() -> Print all edges on the screen")
        print ("** - self.Save(file_name) -> save all edges in a file")
        print ("** - edge.Image(Node, Image_File_Name, ImageSize(dpi)) -> save a image")
        print ("***************************************************************************")

    def Add(self, edge):
        self.Edge.append(edge)
        
    def Tuple(self):
        I = len(self.Edge)
        J = len(self.Edge[0])
        LST = []
        for i in range(I):
            for j in range(J):
                if j == 3:
                    LST.append(int(self.Node[i][3].split("S")[1]))
                else:
                    LST.append(self.Edge[i][j])
        
        tuplelst = tuple(LST)
        
        return tuplelst, J

    def Nodes(self, **args):
        Node = NODE()
        for key, value in args.items():
            if key == 'Node' or key == 'node':
                Node = value

        I = len(self.Edge)
        NL = []
        
        for i in range(I):
            for j in range(2):
                NL.append(self.Edge[i][j])
        
        i=0
        while i < len(NL):
            j = i+1
            while j < len(NL):
                if NL[i] == NL[j]:
                    del(NL[j])
                    j -= 1
                j+=1
            i+= 1
        
        if len(Node.Node) == 0:
            # print ("# Node IDs in ELSET : Node_ID=[]")
            return NL

        I = len(NL)
        NC = NODE()
        for i in range(I):
            N = Node.NodeByID(NL[i])
            NC.Add(N)
        # print ("# Nodes in ELSET : Node=NODE()")
        return NC
        

    def Image(self, Node, file='EDGE', marker ="", dpi=100):
        MembWidth = 0.5
        color = 'black'

        fig, ax = plt.subplots()
        ax.axis('equal')
        ax.axis('on')
        N = len(self.Edge)
        MinX = 100000.0
        MaxX = -100000.0
        MinY = 100000.0
        MaxY = -100000.0
        for i in range(N):
            N1 = Node.NodeByID(self.Edge[i][0])
            N2 = Node.NodeByID(self.Edge[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            plt.plot([x1, x2], [y1, y2], color, lw=MembWidth, marker=marker)
            if MinX > x1:
                MinX = x1
            if MaxX < x1:
                MaxX = x1
            if MinY > y1:
                MinY = y1
            if MaxY < y1:
                MaxY = y1
            if MinX > x2:
                MinX = x2
            if MaxX < x2:
                MaxX = x2
            if MinY > y2:
                MinY = y2
            if MaxY < y2:
                MaxY = y2
        plt.xlim(MinX - 0.01, MaxX + 0.01)
        plt.ylim(MinY - 0.01, MaxY + 0.01)
        plt.savefig(file, dpi=dpi)
        # print file, 'Image printed'

    def Print(self):
        for edge in self.Edge:
            line = ''
            for item in edge:
                line += str(item) + "    "
            print (line)


    def Save(self, file="EDGE.txt"):
        N = len(self.Edge)
        f = open(file, "w")
        fline = []
        for i in range(N):
            text = str(self.Edge[i]) + '\n'
            fline.append([text])
        f.writelines('%s' % str(item[0]) for item in fline)
        f.close()

    def Delete(self, n):
        del (self.Edge[n])
        
    def Combine(self, iEdge):
        N = len(iEdge.Edge)
        for i in range(N): 
            self.Add(iEdge.Edge[i])
    
    def Sort(self, item=0, reverse=False):
        ## item < 0 sort by connection
        ## item = N sort by Nth number
        if item < 0:
            starts = []
            if reverse == False:
                for i, iedge in enumerate(self.Edge):
                    start = 1
                    for j, jedge in enumerate(self.Edge):
                        if i != j and iedge[0] == jedge[1]:
                            start = 0
                    if start ==1:
                        starts.append(i)

                sortedEdge=EDGE()
                for n in starts:
                    sortedEdge.Add(self.Edge[n])
                    for i, iedge in enumerate(self.Edge):
                        for j, jedge in enumerate(self.Edge):
                            if sortedEdge.Edge[len(sortedEdge.Edge)-1][1] == jedge[0]:
                                sortedEdge.Add(jedge)
                                break
            else:
                for i, iedge in enumerate(self.Edge):
                    start = 1
                    for j, jedge in enumerate(self.Edge):
                        if i != j and iedge[1] == jedge[0]:
                            start = 0
                    if start ==1:
                        starts.append(i)

                sortedEdge=EDGE()
                for n in starts:
                    sortedEdge.Add(self.Edge[n])
                    for i, iedge in enumerate(self.Edge):
                        for j, jedge in enumerate(self.Edge):
                            if sortedEdge.Edge[len(sortedEdge.Edge)-1][0] == jedge [1]:
                                sortedEdge.Add(jedge)
                                break
            for i, edge in enumerate(sortedEdge.Edge):
                self.Edge[i]=edge

        else:
            sortedEdge = EDGE()
            for i, edge in enumerate(self.Edge):
                sortedEdge.Add(edge)
                if i == 0:
                    continue
                else:
                    I = len(sortedEdge.Edge)
                    for j, sedge in enumerate(sortedEdge.Edge):
                        if reverse == True:
                            if sedge[item] < edge[item]:
                                del(sortedEdge.Edge[I-1])
                                sortedEdge.Edge.insert(j, edge)
                                I = j 
                                break
                        else:
                            if sedge[item] > edge[item]:
                                del(sortedEdge.Edge[I-1])
                                sortedEdge.Edge.insert(j, edge)
                                I = j 
                                break


        for i, edge in enumerate(sortedEdge.Edge):
            self.Edge[i] = edge
        del(sortedEdge)

class NODE:
    def __init__(self):
        self.Node = []

    def Add(self, d):
        self.Node.append(d)

    def Addnparray(self, array):
        # for id in self.Node: id[0] = float(id[0])
        npNode = np.array(self.Node)
        self.Node = np.concatenate((npNode, array), axis=0)
    def Nparray(self, array): 
        self.Node = np.array(array)

    def Delete(self, n):
        N = len(self.Node)
        for i in range(N):
            if self.Node[i][0] == n:
                del (self.Node[i])
                break

    def Sort(self, item=0, reverse=False):
        tmpNode = NODE()
        try:
            arr = self.Node[:, item]
        except:
            npNode = np.array(self.Node)
            arr = npNode[:, item]
        if reverse == False: args = np.argsort(arr)
        else:                args = np.argsort(arr)[::-1]
        for nd in self.Node:    tmpNode.Add(nd) 
        sortedlist = []
        for i, arg in enumerate(args):
            self.Node[i] = tmpNode.Node[int(arg)]
            sortedlist.append(tmpNode.Node[int(arg)])
        del(tmpNode)
        sortedlist = np.array(sortedlist)
        return sortedlist


    def Tuple(self):
        I = len(self.Node)
        J = len(self.Node[0])
        LST = []
        for i in range(I):
            for j in range(J):
                LST.append(self.Node[i][j])
        
        tuplelst = tuple(LST)
        
        return tuplelst, J
        
    def DeleteDuplicate(self):
        npary = np.array(self.Node)
        uniques = np.unique(npary)
        N = len(uniques)
        for i, nd in enumerate(self.Node): 
            if i < N :             nd = uniques[i]
        i = N 
        while i < len(self.Node): del(self.Node[i])


    def AddItem(self, n, d):
        N = len(self.Node)
        for i in range(N):
            if self.Node[i][0] == n:
                self.Node[i].append(d)
                break

    def DeleteItem(self, n, j):
        N = len(self.Node)
        for i in range(N):
            if self.Node[i][0] == n:
                del (self.Node[i][j])
                break
    def Combine(self, node):
        N = len(node.Node)
        for i in range(N): 
            self.Add(node.Node[i])
    
    def Rotate(self, Angle, XY=23, Xc=0.0, Yc=0.0, **args): 
        for key, value in args.items():
            if key == 'xy':
                XY=int(value)
            if key == 'xc' or key == 'XC': 
                Xc = float(value)
            if key == 'yc' or key == 'YC': 
                Yc = float(value)
    
        cx = int(XY / 10)
        cy = int(XY) % 10 
        Angle = Angle * math.pi / 180.0 
        
        N = len(self.Node)
        for i in range(N): 
            self.Node[i][cx] = math.cos(Angle) * (self.Node[i][cx] - Xc) + math.sin(Angle) * (self.Node[i][cy] - Yc)
            self.Node[i][cy] = -math.sin(Angle) * (self.Node[i][cx] - Xc) + math.cos(Angle) * (self.Node[i][cy] - Yc)

            
    def Move(self, x=0.0, y=0.0, z=0.0):
        I = len(self.Node)
        for i in range(I):
            self.Node[i][1] += x
            self.Node[i][2] += y
            self.Node[i][3] += z
    
    def Image(self, file="NODE", dpi=100, XY=23, size=0.1, marker='o', cm=0, ci=0, vmin='', vmax='', equalxy=1, **args):
        edgecolor = 'none'
        alpha = 0.5
        dotcolor = 'black'
        text = 'NODES'
        viewaxis = 1
        legendtext = ''
        for key, value in args.items():
            if key =='DPI' or key == 'Dpi':
                dpi= int(value)
            if key == 'xy': 
                XY = int(value)
            if key == 'alpha':
                alpha = value
            if key == 'edgecolors':
                edgecolor = value
            if key == 'color':
                dotcolor = value
            if key == 'label':
                text = value 
            if key == 'axis' or key == 'viewaxis':
                viewaxis = value
            if key == 'legendtext':
                legendtext = value 
                
        
        fig, ax = plt.subplots()
        if equalxy == 1:
            ax.axis('equal')
        
        if viewaxis == 1:
            ax.axis('on')
        else:
            ax.axis('off')
            
        N = len(self.Node)
        x = []
        y = []
        v = []
        cx = int(XY / 10)
        cy = int(XY) % 10 
        if (cx == 1 and cy == 2) or (cx == 2 and cy ==1): 
            cv =3
        elif (cx == 1 and cy == 3) or (cx == 3 and cy ==1): 
            cv =2
        else:
            cv = 1
        if ci != 0:
            cv = ci
        
        for nd in self.Node:
            x.append(nd[cx])
            y.append(nd[cy])
            v.append(nd[cv])
        npnode = np.array(self.Node)

        npV = np.array(v)

        min = np.min(npV)
        max = np.max(npV)

        if cm == 0: 
            plt.scatter(x, y, color=dotcolor, s=size, marker=marker, label=text, alpha = alpha, edgecolors=edgecolor)
        else:
            if vmin !='':
                min = vmin
            if vmax !='':
                max =vmax 
            
            contour= plt.scatter(x, y, c=v,  s=size, edgecolors=edgecolor, marker=marker, vmin=min, vmax=max, alpha = alpha, cmap='jet')
            
            if legendtext != '':
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="1%", pad=0.1)
                cbar = plt.colorbar(contour, cax=cax, format='%.2f')
                cbar.ax.tick_params(labelsize=8)
                plt.title(legendtext , fontsize=8)
            else:
                cb = plt.colorbar(format="%.2E")
                cb.ax.tick_params(labelsize=7)


            
        plt.savefig(file, dpi=dpi)
        plt.clf()
        
    
    def ImageLine(self, file="NODE", dpi=100, XY=23, marker='o', equalxy=1, size=1, color = 'black', **args):
        viewaxis = 1
        for key, value in args.items():
            if key == 'xy':
                XY=int(value)
            if key == 'axis' or key == 'viewaxis':
                viewaxis = value
                
        color = 'black'
        text = 'NODES'
        fig, ax = plt.subplots()
        if equalxy == 1:
            ax.axis('equal')
        if viewaxis == 1:
            ax.axis('on')
        else:
            ax.axis('off')
        
        N = len(self.Node)
        x = []
        y = []
        v = []
        cx = int(XY / 10)
        cy = int(XY) % 10 
        if (cx == 1 and cy == 2) or (cx == 2 and cy ==1): 
            cv =3
        elif (cx == 1 and cy == 3) or (cx == 3 and cy ==1): 
            cv =2
        else:
            cv = 1
                
        for nd in self.Node:
            x.append(nd[cx])
            y.append(nd[cy])
            v.append(nd[cv])
        npnode = np.array(self.Node)

        npV = np.array(v)

        min = np.min(npV)
        max = np.max(npV)

        plt.plot(x, y, color=color, marker=marker, label=text, markersize=size)
        plt.savefig(file, dpi=dpi)
        plt.clf()

    def Print(self):
        N = len(self.Node)
        J = len(self.Node[0])
        for i in range(N):
            line = ''
            for j in range(J):
                if j != J-1:
                    line += str(self.Node[i][j]) + ", "
                else:
                    line += str(self.Node[i][j]) + ""
            print (line)

    def Save(self, file='NODE.txt'):
        N = len(self.Node)
        iN = len(self.Node[0])
        f = open(file, "w")
        fline = []
        
        for i in range(N):
            text = ""
            for j in range(iN): 
                text += str(self.Node[i][j]) 
                if j != iN -1:
                    text += ', '
                else:
                    text += '\n'
            fline.append([text])
        f.writelines('%s' % str(item[0]) for item in fline)
        f.close()

    def NodeByID(self, n, SORT=0, **args):
        callfrom=''
        for key, value in args.items():
            if key == 'sort':
                SORT=int(value)
            if key == 'name': 
                callfrom = value 

        N = len(self.Node)
        if SORT ==1:
            sorted(self.Node, key=lambda x:x[0])
        if N>100:
            if self.Node[int(N / 4)][0] > n:
                k1 = 0
                k2 = int(N / 4)
            elif self.Node[int(N / 2)][0] > n:
                k1 = int(N / 4)
                k2 = int(N / 2)
            elif self.Node[int(3 * N / 4)][0] > n:
                k1 = int(N / 2)
                k2 = 3 * int(N / 4)
            else:
                k1 = 3 * int(N / 4)
                k2 = N
            for i in range(k1, k2):
                if self.Node[i][0] == n:
                    return self.Node[i]
        for i in range(N):
            if self.Node[i][0] == n:
                return self.Node[i]
        if callfrom == '':  print ("Cannot Find the Node (%d)"%(n))
        else: print ("Cannot Find the Node (%d) for %s"%(n, callfrom))
        NullList = [0, 0.0, 0.0, 0.0]
        return NullList

    def NodeIDByCoordinate(self, PO, v, closest=0, **args):
    
        N = len(self.Node)
        
        if closest != 0:
            min = 1000000000.0
            
            if PO == 'x' or PO == 'X':
                for i in range(N):
                    if abs(self.Node[i][1]-v) < min:
                        min = self.Node[i][1]
                        ClosestNode = self.Node[i][0]
            elif PO == 'y' or PO == 'Y':
                for i in range(N):
                    if abs(self.Node[i][2]-v) < min:
                        min = self.Node[i][2]
                        ClosestNode = self.Node[i][0]
            elif PO == 'z' or PO == 'Z':
                for i in range(N):
                    if abs(self.Node[i][3]-v) < min:
                        min = self.Node[i][3]
                        ClosestNode = self.Node[i][0]
            else:
                print ("* Check INPUT x/y/z - you input %s"%(PO))
            return ClosestNode
        else: 
            IDs = []
            if PO == 'x' or PO == 'X':
                for i in range(N):
                    if self.Node[i][1] == v:
                        IDs.append(self.Node[i][0])
            elif PO == 'y' or PO == 'Y':
                for i in range(N):
                    if self.Node[i][2] == v:
                        IDs.append(self.Node[i][0])
            elif PO == 'z' or PO == 'Z':
                for i in range(N):
                    if self.Node[i][3] == v:
                        IDs.append(self.Node[i][0])
            else:
                print ("* Check INPUT x/y/z - you input", PO)
            if len(IDs) == 0:
                print ("* Matching Node (", PO, ":", v,")was not found!!")
            return IDs

    def Help(self):
        print ("*************************************************************************************")
        print ("** [Node_ID, X, Y, Z]")
        print ("** - Based on SAE Tire standard Tire Axis System.")
        print ("** - X : longitudinal axis (direction of wheel heading)")
        print ("** - Y : lateral axis")
        print ("** - Z : Vertical axis")
        print ("** - From CUTE : int(ID[0]), float([3]), float([2]), float([1])")
        print ("** Related Function ******************************************************")
        print ("** - self.Add([]) -> Add a set of Node components")
        print ("** - self.Delete(n) => delete Node ID 'n'")
        print ("** - self.AddItem(n, v) => Add a item 'v' to Node ID 'n'")
        print ("** - self.DeleteItem(n, j) => delete 'j'th item from Node ID 'n'")
        print ("** - self.Print() => print on the screen")
        print ("** - self.Save(file_name) => Save Nodes in a file")
        print ("** - self.NodeByID(n) => returns a list of Node ID 'n'")
        print ("** - self.NodeIDByCoordinate(x/y/z, v) ==> returns Node IDs with x/y/z position v")
        print ("** - self.Image(Image_File_Name, ImageSize(dpi)) => generates a image of nodes")
        print ("*************************************************************************************")

class SURFACE:
    def __init__(self):
        self.Surface = []
    def Add(self, surface):
        self.Surface.append(surface)
    def Print(self):
        N = len(self.Surface)
        J = len(self.Surface[0])
        for i in range(N):
            line = ''
            for j in range(J):
                if j != J-1:
                    line += str(self.Surface[i][j]) + ", "
                else:
                    line += str(self.Surface[i][j]) 
            print (line)

    def Image(self, Node, file='SURFACE', dpi=100, XY=23, **args):
        icolor = 'lightgray'
        for key, value in args.items():
            if key == 'Dpi':
                dpi = int(value)
            if key == 'xy':
                XY = int(value)
            if key == 'color':
                icolor = value

        
        x=int(XY/10)
        y=int(XY%10)

        fig, ax = plt.subplots()
        ax.axis('equal')
        ax.axis('on')

        cdepth = 0.5
        MeshLineWidth = 0.3
        MembWidth = 0.3
        Mcolor = 'red'

        N = len(self.Surface)
        MinX = 100000.0
        MaxX = -100000.0
        MinY = 100000.0
        MaxY = -100000.0
        

        for i in range(N):
            N1 = Node.NodeByID(self.Surface[i][0])
            N2 = Node.NodeByID(self.Surface[i][1])
            x1 = N1[x]
            y1 = N1[y]
            x2 = N2[x]
            y2 = N2[y]
            
            if self.Surface[i][3] == 0:
                N3 = Node.NodeByID(self.Surface[i][2])
                x3 = N3[x]
                y3 = N3[y]
                # icolor = Color(self.Surface[i][5])
                # if x1 == 0.0 or x2 == 0.0 or x3 == 0.0  :
                    # continue
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
                ax.add_patch(polygon)
                if MinX > x3:
                    MinX = x3
                if MaxX < x3:
                    MaxX = x3
                if MinY > y3:
                    MinY = y3
                if MaxY < y3:
                    MaxY = y3
            else:
                N3 = Node.NodeByID(self.Surface[i][2])
                N4 = Node.NodeByID(self.Surface[i][3])
                x3 = N3[x]
                y3 = N3[y]
                x4 = N4[x]
                y4 = N4[y]
                # icolor = Color(self.Surface[i][5])
                # if x1 == 0.0 or x2 == 0.0 or x3 == 0.0 or x4 == 0.0 :
                    # continue
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
                ax.add_patch(polygon)
                if MinX > x3:
                    MinX = x3
                if MaxX < x3:
                    MaxX = x3
                if MinY > y3:
                    MinY = y3
                if MaxY < y3:
                    MaxY = y3
                if MinX > x4:
                    MinX = x4
                if MaxX < x4:
                    MaxX = x4
                if MinY > y4:
                    MinY = y4
                if MaxY < y4:
                    MaxY = y4
            if MinX > x1:
                MinX = x1
            if MaxX < x1:
                MaxX = x1
            if MinY > y1:
                MinY = y1
            if MaxY < y1:
                MaxY = y1
            if MinX > x2:
                MinX = x2
            if MaxX < x2:
                MaxX = x2
            if MinY > y2:
                MinY = y2
            if MaxY < y2:
                MaxY = y2
        plt.xlim(MinX - 0.01, MaxX + 0.01)
        plt.ylim(MinY - 0.01, MaxY + 0.01)
        plt.savefig(file, dpi=dpi)
 
    def Nodes(self, Node=NODE()):
        I = len(self.Surface)
        NL = []
        
        for i in range(I):
            for j in range(4):
                if self.Surface[i][j] != 0:
                    NL.append(self.Surface[i][j])
        
        i=0
        while i < len(NL):
            j = i+1
            while j < len(NL):
                if NL[i] == NL[j]:
                    del(NL[j])
                    j -= 1
                j+=1
            i+= 1
        
        if len(Node.Node) == 0:
            # print ("# Node IDs in ELSET : Node_ID=[]")
            return NL

        I = len(NL)
        NC = NODE()
        for i in range(I):
            N = Node.NodeByID(NL[i])
            NC.Add(N)
        # print ("# Nodes in ELSET : Node=NODE()")
        return NC 
        
        
class ELEMENT3D:
    def __init__(self):
        self.Element = []

    def Add(self, e):
        self.Element.append(e)
    def Print(self):
        N = len(self.Element)
        J = len(self.Element[0])
        for i in range(N):
            line = ''
            for j in range(J):
                if j != J-1:
                    line += str(self.Element[i][j]) + ", "
                else:
                    line += str(self.Element[i][j]) 
            print (line)
    def Surface(self):
        I = len(self.Element)
        eset = len(self.Element[0])
        elist = []
        for i in range(I):
            for j in range(eset):
                elist.append(self.Element[i][j])
        etuple = tuple(elist)
        t1 = time.time()
        r=_islm.Element3Dtosurface(etuple, eset)
        t2 = time.time()
        print (t2 - t1 )
        I = len(r)
        surface = SURFACE()
        for i in range(int(I/7)):
            surface.Add([r[i*7], r[i*7+1], r[i*7+2], r[i*7+3], r[i*7+4], r[i*7+5], r[i*7+6]])
        
        return surface

class ELEMENT:
    def __init__(self):
        self.Element = []
        
    def Help(self):
        print ("*************************************************************************************")
        print ("** Element_ID, Node1, Node2, Node3, Node4, Elset_Name, How_Many_Nodes,")
        print ("**             Area/Length, Center_Y(Lateral), Center_Z(Vertical)")
        print ("** Related Functions *****************************************************")
        print ("** - self.Add([]) => Add a ITEM[]")
        print ("** - self.Delete(n) => delete a Element ID 'n'")
        print ("** - self.AddItem(n, v) => Add a item 'v' to Element ID 'n'")
        print ("** - self.DeleteItem(n, j) => delete 'j'th item from Element ID 'n'")
        print ("** - self.Print() => print Element on the screen")
        print ("** - self.Save(File_Name) => Save Element in a file")
        print ("** - self.ElementByID(n) => return Element List of Element ID 'n'")
        print ("** - self.ElementsBySetname('Name') => return a list of element IDs with the same ELSET Name")
        print ("** - self.ElsetNames() => return a list with Elset Names of the class")
        print ("** - self.ChangeSetNameByElset(name1, name2) => Change Elset name from name1 to name2")
        print ("** - self.ChangeSetNameByID(n, Name) => Change Elset name of Element ID 'n' to Name")
        print ("** - self.Image(Node(Class), Image_file_Name, Image_Size)")
        print ("** - self.Elset('Elset_Name') --> create a Element Class of 'Elset_Name'")
        print ("** - self.AllEdge() -> create a EDGE Class from this Element class")
        print ("** - self.FreeEdge() -> return a Edge Class with free edges")
        print ("** - self.OuterEdge(Node) -> Return a Edge class with Outer edges")
        print ("** - self.TieEdge(Node) --> Return a Edge Class with Tie edges")
        print ("*************************************************************************************")

    def Add(self, e):
        self.Element.append(e)

    def Delete(self, n):
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][0] == n:
                del (self.Element[i])
                break
                
    def Sort(self, item=0, reverse=False):
        sortedElement = ELEMENT()
        for i, element in enumerate(self.Element):
            sortedElement.Add(element)
            if i == 0:
                continue
            else:
                I = len(sortedElement.Element)
                for j, selement in enumerate(sortedElement.Element):
                    if reverse == True:
                        if selement[item] < element[item]:
                            del(sortedElement.Element[I-1])
                            sortedElement.Element.insert(j, element)
                            I = j 
                            break
                    else:
                        if selement[item] > element[item]:
                            del(sortedElement.Element[I-1])
                            sortedElement.Element.insert(j, element)
                            I = j 
                            break
        for i, element in enumerate(sortedElement.Element):
            self.Element[i] = element
        del(sortedElement)

    def Tuple(self):
        I = len(self.Element)
        J = len(self.Element[0])
        LST = []
        for i in range(I):
            for j in range(J):
                if j == 5:
                    LST.append(0)
                if self.Element[i][6] == 2 and j == 3:
                    LST.append(0)
                if self.Element[i][6] == 2 and j == 4:
                    LST.append(0)
                if self.Element[i][6] == 3 and j == 4:
                    LST.append(0)
                LST.append(self.Element[i][j])
        
        tuplelst = tuple(LST)
        
        return tuplelst, J
        
    def ElsetToEdge(self, SetName):
        SetElement = self.Elset(SetName)
        
        mEdge=EDGE()
        N = len(SetElement.Element)
        if N == 0: 
            return mEdge
        if SetElement.Element[0][6] == 2:
            for i in range(N): 
                mEdge.Add([SetElement.Element[i][1], SetElement.Element[i][2], SetElement.Element[i][5], 'S0', SetElement.Element[i][0], SetElement.Element[i][7]])
                
        else:
            for i in range(N):
                mEdge.Add([SetElement.Element[i][1], SetElement.Element[i][2], SetElement.Element[i][5], 'S1', SetElement.Element[i][0], 0])
                mEdge.Add([SetElement.Element[i][2], SetElement.Element[i][3], SetElement.Element[i][5], 'S2', SetElement.Element[i][0], 0])
                if SetElement.Element[i][6] == 3: 
                    mEdge.Add([SetElement.Element[i][3], SetElement.Element[i][1], SetElement.Element[i][5], 'S3', SetElement.Element[i][0], 0])
                if SetElement.Element[i][6] == 4: 
                    mEdge.Add([SetElement.Element[i][3], SetElement.Element[i][4], SetElement.Element[i][5], 'S3', SetElement.Element[i][0], 0])
                    mEdge.Add([SetElement.Element[i][4], SetElement.Element[i][1], SetElement.Element[i][5], 'S4', SetElement.Element[i][0], 0])
        return mEdge
        
    def DeleteDuplicate(self):
        i = 0
        while i < len(self.Element):
            j = i + 1
            while j < len(self.Element):
                if self.Element[i][0] == self.Element[j][0]:
                    del (self.Element[j])
                    j += -1
                j += 1
                if j >= len(self.Element):
                    break
            i += 1
            if i >= len(self.Element):
                break
    def Combine(self, element):
        N=len(element.Element)
        for i in range(N): 
            self.Add(element.Element[i])
            
    def Image(self, Node, file='ELEMENT', dpi=100, XY=23, **args):
        
        for key, value in args.items():
            if key == 'Dpi':
                dpi = int(value)
            if key == 'xy':
                XY = int(value)

        
        x=int(XY/10)
        y=int(XY%10)

        fig, ax = plt.subplots()
        ax.axis('equal')
        ax.axis('on')

        cdepth = 0.8
        MeshLineWidth = 0.1
        MembWidth = 0.3
        Mcolor = 'red'

        N = len(self.Element)
        MinX = 100000.0
        MaxX = -100000.0
        MinY = 100000.0
        MaxY = -100000.0

        for i in range(N):
            N1 = Node.NodeByID(self.Element[i][1])
            N2 = Node.NodeByID(self.Element[i][2])
            x1 = N1[x]
            y1 = N1[y]
            x2 = N2[x]
            y2 = N2[y]
            if self.Element[i][6] == 2:
                plt.plot([x1, x2], [y1, y2], Mcolor, lw=MembWidth)
            elif self.Element[i][6] == 3:
                N3 = Node.NodeByID(self.Element[i][3])
                x3 = N3[x]
                y3 = N3[y]
                icolor = Color(self.Element[i][5])
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
                ax.add_patch(polygon)
                if MinX > x3:
                    MinX = x3
                if MaxX < x3:
                    MaxX = x3
                if MinY > y3:
                    MinY = y3
                if MaxY < y3:
                    MaxY = y3
            elif self.Element[i][6] == 4:
                N3 = Node.NodeByID(self.Element[i][3])
                N4 = Node.NodeByID(self.Element[i][4])
                x3 = N3[x]
                y3 = N3[y]
                x4 = N4[x]
                y4 = N4[y]
                icolor = Color(self.Element[i][5])
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
                ax.add_patch(polygon)
                if MinX > x3:
                    MinX = x3
                if MaxX < x3:
                    MaxX = x3
                if MinY > y3:
                    MinY = y3
                if MaxY < y3:
                    MaxY = y3
                if MinX > x4:
                    MinX = x4
                if MaxX < x4:
                    MaxX = x4
                if MinY > y4:
                    MinY = y4
                if MaxY < y4:
                    MaxY = y4
            if MinX > x1:
                MinX = x1
            if MaxX < x1:
                MaxX = x1
            if MinY > y1:
                MinY = y1
            if MaxY < y1:
                MaxY = y1
            if MinX > x2:
                MinX = x2
            if MaxX < x2:
                MaxX = x2
            if MinY > y2:
                MinY = y2
            if MaxY < y2:
                MaxY = y2
        plt.xlim(MinX - 0.01, MaxX + 0.01)
        plt.ylim(MinY - 0.01, MaxY + 0.01)
        plt.savefig(file, dpi=dpi)

    def Print(self):
        N = len(self.Element)
        J = len(self.Element[0])
        for i in range(N):
            line = ''
            for j in range(J):
                if j != J-1:
                    line += str(self.Element[i][j]) + ", "
                else:
                    line += str(self.Element[i][j]) 
            print (line)

    def Save(self, file='ELEMENT.txt'):
        N = len(self.Element)
        f = open(file, "w")
        fline = []
        for i in range(N):
            text = str(self.Element[i]) + '\n'
            fline.append([text])
        f.writelines('%s' % str(item[0]) for item in fline)
        f.close()

    def AddItem(self, n, d):
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][0] == n:
                self.Element[i].append(d)
                break

    def DeleteItem(self, n, j):
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][0] == n:
                del (self.Element[i][j])
                break


    def ElementByID(self, n):
        N = len(self.Element)
        # self.Element.sort()
        if self.Element[int(N / 4)][0] > n:
            k1 = 0
            k2 = int(N / 4)
        elif self.Element[int(N / 2)][0] > n:
            k1 = int(N / 4)
            k2 = int(N / 2)
        elif self.Element[3 * int(N / 4)][0] > n:
            k1 = int(N / 2)
            k2 = 3 * int(N / 4)
        else:
            k1 = 3 * int(N / 4)
            k2 = N
        for i in range(k1, k2):
            if self.Element[i][0] == n:
                return self.Element[i]
        for i in range(N):
            if self.Element[i][0] == n:
                return self.Element[i]
        print ("Cannot Find Element (%d)"%(n))
        NullList = [0, 0, 0, 0, 0, '', 0, 0.0, 0.0, 0.0]
        return NullList

    def ElementBySetname(self, Name):
        SetList = []
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][5] == Name:
                SetList.append(self.Element[i][0])
        return SetList

    def Elset(self, SetName):
        ESet = ELEMENT()
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][5] == SetName:
                ESet.Add(self.Element[i])
        return ESet
    def Nodes(self, **args):

        Node = NODE()
        for key, value in args.items():
            if key == 'Node' or key == 'node':
                Node = value


        I = len(self.Element)
        NL = []
        
        for i in range(I):
            for j in range(1, self.Element[i][6]+1):
                NL.append(self.Element[i][j])
        
        i=0
        while i < len(NL):
            j = i+1
            while j < len(NL):
                if NL[i] == NL[j]:
                    del(NL[j])
                    j -= 1
                j+=1
            i+= 1
        
        if len(Node.Node) == 0:
            # print ("# Node IDs in ELSET : Node_ID=[]")
            return NL

        I = len(NL)
        NC = NODE()
        for i in range(I):
            N = Node.NodeByID(NL[i])
            NC.Add(N)
        # print ("# Nodes in ELSET : Node=NODE()")
        return NC
        
        
    def ElsetNames(self):
        Names = []
        N = len(self.Element)

        for i in range(N):
            isSet = 0
            M = len(Names)
            for j in range(M):
                if Names[j] == self.Element[i][5]:
                    isSet = 1
                    break
            if isSet == 0:
                Names.append(self.Element[i][5])
        Names.sort()
        return Names
    def NodesInElement(self, node):
        eNode = NODE()
        N = len(self.Element)
        for i in range(N):
            for j in range(1, self.Element[i][6]+1): 
                eNode.Add(node.NodeByID(self.Element[i][j]))
        eNode.DeleteDuplicate()
        return eNode
                
    def AllEdge(self):
        Name = EDGE()
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][6] == 4:
                Name.Add([self.Element[i][1], self.Element[i][2], self.Element[i][5], 'S1', self.Element[i][0], -1])
                Name.Add([self.Element[i][2], self.Element[i][3], self.Element[i][5], 'S2', self.Element[i][0], -1])
                Name.Add([self.Element[i][3], self.Element[i][4], self.Element[i][5], 'S3', self.Element[i][0], -1])
                Name.Add([self.Element[i][4], self.Element[i][1], self.Element[i][5], 'S4', self.Element[i][0], -1])
            elif self.Element[i][6] == 3:
                Name.Add([self.Element[i][1], self.Element[i][2], self.Element[i][5], 'S1', self.Element[i][0], -1])
                Name.Add([self.Element[i][2], self.Element[i][3], self.Element[i][5], 'S2', self.Element[i][0], -1])
                Name.Add([self.Element[i][3], self.Element[i][1], self.Element[i][5], 'S3', self.Element[i][0], -1])
        return Name

    def FreeEdge(self):
        edges = self.AllEdge()
        freeEdge = FreeEdge(edges)
        return freeEdge

    def OuterEdge(self, Node):
        FEdges = self.FreeEdge()
        # print(len(FEdges.Edge))
        OEdges = OuterEdge(FEdges, Node, self)
        return OEdges

    def TieEdge(self, Node):
        FreeEdge = self.FreeEdge()
        OuterEdge(FreeEdge, Node, self)  # Don't Delete this line.
        TieNum = 1
        i = 0;        iTemp = 0;        j = 0
        connectedEdge = []
        TEdge = EDGE()
        while i < len(FreeEdge.Edge):
            if FreeEdge.Edge[i][5] < 1:
                TieNum += 1
                nodeStart = FreeEdge.Edge[i][0]
                FreeEdge.Edge[i][5] = TieNum
                TEdge.Add(FreeEdge.Edge[i])  # marked as TIE edge with No.
                iTemp = i
                while FreeEdge.Edge[iTemp][1] != nodeStart:
                    j += 1
                    if j > 100:
                        break  # in case infinite loop
                    connectedEdge = NextEdge(FreeEdge, iTemp)  # find next edge
                    if len(connectedEdge) == 1:  # in case of being found just 1 edge
                        iTemp = connectedEdge[0]
                    elif len(connectedEdge) == 2:  # when other tie is connected (2 ties are connected)
                        if FreeEdge.Edge[connectedEdge[0]][1] == nodeStart:
                            iTemp = connectedEdge[0]
                        elif FreeEdge.Edge[connectedEdge[1]][1] == nodeStart:
                            iTemp = connectedEdge[1]
                        else:
                            if FreeEdge.Edge[connectedEdge[0]][5] < 1 and FreeEdge.Edge[connectedEdge[1]][5] < 1:
                                iTemp = FindTieLoop(nodeStart, connectedEdge, FreeEdge)
                            elif FreeEdge.Edge[connectedEdge[0]][5] < 1:
                                iTemp = connectedEdge[0]
                            elif FreeEdge.Edge[connectedEdge[1]][5] < 1:
                                iTemp = connectedEdge[1]
                            else:
                                print ('[INPUT] {' + str(FreeEdge.Edge[connectedEdge[0]]) + ',' + str(FreeEdge.Edge[connectedEdge[1]]) + ' (0) TIE Conection InCompletion')
                                break
                    else:
                        print ('[INPUT] 2 or more Ties are Connected.')
                        break
                    # After finding next TIE Edge ################################
                    FreeEdge.Edge[iTemp][5] = TieNum
                    TEdge.Add(FreeEdge.Edge[iTemp])
                del connectedEdge
                connectedEdge = []
            i += 1
        return TEdge
        
    def MasterSlaveEdge(self, Node, Op = 0, **args):
        for key, value in args.items():
            if key == 'op':
                Op = int(value)
        
        TieEdge = self.TieEdge(Node)
        iNum = 2
        mlength = 0 
        ErrRatio = 0.01
        
        NumTie = 0 
        N = len(TieEdge.Edge)
        for i in range(N):
            if TieEdge.Edge[i][5] > NumTie:
                NumTie = TieEdge.Edge[i][5]
            
        iMaster = []
        while iNum <=NumTie:
            MaxLength = 0.0
            SumLength = 0.0
            k = 0
            Save = 0
            while k < N:
                if TieEdge.Edge[k][5] == iNum:
                    N1 = Node.NodeByID(TieEdge.Edge[k][0])
                    N2 = Node.NodeByID(TieEdge.Edge[k][1])
                    Length = math.sqrt((N1[2]-N2[2])* (N1[2]-N2[2]) + (N1[3]-N2[3])*(N1[3]-N2[3]))
                    SumLength += Length
                    if Length > MaxLength:
                        MaxLength = Length
                        Save = k
                k += 1
            SumLength -= MaxLength
            if SumLength > MaxLength * (1+ErrRatio) or SumLength < MaxLength * (1-ErrRatio):
                print ('ERROR::PRE::TIE CREATION INCOMPLETE ON', TieEdge.Edge[Save][3])
            iMaster.append(Save)
            iNum += 1
        
        MasterEdge=EDGE()
        SlaveEdge =EDGE()
        M = len(iMaster)
        for i in range(N):
            exist = 0
            for j in range(M):
                if i == iMaster[j]:
                    MasterEdge.Add(TieEdge.Edge[i])
                    exist =1
                    break
            if exist == 0:
                SlaveEdge.Add(TieEdge.Edge[i])
        
        ## Op == 0 return MasterEdge and SlaveEdge
        ## Op == 1 return only Master Edge
        ## Op == 2 return Only Slave Edge
        if Op == 0:
            return MasterEdge, SlaveEdge
        elif Op == 1:
            return MasterEdge
        else:
            return SlaveEdge
        
    def ChangeSetNameByElset(self, OName, NName):
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][5] == OName:
                self.Element[i][5] = NName

    def ChangeSetNameByID(self, n, NewName):
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][0] == n:
                self.Element[i][5] = NewName

class ELSET:
    def __init__(self):
        self.Elset = []

    def Print(self):
        print ("*************************************************************")
        print ("** [[Elset1, E11, E12, ..], {Elset2, E21, E22, ...], ...]")
        print ("*************************************************************")
        print ("** Related Functions")
        print ("** self.AddName(name) -> Add a new ELSET Name")
        print ("** self.AddNumber(n, name) -> Add a member ")

    def AddName(self, name):
        exist = 0
        for i in range(len(self.Elset)):
            if self.Elset[i][0] == name:
                exist = 1
                break
        if exist == 0:
            self.Elset.append([name])

    def AddNumber(self, n, name):
        for i in range(len(self.Elset)):
            if self.Elset[i][0] == name:
                self.Elset[i].append(n)

 ########################################
 ## Basic Functions 
 ########################################
def Mean(List, Col=0, **args):
    for key, value in args.items():
        if key == 'col' or key == 'column' or key == 'COL':
            Col = int(value)
            
    n = len(List)
    if n == 0:
        return 0
    total = 0.0
    if Col == 0: 
        for i in range(n):
            total += List[i]
    else:
        for i in range(n): 
            total += List[i][Col]
    return total / float(n)

def StandardDeviation(List, Col=0, **args):
    for key, value in args.items():
        if key == 'col' or key == 'column' or key == 'COL':
            Col = int(value)
            
    avg = Mean(List, Col)
    
    n = len(List)
    if n <=1 :
        return 0
    s = 0
    if Col ==0: 
        for i in range(n):
            s += (List[i] - avg) * (List[i] - avg)
    else:
        for i in range(n):
            s += (List[i][Col] - avg)*(List[i][Col] - avg)
            
    return math.sqrt(s / (n - 1)) 

def SaveList(iList, file="ListPrinting.txt"):
    N = len(iList)
    f = open(file, "w")
    fline = []

    for i in range(N):
        text = str(iList[i]) + '\n'
        fline.append([text])
    f.writelines('%s' % str(item[0]) for item in fline)
    f.close()

def PrintList(iList):
    N = len(iList)
    for i in range(N):
        print (iList[i])

def DeleteDuplicate(L, type='int'):
    # print "INITIAl", len(L)
    try:
        TL = tuple(L) 
        RL = _islm.DeleteDuplicate(TL)
        if type == 'int':
            I = len(RL)
            for i in range(I):
                RL[i] = int(RL[i])
        return RL
    except:
        # print "INITIAl", len(L)
        for i in range(len(L)):
            
            for j in range(i+1, len(L)):
                if j > len(L)-1:
                    break
                if L[i] == L[j] :
                    del(L[j])
                    j -= 1
                    continue
        # print "After ", len(L)        
        return L

def ImageEdge(Edge, Node, file="PlotEdges"):
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('on')

    N = len(Edge.Edge)
    MembWidth = 0.5
    color = 'black'
    MinX = 100000.0
    MaxX = -100000.0
    MinY = 100000.0
    MaxY = -100000.0
    for i in range(N):
        N1 = Node.NodeByID(Edge.Edge[i][0])
        N2 = Node.NodeByID(Edge.Edge[i][1])
        x1 = N1[2]
        y1 = N1[3]
        x2 = N2[2]
        y2 = N2[3]
        plt.plot([x1, x2], [y1, y2], color, lw=MembWidth)
        if MinX > x1:
            MinX = x1
        if MaxX < x1:
            MaxX = x1

        if MinY > y1:
            MinY = y1
        if MaxY < y1:
            MaxY = y1
    plt.xlim(MinX - 0.01, MaxX + 0.01)
    plt.ylim(MinY - 0.01, MaxY + 0.01)
    # plt.rcParams['axes.unicode_minus'] = False
    plt.savefig(file, dpi=100)

def ImageElset(SetName, Node, Element):
    file = SetName + '.png'
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('on')

    cdepth = 0.8
    MeshLineWidth = 0.1
    MembWidth = 0.3
    Mcolor = 'blue'
    N = 0
    MinX = 100000.0
    MaxX = -100000.0
    MinY = 100000.0
    MaxY = -100000.0
    N = len(Element.Element)
    EList = []
    for i in range(N):
        if Element.Element[i][5] == SetName:
            EList.append(Element.Element[i])
    N = len(EList)
    if N == 0:
        print ("No Elset -", SetName)
        return 0

    for i in range(N):
        N1 = Node.NodeByID(EList[i][1])
        N2 = Node.NodeByID(EList[i][2])
        x1 = N1[2]
        y1 = N1[3]
        x2 = N2[2]
        y2 = N2[3]
        if EList[i][6] == 2:
            plt.plot([x1, x2], [y1, y2], Mcolor, lw=MembWidth)
        elif EList[i][6] == 3:
            N3 = Node.NodeByID(EList[i][3])
            x3 = N3[2]
            y3 = N3[3]
            icolor = Color(EList[i][5])
            polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
            ax.add_patch(polygon)
        elif EList[i][6] == 4:
            N3 = Node.NodeByID(EList[i][3])
            N4 = Node.NodeByID(EList[i][4])
            x3 = N3[2]
            y3 = N3[3]
            x4 = N4[2]
            y4 = N4[3]
            icolor = Color(EList[i][5])
            polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
            ax.add_patch(polygon)

        if MinX > x1:
            MinX = x1
        if MaxX < x1:
            MaxX = x1

        if MinY > y1:
            MinY = y1
        if MaxY < y1:
            MaxY = y1
    plt.xlim(MinX - 0.1, MaxX + 0.1)
    plt.ylim(MinY - 0.1, MaxY + 0.1)

    plt.savefig(file, dpi=100)

def ImageNode(node1, file="NODE", dpi=100, XY=23, size=1.0, marker='o', cm=0, ci=4, vmin='', vmax='', equalxy=1, **args):
    edgecolor = 'none'
    alpha = 1.0
    dotcolor = 'black'
    text = 'NODE0'
    text2 = 'Node2'
    text3 = 'Node3'
    text4 = 'Node4'
    viewaxis = 1
    node2 = NODE()
    node3 = NODE()
    node4 = NODE()
    dot2color = 'red'
    dot3color = 'blue'
    dot4color = 'green'
    line = 0
    for key, value in args.items():
        if key =='DPI' or key == 'Dpi':            dpi= int(value)
        if key == 'xy':                            XY = int(value)
        if key == 'alpha':                         alpha = value
        if key == 'edgecolors':                    edgecolor = value
        if key == 'color':                         dotcolor = value
        if key == 'label':                         text = value 
        if key == 'label2':                         text2 = value 
        if key == 'label3':                         text3 = value 
        if key == 'label4':                         text4 = value 
        if key == 'axis':                          viewaxis = value
        if key == "n2":                            node2= value
        if key == "n3":                         node3= value
        if key == "n4":                         node4= value
        if key == 'color':                      dotcolor = value
        if key == 'c2':                         dot2color = value
        if key == 'c3':                         dot3color = value
        if key == 'c4':                         dot4color = value
        if key == 'line':                       line = value 
            
    
    fig, ax = plt.subplots()
    if equalxy == 1:
        ax.axis('equal')
    
    if viewaxis == 1:
        ax.axis('on')
    else:
        ax.axis('off')
        
    N = len(node1.Node)
    x = []
    y = []
    v = []
    cx = int(XY / 10)
    cy = int(XY) % 10 
    cv = ci
    
    min = 9.9E15
    max = -9.9E15
    for i in range(N):
        x.append(node1.Node[i][cx])
        y.append(node1.Node[i][cy])
        if cm !=0:
            v.append(node1.Node[i][cv])
            if min > node1.Node[i][cv]: 
                min = node1.Node[i][cv]
            if max < node1.Node[i][cv]: 
                max = node1.Node[i][cv]
    if len(node2.Node)>0:
        I = len(node2.Node)
        x2 = []
        y2 = []
        v2 = []
        for i in range(I):
            x2.append(node2.Node[i][cx])
            y2.append(node2.Node[i][cy])
            if cm !=0:
                v2.append(node2.Node[i][cv])
                if min > v2[i]:
                    min = v2[i]
                if max < v2[i]: 
                    max = v2[i]
    if len(node3.Node)>0:
        I = len(node3.Node)
        x3 = []
        y3 = []
        v3 = []
        for i in range(I):
            x3.append(node3.Node[i][cx])
            y3.append(node3.Node[i][cy])
            if cm !=0:
                v3.append(node3.Node[i][cv])
                if min > v3[i]:
                    min = v3[i]
                if max < v3[i]: 
                    max = v3[i]
    if len(node4.Node)>0:
        I = len(node4.Node)
        x4 = []
        y4 = []
        v4 = []
        for i in range(I):
            x4.append(node4.Node[i][cx])
            y4.append(node4.Node[i][cy])
            if cm !=0:
                v4.append(node4.Node[i][cv])
                if min > v4[i]:
                    min = v4[i]
                if max < v4[i]: 
                    max = v4[i]
    if cm == 0: 
        if line == 0:
            plt.scatter(x, y, color=dotcolor, s=size, marker=marker, label=text, alpha = alpha, edgecolors=edgecolor)
        else:
            plt.plot(x, y, color=dotcolor, marker=marker)
        if len(node2.Node)>0:
            dotcolor = dot2color
            if line == 0:
                plt.scatter(x2, y2, color=dotcolor, s=size, marker=marker, label=text, alpha = alpha, edgecolors=edgecolor)
            else:
                plt.plot(x2, y2, color=dotcolor, marker=marker)
        if len(node3.Node)>0:
            dotcolor = dot3color
            if line ==0:
                plt.scatter(x3, y3, color=dotcolor, s=size, marker=marker, label=text, alpha = alpha, edgecolors=edgecolor)
            else:
                plt.plot(x3, y3, color=dotcolor, marker=marker)
        if len(node4.Node)>0:
            dotcolor = dot4color
            if line ==0:
                plt.scatter(x4, y4, color=dotcolor, s=size, marker=marker, label=text, alpha = alpha, edgecolors=edgecolor)
            else:
                plt.plot(x4, y4, color=dotcolor, marker=marker)
    else:
        # print "Max/Min", min, max
        if vmin !='':
            min = vmin
        if vmax !='':
            max =vmax 
        
        plt.scatter(x, y, c=v,  s=size, edgecolors=edgecolor, marker=marker, vmin=min, vmax=max, alpha = alpha, cmap='jet')
        if len(node2.Node)>0:
            edgecolor = dot2color
            linewidth = size * 0.05
            plt.scatter(x2, y2, c=v2, s=size, edgecolors=edgecolor, marker=marker, vmin=min, vmax=max, alpha = alpha, linewidth = linewidth, cmap='jet')
        if len(node3.Node)>0:
            edgecolor = dot3color
            linewidth = size * 0.05
            plt.scatter(x3, y3, c=v3, s=size, edgecolors=edgecolor, marker=marker, vmin=min, vmax=max, alpha = alpha, linewidth = linewidth, cmap='jet')
        if len(node3.Node)>0:
            edgecolor = dot4color
            linewidth = size * 0.05
            plt.scatter(x4, y4, c=v4, s=size, edgecolors=edgecolor, marker=marker, vmin=min, vmax=max, alpha = alpha, linewidth = linewidth, cmap='jet')
        cb = plt.colorbar(format="%.2E")
        cb.ax.tick_params(labelsize=7)
        
    plt.savefig(file, dpi=dpi)
    plt.clf()

def Area(NodeList, Node, XY=23, **args):   ## Calculate Area of a polygon
    errorimage = 1
    for key, value in args.items():
        if key == 'xy' :   XY = int(value)
        if key == 'error': errorimage= int(value)
    
    if len(Node.Node) > 0:
    
        ii = int(XY/10)
        jj = int(XY)%10
        
        n = len(NodeList)
        x = []
        y = []
        
        for i in range(n):
            Ni = Node.NodeByID(NodeList[i])
            x.append(Ni[ii])
            y.append(Ni[jj])
        x.append(x[0])
        y.append(y[0])
        A = [0.0, 0.0, 0.0]

        for i in range(n):
            s = x[i] * y[i + 1] - x[i + 1] * y[i]
            A[0] += s
            A[1] += (x[i] + x[i + 1]) * s
            A[2] += (y[i] + y[i + 1]) * s

        A[0] = A[0] / 2.0
        try:
            A[1] = A[1] / A[0] / 6
            A[2] = A[2] / A[0] / 6
        except:
            if errorimage > 0: 
                print ("!! Error to calculate Area ", A)
                pNode = NODE()
                for i in range(n):
                    Ni = Node.NodeByID(NodeList[i])
                    pNode.Add(Ni)
                pNode.Image("Error_Area_"+str(pNode.Node[0][0])+".png", size=1.5)
            return [0.0, 0.0, 0.0]

        if A[0] < 0:
            A[0] = -A[0]
            # print 'Negative Area Calculation! '
        return A
    else:
        print ("Length of Node is 0")
        return [0.0, 0.0, 0.0]

def NodeDistance(n1, n2, node):  ## Calculate the distance of the 2 nodes 
    N1 = node.NodeByID(n1)
    N2 = node.NodeByID(n2)
    length = math.sqrt((N1[1] - N2[1]) * (N1[1] - N2[1]) + (N1[2] - N2[2]) * (N1[2] - N2[2]) + (N1[3] - N2[3]) * (N1[3] - N2[3]))
    return length
   
def CalculateRadiusOf3Points(N1, N2, N3, XY=23, R=0, **args):
    for key, value in args.items():
        if key == 'r':    # determine the reverse or not of the radius value 
            R = int(value)
        if key == 'xy':
            XY = int(value)
            
    cx = int(XY / 10)
    cy = int(XY) % 10 
    # #################################################################################
    # Center of the Tire 
    # Xc = (y3-y2*y1-y2)*(x2^2-x1^2+y2^2-y1^2)   /((x2-x1)*(y3-y2)-(y2-y1)*(x3-x2))*0.5
    # Yc = (x2-x3*x2-x1)*(x3^2-x2^2+y3^2-y2^2)   /((x2-x1)*(y3-y2)-(y2-y1)*(x3-x2))*0.5
    # #################################################################################
    
    Det = (N2[cx]-N1[cx])*(N3[cy]-N2[cy])-(N2[cy]-N1[cy])*(N3[cx]-N2[cx])
    A = N2[cx] * N2[cx] - N1[cx] * N1[cx] + N2[cy] * N2[cy] - N1[cy] * N1[cy]
    B = N3[cx] * N3[cx] - N2[cx] * N2[cx] + N3[cy] * N3[cy] - N2[cy] * N2[cy]
    Xc = 0.5 / Det * ( (N3[cy] - N2[cy]) * A + (N1[cy] - N2[cy]) * B  )
    Yc = 0.5 / Det * ( (N2[cx] - N3[cx]) * A + (N2[cx] - N1[cx]) * B  )
    
    Radius = math.sqrt((Xc-N2[cx])*(Xc-N2[cx])+(Yc-N2[cy])*(Yc-N2[cy]))
    if R == cx:
        if Xc > N2[cx] and N2[cx] > 0.0: 
            Radius = -Radius
        if Xc < N2[cx] and N2[cx] < 0.0: 
            Radius = -Radius
    elif R ==cy: 
        if Yc > N2[cy] and N2[cy] > 0.0: 
            Radius = -Radius
        if Yc < N2[cy] and N2[cy] < 0.0: 
            Radius = -Radius
    else:
        pass
    return Radius
    
def CalculateAngleFrom3Node(N1, N2, Center, XY=13, **args):
    for key, value in args.items():
        if key == 'xy':
            XY = int(value)
    
    ix = int(XY/10)
    iy = int(XY)%10  
    
    V1x = N1[ix] - Center[ix]
    V1y = N1[iy] - Center[iy]
    V2x = N2[ix] - Center[ix]
    V2y = N2[iy] - Center[iy]
    
    L1 = math.sqrt(V1x*V1x + V1y*V1y)
    L2 = math.sqrt(V2x*V2x + V2y*V2y)
    
    # print 'L1', L1, ',V1:', V1x, ',', V1y
    # print "L2", L2, ',V2:', V2x, ',', V2y
    try:
        return math.acos(round((V1x*V2x+V1y*V2y)/(L1*L2), 10))
    except: 
        
        print ("ERROR. During Calculating Angle between Nodes - a in acos(a) is over 1.0 or L1*L2 = 0")
        print ("  Length : ", L1,',', L2)
        print ("  Node 1 : ", N1)
        print ("  Node 2 : ", N2)
        print ("  Center : ", Center)
        return 0

def IsPointInPolygon(Point, Polygon):  ## 
    # Point = [a, b]
    # Polygon = [[x1, y1], [x2, y2], ... ]

    # check if the point is on the edge of the polygon
    #      xi <= a <= xj & y = (yj-yi)/(xj-xi) * (x-xi) + yi |x=a = b
    #   if function of the edge is y=b or x=a,
    #####################################################################
    OutofPolygon = -1
    OnLine = 0
    InPolygon = 1
    counting = 0

    Point[0] = float(Point[0])
    Point[1] = float(Point[1])
    for i in range(len(Polygon)):
        for j in range(len(Polygon[i])):
            Polygon[i][j] = float(Polygon[i][j])

    for i in range(len(Polygon)):
        if i != len(Polygon) - 1:
            m = i
            n = i + 1
        else:
            m = i
            n = 0
        if Polygon[m][0] == Point[0] and Polygon[m][1] == Point[1]:
            return OnLine
        elif Polygon[m][0] == Polygon[n][0]:
            if Polygon[m][0] == Point[0]:
                if Polygon[m][1] > Polygon[n][1] and Point[1] < Polygon[m][1] and Point[1] > Polygon[n][1]:
                    return OnLine
                elif Polygon[m][1] < Polygon[n][1] and Point[1] > Polygon[m][1] and Point[1] < Polygon[n][1]:
                    return OnLine
                else:
                    return OutofPolygon
        elif Polygon[m][1] == Polygon[n][1]:
            if Polygon[m][1] == Point[1]:
                if Polygon[m][0] > Polygon[n][0] and Point[0] < Polygon[m][0] and Point[0] > Polygon[n][0]:
                    return OnLine
                elif Polygon[m][0] < Polygon[n][0] and Point[0] > Polygon[m][0] and Point[0] < Polygon[n][0]:
                    return OnLine
                else:
                    return OutofPolygon
            else:
                if Polygon[m][0] > Polygon[n][0] and Point[0] < Polygon[m][0] and Point[0] > Polygon[n][0] and Point[1] < Polygon[m][1]:
                    # print 'c1'
                    counting += 1
                elif Polygon[m][0] < Polygon[n][0] and Point[0] < Polygon[n][0] and Point[0] > Polygon[m][0] and Point[1] < Polygon[n][1]:
                    # print 'c2'
                    counting += 1
        else:
            y0 = (Polygon[n][1] - Polygon[m][1]) / (Polygon[n][0] - Polygon[m][0]) * (Point[0] - Polygon[m][0]) + Polygon[m][1]
            if y0 >= Point[1]:
                if Polygon[m][0] > Polygon[n][0]:
                    if Point[0] < Polygon[m][0] and Point[0] > Polygon[n][0]:
                        # print y0, Point[1]
                        if y0 == Point[1]:
                            return OnLine
                        counting += 1
                        if Polygon[m][1] == y0:
                            counting -= 1
                if Polygon[m][0] < Polygon[n][0]:
                    if Point[0] > Polygon[m][0] and Point[0] < Polygon[n][0]:
                        # print y0, Point[1]
                        if y0 == Point[1]:
                            return OnLine
                        counting += 1
                        if Polygon[m][1] == y0:
                            counting -= 1

    print ('meet', counting)

    if counting % 2 == 0:
        return OutofPolygon
    else:
        return InPolygon
 
def Jacobian(x1, x2, x3, x4, y1, y2, y3, y4):
    count = 0
    for s in [1.0, -1.0]:
        for t in [1.0, -1.0]:
            xs = 0.25 * (-(1-t)*x1 + (1-t)*x2 + (1+t)*x3 - (1+t)*x4)
            ys = 0.25 * (-(1-t)*y1 + (1-t)*y2 + (1+t)*y3 - (1+t)*y4)
            xt = 0.25 * (-(1-s)*x1 - (1+s)*x2 + (1+s)*x3 + (1-s)*x4)
            yt = 0.25 * (-(1-s)*y1 - (1+s)*y2 + (1+s)*y3 + (1-s)*y4)
            jacobian = xs * yt - ys * xt

            if jacobian < 0:
                count += 1
                          
    return count

def NormalVector(x1, x2, x3, y1, y2, y3):
    det = 0.0
    a1 = x2 - x1;    a2 = y2 - y1
    b1 = x3 - x2;    b2 = y3 - y2

    det = a1 * b2 - a2 * b1
    return det

def BoundaryNodeSort(Node, XY=21, Offset = 10000, image=0, file="SortedBoundary", clockwise=1, **args):
    for key, value in args.items():
        if key == 'xy':
            XY = int(value)
        if key == 'offset':
            Offset = int(value)
        if key == 'Clockwise':
            clockwise = int(value)
        if key == 'Image':
            image=int(value)


    x=int(XY/10)
    y=int(XY)%10
    
    I = len(Node.Node)
        
    min = 100000000000.0
    max = -100000000000.0
    for i in range(I): 
        if Node.Node[i][x] < min and  abs(Node.Node[i][y]) < 0.01 :
            min = Node.Node[i][x]
            Nmin = Node.Node[i]
        if Node.Node[i][x] > max and  abs(Node.Node[i][y]) < 0.01:
            max = Node.Node[i][x]
            Nmin2 = Node.Node[i]
    try:
        cx = (Nmin[x]+Nmin2[x])/2.0
        cy = (Nmin[y]+Nmin2[y])/2.0
        if Nmin[x] == Nmin2[x]: 
            ysum = 0.0
            min = 100000000000.0
            max = -100000000000.0
            for i in range(I): 
                ysum += Node.Node[i][y]
                
                if Node.Node[i][x] < min :
                    min = Node.Node[i][x]
                    Nmin = Node.Node[i]
                if Node.Node[i][x] > max :
                    max = Node.Node[i][x]
                    Nmin2 = Node.Node[i]
                    
            cx = (Nmin[x]+Nmin2[x])/2.0
            cy = ysum / float(I)
            
    except:
        # print "NO OF Boundary Node", I
        ysum = 0.0
        min = 100000000000.0
        max = -100000000000.0
        for i in range(I): 
            ysum += Node.Node[i][y]
            
            if Node.Node[i][x] < min :
                min = Node.Node[i][x]
                Nmin = Node.Node[i]
            if Node.Node[i][x] > max :
                max = Node.Node[i][x]
                Nmin2 = Node.Node[i]
                
        cx = (Nmin[x]+Nmin2[x])/2.0
        cy = ysum / float(I)

    ## divide 3 groups 
    
    tcenter = [-1000, 0.0, 0.0, 0.0]
    tcenter[x] = cx
    tcenter[y] = cy
    tmax = max
    tmin = min 
    
    llim = [-1100, 0.0, 0.0, 0.0]
    llim[x] = (cx+min) / 2.0
    llim[y] = cy
    
    rlim = [-1200, 0.0, 0.0, 0.0]
    rlim[x] = (cx+max) / 2.0
    rlim[y] = cy
    
    
    lnode = NODE()
    rnode = NODE()
    cnode = NODE()
    
    for i in range(I):
        if Node.Node[i][x] > min and Node.Node[i][x] < llim[x] : 
            lnode.Add(Node.Node[i])
        if Node.Node[i][x] > llim[x] and Node.Node[i][x] < rlim[x] : 
            cnode.Add(Node.Node[i])
        if Node.Node[i][x] > rlim[x] and Node.Node[i][x] < max : 
            rnode.Add(Node.Node[i])
    # lnode.Image("left", XY=XY)
    # cnode.Image("center", XY=XY)
    # rnode.Image("right", XY=XY)
    
    boundary = NODE()
    ## sort left nodes ###########################################
    center = [-1101, 0.0, 0.0, 0.0]
    center[x] = (tmin*3 + llim[x])/4
    center[y] = cy
    
    cx = center[x]
    
    vertical = [-1, 0.0, 0.0, 0.0]
    vertical[x] = center[x] 
    
    K = len(lnode.Node)
    
    for a in range(90, 360):
        ra = math.radians(float(a))
        min = 10000000.0
        f=0
        for i in range(K):
            if lnode.Node[i][x] > cx:
                vertical[y] = cy + 1.0
                angle = CalculateAngleFrom3Node(vertical, lnode.Node[i], center, XY=XY)
            else:
                vertical[y] = cy - 1.0
                angle = math.pi + CalculateAngleFrom3Node(vertical, lnode.Node[i], center, XY=XY) 
            
            if (angle-ra) > 0 and (angle-ra) < math.pi/180.0 and min> (angle-ra):
                min = (angle-ra)
                nearnode = lnode.Node[i]
                f=1
        if f==1:
            j = len(boundary.Node)
            if j == 0:
                boundary.Add(nearnode)
            elif nearnode[x] != boundary.Node[j-1][x] and nearnode[y] != boundary.Node[j-1][y]:
                boundary.Add(nearnode)
                
    for a in range(0, 90):
        ra = math.radians(float(a))
        min = 10000000.0
        f=0
        for i in range(K):
            if lnode.Node[i][x] > cx:
                vertical[y] = cy + 1.0
                angle = CalculateAngleFrom3Node(vertical, lnode.Node[i], center, XY=XY)
            else:
                vertical[y] = cy - 1.0
                angle = math.pi + CalculateAngleFrom3Node(vertical, lnode.Node[i], center, XY=XY) 
            
            if (angle-ra) > 0 and (angle-ra) < math.pi/180.0 and min> (angle-ra):
                min = (angle-ra)
                nearnode = lnode.Node[i]
                f=1
        if f==1:
            j = len(boundary.Node)
            if j == 0:
                boundary.Add(nearnode)
            elif nearnode[x] != boundary.Node[j-1][x] and nearnode[y] != boundary.Node[j-1][y]:
                boundary.Add(nearnode)
            
    ## end of the left nodes sorting ###########################################       
        
    ## sort center upper nodes ###########################################
    K = len(cnode.Node)
    
    center = [-1102, 0.0, 0.0, 0.0]
    center[x] = (tmin + tmax)/2
    center[y] = cy
    cx = center[x]
    
    vertical = [-1, 0.0, 0.0, 0.0]
    vertical[x] = center[x] 
    
    for a in range(270, 360):
        ra = math.radians(float(a))
        min = 10000000.0
        f =0
        for i in range(K):
            if cnode.Node[i][x] > cx:
                vertical[y] = cy + 1.0
                angle = CalculateAngleFrom3Node(vertical, cnode.Node[i], center, XY=XY)
            else:
                vertical[y] = cy - 1.0
                angle = math.pi + CalculateAngleFrom3Node(vertical, cnode.Node[i], center, XY=XY) 
            
            if (angle-ra) > 0 and abs(angle-ra) < math.pi/180.0 and min> (angle-ra):
                min = (angle-ra)
                nearnode = cnode.Node[i]
                f =1
        if f == 1:
            j = len(boundary.Node)
            if j == 0:
                boundary.Add(nearnode)
            elif nearnode[x] != boundary.Node[j-1][x] and nearnode[y] != boundary.Node[j-1][y]:
                boundary.Add(nearnode)
            
    for a in range(0, 90):
        ra = math.radians(float(a))
        min = 10000000.0
        f=0
        for i in range(K):
            if cnode.Node[i][x] > cx:
                vertical[y] = cy + 1.0
                angle = CalculateAngleFrom3Node(vertical, cnode.Node[i], center, XY=XY)
            else:
                vertical[y] = cy - 1.0
                angle = math.pi + CalculateAngleFrom3Node(vertical, cnode.Node[i], center, XY=XY) 
            
            if (angle-ra) > 0 and abs(angle-ra) < math.pi/180.0 and min> (angle-ra):
                min = (angle-ra)
                nearnode = cnode.Node[i]
                f=1
        if f == 1:
            j = len(boundary.Node)
            if j == 0:
                boundary.Add(nearnode)
            elif nearnode[x] != boundary.Node[j-1][x] and nearnode[y] != boundary.Node[j-1][y]:
                boundary.Add(nearnode)
            
    ## end of the left nodes sorting ###########################################   

    ## sort right nodes ###########################################
    K = len(rnode.Node)
    
    center = [-1103, 0.0, 0.0, 0.0]
    center[x] = ( rlim[x]+ 3*tmax)/4
    center[y] = cy
    cx = center[x]
    
    vertical = [-1, 0.0, 0.0, 0.0]
    vertical[x] = center[x] 
    
    for a in range(270, 360):
        ra = math.radians(float(a))
        min = 10000000.0
        f=0
        for i in range(K):
            if rnode.Node[i][x] > cx:
                vertical[y] = cy + 1.0
                angle = CalculateAngleFrom3Node(vertical, rnode.Node[i], center, XY=XY)
            else:
                vertical[y] = cy - 1.0
                angle = math.pi + CalculateAngleFrom3Node(vertical, rnode.Node[i], center, XY=XY) 
            
            if (angle-ra) > 0 and (angle-ra) < math.pi/180.0 and min> (angle-ra):
                min = (angle-ra)
                nearnode = rnode.Node[i]
                f=1
        if f == 1:
            j = len(boundary.Node)
            if j == 0:
                boundary.Add(nearnode)
            elif nearnode[x] != boundary.Node[j-1][x] and nearnode[y] != boundary.Node[j-1][y]:
                boundary.Add(nearnode)
            
    for a in range(0, 270):
        ra = math.radians(float(a))
        min = 10000000.0
        f=0
        for i in range(K):
            if rnode.Node[i][x] > cx:
                vertical[y] = cy + 1.0
                angle = CalculateAngleFrom3Node(vertical, rnode.Node[i], center, XY=XY)
            else:
                vertical[y] = cy - 1.0
                angle = math.pi + CalculateAngleFrom3Node(vertical, rnode.Node[i], center, XY=XY) 
            
            if (angle-ra) > 0 and (angle-ra) < math.pi/180.0 and min> (angle-ra):
                min = (angle-ra)
                nearnode = rnode.Node[i]
                f=1
        if f == 1:
            j = len(boundary.Node)
            if j == 0:
                boundary.Add(nearnode)
            elif nearnode[x] != boundary.Node[j-1][x] and nearnode[y] != boundary.Node[j-1][y]:
                boundary.Add(nearnode)
            
    ## end of the left nodes sorting ###########################################   
    
    ## sort center lower nodes ###########################################
    K = len(cnode.Node)
    
    center = [-1104, 0.0, 0.0, 0.0]
    center[x] = (tmin + tmax)/2
    center[y] = cy
    cx = center[x]
    
    vertical = [-1, 0.0, 0.0, 0.0]
    vertical[x] = center[x] 
    
    for a in range(90, 270):
        ra = math.radians(float(a))
        min = 10000000.0
        f = 0
        for i in range(K):
            if cnode.Node[i][x] > cx :
                vertical[y] = cy + 1.0
                angle = CalculateAngleFrom3Node(vertical, cnode.Node[i], center, XY=XY)
            else:
                vertical[y] = cy - 1.0
                angle = math.pi + CalculateAngleFrom3Node(vertical, cnode.Node[i], center, XY=XY) 
                            
            if (angle-ra) > 0 and abs(angle-ra) < math.pi/180.0 and min> (angle-ra):
                min = (angle-ra)
                nearnode = cnode.Node[i]
                f =1
                 
        if f == 1:
            j = len(boundary.Node)
            if j == 0:
                boundary.Add(nearnode)
            elif nearnode[x] != boundary.Node[j-1][x] and nearnode[y] != boundary.Node[j-1][y]:
                boundary.Add(nearnode)
    
            
    ## end of the left nodes sorting ###########################################   
    
    if clockwise != 1:
        I = len(boundary.Node) 
        II = int(I/2)
        for i in range(II):
            tmp = boundary.Node[i]
            boundary.Node[i]= boundary.Node[I-1-i]
            boundary.Node[I-1-i] = tmp
        
        
    if image != 0:
        boundary.ImageLine(file, XY=XY)
        # Node.ImageLine(file+"b", XY=XY)
    
    return boundary

def RibBoundary(Node, XY=21, Offset = 10000, image=0, file="Boundary", clockwise=1, **args):
    for key, value in args.items():
        if key == 'xy':
            XY = int(value)
        if key == 'offset':
            Offset = int(value)
        if key == 'Clockwise':
            clockwise = int(value)
        if key == 'Image':
            image=int(value)
    pass
    #### not good program 
    x=int(XY/10)
    y=int(XY)%10
    
    I = len(Node.Node)
    
    ymax=xmax = -100000000000000.0
    ymin=xmin = 100000000000000.0

    for i in range(I):
        if xmax < Node.Node[i][x]:
            xmax = Node.Node[i][x]
        if ymax < Node.Node[i][y]:
            ymax = Node.Node[i][y]
            
        if xmin > Node.Node[i][x]:
            xmin = Node.Node[i][x]
        if ymin > Node.Node[i][y]:
            ymin = Node.Node[i][y]
            
    cx = (xmax+xmin)/2.0
    cy = (ymax+ymin)/2.0
    
    center = [0, 0.0, 0.0, 0.0]
    center[x] = cx
    center[y] = cy
    
    vertical = [-1, 0.0, 0.0, 0.0]
    vertical[x] = cx 
    tmp=NODE()
    for i in range(I):
        
        if Node.Node[i][x] > cx:
            vertical[y] = cy + 1.0
            x1 = vertical[x] - center[x];      y1 = vertical[y] - center[y]
            x2 = Node.Node[i][x] - center[x];  y2 = Node.Node[i][y] - center[y]
            l2 = math.sqrt(x2*x2 + y2*y2)
            if l2 == 0:
                continue
            try:
                angle = math.acos(round((x1*x2+y1*y2)/(l2), 10))
            except:
                print ("ERROR :: Value is not in -1.0 ~ 1.0 : ", round((x1*x2+y1*y2)/(l2), 10))
                
                sys.exit()
        else:
            vertical[y] = cy - 1.0
            x1 = vertical[x] - center[x];      y1 = vertical[y] - center[y]
            x2 = Node.Node[i][x] - center[x];  y2 = Node.Node[i][y] - center[y]
            l2 = math.sqrt(x2*x2 + y2*y2)
            if l2 == 0:
                continue
            try:
                angle = math.acos(round((x1*x2+y1*y2)/(l2), 10))
            except:
                print ("ERROR :: Value is not in -1.0 ~ 1.0 : ", round((x1*x2+y1*y2)/(l2), 10))
                sys.exit()
        angle = angle*180.0/math.pi
        tmp.Add([Node.Node[i][0], Node.Node[i][1], Node.Node[i][2], Node.Node[i][3], l2, angle])
    
    
    
    boundary = NODE()
    I = len(tmp.Node)
    for a in range(360):
        max = 0.0
        fn = []
        for i in range(I):
            if tmp.Node[i][5]>=float(a) and tmp.Node[i][5] < float(a+1):
                if tmp.Node[i][4] > max:
                    max = tmp.Node[i][4]
                    fn = tmp.Node[i]
        if len(fn)>0:
            boundary.Add(fn)
            
    # boundary.Image(XY=XY, size=5)
    
    if clockwise != 1:
        I = len(boundary.Node) 
        II = int(I/2)
        for i in range(II):
            tmp = boundary.Node[i]
            boundary.Node[i]= boundary.Node[I-1-i]
            boundary.Node[I-1-i] = tmp
            
    if image != 0:
        boundary.ImageLine(file, XY=XY)
        Node.ImageLine(file+"b", XY=XY)
    
    del(tmp)
    
    return boundary        
    
def Innerpoints(dots, E, N, XY=21, vmin='', vmax='', **args):
    for key, value in args.items():
        if key == 'xy':
            XY = int(value)

    return ValueInterpolation(dots, E, N, xy=XY)

    
def SearchFootshapeBoundary(Node, XY=21, g=1.0, file='boundary', fxy='', image=0, **args):
    for key, value in args.items():
        if key == 'xy':
            XY = int(value)
        if key == 'G' or key == 'gap' or key == 'Gap':
            g = float(value)
            

    x = int(XY/10)
    y = int(XY)%10
    if fxy == '':
        fxy = XY
    
    fx = int(fxy/10)
    fy = int(fxy)%10
    
    if x != fx or y != fy:
        x = fx
        y = fy
    
    g=g/1000.0
    
    bnode = NODE()
    I = len(Node.Node)
    
    nodelist =[]
    for i in range(I):
        nodelist.append(Node.Node[i][0])
        nodelist.append(Node.Node[i][x])
        nodelist.append(Node.Node[i][y])
        
    tuplenode = tuple(nodelist)
    
    tuplevalue=_islm.SectionLimit(tuplenode, g)
    
    I = len(tuplevalue)
    
    
        
    for i in range(int(I/4)):
        bnode.Add([int(tuplevalue[i*4]), 0.0, 0.0, 0.0, 0])
        bnode.Node[i][x]= tuplevalue[i*4+1]
        bnode.Node[i][y]= tuplevalue[i*4+2]
        bnode.Node[i][4]= int(tuplevalue[i*4+3])
    
    if image == 1:
        bnode.Image(file, XY=XY)
        
    return bnode
        
    
def ConvexHull(oNode, XY=23, **args):
    for key, value in args.items():
        if key == 'xy':
            XY = int(value)
            
    x=int(XY/10); y = int(XY)%10
    I = len(oNode.Node)
    node=NODE()
    for i in range(I):
        node.Add([oNode.Node[i][0], oNode.Node[i][1], oNode.Node[i][2], oNode.Node[i][3]])
    SortedNode=NODE()
    if len(oNode.Node) == 0:
        return SortedNode
        
    min = 10000000000000.0
    nmin = 0
    max = -100000000000.0
    
    for i in range(I):
        if node.Node[i][y] < min:
            min = node.Node[i][y]
            tNode = node.Node[i]
        if node.Node[i][y] > max:
            max = node.Node[i][y]
            mNode = node.Node[i]
    SortedNode.Add(tNode)
    
    Center = tNode
          
    nmax = 0
    pangle = 0.0
    stopangle = math.pi*(2 - 1.0/180.0)
    
    for i in range(I):
        
        mAngle = 10000.0
                         
        for j in range(I):
            if Center[0] != node.Node[j][0]:
                N1 = [Center[0], Center[1], Center[2], Center[3]]
                N1[x]+= 1.0
                N2 = node.Node[j]
                if Center[y]<N2[y] :
                    angle = CalculateAngleFrom3Node(N1, N2, Center, XY=XY)
                else:
                    angle = math.pi * 2 - CalculateAngleFrom3Node(N1, N2, Center, XY=XY) 
                
                if mAngle > angle and angle >= pangle:
                    tCenter = N2
                    mAngle = angle
        
        if SortedNode.Node[0][0] == tCenter[0]:
            break
        if angle > stopangle: 
            break
            
        SortedNode.Add(tCenter)
        Center = tCenter
        pangle = mAngle
    
                                  
    return SortedNode
  
def Contacttreadsurface(pnode,  el3d , slist=[]):
    
    I = len(pnode.Node)
    ni = len(pnode.Node[0])
    p = []
    for i in range(I):
        for j in range(ni):
            p.append(pnode.Node[i][j])
    if len(slist) > 0:
        I = len(slist)
        s = []
        for i in range(I):
            s.append( slist[i][0])
            s.append( slist[i][1])
    else:
        sf = el3d.Surface()
        I = len(sf.Surface)
        s = []
        for i in range(I):
            s.append( sf.Surface[i][4])
            s.append( sf.Surface[i][5])
    I = len(el3d.Element)
    e = []
    J = len(el3d.Element[0])
    for i in range(I):
        for j in range(J):
            e.append( el3d.Element[i][j] )
            
    tp = tuple(p)
    ts = tuple(s)
    te = tuple(e)
    t1 = time.time()
    r = _islm.Contacttreadsurface(tp, ts, te, ni, 2, J)
    t2 = time.time()
    
    I = len(r)
    surface = SURFACE()
    for i in range(int(I/7)):
        surface.Add([int(r[i*7]), int(r[i*7+1]), int(r[i*7+2]), int(r[i*7+3]), int(r[i*7+4]), int(r[i*7+5]), int(r[i*7+6])])
    
    # print "Road contact Surface : ", t2 - t1, "second"
    
    return surface
def Nodeids( sets,  type=''):
    ## in the surface or elements 
    tl = []
    if type == 'surface':
        tcol = tuple([0, 1,2,3])
        I = len(sets.Surface)
        s = len(sets.Surface[0])
        for i in range(I):
            for j in range(s):
                tl.append(sets.Surface[i][j])
        ttl = tuple(tl)
        r = _islm.ListIds(tcol, ttl, s)

    elif type == 'element':
        tcol = tuple([1,2,3,4])
        I = len(sets.Element)
        s = len(sets.Element[0])
        for i in range(I):
            for j in range(s):
                if sets.Element[i][j] == '':
                    sets.Element[i][j] = 0
                tl.append(sets.Element[i][j])
        ttl = tuple(tl)
        r = _islm.ListIds(tcol, ttl, s)
    elif type == 'element3d':
        tcol = tuple([1,2,3,4, 5, 6, 7, 8])
        I = len(sets.Element)
        s = len(sets.Element[0])
        for i in range(I):
            for j in range(s):
                if sets.Element[i][j] == '':
                    sets.Element[i][j] = 0
                tl.append(sets.Element[i][j])
        ttl = tuple(tl)
        r = _islm.ListIds(tcol, ttl, s)
        
        return r
        
     

##//////////////////////////////////////
########################################
## Extract Results from SMART Files
########################################
def ResultSDB(strSDB, strResultSDB, offset, treadno, ResultItem, ResultOption):
    ## ResultItem 
    ## 1 : Node Coordinates / temperature, return NODE()=[Node ID, X1, X2, X3, Temperature]
    ## 2 : Solid Elements - Strain Energy Density, return List = [Element ID, SED]
    ## 3 : Solid Elements - Heat Generation Rate,  return List = [Element ID, Heat Generation Value]
    ## 4 : Membrane Elements - Heat Generation Rate, return List = [Element ID, Heat Generation Value]
    ## 5 : Membrane Elements - Rebar EPI, Angle, return List = [Element ID, Initial EPI, Final EPI, Initial Angle, Final Angle]
    ## 6 : Membrane Elements - Rebar Strain/Force/Stress, return List = [Element ID, Rebar Strain, Rebar Force, Rebar Stress]
    ## 7 : Rim / Drum Node Coordinates [[Drum/Road Node ID, x1, x2, x3], [Rim Node ID, x1, x2, x3]]
    ## Result Option 
    ##   0 : All nodes/elements, -1 : Top Section Nodes/ Elements, -2 : Value average with top section nodes / elements, bottom :-3 
    results = _islm.ResultSDB(strSDB, strResultSDB, offset, treadno, ResultItem, ResultOption)

    if ResultItem == 1 or ResultItem == 0 or ResultItem == 7:
        # if ResultItem == 7: print ("result", results)
        rnode = NODE()
        I = len(results)
        for i in range(I):
            rnode.Add(results[i])
        return rnode
    else:
        return results 
def ResultSFRIC(strSFRIC, strResultSFRIC, offset, treadno, ResultItem, ResultOption):
    ## ResultItem 
    ## 1 : Contact Force, return NODE()=[Node ID, X1, X2, X3, X1 Force, X2 Force, X3 Force, Force magnitude]
    ## 2 : Contact Stress,  return NODE()=[Node ID, X1, X2, X3, X1 Stress, X2 stress, X3 Stress, Stress magnitude]
    ## 3 : Wear rate, return NODE() = [Node ID, X1, X2, X3, Wear Rate, Friction Coefficient, Slip Flag]
    ## 4 : Friction Energy, return NODE() = [Node ID, X1, X2, X3, Friction Energy X, Friction Energy Y, Friction Energy Z, Friction Energy Sum]
    ## 5 : Friction Energy Accumulated, return NODE() = [Node ID, X1, X2, X3, Friction Energy X, Friction Energy Y, Friction Energy Z, Friction Energy Sum]
    ## 6 : Slip Velocity, return NODE() = [Node ID, X1, X2, X3, Slip Velocity X, Slip Velocity Y, Slip Velocity Z, , Slip Velocity Magnitude]
    ## 7 : Node Temperature, Nodal Area, Nodal Area Projection Ratio, return NODE() = [Node ID, x1, x2, x3, Node Temperature, Nodal Area, Area Projection Ratio]
    ## Result Option 
    ##   0 : All nodes/elements, -1 : Top Section Nodes/ Elements, -2 : Value average with top section nodes / elements 
    results = _islm.ResultSFRIC(strSFRIC, strResultSFRIC, offset, treadno, ResultItem, ResultOption)

    rnode = NODE()
    I = len(results)
    for i in range(I):
        rnode.Add(results[i])
    return rnode


def SDBResults(strSDBFileName, sdbResultFileName, ResultItem, ResultSector, NodeOffset=10000, ElementOffset=10000, TreadStartNo=10000000, **args):
    for key, value in args.items():
        if key == 'nodeoffset' or key == 'Nodeoffset':
            NodeOffset = int(value)
        if key == 'elementoffset' or key == 'Elementoffset':
            ElementOffset = int(value)
        if key == 'Treadstartno' or key == 'treadno' or key == 'Treadno' or key == 'treadstartno' or key == 'TreadNo':
            TreadStartNo = int(value)
            
    # result item
    # 1 : Dimension (OD, SW) + Carcass/Belt Tension)
    # 2 : Nodal Temperature
    # 3 : Heat Analysis
    # 4 : Strain Energy Density
    # 5 : Rebar EPI/Angle Information
    # 6 : Rebar Force/Stress/Strain
    # Belt Node Position on the Uppermost sector

    # print " From", sdbResultFileName
    # if ResultItem == 1:
        # print " Coordinates of the nodes and Tire Dimension and Cord Tension "
    # elif ResultItem == 2:
        # print " Temperature at nodes"
    # elif ResultItem == 3:
        # print " Energy Loss Generation Rate(W/Vol)"
    # elif ResultItem == 4:
        # print " Strain Energy Density (J/Vol)"
    # elif ResultItem == 5:
        # print " Rebar EPI / Angle"
    # elif ResultItem == 6:
        # print " Rebar Strain / Force /Stress "

    # if ResultSector == 0:
        # print " For All Nodes", "Offset No.: ", NodeOffset, "Tread Node :", TreadStartNo
    # elif ResultSector > 1000:
        # print " Uppermost Section", "Offset No.: ", NodeOffset, "Tread Node :", TreadStartNo
    # else:
        # print " ResultSector : ", ResultSector, "Offset No.: ", NodeOffset, "Tread Node :", TreadStartNo
        
    i = _islm.ResultFromSDB(strSDBFileName, sdbResultFileName, ResultItem, ResultSector, NodeOffset, ElementOffset, TreadStartNo)
    if i == 0:
        print ("ERROR!! TO READ SDB FILE or You have the wrong Result ITEM")
    else:
        if ResultItem == 1:
            print (" Dimension Result Done.")
            # print " Result : SIM_CODE-NodePosition.tmp"
            # print "   Node ID, Org X, Org Y, Org Z, Del X, DelY, Del Z"
            # print "ISLM Result : SIM_CODE-DimValue.txt"
            # print "   Initial OD=%.2f"
            # print "   Initial SW=%.2f"
            # print "   Deformed OD =%.2f"
            # print "   Deformed SW =%.2f"
            # print " ISLM Result : SIM_CODE-CordTensionValue.txt"
            # print "   BTi"
            # print "   Element ID, Cord Tension(N), Element Length(mm), Node 1 ID, Node 1 Deformed X,  Y, Z, Node 2 ID, Node 2 Deformed X, Y, Z"
            # print "   C0i"
            # print "   Element ID, Cord Tension(N), Element Length(mm), Node 1 ID, Node 1 Deformed X,  Y, Z, Node 2 ID, Node 2 Deformed X, Y, Z"

        elif ResultItem == 2:
            print (" Nordal Temperature Result Done.")
            # print " Result : SIM_CODE-NodeTemperature.tmp"
            # print " if ResultSector == 0"
            # print "     NodeID, Node Temperature, Deformed_X, Deformed_Y, Deformed_Z, CutSection_X, CutSection_Y, CutSection_Z, Angle Between Vertical Line"
            # print "     [angle.tmp] : Deformed Coordinates for drawing Circumferential Shape"
            # print "     Deforded_X, Deformed_Z, Angle"
            # print " else"
            # print "     NodeID, Node Average Temperature, Section Node Deformed X, Y, Z, CutSection_X, CutSection_Y, CutSection_Z"
        elif ResultItem == 3:
            print (" Heat Anlysis Result Done.")
            # print " Result : SIM_CODE-EnergyLoss.tmp"
            # print "  *Energy Uniform Loss Generation Rate"
            # print "   ElementID, Energy Loss Generation Rate"
            # print "  *Energy Hourglass Loss Generation Rate"
            # print "   ElementID, Energy Loss Generation Rate"
            # print "  *Rebar Energy Uniform Loss Generation Rate"
            # print "   ElementID, Energy Loss Generation Rate"
            # print "  *Rebar Energy Hourglass Loss Generation Rate"
            # print "   ElementID, Energy Loss Generation Rate"

        elif ResultItem == 4:
            print (" Strain Energy Density Result Done.")
            # print " Result : SIM_CODE-StranEnergyDensity.tmp"
            # print "   *StrainEnergyUniformDensity(J/Vol)"
            # print "   Element ID, StrainEnergy Energy Density "
            # print "   *StrainEnergyHourglassDensity(J/Vol)"
            # print "   Element ID, StrainEnergy Energy Density "
        elif ResultItem == 5:
            print (" Rebar EPI/Angle Result Done.")
            # print " Result : SIM_CODE-RebarAngleEPI.tmp"
            # print "  *Original Rebar EPI  (BT1~3, C01,C02)"
            # print "  BTi, Element ID, Original EPI"
            # print "  C0i, Element ID, Original EPI"
            # print "  *Original Rebar Angle  (BT1~3, C01,C02)"
            # print "  BTi, Element ID, Original Angle"
            # print "  C0i, Element ID, Original Angle"
            # print "  *Delta Rebar EPI  (BT1~3, C01,C02)"
            # print "  BTi, Element ID, Delta EPI"
            # print "  C0i, Element ID, Delta EPI"
            # print "  *Delta Rebar Angle  (BT1~3, C01,C02)"
            # print "  BTi, Element ID, Delta Angle"
            # print "  C0i, Element ID, Delta Angle"
        elif ResultItem == 6:
            print (" Rebar Force/Strain/Stress Result Done.")
            # print " Result : SIM_CODE-RebarForce.tmp"
            # print "   *Rebar Strain"
            # print "   BTi, Element ID, Rebar Strain"
            # print "   C0i, Element ID, Rebar Strain"
            # print "   *Rebar Force"
            # print "   BTi, Element ID, Rebar Force"
            # print "   C0i, Element ID, Rebar Force"
            # print "   *Rebar Stress"
            # print "   BTi, Element ID, Rebar Stress"
            # print "   C0i, Element ID, Rebar Stress"

        elif ResultItem == 7:
            # print " Result : SIM_CODE-DynamicProfileBeltCoord.tmp"
            # print "*BT1 or BT2 Deformed Coordinates in the Uppermost Sector(Node No, X = 0, Y, Z, Origin X, Y, Z, Del X, Y, Z)"
            print (" Belt Node Position on the Uppermost sector(Dynamic Profile).")
    
def SFRICResults(strSFRICFileName, sfricResultFileName, ResultItem, ResultSector, NodeOffset=10000, TreadStartNo=10000000, **args):
    for key, value in args.items():
        if key == 'nodeoffset' or key == 'Nodeoffset':
            NodeOffset = int(value)
        # if key == 'elementoffset' or key == 'Elementoffset':
            # ElementOffset = int(value)
        if key == 'Treadstartno' or key == 'treadno' or key == 'Treadno' or key == 'treadstartno' or key == 'TreadNo':
            TreadStartNo = int(value)
            
    # print " From", sfricResultFileName
    
    # if ResultItem == 1:
        # print " Coordinates of the nodes on Outer Edges"
    # elif ResultItem == 2:
        # print " Temperature at nodes on Outer Edges"
    # elif ResultItem == 3:
        # print " Nodal Area"
    # elif ResultItem == 4:
        # print " Friction Energy Rate"
    # elif ResultItem == 5:
        # print " Slip Velocity"
    # elif ResultItem == 6:
        # print " Fiction Coefficient"
    # elif ResultItem == 7:
        # print " Contact Shear Force"
    # elif ResultItem == 71:
        # print " Only Contact Normal Force"
    # elif ResultItem == 8:
        # print " Contact Shear Stress"
    # elif ResultItem == 81:
        # print " Only Contact Normal Pressure"
    # elif ResultItem == 9:
        # print " Friction Energy Accumulated"
    # elif ResultItem == 10:
        # print " Wear Rate"

    if ResultSector == 0:
        # print " For All Nodes", "Offset No.: ", NodeOffset, "Tread Node :", TreadStartNo
        pass
    # else:
        # print " ResultSector : ", ResultSector, "Offset No.: ", NodeOffset, "Tread Node :", TreadStartNo
    # print TreadStartNo
    # print NodeOffset
    i = _islm.ResultFromSFRIC(strSFRICFileName, sfricResultFileName, ResultItem, ResultSector, NodeOffset, TreadStartNo)
    if i == 0:
        print ("ERROR!! TO READ SFRIC FILE or You have the wrong Result ITEM")
    else:
        if ResultItem == 1:
            print (" Surface Dimension Result Done. (Dynamic Profile) ")
            # print " Result file : SIM_CODE-SurfaceNodePosition.tmp, SIM_CODE-SurfaceNodePosition1.tmp"
            # print " **** SurfaceNodePosition.tmp"
            # print " NodeID, Org_X, Org_Y, Org_Z, Del_X, Del_Y, Del_Z"
            # print " **** SurfaceNodePosition1.tmp : Uppermost Outer profile"
            # print " EdgeID, Node1, Node2, N1_0.0, N1_Deformed_Y, N1Deformed_Z, N2_0.0, N2_Deformed_Y, N2_Deformed_Z, Outer_Edge, Over_RimFlange"
        elif ResultItem == 2:
            print (" Surface Node Temperature Result Done.")
            # print " Result file : SIM_CODE-SurfaceNodeTemperature.tmp"
            # print " NodeID, Temperature"
        elif ResultItem == 3:
            print (" Nodal Area Done.")
            # print " Result file : SIM_CODE-NodalArea.tmp"
            # print " NodeID, NodalArea, NodalArea_Projected_Ratio"
        elif ResultItem == 4:
            print (" Friction Energy Rate Done.")
            # print " Result file : SIM_CODE-FrictionEnergyRate.tmp"
            # print " NodeID, FrictionEnergy_Sum, FrictionEnergy_X, FrictionEnergy_Y, FrictionEnergy_Z"
        elif ResultItem == 5:
            print (" Slip Velocity Done.")
            # print " Result file : SIM_CODE-SlipVelocity.tmp"
            # print " NodeID, Slip_Velocity_magnitude, Slip_Velocity_X, Slip_Velocity_Y, Slip_Velocity_Z"
        elif ResultItem == 6:
            print (" Friction Coefficient Done.")
            # print " Result file : SIM_CODE-FricCoefficient.tmp"
            # print " NodeID, SlipFlag, Fiction_Coefficient"
        elif ResultItem == 7:
            print (" Contact Shear Force Done.")
            # print " Result file : SIM_CODE-ContactShearForce.tmp"
            # print " NodeID,   Contact_Force_Magnitude,  ContactForce_X,  ContactForce_Y,  ContactForce_Z"
        elif ResultItem == 71:
            print (" Contact Normal Force Only Done.")
            # print " Result file : SIM_CODE-ContactForce.tmp, SIM_CODE-TreadContactForce.tmp"
            # print " ** SIM_CODE-ContactForce.tmp "
            # print " NodeID, NormalContactForce, Deformed_X, Deformed_Y, Deformed_Z"
            # print " ** SIM_CODE-TreadContactForce.tmp "
            # print " Deformed_Y(Lateral), Deformed_X(TravelDirection), NormalContactForce, NodalArea"
        elif ResultItem == 8:
            print (" Contact Shear Stress Done.")
            # print " Result file : SIM_CODE-ContactShearStress.tmp"
            # print " NodeID,   Contact_Stress_Magnitude,  ContactForce_X,  ContactForce_Y,  ContactForce_Z"
        elif ResultItem == 81:
            print (" Contact Pressure (Normal) Only Done.")
            # print " Result file : SIM_CODE-ContactStress.tmp, SIM_CODE-TreadContactPressure.tmp"
            # print " ** SIM_CODE-ContactStress.tmp "
            # print " NodeID, NormalContactStress, Deformed_X, Deformed_Y, Deformed_Z"
            # print " ** SIM_CODE-TreadContactPressure.tmp "
            # print " Deformed_Y(Lateral), Deformed_X(TravelDirection), NormalContactPressure, NodalArea"
        elif ResultItem == 9:
            print (" Friction Energy Accumulated Done.")
            # print " Result file : SIM_CODE-FricEnergyAccumulated.tmp"
            # print " NodeID, FrictionEnergy_AccumulatedSum, FrictionEnergy_Accumulated_X, FrictionEnergy_Accumulated_Y, FrictionEnergy_Accumulated_Z"
        elif ResultItem == 10:
            # print " Result file : SIM_CODE-Wear.tmp"
            # print " NodeID, WearRate"
            print (" Wear Results Done.")

def GetDeformedNodeFromSDB(strSimCode, SectorNo, Step=0, Offset= 10000, TreadNo = 10000000, **args):
    
    """
    :param NodeFile: Results from SDB Result File (*-NodePosition.tmp or Simulation Code)
    :param SectorNo: 0 - all nodes, n = nth sector, 1001 : uppermost node
    :param Offset: default 10000
    :param TreadNo: default 10000000
    :return:
    """
    lastsdb = 0
    SimTime = ''
    strJobDir = ''
    for key, value in args.items():
        if key == 'offset' :            Offset = int(value)
        if key == 'step' :            Step = int(value)
        if key == 'Treadstartno' or key == 'treadno' or key == 'Treadno' or key == 'treadstartno':
            TreadNo = int(value)
        if key == "lastsdb":            lastsdb = value
        if key == 'simtime':            SimTime = value
        if key == 'jobdir':            strJobDir = value

    if SimTime =="":           SimTime = SIMTIME(strSimCode+'.inp')
    if strJobDir == '':        strJobDir = os.getcwd()

    if lastsdb != 0:
        strLastSDBFile = strSimCode
        sdbFileName = strLastSDBFile[:-3]
    else:
        if SimTime.SimulationTime == 0.0:
            sdbFileName = strJobDir + '/' + 'SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
        else:
            sdbFileName = strJobDir + '/' + 'SDB.' + strSimCode + '/' + strSimCode + '.sdb'
        if Step == 0: 
            strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSDBFile =  sdbFileName + str(format(Step, '03'))
    
        if SectorNo > 1000: SectorNo = -1
    DeformedNode = ResultSDB(sdbFileName, strLastSDBFile, Offset,  TreadNo, 1, SectorNo)

    # RimNode  = GetRimCenter(rimfile=strJobDir+'/rigid.tmp')
    RimNode = GetRimCenter(lastsdb=strLastSDBFile)
    I = len(DeformedNode.Node)
    for i in range(I):
        DeformedNode.Node[i][1] -= RimNode.Node[0][1]
        DeformedNode.Node[i][2] -= RimNode.Node[0][2]
        DeformedNode.Node[i][3] -= RimNode.Node[0][3]
    return DeformedNode


def GetDeformedPatternNodeFromSDB(strSimCode, SectorNo, Step=0, Offset= 10000, TreadNo = 10000000, **args):
    
    """
    :param NodeFile: Results from SDB Result File (*-NodePosition.tmp or Simulation Code)
    :param SectorNo: 0 - all nodes, n = nth sector, 1001 : uppermost node
    :param Offset: default 10000
    :param TreadNo: default 10000000
    :return:
    """
    
    for key, value in args.items():
        if key == 'offset' :
            Offset = int(value)
        if key == 'step' :
            Step = int(value)
        if key == 'Treadstartno' or key == 'treadno' or key == 'Treadno' or key == 'treadstartno':
            TreadNo = int(value)
    
    if len(list(strSimCode.split('/'))) > 1:
        SimTime = SIMTIME(strSimCode+'.inp')
        
        strJobDir = os.getcwd()
        word = list(strSimCode.split('/'))
        I = len(word)
        DeformedNodeFileName = ''
        strWorkDir = ''
        for i in range(I):
            if i < I-1:
                strWorkDir += word[i] + '/'
            if i < I-2:
                DeformedNodeFileName += word[i] + '/'
            SimCode = word[i]
        
        DeformedNodeFileName = DeformedNodeFileName + SimCode + '-NodePosition.tmp'
        
        # print "*********", strWorkDir
        # print "*********", DeformedNodeFileName
        
        if SimTime.SimulationTime == 0.0:
            sdbFileName = strWorkDir + 'SDB_PCI.' + SimCode + '/' + SimCode + '.sdb'
        else:
            sdbFileName = strWorkDir + 'SDB.' + SimCode + '/' + SimCode + '.sdb'
        if Step == 0: 
            strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSDBFile =  sdbFileName + str(format(Step, '03'))
        # print "*********", sdbFileName
        # print "*********", strLastSDBFile
        #######################################################################
        SDBResults(sdbFileName, strLastSDBFile, 1, 0, Offset, Offset, TreadNo)
        #######################################################################
        
    else: 
        strJobDir = os.getcwd()
        SimTime = SIMTIME(strSimCode+'.inp')
        DeformedNodeFileName = strJobDir + '/' + strSimCode + '-NodePosition.tmp'
        if SimTime.SimulationTime == 0.0:
            sdbFileName = strJobDir + '/' + 'SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
            
        else:
            sdbFileName = strJobDir + '/' + 'SDB.' + strSimCode + '/' + strSimCode + '.sdb'
        if Step == 0: 
            strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSDBFile =  sdbFileName + str(format(Step, '03'))
        #######################################################################
        SDBResults(sdbFileName, strLastSDBFile, 1, 0, Offset, Offset, TreadNo)
        #######################################################################
    # print "################",DeformedNodeFileName
    UmostSector = 0
    RimNode  = GetRimCenter(lastsdb=strLastSDBFile)
    DeformedNode = NODE()
    with open(DeformedNodeFileName) as InpFile:
        lines = InpFile.readlines()
    c= 0
    MaxZ = 0.0
    MaxN = 0
    X = 0.0
    for line in lines:
        data = list(line.split(','))
        c += 1
        if data[0][0] == '\n' or data[0][0] == '*':
            pass
        else:
            id= int(data[0].strip())
            x = float(data[1].strip())
            dX = float(data[4].strip())
            y =  float(data[2].strip())
            dY = float(data[5].strip())
            z =  float(data[3].strip())
            dZ = float(data[6].strip())

            X = x + dX - RimNode.Node[0][1]
            Y = y + dY - RimNode.Node[0][2]
            Z = z + dZ - RimNode.Node[0][3]
            
            DeformedNode.Add([id, X, Y, Z])
    return DeformedNode


def GetDeformedNodeFromSFRIC(strSimCode, SimTime, ResultSector =0, Step=0, Offset=10000, TreadNo = 10000000, **args):

    for key, value in args.items():
        if key == 'step':
            Step = int(value)
        if key == 'offset':
            Offset = int(value)
        if key == 'Treadstartno' or key == 'treadno' or key == 'Treadno' or key == 'treadstartno' or key == 'TreadStartNo':
            TreadNo = int(value)
        if key == 'resultsector' or key == 'sector':
            ResultSector = int(value)
    # print " **** SurfaceNodePosition.tmp"
            # print " NodeID, Org_X, Org_Y, Org_Z, Del_X, Del_Y, Del_Z"

    
    if '-SurfaceNodePosition.tmp' in strSimCode:
        DeformedNodeFileName = strSimCode
    elif len(list(strSimCode.split('/'))) > 1:
    
        ## strSimCode = ~./DOE/1017440VT00193-0/RND-1017440VT00193-0-D101-0001
        # print strSimCode
    
        word = list(strSimCode.split('/'))
        I = len(word)
        strJobDir = ''
        strWorkDir = ''
        for i in range(I):
            if i < I-1:
                strWorkDir += word[i] + '/'
            if i < I-2:
                strJobDir += word[i] + '/'
            SimCode = word[i]
        
        # DeformedNodeFileName = strJobDir + SimCode + '-SurfaceNodePosition.tmp'
        
        if SimTime.SimulationTime == 0.0:
            sfricFileName = strWorkDir + 'SFRIC_PCI.' + SimCode + '/' + SimCode + '.sfric'
        else:
            sfricFileName = strWorkDir + 'SFRIC.' + SimCode + '/' + SimCode + '.sfric'
        if Step == 0: 
            strLastSFRICFile =  sfricFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSFRICFile =  sfricFileName + str(format(Step, '03'))
        # print "SFRIC"    
        # print sfricFileName
        # print strLastSFRICFile
        SFRICResults(sfricFileName, strLastSFRICFile, 1, 0, Offset, TreadNo)
        DeformedNodeFileName = SimCode + '-SurfaceNodePosition.tmp'
        # print "######################", DeformedNodeFileName
    else: 
        strJobDir = os.getcwd()
        # SimTime = SIMTIME(strSimCode+'.inp')
        # DeformedNodeFileName = strJobDir + '/' + strSimCode + '-SurfaceNodePosition.tmp'
        if SimTime.SimulationTime == 0.0:
            sfricFileName = strJobDir + '/' + 'SFRIC_PCI.' + strSimCode + '/' + strSimCode + '.sfric'
            
        else:
            sfricFileName = strJobDir + '/' + 'SFRIC.' + strSimCode + '/' + strSimCode + '.sfric'
        if Step == 0: 
            strLastSFRICFile =  sfricFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSFRICFile =  sfricFileName + str(format(Step, '03'))
            
        # print "########", sfricFileName
        # print "########", strLastSFRICFile
        #######################################################################
        SFRICResults(sfricFileName, strLastSFRICFile, 1, 0, Offset, TreadNo)
        #######################################################################

        DeformedNodeFileName = strSimCode + "-SurfaceNodePosition.tmp"
        
    # print "FIND TOP"    
    with open(DeformedNodeFileName) as IN:
        lines = IN.readlines()
    # print "FIND TOP"
    Node = NODE()
    for line in lines : 
        if line[0] =="*":
            continue
        else:
            d=list(line.split(","))
            Node.Add( [ int(d[0].strip()), float(d[1].strip()) + float(d[4].strip()), float(d[2].strip()) + float(d[5].strip()), float(d[3].strip()) + float(d[6].strip()) ]  )
    # print "FIND TOP"        
    if ResultSector > 1000:
        # print "FIND TOP"
        I = len(Node.Node)
        max = -1000000000.0
        mid = 0
        for i in range(I):
            if Node.Node[i][3]> max:
                max = Node.Node[i][3]
                mid = Node.Node[i][0]
        if mid > TreadNo:
            mid -= TreadNo
        topsector = int(mid / Offset )
        
        # print "TOP=", topsector, mid
        
        topnode = NODE()
        for i in range(I): 
            if Node.Node[i][0] > Offset*topsector and Node.Node[i][0] < Offset*(topsector+1): 
                topnode.Add(Node.Node[i])
            if Node.Node[i][0] > Offset*topsector + TreadNo and Node.Node[i][0] <  Offset*(topsector+1) + TreadNo: 
                topnode.Add(Node.Node[i])
        del(Node)
        # print "TOP=", topsector, mid
        return topnode        
                
    else:
        return Node

def DeformedNode_SDB(lstSDB, angle=-1.0, sector=-1, Offset=10000, TreadNo=10000000, **args):
    camber = 0
    slip = 0
    for key, value in args.items():
        if key == 'offset':
            Offset = int(value)
        if key == 'Treadstartno' or key == 'treadno' or key == 'Treadno' or key == 'treadstartno' or key == 'TreadStartNo':
            TreadNo = int(value)
        if key == "angle":
            angle = value
        if key == "camber":
            camber = value
        if key == "slip" or key == "slipangle":
            slip = value

    sdb = lstSDB[:-3]
    node = ResultSDB(sdb, lstSDB, Offset, TreadNo, 1, 0)
    RimNode = GetRimCenter(lastsdb=lstSDB) 
    I = len(node.Node)   
    # bodynodeid =[]
    # treadnodeid = []
    for i in range(I):
        node.Node[i][1] -= RimNode.Node[0][1]
        node.Node[i][2] -= RimNode.Node[0][2]
        node.Node[i][3] -= RimNode.Node[0][3]
        # if node.Node[i][0]<Offset:
        #     bodynodeid.append(node.Node[i][0])
        # if node.Node[i][0] >= TreadNo and node.Node[i][0] < TreadNo + Offset:
        #     treadnodeid.apend(node.Node[i][0])
    if camber != 0.0:
        node.Rotate(camber, xy=23)
    if slip != 0.0:
        node.Rotate(-slip, xy=21)

    if angle >=0.0:
        Center = [0, 0.0, 0.0, 0.0]
        N1 = [-1, 0.0, 0.0, 1.0]
        tminangle = 9.9e10
        bminangle = 9.9E10
        bminnode = 0
        tminnode = 0
        for i in range(I):
            angle = CalculateAngleFrom3Node(N1, node.Node[i], Center, xy=13) * 180.0/math.pi
            node.Node[i].append(angle)
            if angle < tminangle and node.Node[i][0] >= TreadNo:
                tminangle = angle
                tminnode = node.Node[i][0]
            if bminangle > angle and node.Node[i][0] < TreadNo:
                bminangle = angle
                bminnode = node.Node[i][0]
        bsector = int(bminnode / Offset)
        tsector = int((tminnode-TreadNo)/Offset)
        Node=NODE()
        for i in range(I):
            if node.Node[i][0]>= bsector*Offset and node.Node[i][0] < (bsector+1)*Offset:
                Node.Add(node.Node[i])
            if node.Node[i][0]>= tsector*Offset + TreadNo and node.Node[i][0] < (tsector+1)*Offset + TreadNo:
                Node.Add(node.Node[i])
        return Node
    elif sector >=0:
        Node=NODE()
        for i in range(I):
            if node.Node[i][0]>= sector*Offset and node.Node[i][0] < (sector+1)*Offset:
                Node.Add(node.Node[i])
            if node.Node[i][0]>= sector*Offset + TreadNo and node.Node[i][0] < (sector+1)*Offset + TreadNo:
                Node.Add(node.Node[i])
        return Node
    else:
        return node

def GetDeformedNodeAtAngleFromSDB(strSimCode, Angle, Step=0, Offset= 10000, TreadNo = 10000000, **args):
    """
    :param NodeFile: Results from SDB Result File (*-NodeTemperature.tmp or Simulation Code)
    :param Angle: Top : 0, Bottom : 180
    :param Offset: default 10000
    :param TreadNo: default 10000000
    :return:
    """
    SimTime = ''
    strJobDir = ''
    strLastSDBFile = ''
    for key, value in args.items():
        if key == 'step':            Step = int(value)
        if key == 'offset':          Offset = int(value)
        if key == 'Treadstartno' or key == 'treadno' or key == 'Treadno' or key == 'treadstartno' or key == 'TreadStartNo':
            TreadNo = int(value)
        if key == 'simtime': SimTime = value 
        if key == 'jobdir': strJobDir = value
        if key == 'lastsdb': strLastSDBFile = value

    if strJobDir == '': strJobDir = os.getcwd()
    if SimTime == '':   
        if ".tmp" in strSimCode: pass
        else:    SimTime = SIMTIME(strSimCode+'.inp')     
    
    
    if '-NodeTemperature.tmp' in strSimCode:
        DeformedNodeFileName = strSimCode
    else: 
        # DeformedNodeFileName = strJobDir + '/' + strSimCode + '-NodeTemperature.tmp'
        DeformedNodeFileName = strSimCode + '-NodeTemperature.tmp'
        if SimTime.SimulationTime == 0.0:
            sdbFileName = strJobDir + '/' + 'SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
        else:
            sdbFileName = strJobDir + '/' + 'SDB.' + strSimCode + '/' + strSimCode + '.sdb'
        if Step == 0: 
            strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSDBFile =  sdbFileName + str(format(Step, '03'))
        #######################################################################
        SDBResults(sdbFileName, strLastSDBFile, 2, 0, Offset, Offset, TreadNo)
        #######################################################################
    
    if strLastSDBFile=='':
        RimNode  = GetRimCenter()
    else:
        RimNode  = GetRimCenter(lastsdb=strLastSDBFile)
    
    with open(DeformedNodeFileName) as InpFile:
        lines = InpFile.readlines()

    AllNode=NODE()
    for line in lines:
        data = list(line.split(','))
        if data[0][0] == '\n' or data[0][0] == '*':
            pass
        else:
            id= int(data[0].strip())
            X = float(data[2].strip()) - RimNode.Node[0][1]
            Y =  float(data[3].strip()) - RimNode.Node[0][2]
            Z =  float(data[4].strip()) - RimNode.Node[0][3]
            A = float(data[8].strip())
            AllNode.Add([id, X, Y, Z, A])
            
    N = len(AllNode.Node)
    NodeList = []
    for i in range(N):
        NodeList.append(AllNode.Node[i][0])
        NodeList.append(AllNode.Node[i][1])
        NodeList.append(AllNode.Node[i][2])
        NodeList.append(AllNode.Node[i][3])
        NodeList.append(AllNode.Node[i][4])
    tupleNode = tuple(NodeList)
    
    NodeFromC = _islm.AngledNode(tupleNode, Angle, 5, Offset, TreadNo)
    ## NodeFromC = [NodeID, X, Y, Z, Angle] # NodeID = Offset*SectorNo + Node ID : Number of ID is below Tread No. 
    ## Sample :  Node 183 on Tread --> [2090183, 0.225989, -0.046647, 0.150740, 59.44] (not 12090183)
    
    
    DeformedNode = NODE()
    iN = len(NodeFromC)
    # print 'No',iN/5, ',', NodeFromC[0], NodeFromC[1], NodeFromC[2], NodeFromC[3], NodeFromC[4]
    for i in range(int(iN/5)):
        DeformedNode.Add([int(NodeFromC[i*5]), NodeFromC[i*5+1], NodeFromC[i*5+2], NodeFromC[i*5+3], NodeFromC[i*5+4]  ])
    DeformedNode.DeleteDuplicate()
    
    
    
    N = len(DeformedNode.Node)
    for i in range(N): 
        DeformedNode.Node[i][3] = math.sqrt(DeformedNode.Node[i][1]*DeformedNode.Node[i][1]+DeformedNode.Node[i][3]*DeformedNode.Node[i][3])
        DeformedNode.Node[i][1] = 0.0
    
    # DeformedNode.Save("PythonNode.txt")
    return DeformedNode
  
def GetDeformedNodeTemperatureFromSDB(strSimCode, SectorNo, Step=0, Offset= 10000, TreadNo = 10000000, SimTime=time, **args):
    """
    :param NodeFile: Results from SDB Result File (*-NodeTemperature.tmp or Simulation Code)
    :param SectorNo: n = nth sector, 1001 : uppermost node
    :param Offset: default 10000
    :param TreadNo: default 10000000
    :return:
    """
    
    for key, value in args.items():
        if key == 'step':
            Step = int(value)
        if key == 'offset':
            Offset = int(value)
        if key == 'Treadstartno' or key == 'treadno' or key == 'Treadno' or key == 'treadstartno' or key == 'TreadStartNo':
            TreadNo = int(value)
        if key == 'Simtime' or key == 'time' or key == 'simtime' or key == 'Time':
            SimTime = value
            
    if len(list(strSimCode.split('/'))) > 1:
    
        ## strSimCode = ~./DOE/1017440VT00193-0/RND-1017440VT00193-0-D101-0001

        SimTime = SIMTIME(strSimCode+'.inp')
        
        # strJobDir = os.getcwd()
        word = list(strSimCode.split('/'))
        I = len(word)
        DeformedNodeFileName = ''
        strWorkDir = ''
        for i in range(I):
            if i < I-1:
                strWorkDir += word[i] + '/'
            if i < I-2:
                DeformedNodeFileName += word[i] + '/'
            SimCode = word[i]
        
        DeformedNodeFileName = DeformedNodeFileName + SimCode + '-NodeTemperature.tmp'
        
        if SimTime.SimulationTime == 0.0:
            sdbFileName = strWorkDir + 'SDB_PCI.' + SimCode + '/' + SimCode + '.sdb'
        else:
            sdbFileName = strWorkDir + 'SDB.' + SimCode + '/' + SimCode + '.sdb'
        if Step == 0: 
            strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSDBFile =  sdbFileName + str(format(Step, '03'))
        if SectorNo == 0:
            SectorNo = 10000
        SDBResults(sdbFileName, strLastSDBFile, 2, SectorNo, Offset, Offset, TreadNo)
            
            
    else: 
        strJobDir = os.getcwd()
        SimTime = SIMTIME(strSimCode+'.inp')
        DeformedNodeFileName = strJobDir + '/' + strSimCode + '-NodeTemperature.tmp'
        print (strJobDir)
        print (DeformedNodeFileName)

        if SimTime.SimulationTime == 0.0:
            sdbFileName = strJobDir + '/' + 'SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
            
        else:
            sdbFileName = strJobDir + '/' + 'SDB.' + strSimCode + '/' + strSimCode + '.sdb'
            
        if Step == 0: 
            strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSDBFile =  sdbFileName + str(format(Step, '03'))
        
        if SectorNo == 0:
            SectorNo = 10000
        SDBResults(sdbFileName, strLastSDBFile, 2, SectorNo, Offset, Offset, TreadNo)
    
    UmostSector = 0
    RimNode  = GetRimCenter(lastsdb=strLastSDBFile)

    DeformedNodeWithT = NODE()
    with open(DeformedNodeFileName) as InpFile:
        lines = InpFile.readlines()
    c= 0
    MaxZ = 0.0
    MaxN = 0
    X = 0.0
    for line in lines:
        data = list(line.split(','))
        c += 1
        if data[0][0] == '\n' or data[0][0] == '*':
            pass
        else:
            id= int(data[0].strip())
            X = float(data[2].strip())  - RimNode.Node[0][1]
            Y =  float(data[3].strip()) - RimNode.Node[0][2]
            Z =  float(data[4].strip()) - RimNode.Node[0][3]
            T = float(data[1].strip())

            if SectorNo == 0:
                id = id % TreadNo
                DeformedNodeWithT.Add([id, X, Y, Z, T])
            else:
                L = math.sqrt(X * X + Z * Z)
                DeformedNodeWithT.Add([id, 0.0, Y, L, T ])
                # print [id, 0.0, Y, L, T ]

    return DeformedNodeWithT

def GetRimCenter(rimfile = "rigid.tmp", **args):
    lastsdb = ''
    sdb = ''
    for key, value in args.items():
        lastsdb = ''
        if key == 'file' or key == 'Rimfile':         rimfile = value
        if key == 'lastsdb':                          lastsdb = value
        if key == 'sdb':                              sdb = value
        
    Rim=NODE()
    if lastsdb != '':
        if sdb == '': sdb = lastsdb[:-3]
        nodes = ResultSDB(sdb, lastsdb, 10000, 10000000, 7, 0)
        if len(nodes.Node) == 1: Rim.Add(nodes.Node[0])
        else: 
            Rim.Add(nodes.Node[1])
        return Rim
    else:
        with open(rimfile) as Rigid:
            RimLine = Rigid.readlines()
        for i in range(len(RimLine)):
            if 'RIM' in RimLine[i]:
                data =  list(RimLine[i + 1].split(','))
                Rim.Add([int(data[0].strip()), float(data[1].strip()), float(data[2].strip()), float(data[3].strip())])
                break

        return Rim
 
def GetDrumCenter(rimfile = "rigid.tmp", **args):
    lastsdb = ''
    sdb = ''
    for key, value in args.items():
        if key == 'file' or key == 'Rimfile':     rimfile = value
        if key == 'lastsdb':                      lastsdb = value
        if key == 'sdb':                          sdb = value
    Drum=NODE()
    if lastsdb != '':
        if sdb == '': sdb = lastsdb[:-3]
        nodes = ResultSDB(sdb, lastsdb, 10000, 10000000, 7, 0)
        Drum.Add(nodes.Node[0])
        return Drum
    else:
        with open(rimfile) as Rigid:
            Line = Rigid.readlines()
        for i in range(len(Line)):
            if 'DRUM' in Line[i]:
                # print RimLine[i + 1]
                data =  list(Line[i + 1].split(','))
                Drum.Add([int(data[0].strip()), float(data[1].strip()), float(data[2].strip()), float(data[3].strip())])
                break

        return Drum
    
def GetIYYFromSMART():
    # Check if '.lsflog' is created or not 
    for i in range(10):
        filelist = os.listdir(os.getcwd())
        isFile = 0
        for file in filelist:
            FileExt = os.path.splitext(file)[-1]
            FileSep = os.path.splitext(file)[0].split('-')[0]
            if '.lsflog' in file:
                ISLM_logfilename = file
                isFile =1
                break;
        if isFile == 0:
            print ("Waiting for being created lsflog file")
            time.sleep(1)
            continue
        else:
            break
    ##################################################################
            
    f = open(ISLM_logfilename, 'r')

    lines = f.readlines()
    for line in lines:
        if 'ACTUAL TIRE IYY' in line:
            IYY = float(list(line.split('='))[1].strip())
            isIYY = 1
            f.close()
            break
    
    
    if isIYY == 0:
        print ("ERROR, NO DATA in 'lsflog' file ")
            
    return IYY 

def GetODSWfromDimResult(strSimCode):
    if 'DimValue.txt' in strSimCode:
        DeformedResult = strSimCode
    else: 
        strJobDir = os.getcwd()
        DeformedResult = strJobDir + '/' + strSimCode + '-DimValue.txt'
    
    with open(DeformedResult) as DIM:
        Lines = DIM.readlines()
        
    for line in Lines:
        word = list(line.split('='))
        if 'Initial OD' in word[0]: 
            InitOD = float(word[1].strip())
        if 'Initial SW' in word[0]: 
            InitSW = float(word[1].strip())
        if 'Deformed OD' in word[0]: 
            DefOD = float(word[1].strip())
        if 'Deformed SW' in word[0]: 
            DefSW = float(word[1].strip())
            
    dim = [InitOD, InitSW, DefOD, DefSW]
    return dim 

def GetODSWfromDeformedNode(DeformedNode, Element, Node, ResultOption=1, Offset=10000, TreadNo=10000000, **args):
    camber = 0.0; slipangle = 0.0
    # load = 0.0; strJobDir = ''
    for key, value in args.items():
        if key == 'resultoption' or key == 'option' or key == 'Resultoption' or key =='result':            ResultOption = int(value)
        if key == 'treadno' or key == 'Treadno' or key == 'Treadstartno' or key == 'TreadStartNo':         TreadNo = int(value)
        if key == 'offset':            Offset = int(value)
        # if key == 'load':              load = value
        if key == 'camber':            camber = value
        if key == 'slipangle':         slipangle = value
        # if key == 'jobdir':            strJobDir = value
            
    # DeformedNode.Image(file="NODE_ROTATED_0", size=1, xy=23)
    if  camber !=0:
        DeformedNode.Rotate(camber, xy=23)
        print ("Camber Angle = %f"%(camber))
        # DeformedNode.Image(file="NODE_ROTATED_camber_23", size=1, xy=23)
    if slipangle !=0:
        DeformedNode.Rotate(-slipangle, xy=21) 
        print ("Slip Angle = %f"%(slipangle))
        # DeformedNode.Image(file="NODE_ROTATED_slipangled_21", size=1, xy=21)

    TireOuter = Element.OuterEdge(Node)   ## Node : 2D Node Class
    BSW = Element.Elset('BSW')
    BSWOuterNodeID=[]
    N = len(TireOuter.Edge)
    M = len(BSW.Element)
    for i in range(N):
        for j in range (M):
            for k in range(1, BSW.Element[j][6]+1): 
                if TireOuter.Edge[i][0] == BSW.Element[j][k]: 
                    BSWOuterNodeID.append(BSW.Element[j][k])
                if TireOuter.Edge[i][1] == BSW.Element[j][k]: 
                    BSWOuterNodeID.append(BSW.Element[j][k])
    
    i=0
    while i < len(BSWOuterNodeID):   ## Delete Duplication. 
        j = i+1
        while j < len(BSWOuterNodeID): 
            if BSWOuterNodeID[i] == BSWOuterNodeID[j]:
                del(BSWOuterNodeID[j])
                j -= 1
            j += 1
        i += 1
    
    C01  = Element.Elset('C01')
    
    N = len(C01.Element)
    MaxCc = -9.0E10
    for i in range(N): 
        Ni = Node.NodeByID(C01.Element[i][1])
        if MaxCc < Ni[3]: 
            MaxCc = Ni[3]
            iTopCc = i
    sortCC = ELEMENT()

    for i in range(N):
        mat = 0
        for j in range(N):
            if i != j and C01.Element[i][1] == C01.Element[j][2]:
                mat = 1
        if mat == 0:
            sortCC.Add(C01.Element[i])
            del(C01.Element[i])
            break
    i=0
    while i < len(C01.Element):
        for j in range(len(C01.Element)):
            if sortCC.Element[len(sortCC.Element)-1][2] == C01.Element[j][1] and i != j:
                sortCC.Add(C01.Element[j])
                del(C01.Element[j])
                i -= 1
                break
        i+=1
                
    N = len(DeformedNode.Node)
    TopNode = 0
    TopZ = -10000.0
    BotZ = 10000.0
    TotalNo = 0 
    
    MaxY = 0.0
    MinY = 0.0
    SWNodeLeft = 0
    SWNodeRight = 0
    SWZRight =0.0
    SWZLeft =0.0
    
    DimX0= DeformedNode.Node[0][1]
    DimX1= DeformedNode.Node[0][1]
    for i in range(N):
        if DeformedNode.Node[i][3] > TopZ:  
            TopZ = DeformedNode.Node[i][3]
            TopNode = DeformedNode.Node[i][0]
        if DeformedNode.Node[i][3] < BotZ:  
            BotZ = DeformedNode.Node[i][3]
        if DeformedNode.Node[i][0] > TotalNo: 
            TotalNo = DeformedNode.Node[i][0]

        if DeformedNode.Node[i][1] > DimX0:  
            DimX0 = DeformedNode.Node[i][1]
        if DeformedNode.Node[i][1] < DimX1:  
            DimX1 = DeformedNode.Node[i][1]

    # print ("OD value %f, %f"%(TopZ-BotZ, DimX1-DimX0))

    if TotalNo > TreadNo: 
        TotalNo = TotalNo - TreadNo
    TotalSectors = int(TotalNo / Offset) + 1
    if TopNode > TreadNo: 
        TopNode = TopNode - TreadNo
    TopSector = int(TopNode / Offset) + 1 

    LoadedNodeSector = TopSector + int(TotalSectors/2)
    if LoadedNodeSector > TotalSectors:
        LoadedNodeSector -= TotalSectors

    MaxY = 0.0
    MinY = 0.0
    N = len(DeformedNode.Node)
    fnode=NODE()
    for i in range(N):
        if DeformedNode.Node[i][0] >= (TopSector-1) * Offset and DeformedNode.Node[i][0] < TopSector * Offset:
            if MaxY < DeformedNode.Node[i][2]: 
                MaxY = DeformedNode.Node[i][2]
            if MinY > DeformedNode.Node[i][2]: 
                MinY = DeformedNode.Node[i][2]
            fnode.Add( [DeformedNode.Node[i][0]%Offset, DeformedNode.Node[i][1], DeformedNode.Node[i][2], DeformedNode.Node[i][3] ] )

            I=len(sortCC.Element)
    msw1 = 0
    sw1=0
    for i in range(int(I/2)):
        n = fnode.NodeByID(sortCC.Element[int(I/2)-i][1])
        if n[2] < 0:
            pass
        elif msw1 <= abs(n[2]):
            msw1 = abs(n[2])
            sw1 = n
        else:
            # print i, n
            break
    msw2 = 0
    sw2=0
    for i in range(int(I/2)):
        n = fnode.NodeByID(sortCC.Element[int(I/2)+i][1])
        if n[2] > 0: 
            pass
        elif msw2 <= abs(n[2]) :
            msw2 = abs(n[2])
            sw2 = n
        else:
            # print i, n
            break
        
    I=len(BSWOuterNodeID)
    msw1=100000.0
    msw2=100000.0
    for i in range(I):
        n = fnode.NodeByID(BSWOuterNodeID[i])
        if n[2] < 0:
            lng = abs (n[3] - sw1[3])
            if msw1 > lng: 
                msw1 = lng
                ssw1 = n
        else:
            lng = abs (n[3] - sw2[3])
            if msw2 > lng: 
                msw2 = lng
                ssw2 = n
                
    
    print ("** Carcass SW = %fmm, Carcass Base Tire SW=%f" % ( abs(sw1[2]-sw2[2])*1000, abs(ssw1[2]-ssw2[2])*1000)  )
    f=open("sw.tmp", 'w')
    f.write("sw=%.6f\n"%( abs(ssw1[2]-ssw2[2]) ))
    f.write("posY=%.6f\n"%(ssw2[3]))
    f.close()
    ##################################################################
    DeformedSW = abs(MaxY- MinY)
    DeformedOD = abs(TopZ - BotZ)
    DeformedOD1 = abs(DimX0 - DimX1)
    if TopZ * BotZ > 0 : 
        DeformedOD = abs(TopZ)*2
    if DeformedOD < DeformedOD1:
        DeformedOD = DeformedOD1
    ##################################################################
    # print ("####", DeformedOD, DeformedSW, TotalSectors, TopSector, LoadedNodeSector)
    if ResultOption == 1: ## Deformed OD, SW
        return DeformedOD, DeformedSW
    elif ResultOption == 2:  ## Sector Information Total Sectors, Top Sector, Bottom Sector 
        return TotalSectors, TopSector, LoadedNodeSector
    elif ResultOption == 3:  ## all
        return [DeformedOD, DeformedSW], [TotalSectors, TopSector, LoadedNodeSector]

def EnergyLossDensity(lstSDB, offset=10000, tread=10000000, **args):
    sector = 0
    for key, value in args.items():
        if key == "sector":
            sector = int(value)
        if key == 'treadno' or key == 'Treadno' or key == 'Treadstartno' or key == 'TreadStartNo':
            tread = int(value)
        if key == "Offset":
            offset = value

    sdb = lstSDB[:-3]
    ELD = ResultSDB(sdb, lstSDB, offset, tread, 3, sector)
    return ELD
    

def GetELDatSectionSMART(strSimCode, Pos, Option='Sector', Offset=10000, TreadNo=10000000, Step=0, **args):
    """
    Option : 'Sector'/'Angle
             'Sector' - Pos should be Integer Number,  'Angle' - Pos should be float number 
    """
    strJobDir = ''
    SimTime = ''
    for key, value in args.items():
        if key == 'option':                     
            Option = value
            if Option == 'sector':              
                Option = 'Sector'
        if key == 'treadno' or key == 'Treadno' or key == 'Treadstartno' or key == 'TreadStartNo':    TreadNo = int(value)
        if key == 'offset':            Offset = int(value)
        if key == 'step':              Step = int(value)
        if key == 'jobdir':            strJobDir = value
        if key == 'simtime':           SimTime = value

    if strJobDir == '': strJobDir = os.getcwd()
    if SimTime == '':   
        if ".tmp" in strSimCode: pass
        else:    SimTime = SIMTIME(strSimCode+'.inp')     
            
    if '-EnergyLoss.tmp' in strSimCode:
        ElossFileName = strSimCode
    else: 
        ElossFileName =  strSimCode + '-EnergyLoss.tmp'
        if SimTime.SimulationTime == 0.0:
            sdbFileName = strJobDir + '/' + 'SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
        else:
            sdbFileName = strJobDir + '/' + 'SDB.' + strSimCode + '/' + strSimCode + '.sdb'
        if Step == 0: 
            strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSDBFile =  sdbFileName + str(format(Step, '03'))
        
        SDBResults(sdbFileName, strLastSDBFile, 3, 0, Offset, Offset, TreadNo)
        
    with open (ElossFileName) as SED:
        lines = SED.readlines()
    Uniform=[]    
    Hourglass=[]
    for line in lines:
        if '*' in line:
            if 'Uniform' in line:
                Uni = 1
            if 'Hourglass' in line:
                Uni = 0
            else:
                pass
        else:
            word = list(line.split(','))
            if Uni == 1:
                Uniform.append(float(word[0].strip()))
                Uniform.append(float(word[1].strip()))
            else:
                Hourglass.append(float(word[0].strip()))
                Hourglass.append(float(word[1].strip()))
    tupleUSED = tuple(Uniform)
    tupleHSED = tuple(Hourglass)
    
    if Option == 'Sector': 
        listSED = _islm.ElementSEDfromSMART(tupleUSED, tupleHSED, 2, Pos, Offset, TreadNo)
    else:
        pass
        
    N = len(listSED)
    
    rSED = []
    for i in range(int(N/2)):
        # print 'i=',i,',', int(listSED[i*2]), ',', listSED[i*2+1]
        rSED.append([int(listSED[i*2]), listSED[i*2+1]])
    
    return rSED


def CalculateTireInnerVolume(Outeredge_Or_Element, DeformedTopSectionNode,  **args):
    Node = NODE()
    xy = 23
    filename = "Points_InnerVolume"
    toe = 0 
    for key, value in args.items():
        if key == "node":
            Node=value
        if key == "xy" or key == "XY":
            xy = value
        if key == 'file':
            filename = value
        if key == 'toe': 
            toe = int(value )
        
    if len(Node.Node) == 0: 
        Node = DeformedTopSectionNode
    
    try:
        I = len(Outeredge_Or_Element.Edge)
        InnerEdge = Outeredge_Or_Element
    except:
        tOuteredge = Outeredge_Or_Element.OuterEdge(Node)
        InnerEdge = EDGE() 
        for edge in tOuteredge.Edge:
            if edge[2] == "IL1" or edge[2] == "L11" or edge[2] == "HUS" or edge[2] == "RIC" : 
                InnerEdge.Add(edge)
        InnerEdge.Sort(item=-1, reverse=False)

        on = 1
        i = 0
        while on > 0:
            N1 = Node.NodeByID(InnerEdge.Edge[i][0])
            N2 = Node.NodeByID(InnerEdge.Edge[i][1])
            if N1[3] > N2[3]:
                del(InnerEdge.Edge[i])
            else:
                on = 0
        on = 1
        while on > 0:
            i = len(InnerEdge.Edge)-1
            N1 = Node.NodeByID(InnerEdge.Edge[i][0])
            N2 = Node.NodeByID(InnerEdge.Edge[i][1])
            if N1[3] < N2[3]:
                del(InnerEdge.Edge[i])
            else:
                on = 0
    ## end of searching for Inner edges 
    InnerNodes = InnerEdge.Nodes()
    result = Area(InnerNodes, DeformedTopSectionNode, xy=xy)

    ## Verification 
    nd = NODE()
    for i in InnerNodes:
        for d in DeformedTopSectionNode.Node:
            if d[0] == i:
                nd.Add(d)
    nd.ImageLine(filename, axis=0, dpi=50)

    if toe ==1: 
        toenode = [InnerNodes[0], InnerNodes[len(InnerNodes)-1]]
        return  result[0] * 2 * math.pi * result[2], toenode 
    else: 
        return  result[0] * 2 * math.pi * result[2] 

def TBR_TL_Alpha(edge_outer, node, rimDia=0): 
    npn = np.array(node.Node)
    edges = edge_outer.Edge
    bdring=EDGE()
    for edge in edges:
        ix = np.where(npn[:,0]==edge[0])[0][0]
        ix1 = np.where(npn[:,0]==edge[1])[0][0]
        if npn[ix][2] > 0 and edge[2] == 'HUS' and npn[ix][3] >= rimDia/2000.0 and npn[ix1][3] >= rimDia/2000.0: 
            bdring.Add(edge)

    bdring.Sort()
    
    for i, edge in enumerate(bdring.Edge):
        if i ==0: continue 
        ix = np.where(npn[:,0]==edge[0])[0][0]
        ix1 = np.where(npn[:,0]==edge[1])[0][0]
        ix0 = np.where(npn[:,0]==bdring.Edge[i-1][1])[0][0]
        n0 = npn[ix0]
        n1 = npn[ix]
        n2 = npn[ix1]

        x1 = n0[2]; x2=n1[2]; x3=n2[2]
        y1 = n0[3]; y2=n1[3]; y3=n2[3]

        A = x1*(y2-y3) - y1 *(x2-x3) + x2*y3 - x3*y2
        B = (x1*x1 + y1*y1)*(y3-y2) +(x2**2 + y2**2)*(y1-y3) + (x3**2+y3**2)*(y2-y1)
        C = (x1**2 + y1**2)*(x2-x3)+(x2**2+y2**2)*(x3-x1) + (x3*x3 + y3*y3)*(x1-x2)
        D = (x1*x1 + y1*y1)*(x3*y2-x2*y3)+(x2*x2+y2*y2)*(x1*y3-x3*y1)+(x3*x3+y3*y3)*(x2*y1-x1*y2)
        SQRT = B*B + C*C - 4*A*D  

        if A == 0 or SQRT < 0.0: ## make line 
            if n1[3] > n2[3]: 
                N1= n2;  N2= n1 
            else: 
                N1= n1;  N2= n2
            print (" TBR BeadRing A-Angle : LINE : %.5f, %.5f"%(A, SQRT) )
            break 
        else:
            cx = -B/A/2.0
            cy = -C/A/2.0
            R = math.sqrt(SQRT) / 2/abs(A)
            if R > 5.0: ## line 
                if n1[3] > n2[3]: 
                    N1= n2;  N2= n1 
                else: 
                    N1= n1;  N2= n2 
                print (" TBR BeadRing A-Angle : Radius=%.1f"%(R*1000))
                break 
    
    NS = [0, 0, N1[2]+1.0, N1[3]]

    return math.degrees(Angle_3nodes(NS, N1, N2, xy=23))

##//////////////////////////////////////

########################################
## For Post Processing of the HK-SMART
########################################

def GrooveDetectionFromEdge(oEdge, node, OnlyTread=1, TreadNumber=10000000, **args):
    for key, value in args.items():
        if key == 'onlytread' or key == 'tread':
            OnlyTread = int(value)
        if key == 'treadno' or key == 'Treadno' or key == 'Treadstartno' or key == 'TreadStartNo':
            TreadNumber = int(value)
        # if key == 'offset':
            # Offset = int(value)
        # if key == 'step':
            # Step = int(value)

    N = len(oEdge.Edge)
    LengthOfEdge = len(oEdge.Edge[0])

    
    # print 'oEDGE - ', oEdge.Edge[5], len(oEdge.Edge)
    # print '        ', node.NodeByID(oEdge.Edge[5][0]), node.NodeByID(oEdge.Edge[5][1])
    # Reverse = 0
    if LengthOfEdge == 9 and OnlyTread == 1:  # Edge from SMART Result
        sN = 0
        eN = N
        for i in range(N):
            oEdge.Edge[i][8] = 2
        cEdge = oEdge

    elif LengthOfEdge == 9 and OnlyTread == 0:  # Edge from SMART Result
        sN = 0
        eN = 0
        OnTread = 0
        cEdge = EDGE()
        for i in range(N):
            if oEdge.Edge[i][0] > TreadNumber and sN == 0 and OnTread == 0:
                sN = i
                OnTread = 1
                # print 'start Tread', sN, cEdge.Edge[i]
            if oEdge.Edge[i][0] < TreadNumber and sN > 0 and OnTread == 1:
                eN = i - 1
                OnTread = 0
                # print 'End Tread', eN, cEdge.Edge[i-1]
                break
            if OnTread == 1:
                oEdge.Edge[i][8] = 2
                cEdge.Add(oEdge[i])

    else:  # Original Edge : [Node 1, Node 2, Elset Name, Face ID, Tie No]
        # Edge from INP(Mesh file) : Add Groove/Tread Edge Mark
        # Data to Add : Edge Length, Groove Mark for Node 1, Groove Mark for Node 2, Tread Mark]
        # Groove Mark : 0 - node not in Groove, 1 - node in Groove
        # Tread Mark : 0 - Edge not on Tread, 2 - Edge on Tread
        TreadElset = ['CTB', 'SUT', 'CTR', 'UTR', 'TRW']
        TN = len(TreadElset)
        cEdge = EDGE()
        counting = 0
        for i in range(N):
            TreadID = 0
            for j in range(TN):
                if oEdge.Edge[i][2] == TreadElset[j]:
                    TreadID = 2
                    cEdge.Add(oEdge.Edge[i])
                    length = NodeDistance(oEdge.Edge[i][0], oEdge.Edge[i][1], node)
                    cEdge.Edge[counting][-1] = length
                    cEdge.Edge[counting].append(0)
                    cEdge.Edge[counting].append(0)
                    cEdge.Edge[counting].append(TreadID)
                    counting += 1
                    break


    CriticalAngle = 45.0   ### if there is an error to detect grooves, check this angle... 
    N = len(cEdge.Edge)
    cEdge.Edge[0][6] = 0
    PA = 0.0  # Previous Angle
    PN = 0  # Previous Node Groove ID : 0 - Not in the groove, 1 - in the groove
    for i in range(1, N):
        N1 = node.NodeByID(cEdge.Edge[i][0])
        N2 = node.NodeByID(cEdge.Edge[i][1])
        if N2[2] - N1[2] != 0: 
            A = math.degrees(math.atan((N2[3] - N1[3]) / (N2[2] - N1[2])))
        else: 
            A = 90.0
            
        if N2[2] < N1[2]:
            A = -A
        cEdge.Edge[i][3] = round(A, 2)

        if i == 1:
            if A > CriticalAngle:
                cEdge.Edge[0][6] = 1  ## To see if TBR shoulder side part
                PN = cEdge.Edge[0][7] = 0
                PA = A
                continue
            else:
                PN = cEdge.Edge[i][7] = 0
                PA = A
                continue
        else:
            cEdge.Edge[i][6] = PN
            if PN == 0:
                if PA > CriticalAngle:
                    if A > CriticalAngle:
                        cEdge.Edge[i][6] = 1
                        PN = cEdge.Edge[i][7] = 0
                        PA = A
                        continue
                    else:  # if  (a < CriticalAngle and a > -CriticalAngle)
                        PN = cEdge.Edge[i][7] = 0
                        PA = A
                        continue
                else:
                    if A < CriticalAngle and A > -CriticalAngle:
                        PN = cEdge.Edge[i][7] = 0
                        PA = A
                        continue
                    elif A < -CriticalAngle and abs(PA - A) > CriticalAngle:
                        PN = cEdge.Edge[i][7] = 1
                        PA = A
                        continue
                    else:  # a > CriticalAngle:
                        PN = cEdge.Edge[i][7] = 1
                        PA = A
                        continue
            else:
                if PA > CriticalAngle:
                    if A < CriticalAngle and A > -CriticalAngle:
                        cEdge.Edge[i][6] = 1
                        PN = cEdge.Edge[i][7] = 0
                        PA = A
                        continue
                    else:
                        PN = cEdge.Edge[i][7] = 1
                        PA = A
                        continue
                else:
                    PN = cEdge.Edge[i][7] = 1
                    PA = A
                    continue

    # for val in cEdge.Edge: 
    #     print (val)                
                    
    for i in range(N-1, 0, -1):
        if (cEdge.Edge[i][6] == 0 and cEdge.Edge[i][7] == 0):
            break
        elif cEdge.Edge[i][6] == 1 and cEdge.Edge[i][7] == 1:
            cEdge.Edge[i][6] = 1
            cEdge.Edge[i][7] = 0
        elif cEdge.Edge[i][6] == 0 and cEdge.Edge[i][7] == 1:    
            cEdge.Edge[i][6] = 1
            cEdge.Edge[i][7] = 0
            break
    
    for i in range(N): 
        DIST = NodeDistance(cEdge.Edge[i][0],cEdge.Edge[i][1], node)
        cEdge.Edge[i][5]=DIST
        N1 = node.NodeByID(cEdge.Edge[i][0])
        N2 = node.NodeByID(cEdge.Edge[i][1])
        N3 = [9999, N1[1], N1[2]+0.1, N1[3]]
        Angle = CalculateAngleFrom3Node(N3, N2, N1, 23)
        cEdge.Edge[i][3]=Angle*180.0/3.141592

    # sys.exit()
    
    return cEdge   # return Crown area

def DeleteGrooveEdgeAfterGrooveDetection(cEdge, node):
    i = 0
    while i < len(cEdge.Edge) - 1:
        if cEdge.Edge[i][6] == 1 and cEdge.Edge[i][7] == 1 and cEdge.Edge[i][8] == 2:
            # print 'Deleted', cEdge.Edge[i]
            cEdge.Delete(i)
            i += -1
        i += 1
    N = len(cEdge.Edge)
    for i in range(N - 1):
        if cEdge.Edge[i][6] == 0 and cEdge.Edge[i][7] == 1 and cEdge.Edge[i][8] == 2:
            cEdge.Edge[i][7] = 0
            cEdge.Edge[i][1] = cEdge.Edge[i + 1][0]
            cEdge.Edge[i][5] = NodeDistance(cEdge.Edge[i][0], cEdge.Edge[i][1], node)

    return cEdge
    
def CalculateDLR(strSimCode, rigid='rigid.tmp', lastsdb='', simcond=''):
    # print "################# RIGID FIEL", rigid
    if lastsdb == '':
        RimNode = GetRimCenter(rigid)
        DrumNode =GetDrumCenter(rigid)
    else:
        RimNode = GetRimCenter(lastsdb=lastsdb)
        DrumNode =GetDrumCenter(lastsdb=lastsdb)
    # print RimNode.Node[0]
    # print DrumNode.Node[0]
    Rigid=NODE()
    Rigid.Add(RimNode.Node[0])
    Rigid.Add(DrumNode.Node[0])
    Distance = NodeDistance(RimNode.Node[0][0], DrumNode.Node[0][0], Rigid) 
    # print " dist = " , Distance
    # distance from Rim Center to Drum Center
    if simcond =="": Con = CONDITION(strSimCode+'.inp')
    else: 
        Con = simcond
    # print "DRUM RAD=", Con.Drum/2.0
    
    return (Distance - Con.Drum/2.0)

def DLR(diameter=0.0, **args):
    radius = diameter/2.0
    node = NODE()
    MinZ = 0.0
    lastsdb = ''
    for key, value in args.items():
        if key == "radius" :            radius = value
        if key == "road":               radius = value/2.0
        if key == "node":               node = value
        if key == "min":                MinZ = value
        if key == 'lastsdb':            lastsdb = value
    if lastsdb == '':    RimNode = GetRimCenter()
    else:                RimNode = GetRimCenter(lastsdb=lastsdb)
    if lastsdb == '': DrumNode = GetDrumCenter()
    else:             DrumNode = GetDrumCenter(lastsdb=lastsdb)
    if radius !=0:
        Rigid=NODE()
        Rigid.Add(RimNode.Node[0])
        Rigid.Add(DrumNode.Node[0])
        Distance = NodeDistance(RimNode.Node[0][0], DrumNode.Node[0][0], Rigid) 
        # distance from Rim Center to Drum Center
        DLR = (Distance - radius)
    elif len(node.Node)>0:
        I= len(node)
        MinZ = 9.9E20
        for i in range(I):
            if MinZ > node.Node[i][3]:
                MinZ = node.Node[i][3]
        # RimNode = GetRimCenter()
        DLR = abs(RimNode.Node[0][3]-MinZ)
    else:
        # RimNode = GetRimCenter()
        DLR = abs(RimNode.Node[0][3]-MinZ)

    return DLR

def getNODEfromSDB(strSDB, lastSDBresultfile, offset, tread, item, option): 
    Node = ResultSDB(strSDB, lastSDBresultfile, offset, tread, item, option)
    return Node



def DRRonDrum(lastSDBresultfile, SimTime, SimCond, offset=10000, tread=10000000, **args):
    for key, value in args.items():
        if key=="Offset" or key == "offset":
            offset = int(value)
        if key=="tread" or key == "Tread" or key == "TreadNo" or key == "Treadno":
            tread = int(value)
    strSDB = lastSDBresultfile[:-3]
    serial = int(lastSDBresultfile[-3:])

    # lastSDBresultfile1 = strSDB+str(format(serial-2, '03'))
    # lastSDBresultfile2 = strSDB+str(format(serial-1, '03'))
    # lastSDBresultfile3 = strSDB+str(format(serial, '03'))
    # Rim1  = GetRimCenter(lastsdb=lastSDBresultfile1)
    # Rim2  = GetRimCenter(lastsdb=lastSDBresultfile2)
    # Rim3  = GetRimCenter(lastsdb=lastSDBresultfile3)
    # with Pool(processes=3) as pool:
    #     Node1 =  pool.apply_async(ResultSDB, (strSDB, lastSDBresultfile1, offset, tread, 1, 0))
    #     Node2 =  pool.apply_async(ResultSDB, (strSDB, lastSDBresultfile2, offset, tread, 1, 0))
    #     Node3 =  pool.apply_async(ResultSDB, (strSDB, lastSDBresultfile3, offset, tread, 1, 0))

    lastSDBresultfile = strSDB+str(format(serial-2, '03'))
    Node1 = ResultSDB(strSDB, lastSDBresultfile, offset, tread, 1, 0)
    Rim1  = GetRimCenter(lastsdb=lastSDBresultfile)
    lastSDBresultfile = strSDB+str(format(serial-1, '03'))
    Node2 = ResultSDB(strSDB, lastSDBresultfile, offset, tread, 1, 0)
    Rim2  = GetRimCenter(lastsdb=lastSDBresultfile)
    lastSDBresultfile = strSDB+str(format(serial, '03'))
    Node3 = ResultSDB(strSDB, lastSDBresultfile, offset, tread, 1, 0)
    Rim3  = GetRimCenter(lastsdb=lastSDBresultfile)
    N = len(Node2.Node)
    Top = 0.0
    iTop = 0
    for i in range(N):
        Node1.Node[i][1] -= Rim1.Node[0][1];        Node1.Node[i][2] -= Rim1.Node[0][2];        Node1.Node[i][3] -= Rim1.Node[0][3]
        Node2.Node[i][1] -= Rim2.Node[0][1];        Node2.Node[i][2] -= Rim2.Node[0][2];        Node2.Node[i][3] -= Rim2.Node[0][3]
        Node3.Node[i][1] -= Rim3.Node[0][1];        Node3.Node[i][2] -= Rim3.Node[0][2];        Node3.Node[i][3] -= Rim3.Node[0][3]
        if Top < Node2.Node[i][3]:
            Top = Node2.Node[i][3]
            iTop = i
    Det = (Node2.Node[iTop][1]-Node1.Node[iTop][1])*(Node3.Node[iTop][3]-Node2.Node[iTop][3])-(Node2.Node[iTop][3]-Node1.Node[iTop][3])*(Node3.Node[iTop][1]-Node2.Node[iTop][1])
    A = Node2.Node[iTop][1] * Node2.Node[iTop][1] - Node1.Node[iTop][1] * Node1.Node[iTop][1] + Node2.Node[iTop][3] * Node2.Node[iTop][3] - Node1.Node[iTop][3] * Node1.Node[iTop][3]
    B = Node3.Node[iTop][1] * Node3.Node[iTop][1] - Node2.Node[iTop][1] * Node2.Node[iTop][1] + Node3.Node[iTop][3] * Node3.Node[iTop][3] - Node2.Node[iTop][3] * Node2.Node[iTop][3]
    Xc = 0.5 / Det * ( (Node3.Node[iTop][3] - Node2.Node[iTop][3]) * A + (Node1.Node[iTop][3] - Node2.Node[iTop][3]) * B  )
    Yc = 0.5 / Det * ( (Node2.Node[iTop][1] - Node3.Node[iTop][1]) * A + (Node2.Node[iTop][1] - Node1.Node[iTop][1]) * B  )

    if Node1.Node[iTop][3] > Yc and Node3.Node[iTop][3] > Yc and Node1.Node[iTop][1] < Xc and Node3.Node[iTop][1] > Xc :
        Angle = math.degrees(CalculateAngleFrom3Node(Node1.Node[iTop], Node3.Node[iTop], [0, Xc, 0.0, Yc]))
    else:
        Angle1 = math.degrees(CalculateAngleFrom3Node(Node1.Node[iTop], Node2.Node[iTop], [0, Xc, 0.0, Yc]))
        if Node1.Node[iTop][1] > Xc:
            Angle1 = 360.0 - Angle1
        Angle2 = math.degrees(CalculateAngleFrom3Node(Node2.Node[iTop], Node3.Node[iTop], [0, Xc, 0.0, Yc]))
        if Node3.Node[iTop][1] < Xc: 
            Angle2 = 360.0 - Angle2    
        Angle = (Angle1 + Angle2)
    DelT = SimTime.DelTime * 2
    
    DrumAngle = SimCond.Speed /3.6/ SimCond.Drum * 2 * 180.0 / math.pi * DelT
    DRR = SimCond.Drum / 2 * DrumAngle / Angle 
    return DRR 

def DRRonRoad(lastSDBresultfile, SimTime, SimCond, offset=10000, tread=10000000, **args):
    for key, value in args.items():
        if key=="Offset" or key == "offset":
            offset = int(value)
        if key=="tread" or key == "Tread" or key == "TreadNo" or key == "Treadno":
            tread = int(value)
    strSDB = lastSDBresultfile[:-3]
    serial = int(lastSDBresultfile[-3:])

    lastSDBresultfile = strSDB+str(format(serial-2, '03'))
    Node1 = ResultSDB(strSDB, lastSDBresultfile, offset, tread, 1, 0)
    Rim1  = GetRimCenter(lastsdb=lastSDBresultfile)
    lastSDBresultfile = strSDB+str(format(serial-1, '03'))
    Node2 = ResultSDB(strSDB, lastSDBresultfile, offset, tread, 1, 0)
    Rim2  = GetRimCenter(lastsdb=lastSDBresultfile)
    lastSDBresultfile = strSDB+str(format(serial, '03'))
    Node3 = ResultSDB(strSDB, lastSDBresultfile, offset, tread, 1, 0)
    Rim3  = GetRimCenter(lastsdb=lastSDBresultfile)

    N = len(Node2.Node)
    Top = 0.0
    iTop = 0
    for i in range(N):
        Node1.Node[i][1] -= Rim1.Node[0][1];        Node1.Node[i][2] -= Rim1.Node[0][2];        Node1.Node[i][3] -= Rim1.Node[0][3]
        Node2.Node[i][1] -= Rim2.Node[0][1];        Node2.Node[i][2] -= Rim2.Node[0][2];        Node2.Node[i][3] -= Rim2.Node[0][3]
        Node3.Node[i][1] -= Rim3.Node[0][1];        Node3.Node[i][2] -= Rim3.Node[0][2];        Node3.Node[i][3] -= Rim3.Node[0][3]
        if Top < Node2.Node[i][3]:
            Top = Node2.Node[i][3]
            iTop = i

    Det = (Node2.Node[iTop][1]-Node1.Node[iTop][1])*(Node3.Node[iTop][3]-Node2.Node[iTop][3])-(Node2.Node[iTop][3]-Node1.Node[iTop][3])*(Node3.Node[iTop][1]-Node2.Node[iTop][1])
    A = Node2.Node[iTop][1] * Node2.Node[iTop][1] - Node1.Node[iTop][1] * Node1.Node[iTop][1] + Node2.Node[iTop][3] * Node2.Node[iTop][3] - Node1.Node[iTop][3] * Node1.Node[iTop][3]
    B = Node3.Node[iTop][1] * Node3.Node[iTop][1] - Node2.Node[iTop][1] * Node2.Node[iTop][1] + Node3.Node[iTop][3] * Node3.Node[iTop][3] - Node2.Node[iTop][3] * Node2.Node[iTop][3]
    Xc = 0.5 / Det * ( (Node3.Node[iTop][3] - Node2.Node[iTop][3]) * A + (Node1.Node[iTop][3] - Node2.Node[iTop][3]) * B  )
    Yc = 0.5 / Det * ( (Node2.Node[iTop][1] - Node3.Node[iTop][1]) * A + (Node2.Node[iTop][1] - Node1.Node[iTop][1]) * B  )
    
    if Node1.Node[iTop][3] > Yc and Node3.Node[iTop][3] > Yc and Node1.Node[iTop][1] < Xc and Node3.Node[iTop][1] > Xc :
        Angle = (CalculateAngleFrom3Node(Node1.Node[iTop], Node3.Node[iTop], [0, Xc, 0.0, Yc]))
    else:
        Angle1 = (CalculateAngleFrom3Node(Node1.Node[iTop], Node2.Node[iTop], [0, Xc, 0.0, Yc]))
        if Node1.Node[iTop][1] > Xc:
            Angle1 = 2*math.pi - Angle1
        Angle2 = (CalculateAngleFrom3Node(Node2.Node[iTop], Node3.Node[iTop], [0, Xc, 0.0, Yc]))
        if Node3.Node[iTop][1] < Xc: 
            Angle2 = 2*math.pi - Angle2    
        Angle = (Angle1 + Angle2)
    DelT = SimTime.DelTime * 2
    DRR = SimCond.Speed/3.6*DelT/ Angle 
    return DRR 
            

def CalculateDRR(strSimCode, LastStep=0, Offset =10000, TreadNo = 10000000, **args):
    SimTime = ''
    SimCond = ''
    strJobDir =''
    for key, value in args.items():
        if key == 'laststep' or key == 'step':            LastStep = int(value)
        if key == 'treadno' or key == 'Treadno' or key == 'Treadstartno' or key == 'TreadStartNo':            TreadNo = int(value)
        if key == 'offset':            Offset = int(value)
        if key == 'simtime':        SimTime = value
        if key == 'simcond':        SimCond = value
        if key == 'jobdir':         strJobDir = value
    
    if SimTime == '': SimTime = SIMTIME(strSimCode+'.inp')
    if SimCond == '': SimCond = CONDITION(strSimCode+'.inp')
    if strJobDir == '': strJobDir = os.getcwd()
    
    #'*********************************************************************
    lstSDB = strJobDir + "/SDB."+strSimCode + '/' + strSimCode + ".sdb"+str(format(SimTime.LastStep-2, "03"))
    Node1 = GetDeformedNodeFromSDB(lstSDB, 0, lastsdb=1, Offset=Offset, TreadNo=TreadNo, jobdir=strJobDir, simtime=SimTime)
    lstSDB = strJobDir + "/SDB."+strSimCode + '/' + strSimCode + ".sdb"+str(format(SimTime.LastStep-1, "03"))
    Node2 = GetDeformedNodeFromSDB(lstSDB, 0, lastsdb=1, Offset=Offset, TreadNo=TreadNo, jobdir=strJobDir, simtime=SimTime)
    # Node2 = GetDeformedNodeFromSDB(strSimCode, 0, SimTime.LastStep -1, simtime=SimTime, jobdir=strJobDir)
    lstSDB = strJobDir + "/SDB."+strSimCode + '/' + strSimCode + ".sdb"+str(format(SimTime.LastStep, "03"))
    Node3 = GetDeformedNodeFromSDB(lstSDB, 0, lastsdb=1, Offset=Offset, TreadNo=TreadNo, jobdir=strJobDir, simtime=SimTime)
    # Node3 = GetDeformedNodeFromSDB(strSimCode, 0, SimTime.LastStep, simtime=SimTime, jobdir=strJobDir)
    # '********************************************************************
    N = len(Node2.Node)
    Top = 0.0
    iTop = 0
    for i in range(N):
        if Top < Node2.Node[i][3]:
            Top = Node2.Node[i][3]
            TopNode = Node2.Node[i][0]
            iTop = i
    # #################################################################################
    # Center of the Tire 
    # Xc = (y3-y2*y1-y2)*(x2^2-x1^2+y2^2-y1^2)   /((x2-x1)*(y3-y2)-(y2-y1)*(x3-x2))*0.5
    # Yc = (x2-x3*x2-x1)*(x3^2-x2^2+y3^2-y2^2)   /((x2-x1)*(y3-y2)-(y2-y1)*(x3-x2))*0.5
    # #################################################################################
    Det = (Node2.Node[iTop][1]-Node1.Node[iTop][1])*(Node3.Node[iTop][3]-Node2.Node[iTop][3])-(Node2.Node[iTop][3]-Node1.Node[iTop][3])*(Node3.Node[iTop][1]-Node2.Node[iTop][1])
    A = Node2.Node[iTop][1] * Node2.Node[iTop][1] - Node1.Node[iTop][1] * Node1.Node[iTop][1] + Node2.Node[iTop][3] * Node2.Node[iTop][3] - Node1.Node[iTop][3] * Node1.Node[iTop][3]
    B = Node3.Node[iTop][1] * Node3.Node[iTop][1] - Node2.Node[iTop][1] * Node2.Node[iTop][1] + Node3.Node[iTop][3] * Node3.Node[iTop][3] - Node2.Node[iTop][3] * Node2.Node[iTop][3]
    Xc = 0.5 / Det * ( (Node3.Node[iTop][3] - Node2.Node[iTop][3]) * A + (Node1.Node[iTop][3] - Node2.Node[iTop][3]) * B  )
    Yc = 0.5 / Det * ( (Node2.Node[iTop][1] - Node3.Node[iTop][1]) * A + (Node2.Node[iTop][1] - Node1.Node[iTop][1]) * B  )
    if Node1.Node[iTop][3] > Yc and Node3.Node[iTop][3] > Yc and Node1.Node[iTop][1] < Xc and Node3.Node[iTop][1] > Xc :
        Angle = math.degrees(CalculateAngleFrom3Node(Node1.Node[iTop], Node3.Node[iTop], [0, Xc, 0.0, Yc]))
    else:
        Angle1 = math.degrees(CalculateAngleFrom3Node(Node1.Node[iTop], Node2.Node[iTop], [0, Xc, 0.0, Yc]))
        if Node1.Node[iTop][1] > Xc:
            Angle1 = 360.0 - Angle1
        Angle2 = math.degrees(CalculateAngleFrom3Node(Node2.Node[iTop], Node3.Node[iTop], [0, Xc, 0.0, Yc]))
        if Node3.Node[iTop][1] < Xc: 
            Angle2 = 360.0 - Angle2    
        Angle = (Angle1 + Angle2)
        # print '**********', Angle1, Angle2
    DelT = SimTime.DelTime * 2
    # print 'Angle - ', Angle, SimCond.Drum, SimCond.Speed, DelT
    
    DrumAngle = SimCond.Speed /3.6/ SimCond.Drum * 2 * 180.0 / math.pi * DelT
    DRR = SimCond.Drum / 2 * DrumAngle / Angle 
    
    # print 'DRR=',DRR, 'mm, Drum Angle=', DrumAngle, 'Del T', DelT
    # cList = [0, Xc, 0.0, Yc]
    # print 'Node 1, ', Node1.Node[iTop][0],',', Node1.Node[iTop][1],',', Node1.Node[iTop][2],',', Node1.Node[iTop][3]
    # print 'Node 2, ', Node2.Node[iTop][0],',', Node2.Node[iTop][1],',', Node2.Node[iTop][2],',', Node2.Node[iTop][3]
    # print 'Node 3, ', Node3.Node[iTop][0],',', Node3.Node[iTop][1],',', Node3.Node[iTop][2],',', Node3.Node[iTop][3]
    # print 'Center, ', cList[1],',', cList[2],',', cList[3]
    return DRR 

def CalculateDRROnRoad(strSimCode, LastStep=0, Offset =10000, TreadNo = 10000000, SimTime='', SimCond='', **args):

    for key, value in args.items():
        if key == 'laststep' or key == 'step':
            LastStep = int(value)
        if key == 'treadno' or key == 'Treadno' or key == 'Treadstartno' or key == 'TreadStartNo':
            TreadNo = int(value)
        if key == 'offset':
            Offset = int(value)
        if key == 'simtime' or key == 'Time' or key == 'time':
            SimTime = value
        if key == 'simcond' or key == 'condition' or key == 'Simcond':
            SimCond = value
            
            
    # strJobDir = os.getcwd()
    if SimTime == '':
        SimTime = SIMTIME(strSimCode+'.inp')
    if SimCond =='':
        SimCond = CONDITION(strSimCode+'.inp')
        
    # print (strSimCode, SimCond.Speed)
    
    #'*********************************************************************
    # GetDeformedNodeFromSDB(strSimCode, SectorNo, Step=0, Offset= 10000, TreadNo = 10000000):
    # os.system('rm -f rigid.tmp')  
    Node1 = GetDeformedNodeFromSDB(strSimCode, 0, SimTime.LastStep -2)
    Node2 = GetDeformedNodeFromSDB(strSimCode, 0, SimTime.LastStep -1)
    Node3 = GetDeformedNodeFromSDB(strSimCode, 0, SimTime.LastStep)
    # '********************************************************************
    N = len(Node2.Node)
    Top = 0.0
    iTop = 0
    for i in range(N):
        if Top < Node2.Node[i][3]:
            Top = Node2.Node[i][3]
            TopNode = Node2.Node[i][0]
            iTop = i
    # #################################################################################
    # Center of the Tire 
    # Xc = (y3-y2*y1-y2)*(x2^2-x1^2+y2^2-y1^2)   /((x2-x1)*(y3-y2)-(y2-y1)*(x3-x2))*0.5
    # Yc = (x2-x3*x2-x1)*(x3^2-x2^2+y3^2-y2^2)   /((x2-x1)*(y3-y2)-(y2-y1)*(x3-x2))*0.5
    # #################################################################################
    Det = (Node2.Node[iTop][1]-Node1.Node[iTop][1])*(Node3.Node[iTop][3]-Node2.Node[iTop][3])-(Node2.Node[iTop][3]-Node1.Node[iTop][3])*(Node3.Node[iTop][1]-Node2.Node[iTop][1])
    A = Node2.Node[iTop][1] * Node2.Node[iTop][1] - Node1.Node[iTop][1] * Node1.Node[iTop][1] + Node2.Node[iTop][3] * Node2.Node[iTop][3] - Node1.Node[iTop][3] * Node1.Node[iTop][3]
    B = Node3.Node[iTop][1] * Node3.Node[iTop][1] - Node2.Node[iTop][1] * Node2.Node[iTop][1] + Node3.Node[iTop][3] * Node3.Node[iTop][3] - Node2.Node[iTop][3] * Node2.Node[iTop][3]
    Xc = 0.5 / Det * ( (Node3.Node[iTop][3] - Node2.Node[iTop][3]) * A + (Node1.Node[iTop][3] - Node2.Node[iTop][3]) * B  )
    Yc = 0.5 / Det * ( (Node2.Node[iTop][1] - Node3.Node[iTop][1]) * A + (Node2.Node[iTop][1] - Node1.Node[iTop][1]) * B  )
    if Node1.Node[iTop][3] > Yc and Node3.Node[iTop][3] > Yc and Node1.Node[iTop][1] < Xc and Node3.Node[iTop][1] > Xc :
        Angle = (CalculateAngleFrom3Node(Node1.Node[iTop], Node3.Node[iTop], [0, Xc, 0.0, Yc]))
    else:
        Angle1 = (CalculateAngleFrom3Node(Node1.Node[iTop], Node2.Node[iTop], [0, Xc, 0.0, Yc]))
        if Node1.Node[iTop][1] > Xc:
            Angle1 = 2*math.pi - Angle1
        Angle2 = (CalculateAngleFrom3Node(Node2.Node[iTop], Node3.Node[iTop], [0, Xc, 0.0, Yc]))
        if Node3.Node[iTop][1] < Xc: 
            Angle2 = 2*math.pi - Angle2    
        Angle = (Angle1 + Angle2)
        # print '**********', Angle1, Angle2
    DelT = SimTime.DelTime * 2
    # print ('Angle - %f, speed=%f km/h, Del T=%f ' %(math.degrees(Angle), SimCond.Speed, DelT))
    # print "Distance = ", abs(Road3.Node[0][1] - Road1.Node[0][1]), "Speed=", abs(Road3.Node[0][1] - Road1.Node[0][1]) / DelT * 3.6, "km/h"
    
    DRR = SimCond.Speed/3.6*DelT/ Angle 
    # DRR = abs(Road3.Node[0][1] - Road1.Node[0][1])/ Angle 
    
    return DRR 
    
def GetNodeEdgeFromSurfaceNodePosition1(strSimCode, Step=0, **args):
    
    for key, value in args.items():
        if key == 'step':
            Step = int(value)
            
    ### NodeFileName = 'SimulationCode-SurfaceNodePosition1.tmp' 
    if '-SurfaceNodePosition1.tmp' in strSimCode:
        NodeFileName = strSimCode
    else: 
        strJobDir = os.getcwd()
        SimTime = SIMTIME(strSimCode+'.inp')
        NodeFileName = strJobDir + '/' + strSimCode + '-SurfaceNodePosition1.tmp'
        if SimTime.SimulationTime == 0.0:
            sfricFileName = strJobDir + '/' + 'SFRIC_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
            
        else:
            sfricFileName = strJobDir + '/' + 'SFRIC.' + strSimCode + '/' + strSimCode + '.sdb'
            
        if Step == 0: 
            strLastSFRICFile =  sfricFileName + str(format(SimTime.LastStep, '03'))
        else: 
            strLastSFRICFile =  sfricFileName + str(format(Step, '03'))
            
        SFRICResults(sfricFileName, strLastSFRICFile, 1, 1001, 10000, 10000000)
    
    
    with open(NodeFileName) as InpFile:
        Lines = InpFile.readlines()
    tNode = NODE()
    tEdge = EDGE()
    for line in Lines:
        data = list(line.split(','))
        tNode.Add([int(data[1]), float(data[3]), float(data[4]), float(data[5])])
        tNode.Add([int(data[2]), float(data[6]), float(data[7]), float(data[8])])
        length = math.sqrt((float(data[4]) - float(data[7])) * (float(data[4]) - float(data[7])) + (float(data[5]) - float(data[8])) * (float(data[5]) - float(data[8])))
        if int(data[9]) == 1:
            tEdge.Add([int(data[1]), int(data[2]), 'Profile', 0, int(data[0]), length, 0, 0, int(data[10])])
    tNode.DeleteDuplicate()    
    
    return tNode, tEdge

def WriteComponentRRforRRSimulation(strSimCode, strJobDir='', RETURN = 0, **args) :
    Cond =""
    for key, value in args.items():
        if key == 'strjobdir' or key == 'jobdir':             strJobDir = value
        if key == 'return' or key == 'Return':                RETURN = int(value)
        if key == 'simcond':                                  Cond = value
            

    if strJobDir == '':        strJobDir = os.getcwd()

    rValue = {} ## if RETURN != 0:, rValue is returned. 
        
    rptFile = strJobDir + '/' + 'REPORT' + '/' + 'vis_' + strSimCode + '.rpt'
    FileNameToWrite = strJobDir + '/' + strSimCode + '-RRValue.txt'
    visrptFile = open(rptFile, 'r')
    lineCount = len(visrptFile.readlines())
    visrptFile.close()
    visrptFile = open(rptFile, 'r')
    i = 0
    Index = 0
    resultfile = open(FileNameToWrite, 'w')
    resultfile.writelines('Component, VOLUME(m^3), RR(N), RR/VOLUME(m^3*10E-3)\n')
    while i < lineCount:
        visrptline = visrptFile.readline()
        if visrptline[0] == '-':
            Index = Index + 1
        else:
            if Index == 2 or Index == 3:
                visrptData = visrptline.split(' ')
                j = 0
                while j < len(visrptData):
                    if visrptData[j] == '':
                        del visrptData[j]
                        j = j - 1
                    j = j + 1
                resultfile.writelines('%s\t\t%s\t\t%s\t\t%s\n' % (visrptData[0], visrptData[2], visrptData[4], visrptData[16].split('\n')[0]))
                rValue[visrptData[0]] = visrptData[4]
            #               print Index, visrptData
            if Index == 6:
                resultfile.writelines('\n')
                if Cond == "":  Cond = CONDITION(strSimCode+'.inp')
                resultfile.writelines('VOLUME(m^3), Total_RR(N), Total_RR/VOLUME(m^3*10E-3)\n')
                visrptData = visrptline.split(' ')
                j = 0
                while j < len(visrptData):
                    if visrptData[j] == '':
                        del visrptData[j]
                        j = j - 1
                    j = j + 1
                resultfile.writelines('%s\t\t%s\t\t%s\n' % (visrptData[0], visrptData[1], visrptData[4].split('\n')[0]))
                rValue["RR"] = visrptData[1]
                resultfile.writelines('\n')
                resultfile.writelines('RRc=%s' % (round((float(visrptData[1]) * 1000 / Cond.Load / 9.8), 4)))
                resultfile.writelines('\n')
        i = i + 1
    resultfile.writelines('\n')
    resultfile.writelines('Success::Post::[Simulation Result] This simulation result was created successfully!!\n')
    visrptFile.close()
    resultfile.close()
    
    if RETURN != 0:
        return rValue
 
def GetDOEFileName(): 
    """
    Supposing 
      - Working directory: /home/fiper/ISLM/ISLM_JobFolder/RND/1999999/1999999VT00001-0/RND-1999999VT00001-0-E100-0001/
             : RND-1999999VT00001-0-E101-0001.sns, RND-1999999VT00001-0-E101-0002.sns, RND-1999999VT00001-0-E101-0003.sns, ...
             : DOE in (parameter list), responses to DOE
      -  Individual Model Directory : Work-Directory / 1999999VT00001-0, Work-Directory/1999999VT00001-1, Work-Directory/1999999VT00001-2, ...
             --> ModelDir 
      -   Job Directory : 
      -    Dimension:  ModelDir/E101  or ModelDir/DIM
      -    Static Footprint : ModelDir/E102  or ModelDir/StaticFootprint
      -    Rolling Footprint : ModelDir/E103 or ModelDir/RollingFootprint
      -    Rolling Resistance : ModelDir/E104 or ModelDir/RR
      -    Endurance          : ModelDir/E105  or ModelDir/StaticLoading(Endurance)
    """
    pass
##//////////////////////////////////////

########################################
## PLOT Functions
########################################

def plot_DetailLayout(filename, Element, Node, dpi=200, AddingNodes=[], rim=[], group='PCR', beadring='Tubeless'):# , Elset):
    
    edge_Outer = Element.OuterEdge(Node)

    for el in Element.Element:
        if el[6] ==2:
            edge =[el[1], el[2], el[5], 'S0', el[0], el[7]]
            edge_Outer.Add(edge)


    BDR  = Element.Elset("BEAD_R")
    BDL = Element.Elset("BEAD_L")
    if len(BDL.Element) ==0:
        i=0
        while i < len(BDR.Element):
            if BDR.Element[i][8] > 0:
                BDL.Add(BDR.Element[i])
                del(BDR.Element[i])
                i-=1
            i += 1
    if len(BDR.Element) ==0:
        i=0
        while i < len(BDL.Element):
            if BDL.Element[i][8] < 0:
                BDR.Add(BDL.Element[i])
                del(BDL.Element[i])
                i-=1
            i += 1

    BDedge = BDL.OuterEdge(Node)
    BDRedge = BDR.OuterEdge(Node)
    BDedge.Combine(BDRedge)
    edge_Outer.Combine(BDedge)

    ## OUTER EDGE _ Black line 

    ## rubber 

    npn = np.array(Node.Node)
    
    edge_Components = EDGE()

    elsets = ["FIL", 'LBF', 'UBF', 'TRW', 'HUS', 'BEC', 'SIR', 'BDF', 'RIC', 'BSW']
    for name in elsets:
        SET = Element.Elset(name)
        POS=ELEMENT(); NEG=ELEMENT()
        if len(SET.Element)>0: 
            for el in SET.Element:
                ix = np.where(npn[:,0]==el[1])[0][0]
                if npn[ix][2] > 0: 
                    POS.Add(el)
                else:
                    NEG.Add(el)
            try:
                edges = NEG.OuterEdge(Node)
                edge_Components.Combine(edges)
                edges = POS.OuterEdge(Node)
                edge_Components.Combine(edges)
            except:
                print(name)
                sys.exit()

    elsets = ["SUT", "CTB"]
    for name in elsets:
        SET = Element.Elset(name)
        if len(SET.Element)>0: 
            edges = SET.OuterEdge(Node)
            edge_Components.Combine(edges)

    ## plotting 
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('off')
    
    LineWidth = 0.5
    textsize = 8

    color = 'black'
    for edge in edge_Outer.Edge:
        ix = np.where(npn[:,0]==edge[0])[0][0]; N1 = npn[ix]
        ix = np.where(npn[:,0]==edge[1])[0][0]; N2 = npn[ix]
        plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, lw=LineWidth)
    color = 'gray'
    for edge in edge_Components.Edge:
        ix = np.where(npn[:,0]==edge[0])[0][0]; N1 = npn[ix]
        ix = np.where(npn[:,0]==edge[1])[0][0]; N2 = npn[ix]
        plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, lw=LineWidth/2)

    nx=[]; ny=[]
    for nd in AddingNodes:
        nx.append(nd[2])
        ny.append(nd[3])

    if len(rim) > 0:
        RimPoint = rim 
        if group != 'TBR': 
            rims=['START, 14.300000,  12.500000',
                'CIRCL, 17.300000,   9.500000, 14.300000,  9.500000', 
                'CIRCL,  7.800000,   0.000000,  7.800000,  9.500000',
                'LINE ,  5.956000,   0.000000',
                'CIRCL, -0.519266,  -5.933488,  5.956000, -6.500000',
                'LINE , -2.262376, -25.857332',
                'CIRCL, -6.921500, -30.411184, -7.243350,-25.421553'
                ]
            AddRimsToDrawing(rims, RimPoint, ax)
            rims=['START, 14.300000,  -12.500000',
                'CIRCL, 17.300000,   -9.500000, 14.300000,  -9.500000', 
                'CIRCL,  7.800000,   -0.000000,  7.800000,  -9.500000',
                'LINE ,  5.956000,   -0.000000',
                'CIRCL, -0.519266,  5.933488,  5.956000, 6.500000',
                'LINE , -2.262376, 25.857332',
                'CIRCL, -6.921500, 30.411184, -7.243350, 25.421553'
                ]
        elif beadring == 'Tubeless':
            rims=[  'START,  10.017000,  20.507000', 
                    'CIRCL,   3.934092,   0.624717,	 0.000000,  12.700000 ', 
                    'CIRCL,  -1.316291,  -4.911422,	 6.411000,  -6.982100 ', 
                    'LINE , -24.593024, -92.774800' 
                ]
            AddRimsToDrawing(rims, RimPoint, ax)
            rims=[  'START,  10.017000,  -20.507000', 
                    'CIRCL,   3.934092,   -0.624717,	 0.000000,  -12.700000 ', 
                    'CIRCL,  -1.316291,  4.911422,	 6.411000,  6.982100 ', 
                    'LINE , -24.593024, 92.774800' 
                ]
        else:
            rims =['START,  28.000000,  16.500000', 
                    'LINE,   28.000000,  14.000000 ', 
                    'CIRCL,  14.000000,   0.000000,  14.000000,  14.000000',
                    'LINE,    7.330650,   0.000000', 
                    'CIRCL,  -0.638907,  -7.302750,   7.330650,  -8.000000', 
                    'LINE,   -3.149590, -36.000000  ', 
                    'CIRCL,  -6.559574, -41.876208, -11.119148, -35.302754' 
                    ]
            AddRimsToDrawing(rims, RimPoint, ax)
            rims =['START,  28.000000,  -16.500000', 
                    'LINE,   28.000000,  -14.000000 ', 
                    'CIRCL,  14.000000,   0.000000,  14.000000,  -14.000000',
                    'LINE,    7.330650,   0.000000', 
                    'CIRCL,  -0.638907,  7.302750,   7.330650,  8.000000', 
                    'LINE,   -3.149590, 36.000000  ', 
                    'CIRCL,  -6.559574, 41.876208, -11.119148, 35.302754' 
                    ]
        
        RimPoint[0] *= -1 
        AddRimsToDrawing(rims, RimPoint, ax)
        
    plt.tight_layout()

    plt.scatter(nx, ny, c='r', s=1.2)
    plt.savefig(filename, dpi=dpi)
    plt.clf()        

def Angle_3nodes(n1=[], n2=[], n3=[], xy=0): ## n2 : mid node 
    v1 = [n1[1]-n2[1], n1[2]-n2[2], n1[3]-n2[3] ]
    v2 = [n3[1]-n2[1], n3[2]-n2[2], n3[3]-n2[3] ]
    
    if xy ==0: 
        cos = round((v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]) /  math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2) / math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2), 9)
        angle = math.acos(cos)
    else: 
        x = int(xy/10)-1;     y = int(xy%10)-1
        cos = round((v1[x]*v2[x] + v1[y]*v2[y] ) /  math.sqrt(v1[x]**2 + v1[y]**2 ) / math.sqrt(v2[x]**2 + v2[y]**2), 9)
        angle = math.acos(cos)

    return angle

def AddRimsToDrawing(rims, RimPoint, ax): 
    try : 
        from matplotlib.patches import Arc
    except:
        pass 

    for line  in rims: 
        word = line.split(",")
        
        if 'START' in word[0].upper(): 
            sx = float(word[2])/1000 + RimPoint[0]
            sy = float(word[1])/1000 + RimPoint[1]

        if 'CIRCL' in word[0].upper(): 
            ex = float(word[2])/1000 + RimPoint[0]
            ey = float(word[1])/1000 + RimPoint[1]
            cx = float(word[4])/1000 + RimPoint[0]
            cy = float(word[3])/1000 + RimPoint[1]
            D = math.sqrt((cx-ex)**2 + (cy-ey)**2)*2

            n1 = [0, 0, sx, sy]
            n2 = [0, 0, cx, cy]
            n3 = [0, 0, ex, ey]
            angle = Angle_3nodes(n1, n2, n3, xy=23)
            
            cn = [0, 0, cx, cy+ 0.1]
            if n1[2] > n3[2] : 
                startangle = Angle_3nodes(n1, n2, cn, xy=23)  * 180.0 / 3.141592  
                sp = sx 
            else: 
                startangle = Angle_3nodes(n3, n2, cn, xy=23)  * 180.0 / 3.141592  
                sp = ex 
            if cx < sp: 
                if startangle >=90: 
                    startangle = 450.0 - startangle 
                else: 
                    startangle = 90.0 - startangle 
            else: 
                startangle += 90.0

            if sp > 0: 
                if ey < cy: 
                    startangle -= angle*180.0/3.141592
            if sp < 0: 
                if sy < cy: 
                    startangle -= angle*180.0/3.141592
            
            arc = Arc((cx, cy), D, D, theta1=0, theta2=angle*180.0/3.141592, angle=startangle, color='black',  linewidth=0.2)
            ax.add_patch(arc)

            sx = ex
            sy = ey 

            # print ("CIRCL", cx,cy, ex,ey)

        if 'LINE' in word[0].upper(): 
            ex = float(word[2])/1000 + RimPoint[0]
            ey = float(word[1])/1000 + RimPoint[1]

            ax.plot([sx,ex], [sy, ey], color='black', linewidth=0.2 ) 
            # print ("Line", cx,cy, ex,ey)

            sx = ex
            sy = ey 
    

def plot_geometry(imagefile, viewNode, viewElement, Element, Node, Elset, MasterEdges=[], SlaveEdges=[], Press=[], RimContact=[], TreadToRoad=[], TreadBaseEdges=[], BodyToTreadEdges=[], TreadNode=[], **args):

    for key, value in args.items():
        if key == 'Masteredge' or key == 'masteredges' or key == 'masteredge':
            MasterEdges = value
        if key == 'slaveedges' or key == 'Slaveedges' or key == 'slaveedge' or key == 'Slaveedges':
            SlaveEdges = value
        if key == 'press' or key == 'pressure':
            Press = value
        if key == 'rimcontact' or key == 'Rimcontact':
            RimContact = value
        if key == 'Treadtoroad' or key == 'treadtoroad' or key == 'treadroad':
            TreadToRoad = value
        if key == 'treadbaseedges' or key == 'treadbase' : 
            TreadBaseEdges = value
        if key == 'bodytotreadedges' or key == 'bodytotreadedge' : 
            BodyToTreadEdges = value
        if key == 'treadnode' or key == 'Treadnode':
            TreadNode = value

    #    print ('*******************************************************')
    #    print (' View Option (Default - Node No : off, Element No.: Off)')
    #    print ('  - Node Number veiw : node/n=on')
    #    print ('  - Element Number view : element/eL/e=on')
    #    print ('    ex) python ...py n=on e=on')
    #    print ('*******************************************************')

    textsize = 10
    cdepth = 0.8

    NodeSize = 0.1
    viewMembrane = 1
    viewTDNode = 0

    MeshLineWidth = 0.1
    MembWidth = 0.3

    if len(Press) > 0 and len(RimContact) > 0:
        viewSurface = 1
    else:
        viewSurface = 0

    if len(MasterEdges) > 0:
        viewTie = 1
    else:
        viewTie = 0

    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('off')

    i = 0;
    c = 0

    while i < len(Element.Element):
        isBetween = 0
        if Element.Element[i][6] == 3:
            hatch = 0
            N1 = Node.NodeByID(Element.Element[i][1])
            N2 = Node.NodeByID(Element.Element[i][2])
            N3 = Node.NodeByID(Element.Element[i][3])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            x3 = N3[2]
            y3 = N3[3]

            j = 0
            # color = 'b'

            icolor = Color(Element.Element[i][5])

            for m in range(len(Elset.Elset)):
                if Elset.Elset[m][0] == 'BETWEEN_BELTS':
                    isBetween = 1
                    break
            if isBetween == 1:
                for k in range(len(Elset.Elset[m])):
                    if Elset.Elset[m][k] == Element.Element[i][0]:
                        hatch = 1;
                        c += 1
                        break
            if hatch == 1:
                if c == 1:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth * 2, hatch='//', label='BETWEEN BELTS')
                else:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth * 2, hatch='//')
            else:
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
            ax.add_patch(polygon)

            if viewElement == 1:
                plt.text((x1 + x2 + x3) / 3, (y1 + y2 + y3) / 3, Element.Element[i][0], color='blue', size=textsize)

        if Element.Element[i][6] == 4:
            hatch = 0
            N1 = Node.NodeByID(Element.Element[i][1])
            N2 = Node.NodeByID(Element.Element[i][2])
            N3 = Node.NodeByID(Element.Element[i][3])
            N4 = Node.NodeByID(Element.Element[i][4])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            x3 = N3[2]
            y3 = N3[3]
            x4 = N4[2]
            y4 = N4[3]
            j = 0;
            # color = 'b'
            icolor = Color(Element.Element[i][5])
            for m in range(len(Elset.Elset)):
                if Elset.Elset[m][0] == 'BETWEEN_BELTS':
                    isBetween = 1
                    break
            if isBetween == 1:
                for k in range(len(Elset.Elset[m])):
                    if Elset.Elset[m][k] == Element.Element[i][0]:
                        hatch = 1;
                        c += 1
                        break
            if hatch == 1:
                if c == 1:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth, hatch='//', label='BETWEEN BELTS')
                else:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth, hatch='//')
            else:
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
            ax.add_patch(polygon)

            if viewElement == 1:
                plt.text((x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4, Element.Element[i][0], color='blue', size=textsize)

        i += 1

    PressWidth = 0.5
    RimWidth = 0.5
    TDBaseWidth = 0.4
    TieWidth = 0.8
    BDTopWidth = TDBaseWidth * 0.5
    TreadRoadWidth = 0.3

    if viewSurface == 1:
        i = 0
        while i < len(Press):
            N1 = Node.NodeByID(Press[i][0])
            N2 = Node.NodeByID(Press[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            color = Color('PRESS')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=PressWidth, label='Pressure')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=PressWidth)
            i += 1

        i = 0
        while i < len(RimContact):
            N1 = Node.NodeByID(RimContact[i][0])
            N2 = Node.NodeByID(RimContact[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            color = Color('RIM')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=RimWidth, label='Rim Contact', linestyle=':')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=RimWidth, linestyle=':')
            i += 1

    if viewTie == 1:
        j = 0
        iColor = ['midnightblue', 'magenta', 'violet', 'brown', 'aqua', 'coral', 'chocolate',
                  'orange', 'steelblue', 'teal', 'dimgray']

        i = 0
        while i < len(MasterEdges):
            N1 = Node.NodeByID(MasterEdges[i][0])
            N2 = Node.NodeByID(MasterEdges[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            if (i + 1) % len(iColor) == 0 or (i + 1) % len(MasterEdges) == 0:
                j = 0
            else:
                j += 1
            if i == 0:
                plt.plot([x1, x2], [y1, y2], iColor[j], linestyle='-', linewidth=TieWidth, label='Tie Master, White line - Slave')
            else:
                plt.plot([x1, x2], [y1, y2], iColor[j], linestyle='-', linewidth=TieWidth)
            i += 1

        i = 0
        while i < len(SlaveEdges):
            N1 = Node.NodeByID(SlaveEdges[i][0])
            N2 = Node.NodeByID(SlaveEdges[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            plt.plot([x1, x2], [y1, y2], 'white', linewidth=TieWidth * 0.5)
            i += 1

    if len(TreadBaseEdges) > 0:
        i = 0
        while i < len(TreadBaseEdges):
            N1 = Node.NodeByID(TreadBaseEdges[i][0])
            N2 = Node.NodeByID(TreadBaseEdges[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            color = Color('TDBASE')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, linewidth=TDBaseWidth, linestyle='-', label='Tread Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, linewidth=TDBaseWidth, linestyle='-')
            i += 1
    if len(TreadToRoad) > 0:
        i = 0
        while i < len(TreadToRoad):
            N1 = Node.NodeByID(TreadToRoad[i][0])
            N2 = Node.NodeByID(TreadToRoad[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            color = Color('TDROAD')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=TreadRoadWidth, linestyle=':', label='Road Contact Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=TreadRoadWidth, linestyle=':')
            i += 1

    if len(BodyToTreadEdges) > 0:
        i = 0
        while i < len(BodyToTreadEdges):
            N1 = Node.NodeByID(BodyToTreadEdges[i][0])
            N2 = Node.NodeByID(BodyToTreadEdges[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            color = Color('BDTOP')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=BDTopWidth, linestyle=':', label='Body Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=BDTopWidth, linestyle=':')
            i += 1

    i = 0
    while i < len(Element.Element):
        if Element.Element[i][6] == 2:
            N1 = Node.NodeByID(Element.Element[i][1])
            N2 = Node.NodeByID(Element.Element[i][2])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]

            color = Color("MEMB")
            if viewMembrane == 1:
                plt.plot([x1, x2], [y1, y2], color, lw=MembWidth)
                if viewElement == 1:
                    plt.text((x1 + x2) / 2, (y1 + y2) / 2, Element.Element[i][0], color=color, size=textsize)
        i += 1

    # View Nodes In Tread
    x = [];
    y = []  # NodeX
    i = 0
    if viewTDNode == 1:
        while i < len(TreadNode):
            x.append(TreadNode[i][2] * -1)
            y.append(TreadNode[i][3])
            i += 1
        color = Color("DOT")
        plt.scatter(x, y, color=color, s=NodeSize, marker='o', label='Tread Nodes')

    # View All Nodes
    x = [];
    y = []  # NodeX
    i = 0
    while i < len(Node.Node):
        x.append(Node.Node[i][2] * -1)
        y.append(Node.Node[i][3])
        i += 1

    if viewNode == 1:
        Num = len(Node.Node)
        ax.scatter(x, y)
        i = 0
        for i, txt in enumerate(Num):
            ax.annotate(txt, (x[i], y[i]), size=textsize)

    # first_legend=plt.legend(handles=[TreadNode], loc=1)
    # leg = ax.legend(loc='upper left', frameon=False, fontsize=5)
    # leg.get_frame().set_alpha(0.4)
    #    items=[nodeText]

    # plt.show()
    # plt.subplots_adjust(wspace=0.001, hspace=0.001)
    plt.savefig(imagefile, dpi=300)
    plt.clf()

    return 1

def plot_lines(imagefileName, Line, Line1=[], Line2=[], Line3=[], Line4=[], Line5=[], **args):
    
    for key, value in args.items():
        if key == 'line1' or key == 'l1' or key == 'L1':
            Line1= value
        if key == 'line2' or key == 'l2' or key == 'L2':
            Line1= value
        if key == 'line3' or key == 'l3' or key == 'L3':
            Line1= value
        if key == 'line4' or key == 'l4' or key == 'L4':
            Line1= value
        if key == 'line5' or key == 'l5' or key == 'L5':
            Line1= value
            
            
    
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('off')
    bar = '-'
    L0c = 'gray'
    L1c = 'gray'
    L2c = 'red'
    L3c = 'red'
    L4c = 'gray'
    L5c = 'orange'
    LineWidth = 0.2

    # Line = [[x11, y11, x12, y12], [x21, y21, x22, y22], [ ... ], ...]
    # you can make Line of list with function below
    # freeEdges= FindElsetFreeEdges(element, Elsetname)
    # Line = MakeLineSetsForPlots(freeEdges, Node)
    # line style = '-'

    N0 = len(Line)
    N1 = len(Line1)
    N2 = len(Line2)
    N3 = len(Line3)
    N4 = len(Line4)
    N5 = len(Line5)

    for i in range(N0):
        plt.plot([Line[i][0], Line[i][2]], [Line[i][1], Line[i][3]], L0c, lw=LineWidth, linestyle=bar)
    for i in range(N1):
        plt.plot([Line1[i][0], Line1[i][2]], [Line1[i][1], Line1[i][3]], L1c, lw=LineWidth, linestyle=bar)
    for i in range(N2):
        plt.plot([Line2[i][0], Line2[i][2]], [Line2[i][1], Line2[i][3]], L2c, lw=LineWidth, linestyle=bar)
    for i in range(N3):
        plt.plot([Line3[i][0], Line3[i][2]], [Line3[i][1], Line3[i][3]], L3c, lw=LineWidth, linestyle=bar)
    for i in range(N4):
        plt.plot([Line4[i][0], Line4[i][2]], [Line4[i][1], Line4[i][3]], L4c, lw=LineWidth, linestyle=bar)
    for i in range(N5):
        plt.plot([Line5[i][0], Line5[i][2]], [Line5[i][1], Line5[i][3]], L5c, lw=LineWidth, linestyle=bar)

    plt.savefig(imagefileName, dpi=200)
    plt.clf()

def Plot_OuterEdgeComparison(ImageFileName, Element, Node1, Node2, dpi=200, Node3=NODE(), L1='', L2='', L3='', xlabel='', ylabel='', **args):
    """
    Element : Element Class
    Node : Node Class
    L1 : Label of the Node1, L2 : Label of the Node2, L3 : Label of the Node3

    """
    for key, value in args.items():
        if key == 'node3':
            Node3 = value
        if key == 'l1':
            L1 = value
        if key == 'l2':
            L2 = value
        if key == 'l3':
            L3 = value
    
    
    OuterEdge = Element.OuterEdge(Node1)

    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('on')

    xList = []
    yList = []
    LineWidth = 0.5
    textsize = 8
    plt.ylabel(ylabel, fontsize=textsize)
    plt.xlabel(xlabel, fontsize=textsize)
    plt.xticks(size=textsize)
    plt.yticks(size=textsize)

    N = len(OuterEdge.Edge)
    for i in range(N):
        N1 = Node1.NodeByID(OuterEdge.Edge[i][0])
        N2 = Node1.NodeByID(OuterEdge.Edge[i][1])
        color = 'black'
        if L1 and i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, lw=LineWidth, label=L1)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, lw=LineWidth)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
        N1 = Node2.NodeByID(OuterEdge.Edge[i][0])
        N2 = Node2.NodeByID(OuterEdge.Edge[i][1])
        color = 'red'
        if L2 and i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, lw=LineWidth, label=L2)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, lw=LineWidth)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
        if len(Node3.Node) > 0:
            N1 = Node3.NodeByID(OuterEdge.Edge[i][0])
            N2 = Node3.NodeByID(OuterEdge.Edge[i][1])
            color = 'blue'
            if L3 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, lw=LineWidth, label=L3)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, lw=LineWidth)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])

    MinX = 100000.0
    MaxX = -100000.0
    MinY = 100000.0
    MaxY = -100000.0

    N = len(xList)
    for i in range(N):
        if MinX > xList[i]:
            MinX = xList[i]
        if MaxX < xList[i]:
            MaxX = xList[i]
        if MinY > yList[i]:
            MinY = yList[i]
        if MaxY < yList[i]:
            MaxY = yList[i]

    plt.xlim(MinX - 0.01, MaxX + 0.01)
    plt.ylim(MinY - 0.05, MaxY + 0.05)
    if L1 or L2 or L3:
        plt.legend(fontsize=textsize)
    plt.savefig(ImageFileName, dpi=dpi)
    plt.clf()

def Plot_LayoutCompare(ImageFileName, L1="", L2="", E1="", N1="", E2="", N2="", xlabel='', ylabel='', **args):
    title =''
    viewaxis = 0
    lt1 = '-'
    lt2 = '-';    
    textsize = 8
    dpi = 150
    LineWidth = 0.5
    for key, value in args.items():
        if key == 'title':       title = value
        if key == 'axis':        viewaxis = value
        if key == 'tsize' or key == 'textsize':     textsize = value
        if key == "lw" or key == 'linewidth':       LineWidth = value
        if key == 'dpi':         dpi = value

    Node1 = N1;     Node2=N2 
    Element = E1;   dElement = E2

    bOuter = Element.OuterEdge(Node1)
    dOuter = dElement.OuterEdge(Node2)

    bCarcass = Element.ElsetToEdge("C01")
    dCarcass = dElement.ElsetToEdge("C01")
    bBT = Element.ElsetToEdge("BT3")
    if len(bBT.Edge) ==0:
        bBT = Element.ElsetToEdge("BT1")
        dBT = dElement.ElsetToEdge("BT1")
        bBT.Combine(Element.ElsetToEdge("BT2"))
        dBT.Combine(dElement.ElsetToEdge("BT2"))
    else:
        bBT = Element.ElsetToEdge("BT2")
        dBT = dElement.ElsetToEdge("BT2")
        bBT.Combine(Element.ElsetToEdge("BT3"))
        dBT.Combine(dElement.ElsetToEdge("BT3"))
    
    bOuter.Combine(bCarcass)
    bOuter.Combine(bBT)
    dOuter.Combine(dCarcass)
    dOuter.Combine(dBT)

    BDR  = Element.Elset("BEAD_R")
    BDL = Element.Elset("BEAD_L")
    if len(BDL.Element) ==0:
        i=0
        while i < len(BDR.Element):
            if BDR.Element[i][8] > 0:
                BDL.Add(BDR.Element[i])
                del(BDR.Element[i])
                i-=1
            i += 1
    if len(BDR.Element) ==0:
        i=0
        while i < len(BDL.Element):
            if BDL.Element[i][8] < 0:
                BDR.Add(BDL.Element[i])
                del(BDL.Element[i])
                i-=1
            i += 1

    BDedge = BDL.OuterEdge(Node1)
    BDRedge = BDR.OuterEdge(Node1)
    BDedge.Combine(BDRedge)
    bOuter.Combine(BDedge)

    BDR  = dElement.Elset("BEAD_R")
    BDL = dElement.Elset("BEAD_L")
    if len(BDL.Element) ==0:
        i=0
        while i < len(BDR.Element):
            if BDR.Element[i][8] > 0:
                BDL.Add(BDR.Element[i])
                del(BDR.Element[i])
                i-=1
            i += 1
    if len(BDR.Element) ==0:
        i=0
        while i < len(BDL.Element):
            if BDL.Element[i][8] < 0:
                BDR.Add(BDL.Element[i])
                del(BDL.Element[i])
                i-=1
            i += 1

    BDedge = BDL.OuterEdge(Node1)
    BDRedge = BDR.OuterEdge(Node1)
    BDedge.Combine(BDRedge)
    dOuter.Combine(BDedge)

    plt.clf()
    fig, ax = plt.subplots()


    ax.axis('equal')
    if viewaxis == 0:
        ax.axis('off')
    else:
        ax.axis("on")

    xList = []
    yList = []
    

    if title != '':
        plt.title(title, fontsize=textsize )

    for i, Edge in enumerate(bOuter.Edge):
        N1 = Node1.NodeByID(Edge[0])
        N2 = Node1.NodeByID(Edge[1])
        color = 'black'
        if L1 !="" and i ==0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, label=L1, linestyle=lt1)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt1)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
    for i, Edge in enumerate(dOuter.Edge):
        N1 = Node2.NodeByID(Edge[0])
        N2 = Node2.NodeByID(Edge[1])
        color = 'red'
        if L2 !="" and i ==0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, label=L2, linestyle=lt2)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt2)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])


    MinX = 100000.0
    MaxX = -100000.0
    MinY = 100000.0
    MaxY = -100000.0

    N = len(xList)
    for i in range(N):
        if MinX > xList[i]:
            MinX = xList[i]
        if MaxX < xList[i]:
            MaxX = xList[i]
        if MinY > yList[i]:
            MinY = yList[i]
        if MaxY < yList[i]:
            MaxY = yList[i]

    plt.xlim(MinX - 0.01, MaxX + 0.01)
    plt.ylim(MinY - 0.01, MaxY + 0.02)
    if L1 !="" or L2 !="" :
        plt.legend(fontsize=textsize, frameon=False)
    plt.savefig(ImageFileName, dpi=dpi)
    plt.clf()


def Plot_EdgeComparison(ImageFileName, Edge, Node1, Node2, dpi=200, Node3=NODE(), L1='', L2='', L3='', xlabel='', ylabel='', Node4=NODE(), Node5=NODE(), Node6=NODE(), L4='', L5='', L6='', **args):
    title =''
    viewaxis = 0
    subplot = 0 
    lt1 = '-';     lt2 = '-';     lt3 = '-';     lt4 = '-';     lt5 = '-';     lt6 = '-'
    for key, value in args.items():
        if key == 'node3':            Node3 = value       
        if key == 'node4':            Node4 = value
        if key == 'node5':            Node5 = value
        if key == 'node6':            Node6 = value
            
        if key == 'l1':            L1 = value
        if key == 'l2':            L2 = value
        if key == 'l3':            L3 = value
        if key == 'l4':            L4 = value
        if key == 'l5':            L5 = value
        if key == 'l6':            L6= value
        if key == 'title':         title = value
        if key == 'axis':          viewaxis = value
        if key == "subplot":       subplot = value
        if key == "plt":           f = value 

        if key == 'linestyle' or key == 'ls': 
            lt1 = value; lt2 = value;  lt3 = value; lt4 = value; lt5 = value; lt6 = value
        if key == 'linestyle1' or key=="ls1":     lt1 = value
        if key == 'linestyle2' or key=="ls2":     lt2 = value
        if key == 'linestyle3' or key=="ls3":     lt3 = value
        if key == 'linestyle4' or key=="ls4":     lt4 = value
        if key == 'linestyle5' or key=="ls5":     lt5 = value
        if key == 'linestyle6' or key=="ls6":     lt6 = value

    if subplot == 0:
        fig, ax = plt.subplots()
    else:
        ax = f.add_subplot(subplot)
        
    ax.axis('equal')
    if viewaxis == 0:
        ax.axis('off')
    else:
        ax.axis("on")

    xList = []
    yList = []
    LineWidth = 0.5
    textsize = 8
    plt.ylabel(ylabel, fontsize=textsize)
    plt.xlabel(xlabel, fontsize=textsize)
    plt.xticks(size=textsize)
    plt.yticks(size=textsize)

    if title != '':
        plt.title(title, fontsize=textsize )

    N = len(Edge.Edge)
    for i in range(N):
        N1 = Node1.NodeByID(Edge.Edge[i][0])
        N2 = Node1.NodeByID(Edge.Edge[i][1])
        color = 'black'
        if L1 and i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, label=L1, linestyle=lt1)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt1)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
        N1 = Node2.NodeByID(Edge.Edge[i][0])
        N2 = Node2.NodeByID(Edge.Edge[i][1])
        color = 'red'
        if L2 and i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, label=L2, linestyle=lt2)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt2)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
        if len(Node3.Node) > 0:
            N1 = Node3.NodeByID(Edge.Edge[i][0])
            N2 = Node3.NodeByID(Edge.Edge[i][1])
            color = 'blue'
            linetype ='-'
            if L3 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L3, linestyle=lt3)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt3)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(Node4.Node) > 0:
            N1 = Node4.NodeByID(Edge.Edge[i][0])
            N2 = Node4.NodeByID(Edge.Edge[i][1])
            color = 'green'
            linetype ='-'
            if L4 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L4, linestyle=lt4)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt4)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(Node5.Node) > 0:
            N1 = Node5.NodeByID(Edge.Edge[i][0])
            N2 = Node5.NodeByID(Edge.Edge[i][1])
            color = 'gray'
            linetype ='-'
            if L5 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L5, linestyle=lt5)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt5)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(Node6.Node) > 0:
            N1 = Node6.NodeByID(Edge.Edge[i][0])
            N2 = Node6.NodeByID(Edge.Edge[i][1])
            color = 'gray'
            linetype ='--'
            if L6 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L6, linestyle=lt6)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt6)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])

    MinX = 100000.0
    MaxX = -100000.0
    MinY = 100000.0
    MaxY = -100000.0

    N = len(xList)
    for i in range(N):
        if MinX > xList[i]:
            MinX = xList[i]
        if MaxX < xList[i]:
            MaxX = xList[i]
        if MinY > yList[i]:
            MinY = yList[i]
        if MaxY < yList[i]:
            MaxY = yList[i]

    plt.xlim(MinX - 0.01, MaxX + 0.01)
    plt.ylim(MinY - 0.01, MaxY + 0.02)
    if L1 or L2 or L3:
        plt.legend(fontsize=textsize, frameon=False)
    if subplot == 0:
        plt.savefig(ImageFileName, dpi=dpi)
        plt.clf()

def Plot_InflatedProfile(ImageFileName, Edge, Node1, Node2, dpi=200, Node3=NODE(), L1='', L2='', L3='', xlabel='', ylabel='', Node4=NODE(), Node5=NODE(), Node6=NODE(), L4='', L5='', L6='', **args):
    title =''
    viewaxis = 0
    subplot = 0 
    lt1 = '-';     lt2 = '-';     lt3 = '-';     lt4 = '-';     lt5 = '-';     lt6 = '-'
    LSH_Dimension=[]
    TOE_Dim = []
    for key, value in args.items():
        if key == 'node3':            Node3 = value       
        if key == 'node4':            Node4 = value
        if key == 'node5':            Node5 = value
        if key == 'node6':            Node6 = value
            
        if key == 'l1':            L1 = value
        if key == 'l2':            L2 = value
        if key == 'l3':            L3 = value
        if key == 'l4':            L4 = value
        if key == 'l5':            L5 = value
        if key == 'l6':            L6= value
        if key == 'title':         title = value
        if key == 'axis':          viewaxis = value
        if key == "subplot":       subplot = value
        if key == "plt":           f = value 

        if key == 'linestyle' or key == 'ls': 
            lt1 = value; lt2 = value;  lt3 = value; lt4 = value; lt5 = value; lt6 = value
        if key == 'linestyle1' or key=="ls1":     lt1 = value
        if key == 'linestyle2' or key=="ls2":     lt2 = value
        if key == 'linestyle3' or key=="ls3":     lt3 = value
        if key == 'linestyle4' or key=="ls4":     lt4 = value
        if key == 'linestyle5' or key=="ls5":     lt5 = value
        if key == 'linestyle6' or key=="ls6":     lt6 = value

        if key == "lsh": LSH_Dimension = value 
        if key == 'toe': TOE_Dim=value


    if subplot == 0:
        fig, ax = plt.subplots()
    else:
        ax = f.add_subplot(subplot)
        
    ax.axis('equal')
    if viewaxis == 0:
        ax.axis('off')
    else:
        ax.axis("on")

    xList = []
    yList = []
    LineWidth = 0.5
    textsize = 8
    plt.ylabel(ylabel, fontsize=textsize)
    plt.xlabel(xlabel, fontsize=textsize)
    plt.xticks(size=textsize)
    plt.yticks(size=textsize)

    if title != '':
        plt.title(title, fontsize=textsize )

    N = len(Edge.Edge)
    for i in range(N):
        N1 = Node1.NodeByID(Edge.Edge[i][0])
        N2 = Node1.NodeByID(Edge.Edge[i][1])
        color = 'black'
        if L1 and i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, label=L1, linestyle=lt1)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt1)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
        N1 = Node2.NodeByID(Edge.Edge[i][0])
        N2 = Node2.NodeByID(Edge.Edge[i][1])
        color = 'red'
        if L2 and i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, label=L2, linestyle=lt2)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt2)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
        if len(Node3.Node) > 0:
            N1 = Node3.NodeByID(Edge.Edge[i][0])
            N2 = Node3.NodeByID(Edge.Edge[i][1])
            color = 'blue'
            linetype ='-'
            if L3 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L3, linestyle=lt3)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt3)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(Node4.Node) > 0:
            N1 = Node4.NodeByID(Edge.Edge[i][0])
            N2 = Node4.NodeByID(Edge.Edge[i][1])
            color = 'green'
            linetype ='-'
            if L4 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L4, linestyle=lt4)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt4)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(Node5.Node) > 0:
            N1 = Node5.NodeByID(Edge.Edge[i][0])
            N2 = Node5.NodeByID(Edge.Edge[i][1])
            color = 'gray'
            linetype ='-'
            if L5 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L5, linestyle=lt5)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt5)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(Node6.Node) > 0:
            N1 = Node6.NodeByID(Edge.Edge[i][0])
            N2 = Node6.NodeByID(Edge.Edge[i][1])
            color = 'gray'
            linetype ='--'
            if L6 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L6, linestyle=lt6)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, linestyle=lt6)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])

    

    MinX = 100000.0
    MaxX = -100000.0
    MinY = 100000.0
    MaxY = -100000.0

    N = len(xList)
    for i in range(N):
        if MinX > xList[i]:
            MinX = xList[i]
        if MaxX < xList[i]:
            MaxX = xList[i]
        if MinY > yList[i]:
            MinY = yList[i]
        if MaxY < yList[i]:
            MaxY = yList[i]

    if len(LSH_Dimension)> 0: 
        ## LSH_Dimension = ["Dimension_Value", Dimension_Position_1 [x, y], Position_2 [x, y] ]
        # plt.plot([LSH_Dimension[1][0], LSH_Dimension[2][0]], [LSH_Dimension[1][1], LSH_Dimension[2][1]], 'gray', linewidth=LineWidth*0.2, linestyle=lt6)

        ax.plot([MaxX+0.01, MaxX+0.01], [LSH_Dimension[1][1], LSH_Dimension[2][1]], ".")
        connectionstyle = "arc3,rad=0"  ## rad = value : the radius of the connecting curve 
        ax.annotate("",
                xy=(MaxX+0.01, LSH_Dimension[1][1]), xycoords='data',
                xytext=(MaxX+0.01, LSH_Dimension[2][1]), textcoords='data',
                arrowprops=dict(arrowstyle="<->", color="0.5",
                                shrinkA=5, shrinkB=5,
                                patchA=None, patchB=None,
                                connectionstyle=connectionstyle,
                                ),
                )

        plt.text(MaxX+0.013, (LSH_Dimension[1][1] + LSH_Dimension[2][1])/2.0, LSH_Dimension[0], fontsize=7) 
        plt.text(MaxX+0.013, (LSH_Dimension[1][1] + LSH_Dimension[2][1])/2.0+0.01, "Deformed", fontsize=7) 
        plt.text(MaxX-0.01, LSH_Dimension[1][1]-0.01, "Mold Rim R="+str(round(LSH_Dimension[1][1]*1000, 1)), fontsize=7) 
        print ("## Dimension_LSH is added")
    if len(TOE_Dim) > 0: 
        Initial_shiftX = 0.008; Deformed_shiftx = 0.015
        InitX = TOE_Dim[0][1]+Initial_shiftX; DeformX = TOE_Dim[1][1]+Deformed_shiftx
        plt.scatter ([InitX, DeformX], [TOE_Dim[0][2], TOE_Dim[1][2]], s=1) 

        if abs(TOE_Dim[0][2] - TOE_Dim[1][2]) <0.05: 
            if TOE_Dim[0][2] > TOE_Dim[1][2] : 
                Initial_shifty = 0.0025; Deformed_shifty = -0.0025; 
            else: 
                Initial_shifty = -0.0025; Deformed_shifty = 0.0025; 
        else:
            Initial_shifty = 0.0; Deformed_shifty = 0.0; 
        plt.text(DeformX+0.005,TOE_Dim[0][2]+Initial_shifty, TOE_Dim[0][0], fontsize=7 )
        plt.text(DeformX+0.005,TOE_Dim[1][2]+Deformed_shifty, TOE_Dim[1][0], fontsize=7 )

        connectionstyle = "arc3,rad=0"  ## rad = value : the radius of the connecting curve 
        ax.annotate("",
                xy=(InitX, TOE_Dim[0][2]), xycoords='data',
                xytext=(InitX, TOE_Dim[1][2]-0.05), textcoords='data',
                arrowprops=dict(arrowstyle="->", color="0.5",
                                shrinkA=5, shrinkB=5,
                                patchA=None, patchB=None,
                                connectionstyle=connectionstyle,
                                ),
                )
        ax.annotate("",
                xy=(DeformX,  TOE_Dim[1][2]), xycoords='data',
                xytext=(DeformX,  TOE_Dim[1][2]-0.05), textcoords='data',
                arrowprops=dict(arrowstyle="->", color="0.5",
                                shrinkA=5, shrinkB=5,
                                patchA=None, patchB=None,
                                connectionstyle=connectionstyle,
                                ),
                )
        print ("## Dimension_TOE is added")


    plt.xlim(MinX - 0.02, MaxX + 0.04)
    plt.ylim(MinY - 0.02, MaxY + 0.03)
    if L1 or L2 or L3:
        plt.legend(fontsize=textsize, frameon=False)
    if subplot == 0:
        plt.savefig(ImageFileName, dpi=dpi)
        plt.clf()

def Plot_Graph(ImageFileName, Data, title='', xlabel='', ylabel='', dpi=200, marker='', markersize=3, c1='black', c2='red', c3='blue', c4='green', c5='lightpink', equalxy=0, grid=1, axis=1, annotate=[], annotate_position=[], **args):
    """
    :param ImageFileName:
    :param Data: [[Data_name, [X, Value], [X, Value], [...]],    [...]      ]
    :param dpi: Image Size
    :return:
    """


    fig = plt.figure()
    textsize = 8
    plt.xticks(size=textsize)
    plt.yticks(size=textsize)
    plt.ylabel(ylabel, fontsize=textsize)
    plt.xlabel(xlabel, fontsize=textsize)
    plt.title(title, fontsize=textsize+1)
    if grid != 0:
        plt.grid()  
    if equalxy != 0:
        plt.axis('equal')
    if axis == 0:
        plt.axis("off")
    

    N = len(Data)
    yMax =-1000000.0 
    yMin = 10000000.0
    xMin = 10000000.0
    xMax = -100000000.0
    for i in range(N):
        M = len(Data[i])
        Pos = []
        Val = []
        for j in range(1, M):
            Pos.append(Data[i][j][0])
            Val.append(Data[i][j][1])
            
            if yMax < Data[i][j][1]: 
                yMax = Data[i][j][1]
            if yMin > Data[i][j][1]: 
                yMin = Data[i][j][1]
            
            if xMin > Data[i][j][0]: 
                xMin = Data[i][j][0]
            if xMax < Data[i][j][0]:
                xMax = Data[i][j][0]
            # print (Data[i][0], ',', Data[i][j][0], ',', Data[i][j][1])
        if i % 5 == 0:
            iColor = c1
        elif i % 5 == 1:
            iColor = c2
        elif i % 5 == 2:
            iColor = c3
        elif i % 5 == 3:
            iColor = c4
        else:
            iColor = c5

        if int(i / 5) == 0:
            ls = '-'
            lw = 1
        elif int(i / 5) == 1:
            ls = '--'
            lw = 0.5
        elif int(i / 5) == 2:
            ls = '-.'
            lw = 0.25
        else:
            ls = ':'
            lw = 0.1

        plt.plot(Pos, Val, color=iColor, linestyle=ls, linewidth=lw, label=str(Data[i][0]), marker=marker, markersize=markersize, markeredgecolor='none')
    plt.legend(fontsize=8, frameon=False, loc='upper left')
    
    if xMin > 0 : 
        plt.xlim(xMin * 0.95,  xMax*1.05)
    elif xMax < 0: 
        plt.xlim(xMin * 1.05,  xMax*0.95)
    else: 
        plt.xlim(xMin * 1.05,  xMax*1.05)
        
    if yMin > 0: 
        plt.ylim(yMin*0.75, yMax *1.25)
    elif yMax < 0: 
        plt.ylim(yMin*1.05, yMax *0.75)
    else: 
        plt.ylim(yMin*1.05, yMax *1.25)

    if len(annotate) > 0: 
        if len(annotate_position) > 0: 
            if annotate[0][1] > annotate[1][1] : 
                uptext = annotate_position[0] + 1
                dwtext = annotate_position[1]  
            else: 
                uptext = annotate_position[1] 
                dwtext = annotate_position[0] +2 
        else: 
            uptext = annotate[0][1] 
            dwtext =  annotate[0][1]

        for i, ann in enumerate(annotate): 
            if i%2 == 0: pos = uptext
            else: pos = dwtext
            if annotate[0][1] > annotate[1][1] : 
                plt.annotate("", xy=(ann[0], ann[1]), xytext=(ann[0]+10, pos), arrowprops={'arrowstyle':'->', 'color':'0.5'})
                plt.text (ann[0]+10, pos, str(round(ann[1], 2)), fontsize=8, color='gray')
            else: 
                plt.annotate("", xy=(ann[0], ann[1]), xytext=(ann[0]+10, pos), arrowprops={'arrowstyle':'->', 'color':'0.5'})
                plt.text (ann[0]+10, pos, str(round(ann[1], 2)), fontsize=8, color='gray')
            
    
    plt.savefig(ImageFileName, dpi=dpi)
    plt.clf()

def Plot_XYList(ImageFileName, Data, marker = "o", size=1.0, vmin=0.0, vmax=0.0, linestyle='-',  title='', xlabel='', ylabel='', linewidth=1,  color='black', dpi=200, grid=1, axis = 1, equalxy=0,  edgecolor='', xmin='', xmax='', value=0, **args):
    """
    :param ImageFileName:
    :param Data: [[X, Value], [X, Value], [...]   ]
    :param dpi: Image Size
    :return:
    """
    plt.figure()
    
    textsize = 8
    plt.xticks(size=textsize)
    plt.yticks(size=textsize)
    plt.ylabel(ylabel, fontsize=textsize)
    plt.xlabel(xlabel, fontsize=textsize)
    plt.title(title, fontsize=textsize+1)
    if grid != 0:
        plt.grid()
    if axis == 0:
        plt.axis("off")
    if equalxy == 1:
        plt.axis('equal')

    M = len(Data)
    Pos = []
    Val = []
    Min = 1000000000000.0
    Max = -1000000000000.0
                
    if M > 0:
        
        if len(Data[0]) == 2: 
            for j in range(M):
                Pos.append(Data[j][0])
                Val.append(Data[j][1])
                if Data[j][1] > Max:
                    Max = Data[j][1] 
                if Data[j][1] < Min:
                    Min = Data[j][1]
                if value !=0:
                    plt.annotate(str(Data[j][1]), (Data[j][0], Data[j][1]), textcoords ="offset points", xytext=(0, 10), ha="center")
                
        if len(Data[0]) == 3: 
            clr = []
            
            for j in range(M):
                Pos.append(Data[j][0])
                Val.append(Data[j][1])   
                clr.append(Data[j][2])
                if value !=0:
                    plt.annotate(str(Data[j][1]), (Data[j][0], Data[j][1]), textcoords ="offset points", xytext=(0, 10), ha="center")
                if Data[j][2] > Max:
                    Max = Data[j][2]
                if Data[j][2] < Min:
                    Min = Data[j][2] 
            if vmin == 0.0:
                vmin = Min
            if vmax == 0.0:
                vmax = Max
               
        if len(Data[0]) == 2:     
            plt.plot(Pos, Val, color=color, linestyle=linestyle, linewidth=linewidth, marker=marker, markersize=size) # ,  markeredgecolor=edgecolor) 
        elif len(Data[0]) == 3:
            # from matplotlib.cm import cm
            # print ("Colored Dot")
            plt.scatter(Pos, Val, c=clr, s=size, marker=marker, vmin=vmin, vmax=vmax, edgecolor=edgecolor)
        
        if xmin!="" or xmax !="":
            plt.xlim(xmin, xmax)
        Max = Max + abs(Data[j][1])*0.3
        Min = Min - abs(Data[j][1])*0.3
        plt.ylim(Min, Max)
        plt.savefig(ImageFileName, dpi=dpi )
        plt.clf()
    else:
        plt.savefig(ImageFileName, dpi=dpi )
        print ("* Cannot PLOT!! No Data in the LIST")

def Plot_ProfileLiftStaticInflation(ImageName, TW, TDPointGap, OuterNodePosition1FileNames, SimConditions,  Offset= 10000, TreadNumber = 10000000, **args):
    """
    This is post-processing only for Static Inflation Analysis
    SimConditions = [RW, P1, P2(, P3)], P1 < P2 < P3
    Results from 'SFRIC'
    """
    group = 'pcr'
    for key, value in args.items():
        if key == 'offset':
            Offset = int(value)
        if key == 'treadno' or key == 'treadnumber':
            TreadNumber = int(value)
        if key == 'group':
            group = value
        if key == 'edge':
            outer = value 
    
    CriticalAngle = 50.0  # for groove Detection
    xMax = TW / 2.0 - 10
    xMin = -TW / 2.0 + 10
    iDivision = int((xMax - xMin) / TDPointGap) + 1
    X = []
    for i in range(iDivision):
        # X.append((xMin/1000.0 + TDPointGap * float(i)) / 1000)
        X.append((-TDPointGap/2.0 * float(iDivision ) + TDPointGap * float(i)) / 1000)  # Point X to calculate Crown Lift
    # lslope = 10.0  # above this angle -> strange data
    # lAngle = 1.0   # below this value (difference between points) -> normal data
    # ht = 1.0 / 10.0 * TDPointGap  # if lift value gap is over ht -> strange data
    # RW = str(SimConditions[0])
    # P1 = str(SimConditions[1])
    # P2 = str(SimConditions[2])
    
    MinNode=NODE()
    MidNode=NODE()
    MaxNode=NODE()
    InN = len(OuterNodePosition1FileNames)
    MinNode = OuterNodePosition1FileNames[0]
    for node in MinNode.Node:
        node[0] = node[0]%Offset
    MidNode = OuterNodePosition1FileNames[1]
    for node in MidNode.Node:
        node[0] = node[0]%Offset
    if InN ==3 :
        MaxNode = OuterNodePosition1FileNames[2]
        for node in MaxNode.Node:
            node[0] = node[0]%Offset
   
    
    MinEdge=EDGE()
    MidEdge=EDGE()
    MaxEdge=EDGE()
    for edge in outer.Edge:
        N1= MinNode.NodeByID(edge[0])
        N2= MinNode.NodeByID(edge[1])
        length = math.sqrt((N1[1]-N2[1])*(N1[1]-N2[1]) + (N1[2]-N2[2])*(N1[2]-N2[2]) + (N1[3]-N2[3])*(N1[3]-N2[3]))
        MinEdge.Add([N1[0], N2[0], edge[2], 0, edge[4], length, 0, 0, 1])      
        MidEdge.Add([N1[0], N2[0], edge[2], 0, edge[4], length, 0, 0, 1])
        
        if InN ==3:
            MaxEdge.Add([N1[0], N2[0], edge[2], 0, edge[4], length, 0, 0, 1])
    # print ("START TO PLOT")
    # if 'RW1' in ImageName:
    #     SubImage = ImageName[:-20] + 'Profile1.png'
    # elif 'RW2' in ImageName:
    #     SubImage = ImageName[:-20] + 'Profile2.png'
    # elif 'RW3' in ImageName:
    #     SubImage = ImageName[:-20] + 'Profile3.png'
    # else:
    #     SubImage = ImageName[:-20] + 'Profile.png'
    # if InN == 3:
    #     Plot_EdgeComparison(SubImage, MidEdge, MinNode, MidNode, 200, MaxNode, 'Pressure=' + str(SimConditions[1]) + '[kgf/cm2]', 'Pressure=' + str(SimConditions[2]) + '[kgf/cm2]', 'Pressure=' + str(SimConditions[3]) + '[kgf/cm2]', title="Profile Comparison on "+str(format(SimConditions[0]/25.4, ".2f"))+" Rim")
    # else:
    #     Plot_EdgeComparison(SubImage, MidEdge, MinNode, MidNode, 200, MaxNode, 'Pressure=' + str(SimConditions[1]) + '[kgf/cm2]', 'Pressure=' + str(SimConditions[2]) + '[kgf/cm2]', title="Profile Comparison on "+str(format(SimConditions[0]/25.4, ".2f"))+" Rim") # , 'Pressure=' + str(SimConditions[3]) + '[kgf/cm2]')

    # MidEdge=GrooveDetectionFromEdge(MidEdge, MidNode, 0)
    # MidEdge= DeleteGrooveEdgeAfterGrooveDetection(NoGrooveEdge, MidNode)
    # NoGrooveEdge.Image(MidNode, 'Mid Profile without Groove')
    # print ("END EDGE COMP")
    # def ImageNode(node1, file="NODE", dpi=100, XY=23, size=1.0, marker='o', cm=0, ci=4, vmin='', vmax='', equalxy=1, **args):
    # ImageNode(MinNode, file="NODES", dpi=200, xy=23, size=1.0, n2=MidNode, n3=MaxNode)
    
    #### Groove Node Detection and Delete
    TEdge = EDGE()
    N = len(MidEdge.Edge)
    for i in range(N):
        if MidEdge.Edge[i][2] == "CTR" or MidEdge.Edge[i][2] == "CTB" or MidEdge.Edge[i][2] == "SUT" or MidEdge.Edge[i][2] == "UTR" or MidEdge.Edge[2] == "TRW":
            TEdge.Add(MidEdge.Edge[i])
    # if 'RW1' in ImageName:
    #     SubImage = ImageName[:-20] + 'Crown1.png'
    # elif 'RW2' in ImageName:
    #     SubImage = ImageName[:-20] + 'Crown2.png'
    # elif 'RW3' in ImageName:
    #     SubImage = ImageName[:-20] + 'Crown3.png'
    # else:
    #     SubImage = ImageName[:-20] + 'Crown.png'
    # if InN == 3:
    #     Plot_EdgeComparison(SubImage, TEdge, MinNode, MidNode, 200, MaxNode, 'Pressure=' + str(SimConditions[1]) + '[kgf/cm2]', 'Pressure=' + str(SimConditions[2]) + '[kgf/cm2]', 'Pressure=' + str(SimConditions[3]) + '[kgf/cm2]', title="Profile Comparison on "+str(format(SimConditions[0]/25.4, ".2f"))+" Rim")
    # else: 
    #     Plot_EdgeComparison(SubImage, TEdge, MinNode, MidNode, 200, MaxNode, 'Pressure=' + str(SimConditions[1]) + '[kgf/cm2]', 'Pressure=' + str(SimConditions[2]) + '[kgf/cm2]', title="Profile Comparison on "+str(format(SimConditions[0]/25.4, ".2f"))+" Rim") # , 'Pressure=' + str(SimConditions[3]) + '[kgf/cm2]')
    TEdge = GrooveDetectionFromEdge(TEdge, MidNode, 1)

    ## Delete Groove
    i = 0
    while i < len(TEdge.Edge) - 1:
        if TEdge.Edge[i][6] == 1 and TEdge.Edge[i][7] == 1:
            for j in range(len(MidEdge.Edge)):
                if TEdge.Edge[i][0] == MidEdge.Edge[j][0] and TEdge.Edge[i][1] == MidEdge.Edge[j][1]:
                    MidEdge.Delete(j)
                    MinEdge.Delete(j)
                    if InN == 3:
                        MaxEdge.Delete(j)
                    break
            TEdge.Delete(i)
            i += -1
        i += 1
    N = len(TEdge.Edge)
    for i in range(N - 1):
        if TEdge.Edge[i][6] == 0 and TEdge.Edge[i][7] == 1:
            for j in range(len(MidEdge.Edge)):
                if TEdge.Edge[i][0] == MidEdge.Edge[j][0] and TEdge.Edge[i][1] == MidEdge.Edge[j][1]:
                    MidEdge.Edge[i][1] = MidEdge.Edge[i + 1][1]
                    MinEdge.Edge[i][1] = MinEdge.Edge[i + 1][1]
                    MidEdge.Edge[i][5] = NodeDistance(MidEdge.Edge[i][0], MidEdge.Edge[i][1], MidNode)
                    MinEdge.Edge[i][5] = NodeDistance(MinEdge.Edge[i][0], MinEdge.Edge[i][1], MinNode)
                    if InN == 3:
                        MaxEdge.Edge[i][1] = MaxEdge.Edge[i + 1][1]
                        MaxEdge.Edge[i][5] = NodeDistance(MaxEdge.Edge[i][0], MaxEdge.Edge[i][1], MaxNode)
                    break

            TEdge.Edge[i][7] = 0
            TEdge.Edge[i][1] = TEdge.Edge[i + 1][1]
            TEdge.Edge[i][5] = NodeDistance(TEdge.Edge[i][0], TEdge.Edge[i][1], MidNode)
            TEdge.Edge[i + 1][3] = -1

    i = 0
    while i < len(TEdge.Edge):
        if TEdge.Edge[i][3] == -1:
            for j in range(len(MidEdge.Edge)):
                if TEdge.Edge[i][0] == MidEdge.Edge[j][0] and TEdge.Edge[i][1] == MidEdge.Edge[j][1]:
                    MidEdge.Delete(j)
                    MinEdge.Delete(j)
                    if InN == 3:
                        MaxEdge.Delete(j)
                    break
            TEdge.Delete(i)
            i += -1
        i += 1

    N = len(MidEdge.Edge)
    G1name = "RW=" + str(format(SimConditions[0] * 0.0393701, '.2f')) + '", Lift = ' + str(SimConditions[1]) + '-' + str(SimConditions[2]) + ' [kgf/cm2]'
    if group != 'pcr':
        G1name = "RW=" + str(format(SimConditions[0] * 0.0393701, '.2f')) + '", Lift = ' + str(SimConditions[2]) + '-' + str(SimConditions[1]) + ' [kgf/cm2]'
    MinMid = [G1name]
    if InN == 3:
        G2name = "RW=" + str(format(SimConditions[0] * 0.0393701, '.2f')) + '", Lift = ' + str(SimConditions[3]) + '-' + str(SimConditions[2]) + ' [kgf/cm2]'
        MaxMid = [G2name]
    Length = 0
    counting = 0

    # tempMID=[]
    for i in range(N):
        if MidEdge.Edge[i][8] > 0:
            counting += 1
            if counting == 1:
                Mid1 = MidNode.NodeByID(MidEdge.Edge[i][0])
                Min1 = MinNode.NodeByID(MidEdge.Edge[i][0])
                MinMid.append([Length, Min1[3] - Mid1[3]])
                # print "MinMid", Length, ',', Min1[3]-Mid1[3]
                # tempMID.append([Mid1[2], Mid1[3]])
                if InN == 3:
                    Max1 = MaxNode.NodeByID(MidEdge.Edge[i][0])
                    MaxMid.append([Length, Max1[3] - Mid1[3]])
            Mid2 = MidNode.NodeByID(MidEdge.Edge[i][1])
            Min2 = MinNode.NodeByID(MidEdge.Edge[i][1])
            Length += MidEdge.Edge[i][5]
            MinMid.append([Length, Min2[3] - Mid2[3]])
            # print "MinMid", Length, ',', Min1[3] - Mid1[3]
            # tempMID.append([Mid2[2], Mid2[3]])
            if InN == 3:
                Max2 = MaxNode.NodeByID(MidEdge.Edge[i][1])
                MaxMid.append([Length, Max2[3] - Mid2[3]])
    # Plot_XYList('MID', tempMID)
    # PrintList(tempMID)
    N = len(MinMid)
    Length = Length / 2.0
    for i in range(1, N):
        MinMid[i][0] = MinMid[i][0] - Length
        MinMid[i][1] = MinMid[i][1] *1000
        if InN == 3:
            MaxMid[i][0] = MaxMid[i][0] - Length
            MaxMid[i][1] = MaxMid[i][1] *1000
    if group != 'pcr':
        for i in range(1, N):
            MinMid[i][1] = -MinMid[i][1] 
            if InN == 3:
                MaxMid[i][1] = -MaxMid[i][1]
    LiftProfile = []
    LiftProfile.append(MinMid)
    if InN == 3:
        LiftProfile.append(MaxMid)
    # ImageName = 'ProfileGrowth'
    Plot_Graph(ImageName, LiftProfile, '', 'Distance From Center [m]', 'Profile Lift [mm]')

    # print 'Min, Mid, Max. Edge', len(MinEdge.Edge), len(MidEdge.Edge), len(MaxEdge.Edge)
    # for i in range(len(MinEdge.Edge)):
    #     print MinEdge.Edge[i], MidEdge.Edge[i] # , MaxEdge.Edge[i]

    #######################################################################################
    ## Calculation of the Y Coordinates of each X coordinates
    #######################################################################################

    N = len(TEdge.Edge)
    Ctemp = MinNode.NodeByID(TEdge.Edge[0][0])
    CStartX = Ctemp[2]
    Ctemp = MinNode.NodeByID(TEdge.Edge[N - 1][1])
    CEndX = Ctemp[2]
    Ctemp = MidNode.NodeByID(TEdge.Edge[0][0])
    if CStartX < Ctemp[2]:
        CStartX = Ctemp[2]
    Ctemp = MidNode.NodeByID(TEdge.Edge[N - 1][1])
    if CEndX > Ctemp[2]:
        CEndX = Ctemp[2]

    if InN == 3:
        Ctemp = MaxNode.NodeByID(TEdge.Edge[0][0])
        if CStartX < Ctemp[2]:
            CStartX = Ctemp[2]
        Ctemp = MaxNode.NodeByID(TEdge.Edge[N - 1][1])
        if CEndX > Ctemp[2]:
            CEndX = Ctemp[2]
    if abs(CStartX) > abs(CEndX):
        CStartX = -CEndX
    else:
        CEndX = -CStartX

    P1Y = []
    P2Y = []
    P3Y = []
    i = 0
    temp = []
    while i < len(X):
        DistMin11 = DistMin12 = 10000.0
        DistMin21 = DistMin22 = 10000.0
        DistMin31 = DistMin32 = 10000.0

        if X[0] < CStartX:
            # print 'DEL', X[0]
            del X[0]
        elif X[i] > CEndX:
            # print 'DEL', X[i]
            del X[i]

        else:
            for j in range(N):
                NMin1 = MinNode.NodeByID(TEdge.Edge[j][0])
                NMin2 = MinNode.NodeByID(TEdge.Edge[j][1])
                if X[i] > NMin1[2] and DistMin11 > X[i] - NMin1[2]:
                    P1X1 = NMin1[2]
                    P1Y1 = NMin1[3]
                    DistMin11 = X[i] - NMin1[2]
                if X[i] < NMin2[2] and DistMin12 > NMin2[2] - X[i]:
                    P1X2 = NMin2[2]
                    P1Y2 = NMin2[3]
                    DistMin12 = NMin2[2] - X[i]

                NMin3 = MidNode.NodeByID(TEdge.Edge[j][0])
                NMin4 = MidNode.NodeByID(TEdge.Edge[j][1])
                if X[i] > NMin3[2] and DistMin21 > X[i] - NMin3[2]:
                    P2X1 = NMin3[2]
                    P2Y1 = NMin3[3]
                    DistMin21 = X[i] - NMin3[2]
                if X[i] < NMin4[2] and DistMin22 > NMin4[2] - X[i]:
                    P2X2 = NMin4[2]
                    P2Y2 = NMin4[3]
                    DistMin22 = NMin4[2] - X[i]

                if InN == 3:
                    NMin5 = MaxNode.NodeByID(TEdge.Edge[j][0])
                    NMin6 = MaxNode.NodeByID(TEdge.Edge[j][1])
                    if X[i] > NMin5[2] and DistMin31 > X[i] - NMin5[2]:
                        P3X1 = NMin5[2]
                        P3Y1 = NMin5[3]
                        DistMin31 = X[i] - NMin5[2]
                    if X[i] < NMin6[2] and DistMin32 > NMin6[2] - X[i]:
                        P3X2 = NMin6[2]
                        P3Y2 = NMin6[3]
                        DistMin32 = NMin6[2] - X[i]
            if P1X1 == P1X2:
                P1Y.append(P1Y1)
            else:
                PY = (P1Y2 - P1Y1) / (P1X2 - P1X1) * (X[i] - P1X1) + P1Y1
                P1Y.append(PY)
            if P2X1 == P2X2:
                P2Y.append(P2Y1)
                temp.append([X[i], P2Y1])
            else:
                PY = (P2Y2 - P2Y1) / (P2X2 - P2X1) * (X[i] - P2X1) + P2Y1
                P2Y.append(PY)
                temp.append([X[i], P2Y1])
            if InN == 3:
                if P3X1 == P3X2:
                    P3Y.append(P3Y1)
                else:
                    PY = (P3Y2 - P3Y1) / (P3X2 - P3X1) * (X[i] - P3X1) + P3Y1
                    P3Y.append(PY)

            i += 1

    # print len(X),',', len(P1Y),',', len(P2Y),',', len(P3Y)
    # PrintList(temp)
    # Plot_XYList('Y2', temp)

    #######################################################################################
    ## Lift Calculation
    #######################################################################################
    if group == 'pcr':
        G1name = "RW=" + str(format(SimConditions[0] * 0.0393701, '.2f')) + '", Lift = ' + str(SimConditions[1]) + '-' + str(SimConditions[2]) + ' [kgf/cm2]'
    else:
        G1name = "RW=" + str(format(SimConditions[0] * 0.0393701, '.2f')) + '", Lift = ' + str(SimConditions[2]) + '-' + str(SimConditions[1]) + ' [kgf/cm2]'
    MinMid = [G1name]
    L1 = [G1name]
    if InN == 3:
        G2name = "RW=" + str(format(SimConditions[0] * 0.0393701, '.2f')) + '", Lift = ' + str(SimConditions[3]) + '-' + str(SimConditions[2]) + ' [kgf/cm2]'
        MaxMid = [G2name]
        L2 = [G2name]

    N = len(X)
    # G1 = []
    # G2=[]
    # G3=[]

    if group == 'pcr':
        for i in range(N):
            L1.append([X[i], (P1Y[i] - P2Y[i]) * 1000])
            L2.append([X[i], (P3Y[i] - P2Y[i]) * 1000])
    else:
        for i in range(N):
            L1.append([X[i], (P2Y[i] - P1Y[i]) * 1000])
        # G1.append([X[i], P1Y[i]])
        # G2.append([X[i], P2Y[i]])
        # G3.append([X[i], P3Y[i]])
        if InN == 3:
            L2.append([X[i], (P3Y[i] - P2Y[i]) * 1000])
    # Plot_XYList('P1_Tread', G1)
    # Plot_XYList('P2_Tread', G2)
    # Plot_XYList('P3_Tread', G3)

    LiftCrown = []
    LiftCrown.append(L1)
    if InN == 3:
        LiftCrown.append(L2)

    if 'RW1' in ImageName:
        SubImage = ImageName[:-20] + 'CrownGrowthRW1.png'
    elif 'RW2' in ImageName:
        SubImage = ImageName[:-20] + 'CrownGrowthRW2.png'
    elif 'RW3' in ImageName:
        SubImage = ImageName[:-20] + 'CrownGrowthRW3.png'
    else:
        SubImage = ImageName[:-20] + 'CrownGrowthRW.png'
    Plot_Graph(SubImage, LiftCrown, '', 'Distance From Center [m]', 'Profile Lift [mm]', 200, 'o')

    return LiftProfile, LiftCrown

def Plot_ProfileLiftForCrownLift (ImageName, OuterNodePosition1FileNames, TW, TITLE='', LGD1='Lift_1', LGD2='Lift_2', LGD3='Lift_3', LGD4='Lift_4', \
                                 LGD5='Lift_5', xlabel='Distance From Center [m]', ylabel='Lift [mm]', dpi=150, TDPointGap=5.0, CriticalAngle = 50, \
                                 Offset= 10000, TreadNumber = 10000000, \
                                 simcode='', time=time, rim1=NODE(), rim2=NODE(), rim3=NODE(), rim4=NODE(), rim5=NODE(), rim6=NODE(), **args):
    """
    This is for Profile and Crown Lift Calculation 
    Max. Simulation 6
    OuterNodePosition1FileNames = [Name1, Name2, ...]
        Name = 'SimulationCode-SurfaceNodePosition1.tmp' 
        --> TIRE.SFRICResults(SFRICFileName, SFRICLastFileName, 1, 1, Offset, TreadNo)
    CriticalAngle : Profile Line Angle for detecting Groove 
    """
    TreadNo = 10000000
    for key, value in args.items():
        if key == 'title':
            TITLE = value
        if key == 'legend1' or key == 'lgd1':
            LGD1 = value
        if key == 'legend2' or key == 'lgd2':
            LGD2 = value
        if key == 'legend3' or key == 'lgd3':
            LGD3 = value
        if key == 'legend4' or key == 'lgd4':
            LGD4 = value
        if key == 'legend5' or key == 'lgd5':
            LGD5 = value
        if key == 'criticalangle' or key == 'ca' :
            CriticalAngle = value
        if key == 'treadnumber' or key == 'Treadno' or key == 'treadno':
            TreadNo = value
            TreadNumber = value
        if key == 'offset':
            Offset = value
        if key == 'dpi' or key == 'Dpi' or key == 'DPI':
            dpi = value
        if key == 'TDpointgap' or key == 'pointgap' or key == 'pointdist' or key == 'pointdistance':
            TDPointGap = value
        if key == 'SimCode' or key == 'Simcode':
            simcode = value
    
    if simcode !='':
        word = list(simcode.split("-"))
        
        simcode = word[1]+"-"+word[2]+'.inp'
        Node, Element, Elset, Comment = Mesh2DInformation(simcode)
        OuterEdge = Element.OuterEdge(Node)
        CTB = Element.Elset('CTB')
        SUT = Element.Elset('SUT')
        CTB.Combine(SUT)
        TreadOuter= CTB.OuterEdge(Node)
        J=len(OuterEdge.Edge)
        I = len(TreadOuter.Edge)
        CrownEdge = EDGE()
        
        for i in range(I):
            for j in range(J): 
                if TreadOuter.Edge[i][0] == OuterEdge.Edge[j][0] and TreadOuter.Edge[i][1] == OuterEdge.Edge[j][1]:
                    CrownEdge.Add([int(TreadOuter.Edge[i][0])+TreadNo, int(TreadOuter.Edge[i][1])+TreadNo, TreadOuter.Edge[i][2], TreadOuter.Edge[i][3], TreadOuter.Edge[i][4], TreadOuter.Edge[i][5]])
        
    xMax = TW / 2.0 - 10
    xMin = -TW / 2.0 + 10
    iDivision = int((xMax - xMin) / TDPointGap) + 1
    X = []
    for i in range(iDivision):
        X.append((-TDPointGap * float(iDivision / 2) + TDPointGap * float(i)) / 1000)  # Point X to calculate Crown Lift
    
    NS = len(OuterNodePosition1FileNames)
    Node1 = GetDeformedNodeFromSFRIC(OuterNodePosition1FileNames[0], time, ResultSector =1001, Step=0, Offset=10000, TreadNo = 10000000)
    Node2 = GetDeformedNodeFromSFRIC(OuterNodePosition1FileNames[1], time, ResultSector =1001, Step=0, Offset=10000, TreadNo = 10000000)
    
    I = len(Node1.Node)
    for i in range(I):
        Node1.Node[i][1] -= rim1.Node[0][1]
        Node1.Node[i][2] -= rim1.Node[0][2]
        Node1.Node[i][3] -= rim1.Node[0][3]
        r = math.sqrt( (Node1.Node[i][1])*(Node1.Node[i][1]) + (Node1.Node[i][3])*(Node1.Node[i][3])    )
        Node1.Node[i][1] = 0.0
        Node1.Node[i][3] = r
        
        Node2.Node[i][1] -= rim2.Node[0][1]
        Node2.Node[i][2] -= rim2.Node[0][2]
        Node2.Node[i][3] -= rim2.Node[0][3]
        r = math.sqrt( (Node2.Node[i][1])*(Node2.Node[i][1]) + (Node2.Node[i][3])*(Node2.Node[i][3])    )
        Node2.Node[i][1] = 0.0
        Node2.Node[i][3] = r
    
    
    I = len(CrownEdge.Edge)
    Edge1=EDGE()
    Edge2=EDGE()
    for i in range(I):
        Edge1.Add(CrownEdge.Edge[i])
        Edge2.Add(CrownEdge.Edge[i])
    if NS > 2:
        Node3 = GetDeformedNodeFromSFRIC(OuterNodePosition1FileNames[2], time, ResultSector =1001, Step=0, Offset=10000, TreadNo = 10000000)
        K = len(Node3.Node)
        for i in range(K):
            Node3.Node[i][1] -= rim3.Node[0][1]
            Node3.Node[i][2] -= rim3.Node[0][2]
            Node3.Node[i][3] -= rim3.Node[0][3]
            r = math.sqrt( (Node3.Node[i][1])*(Node3.Node[i][1]) + (Node3.Node[i][3])*(Node3.Node[i][3])    )
            Node3.Node[i][1] = 0.0
            Node3.Node[i][3] = r
            
        Edge3=EDGE()
        for i in range(I):
            Edge3.Add(CrownEdge.Edge[i])
    if NS > 3:
        Node4 = GetDeformedNodeFromSFRIC(OuterNodePosition1FileNames[3], time, ResultSector =1001, Step=0, Offset=10000, TreadNo = 10000000)
        K = len(Node4.Node)
        for i in range(K):
            Node4.Node[i][1] -= rim4.Node[0][1]
            Node4.Node[i][2] -= rim4.Node[0][2]
            Node4.Node[i][3] -= rim4.Node[0][3]
            r = math.sqrt( (Node4.Node[i][1])*(Node4.Node[i][1]) + (Node4.Node[i][3])*(Node4.Node[i][3])    )
            Node4.Node[i][1] = 0.0
            Node4.Node[i][3] = r
            
        Edge4=EDGE()
        for i in range(I):
            Edge4.Add(CrownEdge.Edge[i])
    if NS > 4:
        Node5 = GetDeformedNodeFromSFRIC(OuterNodePosition1FileNames[4], time, ResultSector =1001, Step=0, Offset=10000, TreadNo = 10000000)
        K = len(Node5.Node)
        for i in range(K):
            Node5.Node[i][1] -= rim5.Node[0][1]
            Node5.Node[i][2] -= rim5.Node[0][2]
            Node5.Node[i][3] -= rim5.Node[0][3]
            r = math.sqrt( (Node5.Node[i][1])*(Node5.Node[i][1]) + (Node5.Node[i][3])*(Node5.Node[i][3])    )
            Node5.Node[i][1] = 0.0
            Node5.Node[i][3] = r
            
        Edge5=EDGE()
        for i in range(I):
            Edge5.Add(CrownEdge.Edge[i])
    if NS > 5:
        Node6 = GetDeformedNodeFromSFRIC(OuterNodePosition1FileNames[5], time, ResultSector =1001, Step=0, Offset=10000, TreadNo = 10000000)
        K = len(Node6.Node)
        for i in range(K):
            Node6.Node[i][1] -= rim6.Node[0][1]
            Node6.Node[i][2] -= rim6.Node[0][2]
            Node6.Node[i][3] -= rim6.Node[0][3]
            r = math.sqrt( (Node6.Node[i][1])*(Node6.Node[i][1]) + (Node6.Node[i][3])*(Node6.Node[i][3])    )
            Node6.Node[i][1] = 0.0
            Node6.Node[i][3] = r
            
        Edge6=EDGE()
        for i in range(I):
            Edge6.Add(CrownEdge.Edge[i])
    # CrownEdge.Image(Node1, "CrownEdge")
    # if NS == 4:
        # ImageNode(Node1, file=ImageName+"-ProfileNodes", dpi=100, xy=23, size=1.5, n2=Node2, n3=Node3, line=0, n4=Node4)
    # elif NS == 3:  
        # ImageNode(Node1, file=ImageName+"-ProfileNodes", dpi=100, xy=23, size=1.5, n2=Node2, n3=Node3, line=0)
    # elif NS == 2:
        # ImageNode(Node1, file=ImageName+"-ProfileNodes", dpi=100, xy=23, size=1.5, n2=Node2,  line=0)
    N = len(Edge1.Edge)
    for i in range(N): 
        if Edge1.Edge[i][0]> TreadNumber: 
            Edge1.Edge[i][0] = Edge1.Edge[i][0] % Offset + TreadNumber 
            Edge1.Edge[i][1] = Edge1.Edge[i][1] % Offset + TreadNumber 
            Edge2.Edge[i][0] = Edge2.Edge[i][0] % Offset + TreadNumber 
            Edge2.Edge[i][1] = Edge2.Edge[i][1] % Offset + TreadNumber 
            if NS > 2: 
                Edge3.Edge[i][0] = Edge3.Edge[i][0] % Offset + TreadNumber 
                Edge3.Edge[i][1] = Edge3.Edge[i][1] % Offset + TreadNumber 
            if NS > 3: 
                Edge4.Edge[i][0] = Edge4.Edge[i][0] % Offset + TreadNumber 
                Edge4.Edge[i][1] = Edge4.Edge[i][1] % Offset + TreadNumber 
            if NS > 4: 
                Edge5.Edge[i][0] = Edge5.Edge[i][0] % Offset + TreadNumber 
                Edge5.Edge[i][1] = Edge5.Edge[i][1] % Offset + TreadNumber 
            if NS > 5: 
                Edge6.Edge[i][0] = Edge6.Edge[i][0] % Offset + TreadNumber 
                Edge6.Edge[i][1] = Edge6.Edge[i][1] % Offset + TreadNumber 
            
        else: 
            Edge1.Edge[i][0] = Edge1.Edge[i][0] % Offset  
            Edge1.Edge[i][1] = Edge1.Edge[i][1] % Offset 
            Edge2.Edge[i][0] = Edge2.Edge[i][0] % Offset 
            Edge2.Edge[i][1] = Edge2.Edge[i][1] % Offset
            if NS > 2: 
                Edge3.Edge[i][0] = Edge3.Edge[i][0] % Offset 
                Edge3.Edge[i][1] = Edge3.Edge[i][1] % Offset 
            if NS > 3: 
                Edge4.Edge[i][0] = Edge4.Edge[i][0] % Offset 
                Edge4.Edge[i][1] = Edge4.Edge[i][1] % Offset  
            if NS > 4: 
                Edge5.Edge[i][0] = Edge5.Edge[i][0] % Offset  
                Edge5.Edge[i][1] = Edge5.Edge[i][1] % Offset 
            if NS > 5: 
                Edge6.Edge[i][0] = Edge6.Edge[i][0] % Offset 
                Edge6.Edge[i][1] = Edge6.Edge[i][1] % Offset 
    
    ProfileImage = ImageName + '-ProfileCompare'
    
    ProfileEdge=EDGE()
    I = len(OuterEdge.Edge)
    for i in range(I):
        if OuterEdge.Edge[i][2] == 'CTB' or OuterEdge.Edge[i][2] == 'SUT' or OuterEdge.Edge[i][2] == 'CTR' or OuterEdge.Edge[i][2] == 'TRW' or OuterEdge.Edge[i][2] == 'BSW' :
            ProfileEdge.Add([OuterEdge.Edge[i][0]%Offset, OuterEdge.Edge[i][1]%Offset, OuterEdge.Edge[i][2], OuterEdge.Edge[i][3], OuterEdge.Edge[i][4] ])
    
    I = len(Node1.Node)
    tN1 = NODE()
    tN2 = NODE()
    tN3 = NODE()
    tN4 = NODE()
    tN5 = NODE()
    tN6 = NODE()
    for i in range(I):  
        tN1.Add([Node1.Node[i][0] %Offset, Node1.Node[i][1], Node1.Node[i][2], Node1.Node[i][3]])
        tN2.Add([Node2.Node[i][0] %Offset, Node2.Node[i][1], Node2.Node[i][2], Node2.Node[i][3]])
        if NS > 2:
            tN3.Add([Node3.Node[i][0] %Offset, Node3.Node[i][1], Node3.Node[i][2], Node3.Node[i][3]])
        if NS > 3:
            tN4.Add([Node4.Node[i][0] %Offset, Node4.Node[i][1], Node4.Node[i][2], Node4.Node[i][3]])
        if NS > 4:
            tN5.Add([Node5.Node[i][0] %Offset, Node5.Node[i][1], Node5.Node[i][2], Node5.Node[i][3]])
        if NS > 5:
            tN6.Add([Node6.Node[i][0] %Offset, Node6.Node[i][1], Node6.Node[i][2], Node6.Node[i][3]])
        
    
    # if NS==2:
    #     Plot_EdgeComparison(ProfileImage, ProfileEdge, tN1, tN2, 200)
    # elif NS ==3: 
    #     Plot_EdgeComparison(ProfileImage, ProfileEdge, tN1, tN2, 200, tN3)
    # elif NS == 4:
    #     Plot_EdgeComparison(ProfileImage, ProfileEdge, tN1, tN2, 200, tN3, '', '', '', '', '', tN4)
    # elif NS == 5:
    #     Plot_EdgeComparison(ProfileImage, ProfileEdge, tN1, tN2, 200, tN3, '', '', '', '', '', tN4, tN5)
    # elif NS == 6:
    #     Plot_EdgeComparison(ProfileImage, ProfileEdge, tN1, tN2, 200, tN3, '', '', '', '', '', tN4, tN5, tN6)
    # else:
    #     pass
    
    
    ## Groove Nodes Detection 
    TEdge = EDGE()
    N = len(Edge1.Edge)
    for i in range(N):
        if Edge1.Edge[i][0] > TreadNumber:
            TEdge.Add(Edge1.Edge[i])
            
    TEdge = GrooveDetectionFromEdge(TEdge, Node1, 1, TreadNumber)
    # TEdge.Print()
    # TEdge.Image(Node1, "Tread Edge")
    
    i = 0
    while i < len(TEdge.Edge) - 1:
        if TEdge.Edge[i][6] == 1 and TEdge.Edge[i][7] == 1:
            for j in range(len(Edge1.Edge)):
                if TEdge.Edge[i][0] == Edge1.Edge[j][0] and TEdge.Edge[i][1] == Edge1.Edge[j][1]:
                    Edge1.Delete(j)
                    Edge2.Delete(j)
                    if NS > 2:
                        Edge3.Delete(j)
                    if NS > 3:
                        Edge4.Delete(j)
                    if NS > 4:
                        Edge5.Delete(j)
                    if NS > 5:
                        Edge6.Delete(j)
                        
                    break
            TEdge.Delete(i)
            i += -1
        i += 1
    
    N = len(TEdge.Edge)
    for i in range(N - 1):
        if TEdge.Edge[i][6] == 0 and TEdge.Edge[i][7] == 1:
            for j in range(len(Edge1.Edge)):
                if TEdge.Edge[i][0] == Edge1.Edge[j][0] and TEdge.Edge[i][1] == Edge1.Edge[j][1]:
                    Edge1.Edge[i][1] = Edge1.Edge[i + 1][1]
                    Edge2.Edge[i][1] = Edge2.Edge[i + 1][1]
                    Edge1.Edge[i][5] = NodeDistance(Edge1.Edge[i][0], Edge1.Edge[i][1], Node1)
                    Edge2.Edge[i][5] = NodeDistance(Edge2.Edge[i][0], Edge2.Edge[i][1], Node2)
                    if NS > 2:
                        Edge3.Edge[i][1] = Edge3.Edge[i + 1][1]
                        Edge3.Edge[i][5] = NodeDistance(Edge3.Edge[i][0], Edge3.Edge[i][1], Node3)
                    if NS > 3:
                        Edge4.Edge[i][1] = Edge4.Edge[i + 1][1]
                        Edge4.Edge[i][5] = NodeDistance(Edge4.Edge[i][0], Edge4.Edge[i][1], Node4)
                    if NS > 4:
                        Edge5.Edge[i][1] = Edge5.Edge[i + 1][1]
                        Edge5.Edge[i][5] = NodeDistance(Edge5.Edge[i][0], Edge5.Edge[i][1], Node5)
                    if NS > 5:
                        Edge6.Edge[i][1] = Edge6.Edge[i + 1][1]
                        Edge6.Edge[i][5] = NodeDistance(Edge6.Edge[i][0], Edge6.Edge[i][1], Node6)
                    break

            TEdge.Edge[i][7] = 0
            TEdge.Edge[i][1] = TEdge.Edge[i + 1][1]
            TEdge.Edge[i][5] = NodeDistance(TEdge.Edge[i][0], TEdge.Edge[i][1], Node1)
            TEdge.Edge[i + 1][3] = -1

    i = 0
    while i < len(TEdge.Edge):
        if TEdge.Edge[i][3] == -1:
            for j in range(len(Edge1.Edge)):
                if TEdge.Edge[i][0] == Edge1.Edge[j][0] and TEdge.Edge[i][1] == Edge1.Edge[j][1]:
                    Edge1.Delete(j)
                    Edge2.Delete(j)
                    if NS > 2:
                        Edge3.Delete(j)
                    if NS > 3:
                        Edge4.Delete(j)
                    if NS > 4:
                        Edge5.Delete(j)
                    if NS > 5:
                        Edge6.Delete(j)
                    break
            TEdge.Delete(i)
            i += -1
        i += 1
    
    # TEdge.Image(Node1, "Tread No Groove")
    
    N = len(Edge1.Edge)
    Length = 0
    counting = 0
    
    PLift1 = [LGD1]
    PLift2 = [LGD2]
    PLift3 = [LGD3]
    PLift4 = [LGD4]
    PLift5 = [LGD5]
    
    for i in range(N):
        if Edge1.Edge[i][8] > 0:
            counting += 1
            if counting == 1:
                N1 = Node1.NodeByID(Edge1.Edge[i][0])
                N2 = Node2.NodeByID(Edge1.Edge[i][0])
                PLift1.append([Length, N2[3] - N1[3]])
                if NS > 2:
                    N3 = Node3.NodeByID(Edge1.Edge[i][0])
                    PLift2.append([Length, N3[3] - N1[3]])
                if NS > 3:
                    N4 = Node4.NodeByID(Edge1.Edge[i][0])
                    PLift3.append([Length, N4[3] - N1[3]])
                if NS > 4:
                    N5 = Node5.NodeByID(Edge1.Edge[i][0])
                    PLift4.append([Length, N5[3] - N1[3]])
                if NS > 5:
                    N6 = Node6.NodeByID(Edge1.Edge[i][0])
                    PLift5.append([Length, N6[3] - N1[3]])
                    
            N1 = Node1.NodeByID(Edge1.Edge[i][1])
            N2 = Node2.NodeByID(Edge1.Edge[i][1])
            Length += Edge1.Edge[i][5]
            PLift1.append([Length, N2[3] - N1[3]])
            if NS > 2:
                N3 = Node3.NodeByID(Edge1.Edge[i][1])
                PLift2.append([Length, N3[3] - N1[3]])
            if NS > 3:
                N4 = Node4.NodeByID(Edge1.Edge[i][1])
                PLift3.append([Length, N4[3] - N1[3]])
            if NS > 4:
                N5 = Node5.NodeByID(Edge1.Edge[i][1])
                PLift4.append([Length, N5[3] - N1[3]])
            if NS > 5:
                N6 = Node6.NodeByID(Edge1.Edge[i][1])
                PLift5.append([Length, N6[3] - N1[3]])
            
    N = len(PLift1)
    hLength = Length / 2
    for i in range(1, N):
        PLift1[i][0] = PLift1[i][0] - hLength
        PLift1[i][1] = PLift1[i][1] * 1000
        if NS > 2:
            PLift2[i][0] = PLift2[i][0] - hLength
            PLift2[i][1] = PLift2[i][1] * 1000
        if NS > 3:
            PLift3[i][0] = PLift3[i][0] - hLength
            PLift3[i][1] = PLift3[i][1] * 1000
        if NS > 4:
            PLift4[i][0] = PLift4[i][0] - hLength
            PLift4[i][1] = PLift4[i][1] * 1000
        if NS > 5:
            PLift5[i][0] = PLift5[i][0] - hLength
            PLift5[i][1] = PLift5[i][1] * 1000
    PLift = []
    PLift.append(PLift1)
    if NS > 2:
        PLift.append(PLift2)
    if NS > 3:
        PLift.append(PLift3)
    if NS > 4:
        PLift.append(PLift4)
    if NS > 5:
        PLift.append(PLift5)
    #################################################################################################
    ## PROFILE Lift Plotting 
    #################################################################################################
    ProfileImageName = ImageName #+'-ProfileLift'
    # Plot_Graph(ProfileImageName, PLift, TITLE, xlabel, ylabel, dpi)
    #################################################################################################
    if NS == 2: 
        return [TEdge, Node1, Node2]
    elif NS ==3:
        return [TEdge, Node1, Node2, Node3]
    elif NS ==4:
        return [TEdge, Node1, Node2, Node3, Node4]
    elif NS ==5:
        return [TEdge, Node1, Node2, Node3, Node4, Node5]
    elif NS ==6:
        return [TEdge, Node1, Node2, Node3, Node4, Node5, Node6]


def Plot_CrownLiftAfterProfileLift (ImageName, TW, TEdge, Node1, Node2, Node3, Node4, Node5, Node6, 
    TITLE='', LGD1='Lift_1', LGD2='Lift_2', LGD3='Lift_3', LGD4='Lift_4', LGD5='Lift_5', xlabel='Distance From Center [m]', ylabel='Lift [mm]',\
    dpi=150, TDPointGap=5.0, CriticalAngle = 50, Offset= 10000, TreadNumber = 10000000, **args):    
    #######################################################################################
    ## Calculation of the Y Coordinates of each X coordinates on the CROWN
    #######################################################################################
    subplot = 0
    for key, value in args.items():
        if key == 'title':
            TITLE = value
        if key == 'legend1' or key == 'lgd1':
            LGD1 = value
        if key == 'legend2' or key == 'lgd2':
            LGD2 = value
        if key == 'legend3' or key == 'lgd3':
            LGD3 = value
        if key == 'legend4' or key == 'lgd4':
            LGD4 = value
        if key == 'legend5' or key == 'lgd5':
            LGD5 = value
        if key == 'criticalangle' or key == 'ca' :
            CriticalAngle = value
        if key == 'treadnumber' or key == 'Treadno' or key == 'treadno' or key == 'Treadnumber':
            TreadNumber = value
        if key == 'offset':
            Offset = value
        if key == 'dpi' or key == 'Dpi' or key == 'DPI':
            dpi = value
        if key == 'TDpointgap' or key == 'pointgap' or key == 'pointdist' or key == 'pointdistance':
            TDPointGap = value
        if key == 'SimCode' or key == 'Simcode':
            simcode = value
        if key == 'subplot':
            subplot = value
            
    xMax = TW / 2.0 - 10
    xMin = -TW / 2.0 + 10
    iDivision = int((xMax - xMin) / TDPointGap) + 1
    X = []
    for i in range(iDivision):
        X.append((-TDPointGap * float(iDivision / 2) + TDPointGap * float(i)) / 1000)  # Point X to calculate Crown Lift
    
    NS = 0
    if len(Node1.Node) > 0: 
        NS += 1
    if len(Node2.Node) > 0: 
        NS += 1
    if len(Node3.Node) > 0: 
        NS += 1
    if len(Node4.Node) > 0: 
        NS += 1
    if len(Node5.Node) > 0: 
        NS += 1
    if len(Node6.Node) > 0: 
        NS += 1

    N = len(TEdge.Edge)
    Ctemp = Node1.NodeByID(TEdge.Edge[0][0])
    CStartX = Ctemp[2]
    Ctemp = Node1.NodeByID(TEdge.Edge[N - 1][1])
    CEndX = Ctemp[2]
    Ctemp = Node2.NodeByID(TEdge.Edge[0][0])
    if CStartX < Ctemp[2]:
        CStartX = Ctemp[2]
    Ctemp = Node2.NodeByID(TEdge.Edge[N - 1][1])
    if CEndX > Ctemp[2]:
        CEndX = Ctemp[2]

    if NS > 2:
        Ctemp = Node3.NodeByID(TEdge.Edge[0][0])
        if CStartX < Ctemp[2]:
            CStartX = Ctemp[2]
        Ctemp = Node3.NodeByID(TEdge.Edge[N - 1][1])
        if CEndX > Ctemp[2]:
            CEndX = Ctemp[2]
    if NS > 3:
        Ctemp = Node4.NodeByID(TEdge.Edge[0][0])
        if CStartX < Ctemp[2]:
            CStartX = Ctemp[2]
        Ctemp = Node4.NodeByID(TEdge.Edge[N - 1][1])
        if CEndX > Ctemp[2]:
            CEndX = Ctemp[2]
    if NS > 4:
        Ctemp = Node5.NodeByID(TEdge.Edge[0][0])
        if CStartX < Ctemp[2]:
            CStartX = Ctemp[2]
        Ctemp = Node5.NodeByID(TEdge.Edge[N - 1][1])
        if CEndX > Ctemp[2]:
            CEndX = Ctemp[2]
    if NS > 5:
        Ctemp = Node6.NodeByID(TEdge.Edge[0][0])
        if CStartX < Ctemp[2]:
            CStartX = Ctemp[2]
        Ctemp = Node6.NodeByID(TEdge.Edge[N - 1][1])
        if CEndX > Ctemp[2]:
            CEndX = Ctemp[2]
    
    if abs(CStartX) > abs(CEndX):
        CStartX = -CEndX
    else:
        CEndX = -CStartX
        
    ## End of X Range

    P1Y = [];    P2Y = [];    P3Y = [];    P4Y = [];    P5Y = [];    P6Y = []
    i = 0
    while i < len(X):
        DistMin11 = DistMin12 = 10000.0
        DistMin21 = DistMin22 = 10000.0
        DistMin31 = DistMin32 = 10000.0
        DistMin41 = DistMin42 = 10000.0
        DistMin51 = DistMin52 = 10000.0
        DistMin61 = DistMin62 = 10000.0

        if X[0] < CStartX:
            # print 'DEL', X[0]
            del X[0]
        elif X[i] > CEndX:
            # print 'DEL', X[i]
            del X[i]

        else:
            for j in range(N):
                NMin1 = Node1.NodeByID(TEdge.Edge[j][0])
                NMin2 = Node1.NodeByID(TEdge.Edge[j][1])
                if X[i] > NMin1[2] and DistMin11 > X[i] - NMin1[2]:
                    P1X1 = NMin1[2]
                    P1Y1 = NMin1[3]
                    DistMin11 = X[i] - NMin1[2]
                if X[i] < NMin2[2] and DistMin12 > NMin2[2] - X[i]:
                    P1X2 = NMin2[2]
                    P1Y2 = NMin2[3]
                    DistMin12 = NMin2[2] - X[i]

                NMin3 = Node2.NodeByID(TEdge.Edge[j][0])
                NMin4 = Node2.NodeByID(TEdge.Edge[j][1])
                if X[i] > NMin3[2] and DistMin21 > X[i] - NMin3[2]:
                    P2X1 = NMin3[2]
                    P2Y1 = NMin3[3]
                    DistMin21 = X[i] - NMin3[2]
                if X[i] < NMin4[2] and DistMin22 > NMin4[2] - X[i]:
                    P2X2 = NMin4[2]
                    P2Y2 = NMin4[3]
                    DistMin22 = NMin4[2] - X[i]

                if NS > 2:
                    NMin5 = Node3.NodeByID(TEdge.Edge[j][0])
                    NMin6 = Node3.NodeByID(TEdge.Edge[j][1])
                    if X[i] > NMin5[2] and DistMin31 > X[i] - NMin5[2]:
                        P3X1 = NMin5[2]
                        P3Y1 = NMin5[3]
                        DistMin31 = X[i] - NMin5[2]
                    if X[i] < NMin6[2] and DistMin32 > NMin6[2] - X[i]:
                        P3X2 = NMin6[2]
                        P3Y2 = NMin6[3]
                        DistMin32 = NMin6[2] - X[i]
                if NS > 3:
                    NMin7 = Node4.NodeByID(TEdge.Edge[j][0])
                    NMin8 = Node4.NodeByID(TEdge.Edge[j][1])
                    if X[i] > NMin7[2] and DistMin41 > X[i] - NMin7[2]:
                        P4X1 = NMin7[2]
                        P4Y1 = NMin7[3]
                        DistMin41 = X[i] - NMin7[2]
                    if X[i] < NMin8[2] and DistMin42 > NMin8[2] - X[i]:
                        P4X2 = NMin8[2]
                        P4Y2 = NMin8[3]
                        DistMin42 = NMin8[2] - X[i]
                if NS > 4:
                    NMin9 = Node5.NodeByID(TEdge.Edge[j][0])
                    NMin10 = Node5.NodeByID(TEdge.Edge[j][1])
                    if X[i] > NMin9[2] and DistMin51 > X[i] - NMin9[2]:
                        P5X1 = NMin9[2]
                        P5Y1 = NMin9[3]
                        DistMin51 = X[i] - NMin9[2]
                    if X[i] < NMin10[2] and DistMin52 > NMin10[2] - X[i]:
                        P5X2 = NMin10[2]
                        P5Y2 = NMin10[3]
                        DistMin52 = NMin10[2] - X[i]
                if NS > 5:
                    NMin11 = Node6.NodeByID(TEdge.Edge[j][0])
                    NMin12 = Node6.NodeByID(TEdge.Edge[j][1])
                    if X[i] > NMin11[2] and DistMin61 > X[i] - NMin11[2]:
                        P6X1 = NMin11[2]
                        P6Y1 = NMin11[3]
                        DistMin61 = X[i] - NMin5[2]
                    if X[i] < NMin12[2] and DistMin62 > NMin12[2] - X[i]:
                        P6X2 = NMin12[2]
                        P6Y2 = NMin12[3]
                        DistMin62 = NMin12[2] - X[i]
                
            if P1X1 == P1X2:
                P1Y.append(P1Y1)
            else:
                PY = (P1Y2 - P1Y1) / (P1X2 - P1X1) * (X[i] - P1X1) + P1Y1
                P1Y.append(PY)
                
            if P2X1 == P2X2:
                P2Y.append(P2Y1)
            else:
                PY = (P2Y2 - P2Y1) / (P2X2 - P2X1) * (X[i] - P2X1) + P2Y1
                P2Y.append(PY)
                
            if NS > 2:
                if P3X1 == P3X2:
                    P3Y.append(P3Y1)
                else:
                    PY = (P3Y2 - P3Y1) / (P3X2 - P3X1) * (X[i] - P3X1) + P3Y1
                    P3Y.append(PY)
            if NS > 3:
                if P4X1 == P4X2:
                    P4Y.append(P4Y1)
                else:
                    PY = (P4Y2 - P4Y1) / (P4X2 - P4X1) * (X[i] - P4X1) + P4Y1
                    P4Y.append(PY)
            if NS > 4:
                if P5X1 == P5X2:
                    P5Y.append(P5Y1)
                else:
                    PY = (P5Y2 - P5Y1) / (P5X2 - P5X1) * (X[i] - P5X1) + P5Y1
                    P5Y.append(PY)
            if NS > 5:
                if P6X1 == P6X2:
                    P6Y.append(P6Y1)
                else:
                    PY = (P6Y2 - P6Y1) / (P6X2 - P6X1) * (X[i] - P6X1) + P6Y1
                    P6Y.append(PY)

            i += 1
    
    #######################################################################################
    ## Lift Calculation
    #######################################################################################
    
    CLift1 = [LGD1]
    CLift2 = [LGD2]
    CLift3 = [LGD3]
    CLift4 = [LGD4]
    CLift5 = [LGD5]
    N = len(X)
    for i in range(N): 
        CLift1.append([X[i], (P2Y[i] - P1Y[i]) * 1000])
        if NS > 2:
            CLift2.append([X[i], (P3Y[i] - P1Y[i]) * 1000])
        if NS > 3:
            CLift3.append([X[i], (P4Y[i] - P1Y[i]) * 1000])
        if NS > 4:
            CLift4.append([X[i], (P5Y[i] - P1Y[i]) * 1000])
        if NS > 5:
            CLift5.append([X[i], (P6Y[i] - P1Y[i]) * 1000])
        
    CLift = [CLift1]
    if NS>2:
        CLift.append(CLift2)
    if NS>3:
        CLift.append(CLift3)
    if NS>4:
        CLift.append(CLift4)
    if NS>5:
        CLift.append(CLift5)
        
    CrownImageName = ImageName #+'-CrownLift'
    if subplot == 0:
        Plot_Graph(CrownImageName, CLift, TITLE, xlabel, ylabel, dpi, 'o')
    
    if subplot != 0:
        return CLift

def Plot_TemperatureContour(ImageName, TNode, Element, dpi=200, Offset = 10000, **args): 
    dotgap = 0.5E-3
    # xy = 23
    x=2
    y=3
    viewaxis = 0
    equalxy  = 1
    edgecolor = "gray"
    alpha =0.8
    titlesize = 10
    colormap = "jet"
    marker = "o"
    textsize = 8
    size = 1.0
    for key, value in args.items():
        if key == 'offset':
            Offset = value
        if key == 'DPI' or key == 'Dpi':
            dpi = value
        if key == "gap":
            dotgap = value
        if key == "size":
            dotsize = value
        if key == "axis":
            viewaxis = value
        if key == "alpha":
            alpha = value 
        if key == "cmap":
            colormap = value
        if key == "marker":
            marker = value
        if key == "size":
            size = value 
        
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('off')
    textsize = 8
    

    color = 'gray'
    lw = 0.2
    N = len(Element.Element)
    for i in range(N): 
        if Element.Element[i][6] == 3: 
            N1 = TNode.NodeByID(Element.Element[i][1])
            N2 = TNode.NodeByID(Element.Element[i][2])
            N3 = TNode.NodeByID(Element.Element[i][3])
        
            iX = [N1[2], N2[2], N3[2], N1[2]]
            iY = [N1[3], N2[3], N3[3], N1[3]]
            plt.plot(iX, iY, color, lw=lw, linestyle='-')
        if Element.Element[i][6] == 4: 
            N1 = TNode.NodeByID(Element.Element[i][1])
            N2 = TNode.NodeByID(Element.Element[i][2])
            N3 = TNode.NodeByID(Element.Element[i][3])
            N4 = TNode.NodeByID(Element.Element[i][4])
        
            iX = [N1[2], N2[2], N3[2], N4[2], N1[2]]
            iY = [N1[3], N2[3], N3[3], N4[3], N1[3]]
            plt.plot(iX, iY, color, lw=lw, linestyle='-')
        else: 
            pass
    X = []
    Y = []
    T = []
    MaxT = 0.0
    N = len(TNode.Node)
    for i in range(N): 
        X.append(TNode.Node[i][2])
        Y.append(TNode.Node[i][3])
        T.append(TNode.Node[i][4])
        
        if TNode.Node[i][4]>MaxT:
            MaxT = TNode.Node[i][4] 

    strMaxT = 'Max Inner Temperature='+str(format(MaxT,".1f"))
    
    plt.title(strMaxT, fontsize=textsize)
    
    cont = plt.tricontourf(X, Y, T, 50, cmap='jet')

    sf = []
    Out = Element.OuterEdge(TNode)
    N = len(Out.Edge)
    for i in range(N):
        Ni = TNode.NodeByID(Out.Edge[i][0])
        sf.append([Ni[2], Ni[3]])
    Ni = TNode.NodeByID(Out.Edge[N-1][1])
    sf.append([Ni[2], Ni[3]])
    patch = PathPatch(Path(sf), facecolor='none', edgecolor='none')
    ax.add_patch(patch)
    for c in cont.collections:
        c.set_clip_path(patch)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1%", pad=0.01)
    cbar = plt.colorbar(cont, cax=cax)
    cbar.ax.tick_params(labelsize=5)
    plt.savefig(ImageName, dpi=dpi)
    plt.clf()

def Plot_TemperatureDotting(ImageName, TNode, Element, dpi=200, Offset = 10000, **args): 
    print ("Start to plotting the Temperature distribution")
    dotgap = 0.3E-3
    x=2;     y=3
    viewaxis = 0;     equalxy  = 1
    edgecolor = "gray"
    alpha =0.8;     titlesize = 10
    colormap = "jet";     marker = "o"
    textsize = 8;     size = 1.0
    for key, value in args.items():
        if key == 'offset':
            Offset = value
        if key == 'DPI' or key == 'Dpi':
            dpi = value
        if key == "gap":
            dotgap = value
        if key == "size":
            dotsize = value
        if key == "axis":
            viewaxis = value
        if key == "alpha":
            alpha = value 
        if key == "cmap":
            colormap = value
        if key == "marker":
            marker = value
        if key == "size":
            size = value 
            
    MaxT = 0.0
    N = len(TNode.Node)
    for i in range(N): 
        if TNode.Node[i][4]>MaxT:
            MaxT = TNode.Node[i][4] 
    title = 'Max Inner Temperature='+str(format(MaxT,".1f"))
    print (title)
    # dots=Innerpoints(dotgap, Element, TNode, XY=23)
    dots = ValueInterpolation(dotgap, Element, TNode, XY=23)

    print ("END of Interpolation")

    dots = np.array(dots.Node)
    px = dots[:,[x]]
    py = dots[:,[y]]
    pv = dots[:,[4]]
    min = np.min(pv)
    max = np.max(pv)


    fig, ax = plt.subplots()
    if equalxy == 1:
        ax.axis('equal')
    
    if viewaxis == 1:
        ax.axis('on')
    else:
        ax.axis('off')
    if title != '':
        plt.title(title, fontsize=titlesize)


    cont = plt.scatter(px, py, c=pv,  s=size, edgecolors="none", marker=marker, vmin=min, vmax=max, alpha = alpha, cmap=colormap)
    

    lw = 0.2
    N = len(Element.Element)
    for i in range(N): 
        if Element.Element[i][6] == 3: 
            N1 = TNode.NodeByID(Element.Element[i][1])
            N2 = TNode.NodeByID(Element.Element[i][2])
            N3 = TNode.NodeByID(Element.Element[i][3])
        
            iX = [N1[2], N2[2], N3[2], N1[2]]
            iY = [N1[3], N2[3], N3[3], N1[3]]
            plt.plot(iX, iY, edgecolor, lw=lw, linestyle='-')
        if Element.Element[i][6] == 4: 
            N1 = TNode.NodeByID(Element.Element[i][1])
            N2 = TNode.NodeByID(Element.Element[i][2])
            N3 = TNode.NodeByID(Element.Element[i][3])
            N4 = TNode.NodeByID(Element.Element[i][4])
        
            iX = [N1[2], N2[2], N3[2], N4[2], N1[2]]
            iY = [N1[3], N2[3], N3[3], N4[3], N1[3]]
            plt.plot(iX, iY, edgecolor, lw=lw, linestyle='-')
        else: 
            pass
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1%", pad=0.01)
    cbar = plt.colorbar(cont, cax=cax)
    cbar.ax.tick_params(labelsize=5)
    plt.savefig(ImageName, dpi=dpi)
    plt.clf()

def ValueInterpolation (dots, E, N, XY=21, vmin='', vmax='', **args):
    for key, value in args.items():
        if key == 'xy':
            XY = int(value)

    x=int(XY/10); y=int(XY%10)
    
    ################################################################################
    t0 = time.time()
    gap = dots
    xy = NODE()
    el3=ELEMENT()
    I = -1
    for el in E.Element:
        if el[6] == 2: continue
        elif el[6] == 4:
            N1 = N.NodeByID(el[1])
            N2 = N.NodeByID(el[2])
            N3 = N.NodeByID(el[3])
            N4 = N.NodeByID(el[4])
            # print (N1[x], N1[y],  " | ", N1[x], N1[y],  " | ", N1[x], N1[y], " | ",  N1[x], N1[y])

            xmax = N1[x]; xmin=N1[x]
            ymax = N1[y]; ymin=N1[y]

            if xmax < N2[x]: xmax = N2[x]     
            if xmin > N2[x]: xmin = N2[x]
            if ymax < N2[y]: ymax = N2[y]
            if ymin > N2[y]: ymin = N2[y]

            if xmax < N3[x]: xmax = N3[x]     
            if xmin > N3[x]: xmin = N3[x]
            if ymax < N3[y]: ymax = N3[y]
            if ymin > N3[y]: ymin = N3[y]

            if xmax < N4[x]: xmax = N4[x]     
            if xmin > N4[x]: xmin = N4[x]
            if ymax < N4[y]: ymax = N4[y]
            if ymin > N4[y]: ymin = N4[y]

            gapx = (xmax-xmin)
            gapy = (ymax-ymin)

            dotx = int(gapx/gap)
            doty = int(gapy/gap)
            if dotx < 3: dotx = 3
            if doty < 3: doty = 3

            s =[]; t=[]
            g = 2.0 / float(dotx) 
            v = -1.0
            for i in range(dotx): 
                s.append(v)
                v += g 
            g = 2.0 / float(doty) 
            v = -1.0
            for i in range(doty+1): 
                t.append(v)
                v += g 
            px = [N1[x], N2[x], N3[x], N4[x]]
            py = [N1[y], N2[y], N3[y], N4[y]]
            pv = [N1[4], N2[4], N3[4], N4[4]]

            for m in range(dotx): 
                for n in range(doty): 
                    tlist = [I, 0.0, 0.0, 0.0, 0.0]
                    tlist[x] = 0.25*((1-s[m])*(1-t[n])*px[0] + (1+s[m])*(1-t[n])*px[1] + (1+s[m])*(1+t[n])*px[2] + (1-s[m])*(1+t[n])*px[3])
                    tlist[y] = 0.25*((1-s[m])*(1-t[n])*py[0] + (1+s[m])*(1-t[n])*py[1] + (1+s[m])*(1+t[n])*py[2] + (1-s[m])*(1+t[n])*py[3])
                    tlist[4] = 0.25*((1-s[m])*(1-t[n])*pv[0] + (1+s[m])*(1-t[n])*pv[1] + (1+s[m])*(1+t[n])*pv[2] + (1-s[m])*(1+t[n])*pv[3])
                    xy.Add(tlist)
                    I -= 1

        elif el[6] == 3:
            el3.Add(el)

    tI = -I
    # print ("END innerpoints ")
    
    I = len(el3.Element)
    for i in range(I):
        N1 = N.NodeByID(el3.Element[i][1])
        N2 = N.NodeByID(el3.Element[i][2])
        N3 = N.NodeByID(el3.Element[i][3])
        X = [N1[x], N2[x], N3[x]]
        Y = [N1[y], N2[y], N3[y]]
        V = [N1[4], N2[4], N3[4]]
        Stx = (X[0], X[1], X[2])
        Sty = (Y[0], Y[1], Y[2])
        Stv = (V[0], V[1], V[2])
        results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, 0.99, dots)
        del(Stx)
        del(Sty)
        del(Stv)
        Nn = len(results)
        for m in range(int(Nn/3)):
            if math.isnan(results[m * 3 + 2]) == False:
                t =[tI, 0.0, 0.0, 0.0, 0.0]
                t[x] = results[m*3]
                t[y] = results[m*3+1]
                t[4] = results[m*3+2]
                xy.Add(t)
    
    t1 = time.time()
    print ("time to generating dots for contour", round(t1-t0, 2), len(xy.Node))
    return xy
    

def Plot_LoadedTireProfile(ImageName, sdb, sdbresult, simcondition,  dpi=200, **args):
    offset = 10000
    treadno =  10000000
    mesh = ''
    sidewave = 0
    for key, value in args.items():
        if key == 'tread' or key == 'treadno' or key == 'TreadNo' or key == 'Tread':
            treadno = value
        if key == 'dpi':
            dpi == value
        if key == 'mesh':
            mesh = value  # 2D mesh file (.inp)
        if key == 'sidewave':
            sidewave = value
        if key == "offset":
            offset = value
    if mesh == '':
        jobdir = os.getcwd()
        lstInp = glob.glob(jobdir+"/*.inp")
        I = len(lstInp)
        for i in range(I):
            if "RND" in lstInp[i] or "ATC" in lstInp[i] or "CTC" in lstInp[i] or "ETC" in lstInp[i]:
                pass
            else:
                mesh = lstInp[i]
                break

    ND, EL, ES, CM = Mesh2DInformation(mesh)
    BSW = EL.Elset("BSW")
    Outeredge = EL.OuterEdge(ND)
    C01edge = EL.ElsetToEdge("C01")
    BT3 = EL.Elset("BT3")
    if len(BT3.Element) == 0:
        BTedge = EL.ElsetToEdge("BT1")
    else:
        BTedge = EL.ElsetToEdge("BT2")
    
    BDR  = EL.Elset("BEAD_R")
    BDL = EL.Elset("BEAD_L")
    if len(BDL.Element) ==0:
        i=0
        while i < len(BDR.Element):
            if BDR.Element[i][8] > 0:
                BDL.Add(BDR.Element[i])
                del(BDR.Element[i])
                i-=1
            i += 1
    if len(BDR.Element) ==0:
        i=0
        while i < len(BDL.Element):
            if BDL.Element[i][8] < 0:
                BDR.Add(BDL.Element[i])
                del(BDL.Element[i])
                i-=1
            i += 1

    BDedge = BDL.OuterEdge(ND)
    BDRedge = BDR.OuterEdge(ND)
    BDedge.Combine(BDRedge)

    FEdge = EDGE()
    FEdge.Combine(Outeredge)
    FEdge.Combine(C01edge)
    FEdge.Combine(BTedge)
    FEdge.Combine(BDedge)

    Node = ResultSDB(sdb, sdbresult, offset, treadno, 1, 0)
    Rim = GetRimCenter(lastsdb=sdbresult)
    RimX = Rim.Node[0][1]
    RimY = Rim.Node[0][2]
    RimZ = Rim.Node[0][3]
    Node.Rotate(simcondition.Camber, xy=23, xc=RimY, yc=RimZ)
    Node.Rotate(-simcondition.SlipAngle, xy=21, xc=RimY, yc=RimX)

    I = len(Node.Node)
    TopNode = 0
    MaxID = 0
    MaxY = -9.9E-20
    for i in range(I):
        if MaxY < Node.Node[i][3]:
            MaxY = Node.Node[i][3]
            TopNode = Node.Node[i][0]
        if MaxID < Node.Node[i][0]:
            MaxID = Node.Node[i][0]
    
    if MaxID > treadno:
        MaxID -= treadno
    Sectors = int(MaxID / offset) + 1
    # print "sectors", Sectors, MaxID, offset
    if TopNode > treadno:
        TopNode -= treadno
    Topsector = int(TopNode / offset) + 1
    # print "top sector", Topsector 
    Bottomsector = Topsector + int(Sectors / 2 )
    # print "Bottome sector ", Bottomsector, 
    if Bottomsector > Sectors:
        Bottomsector -= Sectors
    # print " ", Bottomsector
    Top = NODE()
    Bottom = NODE()
    for i in range(I):
        if ( Node.Node[i][0] >= (Topsector-1)*offset and Node.Node[i][0] < Topsector*offset ) or ( Node.Node[i][0] >= (Topsector-1)*offset + treadno and Node.Node[i][0] < Topsector*offset +treadno):
            r = math.sqrt(Node.Node[i][1]*Node.Node[i][1]+(Node.Node[i][3]-RimZ)*(Node.Node[i][3]-RimZ))
            Top.Add([Node.Node[i][0]%offset, 0.0, Node.Node[i][2], r])
        if ( Node.Node[i][0] >= (Bottomsector-1)*offset and Node.Node[i][0] < Bottomsector*offset ) or ( Node.Node[i][0] >= (Bottomsector-1)*offset + treadno and Node.Node[i][0] < Bottomsector*offset +treadno):
            r = math.sqrt(Node.Node[i][1]*Node.Node[i][1]+(Node.Node[i][3]-RimZ)*(Node.Node[i][3]-RimZ))
            Bottom.Add( [Node.Node[i][0]%offset,  0.0,   Node.Node[i][2],    r])
    
    ## ////////////////////////
    bdnode = BDR.Element[0][1]
    topbead = Top.NodeByID(bdnode)
    bottombead = Bottom.NodeByID(bdnode)
    
    if abs(topbead[3] - bottombead[3]) > 0.01:
        print ("** NODE SHIFT : DIST=", topbead[3] - bottombead[3], "RIM Center:", Rim.Node[0])
        # print len(Top.Node), len(Bottom.Node), Bottomsector, Topsector
        I = len(Top.Node)
        for i in range(I):
            # print Top.Node[i], Bottom.Node[i], 
            Top.Node[i][3] -= abs(Rim.Node[0][3])
            Bottom.Node[i][3] += abs(Rim.Node[0][3])
            # print "-->", Top.Node[i][3], Bottom.Node[i][3]

    # ImageNode(Top, n2=Bottom, file=ImageName+"-NODE", size=5, xy=23, axis=0)    
    # print Topsector, Bottomsector, Sectors, "offset=", offset

    Plot_EdgeComparison(ImageName+'-ProfileCompare', FEdge, Top, Bottom, L1="Unloading", L2="Loading", axis=0)
    
    if sidewave != 0:
        NodeBSW = BSW.Nodes()
        NodeOuter = Outeredge.Nodes()
        BSWOuternodes = []
        I = len(NodeBSW)
        J = len(NodeOuter)
        NoBSW = 0
        for i in range(I):
            for j in range(J):
                if NodeBSW[i] == NodeOuter[j]:
                    BSWOuternodes.append(NodeBSW[i])
                    NoBSW +=1
                    break
        J = len(Node.Node)
        BSWDelY =[]
        Side1 = NODE()
        Side2 = NODE()
        for i in range(NoBSW):
            tList = [[BSWOuternodes[i], 0.0, 0.0, 0.0, 0.0]]
            sum = 0.0
            c =0
            for j in range(J):
                if BSWOuternodes[i] == Node.Node[j][0] % offset:
                    if Node.Node[j][2] > 0.0:
                        tList.append([Node.Node[j][0], Node.Node[j][2]])
                        sum += Node.Node[j][2]
                        c += 1
                        Side1.Add([Node.Node[j][0], Node.Node[j][1], Node.Node[j][2], Node.Node[j][3], 0.0])
                    else:
                        tList.append([Node.Node[j][0], Node.Node[j][2]])
                        sum += Node.Node[j][2]
                        c += 1
                        Side2.Add([Node.Node[j][0], Node.Node[j][1], Node.Node[j][2], Node.Node[j][3], 0.0])
            tList[0][1] = sum / float(c)
            BSWDelY.append(tList)
        
        # print "N Size", len(Side1.Node), len(Side2.Node), "BSWNODE=", NoBSW
        for i in range(NoBSW):
            J = len(BSWDelY[i])
            min = 9.9E10
            max = -9.9E10
            for j in range(1, J):
                BSWDelY[i][j][1] -= BSWDelY[i][0][1]
                if BSWDelY[i][j][1] < min:
                    min = BSWDelY[i][j][1]
                if BSWDelY[i][j][1] > max:
                    max = BSWDelY[i][j][1]
            BSWDelY[i][0][2] = min
            BSWDelY[i][0][3] = max
            BSWDelY[i][0][4] = abs(max - min)
            # print BSWDelY[i][0]

        max1 = 0.0
        max2 = 0.0
        WaveMax1=[]
        WaveMax2=[]
        for i in range(NoBSW):
            if abs(BSWDelY[i][0][4]) > max1 and BSWDelY[i][0][1] > 0:
                max1 = abs(BSWDelY[i][0][4])
                WaveMax1 = BSWDelY[i]
                # print "SIDE 1 MAX", WaveMax1[0]
            if abs(BSWDelY[i][0][4]) > max2 and BSWDelY[i][0][1] < 0:
                max2 = abs(BSWDelY[i][0][4])
                WaveMax2 = BSWDelY[i]

                # print "SIDE 2 MAX", WaveMax2[0]
        Side = NODE()
        maxside = 0
        if max2 > max1 :
            Wavemax = WaveMax2
            I = len(Side2.Node)
            for i in range(I): Side.Add( [Side2.Node[i][0], Side2.Node[i][1], -Side2.Node[i][2], Side2.Node[i][3], Side2.Node[i][4] ])
            maxside =2
        else:
            Wavemax = WaveMax1
            I = len(Side1.Node)
            for i in range(I): Side.Add(Side1.Node[i])
            maxside =1

        I = len(Side.Node)
        min = 9.9E20
        max = -9.9E20
        for i in range(I):
            for j in range(NoBSW):
                for k in range(1, Sectors+1):
                    if Side.Node[i][0] == BSWDelY[j][k][0]:
                        if maxside == 2:
                            val = -BSWDelY[j][k][1]*1000
                        else:
                            val = BSWDelY[j][k][1]*1000
                        Side.Node[i][4] = val
                        if min > val:
                            min = val
                        if max < val:
                            max = val
                        break
        
        amp = 0.7
        Side.Image(ImageName+"-ColoredSide", xy=13, vmin = min*amp, vmax=max*amp*0.9, dpi=100, cm=1, ci=4, size=20, legendtext="Gap From Average[mm]", axis=0)# , vmin=min*amp, vmax=max*amp*0.9)


        # Topsector, Sectors
        StandingWave=[]                    
        SWNodeLeftList=['Max SW Node Right ('+str(WaveMax1[0][0]%offset)+')']
        SWNodeRightList=['Max SW Node Left ('+str( WaveMax2[0][0]%offset)+')']
        
        for i in range(Sectors):
            nodeid1 = (Topsector-1 + i)*offset + WaveMax1[0][0]
            if nodeid1 > Sectors*offset:
                nodeid1 -= Sectors*offset
            nodeid2 = (Topsector-1 + i)*offset + WaveMax2[0][0]
            if nodeid2 > Sectors*offset:
                nodeid2 -= Sectors*offset
            for j in range(1, Sectors+1):
                if nodeid1 == WaveMax1[j][0]:   # left side 
                    if i ==0:
                        itop = j
                    SWNodeLeftList.append([i,  (WaveMax1[j][1]-WaveMax1[itop][1])*1000 ])

                if nodeid2 == WaveMax2[j][0]:   # left side 
                    if i ==0:
                        itop = j
                    SWNodeRightList.append([i,  (WaveMax2[j][1]-WaveMax2[itop][1])*1000 ])

        
        if maxside == 1:
            side = SWNodeLeftList
        else:
            side = SWNodeRightList


        max1 = 0.0
        max2 = 0.0
        max3 = 0.0
        max4 = 0.0
        t1s = Topsector
        t2s = Topsector
        t3s = Topsector
        t4s = Topsector
        
        tempmax=0
        maxdeformedsector = 0 
        for i in range(1, Sectors+1):
            if tempmax < abs(SWNodeLeftList[i][1]-SWNodeRightList[i][1]):
                tempmax = abs(SWNodeLeftList[i][1]-SWNodeRightList[i][1])
                max1 = side[i][1]
                ts = i
                maxdeformedsector=i

        if abs(SWNodeLeftList[maxdeformedsector+1][1]) > abs(max1): 
            maxdeformedsector = maxdeformedsector+1
            max1 = side[maxdeformedsector][1]
        if abs(SWNodeLeftList[maxdeformedsector-1][1]) > abs(max1): 
            maxdeformedsector = maxdeformedsector - 1
            max1 = side[maxdeformedsector][1]

        
        t1s = maxdeformedsector + Topsector
        if t1s > Sectors:
            t1s -= Sectors
        ts1= 0
        tempmax=0
        cnt = 0 
        tmax1=max1 
        wave1=0; wave2 = 0 
        minwavesector = 0
        maxwavesector = 0 
        for i in range(ts+2, Sectors+1):
            if abs(tmax1 - side[i][1]) >= tempmax : 
                tempmax = abs(tmax1 - side[i][1]) 
                if cnt == 0 : 
                    wave1 = tempmax 
                    minwavesector = i
                max2 = side[i][1]
                ts1 = i
            else: 
                if i + 1 < len(side): 
                    if abs(tmax1 - side[i+1][1]) >= tempmax : 
                        continue 
                    cnt += 1
                    if cnt == 3: 
                        wave2 = tempmax 
                        ts1 = i
                        break 

                    tempmax = 0 
                    tmax1 = max2
                    maxwavesector = i


        ts2= 0
        tempmax=0
        cnt = 0 
        tmax2=max2 
        wave3=0 
        
        for i in range(ts1+2, Sectors+1):
            # if max1 * side[i][1] < 0 and abs(max2) < abs(side[i][1]):
            if abs(tmax2 - side[i][1]) >= tempmax : 
                tempmax = abs(tmax2 - side[i][1]) 
                max3 = side[i][1]
                ts2 = i
            else: 
                if i + 1 < len(side): 
                    if abs(tmax2 - side[i+1][1]) >= tempmax : 
                        continue 
                    cnt += 1
                    if cnt ==2: 
                        wave3 = tempmax 
                        ts2 = i
                        break 
                    tempmax = 0 
                    tmax2 = max3
                    # print ("  max3=", max3)
        
        if minwavesector == Sectors:
            t2s = Topsector
        else:
            t2s = minwavesector + Topsector
            if t2s > Sectors: t2s -= Sectors

        if maxwavesector == Sectors:
            t3s = Topsector
        else:
            t3s = maxwavesector + Topsector
            if t3s > Sectors: t3s -= Sectors

        print ("... 1st wave1=%.3f (%d)"%( wave1, maxdeformedsector))
        print ("... 2nd wave2=%.3f (%d)"%( wave2, minwavesector))
        print ("... 3rd wave3=%.3f (max wave sector =%d, top sector no=%d)"%( wave3, maxwavesector, Topsector))

        #####################################################################
        # print ("#### 1st Max Disp=%.2f(sector=%d), 2nd max = %.2f(%d), 3rd max=%.2f(%d), Max wave sector=%d(%d), Min wave sector=%d(%d), \
        #     3rd sector=%d(%d)"%(max1, t1s, max2, t2s, max3, t3s, ts1, ts, t2s, ts1, t3s, ts2))
        #####################################################################
        Mnode = NODE()
        Snode = NODE()
        Dnode = NODE()
        I = len(Node.Node)
        MinSW = 9.9E20
        MaxSW = -9.9E20
        for i in range(I):
            if ( Node.Node[i][0] >= (t1s-1)*offset and Node.Node[i][0] < t1s*offset ) or ( Node.Node[i][0] >= (t1s-1)*offset + treadno and Node.Node[i][0] < t1s*offset +treadno):
                r = math.sqrt(Node.Node[i][1]*Node.Node[i][1]+(Node.Node[i][3]-RimZ)*(Node.Node[i][3]-RimZ))
                Mnode.Add([Node.Node[i][0]%offset, 0.0, Node.Node[i][2], r])
                if MinSW > Node.Node[i][2]:
                    MinSW = Node.Node[i][2]
                if MaxSW < Node.Node[i][2]:
                    MaxSW = Node.Node[i][2]
            if ( Node.Node[i][0] >= (t2s-1)*offset and Node.Node[i][0] < t2s*offset ) or ( Node.Node[i][0] >= (t2s-1)*offset + treadno and Node.Node[i][0] < t2s*offset +treadno):
                r = math.sqrt(Node.Node[i][1]*Node.Node[i][1]+(Node.Node[i][3]-RimZ)*(Node.Node[i][3]-RimZ))
                Snode.Add( [Node.Node[i][0]%offset,  0.0,   Node.Node[i][2],    r])
            if ( Node.Node[i][0] >= (t3s-1)*offset and Node.Node[i][0] < t3s*offset ) or ( Node.Node[i][0] >= (t3s-1)*offset + treadno and Node.Node[i][0] < t3s*offset +treadno):
                r = math.sqrt(Node.Node[i][1]*Node.Node[i][1]+(Node.Node[i][3]-RimZ)*(Node.Node[i][3]-RimZ))
                Dnode.Add( [Node.Node[i][0]%offset,  0.0,   Node.Node[i][2],    r])
        # print("##### wave1=%.3f, wave2=%.3f, wave3=%.3f, Max deformed sec1=%d, Min wave sec2=%d, Max wave sec3=%d, sec dif 1~2=%d"%(wave1, wave2, wave3, t1s, t2s, t3s, int(Sectors/5)))
        if wave3 > 1.0 and abs(ts1 - ts2) < int(Sectors/5):  
            # print("#######################", wave1, wave2, wave3, int(Sectors/5))
            mbd = Mnode.NodeByID(bdnode)
            sbd = Snode.NodeByID(bdnode)  
            dbd = Dnode.NodeByID(bdnode)  

            if abs(mbd[3] - dbd[3]) > 0.001:
                smove = mbd[3] - sbd[3]
                dmove = mbd[3] - dbd[3]
                I = len(Mnode.Node)
                for i in range(I):
                    Snode.Node[i][3] += smove
                    Dnode.Node[i][3] += dmove
            Plot_EdgeComparison(ImageName+'-ProfileCompare', FEdge, Mnode, Dnode, Node3=Snode, L1="Max Deformed", L2="Wave Max", L3="Wave Min", axis=0)
        # Left_waves = Standingwave_amplitude(SWNodeLeftList)
        Left_waves, leftminmax = Standingwave_amplitude(SWNodeRightList, direction = -1)
        Right_waves, rightminmax = Standingwave_amplitude(SWNodeLeftList, direction = 1)
        positions=[]
        showvalue = 1 
        if Left_waves[0] > Right_waves[0]:  
            positions = leftminmax
            array = np.array(leftminmax)
            ar_min = np.min(array[:, 1])
            ar_max = np.max(array[:, 1])
            if Left_waves[2] <=1.0 : showvalue = 0

        else:                               
            positions = rightminmax 
            array = np.array(rightminmax)
            ar_min = np.min(array[:, 1])
            ar_max = np.max(array[:, 1])
            if Right_waves[2] <=1.0 : showvalue = 0
        
        pos=[ar_max, ar_min]

        StandingWave.append(SWNodeLeftList)
        StandingWave.append(SWNodeRightList)

        TITLE = 'Sidewall Node lateral displacement'
        if showvalue ==1: 
            Plot_Graph(ImageName+'-StandingWave', StandingWave, TITLE, 'Sector From Top ( Bottom Sector ' + str(int(Sectors/2))+')', 'SW Wave[mm]', 120, 'o', 2, c1='black', c2 = 'red', c3='black', c4='red', annotate=positions, annotate_position=pos)
        else: 
            Plot_Graph(ImageName+'-StandingWave', StandingWave, TITLE, 'Sector From Top ( Bottom Sector ' + str(int(Sectors/2))+')', 'SW Wave[mm]', 120, 'o', 2, c1='black', c2 = 'red', c3='black', c4='red')


        out = open(ImageName+'-SidewaveValues.txt', "w")
        line = "Lateral displacements of sidewall node "+str(WaveMax1[0][0]%offset) + ", " + str(WaveMax2[0][0]%offset)+"\n"
        out.write(line)
        for i in range(1,Sectors+1):
            line = str(i)+', ' + str(SWNodeLeftList[i][1]) + ", " + str(SWNodeRightList[i][1])+"\n"
            out.write(line)
        out.write("\n\n")
        out.write("Success::Post::[Simulation Result] This simulation result was created successfully!!")
        out.close()
        DLW = MaxSW - MinSW 
        print ("* Left  1st Wave = %7.3f, 2nd wave = %7.3f, 3rd wave = %7.3f"%(Left_waves[0], Left_waves[1], Left_waves[2]))
        print ("* Right 1st Wave = %7.3f, 2nd wave = %7.3f, 3rd wave = %7.3f"%(Right_waves[0], Right_waves[1], Right_waves[2]))
        print ("* DLW = %.3f"%(DLW*1000))
        return Left_waves, Right_waves, DLW


def Standingwave_amplitude(values, direction=1): 
    
    vs = []
    ts = []
    for i, v in enumerate(values):
        if i ==0: continue 
        vs.append(v[1])
        ts.append(abs(v[1]))
        
    vmax = max(vs)
    vmin = min(vs)

    tmax = max(ts)
    tc=0;  xc = 0; nc = 0 
    for i, v in enumerate(values):
        if i ==0: continue 
        if tmax == abs(v[1]) : tc = i
        if vmax == v[1] : xc = i
        if vmin == v[1] : nc = i

    N = len(values)-1
    
    if direction == -1: 
        for i, _ in enumerate(vs): 
            vs[i] = -vs[i]

    vmax = max(vs)

    icnt0 = 0 
    i = 0
    ival = 0 
    while i < len(vs): 
        if vs[i] == vmax : 
            icnt0 = ival 
            break 
        del(vs[i])
        ival += 1 
    min_max=[[icnt0, vmax*direction]]

    i = 0
    icnt1 = 0 
    while i < len(vs):
        if i == len(vs)-1 : break 

        slope = vs[i+1] - vs[i]
        if slope > 0: 
            vmin = vs[i]
            icnt1 = ival 
            break 
        del(vs[i])
        ival += 1 

    wave1st = vmax - vmin 
    min_max.append([icnt1, vmin*direction])

    vmax = 0; vmin = 0 
    icnt2=0
    i = 0
    while i < len(vs):
        if i == len(vs)-1 : break 

        slope = vs[i+1] - vs[i]
        if slope < 0: 
            vmax = vs[i]
            icnt2 = ival 
            break 
        del(vs[i])
        ival += 1
    min_max.append([icnt2, vmax*direction])
    
    i = 0
    icnt3=0 
    while i < len(vs):
        if i == len(vs)-1 : break 

        slope = vs[i+1] - vs[i]
        
        if slope > 0: 
            vmin = vs[i]
            icnt3 = ival 
            try:
                if vs[i+4] - vs[i+3] > 0  or vs[i+3] - vs[i+2] > 0:  
                    break 
            except:
                del(vs[i])
                ival += 1 
                continue 
        del(vs[i])
        ival += 1 

    wave2nd = vmax - vmin 
    min_max.append([icnt3, vmin*direction])

    vmax = 0; vmin = 0 
    icnt4=0 
    i = 0
    while i < len(vs):
        if i == len(vs)-1 : break 

        slope = vs[i+1] - vs[i]
        if slope < 0: 
            vmax = vs[i]
            icnt4 = ival
            break 
        del(vs[i])
        ival += 1
    min_max.append([icnt4, vmax*direction])
    
    i = 0
    icnt5=0 
    while i < len(vs):
        if i == len(vs)-1 : break 

        slope = vs[i+1] - vs[i]
        if slope > 0: 
            vmin = vs[i]
            icnt5 = ival
            try: 
                if vs[i+3] - vs[i+2] > 0  or vs[i+2] - vs[i+1] > 0:  
                    break 
            except:
                del(vs[i])
                ival += 1
                continue 
        del(vs[i])
        ival += 1

    wave3rd = vmax - vmin 
    min_max.append([icnt5, vmin*direction])
    waves = [wave1st, wave2nd, wave3rd]
    return waves, min_max




def Plot_ContourNoPatch(ImageName, TNode, Element, dpi=200, vmin=0, vmax=0): 
    fig, ax = plt.subplots()
    ax.axis('equal')
    # ax.axis('off')
    textsize = 8
    

    color = 'gray'
    lw = 0.2
    
    N = len(Element.Element)
    for i in range(N): 
        if Element.Element[i][6] == 3: 
            N1 = TNode.NodeByID(Element.Element[i][1])
            N2 = TNode.NodeByID(Element.Element[i][2])
            N3 = TNode.NodeByID(Element.Element[i][3])
        
            iX = [N1[2], N2[2], N3[2], N1[2]]
            iY = [N1[3], N2[3], N3[3], N1[3]]
            plt.plot(iX, iY, color, lw=lw, linestyle='-')
        if Element.Element[i][6] == 4: 
            N1 = TNode.NodeByID(Element.Element[i][1])
            N2 = TNode.NodeByID(Element.Element[i][2])
            N3 = TNode.NodeByID(Element.Element[i][3])
            N4 = TNode.NodeByID(Element.Element[i][4])
        
            iX = [N1[2], N2[2], N3[2], N4[2], N1[2]]
            iY = [N1[3], N2[3], N3[3], N4[3], N1[3]]
            plt.plot(iX, iY, color, lw=lw, linestyle='-')
        else: 
            pass
    X = []
    Y = []
    T = []
    MaxT = 0.0
    MinT = 0.0
    MaxY = -10000.0
    MinY = 10000.0
    N = len(TNode.Node)
    for i in range(N): 
        X.append(TNode.Node[i][2])
        Y.append(TNode.Node[i][3])
        T.append(TNode.Node[i][4])
        
        if TNode.Node[i][3]>MaxY and TNode.Node[i][4]> vmin:
            MaxY = TNode.Node[i][3] 
        if TNode.Node[i][3]<MaxY and TNode.Node[i][4]> vmin:
            MinY = TNode.Node[i][3] 
        
        if TNode.Node[i][4]>MaxT:
            MaxT = TNode.Node[i][4] 
        if TNode.Node[i][4]<MinT:
            MinT = TNode.Node[i][4] 
    strMaxT = 'Max Inner Temperature='+str(format(MaxT,".1f"))
    # print strMaxT
    plt.title(strMaxT, fontsize=textsize)
    
    if vmin == 0 and vmax ==0:
        vmin = MinT
        vmax = MaxT
        levels = np.linspace(vmin, vmax, 100)
    if vmin != 0 and vmax ==0: 
        # vmin = MinT
        vmax = MaxT
        levels = np.linspace(vmin, vmax, 100)
        # print "vmin", vmin
    elif vmin == 0 and vmax !=0: 
        vmin = MinT
        # vmax = MaxT
        levels = np.linspace(vmin, vmax, 100)
    else:         
        levels = np.linspace(vmin, vmax, 100)
    
    # levels = np.linspace(100000.0, 500000, 100)
    cont = plt.tricontourf(X, Y, T, levels, extend = "max", antialiased=True, cmap='jet')
    
    plt.ylim(MinY*1.5, MaxY*1.5)
    # print MinY, MaxY
    
    sf = []
    Out = Element.OuterEdge(TNode)
    N = len(Out.Edge)
    for i in range(N):
        Ni = TNode.NodeByID(Out.Edge[i][0])
        sf.append([Ni[2], Ni[3]])
    Ni = TNode.NodeByID(Out.Edge[N-1][1])
    sf.append([Ni[2], Ni[3]])
        
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2%", pad=0.01)
    cbar = plt.colorbar(cont, cax=cax)
    cbar.ax.tick_params(labelsize=5)
    plt.savefig(ImageName, dpi=dpi)
    plt.clf()

def Plot_BarChart(ImageName, Names, Values, V1=[], V2=[], dpi=80, width=0.8, title='', label1='', label2='', label3='', xlabel='', ylabel='', value=0, **args): 
    
    for key, value in args.items():
        if key == 'v1':
            V1 = value
        if key == 'v2':
            V2 = value
            
    # fig, ax = plt.subplots()
    n = 1
    if len(V1)>0:
        n += 1
    if len(V2)>0:
        n += 1
    
    width = width / float(n)
    # print "N-", n, "Values=", Values
    
    X1=[]
    X2=[]
    X3=[]
    X = []
    max = 0.0
    if n ==1:
        
        for i in range(len(Names)):
            X.append(float(i)+(1-width)/2)
            if Values[i] > max:
                max = Values[i]
            
        if label1 !="":
            plt.bar(X, Values, width, color='b' , label=label1)
            if value ==1 :
                for i in range(len(Names)):
                    plt.text(X[i]+0.4, Values[i] * 1.05, Values[i], ha='center', va='bottom')
        else:
            plt.bar(X, Values, width, color='b')
            if value ==1 :
                for i in range(len(Names)):
                    plt.text(X[i]+0.4, Values[i] * 1.05, Values[i], ha='center', va='bottom')
            
        # print "Bar Position=", X
            
    if n == 2: 
        for i in range(len(Names)):
            X.append(float(i)+(1-width)/2 - width/2)
            X2.append(float(i)+(1-width)/2 + width/2 )
            if Values[i] > max:
                max = Values[i]
            if V1[i] > max:
                max = V1[i]
            
        if label1 !="":
            plt.bar(X, Values, width, color='b', label=label1)
        else: 
            plt.bar(X, Values, width, color='b')#, align="center")
    
        if label2 != "":
            plt.bar(X2, V1, width, color = 'green', label=label2)
        else:
            plt.bar(X2, V1, width, color = 'green')#, align="center")
            
    if n == 3: 
        for i in range(len(Names)):
            X.append(float(i)+(1-width)/2 - width)
            X2.append(float(i)+(1-width)/2 + 0)
            X3.append(float(i)+(1-width)/2 + width )
            if Values[i] > max:
                max = Values[i]
            if V1[i] > max:
                max = V1[i]
            if V2[i] > max:
                max = V2[i]
            
        if label1 !="":
            plt.bar(X, Values, width, color='b', label=label1)
        else: 
            plt.bar(X, Values, width, color='b')#, align="center")
    
        if label2 != "":
            plt.bar(X2, V1, width, color = 'green', label=label2)
        else:
            plt.bar(X2, V1, width, color = 'green')#, align="center")
        
        if label3 != "":
            plt.bar(X3, V2, width, color = 'gray', label=label3)# , align="center") 
        else: 
            plt.bar(X3, V2, width, color = 'gray')# , align="center")
            
    for i in range(len(Names)):        
        X1.append(float(i)+0.5)
    plt.xticks(X1, Names)
    if label1 != '' or label2 != '' or label3 != '':
        plt.legend()
    if xlabel != "":
        plt.xlabel(xlabel)
    if ylabel != "":
        plt.ylabel(ylabel)
    if title != "":
        plt.title(title)
    plt.tight_layout()
    plt.ylim(0, max*1.2)
    plt.savefig(ImageName, dpi=dpi)
    
    plt.clf()

def Plot_MappedContour(N, E, ImagefileName, dpi=300, RangeMin=0.0, RangeMax=3.0, NR=0.99, PointGap=0.15E-3, ColorRangeMax=0, Angle=0, **args):
    print ("*** Plotting Contour Image :%s"%(ImagefileName))
    # Values = ElementValueToNodeValue(N, E, NR, PointGap)
    
    for key, value in args.items():
        if key == 'Dpi' or key == 'DPI':
            dpi = value
        if key == 'rangemin' or key == 'Rangemin' or key == 'rmn':
            RangeMin = value
        if key == 'rangemax' or key == 'Rangemax' or key == 'rmx':
            RangeMax = value
        if key == 'nr':
            NR = value
        if key == 'pointgap' or key == 'Pointgap' or key == 'pointdist' or key == 'pointdistance':
            PointGap = value
        if key == 'colorrangemax' or key == 'crangemax' or key == 'crmx' or key == 'colormax':
            ColorRangeMax = value
        if key == 'angle':
            Angle = value
            
        

    # t1 = time.time()
    Values = ElementCenterValueToInnerValues(N, E, NR, PointGap)
    # t2 = time.time()
    # print ("getting inner values", t2-t1)
    
    MappedPlot(Values, N, E, ImagefileName, dpi, RangeMin, RangeMax, ColorRangeMax, Angle)
  
def MappedPlot(PointValues, N, E, ImName, dpi=300, RangeMin=0.0, RangeMax=3.0, ColorRangeMax=0, angle=0, **args):
    
    for key, value in args.items():
        if key == 'Dpi' or key == 'DPI':
            dpi = value
        if key == 'rangemin' or key == 'Rangemin' or key == 'rmn':
            RangeMin = value
        if key == 'rangemax' or key == 'Rangemax' or key == 'rmx':
            RangeMax = value
        if key == 'nr':
            NR = value
        if key == 'colorrangemax' or key == 'crangemax' or key == 'crmx' or key == 'colormax':
            ColorRangeMax = value
        if key == 'angle':
            Angle = value
    
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('off')
    color = 'gray'
    lw = 0.2

    for i in range(len(E.Element)):
        if E.Element[i][6] == 3:
            N1 = N.NodeByID(E.Element[i][1])
            N2 = N.NodeByID(E.Element[i][2])
            N3 = N.NodeByID(E.Element[i][3])
            x1 = N1[2]
            x2 = N2[2]
            x3 = N3[2]
            y1 = N1[3]
            y2 = N2[3]
            y3 = N3[3]

            iX = [x1, x2, x3, x1]
            iY = [y1, y2, y3, y1]
            plt.plot(iX, iY, color, lw=lw, linestyle='-')

        elif E.Element[i][6] == 4:
            N1 = N.NodeByID(E.Element[i][1])
            N2 = N.NodeByID(E.Element[i][2])
            N3 = N.NodeByID(E.Element[i][3])
            N4 = N.NodeByID(E.Element[i][4])
            x1 = N1[2]
            x2 = N2[2]
            x3 = N3[2]
            x4 = N4[2]
            
            y1 = N1[3]
            y2 = N2[3]
            y3 = N3[3]
            y4 = N4[3]

            iX = [x1, x2, x3, x4, x1]
            iY = [y1, y2, y3, y4, y1]
            plt.plot(iX, iY, color, lw=lw, linestyle='-')

        else:
            pass

    sf = []
    edge = []
    #    print 'EDGE', OE[0]
    
    OE = E.OuterEdge(N)
    for i in range(len(OE.Edge)):
        N1 = N.NodeByID(OE.Edge[i][0])
        x1 = N1[2]
        y1 = N1[3]
        
        sf.append([x1, y1])
        edge.append([OE.Edge[i][0], x1, y1])

    N1 = N.NodeByID(OE.Edge[i-1][1])
    x1 = N1[2]
    y1 = N1[3]
    sf.append([x1, y1])

    # t1 = time.time()
    # Ni = len(PointValues)
    # Xi = []
    # Yi = []
    # listValue =[]
    # for i in range(Ni):
    #     Xi.append(PointValues[i][0])
    #     Yi.append(PointValues[i][1])
    #     listValue.append(PointValues[i][2])
    # t2 = time.time()
    # print ("converting previous", t2-t1)

    # t1 = time.time()
    PV = np.array(PointValues)
    Xi = PV[:, [0] ]
    Yi = PV[:, [1]]
    listValue = PV[:, [2]]
    # t2 = time.time()
    # print ("converting", t2-t1)

    
    Mid = Mean(listValue)
    stdev = StandardDeviation(listValue)

    if ColorRangeMax == 0:
        rMax = Mid + stdev * RangeMax
    else:
        angle = angle - 180
        txtTitle = 'Viscoelastic Energy Loss Distribution at ' + str(angle) + ' Degree'
        plt.title(txtTitle)
        rMax = ColorRangeMax
    # t1 = time.time()
    contour = plt.scatter(Xi, Yi, c =listValue, s=0.3, edgecolors='none', vmin=0, vmax=rMax, cmap='jet')
    # t2 = time.time()
    # print ("matplot scatter", t2-t1)

    # print 'Range Max=', RangeMax, rMin, rMax
    patch = PathPatch(Path(sf), facecolor='none', edgecolor='none')
    ax.add_patch(patch)
    # for c in contour.collections:
    #     c.set_clip_path(patch)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1%", pad=0.1)

    cbar = plt.colorbar(contour, cax=cax, format='%.0f')
    cbar.ax.tick_params(labelsize=5)
    plt.savefig(ImName, dpi=dpi)
    # t1 = time.time()
    # Vmin = 10000000.0
    # Vmax = 0.0
    # for i in range(len(PointValues)):
    #     if Vmin > PointValues[i][2]:
    #         Vmin = PointValues[i][2]
    #     if Vmax < PointValues[i][2]:
    #         Vmax = PointValues[i][2]
    # t2 = time.time()
    # print ("min/max", t2-t1)
    Vmin = np.min(listValue)
    Vmax = np.max(listValue)
    # t3 = time.time()
    # print ("np min/max", t3-t2)

    # print ('Max=', format(Vmax, '.0f'), 'Min=', format(Vmin, '.0f'), 'Mean=', format(Mid, '.0f'), 'Std Dev=', format(stdev, '.0f'))
    print ("Max = %.0f, Min = %.0f, Mean = %.0f, Std Dev = %.0f"%(Vmax, Vmin, Mid, stdev))
    plt.clf()

def Plot_AngleMappedELDContour(AngleNode, ELDFile, Angle, Offset, Element, ImagefileName, dpi=300, RangeMin=0.0, RangeMax=3.0, NR=0.99, PointGap=0.15E-3, RangeMaxValue=0, **args):
    SimTime = ''
    for key, value in args.items():
        if key == 'Dpi' or key == 'DPI':
            dpi = value
        if key == 'rangemin' or key == 'Rangemin' or key == 'rmn':
            RangeMin = value
        if key == 'rangemax' or key == 'Rangemax' or key == 'rmx':
            RangeMax = value
        if key == 'nr':
            NR = value
        if key == 'pointgap' or key == 'Pointgap' or key == 'pointdist' or key == 'pointdistance':
            PointGap = value
        if key == 'colorrangemax' or key == 'crangemax' or key == 'crmx' or key == 'colormax' or key == 'rangemaxvalue' or key == 'Rangemaxvalue':
            RangeMaxValue = value
        if key == 'simtime': 
            SimTime = value
            
            

    N = len(AngleNode.Node)
    SeekSector=[]
    Counting=[]
    for i in range(N):
        Sect = int(AngleNode.Node[i][0]/Offset)
        if AngleNode.Node[i][4] > Angle:
            Sect -= 1
        if i ==0:
            SeekSector.append(Sect)
            Counting.append(1)
        else:
            isSector = 0    
            for j in range(len(SeekSector)):
                if SeekSector[j] == Sect:
                    Counting[j] += 1
                    isSector = 1
                    break
            if isSector == 0:
                SeekSector.append(Sect)
                Counting.append(1)
    N=len(Counting)
    M = Counting[0]
    index = 0
    for i in range(1, N):
        if Counting[i] > M:
            M = Counting[i]
            index = i
    Sector = SeekSector[index]
    # print '************** Sector:', Sector, SeekSector, Counting
    
    ELD = GetELDatSectionSMART(ELDFile, Sector, simtime=SimTime)
    
    N = len(Element.Element)
    M = len(ELD)
    for i in range(N): 
        for j in range(M): 
            if Element.Element[i][0] == ELD[j][0]:
                Element.Element[i][10] = ELD[j][1]
                break
    N = len(AngleNode.Node)
    if Angle > 90 and Angle < 270: 
        for i in range(N):
            AngleNode.Node[i][0] = AngleNode.Node[i][0] % Offset
            AngleNode.Node[i][3] = - AngleNode.Node[i][3]
    else:
        for i in range(N):
            AngleNode.Node[i][0] = AngleNode.Node[i][0] % Offset
            AngleNode.Node[i][3] =  AngleNode.Node[i][3]
    
    Plot_MappedContour(AngleNode, Element, ImagefileName , dpi, RangeMin, RangeMax, NR, PointGap, RangeMaxValue, Angle)
    
def Plot_CordTension(sdb, targetsdb, imagename, Element, Offset=10000, TreadNo=10000000, node=''):
    
    text = '** Cord Tension Data (Distance from center[mm], Tension[kgf])\n\n'
    Tensions = ResultSDB(sdb, targetsdb, Offset, TreadNo, 6, -1)   ## [Element_ID, Strain, Force, Stress]
    for lst in Tensions:        lst[0] = lst[0]%Offset
    BtTensions=[]
    CcTensions=[]
    BTmax = 0; CCmax = 0

    BT1Length = 0; BT2Length = 0; BT3Length = 0; BT4Length = 0
    C01Length = 0; C02Length = 0
    BT1Edge = Element.ElsetToEdge("BT1");     BT1Edge.Sort(item=-1,   reverse=True)
    text += "** Belt 1 Cord Tension\n"
    for edge in BT1Edge.Edge:        
        BT1Length += edge[5]
        edge[5] = BT1Length 
    tmp =["BT1"]
    for edge in BT1Edge.Edge:        
        edge[5] -= BT1Length/2.0
        for tn in Tensions: 
            if tn[0] == edge[4]: 
                tmp.append([edge[5]*1000, tn[2]/9.8])
                text += str(format(edge[5]*1000, '.2f')) +", " + str(tn[2]/9.8) + "\n"
                if tn[2]/9.8 > BTmax: 
                    BTmax = tn[2]/9.8
                break
    BtTensions.append(tmp)




    BT2Edge = Element.ElsetToEdge("BT2");     BT2Edge.Sort(item=-1,   reverse=True)
    text += "\n** Belt 2 Cord Tension\n"
    for edge in BT2Edge.Edge:        
        BT2Length += edge[5]
        edge[5] = BT2Length 
    tmp =["BT2"]
    for edge in BT2Edge.Edge:        
        edge[5] -= BT2Length/2.0
        for tn in Tensions: 
            if tn[0] == edge[4]: 
                tmp.append([edge[5]*1000, tn[2]/9.8])
                text += str(format(edge[5]*1000, '.2f')) +", " + str(tn[2]/9.8) + "\n"
                if tn[2]/9.8 > BTmax: 
                    BTmax = tn[2]/9.8
                break
    BtTensions.append(tmp)

    BT3Edge = Element.ElsetToEdge("BT3")   
    if len(BT3Edge.Edge) > 0: 
        text += "\n** Belt 3 Cord Tension\n"
        BT3Edge.Sort(item=-1,   reverse=True)
        for edge in BT3Edge.Edge:        
            BT3Length += edge[5]
            edge[5] = BT3Length 
        tmp=["BT3"]
        for edge in BT3Edge.Edge:        
            edge[5] -= BT3Length/2.0
            for tn in Tensions: 
                if tn[0] == edge[4]: 
                    tmp.append([edge[5]*1000, tn[2]/9.8])
                    text += str(format(edge[5]*1000, '.2f')) +", " + str(tn[2]/9.8) + "\n"
                    if tn[2]/9.8 > BTmax: 
                        BTmax = tn[2]/9.8
                    break
        BtTensions.append(tmp)

    BT4Edge = Element.ElsetToEdge("BT4")     
    if len(BT4Edge.Edge) > 0: 
        text += "\n** Belt 4 Cord Tension\n"
        BT4Edge.Sort(item=-1,   reverse=True)
        for edge in BT4Edge.Edge:        
            BT4Length += edge[5]
            edge[5] = BT4Length
        tmp=["BT4"] 
        for edge in BT4Edge.Edge:        
            edge[5] -= BT4Length/2.0
            for tn in Tensions: 
                if tn[0] == edge[4]: 
                    tmp.append([edge[5]*1000, tn[2]/9.8])
                    text += str(format(edge[5]*1000, '.2f')) +", " + str(tn[2]/9.8) + "\n"
                    if tn[2]/9.8 > BTmax: 
                        BTmax = tn[2]/9.8
                    break
        BtTensions.append(tmp)

    SPCEdge = Element.ElsetToEdge("SPC")     
    SPCLength = 0.0
    if len(SPCEdge.Edge) > 0: 
        text += "\n** Spiral Coil Cord Tension\n"
        SPCEdge.Sort(item=-1,   reverse=True)
        for edge in SPCEdge.Edge:        
            SPCLength += edge[5]
            edge[5] = SPCLength
        tmp=["SPC"] 
        for edge in SPCEdge.Edge:        
            edge[5] -= SPCLength/2.0
            for tn in Tensions: 
                if tn[0] == edge[4]: 
                    tmp.append([edge[5]*1000, tn[2]/9.8])
                    text += str(format(edge[5]*1000, '.2f')) +", " + str(tn[2]/9.8) + "\n"
                    if tn[2]/9.8 > BTmax: 
                        BTmax = tn[2]/9.8
                    break
        BtTensions.append(tmp)

    C01Edge = Element.ElsetToEdge("C01");     C01Edge.Sort(item=-1,   reverse=True)
    text += "\n** Carcass (1) Cord Tension\n"
    for edge in C01Edge.Edge:        
        C01Length += edge[5]
        edge[5] = C01Length 
    tmp=["C01"]  
    for edge in C01Edge.Edge:        
        edge[5] -= C01Length/2.0
        for tn in Tensions: 
            if tn[0] == edge[4]: 
                tmp.append([edge[5]*1000, tn[2]/9.8])
                text += str(format(edge[5]*1000, '.2f')) +", " + str(tn[2]/9.8) + "\n"
                if tn[2]/9.8 > CCmax: 
                    CCmax = tn[2]/9.8
                break
    CcTensions.append(tmp)

    C02Edge = Element.ElsetToEdge("C02")     
    if len(C02Edge.Edge) > 0: 
        text += "\n** Carcass (1) Cord Tension\n"
        C02Edge.Sort(item=-1,   reverse=True)
        for edge in C02Edge.Edge:        
            C02Length += edge[5]
            edge[5] = C02Length 
        tmp = ["C02"]
        for edge in C02Edge.Edge:        
            edge[5] -= C02Length/2.0
            for tn in Tensions: 
                if tn[0] == edge[4]: 
                    tmp.append([edge[5]*1000, tn[2]/9.8])
                    text += str(format(edge[5]*1000, '.2f')) +", " + str(tn[2]/9.8) + "\n"
                    if tn[2]/9.8 > CCmax: 
                        CCmax = tn[2]/9.8
                    break
        CcTensions.append(tmp)

    if len(BT3Edge.Edge)> 0:
        tmp =["BT2 Range"]
        for edge in BT2Edge.Edge:        
            for tn in Tensions: 
                if tn[0] == edge[4]: 
                    tmp.append([edge[5]*1000, CCmax])
                    break
        CcTensions.append(tmp)
    else:
        tmp =["BT1 Range"]
        for edge in BT1Edge.Edge:        
            for tn in Tensions: 
                if tn[0] == edge[4]: 
                    tmp.append([edge[5]*1000, CCmax])
                    break
        CcTensions.append(tmp)

    title = 'Belt Tension (Max. ' + str(round(BTmax, 1)) + 'kgf)'
    xlb = 'Distance From Center(mm)'
    ylb = 'Tension(kgf)'
    dpi = 150
    Plot_Graph(imagename+ '-BT_Tension.png', BtTensions, title, xlabel=xlb, ylabel=ylb, dpi=dpi)

    title = 'Carcass Tension (Max. ' + str(round(CCmax, 1)) + 'kgf)'
    xlb = 'Distance From Center(mm)'
    ylb = 'Tension(kgf)'
    dpi = 150
    if len(C02Edge.Edge) > 0: 
        Plot_Graph(imagename+ '-CC_Tension.png', CcTensions, title, xlabel=xlb, ylabel=ylb, dpi=dpi, c3="lightgray")
    else:
        Plot_Graph(imagename+ '-CC_Tension.png', CcTensions, title, xlabel=xlb, ylabel=ylb, dpi=dpi, c2="lightgray")

    tensionfile = sdb.split("/")[-1][:-4] + "-CordTensionValue.txt"
    f = open(tensionfile, "w")
    f.writelines(text)
    f.close()

    return 1
    

def PlotCordTension(CordTensionFileName, imageFileName):
    
    with open(CordTensionFileName) as InpFile:
        lines = InpFile.readlines()
        
    bNode = NODE()
    bElement = ELEMENT()
    bElset = ELSET()
    
    for line in lines:
        data = list(line.split(','))
        if data == '\n':
            pass
        elif data[0][0] == '*':
            word = data[0][1:].strip()
            if 'BT' in word or 'C0' in word:
                bElset.AddName(word)

        else:
            bElement.Add([int(data[0]), int(data[3]), int(data[7]), 0, 0, word, 2, float(data[2]), (float(data[5]) + float(data[9]))/2.0, (float(data[6]) + float(data[10].strip()))/2.0, float(data[1])])
            bNode.Add([int(data[3]), float(data[4]), float(data[5]), float(data[6])])
            bNode.Add([int(data[7]), float(data[8]), float(data[9]), float(data[10].strip())])
            bElset.AddNumber(int(data[0]), word)
    bNode.DeleteDuplicate()  
    # bElement.Print()
    ENames = bElement.ElsetNames()
    N = len(ENames)
    
    BtTensions=[]
    CoTensions=[]
    for i in range(N):
        Set = bElement.Elset(ENames[i])
        sN = len(Set.Element)
        tmp = [ENames[i]]
        length = 0.0
        for j in range(sN): 
            length += Set.Element[j][7]
            tmp.append([length, Set.Element[j][10]/9.8])
        # print 'SET NAME ====> ', ENames[i], 'Length', length
        for j in range(1,sN+1): 
            # print 'Position', tmp[j][0], 'Shifted to ',  tmp[j][0] - length/2.0
            tmp[j][0] = tmp[j][0] - length/2.0
        if 'BT' in ENames[i]:
            BtTensions.append(tmp)
        else:
            CoTensions.append(tmp)
        
    Max = 0.0
    N = len(BtTensions)
    for i in range(N):
        M = len(BtTensions[i])
        for j in range(1, M):
            if BtTensions[i][j][1] > Max:
                Max = BtTensions[i][j][1]    
    
    title = 'Belt Tension (Max. ' + str(round(Max, 1)) + 'kgf)'
    file = imageFileName + '-BT_Tension.png'
    Plot_Graph(file, BtTensions, title, 'Distance From Center(mm)', 'Tension(kgf)', 150)
    Max = 0.0
    N = len(CoTensions)
    for i in range(N):
        M = len(CoTensions[i])
        for j in range(1, M):
            if CoTensions[i][j][1] > Max:
                Max = CoTensions[i][j][1]    
    title = 'Carcass Tension (Max. ' + str(round(Max, 1)) + 'kgf)'
    file = imageFileName + '-CC_Tension.png'
    Plot_Graph(file, CoTensions, title, 'Distance From Center(mm)', 'Tension(kgf)', 150)   

def Color(elsetname):                ## Define Color set 
    c = ''
    if elsetname == 'CTR' or elsetname == 'CTB':
        c = 'darkgray'
    elif elsetname == 'UTR' or elsetname == 'SUT':
        c = 'lightpink'
    elif elsetname == 'CC1' or elsetname == 'C01' or elsetname == 'C02':
        c = 'lightsalmon'
    elif elsetname == 'CCT':
        c = 'purple'
    elif elsetname == 'BTT':
        c = 'steelblue'
    elif elsetname == 'FIL' or elsetname == 'LBF':
        c = 'green'
    elif elsetname == 'UBF':
        c = 'lightpink'
    elif elsetname == 'IL1' or elsetname == 'L11':
        c = 'y'
    elif elsetname == 'BSW':
        c = 'yellowgreen'
    elif elsetname == 'HUS':
        c = 'steelblue'
    elif elsetname == 'RIC':
        c = 'darkgray'
    elif elsetname == 'SHW':
        c = 'darkcyan'
    elif elsetname == 'BD1':
        c = 'dimgray'
    elif elsetname == 'BDC':
        c = 'black'
    elif elsetname == 'MEMB':
        c = 'black'
    elif elsetname == 'DOT':
        c = 'red'
    elif elsetname == 'PRESS':
        c = 'blue'
    elif elsetname == 'RIM':
        c = 'red'
    elif elsetname == 'TDBASE':
        c = 'aqua'
    elif elsetname == 'TDROAD':
        c = 'coral'
    elif elsetname == 'BDTOP':
        c = 'gray'
    else:
        c = 'silver'
    return c

def ListNodeOnlySlave(Master, Slave):  ##  for calculating Nodal value at node which is on Slave Tie Edge  
    
    Nodes = []
    
    for i in range(len(Slave.Edge)):
        
        for m in range(2):
            f = 0
            for j in range(len(Master.Edge)):
                if Slave.Edge[i][m] == Master.Edge[j][0] or Slave.Edge[i][m] == Master.Edge[j][1]:
                    f = 1
                    break
            if f == 0:
                for j in range(len(Master.Edge)):
                    if Master.Edge[j][5] == Slave.Edge[i][5]:
                        # print 'Master', Master.Edge[j]
                        # print 'Slave ', Slave.Edge[j]
                        # print '-', Slave.Edge[i][m], Slave.Edge[i][2], Slave.Edge[i][4], Slave.Edge[i][0], Slave.Edge[i][1], \
                              # Master.Edge[j][2], Master.Edge[j][4], Master.Edge[j][0], Master.Edge[j][1]
                        Nodes.append([Slave.Edge[i][m], Slave.Edge[i][2], Slave.Edge[i][4], Slave.Edge[i][0], Slave.Edge[i][1], \
                                      Master.Edge[j][2], Master.Edge[j][4], Master.Edge[j][0], Master.Edge[j][1]])
                        ## NodeSlave =[[SlaveNodeID, Element Name of the node, Slave EL No(ID), Slave Edge N1, N2, Master Element Name, Master EL No, Master Edge N1, N2], ..]
    return Nodes           
    
def ElementValueToNodeValue(N, E, NR=0.98, G= 0.15E-3, **args):   ## For Calculating the values at points in Element based on nodal value 
    
    for key, value in args.items():
        if key == 'nr':
            NR = value
        if key == 'pointgap' or key == 'Pointgap' or key == 'pointdist' or key == 'pointdistance' or key == 'g':
            G = value
    

    ## G : Gap Between Points (mm)
    Values=[]
    EN = len(E.Element)
    
    MasterEdge, SlaveEdge = E.MasterSlaveEdge(N)
    NodeSlave = ListNodeOnlySlave(MasterEdge, SlaveEdge)
    ## NodeSlave =[[SlaveNodeID, Element Name of the node, Slave EL No(ID), Slave Edge N1, N2, Master Element Name, Master EL No, Master Edge N1, N2], ..]
    for i in range(EN): 
        if E.Element[i][6] == 3 or E.Element[i][6] == 4:
            if len(E.Element[i]) == 11: 
                AlreadyDone = 0
                break
            elif len(E.Element[i]) == 19: 
                AlreadyDone = 1
                break
            else: 
                print ("CHECK ELEMENT Member.. (Element Value to Node Value)")
                return 0
        
    
    if AlreadyDone == 0 :
        for i in range(EN): 
            if E.Element[i][6] == 3 or E.Element[i][6] == 4:
                nN = E.Element[i][6]
                NodalArea = ElementNodalArea(E.Element[i], N)
                for j in range(3):
                    E.Element[i].append(NodalArea[j])
                if nN == 4:
                    E.Element[i].append(NodalArea[3])
                else:
                    E.Element[i].append('')
            else:
                E.Element[i].append('')
                E.Element[i].append('')
                E.Element[i].append('')
                E.Element[i].append('')
    else:
        # print 'Data is Filled already', E.Element[i]
        for i in range(EN): 
            if E.Element[i][6] == 3 or E.Element[i][6] == 4:
                nN = E.Element[i][6]
                NodalArea = ElementNodalArea(E.Element[i], N)
                for j in range(3):
                    E.Element[i][11+j]= NodalArea[j]
                if nN == 4:
                    E.Element[i][14]= NodalArea[3]
                else:
                    E.Element[i][14] = ''
                    
    # print 'Nodal Area, ', E.Element[i]  
    E.Save()
    for i in range(EN):
        # print 'i', i, E.Element[i]
        # print E.Element[i][6]
        if E.Element[i][6] == 3 or E.Element[i][6] == 4:
            nN = E.Element[i][6]
            
            for j in range(1, nN+1):
                nValue=[]
                SumArea = 0.0
                
                #######################################################
                ## Check if the node is a node on slave edge or not 
                ##  then calculate nodal value with length 
                #######################################################
                isSlave = 0
                sN = len(NodeSlave)
                TieShareEL=[]
                for k in range(sN): 
                    if E.Element[i][j] == NodeSlave[k][0]  and NodeSlave[k][1] == NodeSlave[k][5] and NodeSlave[k][1] == E.Element[i][5]:
                        isSlave = 1
                        MasterEL = NodeSlave[k][6]
                        TieShareEL.append(NodeSlave[k][2])
                        # print 'SlaveNODE', NodeSlave[k]
                #######################################################
                ## if the node is a slave node... 
                if isSlave ==1:
                    TieShareEL.append(MasterEL)
                    # print 'Calculation Slave', TieShareEL, 'at', E.Element[i][j], 'of', E.Element[i][0]
                    counting = 0
                    sN = len(TieShareEL)
                    SumLength = 0.0
                    for k in range(sN):
                        for m in range(EN):
                            if TieShareEL[k] == E.Element[m][0]: 
                                counting += 1
                                N1 = N.NodeByID(E.Element[i][j])
                                dist = math.sqrt((N1[2]-E.Element[m][8])*(N1[2]-E.Element[m][8]) + (N1[3]-E.Element[m][9])*(N1[3]-E.Element[m][9]))
                                nValue.append([dist, E.Element[m][10]])
                                SumLength += dist
                    if len(nValue) == 1:
                        if AlreadyDone == 0:
                            E.Element[i].append(nValue[0][1])
                        else: 
                            E.Element[i][14+j]= nValue[0][1]
                    else:
                        sN = len(nValue)
                        NodalValue = 0.0
                        for k in range(sN):
                            NodalValue += (1 - nValue[k][0] / SumLength) * nValue[k][1]
                        if AlreadyDone == 0:
                            E.Element[i].append(NodalValue)
                        else: 
                            E.Element[i][14+j]= NodalValue
                ## if the node is NOT a slave node... 
                else:
                    nValue.append([E.Element[i][10+j], E.Element[i][10]])
                    SumArea += E.Element[i][10+j]
                    for k in range(EN):
                        if i != k and  (E.Element[k][6] == 3 or E.Element[k][6] == 4) and (E.Element[i][5] == E.Element[k][5] ):
                            nNk = E.Element[k][6]
                            for m in range(1, nNk+1):
                                if E.Element[i][j] == E.Element[k][m]:
                                    nValue.append([E.Element[k][10+m], E.Element[k][10]])
                                    SumArea += E.Element[k][10+m]
                    
                    vN = len(nValue)
                    NodalValue = 0.0
                    for k in range(vN):
                        NodalValue += nValue[k][0] / SumArea * nValue[k][1]
                    if AlreadyDone == 0:
                        E.Element[i].append(NodalValue)
                    else:
                        E.Element[i][14+j]= NodalValue
            if nN == 3:
                if AlreadyDone == 0:
                    E.Element[i].append('')
                else:
                    E.Element[i][18]= ''
                
            ###### DONE : The End of Nodal Value Calculation at all nodes of a Element
             
            if NR == 0.3:
                for m in range(len(V)):
                    if math.isnan(V[m]) == False:
                        Values.append([X[m], Y[m], V[m]])

            else:
                # print '* ', E.Element[i]
                N1 = N.NodeByID(E.Element[i][1])
                N2 = N.NodeByID(E.Element[i][2])
                N3 = N.NodeByID(E.Element[i][3])
                if E.Element[i][6] == 3:
                    # print '*** [3]', E.Element[i]
                    X = [N1[2], N2[2], N3[2]]
                    Y = [N1[3], N2[3], N3[3]]
                    V = [E.Element[i][15], E.Element[i][16], E.Element[i][17]]
                    Stx = (X[0], X[1], X[2])
                    Sty = (Y[0], Y[1], Y[2])
                    Stv = (V[0], V[1], V[2])
                    # print "6", Stx, Sty, Stv
                    results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, NR, G)
                    del(Stx)
                    del(Sty)
                    del(Stv)
                    Nn = len(results)
                    for m in range(Nn/3):
                        if math.isnan(results[m * 3 + 2]) == False:
                            Values.append([results[m*3], results[m*3+1], results[m*3+2]])

                elif E.Element[i][6] == 4:
                
                    N4 = N.NodeByID(E.Element[i][4])
                    X = [N1[2], N2[2], N3[2], N4[2]]
                    Y = [N1[3], N2[3], N3[3], N4[3]]
                    V = [E.Element[i][15], E.Element[i][16], E.Element[i][17], E.Element[i][18]]
                    
                    Stx = (X[0], X[1], X[2])
                    Sty = (Y[0], Y[1], Y[2])
                    Stv = (V[0], V[1], V[2])
                    results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, NR, G*1.5)
                    del (Stx)
                    del (Sty)
                    del (Stv)
                    Nn = len(results)
                    for m in range(int(Nn / 3)):
                        if math.isnan(results[m * 3 + 2]) == False:
                            Values.append([results[m * 3], results[m * 3 + 1], results[m * 3 + 2]])
                    Stx = (X[2], X[3], X[0])
                    Sty = (Y[2], Y[3], Y[0])
                    Stv = (V[2], V[3], V[0])
                    results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, NR, G * 1.5)
                    del (Stx)
                    del (Sty)
                    del (Stv)
                    Nn = len(results)
                    for m in range(int(Nn / 3)):
                        if math.isnan(results[m * 3 + 2]) == False:
                            Values.append([results[m * 3], results[m * 3 + 1], results[m * 3 + 2]])
                    Stx = (X[0], X[1], X[3])
                    Sty = (Y[0], Y[1], Y[3])
                    Stv = (V[0], V[1], V[3])
                    results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, NR, G * 1.5)
                    del (Stx)
                    del (Sty)
                    del (Stv)
                    Nn = len(results)
                    for m in range(int(Nn / 3)):
                        if math.isnan(results[m * 3 + 2]) == False:
                            Values.append([results[m * 3], results[m * 3 + 1], results[m * 3 + 2]])
                    Stx = (X[1], X[2], X[3])
                    Sty = (Y[1], Y[2], Y[3])
                    Stv = (V[1], V[2], V[3])
                    results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, NR, G * 1.5)
                    del (Stx)
                    del (Sty)
                    del (Stv)
                    Nn = len(results)
                    for m in range(int(Nn / 3)):
                        if math.isnan(results[m * 3 + 2]) == False:
                            Values.append([results[m * 3], results[m * 3 + 1], results[m * 3 + 2]]) 
        else:
            if AlreadyDone == 0:
                E.Element[i].append('')
                E.Element[i].append('')
                E.Element[i].append('')
                E.Element[i].append('')    
    # print 'Len=', len(Values)
    return Values

def ElementCenterValueToInnerValues(N, E, NR=0.98, G= 0.15E-3, **args):
    for key, value in args.items():
        if key == 'nr':
            NR = value
        if key == 'pointgap' or key == 'Pointgap' or key == 'pointdist' or key == 'pointdistance' or key == 'g':
            G = value
            
            
    Values=[]
    EN = len(E.Element)
    
    MasterEdge, SlaveEdge = E.MasterSlaveEdge(N)
    NodeSlave = ListNodeOnlySlave(MasterEdge, SlaveEdge)
    ## NodeSlave =[[SlaveNodeID, Element Name of the node, Slave EL No(ID), Slave Edge N1, N2, Master Element Name, Master EL No, Master Edge N1, N2], ..]
    for i in range(EN): 
        if E.Element[i][6] == 3 or E.Element[i][6] == 4:
            if len(E.Element[i]) == 11: 
                AlreadyDone = 0
                break
            elif len(E.Element[i]) == 19: 
                AlreadyDone = 1
                break
            else: 
                print ("CHECK ELEMENT Member.. (Element Value to Node Value)")
                return 0
        
    
    if AlreadyDone == 0 :
        for i in range(EN): 
            if E.Element[i][6] == 3 or E.Element[i][6] == 4:
                nN = E.Element[i][6]
                NodalArea = ElementNodalArea(E.Element[i], N)
                for j in range(3):
                    E.Element[i].append(NodalArea[j])
                if nN == 4:
                    E.Element[i].append(NodalArea[3])
                else:
                    E.Element[i].append('')
            else:
                E.Element[i].append('')
                E.Element[i].append('')
                E.Element[i].append('')
                E.Element[i].append('')
    else:
        # print 'Data is Filled already', E.Element[i]
        for i in range(EN): 
            if E.Element[i][6] == 3 or E.Element[i][6] == 4:
                nN = E.Element[i][6]
                NodalArea = ElementNodalArea(E.Element[i], N)
                for j in range(3):
                    E.Element[i][11+j]= NodalArea[j]
                if nN == 4:
                    E.Element[i][14]= NodalArea[3]
                else:
                    E.Element[i][14] = ''
                    
    # print 'Nodal Area, ', E.Element[i]  
    E.Save()
    EL4 = ELEMENT()
    NodesEL4=NODE()
    NoEL4 = 10000
    nc = 0
    for i in range(EN):
        # print 'i', i, E.Element[i]
        # print E.Element[i][6]
        if E.Element[i][6] == 3 or E.Element[i][6] == 4:
            nN = E.Element[i][6]
            
            for j in range(1, nN+1):
                nValue=[]
                SumArea = 0.0
                
                #######################################################
                ## Check if the node is a node on slave edge or not 
                ##  then calculate nodal value with length 
                #######################################################
                isSlave = 0
                sN = len(NodeSlave)
                TieShareEL=[]
                for k in range(sN): 
                    if E.Element[i][j] == NodeSlave[k][0]  and NodeSlave[k][1] == NodeSlave[k][5] and NodeSlave[k][1] == E.Element[i][5]:
                        isSlave = 1
                        MasterEL = NodeSlave[k][6]
                        TieShareEL.append(NodeSlave[k][2])
                        # print 'SlaveNODE', NodeSlave[k]
                #######################################################
                ## if the node is a slave node... 
                if isSlave ==1:
                    TieShareEL.append(MasterEL)
                    # print 'Calculation Slave', TieShareEL, 'at', E.Element[i][j], 'of', E.Element[i][0]
                    counting = 0
                    sN = len(TieShareEL)
                    SumLength = 0.0
                    for k in range(sN):
                        for m in range(EN):
                            if TieShareEL[k] == E.Element[m][0]: 
                                counting += 1
                                N1 = N.NodeByID(E.Element[i][j])
                                dist = math.sqrt((N1[2]-E.Element[m][8])*(N1[2]-E.Element[m][8]) + (N1[3]-E.Element[m][9])*(N1[3]-E.Element[m][9]))
                                nValue.append([dist, E.Element[m][10]])
                                SumLength += dist
                    if len(nValue) == 1:
                        if AlreadyDone == 0:
                            E.Element[i].append(nValue[0][1])
                        else: 
                            E.Element[i][14+j]= nValue[0][1]
                    else:
                        sN = len(nValue)
                        NodalValue = 0.0
                        for k in range(sN):
                            NodalValue += (1 - nValue[k][0] / SumLength) * nValue[k][1]
                        if AlreadyDone == 0:
                            E.Element[i].append(NodalValue)
                        else: 
                            E.Element[i][14+j]= NodalValue
                ## if the node is NOT a slave node... 
                else:
                    nValue.append([E.Element[i][10+j], E.Element[i][10]])
                    SumArea += E.Element[i][10+j]
                    for k in range(EN):
                        if i != k and  (E.Element[k][6] == 3 or E.Element[k][6] == 4) and (E.Element[i][5] == E.Element[k][5] ):
                            nNk = E.Element[k][6]
                            for m in range(1, nNk+1):
                                if E.Element[i][j] == E.Element[k][m]:
                                    nValue.append([E.Element[k][10+m], E.Element[k][10]])
                                    SumArea += E.Element[k][10+m]
                    
                    vN = len(nValue)
                    NodalValue = 0.0
                    for k in range(vN):
                        NodalValue += nValue[k][0] / SumArea * nValue[k][1]
                    if AlreadyDone == 0:
                        E.Element[i].append(NodalValue)
                    else:
                        E.Element[i][14+j]= NodalValue
            if nN == 3:
                if AlreadyDone == 0:
                    E.Element[i].append('')
                else:
                    E.Element[i][18]= ''
                
            ###### DONE : The End of Nodal Value Calculation at all nodes of a Element
             
            if NR == 0.3:
                for m in range(len(V)):
                    if math.isnan(V[m]) == False:
                        Values.append([X[m], Y[m], V[m]])

            else:
                # print '* ', E.Element[i]
                N1 = N.NodeByID(E.Element[i][1])
                N2 = N.NodeByID(E.Element[i][2])
                N3 = N.NodeByID(E.Element[i][3])
                if E.Element[i][6] == 3:
                    # print '*** [3]', E.Element[i]
                    X = [N1[2], N2[2], N3[2]]
                    Y = [N1[3], N2[3], N3[3]]
                    V = [E.Element[i][15], E.Element[i][16], E.Element[i][17]]
                    Stx = (X[0], X[1], X[2])
                    Sty = (Y[0], Y[1], Y[2])
                    Stv = (V[0], V[1], V[2])
                    # print "6", Stx, Sty, Stv
                    results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, NR, G)
                    del(Stx)
                    del(Sty)
                    del(Stv)
                    Nn = len(results)
                    for m in range(int(Nn/3)):
                        if math.isnan(results[m * 3 + 2]) == False:
                            Values.append([results[m*3], results[m*3+1], results[m*3+2]])

                elif E.Element[i][6] == 4:
                    N4 = N.NodeByID(E.Element[i][4]) 
                                                    
                                                    
                                                                                                
                    
                    # tNode=NODE()
                    # tNode.Add( [NoEL4+nc*4 + 1, N1[1], N1[2], N1[3], E.Element[i][15] ])
                    # tNode.Add( [NoEL4+nc*4 + 2, N2[1], N2[2], N2[3], E.Element[i][16] ])
                    # tNode.Add( [NoEL4+nc*4 + 3, N3[1], N3[2], N3[3], E.Element[i][17] ])
                    # tNode.Add( [NoEL4+nc*4 + 4, N4[1], N4[2], N4[3], E.Element[i][18] ])
                    
                    # srnode =ConvexHull(tNode, 23)
                    
                    NodesEL4.Add( [NoEL4+nc*4 + 1, N1[1], N1[2], N1[3], E.Element[i][15] ])
                    NodesEL4.Add( [NoEL4+nc*4 + 2, N2[1], N2[2], N2[3], E.Element[i][16] ])
                    NodesEL4.Add( [NoEL4+nc*4 + 3, N3[1], N3[2], N3[3], E.Element[i][17] ])
                                                                                                   
                    NodesEL4.Add( [NoEL4+nc*4 + 4, N4[1], N4[2], N4[3], E.Element[i][18] ])
                    # try:
                        # EL4.Add( [ NoEL4+nc+1, srnode.Node[0][0], srnode.Node[1][0], srnode.Node[2][0],srnode.Node[3][0] ] )
                    
                    EL4.Add( [ NoEL4+nc+1, NoEL4+nc*4 + 1, NoEL4+nc*4 + 2, NoEL4+nc*4 + 3, NoEL4+nc*4 + 4, E.Element[i][5], E.Element[i][6], E.Element[i][7]    ] )
                    # except:
                        # print  "OUTPUT", len(srnode.Node)
                        # tNode.Image('ERR0-'+str(NoEL4+nc+1), XY=23, cm = 1, ci=4, size = 10)
                        # srnode.Image('ERR-'+str(NoEL4+nc+1), XY=23, cm = 0, ci=0, size = 10)
                        # srnode.ImageLine('ERR-'+str(NoEL4+nc+1), XY=23, size = 10)
                        
                        # sys.exit()
                    
                    nc += 1
                    
                    # etl = ELEMENT()
                    # etl.Add( EL4.Element[nc-1] )
                    
                    # if etl.Element[0][0] == 10029 or etl.Element[0][0] == 10524 or etl.Element[0][0] == 10523:
                        # print etl.Element[0]
                        # print "/////", srnode.Node[0][0], srnode.Node[1][0], srnode.Node[2][0], srnode.Node[3][0]
                        # srnode.ImageLine('ERR1-'+str(NoEL4+nc), XY=23, size = 10)
                        
                        # tnode = Innerpoints(G, etl, NodesEL4, XY=23)
                    
                        # tnode.Image(str(etl.Element[0][0]), XY=23, cm = 1, ci=4, size = 10)
                        # print ("no of points = %d (%f)\n" %(len(tnode.Node), G))
                        # print NodesEL4.Node[(nc-1)*4]
                        # print NodesEL4.Node[(nc-1)*4+1]
                        # print NodesEL4.Node[(nc-1)*4+2]
                        # print NodesEL4.Node[(nc-1)*4+3]
                        
                    
                    # def Jacobian(x1, x2, x3, x4, y1, y2, y3, y4):
                    ####################################################################################
                    # N4 = N.NodeByID(E.Element[i][4])
                    # X = [N1[2], N2[2], N3[2], N4[2]]
                    # Y = [N1[3], N2[3], N3[3], N4[3]]
                    # V = [E.Element[i][15], E.Element[i][16], E.Element[i][17], E.Element[i][18]]
                    
                    # Stx = (X[0], X[1], X[2])
                    # Sty = (Y[0], Y[1], Y[2])
                    # Stv = (V[0], V[1], V[2])
                    # results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, NR, G*1.5)
                    # del (Stx)
                    # del (Sty)
                    # del (Stv)
                    # Nn = len(results)
                    # for m in range(Nn / 3):
                        # if math.isnan(results[m * 3 + 2]) == False:
                            # Values.append([results[m * 3], results[m * 3 + 1], results[m * 3 + 2]])
                    # Stx = (X[2], X[3], X[0])
                    # Sty = (Y[2], Y[3], Y[0])
                    # Stv = (V[2], V[3], V[0])
                    # results = _islm.ValuesOfPointsInElement(Stx, Sty, Stv, NR, G * 1.5)
                    # del (Stx)
                    # del (Sty)
                    # del (Stv)
                    # Nn = len(results)
                    # for m in range(Nn / 3):
                        # if math.isnan(results[m * 3 + 2]) == False:
                            # Values.append([results[m * 3], results[m * 3 + 1], results[m * 3 + 2]])
                    ####################################################################################
                    
                    
        else:
            if AlreadyDone == 0:
                E.Element[i].append('')
                E.Element[i].append('')
                E.Element[i].append('')
                E.Element[i].append('') 
                    
    
    # I = len(NodesEL4.Node)
    # max = -10000000000000000.0
    # for i in range(I):
        # if NodesEL4.Node[i][4] > max:
            # max = NodesEL4.Node[i][4]
    xyv = Innerpoints(G, EL4, NodesEL4, XY=23)
    I = len(xyv.Node)
    for i in range(I):
        # if xyv.Node[i][4] > 0 and xyv.Node[i][4] < max:
            Values.append( [ xyv.Node[i][2], xyv.Node[i][3], xyv.Node[i][4] ]) 
    
    return Values

def ElementNodalArea(listElement, Node):    ## For Calculating the Nodal Area at each node on a Element 
    
    nN= listElement[6]
    eNode=NODE()
    
    N1 = Node.NodeByID(listElement[1])
    eNode.Add(N1)
    N2 = Node.NodeByID(listElement[2])
    eNode.Add(N2)
    N3 = Node.NodeByID(listElement[3])
    eNode.Add(N3)
    
    eNode.Add([5001, (N1[1]+N2[1])/2, (N1[2]+N2[2])/2, (N1[3]+N2[3])/2  ])
    eNode.Add([5002, (N2[1]+N3[1])/2, (N2[2]+N3[2])/2, (N2[3]+N3[3])/2  ])
    
    nArea = []
    
    if nN == 3: 
        eArea = Area([N1[0], N2[0], N3[0]], eNode)
        eNode.Add([5000, (N1[1]+N2[1]+N3[1])/2, eArea[1], eArea[2] ])
        eNode.Add([5003, (N3[1]+N1[1])/2, (N3[2]+N1[2])/2, (N3[3]+N1[3])/2  ])
        area = Area([N1[0], 5001, 5000, 5003], eNode)
        nArea.append(area[0])
        area = Area([N2[0], 5002, 5000, 5001], eNode)
        nArea.append(area[0])
        area = Area([N3[0], 5003, 5000, 5002], eNode)
        nArea.append(area[0])
    elif nN == 4: 
        N4 = Node.NodeByID(listElement[4])
        eNode.Add(N4)
        eArea = Area([N1[0], N2[0], N3[0], N4[0]], eNode)
        eNode.Add([5000, (N1[1]+N2[1]+N3[1]+N4[1])/2, eArea[1], eArea[2] ])
        eNode.Add([5003, (N3[1]+N4[1])/2, (N3[2]+N4[2])/2, (N3[3]+N4[3])/2  ])
        eNode.Add([5004, (N4[1]+N1[1])/2, (N4[2]+N1[2])/2, (N4[3]+N1[3])/2  ])
        area = Area([N1[0], 5001, 5000, 5004], eNode)
        nArea.append(area[0])
        area = Area([N2[0], 5002, 5000, 5001], eNode)
        nArea.append(area[0])
        area = Area([N3[0], 5003, 5000, 5002], eNode)
        nArea.append(area[0])
        area = Area([N4[0], 5004, 5000, 5003], eNode)
        nArea.append(area[0])
    del(eNode)
    return nArea

def NodeContactShearForce (sfricFileName, resultfile, strSimCode, Offset=10000, TreadNo = 10000000, **args): 
    
    for key, value in args.items():
        if key == 'offset':
            Offset = value
        if key == 'treadno' or key == 'Treadno' or key == 'treadnumber' or key == 'Treadnumber' :
            TreadNo = value
    
    # print "Contact Shear"
    ContactPressureFile = strSimCode + "-ContactShearForce.tmp"
    # print "Contact Shear", ContactPressureFile
    # print "model", sfricFileName
    # print "result", resultfile
    SFRICResults(sfricFileName, resultfile, 7, 0, Offset, TreadNo) ## force 
    # print "Contact Shear"
    ContactPressureFile = strSimCode + "-ContactShearForce.tmp"
    sNode = NODE()
    with open(ContactPressureFile) as FPtxt:
        FPData = FPtxt.readlines()
    for line in FPData: 
        if line[0] == '*':
            continue
        data = list(line.split(","))
        sNode.Add([int(data[0].strip()), float(data[2].strip()), float(data[3].strip()), float(data[4].strip()), float(data[1].strip())])
        
    return sNode      

def RollingContactPressure(lastSFRIC, iter=1, vmin=50000, vmax=50000, treadno= 10000000, offset=10000, **args):

    print ("iteration=", iter)
    for key, value in args.items():
        if key == "simcode":
            strSimcode=value

    serial = int(lastSFRIC[-3:])
    SFRIC = lastSFRIC[:-3]
    pnode = NODE()
    dottingnode=NODE()
    for i in range(iter):
        lstSFRIC = SFRIC + str(format(serial-i, "03"))
        node = ResultSFRIC(SFRIC, lstSFRIC, offset, treadno, 2, 0)
        J = len(node.Node)
        for j in range(J):
            if node.Node[j][0]>=treadno and  node.Node[j][7] > 0:
                if i ==0:
                    pnode.Add([node.Node[j][0], node.Node[j][1], node.Node[j][2], node.Node[j][3], node.Node[j][6]] )
                dottingnode.Add([node.Node[j][0], node.Node[j][1], node.Node[j][2], node.Node[j][3], node.Node[j][6]] )
    if iter > 1:
        ImageNode(dottingnode, file=strSimcode+"-RoadContactPoints.png", dpi=200, xy=21, cm=1)
    del(dottingnode)

    return pnode
        
def RibsBoundary (cedge, NodePressure, NodeDeformed, RibNo, sectors, file='Rib', image=0, bgap=0.5,\
                    offset=10000, treadno= 10000000, dotgap=0.25E-3, XY=21, vmin='', vmax='', dpi=150, \
                    pmin= 50000, pmax =500000, nodereturn=0, fitting=6, **args):
                    
    for key, value in args.items():
        if key == 'xy':
            XY = value
            
            
    print ("## Rib Boundary ###################################")
    # PrintList(sectors)
    
    boundlimit = 0.1
    
    RibArea=[]
    RibLength=[]
    AllNode=NODE()
    ubound = NODE()
    lbound = NODE()
    for m in range(RibNo):
        # print "RIB #", m+1
        K = len(cedge.Edge)
        I = len(sectors)
        
        nodeids=[]
        ContactSurface = ELEMENT()
        for i in range(I-1):
            for k in range(K):
                # print k,',', cedge.Edge[k], 'LEN=', len(cedge.Edge)
                if cedge.Edge[k][8] == m:
                    s1 = sectors[i]*offset
                    s2 = sectors[i+1]*offset
                    ContactSurface.Add( [ cedge.Edge[k][4] + s1, \
                                          cedge.Edge[k][1] + s1 + treadno, \
                                          cedge.Edge[k][0] + s1 + treadno, \
                                          cedge.Edge[k][0] + s2 + treadno, \
                                          cedge.Edge[k][1] + s2 + treadno,  \
                                          "ContactSurface"] )
                    if i ==0:
                        nodeids.append(cedge.Edge[k][0] + s1 + treadno)
                        nodeids.append(cedge.Edge[k][1] + s1 + treadno)
                        nodeids.append(cedge.Edge[k][0] + s2 + treadno)
                        nodeids.append(cedge.Edge[k][1] + s2 + treadno)
                    else:
                        nodeids.append(cedge.Edge[k][0] + s2 + treadno)
                        nodeids.append(cedge.Edge[k][1] + s2 + treadno)
        nodeids= DeleteDuplicate(nodeids, type='int')
        ##############################################################################
        try:
            nodes = tuple(nodeids)
            NodeContact=NODE()
            
            cNode=NODE()
            cNode.Combine(NodePressure)
            cNode.Combine(NodeDeformed)
            
            P = len(cNode.Node)
            listnodes=[]
            for p in range(P):
                listnodes.append(cNode.Node[p][0])
                listnodes.append(cNode.Node[p][1])
                listnodes.append(cNode.Node[p][2])
                listnodes.append(cNode.Node[p][3])
                try:
                    listnodes.append(cNode.Node[p][4])
                except:
                    listnodes.append(0.0)
            tuplenodes = tuple(listnodes)
            iset=5
            # print "start is matched", P, len(nodeids)
            
            res = _islm.IdMatched(nodes, tuplenodes, iset)
            # print "end is mateched"
            
            I = int(len(res)/iset)
            for i in range(I):
                NodeContact.Add( [int(res[i*iset]), float(res[i*iset+1]), float(res[i*iset+2]), float(res[i*iset+3]), float(res[i*iset+4]) ])
        ##############################################################################
        except:
            print (" error during _islm.IdMatched #")
            I = len(nodeids)
            M = len(NodePressure.Node)
            NodeContact=NODE()
            
            i=0
            while i < len(nodeids):
                for k in range(M):
                    if nodeids[i] == NodePressure.Node[k][0]:
                        NodeContact.Add(NodePressure.Node[k])
                        del(nodeids[i])
                        i-=1
                        break
                i+=1
            I = len(nodeids)
            M = len(NodeDeformed.Node)
            for i in range(I):
                for k in range(M):
                    if nodeids[i] == NodeDeformed.Node[k][0]:
                        NodeDeformed.Node[k].append(0.0)
                        if len(NodeDeformed.Node[k]) <4:
                            print (NodeDeformed.Node[k])
                        NodeContact.Add(NodeDeformed.Node[k])
                        break
        # print "Start Inner points "
        # ContactSurface.Save("contactsurface.txt")
        # NodeContact.Save("node Contact.txt")
        if vmin =='':             
            NodePressDist = Innerpoints(dotgap, ContactSurface, NodeContact, XY=XY,  vmin=vmin, vmax=vmax)
        else:
            NodePressDist = Innerpoints(dotgap, ContactSurface, NodeContact, XY=XY,  vmin=pmin, vmax=vmax)
        
        # NodePressDist.Image("inner", XY=XY)
        # print "End of inner points", len(NodePressDist.Node)
        # image =1
        
        imagefile = file+'-Rib'+str(m+1)
        if image !=0:
            NodePressDist.Image(imagefile, XY=XY, size=1.0, cm=1, ci=4, dpi=dpi,  vmin=pmin, vmax=pmax)
        I = len(NodePressDist.Node)
        i=0
        # c = 0
        while i < len(NodePressDist.Node):
            if NodePressDist.Node[i][4]<pmin:
                del(NodePressDist.Node[i])
                i-=1
            i+= 1
            # c+=1
            # if c % 10000 == 0:  print "iteration i=", i, c, pmin, NodePressDist.Node[i]
        NodeBoundary = SearchFootshapeBoundary(NodePressDist, g=bgap, file=imagefile+' Boundary1', XY=XY, image=image)
        x = int(XY/10)
        y = int(XY)%10
        
        
        YX = x*1 + y*10
        LateralBoundary = SearchFootshapeBoundary(NodePressDist, g=bgap*5, file=imagefile+' Boundary2', XY=XY, xy=YX, image=image)
        NodeBoundary.Combine(LateralBoundary)
        if image !=0:
            NodeBoundary.Image(imagefile+' Boundary', XY=XY, size=5)

        lNode = []
        if len(NodeBoundary.Node) > 0:
            SortedRib = BoundaryNodeSort(NodeBoundary, file=imagefile+' Boundarysort', clockwise=0, image=image)
            
            M = len(SortedRib.Node)
            lmx = lmx1 = -10000000000000000.0
            lmn = lmn1 =  10000000000000000.0
            for m in range(M):
                lNode.append(SortedRib.Node[m][0])
                if lmx < SortedRib.Node[m][y]:   ## for upper/lower boundary
                    lmx = SortedRib.Node[m][y]
                if lmn > SortedRib.Node[m][y]:      ## for upper/lower boundary
                    lmn = SortedRib.Node[m][y]
                    
                if lmx1 < SortedRib.Node[m][x]:    ## for rib  left/right boundary
                    lmx1 = SortedRib.Node[m][x]
                if lmn1 > SortedRib.Node[m][x]:     ## for rib  left/right boundary
                    lmn1 = SortedRib.Node[m][x]

            RibLength.append(abs(lmx - lmn))
        
            Ribarea = Area(lNode, SortedRib, XY=XY)
            RibArea.append(Ribarea[0])   ### Area Calculation 
            
            if nodereturn !=0:
                AllNode.Combine(SortedRib)
            ###############################################################
            ### for the points with all ribs boundaries 
            ###############################################################
            for m in range(M):
                if SortedRib.Node[m][y] > lmx - abs((lmx-lmn)*boundlimit) and (SortedRib.Node[m][x] < lmx1 - abs((lmx1-lmn1)*boundlimit) and SortedRib.Node[m][x] > lmn1 + abs((lmx1-lmn1)*boundlimit) ):
                    ubound.Add(SortedRib.Node[m])
                if SortedRib.Node[m][y] < lmn + abs((lmx-lmn)*boundlimit) and (SortedRib.Node[m][x] < lmx1 - abs((lmx1-lmn1)*boundlimit) and SortedRib.Node[m][x] > lmn1 + abs((lmx1-lmn1)*boundlimit) ):
                    lbound.Add(SortedRib.Node[m])
            ################################################################   
            
        else:
            lmx = lmx1 = 0.0
            lmn = lmn1 = 0.0
            RibLength.append(0.0)
            RibArea.append(0.0)
            
    
    od = fitting
    AllboundNode = NODE()
    
    I = len(ubound.Node)
    xi=[]; yi=[]
    mx = -10000000000000.0
    mn = -mx
    for i in range(I):
        xi.append(ubound.Node[i][x])
        yi.append(ubound.Node[i][y])
        if ubound.Node[i][x] > mx:
            mx = ubound.Node[i][x]
        if ubound.Node[i][x] <mn:
            mn = ubound.Node [i][x]
    
    tx = tuple(xi); ty = tuple(yi)
    
    c=-9999999990
    for od in range(od, od+1):
        A = _islm.Curvefitting(tx, ty, od)
        # print "U Curved fitted", A, len(A)
        printnode=NODE()
        px = mn
        
        
        while px < mx:
            yc=0.0
            for i in range(od+1):
                yc += A[i]*math.pow(px, i)
            t = [c+1, 0.0, 0.0, 0.0]
            t[x] = px
            t[y]= yc
            printnode.Add(t)
            c+=1
            px += dotgap*5
            # print '##### ', px,',', yc
        AllboundNode.Combine(printnode)
        printnode.Combine(ubound)
        if image !=0:    
            printnode.Image(file+"-fittingupper-"+str(od), XY=21, size=3)
        
        
    I = len(lbound.Node)
    xi=[]; yi=[]
    mx = -10000000000000.0
    mn = -mx
    for i in range(I):
        xi.append(lbound.Node[i][x])
        yi.append(lbound.Node[i][y])
        if lbound.Node[i][x] > mx:
            mx = lbound.Node[i][x]
        if lbound.Node[i][x] <mn:
            mn = lbound.Node [i][x]
    
    tx = tuple(xi); ty = tuple(yi)
    
    
    for od in range(od, od+1):
        A = _islm.Curvefitting(tx, ty, od)
        # print "L Curved fitted", A, len(A)
        printnode=NODE()
        px = mn
                
        while px < mx:
            yc=0.0
            for i in range(od+1):
                yc += A[i]*math.pow(px, i)
            t = [c+1, 0.0, 0.0, 0.0]
            t[x] = px
            t[y]= yc
            printnode.Add(t)
            c+=1
            px += dotgap*5
            # print '##### ', px,',', yc
        AllboundNode.Combine(printnode)
        printnode.Combine(lbound)
        if image !=0:
            printnode.Image(file+"-fittingower-"+str(od), XY=21, size=3)
    ## side nodes  
    
    
    I = len(AllNode.Node)
    mx = -10000000000000.0; mn = -mx
    for i in range(I):
        if AllNode.Node[i][x] > mx:
            mx = AllNode.Node[i][x]
        if AllNode.Node[i][x] <mn:
            mn = AllNode.Node [i][x]
    for i in range(I):
        if AllNode.Node[i][x] > mx-abs((mx-mn)*boundlimit):
            AllboundNode.Add(AllNode.Node[i])
        if AllNode.Node[i][x] < mn+abs((mx-mn)*boundlimit):
            AllboundNode.Add(AllNode.Node[i])
    if image !=0:
        AllboundNode.Image(file+"-AllBoundNodes", XY=21)
    SortedRib = BoundaryNodeSort(AllboundNode, file=file+"-fitting", clockwise=0, image=image)    
    
    lNode = []
    M = len(SortedRib.Node)
    lmx = -10000000000000000.0
    lmn =  10000000000000000.0
    for m in range(M):
        lNode.append(SortedRib.Node[m][0])
        # print SortedRib.Node[m]
        if lmx < SortedRib.Node[m][y]:
            lmx = SortedRib.Node[m][y]
        if lmn > SortedRib.Node[m][y]:
            lmn = SortedRib.Node[m][y]
    RibLength.append(abs(lmx - lmn))
    Ribarea = Area(lNode, SortedRib, XY=XY)
    # print "Total Area", Ribarea
    RibArea.append(Ribarea[0]) 
    
    # sys.exit()
    ###################################################################    
    
    if nodereturn ==0:
        return RibArea, RibLength
    else:
        return RibArea, RibLength, AllNode
 
def PlotFootprint(imagenamebase, lastSDB, lastSFRIC, mesh2d='', **args):

    file =''
    group = 'PCR'
    iteration = 1
    step = 0
    treadno =  10000000
    offset = 10000
    pmin = ''
    pmax = ''
    vmin = ''
    vmax = ''
    dotgap = 0.5E-3
    XY = 21
    size = 1.0
    ribimage = 0
    bgap = 1.0   ## boudnary dot gap.. 
    dpi = 150
    doe = 0
    fitting = 6
    ribgraph = 0 
    TireOD = 0.0
    Shodrop = 0.0
    getvalue = 0
    for key, value in args.items():
        if key == 'simtime' or key == 'time':
            SimTime = value
        if key == 'Simcondition' or key == 'simcondition' or key == 'condition':
            SimCondition = value 
        if key == 'file':
            file = value
        if key == 'group':
            group = value
        if key == 'mesh2d':
            mesh2d = value
        if key == 'doe':
            doe = int(value)
        if key == 'iter':
            iteration = int(value)
        if key == 'step':
            step = int(value)
        if key == 'treadno':
            treadno = int(value)
        if key == 'offset':
            offset = int(value)
        if key == 'fitting':
            fitting = int(value)
        if key == 'pmin':
            if value =='':
                pass
            else:
                pmin = float(value)
        if key == 'pmax':
            if value =='':
                pass
            else:
                pmax = float(value)
        if key == 'dotgap':   ## gap = 0.5E-3
            dotgap = float(value)
        if key == 'XY':
            XY = int(value)
        if key == 'size':
            size = float(value)
        if key == 'ribimage':
            ribimage = int(value)
        if key == 'bgap' or key == 'boundarygap':
            bgap = float(value)
        if key == 'dpi' or key == 'Dpi': 
            dpi = int(value)
        if key == 'ribgraph':
            ribgraph = int(value)
        if key == 'vmin':
            if value == '':
                vmin = ''
            else:
                vmin = value
            
        if key == 'vmax':
            if value == '':
                vmax = ''
            else:
                vmax = value
        if key == 'od': TireOD = float(value)
        if key == 'shodrop': Shodrop = float(value)
        if key == 'getvalue': getvalue = int(value)
            
    
    x = int(XY/10)
    y = int(XY) % 10   
    
    SDB = lastSDB[:-3]
    SFRIC = lastSFRIC[:-3]
        
        
    ######################################################################################################################
    ## Extract Nodal Area from SFRIC
    #################################################   

    Node, Element, Elset, Comment = Mesh2DInformation(mesh2d)
    TireOuter = Element.OuterEdge(Node)
    # print ("####################################################")
    # print (mesh2d)
    # TireOuter.Print()
    # TireOuter.Image(Node, file="TireOuter")
    # Element.Print()
    CriticalDelAngle = 10.0
    CriticalAngle = 40 
    TDOuter = GrooveDetectionFromEdge(TireOuter, Node, 0)
    # TDOuter.Image(Node, file="TDOuter")
    cedge =EDGE()
    
    
    N = len(TDOuter.Edge)
    Ribs = []
    NodesOnRibs = []
    temp = []
    ntemp = []
    ISRib = 0
    # startcounting = 0 
    for i in range(N):
        if Shodrop > 0.0 and group =='TBR':
            # print (" sho drop > 0 and TBR ")
            N1 = Node.NodeByID(TDOuter.Edge[i][0])
            N2 = Node.NodeByID(TDOuter.Edge[i][1])
            if N1[3] > N2[3] : drop = TireOD/2000.0 - N2[3]
            else: drop = TireOD/2000.0 - N1[3]

            if (TDOuter.Edge[i][6] == 0 or TDOuter.Edge[i][7] == 0) and drop <= Shodrop/1000.0 :
                ISRib = 1
                rn = len(NodesOnRibs)
                TDOuter.Edge[i][8] = rn 
                temp.append(TDOuter.Edge[i])
                cedge.Add(TDOuter.Edge[i])
                ntemp.append(TDOuter.Edge[i][0])
                ntemp.append(TDOuter.Edge[i][1])
                
            else:
                ISRib = 0

        else:
            # print (" Rib no=%d, val 1=%d, val 2=%d, Angle=%.2f"%(len(Ribs), TDOuter.Edge[i][6], TDOuter.Edge[i][7], TDOuter.Edge[i][3]), (TDOuter.Edge[i][6] == 0 or TDOuter.Edge[i][7] == 0),  abs(TDOuter.Edge[i][3]) < CriticalAngle)
            if (TDOuter.Edge[i][6] == 0 or TDOuter.Edge[i][7] == 0)  and abs(TDOuter.Edge[i][3]) < CriticalAngle  :
                # print ("                RIB ", (TDOuter.Edge[i][6] == 0 or TDOuter.Edge[i][7] == 0),  abs(TDOuter.Edge[i][3]) < CriticalAngle )
                ISRib = 1
                rn = len(NodesOnRibs)
                TDOuter.Edge[i][8] = rn 
                temp.append(TDOuter.Edge[i])
                cedge.Add(TDOuter.Edge[i])
                ntemp.append(TDOuter.Edge[i][0])
                ntemp.append(TDOuter.Edge[i][1])
            else:
                # print ("                GROOVE ")
                ISRib = 0
            
        if (ISRib == 0 and len(temp) > 0) or i == N-1:
            Ribs.append(temp)
            NodesOnRibs.append(ntemp)
            # print (" %d ##################################"%(len(Ribs)))
            # print (ntemp)

            temp = []
            ntemp = []
            
    # print ("#######################################")
    # print ("COUNTING RIBS", len(Ribs))
    # print ("         Nodes on ribs", len(NodesOnRibs))
    
        
    M = len(Ribs)
    for i in range(M):
        if len(Ribs[i]) == 0:
            del(Ribs[i])
    M = len(Ribs)
    for i in range(M):
        j = 0
        while j < len(NodesOnRibs[i]): 
            k = j + 1
            while k < len(NodesOnRibs[i]):
                if NodesOnRibs[i][j] == NodesOnRibs[i][k]: 
                    del(NodesOnRibs[i][k])
                    k -= 1
                k += 1
            j += 1
    NodeForce = ResultSFRIC(SFRIC, lastSFRIC, offset, treadno, 1, 0)
    # NodeForce = NodeContactShearForce(SFRIC, lastSFRIC, strSimCode)
        
    N = len(NodeForce.Node)
    ForceSum = 0.0
    MagSum = 0.0
    XSum= 0.0
    YSum = 0.0
    for i in range(N):
        if NodeForce.Node[i][0] > treadno:
            ForceSum += NodeForce.Node[i][6]
            XSum += NodeForce.Node[i][4]
            YSum += NodeForce.Node[i][5]
            MagSum += NodeForce.Node[i][7]
    print ("## Total Node Z-Direction Force = ", ForceSum, ', All Force Sum=', MagSum)
    print ("## X Direction Force Sum=", XSum, ', Y Direction Force Sum=', YSum)
    
    M = len(Ribs)
    K = len(NodeForce.Node)
    RibForces = []
    
    for i in range(M):
        Fsum1 = 0.0 
        N = len(NodesOnRibs[i])
        for j in range(N):
            for k in range(K):
                if NodesOnRibs[i][j] == NodeForce.Node[k][0] % offset and NodeForce.Node[k][0]  > treadno :
                    Fsum1 += NodeForce.Node[k][6]
        
        RibForces.append(Fsum1)
    
    if ribgraph != 0:
        name = "Rib Contact Force"
        rib=[]
        for i in range(M):
            rib.append([i+1, round(RibForces[i], 1)])
        print ("## Contact Force", rib)
        Plot_XYList(imagenamebase+"-Rib Contact Force()", rib, title= "Rib Contact Force[N]", xlabel="Groove Position", marker="o", size=10, xmin=0, xmax=M+1, value=1, dpi=100)
  
    
    # print "***********//********************"
    
    if pmin =='' and pmax =='':
        if group != "TBR":
            MinPressure = 50000
            MaxPressure = 500000
        else:
            MinPressure = 100000
            MaxPressure = 1000000
    else:
        if pmin != '' and pmax =='':
            MinPressure = pmin
            MaxPressure = pmin * 10
        elif pmin == '' and pmax !='':
            MinPressure = pmax / 10.0
            MaxPressure = pmax
        else:
            MinPressure = pmin
            MaxPressure = pmax
    
    NodePressure = RollingContactPressure(lastSFRIC, iter=iteration, vmin=MinPressure, vmax = MaxPressure, treadno=treadno, offset=offset, simcode=imagenamebase)

    ##############################################################
    ## Foot print Image process 
    ##############################################################
    # Deformed = GetDeformedNodeFromSFRIC(strSimCode, SimTime)
    Deformed = ResultSFRIC(SFRIC, lastSFRIC, offset, treadno, 1, 0)
        
    I = len(Deformed.Node)
    NodeDeformed=NODE()
    maxid=0
    # print ("##################", NodePressure.Node[0])
    contactz = NodePressure.Node[0][3] 
    for i in range(I):
        if Deformed.Node[i][0] > maxid:
            maxid = Deformed.Node[i][0]
        if Deformed.Node[i][0] > treadno and Deformed.Node[i][3]  <= contactz + 0.1:
            NodeDeformed.Add([ Deformed.Node[i][0], Deformed.Node[i][1], Deformed.Node[i][2], Deformed.Node[i][3] ])
    msector = int((maxid - treadno) / offset) +1
    
    if iteration == 1:   
        # imin = 10000000000
        # imax = 0
        I = len(NodePressure.Node)
        sectors =[]
        for i in range(I):
            s=int((NodePressure.Node[i][0] - treadno) / offset)
            if i ==0 :
                sectors.append(s)
            else:
                J = len(sectors)
                f=0
                for j in range(J):
                    if s == sectors[j]:
                        f=1
                        break
                if f ==0:
                    sectors.append(s)
        ## save all sector numbers to sectors 
        
        I = len (sectors)
        zerosector = 0
        is1 = 0
        for i in range(I):
            if sectors[i] == 0:
                zerosector = 1
            if sectors[i] == 1:
                is1 = 1
        if zerosector == 1 and is1 == 1:
            c=0
            i=0
            while  sectors[i+1] - sectors[i] < 2 and sectors[i+1] - sectors[i] > 0:
                sectors.append(sectors[i])
                # print (sectors[i], sectors[i+1] - sectors[i])
                del(sectors[i])
                c+= 1
                if c>10000:
                    print("ERROR, FINDING Contacting sectors", sectors)
                    sys.exit()
            sectors.append(sectors[i])
            # del(sectors[i]) 
        elif zerosector == 1 and is1 == 0:
            sectors.append(sectors[0])
            # del(sectors[0])
        
        sectors.append(sectors[I-1])
        I=len(sectors)
        # s0 = sectors [0]
        # sl = sectors [I-1]
        for i in range(I-1):
            
            sectors[i] -= 1
            if sectors[i] ==-1 :
                sectors[i] = msector -1
                
        sectors.append(sectors[I-1]+1)
        if sectors[I] == msector:
            sectors[I] = 0
            
        ContactSurface = ELEMENT()
        K = len(cedge.Edge)
        
        nodeids=[]
        for i in range(I):
            for k in range(K):
                s1 = sectors[i]*offset
                s2 = sectors[i+1]*offset
                ContactSurface.Add( [ cedge.Edge[k][4] + s1, \
                                      cedge.Edge[k][1] + s1 + treadno, \
                                      cedge.Edge[k][0] + s1 + treadno, \
                                      cedge.Edge[k][0] + s2 + treadno, \
                                      cedge.Edge[k][1] + s2 + treadno,  \
                                      "ContactSurface", 4,   cedge.Edge[k][8] ] )
                if i ==0:
                    nodeids.append(cedge.Edge[k][0] + s1 + treadno)
                    nodeids.append(cedge.Edge[k][1] + s1 + treadno)
                    nodeids.append(cedge.Edge[k][0] + s2 + treadno)
                    nodeids.append(cedge.Edge[k][1] + s2 + treadno)
                else:
                    nodeids.append(cedge.Edge[k][0] + s2 + treadno)
                    nodeids.append(cedge.Edge[k][1] + s2 + treadno)
        
        nodeids= DeleteDuplicate(nodeids, type='int')
        # print ("** Making Node Set for contact pressure and calculation")
        print ("   Contact Surface Element =%d EA"%(len(ContactSurface.Element)))
        
        ###############################################################################################
        nodes = tuple(nodeids)
        NodeContact=NODE()
        
        cNode=NODE()
        cNode.Combine(NodePressure)
        cNode.Combine(NodeDeformed)
        P = len(cNode.Node)
        listnodes=[]
        for p in range(P):
            listnodes.append(cNode.Node[p][0])
            listnodes.append(cNode.Node[p][1])
            listnodes.append(cNode.Node[p][2])
            listnodes.append(cNode.Node[p][3])
            try:
                listnodes.append(cNode.Node[p][4])
            except:
                listnodes.append(0.0)
        tuplenodes = tuple(listnodes)
        iset=5
        res = _islm.IdMatched(nodes, tuplenodes, iset)
        I = int(len(res)/iset)
        if SimCondition.Drum == 0:
            for i in range(I):
                NodeContact.Add( [int(res[i*iset]), float(res[i*iset+1]), float(res[i*iset+2]), float(res[i*iset+3]), float(res[i*iset+4]) ])
        else:
            drumcenter=GetDrumCenter(lastsdb=lastSDB)
            dcenter = drumcenter.Node[0]
            
            up = [0, dcenter[1], dcenter[2], dcenter[3]+1.0]
            # print dcenter, up, SimCondition.Drum
            for i in range(I):
                pts = [-1, float(res[i*iset+1]), float(res[i*iset+2]), float(res[i*iset+3])]
                ang = CalculateAngleFrom3Node(up, pts, dcenter, XY=13)
                r= math.sqrt( (float(res[i*iset+1])-dcenter[1])*(float(res[i*iset+1])-dcenter[1]) + (float(res[i*iset+3])-dcenter[3])*(float(res[i*iset+3])-dcenter[3])   )
                # print math.degrees(ang)
                # print  ("%f, %f, (%f)" %(r * ang, float(res[i*set+1]),(r * ang - abs(float(res[i*set+1] )))*1000))
                if float(res[i*iset+1]) > drumcenter.Node[0][1]:
                    NodeContact.Add( [int(res[i*iset]), r * ang, float(res[i*iset+2]), 0.0, float(res[i*iset+4]) ])
                else:
                    NodeContact.Add( [int(res[i*iset]), -r * ang, float(res[i*iset+2]), 0.0, float(res[i*iset+4]) ])
        ###############################################################################################
        try: 
            datfile = open(imagenamebase+"-postfoot.dat", 'w')

            tForce = ResultSFRIC(SFRIC, lastSFRIC, offset, treadno, 1, 0)

            FNode = NODE()
            for nd in tForce.Node: 
                if nd[0] > treadno and nd[6]> 0.0:
                    FNode.Add([nd[0], nd[1], nd[2], nd[3], nd[6]] )
            for k, pnd in enumerate(NodeContact.Node):
                cnt = 0
                for nd in FNode.Node:
                    if int(nd[0]) == int(pnd[0]): 
                        NodeContact.Node[k].append(nd[4])
                        cnt = 1
                        break
                if cnt == 0: 
                    NodeContact.Node[k].append(0.0)

            datfile.write("*NODE\n")
            for nd in NodeContact.Node:
                datline = str(nd[0]) + ", " + str(nd[1]) + ", " + str(nd[2]) + ", " + str(nd[3]) + ", " + str(nd[4]) + ", " + str(nd[5]) + "\n"  
                datfile.write(datline)

            datfile.write("*ELEMENT\n")
            for el in ContactSurface.Element: 
                datline = str(el[0]) +", " + str(el[1]) +", " + str(el[2]) +", " + str(el[3]) +", " + str(el[4]) +"\n"  
                datfile.write(datline)
            datfile.close()
            del(tForce)
            del(FNode)
            print ("#### Pressure/Force data written")
        except:
            pass


        # ContactSurface.Image(cNode, "SurfaceELEMENT", xy=XY)
        # NodeContact.Image("NODEcontact image", xy=XY, size=5, cm=1, ci=4, dpi=dpi,  vmin=MinPressure, vmax=MaxPressure, axis=0)
        if vmin != '':
            NodePressDist = Innerpoints(dotgap, ContactSurface, NodeContact, XY=XY,  vmin=MinPressure, vmax=vmax)
        else:
            NodePressDist = Innerpoints(dotgap, ContactSurface, NodeContact, XY=XY,  vmin=vmin, vmax=vmax)
            
            #####################################################################
            ## for contact area calculation 
            #####################################################################
            MoreExactArea = 1
            if MinPressure > 50000: dotgap2 = dotgap*2
            else: dotgap2 = dotgap
            AllDots=NODE()
            if MoreExactArea > 0:
                t0 = time.time()
                x=int(XY/10); y=int(XY%10)
                vmin = MinPressure
                nd =[]
                for n in NodeContact.Node:
                    nd.append(n[0])
                    nd.append(n[1])
                    nd.append(n[2])
                    nd.append(n[3])
                    nd.append(n[4])
                tuplend = tuple(nd)
                ContactSurfaceAreas =[]
                BoundaryNodes = NODE()
                for E in ContactSurface.Element:
                    el = []
                    xy = NODE()
                    if E[6] == 4 : 
                        el.append(E[0])
                        el.append(E[1])
                        el.append(E[2])
                        el.append(E[3])
                        el.append(E[4])
                        tupleel = tuple(el)

                        xyv =  _islm.EL4Innerpoints(tupleel, tuplend, 5, 5, XY, dotgap2)
                        
                        I  = int(len(xyv)/3)
                        for i in range(I):
                            if xyv[i*3+2] > vmin: 
                                t =[i+1, 0.0, 0.0, 0.0, xyv[i*3+2]]
                                t[x] = xyv[i*3+0]
                                t[y] = xyv[i*3+1]
                                xy.Add(t)
                                AllDots.Add(t)
                                
                        if len(xy.Node) > 3:
                            pdots = ConvexHull(xy, XY=XY)
                            nList = []
                            for nd in pdots.Node:
                                nList.append(nd[0])
                                BoundaryNodes.Add(nd)
                            iArea =  Area(nList, pdots, XY=XY, error=0)
                        
                            ContactSurfaceAreas.append([E[7], iArea[0], E[0]])
                del(xy)
                # t1 = time.time()
                RibAreafromDots =[]
                for i in range(len(Ribs)): 
                    RibAreafromDots.append(0.0)

                for area in ContactSurfaceAreas:
                    RibAreafromDots[area[0]] += round(area[1]*10000.0, 4)

                s = 0.0
                for f in RibForces:
                    s += f
                print ("** Total Normal force =%.1f kgf"%(round(s/9.8, 1)))
                # BoundaryNodes.Image("BoundariesForArea.png", size=0.5, xy=XY, dpi=100) 

                # t1 = time.time()
                # print ("DUR=", t1-t0)
                ## End of contact area calculation ###################################
        
        # print ("making image, %d"%(len(NodePressDist.Node)))
        ribshapefilename = imagenamebase + "-RibShape"
        NodePressDist.Image(ribshapefilename, XY=XY, size=1.0, cm=1, ci=4, dpi=dpi,  vmin=MinPressure, vmax=MaxPressure, axis=0)
        # print ("image done")
    
    ###############################################################
    
    if SimCondition.LateralValue != 0.0: 
    
        centerNode =Node.NodeIDByCoordinate('y', 0)
        max = 0.0
        # N = len(Node.Node)
        N = len(centerNode)
        for i in range(N):
            N1 = Node.NodeByID(centerNode[i])
            if N1[3] > max: 
                max = N1[3]
                cNode = N1
                
        
        N = len(NodeDeformed.Node)
        cX = 1000.0
        for i in range(N):
            if N1[0] == NodeDeformed.Node[i][0] % offset and abs(NodeDeformed.Node[i][y]) <= cX:
                cX = abs(NodeDeformed.Node[i][1])
                CN = NodeDeformed.Node[i]
                
        try:
            print ("## Footprint Rotation Center : %f, %f, %f"%(CN[1], CN[2], CN[3]))
        except:
            I = len(Node.Node)
            max1 = -10000.0
            max2 =-10000.0
            for i in range(I): 
                
                if Node.Node[i][3] > max1 and Node.Node[i][x] > 0.0: 
                    max1 = Node.Node[i][3]
                    N1 = Node.Node[i]
                if Node.Node[i][3] > max2 and Node.Node[i][x] < 0.0: 
                    max2 = Node.Node[i][3]
                    N2 = Node.Node[i]
            
            N = len(NodeDeformed.Node)
            cX1 = 1000.0
            cX2 = 1000.0
            
            for i in range(N):
                if N1[0] == NodeDeformed.Node[i][0] % offset and abs(NodeDeformed.Node[i][y]) <= cX1:
                    # print "N1 - ", NodeDeformed.Node[i]
                    cX1 = abs(NodeDeformed.Node[i][1])
                    CN1 = NodeDeformed.Node[i]
                # if abs(NodeDeformed.Node[i][1]) <= cX2: 
                    # print "cX2=", cX2, NodePressure.Node[i]
                if N2[0] == NodeDeformed.Node[i][0] % offset and abs(NodeDeformed.Node[i][y]) <= cX2:
                    # print "N2 - ", NodeDeformed.Node[i]
                    cX2 = abs(NodeDeformed.Node[i][1])
                    CN2 = NodeDeformed.Node[i]
                    
            CN = [1111111111, (CN1[1]+CN2[1])*0.5, (CN1[2]+CN2[2])*0.5, (CN1[3]+CN2[3])*0.5]
            
            print ("## Footprint Rotation Center : %f, %f, %f"%(CN[1], CN[2], CN[3]))
            
        NodePressure.Rotate(-SimCondition.LateralValue, XY, CN[x], CN[y])
        if iteration == 1: 
            NodePressDist.Rotate(-SimCondition.LateralValue, XY, CN[x], CN[y])
            NodeDeformed.Rotate(-SimCondition.LateralValue, XY, CN[x], CN[y])
            if MoreExactArea > 0: AllDots.Rotate(-SimCondition.LateralValue, XY, CN[x], CN[y])


        
    if iteration == 1: 
        # RibArea, RibLength, NodeBoundary = RibsBoundary(cedge, NodePressure, NodeDeformed, len(Ribs), sectors, imagenamebase, image=ribimage, bgap=bgap, \
        #                 dotgap=dotgap, XY=XY, vmin = vmin, vmax=vmax, pmin=MinPressure, pmax=MaxPressure, dpi=100, nodereturn=1, fitting=fitting, offset=offset)
        # print ("Rib Lenth ", RibLength)
        
        # else: print ("Rib Area ", RibArea)
        
        if MoreExactArea > 0:
            if SimCondition.LateralValue == 0.0:    CN = [1111111111, 0.0, 0.0, 0.0]
            hrange = 5.0E-03
            x=int(XY/10); y=int(XY%10)

            hMax = AllDots.Node[0][y]
            hMin = AllDots.Node[0][y]
            for nd in AllDots.Node:
                if nd[y] > hMax : hMax = nd[y]
                if nd[y] < hMin : hMin = nd[y]

            MaxWidth = 0.0
            Upstep = int(abs(hMax-CN[y])*1000)
            Downstep = int(abs(CN[y] - hMin)*1000)
            cLength = abs(hMax-hMin)
            L15 = hMax - cLength * 0.15
            L25 = hMax - cLength * 0.25
            L50 = hMax - cLength * 0.5
            L75 = hMax - cLength * 0.75
            L85 = hMax - cLength * 0.85
            W15 = 0.0; W25 = 0.0; W75 = 0.0; W85 = 0.0 ; W50 = 0.0
            minboundary = CN[y] -hrange
            for i in range(Upstep-2): 
                wMin =1000.0
                wMax = -1000.0
                for nd in AllDots.Node:
                    if nd[y] < minboundary + hrange/2 and nd[y] > minboundary - hrange/2 : 
                        if nd[x] > wMax: wMax = nd[x]
                        if nd[x] < wMin: wMin = nd[x]
                if MaxWidth < (wMax - wMin): 
                    MaxWidth = (wMax - wMin)
                if L15 >  minboundary - hrange/2 and L15 <= minboundary + hrange/2: 
                    W15 = (wMax - wMin)
                if L50 >  minboundary - hrange/2 and L50 <= minboundary + hrange/2: 
                    W50 = (wMax - wMin)
                if L25 >  minboundary - hrange/2 and L25 <= minboundary + hrange/2: 
                    W25 = (wMax - wMin)
                # print (( minboundary - hrange/2)*1000,  (minboundary + hrange/2)*1000, maxWidth*1000, wMax*1000, wMin*1000)
                minboundary += hrange
            
            minboundary = CN[y]
            for i in range(Downstep-3): 
                
                wMin =1000.0
                wMax = -1000.0
                for nd in AllDots.Node:
                    if nd[y] < minboundary + hrange/2 and nd[y] > minboundary - hrange/2 : 
                        if nd[x] > wMax: wMax = nd[x]
                        if nd[x] < wMin: wMin = nd[x]
                if MaxWidth < (wMax - wMin): 
                    MaxWidth = (wMax - wMin)
                if L50 >  minboundary - hrange/2 and L50 <= minboundary + hrange/2: 
                    W50 = (wMax - wMin)
                if L75 >  minboundary - hrange/2 and L75 <= minboundary + hrange/2: 
                    W75 = (wMax - wMin)
                if L85 >  minboundary - hrange/2 and L85 <= minboundary + hrange/2: 
                    W85 = (wMax - wMin)

                # print (( minboundary - hrange/2)*1000,  (minboundary + hrange/2)*1000, maxWidth*1000, wMax*1000, wMin*1000)

                minboundary -= hrange

            print ("## Contact Width Center  [mm] = %.2f"%(W50*1000))
            print ("## Contact Width Maximum [mm] = %.2f"%(MaxWidth*1000))
            print (" Contact Width 15%, 25%, 75%, 85%")
            print ("  %.1f, %.1f, %.1f, %.1f"%(W15*1000, W25*1000, W75*1000, W85*1000))
            

            
        else:
            pass
        
    else:
        print ("Rib Searching ...")
        RibArea=[] 
        K = len(NodePressure.Node)
        I = len(Ribs)
        
        vnode=NODE()
        
        for i in range(I):
            RibOut=NODE()
            J = len(NodesOnRibs[i])
            pID = 0
            
            AllNodes=NODE()
            for j in range(J): 
                for k in range(K): 
                    if NodesOnRibs[i][j] == NodePressure.Node[k][0] % offset:
                        AllNodes.Add(NodePressure.Node[k])
                        
            M = len(AllNodes.Node)
            
            min = 100000000000.0
            max = -100000000000.0
            for m in range(M): 
                if AllNodes.Node[m][x] < min and  abs(AllNodes.Node[m][y]) < 0.01 :
                    min = AllNodes.Node[m][x]
                    Nmin = AllNodes.Node[m]
                if AllNodes.Node[m][x] > max and  abs(AllNodes.Node[m][y]) < 0.01:
                    max = AllNodes.Node[m][x]
                    Nmin2 = AllNodes.Node[m]
                    
            for j in range(J):
                if pID == NodesOnRibs[i][j]:
                    continue
                    
                if Nmin[0] % offset == NodesOnRibs[i][j] %offset or Nmin2[0] % offset == NodesOnRibs[i][j] % offset:
                    for k in range(K):
                        if NodesOnRibs[i][j] == NodePressure.Node[k][0] % offset:
                            RibOut.Add(NodePressure.Node[k])
                else:
                    # print "J=", j
                    UpNode=[]
                    DownNode=[]
                    Up= -1000000.0
                    Down = 1000000.0
                    for k in range(K):
                        if NodesOnRibs[i][j] == NodePressure.Node[k][0] % offset and NodePressure.Node[k][y] > Up:
                            UpNode = NodePressure.Node[k]
                            Up = NodePressure.Node[k][y]
                        if NodesOnRibs[i][j] == NodePressure.Node[k][0] % offset and NodePressure.Node[k][y] < Down:
                            DownNode = NodePressure.Node[k]
                            Down = NodePressure.Node[k][y]
                            
                    if len(UpNode) > 0:
                        RibOut.Add(UpNode)
                    if len(DownNode) > 0:
                        RibOut.Add(DownNode)
                        
                pID = NodesOnRibs[i][j]
                
                
            if len(RibOut.Node)>0:
                SortedRib = BoundaryNodeSort(RibOut, file=imagenamebase+"-RIB"+str(i)+"sorted", clockwise=0, image=ribimage)
                lNode = []
                M = len(SortedRib.Node)
                for m in range(M):
                    lNode.append(SortedRib.Node[m][0])
                Ribarea = Area(lNode, SortedRib, XY=XY)
                RibArea.append(Ribarea[0])
            else:
                del(Ribs[i])
                # del(RibForces[i])
                i -= 1
                I -= 1

    if getvalue > 0:
        M = len(RibForces)
        RibPressures = []
        for i in range(M): 
            if RibAreafromDots[i] > 0:
                RibPressures.append(RibForces[i]/RibAreafromDots[i] * 10.0)
            else: 
                RibPressures.append(0.0)
        return RibForces, RibAreafromDots, RibPressures, [MaxWidth, W50, W15, W25, W75, W85]
    

def drawarrow(ax, connectionstyle, p1, p2, xy=23):
    X1 = int(xy/10)
    X2 = int(xy%10)
    x1 = p1[X1]; y1 = p1[X2]
    x2 = p2[X1]; y2 = p2[X2]

    ax.plot([x1, x2], [y1, y2], ".")
    ax.annotate("",
                xy=(x1, y1), xycoords='data',
                xytext=(x2, y2), textcoords='data',
                arrowprops=dict(arrowstyle="->", color="0.5",
                                shrinkA=5, shrinkB=5,
                                patchA=None, patchB=None,
                                connectionstyle=connectionstyle,
                                ),
                )

def PlotGrooveDeformation_BetweenGT_Drum(imagename, node_drumprofile, node_gtprifile, profileedge, groovetopnodes, groovebottomnodes, **args):
    dpi = 200;     color = 'black';     linewidth = 0.5;     fontsize = 8
    Label_1 = "Groove Leteral Position on Belt Drum"
    Label_2 = "Groove Leteral Position on GT"
    Label = ""; title = "Tread Extrusion Profile Design Guide"
    IniTR = 0;     dist = 0.005
    xtextshift = 0.005; ytextshift = 0.0
    shift = 0.0   ## values for groove node position shift 
    groovedepth = 12.5/1000; treadwidth = 0
    showidth = 45E-03
    group = "PCR"
    dimcolor = "blue"
    squaregroovecolor = "green" 
    bottomdimcolor = "green"

    for key, value in args.items():
        if key == "dpi":            dpi = value
        if key == 'color':          color = value
        if key == 'lw' or key == 'linewidth':            linewidth = value
        if key == "L1" or key == 'l1':            Label_mold = value
        if key == "fontsize":            fontsize = value
        if key == "height":      ## gap among dimensions on base image 
            dist = value
        if key == "textshiftx":  ## text shift for text on base image 
            xtextshift = value
        if key == "textshifty":  ## text shift for text on base image 
            ytextshift = value
        if key == "shift":              shift = value
        if key == "mold":   ## node coordinates on mold profile            
            node_mold = value
        if key == "groove" : ## groove depth 
            groovedepth = value /1000.0
        if key == "treadwidth":            treadwidth = value /1000.0
        if key == "showidth":            showidth=value/1000.0
        if key == "group":            group = value
        if key == "label":            Label = value
        if key == "title":            title = value
        if key == "dimcolor":            dimcolor = value
        if key == "dimbottomcolor":
            bottomdimcolor = value
            squaregroovecolor = value

    boundminx = 0.0
    boundmaxx = 0.0
    boundmargin = 0.1
    topz = 0.0
    for node in node_drumprofile.Node:
        if node[2]> boundmaxx:
            boundmaxx = node[2]
        if node[2] < boundminx:
            boundminx = node[2]
        if topz < node[3]:
            topz = node[3]

    cf = plt.figure()
    fig = cf.add_subplot(2, 1, 1)

    for i, edge in enumerate(profileedge.Edge):
        N1 = node_drumprofile.NodeByID(edge[0])
        N2 = node_drumprofile.NodeByID(edge[1])
        
        if i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=linewidth, label=Label_1)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=linewidth)

    mtnodes = []
    for nd in groovetopnodes:
        N1 = node_drumprofile.NodeByID(nd)
        mtnodes.append([N1[2], N1[3]])

    sorted(mtnodes, key=lambda x:x[0])

    counting = 0
    first = 0
    for arrow in mtnodes:
        if arrow[0] > 0:
            if first ==0 :
                first =1
            else:
                counting -= 1
        else:
            counting += 1
        tshift = float(counting)*dist
        C0 = [0, 0, 0, mtnodes[0][1] + tshift ]
        N1 = [1, 0, arrow[0], mtnodes[0][1]+tshift]
        connecttionstyle = "arc3,rad="+str(IniTR)
        drawarrow(fig, connecttionstyle, N1, C0)

        tx = arrow[0]; ty = mtnodes[0][1]+tshift
        text = str(abs(round(arrow[0]*1000, 1)))+"mm"

        if arrow[0] < 0.0:
            plt.text(tx-xtextshift, ty+ytextshift, text, size=fontsize, ha='right' )
        else:
            plt.text(tx+xtextshift, ty+ytextshift, text, size=fontsize, ha="left" )

    mbnodes = []
    for nd in groovebottomnodes:
        N1 = node_drumprofile.NodeByID(nd, name="groove bottom node")
        mbnodes.append([N1[2], N1[3]])

    sorted(mbnodes, key=lambda x:x[0])

    counting = 0
    first = 0
    for arrow in mbnodes:
        if arrow[0] > 0:
            if first ==0 :
                first =1
            else:
                counting -= 1
        else:
            counting += 1
        tshift = float(counting)*dist
        C0 = [0, 0, 0, mbnodes[0][1] - tshift ]
        N1 = [1, 0, arrow[0], mbnodes[0][1] - tshift]
        connecttionstyle = "arc3, rad="+str(IniTR)
        
        drawarrow(fig, connecttionstyle, N1, C0)

        tx = arrow[0]; ty = mbnodes[0][1]-tshift
        text = str(abs(round(arrow[0]*1000, 1)))+"mm"
        if arrow[0] < 0.0:
            plt.text(tx-xtextshift, ty+ytextshift, text, size=fontsize, ha="right" )
        else:
            plt.text(tx+xtextshift, ty+ytextshift, text, size=fontsize, ha="left" )



    plt.legend(fontsize=fontsize)
    plt.axis("equal")
    plt.axis("off")
    plt.xlim(boundminx-abs(boundminx*boundmargin), boundmaxx+abs(boundmaxx*boundmargin))
    # print ("min=%f, max=%f"%(boundminx-abs(boundminx*boundmargin), boundmaxx+abs(boundmaxx*boundmargin)))
    
    ################################################################################
    ## GT Profile 
    ################################################################################

    LatDisp = NODE()   ## define NODE for extrusion profile 
    ################################################################################

    fig = cf.add_subplot(2, 1, 2)

    for i, edge in enumerate(profileedge.Edge):
        N1 = node_gtprifile.NodeByID(edge[0], name="extrusion profile - Tread profile node")
        N2 = node_gtprifile.NodeByID(edge[1], name="extrusion profile - Tread profile node")
        
        if i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=linewidth, label=Label_2)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=linewidth)

    dtnodes = []
    for nd in groovetopnodes:
        N1 = node_gtprifile.NodeByID(nd, name = 'extrusion profile - groove top node')
        dtnodes.append([N1[2], N1[3], N1[0]])

    sorted(dtnodes, key=lambda x:x[0])

    

    counting = 0
    first = 0
    for i, arrow in enumerate(dtnodes):
        if arrow[0] > 0:
            if first ==0 :
                first =1
            else:
                counting -= 1
        else:
            counting += 1
        tshift = float(counting)*dist
        C0 = [0, 0, 0, dtnodes[0][1] + tshift ]
        N1 = [1, 0, arrow[0], dtnodes[0][1]+tshift]
        connecttionstyle = "arc3,rad="+str(IniTR)
        drawarrow(fig, connecttionstyle, N1, C0)

        tx = arrow[0]; ty = dtnodes[0][1]+tshift
        # text = str(int(math.ceil(abs(arrow[0])*1000)))+"mm(" + str(round((abs(arrow[0])-abs(mtnodes[i][0]))*1000, 1)) +")"
        text = str(round(abs(arrow[0])*1000, 1))+"mm(" + str(round((abs(arrow[0])-abs(mtnodes[i][0]))*1000, 1)) +")"

        LatDisp.Add([arrow[2], 0, round((abs(arrow[0])-abs(mtnodes[i][0])), 5), 0])


        if arrow[0] < 0.0:
            plt.text(tx-xtextshift, ty+ytextshift, text, size=fontsize, ha='right' )
        else:
            plt.text(tx+xtextshift, ty+ytextshift, text, size=fontsize, ha="left" )

    dbnodes = []
    for nd in groovebottomnodes:
        N1 = node_gtprifile.NodeByID(nd,  name = 'extrusion profile - groove bottom node')
        dbnodes.append([N1[2], N1[3], N1[0]])

    sorted(dbnodes, key=lambda x:x[0])

    counting = 0
    first = 0
    for i, arrow in enumerate(dbnodes):
        if arrow[0] > 0:
            if first ==0 :
                first =1
            else:
                counting -= 1
        else:
            counting += 1
        tshift = float(counting)*dist
        C0 = [0, 0, 0, dbnodes[0][1] - tshift ]
        N1 = [1, 0, arrow[0], dbnodes[0][1] - tshift]
        connecttionstyle = "arc3, rad="+str(IniTR)
        
        drawarrow(fig, connecttionstyle, N1, C0)

        tx = arrow[0]; ty = dbnodes[0][1]-tshift
        # text = str(int(math.ceil(abs(arrow[0])*1000)))+"mm("  + str(round((abs(arrow[0])-abs(mbnodes[i][0]))*1000, 1)) +")"
        text = str(round(abs(arrow[0])*1000, 1))+"mm("  + str(round((abs(arrow[0])-abs(mbnodes[i][0]))*1000, 1)) +")"

        LatDisp.Add([arrow[2], 0, round((abs(arrow[0])-abs(mtnodes[i][0])), 5), 0])

        if arrow[0] < 0.0:
            plt.text(tx-xtextshift, ty+ytextshift, text, size=fontsize, ha="right" )
        else:
            plt.text(tx+xtextshift, ty+ytextshift, text, size=fontsize, ha="left" )

    plt.legend(fontsize=fontsize)
    plt.axis("equal")
    plt.axis("off")
    plt.xlim(boundminx-abs(boundminx*boundmargin), boundmaxx+abs(boundmaxx*boundmargin))

    plt.savefig(imagename+"-base", dpi=100)
    plt.clf()


    ###########################################
    ### "Tread Extrusion Profile Design Guide" Image 
    ###########################################

    fig = plt.figure()

    if group == "PCR": 
        addga=3.0
        btmtxtmulti = 4.0
        btmtxtmulti1 = 2.0
        btmtxtmulti2 = 5.0
        dimbottomht = 0.006
    elif group == "LTR": 
        addga=3.0
        btmtxtmulti = 4.0
        btmtxtmulti1 = 3.0
        btmtxtmulti2 = 6.0
        dimbottomht = 0.008
    elif group == "TBR": 
        addga=10.0
        btmtxtmulti = 5.0
        btmtxtmulti1 = 3.0
        btmtxtmulti2 = 7.0
        dimbottomht = 0.003
    else: addga=2.0

    profiletotalgauge = groovedepth + addga/1000.0
    showidth = profiletotalgauge * math.tan(1.02)
    groovedepth = groovedepth * 0.7

    groovetopnodes=[]
    for ids in dtnodes:
        groovetopnodes.append(ids)
    groovebottomnodes=[]
    for ids in dbnodes:
        groovebottomnodes.append(ids)
    del(dtnodes)
    del(dbnodes)

    moldLat=[]; drumLat=[]; gtLat=[]
    for i in groovetopnodes:
        tnd = node_mold.NodeByID(i[2], name="extrusion profile image (groove top)")
        moldLat.append([i[2], tnd[2], 1])
        tnd = node_drumprofile.NodeByID(i[2], name="extrusion profile image (groove top)")
        drumLat.append([i[2], tnd[2]])
        tnd = node_gtprifile.NodeByID(i[2], name="extrusion profile image (groove top)")
        gtLat.append([i[2], tnd[2]])
    for i in groovebottomnodes:
        tnd = node_mold.NodeByID(i[2], name="extrusion profile image (groove bottom)")
        moldLat.append([i[2], tnd[2], 0])
        tnd = node_drumprofile.NodeByID(i[2], name="extrusion profile image (groove bottom)")
        drumLat.append([i[2], tnd[2]])
        tnd = node_gtprifile.NodeByID(i[2], name="extrusion profile image (groove bottom)")
        gtLat.append([i[2], tnd[2]])

    ProfileNode=NODE()
    for i, ids in enumerate(moldLat):
        if ids[2] == 1:   # top node 
            # print (ids[1], ",", drumLat[i][1], ",", gtLat[i][1], "-->", ids[1] + abs(drumLat[i][1])-abs(gtLat[i][1]) + shift, "shift=", shift)
            if ids[1] > 0.0:   ProfileNode.Add([ids[0], 0.0, ids[1] + abs(drumLat[i][1])-abs(gtLat[i][1]) + shift, 0.0, abs(drumLat[i][1])-abs(gtLat[i][1])])
            else:              ProfileNode.Add([ids[0], 0.0, ids[1] - (abs(drumLat[i][1])-abs(gtLat[i][1])) - shift, 0.0, abs(drumLat[i][1])-abs(gtLat[i][1])])
        else:             # bottom node 
            if ids[1] > 0.0:   ProfileNode.Add([ids[0], 0.0, ids[1] + abs(drumLat[i][1])-abs(gtLat[i][1]) + shift, -groovedepth, abs(drumLat[i][1])-abs(gtLat[i][1])] )
            else:              ProfileNode.Add([ids[0], 0.0, ids[1] - (abs(drumLat[i][1])-abs(gtLat[i][1])) - shift, -groovedepth, abs(drumLat[i][1])-abs(gtLat[i][1])])
        
    topfirst = groovetopnodes[0][2]
    topend = groovetopnodes[len(groovetopnodes)-1][2]     

    N1 = node_mold.NodeByID(topfirst, name="extrusion profile image (first top node from node_mold)")
    tdextend = abs(treadwidth/2.0 - abs(N1[2]))
    N1 = ProfileNode.NodeByID(topfirst)
    ProfileNode.Add([-1, 0.0, N1[2] - tdextend, 0.0, 0.0])
    ProfileNode.Add([-2, 0.0, N1[2] - showidth -tdextend, -profiletotalgauge, 0.0])

    N1 = node_mold.NodeByID(topend, name="extrusion profile image (last top node from node_mold)")
    tdextend = abs(treadwidth/2.0 - abs(N1[2]))
    N1 = ProfileNode.NodeByID(topend)
    ProfileNode.Add([-3, 0.0, N1[2] + tdextend, 0.0, 0.0])
    ProfileNode.Add([-4, 0.0, N1[2] + showidth +tdextend, -profiletotalgauge, 0.0])

    extrusion=EDGE()
    grooves = int(len(groovetopnodes)/2.0)
    # print ("### Groove No = %d, Found Groove Top nodes=%d, Bottom Nodes=%d"%(grooves, len(groovetopnodes), len(groovebottomnodes)))
    if len(groovetopnodes) != len(groovebottomnodes): print (" #####  ERROR!!  to find nodes at groove bottoms and tops")
    for i in range(grooves):
        if i == 0:
            tempedge = [-2, -1, "extrusion", 0, 1, 1]
            extrusion.Add(tempedge)
            tempedge = [-1, groovetopnodes[i*2][2], "extrusion", 0, 1, 1]
            extrusion.Add(tempedge)
        #############################################################################
        
        tempedge = [groovetopnodes[i*2][2], groovebottomnodes[i*2][2], "extrusion", 0, 1, 1]
        extrusion.Add(tempedge)
        tempedge = [groovebottomnodes[i*2][2], groovebottomnodes[i*2+1][2], "extrusion", 0, 1, 1]
        extrusion.Add(tempedge)
        tempedge = [groovebottomnodes[i*2+1][2], groovetopnodes[i*2+1][2], "extrusion", 0, 1, 1]
        extrusion.Add(tempedge)
        #############################################################################
        if i == grooves -1:
            tempedge = [groovetopnodes[i*2+1][2], -3, "extrusion", 0, 1, 1]
            extrusion.Add(tempedge)
            tempedge = [-3, -4, "extrusion", 0, 1, 1]
            extrusion.Add(tempedge)
            tempedge = [-2, -4, "extrusion", 0, 1, 1]
            extrusion.Add(tempedge)
        else:
            tempedge = [groovetopnodes[i*2+1][2], groovetopnodes[i*2+2][2], "extrusion", 0, 1, 1]
            extrusion.Add(tempedge)

    fig = plt.figure(figsize=(10, 4))
    plt.title(title)
    plt.ylabel("")
    plt.xlabel("")
    plt.axis("off")
    plt.axis("equal")

    dimht = 8.0/1000.0
    dimsecondht  = 8.0/1000.0
    
    dimpos = 1.0/1000.0   # dimpos = dimht - 1.0/1000.0  = dimht - dimpos 

    dimbottom = 2.0/1000.0
    
    arrowlength = 1.5/1000.0
    arrowangle = 30.0 * math.pi / 180.0
    dimlinewidth = linewidth/2.0
    dimtxtshift = 2.0/1000.0;   dimtxtshiftx = -1.0/1000.0; dimtxtbottomshift = 0.006
    squarebottomdim = 0.005; squarebottomtxtshift = 0.002


    grooveposition=[]

    for i, edge in enumerate(extrusion.Edge):
        N1 = ProfileNode.NodeByID(edge[0])
        N2 = ProfileNode.NodeByID(edge[1])

        if N1[3] == -groovedepth or N2[3] == -groovedepth:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], squaregroovecolor, linewidth=linewidth/2.0, label=Label)
            if N1[3] >=0.0 and N2[3] < 0.0 : 
                pg_tx = N1[2];                     pg_bx = N2[2]
                pg_ty = N1[3];                     pg_by = N2[3]
                plt.plot([N1[2], N1[2]], [dimbottom, dimbottom+dimht], dimcolor, linewidth=dimlinewidth)

                ################################################################################################
                ## bottom dimension
                ################################################################################################
                if N2[2] > 0.0:
                    plt.plot([N2[2], N2[2]], [N2[3] - dimbottom, N2[3] - dimbottom - dimbottomht], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N2[2], N2[2] - squarebottomdim], [N2[3] - dimbottom - dimbottomht, N2[3] - dimbottom - dimbottomht], bottomdimcolor, linewidth=dimlinewidth)
                    
                    plt.plot([N2[2] - squarebottomdim, N2[2] - squarebottomdim + arrowlength*math.cos(arrowangle)], [N2[3] - dimbottom - dimbottomht , N2[3] - dimbottom - dimbottomht +arrowlength*math.sin(arrowangle)], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N2[2] - squarebottomdim, N2[2] - squarebottomdim + arrowlength*math.cos(arrowangle)], [N2[3] - dimbottom - dimbottomht , N2[3] - dimbottom - dimbottomht -arrowlength*math.sin(arrowangle)], bottomdimcolor, linewidth=dimlinewidth)

                    text = str(round((N2[4])*1000, 1))
                    plt.text( N2[2] + dimtxtshiftx - squarebottomtxtshift*btmtxtmulti2, N2[3] - dimbottom - dimbottomht, text, size=fontsize, ha="left" , color = bottomdimcolor )
                    lasttextposition = [  N2[2] + dimtxtshiftx - squarebottomtxtshift*btmtxtmulti2, N2[3] - dimbottom - dimbottomht]
                else:
                    plt.plot([N2[2], N2[2]], [N2[3] - dimbottom, N2[3] - dimbottom - dimbottomht*2], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N2[2], N2[2] + squarebottomdim], [N2[3] - dimbottom - dimbottomht*2, N2[3] - dimbottom -  dimbottomht*2], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N2[2] + squarebottomdim, N2[2] + squarebottomdim - arrowlength*math.cos(arrowangle)], [N2[3] - dimbottom -  dimbottomht*2 , N2[3] - dimbottom -  dimbottomht*2 +arrowlength*math.sin(arrowangle)], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N2[2] + squarebottomdim, N2[2] + squarebottomdim - arrowlength*math.cos(arrowangle)], [N2[3] - dimbottom -  dimbottomht*2 , N2[3] - dimbottom -  dimbottomht*2 -arrowlength*math.sin(arrowangle)], bottomdimcolor, linewidth=dimlinewidth)
                    text = str(round((N2[4])*1000, 1))
                    plt.text( N2[2] + dimtxtshiftx - squarebottomtxtshift*btmtxtmulti, N2[3] - dimbottom - dimbottomht*2 , text, size=fontsize, ha="left" , color = bottomdimcolor )
                    lasttextposition = [  N2[2] + dimtxtshiftx - squarebottomtxtshift*btmtxtmulti, N2[3] - dimbottom - dimbottomht*2 ]

                ################################################################################################

            elif N1[3] < 0.0 and N2[3] >= 0.0 : 
                plt.plot([pg_tx, (pg_bx+N1[2])/2.0], [pg_ty, pg_by], color, linewidth=linewidth, label=Label)
                plt.plot([(pg_bx+N1[2])/2.0, N2[2]], [pg_by, N2[3]], color, linewidth=linewidth, label=Label)

                plt.plot([pg_tx, (pg_bx+N1[2])/2.0], [dimht - dimpos, dimht - dimpos], dimcolor, linewidth=dimlinewidth)
                plt.plot([(pg_bx+N1[2])/2.0, N2[2]], [dimht - dimpos, dimht - dimpos], dimcolor, linewidth=dimlinewidth)

                plt.plot([(pg_bx+N1[2])/2.0, (pg_bx+N1[2])/2.0], [dimbottom-groovedepth, dimbottom+dimht], dimcolor, linewidth=dimlinewidth)
                plt.plot([N2[2], N2[2]], [dimbottom, dimbottom+dimht], dimcolor, linewidth=dimlinewidth)

                plt.plot([pg_tx, pg_tx+arrowlength*math.cos(arrowangle)], [dimht - dimpos, dimht - dimpos+arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([pg_tx, pg_tx+arrowlength*math.cos(arrowangle)], [dimht - dimpos, dimht - dimpos-arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([(pg_bx+N1[2])/2.0, (pg_bx+N1[2])/2.0-arrowlength*math.cos(arrowangle)], [dimht - dimpos , dimht - dimpos +arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([(pg_bx+N1[2])/2.0, (pg_bx+N1[2])/2.0-arrowlength*math.cos(arrowangle)], [dimht - dimpos , dimht - dimpos -arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)

                text = str(int(round(abs(pg_tx - (pg_bx+N1[2])/2.0)*1000, 0)))
                plt.text((pg_tx + (pg_bx+N1[2])/2.0)/2.0 +dimtxtshiftx, dimht - dimpos +dimtxtshift, text, size=fontsize, ha="left" , color=dimcolor )
                # print ("Dim=", abs(pg_tx - (pg_bx+N1[2])/2.0)*1000)

                plt.plot([(pg_bx+N1[2])/2.0, (pg_bx+N1[2])/2.0+arrowlength*math.cos(arrowangle)], [dimht - dimpos , dimht - dimpos +arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([(pg_bx+N1[2])/2.0, (pg_bx+N1[2])/2.0+arrowlength*math.cos(arrowangle)], [dimht - dimpos , dimht - dimpos -arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([N2[2], N2[2]-arrowlength*math.cos(arrowangle)], [dimht - dimpos , dimht - dimpos +arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([N2[2], N2[2]-arrowlength*math.cos(arrowangle)], [dimht - dimpos , dimht - dimpos -arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)

                text = str(int(round(abs((pg_bx+N1[2])/2.0 - N2[2])*1000, 0)))
                plt.text(((pg_bx+N1[2])/2.0 + N2[2])/2.0 +dimtxtshiftx, dimht - dimpos +dimtxtshift, text, size=fontsize, ha="left", color=dimcolor )
                # print ("Dim=", abs((pg_bx+N1[2])/2.0 - N2[2])*1000)

                ## save groove position for second dim 
                grooveposition.append((pg_bx+N1[2])/2.0)

                ################################################################################################
                ## bottom dimension
                ################################################################################################
                
                if N1[2] > 0 : ## distance smaller
                    plt.plot([N1[2], N1[2]], [N1[3] - dimbottom, N1[3] - dimbottom - dimbottomht*2], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N1[2], N1[2] - squarebottomdim], [N1[3] - dimbottom - dimbottomht*2, N1[3] - dimbottom - dimbottomht*2], bottomdimcolor, linewidth=dimlinewidth)
                    
                    plt.plot([N1[2] - squarebottomdim, N1[2] - squarebottomdim + arrowlength*math.cos(arrowangle)], [N1[3] - dimbottom - dimbottomht*2 , N1[3] - dimbottom - dimbottomht*2 +arrowlength*math.sin(arrowangle)], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N1[2] - squarebottomdim, N1[2] - squarebottomdim + arrowlength*math.cos(arrowangle)], [N1[3] - dimbottom - dimbottomht*2 , N1[3] - dimbottom - dimbottomht*2 -arrowlength*math.sin(arrowangle)], bottomdimcolor, linewidth=dimlinewidth)

                    text = str(round((N1[4])*1000, 1))
                    plt.text( N1[2] + dimtxtshiftx+squarebottomtxtshift*btmtxtmulti1, N1[3] - dimbottom - dimbottomht*2, text, size=fontsize, ha="left" , color = bottomdimcolor )
                    lasttextposition = [ N1[2] + dimtxtshiftx+squarebottomtxtshift*btmtxtmulti1, N1[3] - dimbottom - dimbottomht*2]
                else:
                    plt.plot([N1[2], N1[2]], [N1[3] - dimbottom, N1[3] - dimbottom - dimbottomht], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N1[2], N1[2] + squarebottomdim], [N1[3] - dimbottom - dimbottomht, N1[3] - dimbottom - dimbottomht], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N1[2] + squarebottomdim, N1[2] + squarebottomdim - arrowlength*math.cos(arrowangle)], [N1[3] - dimbottom - dimbottomht , N1[3] - dimbottom - dimbottomht +arrowlength*math.sin(arrowangle)], bottomdimcolor, linewidth=dimlinewidth)
                    plt.plot([N1[2] + squarebottomdim, N1[2] + squarebottomdim - arrowlength*math.cos(arrowangle)], [N1[3] - dimbottom - dimbottomht , N1[3] - dimbottom - dimbottomht -arrowlength*math.sin(arrowangle)], bottomdimcolor, linewidth=dimlinewidth)
                    text = str(round((N1[4])*1000, 1))
                    plt.text( N1[2] + dimtxtshiftx+squarebottomtxtshift*btmtxtmulti, N1[3] - dimbottom - dimbottomht , text, size=fontsize, ha="left" , color = bottomdimcolor )
                    lasttextposition = [ N1[2] + dimtxtshiftx+squarebottomtxtshift*btmtxtmulti, N1[3] - dimbottom - dimbottomht]
               



        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=linewidth)

            if edge[0] > 0 and edge[1] > 0:
                plt.plot([N1[2], N2[2]], [dimht-dimpos, dimht-dimpos ], dimcolor, linewidth=dimlinewidth, label=Label)
                text = str(int(round(abs( N2[2] - N1[2])*1000, 0)))
                plt.text((N1[2] + N2[2])/2.0 +dimtxtshiftx, dimht - dimpos +dimtxtshift, text, size=fontsize, ha="left" , color=dimcolor )
                plt.plot([N1[2], N1[2]+arrowlength*math.cos(arrowangle)], [dimht-dimpos, dimht-dimpos+arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([N1[2], N1[2]+arrowlength*math.cos(arrowangle)], [dimht-dimpos, dimht-dimpos-arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([N2[2], N2[2]-arrowlength*math.cos(arrowangle)], [dimht-dimpos , dimht-dimpos +arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
                plt.plot([N2[2], N2[2]-arrowlength*math.cos(arrowangle)], [dimht-dimpos , dimht-dimpos -arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)

    grvminus = 0
    dimlimit = 0.01
    for cnt in grooveposition:
        if abs(cnt) >= dimlimit and cnt < 0.0:
            grvminus += 1
    
    grvplus=1     
    for cnt in grooveposition:
        if cnt < 0 and abs(cnt) >=dimlimit:
            secdimht = 2*dimbottom + dimht + grvminus * dimsecondht
            secdimbtm = 2*dimbottom + dimht 
            plt.plot ([cnt, cnt], [secdimbtm, secdimht], dimcolor, linewidth=dimlinewidth)
            plt.plot ([0.0, 0.0], [secdimbtm, secdimht], dimcolor, linewidth=dimlinewidth)
            plt.plot ([cnt, 0.0], [secdimht-dimpos, secdimht-dimpos], dimcolor, linewidth=dimlinewidth)

            plt.plot([cnt, cnt+arrowlength*math.cos(arrowangle)], [secdimht-dimpos , secdimht-dimpos +arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
            plt.plot([cnt, cnt+arrowlength*math.cos(arrowangle)], [secdimht-dimpos , secdimht-dimpos -arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
            plt.plot([0.0, 0.0-arrowlength*math.cos(arrowangle)], [secdimht-dimpos , secdimht-dimpos +arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
            plt.plot([0.0, 0.0-arrowlength*math.cos(arrowangle)], [secdimht-dimpos , secdimht-dimpos -arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)

            text = str(int(round(abs(cnt)*1000, 0)))
            plt.text(cnt/2.0 +dimtxtshiftx, secdimht-dimpos +dimtxtshift, text, size=fontsize, ha="left", color=dimcolor )
            grvminus -= 1
        if cnt > 0 and abs(cnt) >=dimlimit:
            secdimht = 2*dimbottom + dimht + grvplus * dimsecondht
            secdimbtm = 2*dimbottom + dimht 
            plt.plot ([0.0, 0.0], [secdimbtm, secdimht], dimcolor, linewidth=dimlinewidth)
            plt.plot ([cnt, cnt], [secdimbtm, secdimht], dimcolor, linewidth=dimlinewidth)
            plt.plot ([0.0, cnt], [secdimht-dimpos, secdimht-dimpos], dimcolor, linewidth=dimlinewidth)

            plt.plot([0.0, arrowlength*math.cos(arrowangle)], [secdimht-dimpos , secdimht-dimpos +arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
            plt.plot([0.0, arrowlength*math.cos(arrowangle)], [secdimht-dimpos , secdimht-dimpos -arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
            plt.plot([cnt, cnt-arrowlength*math.cos(arrowangle)], [secdimht-dimpos , secdimht-dimpos +arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)
            plt.plot([cnt, cnt-arrowlength*math.cos(arrowangle)], [secdimht-dimpos , secdimht-dimpos -arrowlength*math.sin(arrowangle)], dimcolor, linewidth=dimlinewidth)

            text = str(int(round(abs(cnt)*1000, 0)))
            plt.text(cnt/2.0 +dimtxtshiftx, secdimht-dimpos +dimtxtshift, text, size=fontsize, ha="left", color=dimcolor )

            grvplus += 1

    text = " * Lateral Displacement during shaping simulation (" + bottomdimcolor + " letter)"
    plt.text( 0.0, N2[3] - dimbottom - dimbottomht*2 - 0.005, text, size=fontsize, ha="left" )
    # lasttextposition = [  N2[2] + dimtxtshiftx - squarebottomtxtshift*btmtxtmulti, N2[3] - dimbottom - dimbottomht*2 ]

    plt.savefig(imagename, dpi=200)


##//////////////////////////////////////

########################################
## Pre Processing 
########################################
def Mesh2DInformation(InpFileName):
    with open(InpFileName) as INP:
        lines = INP.readlines()

    Node = NODE()
    Element = ELEMENT()
    Elset = ELSET()

    Comments = []
    iComment = 0

    for line in lines:
        if (iComment == 0):
            if '**' in line:
                Comments.append(line)
        word = list(line.split(','))
        if word[0] == '\n' or (word[0][0] == '*' and word[0][1] == '*'):
            pass
        elif word[0][1] != '*':
            iComment += 1
            if word[0][0] == '*':
                command = list(word[0].split('*'))
                if command[1][:7] == 'Heading':
                    spt = 'HD'
                elif command[1] == 'NODE':
                    spt = 'ND'
                elif command[1] == 'ELEMENT':
                    EL = list(word[1].split('='))
                    EL = EL[1].strip()
                    if EL == 'MGAX1':
                        spt = 'M1'
                    elif EL == 'CGAX3H':
                        spt = 'C3'
                    elif EL == 'CGAX4H':
                        spt = 'C4'
                    else:
                        spt = 'NN'
                elif command[1] == 'SURFACE':
                    spt = 'SF'
                    name = word[2].split('=')[1].strip()
                elif command[1] == 'TIE':
                    spt = 'TI'
                    name = word[1].split('=')[1].strip()
                elif command[1] == 'ELSET':
                    spt = 'ES'
                    name = word[1].split('=')[1].strip()
                    if name != "BETWEEN_BELTS" and name != "BD1" and name != "BetweenBelts":
                        Elset.AddName(name)

                elif command[1] == 'NSET':
                    spt = 'NS'
                    name = word[1].split('=')[1].strip()

                else:
                    spt = ''
            else:
                if spt == 'HD':
                    pass
                if spt == 'ND':
                    Node.Add([int(word[0]), float(word[3]), float(word[2]), float(word[1])])
                if spt == 'M1':
                    # Element   [EL No,                  N1,          N2,  N3, N4,'elset Name', N,  Area/length, CenterX, CenterY]
                    N1 = Node.NodeByID(int(word[1]))
                    N2 = Node.NodeByID(int(word[2]))
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), '', '', '', 2, math.sqrt(math.pow(N1[2] - N2[2], 2) + math.pow(N1[3] - N2[3], 2)), (N1[2] + N2[2]) / 2.0, (N1[3] + N2[3]) / 2.0])
                if spt == 'C3':
                    A = Area([int(word[3]), int(word[2]), int(word[1])], Node)
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), int(word[3]), '', '', 3, A[0], A[1], A[2]])
                if spt == 'C4':
                    A = Area([int(word[4]), int(word[3]), int(word[2]), int(word[1])], Node)
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), int(word[3]), int(word[4]), '', 4, A[0], A[1], A[2]])
                if spt == 'NS':
                    pass
                if spt == 'ES':
                    if name != "BETWEEN_BELTS" and name != "BD1" and name != "BetweenBelts":
                        try: 
                            for i in range(len(word)):
                                Elset.AddNumber(int(word[i]), name)
                        except: 
                            pass
                if spt == 'SF':
                    pass

                else:
                    pass

    for i in range(len(Elset.Elset)):
        fd = 0 
        for name in TireRubberComponents: 
            if name == Elset.Elset[i][0]: 
                fd = 1
                break 
        if fd ==0: 
            for name in TireCordComponents: 
                if name == Elset.Elset[i][0]: 
                    fd = 1
                    break 
        if fd ==1 : 

            for j in range(1, len(Elset.Elset[i])):
                for k in range(len(Element.Element)):
                    if Elset.Elset[i][j] == Element.Element[k][0]:
                        Element.Element[k][5] = Elset.Elset[i][0]
                        break

    return Node, Element, Elset, Comments

def ElementShape(k, Elements):
    # k = element No.
    N = len(Elements.Element)
    for i in range(N):
        if k == Elements.Element[i][0]:
            return Elements.Element[i][6]

    print (k, 'Element was not found')
    return 0

def FindAdjcentElements(k, Elements):
    EL = 0
    for e in Elements.Element:
        if e[0] == k: 
            EL = e
            break
    if EL ==0: 
        print ("Element %d is not in the Element List"%(k))
        return EL
    else: 
        SE=ELEMENT()
        if EL[6] ==2: 
            f1 = [EL[1], EL[2]]

            for e in Elements.Element:
                if e[0] == k: continue
                c = 0
                for i in range(1, e[6]+1):
                    if e[i] == f1[0] or e[i] == f1[1]: c += 1

                if c == 2: SE.Add(e)
            return SE

        if EL[6] ==3:
            f1 = [EL[1], EL[2]]
            f2 = [EL[2], EL[3]]
            f3 = [EL[3], EL[1]]

            for e in Elements.Element:
                if e[0] == k: continue
                c1 = 0; c2=0; c3=0
                for i in range(1, e[6]+1):
                    if e[i] == f1[0] or e[i] == f1[1]: c1 += 1
                    if e[i] == f2[0] or e[i] == f2[1]: c2 += 1
                    if e[i] == f3[0] or e[i] == f3[1]: c3 += 1

                if c1 == 2 or c2 == 2 or c3 == 2: SE.Add(e)
            return SE
        if EL[6] == 4: 
            f1 =[EL[1], EL[2]]
            f2 = [EL[2], EL[3]]
            f3= [EL[3], EL[4]]
            f4 = [EL[4], EL[1]]

            for e in Elements.Element:
                if e[0] == k: continue
                c1 = 0; c2=0; c3=0; c4=0
                for i in range(1, e[6]+1):
                    if e[i] == f1[0] or e[i] == f1[1]: c1 += 1
                    if e[i] == f2[0] or e[i] == f2[1]: c2 += 1
                    if e[i] == f3[0] or e[i] == f3[1]: c3 += 1
                    if e[i] == f4[0] or e[i] == f4[1]: c4 += 1
                if c1 == 2 or c2 == 2 or c3 == 2 or c4 == 2: SE.Add(e)
            return SE
    

def ShareEdge(m, n, Elements):
    p = ElementShape(m, Elements)
    q = ElementShape(n, Elements)

    N = len(Elements.Element)
    for i in range(N):
        if m == Elements.Element[i][0]:
            k = i
        if n == Elements.Element[i][0]:
            l = i

    count = 0
    for i in range(1, p+1):
        for j in range(1, q+1):
            if Elements.Element[k][i] == Elements.Element[l][j]:
                count += 1

    if count >= 2:
        return 1  # Edge shared
    else:
        return 0

def SharedNode(M1, M2): 
    """
    Input : Edge or Element 
    """
    
    try: 
        if type(M1.Element[0][0]) == int:
            M1EL = 1
    except: 
        M1EL = 0
    try: 
        if type(M2.Element[0][0]) == int:
            M2EL = 1
    except: 
        M2EL = 0
        
        
    if M1EL == 1:
        M1Node = M1[0][6]
        M1Num = len(M1.Element)
    else:
        M1Node = 2   # if M1 is Edge
        M1Num = len(M1.Edge)
    if M2EL == 1:
        M2Node = M2[0][6]
        M2Num = len(M2.Element)
    else:
        M2Node = 2  # if M2 is Edge 
        M2Num = len(M2.Edge)
        
    SharedNode=[]
    
    for i in range(M1Num): 
        if M1EL == 1: 
            for j in range(1, M1Node+1): 
                for m in range(M2Num): 
                    if M2EL == 1: 
                        for n in range(1, M2Node+1):
                            if M1.Element[i][j] == M2.Element[m][n]: 
                                SharedNode.append(M2.Element[m][n])
                                break
                    else:
                        for n in range(M2Node):
                            if M1.Element[i][j] == M2.Edge[m][n]: 
                                SharedNode.append(M2.Edge[m][n])
                                break
        else:
            for j in range(M1Node): 
                for m in range(M2Num): 
                    if M2EL == 1: 
                        for n in range(1, M2Node+1):
                            if M1.Edge[i][j] == M2.Element[m][n]: 
                                SharedNode.append(M2.Element[m][n])
                                break
                    else:
                        for n in range(M2Node):
                            if M1.Edge[i][j] == M2.Edge[m][n]: 
                                SharedNode.append(M2.Edge[m][n])
                                break
                                
    return SharedNode

def NextEdge(edge, k):
    tmp = k
    connected = []
    N = len(edge.Edge)
    for i in range(N):
        if tmp != i:
            if edge.Edge[tmp][1] == edge.Edge[i][0]:
                connected.append(i)
    return connected

def PreviousEdge(edge, k):
    tmp = k
    connected = []
    N = len(edge.Edge)
    for i in range(N):
        if tmp != i:
            if edge.Edge[tmp][0] == edge.Edge[i][1]:
                connected.append(i)
    return connected

def FreeEdge(edge):
    FEdge = EDGE()
    try:
        tupleL = ()
        for i in range(len(edge.Edge)):
            list = []
            list.append(edge.Edge[i][0])
            list.append(edge.Edge[i][1])
            list.append(0)
            if edge.Edge[i][3] == 'S1':
                list.append(1)
            elif edge.Edge[i][3] == 'S2':
                list.append(2)
            elif edge.Edge[i][3] == 'S3':
                list.append(3)
            elif edge.Edge[i][3] == 'S4':
                list.append(4)
            list.append(edge.Edge[i][4])
            if edge.Edge[i][5] == '':
                edge.Edge[i][5] = -2
            list.append(edge.Edge[i][5])
            tupleL = tupleL + tuple(list)

        flist = _islm.FindFreeEdgePylist(tupleL, 6)

        for i in range(len(edge.Edge)):
            edge.Edge[i][5] = flist[i]
            if flist[i] == 0:
                FEdge.Add(edge.Edge[i])
    except:
        print ("* Finding Free Edges by Python Script")

        for i in range(len(edge.Edge)):
            if edge.Edge[i][5] == -1:
                j = i + 1
                count = 0
                while j < len(edge.Edge):
                    if edge.Edge[j][5] == -1:
                        if edge.Edge[i][0] == edge.Edge[j][0] and edge.Edge[i][1] == edge.Edge[j][1]:
                            count += 1
                            edge.Edge[i][5] = -2
                            edge.Edge[j][5] = -2
                            break
                        elif edge.Edge[i][0] == edge.Edge[j][1] and edge.Edge[i][1] == edge.Edge[j][0]:
                            count += 1
                            edge.Edge[i][5] = -2
                            edge.Edge[j][5] = -2
                            break
                    j += 1
                if count == 0:
                    edge.Edge[i][5] = 0
                    FEdge.Add(edge.Edge[i])

    return FEdge

def OuterEdge(FreeEdge, Node, Element):

    #############################################
    # starting from center bottom     

    # N = len(FreeEdge.Edge)
    
    # MinY = 9.9E20
    
    # cNodes = [0]
    # for i in range(N):
    #     N1 = Node.NodeByID(FreeEdge.Edge[i][0])
    #     N2 = Node.NodeByID(FreeEdge.Edge[i][1])
    #     if N1[3] < MinY:
    #         MinY = N1[3]
    #         cNodes[0] = N1[0]
    #     if N2[3] < MinY:
    #         MinY = N2[3]
    #         cNodes[0] = N2[0]
    # if cNodes[0] == 0:
    #     cNodes[0] = Node.NodeIDByCoordinate('z', 0, closest=1)

    # MAX = 10000   ## max iteration for searching  error
    # ShareNodePos = []
    # #    connectedEdge = []
    # outEdge = EDGE()

    # ## Find a 1st surround edge (IL at the center)
    # low = 9.9E20
    # i = 0
    # savei = 0
    # while i < len(cNodes):
    #     j = 0
    #     while j < len(Node.Node):
    #         if cNodes[i] == Node.Node[j][0]:
    #             if Node.Node[j][3] < low:
    #                 low = Node.Node[j][3]
    #                 savei = j
    #         j += 1
    #     i += 1

    # i = 0
    # while i < len(FreeEdge.Edge):
    #     if Node.Node[savei][0] == FreeEdge.Edge[i][0]:
    #         break
    #     i += 1
    # ##################################################################

    ## starting from right bottom 
    npn = np.array(Node.Node)
    subNodes=NODE()
    for ed in FreeEdge.Edge: 
        ix = np.where(npn[:,0]==ed[0])[0][0]
        subNodes.Add(Node.Node[ix])
        ix = np.where(npn[:,0]==ed[1])[0][0]
        subNodes.Add(Node.Node[ix])
    subNodes.DeleteDuplicate()

    npSubN = np.array(subNodes.Node)
    zMin = np.min(npSubN[:,3])
    idx = np.where(npSubN[:,3]==zMin)[0]

    yMax=-10**10 
    for ix in idx:
        if npSubN[ix][2] > yMax: 
            yMax = npSubN[ix][2]
            rightToe = npSubN[ix]

        
    for k, ix in enumerate(FreeEdge.Edge):
        if ix[0] == rightToe[0]: 
            i = k 
            break 
    #######################################################################

    FreeEdge.Edge[i][5] = 1
    MAX = 10000   ## max iteration for searching  error
    ShareNodePos = []
    outEdge = EDGE()

    outEdge.Add(FreeEdge.Edge[i])
    iFirstNode = FreeEdge.Edge[i][0]

    count = 0

    #    i=  # i is no matter how big, because i is redefined when next edge is found

    while i < len(FreeEdge.Edge):
        count += 1
        if count > MAX:
            print ('[INPUT] CANNOT FIND OUTER EDGES IN THE MODEL')
            del (outEdge)
            outEdge = EDGE()
            return outEdge
        j = 0
        while j < len(FreeEdge.Edge):
            if i != j:
                if FreeEdge.Edge[i][1] == FreeEdge.Edge[j][0]:
                    # print ('edge[i][1], [j][0] ', FreeEdge.Edge[i], FreeEdge.Edge[j], 'i=', i)
                    ShareNodePos.append(j)
                    # print (ShareNodePos, FreeEdge.Edge[ShareNodePos[0]][0])
            j = j + 1
        if len(ShareNodePos) != 0:
            if FreeEdge.Edge[ShareNodePos[0]][0] == iFirstNode:
                break
        else:
            print ('[INPUT] CANNOT FIND CONNECTED FREE EDGE. CHECK TIE CONDITION')
            del (outEdge)
            outEdge = EDGE()
            return outEdge
        # print ('sharenodePos count = ', len(ShareNodePos))

        if len(ShareNodePos) == 1:
            FreeEdge.Edge[ShareNodePos[0]][5] = 1
            outEdge.Add(FreeEdge.Edge[ShareNodePos[0]])
            i = ShareNodePos[0]
            del ShareNodePos
            ShareNodePos = []
        else:
            if FreeEdge.Edge[i][4] == FreeEdge.Edge[ShareNodePos[0]][4]:
                tmpPos = ShareNodePos[1]
            else:
                SHARE = ShareEdge(FreeEdge.Edge[i][4], FreeEdge.Edge[ShareNodePos[1]][4], Element)
                if SHARE == 1:
                    tmpPos = ShareNodePos[0]
                else:
                    tmpPos = ShareNodePos[1]

                    #######################################################
                    nfe1 = 0; nfe2 = 0
                    for fe in FreeEdge.Edge:
                        if fe[4] == FreeEdge.Edge[tmpPos][4]:
                            # print (fe)
                            nfe1 += 1
                        if fe[4] == FreeEdge.Edge[ShareNodePos[0]][4]:
                            # print (fe)
                            nfe2 += 1
                    # print ("nfe=", nfe, FreeEdge[tmpPos])
                    if nfe1 < nfe2:
                        tmpPos = ShareNodePos[0]
                    elif nfe1 == nfe2:
                        tienode = FreeEdge.Edge[tmpPos][0]
                        nc = 0
                        for fe in FreeEdge.Edge:
                            if fe[4] == FreeEdge.Edge[tmpPos][4] and fe[1] == tienode: 
                                nc += 1
                                break
                        if nc == 0:   tmpPos = ShareNodePos[0]
                    ########################################################

            FreeEdge.Edge[tmpPos][5] = 1
            outEdge.Add(FreeEdge.Edge[tmpPos])
            i = tmpPos
            del ShareNodePos
            ShareNodePos = []
            
    return outEdge

def FindTieLoop(TieStartNode, nextEdge, FreeEdge):
    # len(nextEdge) == 2

    MAX = 50
    NextWay = 0
    iNext = []
    startNode = FreeEdge.Edge[nextEdge[0]][0]

    if FreeEdge.Edge[nextEdge[0]][5] < 1:
        testEdge = nextEdge[0]
        saveEdge = testEdge
        if FreeEdge.Edge[testEdge][1] == TieStartNode:
            NextWay = testEdge
            return NextWay
    elif FreeEdge.Edge[nextEdge[1]][5] < 1:
        testEdge = nextEdge[1]
        saveEdge = testEdge
        if FreeEdge.Edge[testEdge][1] == TieStartNode:
            NextWay = testEdge
            return NextWay
    else:
        print ('[INPUT]', FreeEdge.Edge[nextEdge[0]], ',', FreeEdge.Edge[nextEdge[1]], ' (1) TIE Conection InCompletion')
        # logline.append(['ERROR::PRE::[INPUT] {' + str(FreeEdge[nextEdge[0]]) + ', ' + str(FreeEdge[nextEdge[1]] + '} - (1) TIE Connection Incompletion\n')])
        return 0

    #    print ('TieStart', TieStartNode, 'Node start', startNode)
    #    print ('**', FreeEdge[testEdge]) # 1st Edge

    for i in range(MAX):
        iNext = []

        iNext = NextEdge(FreeEdge, testEdge)

        if len(iNext) == 1:
            if FreeEdge.Edge[iNext[0]][5] < 1:
                if FreeEdge.Edge[iNext[0]][1] == TieStartNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[0]
                    else:
                        NextWay = nextEdge[1]
                    #                    print ('1.1',  FreeEdge[iNext[0]])
                    return NextWay
                elif FreeEdge.Edge[iNext[0]][1] == startNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[1]
                    else:
                        NextWay = nextEdge[0]
                    #                    print ('1.2',  FreeEdge[iNext[0]])
                    return NextWay
                else:
                    #                    print ('1', FreeEdge[iNext[0]])
                    testEdge = iNext[0]
            else:
                print ('[INPUT]', FreeEdge.Edge[iNext[0]], ' (2) TIE Conection InCompletion')
                # logline.append(['ERROR::PRE::[INPUT] {' + str(FreeEdge[nextEdge[0]]) + '} - (2) TIE Connection Incompletion\n'])
                return 0
        ##################### ***************** #########################

        elif len(iNext) == 2:  # if another tie is connected
            if FreeEdge.Edge[iNext[0]][5] < 1:
                testEdge = iNext[0]
                #                print ('3.1', FreeEdge[iNext[0]])

                if FreeEdge.Edge[iNext[0]][1] == TieStartNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[0]
                    else:
                        NextWay = nextEdge[1]
                    #                    print ('3.1.1',  FreeEdge[iNext[0]])
                    return NextWay
                elif FreeEdge.Edge[iNext[0]][1] == startNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[1]
                    else:
                        NextWay = nextEdge[0]
                    #                    print ('3.1.2',  FreeEdge[iNext[0]])
                    return NextWay

            elif FreeEdge.Edge[iNext[1][5]] < 1:
                testEdge = iNext[1]
                #                print ('3.2', FreeEdge[iNext[1]])

                if FreeEdge.Edge[iNext[1]][1] == TieStartNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[0]
                    else:
                        NextWay = nextEdge[1]
                    #                    print ('3.2.1',  FreeEdge[iNext[0]])
                    return NextWay
                elif FreeEdge.Edge[iNext[1]][1] == startNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[1]
                    else:
                        NextWay = nextEdge[0]
                    #                    print ('3.2.2',  FreeEdge[iNext[1]])
                    return NextWay
    return NextWay

def FindTie(FreeEdge):
    global TIENUM
    TIENUM = 1
    i = 0
    iTemp = 0
    j = 0
    connectedEdge = []
    TieEdge = EDGE()
    while i < len(FreeEdge.Edge):

        if FreeEdge.Edge[i][5] < 1:
            TIENUM += 1
            nodeStart = FreeEdge.Edge[i][0]
            FreeEdge.Edge[i][5] = TIENUM
            TieEdge.Add(FreeEdge.Edge[i])  # marked as TIE edge with No.
            iTemp = i
            #            print ('$$', FreeEdge.Edge[i])
            while FreeEdge.Edge[iTemp][1] != nodeStart:
                j += 1
                if j > 100:
                    break  # in case infinite loop
                connectedEdge = NextEdge(FreeEdge, iTemp)  # find next edge

                if len(connectedEdge) == 1:  # in case of being found just 1 edge
                    iTemp = connectedEdge[0]

                elif len(connectedEdge) == 2:  # when other tie is connected (2 ties are connected)
                    if FreeEdge.Edge[connectedEdge[0]][1] == nodeStart:
                        iTemp = connectedEdge[0]
                    elif FreeEdge.Edge[connectedEdge[1]][1] == nodeStart:
                        iTemp = connectedEdge[1]
                    else:
                        if FreeEdge.Edge[connectedEdge[0]][5] < 1 and FreeEdge.Edge[connectedEdge[1]][5] < 1:
                            iTemp = FindTieLoop(nodeStart, connectedEdge, FreeEdge)
                        elif FreeEdge.Edge[connectedEdge[0]][5] < 1:
                            iTemp = connectedEdge[0]
                        elif FreeEdge.Edge[connectedEdge[1]][5] < 1:
                            iTemp = connectedEdge[1]
                        else:
                            print ('[INPUT] {' + str(FreeEdge.Edge[connectedEdge[0]]) + ',' + str(FreeEdge.Edge[connectedEdge[1]]) + ' (0) TIE Conection InCompletion')
                            # logline.append(['ERROR::PRE::[INPUT] {' + str(FreeEdge.Edge[connectedEdge[0]]) + ', ' + str(FreeEdge.Edge[connectedEdge[1]]) + '} - (0) TIE Connection Incompletion\n'])
                            break
                else:
                    print ('[INPUT] 2 or more Ties are Connected.')
                    # logline.append(['ERROR::PRE::[INPUT] 2 or more Ties are Connected.\n'])
                    break

                # After finding next TIE Edge ################################
                FreeEdge.Edge[iTemp][5] = TIENUM
                TieEdge.Add(FreeEdge.Edge[iTemp])
            #                print ('  -', FreeEdge.Edge[iTemp])

            # print 'TIENUM = ', TIENUM, 'edge Node=', FreeEdge.Edge.edge[connectedEdge[0]][0], \
            # FreeEdge.edge[connectedEdge[0]][1], 'ref node = ', FreeEdge.edge[i][0], FreeEdge.edge[i][1]

            del connectedEdge
            connectedEdge = []

        i += 1

    #    print ('** TIE EDGE*************')
    #    for i in range(len(TieEdge)):
    #        print (TieEdge[i])
    return TieEdge

def FindMaster(edges, Nodes):
    iNum = 2
    Tedges = EDGE()
    length = 0.0
    sLength = 0.0
    ratio = 0.01
    # logline.append(['* Master Edges\n'])
    while iNum <= TIENUM:
        k = 0
        saveK = 0
        maxLength = 0.0
        sLength = 0
        while k < len(edges.Edge):
            if edges.Edge[k][5] == iNum:
                N1 = Nodes.NodeByID(edges.Edge[k][0])
                N2 = Nodes.NodeByID(edges.Edge[k][1])
                x1 = N1[2]
                y1 = N1[3]
                x2 = N2[2]
                y2 = N2[3]
                length = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
                sLength += length
                if length > maxLength:
                    maxLength = length
                    saveK = k
            k += 1

        sLength += -maxLength
        if sLength > maxLength * (1.0 + ratio) or sLength < maxLength * (1.0 - ratio):
            print ('[INP] TIE CREATION INCOMPLETE Master %s' % (edges.Edge[saveK]))
            # logline.append(['ERROR::PRE::[INP] TIE CREATION INCOMPLETE Master %s\n' % (edges[saveK])])

        Tedges.Add(edges.Edge[saveK])
        # logline.append([' ' + str(edges[saveK]) + '\n'])
        iNum += 1
    # logline.append(['  Found ' + str(len(Tedges)) + ' Tie Masters\n'])
    return Tedges

def FindSlave(Elements, medge, edges):
    i = 0
    slaveedge = EDGE()
    # logline.append(['* Slave Edges\n'])
    while i < len(edges.Edge):
        j = 0
        slave = 0
        while j < len(medge.Edge):
            if edges.Edge[i][3] == medge.Edge[j][3] and edges.Edge[i][4] == medge.Edge[j][4]:
                slave = 0
                break
            else:
                slave = 1
                j += 1
        if slave == 1:
            slaveedge.Add(edges.Edge[i])
            # logline.append([' ' + str(edges[i]) + '\n'])
        i += 1
    # logline.append(['  Found ' + str(len(slaveedge)) + ' Tie Slaves\n'])

    for i in range(len(slaveedge.Edge)):
        for j in range(len(Elements.Element)):
            if slaveedge.Edge[i][4] == Elements.Element[j][0] and Elements.Element[j][6] == 3:
                print ('[INPUT] TIE Slave (%4d) Edge is a part of Triangular Element' % (slaveedge.Edge[i][4]))
                # logline.append(['ERROR::PRE::[INPUT] TIE Slave (%4d) Edge should not be a Triangular Element\n' % (slaveedge[i][4])])

    return slaveedge

def TieSurface(Element, Node):
    AllEdges = Element.AllEdge()
    FreeEdges = FreeEdge(AllEdges)
    CenterNodes = Node.NodeIDByCoordinate('y', 0.0)
    OuterEdges = OuterEdge(FreeEdges, Node, Element)
    TieEdges = FindTie(FreeEdges)
    MasterEdges = FindMaster(TieEdges, Node)
    SlaveEdges = FindSlave(Element, MasterEdges, TieEdges)
    return MasterEdges, SlaveEdges, OuterEdges, CenterNodes, FreeEdges, AllEdges

def ChaferDivide(Elements, ChaferName, Elset):
    N = len(Elset.Elset[0]) - 1
    sum = 0
    S2000 = 2000
    S21 = 0
    S20 = 0
    S1000 = 1000
    S11 = 0
    S10 = 0
    for i in range(1, N + 1):
        sum += Elset.Elset[0][i]
        if Elset.Elset[0][i] > S2000:
            S21 += Elset.Elset[0][i] - S2000
        else:
            S20 += Elset.Elset[0][i]
        if Elset.Elset[0][i] > S1000:
            S11 += Elset.Elset[0][i] - S1000
        else:
            S10 += Elset.Elset[0][i]

    if S2000 == 2 * int((sum - S21 - S20) / N):
        Offset = 2000
    elif S1000 == 2 * int((sum - S11 - S10) / N):
        Offset = 0
    else:
        print ("No Find Offset (left / Right)")
        Offset = 0

    # print 'Left / Right Offset :', Offset

    for i in range(len(Elements.Element)):
        for j in range(len(ChaferName)):
            if Elements.Element[i][5] == ChaferName[j]:
                if Elements.Element[i][0] > Offset:
                    NewName = Elements.Element[i][5] + '_L'
                else:
                    NewName = Elements.Element[i][5] + '_R'
                Elements.Element[i][5] = NewName

    for i in range(len(Elset.Elset)):
        for j in range(len(ChaferName)):
            if Elset.Elset[i][0] == ChaferName[j]:
                left = []
                right = []
                left.append(Elset.Elset[i][0] + '_L')
                right.append(Elset.Elset[i][0] + '_R')
                for k in range(1, len(Elset.Elset[i])):
                    if Elset.Elset[i][k] > Offset:
                        left.append(Elset.Elset[i][k])
                    else:
                        right.append(Elset.Elset[i][k])

                del (Elset.Elset[i])

                Elset.Elset.append(right)
                Elset.Elset.append(left)
                break

    return Elements, Elset, Offset

def ElementDuplicationCheck(AllElements):
    try:
        tupleElement = ()
        for i in range(len(AllElements)):
            tList = []
            for k in range(len(AllElements[i])):
                if AllElements[i][k] == '':
                    tList.append(0)
                elif k == 5 or k > 6:
                    tList.append(0)
                else:
                    tList.append(AllElements[i][k])
            tupleElement = tupleElement + tuple(tList)

        N = len(AllElements[0])
        N = _islm.CheckElementDuplication(tupleElement, N)
        print ("* Element Duplication = %d" % (N))
        if N > 0:
            print ("* Element Duplication = %d" % (N))
            return 0
        else:
            return 1
    except:
        print ("* Element Duplication Check by Python Script")

        i = 0
        while i < len(AllElements):
            if AllElements[i][6] == 2:
                j = 0;
                match = 0
                while j < len(AllElements):
                    if AllElements[j][6] == 2:
                        if i != j:
                            if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][2]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][1]:
                                match = 1
                            if match > 0:
                                print (' Rebar Element ' + str(AllElements[i][0]) + ', ' + str(AllElements[j][0]) + ' are Defined TWICE. ')
                                # logline.append([' - Rebar Element' + str(AllElements[j][0]) + 'was deleted. Twice defined. CHECK MODEL\n'])
                                return 0
                    j += 1

            if AllElements[i][6] == 3:
                match = 0
                j = 0
                while j < len(AllElements):
                    if AllElements[j][6] == 3:
                        if i != j:
                            if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][2] and AllElements[i][3] == AllElements[j][3]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][3] and AllElements[i][3] == AllElements[j][1]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][3] and AllElements[i][2] == AllElements[j][1] and AllElements[i][3] == AllElements[j][2]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][3] and AllElements[i][3] == AllElements[j][2]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][1] and AllElements[i][3] == AllElements[j][3]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][3] and AllElements[i][2] == AllElements[j][2] and AllElements[i][3] == AllElements[j][1]:
                                match = 1
                            if match > 0:
                                print (' CGAX3H Elements ' + str(AllElements[i][0]) + ', ' + str(AllElements[j][0]) + ' are Defined TWICE. ')
                                return 0
                    j += 1

            if AllElements[i][6] == 4:
                j = 0
                while j < len(AllElements):
                    if AllElements[i][6] == 4 and AllElements[j][6] == 4 and i != j:
                        match = 0
                        k1 = 0
                        k2 = 0
                        k3 = 0
                        k4 = 0
                        for k in range(1, 5):
                            if AllElements[i][1] == AllElements[j][k] and k1 == 0:
                                match += 1
                                k1 = 1
                                continue
                            if AllElements[i][2] == AllElements[j][k] and k2 == 0:
                                match += 1
                                k2 = 1
                                continue
                            if AllElements[i][3] == AllElements[j][k] and k3 == 0:
                                match += 1
                                k3 = 1
                                continue
                            if AllElements[i][4] == AllElements[j][k] and k4 == 0:
                                match += 1
                                k4 = 1
                                continue

                        if match == 4:
                            print (' CGAX4H Elements ' + str(AllElements[i][0]) + ', ' + str(AllElements[j][0]) + ' are Defined TWICE. ')
                            return 0
                    j += 1
            i += 1

    return 1

def RebarConnectivity(Elements):
    i = 0
    while i < len(Elements.Element):
        if Elements.Element[i][6] == 2:
            j = 0
            while j < len(Elements.Element):
                if Elements.Element[j][6] == 2:
                    if i != j:
                        if Elements.Element[i][1] == Elements.Element[j][1] and Elements.Element[i][2] == Elements.Element[j][2]:
                            print('[INPUT] Rebar(' + str(Elements.Element[i][0]) + ') needs to be checked the numbering order.')
                            # logline.append(['[INPUT] Rebar(' + str(Elements.Element[i][0]) + ') needs to be checked the numbering order.\n'])
                            return 0
                        if Elements.Element[i][1] == Elements.Element[j][2] and Elements.Element[i][2] == Elements.Element[j][1]:
                            print('[INPUT] Rebar(' + str(Elements.Element[i][0]) + ') needs to be checked the numbering order!')
                            return 0
                j += 1
        i += 1

    i = 0
    while i < len(Elements.Element):
        if Elements.Element[i][6] == 2:
            j = 0
            count = 0
            while j < len(Elements.Element):
                if Elements.Element[j][6] == 3:
                    if Elements.Element[i][1] == Elements.Element[j][1] and Elements.Element[i][2] == Elements.Element[j][2]:
                        count += 1
                    if Elements.Element[i][1] == Elements.Element[j][2] and Elements.Element[i][2] == Elements.Element[j][3]:
                        count += 1
                    if Elements.Element[i][1] == Elements.Element[j][3] and Elements.Element[i][2] == Elements.Element[j][1]:
                        count += 1
                    if Elements.Element[i][2] == Elements.Element[j][1] and Elements.Element[i][1] == Elements.Element[j][2]:
                        count += 1
                    if Elements.Element[i][2] == Elements.Element[j][2] and Elements.Element[i][1] == Elements.Element[j][3]:
                        count += 1
                    if Elements.Element[i][2] == Elements.Element[j][3] and Elements.Element[i][1] == Elements.Element[j][1]:
                        count += 1
                elif Elements.Element[j][6] == 4:
                    if Elements.Element[i][1] == Elements.Element[j][1] and Elements.Element[i][2] == Elements.Element[j][2]:
                        count += 1
                    if Elements.Element[i][1] == Elements.Element[j][2] and Elements.Element[i][2] == Elements.Element[j][3]:
                        count += 1
                    if Elements.Element[i][1] == Elements.Element[j][3] and Elements.Element[i][2] == Elements.Element[j][4]:
                        count += 1
                    if Elements.Element[i][1] == Elements.Element[j][4] and Elements.Element[i][2] == Elements.Element[j][1]:
                        count += 1
                    if Elements.Element[i][2] == Elements.Element[j][1] and Elements.Element[i][1] == Elements.Element[j][2]:
                        count += 1
                    if Elements.Element[i][2] == Elements.Element[j][2] and Elements.Element[i][1] == Elements.Element[j][3]:
                        count += 1
                    if Elements.Element[i][2] == Elements.Element[j][3] and Elements.Element[i][1] == Elements.Element[j][4]:
                        count += 1
                    if Elements.Element[i][2] == Elements.Element[j][4] and Elements.Element[i][1] == Elements.Element[j][1]:
                        count += 1
                j += 1

            if count < 2:
                print('Rebar(' + str(Elements.Element[i][0]) + ') needs to be checked the Element Connection.', count)
                # logline.append(['ERROR::PRE::[INPUT] Rebar(' + str(Elements.Element[i][0]) + ') needs to be checked the Element Connection.\n'])
                return 0
        i += 1
    print ("* Rebar Connectivity Check Completion")
    return 1

def SolidElementOrderCheck(elements, Nodes):
    # Solid element Order Check

    i = 0
    while i < len(elements.Element):
        if elements.Element[i][6] == 4:
            N1 = Nodes.NodeByID(elements.Element[i][1])
            N2 = Nodes.NodeByID(elements.Element[i][2])
            N3 = Nodes.NodeByID(elements.Element[i][3])
            N4 = Nodes.NodeByID(elements.Element[i][4])
            x1 = N1[2] * -1
            y1 = N1[3]
            x2 = N2[2] * -1
            y2 = N2[3]
            x3 = N3[2] * -1
            y3 = N3[3]
            x4 = N4[2] * -1
            y4 = N4[3]

            distortion = Jacobian(x1, x2, x3, x4, y1, y2, y3, y4)
            # print x1, ',', y1, ', ', x2, ',', y2, ', ', x3, ',', y3, ', ', x4, ',', y4

            if distortion > 0:
                print ('[INPUT] Clockwise order or Distorted Element CGAX4H (' + str(elements[i][0]) + ')')
                # logline.append(['[INPUT] Clockwise order : CGAX4H (' + str(elements[i][0]) + ')\n The nodes are reordered to CCW\n'])
                if distortion == 4:
                    j = elements[i][2]
                    elements[i][2] = elements[i][4]
                    elements[i][4] = j
                    # logline.append(['   - The nodes are reordered to CCW.\n'])
                    print ('   - The nodes are reordered to CCW.')
                else:
                    print ('[INPUT] The Element is distorted.')
                    # logline.append(['ERROR::PRE::[INPUT] The Element is distorted.\n'])
                    return 0
        elif elements.Element[i][6] == 3:
            N1 = Nodes.NodeByID(elements.Element[i][1])
            N2 = Nodes.NodeByID(elements.Element[i][2])
            N3 = Nodes.NodeByID(elements.Element[i][3])
            x1 = N1[2] * -1
            y1 = N1[3]
            x2 = N2[2] * -1
            y2 = N2[3]
            x3 = N3[2] * -1
            y3 = N3[3]

            Det1 = NormalVector(x1, x2, x3, y1, y2, y3)
            if Det1 < 0:
                j = elements.Element[i][2]
                elements.Element[i][2] = elements.Element[i][3]
                elements.Element[i][3] = j
                print ('[INPUT] Clockwise order : CGAX3H (' + str(elements.Element[i][0]) + ')')
                print ('   - The nodes are reordered to CCW.')
                # logline.append(['[INPUT] Clockwise order : CGAX3H (' + str(elements[i][0]) + ')\n The nodes are reordered to CCW\n'])
        i += 1

    return 1

def SolidElementShapeCheck(Elements, Nodes, CriticalAngle, CriticalLength):
    NarrowElement = 0
    x1 = 0
    x2 = 0
    x3 = 0
    x4 = 0
    y1 = 0
    y2 = 0
    y3 = 0
    y4 = 0

    for i in range(len(Elements)):
        distance = []

        if Elements[i][6] == 3:
            for j in range(len(Nodes)):
                if Elements[i][1] == Nodes[j][0]:
                    x1 = Nodes[j][3]
                    y1 = Nodes[j][2]
                if Elements[i][2] == Nodes[j][0]:
                    x2 = Nodes[j][3]
                    y2 = Nodes[j][2]
                if Elements[i][3] == Nodes[j][0]:
                    x3 = Nodes[j][3]
                    y3 = Nodes[j][2]
            distance.append(math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2)))
            distance.append(math.sqrt(math.pow(x3 - x2, 2) + math.pow(y3 - y2, 2)))
            distance.append(math.sqrt(math.pow(x1 - x3, 2) + math.pow(y1 - y3, 2)))
            fmin = distance[0]
            fmax = distance[0]

            for m in range(3):
                if fmin > distance[m]:
                    fmin = distance[m]
                if fmax < distance[m]:
                    fmax = distance[m]

            if fmax / fmin > 30.0:
                # print 'Warning! Element(3 Node %d) is Too NARROW. Length Ratio(Max/Min)=%10.2f' % (Elements[i][0], fmax / fmin)
                # ErrorFile.writelines( '[Input] Element(3 Node) Too NARROW. No. %5d, Length Ratio(Max/Min)=%10.2f\n' % (Elements[i][0], fmax / fmin))
                # NarrowElement+=1
                pass
            if fmin < CriticalLength:
                print ('Warning! One of the edges in the Element(3 Node, %d) is too small(%10.7fmm)' % (Elements[i][0], fmin * 1000))

            ####### Angle between edges
            angle = []
            DX1 = x2 - x1
            DY1 = y2 - y1
            DX2 = x3 - x2
            DY2 = y3 - y2
            DX3 = x1 - x3
            DY3 = y1 - y3

            cos = (DX1 * DX2 + DY1 * DY2) / (distance[0] * distance[1])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX2 * DX3 + DY2 * DY3) / (distance[1] * distance[2])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX3 * DX1 + DY3 * DY1) / (distance[2] * distance[0])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            for m in range(len(angle)):
                if angle[m] < CriticalAngle or angle[m] > 180.0 - CriticalAngle:
                    print ('Warning! Element 3 Node %5d(%s) is sharp or almost line shape. Angle between Edge : %6.4f' % (Elements[i][0], Elements[i][5], angle[m]))

        distance = []
        if Elements[i][6] == 4:
            for j in range(len(Nodes)):
                if Elements[i][1] == Nodes[j][0]:
                    x1 = Nodes[j][3]
                    y1 = Nodes[j][2]
                if Elements[i][2] == Nodes[j][0]:
                    x2 = Nodes[j][3]
                    y2 = Nodes[j][2]
                if Elements[i][3] == Nodes[j][0]:
                    x3 = Nodes[j][3]
                    y3 = Nodes[j][2]
                if Elements[i][4] == Nodes[j][0]:
                    x4 = Nodes[j][3]
                    y4 = Nodes[j][2]
            distance.append(math.sqrt(math.pow(x4 - x2, 2) + math.pow(y4 - y2, 2)))
            distance.append(math.sqrt(math.pow(x1 - x3, 2) + math.pow(y1 - y3, 2)))
            distance.append(math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2)))
            distance.append(math.sqrt(math.pow(x3 - x2, 2) + math.pow(y3 - y2, 2)))
            distance.append(math.sqrt(math.pow(x4 - x3, 2) + math.pow(y4 - y3, 2)))
            distance.append(math.sqrt(math.pow(x1 - x4, 2) + math.pow(y1 - y4, 2)))

            fmin = distance[0]
            fmax = distance[0]

            for m in range(6):
                if fmin > distance[m]:
                    fmin = distance[m]
                if fmax < distance[m]:
                    fmax = distance[m]

            if fmin == 0:
                print (distance, Elements[i])

            if fmax / fmin > 10.0:
                # print 'Warning! Element(4 Node %d) is Too NARROW. Diagonal/Edge Length Ratio(Max/Min)=%10.2f' % (Elements[i][0], fmax / fmin)
                pass
            #   ErrorFile.writelines( 'Pre::[Input] Element(4 Node) Too NARROW. No. %5d, Diagonal/Edge Length Ratio(Max/Min)=%10.2f\n' % (Elements[i][0], fmax / fmin))
            #   NarrowElement+=1
            if fmin < CriticalLength:
                print ('Warning! One of the edges in the Element(4 Node %d) is too small(%10.7fmm)' % (Elements[i][0], fmin * 1000))

            ####### Angle between edges
            angle = []
            DX1 = x2 - x1
            DY1 = y2 - y1
            DX2 = x3 - x2
            DY2 = y3 - y2
            DX3 = x4 - x3
            DY3 = y4 - y3
            DX4 = x1 - x4
            DY4 = y1 - y4

            cos = (DX1 * DX2 + DY1 * DY2) / (distance[2] * distance[3])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX2 * DX3 + DY2 * DY3) / (distance[3] * distance[4])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX3 * DX4 + DY3 * DY4) / (distance[4] * distance[5])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX4 * DX1 + DY4 * DY1) / (distance[5] * distance[2])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            for m in range(len(angle)):
                if angle[m] < CriticalAngle or angle[m] > 180.0 - CriticalAngle:
                    print ('Warning! Element %5d is Sharp or almost Triangular shape. Angle between Edge : %6.4f' % (Elements[i][0], angle[m]))

    if NarrowElement > 0:
        print ('No. of NarrowElement = ', NarrowElement)
        return 0

    return 1

def BeadWidth(Element, Node):
    BDCore = ELEMENT()

    for i in range(len(Element.Element)):
        if Element.Element[i][5] == 'BEAD_L':
            BDCore.Add(Element.Element[i])
    if len(BDCore.Element) == 0:
        for i in range(len(Element.Element)):
            if Element.Element[i][5] == 'BEAD_R':
                BDCore.Add(Element.Element[i])
    BDEdge = BDCore.AllEdge()
    BDFree = FreeEdge(BDEdge)
    BDfree = BDCore.FreeEdge()

    nodes = []
    for i in range(len(BDFree.Edge)):
        if i == 0:
            nodes.append(BDFree.Edge[i][0])
            nodes.append(BDFree.Edge[i][1])
        else:
            N = len(nodes)
            match1 = 0
            match2 = 0
            for j in range(N):
                if BDFree.Edge[i][0] == nodes[j]:
                    match1 = 1
                if BDFree.Edge[i][1] == nodes[j]:
                    match2 = 1
            if match1 == 0:
                nodes.append(BDFree.Edge[i][0])
            if match2 == 0:
                nodes.append(BDFree.Edge[i][1])
    N = len(nodes)
    center = Area(nodes, Node)
    min = 100000.0
    max = -100000.0

    for i in range(N):
        Ni = Node.NodeByID(nodes[i])
        if abs(Ni[2]) > max:
            max = abs(Ni[2])
        if abs(Ni[2]) < min:
            min = abs(Ni[2])

    if abs(center[1]) > abs(max) or abs(center[1]) < abs(min):
        center[1] = (abs(max) + abs(min)) / 2.0

    return abs(min), abs(max), abs(center[1])

def FindSolidElementBetweenMembrane(m1, m2, Elements):
    # Data types of m1, m2 are string
    between = []
    Elm1 = []
    Elm2 = []

    for i in range(len(Elements.Element)):
        if Elements.Element[i][5] == m1 or Elements.Element[i][5] == m2:
            for j in range(len(Elements.Element)):
                if j != i and Elements.Element[j][6] == 3:
                    for k in range(1, 3):
                        if k == 1:
                            m = 2
                        else:
                            m = 1
                        for l in range(1, 4):
                            n = l + 1
                            if n > 3:
                                n = l - 3

                            if Elements.Element[i][k] == Elements.Element[j][l] and Elements.Element[i][m] == Elements.Element[j][n]:
                                if Elements.Element[i][5] == m1:
                                    Elm1.append(Elements.Element[j])
                                else:
                                    Elm2.append(Elements.Element[j])
                                break

                elif j != i and Elements.Element[j][6] == 4:
                    for k in range(1, 3):
                        if k == 1:
                            m = 2
                        else:
                            m = 1
                        for l in range(1, 5):
                            n = l + 1
                            if n > 4:
                                n = l - 4

                            if Elements.Element[i][k] == Elements.Element[j][l] and Elements.Element[i][m] == Elements.Element[j][n]:
                                if Elements.Element[i][5] == m1:
                                    Elm1.append(Elements.Element[j])
                                else:
                                    Elm2.append(Elements.Element[j])
                                break

    for i in range(len(Elm1)):
        for j in range(len(Elm2)):
            if Elm1[i][0] == Elm2[j][0]:
                between.append(Elm2[j][0])
                break

    m1f = []
    m2f = []
    for i in range(len(Elm1)):
        match = 0
        for j in range(len(between)):
            if Elm1[i][0] == between[j]:
                match = 1
                break
        if match == 0:
            m1f.append(Elm1[i])

    for i in range(len(Elm2)):
        match = 0
        for j in range(len(between)):
            if Elm2[i][0] == between[j]:
                match = 1
                break
        if match == 0:
            m2f.append(Elm2[i])
    ########################################################
    for i in range(len(m2f)):
        for j in range(len(m1f)):
            match = 0
            for m in range(1, 5):
                for n in range(1, 5):
                    if m2f[i][m] == m1f[j][n] and m1f[j][n] != '':
                        match += 1
            if match == 2:
                between.append(m2f[i][0])
                between.append(m1f[j][0])
                # print "Between Appended"
                break

    return between

def Surface(OutEdges, Node, OffsetLeftRight, TreadElset, Elements):
    # Press=[]; RimContact=[]; TreadToRoad=[]
    Press = EDGE()
    RimContact = EDGE()
    TreadToRoad = EDGE()

    EOffset = NOffset = OffsetLeftRight

    Offset = [EOffset, NOffset]

    low = 100000000.0
    startNode = 0
    nextedge = []
    edgeNo = 0
    i = 0
    opposite = 0
    tmpY = 0
    while i < len(Node.Node):
        if Node.Node[i][3] < low and Node.Node[i][0] > Offset[0] and Node.Node[i][2] > 0:
            low = Node.Node[i][3]
            startNode = Node.Node[i][0]
            tmpY = Node.Node[i][2]
        i += 1
        if i > 100000:
            print ("[INPUT] Cannot Find the 1st Node for Pressure")
            return Press, RimContact, TreadToRoad

    for i in range(len(Node.Node)):
        if low == Node.Node[i][3] and tmpY == -Node.Node[i][2]:
            opposite = Node.Node[i][0]
            break

    i = 0
    while i < len(OutEdges.Edge):
        if OutEdges.Edge[i][0] == startNode:
            edgeNo = i
            break
        i += 1
        if i > 100000:
            print ("[INPUT] Cannot Find the 1st Edge for Pressure")
            return Press, RimContact, TreadToRoad

    i = edgeNo
    #    print ('**', OutEdges.Edge[i]); count=0
    Press.Add(OutEdges.Edge[edgeNo])
    count = 0
    while OutEdges.Edge[i][1] != opposite:
        nextedge = NextEdge(OutEdges, i)
        i = nextedge[0]
        Press.Add(OutEdges.Edge[i])
        if count > 1000:  # in case of infinite loop!!
            break
        count += 1
    #    print ('No of press', len(Press))
    # ADD Bead Base Edge as Pressure Surface
    #    print (Elements.Element[0])

    MAXY = 0
    MINY = 100000000.0
    for i in range(len(Elements.Element)):
        if Elements.Element[i][5] == 'BEAD_R' or Elements.Element[i][5] == 'BEAD_L':
            # print ("BD1 Elements", Elements.Element[i])
            for j in [1, 2, 3, 4]:
                if Elements.Element[i][j] != '':
                    Ni = Node.NodeByID(Elements.Element[i][j])
                    ValueY = Ni[2]
                    if math.fabs(ValueY) > MAXY:
                        MAXY = math.fabs(ValueY)
                    if math.fabs(ValueY) < MINY:
                        MINY = math.fabs(ValueY)
    AVGY = (MAXY + MINY) / 2.0
    # print ("find No", AVGY, MAXY, MINY)

    iNext = nextedge[0]
    nextedge = NextEdge(OutEdges, iNext)
    Ni = Node.NodeByID(OutEdges.Edge[nextedge[0]][0])
    ValueY = Ni[2]
    c = 0
    while math.fabs(ValueY) < AVGY:
        # print ('C=', c, OutEdges[nextedge[0]])
        Press.Add(OutEdges.Edge[nextedge[0]])
        iNext = nextedge[0]
        nextedge = NextEdge(OutEdges, iNext)
        Ni = Node.NodeByID(OutEdges.Edge[nextedge[0]][0])
        ValueY = Ni[2]
        c += 1
        if c > 100000:
            print ('[INPUT] Cannot Find the next Pressure Edge (Right)')
            return Press, RimContact, TreadToRoad

    previousedge = PreviousEdge(OutEdges, edgeNo)
    Ni = Node.NodeByID(OutEdges.Edge[previousedge[0]][1])
    ValueY = Ni[2]
    c = 0
    while math.fabs(ValueY) < AVGY:
        #        print (OutEdges[previousedge[0]])
        Press.Add(OutEdges.Edge[previousedge[0]])
        iNext = previousedge[0]
        previousedge = PreviousEdge(OutEdges, iNext)
        Ni = Node.NodeByID(OutEdges.Edge[previousedge[0]][1])
        ValueY = Ni[2]
        c += 1
        if c > 100000:
            print ('[INPUT] Cannot Find the next Pressure Edge (Left)')
            return Press, RimContact, TreadToRoad

    #    print ('No of press', len(Press))

    if len(Press.Edge) < 1:
        print ('[INPUT] No Surface was created for Inner Pressure')
        return Press, RimContact, TreadToRoad
        # logline.append(['ERROR::PRE::[INPUT] No Surface was created for Inner Pressure\n'])
    else:
        print ('* All Edges for Pressure are searched.')
        # logline.append(['* All Surfaces for Pressure are searched. \n'])

    i = 0
    while i < len(OutEdges.Edge):
        if OutEdges.Edge[i][2] == 'HUS' or OutEdges.Edge[i][2] == 'RIC':
            ipress = 0
            if ipress == 0:
                RimContact.Add(OutEdges.Edge[i])
                # print "Rim Contact", OutEdges[i]
        i += 1
        if i > 100000:
            print ('[INPUT] Cannot Find the Next Outer Edges ')
            return Press, RimContact, TreadToRoad

    #############################################
    ## ADD 5 edges of BSW
    #############################################
    NoOfAddingEdge = 5
    for i in range(len(RimContact.Edge)):
        for j in range(len(OutEdges.Edge)):
            if RimContact.Edge[i] == OutEdges.Edge[j]:
                break
        ne = NextEdge(OutEdges, j)
        m = ne[0]
        if OutEdges.Edge[m][2] == 'BSW':
            RimContact.Add(OutEdges.Edge[m])
            for j in range(NoOfAddingEdge - 1):
                ne = NextEdge(OutEdges, m)
                n = ne[0]
                if OutEdges.Edge[n][2] == 'BSW':
                    RimContact.Add(OutEdges.Edge[n])
                m = n
        ne = PreviousEdge(OutEdges, j)
        m = ne[0]
        if OutEdges.Edge[m][2] == 'BSW':
            RimContact.Add(OutEdges.Edge[m])
            for j in range(NoOfAddingEdge - 1):
                ne = PreviousEdge(OutEdges, m)
                n = ne[0]
                if OutEdges.Edge[n][2] == 'BSW':
                    RimContact.Add(OutEdges.Edge[n])
                m = n
    ###############################################

    if len(RimContact.Edge) < 1:
        print ('ERROR::PRE::[INPUT] No Surface was created for Rim Contact  ')
        return Press, RimContact, TreadToRoad
        # logline.append(['ERROR::PRE::[INPUT] No Surface was created for Rim Contact\n'])
    else:
        print ('* All Edges for Rim Contact are searched.')
        # logline.append(['* All Surfaces for Rim Contact are searched. \n'])
    i = 0
    while i < len(OutEdges.Edge):
        j = 0
        while j < len(TreadElset):
            if OutEdges.Edge[i][2] == TreadElset[j]:
                TreadToRoad.Add(OutEdges.Edge[i])
                break
            j += 1
            if j > 100000:
                print ('[INPUT]Cannot Find the Next Tread To Road Edges ')
                return Press, RimContact, TreadToRoad
        i += 1

    if len(TreadToRoad.Edge) < 1:
        print ('[INPUT] No Surface was created for Road Contact')
        return Press, RimContact, TreadToRoad
        # logline.append(['ERROR::PRE::[INPUT] No Surface was created for Road Contact\n'])
    else:
        print ('* All Edges for Road Contact are searched.')
        # logline.append(['* All Surfaces for Road Contact are searched. \n'])

    return Press, RimContact, TreadToRoad

def ElementCheck(Elements, Nodes):
    # rebar Connectivity
    # Element Shape

    tmpEL = []
    for i in range(len(Elements.Element)):
        tmpEL.append(Elements.Element[i][0])
        tmpEL.append(Elements.Element[i][1])
        tmpEL.append(Elements.Element[i][2])
        if Elements.Element[i][3] == '':
            tmpEL.append(0)
        else:
            tmpEL.append(Elements.Element[i][3])
        if Elements.Element[i][4] == '':
            tmpEL.append(0)
        else:
            tmpEL.append(Elements.Element[i][4])
        tmpEL.append(Elements.Element[i][6])

    tmpND = []
    tmpCoord = []
    for i in range(len(Nodes.Node)):
        tmpND.append(Nodes.Node[i][0])
        tmpCoord.append(Nodes.Node[i][1])
        tmpCoord.append(Nodes.Node[i][2])
        tmpCoord.append(Nodes.Node[i][3])

    tupleEL = tuple(tmpEL)
    tupleND = tuple(tmpND)
    tupleCo = tuple(tmpCoord)

    Results = _islm.SolidRebarCheck(tupleEL, 6, tupleND, tupleCo, 3, 5)

    Message = []
    if Results > 100000:
        if Results % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] More than 1 Sold Element is distorted."])
            Results = 0
        if int(Results / 10) % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] More than 1 Rebar is disconnected."])
            Results = 0
        if int(Results / 100) % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] Some Rebar Elements are Defined Twice or More."])
            Results = 0
        if int(Results / 1000) % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] Some CGAX3H Elements are Defined Twice or More."])
            Results = 0
        if int(Results / 10000) % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] Some CGAX4H Elements are Defined Twice or More."])
            Results = 0
    else:
        Results = 1

    return Results, Message

def Write2DFile(fileFullName, Node, Element, Elset, TreadToRoad, Press, RimContact, MasterEdges, SlaveEdges, Offset, CenterNodes, Comments):
    FileName = os.path.basename(fileFullName)
    FileName = FileName + '.msh'
    f = open(FileName, 'w')

    fline = []
    for i in range(len(Comments)):
        fline.append([Comments[i]])
    fline.append(['*NODE, SYSTEM=R\n'])

    i = 0
    while i < len(Node.Node):
        fline.append(['%10d, %15.6E, %15.6E, %15.6E\n' % (Node.Node[i][0], Node.Node[i][3], Node.Node[i][2], Node.Node[i][1])])
        i += 1
    i = 0
    fline.append(['*ELEMENT, TYPE=MGAX1\n'])
    while i < len(Element.Element):
        if Element.Element[i][6] == 2:
            fline.append(['%10d, %10d, %10d\n' % (Element.Element[i][0], Element.Element[i][1], Element.Element[i][2])])
        i += 1
    i = 0
    fline.append(['*ELEMENT, TYPE=CGAX3H\n'])
    while i < len(Element.Element):
        if Element.Element[i][6] == 3:
            fline.append(['%10d, %10d, %10d, %10d\n' % (Element.Element[i][0], Element.Element[i][1], Element.Element[i][2], Element.Element[i][3])])
        i += 1
    i = 0
    fline.append(['*ELEMENT, TYPE=CGAX4H\n'])
    while i < len(Element.Element):
        if Element.Element[i][6] == 4:
            fline.append(['%10d, %10d, %10d, %10d, %10d\n' % (Element.Element[i][0], Element.Element[i][1], Element.Element[i][2], Element.Element[i][3], Element.Element[i][4])])
        i += 1
    isCH1 = 0
    isCH2 = 0
    isBDr = 0
    isBDl = 0
    for i in range(len(Elset.Elset)):
        fline.append(["*ELSET, ELSET=%s\n" % (Elset.Elset[i][0])])
        if 'CH1' in Elset.Elset[i][0]:
            isCH1 = 1
        if 'CH2' in Elset.Elset[i][0]:
            isCH2 = 1
        if 'BEAD_R' in Elset.Elset[i][0]:
            isBDr = 1
        if 'BEAD_L' in Elset.Elset[i][0]:
            isBDl = 1

        k = 0
        for j in range(1, len(Elset.Elset[i])):
            if ((k + 1) % 10 != 0):
                if (k + 2) == len(Elset.Elset[i]):
                    fline.append(['%8d\n' % (Elset.Elset[i][j])])
                else:
                    fline.append(['%8d,' % (Elset.Elset[i][j])])
            else:
                fline.append(['%8d\n' % (Elset.Elset[i][j])])
            k += 1
    if isCH1 == 1:
        fline.append(['*ELSET,  ELSET=CH1\n'])
        fline.append([' CH1_R, CH1_L\n'])
    if isCH2 == 1:
        fline.append(['*ELSET,  ELSET=CH2\n'])
        fline.append([' CH2_R, CH2_L\n'])

    i = 0
    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=CONT\n'])
    while i < len(TreadToRoad.Edge):
        fline.append(['%6d, %s\n' % (TreadToRoad.Edge[i][4], TreadToRoad.Edge[i][3])])
        i += 1

    i = 0
    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=PRESS\n'])
    while i < len(Press.Edge):
        fline.append(['%6d, %s\n' % (Press.Edge[i][4], Press.Edge[i][3])])
        i += 1

    i = 0
    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=RIC_R\n'])
    # print 'Offset=', Offset
    if Offset == 0 or Offset == 1000:
        sum = 0
        for i in range(len(RimContact.Edge)):
            sum += RimContact.Edge[i][4]
        Offset = int(sum / len(RimContact.Edge))

    # print 'Offset=', Offset, 'Len RC', len(RimContact.Edge)
    i = 0
    while i < len(RimContact.Edge):
        # print 'i=', i, ',', RimContact.Edge[i], ' Offset=', Offset
        if RimContact.Edge[i][4] < Offset:
            fline.append(['%6d, %s\n' % (RimContact.Edge[i][4], RimContact.Edge[i][3])])
        i += 1

    i = 0
    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=RIC_L\n'])
    while i < len(RimContact.Edge):
        if RimContact.Edge[i][4] > Offset:
            fline.append(['%6d, %s\n' % (RimContact.Edge[i][4], RimContact.Edge[i][3])])
        i += 1

    sorted(MasterEdges.Edge, key=lambda element: element[4])
    i = 0;
    while i < len(MasterEdges.Edge):
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=Tie_m' + str(i + 1) + '\n'])
        fline.append(['%6d, %s\n' % (MasterEdges.Edge[i][4], MasterEdges.Edge[i][3])])
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=Tie_s' + str(i + 1) + '\n'])
        j = 0
        while j < len(SlaveEdges.Edge):
            if SlaveEdges.Edge[j][5] == MasterEdges.Edge[i][5]:
                fline.append(['%6d, %s\n' % (SlaveEdges.Edge[j][4], SlaveEdges.Edge[j][3])])
            j += 1
        i += 1

    i = 0
    while i < len(MasterEdges.Edge):
        fline.append(['*TIE, NAME=TIE_' + str(i + 1) + '\n'])
        fline.append(['Tie_s' + str(i + 1) + ', ' + 'Tie_m' + str(i + 1) + '\n'])
        i += 1

    if isBDr == 1 and isBDl == 1:
        fline.append(['*ELSET, ELSET=BD1\n BEAD_R, BEAD_L'])
    elif isBDr == 1:
        fline.append(['*ELSET, ELSET=BD1\n BEAD_R'])
    elif isBDl == 1:
        fline.append(['*ELSET, ELSET=BD1\n BEAD_L'])

    Bdr = [0, 0]
    for i in range(len(Element.Element)):
        if Element.Element[i][5] == 'BEAD_L':
            Bdr[0] = Element.Element[i][1]
        if Element.Element[i][5] == 'BEAD_R':
            Bdr[1] = Element.Element[i][1]

    if Bdr[0] != 0:
        fline.append(['\n*NSET, NSET=BD_L\n'])
        fline.append([str(Bdr[0])])
    if Bdr[1] != 0:
        fline.append(['\n*NSET, NSET=BD_R\n'])
        fline.append([str(Bdr[1])])

    if Bdr[0] != 0 and Bdr[1] != 0:
        fline.append(['\n*NSET, NSET=BDR\n BD_R, BD_L\n'])
    elif Bdr[1] != 0:
        fline.append(['\n*NSET, NSET=BDR\n BD_R\n'])
    elif Bdr[0] != 0:
        fline.append(['\n*NSET, NSET=BDR\n BD_L\n'])
    else:
        pass

    fline.append(['*NSET, NSET=CENTER\n'])

    i = 0
    while i < len(CenterNodes):
        if ((i + 1) % 10 == 0):
            fline.append(['%8d\n' % (CenterNodes[i])])
        else:
            fline.append(['%8d,' % (CenterNodes[i])])
        i += 1

    f.writelines('%s' % str(item[0]) for item in fline)

    f.close()

def Change3DFace(Id):
    face = ''
    if Id == 'S1':
        face = 'S3'
    elif Id == 'S2':
        face = 'S4'
    elif Id == 'S3':
        face = 'S5'
    elif Id == 'S4':
        face = 'S6'
    return face

def DivideTreadAndBody(Element, TreadElset, Node):
    Tread = ELEMENT()
    Body = ELEMENT()

    i = 0
    while i < len(Element.Element):
        j = 0;
        tread = 0
        while j < len(TreadElset):
            if Element.Element[i][5] == TreadElset[j]:
                tread = 1
                break
            j += 1
        if tread == 1:
            Tread.Add(Element.Element[i])
        else:
            Body.Add(Element.Element[i])

        i += 1

    BodyNode = NODE()
    TreadNode = NODE()
    for i in range(len(Node.Node)):
        match = 0
        for j in range(len(Tread.Element)):
            for m in range(1, 5):
                if Tread.Element[j][m] == Node.Node[i][0]:
                    match = 1
                    break
            if match == 1:
                break
        if match == 1:
            TreadNode.Add(Node.Node[i])
        match = 0
        for j in range(len(Body.Element)):
            match = 0
            for m in range(1, 5):
                if Body.Element[j][m] == Node.Node[i][0]:
                    match = 1
                    break
            if match == 1:
                break
        if match == 1:
            BodyNode.Add(Node.Node[i])

    print ('* Number of TREAD NODEs : ' + str(len(TreadNode.Node)))
    print ('* Number of BODY NODEs  : ' + str(len(BodyNode.Node)))

    return TreadNode, BodyNode, Tread, Body

def BodyTopTreadBottomEdge(TDNode, BDNode, TreadElement, BodyElement, TreadToRoadSurface, MasterEdges, SlaveEdges, TreadElset):
    BodyOutEdges = BodyElement.OuterEdge(BDNode)
    TreadOutEdges = TreadElement.OuterEdge(TDNode)

    BodyTop = EDGE()
    TreadBottom = EDGE()

    for i in range(len(TreadOutEdges.Edge)):
        match = 0
        for j in range(len(TreadToRoadSurface.Edge)):
            if (TreadOutEdges.Edge[i][0] == TreadToRoadSurface.Edge[j][0]) and (TreadOutEdges.Edge[i][1] == TreadToRoadSurface.Edge[j][1]):
                match = 1
        if match == 0:
            TreadBottom.Add(TreadOutEdges.Edge[i])

    for i in range(len(TreadOutEdges.Edge)):
        for j in range(len(BodyOutEdges.Edge)):
            if (BodyOutEdges.Edge[j][0] == TreadOutEdges.Edge[i][0] and BodyOutEdges.Edge[j][1] == TreadOutEdges.Edge[i][1]) or (BodyOutEdges.Edge[j][0] == TreadOutEdges.Edge[i][1] and BodyOutEdges.Edge[j][1] == TreadOutEdges.Edge[i][0]):
                BodyTop.Add(BodyOutEdges.Edge[j])
                break

    for i in range(len(MasterEdges.Edge)):
        Mno = 0
        for j in range(len(TreadElset)):
            if MasterEdges.Edge[i][2] == TreadElset[j]:
                Mno = MasterEdges.Edge[i][5]
                break
        if Mno > 0:
            Sno = []
            for j in range(len(SlaveEdges.Edge)):
                if Mno == SlaveEdges.Edge[j][5]:
                    Sno.append(SlaveEdges.Edge[j])

            for j in range(len(Sno)):
                for k in range(len(BodyOutEdges.Edge)):
                    if (Sno[j][0] == BodyOutEdges.Edge[k][0]) and (Sno[j][1] == BodyOutEdges.Edge[k][1]):
                        BodyTop.Add(BodyOutEdges.Edge[k])
                        # print 'Add BODY TOP Surface '
                        break

    for i in range(len(SlaveEdges.Edge)):
        Mno = 0
        for j in range(len(TreadElset)):
            if SlaveEdges.Edge[i][2] == TreadElset[j]:
                Mno = SlaveEdges.Edge[i][5]
                break
        if Mno > 0:
            Sno = []
            for j in range(len(MasterEdges.Edge)):
                if Mno == MasterEdges.Edge[j][5]:
                    Sno.append(MasterEdges.Edge[j])

            for j in range(len(Sno)):
                for k in range(len(BodyOutEdges.Edge)):
                    if (Sno[j][0] == BodyOutEdges.Edge[k][0]) and (Sno[j][1] == BodyOutEdges.Edge[k][1]):
                        m = 0
                        match = 0
                        while m < len(BodyTop.Edge):
                            if BodyTop.Edge[m][4] == Sno[j][4]:
                                match = 1
                                break
                            m += 1
                        if match == 0:
                            BodyTop.Add(BodyOutEdges.Edge[k])
                        break

    return TreadBottom, BodyTop, BodyOutEdges, TreadOutEdges

def TreadTieCheck(MasterEdges, SlaveEdges, TreadBottom, BodyTop):
    M = EDGE()
    S = EDGE()
    for i in range(len(MasterEdges.Edge)):
        match = 0
        for j in range(len(TreadBottom.Edge)):
            if TreadBottom.Edge[j][0] == MasterEdges.Edge[i][0] and TreadBottom.Edge[j][1] == MasterEdges.Edge[i][1]:
                match += 1
                break
        for j in range(len(BodyTop.Edge)):
            if BodyTop.Edge[j][0] == MasterEdges.Edge[i][0] and BodyTop.Edge[j][1] == MasterEdges.Edge[i][1]:
                match += 1
                if MasterEdges.Edge[i][2] == 'BSW':
                    match += -1
                break
        if match == 0:
            M.Add(MasterEdges.Edge[i])

    for i in range(len(SlaveEdges.Edge)):
        match = 0
        for j in range(len(TreadBottom.Edge)):
            if TreadBottom.Edge[j][0] == SlaveEdges.Edge[i][0] and TreadBottom.Edge[j][1] == SlaveEdges.Edge[i][1]:
                match += 1
                break
        for j in range(len(BodyTop.Edge)):
            if BodyTop.Edge[j][0] == SlaveEdges.Edge[i][0] and BodyTop.Edge[j][1] == SlaveEdges.Edge[i][1]:
                match += 1
                break
        if match == 0:
            S.Add(SlaveEdges.Edge[i])

    return M, S

def Write3DBodyMeshWithC(Mesh3DBody, BodyNode, BodyElement, MasterEdges, SlaveEdges, PressureSurface, RimContactSurface, BodyOut, OffsetSector, OffsetLeftRight, Elset, TreadElset, SectorOption, Div):
    Mesh3DBody = Mesh3DBody[:-4]
    if SectorOption == 1:
        MaxR = 0
        for i in range(len(BodyNode.Node)):
            if BodyNode.Node[i][3] > MaxR:
                MaxR = BodyNode.Node[i][3]
        cir = math.pi * 2 * MaxR
        sectors = int(cir / Div)
        iAngle = (math.pi * 2) / float(sectors)
        print ('* Body Sectors  : %d (Element Length=%5.2fmm, Initial Body MAX Dia.= %6.1fmm), Each Sector Angle=%6.4f deg' % (sectors, Div * 1000, MaxR * 2000, iAngle * 180 / math.pi))
    else:
        sectors = int(Div)
        # iAngle = (math.pi*2) / float(sectors)
        print ("* Body Sectors : %d,  Each Sector Angle : %6.4f deg" % (sectors, 360 / float(sectors)))

    tupleNode = ()
    for i in range(len(BodyNode.Node)):
        tupleNode = tupleNode + tuple(BodyNode.Node[i])
    Nset = len(BodyNode.Node[0])
    tupleElement = ()
    for i in range(len(BodyElement.Element)):
        tList = []
        for k in range(len(BodyElement.Element[i])):
            if BodyElement.Element[i][k] == '':
                tList.append(0)
            elif k == 5 or k > 6:
                tList.append(0)
            else:
                tList.append(BodyElement.Element[i][k])
        # print tList
        tupleElement = tupleElement + tuple(tList)
    Eset = len(BodyElement.Element[0])
    _islm.CreateTireBody(Mesh3DBody, tupleNode, Nset, tupleElement, Eset, 5000, 5000, OffsetSector, sectors)

    i = 0
    while i < len(Elset.Elset):
        # for i in range(len(Elset.Elset)):
        match = 0
        # print TreadElset, Elset.Elset[i][0]
        N = len(TreadElset)
        # for j in range(N):
        j = 0
        while j < N:
            if Elset.Elset[i][0] == TreadElset[j]:
                match = 1
                break
            j += 1
        if match == 0:
            list = []
            k = 1
            while k < len(Elset.Elset[i]):
                # for k in range(1, len(Elset.Elset[i])):
                list.append(Elset.Elset[i][k])
                k += 1
            ElsetName = Elset.Elset[i][0]
            tupleList = tuple(list)

            _islm.Write3DElset(sectors, OffsetSector, ElsetName, tupleList, Mesh3DBody + '.axi')
        i += 1

    f = open(Mesh3DBody + '.axi', "a")
    fline = []

    fline.append(["*ELSET, ELSET=BD1\n"])
    i = 0
    while i < len(Elset.Elset):
        # for i in range(len(Elset.Elset)):
        if "BEAD" in Elset.Elset[i][0]:
            k = 0
            while k < sectors:
                # for k in range(sectors):
                count = 0
                m = 1
                while m < len(Elset.Elset[i]):
                    # for m in range(1, len(Elset.Elset[i])):
                    newEL = Elset.Elset[i][m] + k * OffsetSector
                    count += 1
                    if count % 16 == 0 or count == len(Elset.Elset[i]) - 1:
                        fline.append(["%d,\n" % (newEL)])
                    else:
                        fline.append(["%d, " % (newEL)])
                    m += 1
                k += 1
        i += 1
    ############################################################################################
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=TIREBODY\n"])
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(BodyOut.Edge):
            # for j in range(len(BodyOut.Edge)):
            newEL = BodyOut.Edge[j][4] + i * OffsetSector
            face = Change3DFace(BodyOut.Edge[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=RIC_R\n"])
    # print 'OffsetLR', OffsetLeftRight
    if OffsetLeftRight == 0 or OffsetLeftRight == 1000:
        sum = 0
        for i in range(len(RimContactSurface.Edge)):
            sum += RimContactSurface.Edge[i][4]
        OffsetLeftRight = int(sum / len(RimContactSurface.Edge))

    # print 'OffsetLR', OffsetLeftRight

    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(RimContactSurface.Edge):
            # for j in range(len(RimContactSurface.Edge)):
            if RimContactSurface.Edge[j][4] < OffsetLeftRight:
                newEL = RimContactSurface.Edge[j][4] + i * OffsetSector
                face = Change3DFace(RimContactSurface.Edge[j][3])
                fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=RIC_L\n"])
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(RimContactSurface.Edge):
            # for j in range(len(RimContactSurface.Edge)):
            if RimContactSurface.Edge[j][4] > OffsetLeftRight:
                newEL = RimContactSurface.Edge[j][4] + i * OffsetSector
                face = Change3DFace(RimContactSurface.Edge[j][3])
                fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1
    ############################################################################################
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=PRESS\n"])
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(PressureSurface.Edge):
            # for j in range(len(PressureSurface.Edge)):
            newEL = PressureSurface.Edge[j][4] + i * OffsetSector
            face = Change3DFace(PressureSurface.Edge[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1

    Ties = []
    i = 0
    while i < len(MasterEdges.Edge):
        # for i in range(len(MasterEdges.Edge)):
        match = 1
        j = 0
        while j < len(TreadElset):
            # for j in range(len(TreadElset)):
            if MasterEdges.Edge[i][2] == TreadElset[j]:
                match = 0
                break
            j += 1
        if match == 1:
            fline.append(['*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (MasterEdges.Edge[i][5] - 2)])
            Ties.append(MasterEdges.Edge[i][5])
            k = 0
            while k < sectors:
                # for k in range(sectors):
                newEL = MasterEdges.Edge[i][4] + k * OffsetSector
                face = Change3DFace(MasterEdges.Edge[i][3])
                fline.append(['%10d, %s\n' % (newEL, face)])
                k += 1
        i += 1
    i = 0
    while i < len(Ties):
        # for i in range(len(Ties)):
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (Ties[i] - 2)])
        j = 0
        while j < len(SlaveEdges.Edge):
            # for j in range(len(SlaveEdges.Edge)):
            if SlaveEdges.Edge[j][5] == Ties[i]:
                k = 0
                while k < sectors:
                    # for k in range(sectors):
                    newEL = SlaveEdges.Edge[j][4] + k * OffsetSector
                    face = Change3DFace(SlaveEdges.Edge[j][3])
                    fline.append(['%10d, %s\n' % (newEL, face)])
                    k += 1
            j += 1
        i += 1
    fline.append(['****************************************************************************************************************\n'])
    fline.append(['****************************************************************************************************************\n'])
    fline.append(['****************************************************************************************************************\n'])

    i = 0
    while i < len(Ties):
        # for i in range(len(Ties)):
        fline.append(['*TIE, NAME=T%d_TIE\n' % (Ties[i] - 2)])
        fline.append(['S%d_TIE, M%d_TIE\n' % (Ties[i] - 2, Ties[i] - 2)])
        i += 1
    del (Ties)

    i = 0
    while i < len(fline):
        f.writelines('%s' % str(fline[i][0]))
        i += 1

    # f.writelines('%s' % str(item[0]) for item in fline)
    f.close()

def Write3DTreadMeshWithC(Mesh3DTread, TreadNode, TreadElement, MasterEdges, SlaveEdges, TreadToRoadSurface, TreadBottom, TreadNumber, OffsetSector, Elset, TreadElset, SectorOption, Div):
    if SectorOption == 1:
        MaxR = 0
        for i in range(len(TreadNode.Node)):
            if TreadNode.Node[i][3] > MaxR:
                MaxR = TreadNode.Node[i][3]
        cir = math.pi * 2 * MaxR
        sectors = int(cir / Div)
        iAngle = (math.pi * 2) / float(sectors)
        print ('* Tread Sectors : %d (Element Length=%5.2fmm, Initial Tire OD = %6.1fmm), Each Sector Angle=%6.4f deg' % (sectors, Div * 1000, MaxR * 2000, iAngle * 180 / math.pi))
    else:
        sectors = int(Div)
        iAngle = (math.pi * 2) / float(sectors)
        print ("* Tread Sectors : %d, Each Sector Angle : %6.4f deg" % (sectors, 360 / float(sectors)))

    Mesh3DTread = Mesh3DTread[:-4]

    tupleNode = ()
    i = 0
    while i < len(TreadNode.Node):
        tupleNode = tupleNode + tuple(TreadNode.Node[i])
        i += 1

    tupleElement = ()
    for i in range(len(TreadElement.Element)):
        tList = []
        for k in range(len(TreadElement.Element[i])):
            if TreadElement.Element[i][k] == '':
                tList.append(0)
            elif k == 5:
                tList.append(1)
            elif k > 6:
                tList.append(0)
            else:
                tList.append(TreadElement.Element[i][k])
        # print tList
        tupleElement = tupleElement + tuple(tList)
    # print TreadElement.Element[0]
    # print tupleElement[0], tupleElement[1],tupleElement[2], tupleElement[3], tupleElement[4], tupleElement[5], tupleElement[6], tupleElement[7], tupleElement[8], tupleElement[9]
    # print sectors, OffsetSector, TreadNumber, len(TreadNode.Node[0]), len(TreadElement.Element[0]), len(TreadElement.Element)

    _islm.CreateTireTread(Mesh3DTread, tupleNode, len(TreadNode.Node[0]), tupleElement, len(TreadElement.Element[0]), OffsetSector, TreadNumber, sectors)

    i = 0
    while i < len(Elset.Elset):
        match = 0
        N = len(TreadElset)
        j = 0
        while j < N:

            if Elset.Elset[i][0] == TreadElset[j]:
                # print Elset.Elset[i][0], TreadElset
                match = 1
                break
            j += 1
        if match == 1:
            list = []
            k = 1
            while k < len(Elset.Elset[i]):
                list.append(Elset.Elset[i][k])
                k += 1
            ElsetName = Elset.Elset[i][0]
            tupleList = tuple(list)

            _islm.WriteTread3DElset(sectors, OffsetSector, TreadNumber, ElsetName, tupleList, Mesh3DTread + '.trd')
        i += 1

    ############################################################################################
    f = open(Mesh3DTread + '.trd', "a")
    fline = []

    Ties = []
    i = 0
    while i < len(MasterEdges.Edge):
        # for i in range(len(MasterEdges.Edge)):
        j = 0
        while j < len(TreadElset):
            # for j in range(len(TreadElset)):
            if MasterEdges.Edge[i][2] == TreadElset[j]:
                fline.append(['*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (MasterEdges.Edge[i][5] - 2)])
                Ties.append(MasterEdges.Edge[i][5])
                k = 0
                while k < sectors:
                    # for k in range(sectors):
                    newEL = MasterEdges.Edge[i][4] + k * OffsetSector + TreadNumber
                    face = Change3DFace(MasterEdges.Edge[i][3])
                    fline.append(['%10d, %s\n' % (newEL, face)])
                    k += 1
            j += 1
        i += 1
    i = 0
    while i < len(Ties):
        # for i in range(len(Ties)):
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (Ties[i] - 2)])
        j = 0
        while j < len(SlaveEdges.Edge):
            # for j in range(len(SlaveEdges.Edge)):
            if SlaveEdges.Edge[j][5] == Ties[i]:
                k = 0
                while k < sectors:
                    # for k in range(sectors):
                    newEL = SlaveEdges.Edge[j][4] + k * OffsetSector + TreadNumber
                    face = Change3DFace(SlaveEdges.Edge[j][3])
                    fline.append(['%10d, %s\n' % (newEL, face)])
                    k += 1
            j += 1
        i += 1
    i = 0
    while i < len(Ties):
        # for i in range(len(Ties)):
        fline.append(['*TIE, NAME=T%d_TIE\n' % (Ties[i] - 2)])
        fline.append(['S%d_TIE, M%d_TIE\n' % (Ties[i] - 2, Ties[i] - 2)])
        i += 1

    del (Ties)
    ############################################################################################

    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=XTRD1001\n'])
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(TreadToRoadSurface.Edge):
            # for j in range(len(TreadRoad.Edge)):
            newEL = TreadToRoadSurface.Edge[j][4] + i * OffsetSector + TreadNumber
            face = Change3DFace(TreadToRoadSurface.Edge[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1

    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=YTIE1001\n'])
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(TreadBottom.Edge):
            # for j in range(len(TreadOut)):
            newEL = TreadBottom.Edge[j][4] + i * OffsetSector + TreadNumber
            face = Change3DFace(TreadBottom.Edge[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1

    fline.append(['*TIE, NAME=TBD2TRD, ADJUST=YES, POSITION TOLERANCE= 0.0001\n'])
    fline.append([' YTIE1001, TIREBODY\n'])
    # f.writelines('%s' % str(item[0]) for item in fline)
    i = 0
    while i < len(fline):
        f.writelines('%s' % str(fline[i][0]))
        i += 1
    f.close()

def Write3DTreadMesh(FileName, TreadNode, TreadElement, MasterEdges, SlaveEdges, TreadRoad, TreadBottom, TreadNumber, SectorOffset, Elset, TreadElset, SectorOption, Div):
    f = open(FileName, "w")
    fline = []
    fline.append(['*TREADPTN_NIDSTART_NIDOFFSET_EIDSTART_EIDOFFSET=10000000, 10000, 10000000, 10000\n'])
    fline.append(['****************************************************************************************************************\n'])
    fline.append(['*NODE\n'])

    if SectorOption == 1:
        MaxR = 0
        for i in range(len(TreadNode.Node)):
            if TreadNode.Node[i][3] > MaxR:
                MaxR = TreadNode.Node[i][3]
        cir = math.pi * 2 * MaxR
        sectors = int(cir / Div)
        iAngle = (math.pi * 2) / float(sectors)
        print ('* Tread Sectors : %d (Element Length=%5.2fmm, Initial Tire OD = %6.1fmm), Each Sector Angle=%6.4f deg' % (sectors, Div * 1000, MaxR * 2000, iAngle * 180 / math.pi))
    else:
        sectors = int(Div)
        iAngle = (math.pi * 2) / float(sectors)
        print ("* Tread Sectors : %d, Each Sector Angle : %6.4f deg" % (sectors, 360 / float(sectors)))

    for i in range(sectors):
        Angle = float(i) * iAngle
        for j in range(len(TreadNode.Node)):
            newNode = TreadNode.Node[j][0] + i * SectorOffset + TreadNumber
            newR = round(TreadNode.Node[j][3] * math.cos(Angle), 8)
            newZ = TreadNode.Node[j][2]
            newX = round(TreadNode.Node[j][3] * math.sin(Angle), 8)
            fline.append(['%9d, %16.6E, %16.6E, %16.6E\n' % (newNode, newX, newZ, newR)])
    fline.append(["****************************************************************************************************************\n"])
    fline.append(['*ELEMENT, TYPE=C3D6\n'])
    for i in range(sectors):
        for j in range(len(TreadElement.Element)):
            if TreadElement.Element[j][6] == 3:
                newEl = TreadElement.Element[j][0] + (i) * SectorOffset + TreadNumber

                if i + 1 == sectors:
                    newN1 = TreadElement.Element[j][1] + TreadNumber
                    newN2 = TreadElement.Element[j][2] + TreadNumber
                    newN3 = TreadElement.Element[j][3] + TreadNumber
                    newN4 = TreadElement.Element[j][1] + (i) * SectorOffset + TreadNumber
                    newN5 = TreadElement.Element[j][2] + (i) * SectorOffset + TreadNumber
                    newN6 = TreadElement.Element[j][3] + (i) * SectorOffset + TreadNumber
                else:
                    newN1 = TreadElement.Element[j][1] + (i + 1) * SectorOffset + TreadNumber
                    newN2 = TreadElement.Element[j][2] + (i + 1) * SectorOffset + TreadNumber
                    newN3 = TreadElement.Element[j][3] + (i + 1) * SectorOffset + TreadNumber
                    newN4 = TreadElement.Element[j][1] + (i) * SectorOffset + TreadNumber
                    newN5 = TreadElement.Element[j][2] + (i) * SectorOffset + TreadNumber
                    newN6 = TreadElement.Element[j][3] + (i) * SectorOffset + TreadNumber
                fline.append(['%9d, %d, %d, %d, %d, %d, %d\n' % (newEl, newN1, newN2, newN3, newN4, newN5, newN6)])
    fline.append(["****************************************************************************************************************\n"])
    fline.append(['*ELEMENT, TYPE=C3D8R\n'])
    for i in range(sectors):
        for j in range(len(TreadElement.Element)):
            if TreadElement.Element[j][6] == 4:
                newEl = TreadElement.Element[j][0] + (i) * SectorOffset + TreadNumber

                if i + 1 == sectors:
                    newN1 = TreadElement.Element[j][1] + TreadNumber
                    newN2 = TreadElement.Element[j][2] + TreadNumber
                    newN3 = TreadElement.Element[j][3] + TreadNumber
                    newN4 = TreadElement.Element[j][4] + TreadNumber
                    newN5 = TreadElement.Element[j][1] + (i) * SectorOffset + TreadNumber
                    newN6 = TreadElement.Element[j][2] + (i) * SectorOffset + TreadNumber
                    newN7 = TreadElement.Element[j][3] + (i) * SectorOffset + TreadNumber
                    newN8 = TreadElement.Element[j][4] + (i) * SectorOffset + TreadNumber
                else:
                    newN1 = TreadElement.Element[j][1] + (i + 1) * SectorOffset + TreadNumber
                    newN2 = TreadElement.Element[j][2] + (i + 1) * SectorOffset + TreadNumber
                    newN3 = TreadElement.Element[j][3] + (i + 1) * SectorOffset + TreadNumber
                    newN4 = TreadElement.Element[j][4] + (i + 1) * SectorOffset + TreadNumber
                    newN5 = TreadElement.Element[j][1] + (i) * SectorOffset + TreadNumber
                    newN6 = TreadElement.Element[j][2] + (i) * SectorOffset + TreadNumber
                    newN7 = TreadElement.Element[j][3] + (i) * SectorOffset + TreadNumber
                    newN8 = TreadElement.Element[j][4] + (i) * SectorOffset + TreadNumber
                fline.append(['%9d, %d, %d, %d, %d, %d, %d, %d, %d\n' % (newEl, newN1, newN2, newN3, newN4, newN5, newN6, newN7, newN8)])

    for i in range(len(TreadElset)):
        for j in range(len(Elset.Elset)):
            if TreadElset[i] == Elset.Elset[j][0]:
                fline.append(["*ELSET, ELSET=" + Elset.Elset[j][0] + "\n"])
                for k in range(sectors):
                    count = 0
                    for m in range(1, len(Elset.Elset[j])):
                        newEL = Elset.Elset[j][m] + k * SectorOffset + TreadNumber
                        count += 1
                        if count % 16 == 0 or count == len(Elset.Elset[j]) - 1:
                            fline.append(["%10d\n" % (newEL)])
                        else:
                            fline.append(["%10d, " % (newEL)])
    ############################################################################################
    Ties = []
    for i in range(len(MasterEdges.Edge)):
        for j in range(len(TreadElset)):
            if MasterEdges.Edge[i][2] == TreadElset[j]:
                fline.append(['*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (MasterEdges.Edge[i][5])])
                Ties.append(MasterEdges.Edge[i][5])
                for k in range(sectors):
                    newEL = MasterEdges.Edge[i][4] + k * SectorOffset + TreadNumber
                    face = Change3DFace(MasterEdges.Edge[i][3])
                    fline.append(['%10d, %s\n' % (newEL, face)])
    for i in range(len(Ties)):
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (Ties[i])])
        for j in range(len(SlaveEdges.Edge)):
            if SlaveEdges.Edge[j][5] == Ties[i]:
                for k in range(sectors):
                    newEL = SlaveEdges.Edge[j][4] + k * SectorOffset + TreadNumber
                    face = Change3DFace(SlaveEdges.Edge[j][3])
                    fline.append(['%10d, %s\n' % (newEL, face)])
    for i in range(len(Ties)):
        fline.append(['*TIE, NAME=T%d_TIE\n' % (Ties[i])])
        fline.append(['S%d_TIE, M%d_TIE\n' % (Ties[i], Ties[i])])

    del (Ties)
    ############################################################################################

    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=XTRD1001\n'])
    for i in range(sectors):
        for j in range(len(TreadRoad.Edge)):
            newEL = TreadRoad.Edge[j][4] + i * SectorOffset + TreadNumber
            face = Change3DFace(TreadRoad.Edge[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])

    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=YTIE1001\n'])
    for i in range(sectors):
        for j in range(len(TreadBottom.Edge)):
            newEL = TreadBottom.Edge[j][4] + i * SectorOffset + TreadNumber
            face = Change3DFace(TreadBottom.Edge[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])

    fline.append(['*TIE, NAME=TBD2TRD, ADJUST=YES, POSITION TOLERANCE= 0.0001\n'])
    fline.append([' YTIE1001, TIREBODY\n'])
    f.writelines('%s' % str(item[0]) for item in fline)
    f.close()

def Write3DBodyMesh(FileName, BodyNode, BodyElement, MasterEdges, SlaveEdges, PressureSurface, RimContactSurface, BodyOut, SectorOffset, OffsetLR, Elset, TreadElset, SectorOption, Div):
    f = open(FileName, "w")
    fline = []

    fline.append(['*TIREBODY_NIDSTART_NIDOFFSET_EIDSTART_EIDOFFSET=      1, %5d,       1, %5d  (FOR TIRE & LAT100 ONLY)\n' % (SectorOffset, SectorOffset)])  # modified(18.03.19)
    fline.append(['****************************************************************************************************************\n'])
    fline.append(['*NODE\n'])

    if SectorOption == 1:
        MaxR = 0
        for i in range(len(BodyNode.Node)):
            if BodyNode.Node[i][3] > MaxR:
                MaxR = BodyNode.Node[i][3]
        cir = math.pi * 2 * MaxR
        sectors = int(cir / Div)
        iAngle = (math.pi * 2) / float(sectors)
        print ('* Body Sectors  : %d (Element Length=%5.2fmm, Initial Body MAX Dia.= %6.1fmm), Each Sector Angle=%6.4f deg' % (sectors, Div * 1000, MaxR * 2000, iAngle * 180 / math.pi))
    else:
        sectors = int(Div)
        iAngle = (math.pi * 2) / float(sectors)
        print ("* Body Sectors : %d,  Each Sector Angle : %6.4f deg" % (sectors, 360 / float(sectors)))

    for i in range(sectors):
        Angle = float(i) * iAngle
        # print '  Angle = ',Angle*180/math.pi, ', ', i*SectorOffset
        for j in range(len(BodyNode.Node)):
            newNode = BodyNode.Node[j][0] + i * SectorOffset
            newR = round(BodyNode.Node[j][3] * math.cos(Angle), 8)
            newZ = BodyNode.Node[j][2]
            newX = round(BodyNode.Node[j][3] * math.sin(Angle), 8)
            fline.append(['%9d, %16.6E, %16.6E, %16.6E\n' % (newNode, newX, newZ, newR)])
            # if BodyNode.Node[j][0] ==1:
            # print '%10d, %15.6E, %15.6E, %15.6E' % (newNode, newX, newZ, newR)

    fline.append(['*ELEMENT, TYPE=M3D4R\n'])
    for i in range(sectors):
        for j in range(len(BodyElement.Element)):
            if BodyElement.Element[j][6] == 2:
                newEl = BodyElement.Element[j][0] + (i) * SectorOffset
                newN1 = BodyElement.Element[j][1] + (i) * SectorOffset
                newN2 = BodyElement.Element[j][2] + (i) * SectorOffset
                if i + 1 == sectors:
                    newN3 = BodyElement.Element[j][2]
                    newN4 = BodyElement.Element[j][1]
                else:
                    newN3 = BodyElement.Element[j][2] + (i + 1) * SectorOffset
                    newN4 = BodyElement.Element[j][1] + (i + 1) * SectorOffset
                fline.append([' %d, %d, %d, %d, %d\n' % (newEl, newN1, newN2, newN3, newN4)])
    fline.append(['*ELEMENT, TYPE=C3D6\n'])
    for i in range(sectors):
        for j in range(len(BodyElement.Element)):
            if BodyElement.Element[j][6] == 3:
                newEl = BodyElement.Element[j][0] + (i) * SectorOffset
                newN1 = BodyElement.Element[j][1] + (i + 1) * SectorOffset
                newN2 = BodyElement.Element[j][2] + (i + 1) * SectorOffset
                newN3 = BodyElement.Element[j][3] + (i + 1) * SectorOffset
                if i + 1 == sectors:
                    newN4 = BodyElement.Element[j][1]
                    newN5 = BodyElement.Element[j][2]
                    newN6 = BodyElement.Element[j][3]
                else:
                    newN4 = BodyElement.Element[j][1] + (i) * SectorOffset
                    newN5 = BodyElement.Element[j][2] + (i) * SectorOffset
                    newN6 = BodyElement.Element[j][3] + (i) * SectorOffset
                fline.append([' %d, %d, %d, %d, %d, %d, %d\n' % (newEl, newN1, newN2, newN3, newN4, newN5, newN6)])

    fline.append(['*ELEMENT, TYPE=C3D8R\n'])
    for i in range(sectors):
        for j in range(len(BodyElement.Element)):
            if BodyElement.Element[j][6] == 4:
                newEl = BodyElement.Element[j][0] + (i) * SectorOffset
                newN1 = BodyElement.Element[j][1] + (i + 1) * SectorOffset
                newN2 = BodyElement.Element[j][2] + (i + 1) * SectorOffset
                newN3 = BodyElement.Element[j][3] + (i + 1) * SectorOffset
                newN4 = BodyElement.Element[j][4] + (i + 1) * SectorOffset
                if i + 1 == sectors:
                    newN5 = BodyElement.Element[j][1]
                    newN6 = BodyElement.Element[j][2]
                    newN7 = BodyElement.Element[j][3]
                    newN8 = BodyElement.Element[j][4]
                else:
                    newN5 = BodyElement.Element[j][1] + (i) * SectorOffset
                    newN6 = BodyElement.Element[j][2] + (i) * SectorOffset
                    newN7 = BodyElement.Element[j][3] + (i) * SectorOffset
                    newN8 = BodyElement.Element[j][4] + (i) * SectorOffset
                fline.append([' %d, %d, %d, %d, %d, %d, %d, %d, %d\n' % (newEl, newN1, newN2, newN3, newN4, newN5, newN6, newN7, newN8)])

    for j in range(len(Elset.Elset)):
        match = 1
        for i in range(len(TreadElset)):
            if TreadElset[i] == Elset.Elset[j][0]:
                match = 0
                break
        if match == 1:
            fline.append(["*ELSET, ELSET=" + Elset.Elset[j][0] + "\n"])
            count = 0
            for k in range(sectors):
                for m in range(1, len(Elset.Elset[j])):
                    newEL = Elset.Elset[j][m] + k * SectorOffset
                    count += 1
                    if count % 16 == 0:
                        fline.append([" %d,\n" % (newEL)])
                    else:
                        fline.append([" %d," % (newEL)])
            if count % 16 != 0:
                fline.append(["\n"])

    fline.append(["*ELSET, ELSET=BD1\n"])
    i = 0
    while i < len(Elset.Elset):
        # for i in range(len(Elset.Elset)):
        if "BEAD" in Elset.Elset[i][0]:
            k = 0
            while k < sectors:
                # for k in range(sectors):
                count = 0
                m = 1
                while m < len(Elset.Elset[i]):
                    # for m in range(1, len(Elset.Elset[i])):
                    newEL = Elset.Elset[i][m] + k * SectorOffset
                    count += 1
                    if count % 16 == 0 or count == len(Elset.Elset[i]) - 1:
                        fline.append(["%d,\n" % (newEL)])
                    else:
                        fline.append(["%d, " % (newEL)])
                    m += 1
                k += 1
        i += 1
    ############################################################################################
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=TIREBODY\n"])
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(BodyOut.Edge):
            # for j in range(len(BodyOut.Edge)):
            newEL = BodyOut.Edge[j][4] + i * SectorOffset
            face = Change3DFace(BodyOut.Edge[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=RIC_R\n"])
    # print 'Offset LR', OffsetLR
    if OffsetLR == 0 or OffsetLR == 1000:
        sum = 0
        for i in range(len(RimContactSurface.Edge)):
            sum += RimContactSurface.Edge[i][4]
        OffsetLR = int(sum / len(RimContactSurface.Edge))

    # print 'Offset LR', OffsetLR

    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(RimContactSurface.Edge):
            # for j in range(len(RimContactSurface.Edge)):
            if RimContactSurface.Edge[j][4] < OffsetLR:
                newEL = RimContactSurface.Edge[j][4] + i * SectorOffset
                face = Change3DFace(RimContactSurface.Edge[j][3])
                fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=RIC_L\n"])
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(RimContactSurface.Edge):
            # for j in range(len(RimContactSurface.Edge)):
            if RimContactSurface.Edge[j][4] > OffsetLR:
                newEL = RimContactSurface.Edge[j][4] + i * SectorOffset
                face = Change3DFace(RimContactSurface.Edge[j][3])
                fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1
    ############################################################################################
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=PRESS\n"])
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(PressureSurface.Edge):
            # for j in range(len(PressureSurface.Edge)):
            newEL = PressureSurface.Edge[j][4] + i * SectorOffset
            face = Change3DFace(PressureSurface.Edge[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            j += 1
        i += 1

    Ties = []
    i = 0
    while i < len(MasterEdges.Edge):
        # for i in range(len(MasterEdges.Edge)):
        match = 1
        j = 0
        while j < len(TreadElset):
            # for j in range(len(TreadElset)):
            if MasterEdges.Edge[i][2] == TreadElset[j]:
                match = 0
                break
            j += 1
        if match == 1:
            fline.append(['*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (MasterEdges.Edge[i][5] - 2)])
            Ties.append(MasterEdges.Edge[i][5])
            k = 0
            while k < sectors:
                # for k in range(sectors):
                newEL = MasterEdges.Edge[i][4] + k * SectorOffset
                face = Change3DFace(MasterEdges.Edge[i][3])
                fline.append(['%10d, %s\n' % (newEL, face)])
                k += 1
        i += 1
    i = 0
    while i < len(Ties):
        # for i in range(len(Ties)):
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (Ties[i] - 2)])
        j = 0
        while j < len(SlaveEdges.Edge):
            # for j in range(len(SlaveEdges.Edge)):
            if SlaveEdges.Edge[j][5] == Ties[i]:
                k = 0
                while k < sectors:
                    # for k in range(sectors):
                    newEL = SlaveEdges.Edge[j][4] + k * SectorOffset
                    face = Change3DFace(SlaveEdges.Edge[j][3])
                    fline.append(['%10d, %s\n' % (newEL, face)])
                    k += 1
            j += 1
        i += 1
    fline.append(['****************************************************************************************************************\n'])
    fline.append(['****************************************************************************************************************\n'])
    fline.append(['****************************************************************************************************************\n'])

    i = 0
    while i < len(Ties):
        # for i in range(len(Ties)):
        fline.append(['*TIE, NAME=T%d_TIE\n' % (Ties[i] - 2)])
        fline.append(['S%d_TIE, M%d_TIE\n' % (Ties[i] - 2, Ties[i] - 2)])
        i += 1
    del (Ties)

    i = 0
    while i < len(fline):
        f.writelines('%s' % str(fline[i][0]))
        i += 1

    # f.writelines('%s' % str(item[0]) for item in fline)
    f.close()

##//////////////////////////////////////