#file : PreStaticSart.py
#Created by YS Yoon
#Create 2018/05/17
#Version 4.0
#Details : Migration to ISLM Version

import os, glob, math, json, sys, RetrievalData
import numpy as np
import CommonFunction_v3_0 as TIRE

try:
    import CheckExecution
except: 
    pass 

class NODE:
    def __init__(self):
        self.Node = []

    def Add(self, d):
        self.Node.append(d)

class ELEMENT:
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
    def Combine(self, class_element): 
        temp = ELEMENT()
        for el in self.Element: 
            temp.Add(el)
        for el in class_element.Element: 
            temp.Add(el)

        return temp 

    def ElsetNames(self): 
        names = []
        for i, el in enumerate(self.Element): 
            if i ==0: names.append(el[5])
            fd = 0 
            for name in names: 
                if name == el[5]: 
                    fd = 1
                    break 
            if fd == 0: 
                names.append(el[5])
        return names 
            
class ELSET:
    def __init__(self):
        self.Elset = []

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

class SURFACE:
    def __init__(self):
        self.Surface = []

    def AddName(self, name):
        self.Surface.append([name])

    def AddElement(self, name, n, face): 
        exist = -1
        for i in range(len(self.Surface)):
            if self.Surface[i][0] == name:
                exist = i 
                break
        if exist >=0: 
            self.Surface[i].append([n, face])
        else: 
            self.Surface.AddName(name)
            self.Surface.AddElement(name, n, face)

class TIE: 
    def __init__(self): 
        self.Tie =[]
        self.Group=[]
    def AddName(self, name): 
        self.Tie.append([name])
    def AddElement(self, name, n, face): 
        exist = -1
        for i in range(len(self.Tie)):
            if self.Tie[i][0] == name:
                exist = i 
                break
        if exist >=0: 
            self.Tie[i].append([n, face])
        else: 
            self.Tie.AddName(name)
            self.Tie.AddElement(name, n, face)
    def AddGroup(self, name): 
        self.Group.append([name])
    def AddGroupMember(self, name, slave, master): 
        exist = -1
        for i, mem in enumerate(self.Group): 
            if mem[0] == name: 
                self.Group[i].append(slave)
                self.Group[i].append(master)
                exist = 1 
                break 

        if exist == -1 : 
            self.AddGroup(name)
            self.AddGroupMember(self, name, slave, master)


class EDGE:
    def __init__(self):
        self.Edge = []

    def Add(self, edge):
        self.Edge.append(edge)

def isNumber(s):
  try:
    float(s)
    return True
  except ValueError:
    return False



def deleteBlank(strIsBlank):
    return ''.join(strIsBlank.split())

def createInpFile(path, strInpLine, strSimTask, strSimCode):
    fileNewInp = open(path + '/' + strSimCode + '-' + strSimTask + '.inp', 'wb')
    fileNewInp.write(strInpLine)
    fileNewInp.close()
    
class InpNodeElement:
    def readCuteInp(self, path, jsSns):
        self.strVTID = str(jsSns["VirtualTireBasicInfo"]["VirtualTireID"])
        self.strVTHidRev = str(jsSns["VirtualTireBasicInfo"]["HiddenRevision"])
        self.fileCuteInp = open(path + '/' + self.strVTID + '-' + self.strVTHidRev + '.msh')
        self.lstCuteInpTempLines = self.fileCuteInp.readlines()
        self.lstInpLines = []
        for self.strCuteInpTempLines in self.lstCuteInpTempLines:
            if self.strCuteInpTempLines.strip() != '':
                self.lstInpLines.append(self.strCuteInpTempLines.strip() + '\n')

class InpMaterial:
    def createMaterialInp(self, jsSns, version, simulation, MeshFile):
        self.lstInpLines = []
        self.lstFECom = []
        self.lstFECal = []
        self.lstElsetFECom = []
        self.lstElsetFECal = []
        self.lstFEComProperties = []
        self.lstFECalProperties = []
        self.lstPlyInfo = [('C/C Ply', 'C0'), ('Belt Ply', 'BT'), ('Rein. Belt Ply', 'JF'), ('Rein. Belt Ply', 'JE'), ('Rein. Belt Ply', 'JC'), ('RFM Ply', 'RF'), ('Chafer Ply', 'CH'), ('BeadCover Ply', 'BDC'), ('BeadCover Ply', 'PK'), ('BeadFlipper Ply', 'FLI'), ('Spiral Coil Ply', 'SPC')]
        self.lstPlyNameCheck = []
        self.strSlctRawMatCode = ''
        self.strSlctRawMatName = ''
        self.strSlctCalTS = ''
        self.strSlctCalArea = ''
        self.strSlctCalPoisson = ''
        self.strSlctCalDensity = ''
        self.strSlctCalElasticModulus = ''
        self.strSlctCalCompresModulus = ''
        self.strSlctCalCompresStrain = ''
        self.strMdfdCalAngle = ''
        self.lstComMulti = []
        
        self.strDBLoc = str(jsSns["VirtualTireBasicInfo"]["VirtualTireDBLocation"])
        self.strProductLine = str(jsSns["VirtualTireBasicInfo"]["ProductLine"])

        overtype = 1 
        if self.strProductLine == "TBR": 
            try: 
                
                if str(jsSns["VirtualTireParameters"]["OverType"] == "Tread Over Side"):
                    lstCDD = [[15.0,440.],[16.0,460.],[17.5,529.4],[18.0,526.],[20.0,571.5],[22.0,640.],[22.5,660.4],[24.0,686.],[24.5,711.2]]
                else: 
                    lstCDD = [[16.0,377.2],[17.5,407.4],[19.5,458.4],[20.0,483.8],[22.5,528.4],[24.5,576.1]]
                RDi = round(float(jsSns["VirtualTireParameters"]["RimDiameter"]) / 25.4, 1)
                size = jsSns["VirtualTireBasicInfo"]["TireSize"] 
                if "R" in size: RDi = float(size.split("R")[1])
                elif "-" in size : RDi = float(size.split("-")[1])
            except:
                overtype = 0 

        else:
            lstCDD = [[12.,337.],[13.,310.],[14.,335.],[15.,360.],[16.,385.],[17.,417.],[18.,442.],[19.,465.],[20.,490.],[21.,516.],[22.,542.],[23.,567.],[24.,592.],[26.,643.],[28.,694.]]
            RDi = round(float(jsSns["VirtualTireParameters"]["RimDiameter"]) / 25.4, 0)

        # print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # print ("RD", RDi, ">>", jsSns["VirtualTireParameters"]["RimDiameter"])
        if overtype ==1: 
            for cd in lstCDD: 
                if RDi == cd[0]: 
                    RimDia = cd[1]
                    print ("* Rim Dia=%.1f inch (%.1f), Carcass Drum Dia=%.2f mm"%(cd[0], RDi, cd[1]))
                    break 

        with open(MeshFile) as MS: 
            mlines = MS.readlines()
        
        carcass = []
        nodes = []
        EL2 = []
        iset = ''
        for line in mlines: 
            if "*" in line: 
                if "*ELSET, ELSET=C01" in line:   
                    if len(temp) > 1: 
                        carcass.append(temp)
                        
                    iset = 'CC'
                    temp = ['C01']
                elif "*ELSET, ELSET=C02" in line:   
                    if len(temp) > 1: 
                        carcass.append(temp)

                    iset = 'CC'
                    temp = ['C02']
                elif "*ELSET, ELSET=C03" in line:   
                    if len(temp) > 1: 
                        carcass.append(temp)

                    iset = 'CC'
                    temp = ['C03']
                elif "*NODE" in line: 
                    iset = "ND"
                    temp = []
                elif "TYPE=MGAX1" in line : 
                    iset = "M1"
                    temp = []
                else: 
                    if len(temp) > 1: 
                        carcass.append(temp)

                    iset = ''
                    temp = []
                

            else: 
                if iset == "CC": 
                    data = line.split(",")
                    for d in data: 
                        d = d.strip()
                        try: 
                            d = int(d)
                            temp.append(d)
                        except: 
                            pass 
                if iset == "ND": 
                    data = line.split(",")
                    i0 = int(data[0].strip())
                    i1 = float(data[1].strip())
                    i2 = float(data[2].strip())
                    i3 = float(data[3].strip())
                    nodes.append([i0, i1, i2, i3]) 
                if iset == 'M1': 
                    data = line.split(",")
                    i0 = int(data[0].strip())
                    i1 = int(data[1].strip())
                    i2 = int(data[2].strip())
                    EL2.append([i0, i1, i2])

        if len(nodes) > 0: npn = np.array(nodes)
        if len(EL2) > 0: el2 = np.array(EL2) 

        wdr = os.getcwd()
        mat_solid = []
        mat_rebar = []
        if os.path.isfile(wdr+"/density.txt") : 
            with open(wdr+"/density.txt") as DEN: 
                dens = DEN.readlines()
            cmd = ''
            for den in dens: 
                if "**" in den: 
                    continue 
                if "*" in den: 
                    if "*SOLID" in den: cmd = "S"
                    elif "*REBAR" in den: cmd = "R"
                    else: cmd = ""
                else: 
                    if cmd == "S": 
                        data = den.split(",") 
                        mat_solid.append([ data[0].strip(), float(data[2].strip())])
                    if cmd == 'R': 
                        data = den.split(",") 
                        mat_rebar.append([ data[0].strip(),  float(data[2].strip()), float(data[3].strip()),  float(data[10].strip()) ]) 
                        ## mat_rebar = [ELSET, Topping density, Cord Density, Cord Area ]

        
        for self.intNum in range(len(jsSns["ElsetMaterialInfo"]["Mixing"])):
            self.strElset = jsSns["ElsetMaterialInfo"]["Mixing"][self.intNum]["Elset"]
            self.strFECom = jsSns["ElsetMaterialInfo"]["Mixing"][self.intNum]["Compound"]
            try :
                self.strComMulti = jsSns["ElsetMaterialInfo"]["Mixing"][self.intNum]["Multiplier"]
                # print (jsSns["ElsetMaterialInfo"]["Mixing"][self.intNum]["Multiplier"])
            except: 
                self.strComMulti = str(100.0)
            self.lstComMulti.append((self.strElset, self.strComMulti, self.strFECom))
            self.lstElsetFECom.append((self.strElset, self.strFECom))
            if self.strFECom not in self.lstFECom:
                self.lstFECom.append(self.strFECom)
        for self.intNum in range(len(jsSns["ElsetMaterialInfo"]["Calendered"])):
            self.strElset = jsSns["ElsetMaterialInfo"]["Calendered"][self.intNum]["Elset"]
            self.strFECom = jsSns["ElsetMaterialInfo"]["Calendered"][self.intNum]["Compound"]
            self.strRawMatCode = jsSns["ElsetMaterialInfo"]["Calendered"][self.intNum]["MatCode"]
            self.strRawMatName = jsSns["ElsetMaterialInfo"]["Calendered"][self.intNum]["RawCode"]
            self.strAngle = jsSns["ElsetMaterialInfo"]["Calendered"][self.intNum]["Angle"]
            self.strDirection = jsSns["ElsetMaterialInfo"]["Calendered"][self.intNum]["Direction"]
            self.strEPI = jsSns["ElsetMaterialInfo"]["Calendered"][self.intNum]["EPI"]
            self.strGauge = jsSns["ElsetMaterialInfo"]["Calendered"][self.intNum]["Gauge"]
            self.lstElsetFECal.append((self.strElset, self.strFECom, self.strRawMatCode, self.strRawMatName, self.strAngle, self.strDirection, self.strEPI, self.strGauge))
            if 'BT' in self.strElset:
                if ('BTT', self.strFECom) not in self.lstElsetFECom:
                    self.lstElsetFECom.append(('BTT', self.strFECom))
            if 'C0' in self.strElset:
                if ('CCT', self.strFECom) not in self.lstElsetFECom:
                    self.lstElsetFECom.append(('CCT', self.strFECom))
            ### Add materail sets for New mesh standard 2020 
            # if version =="2020": 

            if simulation == 'ENDU':
                if 'JF' in self.strElset:
                    if ('JBT', self.strFECom) not in self.lstElsetFECom:
                        self.lstElsetFECom.append(('JBT', self.strFECom))   ## JBT compound is replaced with BTT for Endurance simalation 
                    print (self.strElset, '* JBT', self.strFECom)
                if 'JE' in self.strElset:
                    
                    if ('JBT', self.strFECom) not in self.lstElsetFECom:
                        self.lstElsetFECom.append(('JBT', self.strFECom))   ## JBT compound is replaced with BTT for Endurance simalation 
                    print (self.strElset, '**JBT', self.strFECom)
            else: 
                if 'JF' in self.strElset:
                    if ('JBT', self.strFECom) not in self.lstElsetFECom:
                        self.lstElsetFECom.append(('JBT', self.strFECom))   
                if 'JE' in self.strElset:
                    if ('JBT', self.strFECom) not in self.lstElsetFECom:
                        self.lstElsetFECom.append(('JBT', self.strFECom))   

            ###########################################################
            if 'RF' in self.strElset or 'PK' in self.strElset or 'FLI' in self.strElset:
                if ('RTT', self.strFECom) not in self.lstElsetFECom:
                    self.lstElsetFECom.append(('SRTT', self.strFECom))
            if self.strFECom not in self.lstFECom:
                self.lstFECom.append(self.strFECom)
            if self.strRawMatCode not in self.lstFECal:
                self.lstFECal.append(self.strRawMatCode)

        # self.strReqType = 'StaticCompound'
        # self.lstFEComProperties = RetrievalData.getData(self.strDBLoc, self.strReqType, self.lstFECom)
        # self.lstFEComProperties.append(('ABW121A', '4000', '176000000000', '0.3'))
        self.strReqType = 'StaticCompoundTemp'
        # elf.lstFEComProperties = (strComName, strComDensity, strComStaticModulus, strComPoisson, strComTanDelta, strComThermalConductivity)
        self.lstFEComProperties = RetrievalData.getData(self.strDBLoc, self.strReqType, self.lstFECom)
        self.lstFEComProperties.append(('ABW121A', '4000', '176000000000', '0.3', '0.0', '0.3'))

        # print("BD Loc", self.strDBLoc)
        # print("Req Type", self.strReqType)
        # print("compd", self.lstFECom)
        # print ("****************************")
        # for pro in self.lstFEComProperties:
        #     print (pro)
        # print ("****************************")

        f=open("Materials.txt", "w")
        f.writelines(str(self.lstFEComProperties))
        
        self.lstElsetFECom.append(('BD1', 'ABW121A'))
        
        self.strReqType = 'StaticCalendered'
        self.lstFECalProperties = RetrievalData.getData(self.strDBLoc, self.strReqType, self.lstFECal)
        f.writelines(str(self.lstFECalProperties))
        f.close()
        # print("BD Loc", self.strDBLoc)
        # print("Req Type", self.strReqType)
        # print("Calendar", self.lstFECal)
        # print ("****************************")
        # for pro in self.lstFECalProperties:
        #     print (pro)
        # print ("****************************")
        
        if simulation == 'ENDU': 
            with open("SWS_Elements.inp")  as SWS: 
                lines = SWS.readlines()
            for line in lines: 
                self.lstInpLines.append(line)          
        # self.lstInpLines.append('*INCLUDE, INPUT=SWS_Elements.inp\n')
        
        self.lstInpLines.append('****************************************************************************************\n')
        self.lstInpLines.append('** Material Properties\n')
        self.lstInpLines.append('****************************************************************************************\n')
        if simulation == 'ENDU': 
            self.lstInpLines.append('******************* SWS **************************\n')
            self.lstInpLines.append('*MATERIAL, NAME=SWS_M\n')
            self.lstInpLines.append('*DENSITY\n')
            self.lstInpLines.append(' 1085\n')
            self.lstInpLines.append('*HYPERELASTIC, NEO HOOKE\n')
            self.lstInpLines.append(' 5.810811E+05, 6.976744E-08\n')
            self.lstInpLines.append('*MEMBRANE SECTION, ELSET=SWS, MATERIAL=SWS_M\n')
            self.lstInpLines.append('0.000001\n')
        
        for self.tupFEComProperties in self.lstFEComProperties:
            self.lstInpLines.append('******************** ' + self.tupFEComProperties[0] + ' ********************\n')
            self.lstInpLines.append('*MATERIAL, NAME=' + self.tupFEComProperties[0] + '\n')
            self.lstInpLines.append('*DENSITY\n')

            eqi_den = self.tupFEComProperties[1] 
            fd = 0 
            for ecom in self.lstElsetFECom:
                eset = ecom[0]; mat = ecom[1] 
                mset = "NO_MATERIAL"
                if mat == self.tupFEComProperties[0]: 
                    mset = eset
                    break 

            for mat in mat_solid: 
                # print (">> ", mat[0], self.tupElsetFECom[0])
                if mat[0] == mset: 
                    eqi_den = str(mat[1]*1000)
                    self.lstInpLines.append('** %s equivalent density adapted. \n'%(mat[0]))
                    fd = 1
                    break 
            # if fd ==0: self.lstInpLines.append('** original density adapted.\n'
            self.lstInpLines.append(' ' + eqi_den + '\n')

            if self.tupFEComProperties[0] == "ABW121A": 
                self.lstInpLines.append('*ELASTIC\n')
                self.lstInpLines.append(' ' + self.tupFEComProperties[2] + ', ' + self.tupFEComProperties[3] + '\n')
            ################################################################################
            ## For Endurance analysis improvement 
            else:
                multi = 1.0 
                for com in self.lstComMulti:
                    # print ("## ", com, "####",  self.tupFEComProperties)
                    if com[2] == self.tupFEComProperties[0]: 
                        multi = float(com[1].strip()) / 100.0
                        # print (multi) 
                        break
                E = float(self.tupFEComProperties[2]) * multi 
                m = float(self.tupFEComProperties[3])
                # self.lstInpLines.append("*HYPERELASTIC, Mooney-Rivlin\n")
                # self.lstInpLines.append("%.6E, %.6E, %.6E\n"%(E*2.0/15.0, E/30.0, 6*(1.0-2.0*m)/E))
                self.lstInpLines.append("*HYPERELASTIC, NEO HOOKE\n")
                self.lstInpLines.append("%.6E, %.6E\n"%(E/(4.0*(1.0+m)), 6.0*(1.0-2.0*m)/E))
            ################################################################################
            
        self.lstInpLines.append('*****************************************************\n')
        
        isJBT = 0 
        for self.tupElsetFECom in self.lstElsetFECom:
            if version == '2019' and self.tupElsetFECom[0] == 'JBT' : continue 
            if self.tupElsetFECom[0] == 'JBT' : 
                isJBT = 1
                continue 
            self.lstInpLines.append('*SOLID SECTION, ELSET=' + self.tupElsetFECom[0] + ', MATERIAL=' + self.tupElsetFECom[1] + '\n')
        if isJBT ==1: 
            for self.tupElsetFECom in self.lstElsetFECom:
                if self.tupElsetFECom[0] == 'BTT': 
                    self.lstInpLines.append('*SOLID SECTION, ELSET=JBT, MATERIAL=' + self.tupElsetFECom[1] + '\n')
                    break 
            
        for self.tupPlyInfo in self.lstPlyInfo:
            self.lstInpLines.append('******************** ' + self.tupPlyInfo[0] + ' ********************\n')
            for self.tupElsetFECal in self.lstElsetFECal:
                if self.tupPlyInfo[1] in self.tupElsetFECal[0]:
                    self.strSlctRawMatCode = self.tupElsetFECal[2]
                    self.strSlctRawMatName = self.tupElsetFECal[3]
                    if self.strSlctRawMatCode not in self.lstPlyNameCheck:
                        self.lstPlyNameCheck.append(self.strSlctRawMatCode)
                        for self.tupFECalProperties in self.lstFECalProperties:
                            if self.strSlctRawMatCode == self.tupFECalProperties[1]:
                                self.strSlctCalTS = self.tupFECalProperties[0]
                                self.strSlctCalArea = self.tupFECalProperties[3]
                                self.strSlctCalPoisson = self.tupFECalProperties[4]
                                self.strSlctCalDensity = self.tupFECalProperties[5]
                                self.strSlctCalElasticModulus = self.tupFECalProperties[6]
                                self.strSlctCalCompresModulus = self.tupFECalProperties[7]
                                self.strSlctCalCompresStrain = self.tupFECalProperties[8]
                                break
                        
                        self.lstInpLines.append('*MATERIAL, NAME=' + self.strSlctCalTS + '_' + deleteBlank(self.strSlctRawMatName) + '\n')
                        self.lstInpLines.append('*DENSITY\n')   ## cord name : self.tupElsetFECal[0], 

                        ## mat_rebar = [ELSET, Topping density, Cord Density, Cord Area ]
                        for mat in mat_rebar: 
                            if mat[0] == self.tupElsetFECal[0]: 
                                self.strSlctCalDensity  = str(mat[2])
                                self.lstInpLines.append("** Equivalent density applied.\n")
                                break 


                        self.lstInpLines.append(' ' + self.strSlctCalDensity + '\n')
                        if 'T' == self.strSlctCalTS:
                            self.lstInpLines.append('*USER MATERIAL,CONSTANTS=3\n')
                            self.lstInpLines.append(' ' + self.strSlctCalElasticModulus + ' , ' + self.strSlctCalCompresModulus + ' , -' + self.strSlctCalCompresStrain + '\n')
                        if 'S' == self.strSlctCalTS:
                            self.lstInpLines.append('*ELASTIC\n')
                            self.lstInpLines.append(' ' + self.strSlctCalElasticModulus + ' , ' + self.strSlctCalPoisson + '\n')
                    
            for self.tupElsetFECal in self.lstElsetFECal:
                if self.tupPlyInfo[1] in self.tupElsetFECal[0]:
                    for self.tupFECalProperties in self.lstFECalProperties:
                        if self.tupElsetFECal[2] == self.tupFECalProperties[1]:
                            self.strSlctCalTS = self.tupFECalProperties[0]
                            break
                    if self.tupElsetFECal[0] == 'CH1' and self.strProductLine != 'TBR':
                        pass
                    else:
                        self.lstInpLines.append('*MEMBRANE SECTION, ELSET=' + self.tupElsetFECal[0] + ', MATERIAL=' + self.tupElsetFECal[1] + '\n')
                        self.lstInpLines.append(' ' + str(float(self.tupElsetFECal[7])/100000) + '\n')
                        
                    if 'BT' in self.tupElsetFECal[0]:
                        if 'R' == self.tupElsetFECal[5]:
                            self.strMdfdCalAngle = str(90-float(self.tupElsetFECal[4]))
                        elif 'L' == self.tupElsetFECal[5]:
                            self.strMdfdCalAngle = '-' + str(90-float(self.tupElsetFECal[4]))
                        else:
                            if 'TBR' == self.strProductLine:
                                if 'BT1' in self.tupElsetFECal[0] or 'BT2' in self.tupElsetFECal[0]:
                                    self.strMdfdCalAngle = str(90-float(self.tupElsetFECal[4]))
                                else:
                                    self.strMdfdCalAngle = '-' + str(90-float(self.tupElsetFECal[4]))
                            else:
                                if 'BT1' in self.tupElsetFECal[0] or 'BT3' in self.tupElsetFECal[0]:
                                    self.strMdfdCalAngle = str(90-float(self.tupElsetFECal[4]))
                                else:
                                    self.strMdfdCalAngle = '-' + str(90-float(self.tupElsetFECal[4]))

                    else:
                        self.strMdfdCalAngle = str(90-float(self.tupElsetFECal[4]))


                    ## mat_rebar = [ELSET, Topping density, Cord Density, Cord Area ]
                    for mat in mat_rebar: 
                        if mat[0] == self.tupElsetFECal[0]: 
                            self.strSlctCalArea  = str(mat[3])
                            self.lstInpLines.append("** Calculated Section area applied.\n")
                            break 

                    if self.tupElsetFECal[0] == 'CH1' and self.strProductLine != 'TBR':
                        pass
                    elif 'C0' in self.tupElsetFECal[0]: 
                        for cc in carcass: 
                            if cc[0] == self.tupElsetFECal[0]: 
                                iset = cc[1:]
                                break 

                        if overtype ==1: 
                            if self.tupElsetFECal[0] == 'C01': cc_gauge = 1.0
                            elif self.tupElsetFECal[0] == 'C02': cc_gauge = 2.0
                            elif self.tupElsetFECal[0] == 'C03': cc_gauge = 3.0
                            else: cc_gauge = 1.0 

                            CcRad = RimDia/2000.0 + cc_gauge/1000

                            for i in iset:
                                ix = np.where(el2[:,0] == i)[0][0] 
                                el = el2[ix]
                                ix = np.where(npn[:,0] == el[1])[0][0]; n1 = npn[ix]
                                ix = np.where(npn[:,0] == el[2])[0][0]; n2 = npn[ix]
                                ht = (n1[1] + n2[1]) / 2.0 
                                LIFT = ht / CcRad 

                                self.lstInpLines.append('*REBAR, ELEMENT=AXIMEMBRANE, MATERIAL=' + self.strSlctCalTS + '_' + deleteBlank(self.tupElsetFECal[3]) + ', GEOM=SKEW, NAME=' + self.tupElsetFECal[0]+"_"+str(i) + '\n')
                                self.lstInpLines.append(str(i) + ', ' + self.strSlctCalArea + ' , ' + str(25.4/(float(self.tupElsetFECal[6])*1000) * LIFT) + ' , ' + self.strMdfdCalAngle + '\n')
                                self.lstInpLines.append("** Initial EPI=%s, Lifted EPI=%.3f, Lift Rate =%.3f (CCR=%.2f, HT=%.2f)\n"%(\
                                        self.tupElsetFECal[6], float(self.tupElsetFECal[6])/LIFT, LIFT, CcRad*1000, ht*1000))
                        else: 
                            LIFT = 1.0
                            self.lstInpLines.append('*REBAR, ELEMENT=AXIMEMBRANE, MATERIAL=' + self.strSlctCalTS + '_' + deleteBlank(self.tupElsetFECal[3]) + ', GEOM=SKEW, NAME=' + self.tupElsetFECal[0] + '\n')
                            self.lstInpLines.append(self.tupElsetFECal[0] + ', ' + self.strSlctCalArea + ' , ' + str(25.4/(float(self.tupElsetFECal[6])*1000) * LIFT) + ' , ' + self.strMdfdCalAngle + '\n')



                    else:
                        self.lstInpLines.append('*REBAR, ELEMENT=AXIMEMBRANE, MATERIAL=' + self.strSlctCalTS + '_' + deleteBlank(self.tupElsetFECal[3]) + ', GEOM=SKEW, NAME=' + self.tupElsetFECal[0] + '\n')
                        self.lstInpLines.append(self.tupElsetFECal[0] + ', ' + self.strSlctCalArea + ' , ' + str(25.4/(float(self.tupElsetFECal[6])*1000)) + ' , ' + self.strMdfdCalAngle + '\n')
                    if jsSns["VirtualTireParameters"]["JLCType"] == 'JF535' and self.tupElsetFECal[0] == 'JFC1':
                        read2dinp = open(str(jsSns["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(jsSns["VirtualTireBasicInfo"]["HiddenRevision"]) + '.inp', 'r')
                        inp2dfile = read2dinp.readlines()
                        read2dinp.close()
                        if '*ELSET, ELSET=OJFC1\n' in inp2dfile or '*ELSET, ELSET=OJFC1\r\n' in inp2dfile:
                            self.lstInpLines.append('*MEMBRANE SECTION, ELSET=OJFC1, MATERIAL=' + self.tupElsetFECal[1] + '\n')
                            self.lstInpLines.append(' ' + str(float(self.tupElsetFECal[7])*1.6/100000) + '\n')
                            self.lstInpLines.append('*REBAR, ELEMENT=AXIMEMBRANE, MATERIAL=' + self.strSlctCalTS + '_' + deleteBlank(self.tupElsetFECal[3]) + ', GEOM=SKEW, NAME=OJFC1\n')
                            self.lstInpLines.append('OJFC1, ' + str(float(self.strSlctCalArea)*1.6) + ' , ' + str(25.4/(float(self.tupElsetFECal[6])*1000)) + ' , ' + self.strMdfdCalAngle + '\n')
                    if jsSns["VirtualTireParameters"]["JLCType"] == 'JF5' and self.tupElsetFECal[0] == 'JFC1':
                        read2dinp = open(str(jsSns["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(jsSns["VirtualTireBasicInfo"]["HiddenRevision"]) + '.inp', 'r')
                        inp2dfile = read2dinp.readlines()
                        read2dinp.close()
                        if '*ELSET, ELSET=OJFC1\n' in inp2dfile or '*ELSET, ELSET=OJFC1\r\n' in inp2dfile:
                            self.lstInpLines.append('*MEMBRANE SECTION, ELSET=OJFC1, MATERIAL=' + self.tupElsetFECal[1] + '\n')
                            self.lstInpLines.append(' ' + str(float(self.tupElsetFECal[7])*1.6/100000) + '\n')
                            self.lstInpLines.append('*REBAR, ELEMENT=AXIMEMBRANE, MATERIAL=' + self.strSlctCalTS + '_' + deleteBlank(self.tupElsetFECal[3]) + ', GEOM=SKEW, NAME=OJFC1\n')
                            self.lstInpLines.append('OJFC1, ' + str(float(self.strSlctCalArea)*1.6) + ' , ' + str(25.4/(float(self.tupElsetFECal[6])*1000)) + ' , ' + self.strMdfdCalAngle + '\n')
                            replaceline = self.lstInpLines.index('*MEMBRANE SECTION, ELSET=' + self.tupElsetFECal[0] + ', MATERIAL=' + self.tupElsetFECal[1] + '\n')
                            del self.lstInpLines[replaceline];del self.lstInpLines[replaceline];del self.lstInpLines[replaceline];del self.lstInpLines[replaceline]
                    if jsSns["VirtualTireParameters"]["JLCType"] == 'JF3' and self.tupElsetFECal[0] == 'JFC1':
                        read2dinp = open(str(jsSns["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(jsSns["VirtualTireBasicInfo"]["HiddenRevision"]) + '.inp', 'r')
                        inp2dfile = read2dinp.readlines()
                        read2dinp.close()
                        if '*ELSET, ELSET=OJFC1\n' in inp2dfile or '*ELSET, ELSET=OJFC1\r\n' in inp2dfile:
                            self.lstInpLines.append('*MEMBRANE SECTION, ELSET=OJFC1, MATERIAL=' + self.tupElsetFECal[1] + '\n')
                            self.lstInpLines.append(' ' + str(float(self.tupElsetFECal[7])*1.6/100000) + '\n')
                            self.lstInpLines.append('*REBAR, ELEMENT=AXIMEMBRANE, MATERIAL=' + self.strSlctCalTS + '_' + deleteBlank(self.tupElsetFECal[3]) + ', GEOM=SKEW, NAME=OJFC1\n')
                            self.lstInpLines.append('OJFC1, ' + str(float(self.strSlctCalArea)*1.6) + ' , ' + str(25.4/(float(self.tupElsetFECal[6])*1000)) + ' , ' + self.strMdfdCalAngle + '\n')
                            replaceline = self.lstInpLines.index('*MEMBRANE SECTION, ELSET=' + self.tupElsetFECal[0] + ', MATERIAL=' + self.tupElsetFECal[1] + '\n')
                            del self.lstInpLines[replaceline];del self.lstInpLines[replaceline];del self.lstInpLines[replaceline];del self.lstInpLines[replaceline]
                    if jsSns["VirtualTireParameters"]["JLCType"] == 'JE3' and self.tupElsetFECal[0] == 'JEC1':
                        read2dinp = open(str(jsSns["VirtualTireBasicInfo"]["VirtualTireID"]) + '-' + str(jsSns["VirtualTireBasicInfo"]["HiddenRevision"]) + '.inp', 'r')
                        inp2dfile = read2dinp.readlines()
                        read2dinp.close()
                        if '*ELSET, ELSET=OJFC1\n' in inp2dfile or '*ELSET, ELSET=OJFC1\r\n' in inp2dfile:
                            self.lstInpLines.append('*MEMBRANE SECTION, ELSET=OJFC1, MATERIAL=' + self.tupElsetFECal[1] + '\n')
                            self.lstInpLines.append(' ' + str(float(self.tupElsetFECal[7])*1.6/100000) + '\n')
                            self.lstInpLines.append('*REBAR, ELEMENT=AXIMEMBRANE, MATERIAL=' + self.strSlctCalTS + '_' + deleteBlank(self.tupElsetFECal[3]) + ', GEOM=SKEW, NAME=OJFC1\n')
                            self.lstInpLines.append('OJFC1, ' + str(float(self.strSlctCalArea)*1.6) + ' , ' + str(25.4/(float(self.tupElsetFECal[6])*1000)) + ' , ' + self.strMdfdCalAngle + '\n')
                            replaceline = self.lstInpLines.index('*MEMBRANE SECTION, ELSET=' + self.tupElsetFECal[0] + ', MATERIAL=' + self.tupElsetFECal[1] + '\n')
                            del self.lstInpLines[replaceline];del self.lstInpLines[replaceline];del self.lstInpLines[replaceline];del self.lstInpLines[replaceline]
            self.lstInpLines.append('******************** ' + self.tupPlyInfo[0] + ' ********************\n')
            
class InpRimContour:
    def createRimContour(self, jsSns):
        self.beadringtype = str(jsSns["VirtualTireParameters"]["BeadringType"])
        self.lstInpLines = []
        if self.beadringtype == 'Tubeless':
            self.rw = float(jsSns["AnalysisInformation"]["AnalysisCondition"][0]["RimWidth"])
            self.rd = round(float(jsSns["VirtualTireParameters"]["RimDiameter"])/25.4)

            # print self.rw, self.rd
            self.startR = 207.821; self.startZ  = 97.394
            self.line1R = 220.934; self.line1Z  = 146.333
            self.line2Z =   82.5; self.line2R   =   0.0
            self.circle1CR = 228.661; self.circle1CZ = 144.263; self.circle1ER = 226.184; self.circle1EZ = 151.87
            self.circle2CR = 222.250; self.circle2CZ = 163.945; self.circle2ER = 227.888; self.circle2EZ = 175.325
            
            
            self.ChangeRW = 0.0
            #self.ChangeRD = 0.0
            self.ChangeRD = 0.5
            self.RimChange= 1.968503937 # 4inch * 25.4
            
            self.RwD = 0.0 
            self.RdD = self.rd + self.ChangeRD - 17.5
            
            if self.rw == 5.25: 
                self.RwD=-19.5/25.4+self.ChangeRW+self.RimChange
            elif self.rw == 6.0:
                self.RwD=self.ChangeRW+self.RimChange
            elif self.rw == 6.75:
                self.RwD=19.0/25.4+self.ChangeRW+self.RimChange
            elif self.rw == 7.5:
                self.RwD=38.0/25.4+self.ChangeRW+self.RimChange
            elif self.rw == 8.25: 
                self.RwD=57.0/25.4+self.ChangeRW+self.RimChange
            elif self.rw == 9.0: 
                self.RwD=76.0/25.4+self.ChangeRW+self.RimChange
            elif self.rw ==9.75: 
                self.RwD=95.0/25.4+self.ChangeRW+self.RimChange
            elif self.rw ==10.5: 
                self.RwD=114.0/25.4+self.ChangeRW+self.RimChange
            elif self.rw ==11.75: 
                self.RwD=146.0/25.4+self.ChangeRW+self.RimChange
            elif self.rw ==12.25: 
                self.RwD=158.5/25.4+self.ChangeRW+self.RimChange
            elif self.rw ==13.0: 
                self.RwD=177.5/25.4+self.ChangeRW+self.RimChange
            elif self.rw ==14.0: 
                self.RwD=203.0/25.4+self.ChangeRW+self.RimChange
            elif self.rw ==15.0: 
                self.RwD=228.5/25.4+self.ChangeRW+self.RimChange
            else:
                self.lstInpLines.append('**************************************************************************\n')
                self.lstInpLines.append('** Input of RW is not define in Flat Base Rim Contours Profile 1 of TRA!  \n')
                self.lstInpLines.append('**************************************************************************\n')
                
            self.startR   =(self.startR   +self.RdD*25.4/2)
            self.line1R   =(self.line1R   +self.RdD*25.4/2)
            self.circle1ER=(self.circle1ER+self.RdD*25.4/2)
            self.circle1CR=(self.circle1CR+self.RdD*25.4/2)
            self.circle2ER=(self.circle2ER+self.RdD*25.4/2)
            self.circle2CR=(self.circle2CR+self.RdD*25.4/2)

            self.startZ   =(self.startZ   +self.RwD*25.4/2)
            self.line1Z   =(self.line1Z   +self.RwD*25.4/2)
            self.circle1EZ=(self.circle1EZ+self.RwD*25.4/2)
            self.circle1CZ=(self.circle1CZ+self.RwD*25.4/2)
            self.circle2EZ=(self.circle2EZ+self.RwD*25.4/2)
            self.circle2CZ=(self.circle2CZ+self.RwD*25.4/2)

            self.lstInpLines.append('** Tubeless Rim Profile\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('** Service Rim Width : ' +jsSns["AnalysisInformation"]["AnalysisCondition"][0]["RimWidth"] + '\n')
            self.lstInpLines.append('** Service Rim Dia   : ' + str(round(float(jsSns["VirtualTireParameters"]["RimDiameter"])/25.4)) + '\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*ELSET,ELSET=FLANGE\nBSW,HUS\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE,TYPE=ELEMENT, NAME=TFLANGE\n')
            self.lstInpLines.append('FLANGE\n')
            self.lstInpLines.append('*NODE,NSET=NLFLANGE\n')
            self.lstInpLines.append(' 3998, 0.0, 0.0, 0.0\n')
            self.lstInpLines.append('*NODE,NSET=NRFLANGE\n')
            self.lstInpLines.append(' 3999, 0.0, 0.0, 0.0\n')
            self.lstInpLines.append('*NSET,NSET=NFLANGE\n')
            self.lstInpLines.append('NLFLANGE,NRFLANGE\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE, TYPE=SEGMENT,NAME=LFLANGE\n')
            self.lstInpLines.append('START,%6.2fE-3,%6.2fE-3\n' % (self.circle2ER, self.circle2EZ))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.circle1ER, self.circle1EZ, self.circle2CR, self.circle2CZ))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.line1R, self.line1Z, self.circle1CR, self.circle1CZ))
            self.lstInpLines.append('LINE,%6.2fE-3,%6.2fE-3\n' % (self.startR, self.startZ))
            self.lstInpLines.append('*RIGID BODY,ANALYTICAL SURFACE=LFLANGE,REF NODE=NLFLANGE\n')
            self.lstInpLines.append('*CONTACT PAIR,INTERACTION=RIML, HCRIT=1.0e-3\nRIC_L,LFLANGE\n')
            self.lstInpLines.append('*SURFACE INTERACTION,NAME=RIML\n*SURFACE BEHAVIOR, AUGMENTED LAGRANGE\n ,0.0,1.0\n*FRICTION\n 0.015\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE, TYPE=SEGMENT,NAME=RFLANGE\n')
            self.lstInpLines.append('START,%6.2fE-3,-%6.2fE-3\n' % (self.startR,self.startZ))
            self.lstInpLines.append('LINE,%6.2fE-3,-%6.2fE-3\n' % (self.line1R,self.line1Z))
            self.lstInpLines.append('CIRCL,%6.2fE-3,-%6.2fE-3,%6.2fE-3,-%6.2fE-3\n' % (self.circle1ER,self.circle1EZ,self.circle1CR,self.circle1CZ))
            self.lstInpLines.append('CIRCL,%6.2fE-3,-%6.2fE-3,%6.2fE-3,-%6.2fE-3\n' % (self.circle2ER,self.circle2EZ,self.circle2CR,self.circle2CZ))
            self.lstInpLines.append('*RIGID BODY,ANALYTICAL SURFACE=RFLANGE,REF NODE=NRFLANGE\n')
            self.lstInpLines.append('*CONTACT PAIR,INTERACTION=RIMR, HCRIT=1.0e-3\nRIC_R,RFLANGE\n')
            self.lstInpLines.append('*SURFACE INTERACTION,NAME=RIMR\n*SURFACE BEHAVIOR, AUGMENTED LAGRANGE\n ,0.0,1.0\n*FRICTION\n 0.015\n')
                    
        elif self.beadringtype == 'Tube Type':

            

            self.rw = float(jsSns["AnalysisInformation"]["AnalysisCondition"][0]["RimWidth"])
            self.rd = round(float(jsSns["VirtualTireParameters"]["RimDiameter"])/25.4)
            
            self.startR = 215.926; self.startZ  =  72.55 
            self.line1R = 256.536; self.line1Z  = 125.247
            self.line2Z =   132.5; self.line2R  =   0.0
            self.circle1CR = 264.506; self.circle1CZ =  124.55; self.circle1ER = 264.506; self.circle1EZ =  132.55
            self.circle2CR =     0.0; self.circle2CZ =  0.0; self.circle2ER =    0.0; self.circle2EZ =  0.0
            
            self.ChangeRW = 0.0
            self.ChangeRD = 0.0
            # self.RimChange=4.0 # 4inch*25.4
            self.Rim_Change=4.0 # 4inch*25.4
            
            self.RwD = 0.0; self.RdD = 0.0
            if self.rw == 6.5: 
                self.line2R = 271.795
                self.circle2CR = 271.795; self.circle2CZ = 150.330; self.circle2ER = 281.122; self.circle2EZ = 165.467
            elif self.rw == 7.0:
                self.RwD       = 0.5
                self.line2R = 273.050
                self.circle2CR = 273.050; self.circle2CZ = 151.600; self.circle2ER = 282.703; self.circle2EZ = 168.023
            elif self.rw == 7.5:
                self.RwD       = 1.0
                self.line2R = 274.320
                self.circle2CR = 274.320; self.circle2CZ = 152.870; self.circle2ER = 284.675; self.circle2EZ = 170.300
            elif self.rw == 8.0: 
                self.RwD       = 1.5
                self.line2R = 275.590
                self.circle2CR = 275.590; self.circle2CZ = 154.140; self.circle2ER = 286.325; self.circle2EZ = 172.872
            elif self.rw == 8.5: 
                self.RwD       = 2.0
                self.line2R = 276.860
                self.circle2CR = 276.860; self.circle2CZ = 155.410; self.circle2ER = 288.037; self.circle2EZ = 175.352
            elif self.rw ==11.0: 
                self.RwD       = 4.5
                self.line2R = 166.992
                self.circle2CR = 166.992; self.circle2CZ = 220.645; self.circle2ER = 176.645; self.circle2EZ = 168.023
            else:
                self.lstInpLines.append('**************************************************************************\n')
                self.lstInpLines.append('** Input of RW is not define in 15degree Rim Contours Profile of TRA!  \n')
                self.lstInpLines.append('**************************************************************************\n')
            
            self.RwD = self.RwD+self.ChangeRW+self.Rim_Change
            
            self.startZ   =(self.startZ   +self.RwD*25.4/2)
            self.line1Z   =(self.line1Z   +self.RwD*25.4/2)
            self.circle1CZ=(self.circle1CZ+self.RwD*25.4/2)
            self.circle1EZ=(self.circle1EZ+self.RwD*25.4/2)
            self.line2Z   =(self.line2Z   +self.RwD*25.4/2)
            self.circle2CZ=(self.circle2CZ+self.RwD*25.4/2)
            self.circle2EZ=(self.circle2EZ+self.RwD*25.4/2)

            self.RdD=self.rd - 20.0 + self.ChangeRD

            self.startR   =(self.startR   +self.RdD*25.4/2)
            self.line1R   =(self.line1R   +self.RdD*25.4/2)
            self.circle1CR=(self.circle1CR+self.RdD*25.4/2)
            self.circle1ER=(self.circle1ER+self.RdD*25.4/2)
            self.line2R   =(self.line2R   +self.RdD*25.4/2)
            self.circle2CR=(self.circle2CR+self.RdD*25.4/2)
            self.circle2ER=(self.circle2ER+self.RdD*25.4/2)
            self.lstInpLines.append('** Tube Type Rim Profile\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('** Service Rim Width : ' + jsSns["AnalysisInformation"]["AnalysisCondition"][0]["RimWidth"] + '\n')
            self.lstInpLines.append('** Service Rim Dia   : ' + str(round(float(jsSns["VirtualTireParameters"]["RimDiameter"])/25.4)) + '\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*ELSET,ELSET=FLANGE\nBSW,HUS\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE,TYPE=ELEMENT, NAME=TFLANGE\n')
            self.lstInpLines.append('FLANGE\n')
            self.lstInpLines.append('*NODE,NSET=NLFLANGE\n')
            self.lstInpLines.append(' 3998, 0.0, 0.0, 0.0\n')
            self.lstInpLines.append('*NODE,NSET=NRFLANGE\n')
            self.lstInpLines.append(' 3999, 0.0, 0.0, 0.0\n')
            self.lstInpLines.append('*NSET,NSET=NFLANGE\n')
            self.lstInpLines.append('NLFLANGE,NRFLANGE\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE, TYPE=SEGMENT,NAME=LFLANGE\n')
            self.lstInpLines.append('START,%6.2fE-3,%6.2fE-3\n' % (self.circle2ER, self.circle2EZ))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.line2R, self.line2Z, self.circle2CR, self.circle2CZ))
            self.lstInpLines.append('LINE,%6.2fE-3,%6.2fE-3\n' % (self.circle1ER, self.circle1EZ))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.line1R, self.line1Z, self.circle1CR, self.circle1CZ))
            self.lstInpLines.append('LINE,%6.2fE-3,%6.2fE-3\n' % (self.startR, self.startZ))
            self.lstInpLines.append('*RIGID BODY,ANALYTICAL SURFACE=LFLANGE,REF NODE=NLFLANGE\n')
            self.lstInpLines.append('*CONTACT PAIR,INTERACTION=RIML, HCRIT=1.0e-3\nRIC_L,LFLANGE\n')
            self.lstInpLines.append('*SURFACE INTERACTION,NAME=RIML\n*SURFACE BEHAVIOR, AUGMENTED LAGRANGE\n ,0.0,1.0\n*FRICTION\n 0.015\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE, TYPE=SEGMENT,NAME=RFLANGE\n')
            self.lstInpLines.append('START,%6.2fE-3,-%6.2fE-3\n' % (self.startR,self.startZ))
            self.lstInpLines.append('LINE,%6.2fE-3,-%6.2fE-3\n' % (self.line1R,self.line1Z))
            self.lstInpLines.append('CIRCL,%6.2fE-3,-%6.2fE-3,%6.2fE-3,-%6.2fE-3\n' % (self.circle1ER,self.circle1EZ,self.circle1CR,self.circle1CZ))
            self.lstInpLines.append('LINE,%6.2fE-3,-%6.2fE-3\n'% (self.line2R,self.line2Z))
            self.lstInpLines.append('CIRCL,%6.2fE-3,-%6.2fE-3,%6.2fE-3,-%6.2fE-3\n' % (self.circle2ER,self.circle2EZ,self.circle2CR,self.circle2CZ))
            self.lstInpLines.append('*RIGID BODY,ANALYTICAL SURFACE=RFLANGE,REF NODE=NRFLANGE\n')
            self.lstInpLines.append('*CONTACT PAIR,INTERACTION=RIMR, HCRIT=1.0e-3\nRIC_R,RFLANGE\n')
            self.lstInpLines.append('*SURFACE INTERACTION,NAME=RIMR\n*SURFACE BEHAVIOR, AUGMENTED LAGRANGE\n ,0.0,1.0\n*FRICTION\n 0.015\n')
        else:
            # The source code of SH Kim is modified.
            self.rw = float(jsSns["AnalysisInformation"]["AnalysisCondition"][0]["RimWidth"])
            self.rd = round(float(jsSns["VirtualTireParameters"]["RimDiameter"])/25.4)
            self.lstInpLines = []
            
            # rxr, rxl, ryr, ryl are the constant values
            self.rxr = [-14.86, -27.095, -2.19, -0.52, 5.96, 5.96, 7.80, 7.80, 13.94]
            self.rxl = [-14.86, -27.095, -2.19, -0.52, 5.96, 5.96, 7.80, 7.80, 13.94]
            self.ryr = [44.621, 22.819, 25.00, 5.93, 6.50, 0.00, 0.00, -9.50, -16.75]
            self.ryl = [-44.621, -22.819, -25.00, -5.93, -6.50, 0.00, 0.00, 9.50, 16.75]
            
            self.rA = self.rw * 25.4        
            
            if (self.rA-math.trunc(self.rA)) >= 0.3 and (self.rA-math.trunc(self.rA)) <= 0.7 :
                self.rA = math.trunc(self.rA) + 0.5
            elif (self.rA-math.trunc(self.rA)) < 0.3:
                self.rA = math.trunc(self.rA)
            else:
                self.rA = math.trunc(self.rA) + 1.0
                
            self.rA = self.rA/2.0
            
            if self.rd <= 16:
                self.rDia = self.rd * 25.4 - 0.8
            if self.rd > 16:
                self.rDia = self.rd * 25.4 + 4.8
                
            self.rDia = self.rDia/2.0
            
            self.i = 0
            while self.i < 9:
                self.rxr[self.i] = self.rxr[self.i] + self.rDia
                self.rxl[self.i] = self.rxl[self.i] + self.rDia
                self.ryr[self.i] = self.ryr[self.i] - (self.rA + 100.0)
                self.ryl[self.i] = self.ryl[self.i] + (self.rA + 100.0)
                self.i = self.i + 1
                
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('** Service Rim Width : ' + jsSns["AnalysisInformation"]["AnalysisCondition"][0]["RimWidth"] + '\n')
            self.lstInpLines.append('** Service Rim Dia   : ' + str(round(float(jsSns["VirtualTireParameters"]["RimDiameter"])/25.4)) + '\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*ELSET,ELSET=FLANGE\nBSW,RIC\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE,TYPE=ELEMENT, NAME=TFLANGE\n')
            self.lstInpLines.append('FLANGE\n')
            self.lstInpLines.append('*NODE,NSET=NLFLANGE\n')
            self.lstInpLines.append(' 3998, 0.0, 0.0, 0.0\n')
            self.lstInpLines.append('*NODE,NSET=NRFLANGE\n')
            self.lstInpLines.append(' 3999, 0.0, 0.0, 0.0\n')
            self.lstInpLines.append('*NSET,NSET=NFLANGE\n')
            self.lstInpLines.append('NLFLANGE,NRFLANGE\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE, TYPE=SEGMENT,NAME=LFLANGE\n')
            self.lstInpLines.append('START,%6.2fE-3,%6.2fE-3\n' % (self.rxl[8],self.ryl[8]))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.rxl[6],self.ryl[6],self.rxl[7],self.ryl[7]))
            self.lstInpLines.append('LINE,%6.2fE-3,%6.2fE-3\n' % (self.rxl[5],self.ryl[5]))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.rxl[3],self.ryl[3],self.rxl[4],self.ryl[4]))
            self.lstInpLines.append('LINE,%6.2fE-3,%6.2fE-3\n' % (self.rxl[2],self.ryl[2]))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.rxl[0],self.ryl[0],self.rxl[1],self.ryl[1]))
            self.lstInpLines.append('*RIGID BODY,ANALYTICAL SURFACE=LFLANGE,REF NODE=NLFLANGE\n')
            self.lstInpLines.append('*CONTACT PAIR,INTERACTION=RIML, HCRIT=1.0e-3\nRIC_L,LFLANGE\n')
            self.lstInpLines.append('*SURFACE INTERACTION,NAME=RIML\n*SURFACE BEHAVIOR, AUGMENTED LAGRANGE\n ,0.0,1.0\n*FRICTION\n 0.015\n')
            self.lstInpLines.append('**************************************************************************\n')
            self.lstInpLines.append('*SURFACE, TYPE=SEGMENT,NAME=RFLANGE\n')
            self.lstInpLines.append('START,%6.2fE-3,%6.2fE-3\n' % (self.rxr[0],self.ryr[0]))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.rxr[2],self.ryr[2],self.rxr[1],self.ryr[1]))
            self.lstInpLines.append('LINE,%6.2fE-3,%6.2fE-3\n' % (self.rxr[3],self.ryr[3]))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.rxr[5],self.ryr[5],self.rxr[4],self.ryr[4]))
            self.lstInpLines.append('LINE,%6.2fE-3,%6.2fE-3\n'% (self.rxr[6],self.ryr[6]))
            self.lstInpLines.append('CIRCL,%6.2fE-3,%6.2fE-3,%6.2fE-3,%6.2fE-3\n' % (self.rxr[8],self.ryr[8],self.rxr[7],self.ryr[7]))
            self.lstInpLines.append('*RIGID BODY,ANALYTICAL SURFACE=RFLANGE,REF NODE=NRFLANGE\n')
            self.lstInpLines.append('*CONTACT PAIR,INTERACTION=RIMR, HCRIT=1.0e-3\nRIC_R,RFLANGE\n')
            self.lstInpLines.append('*SURFACE INTERACTION,NAME=RIMR\n*SURFACE BEHAVIOR, AUGMENTED LAGRANGE\n ,0.0,1.0\n*FRICTION\n 0.015\n')
            
class InpStepDescription:
    def modifyStepDescription(self, path, intNum, jsSns):
        self.lstInpLines = []
        self.strSimTask = jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Task"]  
        
        if self.strSimTask == '2DST':
            self.strSimTask = '2DST_v2_0'   
            try: 
                self.fileAnalysisTemplate = open(path + '/' + self.strSimTask + '.tpl')
            except: 
                self.strSimTask = '2DST'
                self.fileAnalysisTemplate = open(path + '/' + self.strSimTask + '.tpl')
            self.lstAnalysisTemplateTempLines = self.fileAnalysisTemplate.readlines()
            for self.strAnalysisTemplateTempLine in self.lstAnalysisTemplateTempLines:
                self.lstInpLines.append(self.strAnalysisTemplateTempLine.rstrip() + '\n')
            self.intInflation100Num=self.lstInpLines.index('**** STEP DESCRIPTIONS FOR INFLATION (100%)\n')
            self.intDeflation10Num=self.lstInpLines.index('**** STEP DESCRIPTIONS FOR DEFLATION (10%)\n')
            self.intPreCentrifugalNum=self.lstInpLines.index('**** STEP DESCRIPTIONS FOR INFLATION (100%) AGAIN\n')
            self.lstInpLines[self.intInflation100Num+11] = ' PRESS, P, ' + str(float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"])*9.81*(1E-2)*(1E+6)) + '\n'
            self.lstInpLines[self.intDeflation10Num+17] = ' PRESS, P, ' + str(float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"])*9.81*(1E-3)*(1E+6)) + '\n'
            self.lstInpLines[self.intPreCentrifugalNum+11] = ' PRESS, P, ' + str(float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"])*9.81*(1E-2)*(1E+6)) + '\n'

            self.intODNum=self.lstInpLines.index('OD = 667\n')
            self.intSpeedNum=self.lstInpLines.index('SPEED = 80.0\n')
            self.lstInpLines[self.intODNum] = 'OD =  ' + jsSns["VirtualTireParameters"]["OverallDiameter"] + '\n'
            try:
                self.lstInpLines[self.intSpeedNum] = 'SPEED = ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Velocity"] + '\n'
            except:
                self.lstInpLines[self.intSpeedNum] = 'SPEED = 0.0\n' 

        elif self.strSimTask == '3DST':
            self.strSimTask = '3DST_v2_0'   
            try: 
                self.fileAnalysisTemplate = open(path + '/' + self.strSimTask + '.tpl')
            except:
                self.strSimTask = '3DST'    
                self.fileAnalysisTemplate = open(path + '/' + self.strSimTask + '.tpl')
            self.lstAnalysisTemplateTempLines = self.fileAnalysisTemplate.readlines()
            for self.strAnalysisTemplateTempLine in self.lstAnalysisTemplateTempLines:
                PLATE_CONT_ELEM_LENGTH = 0.0118 * float(jsSns["VirtualTireParameters"]["OverallDiameter"]) - 2.7647
                for lstCompMaterial in jsSns["ElsetMaterialInfo"]["Mixing"]:
                    if 'SIR' in lstCompMaterial["Elset"]:
                        if jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"] == '0' or jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"] == '0.0':
                            CONT_SECT_ANG = 40
                    else:
                        CONT_SECT_ANG = 30
                CONT_SECT_ARC_LENGTH = math.pi * float(jsSns["VirtualTireParameters"]["OverallDiameter"]) * CONT_SECT_ANG / 360
                PLATE_CONT_ELEM_NUM = int(CONT_SECT_ARC_LENGTH / PLATE_CONT_ELEM_LENGTH)
                if '30.0, 30' in self.strAnalysisTemplateTempLine:
                    text = '30.0, '+ str(PLATE_CONT_ELEM_NUM) + '\n'
                    self.lstInpLines.append(text)
                elif '10.0,6' in self.strAnalysisTemplateTempLine:
                    pass
                elif '15.0,9' in self.strAnalysisTemplateTempLine:
                    pass
                elif '30.0,7' in self.strAnalysisTemplateTempLine:
                    pass
                else:
                    self.lstInpLines.append(self.strAnalysisTemplateTempLine.rstrip() + '\n')
            self.intParameterNum=self.lstInpLines.index('*PARAMETER\n')
            self.lstInpLines[self.intParameterNum+1] = 'PRESS =   ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"] + '\n'
            self.lstInpLines[self.intParameterNum+2] = 'OD =  ' + jsSns["VirtualTireParameters"]["OverallDiameter"] + '\n'
            self.lstInpLines[self.intParameterNum+3] = 'LOAD_100 =   ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"] + '\n'
            self.lstInpLines[self.intParameterNum+4] = 'CAMBER_ANGLE = ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["CamberAngle"] + '\n'
            try:
                self.lstInpLines[self.intParameterNum+5] = 'SPEED = ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Velocity"] + '\n'
            except:
                self.lstInpLines[self.intParameterNum+5] = 'SPEED = 0.0\n' 
            
            
            
        elif self.strSimTask == '3DKV':
            self.fileAnalysisTemplate = open(path + '/' + self.strSimTask + '.tpl')
            self.lstAnalysisTemplateTempLines = self.fileAnalysisTemplate.readlines()
            for self.strAnalysisTemplateTempLine in self.lstAnalysisTemplateTempLines:
                self.lstInpLines.append(self.strAnalysisTemplateTempLine.rstrip() + '\n')
            self.intParameterNum=self.lstInpLines.index('*PARAMETER\n')
            self.lstInpLines[self.intParameterNum+1] = 'PRESS =  ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"] + '\n'
            self.lstInpLines[self.intParameterNum+2] = 'OD =  ' + jsSns["VirtualTireParameters"]["OverallDiameter"] + '\n'
            Alpha = 0.0
            if float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"]) > 250 and float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"]) <= 800: Alpha = 50
            elif float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"]) > 800 and float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"]) <= 2000:   Alpha = 100
            else: Alpha = 25
            self.lstInpLines[self.intParameterNum+3] = 'LOAD_70 =  ' + str(float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"])-Alpha) + '\n'
            self.lstInpLines[self.intParameterNum+4] = 'LOAD_100 =  ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"] + '\n'
            self.lstInpLines[self.intParameterNum+5] = 'LOAD_140 =  ' + str(float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"])+Alpha) + '\n'
            
        elif self.strSimTask == '3DKL':
            self.fileAnalysisTemplate = open(path + '/' + self.strSimTask + '.tpl')
            self.lstAnalysisTemplateTempLines = self.fileAnalysisTemplate.readlines()
            for self.strAnalysisTemplateTempLine in self.lstAnalysisTemplateTempLines:
                self.lstInpLines.append(self.strAnalysisTemplateTempLine.rstrip() + '\n')
            self.intParameterNum=self.lstInpLines.index('*PARAMETER\n')
            self.lstInpLines[self.intParameterNum+1] = 'PRESS =   ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"] + '\n'
            self.lstInpLines[self.intParameterNum+2] = 'OD =  ' + jsSns["VirtualTireParameters"]["OverallDiameter"] + '\n'
            self.lstInpLines[self.intParameterNum+3] = 'LOAD_100 =   ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"] + '\n'
            
        elif self.strSimTask == '3DKD':
            self.fileAnalysisTemplate = open(path + '/' + self.strSimTask + '.tpl')
            self.lstAnalysisTemplateTempLines = self.fileAnalysisTemplate.readlines()
            for self.strAnalysisTemplateTempLine in self.lstAnalysisTemplateTempLines:
                self.lstInpLines.append(self.strAnalysisTemplateTempLine.rstrip() + '\n')
            self.intParameterNum=self.lstInpLines.index('*PARAMETER\n')
            self.lstInpLines[self.intParameterNum+1] = 'PRESS =   ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"] + '\n'
            self.lstInpLines[self.intParameterNum+2] = 'OD =  ' + jsSns["VirtualTireParameters"]["OverallDiameter"] + '\n'
            self.lstInpLines[self.intParameterNum+3] = 'LOAD_100 =   ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"] + '\n'
            
        elif self.strSimTask == '3DKT':
            self.fileAnalysisTemplate = open(path + '/' + self.strSimTask + '.tpl')
            self.lstAnalysisTemplateTempLines = self.fileAnalysisTemplate.readlines()
            for self.strAnalysisTemplateTempLine in self.lstAnalysisTemplateTempLines:
                self.lstInpLines.append(self.strAnalysisTemplateTempLine.rstrip() + '\n')
            self.intParameterNum=self.lstInpLines.index('*PARAMETER\n')
            self.lstInpLines[self.intParameterNum+1] = 'PRESS =   ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"] + '\n'
            self.lstInpLines[self.intParameterNum+2] = 'OD =  ' + jsSns["VirtualTireParameters"]["OverallDiameter"] + '\n'
            self.lstInpLines[self.intParameterNum+3] = 'LOAD_100 =   ' + jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Load"] + '\n'

def CreateMODEL(strSimCode, OD, Speed, Pressure):
    line = "** abaqus FIL file name 2d,3d w/o .file\n"
    line += strSimCode+"-2DST\n"
    line += strSimCode+"-3DST\n"
    line += "** MAT file name (tand)\n"
    line += "Mat12.txt\n"
    line += "** tire OD [mm], velocity [km/h]\n"
    line += str(OD) + "  " + str(Speed) + "\n"
    line += "** inflation pressure (bar,kgf/cm2)\n"
    line += str(Pressure) + "\n"
    line += "**STEP NUMBER : TARGET STEP FOR DATA ACQUISITION\n4\n"
    line += "**FULL KEY INDEX (1:HALF MODEL | 2:FULL MODEL)\n2\n"
    line += "** i_se, i_dw(0:dissip,1:fourier) : fix\n1  0\n"
    line += "**ORDER OF FOURIER SERIES : (in case of i_dw=1) fix\n20\n"
    line += "** angle (total sum =360), number of dividing\n"
    with open(strSimCode+"-3DST.inp", "r") as INP3D:
        lines = INP3D.readlines()
    for i, li in enumerate(lines):
        if "*SYMMETRIC MODEL GENERATION" in li:
            angle_section=lines[i+3]
            break
    # line += "30.0, 28\n"
    line += angle_section
    line += "60.0,6\n"
    line += "180.0,12\n"
    line += "60.0,6\n"
    # line += "30.0, 28"
    line += angle_section

    f = open("MODEL.txt", "w")
    f.writelines(line)
    f.close()

def CreateMaterial(ElsetCal, MatCal, ElsetSolid, MatSol):
    line = "** RUBBER MODULUS at 60 C\n*START MAT\n"
    tand_column = 4 ### need to change  to 4 (probably)
                    ### ('B87', '1218', '5.05E+07', '0.48'), 
    for name in ElsetSolid:
        for mat in MatSol: 
            if name[1] == mat[0]: 
                line+= "ELSET="+name[0]+"\n"
                if 'BD1' in name[0] : 
                    line+= "1.0  0.0 \n"
                else:
                    try:                    line+= "1.0  "+mat[tand_column] + "\n"
                    except:                 line+= "1.0  0.1 \n"

                break
    tand_column = 9 ### need to change  to 9 (probably)
                    ### ('T', 'ABM201A', 'N66 840D/2 28EPI', '2.46E-07', '0.4', '8.70E+02', '1.72358E+09', '1.00E-02', '1.00E-03')
    for name in ElsetCal:
        for mat in MatCal: 
            if name[2] == mat[1]: 
                line+= "ELSET="+name[0]+"\n"
                try:            line+= "1.0  "+mat[tand_column] + "\n"
                except:         line+= "1.0  0.0\n"
                break
    line += "ELSET=SWS\n1.0  0.0\n"
    line += "*END MAT"

    f = open("Mat12.txt", "w")
    f.writelines(line)
    f.close()

def CreateHeatInpFile(path, strInpLine, strSimTask, strSimCode):
    fileNewInp = open(path + '/' + strSimCode + '-' + strSimTask + '.inp', 'wb')
    fileNewInp.write(strInpLine)
    fileNewInp.close()  

def EdgeSharingElement(m, Element, show=0):


    
    for el in Element.Element:
        if m == el[0]: 
            target=el
            break 
    tnode=[]
    for i, tn in enumerate(target): 
        if i ==0: continue 
        if i ==5: break 
        if tn > 0 and not "" == tn: 
            tnode.append(tn)
    mN = len(tnode)

    if show ==1: print ("Target EL", target, "Nodes", tnode)

    # print ("Target EL", target, "Nodes", tnode)

    MATCH=TIRE.ELEMENT()

    for el in Element.Element:
        tmp=[]
        for i in range(1, el[6]+1): 
            if el[i] >0 or el[i]!='':           tmp.append(el[i])

        match = 0
        matchorder= []
        for tn in tnode:
            for k, t in enumerate(tmp):
                if tn == t:
                    match +=1
                    matchorder.append(k+1)
        if target[6] > 2:   ## not membrane 
            if match ==2 and el[0] != m and el[6] > 2:          
                MATCH.Add(el)
                # print ("EL", el)
        else:   ## membrane 
            if match ==2 and el[0] != m:
                if  matchorder[0] == el[6] and matchorder[1] ==1 : 
                    fEL = el 
                    # print ('order1', matchorder)
                else: 
                    if  matchorder[0] < matchorder[1] : 
                        # print ('order1', matchorder)
                        fEL = el
                    else: 
                        # print ('order2', matchorder)
                        sEL = el

    if target[6] == 2:
        MATCH.Add(fEL)
        MATCH.Add(sEL)
        # print ("T6")

    return MATCH

def AddNode(nodeid, shared, edge1, edge2, Node, ga):
    N1 = Node.NodeByID(edge1)
    N0 = Node.NodeByID(edge2)
    NormalVector = [0, N0[1]-N1[1], -N0[3]+N1[3], N0[2]-N1[2]]
    cl = math.sqrt((N1[2]-N0[2])*(N1[2]-N0[2])+(N1[3]-N0[3])*(N1[3]-N0[3]))

    for id in range(1, shared[6]+1):
        if shared[id] == edge1: 
            m = id
            mn = m+1
            mp = m-1
            if m == shared[6]:              mn = 1
            if m == 1:                      mp = shared[6]
            if shared[mn] == edge2:         LineNode = shared[mp]
            if shared[mp] == edge2: 
                mp = m+1
                if mp > shared[6]:          mp -= shared[6]
                LineNode = shared[mp]
    
    ## length between N1 and LineNode 
    N2 = Node.NodeByID(LineNode)
    LineVector = [0, N2[1]-N1[1], N2[2]-N1[2], N2[3]-N1[3]]
    pl = math.sqrt((N1[2]-N2[2])*(N1[2]-N2[2])+(N1[3]-N2[3])*(N1[3]-N2[3]))
    cos = (NormalVector[2]*LineVector[2] + NormalVector[3]*LineVector[3]) / (cl*pl)
    ratio = (0.5*ga)/abs(pl*cos)
    P1 = [nodeid, N1[1], N1[2]+LineVector[2]*ratio, N1[3] + LineVector[3]*ratio]
    
    Node.Add(P1)
    Info =[P1[0], shared[0], m, shared[m], LineNode]
    return Info

def Find_Elements_with_2nodes(n1, n2, Element): 
    element = TIRE.ELEMENT()
    for el in Element.Element:
        match = 0
        for i in range(1, el[6]+1): 
            if n1 == el[i] or n2 == el[i] : match+=1
        if match ==2: element.Add(el)
    return element

def Find_Element_with_1Node(n1, Element):
    element = TIRE.ELEMENT()
    for el in Element.Element:
        for i in range(1, el[6]+1): 
            if n1 == el[i] : 
                element.Add(el)
    return element

def Sharing_Nodes_with_2Elements(e1, e2, Element):
    n1=[]
    n2 = []
    n3=[]
    for e in Element.Element:
        if e[0] == e1: 
            for en in range(1, e[6]+1): n1.append(e[en])
        if e[0] == e2: 
            for en in range(1, e[6]+1): n2.append(e[en])
    
    for i in n1:
        for j in n2: 
            if i == j : 
                n3.append(i)
                break
    return n3


def CreateSteel(Edge, ga, Node, Element, iNode, iEl, name, sfline=[]):
    ## ga == equivalent gauge of steel cord 
    tmpEL = TIRE.ELEMENT()
    for EL in Element.Element: tmpEL.Add(EL)

    nodeid = iNode
    elid = iEl
    AddedNode=[]
    NodeChange = []
    createdsteel = []
    createdrubber = []
    for i, edge in enumerate(Edge.Edge):
        
        # if edge[4] > 2350 and edge[4] < 2360: show =1 
        # else : show = 0 
        
        shared = EdgeSharingElement(edge[4], Element)#, show=show)
        # if show==1: 
        #     for ed in shared.Element: 
        #         print (edge[4], ": ", ed[0], ed[1])

        if i ==0: 
            P1 = AddNode(nodeid, shared.Element[0], edge[0], edge[1], Node, ga)
            AddedNode.append(P1)
            nodeid +=1
            P2 = AddNode(nodeid, shared.Element[1], edge[0], edge[1], Node, ga)
            AddedNode.append(P2)
            nodeid +=1
            P3 = AddNode(nodeid, shared.Element[0], edge[1], edge[0], Node, ga)
            AddedNode.append(P3)
            nodeid +=1
            P4 = AddNode(nodeid, shared.Element[1], edge[1], edge[0], Node, ga)
            AddedNode.append(P4)
            nodeid +=1

            ## nodes of the elements that share the nodes of the membrane should move to the new nodes 
            node1 = P1[3]
            ElementsAtStart = Find_Element_with_1Node(node1, Element)   ## getting the elements with the 1st node of the membrane 
            k = 0
            membranenode=[0, 0]
            while k < len(ElementsAtStart.Element):
                if ElementsAtStart.Element[k][6] == 2:  
                    membranenode[0]= ElementsAtStart.Element[k][1]
                    membranenode[1]= ElementsAtStart.Element[k][2]                ##  delete 2D elements (cords)
                    del(ElementsAtStart.Element[k])
                    continue
                k += 1

            k = 0
            while k < len(ElementsAtStart.Element): 
                cnt = 0 
                if ElementsAtStart.Element[k][1] == membranenode[0] or ElementsAtStart.Element[k][1] == membranenode[1] : cnt += 1
                if ElementsAtStart.Element[k][2] == membranenode[0] or ElementsAtStart.Element[k][2] == membranenode[1] : cnt += 1
                if ElementsAtStart.Element[k][3] == membranenode[0] or ElementsAtStart.Element[k][3] == membranenode[1] : cnt += 1
                if ElementsAtStart.Element[k][4] == membranenode[0] or ElementsAtStart.Element[k][4] == membranenode[1] : cnt += 1
                
                if cnt == 2: 
                    del(ElementsAtStart.Element[k])
                    k -= 1
                k += 1
                
            # ElementsAtStart.Print()
            Moved=['', '']
            ToNode = ['', '']   # 

            CountMoved = 0
            for start in ElementsAtStart.Element:                  ## Now ElementsAtStart has no topping and steel elements 
                tEL = EdgeSharingElement(start[0], Element)        ## searching for the elements that are adjacent to the ElementsAtStart 
                
                if len(tEL.Element) == 2: ## the elements are tie couple 
                    targettie = 0 
                    cnt = 0 
                    slavetie = []
                    fd = 0
                    for line in sfline:
                        
                        if "Tie_m" in line: 
                            # print (line)
                            fd =1 
                            if targettie ==1: 
                                break 
                            continue 
                        
                        if fd ==1: 
                            if not "*" in line: 
                                data = int(list(line.split(","))[0])
                                if data == start[0]: 
                                    targettie = 1 
                                    continue
                            else:
                                fd = 0        
                        if targettie ==1: 
                            # print ("#####################")
                            cnt += 1
                            if cnt == 1: continue
                            # print (line)
                            if "*" in line: 
                                break 
                            else: 
                                data = int(list(line.split(","))[0])
                                slavetie.append(data)
                    # print (slavetie)           
                    for ed in slavetie: 
                        for el in Element.Element: 
                            if ed == el[0]: 
                                tEL.Add(el)
                                break 
                                
                                
                                
                k = 0                                              ## tEL may have topping and steel elements(membrane), therefore it needs to delete membrane (and topping elements??)
                while k < len(tEL.Element):       ## 1. delete membrane elements (they are not used in Heat analysis) from tEL.Element
                    if tEL.Element[k][6] == 2: 
                        del(tEL.Element[k])
                        continue
                    k+= 1
                for mch in tEL.Element:          ## normally it has 4 elements that share the node at the edge of membrane 
                    if mch[0] == P1[1]:          ## 2 of them are topping elements, and the others are the adjacent elements to the topping    (ToNode, Moved should have at least 2 values)
                        for k in range(1, start[6]+1):    ## P1 / P2 : element is on or under the membrane  
                            if P1[3] == start[k]:           ## check if the elements is adjacent to P1 element or P2 element 
                                for EL in Element.Element:
                                    if EL[0] == start[0]: 
                                        ToNode[0] = [EL[k], P2[0]]                      ## remember target node and element
                                        AddedNode.append([P1[0], EL[0], k, EL[k], 0])    ## remember the target node and element to move 
                                        start[9] = 0
                                        Moved[0]=EL
                                        CountMoved += 1
                                        break
                                break 
                        break
                    elif mch[0] == P2[1]: 
                        for k in range(1, start[6]+1):
                            if P2[3] == start[k]: 
                                for EL in Element.Element:
                                    if EL[0] == start[0]: 
                                        ToNode[1] = [EL[k], P2[0]]
                                        AddedNode.append([P2[0], EL[0], k, EL[k], 0])
                                        start[9]= 0
                                        Moved[1]=EL
                                        CountMoved += 1
                                        break
                                break 
                        break
            if Moved[0] !="": BetwEL = [AddedNode[len(AddedNode)-1][1], AddedNode[len(AddedNode)-2][1], AddedNode[len(AddedNode)-1][3], Moved[0][5]]
            else: BetwEL = [AddedNode[len(AddedNode)-1][1], AddedNode[len(AddedNode)-2][1], AddedNode[len(AddedNode)-1][3], Moved[1][5]]
            ## 
            ## ToNode should have 2 
            if CountMoved > 1: 
                for start in ElementsAtStart.Element:
                    if start[9] !=0:                        #  if there are another elements that should moved to new nodes 
                        if start[5] != Moved[0][5]:         #  if the name of the element is different from the already node moved element 
                            for EL in Element.Element:
                                if EL[0] == start[0]: 
                                    for k in range(1, EL[6]+1):
                                        if EL[k] == ToNode[1][0]: 
                                            AddedNode.append([P2[0], EL[0], k, EL[k], 0])
                                            BetwEL = [EL[0], start[0], EL[k], Moved[1][5]]
                        else:
                            for EL in Element.Element:
                                if EL[0] == start[0]: 
                                    for k in range(1, EL[6]+1):
                                        if EL[k] == ToNode[0][0]: 
                                            AddedNode.append([P1[0], EL[0], k, EL[k], 0])
                                            BetwEL = [EL[0], start[0], EL[k], Moved[0][5]]  ## insert triangular element into Void (that is made by node moving)
                                            break 
            else:
                for start in ElementsAtStart.Element:
                    if start[9] !=0:                        
                        for EL in Element.Element:
                            if EL[0] == start[0]: 
                                if  ToNode[1] != '':    m = 1
                                else: m = 0

                                for k in range(1, EL[6]+1):
                                    if EL[k] == ToNode[m][0]: 
                                        if ToNode[1] != '': AddedNode.append([P1[0], EL[0], k, EL[k], 0])
                                        else: AddedNode.append([P2[0], EL[0], k, EL[k], 0])
                                        BetwEL = [EL[0], start[0], EL[k], Moved[m][5]]
                                        
                
            CN = Sharing_Nodes_with_2Elements(BetwEL[0], BetwEL[1], Element)
            thirdNode =0
            for cn in CN:
                if cn != BetwEL[2]: 
                    thirdNode = cn 
                    break

            N1 = Node.NodeByID(P1[0])
            N2 = Node.NodeByID(P2[0])
            N3 = Node.NodeByID(thirdNode)

            if TIRE.NormalVector(N1[2], N2[2], N3[2], N1[3], N2[3], N3[3]) < 0:
                Element.Add([elid, P1[0], P2[0], thirdNode, '', BetwEL[3], 3, 0.0, 0.0, 0.0])
                createdrubber.append([elid, BetwEL[3]])
            else:
                Element.Add([elid, P2[0], P1[0], thirdNode, '', BetwEL[3], 3, 0.0, 0.0, 0.0])
                createdrubber.append([elid, BetwEL[3]])
            elid += 1
            
        elif i == len(Edge.Edge)-1:
        
            # print ("########################################")
            
            ################################################################
            ## for pre-existing element node change
            AddedNode.append(AddNode(nodeid-2, shared.Element[0], edge[0], edge[1], Node, ga))
            AddedNode.append(AddNode(nodeid-1, shared.Element[1], edge[0], edge[1], Node, ga))
            ################################################################
            P1 = P3
            P2 = P4 
            NN = len(AddedNode)
            P3 = AddNode(nodeid, shared.Element[0], edge[1], edge[0], Node, ga)
            
            AddedNode.append(P3)
            nodeid +=1
            
            P4 =AddNode(nodeid, shared.Element[1], edge[1], edge[0], Node, ga)
            AddedNode.append(P4)
            nodeid +=1
            # print (nodeid, shared.Element[1][0], 'EDGE', edge[1], edge[0], ga)
            # print (" >> P4 >> ", P4)  ## 
            node1 = P3[3]
            ElementsAtEnd = Find_Element_with_1Node(node1, Element)
            # print (">", len(ElementsAtEnd.Element))
            # for E in ElementsAtEnd.Element:
                # print (E[0])
            k = 0
            membranenode=[0, 0]
            while k < len(ElementsAtEnd.Element):    ## delete membrane element 
                if ElementsAtEnd.Element[k][6] == 2: 
                    membranenode[0]= ElementsAtEnd.Element[k][1]
                    membranenode[1]= ElementsAtEnd.Element[k][2]
                    del(ElementsAtEnd.Element[k])
                    continue
                k += 1
            # print (">>", len(ElementsAtEnd.Element))
            # for E in ElementsAtEnd.Element:
                # print (E[0])
            
            k = 0
            while k < len(ElementsAtEnd.Element): 
                cnt = 0 
                if ElementsAtEnd.Element[k][1] == membranenode[0] or ElementsAtEnd.Element[k][1] == membranenode[1] : cnt += 1
                if ElementsAtEnd.Element[k][2] == membranenode[0] or ElementsAtEnd.Element[k][2] == membranenode[1] : cnt += 1
                if ElementsAtEnd.Element[k][3] == membranenode[0] or ElementsAtEnd.Element[k][3] == membranenode[1] : cnt += 1
                if ElementsAtEnd.Element[k][4] == membranenode[0] or ElementsAtEnd.Element[k][4] == membranenode[1] : cnt += 1
                
                if cnt == 2: 
                    del(ElementsAtEnd.Element[k])
                    k -= 1
                k += 1
                    
                
            
            Moved=['', '']
            ToNode = ['', '']
            # print (">>>", len(ElementsAtEnd.Element))
            # for E in ElementsAtEnd.Element:
            #     print (E[0])
            CountMoved = 0
            for start in ElementsAtEnd.Element:
                tEL = EdgeSharingElement(start[0], Element)
                # print ("NO", len(tEL.Element), start)
                # for el in tEL.Element: 
                #     print ("      %d"%(el[0]))
                    
                if len(tEL.Element) == 2: ## the elements are tie couple 
                    targettie = 0 
                    cnt = 0 
                    slavetie = []
                    fd = 0
                    for line in sfline:
                        
                        if "Tie_m" in line: 
                            # print (line)
                            fd =1 
                            if targettie ==1: 
                                break 
                            continue 
                        
                        if fd ==1: 
                            if not "*" in line: 
                                data = int(list(line.split(","))[0])
                                if data == start[0]: 
                                    targettie = 1 
                                    continue
                            else:
                                fd = 0        
                        if targettie ==1: 
                            # print ("#####################")
                            cnt += 1
                            if cnt == 1: continue
                            # print (line)
                            if "*" in line: 
                                break 
                            else: 
                                data = int(list(line.split(","))[0])
                                slavetie.append(data)
                    # print (slavetie)           
                    for ed in slavetie: 
                        for el in Element.Element: 
                            if ed == el[0]: 
                                tEL.Add(el)
                                break 
                                
                
                k = 0 
                while k < len(tEL.Element): 
                    if tEL.Element[k][6] == 2: 
                        del(tEL.Element[k])
                        continue
                    k+= 1
                for mch in tEL.Element:
                    # print ("in .. ", mch[0], P3[1], P4[1])
                    if mch[0] == P3[1]:
                        for k in range(1, start[6]+1):
                            if P3[3] == start[k]: 
                                for EL in Element.Element:
                                    if EL[0] == start[0]: 
                                        ToNode[0] = [EL[k], P4[0]]
                                        AddedNode.append([P3[0], EL[0], k, EL[k], 0])
                                        # print ("11", P3[0], EL[0], k, EL[k])
                                        start[9] = 0
                                        Moved[0]=EL
                                        CountMoved += 1
                                        break
                                break 
                        break
                    elif mch[0] == P4[1]: 
                        
                        for k in range(1, start[6]+1):
                            if P4[3] == start[k]: 
                                for EL in Element.Element:
                                    if EL[0] == start[0]: 
                                        ToNode[1] = [EL[k], P4[0]]
                                        AddedNode.append([P4[0], EL[0], k, EL[k], 0])
                                        # print ("22", P4[0], EL[0], k, EL[k])
                                        start[9]= 0
                                        Moved[1]=EL
                                        CountMoved += 1
                                        break
                                break 
                        break
                    # else: 
                    #     print (" ll tie elementsss ")
                    #     print ("mch", mch[0], "p3", "p4", P3[1], P4[1])
                        
            if Moved[0] !="": 
                BetwEL = [AddedNode[len(AddedNode)-1][1], AddedNode[len(AddedNode)-2][1], AddedNode[len(AddedNode)-1][3], Moved[0][5]]
                # print ("AAA")
            else: 
                # print ("BBB")
                BetwEL = [AddedNode[len(AddedNode)-1][1], AddedNode[len(AddedNode)-2][1], AddedNode[len(AddedNode)-1][3], Moved[1][5]]
            # print ("3", BetwEL)
            if CountMoved > 1: 
                for start in ElementsAtEnd.Element:
                    if start[9] !=0:
                        if start[5] != Moved[0][5]: 
                            for EL in Element.Element:
                                if EL[0] == start[0]: 
                                    for k in range(1, EL[6]+1):
                                        if EL[k] == ToNode[1][0]: 
                                            AddedNode.append([P4[0], EL[0], k, EL[k], 0])
                                            BetwEL = [EL[0], start[0], EL[k], Moved[1][5]]
                        else:
                            for EL in Element.Element:
                                if EL[0] == start[0]: 
                                    for k in range(1, EL[6]+1):
                                        if EL[k] == ToNode[0][0]: 
                                            AddedNode.append([P3[0], EL[0], k, EL[k], 0])
                                            BetwEL = [EL[0], start[0], EL[k], Moved[0][5]]
            else:
                for start in ElementsAtEnd.Element:
                    if start[9] !=0:
                        for EL in Element.Element:
                            if EL[0] == start[0]: 
                                if ToNode[1] != '': m = 1
                                else: m = 0 
                                for k in range(1, EL[6]+1):
                                    if EL[k] == ToNode[m][0]: 
                                        if m == 1: AddedNode.append([P3[0], EL[0], k, EL[k], 0])
                                        else:  AddedNode.append([P4[0], EL[0], k, EL[k], 0])
                                        # print (P4[0], EL[0], k, EL[k], 0)
                                        # print (P3[0], EL[0], k, EL[k], 0)
                                        BetwEL = [EL[0], start[0], EL[k], Moved[m][5]]
                
            CN = Sharing_Nodes_with_2Elements(BetwEL[0], BetwEL[1], Element)
            # print (BetwEL[0],  BetwEL[1], CN)
            thirdNode =0
            for cn in CN:
                if cn != BetwEL[2]: 
                    thirdNode = cn 
                    break

            N1 = Node.NodeByID(P3[0])
            N2 = Node.NodeByID(P4[0])
            N3 = Node.NodeByID(thirdNode)
            # if elid == 10293: print (N3, CN)
            if TIRE.NormalVector(N1[2], N2[2], N3[2], N1[3], N2[3], N3[3]) < 0:
                Element.Add([elid, P3[0], P4[0], thirdNode, '', BetwEL[3], 3, 0.0, 0.0, 0.0])
                createdrubber.append([elid, BetwEL[3]])
            else:
                Element.Add([elid, P4[0], P3[0], thirdNode, '', BetwEL[3], 3, 0.0, 0.0, 0.0])
                createdrubber.append([elid, BetwEL[3]])

            elid += 1

        else:
            ################################################################
            ## for pre-existing element node change
            AddedNode.append(AddNode(nodeid-2, shared.Element[0], edge[0], edge[1], Node, ga))
            AddedNode.append(AddNode(nodeid-1, shared.Element[1], edge[0], edge[1], Node, ga))
            ################################################################
            
            P1 = P3
            P2 = P4 
            P3 = AddNode(nodeid, shared.Element[0], edge[1], edge[0], Node, ga)
            AddedNode.append(P3)
            nodeid +=1
            P4 = AddNode(nodeid, shared.Element[1], edge[1], edge[0], Node, ga)
            AddedNode.append(P4)
            nodeid +=1

        
        N1 = Node.NodeByID(P1[0])
        N2 = Node.NodeByID(P2[0])
        N3 = Node.NodeByID(P3[0])
        N4 = Node.NodeByID(P4[0])

        # if TIRE.NormalVector(N1[2], N2[2], N3[2], N1[3], N2[3], N3[3]) < 0:
        #       Element.Add([elid, P1[0], P2[0], thirdNode, '', BetwEL[3], 3, 0.0, 0.0, 0.0])
        #       createdrubber.append([elid, BetwEL[3]])
        for k in range(5): 
            if k == 0: 
                x1 = N1[2]; x2 = N2[2]; x3 = N3[2]; x4 = N4[2]
                y1 = N1[3]; y2 = N2[3]; y3 = N3[3]; y4 = N4[3]
                Jacob = TIRE.Jacobian(x1, x2, x3, x4, y1, y2, y3, y4)
                if Jacob > 0:       continue
                else:
                    Vec = TIRE.NormalVector(x1, x2, x3, y1, y2, y3)
                    if  Vec < 0:    EN1 = P1; EN2 = P2; EN3 = P3; EN4=P4
                    else:           EN1 = P1; EN2 = P4; EN3 = P3; EN4=P2
                    # print ("%d - CASE 1 (%f)"%(elid, Vec) )
                    break 
            if k == 1: 
                x1 = N2[2]; x2 = N1[2]; x3 = N3[2]; x4 = N4[2]
                y1 = N2[3]; y2 = N1[3]; y3 = N3[3]; y4 = N4[3]
                Jacob = TIRE.Jacobian(x1, x2, x3, x4, y1, y2, y3, y4)
                if Jacob > 0:       continue
                else:
                    Vec = TIRE.NormalVector(x1, x2, x3, y1, y2, y3)
                    if  Vec < 0:    EN1 = P2; EN2 = P1; EN3 = P3; EN4=P4
                    else:           EN1 = P2; EN2 = P4; EN3 = P3; EN4=P1
                    # print ("%d - CASE 2 (%f)"%(elid, Vec) )
                    break 
            if k == 2: 
                x1 = N1[2]; x2 = N2[2]; x3 = N4[2]; x4 = N3[2]
                y1 = N1[3]; y2 = N2[3]; y3 = N4[3]; y4 = N3[3]
                Jacob = TIRE.Jacobian(x1, x2, x3, x4, y1, y2, y3, y4)
                if Jacob > 0:       continue
                else:
                    Vec = TIRE.NormalVector(x1, x2, x3, y1, y2, y3)
                    if  Vec < 0:    EN1 = P1; EN2 = P2; EN3 = P4; EN4=P3
                    else:           EN1 = P1; EN2 = P3; EN3 = P4; EN4=P2
                    # print ("%d - CASE 3 (%f)"%(elid, Vec) )
                    break 
            if k == 3: 
                x1 = N1[2]; x2 = N4[2]; x3 = N3[2]; x4 = N2[2]
                y1 = N1[3]; y2 = N4[3]; y3 = N3[3]; y4 = N2[3]
                Jacob = TIRE.Jacobian(x1, x2, x3, x4, y1, y2, y3, y4)
                if Jacob > 0:       continue
                else:
                    Vec = TIRE.NormalVector(x1, x2, x3, y1, y2, y3)
                    if  Vec < 0:    EN1 = P1; EN2 = P4; EN3 = P3; EN4=P2
                    else:           EN1 = P1; EN2 = P2; EN3 = P3; EN4=P4
                    # print ("%d - CASE 4 (%f)"%(elid, Vec) )
                    break 
            if k == 4: 
                x1 = N2[2]; x2 = N1[2]; x3 = N4[2]; x4 = N3[2]
                y1 = N2[3]; y2 = N1[3]; y3 = N4[3]; y4 = N3[3]
                Jacob = TIRE.Jacobian(x1, x2, x3, x4, y1, y2, y3, y4)
                if Jacob > 0:       continue
                else:
                    Vec = TIRE.NormalVector(x1, x2, x3, y1, y2, y3)
                    if  Vec < 0:    EN1 = P2; EN2 = P1; EN3 = P4; EN4=P3
                    else:           EN1 = P2; EN2 = P3; EN3 = P4; EN4=P1
                    # print ("%d - CASE 5 (%f)"%(elid, Vec) )
                    break 
            if k == 5: 
                x1 = N2[2]; x2 = N3[2]; x3 = N4[2]; x4 = N1[2]
                y1 = N2[3]; y2 = N3[3]; y3 = N4[3]; y4 = N1[3]
                Jacob = TIRE.Jacobian(x1, x2, x3, x4, y1, y2, y3, y4)
                if Jacob > 0:       continue
                else:
                    Vec = TIRE.NormalVector(x1, x2, x3, y1, y2, y3)
                    if  Vec < 0:    EN1 = P2; EN2 = P3; EN3 = P4; EN4=P1
                    else:           EN1 = P2; EN2 = P1; EN3 = P4; EN4=P3
                    # print ("%d - CASE 6 (%f)"%(elid, Vec) )
                    break 
        Element.Add([elid, EN1[0], EN2[0], EN3[0], EN4[0], name, 4, 0.0, 0.0, 0.0])
        
        createdsteel.append(elid)
        elid += 1
        P1 = EN4; P2 = EN3 
    
    changedel=[]
    for add in AddedNode:
        for EL in Element.Element:
            if EL[6] == 3:
                if EL[0] == add[1]:     
                    cnode = EL[add[2]]
                    E_shared = EdgeSharingElement(EL[0], tmpEL) 
                    for a in AddedNode:
                        k = 0
                        while k < len(E_shared.Element) : 
                            if a[1] == E_shared.Element[k][0]: 
                                del(E_shared.Element[k])
                                k -= 1
                            k += 1
                    if len(E_shared.Element)> 0:        
                        for sel in Element.Element:
                            if sel[0] == E_shared.Element[0][0]: 
                                for ni in range(1, sel[6]+1): 
                                    if sel[ni] == EL[add[2]]: 
                                        sel[ni] = add[0]          ## change the node id for the element adjacent to the tri-angular element  to the newly created node. 
                    EL[add[2]] = add[0]  ## change the node id to the newly created node. 
                    break

            else:
                if EL[0] == add[1]:     
                    EL[add[2]] = add[0]  ## change the node id to the newly created node. 
                    break

    del(tmpEL)
    return nodeid, elid, createdsteel, createdrubber


def CreateHeatAnalysisInput(path, jsSns, SolidElset, SolidMat, CalElset, CalMat, ambient=25.0, steel=1, OD=0.0, Speed=0.0):
    strSimCode = str(jsSns["AnalysisInformation"]["SimulationCode"])
    with open(path + '/' + strSimCode + '-2DST.inp') as fileCuteInp:
        lstCuteInpTempLines = fileCuteInp.readlines()
    lstInpLines = []
    for strCuteInpTempLines in lstCuteInpTempLines:
        if strCuteInpTempLines.strip() != '':
            lstInpLines.append(strCuteInpTempLines.strip() + '\n')

    lstCommentLines =[]
    lstHeadingLines=[]
    lstElsetLines = []
    lstSurfaceLines=[]
    lstTieLines=[]
    lstNsetLines=[]
    lstMaterialLines=[]
    ABWcount =0 
    for line in lstInpLines:
        if '***** C/C Ply ****' in line or '****** Belt Ply *******' in line: break
        if '**' in line:
            lstCommentLines.append(line)
            continue

        word = list(line.split(','))
        if word[0] == '\n' :
            pass
        else:
            if word[0][0] == '*':
                command = list(word[0].split('*'))
                if command[1][:7] == 'Heading':
                    spt = 'HD'
                    lstHeadingLines.append(line)
                elif command[1] == 'NODE':
                    spt = 'ND'
                elif command[1] == 'ELEMENT':
                    EL = list(word[1].split('='))
                    EL = EL[1].strip()
                    if EL == 'MGAX1':               spt = 'M1'
                    elif EL == 'CGAX3H':            spt = 'C3'
                    elif EL == 'CGAX4H':            spt = 'C4'
                    else:                           spt = 'NN'
                elif command[1] == 'SURFACE':
                    spt = 'SF'
                    lstSurfaceLines.append(line)
                elif command[1] == 'TIE':
                    spt = 'TI'
                    lstTieLines.append(line)
                elif command[1] == 'ELSET':
                    if "C0" in word[1] or "CH" in word[1] or "JF" in word[1] or "BDC" in word[1] \
                        or "JE" in word[1] or "BT1" in word[1]  or "BT2" in word[1]  or "BT3" in word[1]  or "BT4" in word[1]  or "SPC" in word[1] or "RFM" in word[1] : 
                        spt = "MEMB"
                    else:   
                        spt = 'ES'
                        lstElsetLines.append(line)
                elif command[1] == 'NSET':
                    spt = 'NS'
                    lstNsetLines.append(line)
                elif 'MATERIAL' in command[1]:     
                    lstMaterialLines.append(line)
                    materialName = word[1].split("=")[1].strip()
                    spt = 'MT_n'
                elif 'DENSITY'in  command[1]:           
                    lstMaterialLines.append(line)
                    spt = 'MT_d'
                elif 'HYPERELASTIC'in  command[1] or 'ELASTIC'in  command[1]  :
                    lstMaterialLines.append(line)
                    spt = 'MT_e'
                elif 'SOLID SECTION'in  command[1]:         
                    lstMaterialLines.append( line )
                else:
                    spt = ''
            else:
                if spt == 'HD':                 pass
                if spt == 'ND':                 pass
                if spt == 'M1':                 pass
                if spt == 'C3':                 pass
                if spt == 'C4':                 pass
                if spt == 'NS':                 lstNsetLines.append(line)
                if spt == 'ES':                 lstElsetLines.append(line)
                if spt == 'SF':                 lstSurfaceLines.append(line)
                if spt == 'TI':                 lstTieLines.append(line)
                if spt == 'MT_n':               lstMaterialLines.append(line)
                if spt == 'MT_d':               lstMaterialLines.append(line)
                if spt == 'MT_e':
                    lstMaterialLines.append(line)
                    ### ('B87', '1218', '5.05E+07', '0.48', tan d, conductivity), 
                    if 'SWS' in materialName: 
                        for name in SolidElset:
                            if "BSW" in name[0] : 
                                materialName = name[1]
                                break

                    for name in SolidElset:
                        fd = 0 
                        for mat in SolidMat: 
                            if materialName == mat[0]: 
                                line = '*CONDUCTIVITY\n' + str(mat[5]) + "\n"
                                lstMaterialLines.append(line)
                                fd = 1
                                break
                        if fd == 1: 
                            break 
                        
                else:
                    pass

    # for mat in SolidMat: 
    #     print ("Material", mat)
    # for name in SolidElset:
    #     print ("ELSET", name)

    Mesh2D = strSimCode.split("-")[1]+"-"+strSimCode.split("-")[2]+".inp"
    Mesh2D = strSimCode.split("-")[1]+"-"+strSimCode.split("-")[2]+".msh"
    Node, Element, Elset, commt = TIRE.Mesh2DInformation(path + '/' +Mesh2D)
    outerprofile = Element.OuterEdge(Node)

    EdgeTread = TIRE.EDGE()
    for edge in outerprofile.Edge:      
        if edge[2] == "CTB" or edge[2] == "SUT" or edge[2] == "TRW": EdgeTread.Add(edge)
    try:
        TreadDesignWidth = float(jsSns["VirtualTireParameters"]["TreadDesignWidth"])
    except:
        print ("No Tread Design Width Value in SNS file. Replace it with Widest Belt Width+5%")
        BT = Element.Elset("BT3")
        if len(BT.Element) == 0:
            BT = Element.Elset("BT1")
        else:
            BT = Element.Elset("BT2")
        Length = 0.0
        for el in BT.Element:
            Length += el[7]
        TreadDesignWidth = Length * 1.05 * 1000


        
    GrooveCrown = TIRE.GrooveDetectionFromEdge(outerprofile, Node, OnlyTread=1, TreadNumber=1)
    NoGrooveCrown = TIRE.DeleteGrooveEdgeAfterGrooveDetection(GrooveCrown, Node)
    # NoGrooveCrown.Image(Node,"NoGroove", "o")
    N = len(NoGrooveCrown.Edge)
    
    TWEnd = 0
    TWStart = 0 
    CenterEdge = 0 
    CrownEdge = TIRE.EDGE()
    TopZ = 0.0
    TopNode = 0
    iscentergroove = 0
    for i in range(N):
        N1 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
        N2 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
        if N1[2] == 0.0:
            CenterEdge = i
            CenterNode = N1
            iscentergroove = 0
        elif N1[2]*N2[2] < 0.0:
            CenterEdge = i
            CenterNode = [0, 0.0, 0.0, (N1[3]*abs(N2[2])+N2[3]*abs(N1[2]))/(abs(N1[2])+abs(N2[2]))]
            iscentergroove = 1

    Min = 9.9E20;    hMin = 9.9E20
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
        # print ("right", NoGrooveCrown.Edge[i], Length, TreadDesignWidth/2000)

        if TreadDesignWidth/2000.0-Length >= 0: 
            RightTWNode = N2
    # print ("Right TW Node = %d, Right Mid node = %d"%(RightTWNode[0], RightMidNode[0]))

    Min = 9.9E20;    hMin = 9.9E20
    Length = 0.0
    for i in range(CenterEdge, -1, -1):
        if iscentergroove ==1 and i == CenterEdge:
            N1 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
            Length += math.sqrt( (CenterNode[2] - N1[2]) * (CenterNode[2] - N1[2]) + (CenterNode[3] - N1[3]) * (CenterNode[3] - N1[3]) )
            # print ("Left 0", NoGrooveCrown.Edge[i], Length*1000, TreadDesignWidth/2.0)
            CenterNode = Node.Node[0]
            for nd in Node.Node:
                if nd[2] == 0 and nd[3] > CenterNode[3]:   CenterNode = nd 
        else:
            if i != CenterEdge:
                N1 = Node.NodeByID(NoGrooveCrown.Edge[i][0])
                N2 = Node.NodeByID(NoGrooveCrown.Edge[i][1])
                Length += math.sqrt( (N1[2] - N2[2]) * (N1[2] - N2[2]) + (N1[3] - N2[3]) * (N1[3] - N2[3]) )
                # print ("Left -", NoGrooveCrown.Edge[i], Length*1000, TreadDesignWidth/2.0)

        if TreadDesignWidth/2000.0-Length >= 0: 
            LeftTWNode = N1

    # print ("Left TW Node = %d, Left Mid node = %d"%(LeftTWNode[0], LeftMidNode[0]))
    # print ("Tread Width = %f"%(TreadDesignWidth))
    TWStart = LeftTWNode[0];     TWEnd = RightTWNode[0]; TopNode = CenterNode[0]

    print ("** Sho.Drop Check Node ID : %d, %d, Crown Center Node ID : %d"%(TWStart, TWEnd, TopNode))
    outerprofile = Element.OuterEdge(Node)
    EdgeInner = TIRE.EDGE()
    EdgeTread = TIRE.EDGE()
    EdgeSide = TIRE.EDGE()
    for edge in outerprofile.Edge:
        if edge[2] == "L11": EdgeInner.Add(edge)
        if edge[2] == "CTB" or edge[2] == "SUT" or edge[2] == "TRW": EdgeTread.Add(edge)
        if edge[2] == "BSW": EdgeSide.Add(edge)
        if edge[2] == "RIC" or edge[2] == "HUS": EdgeInner.Add(edge)

    TreadSurface = []
    UppersideSurface=[]
    EdgeTread.Sort(item=-1)
    isin = 0
    for edge in EdgeTread.Edge:
        if edge[0] == TWStart:          isin =1
        if edge[0] == TWEnd:            isin = 0
        if isin == 1:           TreadSurface.append([edge[4], edge[3]])
        else:                   UppersideSurface.append([edge[4], edge[3]])
        
        # if isin==1: print (edge[4], edge[3])

    EdgeInner.Sort(item=-1)
    InnerSurface=[]
    
    for edge in EdgeInner.Edge:
        N1 = Node.NodeByID(edge[0]); N2 = Node.NodeByID(edge[1])
        if N1[3] > N2[3] :          edge[5] =0
        else:                       break
    I = len(EdgeInner.Edge)
    for i in range(I-1, 0, -1):
        N1 = Node.NodeByID(EdgeInner.Edge[i][0])
        N2 = Node.NodeByID(EdgeInner.Edge[i][1])
        if N1[3] < N2[3] :          EdgeInner.Edge[i][5] =0
        else:                       break
    
    for edge in EdgeInner.Edge:
        if edge[5] ==1: InnerSurface.append([edge[4], edge[3]])

    file2Dst= path + '/' + strSimCode + '-2DST.inp'
    with open(file2Dst, "r") as In:
        lines = In.readlines()
    SteelElset=[]
    for i, line in enumerate(lines):
        if '*SURFACE' in line and 'SEGMENT' in line and 'LFLANGE' in line: 
            flangecircle = lines[i+2]
        if '*REBAR' in line and 'MATERIAL=S' in line:
            SteelElset.append(line)
    
    circle = flangecircle.split(",")
    flange_r = math.sqrt(  (float(circle[1])-float(circle[3]))*(float(circle[1])-float(circle[3]))+(float(circle[2])-float(circle[4]))*(float(circle[2])-float(circle[4]))  )
    flange_h = float(circle[3])+flange_r + 0.005
    del(lines)

    BeadSurface=[]
    LowsideSurfce = []
    for edge in EdgeInner.Edge:
        if edge[5] == 0:
            N1 = Node.NodeByID(edge[0])
            N2 = Node.NodeByID(edge[1])

            if N1[3] < flange_h or N2[3] < flange_h: 
                BeadSurface.append([edge[4], edge[3]])
            else: LowsideSurfce.append([edge[4], edge[3]])
    
    cedge = Element.ElsetToEdge("C01")
    cedge.Sort(item=-1)
    i = 0
    while len(cedge.Edge)> 0:
        N1 = Node.NodeByID(cedge.Edge[i][0])
        N2 = Node.NodeByID(cedge.Edge[i][1])
        if N1[3] > N2[3]: 
            del(cedge.Edge[i])
            i -=1
        else: 
            break
    maxcw = 0.0
    maxcwh = 0.0
    for edge in cedge.Edge:
        N1 = Node.NodeByID(edge[0])
        if N1[2]> maxcw:
            maxcw = N1[2]
            maxcwh = N1[3]

    for edge in EdgeSide.Edge:
        N1 = Node.NodeByID(edge[0])
        N2 = Node.NodeByID(edge[1])
        if N1[3] < maxcwh and N2[3] < maxcwh:   LowsideSurfce.append([edge[4], edge[3]])
        else:                                   UppersideSurface.append([edge[4], edge[3]])


    if steel ==1:
        
        line += "*****************************************************************\n"
        line += "** Steel Element Generateion\n"
        line += "*****************************************************************\n"
        ## ('S', 'ABS401A', '3+9(0.22)+wNT', '4.94E-07', '0.3', '7.77E+03', '1.51342E+11', '1.00E-02', '1.00E-03'
        ## steel/Textile, code, structure, section area, V, ??, E(modulus), Compression_modulus??, Compression_strain??

        # for el in Element.Element:
        #     print(el)
        
        # print ("A")
        steel = []
        for elset in CalElset:
            for mat in CalMat:
                if elset[2] == mat[1] and mat[0] == 'S': 
                    ht = float(mat[3]) * float(elset[6]) / 0.0254 * 2
                    steel.append( [elset[0], ht] )
        # print ("B")
        nid = 10001
        eid = 10001
        for el in steel:
            membedge = Element.ElsetToEdge(el[0])
            if 'CH' in el[0]: 
                CH_R = TIRE.EDGE()
                CH_L = TIRE.EDGE()
                for mem in membedge.Edge:
                    if Node.NodeByID(mem[0])[2]> 0: CH_R.Add(mem)
                    else: CH_L.Add(mem)
                
                CH_R.Sort(item=-1)
                CH_L.Sort(item=-1)
                nid, eid, EL_steel_R, EL_rubber_R = CreateSteel(CH_R, el[1], Node, Element, nid, eid, el[0], sfline=lstSurfaceLines)
                nid, eid, EL_steel_L, EL_rubber_L = CreateSteel(CH_L, el[1], Node, Element, nid, eid, el[0], sfline=lstSurfaceLines)
            elif 'RFM' in el[0]: 
                RFM_R = TIRE.EDGE()
                RFM_L = TIRE.EDGE()
                for mem in membedge.Edge:
                    if Node.NodeByID(mem[0])[2]> 0: RFM_R.Add(mem)
                    else: RFM_L.Add(mem)
                
                RFM_R.Sort(item=-1)
                RFM_L.Sort(item=-1)
                nid, eid, EL_steel_R, EL_rubber_R = CreateSteel(RFM_R, el[1], Node, Element, nid, eid, el[0], sfline=lstSurfaceLines)
                nid, eid, EL_steel_L, EL_rubber_L = CreateSteel(RFM_L, el[1], Node, Element, nid, eid, el[0], sfline=lstSurfaceLines)
            else:
                membedge.Sort(item=-1)
                nid, eid, EL_steel, EL_rubber = CreateSteel(membedge, el[1], Node, Element, nid, eid, el[0], sfline=lstSurfaceLines)
                
            lstElsetLines += ["*ELSET, ELSET="+el[0]+"\n"]
            txt = ''
            if 'CH' in el[0] or 'RFM' in el[0]: 
                for k, st in enumerate(EL_steel_R):
                    if (k+1) % 10 !=0:      txt += str(format(st, '6d'))+', '
                    else:                   txt += str(format(st, '6d'))+'\n'
                if (k+1) % 10 ==0:  txt += ''
                else: txt += '\n'
                for k, st in enumerate(EL_steel_L):
                    if (k+1) % 10 !=0:      txt += str(format(st, '6d'))+', '
                    else:                   txt += str(format(st, '6d'))+'\n'
                lstElsetLines += txt    
                if (k+1) % 10 ==0:  txt = ''
                else: txt = '\n'

                for k, st in enumerate(EL_rubber_R):
                    txt += "*ELSET, ELSET="+st[1]+"\n"
                    txt += str(format(st[0], '6d'))+'\n'
                for k, st in enumerate(EL_rubber_L):
                    txt += "*ELSET, ELSET="+st[1]+"\n"
                    txt += str(format(st[0], '6d'))+'\n'
                
            else:
                if len(EL_steel) > 0: 
                    for k, st in enumerate(EL_steel):
                        if (k+1) % 10 !=0:      txt += str(format(st, '6d'))+', '
                        else:                   txt += str(format(st, '6d'))+'\n'
                    lstElsetLines += txt    
                    if (k+1) % 10 ==0:  txt = ''
                    else: txt = '\n'
                if len(EL_rubber)>0: 
                    for k, st in enumerate(EL_rubber):
                        txt += "*ELSET, ELSET="+st[1]+"\n"
                        txt += str(format(st[0], '6d'))+'\n'

                    if EL_rubber[0][1] == 'SHOTOPPING': 
                         for k, st in enumerate(EL_rubber):
                            txt += "*ELSET, ELSET=BTT\n"
                            txt += str(format(st[0], '6d'))+'\n'

                    
            lstElsetLines += txt    
        Helement = TIRE.ELEMENT()
        NELr = TIRE.ELEMENT()
        for EL in Element.Element:
            if EL[6] > 2:# and EL[5] != "BT1" and EL[5] != "BT2" and EL[5] != "BT3" and EL[5] != "C01" and EL[5] != "BT4" and EL[5] != "CH1" : 
                Helement.Add(EL)
            if EL[0] >= 10000: NELr.Add(EL)
        imagefilename = strSimCode.split("-")[1] +"-" + strSimCode.split("-")[2] + "-2DMesh.png"
        Helement.Image(Node, imagefilename, dpi=500)


    Node.DeleteDuplicate()
    line = []
    for l in lstCommentLines: 
        if "END OF MATERIAL INFO" in l: 
            break
        line += l
    line += lstHeadingLines
    line += "*NODE, SYSTEM=R, NSET=NODEALL\n"
    Node.DeleteDuplicate()
    for node in Node.Node:
        txt = str(format(node[0], '6d')) + ", " + str(format(node[3], '6E')) + ", " + str(format(node[2], '.6E')) + ", " + str(format(node[1], '.6E')) + "\n"
        line += txt
    line += "*ELEMENT, TYPE=DCAX3\n"
    for EL in Element.Element:
        if EL[6] == 3:
            txt = str(format(EL[0], '6d')) + ","+ str(format(EL[1], '6d')) + ","+ str(format(EL[2], '6d')) + ","+ str(format(EL[3], '6d')) + "\n"
            line += txt
    line += "*ELEMENT, TYPE=DCAX4\n"
    for EL in Element.Element:
        if EL[6] == 4:
            txt = str(format(EL[0], '6d')) + ","+ str(format(EL[1], '6d')) + ","+ str(format(EL[2], '6d')) + ","+ str(format(EL[3], '6d')) + ","+ str(format(EL[4], '6d')) + "\n"
            line += txt
    line += lstElsetLines
    line += lstNsetLines
    line += lstSurfaceLines
    line += lstTieLines
    line += lstMaterialLines
    
    steel_cond = 40.0               ### temporary
    for el in steel: 
        line += "*SOLID SECTION, ELSET="+ el[0] + ",    MATERIAL=" + el[0] +"\n"
        line += "*MATERIAL, NAME=" + el[0] + '\n'
        line += "*CONDUCTIVITY\n" + str(steel_cond) + '\n'

    line += "*SURFACE, TYPE=ELEMENT, NAME=SURFACE_TREAD\n"
    for li in TreadSurface:         line += str(li[0]) +", " + li[1] + "\n"
    line += "*SURFACE, TYPE=ELEMENT, NAME=SURFACE_UPSIDE\n"
    for li in UppersideSurface:         line += str(li[0]) +", " + li[1] + "\n"
    line += "*SURFACE, TYPE=ELEMENT, NAME=SURFACE_DOWNSIDE\n"
    for li in LowsideSurfce:        line += str(li[0]) +", " + li[1] + "\n"
    line += "*SURFACE, TYPE=ELEMENT, NAME=SURFACE_BEAD\n"
    for li in BeadSurface:      line += str(li[0]) +", " + li[1] + "\n"
    line += "*SURFACE, TYPE=ELEMENT, NAME=SURFACE_INNER\n"
    for li in InnerSurface:         line += str(li[0]) +", " + li[1] + "\n"

    line += "*ELSET, ELSET=CAVITYELSET\n"
    for k, li in enumerate(TreadSurface):       
        # line += str(li[0]) +", " + li[1] + "\n"
        if (k+1)%10 == 0:   line += str(li[0]) + "\n"
        else:               line += str(li[0]) + ", "
    if (k+1)%10 !=0: line += "\n"
    for k, li in enumerate(UppersideSurface):       
        # line += str(li[0]) +", " + li[1] + "\n"
        if (k+1)%10 == 0:   line += str(li[0]) + "\n"
        else:               line += str(li[0]) + ", "
    if (k+1)%10 !=0: line += "\n"
    for k, li in enumerate(LowsideSurfce):      
        # line += str(li[0]) +", " + li[1] + "\n"
        if (k+1)%10 == 0:   line += str(li[0]) + "\n"
        else:               line += str(li[0]) + ", "
    if (k+1)%10 !=0: line += "\n"
    line += '*SURFACE, NAME=CAVITY_SURFACE, PROPERTY=RUBBER_EMISSIVITY, TYPE=ELEMENT\n CAVITYELSET\n'
    line += '*SURFACE PROPERTY, NAME=RUBBER_EMISSIVITY\n'
    line += '*EMISSIVITY\n 0.9\n'

    ## initial temperature (ambient/inner): 25degree 

    line += '*CAVITY DEFINITION, NAME=SURFACE_CAVITY, AMBIENT TEMP='+str(ambient)+'\n CAVITY_SURFACE, CAVITY_SURFACE\n'
    line += '*PHYSICAL CONSTANTS, STEFAN=5.67E-8, ABSOLUTE ZERO=-273.15\n'
    line += '*INITIAL CONDITION,TYPE=TEMPERATURE\n'
    line += ' NODEALL, '+str(ambient)+'\n'

    ########################################################################
    ## Loading Step
    ########################################################################
    line += "******************************************\n"
    line += "**                                      **\n"
    line += "**     LOADING HISTORY DEFINITION       **\n"
    line += "**                                      **\n"
    line += "******************************************\n"
    line += "*RESTART, WRITE, FREQUENCY=100\n"
    line += "*STEP, INC=100\n"
    line += " STEP 1 : THERMAL ANALYSIS\n"
    line += "*HEAT TRANSFER, STEADY STATE\n"
    line += " 1.0, 1.0\n"
    line += "** HEAT LOSS FILE IMPORTING (*hloss)\n"
    line += "*DFLUX\n"
    line += "*INCLUDE, INPUT="+strSimCode+"-3DST-HGR-4.txt\n"
    line += "*SFILM\n"
    H_Tread = 9.0/8.0*Speed*OD /1000.0
    H_UpSW  = 9.0/8.0*Speed*OD /1000.0 
    H_DnSW  = 3.0/4.0*Speed*OD/1000.0 +10.0
    H_Inner = 6.0
    H_Rim   = 30.0
    line += " SURFACE_TREAD, F, 38., " + str(H_Tread) + "\n"
    line += " SURFACE_UPSIDE, F, 38, " + str(H_UpSW) + "\n"
    line += " SURFACE_DOWNSIDE, F, 38, " + str(H_DnSW) + "\n"
    line += " SURFACE_BEAD, F, 50, "  + str(H_Rim) + "\n"
    line += " SURFACE_INNER, F, 38, " + str(H_Inner) + "\n"
    line += "*RADIATION VIEWFACTOR, CAVITY=SURFACE_CAVITY\n SURFACE_CAVITY\n" 
    line += "** \n"
    line += "** ODB FILE(*.odb) OUTPUT REQUEST\n"
    line += "** \n"
    line += "*OUTPUT, FIELD, FREQUENCY=100\n"
    line += "*NODE OUTPUT\n"
    line += " NT, COORD\n"
    # line += "*ELEMENT OUTPUT, POSITION=CENTROIDAL\n"
    # line += " TEMP\n"
    line += "** \n"
    line += "** RESULT FILE(*.fil) OUTPUT REQUEST\n"
    line += "** \n"
    line += "*NODE FILE, FREQUENCY=100\n"
    line += " NT\n"
    line += "*EL FILE, POSITION=CENTROIDAL, FREQUENCY=100\n"
    line += " TEMP\n"
    line += "*END STEP\n"
        
    f=open(path + '/' + strSimCode + '-2DTH.inp',"w")   
    f.writelines(line)
    f.close()

def Mesh2DInformation(InpFileName):
    with open(InpFileName) as INP:
        lines = INP.readlines()

    Node = NODE()
    Element = ELEMENT()
    Elset = ELSET()
    Surface = SURFACE()
    Tie = TIE()
    Nset = ELSET()
    
    Comments = []
    iComment = 0
    

    for line in lines:
        word = list(line.split(','))
        if word[0] == '\n' or ( '**' in word[0]):
            pass
        else:
            if '*' in word[0]:
                # command = list(word[0].split('*'))
                # print (word)
                if '*Heading' in word[0]:
                    spt = 'HD'
                elif '*NODE'  in word[0]:
                    spt = 'ND'
                elif '*ELEMENT'  in word[0]:
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
                elif '*SURFACE'  in word[0]:
                    name = word[2].split('=')[1].strip()
                    # print (word)
                    if 'Tie_' in name: 
                        spt = "TI"
                        Tie.AddName(name)
                    else:
                        spt = 'SF'
                        Surface.AddName(name)
                #                    print ('Name=', name, 'was stored', Surface.Surface)
                elif '*TIE'  in word[0]:
                    name = word[1].split('=')[1].strip()
                    Tie.AddGroup(name)
                    spt = 'TG'

                elif '*ELSET'  in word[0]:
                    spt = 'ES'
                    name = word[1].split('=')[1].strip()
                    if name != "BETWEEN_BELTS" and name != "BD1" and name != "BetweenBelts":
                        Elset.AddName(name)

                elif '*NSET'  in word[0]:
                    name = word[1].split('=')[1].strip()
                    if name == 'BD_R' or name == 'BD_L': 
                        spt = 'NS'
                        Nset.AddName(name)

                else:
                    spt = ''
            else:
                if spt == 'HD':
                    pass
                if spt == 'ND':
                    Node.Add([int(word[0]), float(word[1]), float(word[2]), float(word[3])])
                if spt == 'M1':
                    # Element   [EL No,                  N1,          N2,  N3, N4,'elset Name', N,  Area/length, CenterX, CenterY]
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), '', '', '', 2])#, math.sqrt(math.pow(C1[1] - C2[1], 2) + math.pow(C1[2] - C2[2], 2)), (C1[1] + C2[1]) / 2.0, (C1[2] + C2[2]) / 2.0])
                if spt == 'C3':
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), int(word[3]), '', '', 3])#, A[0], A[1], A[2]])
                if spt == 'C4':
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), int(word[3]), int(word[4]), '', 4])#, A[0], A[1], A[2]])
                if spt == 'NS':
                    for i in range(len(word)):
                        if isNumber(word[i]) == True:    Nset.AddNumber(int(word[i]), name)
                if spt == 'ES':
                    if name != "BETWEEN_BELTS" and name != "BD1" and name != "BetweenBelts":
                        for i in range(len(word)):
                            if isNumber(word[i]) == True:      Elset.AddNumber(int(word[i]), name)
                if spt == 'SF':
                    Surface.AddElement(name, int(word[0].strip()), word[1].strip())
                if spt == 'TI':
                    Tie.AddElement(name, int(word[0].strip()), word[1].strip())
                if spt == 'TG':
                    Tie.AddGroupMember(name, word[0].strip(), word[1].strip())
                else:
                    pass

    for i in range(len(Elset.Elset)):
        TireRubberComponents, TireCordComponents = TIRE.GET_TIRE_COMPONENT()
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

    nodes = np.array(Node.Node)

    for k, el in enumerate(Element.Element):
        indx = np.where(nodes[:,0]==el[1])[0][0]
        N1 = [int(nodes[indx][0]), nodes[indx][1], nodes[indx][2], nodes[indx][3]]
        indx = np.where(nodes[:,0]==el[2])[0][0]
        N2 = [int(nodes[indx][0]), nodes[indx][1], nodes[indx][2], nodes[indx][3]]

        if el[6]==2: 
            temp =[Element.Element[k][0], N1, N2, "", "", el[5], 2]
        elif el[6] ==3: 
            indx = np.where(nodes[:,0]==el[3])[0][0]
            N3 = [int(nodes[indx][0]), nodes[indx][1], nodes[indx][2], nodes[indx][3]]
            temp =[Element.Element[k][0], N1, N2, N3, "", el[5], 3]
        else: 
            indx = np.where(nodes[:,0]==el[3])[0][0]
            N3 = [int(nodes[indx][0]), nodes[indx][1], nodes[indx][2], nodes[indx][3]]
            indx = np.where(nodes[:,0]==el[4])[0][0]
            N4 = [int(nodes[indx][0]), nodes[indx][1], nodes[indx][2], nodes[indx][3]]
            temp =[Element.Element[k][0], N1, N2, N3, N4, el[5], 4]

        Element.Element[k]=temp

    return Node, Element, Elset, Surface, Tie, Nset

def Facing_ElementsTo(elm, among): 
    
    eln = elm.Nodes()
    amn = among.Nodes()
    eln = np.array(eln, dtype='int32')
    amn = np.array(amn, dtype='int32')
    common = np.intersect1d(eln[:,0], amn[:,0])

    fel = ELEMENT()
    for el in among.Element: 
        cnt = 0 
        for n in common: 
            if n == el[1][0]: 
                cnt += 1
                break 
        for n in common: 
            if n == el[2][0]: 
                cnt += 1
                break 
        if el[3] != "": 
            for n in common: 
                if n ==el[3][0]: 
                    cnt += 1
                    break 
        if el[4] != "": 
            for n in common: 
                if n == el[4][0]: 
                    cnt += 1
                    break 
        if cnt == 2: 
            fel.Add(el) 
    return fel 

def Grouping_FILTD(els=[]): 

    i = 0 
    while i < len(els.Element): 
        nd0 = np.array([els.Element[i][1][0], els.Element[i][2][0], els.Element[i][3][0], els.Element[i][4][0]])
        mch = 0
        f = 0  
        for j, el in enumerate(els.Element):
            
            nd = np.array([el[1][0], el[2][0], el[3][0], el[4][0]])
            mch = np.intersect1d(nd, nd0)
            if len(mch) == 2: 
                # print (els.Element[i][0], el[0], mch)
                f = 1 
                break 
        if f == 0: 
            # print ("del", els.Element[i][0])
            del(els.Element[i])
            i -= 1
        i += 1 

    pos = []; 
    neg = []
    for i, e1 in enumerate(els.Element): 
        f = 0 
        cnt = 0
        nd0 = np.array([e1[1][0], e1[2][0], e1[3][0], e1[4][0]])
        for j, e2 in enumerate(els.Element): 
            if i == j: continue 
            nd = np.array([e2[1][0], e2[2][0], e2[3][0], e2[4][0]])
            mch = np.intersect1d(nd0, nd)
            if len(mch) == 2: 
                cnt += 1 
        if cnt == 1: 
            if e1[1][2] < 0: neg.append(e1)
            else:            pos.append(e1)


    min1 = 0 
    zmin = 10**10 
    for i, e1 in enumerate(pos): 
        if e1[1][1] < zmin: 
            zmin = e1[1][1]
            min1 = i 
    zmin = 10**10 
    for i, e1 in enumerate(pos): 
        if i == min1 : continue 
        if e1[1][1] < zmin:
            zmin = e1[1][1] 
            min2 = i 

    start_pos = []
    if pos[min1][1][2] < pos[min2][1][2]: 
        start_pos.append(pos[min1])
    else:
        start_pos.append(pos[min2])

    min1 = 0 
    zmin = 10**10 
    for i, e1 in enumerate(neg): 
        if e1[1][1] < zmin: 
            zmin = e1[1][1] 
            min1 = i 
    zmin = 10**10 
    for i, e1 in enumerate(neg): 
        if i == min1 : continue 
        if e1[1][1] < zmin: 
            zmin = e1[1][1] 
            min2 = i 

    start_neg = []
    if neg[min1][1][2] < neg[min2][1][2]: 
        start_neg.append(neg[min2])
    else:
        start_neg.append(neg[min1])


    next = start_pos[0]
    head = [next[0]]
    while len(next): 
        next, head = Next4Solid(next, els.Element, head=head)
    
    next = start_neg[0]
    head.append(next[0])
    while len(next): 
        next, head = Next4Solid(next, els.Element, head=head)
    # print (head)

    return head 

def Next4Solid(sol, Element, head=[]): 
    nd0 = np.array([sol[1][0], sol[2][0], sol[3][0], sol[4][0]])
    for e in Element: 
        nd = np.array([e[1][0], e[2][0], e[3][0], e[4][0]])
        mch = np.intersect1d(nd0, nd)
        if len(mch) ==2: 
            prev = 0 
            for hd in head: 
                if hd == e[0]: 
                    prev = 1 
                    break 
            if  prev == 0: 
                head.append(e[0]) 
                return e, head 
    end = []
    return end, head 

def OtherNodes_InSolid(solid, node_ids): 
    # solid   [ 0 = EL ID, 1=N1, 2=N2, 3=N3, 4=N4, 5=ESet Name, 6=No of nodes]
    lefts=[]
    nodes = node_ids 
    if len(node_ids) >= solid[6]: 
        return lefts
    mch = []
    for i, nd in enumerate(nodes): 
        if nd == solid[1]: mch.append([nd, 1])
        if nd == solid[2]: mch.append([nd, 2])
        if nd == solid[3]: mch.append([nd, 3])
        if nd == solid[4]: mch.append([nd, 4])
    tmp = []
    for i in range(1, 5): 
        f = 0 
        for d in mch: 
            if d[1] == i : 
                f = 1 
                break 
        if f == 0 : 
            tmp.append(i)
    
    for i in tmp: 
        lefts.append([solid[1+i], i])
    return lefts 

def Mesh2D_ElsetDefinition_Endurance(meshfile): 
    ##############################################
    ## duplication check 
    ##############################################
    with open(meshfile) as tmp: 
        lines = tmp.readlines()
    
    done = 0 
    for line in lines:   ## duplication check.. 
        if "ELSET, ELSET=C01TU" in line : 
            done = 1
    ##############################################
    
    if done ==0: 
        # print (meshfile)
        Node, Element, Elset, Surface, Tie, Nset = Mesh2DInformation(meshfile)
        with open(meshfile) as ms: 
            lines = ms.readlines()
        cmd = ''
        btbset = []
        for line in lines: 
            if "**"  in line: continue 
            if "*" in line: 
                if "BETWEEN_BELTS" in line: 
                    cmd = "btb"
                else: 
                    cmd = ''
            else: 
                if cmd == 'btb': 
                    words = line.split(",")
                    for w in words: 
                        if w.strip()!= "": btbset.append(int(w.strip()))
        
        npel = []
        for e in Element.Element:
            if e[3] =="": e[3] = [0]
            if e[4] =="": e[4] = [0]
            npel.append([e[0], e[1][0], e[2][0], e[3][0], e[4][0]])
        npel = np.array(npel)


        CCT = Element.Elset("CCT")
        FIL = Element.Elset("FIL")
        RIC = Element.Elset("RIC")
        C01 = Element.Elset("C01")
        C03 = Element.Elset("C03")

        f = open(meshfile, 'a')
        
        ##########################################
        ## CCT elements adjacent to RIC (RIC elements in old version)
        CCT2RIC = Facing_ElementsTo(RIC, CCT)
        RICTU = Grouping_FILTD(CCT2RIC)
        
        f.write("\n*ELSET, ELSET=RICTU\n")
        enter = 0
        for i, num in enumerate(RICTU): 
            if int((i+1)%10) == 0: 
                f.write("\n")
                enter=1
            f.write("%8d,"%(int(num)))
            enter = 0
        if enter ==0: f.write("\n")
        ##########################################
        ## C01 or C03 elements adjacent to RICTU 
        RCCT=ELEMENT()
        for e in CCT.Element: 
            for rt in RICTU: 
                if e[0] == rt: 
                    RCCT.Add(e)
                    break 


        if len(C03.Element) ==0: 
            C01TUE = Facing_ElementsTo(RCCT, C01)
        else:
            C01TUE = Facing_ElementsTo(RCCT, C03)

        C01TU=[]
        for el in C01TUE.Element: 
            C01TU.append(el[0])
        
        f.write("\n*ELSET, ELSET=C01TU\n")
        enter = 0
        for i, num in enumerate(C01TU): 
            if int((i+1)%10) == 0: 
                f.write("\n")
                enter=1
            f.write("%8d,"%(int(num)))
            enter = 0
        if enter ==0: f.write("\n")
        ##########################################

        sortedC01 = SortingMembrane("C01", Element)
        npn = np.array(Node.Node)

        nC01 =[]
        for i, ed in enumerate(sortedC01):
            if i == 0: 
                ix = np.where(npn[:,0]==ed[1][0])[0][0]
                nC01.append(npn[ix])
            ix = np.where(npn[:,0]==ed[2][0])[0][0]
            nC01.append(npn[ix])
            sortedC01[i].append(npn[ix])

        nC01 = np.array(nC01)
        mzC01 = np.max(nC01[:,1])
        # print("sorted c01", len(sortedC01))
        # print(sortedC01[0])
        # print(" Max C01 z", mzC01)


        cY = 0 
        start = 0
        zSW = 0 
        N = int(len(sortedC01)/2)
        for i in range(N-1, -1, -1):
            ed = sortedC01[i] 
            if ed[-1][1] == mzC01: start = 1
            # print(start, ":", ed[0],",",  ed[1][0], ",", ed[2][0], ", %.1f"%(ed[-1][2]*1000))
            if start ==1: 
                if cY <= abs(ed[-1][2]) : 
                    cY = abs(ed[-1][2])
                    zSW = ed[-1][1]
                    # print (">>> SW Z=", zSW, "SW Y=", cY )
                else:
                    break 

        # print ("SW Z=", zSW, "SW Y=", cY )


        BD = Element.Elset("BEAD_L")
        if len(BD.Element) ==0: 
            BD = Element.Elset("BEAD_R")
        nBD =[]
        for el in BD.Element:
            nBD.append(el[1][0])
            nBD.append(el[2][0])
            nBD.append(el[3][0])
        nBD=np.array(nBD)
        nBD=np.unique(nBD)

        maxBD_Z=0.0
        for n in nBD:
            ix = np.where(npn[:,0]==n)[0][0]
            if maxBD_Z < npn[ix][1]: 
                maxBD_Z = npn[ix][1]

        UCCT = []
        LCCT = []
        for el in CCT.Element:
            if el[4][0]> 0: 
                if el[1][1]>=zSW or el[2][1]>=zSW or el[3][1]>=zSW or el[4][1]>=zSW : 
                    UCCT.append(el[0])
                elif el[1][1] > maxBD_Z and el[2][1] > maxBD_Z and el[3][1] > maxBD_Z and el[4][1] > maxBD_Z :
                    LCCT.append(el[0])
            else:
                if el[1][1]>=zSW or el[2][1]>=zSW or el[3][1]>=zSW : 
                    UCCT.append(el[0])
                elif el[1][1] > maxBD_Z and el[2][1] > maxBD_Z and el[3][1] > maxBD_Z  :
                    LCCT.append(el[0])

        
        f.write("\n*ELSET, ELSET=UCCT\n")
        enter = 0
        for i, num in enumerate(UCCT): 
            if int((i+1)%10) == 0: 
                f.write("\n")
                enter=1
            f.write("%8d,"%(int(num)))
            enter = 0
        if enter ==0: f.write("\n")



        TuCCT =[]

        N = int(len(sortedC01)/2)
        bd_in =0; bd_out = 0 
        for i in range(N-1, -1, -1):
            if sortedC01[i][-1][1] <  maxBD_Z : 
                bd_in = 1 
            if bd_in == 1 and sortedC01[i][-1][1] >=  maxBD_Z: 
                bd_out = 1
            if bd_out ==1:
                
                for el in CCT.Element:
                    e1 = 0; e2=0 
                    if el[1][0] == sortedC01[i][1][0] or el[2][0] == sortedC01[i][1][0] or el[3][0] == sortedC01[i][1][0] or el[4][0] == sortedC01[i][1][0] : e1 = 1 
                    if el[1][0] == sortedC01[i][2][0] or el[2][0] == sortedC01[i][2][0] or el[3][0] == sortedC01[i][2][0] or el[4][0] == sortedC01[i][2][0] : e2 = 1 
                    # print (" %d, %d : %d, %d, %d, %d,   e1=%d, e2=%d"%(sortedC01[i][1][0], sortedC01[i][2][0], el[1][0], el[2][0], el[3][0], el[4][0], e1, e2))# , end="")

                    if e1 == 1 and e2 ==1: 
                        TuCCT.append(el[0]) 

        tN = len(sortedC01)
        bd_in =0; bd_out = 0 
        for i in range(N, tN):
            if sortedC01[i][-1][1] <  maxBD_Z : 
                bd_in = 1 
            if bd_in == 1 and sortedC01[i][-1][1] >=  maxBD_Z: 
                bd_out = 1
            if bd_out ==1:
                for el in CCT.Element:
                    e1 = 0; e2=0 
                    if el[1][0] == sortedC01[i][1][0] or el[2][0] == sortedC01[i][1][0] or el[3][0] == sortedC01[i][1][0] or el[4][0] == sortedC01[i][1][0] : e1 = 1 
                    if el[1][0] == sortedC01[i][2][0] or el[2][0] == sortedC01[i][2][0] or el[3][0] == sortedC01[i][2][0] or el[4][0] == sortedC01[i][2][0] : e2 = 1 
                    if e1 == 1 and e2 ==1: 
                        TuCCT.append(el[0])

        sortedC02 = SortingMembrane("C02", Element)
        
        if len(sortedC02) > 0: 
            for i, ed in enumerate(sortedC02):
                ix = np.where(npn[:,0]==ed[2][0])[0][0]
                sortedC02[i].append(npn[ix])

            N = int(len(sortedC02)/2)
            bd_in =0; bd_out = 0 
            for i in range(N-1, -1, -1):
                
                if sortedC02[i][-1][1] <  maxBD_Z : 
                    bd_in = 1 
                if bd_in == 1 and sortedC02[i][-1][1] >=  maxBD_Z: 
                    bd_out = 1
                if bd_out ==1:
                    for el in CCT.Element:
                        e1 = 0; e2=0 
                        if el[1][0] == sortedC02[i][1][0] or el[2][0] == sortedC02[i][1][0] or el[3][0] == sortedC02[i][1][0] or el[4][0] == sortedC02[i][1][0] : e1 = 1 
                        if el[1][0] == sortedC02[i][2][0] or el[2][0] == sortedC02[i][2][0] or el[3][0] == sortedC02[i][2][0] or el[4][0] == sortedC02[i][2][0] : e2 = 1 

                        if e1 == 1 and e2 ==1: 
                            TuCCT.append(el[0]) 

            tN = len(sortedC02)
            bd_in =0; bd_out = 0 
            for i in range(N, tN):
                if sortedC02[i][-1][1] <  maxBD_Z : 
                    bd_in = 1 
                if bd_in == 1 and sortedC02[i][-1][1] >=  maxBD_Z: 
                    bd_out = 1
                if bd_out ==1:
                    for el in CCT.Element:
                        e1 = 0; e2=0 
                        if el[1][0] == sortedC02[i][1][0] or el[2][0] == sortedC02[i][1][0] or el[3][0] == sortedC02[i][1][0] or el[4][0] == sortedC02[i][1][0] : e1 = 1 
                        if el[1][0] == sortedC02[i][2][0] or el[2][0] == sortedC02[i][2][0] or el[3][0] == sortedC02[i][2][0] or el[4][0] == sortedC02[i][2][0] : e2 = 1 

                        if e1 == 1 and e2 ==1: 
                            TuCCT.append(el[0])

        sortedC03 = SortingMembrane("C03", Element)
        if len(sortedC03) > 0: 
            for i, ed in enumerate(sortedC03):
                ix = np.where(npn[:,0]==ed[2][0])[0][0]
                sortedC03[i].append(npn[ix])

            N = int(len(sortedC03)/2)
            bd_in =0; bd_out = 0 
            for i in range(N-1, -1, -1):
                if sortedC03[i][-1][1] <  maxBD_Z : 
                    bd_in = 1 
                if bd_in == 1 and sortedC03[i][-1][1] >=  maxBD_Z: 
                    bd_out = 1
                if bd_out ==1:
                    for el in CCT.Element:
                        e1 = 0; e2=0 
                        if el[1][0] == sortedC03[i][1][0] or el[2][0] == sortedC03[i][1][0] or el[3][0] == sortedC03[i][1][0] or el[4][0] == sortedC03[i][1][0] : e1 = 1 
                        if el[1][0] == sortedC03[i][2][0] or el[2][0] == sortedC03[i][2][0] or el[3][0] == sortedC03[i][2][0] or el[4][0] == sortedC03[i][2][0] : e2 = 1 

                        if e1 == 1 and e2 ==1: 
                            TuCCT.append(el[0]) 

            tN = len(sortedC03)
            bd_in =0; bd_out = 0 
            for i in range(N, tN):
                if sortedC03[i][-1][1] <  maxBD_Z : 
                    bd_in = 1 
                if bd_in == 1 and sortedC03[i][-1][1] >=  maxBD_Z: 
                    bd_out = 1
                if bd_out ==1:
                    for el in CCT.Element:
                        e1 = 0; e2=0 
                        if el[1][0] == sortedC03[i][1][0] or el[2][0] == sortedC03[i][1][0] or el[3][0] == sortedC03[i][1][0] or el[4][0] == sortedC03[i][1][0] : e1 = 1 
                        if el[1][0] == sortedC03[i][2][0] or el[2][0] == sortedC03[i][2][0] or el[3][0] == sortedC03[i][2][0] or el[4][0] == sortedC03[i][2][0] : e2 = 1 

                        if e1 == 1 and e2 ==1: 
                            TuCCT.append(el[0])

        TuCCT = np.array(TuCCT)
        TuCCT = np.unique(TuCCT)

        f.write("*ELSET, ELSET=TUCCT\n")
        enter = 0
        for i, num in enumerate(TuCCT): 
            if int((i+1)%10) == 0: 
                f.write("\n")
                enter=1
            f.write("%8d,"%(int(num)))
            enter = 0
        if enter ==0: f.write("\n")

        ## CuCCT ending ##########################################


        i = 0 
        while i < len(LCCT):
            ix = np.where(TuCCT[:] == LCCT[i])[0]
            if len(ix) ==1:
                del(LCCT[i])
                continue 
            i += 1 
        

        f.write("*ELSET, ELSET=LCCT\n")

        enter = 0
        for i, num in enumerate(LCCT): 
            if int((i+1)%10) == 0: 
                f.write("\n")
                enter=1
            f.write("%8d,"%(int(num)))
            enter = 0
        if enter ==0: f.write("\n")

        ## LCCT ending ############################################


        JBT  = Element.Elset("JBT")
        if len(JBT.Element) ==0: 
            isBT3 = 0
            isBT4 = 0 
            elbt1 =[]
            elbt2 = []
            elbt3=[]
            elbt4=[]
            for el in Element.Element:
                if el[5] == "BT1": elbt1.append(el)
                if el[5] == "BT2": elbt2.append(el)
                if el[5] == "BT3": elbt3.append(el)
                if el[5] == "BT4": elbt4.append(el)


            JBT = ELEMENT()
            if len(elbt3) ==0: 

                JBTUP = []
                for et in elbt1: 
                    for el in Element.Element: 
                        if et[0] != el[0]: 
                            if et[1][0] == el[1][0] and et[2][0] == el[2][0] :  
                                JBTUP.append(el)
                                break 
                for et in elbt2: 
                    for el in Element.Element: 
                        if et[0] != el[0] : 
                            if et[1][0] == el[1][0] and et[2][0] == el[2][0] :  
                                JBTUP.append(el)
                                break 

                i =0
                while i < len(JBTUP): 
                    fd = 0 
                    for btb in btbset: 
                        if btb == JBTUP[i][0]: 
                            fd = 1
                            break 
                    if fd == 1: 
                        del(JBTUP[i])
                        i -= 1
                    else: 
                        JBT.Add(JBTUP[i])
                    i += 1

            else: 
                JBTUP = []
                for et in elbt2: 
                    for el in Element.Element: 
                        if et[1][0] == el[1][0] and et[2][0] == el[2][0] : 
                            JBTUP.append(el)
                            break 
                
                for et in elbt3:  
                    for el in Element.Element: 
                        if et[1][0] == el[1][0] and et[2][0] == el[2][0] :  
                            JBTUP.append(el)
                            break 
                for et in elbt4:  
                    for el in Element.Element: 
                        if et[1][0] == el[1][0] and et[2][0] == el[2][0] : 
                            JBTUP.append(el)
                            break 

                i =0
                while i < len(JBTUP): 
                    f = 0 
                    for btb in btbset: 
                        if btb == JBTUP[i][0]: 
                            f = 1
                            break 
                    if f == 1: 
                        del(JBTUP[i])
                        i -= 1
                    else: 
                        JBT.Add(JBTUP[i])
                    i += 1


        JBT_range = 30.0E-03 
        max_y = 0 

        for el in JBT.Element: 
            if max_y < abs(el[1][2]) :  max_y = abs(el[1][2]) 
            if max_y < abs(el[2][2]) :  max_y = abs(el[2][2]) 

        JBT_minY = max_y - JBT_range

        JBTUP = []
        for el in JBT.Element: 
            if JBT_minY <= abs(el[1][2]) or JBT_minY <= abs(el[2][2]) : 
                JBTUP.append(el[0])

        f.write("*ELSET, ELSET=SHOTOPPING\n")
        enter = 0
        for i, num in enumerate(JBTUP): 
            if int((i+1)%10) == 0: 
                f.write("\n")
                enter=1
            f.write("%8d,"%(int(num)))
            enter = 0
        if enter ==0: f.write("\n")

        f.close()
    else: 
        print ("Elsets for Endurance are already exist.")

def Mesh2DModification(meshfile):
    
    Node, Element, Elset, Surface, Tie, Nset = Mesh2DInformation(meshfile)
    npel = []
    for i, el in enumerate(Element.Element): 
        # if i < 100: print(el)
        if el[3] =="": el[3] = [0] 
        if el[4] =="": el[4] = [0]
        npel.append([el[0], el[1][0], el[2][0], el[3][0], el[4][0]])
    npel = np.array(npel)

    sortedcc = SortingMembrane("C01", Element)
    beadcore_R = ExtractingElementsbySet("BEAD_R", Element)
    nodesbdr = ExtractingNodesfromElement(beadcore_R)
    beadcore_L = ExtractingElementsbySet("BEAD_L", Element)
    nodesbdl = ExtractingNodesfromElement(beadcore_L)
    nodesbd = np.union1d(nodesbdr, nodesbdl)

    nodes = np.array(Node.Node)
    hts =[]
    for nd in nodesbd: 
        indx = np.where(nodes[:,0]==float(nd))[0][0]
        hts.append(nodes[indx][1])
    maxht = max(hts)


    cc1pos =[]
    cc1neg =[]
    cc1reg = []

    cnt = 1
    counting =0 
    for cc in sortedcc: 
        if cc[2][1] <= maxht and cnt ==1 :    cnt = 0
        if cnt ==1:              cc1pos.append(cc)
        else: 
            counting += 1
            if counting > 5 and cc[2][2]>0.0: 
                cc1reg.append(cc)
        
    cnt = 1
    counting =0 
    N = len(sortedcc)
    for i in range(N-1, 0, -1):
        if sortedcc[i][1][1] <= maxht and cnt ==1:   cnt = 0
        if cnt == 1:                     cc1neg.append(sortedcc[i]) 
        else: 
            counting += 1
            if counting > 5 and sortedcc[i][1][2]<=0.0: 
                cc1reg.append(sortedcc[i])
        
    cc2reg = []
    sortedcc2 = SortingMembrane("C02", Element)
    cnt = 1
    counting =0 
    for cc in sortedcc2: 
        if cc[2][1] <= maxht and cnt==1:    cnt = 0
        if cnt ==0:             
            counting += 1
            if counting > 5 and cc[2][2]>0.0: 
                cc2reg.append(cc)
        
    cnt = 1
    counting =0 
    N = len(sortedcc2)
    for i in range(N-1, 0, -1):
        if sortedcc2[i][1][1] <= maxht and cnt==1:   cnt = 0
        if cnt == 0:             
            counting += 1
            if counting > 5 and sortedcc2[i][1][2]<=0.0: 
                cc2reg.append(sortedcc2[i])

    # print ("CC1 : No pos=%d, neg=%d, rest=%d"%(len(cc1pos), len(cc1neg), len(cc1reg)))
    # print ("CC2 : No                 rest=%d"%( len(cc2reg)))

    FIL = ExtractingElementsbySet("FIL", Element)
    RIC = ExtractingElementsbySet("RIC", Element)

    dist = 0.5E-03 # unit : m 

    ## 

    newnodes=[]
    newelement =[]
    neweltiecheck=[]
    el_number = 3990
    nd_number = 3990
    filnew=[]
    ricnew=[]
    
    for el in FIL: 
        face = FaceContactingToMembrane(el, cc1reg)
        if face ==0: 
            face = FaceContactingToMembrane(el, cc2reg)
        # print ("FIL EL type=%d, face=%d"%(el[6], face))
        if face !=0: 
            el_number -= 1 
            nd_number -= 2 
            gnode, orign, newel = GenerateNodeson4NodeElement(dist, face, el, elid=el_number, ndid=nd_number)
            newnodes.append(gnode[0])
            newnodes.append(gnode[1])

            newelement.append(newel)
            filnew.append(newel[0])
            neweltiecheck.append([orign[0], newel[0]])

            for k, etl in enumerate(Element.Element): 
                if etl[0] == orign[0]: 
                    Element.Element[k][1] = orign[1]
                    Element.Element[k][2] = orign[2]
                    Element.Element[k][3] = orign[3]
                    Element.Element[k][4] = orign[4]

                    break
    # print ("New nodes generated ", len(newnodes))
    newnodes_ric =[]
    
    for el in RIC: 
        face = FaceContactingToMembrane(el, cc1pos)
        if face ==0: 
            face = FaceContactingToMembrane(el, cc1neg)
        # print ("element type=%d, face=%d"%(el[6], face))
        if face !=0: 
            el_number -= 1 
            nd_number -= 2 
            gnode, orign, newel = GenerateNodeson4NodeElement(dist, face, el, elid=el_number, ndid=nd_number)
            newnodes_ric.append(gnode[0])
            newnodes_ric.append(gnode[1])

            newelement.append(newel)
            ricnew.append(newel[0])
            # print("%d, %d, %d, %d, %d"%(newel[0], newel[1][0], newel[2][0], newel[3][0], newel[4][0]))
            N=len(newelement)
            # print("  >> %d, %d, %d, %d, %d"%(newelement[N-1][0], newelement[N-1][1][0], newelement[N-1][2][0], newelement[N-1][3][0], newelement[N-1][4][0]))
            neweltiecheck.append([orign[0], newel[0]])

            for k, etl in enumerate(Element.Element): 
                if etl[0] == orign[0]: 
                    # print (etl[0], ", ", orign[0], newel[0])
                    Element.Element[k][1] = orign[1]
                    Element.Element[k][2] = orign[2]
                    Element.Element[k][3] = orign[3]
                    Element.Element[k][4] = orign[4]
                    break
                
            # print("  >>> %d, %d, %d, %d, %d"%(newelement[N-1][0], newelement[N-1][1][0], newelement[N-1][2][0], newelement[N-1][3][0], newelement[N-1][4][0]))

    # for el in newelement: 
    #     print("** %d, %d, %d, %d, %d"%(el[0], el[1][0], el[2][0], el[3][0], el[4][0]))


    
    nodetochange=[]
    i = 0
    while i < len(newnodes): 
        j = i + 1
        while j < len(newnodes): 
            if newnodes[i][0][1] == newnodes[j][0][1] and newnodes[i][0][2] == newnodes[j][0][2]: 
                nodetochange.append([newnodes[j][0], newnodes[i][0]])
                del(newnodes[j])
                j -=1
                break 
            j+=1
        i += 1
    i=0
    while i < len(newnodes_ric): 
        j = i + 1
        while j < len(newnodes_ric): 
            if newnodes_ric[i][0][1] == newnodes_ric[j][0][1] and newnodes_ric[i][0][2] == newnodes_ric[j][0][2]:
                nodetochange.append([newnodes_ric[j][0], newnodes_ric[i][0]])
                del(newnodes_ric[j])
                j -= 1
                break 
            j+=1
        i += 1

    print ("* New nodes generated on Filler = %d, On RIC=%d"%(len(newnodes), len(newnodes_ric)))
    print ("* New elements generated =%d"%(len(newelement)))

    for nd in nodetochange: 
        for i, el in enumerate(Element.Element):
            for j in range(1, el[6]+1) :
                if nd[0][0] == el[j][0]: 
                    Element.Element[i][j][0]=nd[1][0]

    for nd in nodetochange: 
        for i, el in enumerate(newelement):
            # print ("%d: %d, %d, %d, %d"%(newelement[i][0], newelement[i][1][0], newelement[i][2][0], newelement[i][3][0], newelement[i][4][0]))
            for j in range(1, el[6]+1) :
                if nd[0][0] == el[j][0]: 
                    newelement[i][j][0]=nd[1][0]
            # print (" >> %d: %d, %d, %d, %d"%(newelement[i][0], newelement[i][1][0], newelement[i][2][0], newelement[i][3][0], newelement[i][4][0]))
                    

    with open(meshfile) as mesh:
        lines = mesh.readlines()

    cmd = ''
    btbset = []
    for line in lines: 
        if "**"  in line: continue 
        if "*" in line: 
            if "BETWEEN_BELTS" in line: 
                cmd = "btb"
            else: 
                cmd = ''
        else: 
            if cmd == 'btb': 
                words = line.split(",")
                for w in words: 
                    if w.strip() != "": btbset.append(int(w.strip()))
            
    
    newfile = meshfile[:-4]+"-backup.msh"
    f = open(newfile, 'w')
    f.writelines(lines)
    f.close()
    
    newfile = meshfile[:-4]+".msh"
    f = open(newfile, 'w')

    f.write("\n*NODE, SYSTEM=R, NSET=ALLNODES\n")
    
    for nd in Node.Node: 
        f.write("%8d, %.7E, %.7E, %.7E\n"%(nd[0], nd[1], nd[2], nd[3]))
    # f.write("***************************************************\n")
    for nd in newnodes: 
        f.write("%8d, %.7E, %.7E, %.7E\n"%(nd[0][0], float(nd[0][1]), float(nd[0][2]), float(nd[0][3])))
    # f.write("***************************************************\n")
    for nd in newnodes_ric: 
        f.write("%8d, %.7E, %.7E, %.7E\n"%(nd[0][0], nd[0][1], nd[0][2], nd[0][3]))

    f.write("*ELEMENT, TYPE=MGAX1, ELSET=ALLELSET\n")
    for el in Element.Element: 
        if el[6]==2:
            f.write("%8d, %8d, %8d\n"%(el[0], el[1][0], el[2][0]))

    f.write("*ELEMENT, TYPE=CGAX3H, ELSET=ALLELSET\n")
    for el in Element.Element: 
        if el[6]==3:
            f.write("%8d, %8d, %8d, %8d\n"%(el[0], el[1][0], el[2][0], el[3][0]))

    f.write("*ELEMENT, TYPE=CGAX4H, ELSET=ALLELSET\n")
    
    for el in Element.Element: 
        if el[6]==4:
            f.write("%8d, %8d, %8d, %8d, %8d\n"%(el[0], el[1][0], el[2][0], el[3][0], el[4][0]))
    # f.write("***************************************************\n")
    for el in newelement: 
        f.write("%8d, %8d, %8d, %8d, %8d\n"%(el[0], el[1][0], el[2][0], el[3][0], el[4][0]))
        # print ("*%8d, %8d, %8d, %8d, %8d\n"%(el[0], el[1][0], el[2][0], el[3][0], el[4][0]))

    for el in Elset.Elset: 
        # if "BETWEEN_BELTS" in el[0]: continue 
        f.write("*ELSET, ELSET=%s\n"%(el[0]))
        
        enter = 0
        for i in range(1, len(el)): 
            if int(i%10) == 0: 
                f.write("\n")
                enter=1
        
            f.write("%8d,"%(int(el[i])))
            enter = 0
        if ('CH1' in el[0] or 'CH2' in el[0]) and len(el) ==1: 
            f.write("  %s_L, %s_R\n"%(el[0], el[0])) 
            enter = 1
        if enter !=1: f.write("\n")
        
        if len(ricnew)> 0 and el[0] == "RIC": 
            enter = 0
            for i, ei in enumerate(ricnew): 
                if int((i+1)%10) == 0: 
                    f.write("\n")
                    enter=1
            
                f.write("%8d,"%(ei))
                enter = 0
            if enter !=1: f.write("\n")

        if len(filnew)> 0 and el[0] == "FIL": 
            enter = 0
            for i, ei in enumerate(filnew): 
                if int((i+1)%10) == 0: 
                    f.write("\n")
                    enter=1
            
                f.write("%8d,"%(ei))
                enter = 0
            if enter !=1: f.write("\n")


    if len(cc1pos) :
        f.write("*ELSET, ELSET=C01TU\n")
        enter = 0
        for i, num in enumerate(cc1pos): 
            if int((i+1)%10) == 0: 
                f.write("\n")
                enter=1
            f.write("%8d,"%(int(num[0])))
            enter = 0
        if enter ==0: f.write("\n")
        enter = 0
        for i, num in enumerate(cc1neg): 
            if int((i+1)%10) == 0: 
                f.write("\n")
                enter=1
            f.write("%8d,"%(int(num[0])))
            enter = 0
        if enter ==0: f.write("\n")

    if len(newelement) > 0: 
        f.write("*ELSET, ELSET=RICTU\n")
        i = 0
        enter = 0
        for num in newelement: 
            
            if num[5]=="RIC": 
                if int((i+1)%10) == 0: 
                    f.write("\n")
                    enter=1
                f.write("%8d,"%(int(num[0])))
                enter = 0
                i+=1
        if enter ==0: f.write("\n")      
        f.write("*ELSET, ELSET=FILTD\n")
        i = 0
        enter = 0
        for num in newelement: 
            
            if num[5]=="FIL": 
                if int((i+1)%10) == 0: 
                    f.write("\n")
                    enter=1
                f.write("%8d,"%(int(num[0])))
                enter = 0
                i+= 1
        if enter ==0: f.write("\n") 
    else: 
        line = "*ELSET, ELSET=TUCCT\n"
        # f.write("*ELSET, ELSET=TUCCT\n")
        cnt = 0
        enter = 0
        for i, num in enumerate(cc1pos):
            # print (num) 
            if int((i+1)%5) == 0: 
                # f.write("\n")
                line += "\n"
                enter=1
            ix = np.where(npel[:,0]==num[0])[0][0]
            el = npel[ix]
            # print (el)
            ix1 = np.where(npel[:,1:5]==el[1])[0]
            ix2 = np.where(npel[:,1:5]==el[2])[0]
            ix0 = np.intersect1d(ix1, ix2)
            if len(ix0) == 3: 
                for xt in ix0 : 
                    if xt != ix: 
                        en = npel[xt][0]
                        # f.write("%8d,"%(int(en)))
                        line += "%8d,"%(int(en))
                        cnt += 1
            # else: 
            #     print (len(ix0))

            enter = 0
        if enter ==0: 
            # f.write("\n")
            line += "\n"
        enter = 0
        for i, num in enumerate(cc1neg): 
            if int((i+1)%5) == 0: 
                # f.write("\n")
                line += "\n"
                enter=1
            ix = np.where(npel[:,0]==num[0])[0][0]
            el = npel[ix]
            ix1 = np.where(npel[:,1:5]==el[1])[0]
            ix2 = np.where(npel[:,1:5]==el[2])[0]
            ix0 = np.intersect1d(ix1, ix2)
            if len(ix0) == 3: 
                for xt in ix0 : 
                    if xt != ix: 
                        en = npel[xt][0]
                        # f.write("%8d,"%(int(en)))
                        line += "%8d,"%(int(en))
                        cnt += 1
            enter = 0
        if enter ==0: 
            # f.write("\n") 
            line += "\n"
        if cnt > 0: 
            f.write(line)

    ## endurance element elsets 

    materialnames = Element.ElsetNames()
    RINF = ELEMENT()
    for name in materialnames: 
        if "JEC" in name or "JFC" in name: 
            JC = Element.Elset(name)
            RINF = RINF.Combine(JC)
            # print ("SEARCHING .. ", name, ">> ", len(JC.Element), "TOTAL", len(RINF.Element))

    
    if len(RINF.Element) ==0 : 
        # print (" JB TOPPING No=", len(RINF.Element))
        isBT3 = 0
        isBT4 = 0 
        elbt1 =[]
        elbt2 = []
        elbt3=[]
        elbt4=[]
        for el in Element.Element:
            if el[5] == "BT1": elbt1.append(el)
            if el[5] == "BT2": elbt2.append(el)
            if el[5] == "BT3": elbt3.append(el)
            if el[5] == "BT4": elbt4.append(el)

        JBT = ELEMENT()
        if len(elbt3) ==0: 
            JBTUP = []
            for et in elbt1: 
                for el in Element.Element: 
                    if el[0] != et[0]: 
                        if et[1][0] == el[1][0] and et[2][0] == el[2][0] : 
                            JBTUP.append(el)
                            break 
            for et in elbt2: 
                for el in Element.Element: 
                    if el[0] != et[0]: 
                        if et[1][0] == el[1][0] and et[2][0] == el[2][0] : 
                            JBTUP.append(el)
                            break 

            i =0
            while i < len(JBTUP): 
                fd = 0 
                for btb in btbset: 
                    if btb == JBTUP[i][0]: 
                        fd = 1
                        break 
                if fd == 1: 
                    del(JBTUP[i])
                    i -= 1
                else: 
                    JBT.Add(JBTUP[i])
                i += 1

        else: 
            # print (" JB TOPPING No=", len(RINF.Element))
            JBTUP = []
            for et in elbt2: 
                for el in Element.Element: 
                    if et[1][0] == el[1][0] and et[2][0] == el[2][0] : 
                        JBTUP.append(el)
                        break 
            
            for et in elbt3:  
                for el in Element.Element: 
                    if et[1][0] == el[1][0] and et[2][0] == el[2][0] :   
                        JBTUP.append(el)
                        break 
            for et in elbt4:  
                for el in Element.Element: 
                    if et[1][0] == el[1][0] and et[2][0] == el[2][0] : 
                        JBTUP.append(el)
                        break 

            i =0
            while i < len(JBTUP): 
                fd = 0 
                for btb in btbset: 
                    if btb == JBTUP[i][0]: 
                        fd = 1
                        break 
                if fd == 1: 
                    del(JBTUP[i])
                    i -= 1
                else: 
                    JBT.Add(JBTUP[i])
                i += 1

    else: 
        JBT = ELEMENT()
        for el in RINF.Element: 
            # print (el)
            for et in Element.Element: 
                if el[0] != et[0]: 
                    if (el[1][0] == et[1][0] and el[2][0] == et[2][0]) or (el[1][0] == et[4][0] and el[2][0] == et[3][0]): 
                        JBT.Add(et)

    JBT_range = 30.0E-03 
    max_y = 0 

    for el in JBT.Element: 
        # print (el[1])
        if max_y < abs(el[1][2]) :  max_y = abs(el[1][2]) 
        if max_y < abs(el[2][2]) :  max_y = abs(el[2][2]) 

    JBT_minY = max_y - JBT_range

    JBTUP = []
    for el in JBT.Element: 
        if JBT_minY <= abs(el[1][2]) or JBT_minY <= abs(el[2][2]) : 
            JBTUP.append(el[0])


    f.write("*ELSET, ELSET=BETWEEN_BELTS\n")
    enter = 0
    for i, num in enumerate(btbset): 
        if int((i+1)%10) == 0: 
            f.write("\n")
            enter=1
        f.write("%8d,"%(int(num)))
        enter = 0
    if enter ==0: f.write("\n")

    f.write("*ELSET, ELSET=SHOTOPPING\n")
    enter = 0
    for i, num in enumerate(JBTUP): 
        if int((i+1)%10) == 0: 
            f.write("\n")
            enter=1
        f.write("%8d,"%(int(num)))
        enter = 0
    if enter ==0: f.write("\n")

    for surf in Surface.Surface: 
        f.write("*SURFACE, TYPE=ELEMENT, NAME=%s\n"%(surf[0]))
        N = len(surf)
        for i in range(1, N): 
            f.write("%8d, %s\n"%(surf[i][0], surf[i][1]))

    for tie in Tie.Tie: 
        f.write("*SURFACE, TYPE=ELEMENT, NAME=%s\n"%(tie[0]))
        N = len(tie)
        for i in range(1, N): 
            f.write("%8d, %s\n"%(tie[i][0], tie[i][1]))
            for j, ne in enumerate(neweltiecheck): 
                if tie[i][0] == ne[0]: 
                    f.write("%8d, %s\n"%(ne[1], tie[i][1]))
                    del(neweltiecheck[j])
                    break 

    for grp in Tie.Group: 
        f.write("*TIE, NAME=%s\n"%(grp[0]))
        f.write(" %s, %s\n"%(grp[1], grp[2]))
        
        
    if len(neweltiecheck)>0: 
        
        for el in newelement: 
            Element.Add(el)

        CCT = ExtractingElementsbySet("CCT", Element)
        BeadR = ExtractingElementsbySet("BEAD_R", Element)
        BeadL = ExtractingElementsbySet("BEAD_L", Element)
        RIC   = ExtractingElementsbySet("RIC", Element)
        BSW   = ExtractingElementsbySet("BSW", Element)

        for m, chk in enumerate(neweltiecheck): 
            ties = Tie_slavemaster(chk[0], chk[1], CCT, Element)
            if ties[3] > 0: 
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_s%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(chk[0], ties[0]))
                f.write(" %d, S%d\n"%(chk[1], ties[1]))
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_m%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(ties[2], ties[3]))
                f.write("*TIE, NAME=TIE_%d\n"%(1000+m))
                f.write(" Tie_s%d, Tie_m%d\n"%(1000+m, 1000+m))
            
            ties = Tie_slavemaster(chk[0], chk[1], BeadR, Element)
            if ties[3] > 0: 
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_s%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(chk[0], ties[0]))
                f.write(" %d, S%d\n"%(chk[1], ties[1]))
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_m%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(ties[2], ties[3]))
                f.write("*TIE, NAME=TIE_%d\n"%(1000+m))
                f.write(" Tie_s%d, Tie_m%d\n"%(1000+m, 1000+m))
            
            ties = Tie_slavemaster(chk[0], chk[1], BeadL, Element)
            if ties[3] > 0: 
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_s%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(chk[0], ties[0]))
                f.write(" %d, S%d\n"%(chk[1], ties[1]))
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_m%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(ties[2], ties[3]))
                f.write("*TIE, NAME=TIE_%d\n"%(1000+m))
                f.write(" Tie_s%d, Tie_m%d\n"%(1000+m, 1000+m))

            ties = Tie_slavemaster(chk[0], chk[1], RIC, Element)
            if ties[3] > 0: 
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_s%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(chk[0], ties[0]))
                f.write(" %d, S%d\n"%(chk[1], ties[1]))
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_m%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(ties[2], ties[3]))
                f.write("*TIE, NAME=TIE_%d\n"%(1000+m))
                f.write(" Tie_s%d, Tie_m%d\n"%(1000+m, 1000+m))

            ties = Tie_slavemaster(chk[0], chk[1], BSW, Element)
            if ties[3] > 0: 
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_s%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(chk[0], ties[0]))
                f.write(" %d, S%d\n"%(chk[1], ties[1]))
                f.write("*SURFACE, TYPE=ELEMENT, NAME=Tie_m%d\n"%(1000+m))
                f.write(" %d, S%d\n"%(ties[2], ties[3]))
                f.write("*TIE, NAME=TIE_%d\n"%(1000+m))
                f.write(" Tie_s%d, Tie_m%d\n"%(1000+m, 1000+m))
        

    f.write("*ELSET, ELSET=BD1\n BEAD_R")
    bdl = 0 
    for sets in Elset.Elset: 
        if sets[0] == "BEAD_L": 
            f.write(", BEAD_L")
            bdl = 1
            break 
    f.write("\n")

    for el in Nset.Elset: 
        f.write("*NSET, NSET=%s\n"%(el[0]))
        enter = 0
        for i in range(1, len(el)): 
            if int(i%10) == 0: 
                f.write("\n")
                enter=1
            else: 
                enter = 0
                f.write("%8d,"%(int(el[i])))
        if enter ==0: f.write("\n")


    f.close()
def Tie_slavemaster(el1, el2, masterel, Element) : 
    
    indx1=[]
    indx2=[]
    nd1=[]
    nd2=[]
    ele1 = []
    for e in Element.Element: 
        if e[0] == el1: 
            ele1 = e
            break
    ele2=[]
    for e in Element.Element: 
        if e[0] == el2: 
            ele2 = e
            break


    for i in range(1, ele1[6]+1): 
        nd1.append(ele1[i][0]) 
    for i in range(1, ele2[6]+1): 
        nd2.append(ele2[i][0]) 

    nd1=np.array(nd1)
    nd2=np.array(nd2)
    intnd = np.intersect1d(nd1, nd2)
    nd1 = np.setdiff1d(nd1, nd2)
    nd2 = np.setdiff1d(nd2, nd1)

    masterelid =0
    masterface = 0 
    master = []
    for el in masterel: 
        m1 = 0 
        md1 = 0
        for i in range(1, el[6]+1): 
            if el[i][0] == nd1[0] or el[i][0] == nd1[1]: 
                m1 += 1 
                md1 = i

        m2 = 0
        md2 = 0
        for i in range(1, el[6]+1): 
            if el[i][0] == nd2[0] or el[i][0] == nd2[1]: 
                m2 += 1 
                md2 = i 
        
        if m1 == 1 and m2 ==1:
            masterelid=el[0]
            master = [el[0], el[1], el[2], el[3], el[4], el[5], el[6]] 
            if (md1 ==1 and md2 ==2) or (md1 ==2 and md2 ==1) :  masterface = 1
            if (md1 ==2 and md2 ==3) or (md1 ==3 and md2 ==2) :  masterface = 2
            if (md1 ==3 and md2 ==4) or (md1 ==4 and md2 ==3) :  masterface = 3
            if (md1 ==4 and md2 ==1) or (md1 ==1 and md2 ==4) :  masterface = 4

            break 

    if masterface == 0: return [0, 0, 0, 0]
       
    
    ch1=0
    for i in range(1, ele1[6]+1): 
        if ele1[i][0] == master[md1][0]: 
            ch1 = i 
            break

    ch = 0
    for i in range(1, ele1[6]+1): 
        if ele1[i][0] != intnd[0] and  ele1[i][0] != intnd[1] and ele1[i][0] != master[md1][0] : 
            ch=i
            break
    
    if ch == ch1 + 1: face1 = ch -2
    elif ch == ch1 -1: face1 = ch1 
    
    if face1 ==0: face1 = 4
    if face1 == -1: face1 = 3
    
    ch2=0
    for i in range(1, ele2[6]+1): 
        if ele2[i][0] == master[md2][0]: 
            ch2 = i 
            break

    ch = 0
    for i in range(1, ele2[6]+1): 
        if ele2[i][0] != intnd[0] and  ele2[i][0] != intnd[1] and ele2[i][0] != master[md2][0] : 
            ch=i
            break
    
    if ch == ch2 + 1: face2 = ch -2
    elif ch == ch2 -1: face2 = ch2 
    if face2 ==0: face2 = 4
    if face2 == -1: face2 = 3 
            

    # if masterface ==0: print (face1, face2, masterelid, masterface)
    return [face1, face2, masterelid, masterface]


def GenerateNodeson4NodeElement(dist, face, el,  elid=0, ndid=0):
    of = face 
    n1 = el[face]
    face += 1
    if face > 4: face -= 4 
    of1 = face
    n2 = el[face]

    face = of -1 
    if face ==0: face = 4 
    oft = face
    n1t = el[face]
    face = of + 2
    if face > 4: face -= 4
    of1t = face  
    n2t = el[face]

    d1 = NodeDistance (n1, n1t)
    if d1 > dist * 1.5:         v1 = [ndid, round(n1[1] + dist * (n1t[1]-n1[1])/d1, 5), round(n1[2] + dist * (n1t[2]-n1[2])/d1, 5), 0.0]
    else:                       v1 = [ndid, round(n1[1] + (n1t[1]-n1[1])/2, 5), round(n1[2] + (n1t[2]-n1[2])/2, 5), 0.0]
    d2 = NodeDistance (n2, n2t)
    if d2 > dist * 1.5:         v2 = [ndid+1, round(n2[1] + dist * (n2t[1]-n2[1])/d2, 5), round(n2[2] + dist * (n2t[2]-n2[2])/d2, 5), 0.0]
    else:                       v2 = [ndid+1, round(n2[1] + (n2t[1]-n2[1])/2, 5), round(n2[2] + (n2t[2]-n2[2])/2, 5), 0.0]

    N1 =[ v1, n1[0], n1t[0], el[0], of   ]
    N2 =[ v2, n2[0], n2t[0], el[0], of   ]

    orign = [ el[0], el[1], el[2], el[3], el[4], el[5], el[6] ]
    # print ("%5d, %5d, %5d, %5d, %5d, %s, face=%d"%(orign[0], orign[1][0], orign[2][0], orign[3][0], orign[4][0], orign[5], of))
    orign[of] = v1; orign[of1] = v2 
    # print ("    >> %5d, %5d, %5d, %5d, %s, face=%d"%(orign[1][0], orign[2][0], orign[3][0], orign[4][0], orign[5], of))

    newel = [ elid, el[1], el[2], el[3], el[4], el[5], el[6] ]
    newel[oft] = v1; newel[of1t] = v2
    # print (" %5d, %5d, %5d, %5d, %5d, %s, face=%d"%(newel[0], newel[1][0], newel[2][0], newel[3][0], newel[4][0], newel[5], of))
    
    return [N1, N2], orign, newel 

    

def DistanceFromLineToNode2D(N0, nodes=[], xy=12):
    x = int(xy/10)
    y = int(xy%10)

    N1=nodes[0]
    N2=nodes[1]
    if len(nodes) ==2: 
        a = (N2[y]-N1[y])/(N2[x]-N1[x])
        A = -a
        C = a * N1[x] - N1[y]

        ## intersection position : N 
        cx = (-a * (-a*N1[x] + N1[y]) +     (N0[x] + a * N0[y]) )/ (1 + a*a)
        cy = (     (-a*N1[x] + N1[y]) + a * (N0[x] + a * N0[y]) )/ (1 + a*a)
        intersection_point=[-1, 0, 0, 0]
        intersection_point[x] = cx
        intersection_point[y] = cy
        ## N 
        return abs(A*N0[x]+N0[y]+C) / math.sqrt(A*A+1), intersection_point 

def NodeDistance(N1, N2): 
    return math.sqrt((N2[1]-N1[1])*(N2[1]-N1[1]) + (N2[2]-N1[2])*(N2[2]-N1[2]) + (N2[3]-N1[3])*(N2[3]-N1[3]))

def FaceContactingToMembrane(el, memb):

    n1 = el[1][0]
    n2 = el[2][0]
    n3 = el[3][0]
    try: 
        n4 = el[4][0]
        el4 = 1
    except:
        el4 = 0 
    face =0
    for mem in memb: 
        if (mem[1][0] == n1 and mem[2][0] == n2) or (mem[1][0] == n2 and mem[2][0] == n1):
            face = 1
            break
        if (mem[1][0] == n2 and mem[2][0] == n3) or (mem[1][0] == n3 and mem[2][0] == n2):
            face = 2
            break
        if el4 == 1: 
            if (mem[1][0] == n3 and mem[2][0] == n4) or (mem[1][0] == n4 and mem[2][0] == n3):
                face = 3
                break
            if (mem[1][0] == n4 and mem[2][0] == n1) or (mem[1][0] == n1 and mem[2][0] == n4):
                face = 4
                break
        elif el4 ==0: 
            if (mem[1][0] == n3 and mem[2][0] == n1) or (mem[1][0] == n1 and mem[2][0] == n3):
                face = 3
                break
        
    return face 

def ExtractingElementsbySet(name, Element): 
    element=[]
    for el in Element.Element:
        if el[5] == name: 
            element.append(el)
    
    return element

def ExtractingNodesfromElement(elements): 
    ns=[]
    for el in elements:
        ns.append(el[1][0])
        ns.append(el[2][0])
        if el[6] ==3:  
            ns.append(el[3][0])
        elif el[6] == 4: 
            ns.append(el[3][0])
            ns.append(el[4][0])

    ns = np.array(ns, dtype=np.int32)
    ns = np.unique(ns)
    return ns 


    
def SortingMembrane(name, Element):

    element=[]
    for el in Element.Element:
        if el[5] == name: 
            element.append(el)

    n1=[]; n2=[]
    for el in element:
        n1.append(el[1][0])
        n2.append(el[2][0])
    n1=np.array(n1)
    n2=np.array(n2)

    n=np.setdiff1d(n1, n2)

    nextmem = []
    sortedset =[]
    for el in element: 
        if el[1][0] == n[0]: 
            nextmem = el 

    while len(nextmem)>0: 
        sortedset.append(nextmem)
        nextmem = Next2nodeElement(nextmem, element)

    return sortedset 

def Next2nodeElement(element, elements): 
    for el in elements:
        if element[2][0] == el[1][0]: 
            return el 
    return []



if __name__ == "__main__":
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass 
    strJobDir = os.getcwd()
    lstSnsFileNames = glob.glob(strJobDir + '/*.sns')
    strSnsFileName = lstSnsFileNames[0]

    temperature = 25.0
    
    with open(strSnsFileName) as data_file:
        jsSns = json.load(data_file)

    TireGroup = str(jsSns["VirtualTireBasicInfo"]["ProductLine"])
    version = '2019'
    if 'S106' in strSnsFileName or 'S105' in strSnsFileName: 
        sims = 'ENDU'
    else: 
        sims = 'ELSE'

    # if TireGroup == "LTR" or TireGroup == "PCR": 

    VirtualTireID = str(jsSns["VirtualTireBasicInfo"]["VirtualTireID"])
    Revision = str(jsSns["VirtualTireBasicInfo"]["HiddenRevision"])
    MeshFile = VirtualTireID +"-"+Revision+".msh"
    # Mesh2D_ElsetDefinition_Endurance(MeshFile)
    Versioncheckfile = MeshFile[:-4]+".inp"
    
    with open (Versioncheckfile) as VER: 
        lines = VER.readlines()
    for line in lines: 
        if "** STANDARD MESH VERSION :" in line: 
            words = line.split(":")
            if "2020" in words[1]: 
                version = '2020'
            else: 
                version = '2019'
            break 
    
    if version == '2020': 
        print ("#####################################")
        print ("# STANDARD MESH VERSION : V2020")
        print ("#####################################")
        Mesh2D_ElsetDefinition_Endurance(MeshFile)  ## mesh standard 2020 
        ## adding element sets for pc/lt endurance simulation 
    else:
        print ("#####################################")
        print ("# STANDARD MESH VERSION : V2019")
        print ("#####################################")
        # print (" previous mesh ")
        Mesh2DModification(MeshFile) ## Initial Standard. 
        
    cInpNodeElement = InpNodeElement()
    cInpNodeElement.readCuteInp(strJobDir, jsSns) 
    
    cInpMaterial = InpMaterial()
    cInpMaterial.createMaterialInp(jsSns, version, sims, MeshFile)

    cInpRimContour = InpRimContour()
    cInpRimContour.createRimContour(jsSns)
    
    strSimCode = str(jsSns["AnalysisInformation"]["SimulationCode"])
    
    cInpStepDesc = InpStepDescription()
    strPathSART = '/home/fiper/ISLM/ISLMCommands/SART/Static/'
    # strPathSART = '/home/users/fiper/Documents/KJG/ABAQUS_Script/Endurance'            ### Temporary 

    for intNum in range(len(jsSns["AnalysisInformation"]["AnalysisCondition"])):
        cInpStepDesc.modifyStepDescription(strPathSART, intNum, jsSns)
        strSimTask = jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Task"]
        if strSimTask == '2DST':
            strInpLine = ''.join(cInpNodeElement.lstInpLines + cInpMaterial.lstInpLines + cInpRimContour.lstInpLines + cInpStepDesc.lstInpLines)
            createInpFile(strJobDir, strInpLine, strSimTask, strSimCode)

        elif strSimTask == '3DKV'  or strSimTask == '3DKL' or strSimTask == '3DKD' or strSimTask == '3DKT':
            strInpLine = ''.join(cInpStepDesc.lstInpLines)
            createInpFile(strJobDir, strInpLine, strSimTask, strSimCode)
        elif strSimTask == '3DST': # or strSimTask == '2DTH': 
            strInpLine = ''.join(cInpStepDesc.lstInpLines)
            createInpFile(strJobDir, strInpLine, strSimTask, strSimCode)

            try: Speed = float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Velocity"])
            except: Speed = 0.0
            if Speed > 0.0:
                # print ("Speed (kph)=", Speed)
                Pressure = float(jsSns["AnalysisInformation"]["AnalysisCondition"][intNum]["Pressure"])

                OD =float(jsSns["VirtualTireParameters"]["OverallDiameter"])
                CreateMODEL(strSimCode, OD, Speed, Pressure)

                CreateMaterial(cInpMaterial.lstElsetFECal, cInpMaterial.lstFECalProperties, cInpMaterial.lstElsetFECom, cInpMaterial.lstFEComProperties)
                strHeatInpLine = CreateHeatAnalysisInput(strJobDir, jsSns, cInpMaterial.lstElsetFECom, cInpMaterial.lstFEComProperties, cInpMaterial.lstElsetFECal, cInpMaterial.lstFECalProperties, ambient=temperature, steel=1, OD=OD, Speed=Speed)

    
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass 
