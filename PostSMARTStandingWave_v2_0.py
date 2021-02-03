# *******************************************************************
#    Import library
# *******************************************************************
import os, glob, json, time, sys
import CommonFunction as TIRE
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import math
try:
    import CheckExecution
except: 
    pass 
########################################################################################################################
"""
Simulation Time = 0.25 / 0.35 (The same with RR)
Output Time Step = 0.01 sec 
Temperature control  = 1 (Start Time > 0.25)
No Lateral, Rotation Control
Rim Diameter = 1.707 (The same with RR)
Road Friction (The Same with RR) :  3.125, 0.44, 0.38, 0.34, 0.46, 8.68, 0.55, 2.94
User Input : Pressure, Load, Ground Speed, RW, Camber Angle can ba applied 
"""
########################################################################################################################
if __name__ == "__main__":
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass 

    debug = 0
    t0 = time.time()
    
    strSimCode = ""; str2DInp=""; TireGroup="PCR"
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i].split("=")
        if arg[0] == "smart" or arg[0] == "s":
            strSimCode = arg[1]
            if ".inp" in strSimCode:
                strSimCode = strSimCode[:-4]
        if arg[0] == "mesh" or arg[0] == "m":
            str2DInp = arg[1]
            if not ".inp" in str2DInp:
                str2DInp += ".inp"
        if arg[0] == "group" or arg[0] == "g":
            TireGroup = arg[1]
    
    strJobDir = os.getcwd()
    if strSimCode == "":
        lstSmartFileNames = glob.glob(strJobDir + '/*.sns')
        strSmartFileName = lstSmartFileNames[0]
        strSmartInpFIleName = strSmartFileName[:-4] + '.inp'
        
        tmpList = list(strSmartInpFIleName.split('/'))
        tmpList = list(tmpList[-1].split('-'))
        for i in range(len(tmpList)):
            if 'VT' in tmpList[i]: 
                str2DInp = strJobDir + '/' + tmpList[i] + '-' + tmpList[i+1] +'.inp'
                break

        with open(strSmartFileName) as Sns_file:
            lstSnsInfo = json.load(Sns_file)

        strSimCode = lstSnsInfo["AnalysisInformation"]["SimulationCode"]
        TireGroup = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]
        
        
    ##################################################################################################################### 

    SimTime = TIRE.SIMTIME(strSimCode+'.inp')
    SimCondition=TIRE.CONDITION(strSimCode+'.inp')
    
    strErrFileName = strSimCode + '.err'
    err=open(strErrFileName, 'w')
    try:
        Node, Element, Elset, Comment = TIRE.Mesh2DInformation(str2DInp)
    except:
        line = "ERROR::POST::[STANDINGWAVE] - Cannot open 2D Mesh File (VT-Code.inp)+\n"
        err.writelines(line)
        err.close()
        try:
            CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        except:
            pass 
        sys.exit()
    ###################################
    
    
    if SimTime.SimulationTime == 0.0:
        strSDBDir = strJobDir + '/' + 'SDB_PCI.' + strSimCode
        sdbFileName = strJobDir + '/' + 'SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
        sfricFileName = strJobDir + '/' + 'SFRIC_PCI.' + strSimCode + '/' + strSimCode + '.sfric'
    else:
        strSDBDir = strJobDir + '/' + 'SDB.' + strSimCode
        sdbFileName = strJobDir + '/' + 'SDB.' + strSimCode + '/' + strSimCode + '.sdb'
        sfricFileName = strJobDir + '/' + 'SFRIC.' + strSimCode + '/' + strSimCode + '.sfric'

    strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))
    strLastSFRICFile =  sfricFileName + str(format(SimTime.LastStep, '03'))
    Offset =10000
    TreadNo = 10000000
    
    LeftWave, RightWave, DLW = TIRE.Plot_LoadedTireProfile(strSimCode, sdbFileName,  strLastSDBFile, SimCondition, offset=Offset, Tread=TreadNo, sidewave=1, mesh=str2DInp, dpi=200)
    #######################################################################################
    # DLR
    #######################################################################################
    if SimCondition.Drum !=0:
        RimNode = TIRE.GetRimCenter()
        DrumNode = TIRE.GetDrumCenter()
        Rigid=TIRE.NODE()
        Rigid.Add(RimNode.Node[0])
        Rigid.Add(DrumNode.Node[0])
        Distance = TIRE.NodeDistance(RimNode.Node[0][0], DrumNode.Node[0][0], Rigid) 
        # distance from Rim Center to Drum Center
        DLR = (Distance - float(SimCondition.Drum)/2.0)
    else:
        allnodes = TIRE.ResultSDB(sdbFileName, strLastSDBFile, Offset, TreadNo, 1, 0)
        I= len(allnodes.Node)
        MinZ = 9.9E20
        for i in range(I):
            if MinZ > allnodes.Node[i][3]:
                MinZ = allnodes.Node[i][3]
        RimNode = TIRE.GetRimCenter()
        DLR = abs(RimNode.Node[0][3]-MinZ)
    ########################################################################################
    #######################################################################################
    # DRR
    ######################################################################################
    if SimCondition.Drum !=0:
        DRR = TIRE.CalculateDRR(strSimCode)
    else:
        DRR = TIRE.CalculateDRROnRoad(strSimCode)
    print ('* Dynamic Dimension  ')
    print (" DLR = %.2f, DRR = %.2f, DLW = %.2f"%(DLR*1000, DRR*1000, DLW*1000))
    
    #######################################################################################
    # Temperature 
    #######################################################################################
    TNode = TIRE.ResultSDB(sdbFileName, strLastSDBFile, Offset, TreadNo, 1, -2)
    if debug ==1 : print ("Temperature reading from SDB done")
    TNode.Rotate(SimCondition.Camber, xy=23, xc=RimNode.Node[0][2], yc=RimNode.Node[0][3])
    TNode.Rotate(-SimCondition.SlipAngle, xy=21, xc=RimNode.Node[0][2], yc=RimNode.Node[0][1])
    N = len(TNode.Node)
    MinZ = 9.9E20
    MaxZ = -9.9E20
    for i in range(N):
        TNode.Node[i][0] = TNode.Node[i][0] % Offset
        if MinZ > TNode.Node[i][3]:
            MinZ = TNode.Node[i][3]
        if MaxZ < TNode.Node[i][3]:
            MaxZ = TNode.Node[i][3]
    SWz= (MinZ+MaxZ)/2.0
    MaxBeltT = 0.0
    MaxBeadT = 0.0
    for i in range(N):
        if TNode.Node[i][4]>MaxBeltT and TNode.Node[i][3] > SWz:
            MaxBeltT = TNode.Node[i][4]
        if TNode.Node[i][4]>MaxBeadT and TNode.Node[i][3] < SWz:
            MaxBeadT = TNode.Node[i][4]
            maxBdNode = TNode.Node[i]
    if debug ==1 : print (" Max Temperature Belt =%f, Bead %f"%(MaxBeltT, MaxBeadT))
    TIRE.Plot_TemperatureDotting(strSimCode+'-Temperature', TNode, Element)
    # TIRE.Plot_TemperatureContour(strSimCode+'-Temperature', TNode, Element)
    #######################################################################################
    # Write Results 
    #######################################################################################
    f= open(strSimCode+'-StandingWave.txt', "w")

    line = 'Wave Amplitude Max at SW Left Node [mm] = ' + str(format(LeftWave[0], '.3f')) + '\n'
    f.writelines(line)
    line = 'Wave Amplitude 2nd Wave at SW Left Node [mm] = ' + str(format(LeftWave[1], '.3f')) + '\n'
    f.writelines(line)
    line = 'Wave Amplitude 3rd Wave at SW Left Node [mm] = '  + str(format(LeftWave[2], '.3f')) + '\n'
    f.writelines(line)

    line = 'Wave Amplitude Max at SW Right Node [mm] = ' + str(format(RightWave[0], '.3f')) + '\n'
    f.writelines(line)
    line = 'Wave Amplitude 2nd Wave at SW Right Node [mm] = ' + str(format(RightWave[1], '.3f')) + '\n'
    f.writelines(line)
    line = 'Wave Amplitude 3rd Wave at SW Right Node [mm] = '  + str(format(RightWave[2], '.3f')) + '\n'
    f.writelines(line)

    line = 'Max Inner Temperature Crown = '  + str(format(MaxBeltT, '.2f') )  + '\n'
    f.writelines(line)
    line = 'Max Inner Temperature Bead = '  + str(format(MaxBeadT, '.2f') ) + '\n'
    f.writelines(line)

    line = 'SDW_DLR = '  + str(format(DLR*1000, '.2f') ) + '\n'
    f.writelines(line)
    line = 'SDW_DLW = '  + str(format(DLW*1000, '.2f') ) + '\n'
    f.writelines(line)
    line = 'SDW_DRR = '  + str(format(DRR*1000, '.2f') ) + '\n'
    f.writelines(line)
    
    line = '\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!' + '\n\n'
    f.writelines(line)
    
    f.close()
    err.close()


    fittingorder = 6
    TIRE.PlotFootprint(strSimCode, strLastSDBFile, strLastSFRICFile, group=TireGroup, mesh2d= str2DInp, iter=1, step =0, offset=Offset, \
        treadno=TreadNo, dpi=150, ribimage=0, vmin='', doe=0, fitting=fittingorder, ribgraph=0, simcondition=SimCondition)
    
    os.system('rm -f *.tmp')
    os.system('rm -f *Value.txt')

    t1 = time.time()
    # print "Duration :", t1 - t0, "sec"
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass 

    







