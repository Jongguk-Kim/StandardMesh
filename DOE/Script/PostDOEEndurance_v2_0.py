#file : PostBeltSEDValue.py
#Created by SH Kim
#Create 2015/06/18
#Modified by YS Yoon
#Modify 2018/05/31
#Version 4.0
#Details : Migration to ISLM Version

# *******************************************************************
#    Import library                                                  
# *******************************************************************
import sys, string, math, linecache, os, glob, json, time
import multiprocessing as mp 
#import pickle                                                        
from odbAccess import *                                              
from abaqusConstants import *

try:
    import CheckExecution
except:
    pass

#####################################################################
def Distance(fx,fy,fz,lx,ly,lz):
    xd = lx-fx
    yd = ly-fy
    zd = lz-fz
    dist = math.sqrt(xd*xd + yd*yd +zd*zd)
    return dist
    
def BinarySearch(NODE, tmpNode, low, high):
    mid = 0
    while low<=high:
        m = low+high
        m = m/2
        if tmpNode < NODE[m].nodeLabel:
            high = m-1
        elif tmpNode > NODE[m].nodeLabel:
            low = m+1
        else:
            mid = m
            return mid
    return -1
    
def sort_on(list_to_sort, field_num):
    templist = [ (item[field_num], item) for item in list_to_sort ]
    templist.sort()
    return [ item[1] for item in templist ]


def CalKT(strJobDir, simcode, rev): 
    # f=open("end err.txt", "w")
    path = strJobDir+'/'+ simcode+ '-3DKT.odb'
    # f.write(path)
    # f.close()
    odb = openOdb(path) 
    
    stp='Step-4'

    Last_RF = 0
    lastFrame = odb.steps[stp].frames[-1]

    RF_Value = lastFrame.fieldOutputs['RF']
    NFLANGE = odb.rootAssembly.instances['PART-1-1'].nodeSets['NFLANGE']
    NFLANGE_RF = RF_Value.getSubset(region=NFLANGE)
    NFLANGE_Values = NFLANGE_RF.values
    for v in NFLANGE_Values:
        Last_RF+=v.data[2]
    NodeSets = odb.rootAssembly.instances['PART-1-1'].nodeSets.keys()
    for v in NodeSets:
        if(v == 'BDR'):
            BDR = odb.rootAssembly.instances['PART-1-1'].nodeSets['BDR']
            BDR_RF = RF_Value.getSubset(region=BDR)
            BDR_Values = BDR_RF.values
            for v in BDR_Values:
                Last_RF+=v.data[2]
    Last_RF=Last_RF/9.81

    Last_U = 0
    U_Value = lastFrame.fieldOutputs['U']
    NROAD = odb.rootAssembly.instances['PART-1-1'].nodeSets['NROAD']
    NROAD_RF = U_Value.getSubset(region=NROAD)
    NROAD_Values = NROAD_RF.values
    for v in NROAD_Values:
        Last_U = -v.data[2]*1000
    First_RF = 0
    FirstFrame = odb.steps[stp].frames[0]
    RF_Value = FirstFrame.fieldOutputs['RF']
    NFLANGE = odb.rootAssembly.instances['PART-1-1'].nodeSets['NFLANGE']
    NFLANGE_RF = RF_Value.getSubset(region=NFLANGE)
    NFLANGE_Values = NFLANGE_RF.values
    for v in NFLANGE_Values:
        First_RF+=v.data[2]
    NodeSets = odb.rootAssembly.instances['PART-1-1'].nodeSets.keys()
    for v in NodeSets:
        if(v == 'BDR'):
            BDR = odb.rootAssembly.instances['PART-1-1'].nodeSets['BDR']
            BDR_RF = RF_Value.getSubset(region=BDR)
            BDR_Values = BDR_RF.values
            for v in BDR_Values:
                First_RF+=v.data[2]
    First_RF=First_RF/9.81

    First_U = 0
    U_Value = FirstFrame.fieldOutputs['U']
    NROAD = odb.rootAssembly.instances['PART-1-1'].nodeSets['NROAD']
    NROAD_RF = U_Value.getSubset(region=NROAD)
    NROAD_Values = NROAD_RF.values
    for v in NROAD_Values:
        First_U = -v.data[2]*1000

    RF = Last_RF-First_RF
    U  = Last_U-First_U

    KT = RF/U
    Value = [RF, U, KT]

    dispFile = open(strJobDir + '/' + simcode+ '-Endurance.txt','a')
    dispFile.writelines('%s, RF_Traction (kgf)=\t%f\n' % (rev, Value[0]))
    dispFile.writelines('%s, Travel Direction Displacement (mm)=\t%f\n' % (rev, Value[1]))
    dispFile.writelines('%s, Tractional Stiffness (kgf/mm)=\t%f\n' % (rev, Value[2]))
    dispFile.close()
    
    dispFile = open(strJobDir + '/' + simcode+ '-3DKT-Stiff.txt','w')
    dispFile.writelines('********************************************************************************\n')
    dispFile.writelines('***** TORSIONAL STIFFNESS RESULT ***********************************************\n')
    dispFile.writelines('********************************************************************************\n')
    dispFile.writelines('RF(kgf)=\t%f\n' % (Value[0]))
    dispFile.writelines('U(mm)=\t%f\n' % (Value[1]))
    dispFile.writelines('TStiff(kgf/mm)=\t%f\n' % (Value[2]))
    dispFile.writelines('\n')
    dispFile.writelines('\n')
    dispFile.writelines('Success::Post::[Simulation Result] This simulation result was created successfully!!\n')
    
    # dispFile.writelines('RF(kgf)= %f\n' % (Value[0]))
    # dispFile.writelines('U(mm)=	%f\n' % (Value[1]))
    # dispFile.writelines('TStiff(kgf/mm)= %f\n' % (Value[2]))
    # dispFile.writelines("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!!")
    dispFile.close()
    odb.close()
    print ('RF(kgf)= %f\n' % (Value[0]))

def CalKV(strJobDir, simcode, rev): 
    path = strJobDir+'/'+ simcode+  '-3DKV.odb'
    odb = openOdb(path)  
    stp = 'Step-5'
    Last_RF = 0
    lastFrame = odb.steps[stp].frames[-1]

    RF_Value = lastFrame.fieldOutputs['RF']
    NFLANGE = odb.rootAssembly.instances['PART-1-1'].nodeSets['NFLANGE']
    NFLANGE_RF = RF_Value.getSubset(region=NFLANGE)
    NFLANGE_Values = NFLANGE_RF.values
    for v in NFLANGE_Values:
        Last_RF+=v.data[0]
    NodeSets = odb.rootAssembly.instances['PART-1-1'].nodeSets.keys()
    for v in NodeSets:
        if(v == 'BDR'):
            BDR = odb.rootAssembly.instances['PART-1-1'].nodeSets['BDR']
            BDR_RF = RF_Value.getSubset(region=BDR)
            BDR_Values = BDR_RF.values
            for v in BDR_Values:
                Last_RF+=v.data[0]
    Last_RF=Last_RF/9.81

    Last_U = 0
    U_Value = lastFrame.fieldOutputs['U']
    NROAD = odb.rootAssembly.instances['PART-1-1'].nodeSets['NROAD']
    NROAD_RF = U_Value.getSubset(region=NROAD)
    NROAD_Values = NROAD_RF.values
    for v in NROAD_Values:
        Last_U = -v.data[0]*1000
    First_RF = 0
    FirstFrame = odb.steps[stp].frames[0]
    RF_Value = FirstFrame.fieldOutputs['RF']
    NFLANGE = odb.rootAssembly.instances['PART-1-1'].nodeSets['NFLANGE']
    NFLANGE_RF = RF_Value.getSubset(region=NFLANGE)
    NFLANGE_Values = NFLANGE_RF.values
    for v in NFLANGE_Values:
        First_RF+=v.data[0]
    NodeSets = odb.rootAssembly.instances['PART-1-1'].nodeSets.keys()
    for v in NodeSets:
        if(v == 'BDR'):
            BDR = odb.rootAssembly.instances['PART-1-1'].nodeSets['BDR']
            BDR_RF = RF_Value.getSubset(region=BDR)
            BDR_Values = BDR_RF.values
            for v in BDR_Values:
                First_RF+=v.data[0]
    First_RF=First_RF/9.81

    First_U = 0
    U_Value = FirstFrame.fieldOutputs['U']
    NROAD = odb.rootAssembly.instances['PART-1-1'].nodeSets['NROAD']
    NROAD_RF = U_Value.getSubset(region=NROAD)
    NROAD_Values = NROAD_RF.values
    for v in NROAD_Values:
        First_U = -v.data[0]*1000

    RF = Last_RF-First_RF
    U  = Last_U-First_U
    
    KV = RF/U
    Value = [RF, U, KV]

    # dispFile.writelines('%s, RF_Vertical (kgf)=\t%f\n' % (rev, Value[0]))
    # dispFile.writelines('%s, Vertical Displacement (mm)=\t%f\n' % (rev, Value[1]))
    # dispFile.writelines('%s, Vertical Stiffness (kgf/mm)=\t%f\n' % (rev, Value[2]))
    # dispFile.close()

    line = str(rev) + ", RF_Vertical (kgf)=" + str(Value[0]) + "\n"
    line += str(rev) + ", Vertical Displacement (mm)=" + str(Value[1]) + "\n"
    line += str(rev) + ", Vertical Stiffness (kgf/mm)=" + str(Value[2]) + "\n"
    
    dispFile = open(strJobDir + '/' + simcode+ '-Endurance.txt','a')
    dispFile.writelines(line)
    dispFile.close()
    
    dispFile = open(strJobDir + '/' + simcode+ '-3DKV-Stiff.txt','w')
    dispFile.writelines('********************************************************************************\n')
    dispFile.writelines('***** VERTICAL STIFFNESS RESULT ************************************************\n')
    dispFile.writelines('********************************************************************************\n')
    dispFile.writelines('RF(kgf)=\t%f\n' % (Value[0]))
    dispFile.writelines('U(mm)=\t%f\n' % (Value[1]))
    dispFile.writelines('VStiff(kgf/mm)=\t%f\n' % (Value[2]))
    dispFile.writelines('\n')
    dispFile.writelines('\n')
    dispFile.writelines('Success::Post::[Simulation Result] This simulation result was created successfully!!\n')
    # dispFile.writelines('RF(kgf)= %f\n' % (Value[0]))
    # dispFile.writelines('U(mm)=	%f\n' % (Value[1]))
    # dispFile.writelines('VStiff(kgf/mm)=	%f\n' % (Value[2]))
    # dispFile.writelines("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!")
    dispFile.close()

    odb.close()

def CalKL(strJobDir, simcode, rev): 
    path = strJobDir+'/'+ simcode+  '-3DKL.odb'
    odb = openOdb(path) 

    stp='Step-5' 

    Last_RF = 0
    lastFrame = odb.steps[stp].frames[-1]

    RF_Value = lastFrame.fieldOutputs['RF']
    NFLANGE = odb.rootAssembly.instances['PART-1-1'].nodeSets['NFLANGE']
    NFLANGE_RF = RF_Value.getSubset(region=NFLANGE)
    NFLANGE_Values = NFLANGE_RF.values
    for v in NFLANGE_Values:
        Last_RF+=v.data[1]
    NodeSets = odb.rootAssembly.instances['PART-1-1'].nodeSets.keys()
    for v in NodeSets:
        if(v == 'BDR'):
            BDR = odb.rootAssembly.instances['PART-1-1'].nodeSets['BDR']
            BDR_RF = RF_Value.getSubset(region=BDR)
            BDR_Values = BDR_RF.values
            for v in BDR_Values:
                Last_RF+=v.data[1]
    Last_RF=Last_RF/9.81

    Last_U = 0
    U_Value = lastFrame.fieldOutputs['U']
    NROAD = odb.rootAssembly.instances['PART-1-1'].nodeSets['NROAD']
    NROAD_RF = U_Value.getSubset(region=NROAD)
    NROAD_Values = NROAD_RF.values
    for v in NROAD_Values:
        Last_U = -v.data[1]*1000
    First_RF = 0
    FirstFrame = odb.steps[stp].frames[0]
    RF_Value = FirstFrame.fieldOutputs['RF']
    NFLANGE = odb.rootAssembly.instances['PART-1-1'].nodeSets['NFLANGE']
    NFLANGE_RF = RF_Value.getSubset(region=NFLANGE)
    NFLANGE_Values = NFLANGE_RF.values
    for v in NFLANGE_Values:
        First_RF+=v.data[1]
    NodeSets = odb.rootAssembly.instances['PART-1-1'].nodeSets.keys()
    for v in NodeSets:
        if(v == 'BDR'):
            BDR = odb.rootAssembly.instances['PART-1-1'].nodeSets['BDR']
            BDR_RF = RF_Value.getSubset(region=BDR)
            BDR_Values = BDR_RF.values
            for v in BDR_Values:
                First_RF+=v.data[1]
    First_RF=First_RF/9.81

    First_U = 0
    U_Value = FirstFrame.fieldOutputs['U']
    NROAD = odb.rootAssembly.instances['PART-1-1'].nodeSets['NROAD']
    NROAD_RF = U_Value.getSubset(region=NROAD)
    NROAD_Values = NROAD_RF.values
    for v in NROAD_Values:
        First_U = -v.data[1]*1000
    
    RF = Last_RF-First_RF
    U  = Last_U-First_U

    KL = RF/U
    Value = [RF, U, KL]

    # dispFile.writelines('%s, RF_Lateral (kgf)=\t%f\n' % (rev, Value[0]))
    # dispFile.writelines('%s, Lateral Displacement (mm)=\t%f\n' % (rev, Value[1]))
    # dispFile.writelines('%s, Lateral Stiffness (kgf/mm)=\t%f\n' % (rev, Value[2]))
    # dispFile.close()

    line = str(rev) + ", RF_Lateral (kgf)=" + str(Value[0]) + "\n"
    line += str(rev) + ", Lateral Displacement (mm)=" + str(Value[1]) + "\n"
    line += str(rev) + ", Lateral Stiffness (kgf/mm)=" + str(Value[2]) + "\n"
    
    dispFile = open(strJobDir + '/' + simcode+ '-Endurance.txt','a')
    dispFile.writelines(line)
    dispFile.close()
    
    dispFile = open(strJobDir + '/' + simcode+ '-3DKL-Stiff.txt','w')
    dispFile.writelines('********************************************************************************\n')
    dispFile.writelines('***** LATERAL STIFFNESS RESULT *************************************************\n')
    dispFile.writelines('********************************************************************************\n')
    dispFile.writelines('RF(kgf)=\t%f\n' % (Value[0]))
    dispFile.writelines('U(mm)=\t%f\n' % (Value[1]))
    dispFile.writelines('LStiff(kgf/mm)=\t%f\n' % (Value[2]))
    dispFile.writelines('\n')
    dispFile.writelines('\n')
    dispFile.writelines('Success::Post::[Simulation Result] This simulation result was created successfully!!\n')

    # dispFile.writelines('RF(kgf)= %f\n' % (Value[0]))
    # dispFile.writelines('U(mm)=	%f\n' % (Value[1]))
    # dispFile.writelines('LStiff(kgf/mm)=	%f\n' % (Value[2]))
    # dispFile.writelines("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!")
    dispFile.close()
    
    odb.close()

def CalKD(strJobDir, simcode, rev): 
    path = strJobDir+'/'+ simcode+   '-3DKD.odb'
    odb = openOdb(path) 
    
    stp='Step-5'

    Last_RF = 0
    lastFrame = odb.steps[stp].frames[-1]

    RF_Value = lastFrame.fieldOutputs['RM']
    NFLANGE = odb.rootAssembly.instances['PART-1-1'].nodeSets['NFLANGE']
    NFLANGE_RF = RF_Value.getSubset(region=NFLANGE)
    NFLANGE_Values = NFLANGE_RF.values
    for v in NFLANGE_Values:
        Last_RF+=v.data[0]
    NodeSets = odb.rootAssembly.instances['PART-1-1'].nodeSets.keys()
    for v in NodeSets:
        if(v == 'BDR'):
            BDR = odb.rootAssembly.instances['PART-1-1'].nodeSets['BDR']
            BDR_RF = RF_Value.getSubset(region=BDR)
            BDR_Values = BDR_RF.values
            for v in BDR_Values:
                Last_RF+=v.data[0]
    Last_RF=Last_RF/9.81

    Last_U = 0
    U_Value = lastFrame.fieldOutputs['UR']
    NROAD = odb.rootAssembly.instances['PART-1-1'].nodeSets['NROAD']
    NROAD_RF = U_Value.getSubset(region=NROAD)
    NROAD_Values = NROAD_RF.values
    for v in NROAD_Values:
        Last_U = -v.data[0]
    First_RF = 0
    FirstFrame = odb.steps[stp].frames[0]
    RF_Value = FirstFrame.fieldOutputs['RM']
    NFLANGE = odb.rootAssembly.instances['PART-1-1'].nodeSets['NFLANGE']
    NFLANGE_RF = RF_Value.getSubset(region=NFLANGE)
    NFLANGE_Values = NFLANGE_RF.values
    for v in NFLANGE_Values:
        First_RF+=v.data[0]
    NodeSets = odb.rootAssembly.instances['PART-1-1'].nodeSets.keys()
    for v in NodeSets:
        if(v == 'BDR'):
            BDR = odb.rootAssembly.instances['PART-1-1'].nodeSets['BDR']
            BDR_RF = RF_Value.getSubset(region=BDR)
            BDR_Values = BDR_RF.values
            for v in BDR_Values:
                First_RF+=v.data[0]
    First_RF=First_RF/9.81

    First_U = 0
    U_Value = FirstFrame.fieldOutputs['UR']
    NROAD = odb.rootAssembly.instances['PART-1-1'].nodeSets['NROAD']
    NROAD_RF = U_Value.getSubset(region=NROAD)
    NROAD_Values = NROAD_RF.values
    for v in NROAD_Values:
        First_U = -v.data[0]

    RF = Last_RF-First_RF
    U  = Last_U-First_U

    KD = RF/U
    Value = [RF, U, KD]

    dispFile = open(strJobDir + '/' + simcode+ '-Endurance.txt','a')
    # dispFile.writelines('%s, RM_Distortion (kgf*m)=\t%f\n' % (rev, Value[0]))
    # dispFile.writelines('%s, Torsional Displacement (rad)=\t%f\n' % (rev, Value[1]))
    # dispFile.writelines('%s, Tortional Stiffness (kgf*m/rad)=\t%f\n' % (rev, Value[2]))

    line = str(rev) + ", RM_Distortion (kgf*m)=" + str(Value[0]) + "\n"
    line += str(rev) + ", Torsional Displacement (degree)=" + str(Value[1]) + "\n"
    line += str(rev) + ", Tortional Stiffness (kgf*m/degree)=" + str(Value[2]) + "\n"
    dispFile = open(strJobDir + '/' + simcode+ '-Endurance.txt','a')
    dispFile.writelines(line)
    dispFile.close()
    
    dispFile = open(strJobDir + '/' + simcode+ '-3DKD-Stiff.txt','w')
    dispFile.writelines('********************************************************************************\n')
    dispFile.writelines('***** DISTORTIONAL STIFFNESS RESULT ******************************************\n')
    dispFile.writelines('********************************************************************************\n')
    dispFile.writelines('RM(kgf*m)=\t%f\n' % (Value[0]))
    dispFile.writelines('UR(rad)=\t%f\n' % (Value[1]))
    dispFile.writelines('DStiff(kgf*mm/rad)=\t%f\n' % (Value[2]))
    dispFile.writelines('\n')
    dispFile.writelines('\n')
    dispFile.writelines('Success::Post::[Simulation Result] This simulation result was created successfully!!\n')
    dispFile.close()
    
    
    odb.close()

def CalENDU(strJobDir, simcode, rev): 
    path = strJobDir+'/'+ simcode+ '-3DST.odb'
    odb = openOdb(path)                                                  
    
    #####################################################################
    
    NODE1 = []
    NODE2 = []
    Coord=odb.steps['Step-3'].frames[-1].fieldOutputs['COORD']
    CoordValue = Coord.values
    if strProductLine == 'PCR':
        BT2 = odb.rootAssembly.instances['PART-1-1'].elementSets['BT2']
    elif strProductLine == 'LTR':
        BT2 = odb.rootAssembly.instances['PART-1-1'].elementSets['BT2']
    elif strProductLine == 'TBR':
        BT2 = odb.rootAssembly.instances['PART-1-1'].elementSets['BT3']
    else:
        BT2 = odb.rootAssembly.instances['PART-1-1'].elementSets['BT2']  
    
    BT2El = BT2.elements
    BT2LAST = []
    strBT1=''
    strBT2=''
    for element in BT2El:
        if element.label < OFFSET:
            firstN=element.connectivity[0]
            LastN=element.connectivity[1]
            BT2LAST.append(LastN)
    #print BT2LAST
    if strProductLine == 'TBR':
        BT1 = odb.rootAssembly.instances['PART-1-1'].elementSets['BT2']
        BT2 = odb.rootAssembly.instances['PART-1-1'].elementSets['BT3']
        strBT1='BT2'
        strBT2='BT3'
    else:
        BT1 = odb.rootAssembly.instances['PART-1-1'].elementSets['BT1']
        BT2 = odb.rootAssembly.instances['PART-1-1'].elementSets['BT2']
        strBT1='BT1'
        strBT2='BT2'

    BT1El = BT1.elements
    BT1LAST = []
    for element in BT1El:
        if element.label < OFFSET:
            firstN=element.connectivity[0]
            LastN=element.connectivity[1]
            BT1LAST.append(LastN)
    BT2El = BT2.elements
    BT2LAST = []
    for element in BT2El:
        if element.label < OFFSET:
            firstN = element.connectivity[0]
            LastN = element.connectivity[1]
            BT2LAST.append(LastN)
    #print BT1LAST
    #print BT2LAST[len(BT2LAST)-1]
    #print BT1LAST[len(BT1LAST)-1]
    #print BT1LAST[len(BT2LAST)-1]

    TotalSector = 0
    
    SENER = odb.steps['Step-3'].frames[-1].fieldOutputs['SENER']

    ElementSet = 'BTT'
    BELTSED = odb.rootAssembly.instances['PART-1-1'].elementSets[ElementSet]
    SEDNOD = SENER.getSubset(region=BELTSED, position=ELEMENT_NODAL, elementType="C3D8H")
    values = SEDNOD.values
    for v in values:
        if v.nodeLabel % SectorOffset == BT1LAST[len(BT1LAST) - 1]:
            NODE1.append([v.nodeLabel, v.data, ElementSet])
            if TotalSector < v.nodeLabel:
                TotalSector = v.nodeLabel
        if v.nodeLabel % SectorOffset == BT2LAST[len(BT2LAST) - 1]:
            NODE2.append([v.nodeLabel, v.data, ElementSet])
    SEDNOD = SENER.getSubset(region=BELTSED, position=ELEMENT_NODAL, elementType="CCL12H")
    values = SEDNOD.values
    for v in values:
        if v.nodeLabel % SectorOffset == BT1LAST[len(BT1LAST) - 1]:
            NODE1.append([v.nodeLabel, v.data, ElementSet])
        if v.nodeLabel % SectorOffset == BT2LAST[len(BT2LAST) - 1]:
            NODE2.append([v.nodeLabel, v.data, ElementSet])
            
    TotalSector = TotalSector / SectorOffset

    

    BT1Max = 0
    BT1Min = 1000000.0
    BT1Max_N = 0
    BT1Min_N = 0
    BT2Max = 0
    BT2Min = 10000000.0
    BT2Max_N = 0
    BT2Min_N = 0

    BT1SED=[]
    BT2SED=[]

    for i in range(TotalSector + 1):
        sumSED1 = 0
        cntSED1 = 0
        sumSED2 = 0
        cntSED2 = 0

        for j in range(len(NODE1)):
            if BT1LAST[len(BT1LAST)-1] + i*SectorOffset == NODE1[j][0]:
                sumSED1 += NODE1[j][1]
                cntSED1 += 1
        for j in range(len(NODE2)):
            if BT2LAST[len(BT2LAST)-1] + i*SectorOffset == NODE2[j][0]:
                sumSED2 += NODE2[j][1]
                cntSED2 += 1

        try :
            AvgSED1 = sumSED1 / float(cntSED1)
        except:
            dispFile.writelines("** %s %d has No Value\n" %(strBT1, BT1LAST[len(BT1LAST)-1] + i*SectorOffset) )
        else:
            BT1SED.append([BT1LAST[len(BT1LAST)-1] + i*SectorOffset, AvgSED1])
            if BT1Max < AvgSED1:
                BT1Max = AvgSED1
                BT1Max_N = BT1LAST[len(BT1LAST)-1] + i*SectorOffset
            if BT1Min > AvgSED1:
                BT1Min = AvgSED1
                BT1Min_N = BT1LAST[len(BT1LAST) - 1] + i * SectorOffset
        AvgSED2=0
        try :
            AvgSED2 = sumSED2 / float(cntSED2)
        except:
            dispFile.writelines("** %s %d has No Value\n" %(strBT2, BT2LAST[len(BT2LAST)-1] + i*SectorOffset) )
        else:
            BT2SED.append([BT2LAST[len(BT2LAST)-1] + i*SectorOffset, AvgSED2])
            if BT2Max < AvgSED2:
                BT2Max = AvgSED2
                BT2Max_N = BT2LAST[len(BT2LAST) - 1] + i * SectorOffset
            if BT2Min > AvgSED2:
                BT2Min = AvgSED2
            BT2Min_N = BT2LAST[len(BT2LAST) - 1] + i * SectorOffset
    
    # dispFile.writelines('%s, %sMaxNodeNumber=\t%d\n' % (rev, strBT2, BT2Max_N))
    # dispFile.writelines('%s, %sMaxSED(MPa)=\t%f\n' % (rev, strBT2, float((BT2Max) * (1E-6))))
    # dispFile.writelines('%s, %sMinNodeNumber=\t%d\n' % (rev, strBT2, BT2Min_N))
    # dispFile.writelines('%s, %sMinSED(MPa)=\t%f\n' % (rev, strBT2, float((BT2Min) * (1E-6))))
    # dispFile.writelines('%s, %sSEDAmplitude(MPa)=\t%f\n' % (rev, strBT2, float((BT2Max) * (1E-6))- float((BT2Min) * (1E-6))))
    
    ##########################################################################################################
    ######### DONE WITH BELT 
    ##########################################################################################################
    BSW = odb.rootAssembly.instances['PART-1-1'].elementSets['BSW']  
    BSWPOS = odb.steps['Step-3'].frames[-1].fieldOutputs['LE']
    BSWELNODE = BSWPOS.getSubset(region=BSW, position=ELEMENT_NODAL, elementType = 'C3D8H')
    fieldValues = BSWELNODE.values
    NODE=[]
    for v in fieldValues:
        if v.elementLabel < SectorOffset:
            NODE.append(v.nodeLabel)
    i = 0
    SortNOD = []
    while i < len(NODE):
        if i == 0: SortNOD.append(NODE[i])
        else:
            j = 0; cnt = 0
            while j < i:
                if i != j: 
                    if NODE[i] == NODE[j]: cnt = -1
                j = j + 1
            if cnt != -1: SortNOD.append(NODE[i])
        i = i + 1
    SortNOD.sort()
    del NODE
    
    c = 0
    M = len(SortNOD)
    BSWPLE = []
    
    for m in range(M):
        PLE= []
        for v in fieldValues:
            if v.nodeLabel % SectorOffset == SortNOD[m]:
                if c == 0:  
                    PLE.append([ v.nodeLabel, v.maxPrincipal, 1])
                else:
                    f = 0
                    I = len(PLE)
                    for i in range(I): 
                        if PLE[i][0] == v.nodeLabel:
                            PLE[i][1] += v.maxPrincipal
                            PLE[i][2] += 1
                            f =1
                            break
                    if f == 0:
                        PLE.append([ v.nodeLabel, v.maxPrincipal, 1])
                        c += 1
        
                        
    
        I = len(PLE)
        if I == 0: continue
        max = PLE[0][1] / float(PLE[0][2])
        min = PLE[0][1] / float(PLE[0][2])
        for i in range(I):
            PLE[i][1] = PLE[i][1] / float(PLE[i][2])
            if PLE[i][1] > max:
                max = PLE[i][1]
            if PLE[i][1] < min:
                min = PLE[i][1]
        
        AmpPLE =abs(max - min)
        
        if abs(max) < abs(min):
            max = min
            
        BSWPLE.append([ SortNOD[m], max, AmpPLE])
        
    del(SortNOD)
    
    M = len(BSWPLE)
    Bmxnd = BSWPLE[0][0]
    Bampnd = BSWPLE[0][0]
    Bmaxvalue = BSWPLE[0][1]
    Bmaxamp = BSWPLE[0][2]
    for i in range(M):
        # dispFile.writelines("PLE: %d, %f, %f\n"%(BSWPLE[i][0], BSWPLE[i][1], BSWPLE[i][2]))
        if abs(Bmaxvalue) < abs(BSWPLE[i][1]):
            Bmaxvalue = BSWPLE[i][1]
            Bmxnd = BSWPLE[i][0]
        if Bmaxamp < BSWPLE[i][2]:
            Bmaxamp = BSWPLE[i][2]
            Bampnd = BSWPLE[i][0]
            
    
    
        
    ###########################################################################
    ##### DONE WITH BSW 
    ###########################################################################
    if strProductLine == 'PCR':
        BDF = odb.rootAssembly.instances['PART-1-1'].elementSets['FIL']
    elif strProductLine == 'LTR':
        BDF = odb.rootAssembly.instances['PART-1-1'].elementSets['FIL']
    elif strProductLine == 'TBR':
        BDF = odb.rootAssembly.instances['PART-1-1'].elementSets['UBF']
    else:
        BDF = odb.rootAssembly.instances['PART-1-1'].elementSets['FIL']  
        
    BDFPOS = odb.steps['Step-3'].frames[-1].fieldOutputs['S']
    BDFELNODE = BDFPOS.getSubset(region=BDF, position=ELEMENT_NODAL, elementType = 'C3D8H')
    fieldValues = BDFELNODE.values
    NODE = []
    for v in fieldValues:
        if v.elementLabel < SectorOffset:
            if v.nodeLabel < SectorOffset:
                NODE.append(v.nodeLabel)
    i = 0
    SortNOD = []
    while i < len(NODE):
        if i == 0: SortNOD.append(NODE[i])
        else:
            j = 0; cnt = 0
            while j < i:
                if i != j: 
                    if NODE[i] == NODE[j]: cnt = -1
                j = j + 1
            if cnt != -1: SortNOD.append(NODE[i])
        i = i + 1
    SortNOD.sort()
    del NODE
    
    
    c = 0
    M = len(SortNOD)
    FILLERTRESCA = []
    
    for m in range(M):
        TRESCA= []
        for v in fieldValues:
            if v.nodeLabel % SectorOffset == SortNOD[m]:
                if c == 0:  
                    TRESCA.append([ v.nodeLabel, v.tresca, 1])
                else:
                    f = 0
                    I = len(TRESCA)
                    for i in range(I): 
                        if TRESCA[i][0] == v.nodeLabel:
                            TRESCA[i][1] += v.tresca
                            TRESCA[i][2] += 1
                            f =1
                            break
                    if f == 0:
                        TRESCA.append([ v.nodeLabel, v.tresca, 1])
                        c += 1
        
                        
    
        I = len(TRESCA)
        if I == 0: continue
        max = TRESCA[0][1] / float(TRESCA[0][2])
        min = TRESCA[0][1] / float(TRESCA[0][2])
        for i in range(I):
            TRESCA[i][1] = TRESCA[i][1] / float(TRESCA[i][2])
            if TRESCA[i][1] > max:
                max = TRESCA[i][1]
            if TRESCA[i][1] < min:
                min = TRESCA[i][1]
        
        AmpTRESCA =abs(max - min)
        
        if abs(max) < abs(min):
            max = min
            
        FILLERTRESCA.append([ SortNOD[m], max, AmpTRESCA])
        
    del(SortNOD)
    
    M = len(FILLERTRESCA)
    mxnd = FILLERTRESCA[0][0]
    ampnd = FILLERTRESCA[0][0]
    maxvalue = FILLERTRESCA[0][1]
    maxamp = FILLERTRESCA[0][2]
    for i in range(M):
        ## dispFile.writelines("PLE: %d, %f, %f\n"%(FILLERTRESCA[i][0], FILLERTRESCA[i][1], FILLERTRESCA[i][2]))
        if abs(maxvalue) < abs(FILLERTRESCA[i][1]):
            maxvalue = FILLERTRESCA[i][1]
            mxnd = FILLERTRESCA[i][0]
        if maxamp < FILLERTRESCA[i][2]:
            maxamp = FILLERTRESCA[i][2]
            ampnd = FILLERTRESCA[i][0]
    
    
    
    # dispFile = open(strJobDir + '/' + simcode+ '-3DST-BTSEDValue.txt','w')
    # dispFile.writelines('%s, %s BT SED Max NodeNumber=\t%d\n' % (rev, strBT1, BT1Max_N))
    # dispFile.writelines('%s, %s BT SED Max Value(MPa)=\t%f\n' % (rev, strBT1, float((BT1Max) * (1E-6))))
    # dispFile.writelines('%s, %s BT SED Min NodeNumber=\t%d\n' % (rev, strBT1, BT1Min_N))
    # dispFile.writelines('%s, %s BT SED Min Value(MPa)=\t%f\n' % (rev, strBT1, float((BT1Min) * (1E-6))))
    
    # dispFile.writelines('%s, %s BT SED Amplitude(MPa)=\t%f\n' % (rev, strBT1, float((BT1Max) * (1E-6))- float((BT1Min) * (1E-6))))
    
    # dispFile.writelines('%s, BSW Value Node Number=\t%d\n' % (rev, mxnd))
    # dispFile.writelines('%s, BSW PLE Max Value=\t%f\n' %(rev, maxvalue))
    # dispFile.writelines('%s, BSW Amplitude Node Number=\t%d\n' % (rev, ampnd))
    # dispFile.writelines('%s, BSW PLE Amplitude=\t%f\n' %(rev, maxamp))

    # dispFile.writelines('%s, Filler Value Node Number=\t%d\n' % (rev, mxnd))
    # dispFile.writelines('%s, Filler Tresca Max Value(MPa)=\t%f\n' %(rev, maxvalue/1000000.0))
    # dispFile.writelines('%s, Filler Amplitude Node Number=\t%d\n' % (rev, ampnd))
    # dispFile.writelines('%s, Filler Tresca Amplitude(MPa)=\t%f\n' %(rev, maxamp/1000000.0))
    # dispFile.close()

    line  = str(rev)+', ' + strBT1 + " BT SED Max NodeNumber= " + str(BT1Max_N) + "\n"
    line += str(rev)+', ' + strBT1 + " BT SED Max Value(kJ/m3)= " + str(float((BT1Max) * (1E-3))) + "\n"
    line += str(rev)+', ' + strBT1 + " BT SED Min NodeNumber== " + str(BT1Min_N) + "\n"
    line += str(rev)+', ' + strBT1 + " BT SED Min Value(kJ/m3)= " + str(float((BT1Min) * (1E-3))) + "\n"
    line += str(rev)+', ' + strBT1 + " BT SED Amplitude(kJ/m3)= " + str(float((BT1Max) * (1E-3))- float((BT1Min) * (1E-3))) + "\n"

    line += str(rev)+', ' + "Filler Value Node Number=" + str(mxnd) + "\n"
    line += str(rev)+', ' + "Filler Tresca Max Value(MPa)=" + str(maxvalue/1000000.0) + "\n"
    line += str(rev)+', ' + "Filler Amplitude Node Number=" + str(ampnd) + "\n"
    line += str(rev)+', ' + "Filler Tresca Amplitude(MPa)=" + str(maxamp/1000000.0) + "\n"

    line += str(rev)+', ' + "BSW Value Node Number=" + str(Bmxnd) + "\n"
    line += str(rev)+', ' + "BSW PLE Max Value=" + str(Bmaxvalue) + "\n"
    line += str(rev)+', ' + "BSW Amplitude Node Number=" + str(Bampnd) + "\n"
    line += str(rev)+', ' + "BSW PLE Amplitude=" + str(Bmaxamp) + "\n"

    dispFile = open(strJobDir + '/' + simcode+ '-Endurance.txt','a')
    dispFile.writelines(line)
    dispFile.close()
    odb.close()
#####################################################################

if __name__ == "__main__":

    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass

    tstart = time.time()
    OFFSET = 2000   # left vs right side of the section
    SectorOffset = 4000
    
    
    strJobDir = os.getcwd()
    snss = glob.glob(strJobDir+"/*.sns")
    strSnsFileName = snss[0]
    with open(strSnsFileName) as data_file:
        jsSns = json.load(data_file)
        
    strSimCode = str(jsSns["AnalysisInformation"]["SimulationCode"])
    strProductLine = str(jsSns["VirtualTireBasicInfo"]["ProductLine"])
    strProductLocation = str(jsSns["VirtualTireBasicInfo"]["VirtualTireDBLocation"])
    strProductLocation = strSimCode.split('-')[0]
    
    nameendu = 'S104'

    # Write Odb file name   
    # strSimCode = strJobDir.split("/")[-1]
    dispFile = open(strJobDir + '/' + strSimCode+ '-Endurance.txt','w')
    dispFile.close()
    
    rev = strSimCode.split("/")[-1].split("-")[2]
    
    processes = []
    p = mp.Process(target=CalENDU, args=[strJobDir, strSimCode, rev])
    processes.append(p)
    p.start()

    p = mp.Process(target=CalKV, args=[strJobDir, strSimCode, rev])
    processes.append(p)
    p.start()

    p = mp.Process(target=CalKT, args=[strJobDir, strSimCode, rev])
    processes.append(p)
    p.start()

    p = mp.Process(target=CalKL, args=[strJobDir, strSimCode, rev])
    processes.append(p)
    p.start()

    p = mp.Process(target=CalKD, args=[strJobDir, strSimCode, rev])
    processes.append(p)
    p.start()


    for process in processes: 
        process.join()

    
    
    tend=time.time()
    print ("Duration - Endurance", tend-tstart)
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass








