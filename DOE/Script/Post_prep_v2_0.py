"""****************************************************************************
     This is a Python script that cretes DOE file and run marix (ISLM).

     {1} doeroot - root name for DOE analysis
        
***************************************************************************************"""

import sys, os, glob, json
from types import SimpleNamespace
try:
    import CheckExecution
except:
    pass
################################################################################

class doeDV(list):
    def new(self,name=None,value=None,min_val=None,nom_val=None,max_val=None):
        self.append(SimpleNamespace(**{'name':name,'value':doeDV_Value(),'min_val':min_val,'nom_val':nom_val,'max_val':max_val}))

class doeDV_Value(list):
    def new(self,value=None):
        self.append(value)

class doeResp(list):
    def new(self,name=None,value=None):
        self.append(SimpleNamespace(**{'name':name,'value':doeResp_Value()}))

class doeResp_Value(list):
    def new(self,value=None):
        self.append(value)

#################################################################################
try:
    CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
except:
    pass
# Command line arguments
# doeroot = sys.argv[1]
workingdir = os.getcwd()
doename = glob.glob(workingdir+"/*.in")
doeroot = doename[0].split("/")[-1][:-3]

os.system("rm *.doe >/dev/null 2>&1")
os.system("rm *.xlsx >/dev/null 2>&1")
os.system("rm *.out >/dev/null 2>&1")
os.system("rm *.dat >/dev/null 2>&1")

############################################################################
I=len(os.listdir(workingdir))
for i in range(I):
    if os.listdir(workingdir)[i][-2:] == "-0":
        vtname = os.listdir(workingdir)[i]

with open(workingdir + "/" + vtname + "/" + vtname+".tsl") as tsl:
    lines = tsl.readlines()

for line in lines:
    dat = line.split("	") 
    if dat[0] == 'Y':
        sims = dat[1]
        break
snsroot = workingdir + "/" + vtname + "/" + sims +"/" + sims+ ".sns"

with open(snsroot) as JSON:
    json = json.load(JSON)

TreadWidth_0 = float(json["VirtualTireParameters"]["TreadDesignWidth"])
## Tread Width Information
############################################################################


# Files
dvfile = doeroot+'.in'
respfile = doeroot+'.ppr'
doefile = doeroot+'.doe'
runfile = doeroot+'_matrix.dat'
nomfile = 'nom.results'

# Get design variables
fi = open(dvfile, 'r')
lines = fi.readlines()
fi.close()

nlines = len(lines)
nrun = 0
datline = []
nomdv = []

dv = doeDV()
k = 0
while k <= nlines-1:
    line = lines[k].strip().replace(',','').split()
    line = line[1:]
    if len(line) != 0:
        nrun = nrun + 1
        datline.append(line)
        k = k + 1
    else:
        break
ndv = len(datline[0])
nrun = nrun - 1

for i in range(ndv):
    datline[0][i] = datline[0][i].replace('-', '_')
    datline[0][i] = datline[0][i].replace('TDEP0', '   GD')
    datline[0][i] = datline[0][i].replace('   SHL', 'SH_Low')
    datline[0][i] = datline[0][i].replace('   SR', 'Sho_R')
    datline[0][i] = datline[0][i].replace('  TBP1', 'TD_BP1')
    datline[0][i] = datline[0][i].replace('  TBP2', 'TD_BP2')
    datline[0][i] = datline[0][i].replace('    DR1', 'Deck_R1')
    datline[0][i] = datline[0][i].replace('    DR2', 'Deck_R2')
    datline[0][i] = datline[0][i].replace('    DR3', 'Deck_R3')
    datline[0][i] = datline[0][i].replace('   DRBP1', 'Deck_BP1')
    datline[0][i] = datline[0][i].replace('   DRBP2', 'Deck_BP2')
    datline[0][i] = datline[0][i].replace('     GBA', 'BT_Angle')
    datline[0][i] = datline[0][i].replace('     CBW', 'BT_Width')
    datline[0][i] = datline[0][i].replace('   BFH', 'FIL_Ht')
    datline[0][i] = datline[0][i].replace('  CTUH1', 'Cc_TUH1')
    datline[0][i] = datline[0][i].replace('  CTUH2', 'Cc_TUH2')
    datline[0][i] = datline[0][i].replace('    CTB', 'CTB_Mod')
    datline[0][i] = datline[0][i].replace('     BF', 'Fil_Mod')
    datline[0][i] = datline[0][i].replace('  GBANG', 'Main BT_Angle')
    datline[0][i] = datline[0][i].replace(' SGBANG', '1BT_Angle')
    dv.new(name = datline[0][i])
    for k in range(nrun):
        dv[i].value.new(datline[k+1][i])

# Get responses
fi = open(respfile, 'r')
lines = fi.readlines()
fi.close()

nlines = len(lines)
nrun = 0
datline = []
nomresp = []

resp = doeResp()
k = 0
while k <= nlines-1:
    line = lines[k].strip().replace(',','').split()
    line = line[1:]
    if len(line) != 0:
        nrun = nrun + 1
        datline.append(line)
        k = k + 1
    else:
        break
nresp = len(datline[0])
nrun = nrun - 1

for i in range(nresp):
    datline[0][i] = datline[0][i].replace('-', '_')
    resp.new(name = datline[0][i])
    nomresp.append(datline[1][i])
    for k in range(nrun):
        resp[i].value.new(datline[k+1][i])

# Write run matrix
s0 = 13
s1 = 15
sa = 4
s = []
datlines = []

datline = []
datline.append('%eval_id')
for i in range(ndv):
    if len(dv[i].name) > s1:
        s.append(len(dv[i].name)+sa)
    else:
        s.append(s1+sa)
    datline.append(dv[i].name)
for i in range(nresp):
    if len(resp[i].name) > s1:
        s.append(len(resp[i].name)+sa)
    else:
        s.append(s1+sa)
    datline.append(resp[i].name)
datlines.append(datline)
for k in range(nrun):
    datline = []
    datline.append(k)
    for i in range(ndv):
        datline.append(dv[i].value[k])
    for i in range(nresp):
        datline.append(resp[i].value[k])
    datlines.append(datline)

fo = open(runfile, 'w')
twposition=-1
firsttw = 0 
for k in range(len(datlines)):
    # print (k, datlines[k])
    pline = ''
    if k == 0:
        for i in range (len(datlines[k])):
            if i == 0:
                pline = pline + datlines[k][i].ljust(s0)
                if 'TW' in datlines[k][i].ljust(s0) : twposition = i
                # te = datlines[k][i].ljust(s0)
            else:
                pline = pline + datlines[k][i].ljust(s[i-1])
                if 'TW' in datlines[k][i].ljust(s0) : twposition = i
                # te =  datlines[k][i].ljust(s[i-1])
    else:
        for i in range (len(datlines[k])):
            if i == 0:
                pline = pline + str(datlines[k][i]).strip()[0:11].ljust(s0)
            else:
                # pline = pline + str(format(float(datlines[k][i]),'12.12f')).strip()[0:11].ljust(s[i-1])
                if twposition > 0 and i == twposition: 
                    if firsttw ==0: firsttw = float(datlines[k][i])
                    if firsttw > 0: 
                        line = str(format(TreadWidth_0* float(datlines[k][i])/firsttw,'12.12f')).strip()[0:11].ljust(s[i-1])
                        pline = pline + line
                else:
                    pline = pline + str(format(float(datlines[k][i]),'12.12f')).strip()[0:11].ljust(s[i-1])
            
            # if i == twposition: print (k, i, line, TreadWidth_0)
    pline = pline + '\n'
    fo.write(pline)
fo.close()

# print ("TW Positin", twposition)

# write dummy .doe file
fo = open(doefile, 'w')

fo.write('DOE TOOL VERSION 5.1 \n')
fo.write('/ \n')
fo.write('1 \n')
fo.write('/ \n')
fo.write(str(ndv)+'                ! number of design variables \n')
for i in range(ndv):
    dv_val = [float(x) for x in dv[i].value]
    if twposition > 0 and "TW" in dv[i].name.strip():
        fo.write(dv[i].name.strip()+', '+dv[i].name.strip()+', '+str(TreadWidth_0*float(dv[i].value[0])/firsttw)+', '+str(TreadWidth_0*min(dv_val)/firsttw)+', '+str(TreadWidth_0*max(dv_val)/firsttw)+'\n')
    else:
        fo.write(dv[i].name.strip()+', '+dv[i].name.strip()+', '+str(float(dv[i].value[0]))+', '+str(min(dv_val))+', '+str(max(dv_val))+'\n')
fo.write('0 \n')
fo.write('0 \n')
fo.write('0                ! DOE Type (0 - Screening, 1 - Response Surface) \n')
fo.write(str(nrun-1).ljust(17) + '! number of runs \n')
fo.write('! user-selected responses \n')
fo.write('1,1,' + str(nresp).ljust(13) + '! m3d file, number of loads, number of responses \n')
for i in range(nresp):
    fo.write('kv:kv \"\" \n')
fo.write('#OPTIMIZATION \n')
fo.write('! objective function (-2=min, -1=max : 0 < weighting factor <= 1 : response) \n')
fo.write('! response constraints (0=EU, 1=%Nominal : lower limit: upper limit : response) \n')
fo.write('! DV constraints (lower limit : upper limit : DV) \n')

fo.close()

print ("Pre-DOE analysis DONE !!")
try:
    CheckExecution.getProgramTime(str(sys.argv[0]), "End")
except:
    pass

exit()




