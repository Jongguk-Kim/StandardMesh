
import math, time, shutil
import os, glob, sys, json
import Mesh2DScripts_v3_0 as Mesh2DScripts
import string, linecache, pickle
try: 
    import CheckExecution, StoreFile
    inISLM = 1
except: 
    inISLM = 0 


class GlobalVar:
    def __init__(self, value):
        self.value = value

    def Print(self):
        print (" = ", self.value)

def existEL(SetName, Elsets):

    Exist =0
    for i in range(len(Elsets)):
        if SetName in Elsets[i][0]:
            Exist = 1
            break
    return Exist
def CheckFileName(fileName, ErrorFile):
    filePath = fileName + '.inp'
    inpFile = open(filePath, 'r')
    lineCount = len(inpFile.readlines())
    inpFile.close()
    if lineCount < 1:
        ErrorFile.writelines('Error::Pre::[Input] Model information tranferred in CUTE is empty!')
        return -1
    else:
        return 0

    #     #########################################################################
    #     ## Written by Yoon for the file management - copy and check
    #     #########################################################################
    #     if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    #     strJobDir = os.getcwd()
    #     lstSnsFileNames = glob.glob(strJobDir + '/*.sns')
    #     strSnsFileName = lstSnsFileNames[0]
    #
    #     with open(strSnsFileName) as data_file:
    #         jsSns = json.load(data_file)
    #
    #     strRootJobDir = '/home/fiper/ISLM/ISLM_JobFolder'
    #     # strProductCode = '1014500'
    #     strProductCode = str(jsSns["VirtualTireBasicInfo"]["ProductCode"])
    #     # strVirtualTireCode = '1014500VT00011-0'
    #     strVirtualTireCode = str(jsSns["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(jsSns["VirtualTireBasicInfo"]["HiddenRevision"])
    #     strVTDBLoc = str(jsSns["VirtualTireBasicInfo"]["VirtualTireDBLocation"])
    #     strProductVirtualTireDir = '/' + strVTDBLoc + '/' + strProductCode + '/' + strVirtualTireCode
    #     strCheckLifecycle = 'JobComplete'
    #
    #     if os.access(strRootJobDir + strProductVirtualTireDir + '/' + strVirtualTireCode + '-2DMesh.png', os.F_OK):
    #         print '[ISLM::2DLayout] The 2D mesh image already exist!!'
    #         sys.exit()
    #
    # ############################################################################

def Equivalent_density_calculation(cute_mesh, filename=""): 
    # print ("\n************************************************** ")
    # print ("** Equilivalent Density Calculation")
    # print ("************************************************** ")
    PI = 3.14159265358979
    with open(cute_mesh) as MS: 
        lines = MS.readlines()
    cmd = ''
    start = 0 
    solid=[]
    bdc = []
    roll = []
    for line in lines: 
        if "**" in line : 
            if "WEIGHT" in line: continue 
            if "END OF MATERIAL INFO" in line : 
                # print ("ENDING*********************")
                break 
            if "MATERIAL INFO" in line: 
                start = 1

            if "***" in line: continue
           
            

            if "COMPONENTS EXTRUDED" in line and start ==1: 
                cmd = 'solid'
                continue 
            if "BEAD CORE" in line and start ==1: 
                cmd = 'bead'
                continue 
            if "COMPONENTS ROLLED" in line and start ==1: 
                cmd = 'rolled'
                continue 

            if cmd == 'solid': 
                data = line.split(",")
                tmp = []
                for dt in data: 
                    tmp.append(dt.strip())
                solid.append(tmp)
                # print ("SOLID", tmp)

            if cmd == 'bead': 
                data = line.split(",")
                tmp = []
                for dt in data: 
                    tmp.append(dt.strip())
                bdc.append(tmp)
                # print ("BEAD", tmp)
                
            if cmd == 'rolled': 
                data = line.split(",")
                tmp = []
                for dt in data: 
                    tmp.append(dt.strip())
                roll.append(tmp)
                # print ("ROLLED", tmp)
    
    f = open(filename, "w") 
    if len(solid) ==0 and len(bdc) ==0 and len(roll) ==0: 
        f.close()
        return 
    print ("## Equivalent Density was saved in 'density.txt'\n")
    f.write("*SOLID\n")
    if len(solid) > 0: 
        for sd in solid: 
            name = sd[0].split("(")[0].strip()
            name = name[2:]
            compound = sd[1]
            density = float(sd[2]) * float(sd[3]) 
            f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%(name, compound, density, float(sd[5])/10**9, float(sd[6])))
    if len(bdc) > 0: 
        for sd in bdc: 
            name = sd[0].split("(")[0].strip()
            name = name[2:]
            compound = sd[1]
            density = float(sd[3]) / float(sd[2]) * 10**9 /1000
            f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%(name, compound, density, float(sd[2]) / 10**9, float(sd[3]) ))
    f.write("** CMP, CODE, density, Volume(m3), Weight(kg)\n")

    f.write("*REBAR\n")
    CCT = [];     BTT = [];     JEC = []; JFC=[]
    BDC = [];     SCT = [];     NCT = []
    if len(roll) > 0: 
        for sd in roll: 
            name = sd[0].split("(")[0].strip()
            name = name[2:]
            code =sd[1]
            structure = sd[2]
            try: 
                EPI = float(sd[3])
                dia = float(sd[4])/1000.0
                topping = sd[5]
                ga = float(sd[6]) /1000
                cf = float(sd[7])
                rf = float(sd[8])
                wt = float(sd[11])
                if "ES" in code: 
                    Area = Area_steel_cord(structure)
                else: 
                    Area = PI * dia**2 / 4.0 

                toping_density = rf*10.0 / ga /1000
                cord_density =  cf / 100.0 / Area / 39.37 / EPI
                line_density = cf * 10.0 /39.37 / EPI 
                real_rubber_volume = ga - Area * 39.37 * EPI 
                topping_real_density = rf*10 / real_rubber_volume /1000

                # print ("real density ", topping_real_density)

                f.write("%6s, %8s, %.5f, %.5f, %.5e, %.5f, %.5f, %.5f, %.3f, %.3f, %.3e\n"%(\
                        name, code, toping_density, cord_density, line_density, topping_real_density, rf, cf, wt * cf/(cf+rf), wt * rf/(cf+rf), Area))

                if "C01" in name:   CCT = [name, topping, toping_density, float(sd[10])/10**9, wt * rf/(cf+rf)]
                if "BT2" in name:   BTT = [name, topping, toping_density, float(sd[10])/10**9, wt * rf/(cf+rf)]
                if "JEC" in name:   JEC = [name, topping, toping_density, float(sd[10])/10**9, wt * rf/(cf+rf)]
                if "JFC" in name:   JFC = [name, topping, toping_density, float(sd[10])/10**9, wt * rf/(cf+rf)]
                # if "BDC" in name:   BDC = [name, topping, toping_density, float(sd[10])/10**9, wt * rf/(cf+rf)]
                if "CH1" in name:   SCT = [name, topping, toping_density, float(sd[10])/10**9, wt * rf/(cf+rf)]
                if "CH2" in name:   NCT = [name, topping, toping_density, float(sd[10])/10**9, wt * rf/(cf+rf)]
                
            except:
                pass 

    f.write("** CMP, CODE, Equi-Toping Density, Equi-Cord Dentidy, Line Density, Real-topping density, Rubber factor, cord factor, volume, cord_wt, rubber_wt, area\n")

    f.write("*SOLID\n")
    if len(CCT) > 0: f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%('CCT', CCT[1], CCT[2], CCT[3], CCT[4] ))
    if len(BTT) > 0: f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%('BTT', BTT[1], BTT[2], BTT[3], BTT[4] ))
    if len(JEC) > 0 and len(JFC) ==0 : f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%('JBT', JEC[1], JEC[2], JEC[3], JEC[4] ))
    if len(JFC) > 0: f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%('JBT', JFC[1], JFC[2], JFC[3], JFC[4] ))
    # if len(BDC) > 0: f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%("BDT", BDC[1], BDC[2], BDC[3], BDC[4] ))
    if len(SCT) > 0: f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%('SCT', SCT[1], SCT[2], SCT[3], SCT[4] ))
    if len(NCT) > 0: f.write("%6s, %7s, %.5f, %.3e, %.5f\n"%('NCT', NCT[1], NCT[2], NCT[3], NCT[4] ))

    f.close()
    # print ("************************************************** ")

def Area_steel_cord(cord, wrapping_dia=0.15e-3): 
    PI = 3.14159265358979 
    name = cord.upper().strip()
    if "W" in name: 
        wrp = 1 
        name = name.split("W")[0]
    else: 
        wrp = 0 
    # print (name)
    if name[-1:] == "+": 
        name = name[:-1]
    # print (name, len(name))
    for i in range(len(name)-1, 0, -1): 
        if ")" == name[i]: 
            name = name[:i+1]
            break 
    # print (name, end=" -> ")

    layer = 1;     ls = 0;     lr = 0;     lx = 0 
    fname =''
    for i in range(len(name)): 
        if name[i] == '/' : 
            ls += 1 
            layer += 1 
            fname += "+"
        elif name[i] == '+' : 
            lr += 1 
            layer += 1 
            fname += name[i]
        elif name[i] == 'X' : 
            lx += 1 
            fname += name[i]
        else: 
            fname += name[i]
    # print (fname)
    # print ("layer=%d, same_dir=%d, rev_dir=%d, cross=%d, wrap=%d"%(layer, ls, lr, lx, wrp))

    layers = fname.split("+")
    # print (layers)
    area = 0.0
    nWire = 0 
    for layer in layers: 
        if "X" in layer: 
            wires = layer.split("X")
            w1 = float(wires[0])
            if "(" in wires[1]: 
                wire = wires[1].split("(")
                w2 = float(wire[0])
                dia = float(wire[1].split(")")[0]) /1000.0 
            else: 
                w2 = float(wires[1])
                dia = 0  
            nWire += w1 * w2 
            if dia > 0: 
                # print ("   >> ", layer, " Area Cal : dia=%.3f cord N=%d"%(dia*1000, nWire))
                area += nWire * dia**2* PI/4.0
                nWire = 0 
        else: 
            if "(" in layer: 
                wire = layer.split("(")
                nWire += float(wire[0])
                dia = float(wire[1].split(")")[0]) /1000.0 
            else: 
                nWire += float(layer)
                dia = 0 
            if dia > 0: 
                # print ("   >> ", layer, " Area Cal : dia=%.3f cord N=%d"%(dia*1000, nWire))
                area += nWire * dia**2* PI/4.0
                nWire = 0 
    if wrp ==1: 
        area += wrapping_dia**2* PI/4.0 
    
    # print ("Area=%.3e"%(area)) 
    return area




if __name__=='__main__':
    if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    Tstart = time.time()
    ####################################################################################################
    ## Constants and Options
    ####################################################################################################
    
    ####################################################################################################
    ## Changed scripts for DOE 
    ####################################################################################################
    treadno = 10000000
    offset = 10000
    criticallength = 0.1E-3
    criticalangle = 15.0
    sns=''
    strJobDir = ''
    Mesh2DInpFileName = ''
    doeid = ''
    SMARToutput  =1 


    for i in range(1, len(sys.argv)):
        arg = sys.argv[i].split("=")
        if arg[0] == "treadno":
            treadno = int(arg[1])
        if arg[0] == "offset":
            offset = int(arg[1])
        if arg[0] == 'clength':
            criticallength = float(arg[1])
        if arg[0] == "cangle":
            criticalangle = float(arg[1])

        if arg[0] == "dir":
            strJobDir = arg[1]
        if arg[0] == "sns":
            sns = arg[1]
            
        if arg[0].lower() == "mesh" or arg[0].lower() == "m":
            Mesh2DInpFileName = arg[1] 
        if arg[0] == "doe":
            doeid = arg[1]
        if arg[0] == "smart":
            SMARToutput = int(arg[1])
        if arg[0].lower() == 'group' or arg[0] == 'g': 
            strTireGroup = arg[1].upper()


    TreadNumber = GlobalVar(treadno)
    OffsetSector = GlobalVar(offset)
    CriticalLength = GlobalVar(criticallength)
    CriticalAngle = GlobalVar(criticalangle)
    ####################################################################################################
    
    InsertBETWEENBELTS=1 
    SectorOption_Tread = 0 # 1 = length base, 0 = Angle base
    SectorOption_Body = 0  # 1 = length base, 0 = Angle base
    if SectorOption_Tread ==1: 
        DivTread = 5.0E-3
    else:
        DivTread = 240
    if SectorOption_Body == 1:
        DivBody = 5.0E-3
    else:
        DivBody = 240
    
    TreadElset = ['CTB', 'SUT', 'CTR', 'UTR', 'TRW']
    ChaferName = ['CH1', 'CH2', 'CH3']
    Write2DMesh = 1
    Plot2DMesh = 1
    SnsInfo = []

    if sns ==  '' and Mesh2DInpFileName=='':
        strJobDir = os.getcwd()
        snsFile = glob.glob(strJobDir + '/*.sns')
        ErrorFileName = snsFile[0][:-4] + '.err'
        ErrorFile = open(ErrorFileName, 'w')
        if len(snsFile) == 0:
            ErrorFile.writelines("Error::Pre::[INPUT] NO SNS FILE!!\n")
            if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
            sys.exit()

        i=0
        with open(snsFile[i]) as SNS:
            SnsInfo = json.load(SNS)

        file = ['', 0]
        fileName = str(SnsInfo["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(SnsInfo["VirtualTireBasicInfo"]["HiddenRevision"])
        ErrorFileName = str(SnsInfo["AnalysisInformation"]["SimulationCode"]) + '.err'
        fullErrorFileName = strJobDir + '/' + ErrorFileName
        fullTRDFileName = strJobDir + '/' + fileName + '.trd'
        fullAXIFileName = strJobDir + '/' + fileName + '.axi'

        isERRORFileExist = os.path.isfile(fullErrorFileName)
        isTRDFileExist = os.path.isfile(fullTRDFileName)
        isAXIFileExist = os.path.isfile(fullAXIFileName)

        if CheckFileName(fileName, ErrorFile) == -1:
            if inISLM == 1: 
                CheckExecution.getProgramTime(str(sys.argv[0]), "End")
                sys.exit()
        #     #########################################################################
        #     ## Written by Yoon for the file management - copy and check
        #     #########################################################################
        strRootJobDir = '/home/fiper/ISLM/ISLM_JobFolder'
        strProductCode = str(SnsInfo["VirtualTireBasicInfo"]["ProductCode"])                                                ## EXT-2020-00733 
        strVirtualTireCode = str(SnsInfo["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(SnsInfo["VirtualTireBasicInfo"]["HiddenRevision"])  
        ##                    "VirtualTireID": "EXT-2020-00733VT00002"             "HiddenRevision": 0            
        strVTDBLoc = str(SnsInfo["VirtualTireBasicInfo"]["VirtualTireDBLocation"])  ## RND, ATC, CTC, ETC, ....     "VirtualTireDBLocation": "RND",
        strProductVirtualTireDir = '/' + strVTDBLoc + '/' + strProductCode + '/' + strVirtualTireCode    ## /RND/10100032/10100032VT00001-1 
        strTireGroup = str(SnsInfo["VirtualTireBasicInfo"]["ProductLine"])
        strCheckLifecycle = 'JobComplete'
        VTcode = SnsInfo["AnalysisInformation"]["SimulationCode"].split("-")[1] +"-"+ SnsInfo["AnalysisInformation"]["SimulationCode"].split("-")[2] +"-"+ SnsInfo["AnalysisInformation"]["SimulationCode"].split("-")[3]  
            # D101 << "SimulationCode": "RND-EXT-2020-00733VT00002-0-D101-0001", 

        VirtualTireID = str(SnsInfo["VirtualTireBasicInfo"]["VirtualTireID"])
        Revision = str(SnsInfo["VirtualTireBasicInfo"]["HiddenRevision"])
        Mesh2DInpFileName = VirtualTireID +"-"+Revision+".inp"
        Mesh3DTread = VirtualTireID +"-"+Revision + '.trd'
        Mesh3DBody =VirtualTireID +"-"+Revision + '.axi'
        ImageFile = VirtualTireID +"-"+Revision + '-2DMesh.png'
        Mesh2DInp = VirtualTireID +"-"+Revision
        mesh2dpath = 0

    elif Mesh2DInpFileName and strTireGroup : 
        Mesh3DTread = Mesh2DInpFileName[:-4] + '.trd'
        Mesh3DBody =Mesh2DInpFileName[:-4] + '.axi'
        ImageFile = Mesh2DInpFileName[:-4] + '-2DMesh.png'
        Mesh2DInp = Mesh2DInpFileName[:-4]
        strVirtualTireCode = Mesh2DInpFileName[:-4] +"D"
        mesh2dpath = 0
        strJobDir = os.getcwd()

        Equivalent_density_calculation(Mesh2DInpFileName, filename="density.txt")


    else:
        ErrorFileName = sns[:-4] + '.err'
        ErrorFile = open(ErrorFileName, 'w')
        with open(sns) as SNS:
            SnsInfo = json.load(SNS)
        file = ['', 0]
        fileName = str(SnsInfo["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(SnsInfo["VirtualTireBasicInfo"]["HiddenRevision"])
        ErrorFileName = str(SnsInfo["AnalysisInformation"]["SimulationCode"]) + '.err'
        fullErrorFileName = strJobDir + '/' + ErrorFileName
        fullTRDFileName = strJobDir + '/' + fileName + '.trd'
        fullAXIFileName = strJobDir + '/' + fileName + '.axi'

        strRootJobDir = '/home/fiper/ISLM/ISLM_JobFolder'
        strProductCode = str(SnsInfo["VirtualTireBasicInfo"]["ProductCode"])
        # -> into DOE Code 
        strVirtualTireCode = str(SnsInfo["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(SnsInfo["VirtualTireBasicInfo"]["HiddenRevision"])
        strVTDBLoc = str(SnsInfo["VirtualTireBasicInfo"]["VirtualTireDBLocation"])  ## RND, ATC, CTC, ETC, .... 
        strProductVirtualTireDir = '/' + strVTDBLoc + '/' + doeid+ '/' + strVirtualTireCode    ## DOE : /RND/DOE00001/10100032VT00001-0, 2,
        strTireGroup = str(SnsInfo["VirtualTireBasicInfo"]["ProductLine"])
        strCheckLifecycle = 'JobComplete'

        VTcode = SnsInfo["AnalysisInformation"]["SimulationCode"].split("-")[1]
    # Mesh2DInpFileName = strJobDir+'/' + VTcode + '-' +  SnsInfo["AnalysisInformation"]["SimulationCode"].split("-")[2] + '.inp'

        VirtualTireID = str(SnsInfo["VirtualTireBasicInfo"]["VirtualTireID"])
        Revision = str(SnsInfo["VirtualTireBasicInfo"]["HiddenRevision"])
        Mesh2DInpFileName = VirtualTireID +"-"+Revision+".inp"
        
        Mesh3DTread = Mesh2DInpFileName[:-4] + '.trd'
        Mesh3DBody = Mesh2DInpFileName[:-4] + '.axi'
        ImageFile = Mesh2DInpFileName[:-4] + '-2DMesh.png'
        

        Mesh2DInp =  Mesh2DInpFileName[:-4]

        mesh2dpath = 1
    #################################################################################################################
    beadcorefile = strJobDir+"/bead.tmp"
    ##############################################################################################################
    print ("## Pre-3D Model Generator Version 3.0")

    if SnsInfo: 
        if strTireGroup == "TBR": print ("## TBR Mesh Standard Applied")
        print ("## Virtual Tire No. : %s"%(strVirtualTireCode))
        print ("## Simulation Code  : %s"%(SnsInfo["AnalysisInformation"]["SimulationCode"]))
        
        Equivalent_density_calculation(Mesh2DInpFileName, filename="density.txt")



        snsElsetList = []
        for elset in SnsInfo["ElsetMaterialInfo"]["Mixing"]:
            snsElsetList.append(elset["Elset"])

        for elset in SnsInfo["ElsetMaterialInfo"]["Calendered"]:
            if "CH" in elset["Elset"] and strTireGroup != 'TBR':
                pass
            else:
                snsElsetList.append(elset["Elset"])
        try:
            Node, Element, Elset, Comments = Mesh2DScripts.Mesh2DInformation(Mesh2DInpFileName)
        except :
            ErrorFile.writelines("Error::Pre::[INPUT] NO MESH (2D) FILE ("+Mesh2DInpFileName+")!!\n")
            if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
            ErrorFile.close()
            sys.exit()
    else: 
        Node, Element, Elset, Comments = Mesh2DScripts.Mesh2DInformation(Mesh2DInpFileName)
    # Node.Node[0] = [Node No, X, Y, Z]   -> Node.Add([int(word[0]), float(word[3]), float(word[2]), float(word[1])])
    # Element.Element[0] =  [EL No,  N1,  N2,  N3, N4,'elset Name', N,  Area/length, CenterX, CenterY]
    # Elset.Elset[0] = ["Elset Name", EL no 1, 2, ...]  except BD1 and BETWEEN_BELTS
    
    if len(Node.Node) == 0 or len(Element.Element) == 0:
        
        ErrorFile.writelines("Error::Pre::[INPUT] NO MESH (2D) INFORMATION!!\n")
        if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        ErrorFile.close()
        sys.exit()

    if SnsInfo: 
        ElsetList=[]
        for list in Elset.Elset:
            # print list[0]
            if list[0] != 'BD1' and list[0] != 'BEAD_R' and list[0] != 'BEAD_L' and list[0] != 'BTT' and list[0] != 'CCT' and list[0] != 'CTT' and list[0] != 'SRTT' and list[0] != 'JBT' and list[0] != 'SWS' :# and list[0] != 'SPC':
                ElsetList.append(list[0])

        print ("## Elset checking : Mesh File (No. %d), SNS File (No. %d)"%(len(ElsetList), len(snsElsetList)))
        print (ElsetList)
        print (snsElsetList)

        # if len(ElsetList) != len(snsElsetList):
        #     print (ElsetList)
        #     print ("ERROR!! The ELSET numbers between SNS and Mesh are different.")
        #     ErrorFile.writelines("Error::Pre::[INPUT] ELSET NO. is NOT Equal with that in SNS File!!\n")
        #     if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        #     ErrorFile.close()
        #     print (snsElsetList)
        #     sys.exit()

        del (snsElsetList)
        del (ElsetList)

    try:
        Element.Element, Elset.Elset, Offset = Mesh2DScripts.ChaferDivide(Element.Element, ChaferName, Elset.Elset, Node.Node)
    except:
        print ("Error::Pre::[INPUT] Check ELement Offset between Left and Right!!")
        ErrorFile.writelines("Error::Pre::[INPUT] Check ELement Offset between Left and Right!!\n")
        
        Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset)
        if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        ErrorFile.close()
        sys.exit()
    OffsetLeftRight= GlobalVar(Offset)

    if InsertBETWEENBELTS == 1:
        # exist1bt = existEL('BT1', Elset.Elset)
        # exist2bt = existEL('BT2', Elset.Elset)
        exist3bt = existEL('BT3', Elset.Elset)
        exist4bt = existEL('BT4', Elset.Elset)

        BetweenBelts = ['BETWEEN_BELTS']
        Between = []
        if exist3bt == 1:
            Between = Mesh2DScripts.FindSolidElementBetweenMembrane('BT1', 'BT2', Element.Element)
            BetweenBelts = BetweenBelts + Between
            print ('* Elements Between BT1 ~ BT2 are ADDED into Elset "BETWEEN_BELTS" (%d).' % (len(Between)))
            # print (Between)
            Between = Mesh2DScripts.FindSolidElementBetweenMembrane('BT2', 'BT3', Element.Element)
            BetweenBelts = BetweenBelts + Between
            print ('* Elements Between BT2 ~ BT3 are ADDED into Elset "BETWEEN_BELTS" (%d).' %(len(Between)))
            # print (Between)
        else:
            Between = Mesh2DScripts.FindSolidElementBetweenMembrane('BT1', 'BT2', Element.Element)
            BetweenBelts = BetweenBelts + Between
            print ('* Elements Between BT1 ~ BT2 are ADDED into Elset "BETWEEN_BELTS" (%d).' %(len(Between)))
            # print (Between)
        if exist4bt == 1:
            Between = Mesh2DScripts.FindSolidElementBetweenMembrane('BT3', 'BT4', Element.Element)
            BetweenBelts = BetweenBelts + Between
            print ('* Elements Between BT3 ~ BT4 are ADDED into Elset "BETWEEN_BELTS" (%d).' % (len(Between)))
            # print (Between)

        if len(BetweenBelts)>0:
            Elset.Elset.append(BetweenBelts)
        
        del (BetweenBelts)
        del (Between)
    
    try:
        GeneralElement = Mesh2DScripts.ELEMENT()
        sws =  Mesh2DScripts.ELEMENT()
        for e in Element.Element:
            if e[5] != "SWS":        GeneralElement.Add(e)
            else:                    sws.Add(e)
        e, message = Mesh2DScripts.ElementCheck(GeneralElement.Element, Node.Node)
        print ("# No of 'SWS' Element : %d"%(len(sws.Element)))
        
        if len(sws.Element)>0:
            i=0
            while i < len(Element.Element):
                if Element.Element[i][5] == 'SWS': 
                    del(Element.Element[i])
                    i -=1
                i+= 1

            for i, es in enumerate(Elset.Elset):
                if es[0]  == 'SWS': 
                    ElsetSWS = es 
                    del(Elset.Elset[i])


        if e == 0:
            for i in range(len(message)):
                print (message[i])
            Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset)
            if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
            ErrorFile.close()
            sys.exit()
    except:

        print ("By Python - Rebar Connectivity")
        if Mesh2DScripts.RebarConnectivity(Element.Element) == 0:
            print ("Error::Pre::[INPUT]REBAR ELEMENT CONNECTION ERROR!!")
            ErrorFile.writelines("Error::Pre::[INPUT] REBAR ELEMENT CONNECTION ERROR!!\n")
            Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset)
            if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
            ErrorFile.close()
            sys.exit()

        if Mesh2DScripts.SolidElementOrderCheck(Element.Element, Node.Node) == 0:
            print ("Error::Pre::[INPUT] NODE in SOLID ELEMENT NUMBERING ERROR!!")
            ErrorFile.writelines("Error::Pre::[INPUT] NODE in SOLID ELEMENT NUMBERING ERROR!!\n")
            Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset)
            if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
            ErrorFile.close()
            sys.exit()

        if Mesh2DScripts.SolidElementShapeCheck(Element.Element, Node.Node, CriticalAngle.value, CriticalLength.value) == 0:
            print ("Error::Pre::[INPUT] SOLID ELEMENT SHAPE ERROR!!")
            ErrorFile.writelines("Error::Pre::[INPUT] SOLID ELEMENT SHAPE ERROR!!\n")
            Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset)
            if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
            ErrorFile.close()
            sys.exit()

    BDmin, BDMax, Center = Mesh2DScripts.BeadWidth(Element.Element, Node)
    if BDMax == 0:
        print ("Error::Pre::[INPUT] During Calulation Bead Width!!")
        Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset)
        if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        ErrorFile.close()
        sys.exit()
    else:
        bd=open(beadcorefile, "w")
        bd.writelines("%6.3f" %((BDMax-Center)*2000))
        bd.close()
    # MasterEdge, SlaveEdge, OutEdges, CenterNodes, FreeEdges, AllEdges = Mesh2DScripts.TieSurface(Element.Element, Node.Node)
    try:
        MasterEdge, SlaveEdge, OutEdges, CenterNodes, FreeEdges, AllEdges = Mesh2DScripts.TieSurface(Element.Element, Node.Node)
    except:
        print ("Error::Pre::[INPUT] CANNOT CREATE THE TIE SURFACE!!")
        ErrorFile.writelines("Error::Pre::[INPUT] CANNOT CREATE THE TIE SURFACE!!\n")
        Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset)
        if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        ErrorFile.close()
        sys.exit()        

    # print ("############## TIE SURFACE DONE")

    try:
        PressureSurface, RimContactSurface, TreadToRoadSurface = Mesh2DScripts.Surfaces(OutEdges, Node.Node, OffsetLeftRight.value, TreadElset, Element.Element)
        
    except:
        ErrorFile.writelines("Error::Pre::[INPUT] DURING PRESSURE, RIM CONTACT, TREAD TO SURFACE CREATION ERROR!!\n")
        Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset, MasterEdge, SlaveEdge)
        if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        ErrorFile.close()
        sys.exit()
    if len(TreadToRoadSurface) == 0:
        print ("Error::Pre::[INPUT] PRESSURE, RIM CONTACT, TREAD SURFACE ARE NOT FOUND!!")
        ErrorFile.writelines("Error::Pre::[INPUT] PRESSURE, RIM CONTACT, TREAD SURFACE ARE NOT FOUND!!\n")
        if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        ErrorFile.close()
        sys.exit()


    # try:
    # if strTireGroup == "TBR":  
        # TreadNode, BodyNode, TreadElement, BodyElement, TreadToRoadSurface, TreadBottom, BodyTop, BodyOut, TreadOut = \
            # Mesh2DScripts.Divide_Tread_Body_TBR_StandardMesh(Element.Element, Node.Node, TreadToRoadSurface, OutEdges)
    # else: 
    TreadNode, BodyNode, TreadElement, BodyElement, TreadToRoadSurface, TreadBottom, BodyTop, BodyOut, TreadOut, BD_master, BD_slave, TD_master, TD_slave =\
        Mesh2DScripts.Divide_Tread_Body_PCR_StandardMesh(Element, Node, TreadToRoadSurface, OutEdges)
    # except:
    #     print ("Error::Pre::[INPUT] TREAD / BODY DIVISION!!")
    #     ErrorFile.writelines("Error::Pre::[INPUT] TREAD / BODY DIVISION!!\n")
    #     Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset, MasterEdge, SlaveEdge, PressureSurface, RimContactSurface, TreadToRoadSurface)
    #     if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    #     ErrorFile.close()
    #     sys.exit()
    
    if Write2DMesh == 1:
        if len(sws.Element)>0:
            AllElement=Mesh2DScripts.ELEMENT()
            for e in Element.Element:
                AllElement.Add(e)
            for e in sws.Element:
                AllElement.Add(e)
            allElset=Mesh2DScripts.ELSET()
            for es in Elset.Elset:
                allElset.Elset.append(es)
            allElset.Elset.append(ElsetSWS)
            Mesh2DScripts.Write2DFile(Mesh2DInp, Node.Node, AllElement.Element, allElset.Elset, TreadToRoadSurface, PressureSurface, RimContactSurface, MasterEdge, SlaveEdge, OffsetLeftRight.value, CenterNodes, Comments, fullpath=mesh2dpath)
        else:
            Mesh2DScripts.Write2DFile(Mesh2DInp, Node.Node, Element.Element, Elset.Elset, TreadToRoadSurface, PressureSurface, RimContactSurface, MasterEdge, SlaveEdge, OffsetLeftRight.value, CenterNodes, Comments, fullpath=mesh2dpath)
    # print ("############## 2D Mesh DONE ")

    try:
        if strTireGroup != "TBR":  TreadBottom, BodyTop, BodyOut, TreadOut = Mesh2DScripts.BodyTopTreadBottomEdge(TreadNode, BodyNode, TreadElement, BodyElement, TreadToRoadSurface, MasterEdge, SlaveEdge, TreadElset)
        MasterEdges, SlaveEdges = Mesh2DScripts.TreadTieCheck(MasterEdge, SlaveEdge, TreadBottom, BodyTop)
    except:
        print ("Error::Pre::[INPUT] TERAD / BODY Surface for Adhesion!!")
        ErrorFile.writelines("Error::Pre::[INPUT] TERAD / BODY Surface for Adhesion!!\n")
        Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset, MasterEdge, SlaveEdge, PressureSurface, RimContactSurface, TreadToRoadSurface)
        if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
        ErrorFile.close()
        sys.exit()

    # MasterEdges, SlaveEdges = Mesh2DScripts.TreadTieCheck(MasterEdge, SlaveEdge, TreadBottom, BodyTop)
    
    TMasters = []; TSlaves=[]
    BMasters = []; BSlaves=[]

    for i, ms in enumerate(MasterEdges): 
        for ss in SlaveEdges: 
            mn1 = 0; mn2 = 0 
            for s in ss:
                if ms[0] == s[0] or ms[0] == s[1]: mn1 = 1
                if ms[1] == s[0] or ms[1] == s[1]: mn2 = 1
            if mn1 ==1 and mn2 ==1: 
                if ms[2] == "CTB" or ms[2] == "CTR" or ms[2] == "SUT"  or ms[2] == "UTR" or ms[2] == "TRW" : 
                    TMasters.append(ms)
                    TSlaves.append(ss)

                else: 
                    BMasters.append(ms)
                    BSlaves.append(ss) 
                break 


    Lend= time.time()
    if SMARToutput ==1:         #### Add line for DOE 
        # try:
        if strTireGroup != "TBR": 
            Mesh2DScripts.Write3DTreadMeshWithC(Mesh3DTread, TreadNode, TreadElement, TMasters, TSlaves, TreadToRoadSurface, TreadBottom, TreadNumber.value, OffsetSector.value, Elset.Elset, TreadElset, SectorOption_Tread, DivTread)
            Mesh2DScripts.Write3DBodyMeshWithC(Mesh3DBody, BodyNode, BodyElement, BMasters, BSlaves, PressureSurface, RimContactSurface, BodyOut, OffsetSector.value, OffsetLeftRight.value, Elset.Elset, TreadElset, SectorOption_Body, DivBody)
        else:
            Mesh2DScripts.Write3DTreadMeshWithC_TBR(Mesh3DTread, TreadNode, TreadElement, TMasters, TSlaves, TreadToRoadSurface, TreadBottom, TreadNumber.value, OffsetSector.value, Elset.Elset, TreadElset, SectorOption_Tread, DivTread)
            Mesh2DScripts.Write3DBodyMeshWithC_TBR(Mesh3DBody, BodyNode, BodyElement, BMasters, BSlaves, PressureSurface, RimContactSurface, BodyOut, OffsetSector.value, OffsetLeftRight.value, Elset.Elset, TreadElset, SectorOption_Body, DivBody)

        D3End = time.time()

        if sns: ErrorFile.writelines('The 3D models are created successfully!\n')

        print ("\n## Processing Time = %5.3f sec [Mesh Reading & Treatment = %5.3f sec, 3D Model Creation = %5.3f sec]"% (D3End - Tstart, Lend-Tstart, D3End-Lend))
    
    if Plot2DMesh == 1:
        MasterEdge=Mesh2DScripts.EDGE();     MasterEdge.Combine(BMasters);     MasterEdge.Combine(TMasters)
        MasterEdges = MasterEdge.Edge
        Mesh2DScripts.plot_geometry(ImageFile, 0, 0, Element.Element, Node.Node, Elset.Elset, MasterEdges, SlaveEdges, PressureSurface, RimContactSurface, TreadToRoadSurface, TreadBottom, BodyTop, TreadNode)
        if sns: ErrorFile.writelines('\n* The 2D Mesh Image is created successfully!\n')
    if sns: ErrorFile.close()
    
    # del (Element)
    # del (Node)
    # del (Elset)
    # del (FreeEdges)
    # del (PressureSurface)
    # del (RimContactSurface)
    # del (MasterEdges)
    # del (SlaveEdges)
    # del (TreadToRoadSurface)
    # del (BodyTop)
    # del (TreadBottom)
    # del (AllEdges)
    # del (TreadNode)

    #########################################################################
    ## Written by Yoon for the file management - copy and check
    #########################################################################

    # if os.access(strRootJobDir + strProductVirtualTireDir + '/' + strVirtualTireCode + '-2DMesh.png', os.F_OK):
    #     print '[ISLM::2DLayout] The 2D mesh image already exist!!'
    #     if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    #     sys.exit()

    # shutil.copyfile(strVirtualTireCode + '-2DMesh.png', strRootJobDir + strProductVirtualTireDir + '/' + strVirtualTireCode + '-2DMesh.png')

    # lstFile = []
    # lstFile.append(strVirtualTireCode + '-2DMesh.png')

    # if 'Success' == StoreFile.copyFile(strProductVirtualTireDir, lstFile, strCheckLifecycle):
    #     print '[ISLM::2DLayout] The 2D mesh image was well copied in the file server!!'
    # else:
    #     print '[ISLM::2DLayout] The 2D Mesh Image File Copy Error : Contact the system administrator!!'
    # if inISLM == 1: CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    print ("##################################################################################################")

































