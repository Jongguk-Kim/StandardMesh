import glob, os, sys, json, time

try:
    import CheckExecution
except:
    pass


def Printlist(iList):
    N = len(iList)
    for i in range(N):
        print (iList[i])


if __name__ == "__main__":
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass

    os.system('rm -f *.err')
    # os.system('rm -f *.png')
    os.system('rm -f *.dat')
    # os.system('rm -f *.txt')
    os.system('rm -f *.tmp')
    t1 = time.time()


    strJobDir = os.getcwd()
    lstDOEparam = glob.glob(strJobDir + '/*.in')
        
    DOEparam = lstDOEparam[0]
    DOEid = DOEparam.split("/")[-1].split('.')[0]
    
    lstDOEVariables = glob.glob(strJobDir + '/*.var')
    DOEVariables = lstDOEVariables[0]
    
    
    # CommandSmartDir = '/home/users/fiper/ISLM/ISLMCommands/SART/SMART'
    # CommandAbaqusDir = '/home/users/fiper/ISLM/ISLMCommands/SART/Static'
    
    # CommandSmartDir = strJobDir          ## test 
    # CommandAbaqusDir = strJobDir         ## test 
    
    CommandSmartDir = '/home/users/fiper/ISLM/ISLMCommands/SART/DOE'
    CommandAbaqusDir = '/home/users/fiper/ISLM/ISLMCommands/SART/DOE'
    
    # Postdim = 'PostDOEDimension.py'
    # Postfoot1 = 'PostSMARTFootshape_DOE_v1_0.py'
    # Postfootd = 'PostSMARTFootshape_DOE_v1_0.py'
    # Postfoot2 = 'PostDOEFootprint.py'
    # Postrr = 'PostDOERR.py'
    # Postendu = 'PostDOEEndurance.py'
    
    strErrFileName = DOEid + '-GatheringResult.err'
    err=open(strErrFileName, 'w')
    
    with open(DOEparam) as IN:
        lines = IN.readlines()
    c = 0  
    isTW = 0
    paramname = []
    paramvalue= []
    for line in lines:
        data = list(line.split(","))
        I = len(data)
        ltemp = []
        for i in range(I):
            if c == 0:
                paramname.append(data[i].strip())
                if "TW" in data[i].strip() :
                    isTW = i
            else:
                if i == 0:
                    ltemp.append(int(data[i].strip()))
                else:
                    ltemp.append(float(data[i].strip()))
        if c != 0:
            paramvalue.append(ltemp)
        c += 1
        
    I=len(os.listdir(strJobDir))
    for i in range(I):
        if os.listdir(strJobDir)[i][-2:] == "-0":
            vtname = os.listdir(strJobDir)[i][:-2]
    basemodelsimulationlist = os.listdir(strJobDir+"/"+vtname+"-0/")
    i = 0
    while i < len(basemodelsimulationlist): 
        if "." in basemodelsimulationlist[i]:
            del basemodelsimulationlist[i]
            i -= 1
        i+= 1

    DIM = 0
    SFOOT = 0
    DFOOT = 0
    DRR = 0
    CSTIFF = 0
    SSTIFF =0 
    ENDU = 0
    MODAL = 0
    
    sDim = 'D103'
    sSfoot = 'D101'
    sDfoot = 'D104'
    sRR = 'D102'
    sCStiff = 'D205'
    sStff = 'S104'
    sEndu = 'S106' 
    sModal = 'S201'

    I = len(basemodelsimulationlist)
    for i in range(I):
        if sSfoot in basemodelsimulationlist[i]:
            SFOOT = 1
            dirSF = basemodelsimulationlist[i]
        if sRR in basemodelsimulationlist[i]:
            DRR = 1
            dirRR = basemodelsimulationlist[i]
        if sDim in basemodelsimulationlist[i]:
            DIM = 1
            dirDM = basemodelsimulationlist[i]
        if sDfoot in basemodelsimulationlist[i]:
            DFOOT = 1
            dirDF = basemodelsimulationlist[i]
        if sEndu in basemodelsimulationlist[i]:
            ENDU = 1
            dirEN = basemodelsimulationlist[i]
        if sStff in basemodelsimulationlist[i]:
            SSTIFF = 1
            dirSS = basemodelsimulationlist[i]
        if sCStiff in basemodelsimulationlist[i]:
            CSTIFF = 1
            dirCS = basemodelsimulationlist[i]
        if sModal in basemodelsimulationlist[i]:
            MODAL = 1
            dirMD = basemodelsimulationlist[i]

    print ("** Smulation types (1=Yes, 0=No)\n   Dimension=%d, Static Footprint=%d, Dynamic Footprint=%d, \
Cornering Stiffness=%d, RR=%d, Endurance=%d, \
Static Stiffness=%d, Modal=%d"%(DIM, SFOOT, DFOOT, CSTIFF, DRR, ENDU, SSTIFF, MODAL))

    
    DMVariables = {"DM-Initial_OD" :"Initial OD", \
                   "DM-Initial_SW" :"Initial SW", \
                   "DM-Initial_ShoDrop" :"Initial Sho. Drop", \
                   "DM-Initial_CrownRadius" :"Initial Crown Radius", \
                   "DM-Initial_BeltRadius" :"Initial Belt Radius", \
                   "DM-Initial_CarcassRadius" :"Initial Carcass Radius", \
                   "DM-Deformed_OD" :"Deformed OD", \
                   "DM-Deformed_SW" :"Deformed SW", \
                   "DM-Deformed_ShoDrop" :"Deformed Sho. Drop", \
                   "DM-Deformed_CrownRadius" :"Deformed Crown Radius", \
                   "DM-Deformed_BeltRadius" :"Deformed Belt Radius", \
                   "DM-Deformed_CarcassRadius" :"Deformed Carcass Radius", \
                   "DM-BTLiftCenter" :"Belt Center Lift", \
                   "DM-BTLiftEdge" :"Belt Edge Lift", \
                   "DM-BTDrop" :"Belt Edge Drop", \
                   "DM-Weight" :"Weight", \
                   "DM-Mold_K_Factor_A_Angle" :"Mold K-Factor", \
                   "DM-Inflated_K_Factor" :"Inflated K-Factor", \
                   }
    
    SFVariables = {"SF-SLR" : "SLR", \
                   "SF-SLW" : "SLW", \
                   "SF-ContactLength_Max" : "Contact Length Max", \
                   "SF-ContactLength_Cen" : "Contact Length Center", \
                   "SF-ContactLength_25": "Contact Length 25", \
                   "SF-ContactLength_15": "Contact Length 15", \
                   "SF-ContactLength_75": "Contact Length 75", \
                   "SF-ContactLength_85": "Contact Length 85", \
                   "SF-ContactLength_Ratio2575": "Contact Length Ratio 25%/75%", \
                   "SF-ContactLength_Ratio1585": "Contact Length Ratio 15%/85%", \
                   
                   "SF-ContactWidth_Max": "Contact Width Max", \
                   "SF-ContactWidth_Cen": "Contact Width Center", \
                   "SF-SquareRatio_25": "Square Ratio 25", \
                   "SF-SquareRatio_15": "Square Ratio 15", \
                   "SF-SquareRatio_75": "Square Ratio 75", \
                   "SF-SquareRatio_85": "Square Ratio 85", \
                   "SF-RibForceRatio": "Rib Contact Force Ratio", \
                   "SF-RibAreaRatio": "Rib Contact Area Ratio", \
                   "SF-ContactArea_Actual": "Actual Contact Area", \
                   "SF-ContactArea_Total": "Total Contact Area", \
                   "SF-Roundness": "Roundness", \
                   "SF-Snowscore": "SNOW SCORE", \
                    }
    DFVariables = {"DF-DLR": "DLR", \
                   "DF-DLW": "DLW", \
                   "DF-DRR": "DRR", \
                   "DF-ContactLength_Max": "Contact Length Max", \
                   "DF-ContactLength_Cen": "Contact Length Center", \
                   "DF-ContactLength_25": "Contact Length 25", \
                   "DF-ContactLength_15": "Contact Length 15", \
                   "DF-ContactLength_75": "Contact Length 75", \
                   "DF-ContactLength_85": "Contact Length 85", \
                   "DF-ContactLength_Ratio2575": "Contact Length Ratio 25%/75%", \
                   "DF-ContactLength_Ratio1585": "Contact Length Ratio 15%/85%", \
                   "DF-ContactWidth_Max": "Contact Width Max", \
                   "DF-ContactWidth_Cen": "Contact Width Center", \
                   
                   "DF-SquareRatio_25": "Square Ratio 25", \
                   "DF-SquareRatio_15": "Square Ratio 15", \
                   "DF-SquareRatio_75": "Square Ratio 75", \
                   "DF-SquareRatio_85": "Square Ratio 85", \
                   "DF-RibForceRatio": "Rib Contact Force Ratio", \
                   "DF-RibAreaRatio": "Rib Contact Area Ratio", \
                   "DF-ContactArea_Actual": "Actual Contact Area", \
                   "DF-ContactArea_Total": "Total Contact Area", \
                   "DF-Roundness": "Roundness", \
                   "DF-CorneringForce": "Cornering Force", \
                   "DF-AligningMoment": "Aligning Moment", \
                   
                   "DF-Temp_CrownMax": "Temperature Max Crown", \
                   "DF-Temp_BeltL": "Temperature Belt Edge Left", \
                   "DF-Temp_BeltR": "Temperature Belt Edge Right", \
                   "DF-Temp_BeadMax": "Temperature Max Bead", \
                   "DF-Total_RR": "Energy Loss Total", \
                   "DF-Crown_RR": "Energy Loss Crown", \
                   "DF-Filler_RR": "Energy Loss Filler", \
                   "DF-BSW_RR": "Energy Loss Sidewall", \
                    }
    CSVariables = {"CS-DLR": "DLR", \
                   "CS-DLW": "DLW", \
                   "CS-DRR": "DRR", \
                   "CS-ContactLength_Max": "Contact Length Max", \
                   "CS-ContactLength_Cen": "Contact Length Center", \
                   "CS-ContactLength_25": "Contact Length 25", \
                   "CS-ContactLength_15": "Contact Length 15", \
                   "CS-ContactLength_75": "Contact Length 75", \
                   "CS-ContactLength_85": "Contact Length 85", \
                   "CS-ContactLength_Ratio2575": "Contact Length Ratio 25%/75%", \
                   "CS-ContactLength_Ratio1585": "Contact Length Ratio 15%/85%", \
                   "CS-ContactWidth_Max": "Contact Width Max", \
                   "CS-ContactWidth_Cen": "Contact Width Center", \
                   
                   "CS-SquareRatio_25": "Square Ratio 25", \
                   "CS-SquareRatio_15": "Square Ratio 15", \
                   "CS-SquareRatio_75": "Square Ratio 75", \
                   "CS-SquareRatio_85": "Square Ratio 85", \
                   "CS-RibForceRatio": "Rib Contact Force Ratio", \
                   "CS-RibAreaRatio": "Rib Contact Area Ratio", \
                   "CS-ContactArea_Actual": "Actual Contact Area", \
                   "CS-ContactArea_Total": "Total Contact Area", \
                   "CS-Roundness": "Roundness", \
                   "CS-CorneringForce": "Cornering Force", \
                   "CS-AligningMoment": "Aligning Moment", \
                   
                   "CS-CorneringStiffness": "Cornering Stiffness", \
                   "CS-AligningStiffness": "Aligning-Moment Stiffness", \
                   
                   "CS-Temp_CrownMax": "Temperature Max Crown", \
                   "CS-Temp_BeltL": "Temperature Belt Edge Left", \
                   "CS-Temp_BeltR": "Temperature Belt Edge Right", \
                   "CS-Temp_BeadMax": "Temperature Max Bead", \
                   "CS-Total_RR": "Energy Loss Total", \
                   "CS-Crown_RR": "Energy Loss Crown", \
                   "CS-Filler_RR": "Energy Loss Filler", \
                   "CS-BSW_RR": "Energy Loss Sidewall", \
                    }
    RRVariables = {"RR-DLR": "DLR", \
                   "RR-DLW": "DLW", \
                   "RR-DRR": "DRR", \
                   "RR-Temp_CrownMax": "Temperature Max Crown", \
                   "RR-Temp_BeltEdgeL": "Temperature Belt Edge L", \
                   "RR-Temp_BeltEdgeR": "Temperature Belt Edge R", \
                   "RR-Temp_BeadMax": "Temperature Max Bead", \
                   "RR-Total_RR": "Energy Loss Total", \
                   "RR-Crown_RR": "Energy Loss Crown", \
                   "RR-Filler_RR": "Energy Loss Filler", \
                   "RR-BSW_RR": "Energy Loss Sidewall", \
                    }
    ENVariables = {
                   "EN-ReBeltStrain": "Re-BT Strain", \
                   "EN-ReBeltTemp": "Re-BT Temperature", \
                   "EN-ReBeltLife": "Re-BT Life Index", \

                   "EN-BeltStrain": "BT Edge Strain", \
                   "EN-BeltTemp": "BT Edge Temperature", \
                   "EN-BeltLife": "BT Edge Life Index", \
                    
                   "EN-UpCcStrain": "Upper Cc Area Strain", \
                   "EN-UpCcTemp": "Upper Cc Area Temperature", \
                   "EN-UpCcLife": "Upper Cc Area Life Index", \
                   
                   "EN-LowCcStrain": "Low Cc Area Strain", \
                   "EN-LowCcTemp": "Low Cc Area Temperature", \
                   "EN-LowCcLife": "Low Cc Area Life Index", \
                   
                   "EN-TurnUpStrain": "Cc Turn Up Strain", \
                   "EN-TurnUpTemp": "Cc Turn Up Temperature", \
                   "EN-TurnUpLife": "Cc Turn Up Life Index", \
                    }
    SSVariables = {
                   "SS-CyclicSED_BT": "BT SED Amplitude", \
                   "SS-MaxSED_BT": "BT SED Max Value", \
                   "SS-CyclicPLE_BSW": "BSW PLE Amplitude", \
                   "SS-MaxPLE_BSW": "BSW PLE Max", \
                   "SS-CyclicTresca_Filler": "Filler Tresca Amplitude", \
                   "SS-MaxTresca_Filler": "Filler Tresca Max", \
                   "SS-KL": "Lateral Stiffness", \
                   "SS-KD": "Tortional Stiffness", \
                   "SS-KV": "Vertical Stiffness", \
                   "SS-KT": "Tractional Stiffness", \
                   "SS-KVLinear": "Linear Assump. KV", \

                #    "SS-KL": "LStiff", \
                #    "SS-KD": "DStiff", \
                #    "SS-KV": "VStiff_AtFullLoad", \
                #    "SS-KT": "TStiff", \
                    }

    MDVariables = {
                    "MD-EigenValue_1": "EigenValues 1", \
                   "MD-Frequency_1": "Frequency(Rad/Time) 1", \
                   "MD-GeneralizedMass_1": "Generalized mass 1", \

                   "MD-EigenValue_2": "EigenValues 2", \
                   "MD-Frequency_2": "Frequency(Rad/Time) 2", \
                   "MD-GeneralizedMass_2": "Generalized mass 2", \

                   "MD-EigenValue_3": "EigenValues 3", \
                   "MD-Frequency_3": "Frequency(Rad/Time) 3", \
                   "MD-GeneralizedMass_3": "Generalized mass 3", \

                   "MD-EigenValue_4": "EigenValues 4", \
                   "MD-Frequency_4": "Frequency(Rad/Time) 4", \
                   "MD-GeneralizedMass_4": "Generalized mass 4", \

                   "MD-EigenValue_5": "EigenValues 5", \
                   "MD-Frequency_5": "Frequency(Rad/Time) 5", \
                   "MD-GeneralizedMass_5": "Generalized mass 5", \

                   "MD-EigenValue_6": "EigenValues 6", \
                   "MD-Frequency_6": "Frequency(Rad/Time) 6", \
                   "MD-GeneralizedMass_6": "Generalized mass 6", \

                   "MD-EigenValue_7": "EigenValues 7", \
                   "MD-Frequency_7": "Frequency(Rad/Time) 7", \
                   "MD-GeneralizedMass_7": "Generalized mass 7", \

                   "MD-EigenValue_8": "EigenValues 8", \
                   "MD-Frequency_8": "Frequency(Rad/Time) 8", \
                   "MD-GeneralizedMass_8": "Generalized mass 8", \

                   "MD-EigenValue_9": "EigenValues 9", \
                   "MD-Frequency_9": "Frequency(Rad/Time) 9", \
                   "MD-GeneralizedMass_9": "Generalized mass 9", \

                   "MD-EigenValue_10": "EigenValues 10", \
                   "MD-Frequency_10": "Frequency(Rad/Time) 10", \
                   "MD-GeneralizedMass_10": "Generalized mass 10", \
                      
                    }
    
    
    I = len(paramvalue)
    cwdfiles = os.listdir(strJobDir)
    dirnames = []
    for directory in cwdfiles: 
        if '-' in directory and not "." in directory:
            dirnames.append(directory)
    vts = len(dirnames)
    vtnames = []
    for i in range(vts):
        for v in dirnames: 
            if int(v.split("-")[1]) == i: 
                vtnames.append(v)
    
    if DIM == 1:
        result = DOEid + '-Dimension.txt'
        f = open (result, "w")
        for name in vtnames: 
            v_tires = strJobDir + "/" + name + "/"
            wdjobs = os.listdir(v_tires)
            
            for dt in wdjobs: 
                if sDim in dt:
                    wd = dt
                    break
            resultfile = v_tires +wd + "/" + wd+"-Dimension.txt"
            # print (resultfile)
            with open(resultfile) as rst:
                lines = rst.readlines()
            f.writelines(lines)
        f.close()
        resultdim = DOEid + '-Dimension.txt'
        with open(resultdim) as IN:
            dm = IN.readlines()
    
    if SFOOT == 1:
        result = DOEid + '-Staticfootprint.txt'
        f = open (result, "w")
        for name in vtnames: 
            v_tires = strJobDir + "/" + name + "/"
            wdjobs = os.listdir(v_tires)
            for dt in wdjobs: 
                if sSfoot in dt:
                    wd = dt
                    break
            resultfile = v_tires +wd + "/" + wd+"-DOE-Staticfootprint.txt"
            # print (resultfile)
            with open(resultfile) as rst:
                lines = rst.readlines()
            f.writelines(lines)

            resFPC =  v_tires +wd + "/" + wd+"-FPC.txt"
            with open(resFPC) as FPC:
                fpclines = FPC.readlines()
            ribNo=0 
            foot_rev = wd.split("-")[2]
            for line in fpclines: 
                if "Fitted Length for Rib" in line: 
                    values = line.split("=")[1].strip()
                    values = values.split("/")
                    txt = "%s, Fitted Center Length Rib %d=%.3f\n"%(foot_rev, ribNo, float(values[0].strip()))
                    f.write(txt)
                    txt = "%s, Fitted Left Length Rib %d=%.3f\n"%(foot_rev, ribNo, float(values[1].strip()))
                    f.write(txt)
                    txt = "%s, Fitted Right Length Rib %d=%.3f\n"%(foot_rev, ribNo, float(values[2].strip()))
                    f.write(txt)
                    ribNo+=1 
        f.close()

        AddingVar=[]
        for k in range(ribNo): 
            key = 'SF-RIB%d_CenterLength'%(k)
            val = 'Fitted Center Length Rib %d'%(k)
            AddingVar.append(key)
            SFVariables[key]=val
            key = 'SF-RIB%d_LeftLength'%(k)
            val = 'Fitted Left Length Rib %d'%(k)
            AddingVar.append(key)
            SFVariables[key]=val
            key = 'SF-RIB%d_RightLength'%(k)
            val = 'Fitted Right Length Rib %d'%(k)
            AddingVar.append(key)
            SFVariables[key]=val

        resultsf = DOEid + '-Staticfootprint.txt'
        with open(resultsf) as IN:
            sf = IN.readlines()

        wdir = os.getcwd()
        IDFile = wdir+"/"+DOEid
        IDFileTmp = wdir+"/"+DOEid+".tp1"
        if not os.path.isfile(IDFileTmp): 
            tf = open(IDFileTmp, 'w')
            with open(IDFile+".var") as VAR: 
                lines = VAR.readlines()
            for line in lines:
                tf.write(line)
            tf.close()
        
        with open(IDFileTmp) as VAR: 
            lines = VAR.readlines()

        f=open(IDFile+".var",'w')
        for line in lines: 
            f.write(line)
        f.close()

        f=open(IDFile+".var",'a')
        for var in AddingVar: 
            f.write("\n"+var)
        f.close()

    if DFOOT == 1:
        result = DOEid + '-Rollingfootprint.txt'
        f = open (result, "w")
        for name in vtnames: 
            v_tires = strJobDir + "/" + name + "/"
            wdjobs = os.listdir(v_tires)
            for dt in wdjobs: 
                if sDfoot in dt:
                    wd = dt
                    break
            resultfile = v_tires +wd + "/" + wd+"-DOE-Rollingcharacteristics.txt"
            # print (resultfile)
            with open(resultfile) as rst:
                lines = rst.readlines()
            try:lines[38] = lines[38].replace("-","") #remove minus sign from Cornering Force
            except:  pass
            f.writelines(lines)
        f.close()
        resultdf = DOEid + '-Rollingfootprint.txt'
        with open(resultdf) as IN:
            df = IN.readlines()

    if DRR == 1:
        result = DOEid + '-RR.txt'
        f = open (result, "w")
        for name in vtnames: 
            v_tires = strJobDir + "/" + name + "/"
            wdjobs = os.listdir(v_tires)
            for dt in wdjobs: 
                if sRR in dt:
                    wd = dt
                    break
            resultfile = v_tires +wd + "/" + wd+"-RR.txt"
            # print (resultfile)
            with open(resultfile) as rst:
                lines = rst.readlines()

            f.writelines(lines)
        f.close()
        resultrr = DOEid + '-RR.txt'
        with open(resultrr) as IN:
            rr = IN.readlines()

    if SSTIFF ==1: 
        result = DOEid + '-StaticStiffness.txt'
        isOldStiffness=0
        f = open (result, "w")
        for name in vtnames: 
            v_tires = strJobDir + "/" + name + "/"
            wdjobs = os.listdir(v_tires)
            for dt in wdjobs: 
                if sStff in dt:
                    wd = dt
                    break
            resultfile = v_tires +wd + "/" + wd+"-StaticStiffness.txt"
            if not os.path.isfile(resultfile):
                resultfile = v_tires +wd + "/" + wd+"-StaticStiffnessENDU.txt"
                with open(resultfile) as rst:
                    lines = rst.readlines()
                f.writelines(lines)
                isOldStiffness = 1
            else:
                revision = wd.split("-")[2]
                with open(resultfile) as rst:
                    lines = rst.readlines()
                for line in lines: 
                    if 'Success' in line:    break
                    if "**" in line: continue 

                    if "VStiff_LinearAssumption" in line: 
                        LinearKv = line.split("=")[1].strip()
                    if "VStiff_AtFullLoad" in line: 
                        Kv = line.split("=")[1].strip()
                    
                    if "TStiff" in line: 
                        Kt = line.split("=")[1].strip()
                    if "LStiff" in line: 
                        Kl = line.split("=")[1].strip()
                    if "DStiff" in line: 
                        Kd = line.split("=")[1].strip()
                    
                dataline = "%s, Vertical Stiffness=%s\n"%(revision, Kv)
                f.writelines(dataline)
                dataline = "%s, Linear Assump. KV=%s\n"%(revision, LinearKv)
                f.writelines(dataline)
                dataline = "%s, Tractional Stiffness=%s\n"%(revision, Kt)
                f.writelines(dataline)
                dataline = "%s, Lateral Stiffness=%s\n"%(revision, Kl)
                f.writelines(dataline)
                dataline = "%s, Tortional Stiffness=%s\n"%(revision, Kd)
                f.writelines(dataline)

        f.close()
        
        with open(result) as IN:
            ss = IN.readlines()
    
    if ENDU ==1:
        result = DOEid + '-LongTermEndurance.txt'
        f = open (result, "w")
        for name in vtnames: 
            v_tires = strJobDir + "/" + name + "/"
            wdjobs = os.listdir(v_tires)
            for dt in wdjobs: 
                if sEndu in dt:
                    wd = dt
                    break
            resultfile = v_tires +wd + "/" + wd+"-LongTermEndurance.txt"
            revision = wd.split("-")[2]
            with open(resultfile) as rst:
                lines = rst.readlines()

            for line in lines:
                if "Success" in line: break 
                if '*' in line and not "Endurance" in line: break  
                # print(line)
                words = line.split(" ")
                cnt =0
                for word in words: 
                    if word =="": continue 
                    cnt += 1
                    if cnt == 4: strain = word.strip()
                    if cnt == 5: temperature = word.strip()
                    if cnt == 6: lifeIdx = word.strip()
                # print(words)
                if 'Rein' in line: 
                    dataline = "%s, Re-BT Strain=%s\n"%(revision, strain);              f.writelines(dataline)
                    dataline = "%s, Re-BT Temperature=%s\n"%(revision, temperature);    f.writelines(dataline)
                    dataline = "%s, Re-BT Life Index=%s\n"%(revision, lifeIdx);           f.writelines(dataline)
                if 'Between' in line: 
                    dataline = "%s, BT Edge Strain=%s\n"%(revision, strain);              f.writelines(dataline)
                    dataline = "%s, BT Edge Temperature=%s\n"%(revision, temperature);    f.writelines(dataline)
                    dataline = "%s, BT Edge Life Index=%s\n"%(revision, lifeIdx);           f.writelines(dataline)
                if 'Upper' in line: 
                    dataline = "%s, Upper Cc Area Strain=%s\n"%(revision, strain);              f.writelines(dataline)
                    dataline = "%s, Upper Cc Area Temperature=%s\n"%(revision, temperature);    f.writelines(dataline)
                    dataline = "%s, Upper Cc Area Life Index=%s\n"%(revision, lifeIdx);           f.writelines(dataline)
                if 'Lower' in line: 
                    dataline = "%s, Low Cc Area Strain=%s\n"%(revision, strain);              f.writelines(dataline)
                    dataline = "%s, Low Cc Area Temperature=%s\n"%(revision, temperature);    f.writelines(dataline)
                    dataline = "%s, Low Cc Area Life Index=%s\n"%(revision, lifeIdx);           f.writelines(dataline)
                if 'TurnUp' in line: 
                    dataline = "%s, Cc Turn Up Strain=%s\n"%(revision, strain);              f.writelines(dataline)
                    dataline = "%s, Cc Turn Up Temperature=%s\n"%(revision, temperature);    f.writelines(dataline)
                    dataline = "%s, Cc Turn Up Life Index=%s\n"%(revision, lifeIdx);         f.writelines(dataline)

        f.close()
        # resultendu = DOEid + '-LongTermEndurance.txt'
        with open(result) as IN:
            en = IN.readlines()

    if CSTIFF == 1:
        result = DOEid + '-CorneringStiffness.txt'
        f = open (result, "w")
        for name in vtnames: 
            v_tires = strJobDir + "/" + name + "/"
            wdjobs = os.listdir(v_tires)
            for dt in wdjobs: 
                if sCStiff in dt:
                    wd = dt
                    break
            resultfile = v_tires +wd + "/" + wd+"-DOE-CorneringStiffness.txt"
            with open(resultfile) as rst:
                lines = rst.readlines()
            f.writelines(lines)
        f.close()
        resultcs = result
        with open(resultcs) as IN:
            cs = IN.readlines()

    if MODAL ==1: 
        result = DOEid + '-Modal.txt'
        f = open (result, "w")
        for name in vtnames: 
            v_tires = strJobDir + "/" + name + "/"
            wdjobs = os.listdir(v_tires)
            for dt in wdjobs: 
                if sModal in dt:
                    wd = dt
                    break
            resultfile = v_tires +wd + "/" + wd+"-ModalResults.txt"
            # print (resultfile)
            revision = wd.split("-")[2]
            with open(resultfile) as rst:
                lines = rst.readlines()
            for line in lines:
                if 'Success' in line: 
                    break 
                if "Mode" in line: continue 
                words = line.split(" ")
                cnt = 0 
                for word in words:
                    if word=="": continue 
                    cnt += 1
                    if cnt == 1: 
                        mode = word.strip()
                    if cnt == 2 : 
                        eigen = word.strip()
                    if cnt == 3 : 
                        freq = word.strip()
                    if cnt == 5 : 
                        mass = word.strip()
                    
                dataline = "%s, EigenValues %s=%s\n"%(revision, mode, eigen)
                f.writelines(dataline)
                dataline = "%s, Frequency(Rad/Time) %s=%s\n"%(revision, mode, freq)
                f.writelines(dataline)
                dataline = "%s, Generalized mass %s=%s\n"%(revision, mode, mass)
                f.writelines(dataline)

        f.close()
        resultmodal = result
        with open(resultmodal) as IN:
            md = IN.readlines()
    ##################################################################
    with open(DOEVariables) as IN:
        lines = IN.readlines()   

    variableitems=[]
    isDM = 0 
    isK_factor = 0 
    for line in lines:
        if "*" in line :
            pass
        else:
            if "DM-" in line: 
                isDM = 1 
            if 'MD-EigenValue' in line:
                for i in range(10): 
                    ivar = 'MD-EigenValue_%d'%(i+1)
                    variableitems.append(ivar)
            elif 'MD-Frequency' in line:
                for i in range(10): 
                    ivar = 'MD-Frequency_%d'%(i+1)
                    variableitems.append(ivar)
            elif 'MD-GeneralizedMass' in line:
                for i in range(10): 
                    ivar = 'MD-GeneralizedMass_%d'%(i+1)
                    variableitems.append(ivar)
            elif 'DM-KFactor' in line:
                isK_factor =1 
                variableitems.append('DM-Mold_K_Factor_A_Angle')
                variableitems.append('DM-Inflated_K_Factor')
            elif "EN-" in line: 
                if "EN-CyclicSED_BT" in line:   variableitems.append("SS-CyclicSED_BT")
                elif "EN-MaxSED_BT" in line:   variableitems.append("SS-MaxSED_BT")
                elif "EN-CyclicPLE_BSW" in line:   variableitems.append("SS-CyclicPLE_BSW")
                elif "EN-MaxPLE_BSW" in line:   variableitems.append("SS-MaxPLE_BSW")
                elif "EN-CyclicTresca_Filler" in line:   variableitems.append("SS-CyclicTresca_Filler")
                elif "EN-MaxTresca_Filler" in line:   variableitems.append("SS-MaxTresca_Filler")
                elif "EN-KL" in line:   variableitems.append("SS-KL")
                elif "EN-KD" in line:   variableitems.append("SS-KD")
                elif "EN-KV" in line:   variableitems.append("SS-KV")
                elif "EN-KT" in line:   variableitems.append("SS-KT")
                elif "EN-KVLinear" in line:   variableitems.append("SS-KVLinear")
                else: variableitems.append(line.strip())

            else:
                variableitems.append(line.strip())
    if isDM ==1 and isK_factor ==0: 
        variableitems.append('DM-Mold_K_Factor_A_Angle')
        variableitems.append('DM-Inflated_K_Factor')

    values =[]
    c=0
    for items in variableitems:
        values.append([])
        
        print ("items=%s"%(items))
        if "DM-" in items:
            # print " DM : ", DMVariables[items]
            for line in dm:
                # print ("LINE", line)
                if DMVariables[items] in line:
                    variables = items
                    revision = int(line.split(',')[0].strip())
                    value = float(line.split(',')[1].split('=')[1].strip())
                    if revision==0: print (" * %s - %d, %f " %( variables, revision, value))
                    values[c].append(value)
        if "SF-" in items:
            # print " SF : ", SFVariables[items]   #  "SF-Snowscore": "SNOW SCORE", \
            for line in sf:
                if SFVariables[items] in line:
                    variables = items
                    revision = int(line.split(',')[0].strip())
                    value = float(line.split(',')[1].split('=')[1].strip())
                    if "SNOW SCORE" in SFVariables[items] :
                        if revision == 0:
                            snowscorebase = value 
                        value = value / snowscorebase * 100.0
                    if revision==0: print (" * %s - %d, %f " %( variables, revision, value))
                    
                    values[c].append(value)
        if "DF-" in items:
            # print " DF : ", DFVariables[items]
            for line in df:
                if DFVariables[items] in line:
                    variables = items
                    revision = int(line.split(',')[0].strip())
                    value = float(line.split(',')[1].split('=')[1].strip())
                    if revision==0: print (" * %s - %d, %f " %( variables, revision, value))
                    values[c].append(value)
        if "RR-" in items:
            # print " RR : ", RRVariables[items]
            for line in rr:
                if RRVariables[items] in line:
                    variables = items
                    revision = int(line.split(',')[0].strip())
                    value = float(line.split(',')[1].split('=')[1].strip())
                    if revision==0: print (" * %s - %d, %f " %( variables, revision, value))
                    values[c].append(value)
        if "EN-" in items:
            # print ("*** EN : ", items[2:])
            for line in en:
                if ENVariables[items] in line:
                    variables = items
                    revision = int(line.split(',')[0].strip())
                    value = float(line.split(',')[1].split('=')[1].strip())
                    if revision==0: print (" * %s - %d, %f " %( variables, revision, value))
                    values[c].append(value)
        if "SS-" in items:
            # print " SS : ", SSVariables[items]
            for line in ss:
                try:
                    if SSVariables[items] in line:
                        variables = items
                        revision = int(line.split(',')[0].strip())
                        value = float(line.split(',')[1].split('=')[1].strip())
                        if revision==0: print (" * %s - %d, %f " %( variables, revision, value))
                        values[c].append(value)
                except:
                    continue 

        if "CS-" in items:
            # print (" CS : %s >> "%(items), CSVariables[items])
            for line in cs:
                if CSVariables[items] in line:
                    variables = items
                    revision = int(line.split(',')[0].strip())
                    value = float(line.split(',')[1].split('=')[1].strip())
                    if revision==0: print (" * %s - %d, %f " %( variables, revision, value))
                    values[c].append(value)
        
        if "MD-" in items:
            print (" MD : ", MDVariables[items])
            for line in md:
                if MDVariables[items] in line:
                    variables = items
                    revision = int(line.split(',')[0].strip())
                    value = float(line.split(',')[1].split('=')[1].strip())
                    if revision==0: print (" * %s - %d, %E " %( variables, revision, value))
                    values[c].append(value)
        
        c += 1
    
    f = open(DOEid+".ppr", "w")   ## ppr : post-processing results 
    line = ' NO'
    for item in variableitems:
        line += ',%27s'%(item)
    line += '\n'
    f.writelines(line)  
    # print "No of Item =", c, len(values), len(values[0])
    
    M = len(values)
    I = len(values[0])
    print ("### No of VTs=%d"%(I))
    for i in range(I):
        line = str(format(i, "3"))
        for j in range(M): 
            try:
                line += ',' + str(format(values[j][i], '27.6f'))
            except:
                print ("ERROR !! %s j=%d, i=%d Model No=%d\n"%(variableitems[j], j, i, I))
                sys.exit()
        line += '\n'
        f.writelines(line)    
    f.writelines("\nSuccess::Post::[DOE] This simulation result was created successfully!!")
        
    f.close()

    err.close()
    tEnd = time.time()
    print ("DOE Collecting Results Done !! - %f"%(tEnd - t1))
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass
    
    
    
    

        
        