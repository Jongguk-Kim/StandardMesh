# from os import system, getcwd 
import os 
from glob import glob
from json import load  
try:    import CommonFunction as TIRE
except: import CommonFunction_v3_0 as TIRE
import SMARTDynamicFootshapeForCorneringStiffness as DF 
import SMARTRollingcharactericsForCorneringStiffness as RC

def plotribshape(Imagenamebase, lastSDBFile, lastSFRIC, group='PCR', mesh2d='', iter=1, step=0, condition='', offset=10000, treadno=10000000, dpi=100, ribimage=0, vmin='', doe=0, fitting=6, ribgraph=0):
    TIRE.PlotFootprint(Imagenamebase, lastSDBFile, lastSFRIC, group=group, mesh2d= mesh2d, iter=iter, step =step, condition=condition, offset=offset, treadno=treadno, dpi=dpi, ribimage=ribimage, vmin=vmin, doe=doe, fitting=fitting, ribgraph=ribgraph)


if __name__ == "__main__": 

    #################################################
    # Define Sub Folder & File Definition
    #################################################
    SubFolderBasicName = 'CS'
    SubFolderSerialDigit = '03'
    SubFileBasicName = '-CS'
    SubFileSerialDigit = '03'
    #################################################

    cwd = os.getcwd()
    snsFile = glob(cwd+"/*.sns")[0]
    with open(snsFile) as SNS: 
        snsInfo = load(SNS)
    strSimCode = snsInfo["AnalysisInformation"]["SimulationCode"]
    strSimCode = snsFile.split("/")[-1]
    strSimCode = strSimCode[:-4]
    ProductLine = snsInfo["VirtualTireBasicInfo"]["ProductLine"]
    
    i = 1
    Serial = str(format(i, SubFolderSerialDigit))
    subFolderName = SubFolderBasicName + Serial
    subFileName = strSimCode + SubFileBasicName + Serial
    SmartInpFileName = subFileName + '.inp'
    str2DInp = strSimCode.split("-")[1]+"-"+strSimCode.split("-")[2]+".inp"

    revision = snsFile.split("-")[2]

    angles=[]
    simFiles=[]
    for i in range(2): 
        Serial = str(format(i+1, SubFolderSerialDigit))
        subFolderName = SubFolderBasicName + Serial 
        subFileName = strSimCode + SubFileBasicName + Serial
        smartInputFile = cwd+"/" + subFileName +".inp"
        SimTime = TIRE.SIMTIME(smartInputFile)
        Condition = TIRE.CONDITION(smartInputFile)
        ResultStep =  str(format(SimTime.LastStep, '03'))

        angles.append(Condition.SlipAngle)
        simFiles.append(subFileName+'-DOE-Rollingcharacteristics.txt')

        sfric = cwd+"/"+subFolderName+"/SFRIC."+subFileName+"/"+subFileName+".sfric"
        result =cwd+"/"+subFolderName+"/SFRIC."+subFileName+"/"+subFileName+".sfric" + ResultStep
        trd = cwd+"/"+str2DInp[:-3]+"trd"
        shist = cwd+"/"+subFolderName + "/REPORT/frc_"+subFileName+".rpt"
        contour = cwd+"/"+subFileName 
        slip = Condition.SlipAngle
        load = Condition.Load
        product = ProductLine
        mesh = cwd+"/"+str2DInp
        point = cwd+"/"+subFileName+'-ContactShapePoint.dat'
        press = cwd+"/"+subFileName+'-CpressAlongCenter.txt'
        value = cwd+"/"+subFileName+'-CharacteristicValues.txt'
        area = cwd+"/"+subFileName+'-ContactSurfaceArea.txt'
        fpc = cwd+"/"+subFileName+'-FPC.txt'


        DF.main(sfricFileName=sfric, sfricResultFileName=result, \
            trdFileName=trd, shistFileName=shist, contourFileName=contour, SlipAngle=slip,\
            vload=load, ProductLine=product,  CUTEInpFileName=mesh, \
            pointFileName=point, pressFileName=press, valuesFileName=value,\
			areaFileName=area,infoFileName=fpc)

        simCode =  subFileName
        sns = snsFile
        rimForce = shist 
        energyLoss = cwd+"/"+subFolderName + "/REPORT/vis_"+subFileName+".rpt"
        sdb = cwd+"/"+subFolderName+"/SDB."+subFileName+"/"+subFileName+".sdb"
        sdbresult =cwd+"/"+subFolderName+"/SDB."+subFileName+"/"+subFileName+".sdb" + ResultStep
        smart = smartInputFile
        RC.main(CorneringStiffnessSimulation=1, iSimCode=simCode, sns=sns, rimfile=rimForce, LossFile=energyLoss,\
             SDB=sdb, SFRIC=sfric, lastSDB=sdbresult, lastSFRIC=result, mesh=mesh, FPCfile=fpc,smart=smart )

    with open(simFiles[0]) as F1: 
        ln1 = F1.readlines()
    with open(simFiles[1]) as F1: 
        ln2 = F1.readlines()

    fp = open(snsFile[:-4]+"-DOE-CorneringStiffness.txt", 'w')
    Force =[]
    Moment=[]
    for l1, l2 in zip(ln1, ln2): 
        words = l1.split(",")
        line = revision +"," 
        word = words[1].split("=")
        line += word[0] + "="
        data1 = float(word[1].strip())

        words = l2.split(",")[1]
        data2 = words.split("=")[1]
        data2 = float(data2.strip())

        data = (data1+data2)/2.0
        line += "%.3f\n"%(data)
        fp.write(line)

        if "Cornering Force" in word[0]: 
            Force = [data1, data2]
        if "Aligning Moment" in word[0]: 
            Moment = [data1, data2]

    delAngle = abs(angles[1]-angles[0])

    
    if angles[1] > angles[0]: 
        line1 = "%s, Cornering Stiffness[N/degree]=%.3f\n"%(revision, -(Force[1]-Force[0])/delAngle)
        line2 = "%s, Aligning-Moment Stiffness[N-m/degree]=%.3f\n"%(revision, (Moment[1]-Moment[0])/delAngle)
    else:
        line1 = "%s, Cornering Stiffness[N/degree]=%.3f\n"%(revision,-(Force[0]-Force[1])/delAngle)
        line2 = "%s, Aligning-Moment Stiffness[N-m/degree]=%.3f\n"%(revision,  (Moment[1]-Moment[0])/delAngle)

    fp.write(line1)
    fp.write(line2)
    fp.close()

    f = open(snsFile[:-4]+"-CorneringStiffness.txt", 'w')
    f.write("Slip Angle=%.2f\n"%((angles[0]+angles[1])/2.0))
    line1 = line1.split(",")[1]
    line2 = line2.split(",")[1]
    f.write(line1[1:])
    f.write(line2[1:])
    f.write("Lateral Force=%.3f\n"%((Force[0]+Force[1])/2.0) )
    f.write("Aligning-Moment=%.3f\n"%((Moment[0]+Moment[1])/2.0) )
    f.write("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!\n")
    
    f.close()
    # print("!! Done Cornering stiffness post-processing")


        


    

    





        



