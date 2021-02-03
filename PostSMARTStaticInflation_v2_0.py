# *******************************************************************
#    Import library
# *******************************************************************
import os, glob, json, sys
# import sys, string, struct, math
import time, math, CheckExecution
import CommonFunction as TIRE

def GetDeformedNodeClassFromSMARTResult(NodeFile, SectorOffset=10000, TreadNumber=10000000):
    tNode = TIRE.NODE()
    with open(NodeFile) as InpFile:
        lines = InpFile.readlines()

    for data in lines:
        line = list(data.split(','))
        if int(line[0]) < SectorOffset:
            tNode.Add([int(line[0]), float(line[1]) + float(line[4]), float(line[2]) + float(line[5]), float(line[3]) + float(line[6].strip())])

        if int(line[0]) > TreadNumber and (int(line[0]) - TreadNumber) < SectorOffset:
            tNode.Add([int(line[0]) - TreadNumber, float(line[1]) + float(line[4]), float(line[2]) + float(line[5]), float(line[3]) + float(line[6].strip())])
    tNode.DeleteDuplicate()
    return tNode

def GetODSW(DimValueFile):
    with open(DimValueFile) as InpFile:
        lines = InpFile.readlines()
    ODSW = [0.0, 0.0]
    for l in lines:
        data = list(l.split('='))
        if 'Deformed OD' in data[0]:
            ODSW[0] = float(data[1].strip())
        if 'Deformed SW' in data[0]:
            ODSW[1] = float(data[1].strip())
    return ODSW
########################################################################################################################
########################################################################################################################
if __name__ == "__main__":
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass 

    t0 = time.time()
    offset = 10000
    treadno = 10000000
    strJobDir = os.getcwd()
    lstSmartFileNames = glob.glob(strJobDir + '/*.sns')
    strSmartFileName = lstSmartFileNames[0]

    with open(strSmartFileName) as Sns_file:
        lstSnsInfo = json.load(Sns_file)

    strSimCode = lstSnsInfo["AnalysisInformation"]["SimulationCode"]  # Simulation Code from 'SNS' File
    strSimCode = strSmartFileName.split('/')[-1][:-4]  # from 'SNS' File Name
    strSimGroup = strSimCode.split('-')[-2]  # Simulation Group : D10? .. form Simulation Code
    wList = strSimCode.split('-')
    str2DInp =strJobDir + '/' + wList[1] + '-' + wList[2] + '.inp'

    strProductLine = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]  # TBR/LTR/PCR
    TreadDesignWidth = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"])  # Mold TW
    OverallDiamter = float(lstSnsInfo["VirtualTireParameters"]["OverallDiameter"])  # Mold OD


    sdbFileName = ''
    sfricResultFileName = ''
    # errFileName = strSimCode + '.err'
    # err = open(errFileName, 'w')  # Create ERROR check file 'SimulationCode.err'

    #######################################################################
    # Sub Folder and SMART INP File Names
    #######################################################################
    subFolderBasicName = 'IF'
    subFolderSerialDigit = '03'  # SUB Folder : ./IF001~IF009
    subFileBasicName = '-IF'
    subFileSerialDigit = '03'  # SMART INP FILE NAME : ./IF001/RND-1000000VT00001-0-D10x-001-IF001.inp
    ######################################################################

    TotalSimNoPCR = 9  # No of Simulations, PCR 9
    TotalSimNoTBR = 6  # TBR/LTR 6

    subFolderName = subFolderBasicName + '001'
    subFileName = strSimCode + subFileBasicName + '001'
    SmartInpFileName001 = strJobDir + '/' + subFolderName + '/' + subFileName + '.inp'

    # ResultStep, EndTime = GetSimSteps(SmartInpFileName001)
    SimTime = TIRE.SIMTIME(SmartInpFileName001)
    strResultStep = str(format(SimTime.LastStep, '03'))

    #######################################################################
    # Variables to open SFRIC result file
    #######################################################################
    NodeOffset = TIRE.STATIC(10000)
    TreadNumber = TIRE.STATIC(10000000)
    ResultSector = 1  # Results from 1st Sector
    ResultItem = 1  # Results of Node Coordinates
    ResultContactPressure = 81  # Results of Contact Pressure
    #######################################################################
    # Read Pressure and RW Information from SMART Input files (~.inp)
    #######################################################################
    SimulationPressure = []  # Buffer for Pressure
    SimulationRimWidth = []  # Buffer for RW
    if strProductLine == 'PCR':
        SimulationRun = TotalSimNoPCR
    else: 
        SimulationRun = TotalSimNoTBR
    for i in range(1, SimulationRun + 1):
        Serial = str(format(i, subFolderSerialDigit))
        subFolderName = subFolderBasicName + Serial
        Serial = str(format(i, subFileSerialDigit))
        subFileName = strSimCode + subFileBasicName + Serial

        SmartInpFileName = strJobDir + '/' + subFolderName + '/' + subFileName + '.inp'
        Condition = TIRE.CONDITION(SmartInpFileName)
        SimulationPressure.append(Condition.Pressure)
        SimulationRimWidth.append(Condition.RimWidth)
    #######################################################################
    # for i in range(len(SimulationRimWidth)):
    #     print "RIM WIDTH ", i, '=', SimulationRimWidth

    ##################################################################################################
    ## DEFORMED SHAPE COMPARISON
    #
    # SurfaceNodePosition1.tmp Data format
    # 313,       1635,       1637, 0.000000E+00,    9.752745E-02,    2.295368E-01, 0.000000E+00,    9.479543E-02,    2.292978E-01, 1
    # faceID,    Node1,     Node2, Node1-Coord1, Node1-Coord2(X), Node1-Coord3(Z), Node2-Coord1, Node2-Coord2(X), Node2-Coord3(Z), OuterSurfaceID (1=Yes, 0=No)
    ##################################################################################################

    ##############################################################################################################################################################################################
    ## Deformed Shape Comparison versus RIM CHANGE (The Same Pressure)
    ################################################################################################################################################################################################
    Node, Element, Elset, Comments = TIRE.Mesh2DInformation(str2DInp)
    
    outeredge = Element.OuterEdge(Node)
    oedge = TIRE.EDGE()
    for edge in outeredge.Edge:
        if edge[2] == "CTR" or edge[2] == "CTB" or edge[2] == "UTR" or edge[2] == "SUT" or edge[2] == "BSW" or edge[2] == "TRW":
            oedge.Add(edge)

    print ('Runs - %d'%(SimulationRun))
    NodePositionFileName=[]
    SurfacePostionFileName = []
    ImageDPI = 200
    ODSW=[]
    sdbs=[]
    sfrics=[]
    for i in range(1, SimulationRun+1):
        Serial = str(format(i, subFolderSerialDigit))
        subFolderName = subFolderBasicName + Serial
        Serial = str(format(i, subFileSerialDigit))
        subFileName = strSimCode + subFileBasicName + Serial
        if SimTime.SimulationTime == 0.0:
            SDBFileName = strJobDir + '/' + subFolderName + '/SDB_PCI.' + subFileName + '/' + subFileName + '.sdb'
            SDBLastFileName = strJobDir + '/' + subFolderName + '/SDB_PCI.' + subFileName + '/' + subFileName + '.sdb' + strResultStep
            sdbs.append(SDBLastFileName)
            SFRICFileName = strJobDir + '/' + subFolderName + '/SFRIC_PCI.' + subFileName + '/' + subFileName + '.sfric'
            SFRICLastFileName = strJobDir + '/' + subFolderName + '/SFRIC_PCI.' + subFileName + '/' + subFileName + '.sfric' + strResultStep
            sfrics.append(SFRICLastFileName)
        else:
            SDBFileName = strJobDir + '/' + subFolderName + '/SDB.' + subFileName + '/' + subFileName + '.sdb'
            SDBLastFileName = strJobDir + '/' + subFolderName + '/SDB.' + subFileName + '/' + subFileName + '.sdb' + strResultStep
            sdbs.append(SDBLastFileName)
            SFRICFileName = strJobDir + '/' + subFolderName + '/SFRIC.' + subFileName + '/' + subFileName + '.sfric'
            SFRICLastFileName = strJobDir + '/' + subFolderName + '/SFRIC.' + subFileName + '/' + subFileName + '.sfric' + strResultStep
            sfrics.append(SFRICLastFileName)

    UnitToInch = 0.0393701

    TN = TIRE.ResultSDB(sdbs[0][:-3], sdbs[0], offset, treadno, 1, 0)
    mx, nx = 0.0, 0.0
    for N in TN.Node:
        if N[3] < nx:
            nx = N[3]
        if N[3] > mx:
            mx = N[3]
    iod = mx-nx
    N1 = TIRE.ResultSDB(sdbs[0][:-3], sdbs[0], offset, treadno, 1, -1)
    mz = 0
    for inode in N1.Node:
        if mz < inode[3]:
            mz = inode[3]
    if iod/2.0 != mz:
        movez = iod/2.0 - mz
        for inode in N1.Node:
            inode[3] += movez
    for n in N1.Node:
        n[0] = n[0] % treadno
        n[1] = 0.0
        n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
    od, sw=TIRE.GetODSWfromDeformedNode(N1, Element, Node, 1, offset, treadno, mesh=1, option=1)
    ODSW.append([od, sw])
        
    TN = TIRE.ResultSDB(sdbs[1][:-3], sdbs[1], offset, treadno, 1, 0)
    mx, nx = 0.0, 0.0
    for N in TN.Node:
        if N[3] < nx:
            nx = N[3]
        if N[3] > mx:
            mx = N[3]
    iod = mx-nx
    N2 = TIRE.ResultSDB(sdbs[1][:-3], sdbs[1], offset, treadno, 1, -1)
    mz = 0
    for inode in N2.Node:
        if mz < inode[3]:
            mz = inode[3]
    if iod/2.0 != mz:
        movez = iod/2.0 - mz
        for inode in N2.Node:
            inode[3] += movez
    for n in N2.Node:
        n[0] = n[0] % treadno
        n[1] = 0.0
        n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
    od, sw=TIRE.GetODSWfromDeformedNode(N2, Element, Node, 1, offset, treadno, mesh=1, option=1)
    ODSW.append([od, sw])
    
    TN = TIRE.ResultSDB(sdbs[2][:-3], sdbs[2], offset, treadno, 1, 0)
    mx, nx = 0.0, 0.0
    for N in TN.Node:
        if N[3] < nx:
            nx = N[3]
        if N[3] > mx:
            mx = N[3]
    iod = mx-nx
    N3 = TIRE.ResultSDB(sdbs[2][:-3], sdbs[2], offset, treadno, 1, -1)
    mz = 0
    for inode in N3.Node:
        if mz < inode[3]:
            mz = inode[3]
    if iod/2.0 != mz:
        movez = iod/2.0 - mz
        for inode in N3.Node:
            inode[3] += movez
    for n in N3.Node:
        n[0] = n[0] % treadno
        n[1] = 0.0
        n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
    od, sw=TIRE.GetODSWfromDeformedNode(N3, Element, Node, 1, offset, treadno, mesh=1, option=1)
    ODSW.append([od, sw])
    
    TN = TIRE.ResultSDB(sdbs[3][:-3], sdbs[3], offset, treadno, 1, 0)
    mx, nx = 0.0, 0.0
    for N in TN.Node:
        if N[3] < nx:
            nx = N[3]
        if N[3] > mx:
            mx = N[3]
    iod = mx-nx
    N4 = TIRE.ResultSDB(sdbs[3][:-3], sdbs[3], offset, treadno, 1, -1)
    mz = 0
    for inode in N4.Node:
        if mz < inode[3]:
            mz = inode[3]
    if iod/2.0 != mz:
        movez = iod/2.0 - mz
        for inode in N4.Node:
            inode[3] += movez
    for n in N4.Node:
        n[0] = n[0] % treadno
        n[1] = 0.0
        n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
    od, sw=TIRE.GetODSWfromDeformedNode(N4, Element, Node, 1, offset, treadno, mesh=1, option=1)
    ODSW.append([od, sw])
    
    TN = TIRE.ResultSDB(sdbs[4][:-3], sdbs[4], offset, treadno, 1, 0)
    mx, nx = 0.0, 0.0
    for N in TN.Node:
        if N[3] < nx:
            nx = N[3]
        if N[3] > mx:
            mx = N[3]
    iod = mx-nx

    N5 = TIRE.ResultSDB(sdbs[4][:-3], sdbs[4], offset, treadno, 1, -1)  

    mz = 0
    for inode in N5.Node:
        if mz < inode[3]:
            mz = inode[3]

    if iod/2.0 != mz:
        movez = iod/2.0 - mz
        for inode in N5.Node:
            inode[3] += movez
        
    for n in N5.Node:
        n[0] = n[0] % treadno
        n[1] = 0.0
        n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
    od, sw=TIRE.GetODSWfromDeformedNode(N5, Element, Node, 1, offset, treadno, mesh=1, option=1)
    ODSW.append([od, sw])
    
    TN = TIRE.ResultSDB(sdbs[5][:-3], sdbs[5], offset, treadno, 1, 0)
    mx, nx = 0.0, 0.0
    for N in TN.Node:
        if N[3] < nx:
            nx = N[3]
        if N[3] > mx:
            mx = N[3]
    iod = mx-nx
    N6 = TIRE.ResultSDB(sdbs[5][:-3], sdbs[5], offset, treadno, 1, -1)
    mz = 0
    for inode in N6.Node:
        if mz < inode[3]:
            mz = inode[3]
    if iod/2.0 != mz:
        movez = iod/2.0 - mz
        for inode in N6.Node:
            inode[3] += movez
    for n in N6.Node:
        n[0] = n[0] % treadno
        n[1] = 0.0
        n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
    od, sw=TIRE.GetODSWfromDeformedNode(N6, Element, Node, 1, offset, treadno, mesh=1, option=1)
    ODSW.append([od, sw])
    
    L1 = textline = 'Press : ' + str(SimulationPressure[0]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[0] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[0][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[0][1]*1000, '.1f')) + ')'
    L2 = textline = 'Press : ' + str(SimulationPressure[1]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[1] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[1][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[1][1]*1000, '.1f')) + ')'
    L3 = textline = 'Press : ' + str(SimulationPressure[2]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[2] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[2][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[2][1]*1000, '.1f')) + ')'
    L4 = textline = 'Press : ' + str(SimulationPressure[3]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[3] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[3][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[3][1]*1000, '.1f')) + ')'
    L5 = textline = 'Press : ' + str(SimulationPressure[4]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[4] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[4][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[4][1]*1000, '.1f')) + ')'
    L6 = textline = 'Press : ' + str(SimulationPressure[5]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[5] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[5][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[5][1]*1000, '.1f')) + ')'

    if strProductLine == 'PCR':
        TN = TIRE.ResultSDB(sdbs[6][:-3], sdbs[6], offset, treadno, 1, 0)
        mx, nx = 0.0, 0.0
        for N in TN.Node:
            if N[3] < nx:
                nx = N[3]
            if N[3] > mx:
                mx = N[3]
        iod = mx-nx
        N7 = TIRE.ResultSDB(sdbs[6][:-3], sdbs[6], offset, treadno, 1, -1)
        mz = 0
        for inode in N7.Node:
            if mz < inode[3]:
                mz = inode[3]
        if iod/2.0 != mz:
            movez = iod/2.0 - mz
            for inode in N7.Node:
                inode[3] += movez
        for n in N7.Node:
            n[0] = n[0] % treadno
            n[1] = 0.0
            n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
        od, sw=TIRE.GetODSWfromDeformedNode(N7, Element, Node, 1, offset, treadno, mesh=1, option=1)
        ODSW.append([od, sw])
       
        TN = TIRE.ResultSDB(sdbs[7][:-3], sdbs[7], offset, treadno, 1, 0)
        mx, nx = 0.0, 0.0
        for N in TN.Node:
            if N[3] < nx:
                nx = N[3]
            if N[3] > mx:
                mx = N[3]
        iod = mx-nx
        N8 = TIRE.ResultSDB(sdbs[7][:-3], sdbs[7], offset, treadno, 1, -1)
        mz = 0
        for inode in N8.Node:
            if mz < inode[3]:
                mz = inode[3]
        if iod/2.0 != mz:
            movez = iod/2.0 - mz
            for inode in N8.Node:
                inode[3] += movez
        for n in N8.Node:
            n[0] = n[0] % treadno
            n[1] = 0.0
            n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
        od, sw=TIRE.GetODSWfromDeformedNode(N8, Element, Node, 1, offset, treadno, mesh=1, option=1)
        ODSW.append([od, sw])
        
        TN = TIRE.ResultSDB(sdbs[8][:-3], sdbs[8], offset, treadno, 1, 0)
        mx, nx = 0.0, 0.0
        for N in TN.Node:
            if N[3] < nx:
                nx = N[3]
            if N[3] > mx:
                mx = N[3]
        iod = mx-nx
        N9 = TIRE.ResultSDB(sdbs[8][:-3], sdbs[8], offset, treadno, 1, -1)
        mz = 0
        for inode in N9.Node:
            if mz < inode[3]:
                mz = inode[3]
        if iod/2.0 != mz:
            movez = iod/2.0 - mz
            for inode in N9.Node:
                inode[3] += movez
        for n in N9.Node:
            n[0] = n[0] % treadno
            n[1] = 0.0
            n[3] = math.sqrt(n[1]*n[1]+n[3]*n[3])
        od, sw=TIRE.GetODSWfromDeformedNode(N9, Element, Node, 1, offset, treadno, mesh=1, option=1)
        ODSW.append([od, sw])
        
        L7 = textline = 'Press : ' + str(SimulationPressure[6]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[6] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[6][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[6][1]*1000, '.1f')) + ')'
        L8 = textline = 'Press : ' + str(SimulationPressure[7]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[7] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[7][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[7][1]*1000, '.1f')) + ')'
        L9 = textline = 'Press : ' + str(SimulationPressure[8]) + ' kgf/cm2, RW : ' + str(format(SimulationRimWidth[8] * UnitToInch, '.2f'))  + '" (OD =' + str(format(ODSW[8][0]*1000, '.1f')) + ', SW= ' + str(format(ODSW[8][1]*1000, '.1f')) + ')'

    ProfileGrowthFileName = strSimCode + '-ProfileGrowthStaticInflation.txt'
    f = open(ProfileGrowthFileName, 'w')
    textline = '* Outer Profile Lift in the Vertical direction\n'
    f.write(textline)
    textline = '* Distance from Crown Center, Lift[mm]\n'
    f.write(textline)

    CrownGrowthFileName = strSimCode + '-CrownGrowthStaticInflation.txt'
    fc = open(CrownGrowthFileName, 'w')
    textline = '* Crown Lift in the Vertical direction\n'
    fc.write(textline)
    textline = '* Distance from Crown Center, Lift[mm]\n'
    fc.write(textline)

    if strProductLine == 'PCR':
        ImageFileName = strSimCode + '-RimChangePress1.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N1, N2, ImageDPI, N3, L1, L2, L3)
        ImageFileName = strSimCode + '-RimChangePress2.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N4, N5, ImageDPI, N6, L4, L5, L6)
        ImageFileName = strSimCode + '-RimChangePress3.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N7, N8, ImageDPI, N9, L7, L8, L9)

        ImageFileName = strSimCode + '-PressureChangeRW1.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N1, N4, ImageDPI, N7, L1, L4, L7)
        ImageFileName = strSimCode + '-PressureChangeRW2.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N2, N5, ImageDPI, N8, L2, L5, L8)
        ImageFileName = strSimCode + '-PressureChangeRW3.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N3, N6, ImageDPI, N9, L3, L6, L9)

        Sim = [SimulationRimWidth[0], SimulationPressure[0], SimulationPressure[3], SimulationPressure[6]]
        Fname = [N1, N4, N7]
        ## oedge : outer edge (ctb, sut, bsw)
        ImageFileName = strSimCode + '-ProfileGrowthRW1.png'
        ProfileLift, CrownLift = TIRE.Plot_ProfileLiftStaticInflation(ImageFileName, TreadDesignWidth, 5.0, Fname, Sim, Offset=NodeOffset.value, TreadNumber=TreadNumber.value, group='pcr', edge=oedge)
        N = len(ProfileLift)
        for i in range(N):
            textline = '*' + ProfileLift[i][0] + '\n'
            f.write(textline)
            M = len(ProfileLift[i])
            for j in range(1, M):
                textline = str(format(ProfileLift[i][j][0], '.6f')) + ', ' + str(ProfileLift[i][j][1]) + '\n'
                f.write(textline)

        N = len(CrownLift)
        for i in range(N):
            textline = '*' + CrownLift[i][0] + '\n'
            fc.write(textline)
            M = len(CrownLift[i])
            for j in range(1, M):
                textline = str(format(CrownLift[i][j][0], '.6f')) + ', ' + str(CrownLift[i][j][1]) + '\n'
                fc.write(textline)

        Sim = [SimulationRimWidth[1], SimulationPressure[1], SimulationPressure[4], SimulationPressure[7]]
        Fname = [N2, N5, N8]
        ImageFileName = strSimCode + '-ProfileGrowthRW2.png'
        ProfileLift, CrownLift = TIRE.Plot_ProfileLiftStaticInflation(ImageFileName, TreadDesignWidth, 5.0, Fname, Sim, Offset=NodeOffset.value, TreadNumber=TreadNumber.value, group='pcr', edge=oedge)
        N = len(ProfileLift)
        for i in range(N):
            textline = '*' + ProfileLift[i][0] + '\n'
            f.write(textline)
            M = len(ProfileLift[i])
            for j in range(1, M):
                textline = str(format(ProfileLift[i][j][0], '.6f')) + ', ' + str(ProfileLift[i][j][1]) + '\n'
                f.write(textline)

        N = len(CrownLift)
        for i in range(N):
            textline = '*' + CrownLift[i][0] + '\n'
            fc.write(textline)
            M = len(CrownLift[i])
            for j in range(1, M):
                textline = str(format(CrownLift[i][j][0], '.6f')) + ', ' + str(CrownLift[i][j][1]) + '\n'
                fc.write(textline)

        Sim = [SimulationRimWidth[2], SimulationPressure[2], SimulationPressure[5], SimulationPressure[8]]
        Fname = [N3, N6, N9]
        ImageFileName = strSimCode + '-ProfileGrowthRW3.png'
        ProfileLift, CrownLift = TIRE.Plot_ProfileLiftStaticInflation(ImageFileName, TreadDesignWidth, 5.0, Fname, Sim, Offset=NodeOffset.value, TreadNumber=TreadNumber.value, group='pcr', edge=oedge)
        N = len(ProfileLift)
        for i in range(N):
            textline = '*' + ProfileLift[i][0] + '\n'
            f.write(textline)
            M = len(ProfileLift[i])
            for j in range(1, M):
                textline = str(format(ProfileLift[i][j][0], '.6f')) + ', ' + str(ProfileLift[i][j][1]) + '\n'
                f.write(textline)

        N = len(CrownLift)
        for i in range(N):
            textline = '*' + CrownLift[i][0] + '\n'
            fc.write(textline)
            M = len(CrownLift[i])
            for j in range(1, M):
                textline = str(format(CrownLift[i][j][0], '.6f')) + ', ' + str(CrownLift[i][j][1]) + '\n'
                fc.write(textline)

        DummyList = []
        DummyRimcontactImage = strSimCode + '-RimContactPressRW1.png'
        TIRE.Plot_XYList(DummyRimcontactImage, DummyList, '', 'Not Supported in SMART-PCI', '', '', 100)
        DummyRimcontactImage = strSimCode + '-RimContactPressRW2.png'
        TIRE.Plot_XYList(DummyRimcontactImage, DummyList, '', 'Not Supported in SMART-PCI', '', '', 100)
        DummyRimcontactImage = strSimCode + '-RimContactPressRW3.png'
        TIRE.Plot_XYList(DummyRimcontactImage, DummyList, '', 'Not Supported in SMART-PCI', '', '', 100)

    else:
        dNode=TIRE.NODE()
        ImageFileName = strSimCode + '-PressureChangeRW1.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N1, N4, ImageDPI, dNode, L1, L4)
        ImageFileName = strSimCode + '-PressureChangeRW2.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N2, N5, ImageDPI, dNode, L2, L5)
        ImageFileName = strSimCode + '-PressureChangeRW3.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N3, N6, ImageDPI, dNode, L3, L6)

        ImageFileName = strSimCode + '-RimChangePress1.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N1, N2, ImageDPI, N3, L1, L2, L3)
        ImageFileName = strSimCode + '-RimChangePress2.png'
        TIRE.Plot_OuterEdgeComparison(ImageFileName, Element, N4, N5, ImageDPI, N6, L4, L5, L6)

        Sim = [SimulationRimWidth[0], SimulationPressure[0], SimulationPressure[3]]
        Fname = [N1, N4]
        ImageFileName = strSimCode + '-ProfileGrowthRW1.png'
        
        ProfileLift, CrownLift = TIRE.Plot_ProfileLiftStaticInflation(ImageFileName, TreadDesignWidth, 5.0, Fname, Sim, Offset=NodeOffset.value, TreadNumber=TreadNumber.value, group='tbr', edge=oedge)
        N = len(ProfileLift)
        for i in range(N):
            textline = '*' + ProfileLift[i][0] + '\n'
            f.write(textline)
            M = len(ProfileLift[i])
            for j in range(1, M):
                textline = str(format(ProfileLift[i][j][0], '.6f')) + ', ' + str(ProfileLift[i][j][1]) + '\n'
                f.write(textline)

        N = len(CrownLift)
        for i in range(N):
            textline = '*' + CrownLift[i][0] + '\n'
            fc.write(textline)
            M = len(CrownLift[i])
            for j in range(1, M):
                textline = str(format(CrownLift[i][j][0], '.6f')) + ', ' + str(CrownLift[i][j][1]) + '\n'
                fc.write(textline)
        # print Sim, Fname

        Sim = [SimulationRimWidth[1], SimulationPressure[1], SimulationPressure[4]]
        Fname = [N2, N5]
        ImageFileName = strSimCode + '-ProfileGrowthRW2.png'
        ProfileLift, CrownLift = TIRE.Plot_ProfileLiftStaticInflation(ImageFileName, TreadDesignWidth, 5.0, Fname, Sim, Offset=NodeOffset.value, TreadNumber=TreadNumber.value, group='tbr', edge=oedge)
        N = len(ProfileLift)
        for i in range(N):
            textline = '*' + ProfileLift[i][0] + '\n'
            f.write(textline)
            M = len(ProfileLift[i])
            for j in range(1, M):
                textline = str(format(ProfileLift[i][j][0], '.6f')) + ', ' + str(ProfileLift[i][j][1]) + '\n'
                f.write(textline)

        N = len(CrownLift)
        for i in range(N):
            textline = '*' + CrownLift[i][0] + '\n'
            fc.write(textline)
            M = len(CrownLift[i])
            for j in range(1, M):
                textline = str(format(CrownLift[i][j][0], '.6f')) + ', ' + str(CrownLift[i][j][1]) + '\n'
                fc.write(textline)
        # print Sim, Fname

        Sim = [SimulationRimWidth[2], SimulationPressure[2], SimulationPressure[5]]
        # Fname = [SurfacePostionFileName[2], SurfacePostionFileName[5]]
        Fname = [N3, N6]
        ImageFileName = strSimCode + '-ProfileGrowthRW3.png'
        ProfileLift, CrownLift = TIRE.Plot_ProfileLiftStaticInflation(ImageFileName, TreadDesignWidth, 5.0, Fname, Sim, Offset=NodeOffset.value, TreadNumber=TreadNumber.value, group='tbr', edge=oedge)
        N = len(ProfileLift)
        for i in range(N):
            textline = '*' + ProfileLift[i][0] + '\n'
            f.write(textline)
            M = len(ProfileLift[i])
            for j in range(1, M):
                textline = str(format(ProfileLift[i][j][0], '.6f')) + ', ' + str(ProfileLift[i][j][1]) + '\n'
                f.write(textline)

        N = len(CrownLift)
        for i in range(N):
            textline = '*' + CrownLift[i][0] + '\n'
            fc.write(textline)
            M = len(CrownLift[i])
            for j in range(1, M):
                textline = str(format(CrownLift[i][j][0], '.6f')) + ', ' + str(CrownLift[i][j][1]) + '\n'
                fc.write(textline)

        DummyList = []
        DummyRimcontactImage = strSimCode + '-RimContactPressRW1.png'
        TIRE.Plot_XYList(DummyRimcontactImage, DummyList, '', 'Not Supported in SMART-PCI', '', '', 100)
        DummyRimcontactImage = strSimCode + '-RimContactPressRW2.png'
        TIRE.Plot_XYList(DummyRimcontactImage, DummyList, '', 'Not Supported in SMART-PCI', '', '', 100)
        DummyRimcontactImage = strSimCode + '-RimContactPressRW3.png'
        TIRE.Plot_XYList(DummyRimcontactImage, DummyList, '', 'Not Supported in SMART-PCI', '', '', 100)

        # print Sim, Fname


    f.writelines("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!")
    f.close()
    fc.writelines("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!")
    fc.close()

    f=open(strSimCode + '-RimContactPressureStaticInflation.txt', "w")
    f.writelines("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!")
    f.close()

    t1 = time.time()
    os.system('rm -f *.tmp')
    os.system('rm -f *Value.txt')
    print "Duration :", t1 - t0, "sec"
    
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass 

