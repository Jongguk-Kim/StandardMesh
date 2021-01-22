try:    import CommonFunction_v3_0 as TIRE
except: import CommonFunction as TIRE
import glob, os, sys, json, time
import multiprocessing as mp
import math
try:     import CheckExecution
except:  pass 

def Plot_TemperatureDotting(filename, TNode, Element, gap=0.4E-3, size=1.30, dpi=150):
    TIRE.Plot_TemperatureDotting(filename, TNode, Element, gap=gap, size=size, dpi=dpi)

def Plot_MappedContour(DeformedNode, Element, filename, dpi, minr, maxr, nr, PointDist):
    TIRE.Plot_MappedContour(DeformedNode, Element, filename, dpi, minr, maxr, nr, PointGap=PointDist)

def Plot_BarChart(filename, names, areavalues, title, value): 
    TIRE.Plot_BarChart(filename, names, areavalues, title, value)

def PlotFootprint(filename_base, lastSDB, lastSFRIC, group, mesh2d, ite=1, step=0, condition='', offset=10000, treadno=10000000, dpi=150, ribimage=0, vmin='', doe=0, fitting=6, ribgraph=0):
    TIRE.PlotFootprint(filename_base, lastSDB, lastSFRIC, group, mesh2d, ite, step, condition, offset, treadno, dpi, ribimage, vmin, doe, fitting, ribgraph)
    
#   TIRE.PlotFootprint(filename_base, lastSDB, lastSFRIC, group=TireGroup, mesh2d= str2DInp, iter=steps, step =0, condition=SimCondition, offset=Offset, treadno=TreadNo, dpi=100, ribimage=0, vmin='', doe=isdoe, fitting=fittingorder, ribgraph=0)
if __name__ == "__main__":
    tstart = time.time()

    Offset = 10000
    TreadNo = 10000000
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass 
    
    doe = ''
    twratio = 1.0
    rev =0
    steps = 1
    CorneringStiffnessSimulation = 0 
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i].split('=')
        if arg[0] == 'mesh':             str2DInp = arg[1]
        if arg[0] == 'sns':              snsfile=arg[1]
        if arg[0] == 'tw':
            twratio = float(arg[1])
            if rev == 0:
                reftwratio = twratio
            twratio = twratio / reftwratio
        if arg[0] == 'rev':              rev = int(arg[1])
        if arg[0] == 'doe':              doe = arg[1]
        if arg[0] == "offset":           Offset = int(arg[1])
        if arg[0] == "nodepress":        steps = int(arg[1])

        if 'corneringstiffness' in arg[0]: CorneringStiffnessSimulation =1 
        if 'simcode' in arg[0]: iSimCode = arg[1]

        if 'shist' in arg[0]: rimfile = arg[1]
        if 'loss' in arg[0]: LossFile = arg[1]
        if 'sdb' in arg[0] and not 'sdbresult' in arg[0]: SDB = arg[1]
        if 'sfric' in arg[0]: SFRIC = arg[1]
        if 'sdbresult' in arg[0]: lastSDB = arg[1]
        if 'result' in arg[0]: lastSFRIC = arg[1]
        if 'fpc' in arg[0]: FPCfile = arg[1]
        if 'smart' in arg[0]: smart = arg[1]

def main(CorneringStiffnessSimulation=1,  iSimCode='simCode', sns='sns', rimfile='rimForce', LossFile='energyLoss',\
             SDB='sdb', SFRIC='sfric', lastSDB='sdbresult', lastSFRIC='result', mesh='mesh', FPCfile='fpc',smart='smart' ):


    # print ("CorneringStiffnessSimulation", CorneringStiffnessSimulation)
    tstart= time.time()
    doe =''
    str2DInp= mesh
    steps = 1
    rev =0 
    
    if CorneringStiffnessSimulation == 1: 
        # str2DInp
        strSmartInpFIleName = smart
        strSimCode = iSimCode
        snsfile=sns
        with open(snsfile) as Sns_file:
            lstSnsInfo = json.load(Sns_file)

        TreadDesignWidth = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"])
        TireGroup = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]
        Groovedepth = lstSnsInfo["VirtualTireParameters"]["MainGrooveDepth"]
        try:
            Shodrop = float(lstSnsInfo["VirtualTireParameters"]["ShoulderDrop"])
        except:
            Shodrop = 0.0
        TireOD =  float(lstSnsInfo["VirtualTireParameters"]["OverallDiameter"])

        SimTime = TIRE.SIMTIME(strSmartInpFIleName)
        SimCondition = TIRE.CONDITION(strSmartInpFIleName)

        filename_base = strSimCode
        strErrFileName = strSimCode + '.err'
        rev = strSimCode.split("-")[2]

        Offset = 10000
        TreadNo = 10**7

        isdoe = 0
            
    if doe != '' and CorneringStiffnessSimulation ==0 :        
        word = list(smart.split('/'))
        I = len(word)
        dirname = ''
        strJobDir = ''
        for i in range(I):
            if i < I-1:
                dirname += word[i]+'/'
            else:
                simfile = word[i]
            if i < I-2:
                strJobDir +=  word[i]+'/'
                
        SimTime = TIRE.SIMTIME(smart)
        SimCondition = TIRE.CONDITION(smart)
        
        
        with open(snsfile) as Sns_file:
            lstSnsInfo = json.load(Sns_file)
            
        TireGroup = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]
        strSimCode = simfile[:-4]
        Groovedepth = lstSnsInfo["VirtualTireParameters"]["MainGrooveDepth"]
        TreadDesignWidth = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"]) 
        try:
            Shodrop = float(lstSnsInfo["VirtualTireParameters"]["ShoulderDrop"])
        except:
            Shodrop = 0.0
        TireOD =  float(lstSnsInfo["VirtualTireParameters"]["OverallDiameter"])

        rimfile = dirname+ "REPORT/frc_"+strSimCode+".rpt"
        LossFile= dirname + "REPORT/vis_"+strSimCode+".rpt"

        if SimTime.SimulationTime == 0.0:
            strSDBDir = dirname + 'SDB_PCI.' + strSimCode
            SDB = dirname + 'SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
            strSFRICDir = dirname + 'SFRIC_PCI.' + strSimCode
            SFRIC = dirname + 'SFRIC_PCI.' + strSimCode + '/' + strSimCode + '.sfric'
        else:
            strSDBDir = dirname + 'SDB.' + strSimCode
            SDB = dirname + 'SDB.' + strSimCode + '/' + strSimCode + '.sdb'
            strSFRICDir = dirname + 'SFRIC.' + strSimCode
            SFRIC = dirname + 'SFRIC.' + strSimCode + '/' + strSimCode + '.sfric'

        lastSFRIC = SFRIC + str(format(SimTime.LastStep, "03"))
        lastSDB = SDB + str(format(SimTime.LastStep, "03"))

        FPCfile = dirname+strSimCode+"-FPC.txt"

        filename_base = dirname+strSimCode
        strErrFileName = filename_base + '.err'

        isdoe = 1
    
    elif CorneringStiffnessSimulation ==0:
        strJobDir = os.getcwd()
        lstSmartFileNames = glob.glob(strJobDir + '/*.sns')
        for sns in lstSmartFileNames:
            # if "D101" in sns or "D104" in sns or "D102" in sns or "D105" in sns:
                strSmartFileName = sns
        # strSmartFileName = lstSmartFileNames[0]
        strSmartInpFIleName = strSmartFileName[:-4] + '.inp'
        
        tmpList = list(strSmartInpFIleName.split('/'))
        tmpList = list(tmpList[-1].split('-'))
        for i in range(len(tmpList)):
            if 'VT' in tmpList[i]: 
                str2DInp = strJobDir + '/' + tmpList[i] + '-' + tmpList[i+1] +'.inp'
                rev = int(tmpList[i+1])
                break

        with open(strSmartFileName) as Sns_file:
            lstSnsInfo = json.load(Sns_file)

        strSimCode = lstSnsInfo["AnalysisInformation"]["SimulationCode"]
        TreadDesignWidth = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"])
        TireGroup = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]
        Groovedepth = lstSnsInfo["VirtualTireParameters"]["MainGrooveDepth"]
        try:
            Shodrop = float(lstSnsInfo["VirtualTireParameters"]["ShoulderDrop"])
        except:
            Shodrop = 0.0
        TireOD =  float(lstSnsInfo["VirtualTireParameters"]["OverallDiameter"])
        
        
        SimTime = TIRE.SIMTIME(strSimCode+'.inp')
        SimCondition = TIRE.CONDITION(strSimCode+'.inp')

        rimfile = strJobDir + "/REPORT/frc_"+strSimCode+".rpt"
        LossFile= strJobDir + "/REPORT/vis_"+strSimCode+".rpt"

        if SimTime.SimulationTime == 0.0:
            strSDBDir = strJobDir + '/SDB_PCI.' + strSimCode
            SDB = strJobDir + '/SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
            strSFIRCDir = strJobDir + '/SFRIC_PCI.' + strSimCode
            SFRIC = strJobDir + '/SFRIC_PCI.' + strSimCode + '/' + strSimCode + '.sfric'
        else:
            strSDBDir = strJobDir + '/SDB.' + strSimCode
            SDB = strJobDir + '/SDB.' + strSimCode + '/' + strSimCode + '.sdb'
            strSFRICDir = strJobDir + '/SFRIC.' + strSimCode
            SFRIC = strJobDir + '/SFRIC.' + strSimCode + '/' + strSimCode + '.sfric'

        lastSFRIC = SFRIC + str(format(SimTime.LastStep, "03"))
        lastSDB = SDB + str(format(SimTime.LastStep, "03"))
        FPCfile = strSimCode+"-FPC.txt"

        isdoe = 0
        filename_base = strSimCode
        strErrFileName = strSimCode + '.err'
        rev = strSimCode.split("-")[2]
        print ("** Simulation Time : %f, Del Time : %f, Time Averaging : %f, Last Step : %d"%(SimTime.SimulationTime, SimTime.DelTime, SimTime.AveragingTime, SimTime.LastStep))
    

    if TireGroup == "TBR": IsTBR =1
    else: IsTBR =0
    
    err=open(strErrFileName, 'w')

    
        
    try:
        Node, Element, Elset, Comment = TIRE.Mesh2DInformation(str2DInp)
        TireOuter = Element.OuterEdge(Node)
    except:
        line = "ERROR::POST::[STANDINGWAVE] - Cannot open 2D Mesh File (VT-Code.inp)+\n"
        print ('Error, Cannot read -%s'%(str2DInp))
        try:
            CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        except:
            pass
        sys.exit()

    if CorneringStiffnessSimulation == 0: 
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
    
    processes=[]

    try: 
        temp = Groovedepth.split(";")
        Groovedepth =0.0
        for t in temp:
            if Groovedepth < t: 
                Groovedepth = t
        Groovedepth = str(Groovedepth)
    except: 
        pass 
    ######################################################################################
    ## Temperature 
    ######################################################################################
    if SimCondition.Speed > 0.0: 
        TNode = TIRE.ResultSDB(SDB, lastSDB, Offset, TreadNo, 1, -2)
        N = len(TNode.Node)
        MinZ = 9.9E20
        MaxZ = -9.9E20
        for i in range(N):
            TNode.Node[i][0] = TNode.Node[i][0] % Offset
            if MinZ > TNode.Node[i][3]:
                MinZ = TNode.Node[i][3]
            if MaxZ < TNode.Node[i][3]:
                MaxZ = TNode.Node[i][3]
        # TNode.DeleteDuplicate()
        SWz= (MinZ+MaxZ)/2.0
        MaxBeltT = 0.0
        MaxBeadT = 0.0

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
        for n in tdnodelist:
            counting = 0
            el3 = 0
            for e in CrownElement.Element:
                for i in range(1, e[6]+1):
                    if n == e[i]:
                        counting += 1
                        if e[6] == 3:
                            el3=1
                        break
            if counting == 1:
                groovetop.append(n)
            elif counting >= 3 and el3 == 0:
                groovebottomnode.append(n)
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
        print ("groove bottom nodes", groovebottomnode)


        
        Outer = Element.OuterEdge(Node)
        I = len(Outer.Edge)
        trd = TIRE.EDGE()
        for i in range(I):
            if Outer.Edge[i][2] == "CTB" or Outer.Edge[i][2] == "CTR" or Outer.Edge[i][2] == "UTR" or Outer.Edge[i][2] == "SUT":
                trd.Add(Outer.Edge[i])
        trd.Sort()
        I = len(trd.Edge)
        dual = []
        f = 0
        for i in range(I-1):
            if f == 1:
                f = 0
                continue
            temp = []
            for j in range(i+1, I-1):
                if trd.Edge[i][4] == trd.Edge[j][4]:
                    temp.append(trd.Edge[i])
                    temp.append(trd.Edge[j])
                    dual.append(temp)
                    f = 1
                    break
            if f == 0:
                n11 = TNode.NodeByID(trd.Edge[i][0])
                n12 = TNode.NodeByID(trd.Edge[i][1])
                n22 = TNode.NodeByID(trd.Edge[i+1][1])
                if (abs(n11[2]-n12[2]) < abs(n11[3]-n12[3])) and (abs(n22[2]-n12[2]) > abs(n22[3]-n12[3])):
                    f = 1
                elif (abs(n11[2]-n12[2]) > abs(n11[3]-n12[3])) and (abs(n22[2]-n12[2]) < abs(n22[3]-n12[3])):
                    f = 1
                
                if f == 1:
                    if TIRE.ShareEdge(trd.Edge[i][4], trd.Edge[i+1][4], Element):
                        temp = []
                        temp.append(trd.Edge[i])
                        temp.append(trd.Edge[i+1])
                        dual.append(temp)
                        continue
        I = len(dual)
        # print ("NO=%d"%(I))
        # TIRE.PrintList(dual)
        for i in range(I):
            n11 = dual[i][0][0]
            n12 = dual[i][0][1]
            n21 = dual[i][1][0]
            n22 = dual[i][1][1]
            if n11 == n21:
                n01 = n11;     n02 = n12;     n03 = n22
            elif n11 == n22:
                n01 = n11;     n02 = n12;     n03 = n21
            elif n12 == n21:
                n01 = n12;     n02 = n11;     n03 = n22
            else:
                n01 = n12;     n02 = n11;     n03 = n21
            
            T1 = TNode.NodeByID(n02)
            T2 = TNode.NodeByID(n03)
            T0 = (T1[4]+T2[4])/2.0
            J = len(TNode.Node)
            for j in range(J):
                if TNode.Node[j][0] == n01:
                    TNode.Node[j][4] = T0
                    break

        BT = Element.Elset("BT3")
        if len(BT.Element) ==0:
            BTEdge = Element.ElsetToEdge("BT2")
        else:
            BTEdge = Element.ElsetToEdge("BT3")
        
        N = len(BTEdge.Edge)
        BTEnd = 0
        BTStart = 0 
        for i in range(N):
            fs = 0
            fe = 0
            for j in range(N):
                if i != j and ( BTEdge.Edge[i][0] == BTEdge.Edge[j][1] ) :
                    fs =1 
                    break
                if i != j and ( BTEdge.Edge[i][1] == BTEdge.Edge[j][0] ) :
                    fe = 1
            if fs == 0:
                BTStart = BTEdge.Edge[i][0]
            if fe == 0:
                BTEnd = BTEdge.Edge[i][1]
            
        

        N = len(TNode.Node)
        for i in range(N):
            if TNode.Node[i][4]>MaxBeltT and TNode.Node[i][3] > SWz:
                MaxBeltT = TNode.Node[i][4]
            if TNode.Node[i][4]>MaxBeadT and TNode.Node[i][3] < SWz:
                MaxBeadT = TNode.Node[i][4]
                maxBdNode = TNode.Node[i]

            if TNode.Node[i][0] == BTStart: 
                BTStart = TNode.Node[i][4]
            if TNode.Node[i][0] == BTEnd: 
                BTEnd = TNode.Node[i][4]


        p = mp.Process(target=Plot_TemperatureDotting, args=[filename_base+'-Temperature', TNode, Element, 0.15E-3, 0.7, 150])
        processes.append(p)
        p.start()

    
    ######################################################################################
    # DLW/SLW, DLR/SLR, DRR
    ######################################################################################
    WaveLeft, WaveRight, DLW= TIRE.Plot_LoadedTireProfile (filename_base, SDB, lastSDB, SimCondition, mesh=str2DInp, tread=TreadNo, offset=Offset, sidewave=1)

    DeformedNode = TIRE.ResultSDB(SDB, lastSDB, Offset, TreadNo, 1, 0)
    I = len(DeformedNode.Node)
    MinZ = 9.9E20
    for i in range(I):
        if MinZ > DeformedNode.Node[i][3]:
            MinZ = DeformedNode.Node[i][3]

    RimNode = TIRE.GetRimCenter(lastsdb=lastSDB)
    DLR = abs(MinZ - RimNode.Node[0][3]) 
    # print (" ist...   DLR=%.2f,  DLW=%.2f"%(DLR*1000, DLW*1000))
    if SimCondition.Speed == 0.0: 
        # print ('## Static Loaded Dimension  ')
        # print ("   SLR=%.2f,  SLW=%.2f"%(DLR*1000, DLW*1000))
        pass
    else:
        DRR = TIRE.DRRonRoad(lastSDB, SimTime, SimCondition, offset=Offset, tread=TreadNo)
        # print ('## Dynamic Rolling Dimension  ')
        # print ("   DLR=%.2f, DRR=%.2f, DLW=%.2f"%(DLR*1000, DRR*1000, DLW*1000))
        
    
    
    # ######################################################################
    # ## Hysteresis Energy Loss Density
    # ######################################################################
    
        Angle = 0
        DeformedNode = TIRE.DeformedNode_SDB(lastSDB, angle=Angle, Offset=Offset, TreadNo=TreadNo)
        N = len(DeformedNode.Node)
        for i in range(N):
            DeformedNode.Node[i][0] = DeformedNode.Node[i][0] % Offset
        ELD = TIRE.EnergyLossDensity(lastSDB, offset=Offset, tread=TreadNo, sector=-2)
        
        N = len(Element.Element)
        M = len(ELD)
        
        for i in range(N):
            Found = 0
            for j in range(M):
                if Element.Element[i][0] == ELD[j][0]%Offset: 
                    Value = ELD[j][1]
                    Found =1
                    break
            if Found == 1:
                Element.AddItem(Element.Element[i][0], Value)
            else:
                Element.AddItem(Element.Element[i][0], 0.0)
                
        PointDist = 0.2E-3
        ### TIRE.Plot_MappedContour(DeformedNode, Element, filename_base+'-Hysteresis', 150, 0, 1.5, 0.99, PointGap=PointDist)

        p = mp.Process(target=Plot_MappedContour, args=[DeformedNode, Element, filename_base+'-Hysteresis', 150, 0, 1.5, 0.99, PointDist])
        processes.append(p)
        p.start()
        for process in processes:
            process.join()
        print ("Plot Energy Loss Density")
    
    ####################################################################################################################3
    t1 = time.time()
    fittingorder = 6
    Ribforce, RibArea, RibPressure, Widths = TIRE.PlotFootprint(filename_base, lastSDB, lastSFRIC, group=TireGroup, mesh2d= str2DInp, iter=steps, step =0, condition=SimCondition, offset=Offset, treadno=TreadNo, dpi=100, ribimage=0, vmin='', doe=isdoe, fitting=fittingorder, ribgraph=0, od=TireOD, shodrop=Shodrop, getvalue=1)
    # print ("Rib Normal Force(N)", Ribforce)
    text = "** Rib Normal Force(N) : "
    for txt in Ribforce: 
        text += str(format(txt, ".1f")) +", "
    text = text[:-2]
    print (text)
    # print ("Rib Contact Area(cm2)", RibArea)
    text = "** Rib Contact Area(cm2) : "
    for txt in RibArea: 
        text += str(format(txt, ".1f")) +", "
    text = text[:-2]
    print (text)
    # print ("Rib Avg. Pressure(kPa)", RibPressure)
    text = "** Rib Avg. Pressure(kPa) : "
    for txt in RibPressure: 
        text += str(format(txt, ".1f")) +", "
    text = text[:-2]
    print (text)
    t2 = time.time()
    print ("** Contact Width Center = %.1f, Max = %.1f"%(Widths[1]*1000, Widths[0]*1000))
    print ("** RIB SHAPE DONE %.2f sec\n"%(t2-t1 ))

    ####################################################################################
    ## FPC  DATA 
    ####################################################################################
    isFPC = 1
    try:
        with open(FPCfile) as FPC:
            lines = FPC.readlines()
    except:
        isFPC = 0
        print ("** There is no 'FPC result' file!!")

    if isFPC == 1:
        N = len(lines)
        for i in range(N):
            data = list(lines[i].split("="))
            
            if "ContactLength(mm)" in data[0] and "max/center" in data[0]:
                values = list(data[1].split("/"))
                MaxContactLength = float(values[0].strip())
                CenterContactLength = float(values[1].strip())
                if "ContactLength(mm)" in data[0] and "15%/85%" in data[0]:
                    ContactLength15 = float(values[2].strip()) 
                    ContactLength85 = float(values[3].strip())
                if "ContactLength(mm)" in data[0] and "25%/75%" in data[0]:
                    ContactLength25 = float(values[2].strip()) 
                    ContactLength75 = float(values[3].strip())
            if "ContactWidth(mm)"  in data[0] and "max/center"  in data[0]:
                values = list(data[1].split("/"))
                MaxContactWidth = float(values[0].strip())
                CenterContactWidth = float(values[1].strip())
                if "ContactWidth(mm)" in data[0] and "15%/85%" in data[0]:
                    ContactWidth15 = float(values[2].strip()) 
                    ContactWidth85 = float(values[3].strip())
                if "ContactWidth(mm)" in data[0] and "25%/75%" in data[0]:
                    ContactWidth25 = float(values[2].strip()) 
                    ContactWidth75 = float(values[3].strip())
                    
            if "SquareRatio" in data[0]:
                SquareRatio = float(data[1].strip())
            if "ContactRatio" in data[0]:
                ContactRatio = float(data[1].strip())
            if "Roundness(%)" in data[0]:
                Roundness = float(data[1].strip())
                
            if "ActualContactArea" in data[0]:
                ActualContactArea = float(data[1].strip())
            if "TotalContactArea" in data[0]:
                TotalContactArea = float(data[1].strip())
                
            if "DetailedContactLength" in data[0]:
                ContactLength={}
                items = list(data[0].split())
                items = list(items[1].split("/"))
                values = list(data[1].split("/"))
                
                M = len(items)
                for j in range(M):
                    ContactLength[items[j].strip()] = float(values[j].strip())
            if "DetailedContactWidth" in data[0]:
                ContactWidth={}
                items = list(data[0].split())
                items = list(items[1].split("/"))
                values = list(data[1].split("/"))
                
                M = len(items)
                for j in range(M):
                    ContactWidth[items[j].strip()] = float(values[j].strip())

            if "From" in data[0] and "To" in data[0]: 
                
                Rib=[]
                data=list(data[0].split())
                M = len(data)
                tmp = []
                for j in range(M):
                    if "From" in data[j] or "To" in data[j] or "Length" in data[j] or "Area" in data[j] or "Press" in data[j] or "Force" in data[j] : 
                        if "Total" in data[j]:
                            continue
                        tmp.append(data[j].strip())
                Rib.append(tmp)

                i += 1
                while lines[i][0] != '\n':
                    values = list(lines[i].split())
                    M = len(values)
                    tmp = []
                    for j in range(M):
                        tmp.append(float(values[j].strip()))
                    Rib.append(tmp)
                    i+=1
        ############################################################# Verification
        print ("## Length/Width : Max, Center, (25/15)%, (75/85)%")
        MaxContactWidth = str(round(Widths[0]*1000, 1))
        CenterContactWidth = str(round(Widths[1]*1000, 1))
        ContactWidth15 = str(round(Widths[2]*1000, 1))
        ContactWidth25 = str(round(Widths[3]*1000, 1))
        ContactWidth75 = str(round(Widths[4]*1000, 1))
        ContactWidth85 = str(round(Widths[5]*1000, 1))
        if IsTBR == 1 :
            print ("   Contact Length : %.3f, %.3f, %.3f, %.3f"%(float(MaxContactLength), float(CenterContactLength), float(ContactLength15), float(ContactLength85)))
            print ("   Contact Width  : %.3f, %.3f, %.3f, %.3f"%(float(MaxContactWidth), float(CenterContactWidth), float(ContactWidth15), float(ContactWidth85)))
        else:
            print ("   Contact Length : %.3f, %.3f, %.3f, %.3f"%(float(MaxContactLength), float(CenterContactLength), float(ContactLength25), float(ContactLength75)))
            print ("   Contact Width  : %.3f, %.3f, %.3f, %.3f"%(float(MaxContactWidth), float(CenterContactWidth), float(ContactWidth25), float(ContactWidth75)))
        
        SumRibArea = 0
        for val in RibArea:
            SumRibArea += val
        CalTotalArea = SumRibArea + (float(TotalContactArea) - float(ActualContactArea))
        CalRoundness = CalTotalArea / (float(CenterContactLength) * float(CenterContactWidth))*10000

        print ("   ActualContactArea [cm2] : %.3f -> %.3f"%(float(ActualContactArea), SumRibArea))
        print ("   TotalContactArea [cm2] : %.3f -> %.3f"%(float(TotalContactArea), CalTotalArea))
        print ("   Roundness [%%] : %.2f -> %.2f"%(float(Roundness), CalRoundness))
        ActualContactArea = SumRibArea
        TotalContactArea = CalTotalArea
        Roundness = CalRoundness

        print ("## Contact Length Detail ")
        print (ContactLength)
        # print ("## Contact Length Detail", ContactLength)
        print ("## Rib Values")        
        N = len(Rib)
        for i in range(N):
            print (Rib[i])
        
        SquareRatio15= float(round(ContactLength["15"]/ContactLength["50"] * 100, 3))
        SquareRatio85= float(round(ContactLength["85"]/ContactLength["50"] * 100, 3))

        print ("## Square Ratio 15%% = %f"%(float(SquareRatio15)))
        print ("   Square Ratio 85%% = %f"%(float(SquareRatio85)))
        print ("   Square Ratio TB  = %f"%((SquareRatio15*0.5 + SquareRatio85 * 0.5)))
        ContactLengthRatioTB = round(ContactLength["15"]/ContactLength["85"] * 100, 3)
        print ("   Contact Length Ratio (15%%/85%%)= %.2f"%(ContactLengthRatioTB))
        SquareRatio25= round(ContactLength["25"]/ContactLength["50"] * 100, 3)
        SquareRatio75= round(ContactLength["75"]/ContactLength["50"] * 100, 3)
        print ("## Square Ratio 25%% = %.2f"%(SquareRatio25))
        print ("   Square Ratio 75%% = %.2f"%(SquareRatio75))
        print ("   Square Ratio PCLT= %.2f"%((SquareRatio25*0.5 + SquareRatio75 * 0.5)))
        ContactLengthRatioPCLT = round(ContactLength["25"]/ContactLength["75"] * 100, 3)
        print ("   Contact Length Ratio (25%%/75%%) = %.2f"%(ContactLengthRatioPCLT))

            
        M = len(Rib[0]) 
        N = len(Rib)       
        KEY = "Area"
        for i in range(M):
            if KEY in Rib[0][i]:
                iKey = i
                break
        names = []
        areavalues = []
        for i in range(1, N):
            names.append("RIB"+str(i))
            areavalues.append(round(Rib[i][iKey], 1))
        # print ("AREA:", RibArea)

        # Ribforce, RibArea, RibPressure
        for i, val in enumerate(RibArea): 
            RibArea[i] = round(val, 1)
        # print (RibArea)
        cnt = 0 
        if len(names) != len(RibArea): 
            # print (len(names), ", ",  len(RibArea))
            for va in RibArea: 
                if round(va, 1) ==0: cnt +=1
            # print (len(names), ", ",  len(RibArea)- cnt)
            if len(RibArea) - cnt == len(names): 
                # print (" matched ")
                temp = []
                for va in RibArea: 
                    if va > 0: 
                        temp.append(va)
                        # print (" IN", va)
                    # else:    print (" OUT", va)
                RibArea = temp

        # print (RibArea)
        TIRE.Plot_BarChart(filename_base+"-Ribarea", names, RibArea, title="Rib Contact Area[cm2]", value = 1)

        areavalues = []
        for i in range(1, N):
            areavalues.append(Rib[i][iKey])
        
        
        KEY = "Press"
        for i in range(M):
            if KEY in Rib[0][i]:
                iKey = i
                break
        names = []
        pressvalues = []
        for i in range(1, N):
            names.append("RIB"+str(i))
            pressvalues.append(round(Rib[i][iKey]/1000, 2))
        # print ("PRESS:", RibPressure)
        for i, val in enumerate(RibPressure): 
            RibPressure[i] =  round(val, 1)
        cnt = 0 
        if len(names) != len(RibPressure): 
            for va in RibPressure: 
                if round(va, 1) ==0: cnt +=1
            if len(RibPressure) - cnt == len(names): 
                temp = []
                for va in RibPressure: 
                    if va > 0: 
                        temp.append(va)
                RibPressure = temp
        TIRE.Plot_BarChart(filename_base+"-Ribpressure", names, RibPressure, title="Rib Average Contact Pressure [kPa]", value=1)

        pressvalues = []
        for i in range(1, N):
            pressvalues.append(Rib[i][iKey]/1000)
        
        KEY = "Force"
        for i in range(M):
            if KEY in Rib[0][i]:
                iKey = i
                break
        ################## print iKey 
        names = []
        forcevalues = []
        for i in range(1, N):
            names.append("RIB"+str(i))
            forcevalues.append(round(Rib[i][iKey]/9.8, 1))
        # print ("FORCE:", Ribforce)
        for i, val in enumerate(Ribforce): 
            Ribforce[i] = round(val/9.8, 1)

        cnt = 0 
        if len(names) != len(Ribforce): 
            for va in Ribforce: 
                if round(va, 1) ==0: cnt +=1
            if len(Ribforce) - cnt == len(names): 
                temp = []
                for va in Ribforce: 
                    if va > 0: 
                        temp.append(va)
                Ribforce = temp

        TIRE.Plot_BarChart(filename_base+"-Ribforce", names, Ribforce, title="Rib Total Contact Force [kgf]", value =1)

        forcevalues = []
        for i in range(1, N):
            forcevalues.append(Rib[i][iKey]/9.8)
    

    ######################################################################################################################
    if CorneringStiffnessSimulation == 0: 
        if doe != "":
            rimfile = dirname+ "REPORT/frc_"+strSimCode+".rpt"
            LossFile= dirname + "REPORT/vis_"+strSimCode+".rpt"
        else:
            rimfile = strJobDir + "/REPORT/frc_"+strSimCode+".rpt"
            LossFile= strJobDir + "/REPORT/vis_"+strSimCode+".rpt"

    if SimCondition.Speed > 0:     
        RimForce = TIRE.RIMFORCE(rimfile)    
        
        LateralForce = RimForce.FY
        AligningMoment = RimForce.MZ 
        
        print ("## Lateral Force on Axle       = %f N"%(LateralForce))
        print ("## Self-Aligning Moment on Axle= %f N-m"%(AligningMoment))
        
        
        with open(LossFile) as LOSS:
            line = LOSS.readlines()
            
        LossBSW = 0.0
        LossTRD = 0.0
        LossFIL = 0.0
        LossTotal = 0.0
        N = len(line)
        for i in range(N) :
            if 'BSW' in line[i] : 
                data = list(line[i].split())
                LossBSW += float(data[4].strip())
            if 'CTB' in line[i] : 
                data = list(line[i].split())
                LossTRD += float(data[4].strip())
            if 'SUT' in line[i] : 
                data = list(line[i].split())
                LossTRD += float(data[4].strip())
            if 'TRW' in line[i] : 
                data = list(line[i].split())
                LossTRD += float(data[4].strip())
            if 'FIL' in line[i] : 
                data = list(line[i].split())
                LossFIL += float(data[4].strip())
            if 'UBF' in line[i] : 
                data = list(line[i].split())
                LossFIL += float(data[4].strip())
            if 'LBF' in line[i] : 
                data = list(line[i].split())
                LossFIL += float(data[4].strip())
            if 'TOTAL_RR' in line[i] : 
                i += 2
                data = list(line[i].split())
                LossTotal = float(data[1].strip())  
        print ("# Rolling Resistance [N] ")
        print ("  TREAD: %.2f, SIDEWALL: %.2f, FILLER: %.2f, TOTAL: %.2f"%(LossTRD, LossBSW, LossFIL, LossTotal))
    
    
    # SquareRatio85, SquareRatio75
    
    # lstdoeid = os.getcwd()
    # resultfile = lstdoeid.split("/")[-1]
    # print "###############################",strSimCode
    if SimCondition.Speed == 0:
        f = open(filename_base+'-Staticfootprint.txt', 'w')
    else:
        f = open(filename_base+'-Rollingcharacteristics.txt', 'w')

    if SimCondition.Speed == 0: 
        line = 'SF_SLR[mm]=' + str(format(DLR*1000, '.3f'))+'\n'
        f.writelines(line)
        line = 'SF_SLW[mm]=' + str(format(DLW*1000, '.3f'))+'\n'
        f.writelines(line)
        # line = 'SNOW SCORE [index]=' + str(snowscore)+'\n'
        ## snow score = 1.199 * 32 / 25.4 * GD - 116.975 * (1 - Total Area / (L * W)) + 29.601 * Length / Width + 85.005
        ## regardless of Tan d, sipe density  
        if isFPC == 1:       
            snowscore = 1.199 * 32.0 /25.4 * float(Groovedepth) - 116.975 * (1 - float(TotalContactArea)*100.0 /(float(MaxContactWidth)*float(MaxContactLength)) )\
                 + 29.601 * float(MaxContactLength) / float(MaxContactWidth) + 85.005
            line = 'SNOW SCORE =' + str(snowscore)+'\n'
            f.writelines(line)
            print (line[:-1])
    
    else:
        ca = LateralForce
        line = 'DF_Cornering Force[N]=' + str(format(ca, '.6f'))+'\n'
        f.writelines(line)
            
        line = 'DF_DLR[mm]=' + str(format(DLR*1000, '.3f'))+'\n'
        f.writelines(line)
        line = 'DF_DLW[mm]=' + str(format(DLW*1000, '.3f'))+'\n'
        f.writelines(line)
        line = 'DF_DRR[mm]=' + str(format(DRR*1000, '.3f'))+'\n'
        f.writelines(line)
        line = 'DF_Temperature Max Crown=' + str(format(MaxBeltT, '.3f'))+'\n'
        f.writelines(line)
        line = 'DF_Temperature Max Bead=' + str(format(MaxBeadT, '.3f'))+'\n'
        f.writelines(line)
        line = 'DF_Energy Loss Total[J]=' + str(format(LossTotal, '.4f'))+'\n'
        f.writelines(line)

        text = '\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!'
        f.write(text)
    f.close()


    if SimCondition.Speed == 0:
        f = open(filename_base+'-DOE-Staticfootprint.txt', 'w')
    else:
        f = open(filename_base+'-DOE-Rollingcharacteristics.txt', 'w')

    if isFPC == 1:
        line = str(rev) + ', Contact Length Max[mm]=' + str(MaxContactLength)+'\n'
        f.writelines(line)
        line = str(rev) + ', Contact Length Center[mm]=' + str(CenterContactLength)+'\n'
        f.writelines(line)
        
        line = str(rev) + ', Contact Length 15%[mm]=' + str(ContactLength["15"])+'\n'
        f.writelines(line)
        line = str(rev) + ', Contact Length 25%[mm]=' + str(ContactLength["25"])+'\n'
        f.writelines(line)
        # line = str(rev) + ', Contact Length 50%[mm]=' + str(ContactLength["50"])+'\n'
        # f.writelines(line)
        line = str(rev) + ', Contact Length 75%[mm]=' + str(ContactLength["75"])+'\n'
        f.writelines(line)
        line = str(rev) + ', Contact Length 85%[mm]=' + str(ContactLength["85"])+'\n'
        f.writelines(line)
        ContactLengthRatioPCLT = round(ContactLength["25"]/ContactLength["75"] * 100, 3)
        line = str(rev) + ', Contact Length Ratio 25%/75%[%]=' + str(ContactLengthRatioPCLT)+'\n'
        f.writelines(line)
        ContactLengthRatioTB = round(ContactLength["15"]/ContactLength["85"] * 100, 3)
        line = str(rev) + ', Contact Length Ratio 15%/85%[%]=' + str(ContactLengthRatioTB)+'\n'
        f.writelines(line)
        
        
        line = str(rev) + ', Contact Width Max[mm]=' + str(MaxContactWidth)+'\n'
        f.writelines(line)
        line = str(rev) + ', Contact Width Center[mm]=' + str(CenterContactWidth)+'\n'
        f.writelines(line)
        line = str(rev) + ', Contact Width 15%[mm]=' + str(ContactWidth15)+'\n'
        f.writelines(line)
        line = str(rev) + ', Contact Width 25%[mm]=' + str(ContactWidth25)+'\n'
        f.writelines(line)
        # line = str(rev) + ', Contact Width 50%[mm]=' + str(ContactWidth50)+'\n'
        # f.writelines(line)
        line = str(rev) + ', Contact Width 75%[mm]=' + str(ContactWidth75)+'\n'
        f.writelines(line)
        line = str(rev) + ', Contact Width 85%[mm]=' + str(ContactWidth85)+'\n'
        f.writelines(line)
        
        line = str(rev) + ', Square Ratio 15%[%]=' + str(SquareRatio15)+'\n'
        f.writelines(line)
        line = str(rev) + ', Square Ratio 25%[%]=' + str(SquareRatio25)+'\n'
        f.writelines(line)
        line = str(rev) + ', Square Ratio 75%[%]=' + str(SquareRatio75)+'\n'
        f.writelines(line)
        line = str(rev) + ', Square Ratio 85%[%]=' + str(SquareRatio85)+'\n'
        f.writelines(line)
        
        
        line = str(rev) + ', Actual Contact Area[cm2]=' + str(ActualContactArea)+'\n'
        f.writelines(line)
        line = str(rev) + ', Total Contact Area[cm2]=' + str(TotalContactArea)+'\n'
        f.writelines(line)
        line = str(rev) + ', Roundness [Total Area/(Center Length*Center Width) %] =' + str(format(Roundness, ".2f"))+'\n'
        f.writelines(line)
        
        N = len(Ribforce)
        ForceRatio =   Ribforce[0] / Ribforce[N-1]
        line = str(rev) + ', Rib Contact Force Ratio [ 1st / lst Rib %] =' + str(format(ForceRatio, ".2f"))+'\n'
        f.writelines(line)
        AreaRatio =   RibArea[0] / RibArea[N-1]
        line = str(rev) + ', Rib Contact Area Ratio [ 1st / lst Rib %] =' + str(format(AreaRatio, ".2f"))+'\n'
        f.writelines(line)
        
        I = len(RibArea)
        for i in range(I):
            line = str(rev) + ', Rib'+str(i+1)+'Force[kgf] =' + str(Ribforce[i])+'\n'
            f.writelines(line)
        for i in range(I):
            line = str(rev) + ', Rib'+str(i+1)+'Area[cm2] =' + str(RibArea[i])+'\n'
            f.writelines(line)
        for i in range(I):
            line = str(rev) + ', Rib'+str(i+1)+'Press[kPa] =' + str(RibPressure[i])+'\n'
            f.writelines(line)
    
    
    
    if SimCondition.Speed == 0: 
        
        line = str(rev) + ', SLR[mm]=' + str(format(DLR*1000, '.3f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', SLW[mm]=' + str(format(DLW*1000, '.3f'))+'\n'
        f.writelines(line)
        # line = str(rev) + ', SNOW SCORE [index]=' + str(snowscore)+'\n'
        ## snow score = 1.199 * 32 / 25.4 * GD - 116.975 * (1 - Total Area / (L * W)) + 29.601 * Length / Width + 85.005
        ## regardless of Tan d, sipe density         
        if isFPC == 1:
            line = str(rev) + ', SNOW SCORE =' + str(format(snowscore, ".2f"))+'\n'
            f.writelines(line)
            print (line[:-1])
        
    
    else:
    
        ca = LateralForce
        line = str(rev) + ', Cornering Force[N]=' + str(format(ca, '.6f'))+'\n'
        f.writelines(line)
        aa = AligningMoment 
        line = str(rev) + ', Aligning Moment[N-m]=' + str(format(aa, '.6f'))+'\n'
        f.writelines(line)
            
        line = str(rev) + ', DLR[mm]=' + str(format(DLR*1000, '.3f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', DLW[mm]=' + str(format(DLW*1000, '.3f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', DRR[mm]=' + str(format(DRR*1000, '.3f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', Temperature Max Crown=' + str(format(MaxBeltT, '.3f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', Temperature Max Bead=' + str(format(MaxBeltT, '.3f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', Temperature Belt Edge Right=' + str(format(BTStart, '.3f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', Temperature Belt Edge Left=' + str(format(BTEnd, '.3f'))+'\n'
        f.writelines(line)
        
        
        line = str(rev) + ', Energy Loss Total[N Force]=' + str(format(LossTotal, '.4f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', Energy Loss Crown[N Force]=' + str(format(LossTRD, '.4f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', Energy Loss Sidewall[N Force]=' + str(format(LossBSW, '.4f'))+'\n'
        f.writelines(line)
        line = str(rev) + ', Energy Loss Filler[N Force]=' + str(format(LossFIL, '.4f'))+'\n'
        f.writelines(line)
    f.close()
    
    if isFPC == 1 and TireGroup =="TBR":
        with open(FPCfile) as FPC:
            lines = FPC.readlines()
        for i, line in enumerate(lines):
            if "ActualContactArea" in line :  lines[i] = "ActualContactArea(cm^2)=\t" + str(format(ActualContactArea, ".1f"))+"\n"
            if "TotalContactArea" in line :  lines[i] = "TotalContactArea(cm^2)=\t" + str(format(TotalContactArea, ".1f"))+"\n"
            if "ContactWidth(mm)  max/center/15%/85%=" in line :  lines[i] = "ContactWidth(mm)  max/center/15%/85%=\t" + str(format(float(MaxContactWidth), ".1f")) + "/"+ str(format(float(CenterContactWidth), ".1f")) + "/"+ str(format(float(ContactWidth15), ".1f")) + "/"+ str(format(float(ContactWidth85), ".1f")) + "\n"
            if "ContactWidth(mm)  max/center/25%/75%=" in line :  lines[i] = "ContactWidth(mm)  max/center/15%/85%=\t" + str(format(float(MaxContactWidth), ".1f")) + "/"+ str(format(float(CenterContactWidth), ".1f")) + "/"+ str(format(float(ContactWidth25), ".1f")) + "/"+ str(format(float(ContactWidth75), ".1f")) + "\n"

            calContactRatio = ActualContactArea / TotalContactArea * 100
            if "ContactRatio" in line :  lines[i] = "ContactRatio(%)=\t" + str(format(calContactRatio, ".1f"))+"\n"
            if "Roundness(%)=" in line :  lines[i] = "Roundness(%)=\t"  + str(format(Roundness, ".1f"))+"\n"
            if "DetailedContactWidth(mm)" in line :  lines[i] = "DetailedContactWidth(mm) 15/25/50/75/85=\t" + str(format(float(ContactWidth15), ".1f")) + "/"+ str(format(float(ContactWidth25), ".1f")) + "/"+ str(format(float(CenterContactWidth), ".1f")) + "/"+ str(format(float(ContactWidth75), ".1f")) + "/"+ str(format(float(ContactWidth85), ".1f")) + "\n"

        f = open(FPCfile, "w")
        f.writelines(lines)
        f.close()
    
    
    err.close()
    tend = time.time()
    print ("DURATION - After Footprint ", tend-tstart)
    # print "DONE!!!!!!!!!!"

    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass
    