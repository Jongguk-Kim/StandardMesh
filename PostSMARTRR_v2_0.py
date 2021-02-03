import glob, os, json, math, sys
import time
try:
    import CommonFunction as TIRE
except: 
    import CommonFunction_v2_0 as TIRE
import multiprocessing as mp
try:
    import CheckExecution
except: 
    pass 

class DynamicDimension:
    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        self.DLR=0.0
        self.DRR=0.0
        self.DLW=0.0
        self.WaveRight=[]
        self.WaveLeft=[]
    def Addvalue(self,  dlr, drr, dlw, left, right):
        self.DLR=dlr
        self.DRR=drr
        self.DLW=dlw
        self.WaveLeft.append(left)
        self.WaveRight.append(right)

def Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, dpi, Rangemin, RangeMax, NR, PointGap, ColorMax, step=0, imagefile="image", Offset=10000, TreadNo=10000000, simtime='', lastsdb=''):
    AngleNode  = TIRE.GetDeformedNodeAtAngleFromSDB(DeformedNodeFile, Angle, Step=0, Offset=Offset, TreadNo=TreadNo, simtime=SimTime, lastsdb=strLastSDBFile)
    TIRE.Plot_AngleMappedELDContour(AngleNode,SEDFile, Angle, Offset, Element, imagefile, dpi, Rangemin, RangeMax, NR, PointGap,  ColorMax, simtime=SimTime, lastsdb=strLastSDBFile)

if __name__ == "__main__":
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass 
    Tstart = time.time()
    TreadNo = 10000000
    Offset = 10000

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

    if doe == '':
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
        errFile = strSimCode + '.err'

        SimTime = TIRE.SIMTIME(strSimCode+'.inp')
        SimCondition = TIRE.CONDITION(strSimCode+'.inp')

        filename_base = strSimCode
        # rev = lstSnsInfo["VirtualTireBasicInfo"]["HiddenRevision"]
        rev = strSimCode.split("-")[2]
        # print (strSimCode.split("-")[2])

    else:
        with open(snsfile) as Sns_file:
            lstSnsInfo = json.load(Sns_file)

        strSimCode = lstSnsInfo["AnalysisInformation"]["SimulationCode"]
        TreadDesignWidth = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"])
        groovedepth = float(lstSnsInfo["VirtualTireParameters"]["MainGrooveDepth"])
        tiregroup = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]
        TreadDesignWidth  = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"]) 

        SimTime = TIRE.SIMTIME(smart)
        SimCondition = TIRE.CONDITION(smart)

        lstSmart = smart.split("/")
        strJobDir = ''
        for i in range(len(lstSmart)-1): strJobDir += lstSmart[i]+'/'
        strJobDir = strJobDir[:-1]    

        errFile = smart[:-4] + '.err'

        filename_base =  smart[:-4] 
        rev = lstSnsInfo["VirtualTireBasicInfo"]["HiddenRevision"]
        


    err = open(errFile, 'w')
    #####################################################################
    ## Read Rolling Resistance of each Component!'
    #####################################################################
    TIRE.WriteComponentRRforRRSimulation(strSimCode, jobdir=strJobDir, simcond=SimCondition)
    LossFile = strJobDir + "/REPORT/vis_"+strSimCode+".rpt"
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
    print ("# Rolling Resistance[N] ")
    print ("  TREAD: %.2f, SIDEWALL: %.2f, FILLER: %.2f, TOTAL: %.2f"%(LossTRD, LossBSW, LossFIL, LossTotal))
    
    #####################################################################
    ## Temperature Contour
    #####################################################################
    # print "** Simulation Time :", SimTime.SimulationTime, ', Del Time', SimTime.DelTime, ', Averaging', SimTime.AveragingTime, ', Last Step', SimTime.LastStep
    try:
        Node, Element, Elset, Comment = TIRE.Mesh2DInformation(str2DInp)
    except:
        line = "ERROR::POST::[Rolling Resistance] - Cannot open 2D Mesh File (VT-Code.inp)+\n"
        err.writelines(line)
        err.close()
        try:
            CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        except:
            pass 

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
    
    # TNode = TIRE.GetDeformedNodeTemperatureFromSDB(strSimCode, 1001, Step=0, Offset=Offset, TreadNo=TreadNo)
    TNode = TIRE.GetDeformedNodeFromSDB(strSimCode, -1, Offset=Offset, TreadNo=TreadNo, jobdir=strJobDir, simtime=SimTime)
    MinZ = TNode.Node[0][3]
    MaxZ = TNode.Node[0][3]
    for nd in TNode.Node: 
        nd[0] %=Offset
        if MinZ > nd[3]:
            MinZ = nd[3]
        if MaxZ < nd[3]:
            MaxZ = nd[3]
    SWz= (MinZ+MaxZ)/2.0
    TNode.DeleteDuplicate()
    
    Outer = Element.OuterEdge(Node)
    I = len(Outer.Edge)
    dual = []
    for i in range(I):
        temp = []
        for j in range(i+1, I):
            if Outer.Edge[i][4] == Outer.Edge[j][4]:
                temp.append(Outer.Edge[i])
                temp.append(Outer.Edge[j])
                dual.append(temp)
                break
    I = len(dual)
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

    N = len(TNode.Node)
    MaxBeltT = 0.0
    MaxBeadT = 0.0
    MinZ = TNode.Node[0][4]
    MaxZ = TNode.Node[0][4]
    for i in range(N):
        if TNode.Node[i][4]>MaxBeltT and TNode.Node[i][3] > SWz:
            MaxBeltT = TNode.Node[i][4]
        if TNode.Node[i][4]>MaxBeadT and TNode.Node[i][3] < SWz:
            MaxBeadT = TNode.Node[i][4]
            maxBdNode = TNode.Node[i]

    BT = Element.Elset("BT3")
    if len(BT.Element) ==0:
        BTEdge = Element.ElsetToEdge("BT1")
    else:
        BTEdge = Element.ElsetToEdge("BT2")
    
    N = len(BTEdge.Edge)
    BTEdge.Sort(item=-1)
    BTStart = BTEdge.Edge[0][0]
    BTEnd   = BTEdge.Edge[N-1][1]
            
    N = len(TNode.Node)
    for i in range(N): 
        if TNode.Node[i][0] == BTStart: 
            BTStart = TNode.Node[i][4]
        if TNode.Node[i][0] == BTEnd: 
            BTEnd = TNode.Node[i][4]
            
    print ('## Temperature Max at Belt= %.1f, at Bead=%.1f'%(MaxBeltT, MaxBeadT))
    ImageFileName = filename_base + '-Temperature.png'
    TIRE.Plot_TemperatureDotting(ImageFileName, TNode, Element, 200)
    print ("## BT End Temperature = %.1f, %.1f, Average=%.1f"%(BTStart, BTEnd, (BTStart+BTEnd)/2.0))
    #####################################################################
    ## Dynamic Dimension
    #####################################################################
    if SimTime.SimulationTime == 0.0:
        strSDBDir = strJobDir + '/SDB_PCI.' + strSimCode
        sdbFileName = strJobDir + '/SDB_PCI.' + strSimCode + '/' + strSimCode + '.sdb'
    else:
        strSDBDir = strJobDir + '/SDB.' + strSimCode
        sdbFileName = strJobDir + '/SDB.' + strSimCode + '/' + strSimCode + '.sdb'

    strLastSDBFile =  sdbFileName + str(format(SimTime.LastStep, '03'))

    LeftWave, RightWave, DLW = TIRE.Plot_LoadedTireProfile(filename_base, sdbFileName,  strLastSDBFile, SimCondition, offset=Offset, Tread=TreadNo, sidewave=1, mesh=str2DInp, dpi=200)
    DLR = TIRE.DLR(diameter=SimCondition.Drum, lastsdb=strLastSDBFile)
    DRR = TIRE.DRRonDrum(strLastSDBFile, SimTime, SimCondition, offset=Offset, tread=TreadNo)
    print ('## Dynamic Dimension  ')
    print ("   DLR=%.2f, DRR=%.2f, DLW=%.2f"%(DLR*1000, DRR*1000, DLW*1000))

    DynamicResultFileName = filename_base + '-DynamicRadius.txt'  
    DRF=open(DynamicResultFileName, 'w')
    text = 'DLR='+str(format(DLR*1000, '10.3f'))+'\n'
    DRF.write(text)
    text = 'DRR=' + str(format(DRR*1000, '10.3f')) + '\n'
    DRF.write(text)
    text = '\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!' + '\n'
    DRF.write(text)
    DRF.close()

    ######################################################################
    ## Hysteresis Energy Loss Density
    ######################################################################
    TireOuter = Element.OuterEdge(Node)
    
    Angle = 0
    DeformedNode= TIRE.GetDeformedNodeAtAngleFromSDB(strSimCode, Angle, Step=0, Offset=Offset, TreadNo=TreadNo, simtime=SimTime, jobdir=strJobDir)
    N = len(DeformedNode.Node)
    for i in range(N):
        DeformedNode.Node[i][0] = DeformedNode.Node[i][0] % Offset
        
    SED = TIRE.GetELDatSectionSMART(strSimCode, -1, Option='Sector', Offset=Offset, TreadNo=TreadNo, Step=0,   jobdir=strJobDir, simtime=SimTime)
    
    N = len(Element.Element)
    M = len(SED)
    
    for i in range(N):
        Found = 0
        for j in range(M):
            if Element.Element[i][0] == SED[j][0]: 
                Value = SED[j][1]
                Found =1
                break
        if Found == 1:
            Element.AddItem(Element.Element[i][0], Value)
        else:
            Element.AddItem(Element.Element[i][0], 0.0)
            
    PointDist = 0.15E-3
    TIRE.Plot_MappedContour(DeformedNode, Element, filename_base+'-Hysteresis', 150, 0, 1.5, 0.99, PointGap=PointDist)
    
    ######################################################################
    ## Energy Loss Density at Specific Angle when rotating 
    ######################################################################
    DeformedNodeFile = strSimCode + '-NodeTemperature.tmp'
    SEDFile = strSimCode + '-EnergyLoss.tmp'
    SED = TIRE.GetELDatSectionSMART(SEDFile, 0, Option="Sector", Offset=Offset, TreadNo=TreadNo, Step=0, simtime=SimTime)
    
    AvgSED = TIRE.Mean(SED, 1)
    StdevSED  = TIRE.StandardDeviation(SED, 1)
    
    # print "Standard Dev SED", format(StdevSED, '.0f'), 'AVG', format(AvgSED, '.0f')
    
    print ("# Standard Deviation of SED=%.0f, Avg=%.0f"%(StdevSED, AvgSED))
    multi = 4.5
    ColorMax = AvgSED + StdevSED * multi 

    # Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, dpi, Rangemin, RangeMax, NR, PointGap, ColorMax, step=0, imagefile="image", Offset=10000, TreadNo=10000000, simtime='', lastsdb=''):
    imagename= filename_base+'-RRContour_0'
    Angle = 180.0
    Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile)

    imagename= filename_base+'-RRContour_m2'
    Angle = 178.0
    Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile)

    imagename= filename_base+'-RRContour_m4'
    Angle = 178.0
    Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile)

    imagename= filename_base+'-RRContour_m6'
    Angle = 174.0
    Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile)

    imagename= filename_base+'-RRContour_p2'
    Angle = 182.0
    Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile)

    imagename= filename_base+'-RRContour_p4'
    Angle = 184.0
    Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile)

    imagename= filename_base+'-RRContour_p6'
    Angle = 186.
    Hysteresis_angle(DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile)

    
    
    # processes = []
    # imagename= filename_base+'-RRContour_0'
    # Angle = 180.0
    # p0 = mp.Process(target=Hysteresis_angle, args=[DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile])
    # processes.append(p0)
    # p0.start()

    # imagename= filename_base+'-RRContour_m2'
    # Angle = 178.0
    # p1 = mp.Process(target=Hysteresis_angle, args=[DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile])
    # processes.append(p1)
    # p1.start()

    # imagename= filename_base+'-RRContour_m4'
    # Angle = 176.0
    # p2 = mp.Process(target=Hysteresis_angle, args=[DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile])
    # processes.append(p2)
    # p2.start()

    # imagename= filename_base+'-RRContour_m6'
    # Angle = 174.0
    # p3 = mp.Process(target=Hysteresis_angle, args=[DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile])
    # processes.append(p3)
    # p3.start()

    # imagename= filename_base+'-RRContour_p2'
    # Angle = 182.0
    # p4 = mp.Process(target=Hysteresis_angle, args=[DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile])
    # processes.append(p4)
    # p4.start()

    # imagename= filename_base+'-RRContour_p4'
    # Angle = 184.0
    # p5 = mp.Process(target=Hysteresis_angle, args=[DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile])
    # processes.append(p5)
    # p5.start()

    # imagename= filename_base+'-RRContour_p6'
    # Angle = 186.0
    # p6 = mp.Process(target=Hysteresis_angle, args=[DeformedNodeFile, Angle, SEDFile, Element, 100, 0, 1.5, 0.99, 0.15E-3, ColorMax, 0, imagename, Offset, TreadNo, SimTime, strLastSDBFile])
    # processes.append(p6)
    # p6.start()

    # for process in processes:
    #     process.join()
    
    if doe != '':
        cwd = os.getcwd()

        if rev == 0:
            f = open(cwd+"/"+doe+'-RR.txt', 'w')
        else:
            f = open(cwd+"/"+doe+'-RR.txt', 'a')
    else:
        f = open(filename_base+'-RR.txt', 'w')
        
    # print (filename_base+'-RR.txt   '+str(rev))
    line = str(rev) + ', Energy Loss Total[N Force] =' + str(format(LossTotal, '.4f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', Energy Loss Crown[N Force] =' + str(format(LossTRD, '.4f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', Energy Loss Sidewall[N Force] =' + str(format(LossBSW, '.4f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', Energy Loss Filler[N Force] =' + str(format(LossFIL, '.4f'))+'\n'
    f.writelines(line)
    
    line = str(rev) + ', DLR[mm]=' + str(format(DLR*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', DLW[mm]=' + str(format(DLW*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', DRR[mm]=' + str(format(DRR*1000, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', Temperature Max Crown=' + str(format(MaxBeltT, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', Temperature Max Bead=' + str(format(MaxBeadT, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', Temperature Belt Edge R=' + str(format(BTStart, '.3f'))+'\n'
    f.writelines(line)
    line = str(rev) + ', Temperature Belt Edge L=' + str(format(BTEnd, '.3f'))+'\n'
    f.writelines(line)
    
    f.close()

    err.close()

    os.system('rm -f *.tmp')
    os.system('rm -f *mValue.txt')
    os.system('rm -f *nValue.txt')
    Tend = time.time()
    print ('Duration RR =', round(Tend-Tstart, 2))
    
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass 




