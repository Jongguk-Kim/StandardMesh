import matplotlib
matplotlib.use('Agg')
import os, glob, json, sys
import matplotlib.pyplot as plt
import math, time
try:
    import CommonFunction as TIRE
except:
    import CommonFunction_v2_0 as TIRE
import multiprocessing as mp
try:
    import CheckExecution
except: 
    pass 

def plotribshape(Imagenamebase, lastSDBFile, lastSFRIC, group='PCR', mesh2d='', iter=1, step=0, condition='', offset=10000, treadno=10000000, dpi=100, ribimage=0, vmin='', doe=0, fitting=6, ribgraph=0):
    TIRE.PlotFootprint(Imagenamebase, lastSDBFile, lastSFRIC, group=group, mesh2d= mesh2d, iter=iter, step =step, condition=condition, offset=offset, treadno=treadno, dpi=dpi, ribimage=ribimage, vmin=vmin, doe=doe, fitting=fitting, ribgraph=ribgraph)

if __name__ == '__main__':
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass 
    T_start = time.time()

    strJobDir = os.getcwd()
    lstSmartFileNames = glob.glob(strJobDir + '/*.sns')
    strSmartFileName = lstSmartFileNames[0]
    with open(strSmartFileName) as SNS:
        lstSnsInfo = json.load(SNS)

    strSimCode = lstSnsInfo["AnalysisInformation"]["SimulationCode"]  # RND-3000000VT00001-0-D105-0001
    strSimCode = strSmartFileName.split('/')[-1][:-4]  # Simulation Code from 'SNS' file name
    strSimGroup = strSimCode.split('-')[-2]  # D105
    strProductLine = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]  # TBR
    lstSimConditions = lstSnsInfo["AnalysisInformation"]["AnalysisCondition"]  # Pressure, Load, etc


    #################################################
    # Define Sub Folder & File Definition
    #################################################
    SubFolderBasicName = 'FM'
    SubFolderSerialDigit = '03'
    SubFileBasicName = '-FM'
    SubFileSerialDigit = '03'
    #################################################

    TotalSimNo = 10
    Offset = 10000
    TreadNo = 10000000
    doe = 0

    i=1
    Serial = str(format(i, SubFolderSerialDigit))
    subFolderName = SubFolderBasicName + Serial
    Serial = str(format(i, SubFileSerialDigit))
    subFileName = strSimCode + SubFileBasicName + Serial
    SmartInpFileName = subFolderName + '/' + subFileName + '.inp'
    str2DInp = strSimCode.split("-")[1]+"-"+strSimCode.split("-")[2]+".inp"
    
    SimTime = TIRE.SIMTIME(SmartInpFileName)
    strResultStep = str(format(SimTime.LastStep, '03'))
     
    CF = [0.0, 0.0, 0.0, 0.0, 0.0]
    AF = [0.0, 0.0, 0.0, 0.0, 0.0]
    Load=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    processes = []
    for i in range(1, TotalSimNo + 1):
        lastSDBFile = './'+ SubFolderBasicName + str(format(i, SubFolderSerialDigit)) + '/SDB.' + strSimCode + '-' + SubFolderBasicName + str(format(i, SubFileSerialDigit)) + '/' + strSimCode + SubFileBasicName + str(format(i, SubFileSerialDigit)) + '.sdb' + strResultStep
        lastSFRIC   = './'+ SubFolderBasicName + str(format(i, SubFolderSerialDigit)) + '/SFRIC.' + strSimCode + '-' + SubFolderBasicName + str(format(i, SubFileSerialDigit)) + '/' + strSimCode + SubFileBasicName + str(format(i, SubFileSerialDigit)) + '.sfric' + strResultStep
        if os.path.isfile(lastSDBFile) != True:
            print (lastSDBFile, os.path.isfile(lastSDBFile))
            sys.exit()
            
        if i%2 == 1:
            rptFileName ='./'+  SubFolderBasicName + str(format(i, SubFolderSerialDigit)) + '/REPORT/frc_' + strSimCode + SubFileBasicName + str(format(i, SubFileSerialDigit)) + '.rpt'
            S1=TIRE.RIMFORCE(rptFileName)
            inpFileName = './' + SubFolderBasicName + str(format(i, SubFolderSerialDigit)) + '/' + strSimCode + SubFileBasicName + str(format(i, SubFileSerialDigit)) + '.inp'
            C1=TIRE.CONDITION(inpFileName)
            
            S1FY = S1.FY
            S1MZ = S1.MZ
            C1Angle = C1.LateralValue
            Load[i-1] = C1.Load

            fittingorder = 6
            Imagenamebase = strSimCode + SubFileBasicName + str(format(i, SubFileSerialDigit))
            p = mp.Process(target=plotribshape, args=[Imagenamebase, lastSDBFile, lastSFRIC, strProductLine, str2DInp, 1, 0, C1, Offset, TreadNo, 100, 0, '', doe, fittingorder, 0])
            processes.append(p)
            p.start()
            # TIRE.PlotFootprint(Imagenamebase, lastSDBFile, lastSFRIC, group=strProductLine,\
            #      mesh2d= str2DInp, iter=1, step =0, condition=C1, offset=Offset, treadno=TreadNo, dpi=100, ribimage=0, vmin='', doe=doe, fitting=fittingorder, ribgraph=0)
            
        else:
            rptFileName ='./'+  SubFolderBasicName + str(format(i, SubFolderSerialDigit)) + '/REPORT/frc_' + strSimCode + SubFileBasicName + str(format(i, SubFileSerialDigit)) + '.rpt'
            S2=TIRE.RIMFORCE(rptFileName)
            inpFileName = './' + SubFolderBasicName + str(format(i, SubFolderSerialDigit)) + '/' + strSimCode + SubFileBasicName + str(format(i, SubFileSerialDigit)) + '.inp'
            C2=TIRE.CONDITION(inpFileName)
        
            CF[i/2-1] = abs(S2.FY - S1FY) / abs(C2.LateralValue - C1Angle)
            AF[i/2-1] = abs(S2.MZ - S1MZ) / abs(C2.LateralValue - C1Angle)
            Load[i-1] = C2.Load
        
    for process in processes:
        process.join()
    
    
    ###################################################################
    ## FILE WRITING
    ResultFileName = strSimCode + '-ForceMomentValue.txt'
    f = open(ResultFileName, 'w')

    text = 'Load = ' + str(format(Load[0], '.1f')) + '/' + str(format(Load[2], '.1f'))+ '/' + str(format(Load[4], '.1f'))+ '/' + str(format(Load[6], '.1f'))+ '/' + str(format(Load[8], '.1f')) + '\n'
    f.write(text)
    text = 'Ca   = ' + str(format(CF[0] / 9.8, '.2f')) + '/' + str(format(CF[1] / 9.8, '.2f'))+ '/' + str(format(CF[2] / 9.8, '.2f'))+ '/' + str(format(CF[3] / 9.8, '.2f'))+ '/' + str(format(CF[4] / 9.8, '.2f'))+ '\n'
    f.write(text)
    text = 'Aa   = ' + str(format(AF[0] / 9.8, '.2f')) + '/' + str(format(AF[1] / 9.8, '.2f'))+ '/' + str(format(AF[2] / 9.8, '.2f'))+ '/' + str(format(AF[3] / 9.8, '.2f'))+ '/' + str(format(AF[4] / 9.8, '.2f'))+ '\n'
    f.write(text)

    if CF[0] !=0:
        counting = 1
    else:
        counting = 0

    if counting == 0:
        text = '\nERROR::POST::[FORCE MOMENT] - No Result for Cornrering Stiffness Calculation!\n'
        f.write(text)
        print (text)

    else:
        text = '\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!'
        f.write(text)
        print (text)

    f.close()
    ####################################################################

    fig, ax = plt.subplots()

    max=0

    for i in range(int(TotalSimNo / 2)):
        plt.plot(Load[2 * i], CF[i] / 9.8, 'ro')
        if CF[i] / 9.8 > max:
            max = CF[i] / 9.8

    plt.xlabel('Load [kgf]')
    plt.ylabel('Ca [kgf/deg]')
    plt.xlim(0, Load[9]*1.1)
    plt.ylim(0, max * 1.2)
    ImageFileName = strSimCode + '-CorneringStiffness.png'
    plt.savefig(ImageFileName, dpi=300)

    T_end = time.time()
    print ('Duration', round(T_end - T_start, 2), 'sec')

    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass 