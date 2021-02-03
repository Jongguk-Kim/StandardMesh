try:
    import CommonFunction as TIRE
except: 
    import CommonFunction_v3_0 as TIRE
import glob, os, sys, json, time, math
try:
    import CheckExecution
except: 
    pass 

## Rim Dia Information 
## PC/LT : Design Rim base
PC_LT_RimDia = [[12.0, 302.8], 
                [13.0, 328.2], 
                [14.0, 353.4], 
                [15.0, 378.8], 
                [16.0, 404.2], ## LTR/M, 404.2 for LTR/S
                [16.0, 404.8],
                [16.5, 417.0], 
                [17.0, 435.2], 
                [18.0, 460.6],
                [19.0, 486.0], ## 243*2
                [20.0, 511.4], 
                [21.0, 536.8], ## 268.4*2
                [22.0, 562.2], 
                [23.0, 587.6] ## 293.8*2  
                ]
## TBR : Test Rim base 
TB_RimDia = [
    [17.5,444.5],[19.5,495.3],[22.5,571.5],[24.5,622.3],[26.5,673.1], ## Tubeless 
    [15.0,385.0],[16.0,405.0],[18.0,461.8],[20.0,517.0],[24.0,613.6]
]


if __name__ == "__main__":
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass 
    
    Offset = 10000
    TreadNo = 10000000
    tstart = time.time()
    ###############################################################################################
    ## FOR DOE 
    ###############################################################################################
    twratio = 1.0
    doe = ''
    rev = 0
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i].split('=')
        
        if arg[0] == 'smart':            smart = arg[1].strip()
        if arg[0] == 'mesh':             str2DInp = arg[1]
        if arg[0] == 'sns':              snsfile=arg[1].strip()
        
        if arg[0] == 'rev':              rev = int(arg[1].strip())  
        if arg[0] == 'tw':
            twratio = float(arg[1].strip())
            if rev == 0:
                reftwratio = twratio
            twratio = twratio / reftwratio
        if arg[0] == 'doe'  :           doe = arg[1].strip()
    #################################################################################

    if doe != '':
        with open(snsfile) as Sns_file:
            lstSnsInfo = json.load(Sns_file)

        strSimCode = lstSnsInfo["AnalysisInformation"]["SimulationCode"]
        TreadDesignWidth = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"])
        listGD = lstSnsInfo["VirtualTireParameters"]["MainGrooveDepth"].split(";")
        Shodrop = float(lstSnsInfo["VirtualTireParameters"]["ShoulderDrop"]) 
        TireOD =  float(lstSnsInfo["VirtualTireParameters"]["OverallDiameter"])
        groovedepth = 0.0
        for gd in listGD:
            if groovedepth < float(gd):  groovedepth = float(gd)

        tiregroup = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]
        TreadDesignWidth  = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"]) 

        SimTime = TIRE.SIMTIME(smart)
        SimCondition = TIRE.CONDITION(smart)

        lstSmart = smart.split("/")
        strJobDir = ''
        for i in range(len(lstSmart)-1): strJobDir += lstSmart[i]+'/'
        strJobDir = strJobDir[:-1]    

        strErrFileName = smart[:-4] + '.err'

        filename_base =  smart[:-4] 

    else:
        strJobDir = os.getcwd()
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
        TreadDesignWidth = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"])
        listGD = lstSnsInfo["VirtualTireParameters"]["MainGrooveDepth"].split(";")
        Shodrop = float(lstSnsInfo["VirtualTireParameters"]["ShoulderDrop"])
        TireOD =  float(lstSnsInfo["VirtualTireParameters"]["OverallDiameter"])
        groovedepth = 0.0
        for gd in listGD:
            if groovedepth < float(gd):  groovedepth = float(gd)
        tiregroup = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]
        
        SimTime = TIRE.SIMTIME(strSimCode+'.inp')
        SimCondition = TIRE.CONDITION(strSimCode+'.inp')
        strErrFileName = strSimCode + '.err' 
        
        filename_base =  strSimCode
        
        rev = strSimCode.split("-")[2]
    ###############################################################################################


    err=open(strErrFileName, 'w')
    
    print ("** Simulation Time :", SimTime.SimulationTime, ', Del Time', SimTime.DelTime, ', Averaging', SimTime.AveragingTime, ', Last Step', SimTime.LastStep)
    
    try:
        Node, Element, Elset, Comment = TIRE.Mesh2DInformation(str2DInp)
    except:
        line = "ERROR::POST::[STANDINGWAVE] - Cannot open 2D Mesh File (VT-Code.inp)+\n"
        err.writelines(line)
        err.close()
        sys.exit()
    try:
        doewdir =  os.getcwd()
        namedoewdir = doewdir.split("-")
        namedoewdir[-3] = "0"
        namedoewdir[-5] = "0/"+ namedoewdir[-5].split("/")[1] 
        dirname = ""
        for name in namedoewdir:
            dirname += name + "-"
        dirname = dirname[:-1]
        tmp=str2DInp.split("/")[-1]
        tmp = tmp.split("-")
        DoeBase2DInp = dirname +"/" + tmp[0] + "-0.inp"
        baseNode, baseElement, baseElset, baseComment = TIRE.Mesh2DInformation(DoeBase2DInp)
        imagename = str2DInp[:-4]+"-DOELayoutCompare.png"

        TIRE.Plot_LayoutCompare(imagename, L1="Base Model", N1=baseNode, E1=baseElement, L2="Generated Model", N2=Node, E2=Element, dpi=150)
    except:
        pass


    
    ####################################################################################
    ## Groove Deformation 
    #################################################################################### 
    sdb = strJobDir + "/SDB_PCI." + strSimCode + "/" + strSimCode + ".sdb"
    tm1 = str(format(int (0.02 / SimTime.DelTime), "03"))
    lstsdb = sdb + tm1
    Node02 = TIRE.ResultSDB(sdb, lstsdb, Offset, TreadNo, 1, -1)
    for n in Node02.Node:        n[0] = n[0] % Offset
    tm1 = str(format(int (0.03 / SimTime.DelTime), "03"))
    lstsdb = sdb + tm1
    Node03 = TIRE.ResultSDB(sdb, lstsdb, Offset, TreadNo, 1, -1)
    for n in Node03.Node:        n[0] = n[0] % Offset
    if len(Node02.Node) != len(Node03.Node): 
        print ("ERROR!! Node No. between Time 0.02 and 0.03 are different (Maybe no results in the last step file)!!")
        print ("#####   Processing is going to stop!!")
        sys.exit()


    outerprofile = Element.OuterEdge(Node)
    treadprofile = TIRE.EDGE()
    for of in outerprofile.Edge:
        if of[2] == "SUT" or of[2] == "CTB"  or of[2] == "CTR" or of[2] == "UTR" or of[2] == "TRW" :
            treadprofile.Add(of)
    tdnodelist = treadprofile.Nodes()
    
    TreadElset =["SUT", "CTB", "CTR", "UTR", "TRW"]
    CrownElement=TIRE.ELEMENT()
    for elset in TreadElset:
        tmpelset = Element.Elset(elset)
        CrownElement.Combine(tmpelset)


    groovetop = []
    groovebottomnode = []
    for i, n in enumerate(tdnodelist):
        if i < 3 or i > len(tdnodelist)-4: continue
        counting = 0
        el3 = 0
        for e in CrownElement.Element:  # check if the node is on the tri-angular element 
            for i in range(1, e[6]+1):
                if n == e[i]:
                    counting += 1
                    if e[6] == 3:
                        el3=e[0]     # -> node on a tri-angular element 
                    break
        if counting == 1:
            groovetop.append(n)
        elif counting >= 3 and el3 == 0:
            groovebottomnode.append(n)
        elif counting >=3 and el3 > 0:                                 ## if bottom node is on tri-angular element, that has no contact with "BSW", "SHW" or "BEC"
            ADJ = TIRE.FindAdjcentElements(el3, Element)
            bgroove = 1
            for adj in ADJ.Element:
                if adj[5] == "BSW" or adj[5] == "SHW" or adj[5] == "BEC":  bgroove = 0    ## if 
            if bgroove ==1: groovebottomnode.append(n)

    groovetopnode = []
    for top in groovetop:
        counting = 0
        for tedge in treadprofile.Edge:
            if top == tedge[0] or top == tedge[1]:
                counting += 1
        if counting == 2:
            groovetopnode.append(top)
    del(groovetop)

    print ("Groove Top Node", groovetopnode)
    LY = []
    for nd in groovetopnode: 
        N = Node.NodeByID(nd)
        LY.append(N[2])

    if len(LY) > 0: 
        MinLY=min(LY)
        MaxLY=max(LY)

        LY = []
        for nd in groovebottomnode: 
            N = Node.NodeByID(nd)
            if N[2] < MaxLY and N[2]>MinLY: LY.append(nd)
        
        groovebottomnode = LY 
    

    if len(groovebottomnode) != len(groovetopnode): 
        print (" ## CHECK GROOVE EDGE NODE SEARCH ALGORITHM - NOT THE SAME NO. OF NDOES.")
        print ("groove bottom nodes", groovebottomnode)


    if len(groovetopnode) > 2:
        TIRE.PlotGrooveDeformation_BetweenGT_Drum(filename_base+"-Grooveshape", Node02, Node03, treadprofile, groovetopnode, groovebottomnode, shift=0.0, mold=Node,\
                groove=groovedepth, treadwidth=TreadDesignWidth, group=tiregroup, color="black", label="", fontsize=5, lw=1.0, dimcolor="royalblue", dimbottomcolor="darkorange")
    
    ## End Tread Extrusion Design Guide 
    ####################################################################################
    Node, Element, Elset, Comment = TIRE.Mesh2DInformation(str2DInp)

    DeformedNode = TIRE.GetDeformedNodeFromSDB(strSimCode, 0, Step=0, Offset=Offset, TreadNo=TreadNo, simtime=SimTime, jobdir=strJobDir)
    for i, nd in enumerate(DeformedNode.Node):
        if math.isnan(nd[1]): 
            textline = 'ERROR::POST::[DIMENSION] - There is no information of the deformed shape\n'
            print (textline)
            err.write(textline)
            try:
                CheckExecution.getProgramTime(str(sys.argv[0]), "End")
            except:
                pass 

            sys.exit()

    InitialOD, InitialSW = TIRE.GetODSWfromDeformedNode(Node, Element, Node, ResultOption=1, Offset=Offset, TreadNo=TreadNo)
    with open('sw.tmp') as SW:
        lines = SW.readlines()
    for line in lines:
        if "sw" in line:
            data = line.split("=")[1].strip()
            InitialSWPointX=float(data)*500
        if 'posY' in line:
            data = line.split("=")[1].strip()
            InitialSWPointY=float(data)*1000

    DeformedOD, DeformedSW = TIRE.GetODSWfromDeformedNode(DeformedNode, Element, Node, ResultOption=1, Offset=Offset, TreadNo=TreadNo, slipangle=SimCondition.SlipAngle, camber=SimCondition.Camber)
    with open('sw.tmp') as SW:
        lines = SW.readlines()
    for line in lines:
        if "sw" in line:
            data = line.split("=")[1].strip()
            DeformedSWPointX=float(data)*500
        if 'posY' in line:
            data = line.split("=")[1].strip()
            DeformedSWPointY=float(data)*1000
    
 

    RimDia = SimCondition.RimDiameter
    MinGap=10**7
    if tiregroup != 'TBR': 
        for dia in PC_LT_RimDia: 
            if abs(SimCondition.RimDiameter - dia[1])< MinGap: 
                RimDia = dia[1]
                MinGap = abs(SimCondition.RimDiameter - dia[1])
        
    else:
        BeadringType =  lstSnsInfo["VirtualTireParameters"]["BeadringType"]
        for dia in TB_RimDia: 
            if abs(SimCondition.RimDiameter - dia[1])< MinGap: 
                RimDia = dia[1]
                MinGap = abs(SimCondition.RimDiameter - dia[1])

    MoldRimWidth = SimCondition.RimWidth
    with open(str2DInp) as SW: 
        lines = SW.readlines()
    for line in lines:
        if "LAYOUT RIM WIDTH" in line:
            data = line.split(":")[1].strip()
            MoldRimWidth = float(data)
            print(MoldRimWidth)
            break 

    tireSize = lstSnsInfo["VirtualTireBasicInfo"]["TireSize"]
    if tiregroup != 'TBR': rimHt = 9.2
    elif BeadringType=="Tubeless": 
        rimHt = 0.0
    else: 
        if "900R" in tireSize or "9.00R" in tireSize:    rimHt = 12.6
        elif "1000R" in tireSize or "10.00R" in tireSize:    rimHt = 14.0
        elif "1100R" in tireSize or "11.00R" in tireSize:    rimHt = 14.7
        elif "1200R" in tireSize or "12.00R" in tireSize:    rimHt = 14.7
        elif "365/80R20" in tireSize :    rimHt = 18.0
        elif "750R" in tireSize or "7.5R" in tireSize:    rimHt = 14.4
        elif "825R" in tireSize or "8.25R" in tireSize:    rimHt = 16.0
        else: rimHt = 14.7  ## default : most popular size 

    if tiregroup == 'TBR' and BeadringType=="Tubeless": 
        InitialK_Factor =  TIRE.TBR_TL_Alpha(outerprofile, Node, rimDia=RimDia)
    else: 

        InitialLSH = InitialSWPointY - RimDia/2.0 -rimHt
        InitialDW = InitialSWPointX - MoldRimWidth/2.0 
        InitialK_Factor = (InitialLSH**2 - InitialDW**2)/InitialLSH/2/InitialDW
        # print("SW Point x=%.4f, y=%.4f"%(InitialSWPointX,InitialSWPointY))
        # print("RIM Point x=%.4f, y=%.4f, Hb=%.1f"%(MoldRimWidth/2.0 ,RimDia/2.0, rimHt))
        # print ("LSH=%.1f, DW=%.1f"%(InitialLSH, InitialDW))


    DeformedLSH = DeformedSWPointY - RimDia/2.0 -rimHt
    DeformedDW = DeformedSWPointX - SimCondition.RimWidth/2.0
    DeformedK_Factor = (DeformedLSH**2 - DeformedDW**2)/DeformedLSH/2/DeformedDW

    # print("####################################################")
    print (" TIRE SIZE : %s"%(tireSize))    
    print (" Mold RW=%.2f, test RW=%.2f"%(MoldRimWidth, SimCondition.RimWidth))
    print (" Mold RD=%.2f <- used to calculate (test RD=%.2f)"%(RimDia, SimCondition.RimDiameter))

    print (" Init SW Point x=%.3f, y=%.3f"%(InitialSWPointX, InitialSWPointY))
    print (" Deformed SW Point x=%.3f, y=%.3f"%(DeformedSWPointX, DeformedSWPointY))
    print("** Mold K-Factor = %.2f, Deformed K-Factor=%.2f"%(InitialK_Factor, DeformedK_Factor))

    SWPointForK_factor = [[0, 0, DeformedSWPointX/1000, DeformedSWPointY/1000]]
    SWPointForK_factor.append([0, 0,SimCondition.RimWidth/2000, RimDia/2000])

    # print "** Initial OD=", format(InitialOD*1000, '.1f'), 'mm, SW=', format(InitialSW*1000, '.1f'),'mm', ", Deformed OD=", format(DeformedOD*1000, '.1f'), 'mm, SW=', format(DeformedSW*1000, '.1f'),'mm'
    print ("** Initial OD=%.1fmm, SW=%.1fmm, Deformed OD=%.1fmm, Deformed SW=%.1fmm"%(InitialOD*1000, InitialSW*1000, DeformedOD*1000, DeformedSW*1000))
    
    ####################################################################################
    # Node3DFileName = strSimCode+'-NodePosition.tmp'
    # DeformedTopNode = TIRE.GetDeformedNodeFromSDB(Node3DFileName, 1001, Step=0, Offset=Offset, TreadNo=TreadNo)
    DeformedTopNode = TIRE.GetDeformedNodeFromSDB(strSimCode, -1, Step=0, Offset=Offset, TreadNo=TreadNo, simtime=SimTime, jobdir=strJobDir)
    for nd in DeformedTopNode.Node:
        nd[0] %= Offset
    # DeformedTopNode.Image(file="DEFORMED_ROTATED_camber_0", size=10, xy=21)
    DeformedTopNode.Rotate(SimCondition.Camber, xy=23)
    # DeformedTopNode.Image(file="DEFORMED_ROTATED_camber_23_", size=10, xy=21)
    DeformedTopNode.Rotate(-SimCondition.SlipAngle, xy=21)
    # DeformedTopNode.Image(file="DEFORMED_ROTATED_camber_slipangle_21_", size=10, xy=21)
    NullNode = TIRE.NODE()

    mz = 0
    for inode in DeformedTopNode.Node:
        if mz < inode[3]:
            mz = inode[3]

    if DeformedOD/2.0 != mz:
        movez = DeformedOD/2.0 - mz
        for inode in DeformedTopNode.Node:
            inode[3] += movez
        print ("** Top node Z=%f, modified node = %f, node moved %f"%(mz, mz+movez, movez) )
    
    # TIRE.Plot_OuterEdgeComparison(strSimCode+"-InitialInflated", Element, Node, DeformedTopNode, 150,NullNode, "Initial", "Inflated")
    
    BT1edge = Element.ElsetToEdge('BT1')
    BT2edge = Element.ElsetToEdge('BT2')
    BT3edge = Element.ElsetToEdge('BT3')
    C01edge = Element.ElsetToEdge("C01")
    
    BDR = Element.Elset('BEAD_R')
    BDL = Element.Elset('BEAD_L')
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

    BDROuter = BDR.OuterEdge(Node)
    BDLOuter = BDL.OuterEdge(Node)
    # C01edge = Element.ElsetToEdge('C01')
    
    tOuteredge = Element.OuterEdge(Node)
    if len(BT3edge.Edge) > 0: 
        tOuteredge.Combine(BT2edge)
    else:
        tOuteredge.Combine(BT1edge)
    tOuteredge.Combine(BDROuter)
    tOuteredge.Combine(BDLOuter)
    tOuteredge.Combine(C01edge)

    if len(groovetopnode) ==0 :
        TIRE.Plot_EdgeComparison(filename_base+"-Grooveshape", tOuteredge, Node, Node02, Node3=Node03,\
         L1="Time_0.00 (In-Mold)", L2="Time_0.02", L3="Time_0.03", ls1=":")
    else:
        TIRE.Plot_EdgeComparison(filename_base+"-Shaping", tOuteredge, Node, Node02, Node3=Node03,\
         L1="Time_0.00 (In-Mold)", L2="Time_0.02", L3="Time_0.03", ls1=":")
    ####################################################################################

    OuterEdge = outerprofile # Element.OuterEdge(Node)
    GrooveCrown = TIRE.GrooveDetectionFromEdge(OuterEdge, Node, OnlyTread=1, TreadNumber=TreadNo)
    # GrooveCrown.Image(Node, "EDGE", "o")
    NoGrooveCrown = TIRE.DeleteGrooveEdgeAfterGrooveDetection(GrooveCrown, Node)
    
    # NoGrooveCrown.Image(Node,"NoGroove", "o")

    ## finding sho. drop check node  (Shodrop = Tire Shoulder Drop from SNS, TireOD = Tire Overall diameter from SNS)


    N = len(NoGrooveCrown.Edge)
    
    TWEnd = 0
    TWStart = 0 
    CenterEdge = 0 
    CrownEdge = TIRE.EDGE()
    TopZ = 0.0
    TopNode = 0
    LeftMidNode = 0
    RightMidNode = 0
    iscentergroove = 0
    for i in range(N):
        N1 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
        N2 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
        if N1[2] == 0.0:
            CenterEdge = i
            CenterNode = N1
            iscentergroove = 0
        if N1[2]*N2[2] < 0.0:
            CenterEdge = i
            CenterNode = [0, 0.0, 0.0, (N1[3]*abs(N2[2])+N2[3]*abs(N1[2]))/(abs(N1[2])+abs(N2[2]))]
            iscentergroove = 1

    
    if Shodrop > 0.0: 
        # hMin = 100.0
        PreTWNode = []
        NextTWNode = []
        TWNode = 0
        ShoDropRatio = 0
        for i in range(CenterEdge+1, N):
            N2 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
            if (TireOD/2000.0 - N2[3] ) <= Shodrop/1000.0: 
                # hMin =  (TireOD/2000.0 - N2[3] ) - Shodrop/1000.0 
                PreTWNode=[N2[0], N2[3]]
                NextTWNode=[N2[0], N2[3]]
                TWNode = N2[0]
            else:
                PreTWNode=[PreTWNode[0], PreTWNode[1], TireOD/2000.0-PreTWNode[1]]
                NextTWNode = [N2[0], N2[3], TireOD/2000.0 - N2[3]] 
                ShoDropRatio = (Shodrop/1000-PreTWNode[2]) / (PreTWNode[1] - NextTWNode[1]) 
                break
        
        
        TopNode = 0
        hMax = 0.0
        for nd in Node.Node:
            if hMax < nd[3] and nd[2] >= 0.0: 
                hMax = nd[3]
                TopNode = nd[0]

        Min = 9.9E20;     hMin = 9.9E20
        Length = 0.0
        for i in range(CenterEdge, N):
            if i == CenterEdge:
                N2 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
                Length += math.sqrt( (CenterNode[2] - N2[2]) * (CenterNode[2] - N2[2]) + (CenterNode[3] - N2[3]) * (CenterNode[3] - N2[3]) )
                continue
            
            N1 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
            N2 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
            Length += math.sqrt( (N1[2] - N2[2]) * (N1[2] - N2[2]) + (N1[3] - N2[3]) * (N1[3] - N2[3]) )
            
            if TreadDesignWidth/4000.0-Length >= 0: RightMidNode = N2[0]

        Min = 9.9E20;     hMin = 9.9E20
        Length = 0.0
        for i in range(CenterEdge, -1, -1):
            if iscentergroove ==1 and i == CenterEdge:
                N1 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
                Length += math.sqrt( (CenterNode[2] - N1[2]) * (CenterNode[2] - N1[2]) + (CenterNode[3] - N1[3]) * (CenterNode[3] - N1[3]) )

                CenterNode = Node.Node[0]
                for nd in Node.Node:
                    if nd[2] == 0 and nd[3] > CenterNode[3]:   
                        CenterNode = nd 
            else:
                if i != CenterEdge: 
                    N1 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
                    N2 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
                    Length += math.sqrt( (N1[2] - N2[2]) * (N1[2] - N2[2]) + (N1[3] - N2[3]) * (N1[3] - N2[3]) )
                    
            if TreadDesignWidth/4000.0-Length >= 0: LeftMidNode = N1[0]
            

        
        N1 = Node.NodeByID(LeftMidNode)
        N2 = Node.NodeByID(TopNode)
        N3 = Node.NodeByID(RightMidNode)
        InitialTR = TIRE.CalculateRadiusOf3Points(N1, N2, N3, 23, 3)
        N1 = Node.NodeByID(PreTWNode[0])
        N11 = Node.NodeByID(NextTWNode[0])
        InitialShoDrop= round(N2[3] - N1[3] + (N1[3]-N11[3])*ShoDropRatio, 5)
        # print (TireOD/2000.0, N2, N1, N11) 

        # print ("** Center Node = [%f, %f, %f]"%(CenterNode[1], CenterNode[2], CenterNode[3]))
        print ("** Sho. Drop Initial :  Node 1=%d(%.3fmm), Node 2=%d(%.3fmm), ratio=%.3f)"%(PreTWNode[0], (N2[3]-N1[3])*1000, NextTWNode[0], (N2[3]-N11[3])*1000, ShoDropRatio))

        N1 = DeformedTopNode.NodeByID(LeftMidNode)
        N2 = DeformedTopNode.NodeByID(TopNode)
        N3 = DeformedTopNode.NodeByID(RightMidNode)
        DeformedTR = TIRE.CalculateRadiusOf3Points(N1, N2, N3, 23, 3)
        
        N1 = DeformedTopNode.NodeByID(PreTWNode[0])
        N11 = DeformedTopNode.NodeByID(NextTWNode[0])
        DeformedShoDrop= round(N2[3] - N1[3] + (N1[3]-N11[3])*ShoDropRatio, 5)
        print ("** Sho. Drop Deformed : Node 1=%d(%.3fmm), Node 2=%d(%.3fmm), ratio=%.3f)"%(PreTWNode[0], (N2[3]-N1[3])*1000, NextTWNode[0], (N2[3]-N11[3])*1000, ShoDropRatio))
        print ("   ==> Sho. Drop Initial=%.2fmm (in SNS %.2f) --> Deformed=%.2fmm"%(InitialShoDrop*1000, Shodrop,  DeformedShoDrop*1000))
        
        print ("** Tread Radius check Node ID: %d, %d, Center Node ID : %d"%(LeftMidNode, RightMidNode, TopNode))
        print ("   ==> Initial TR=%.0fmm --> Deformed TR=%.0fmm"%(InitialTR*1000, DeformedTR*1000))
        

    else:    ## if there is no sho.drop information at SNS file, there can be error in calculation logic when you try to compare results with other models.

        CriticalAngle = 40.0

        Min = 9.9E20;     hMin = 9.9E20
        Length = 0.0
        for i in range(CenterEdge, N):
            if i == CenterEdge:
                N2 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
                Length += math.sqrt( (CenterNode[2] - N2[2]) * (CenterNode[2] - N2[2]) + (CenterNode[3] - N2[3]) * (CenterNode[3] - N2[3]) )
                # print ("right", NoGrooveCrown.Edge[i], Length*1000, TreadDesignWidth/2.0)
                
                continue
            
            N1 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
            N2 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
            Length += math.sqrt( (N1[2] - N2[2]) * (N1[2] - N2[2]) + (N1[3] - N2[3]) * (N1[3] - N2[3]) )
            
            N1a = [N1[0], N1[1], abs(N1[2]), N1[3]]
            N2a = [N2[0], N2[1], abs(N2[2]), N2[3]]
            angle = TIRE.CalculateAngleFrom3Node(N2a, [0, N2a[1], N2a[2]+1.0, N2a[3]], N1a, XY=23)*180.0/math.pi
            if TreadDesignWidth/2000.0-Length >= 0 and abs(angle) < CriticalAngle: 
                RightTWNode = N2
                # print ("right", NoGrooveCrown.Edge[i], Length*1000, TreadDesignWidth/2.0, angle)
            if TreadDesignWidth/4000.0-Length >= 0: RightMidNode = N2

        # print ("Right TW Node = %d, Right Mid node = %d"%(RightTWNode[0], RightMidNode[0]))
        # print ("Angle", angle)
        Min = 9.9E20;     hMin = 9.9E20
        Length = 0.0
        for i in range(CenterEdge, -1, -1):
            if iscentergroove ==1 and i == CenterEdge:
                N1 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
                Length += math.sqrt( (CenterNode[2] - N1[2]) * (CenterNode[2] - N1[2]) + (CenterNode[3] - N1[3]) * (CenterNode[3] - N1[3]) )
                # print ("Left", NoGrooveCrown.Edge[i], Length*1000, TreadDesignWidth/2.0)
                CenterNode = Node.Node[0]
                for nd in Node.Node:
                    if nd[2] == 0 and nd[3] > CenterNode[3]:   
                        CenterNode = nd 
            else:
                if i != CenterEdge: 
                    N1 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
                    N2 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
                    Length += math.sqrt( (N1[2] - N2[2]) * (N1[2] - N2[2]) + (N1[3] - N2[3]) * (N1[3] - N2[3]) )
                    
            N1a = [N1[0], N1[1], abs(N1[2]), N1[3]]
            N2a = [N2[0], N2[1], abs(N2[2]), N2[3]]
            angle = TIRE.CalculateAngleFrom3Node(N1a, [0, N1a[1], N1a[2]+1.0, N1a[3]], N2a, XY=23)*180.0/math.pi
            if TreadDesignWidth/2000.0-Length >= 0  and abs(angle) < CriticalAngle: 
                LeftTWNode = N1
                # print ("Left", NoGrooveCrown.Edge[i], Length*1000, TreadDesignWidth/2.0)
            if TreadDesignWidth/4000.0-Length >= 0: LeftMidNode = N1
        # print ("Left TW Node = %d, Left Mid node = %d"%(LeftTWNode[0], LeftMidNode[0]))
        # print ("Tread Width = %f"%(TreadDesignWidth))
        TWStart = LeftTWNode[0];     TWEnd = RightTWNode[0]; 

        N1 = Node.NodeByID(TWStart)
        N2 = Node.NodeByID(TWEnd)
        # print ("N1", N1, abs(N1[2])-TreadDesignWidth/2000.0)
        # print ("N2", N2, abs(N2[2])-TreadDesignWidth/2000.0)
        if abs(N2[2]) > abs(N1[2]):  TWNode = N1[0]
        else: TWNode = N2[0]

        cnodes = NoGrooveCrown.Nodes()
        iy = 1000.0
        for nd in cnodes:
            nn = Node.NodeByID(nd)
            if iy > abs(nn[2]): 
                iy = abs(nn[2])
                TopNode = nn[0]
        # TopNode = CenterNode[0]
        LeftMidNode = LeftMidNode[0]; RightMidNode = RightMidNode[0]
        print ("** Center Node = [%f, %f, %f]"%(CenterNode[1], CenterNode[2], CenterNode[3]))
        print ("** Sho.Drop Check Node ID : %d, %d -> %d, Crown Center Node ID : %d"%(TWStart, TWEnd, TWNode, TopNode))
        print ("** Tread Radius check Node ID: %d, %d, Center Node ID : %d"%(LeftMidNode, RightMidNode, TopNode))
    
        N1 = Node.NodeByID(LeftMidNode)
        N2 = Node.NodeByID(TopNode)
        N3 = Node.NodeByID(RightMidNode)
        InitialTR = TIRE.CalculateRadiusOf3Points(N1, N2, N3, 23, 3)
        N1 = DeformedTopNode.NodeByID(LeftMidNode)
        N2 = DeformedTopNode.NodeByID(TopNode)
        N3 = DeformedTopNode.NodeByID(RightMidNode)
        DeformedTR = TIRE.CalculateRadiusOf3Points(N1, N2, N3, 23, 3)
        
        N1 = Node.NodeByID(TWNode)
        N2 = Node.NodeByID(TopNode)
        InitialShoDrop=(N2[3]-N1[3])
        N1 = DeformedTopNode.NodeByID(TWNode)
        N2 = DeformedTopNode.NodeByID(TopNode)
        DeformedShoDrop=(N2[3]-N1[3])

        print ("** Initial TR=%.0fmm --> Deformed TR=%.0fmm"%(InitialTR*1000, DeformedTR*1000))
        print ("** Sho. Drop Initial=%.2fmm --> Deformed=%.2fmm"%(InitialShoDrop*1000, DeformedShoDrop*1000))

    #########################################################################################
    
    tC01 = Element.Elset('C01')
    tBT = Element.Elset('BT3')
    
    if len(tBT.Element) == 0: 
        tBT = Element.Elset('BT1')
    else: 
        tBT = Element.Elset('BT2')
    
    Nc01 = len(tC01.Element)
    Nbt  = len(tBT.Element)
    
    ## FirstCo/FirstBt
    for i in range(Nc01):
        match = 0
        for j in range(Nc01):
            if tC01.Element[i][2] == tC01.Element[j][1]: 
                match = 1
                break
        if match ==0:
            FirstCo= i
            break
    for i in range(Nbt):
        match = 0
        for j in range(Nbt):
            if tBT.Element[i][2] == tBT.Element[j][1]: 
                match = 1
                break
        if match ==0:
            FirstBt= i
            break
            
    C01=TIRE.ELEMENT()
    C01.Add(tC01.Element[FirstCo])
    del(tC01.Element[FirstCo])
    i=0
    while len(C01.Element) < Nc01: 
        found = 0
        for j in range(len(tC01.Element)): 
            if C01.Element[i][1] == tC01.Element[j][2]: 
                C01.Add(tC01.Element[j])
                del(tC01.Element[j])
                found = 1
                break
        
        if found == 0:
            break
        if found == 1: 
            i += 1
    
    BT=TIRE.ELEMENT()
    BT.Add(tBT.Element[FirstBt])
    del(tBT.Element[FirstBt])
    i=0
    
    while len(BT.Element) < Nbt: 
        found = 0
        for j in range(len(tBT.Element)): 
            if BT.Element[i][1] == tBT.Element[j][2]: 
                BT.Add(tBT.Element[j])
                del(tBT.Element[j])
                found = 1
                break
        
        if found == 0:
            break
        if found == 1: 
            i += 1
    del(tBT)    
    del(tC01)
    # BT.Image(Node, "BT")
    # C01.Image(Node, "C01")
    # BT.Print()
    # C01.Print()
    MaxC01 = -10000.0
    for i in range(Nc01): 
        if C01.Element[i][9]> MaxC01:
            MaxC01 = C01.Element[i][9]
            iMaxC01 = i
    
    for i in range(iMaxC01+1, Nc01): 
        N1 = Node.NodeByID(C01.Element[i][1])
        N2 = Node.NodeByID(C01.Element[i][2])
        
        if N1[2] > N2[2]: 
            iC01 = C01.Element[i][1]
            iC01p = C01.Element[i-3][2]
            iC01n = C01.Element[i+2][1]
            # print (C01.Element[i], N1, N2, iC01)
        else: 
            # print ("***", C01.Element[i], N1, N2)
            break
    N1 = Node.NodeByID(iC01p)
    N2 = Node.NodeByID(iC01)
    N3 = Node.NodeByID(iC01n)
    InitialC01R = TIRE.CalculateRadiusOf3Points(N1, N2, N3, 23, 2)
    
    for i in range(iMaxC01+1, Nc01): 
        N1 = DeformedTopNode.NodeByID(C01.Element[i][1])
        N2 = DeformedTopNode.NodeByID(C01.Element[i][2])
        
        if N1[2] > N2[2]: 
            iC01 = C01.Element[i][1]
            iC01p = C01.Element[i-3][2]
            iC01n = C01.Element[i+2][1]
        else: 
            break
    N1 = DeformedTopNode.NodeByID(iC01p)
    N2 = DeformedTopNode.NodeByID(iC01)
    N3 = DeformedTopNode.NodeByID(iC01n)
    DeformedC01R = TIRE.CalculateRadiusOf3Points(N1, N2, N3, 23, 2) 
    SW_Carcass = N2 
            
    MinBT = 10000.0
    for i in range(Nbt): 
        N1 = Node.NodeByID(BT.Element[i][1])
        if abs(N1[2]) < MinBT: 
            iBT = BT.Element[i][1]
            MinBT = abs(N1[2])
            iMinBT = i
    
    iBTn = BT.Element[iMinBT-Nbt/4][1]
    iBTp = BT.Element[iMinBT+Nbt/4][2]
    
    N1 = Node.NodeByID(iBTp)
    N2 = Node.NodeByID(iBT)
    N3 = Node.NodeByID(iBTn)
    InitialBeltCenter = N2
    InitialBTR = TIRE.CalculateRadiusOf3Points(N1, N2, N3, 23, 3)
    N1 = DeformedTopNode.NodeByID(iBTp)
    N2 = DeformedTopNode.NodeByID(iBT)
    N3 = DeformedTopNode.NodeByID(iBTn)
    DeformedBeltCenter = N2
    DeformedBTR = TIRE.CalculateRadiusOf3Points(N1, N2, N3, 23, 3)

    ## inner volume calculation
    Innervolume, tnodeid = TIRE.CalculateTireInnerVolume(Element, DeformedTopNode, node=Node, file=filename_base+"-PointsForVolume.png", toe=1)

    RimRadius = float(lstSnsInfo["VirtualTireParameters"]["RimDiameter"]) / 2000.0 
    LSH = SW_Carcass[3] - RimRadius
    LSH_Comment = "Cc LSH="+format(round(LSH*1000, 1))
    x=abs(SW_Carcass[2])
    y1=RimRadius 
    y2=SW_Carcass[3]
    lsh = [LSH_Comment, [x,y1], [x, y2]]
    print ("CC SW", SW_Carcass)

    if tiregroup =='TBR': 
        Toe0 = Node.NodeByID(tnodeid[1])
        Toe1 = DeformedTopNode.NodeByID(tnodeid[1])

        TOE1_Comment = "Initial Toe R="+str(round(Toe0[3]*1000,1))
        TOE2_Comment = "Deformed Toe R="+str(round(Toe1[3]*1000,1))

        lift = round(Toe1[3]*1000 - Toe0[3]*1000,1)
        if lift >= 0 : TOE2_Comment += "(+"+str(lift)+")"
        else: TOE2_Comment += "("+str(lift)+")"

        TOE1 =[TOE1_Comment, Toe1[2], Toe0[3]]
        TOE2 =[TOE2_Comment, Toe1[2], Toe1[3]]

        ToeDim = [TOE1, TOE2]

    else: 
        ToeDim =[]


    TIRE.Plot_InflatedProfile(filename_base+"-Inflated.png", tOuteredge, Node, DeformedTopNode, 120, NullNode, "Initial", "Inflated (Air Volume="+str(format(Innervolume, ".6f"))+"m^3)", \
            lsh=lsh, toe=ToeDim)

    ## Deformed shape detail image 
    # SWPointForK_factor.append([0, 0,SimCondition.RimWidth/2000, SimCondition.RimDiameter/2000])
    pRim = [SimCondition.RimWidth/2000, SimCondition.RimDiameter/2000]
    TIRE.plot_DetailLayout(filename_base+"-Deformed.png", Element, DeformedTopNode, dpi=300,\
         AddingNodes=SWPointForK_factor, rim=pRim, group=tiregroup, beadring=BeadringType)  ## if tiregroup != 'TBR': rimHt = 9.2    elif BeadringType=="Tubeless": 
    print ("** Initial Vs. Inflated (Inner Volume=%.6fm^3) Image was created.!!"%(Innervolume))
    
    # print "** Carcass Radius Initial=", format(InitialC01R*1000, '.0f'), "mm, Deformed=", format(DeformedC01R*1000, '.0f'), 'mm'
    # print "** Belt Radius Initial=", format(InitialBTR*1000, '.0f'), "mm, Deformed=", format(DeformedBTR*1000, '.0f'), 'mm'
    print ("** Carcass Inital Radius=%.0fmm, Deformed Radius=%.0fmm"%(InitialC01R*1000, DeformedC01R*1000 ))
    print ("** Belt Inital Radius=%.0fmm, Deformed Radius=%.0fmm"%(InitialBTR*1000, DeformedBTR*1000 ))
    LiftBeltCenter = DeformedBeltCenter[3] - InitialBeltCenter[3]
    fristbtnode = BT.Element[0][1]
    lastbtnode  = BT.Element[Nbt-1][2]

    firstNodelift = DeformedTopNode.NodeByID(fristbtnode)[3] - Node.NodeByID(fristbtnode)[3]
    lastNodelift = DeformedTopNode.NodeByID(lastbtnode)[3] - Node.NodeByID(lastbtnode)[3]
    LiftBeltEdge = (lastNodelift+firstNodelift)/2.0

    BTEdgeDrop = DeformedBeltCenter[3] - (DeformedTopNode.NodeByID(fristbtnode)[3]+DeformedTopNode.NodeByID(lastbtnode)[3])/2.0

    ########################################################################################
    f=open(filename_base+'-DimValue.txt', 'w')
    
    line = 'Initial OD=' + str(format(InitialOD*1000, '.2f'))+'\n'
    f.writelines(line)
    line = 'Initial SW=' + str(format(InitialSW*1000, '.2f'))+'\n'
    f.writelines(line)
    line = 'Deformed OD=' + str(format(DeformedOD*1000, '.2f'))+'\n'
    f.writelines(line)
    line = 'Deformed SW=' + str(format(DeformedSW*1000, '.2f'))+'\n'
    f.writelines(line)
    line = 'Mold K-Factor=' + str(format(InitialK_Factor, '.3f'))+'\n'
    f.writelines(line)
    line = 'Inflated K-Factor=' + str(format(DeformedK_Factor, '.3f'))+'\n'
    f.writelines(line)
    
    for i in range(5):
        filelist = os.listdir(strJobDir)
        isFile = 0
        for lfile in filelist:
            FileExt = os.path.splitext(lfile)[-1]
            FileSep = os.path.splitext(lfile)[0].split('-')[0]
            if '.lsflog' in lfile:
                ISLM_logfilename = strJobDir+"/"+lfile
                isFile =1
                break
        if isFile == 0:
            print ("Waiting for being created lsflog file")
            time.sleep(1)
            continue
        else:
            break
    try:
        iyyf = open(ISLM_logfilename, 'r')
        lines = iyyf.readlines()
        isIYY = 0
        for line in lines:
            if 'ACTUAL TIRE IYY' in line:
                data = list(line.split('='))[1].strip()
                # print "IYY=", data
                isIYY = 1
                break
        for line in lines:
            if 'ACTUAL TIRE MASS' in line:
                Weight = list(line.split('='))[1].strip()
                break
        iyyf.close()

        if isIYY == 0:
            print ("ERROR, NO DATA in 'lsflog' file ")
            textline = '\nERROR::Post::[Simulation Result] This simulation result was not created successfully!!'
            f.write(textline)
            f.close()
        else:

            textline = 'TIRE IYY ='+ data+'\n'
            f.write(textline)
            # print ("** %s"(textline))
            textline = '\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!'
            f.write(textline)
            
            f.close()
    except: 
        print ("ERROR, NO DATA in 'lsflog' file ")
        textline = '\nERROR::Post::[Simulation Result] This simulation result was not created successfully!!'
        f.write(textline)
        f.close()
        
    sdb = strJobDir + "/SDB_PCI." + strSimCode + "/" + strSimCode + ".sdb"
    tm1 = str(format(int (0.06 / SimTime.DelTime), "03"))
    lstsdb = sdb + tm1

    gc = TIRE.Plot_CordTension(sdb, lstsdb, filename_base, Element, Offset=Offset, TreadNo=TreadNo, node=DeformedTopNode)
    
    if gc == 1:
        textline = '\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!'
        err.write(textline)
    else:
        textline = 'ERROR::POST::[DIMENSION] - CANNOT PLOT CORD TENSION\n'
        print (textline)
        err.write(textline)

    

    f = open(filename_base+'-Dimension.txt', 'w')
    # print ("######### DOE Result ", cwd+"/"+doe+'-Dimension.txt')
    line = str(rev) + ', Initial OD[mm]=' + str(format(InitialOD*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Initial SW[mm]=', str(format(InitialSW*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Initial Crown Radius[mm]=', str(format(InitialTR*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Initial Sho. Drop[mm]=', str(format(InitialShoDrop*1000, '.6f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Initial Belt Radius[mm]=', str(format(InitialBTR*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Initial Carcass Radius[mm]=', str(format(InitialC01R*1000, '.3f'))+'\n'
    f.writelines(line)
    
    line = str(rev) + ',Deformed OD[mm]=', str(format(DeformedOD*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Deformed SW[mm]=', str(format(DeformedSW*1000, '.3f'))+'\n'
    f.writelines(line)
    
    line = str(rev) + ',Deformed Crown Radius[mm]=', str(format(DeformedTR*1000, '.3f'))+'\n'
    f.writelines(line)
    
    line = str(rev) + ',Deformed Sho. Drop[mm]=', str(format(DeformedShoDrop*1000, '.6f'))+'\n'
    f.writelines(line)
    
    line = str(rev) + ',Deformed Belt Radius[mm]=', str(format(DeformedBTR*1000, '.3f'))+'\n'
    f.writelines(line)
    
    line = str(rev) + ',Deformed Carcass Radius[mm]=', str(format(DeformedC01R*1000, '.3f'))+'\n'
    f.writelines(line)

    line = str(rev) + ',Belt Center Lift[mm]=', str(format(LiftBeltCenter*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Belt Edge Lift[mm]=', str(format(LiftBeltEdge*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Belt Edge Drop[mm]=', str(format(BTEdgeDrop*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ',Weight[kg]=%.3f\n'%(float(Weight))
    f.writelines(line)
    line = str(rev) + ',Mold K-Factor=%.3f\n'%(float(InitialK_Factor))
    f.writelines(line)
    line = str(rev) + ',Inflated K-Factor=%.3f\n'%(float(DeformedK_Factor))
    f.writelines(line)

    f.close()
    

    err.close()

    tend = time.time()
    print ("DURATION -DImension ", tend-tstart)
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass 

