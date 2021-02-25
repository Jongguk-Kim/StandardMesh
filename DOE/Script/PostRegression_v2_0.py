"""******************************************************************
     This is a Python script used in DOE/Optimization postprocessing.
     It creates regression analysis from the run matrix.

     {1} doeroot  - root name for DOE analysis

***************************************************************************************"""

import sys, os, glob, json
import xlsxwriter
from PIL import Image
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import pandas as pd
from DOE.DoeFile import DoeFile
from DOE.DoeResponses import respCategories, valid_xml_files, steps, respKeys
from types import SimpleNamespace
try:
    import CheckExecution
except:
    pass
###########################################################################################

class doeDV(list):
    def new(self,name=None,value=None,min_val=None,nom_val=None,max_val=None):
        self.append(SimpleNamespace(**{'name':name,'value':doeDV_Value(),'min_val':min_val,'nom_val':nom_val,'max_val':max_val}))

class doeDV_Value(list):
    def new(self,value=None):
        self.append(value)

class doeResp(list):
    def new(self,name=None,value=None):
        self.append(SimpleNamespace(**{'name':name,'value':doeResp_Value(),'surf_fit':doeSurfFit()}))

class doeResp_Value(list):
    def new(self,value=None):
        self.append(value)

class doeSurfFit(list):
    def new(self,order=None,rsquared=None,fvalue=None):
        self.append(SimpleNamespace(**{'order':order,'coeff_name':doeCoeff_Name(),'coeff_value':doeCoeff_Value(),'coeff_pvalue':doeCoeff_Pvalue(),'rsquared':rsquared,'fvalue':fvalue}))

class doeCoeff_Name(list):
    def new(self,name=None):
        self.append(name)

class doeCoeff_Value(list):
    def new(self,value=None):
        self.append(value)

class doeCoeff_Pvalue(list):
    def new(self,value=None):
        self.append(value)


def calc_reg(order,x_val,coeff_val):
    x = []
    x.append(1)
    x_lab = []
    c = coeff_val
    n = len(x_val)
    nc = len(coeff_val)
    if order == 1:
        for i in range(n):
            x.append(x_val[i])
    if order == 2:
        for i in range(n):
            x.append(x_val[i])
            for j in range(i,n):
                x.append(x_val[i]*x_val[j])
    z = 0
    for i in range(nc):
        z = z + c[i] * x[i]

    return x,z

###################################################################################
try:
    CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
except:
    pass

# Command line arguments
# doeroot = sys.argv[1]
doe_type = 0
pwd = os.getcwd()
pprs = glob.glob(pwd+"/DOE*.ppr")
## doeroot : directory name 
doeroot = pprs[0].split("/")[-1][:-4]

doeids = glob.glob(pwd+"/*.in") 
doeid = doeids[0].split("/")[-1][:-3]
###############################################################
print (doeroot)

# Reading the DOE answer file
DOE = DoeFile(doeroot + '.doe')
MV, CV, MATV, userRespList, ObjFun, ReConstr, DVConstr, doetype, nruns = DOE.read()
m3d   = len(DOE.m3droot)		# num of m3d files
nmv   = len(MV)				# tot num of mold design variables
ncv   = len(CV)			        # tot num of construction design variables
nmatv = len(MATV)		        # tot num of material design variables
ndv   = nmv + ncv + nmatv		# tot num of design variables
nresp = 0
for key in userRespList.keys():
    nresp += len(userRespList[key])	# tot num of responses

# Read run matrix
runfile = doeroot+'_matrix.dat'
run_matrix = pd.read_csv(runfile,sep = "\s+",engine='python')
run_matrix = run_matrix.rename(columns=lambda x: x.strip())
nrun = len(run_matrix)
xname = []
for i in range(ndv):
    xname.append(run_matrix.columns[i+1])
yname = []
for i in range(nresp):
    yname.append(run_matrix.columns[ndv+i+1])

# Open regression results file
outname = doeroot+'_regression.out'
outfile = open(outname, 'w')
outfile.write('Regression Output \n')
outfile.write('\n')


# Linear polynomial
coeff1 = []
pval1 = []
rsquared1 = []
fvalue1 = []
ofile1 = open('dakota_sbgo_1.out', 'w')
ofile1.write('Dakota Output - sbgo_1\n')
ofile1.write('\n')
ofile1.write('Design variables:'+'  '.join(xname)+'\n')
ofile1.write('\n')
ofile1.write('Response variables:'+'  '.join(yname)+'\n')
ofile1.write('\n')
for k in range(nresp):
    outfile.write('\n')
    outfile.write('******************************************************************************\n')
    outfile.write('\n')
    outfile.write(' Linear Fit - ' + yname[k] + '\n')
    outfile.write('\n')
    eq_str = yname[k] + ' ~ 1 '
    for i in range(ndv):
        eq_str = eq_str + ' + ' + xname[i]
    poly_1 = smf.ols(formula=eq_str, data=run_matrix).fit()
    outfile.write(str(poly_1.summary()))
    ofile1.write('#Response '+str(k+1)+':  '+yname[k]+'\n')
    ofile1.write('Unity \n')
    for i in range(ndv):
        ofile1.write(str(i)+'\n')
    coeff = ''
    c1 = []
    p1 = []
    for i in range(len(poly_1.params.values)):
        c1.append(poly_1.params.values[i])
        p1.append(poly_1.pvalues[i])
        coeff = coeff + '  ' + str(poly_1.params.values[i])
    coeff1.append(c1)
    pval1.append(p1)
    ofile1.write('coeffs: '+coeff+'\n')
    sum_squared = poly_1.ssr
    max_abs = poly_1.resid.abs().max()
    rsquared = poly_1.rsquared
    rsquared1.append(rsquared)
    fvalue = poly_1.fvalue
    fvalue1.append(fvalue)
    root_mean_squared = np.sqrt(poly_1.ssr/poly_1.nobs)
    mean_abs = poly_1.resid.abs().mean()
    ofile1.write('Surrogate quality metrics \n')
    ofile1.write('         sum_squared    '+str(sum_squared)+'\n')
    ofile1.write('             max_abs    '+str(max_abs)+'\n')
    ofile1.write('            rsquared    '+str(rsquared)+'\n')
    ofile1.write('   root_mean_squared    '+str(root_mean_squared)+'\n')
    ofile1.write('            mean_abs    '+str(mean_abs)+'\n')
    ofile1.write('\n')
ofile1.write('Partial Rank Correlation Matrix between input and output:\n')
ofile1.write('             '+'  '.join(yname)+'\n')
mstr = ''
for i in range(nresp):
    mstr = mstr + '        1.0'
for i in range(ndv):
    ofile1.write('         '+xname[i]+mstr+'\n') 
ofile1.write('\n')
ofile1.close()

# Quadratic polynomial
coeff2 = []
pval2 = []
rsquared2 = []
fvalue2 = []
ofile2 = open('dakota_sbgo_2.out', 'w')
ofile2.write('Dakota Output - sbgo_2\n')
ofile2.write('\n')
ofile2.write('Design variables:  '+'  '.join(xname)+'\n')
ofile2.write('\n')
ofile2.write('Response variables:  '+'  '.join(yname)+'\n')
ofile2.write('\n')
for k in range(nresp):
    outfile.write('\n')
    outfile.write('******************************************************************************\n')
    outfile.write('\n')
    outfile.write(' Quadratic Fit - ' + yname[k] + '\n')
    outfile.write('\n')
    eq_str = yname[k] + ' ~ 1 '
    for i in range(ndv):
        eq_str = eq_str + ' + ' + xname[i]
        for j in range(i,ndv):
            eq_str = eq_str + ' + I(' + xname[i] + ' * ' + xname[j] + ')'
    poly_2 = smf.ols(formula=eq_str, data=run_matrix).fit()
    outfile.write(str(poly_2.summary()))
    ofile2.write('#Response '+str(k+1)+':  '+yname[k]+'\n')
    ofile2.write('Unity \n')
    for i in range(ndv):
        ofile2.write(str(i)+'\n')
        for j in range(i,ndv):
            ofile2.write(str(i) + ' '+str(j)+'\n')
    coeff = ''
    c2 = []
    p2 = []
    for i in range(len(poly_2.params.values)):
        c2.append(poly_2.params.values[i])
        p2.append(poly_2.pvalues[i])
        coeff = coeff + '  ' + str(poly_2.params.values[i])
    coeff2.append(c2)
    pval2.append(p2)
    ofile2.write('coeffs: '+coeff+'\n')
    sum_squared = poly_2.ssr
    max_abs = poly_2.resid.abs().max()
    rsquared = poly_2.rsquared
    rsquared2.append(rsquared)
    fvalue = poly_2.fvalue
    fvalue2.append(fvalue)
    root_mean_squared = np.sqrt(poly_2.ssr/poly_2.nobs)
    mean_abs = poly_2.resid.abs().mean()
    ofile2.write('Surrogate quality metrics \n')
    ofile2.write('         sum_squared    '+str(sum_squared)+'\n')
    ofile2.write('             max_abs    '+str(max_abs)+'\n')
    ofile2.write('            rsquared    '+str(rsquared)+'\n')
    ofile2.write('   root_mean_squared    '+str(root_mean_squared)+'\n')
    ofile2.write('            mean_abs    '+str(mean_abs)+'\n')
    ofile2.write('\n')
ofile2.write('Partial Rank Correlation Matrix between input and output:\n')
ofile2.write('             '+'  '.join(yname)+'\n')
mstr = ''
for i in range(nresp):
    mstr = mstr + '        1.0'
for i in range(ndv):
    ofile2.write('         '+xname[i]+mstr+'\n') 
ofile2.write('\n')
ofile2.close()

outfile.close()


# Write Excel file
coeffs = []
coeffs.append(coeff1)
coeffs.append(coeff2)
pvals = []
pvals.append(pval1)
pvals.append(pval2)
rsquared = []
rsquared.append(rsquared1)
rsquared.append(rsquared2)
fvalue = []
fvalue.append(fvalue1)
fvalue.append(fvalue2)
nc = []
nc.append(int(ndv + 1))
nc.append(int((ndv*ndv + 3*ndv  + 2)/2))

dv = doeDV()
for i in range(ndv):
    dv.new(name = xname[i])
    for j in range (len(MV)):
        if(MV[j].abbrev.strip() == xname[i].strip()):
            dv[i].min_val = MV[j].vmin
            dv[i].nom_val = MV[j].vnom
            dv[i].max_val = MV[j].vmax
    for j in range (len(CV)):
        if(CV[j].abbrev.strip() == xname[i].strip()):
            dv[i].min_val = CV[j].vmin
            dv[i].nom_val = CV[j].vnom
            dv[i].max_val = CV[j].vmax
    for j in range (len(MATV)):
        if(MATV[j].abbrev.strip() == xname[i].strip()):
            dv[i].min_val = MATV[j].vmin
            dv[i].nom_val = MATV[j].vnom
            dv[i].max_val = MATV[j].vmax
    for j in range(nrun):
        dv[i].value.new(run_matrix.iloc[j,i+1])    

resp = doeResp()
for i in range(nresp):
    resp.new(name = yname[i])
    for j in range(nrun):
        resp[i].value.new(run_matrix.iloc[j,i+1+ndv]) 
    for j in range(2):
        resp[i].surf_fit.new(order=j+1)
        resp[i].surf_fit[j].rsquared = rsquared[j][i]
        resp[i].surf_fit[j].fvalue = fvalue[j][i]
        for k in range(len(coeffs[j][i])):
            resp[i].surf_fit[j].coeff_value.new(coeffs[j][i][k]) 
            resp[i].surf_fit[j].coeff_pvalue.new(pvals[j][i][k])
        resp[i].surf_fit[j].coeff_name.new('Intercept')
        for k in range(ndv):
            resp[i].surf_fit[j].coeff_name.new(dv[k].name)
            if j == 1:
                for kk in range(k,ndv):
                    resp[i].surf_fit[j].coeff_name.new(dv[k].name+'*'+dv[kk].name)


# Create workbook
wb = xlsxwriter.Workbook(doeroot+'-Summary.xlsx')
blank = []
for i in range(1000):
    blank.append('')

# Create formats
format_bold = wb.add_format({'bold': 1})
format_blank = wb.add_format({
    'bg_color': 'white',
})
format_title = wb.add_format({
    'bg_color': '#8181FF',
    'font_size': 11,
    'num_format': '0',
    'bold': True,
    'font_color': 'black',
})
format_intro = wb.add_format({
    'bg_color': '#CCCCFF',
    'font_size': 11,
    'num_format': '0',
    'bold': False,
    'font_color': 'black',
})
format_header = wb.add_format({
    'font_name': 'Calibri',
    'font_size': 11,
    'num_format': '0',
    'bold': True,
    'font_color': 'black',
    'align': 'center',
    'underline': False,
    'bg_color': '#CCCCFF',
    'bottom': 1,
})
format_header_blank = wb.add_format({
    'font_name': 'Calibri',
    'font_size': 11,
    'num_format': '0',
    'bold': True,
    'font_color': 'black',
    'align': 'center',
    'underline': False,
    'bg_color': '#CCCCFF',
})
format_header_right = wb.add_format({
    'font_name': 'Calibri',
    'font_size': 11,
    'num_format': '0',
    'bold': True,
    'font_color': 'black',
    'align': 'center',
    'underline': False,
    'bg_color': '#CCCCFF',
    'right': 1,
    'bottom': 1,
})
format_header_2 = wb.add_format({
    'font_name': 'Calibri',
    'font_size': 11,
    'num_format': '0',
    'bold': True,
    'font_color': 'black',
    'align': 'center',
    'underline': False,
    'bg_color': '#ABABFF',
    'bottom': 1,
})
format_header_3 = wb.add_format({
    'font_name': 'Calibri',
    'font_size': 11,
    'num_format': '0',
    'bold': True,
    'font_color': 'black',
    'align': 'center',
    'underline': False,
    'bg_color': '#8181FF',
    'bottom': 1,
})
format_label = wb.add_format({
    'font_name': 'Ariel',
    'font_size': 10,
    'num_format': '0',
    'bold': False,
    'font_color': 'black',
    'align': 'center',
    'underline': False,
    'bg_color': False,
})
format_real = wb.add_format({
    'font_name': 'Ariel',
    'font_size': 10,
    'num_format': '0.0000',
    'bold': False,
    'font_color': 'black',
    'align': 'right',
    'underline': False,
    'bg_color': False,
})
format_real_blank = wb.add_format({
    'font_name': 'Ariel',
    'font_size': 10,
    'num_format': '0.0000',
    'bold': False,
    'font_color': 'white',
    'align': 'right',
    'underline': False,
    'bg_color': 'white',
})
format_real_right = wb.add_format({
    'font_name': 'Ariel',
    'font_size': 10,
    'num_format': '0.0000',
    'bold': False,
    'font_color': 'black',
    'align': 'right',
    'underline': False,
    'bg_color': False,
    'right': 1,
})
format_input_real_right = wb.add_format({
    'font_name': 'Ariel',
    'font_size': 10,
    'num_format': '0.0000',
    'bold': False,
    'font_color': 'blue',
    'align': 'right',
    'underline': False,
    'bg_color': False,
    'right': 1,
})
format_integer = wb.add_format({
    'font_name': 'Ariel',
    'font_size': 10,
    'num_format': '0',
    'bold': False,
    'font_color': 'black',
    'align': 'right',
    'underline': False,
    'bg_color': False,
})
format_top = wb.add_format({
    'top': 1,
    'bg_color': 'white',
})
format_bottom = wb.add_format({
    'bottom': 1,
    'bg_color': 'white',
})
format_left = wb.add_format({
    'left': 1,
    'bg_color': 'white',
})
format_right = wb.add_format({
    'right': 1,
    'bg_color': 'white',
})
format_textgray = wb.add_format({
    'font_color': 'gray',
})
format_textblue = wb.add_format({
    'font_color': 'blue',
})
format_top = wb.add_format({
    'top': 1,
    'bg_color': 'white',
})
format_bottom = wb.add_format({
    'bottom': 1,
    'bg_color': 'white',
})
format_left = wb.add_format({
    'left': 1,
    'bg_color': 'white',
})
format_right = wb.add_format({
    'right': 1,
    'bg_color': 'white',
})
# Create worksheets
ws1 = wb.add_worksheet('Run Log')
ws2 = wb.add_worksheet('Regression')
ws3 = wb.add_worksheet('Linear Data')
ws4 = wb.add_worksheet('Quadratic Data')
ws5 = wb.add_worksheet('Calculator')
ws6 = wb.add_worksheet('Effects Data')
ws7 = wb.add_worksheet('Main Effects - Linear')
ws8 = wb.add_worksheet('Main Effects - Quadratic')
ws9 = wb.add_worksheet('Interaction Effects - Quadratic')

# Write run log
title_ws1 = 'Run Log'
ws1.set_column(0, 0, 12,format_blank)
# ws1.set_column(1, 1000, 30,format_blank)
ws1.set_row(0,15,format_intro)
ws1.set_row(1,15,format_intro)
ws1.set_row(2,15,format_intro)
ws1.set_row(3,15,format_intro)
ws1.set_row(4,15,format_intro)
ws1.set_row(5,15,format_intro)
ws1.set_row(6,15,format_intro)
ws1.write(0,0,title_ws1,format_title)
ws1.write(2,0,' - Summary of the Design Variables and Responses (Simulation Results)',format_intro)

ws1.write(9,1,'Run #',format_header_3)
for j in range(ndv):
    if dv[j].name == "BWID": dv[j].name = "BT_Half_Width"
    if dv[j].name == "TUPHT1": dv[j].name = "CC_TUH1"
    if dv[j].name == "TUPHT2": dv[j].name = "CC_TUH2"
    if dv[j].name == "SHL": dv[j].name = "SH_Low(%)"
    if dv[j].name == "GBANG": dv[j].name = "Main_BT_Angle"
    if dv[j].name == "SGBANG": dv[j].name = "1BT_Angle"
    if dv[j].name == "BFH": dv[j].name = "Filler_Ht"
    if dv[j].name == "MATCTB": dv[j].name = "CTB_Modulus(%)"
    if dv[j].name == "MATFIL": dv[j].name = "FIL_Modulus(%)"
    if dv[j].name == "MATBSW": dv[j].name = "BSW_Modulus(%)"
    if dv[j].name == "TBP1": dv[j].name = "TR1_BreakPoint"
    if dv[j].name == "TBP2": dv[j].name = "TR2_BreakPoint"
    if dv[j].name == "TBP3": dv[j].name = "TR3_BreakPoint"
    ws1.write(9,j+2,dv[j].name,format_header_2)
    textlength = len(dv[j].name)
    if textlength <= 4: ws1.set_column(j+2, j+2, 7,format_blank)
    elif textlength == 5: ws1.set_column(j+2, j+2, 8,format_blank)
    elif textlength < 8: ws1.set_column(j+2, j+2, 9,format_blank)
    elif textlength < 9: ws1.set_column(j+2, j+2, 11,format_blank)
    elif textlength < 10: ws1.set_column(j+2, j+2, 13,format_blank)
    elif textlength < 11: ws1.set_column(j+2, j+2, 14,format_blank)
    elif textlength < 12: ws1.set_column(j+2, j+2, 15,format_blank)
    elif textlength < 13: ws1.set_column(j+2, j+2, 16,format_blank)
    elif textlength < 14: ws1.set_column(j+2, j+2, 17,format_blank)
    elif textlength < 16: ws1.set_column(j+2, j+2, 19,format_blank)
    elif textlength < 18: ws1.set_column(j+2, j+2, 20,format_blank)
    elif textlength < 20: ws1.set_column(j+2, j+2, 21,format_blank)
    else: ws1.set_column(j+2, j+2, 25,format_blank)

for i in range(nrun):
    if i == 0:
        ws1.write(10,0,'',format_right)
        ws1.write(10,1,'nominal',format_label)
    else:
        ws1.write(i+10,0,'',format_right)
        ws1.write(i+10,1,i,format_label)
    for j in range(ndv):
        ws1.write(i+10,j+2,dv[j].value[i],format_real)

for j in range(nresp):
    if resp[j].name == "DF_Eloss_Total": resp[j].name = "DF_RR_Force_Total"
    if resp[j].name == "DF_Eloss_Crown": resp[j].name = "DF_RR_Force_Crown"
    if resp[j].name == "DF_Eloss_Filler": resp[j].name = "DF_RR_Force_Filler"
    if resp[j].name == "DF_Eloss_BSW": resp[j].name = "DF_RR_Force_BSW"

    if resp[j].name == "RR_Eloss_Total": resp[j].name = "RR_Force_Total"
    if resp[j].name == "RR_Eloss_Crown": resp[j].name = "RR_Force_Crown"
    if resp[j].name == "RR_Eloss_Filler": resp[j].name = "RR_Force_Filler"
    if resp[j].name == "RR_Eloss_BSW": resp[j].name = "RR_Force_BSW"
    ws1.write(9,j+2+ndv,resp[j].name,format_header)
    textlength = len(resp[j].name)
    if textlength <= 4: ws1.set_column(j+2+ndv, j+2+ndv, 7,format_blank)
    elif textlength == 5: ws1.set_column(j+2+ndv, j+2+ndv, 8,format_blank)
    elif textlength < 8: ws1.set_column(j+2+ndv, j+2+ndv, 9,format_blank)
    elif textlength < 9: ws1.set_column(j+2+ndv, j+2+ndv, 11,format_blank)
    elif textlength < 10: ws1.set_column(j+2+ndv, j+2+ndv, 13,format_blank)
    elif textlength < 11: ws1.set_column(j+2+ndv, j+2+ndv, 14,format_blank)
    elif textlength < 12: ws1.set_column(j+2+ndv, j+2+ndv, 15,format_blank)
    elif textlength < 13: ws1.set_column(j+2+ndv, j+2+ndv, 16,format_blank)
    elif textlength < 14: ws1.set_column(j+2+ndv, j+2+ndv, 17,format_blank)
    elif textlength < 16: ws1.set_column(j+2+ndv, j+2+ndv, 19,format_blank)
    elif textlength < 18: ws1.set_column(j+2+ndv, j+2+ndv, 20,format_blank)
    elif textlength < 20: ws1.set_column(j+2+ndv, j+2+ndv, 21,format_blank)
    else: ws1.set_column(j+2+ndv, j+2+ndv, 25,format_blank)

for i in range(nrun):
    if i == 0:
        ws1.write(i+10,ndv+nresp+2,'',format_left)   
    ws1.write(i+10,ndv+nresp+2,'',format_left)
    for j in range(nresp):
        ws1.write(i+10,j+2+ndv,resp[j].value[i],format_real)

for j in range(ndv+nresp+1):
    ws1.write(nrun+10,j+1,'',format_top)
 
ws1.freeze_panes(0, 2+ndv) 

# Write regression
title_ws2 = 'Regression Analysis'
ws2.set_column(0, 0, 20,format_blank)
ws2.set_column(1, 1, 30,format_blank)
ws2.set_column(2, 1000, 20,format_blank)  
ws2.set_row(0,15,format_intro)
ws2.set_row(1,15,format_intro)
ws2.set_row(2,15,format_intro)
ws2.set_row(3,15,format_intro)
ws2.set_row(4,15,format_intro)
ws2.set_row(5,15,format_intro)
ws2.set_row(6,15,format_intro)
ws2.write(0,0,title_ws2,format_title)
ws2.write(2,0,' - R-Squared (0.0-1.0): How well a regression line fits the data points (1.0 = perfect correlation)',format_intro)
ws2.write(3,0,' - F-Value = (the mean regression sum of squares) / (the error sum of squares): the overall significance of the regression model',format_intro)
ws2.write(4,0,' - P-Value = the probability of the null hypothesis that coefficient is zero, which can be rejected if the value is less than or equal to a certain value(0.05)',format_intro)
ws2.write(5,0,' - Regression equation (DP1(Design Parameter 1), DP2, .. )= (Intercept) + DP1 * Coefficient_DP1 + DP2 * Coefficient_DP2 + ... ',format_intro)

plot = []
m = 7
mpos = 9
for ii in range (len(nc)):
    m = m + 2
    mpos = mpos + 2
    if ii == 0:
        ws2.write(m,1,'Linear Results',format_header_3)
    if ii == 1:
        ws2.write(m,1,'Quadratic Results',format_header_3)
    for k in range(nresp):
        m = m + 2
        ws2.write(m,1,resp[k].name,format_header_2)
        ws2.write(m,2,'R-Squared',format_header)
        ws2.write(m,3,'F-Value',format_header)
        m = m + 1
        ws2.write(m,1,'',format_right)
        try:
            ws2.write(m,2,resp[k].surf_fit[ii].rsquared,format_real)
            ws2.write(m,3,resp[k].surf_fit[ii].fvalue,format_real)
        except:
            ws2.write(m,2, 'Constant Value',format_real)
            # ws2.write(m,3, resp[k].surf_fit[ii].fvalue,format_real)
        # ws2.write(m,2,resp[k].surf_fit[ii].rsquared,format_real)
        ws2.write(m,4,'',format_left)
        m = m + 1
        ws2.write(m,2,'',format_top)  
        ws2.write(m,3,'',format_top)  
        m = m + 1
        ws2.write(m,2,'Term',format_header)
        ws2.write(m,3,'Coefficient',format_header)
        ws2.write(m,4,'P Value',format_header)

        for i in range(nc[ii]):
            m = m + 1
            ws2.write(m,1,'',format_right)
            ws2.write(m,2,resp[k].surf_fit[ii].coeff_name[i],format_real)
            ws2.write(m,3,resp[k].surf_fit[ii].coeff_value[i],format_real)
            try: 
                ws2.write(m,4,resp[k].surf_fit[ii].coeff_pvalue[i],format_real)
                ws2.write(m,5,'',format_left)
                ws2.write(m,6,1.0-resp[k].surf_fit[ii].coeff_pvalue[i],format_real_blank)
            except: 
                ws2.write(m,4, 1.0,format_real)
                ws2.write(m,5,'',format_left)
                ws2.write(m,6, 0.0,format_real_blank)
            
        for kk in range(3):
            ws2.write(m+1,kk+2,'',format_top)

        plot.append('plot_'+str(i))
        plot[k] = wb.add_chart({
            'type': 'column',
        })
        plot[k].set_size({
            'width': 300*(1+ii),
            'height': 165*(1+0.3*ii),
        })
        plot[k].set_chartarea({
           'border': {'color': 'black',},
        })
        plot[k].add_series({
            'name': resp[k].name,
            'categories': ['Regression',mpos+5,2,mpos+3+nc[ii],2],
            'values': ['Regression',mpos+5,6,mpos+3+nc[ii],6],
            'line': {'width': 2, 'color': 'blue'},
        })
        plot[k].set_legend({
            'position': 'none',
        })
        plot[k].set_title ({
            'name': 'Relative Significance - '+resp[k].name, 
            'name_font': {'name': "Arial", 'size':12, 'color': 'black'},
        })  
        plot[k].set_x_axis({
            'num_format': '#.##',
            'num_font': {'name': "Arial", 'size':9, 'color': 'black'},
            'name_font': {'name': "Arial", 'size':10, 'color': 'black'},
        })  
        plot[k].set_y_axis({
            'num_format': '#.##',
            'num_font': {'name': "Arial", 'size':9, 'color': 'black'},
            'name_font': {'name': "Arial", 'size':10, 'color': 'black'},
            'min': 0,
            'max': 1,
        })  
        plot[k].set_style(11)  
        ws2.insert_chart(mpos,6,plot[k])

        mpos = mpos + 5 +nc[ii]

# Write linear data
title_ws3 = 'Data - Linear'
ws3.set_column(0, 0, 15,format_blank)
ws3.set_column(1, 1000, 30,format_blank) 
ws3.set_row(0,15,format_intro)
ws3.set_row(1,15,format_intro)
ws3.set_row(2,15,format_intro)
ws3.set_row(3,15,format_intro)
ws3.set_row(4,15,format_intro)
ws3.set_row(5,15,format_intro)
ws3.set_row(6,15,format_intro)
ws3.write(0,0,title_ws3,format_title)

ws3.write(9,1,'Parameter',format_header)
ws3.write(9,2,'Value',format_header)
for j in range(nresp):
    ws3.write(9,j+3,resp[j].name,format_header)
ws3.write(10,0,'',format_right)
ws3.write(10,1,'Intercept',format_label)
ws3.write(10,2,'1',format_integer)
ws3.write(10,nresp+3,'',format_left)
m = 0
for i in range(ndv):
    m = m + 1
    ws3.write(m+10,0,'',format_right)
    ws3.write(m+10,1,dv[i].name,format_label)
    ws3.write_formula(m+10,2,'Calculator!f'+str(m+10),format_real)
    ws3.write(m+10,nresp+3,'',format_left)
ws3.write(m+11,0,'',format_right)
ws3.write(m+11,1,'Response',format_label)
ws3.write(m+11,2,'',format_label)
ws3.write(m+12,0,'',format_right)
ws3.write(m+12,1,'R-squared',format_label)
ws3.write(m+12,2,'',format_label)
ws3.write(m+11,nresp+3,'',format_left)
ws3.write(m+12,nresp+3,'',format_left)
for j in range(nresp):
    rf = ''
    for i in range(nc[0]):
        ws3.write(i+10,j+3,resp[j].surf_fit[0].coeff_value[i],format_real)
        rf = rf + 'index(A1:ZZ1000,'+str(i+11)+',3)*index(A1:ZZ1000,'+str(i+11)+','+str(j+4)+')+'
    rf = rf.rstrip('+')
    ws3.write_formula(nc[0]+10,j+3,''+rf+'',format_real)
    try:
        ws3.write(nc[0]+11,j+3,resp[j].surf_fit[0].rsquared,format_real)
    except:
        ws3.write(nc[0]+11,j+3, 'Fixed Value',format_real)
for jj in range(2+nresp):
    ws3.write(nc[0]+12,jj+1,'',format_top)

# Write quadratic data
title_ws4 = 'Data - Quadratic'
ws4.set_column(0, 0, 15,format_blank)
ws4.set_column(1, 1000, 30,format_blank) 
ws4.set_row(0,15,format_intro)
ws4.set_row(1,15,format_intro)
ws4.set_row(2,15,format_intro)
ws4.set_row(3,15,format_intro)
ws4.set_row(4,15,format_intro)
ws4.set_row(5,15,format_intro)
ws4.set_row(6,15,format_intro)
ws4.write(0,0,title_ws4,format_title)

ws4.write(9,1,'Parameter',format_header)
ws4.write(9,2,'Value',format_header)
for j in range(nresp):
    ws4.write(9,j+3,resp[j].name,format_header)
ws4.write(10,0,'',format_right)
ws4.write(10,1,'Intercept',format_label)
ws4.write(10,2,'1',format_integer)
ws4.write(10,nresp+3,'',format_left)
m = 0
for i in range(ndv):
    m = m + 1
    ws4.write(m+10,0,'',format_right)
    ws4.write(m+10,1,dv[i].name,format_label)
    ws4.write_formula(m+10,2,'Calculator!f'+str(i+11),format_real)
    ws4.write(m+10,nresp+3,'',format_left)
    for j in range(i,ndv):
        m = m + 1
        ws4.write(m+10,0,'',format_right)       
        ws4.write(m+10,1,dv[i].name + ' * ' + dv[j].name,format_label)
        ws4.write_formula(m+10,2,'Calculator!f'+str(i+11)+'*Calculator!f'+str(j+11),format_real)
        ws4.write(m+10,nresp+3,'',format_left)
ws4.write(m+11,0,'',format_right)
ws4.write(m+11,1,'Response',format_label)
ws4.write(m+11,2,'',format_label)
ws4.write(m+12,0,'',format_right)
ws4.write(m+12,1,'R-squared',format_label)
ws4.write(m+12,2,'',format_label)
ws4.write(m+11,nresp+3,'',format_left)
ws4.write(m+12,nresp+3,'',format_left)
for j in range(nresp):
    rf = ''
    for i in range(nc[1]):
        ws4.write(i+10,j+3,resp[j].surf_fit[1].coeff_value[i],format_real)
        rf = rf + 'index(A1:ZZ1000,'+str(i+11)+',3)*index(A1:ZZ1000,'+str(i+11)+','+str(j+4)+')+'
    rf = rf.rstrip('+')
    ws4.write_formula(nc[1]+10,j+3,''+rf+'',format_real)
    try:
        ws4.write(nc[1]+11,j+3,resp[j].surf_fit[1].rsquared,format_real)
    except:
        ws4.write(nc[1]+11,j+3,'Fixed Value',format_real)
for jj in range(2+nresp):
    ws4.write(nc[1]+12,jj+1,'',format_top)

# Write calculator
title_ws5 = 'Calculator'
ws5.set_column(0, 0, 20,format_blank)
ws5.set_column(1, 1, 30,format_blank)
ws5.set_column(2, 1000, 20,format_blank)   
ws5.set_row(0,15,format_intro)
ws5.set_row(1,15,format_intro)
ws5.set_row(2,15,format_intro)
ws5.set_row(3,15,format_intro)
ws5.set_row(4,15,format_intro)
ws5.set_row(5,15,format_intro)
ws5.set_row(6,15,format_intro)
ws5.write(0,0,title_ws5,format_title)
ws5.write(2,0,' - Response estimation with regression equation via user input',format_intro)


ws5.write(9,1,'Design Variable',format_header_2)
ws5.write(9,2,'Minimum',format_header)
ws5.write(9,3,'Nominal',format_header)
ws5.write(9,4,'Maximum',format_header)
ws5.write(9,5,'User',format_header_3)

for i in range(ndv):
    ws5.write(i+10,0,'',format_right)
    ws5.write(i+10,1,dv[i].name,format_real_right)
    ws5.write(i+10,2,dv[i].min_val,format_real)
    ws5.write(i+10,3,dv[i].nom_val,format_real)
    ws5.write(i+10,4,dv[i].max_val,format_real_right)
    ws5.write(i+10,5,dv[i].nom_val,format_input_real_right)
for j in range(5):
    ws5.write(ndv+10,j+1,'',format_top)

mpos =12+ndv
ws5.write(mpos,1,'Response Name',format_header_2)
ws5.write(mpos,2,'Linear Response',format_header)
ws5.write(mpos,3,'Linear R-Squared',format_header)
ws5.write(mpos,4,'Quadratic Response',format_header)
ws5.write(mpos,5,'Quadratic R-Squared',format_header)
for j in range(nresp):
    mpos = mpos + 1
    ws5.write(mpos,0,'',format_right)
    ws5.write(mpos,1,resp[j].name,format_real_right)
    ws5.write_formula(mpos,2,'index(\'Linear Data\'!A1:ZZ1000,'+str(nc[0]+11)+','+str(j+4)+')',format_real)
    ws5.write_formula(mpos,3,'index(\'Linear Data\'!A1:ZZ1000,'+str(nc[0]+12)+','+str(j+4)+')',format_real)
    ws5.write_formula(mpos,4,'index(\'Quadratic Data\'!A1:ZZ1000,'+str(nc[1]+11)+','+str(j+4)+')',format_real)
    ws5.write_formula(mpos,5,'index(\'Quadratic Data\'!A1:ZZ1000,'+str(nc[1]+12)+','+str(j+4)+')',format_real)
    ws5.write(mpos,6,'',format_left)

ws5.conditional_format(17, 3, 1000, 3, {
    'type':'cell',
    'criteria':'<', 
    'value': 0.9, 
    'format' : format_textgray
})
ws5.conditional_format(17, 3, 1000, 3, {
    'type':'cell',
    'criteria':'>=', 
    'value': 0.9, 
    'format' : format_textblue
})
ws5.conditional_format(17, 5, 1000, 5, {
    'type':'cell',
    'criteria':'<', 
    'value': 0.9, 
    'format' : format_textgray
})
ws5.conditional_format(17, 5, 1000, 5, {
    'type':'cell',
    'criteria':'>', 
    'value': 0.9, 
    'format' : format_textblue
})

mpos = mpos + 1
for j in range(5):
    ws5.write(mpos,j+1,'',format_top)

# Write effects data
title_ws6 = 'Data - Effects'
ws6.set_column(0, 0, 15,format_blank)
ws6.set_column(1, 1, 30,format_blank)
ws6.set_column(2, 5, 20,format_blank) 
ws6.set_column(6, 6, 30,format_blank)
ws6.set_column(7, 10, 20,format_blank) 
ws6.set_column(11, 11, 30,format_blank) 
ws6.set_column(12, 1000, 20,format_blank) 
ws6.set_row(0,15,format_intro)
ws6.set_row(1,15,format_intro)
ws6.set_row(2,15,format_intro)
ws6.set_row(3,15,format_intro)
ws6.set_row(4,15,format_intro)
ws6.set_row(5,15,format_intro)
ws6.set_row(6,15,format_intro)
ws6.write(0,0,title_ws6,format_title)

dv_val = []
for i in range(ndv):
    dv_val.append(dv[i].nom_val)

z1_min = []
z1_max = []
m = 9
ws6.write(8,1,'Main Effects - Linear',format_header)
for j in range(3):
    ws6.write(9,j+2,'',format_bottom)
for k in range(nresp):

    lpos = m + 1

    zn = []
    zx = []
    for i in range(ndv):
        for ii in range(1,4):
            if ii == 1:
                dv_val[i] = dv[i].min_val
                x,zmin = calc_reg(1,dv_val,resp[k].surf_fit[0].coeff_value)
                z = zmin
            elif ii == 2:
                dv_val[i] = dv[i].nom_val
                x,znom = calc_reg(1,dv_val,resp[k].surf_fit[0].coeff_value)
                z = znom
            elif ii == 3:
                dv_val[i] = dv[i].max_val
                x,zmax = calc_reg(1,dv_val,resp[k].surf_fit[0].coeff_value)
                z = zmax
            m = m + 1
            ws6.write(m,1,'',format_right)
            ws6.write(m,2,dv[i].name,format_real)
            ws6.write(m,3,dv_val[i],format_real)
            ws6.write(m,4,z,format_real)
            ws6.write(m,5,'',format_left)
            dv_val[i] = dv[i].nom_val
 
        zn.append(min(zmin,znom,zmax))
        zx.append(max(zmin,znom,zmax))

    ws6.write(lpos,1,resp[k].name,format_header_right)

    z1_min.append(min(zn))
    z1_max.append(max(zx))

for j in range(3):
    ws6.write(m+1,j+2,'',format_top)

z2_min = []
z2_max = []
m = 9
ws6.write(8,6,'Main Effects - Quadratic',format_header)
for j in range(3):
    ws6.write(9,j+7,'',format_bottom)
for k in range(nresp):

    lpos = m + 1

    zn = []
    zx = []
    for i in range(ndv):
        
        for ii in range(1,4):
            if ii == 1:
                dv_val[i] = dv[i].min_val
                x,zmin = calc_reg(2,dv_val,resp[k].surf_fit[1].coeff_value)
                z = zmin
            elif ii == 2:
                dv_val[i] = dv[i].nom_val
                x,znom = calc_reg(2,dv_val,resp[k].surf_fit[1].coeff_value)
                z = znom
            elif ii == 3:
                dv_val[i] = dv[i].max_val
                x,zmax = calc_reg(2,dv_val,resp[k].surf_fit[1].coeff_value)
                z = zmax
            m = m + 1
            ws6.write(m,6,'',format_right)
            ws6.write(m,7,dv[i].name,format_real)
            ws6.write(m,8,dv_val[i],format_real)
            ws6.write(m,9,z,format_real)
            ws6.write(m,10,'',format_left)
            dv_val[i] = dv[i].nom_val

        zn.append(min(zmin,znom,zmax))
        zx.append(max(zmin,znom,zmax))

    ws6.write(lpos,6,resp[k].name,format_header_right)

    z2_min.append(min(zn))
    z2_max.append(max(zx))

for j in range(3):
    ws6.write(m+1,j+7,'',format_top)

z3_min = []
z3_max = []
m = 9
ws6.write(8,11,'Interaction Effects - Quadratic',format_header)
for j in range(5):
    ws6.write(9,j+12,'',format_bottom)
for k in range(nresp):

    lpos = m + 1

    zn = []
    zx = []
    for i in range(ndv-1):
        for j in range(i+1,ndv):
            for jj in range(1,4):
                if jj == 1:
                    dv_val[j] = dv[j].min_val
                    for ii in range(1,4):
                        if ii == 1:
                            dv_val[i] = dv[i].min_val
                        elif ii == 2:
                            dv_val[i] = dv[i].nom_val
                        elif ii == 3:
                            dv_val[i] = dv[i].max_val
                        x,z = calc_reg(2,dv_val,resp[k].surf_fit[1].coeff_value)
                        m = m + 1
                        ws6.write(m,11,'',format_right)
                        ws6.write(m,12,dv[i].name,format_real)
                        ws6.write(m,13,dv_val[i],format_real)
                        ws6.write(m,14,dv[j].name,format_real)
                        ws6.write(m,15,dv_val[j],format_real)
                        ws6.write(m,16,round(z, 8),format_real)
                        ws6.write(m,17,'',format_left)
                        dv_val[i] = dv[i].nom_val
                elif jj == 2:
                    dv_val[j] = dv[j].nom_val
                    for ii in range(1,4):
                        if ii == 1:
                            dv_val[i] = dv[i].min_val
                        elif ii == 2:
                            dv_val[i] = dv[i].nom_val
                        elif ii == 3:
                            dv_val[i] = dv[i].max_val
                        x,z = calc_reg(2,dv_val,resp[k].surf_fit[1].coeff_value)
                        m = m + 1
                        ws6.write(m,11,'',format_right)
                        ws6.write(m,12,dv[i].name,format_real)
                        ws6.write(m,13,dv_val[i],format_real)
                        ws6.write(m,14,dv[j].name,format_real)
                        ws6.write(m,15,dv_val[j],format_real)
                        ws6.write(m,16,round(z, 8),format_real)
                        ws6.write(m,17,'',format_left)
                        dv_val[i] = dv[i].nom_val
                elif jj == 3:
                    dv_val[j] = dv[j].max_val
                    for ii in range(1,4):
                        if ii == 1:
                            dv_val[i] = dv[i].min_val
                        elif ii == 2:
                            dv_val[i] = dv[i].nom_val
                        elif ii == 3:
                            dv_val[i] = dv[i].max_val
                        x,z = calc_reg(2,dv_val,resp[k].surf_fit[1].coeff_value)
                        m = m + 1
                        ws6.write(m,11,'',format_right)
                        ws6.write(m,12,dv[i].name,format_real)
                        ws6.write(m,13,dv_val[i],format_real)
                        ws6.write(m,14,dv[j].name,format_real)
                        ws6.write(m,15,dv_val[j],format_real)
                        ws6.write(m,16,round(z, 8),format_real)
                        ws6.write(m,17,'',format_left)
                        dv_val[i] = dv[i].nom_val
            dv_val[j] = dv[j].nom_val

        zn.append(min(zmin,znom,zmax))
        zx.append(max(zmin,znom,zmax))

    ws6.write(lpos,11,resp[k].name,format_header_right)

    z3_min.append(min(zn))
    z3_max.append(max(zx))

for j in range(5):
    ws6.write(m+1,j+12,'',format_top)

# Main effects plots - linear
title_ws7 = 'Main Effects Plots - Linear'
ws7.set_column(0, 0, 30,format_blank)
ws7.set_column(1, 1000, 15,format_blank) 
ws7.set_row(0,15,format_intro)
ws7.set_row(1,15,format_intro)
ws7.set_row(2,15,format_intro)
ws7.set_row(3,15,format_intro)
ws7.set_row(4,15,format_intro)
ws7.set_row(5,15,format_intro)
ws7.set_row(6,15,format_intro)
ws7.write(0,0,title_ws7,format_title)
ws7.write(2,0,' - Responses of changing one variable and holding others constant',format_intro)
plot = []
m = 7
mpos = 9
markersize = 4
linewidth = 1
for k in range(nresp):
    min_resp = z1_min[k] - 0.1*abs(z1_min[k])
    max_resp = z1_max[k] + 0.1*abs(z1_max[k])
    for i in range(ndv):
        plot.append('plot_'+str(i))
        plot[i] = wb.add_chart({
            'type': 'scatter', 'subtype': 'smooth',
        })
        plot[i].set_size({
            'width': 400,
            'height': 250,
        })
        plot[i].set_chartarea({
           'border': {'color': 'black',},
        })
        m = m + 3
        plot[i].add_series({
            'name': resp[k].name,
            'categories': ['Effects Data',m,3,m+2,3],
            'values': ['Effects Data',m,4,m+2,4],
            'line': {'width': linewidth, 'color': 'blue'},
            'marker' : {"type" : "circle", 'size': markersize, 'fill': {'color':'blue' }, 'border':{'color':'blue'}},
            'data_labels' : {'value': True, 'num_format': '#,##0.00'},
        })
        plot[i].set_legend({
            'position': 'none',
        })
        plot[i].set_title ({
            'name': resp[k].name + ' vs ' + dv[i].name, 
            'name_font': {'name': "Arial", 'size':12, 'color': 'black'},
        })  
        plot[i].set_x_axis({
            'name': dv[i].name,
            'num_format': '#.##',
            'num_font': {'name': "Arial", 'size':9, 'color': 'black'},
            'name_font': {'name': "Arial", 'size':10, 'color': 'black'},
            'min' :  dv[i].min_val - abs(dv[i].min_val) * 0.02, 'max' : dv[i].max_val + abs(dv[i].max_val) * 0.02,  
        })  
        plot[i].set_y_axis({
            'name': resp[k].name,
            'num_format': '#.##',
            'num_font': {'name': "Arial", 'size':9, 'color': 'black'},
            'name_font': {'name': "Arial", 'size':10, 'color': 'black'},
            'min': min_resp,
            'max': max_resp,
        })  
        plot[i].set_style(11)  
        ws7.insert_chart(mpos,1 + 4*i,plot[i])

    mpos = mpos + 15

# Main effects plots - quadratic
title_ws8 = 'Main Effects Plots - Quadratic'
ws8.set_column(0, 0, 30,format_blank)
ws8.set_column(1, 1000, 15,format_blank) 
ws8.set_row(0,15,format_intro)
ws8.set_row(1,15,format_intro)
ws8.set_row(2,15,format_intro)
ws8.set_row(3,15,format_intro)
ws8.set_row(4,15,format_intro)
ws8.set_row(5,15,format_intro)
ws8.set_row(6,15,format_intro)
ws8.write(0,0,title_ws8,format_title)
ws8.write(2,0,' - Responses of changing one variable and holding others constant',format_intro)
plot = []
m = 7
mpos = 9
for k in range(nresp):
    min_resp = z2_min[k] - 0.1*abs(z2_min[k])
    max_resp = z2_max[k] + 0.1*abs(z2_max[k])
    for i in range(ndv):
        plot.append('plot_'+str(i))
        plot[i] = wb.add_chart({
            'type': 'scatter', 'subtype': 'smooth',
        })
        plot[i].set_size({
            'width': 400,
            'height': 250,
        })
        plot[i].set_chartarea({
           'border': {'color': 'black',},
        })
        m = m + 3
        plot[i].add_series({
            'name': resp[k].name,
            'categories': ['Effects Data',m,8,m+2,8],
            'values': ['Effects Data',m,9,m+2,9],
            'line': {'width': linewidth, 'color': 'blue'},
            'marker' : {"type" : "circle", 'size': markersize, 'fill': {'color':'blue' }, 'border':{'color':'blue'}},
            'data_labels' : {'value': True, 'num_format': '#,##0.00'},
         })
        plot[i].set_legend({
            'position': 'none',
        })
        plot[i].set_title ({
            'name': resp[k].name + ' vs ' + dv[i].name, 
            'name_font': {'name': "Arial", 'size':11, 'color': 'black'},
        })  
        plot[i].set_x_axis({
            'name': dv[i].name,
            'num_format': '#.##',
            'num_font': {'name': "Arial", 'size':10, 'color': 'black'},
            'name_font': {'name': "Arial", 'size':10, 'color': 'black'},
            'min' :  dv[i].min_val - abs(dv[i].min_val) * 0.02, 'max' : dv[i].max_val + abs(dv[i].max_val) * 0.02,  
        })  
        plot[i].set_y_axis({
            'name': resp[k].name,
            'num_format': '#.##',
            'num_font': {'name': "Arial", 'size':10, 'color': 'black'},
            'name_font': {'name': "Arial", 'size':10, 'color': 'black'},
            'min': min_resp,
            'max': max_resp,
        })  
        plot[i].set_style(11)  
        ws8.insert_chart(mpos,1 + 4*i,plot[i])

    mpos = mpos + 15

# Interaction plots
title_ws9 = 'Interaction Plots - Quadratic'
ws9.set_column(0, 0, 30,format_blank)
ws9.set_column(1, 1000, 15,format_blank) 
ws9.set_row(0,15,format_intro)
ws9.set_row(1,15,format_intro)
ws9.set_row(2,15,format_intro)
ws9.set_row(3,15,format_intro)
ws9.set_row(4,15,format_intro)
ws9.set_row(5,15,format_intro)
ws9.set_row(6,15,format_intro)
ws9.write(0,0,title_ws9,format_title)
ws9.write(2,0,' - Responses of changing two variables and holding others constant',format_intro)
plot = []
m = 7
mpos = 9

for k in range(nresp):
    min_resp = z2_min[k] - 0.1*abs(z2_min[k])
    max_resp = z2_max[k] + 0.1*abs(z2_max[k])
    ii = -1
    for i in range(ndv):
        for j in range(i+1,ndv):
            ii = ii + 1
            plot.append('plot_'+str(ii))
            plot[ii] = wb.add_chart({
                'type': 'scatter', 'subtype': 'smooth',
            })
            plot[ii].set_size({
                'width': 400,
                'height': 250,
            })
            plot[i].set_chartarea({
               'border': {'color': 'black',},
            })
            m = m + 3
            plot[ii].add_series({
                'name': dv[j].name+' = '+ str(dv[j].min_val),
                'categories': ['Effects Data',m,13,m+2,13],
                'values': ['Effects Data',m,16,m+2,16],
                'line': {'width': linewidth, 'color': 'blue'},
                'marker' : {"type" : "circle", 'size': markersize, 'fill': {'color':'blue' }, 'border':{'color':'blue'}},
                
            })
            m = m + 3
            plot[ii].add_series({
                'name': dv[j].name+' = '+ str(dv[j].nom_val),
                'categories': ['Effects Data',m,13,m+2,13],
                'values': ['Effects Data',m,16,m+2,16],
                'line': {'width': linewidth, 'color': 'red'},
                'marker' : {"type" : "circle", 'size': markersize, 'fill': {'color':'red' }, 'border':{'color':'red'}},
             })
            m = m + 3
            plot[ii].add_series({
                'name': dv[j].name+' = '+ str(dv[j].max_val),
                'categories': ['Effects Data',m,13,m+2,13],
                'values': ['Effects Data',m,16,m+2,16],
                'line': {'width': linewidth, 'color': 'green'},
                'marker' : {"type" : "circle", 'size': markersize, 'fill': {'color':'green' }, 'border':{'color':'green'}},
            })
            plot[ii].set_title ({
                'name': resp[k].name+': '+dv[j].name + ' vs ' + dv[i].name, 
                'name_font': {'name': "Arial", 'size':11, 'color': 'black'},
            })  
            plot[ii].set_x_axis({
                'name': dv[i].name,
                'num_format': '#.##',
                'num_font': {'name': "Arial", 'size':10, 'color': 'black'},
                'name_font': {'name': "Arial", 'size':10, 'color': 'black'},
                'min' :  dv[i].min_val - abs(dv[i].min_val) * 0.02, 'max' : dv[i].max_val + abs(dv[i].max_val) * 0.02,  
            })  
            plot[ii].set_y_axis({
                'name': resp[k].name,
                'num_format': '#.##',
                'num_font': {'name': "Arial", 'size': 8, 'color': 'black'},
                'name_font': {'name': "Arial", 'size':9, 'color': 'black'},
            })  
            
            plot[ii].set_style(11)  
            ws9.insert_chart(mpos,1 + 4*ii,plot[ii])


    mpos = mpos + 15

# Hide Sheets
ws3.hide()
ws4.hide()
ws6.hide()


SDM = 0 # Dimension
SSF = 0 # static footprint
SDF = 0 # Dynamic footprint
SRR = 0 # RR
SEN = 0 # Endurance
SSS = 0 # Static Stiffness 
SCS = 0 # Cornering stiffness
SMD = 0 # Modal 
for j in range(nresp):
    if "DM_" in resp[j].name: SDM = 1
    if "SF_" in resp[j].name: SSF = 1
    if "DF_" in resp[j].name: SDF = 1
    if "RR_" in resp[j].name: SRR = 1
    if "EN_" in resp[j].name: SEN = 1
    if "SS_" in resp[j].name: SSS = 1
    if "CS_" in resp[j].name: SCS = 1
    if "MD_" in resp[j].name: SMD = 1


if SDM == 1: ws101 = wb.add_worksheet('Results_Dimension')
if SSF == 1: ws102 = wb.add_worksheet('Results_StaticFoot')
if SDF == 1: ws103 = wb.add_worksheet('Results_RollingFoot')
if SRR == 1: ws104 = wb.add_worksheet('Results_RR')
if SEN == 1: ws105 = wb.add_worksheet('Results_Endurance')
if SSS == 1: ws106 = wb.add_worksheet('Result_StaticStiffness')
if SCS == 1: ws107 = wb.add_worksheet('Results_CorneringStiffness')
if SMD == 1: ws108 = wb.add_worksheet('Result_Modal')

if SDM == 1: 
    WbTitle = "Dimension Simulation Results"
    ws101.write(0,0,WbTitle,format_title)
if SSF == 1: 
    WbTitle = "Static Footprint Simulation Results"
    ws102.write(0,0,WbTitle,format_title)
if SDF == 1: 
    WbTitle = "Rolling Footprint Simulation Results"
    ws103.write(0,0,WbTitle,format_title)
if SRR == 1: 
    WbTitle = "Rolling Resistance Simulation Results"
    ws104.write(0,0,WbTitle,format_title)
if SEN == 1: 
    WbTitle = "Endurance Simulation Results"
    ws105.write(0,0,WbTitle,format_title)
if SSS ==1: 
    WbTitle = "Static Stiffness Simulation Results"
    ws106.write(0,0,WbTitle,format_title)
if SCS ==1: 
    WbTitle = "Cornering Stiffness Simulation Results"
    ws107.write(0,0,WbTitle,format_title)
if SMD ==1: 
    WbTitle = "Modal Simulation Results"
    ws108.write(0,0,WbTitle,format_title)



format_size_Pattern = wb.add_format({
    'font_name': 'Ariel',
    'font_size': 10,
    'num_format': '0.0000',
    'bold': False,
    'font_color': 'black',
    'align': 'center',
    'valign' : 'vcenter',
    'underline': False,
    'bg_color': False,
    'right': 1,
    'bottom': 1, 
})

format_BG_gray_text = wb.add_format({
    'font_name': 'Ariel', 
    'font_size': 10, 
    'bold': False,
    'bg_color' : '#C0C0C0',
    'right': 1, 
    'bottom': 1,
    'top': 1, 
    'align': 'center',
    'valign' : 'vcenter',
})

cwd = os.getcwd()
tvls = glob.glob(cwd+"/*.tvl")
with open(tvls[0]) as TL:
    lines = TL.readlines()
Model_0 = lines[0].strip()
NoModels = len(lines)
VT_0 = Model_0.split("-")[1] +"-" + Model_0.split("-")[2] 

RefModelVT = lines[0].strip()

if SDM == 1: 
    ws101.freeze_panes(3, 2)
    cellw = 50.0
    ws101.set_column(0, 1, 16,format_blank) 
    ws101.set_column(2, 100, cellw,format_blank) 
    ws101.set_row(0, 20, format_blank)
    ws101.set_row(1, 20, format_blank)
    ws101.set_row(2, 20, format_blank)
    ws101.set_row(3, 225, format_blank)
    for i in range(4, 22,1):     ws101.set_row(i, 20, format_blank)
    ws101.set_row(22, 225, format_blank)
    ws101.set_row(23, 225, format_blank)
    ws101.set_row(24, 225, format_blank)
    ws101.set_row(25, 225, format_blank)

    sns = cwd+"/" + VT_0 + "/" + Model_0+"-D103-0001/" + Model_0 + "-D103-0001.sns"
    with open(sns) as Json: 
        Dsns = json.load(Json)

    size = Dsns["VirtualTireBasicInfo"]["TireSize"]
    pattern = Dsns["VirtualTireBasicInfo"]["Pattern"]
    
    ws101.write(0,0, 'SIZE', format_size_Pattern)
    ws101.write(1,0, "PATTERN", format_size_Pattern)
    ws101.write(0,1, size, format_size_Pattern)
    ws101.write(1,1, pattern, format_size_Pattern)
    VTid =  Dsns["VirtualTireBasicInfo"]["VirtualTireID"]
    ws101.write(0,2, "VT Code: "+ VTid, format_size_Pattern)

    ws101.merge_range("A3:B3", 'Model Revision', format_BG_gray_text)
    ws101.merge_range("A4:B4", 'Layout Comparison', format_size_Pattern)
    ws101.merge_range("A5:A6", 'OD', format_size_Pattern)
    ws101.merge_range("A7:A8", 'SW', format_size_Pattern)
    ws101.merge_range("A9:A10", 'Shoulder Drop', format_size_Pattern)
    ws101.merge_range("A11:A12", 'Crown Radius', format_size_Pattern)
    ws101.merge_range("A13:A14", 'Belt Radius', format_size_Pattern)
    ws101.merge_range("A15:A16", 'Carcass Radius at side', format_size_Pattern)
    ws101.merge_range("A17:A18", 'Belt Lift', format_size_Pattern)
    

    ws101.write(4, 1, "Initial", format_BG_gray_text)
    ws101.write(5, 1, "Deformed", format_size_Pattern)
    ws101.write(6, 1, "Initial", format_BG_gray_text)
    ws101.write(7, 1, "Deformed", format_size_Pattern)
    ws101.write(8, 1, "Initial", format_BG_gray_text)
    ws101.write(9, 1, "Deformed", format_size_Pattern)
    ws101.write(10, 1, "Initial", format_BG_gray_text)
    ws101.write(11, 1, "Deformed", format_size_Pattern)
    ws101.write(12, 1, "Initial", format_BG_gray_text)
    ws101.write(13, 1, "Deformed", format_size_Pattern)
    ws101.write(14, 1, "Initial", format_BG_gray_text)
    ws101.write(15, 1, "Deformed", format_size_Pattern)
    ws101.write(16, 1, "Center", format_BG_gray_text)
    ws101.write(17, 1, "Edge", format_size_Pattern)

    ws101.write(18, 0, "Belt Drop", format_size_Pattern)
    ws101.write(18, 1, "Center-Edge", format_BG_gray_text)

    ws101.merge_range("A20:B20", 'Weight[kg]', format_size_Pattern)
    ws101.merge_range("A21:B21", 'Mold K-Factor/A-Angle', format_BG_gray_text)
    ws101.merge_range("A22:B22", 'Inlfated K-Factor', format_BG_gray_text)

    ws101.merge_range("A23:B23", 'Initial Vs. Inflated Profile', format_size_Pattern)
    ws101.merge_range("A24:B24", 'Belt Cord Tension', format_size_Pattern)
    ws101.merge_range("A25:B25", 'Carcass Cord Tension', format_size_Pattern)

    for i in range(NoModels): 
        ws101.write(2, i+2, i, format_BG_gray_text)
        ws101.write(3, i+2, "", format_size_Pattern)
        ws101.write(19, i+2, "", format_size_Pattern)
        ws101.write(20, i+2, "", format_size_Pattern)
        ws101.write(21, i+2, "", format_size_Pattern)

        spec =""
        for k in range(ndv):
            spec += dv[k].name +":"
            if k == ndv-1: spec += str(format(dv[k].value[i], ".2f")) 
            else: spec += str(format(dv[k].value[i], ".2f"))  +" / "
        ws101.write(1, i+2, spec, format_size_Pattern)

        Model = lines[i].strip()
        VT = Model.split("-")[1] +"-" + Model.split("-")[2] 
        filedir = cwd+"/" + VT + "/" + Model+"-D103-0001"
        resultfile = filedir +"/" + Model + '-D103-0001-Dimension.txt'
        Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png"
        Profilefile = filedir + '/' + Model + "-D103-0001-Inflated.png"
        BeltTensionfile = filedir + '/' + Model + "-D103-0001-BT_Tension.png"
        CarcassTensionfile = filedir + '/' + Model + "-D103-0001-CC_Tension.png"
        
        col_name = xlsxwriter.utility.xl_col_to_name(i+2, False)
        position = col_name+"4"
        xscale = 0.490 # cellw / wth 
        ws101.insert_image(position, Meshfile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"23"
        ws101.insert_image(position, Profilefile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"24"
        ws101.insert_image(position, BeltTensionfile, {'x_scale':xscale, 'y_scale': xscale})
        position = col_name+"25"
        ws101.insert_image(position, CarcassTensionfile, {'x_scale': xscale, 'y_scale': xscale})

        with open(resultfile) as R: 
            results = R.readlines()
        
        for line in results:
            data = line.split("=")
            if 'Initial OD' in data[0]: ws101.write(4, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Deformed OD' in data[0]: ws101.write(5, i+2,float(data[1].strip()), format_size_Pattern)

            if 'Initial SW' in data[0]: ws101.write(6, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Deformed SW' in data[0]: ws101.write(7, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Initial Sho.' in data[0]: ws101.write(8, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Deformed Sho.' in data[0]: ws101.write(9, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Initial Crown' in data[0]: ws101.write(10, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Deformed Crown' in data[0]: ws101.write(11, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Initial Belt' in data[0]: ws101.write(12, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Deformed Belt' in data[0]: ws101.write(13, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Initial Carcass' in data[0]: ws101.write(14, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Deformed Carcass' in data[0]: ws101.write(15, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Belt Center' in data[0]: ws101.write(16, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Belt Edge Lift' in data[0]: ws101.write(17, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Belt Edge Drop' in data[0]: ws101.write(18, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Weight' in data[0]: ws101.write(19, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Mold K-Factor' in data[0]: ws101.write(20, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Inflated K-Factor' in data[0]: ws101.write(21, i+2, float(data[1].strip()), format_BG_gray_text)

if SSF == 1: 
    ws102.freeze_panes(3, 2)
    cellw = 50.0
    cellh = 18
    cellimh = 215
    ws102.set_column(0, 1, 16,format_blank) 
    ws102.set_column(2, 100, cellw,format_blank) 
    ws102.set_row(0, cellh, format_blank)
    ws102.set_row(1, cellh, format_blank)
    ws102.set_row(2, cellh, format_blank)
    ws102.set_row(3, cellimh, format_blank)
    ws102.set_row(4, cellimh, format_blank)
    for i in range(5, 27,1):     ws102.set_row(i, cellh, format_blank)
    ws102.set_row(27, cellimh, format_blank)
    for i in range(28, 30,1):     ws102.set_row(i, cellh, format_blank)
    ws102.set_row(30, cellimh, format_blank)
    ws102.set_row(31, cellimh, format_blank)
    ws102.set_row(32, cellimh, format_blank)
    ws102.set_row(33, cellimh, format_blank)
    ws102.set_row(34, cellimh, format_blank)

    sns = cwd+"/" + VT_0 + "/" + Model_0+"-D101-0001/" + Model_0 + "-D101-0001.sns"
    with open(sns) as Json: 
        Dsns = json.load(Json)

    size = Dsns["VirtualTireBasicInfo"]["TireSize"]
    pattern = Dsns["VirtualTireBasicInfo"]["Pattern"]
    ws102.write(0,0, 'SIZE', format_size_Pattern)
    ws102.write(1,0, "PATTERN", format_size_Pattern)
    ws102.write(0,1, size, format_size_Pattern)
    ws102.write(1,1, pattern, format_size_Pattern)
    VTid =  Dsns["VirtualTireBasicInfo"]["VirtualTireID"]
    ws102.write(0,2, "VT Code: "+ VTid, format_size_Pattern)

    ws102.merge_range("A3:B3", 'Model Revision', format_BG_gray_text)
    ws102.merge_range("A4:B4", 'Layout Comparison', format_size_Pattern)
    ws102.merge_range("A5:B5", 'Foot shape', format_size_Pattern)
    
    ws102.merge_range("A6:A11", 'Contact Length', format_size_Pattern)
    ws102.merge_range("A12:A15", 'Square Ratio', format_size_Pattern)
    ws102.merge_range("A16:A17", 'Contact Length Ratio(%)', format_size_Pattern)
    ws102.merge_range("A18:A23", 'Contact Width', format_size_Pattern)
    ws102.merge_range("A24:A25", 'Contact Area(cm2)', format_size_Pattern)
    ws102.merge_range("A26:B26", 'Roundness', format_BG_gray_text)
    ws102.merge_range("A27:B27", 'Snow Score Index(FORD)', format_size_Pattern)
    ws102.merge_range("A28:B28", 'Contact pressure along center', format_size_Pattern)
    ws102.merge_range("A29:A30", 'Dimension', format_size_Pattern)
    ws102.merge_range("A31:B31", 'Profile', format_size_Pattern)
    ws102.merge_range("A32:B32", 'Rib Shape', format_size_Pattern)
    ws102.merge_range("A33:B33", 'Rib Contact Area(cm2)', format_size_Pattern)
    ws102.merge_range("A34:B34", 'Rib Contact Force(kgf)', format_size_Pattern)
    ws102.merge_range("A35:B35", 'Rib Contact Avg. Pressure(kPa)', format_size_Pattern)
    

    ws102.write(5, 1, "Max", format_BG_gray_text)
    ws102.write(6, 1, "Center", format_size_Pattern)
    ws102.write(7, 1, "15%", format_BG_gray_text)
    ws102.write(8, 1, "25%", format_size_Pattern)
    ws102.write(9, 1, "75%", format_BG_gray_text)
    ws102.write(10, 1, "85%", format_size_Pattern)

    ws102.write(11, 1, "15% / Center", format_BG_gray_text)
    ws102.write(12, 1, "25% / Center", format_size_Pattern)
    ws102.write(13, 1, "75% / Center", format_BG_gray_text)
    ws102.write(14, 1, "85% / Center", format_size_Pattern)
    ws102.write(15, 1, "25% / 75%", format_BG_gray_text)
    ws102.write(16, 1, "15% / 85%", format_size_Pattern)

    ws102.write(17, 1, "Max", format_BG_gray_text)
    ws102.write(18, 1, "Center", format_size_Pattern)
    ws102.write(19, 1, "15%", format_BG_gray_text)
    ws102.write(20, 1, "25%", format_size_Pattern)
    ws102.write(21, 1, "75%", format_BG_gray_text)
    ws102.write(22, 1, "85%", format_size_Pattern)

    ws102.write(23, 1, "Total", format_BG_gray_text)
    ws102.write(24, 1, "Actual", format_size_Pattern)

    ws102.write(28, 1, "SLR", format_BG_gray_text)
    ws102.write(29, 1, "SLW", format_size_Pattern)

    RawFiles = [" "] * 17 # Added by JSL
    
    for i in range(NoModels): 
        ws102.write(2, i+2, i, format_BG_gray_text)
        ws102.write(3, i+2, "", format_size_Pattern)
        ws102.write(4, i+2, "", format_size_Pattern)
        ws102.write(27, i+2, "", format_size_Pattern)
        ws102.write(30, i+2, "", format_size_Pattern)
        ws102.write(31, i+2, "", format_size_Pattern)
        ws102.write(32, i+2, "", format_size_Pattern)
        ws102.write(33, i+2, "", format_size_Pattern)

        spec =""
        for k in range(ndv):
            spec += dv[k].name +":"
            if k == ndv-1: spec += str(format(dv[k].value[i], ".2f")) 
            else: spec += str(format(dv[k].value[i], ".2f"))  +" / "
        ws102.write(1, i+2, spec, format_size_Pattern)


        Model = lines[i].strip()
        VT = Model.split("-")[1] +"-" + Model.split("-")[2] 
        filedir = cwd+"/" + VT + "/" + Model+"-D101-0001"
        resultfile = filedir +"/" + Model + '-D101-0001-DOE-Staticfootprint.txt'
        Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png"
        Profilefile = filedir + '/' + Model + "-D101-0001-ProfileCompare.png"  
        if os.path.isfile(Profilefile) == False:
            Profilefile = filedir + '/' + Model + "-D101-0001-Profilecompare.png" 
        Footshapefile = filedir + '/' + Model + "-D101-0001-Footshape.png"
        Contactpressurefile = filedir + '/' + Model + "-D101-0001-CpressGraph.png"
        Ribshapefile = filedir + '/' + Model + "-D101-0001-RibShape.png"
        Areafile = filedir + '/' + Model + "-D101-0001-Ribarea.png"
        Forcefile = filedir + '/' + Model + "-D101-0001-Ribforce.png"
        Pressurefile = filedir + '/' + Model + "-D101-0001-Ribpressure.png"
        
        # Characteristic Files
        RawFiles[i] = filedir + "/" + Model + "-D101-0001-CharacteristicValues.txt" # Added by JSL
        
        col_name = xlsxwriter.utility.xl_col_to_name(i+2, False)
        position = col_name+"4"
        xscale = 0.490 # cellw / wth 
        ws102.insert_image(position, Meshfile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"5"
        ws102.insert_image(position, Footshapefile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"28"
        ws102.insert_image(position, Contactpressurefile, {'x_scale':xscale, 'y_scale': xscale})

        position = col_name+"31"
        ws102.insert_image(position, Profilefile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"32"
        ws102.insert_image(position, Ribshapefile, {'x_scale': xscale, 'y_scale': xscale})
        xscale = 0.45
        position = col_name+"33"
        ws102.insert_image(position, Areafile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"34"
        ws102.insert_image(position, Forcefile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"35"
        ws102.insert_image(position, Pressurefile, {'x_scale': xscale, 'y_scale': xscale})

        with open(resultfile) as R: 
            results = R.readlines()
        Ribforce =[]
        Ribarea = []
        Ribpress =[]
        for line in results:
            data = line.split("=")
            if 'Contact Length Max' in data[0]: ws102.write(5, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length Center' in data[0]: ws102.write(6, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Contact Length 15%' in data[0]: ws102.write(7, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length 25%' in data[0]: ws102.write(8, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Contact Length 75%' in data[0]: ws102.write(9, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length 85%' in data[0]: ws102.write(10, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Square Ratio 15%' in data[0]: ws102.write(11, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Square Ratio 25%' in data[0]: ws102.write(12, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Square Ratio 75%' in data[0]: ws102.write(13, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Square Ratio 85%' in data[0]: ws102.write(14, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Contact Length Ratio 25%/75%' in data[0]: ws102.write(15, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length Ratio 15%/85%' in data[0]: ws102.write(16, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Contact Width Max' in data[0]: ws102.write(17, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width Center' in data[0]: ws102.write(18, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Contact Width 15%' in data[0]: ws102.write(19, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width 25%' in data[0]: ws102.write(20, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Contact Width 75%' in data[0]: ws102.write(21, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width 85%' in data[0]: ws102.write(22, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Total Contact Area' in data[0]: ws102.write(23, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Actual Contact Area' in data[0]: ws102.write(24, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Roundness' in data[0]: ws102.write(25, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'SNOW SCORE' in data[0]: 
                # print ('snow  %f'%(float(data[1].strip())))
                if i ==0: 
                    ws102.write(26, i+2, 100.0, format_size_Pattern)
                    SC0 = float(data[1].strip())
                else:
                    SC = round(float(data[1].strip()) / SC0*100, 3)
                    ws102.write(26, i+2, SC, format_size_Pattern)

            if 'SLR' in data[0]: ws102.write(28, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'SLW' in data[0]: ws102.write(29, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Rib' in data[0] and 'Force[kgf]' in data[0] : Ribforce.append(float(data[1].strip()))
            if 'Rib' in data[0] and 'Area[cm2]' in data[0] : Ribarea.append(float(data[1].strip()))
            if 'Rib' in data[0] and 'Press[kPa]' in data[0] : Ribpress.append(float(data[1].strip()))

            if 'Rib' in data[0] and 'Force[kgf]' in data[0]: ws102.write(34+len(Ribforce), i+2, float(data[1].strip()), format_size_Pattern)
            if 'Rib' in data[0] and 'Area[cm2]' in data[0]: ws102.write(34+len(Ribforce)+len(Ribarea), i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Rib' in data[0] and 'Press[kPa]' in data[0]: ws102.write(34+len(Ribforce)+len(Ribarea) + len(Ribpress), i+2, float(data[1].strip()), format_size_Pattern)

    NoRibs = len(Ribforce)
    # print (NoRibs)
    if NoRibs > 1:
        rowrange = 'A'+str(36) + ":" + 'A'+str (36+NoRibs-1)
        # print ("1", rowrange)
        ws102.merge_range(rowrange, 'Rib Force', format_size_Pattern)
        for k in range (NoRibs): ws102.write(35+k, 1, "#"+str(k+1), format_size_Pattern)

        rowrange = 'A'+str(36+NoRibs) + ":" + 'A'+str (36+2*NoRibs-1)
        ws102.merge_range(rowrange, 'Rib Area', format_BG_gray_text)
        for k in range (NoRibs): ws102.write(35+NoRibs+k, 1, "#"+str(k+1), format_BG_gray_text)
        # print ("2", rowrange)
        rowrange = 'A'+str(36+2*NoRibs) + ":" + 'A'+str (36+3*NoRibs-1)
        ws102.merge_range(rowrange, 'Rib Pressure', format_size_Pattern)
        for k in range (NoRibs): ws102.write(35+2*NoRibs+k, 1, "#"+str(k+1), format_size_Pattern)
        # print ("3", rowrange)
    else:
        ws102.write(35, 0, "Rib Force(kgf)", format_size_Pattern)
        ws102.write(35, 1, "#1", format_size_Pattern)

        ws102.write(36, 0, "Rib Area(cm2)", format_size_Pattern)
        ws102.write(36, 1, "#1", format_size_Pattern)

        ws102.write(37, 0, "Rib Pressure(kPa)", format_size_Pattern)
        ws102.write(37, 1, "#1", format_size_Pattern)

    # Added by JSL
    # Write Footshape Raw Data
    ws200 = wb.add_worksheet('FS Raw 00')
    ws201 = wb.add_worksheet('FS Raw 01')
    ws202 = wb.add_worksheet('FS Raw 02')
    ws203 = wb.add_worksheet('FS Raw 03')
    ws204 = wb.add_worksheet('FS Raw 04')
    ws205 = wb.add_worksheet('FS Raw 05')
    ws206 = wb.add_worksheet('FS Raw 06')
    ws207 = wb.add_worksheet('FS Raw 07')
    ws208 = wb.add_worksheet('FS Raw 08')
    ws209 = wb.add_worksheet('FS Raw 09')
    ws210 = wb.add_worksheet('FS Raw 10')
    ws211 = wb.add_worksheet('FS Raw 11')
    ws212 = wb.add_worksheet('FS Raw 12')
    ws213 = wb.add_worksheet('FS Raw 13')
    ws214 = wb.add_worksheet('FS Raw 14')
    ws215 = wb.add_worksheet('FS Raw 15')
    ws216 = wb.add_worksheet('FS Raw 16')
    
    
    if os.path.isfile(RawFiles[1]): 
        # Footshape 00
        f00 = open(RawFiles[0], 'r')
        lines00 = f00.readlines()
        size_arr = np.size(lines00)
        line1 = lines00[0].split()
        line2 = lines00[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines00[i].split()
        ws200.write_row(0,0, line1)
        ws200.write_row(1,0, line2)
        ws200.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws200.write_row(i+3,0, raw[i])
        f00.close()
        
        # Footshape 01
    
        f01 = open(RawFiles[1], 'r')
        lines01 = f01.readlines()
        size_arr = np.size(lines01)
        
        line1 = lines01[0].split()
        line2 = lines01[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines01[i].split()
        ws201.write_row(0,0, line1)
        ws201.write_row(1,0, line2)
        ws201.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws201.write_row(i+3,0, raw[i])
        f01.close()
        
        # Footshape 02
        f02 = open(RawFiles[2], 'r')
        lines02 = f02.readlines()
        size_arr = np.size(lines02)
        line1 = lines02[0].split()
        line2 = lines02[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines02[i].split()
        ws202.write_row(0,0, line1)
        ws202.write_row(1,0, line2)
        ws202.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws202.write_row(i+3,0, raw[i])
        f02.close()
        
        # Footshape 03
        f03 = open(RawFiles[3], 'r')
        lines03 = f03.readlines()
        size_arr = np.size(lines03)
        line1 = lines03[0].split()
        line2 = lines03[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines03[i].split()
        ws203.write_row(0,0, line1)
        ws203.write_row(1,0, line2)
        ws203.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws203.write_row(i+3,0, raw[i])
        f03.close()
        
        # Footshape 04
        f04 = open(RawFiles[4], 'r')
        lines04 = f04.readlines()
        size_arr = np.size(lines04)
        line1 = lines04[0].split()
        line2 = lines04[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines04[i].split()
        ws204.write_row(0,0, line1)
        ws204.write_row(1,0, line2)
        ws204.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws204.write_row(i+3,0, raw[i])
        f04.close()
        
        # Footshape 05
        f05 = open(RawFiles[5], 'r')
        lines05 = f05.readlines()
        size_arr = np.size(lines05)
        line1 = lines05[0].split()
        line2 = lines05[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines05[i].split()
        ws205.write_row(0,0, line1)
        ws205.write_row(1,0, line2)
        ws205.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws205.write_row(i+3,0, raw[i])
        f05.close()
        
        # Footshape 06
        f06 = open(RawFiles[6], 'r')
        lines06 = f06.readlines()
        size_arr = np.size(lines06)
        line1 = lines06[0].split()
        line2 = lines06[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines06[i].split()
        ws206.write_row(0,0, line1)
        ws206.write_row(1,0, line2)
        ws206.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws206.write_row(i+3,0, raw[i])
        f06.close()
        
        # Footshape 07
        f07 = open(RawFiles[7], 'r')
        lines07 = f07.readlines()
        size_arr = np.size(lines07)
        line1 = lines07[0].split()
        line2 = lines07[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines07[i].split()
        ws207.write_row(0,0, line1)
        ws207.write_row(1,0, line2)
        ws207.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws207.write_row(i+3,0, raw[i])
        f07.close()
        
        # Footshape 08
        f08 = open(RawFiles[8], 'r')
        lines08 = f08.readlines()
        size_arr = np.size(lines08)
        line1 = lines08[0].split()
        line2 = lines08[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines08[i].split()
        ws208.write_row(0,0, line1)
        ws208.write_row(1,0, line2)
        ws208.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws208.write_row(i+3,0, raw[i])
        f08.close()
        
        # Footshape 09
        f09 = open(RawFiles[9], 'r')
        lines09 = f09.readlines()
        size_arr = np.size(lines09)
        line1 = lines09[0].split()
        line2 = lines09[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines09[i].split()
        ws209.write_row(0,0, line1)
        ws209.write_row(1,0, line2)
        ws209.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws209.write_row(i+3,0, raw[i])
        f09.close()
        
        # Footshape 10
        f10 = open(RawFiles[10], 'r')
        lines10 = f10.readlines()
        size_arr = np.size(lines10)
        line1 = lines10[0].split()
        line2 = lines10[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines10[i].split()
        ws210.write_row(0,0, line1)
        ws210.write_row(1,0, line2)
        ws210.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws210.write_row(i+3,0, raw[i])
        f10.close()
        
        # Footshape 11
        f11 = open(RawFiles[11], 'r')
        lines11 = f11.readlines()
        size_arr = np.size(lines11)
        line1 = lines11[0].split()
        line2 = lines11[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines11[i].split()
        ws211.write_row(0,0, line1)
        ws211.write_row(1,0, line2)
        ws211.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws211.write_row(i+3,0, raw[i])
        f11.close()
        
        # Footshape 12
        f12 = open(RawFiles[12], 'r')
        lines12 = f12.readlines()
        size_arr = np.size(lines12)
        line1 = lines12[0].split()
        line2 = lines12[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines12[i].split()
        ws212.write_row(0,0, line1)
        ws212.write_row(1,0, line2)
        ws212.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws212.write_row(i+3,0, raw[i])
        f12.close()
        
        # Footshape 13
        f13 = open(RawFiles[13], 'r')
        lines13 = f13.readlines()
        size_arr = np.size(lines13)
        line1 = lines13[0].split()
        line2 = lines13[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines13[i].split()
        ws213.write_row(0,0, line1)
        ws213.write_row(1,0, line2)
        ws213.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws213.write_row(i+3,0, raw[i])
        f13.close()
        
        # Footshape 14
        f14 = open(RawFiles[14], 'r')
        lines14 = f14.readlines()
        size_arr = np.size(lines14)
        line1 = lines14[0].split()
        line2 = lines14[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines14[i].split()
        ws214.write_row(0,0, line1)
        ws214.write_row(1,0, line2)
        ws214.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws214.write_row(i+3,0, raw[i])
        f14.close()
        
        # Footshape 15
        f15 = open(RawFiles[15], 'r')
        lines15 = f15.readlines()
        size_arr = np.size(lines15)
        line1 = lines15[0].split()
        line2 = lines15[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines15[i].split()
        ws215.write_row(0,0, line1)
        ws215.write_row(1,0, line2)
        ws215.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws215.write_row(i+3,0, raw[i])
        f15.close()
        
        # Footshape 16
        f16 = open(RawFiles[16], 'r')
        lines16 = f16.readlines()
        size_arr = np.size(lines16)
        line1 = lines16[0].split()
        line2 = lines16[1].split()
        raw = np.zeros((200,201))
        for i in range(3,203):
            raw[i-3] = lines16[i].split()
        ws216.write_row(0,0, line1)
        ws216.write_row(1,0, line2)
        ws216.write_row(2,0, '$$')
        for i in range(np.shape(raw)[0]):
            ws216.write_row(i+3,0, raw[i])
        f16.close()
        
        # Hide worksheets
        ws200.hide()
        ws201.hide()
        ws202.hide()
        ws203.hide()
        ws204.hide()
        ws205.hide()
        ws206.hide()
        ws207.hide()
        ws208.hide()
        ws209.hide()
        ws210.hide()
        ws211.hide()
        ws212.hide()
        ws213.hide()
        ws214.hide()
        ws215.hide()
        ws216.hide()

if SDF == 1: 
    ws103.freeze_panes(3, 2)
    cellw = 50.0
    cellh = 18
    cellimh = 215
    ws103.set_column(0, 1, 16,format_blank) 
    ws103.set_column(2, 100, cellw,format_blank) 
    ws103.set_row(0, cellh, format_blank)
    ws103.set_row(1, cellh, format_blank)
    ws103.set_row(2, cellh, format_blank)
    ws103.set_row(3, cellimh, format_blank)
    ws103.set_row(4, cellimh, format_blank)
    for i in range(5, 28,1):     ws103.set_row(i, cellh, format_blank)
    ws103.set_row(28, cellimh, format_blank)
    for i in range(29, 32,1):     ws103.set_row(i, cellh, format_blank)
    ws103.set_row(32, cellimh, format_blank)
    ws103.set_row(35, cellimh, format_blank)
    ws103.set_row(40, cellimh, format_blank)
    ws103.set_row(45, cellimh, format_blank)
    ws103.set_row(46, cellimh, format_blank)
    ws103.set_row(47, cellimh, format_blank)
    ws103.set_row(48, cellimh, format_blank)

    sns = cwd+"/" + VT_0 + "/" + Model_0+"-D104-0001/" + Model_0 + "-D104-0001.sns"
    with open(sns) as Json: 
        Dsns = json.load(Json)

    size = Dsns["VirtualTireBasicInfo"]["TireSize"]
    pattern = Dsns["VirtualTireBasicInfo"]["Pattern"]
    ws103.write(0,0, 'SIZE', format_size_Pattern)
    ws103.write(1,0, "PATTERN", format_size_Pattern)
    ws103.write(0,1, size, format_size_Pattern)
    ws103.write(1,1, pattern, format_size_Pattern)
    VTid =  Dsns["VirtualTireBasicInfo"]["VirtualTireID"]
    ws103.write(0,2, "VT Code: "+ VTid, format_size_Pattern)

    ws103.merge_range("A3:B3", 'Model Revision', format_BG_gray_text)
    ws103.merge_range("A4:B4", 'Layout Comparison', format_size_Pattern)
    ws103.merge_range("A5:B5", 'Foot shape', format_size_Pattern)
    
    ws103.merge_range("A6:A11", 'Contact Length', format_size_Pattern)
    ws103.merge_range("A12:A15", 'Square Ratio', format_size_Pattern)
    ws103.merge_range("A16:A17", 'Contact Length Ratio(%)', format_size_Pattern)
    ws103.merge_range("A18:A23", 'Contact Width', format_size_Pattern)
    ws103.merge_range("A24:A25", 'Contact Area', format_size_Pattern)
    ws103.merge_range("A26:B26", 'Roundness', format_BG_gray_text)

    ws103.merge_range("A27:A28", 'Rib Contact Ratio', format_size_Pattern)

    ws103.merge_range("A29:B29", 'Contact pressure along center', format_size_Pattern)
    
    ws103.merge_range("A30:A32", 'Dimension', format_size_Pattern)
    ws103.merge_range("A33:B33", 'Profile', format_size_Pattern)
    ws103.merge_range("A34:B34", 'Cornering Force[N]', format_size_Pattern)
    ws103.merge_range("A35:B35", 'Aligning Moment[N-m]', format_BG_gray_text)
    ws103.merge_range("A36:B36", 'Temperature Distribution', format_size_Pattern)
    ws103.merge_range("A37:A40", 'Temperature', format_size_Pattern)
    ws103.merge_range("A41:B41", 'Hysteresis(Energy Loss Density)', format_size_Pattern)
    ws103.merge_range("A42:A45", 'Rolling Resistance', format_size_Pattern)

    ws103.merge_range("A46:B46", 'Rib Shape', format_size_Pattern)
    ws103.merge_range("A47:B47", 'Rib Contact Area(cm2)', format_size_Pattern)
    ws103.merge_range("A48:B48", 'Rib Contact Force(kgf)', format_size_Pattern)
    ws103.merge_range("A49:B49", 'Rib Contact Avg. Pressure(kPa)', format_size_Pattern)
    

    ws103.write(5, 1, "Max", format_BG_gray_text)
    ws103.write(6, 1, "Center", format_size_Pattern)
    ws103.write(7, 1, "15%", format_BG_gray_text)
    ws103.write(8, 1, "25%", format_size_Pattern)
    ws103.write(9, 1, "75%", format_BG_gray_text)
    ws103.write(10, 1, "85%", format_size_Pattern)

    ws103.write(11, 1, "15% / Center", format_BG_gray_text)
    ws103.write(12, 1, "25% / Center", format_size_Pattern)
    ws103.write(13, 1, "75% / Center", format_BG_gray_text)
    ws103.write(14, 1, "85% / Center", format_size_Pattern)
    ws103.write(15, 1, "25% / 75%", format_BG_gray_text)
    ws103.write(16, 1, "15% / 85%", format_size_Pattern)

    ws103.write(17, 1, "Max", format_BG_gray_text)
    ws103.write(18, 1, "Center", format_size_Pattern)
    ws103.write(19, 1, "15%", format_BG_gray_text)
    ws103.write(20, 1, "25%", format_size_Pattern)
    ws103.write(21, 1, "75%", format_BG_gray_text)
    ws103.write(22, 1, "85%", format_size_Pattern)

    ws103.write(23, 1, "Total", format_BG_gray_text)
    ws103.write(24, 1, "Actual", format_size_Pattern)

    ws103.write(26, 1, "Force(1st/last)", format_BG_gray_text)
    ws103.write(27, 1, "Area(1st/last)", format_size_Pattern)

    ws103.write(29, 1, "DLR", format_BG_gray_text)
    ws103.write(30, 1, "DLW", format_size_Pattern)
    ws103.write(31, 1, "DRR", format_BG_gray_text)

    ws103.write(36, 1, "Max Crown", format_size_Pattern)
    ws103.write(37, 1, "Max Bead", format_BG_gray_text)
    ws103.write(38, 1, "Belt Edge: R", format_size_Pattern)
    ws103.write(39, 1, "Belt Edge: L", format_BG_gray_text)

    ws103.write(41, 1, "Total[N]", format_size_Pattern)
    ws103.write(42, 1, "Crown[N]", format_BG_gray_text)
    ws103.write(43, 1, "BSW[N]", format_size_Pattern)
    ws103.write(44, 1, "Filler[N]", format_BG_gray_text)
    for i in range(NoModels): 
        ws103.write(2, i+2, i, format_BG_gray_text)
        ws103.write(3, i+2, "", format_size_Pattern)
        ws103.write(4, i+2, "", format_size_Pattern)
        ws103.write(5, i+2, "", format_size_Pattern)
        ws103.write(30, i+2, "", format_size_Pattern)
        ws103.write(31, i+2, "", format_size_Pattern)
        ws103.write(32, i+2, "", format_size_Pattern)
        ws103.write(33, i+2, "", format_size_Pattern)

        spec =""
        for k in range(ndv):
            spec += dv[k].name +":"
            if k == ndv-1: spec += str(format(dv[k].value[i], ".2f")) 
            else: spec += str(format(dv[k].value[i], ".2f"))  +" / "
        ws103.write(1, i+2, spec, format_size_Pattern)

        Model = lines[i].strip()
        VT = Model.split("-")[1] +"-" + Model.split("-")[2] 
        filedir = cwd+"/" + VT + "/" + Model+"-D104-0001"
        resultfile = filedir +"/" + Model + '-D104-0001-DOE-Rollingcharacteristics.txt'
        Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png"
        Profilefile = filedir + '/' + Model + "-D104-0001-ProfileCompare.png"  
        if os.path.isfile(Profilefile) == False:
            Profilefile = filedir + '/' + Model + "-D104-0001-Profilecompare.png" 
        Footshapefile = filedir + '/' + Model + "-D104-0001-Footshape.png"
        Contactpressurefile = filedir + '/' + Model + "-D104-0001-CpressGraph.png"
        Ribshapefile = filedir + '/' + Model + "-D104-0001-RibShape.png"
        Areafile = filedir + '/' + Model + "-D104-0001-Ribarea.png"
        Forcefile = filedir + '/' + Model + "-D104-0001-Ribforce.png"
        Pressurefile = filedir + '/' + Model + "-D104-0001-Ribpressure.png"

        Temperaturefile = filedir + '/' + Model + "-D104-0001-Temperature.png"
        Hysteresisfile = filedir + '/' + Model + "-D104-0001-Hysteresis.png"
        
        col_name = xlsxwriter.utility.xl_col_to_name(i+2, False)
        position = col_name+"4"
        xscale = 0.490 # cellw / wth 
        ws103.insert_image(position, Meshfile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"5"
        ws103.insert_image(position, Footshapefile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"29"
        ws103.insert_image(position, Contactpressurefile, {'x_scale':xscale, 'y_scale': xscale})

        position = col_name+"33"
        ws103.insert_image(position, Profilefile, {'x_scale': xscale, 'y_scale': xscale})

        position = col_name+"36"
        ws103.insert_image(position, Temperaturefile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"41"
        ws103.insert_image(position, Hysteresisfile, {'x_scale': xscale, 'y_scale': xscale})

        position = col_name+"46"
        ws103.insert_image(position, Ribshapefile, {'x_scale': xscale, 'y_scale': xscale})
        xscale = 0.45
        position = col_name+"47"
        ws103.insert_image(position, Areafile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"48"
        ws103.insert_image(position, Forcefile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"49"
        ws103.insert_image(position, Pressurefile, {'x_scale': xscale, 'y_scale': xscale})

        with open(resultfile) as R: 
            results = R.readlines()
        Ribforce =[]
        Ribarea = []
        Ribpress =[]
        for line in results:
            data = line.split("=")
            if 'Contact Length Max' in data[0]: ws103.write(5, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length Center' in data[0]: ws103.write(6, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Contact Length 15%' in data[0]: ws103.write(7, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length 25%' in data[0]: ws103.write(8, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Contact Length 75%' in data[0]: ws103.write(9, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length 85%' in data[0]: ws103.write(10, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Square Ratio 15%' in data[0]: ws103.write(11, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Square Ratio 25%' in data[0]: ws103.write(12, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Square Ratio 75%' in data[0]: ws103.write(13, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Square Ratio 85%' in data[0]: ws103.write(14, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Contact Length Ratio 25%/75%' in data[0]: ws103.write(15, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length Ratio 15%/85%' in data[0]: ws103.write(16, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Contact Width Max' in data[0]: ws103.write(17, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width Center' in data[0]: ws103.write(18, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Contact Width 15%' in data[0]: ws103.write(19, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width 25%' in data[0]: ws103.write(20, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Contact Width 75%' in data[0]: ws103.write(21, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width 85%' in data[0]: ws103.write(22, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Total Contact Area' in data[0]: ws103.write(23, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Actual Contact Area' in data[0]: ws103.write(24, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Roundness' in data[0]: ws103.write(25, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Rib Contact Force Ratio' in data[0]: ws103.write(26, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Rib Contact Area Ratio' in data[0]: ws103.write(27, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'DLR' in data[0]: ws103.write(29, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'DLW' in data[0]: ws103.write(30, i+2, float(data[1].strip()), format_size_Pattern)
            if 'DRR' in data[0]: ws103.write(31, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Cornering Force' in data[0]: 
                data = data[1].replace("-","") #remove minus sign from Cornering Force
                ws103.write(33, i+2, float(data.strip()), format_size_Pattern)
                # ws103.write(33, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Aligning Moment' in data[0]: ws103.write(34, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Temperature Max Crown' in data[0]: ws103.write(36, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Temperature Max Bead' in data[0]: ws103.write(37, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Temperature Belt Edge Right' in data[0]: ws103.write(38, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Temperature Belt Edge Left' in data[0]: ws103.write(39, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Energy Loss Total' in data[0]: ws103.write(41, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Energy Loss Crown' in data[0]: ws103.write(42, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Energy Loss Sidewall' in data[0]: ws103.write(43, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Energy Loss Filler' in data[0]: ws103.write(44, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Rib' in data[0] and 'Force[kgf]' in data[0] : Ribforce.append(float(data[1].strip()))
            if 'Rib' in data[0] and 'Area[cm2]' in data[0] : Ribarea.append(float(data[1].strip()))
            if 'Rib' in data[0] and 'Press[kPa]' in data[0] : Ribpress.append(float(data[1].strip()))

            if 'Rib' in data[0] and 'Force[kgf]' in data[0]: ws103.write(48+len(Ribforce), i+2, float(data[1].strip()), format_size_Pattern)
            if 'Rib' in data[0] and 'Area[cm2]' in data[0]: ws103.write(48+len(Ribforce)+len(Ribarea), i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Rib' in data[0] and 'Press[kPa]' in data[0]: ws103.write(48+len(Ribforce)+len(Ribarea) + len(Ribpress), i+2, float(data[1].strip()), format_size_Pattern)

    NoRibs = len(Ribforce)
    if NoRibs > 1: 
        # print (NoRibs)
        rowrange = 'A'+str(50) + ":" + 'A'+str (50+NoRibs-1)
        # print ("1", rowrange)
        ws103.merge_range(rowrange, 'Rib Force', format_size_Pattern)
        for k in range (NoRibs): ws103.write(49+k, 1, "#"+str(k+1), format_size_Pattern)

        rowrange = 'A'+str(50+NoRibs) + ":" + 'A'+str (50+2*NoRibs-1)
        ws103.merge_range(rowrange, 'Rib Area', format_BG_gray_text)
        for k in range (NoRibs): ws103.write(49+NoRibs+k, 1, "#"+str(k+1), format_BG_gray_text)
        # print ("2", rowrange)
        rowrange = 'A'+str(50+2*NoRibs) + ":" + 'A'+str (50+3*NoRibs-1)
        ws103.merge_range(rowrange, 'Rib Pressure', format_size_Pattern)
        for k in range (NoRibs): ws103.write(49+2*NoRibs+k, 1, "#"+str(k+1), format_size_Pattern)
        # print ("3", rowrange)

    else:
        ws103.write(49, 0, "Rib Force(kgf)", format_size_Pattern)
        ws103.write(49, 1, "#1", format_size_Pattern)

        ws103.write(50, 0, "Rib Area(cm2)", format_size_Pattern)
        ws103.write(50, 1, "#1", format_size_Pattern)

        ws103.write(51, 0, "Rib Pressure(kPa)", format_size_Pattern)
        ws103.write(51, 1, "#1", format_size_Pattern)

if SRR == 1: 
    ws104.freeze_panes(3, 2)
    cellw = 50.0
    ws104.set_column(0, 1, 16,format_blank) 
    ws104.set_column(2, 100, cellw,format_blank) 
    ws104.set_row(0, 20, format_blank)
    ws104.set_row(1, 20, format_blank)
    ws104.set_row(2, 20, format_blank)
    ws104.set_row(3, 225, format_blank)
    ws104.set_row(4, 225, format_blank)
    for i in range(5, 8,1):     ws104.set_row(i, 20, format_blank)
    ws104.set_row(8, 225, format_blank)
    for i in range(9, 18,1):   ws104.set_row(i, 20, format_blank)
    rowT = 19
    ws104.set_row(rowT-1, 225, format_blank)
    for i in range(rowT, rowT+4,1):   ws104.set_row(i, 20, format_blank)

    sns = cwd+"/" + VT_0 + "/" + Model_0+"-D102-0001/" + Model_0 + "-D102-0001.sns"
    with open(sns) as Json: 
        Dsns = json.load(Json)

    size = Dsns["VirtualTireBasicInfo"]["TireSize"]
    pattern = Dsns["VirtualTireBasicInfo"]["Pattern"]
    ws104.write(0,0, 'SIZE', format_size_Pattern)
    ws104.write(1,0, "PATTERN", format_size_Pattern)
    ws104.write(0,1, size, format_size_Pattern)
    ws104.write(1,1, pattern, format_size_Pattern)
    VTid =  Dsns["VirtualTireBasicInfo"]["VirtualTireID"]
    ws104.write(0,2, "VT Code: "+ VTid, format_size_Pattern)

    ws104.merge_range("A3:B3", 'Model Revision', format_BG_gray_text)
    ws104.merge_range("A4:B4", 'Layout Comparison', format_size_Pattern)
    ws104.merge_range("A5:B5", 'Profile', format_size_Pattern)
    ws104.merge_range("A6:A8", 'Dimension', format_size_Pattern)
    ws104.merge_range("A9:B9", 'Hysteresis(Energy Loss Density)', format_size_Pattern)
    ws104.merge_range("A10:A18", 'Rolling Resistance', format_size_Pattern)

    ws104.merge_range("A19:B19", 'Temperature Distribution', format_size_Pattern)
    ws104.merge_range("A20:A23", 'Temperature', format_size_Pattern)

    ws104.write(5, 1, "DLR", format_BG_gray_text)
    ws104.write(6, 1, "DLW", format_size_Pattern)
    ws104.write(7, 1, "DRR", format_BG_gray_text)

    ws104.write(9, 1, "RRc", format_BG_gray_text)
    ws104.write(10, 1, "Total [N]", format_size_Pattern)
    ws104.write(11, 1, "CTB", format_BG_gray_text)
    ws104.write(12, 1, "SUT", format_size_Pattern)
    ws104.write(13, 1, "BTT", format_BG_gray_text)
    ws104.write(14, 1, "L11", format_size_Pattern)
    ws104.write(15, 1, "CCT", format_BG_gray_text)
    ws104.write(16, 1, "Filler", format_size_Pattern)
    ws104.write(17, 1, "BSW", format_BG_gray_text)

    ws104.write(19, 1, "Max Crown", format_BG_gray_text)
    ws104.write(20, 1, "Max Bead", format_size_Pattern)
    ws104.write(21, 1, "Belt Edge:R", format_BG_gray_text)
    ws104.write(22, 1, "Belt Edge:L", format_size_Pattern)

    for i in range(NoModels): 
        ws104.write(2, i+2, i, format_BG_gray_text)
        ws104.write(3, i+2, "", format_size_Pattern)
        ws104.write(4, i+2, "", format_size_Pattern)
        ws104.write(8, i+2, "", format_size_Pattern)
        ws104.write(18, i+2, "", format_size_Pattern)

        spec =""
        for k in range(ndv):
            spec += dv[k].name +":"
            if k == ndv-1: spec += str(format(dv[k].value[i], ".2f")) 
            else: spec += str(format(dv[k].value[i], ".2f"))  +" / "
        ws104.write(1, i+2, spec, format_size_Pattern)


        Model = lines[i].strip()
        VT = Model.split("-")[1] +"-" + Model.split("-")[2] 
        filedir = cwd+"/" + VT + "/" + Model+"-D102-0001"
        resultfile = filedir +"/" + Model + '-D102-0001-RR.txt'
        ComponentRRfile = filedir +"/" + Model + '-D102-0001-RRValue.txt'
        Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png"
        Profilefile = filedir + '/' + Model + "-D102-0001-ProfileCompare.png"  
        if os.path.isfile(Profilefile) == False:
            Profilefile = filedir + '/' + Model + "-D102-0001-Profilecompare.png" 

        Temperaturefile = filedir + '/' + Model + "-D102-0001-Temperature.png"
        Hysteresisfile = filedir + '/' + Model + "-D102-0001-Hysteresis.png"
        
        col_name = xlsxwriter.utility.xl_col_to_name(i+2, False)
        position = col_name+"4"
        xscale = 0.490 # cellw / wth 
        ws104.insert_image(position, Meshfile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"5"
        ws104.insert_image(position, Profilefile, {'x_scale': xscale, 'y_scale': xscale})
        position = col_name+"9"
        ws104.insert_image(position, Hysteresisfile, {'x_scale':xscale, 'y_scale': xscale})

        position = col_name+"19"
        ws104.insert_image(position, Temperaturefile, {'x_scale': xscale, 'y_scale': xscale})


        with open(resultfile) as R: 
            results = R.readlines()
        for line in results:
            data = line.split("=")
            if 'DLR' in data[0]: ws104.write(5, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'DLW' in data[0]: ws104.write(6, i+2,float(data[1].strip()), format_size_Pattern)
            if 'DRR' in data[0]: ws104.write(7, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Temperature Max Crown' in data[0]: ws104.write(19, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Temperature Max Bead' in data[0]: ws104.write(20, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Temperature Belt Edge R' in data[0]: ws104.write(21, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Temperature Belt Edge L' in data[0]: ws104.write(22, i+2, float(data[1].strip()), format_size_Pattern)

        with open(ComponentRRfile) as R: 
            results = R.readlines()

        RRc = 0.0;         TOT = 0.0
        CTB = 0.0;         SUT = 0.0
        BTT = 0.0;         L11 = 0.0
        CCT = 0.0;         FIL = 0.0
        BSW = 0.0

        for k, line in enumerate(results):
            data = line.split("\t")
            # print (data)
            if 'RRc' in data[0]: 
                data = line.split("=")
                ws104.write(9, i+2,float(data[1].strip()), format_BG_gray_text)
            if 'VOLUME(m^3), Total_RR(N)' in line: 
                data = results[k+1].split("\t")
                # print (data)
                ws104.write(10, i+2, float(data[2].strip()), format_size_Pattern)
            

            if 'CTB' in data[0]: ws104.write(11, i+2, float(data[4].strip()), format_BG_gray_text)
            if 'SUT' in data[0]: ws104.write(12, i+2, float(data[4].strip()), format_size_Pattern)
            if 'BTT' in data[0]: ws104.write(13, i+2, float(data[4].strip()), format_BG_gray_text)
            if 'L11' in data[0]: ws104.write(14, i+2, float(data[4].strip()), format_size_Pattern)
            if 'CCT' in data[0]: ws104.write(15, i+2, float(data[4].strip()), format_BG_gray_text)
            if 'FIL' in data[0]: FIL += float(data[4].strip())
            if 'UBF' in data[0]: FIL += float(data[4].strip())
            if 'LBF' in data[0]: FIL += float(data[4].strip())
            if 'BSW' in data[0]: ws104.write(17, i+2, float(data[4].strip()), format_BG_gray_text)
        ws104.write(16, i+2, FIL, format_size_Pattern)

if SEN == 1: 
    ws105.freeze_panes(3, 2)
    cellw = 50.0
    ws105.set_column(0, 1, 16,format_blank) 
    ws105.set_column(2, 100, cellw,format_blank) 
    ws105.set_row(0, 20, format_blank)
    ws105.set_row(1, 20, format_blank)
    ws105.set_row(2, 20, format_blank)
    ws105.set_row(3, 225, format_blank)
    for i in range(4, 15,1):     ws105.set_row(i, 20, format_blank)

    sns = cwd+"/" + VT_0 + "/" + Model_0+"-S106-0001/" + Model_0 + "-S106-0001.sns"
    with open(sns) as Json: 
        Dsns = json.load(Json)

    size = Dsns["VirtualTireBasicInfo"]["TireSize"]
    pattern = Dsns["VirtualTireBasicInfo"]["Pattern"]
    ws105.write(0,0, 'SIZE', format_size_Pattern)
    ws105.write(1,0, "PATTERN", format_size_Pattern)
    ws105.write(0,1, size, format_size_Pattern)
    ws105.write(1,1, pattern, format_size_Pattern)
    VTid =  Dsns["VirtualTireBasicInfo"]["VirtualTireID"]
    ws105.write(0,2, "VT Code: "+ VTid, format_size_Pattern)

    ws105.merge_range("A3:B3", 'Model Revision', format_BG_gray_text)
    ws105.merge_range("A4:B4", 'Layout Comparison', format_size_Pattern)
    dataStart = 5
    dRange = "A%d:B%d"%(dataStart+0, dataStart+0); ws105.merge_range(dRange, "Belt Edge Strain", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+1, dataStart+1); ws105.merge_range(dRange, "Belt Edge Temperature", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+2, dataStart+2); ws105.merge_range(dRange, "Belt Edge Life index", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+3, dataStart+3); ws105.merge_range(dRange, "Reinforcement Belt Strain", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+4, dataStart+4); ws105.merge_range(dRange, "Reinforcement Belt Temperature", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+5, dataStart+5); ws105.merge_range(dRange, "Reinforcement Belt Life index", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+6, dataStart+6); ws105.merge_range(dRange, "Upper Carcass Strain", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+7, dataStart+7); ws105.merge_range(dRange, "Upper Carcass Temperature", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+8, dataStart+8); ws105.merge_range(dRange, "Upper Carcass Life index", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+9, dataStart+9); ws105.merge_range(dRange, "Lower Carcass Strain", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+10, dataStart+10); ws105.merge_range(dRange, "Lower Carcass Temperature", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+11, dataStart+11); ws105.merge_range(dRange, "Lower Carcass Life index", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+12, dataStart+12); ws105.merge_range(dRange, "Carcass Turn Up Strain", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+13, dataStart+13); ws105.merge_range(dRange, "Carcass Turn Up Temperature", format_size_Pattern)
    dRange = "A%d:B%d"%(dataStart+14, dataStart+14); ws105.merge_range(dRange, "Carcass Turn Up Life index", format_size_Pattern)

    enduranceResult = cwd+"/" + doeid+"-LongTermEndurance.txt"
    with open(enduranceResult) as R: 
        results = R.readlines()

    for i in range(NoModels): 
        ws105.write(2, i+2, i, format_BG_gray_text)
        ws105.write(3, i+2, "", format_size_Pattern)

        spec =""
        for k in range(ndv):
            spec += dv[k].name +":"
            if k == ndv-1: spec += str(format(dv[k].value[i], ".2f")) 
            else: spec += str(format(dv[k].value[i], ".2f"))  +" / "
        ws105.write(1, i+2, spec, format_size_Pattern)


        Model = lines[i].strip()
        VT = Model.split("-")[1] +"-" + Model.split("-")[2] 
        filedir = cwd+"/" + VT + "/" + Model+"-S106-0001"
        resultfile = filedir +"/" + Model + '-S106-0001-LongTermEndurance.txt'
        Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png"
        if os.path.isfile(Meshfile) == False:
            Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png" 
        
        
        col_name = xlsxwriter.utility.xl_col_to_name(i+2, False)
        position = col_name+"4"
        xscale = 0.490 # cellw / wth 
        ws105.insert_image(position, Meshfile, {'x_scale': xscale, 'y_scale': xscale})

        
        for line in results:
            data = line.split("=")
            if int(data[0].split(",")[0].strip()) == i: 
                # print ("Endurance Results", line.strip(), ">", data[1])
                if 'BT Edge Strain' in data[0]: ws105.write(dataStart-1, i+2, float(data[1].strip()), format_BG_gray_text)
                if 'BT Edge Temperature' in data[0]: ws105.write(dataStart, i+2,float(data[1].strip()), format_size_Pattern)
                if 'BT Edge Life Index' in data[0]: ws105.write(dataStart+1, i+2, float(data[1].strip()), format_BG_gray_text)

                if 'Re-BT Strain' in data[0]: ws105.write(dataStart+2, i+2, float(data[1].strip()), format_size_Pattern)
                if 'Re-BT Temperature' in data[0]: ws105.write(dataStart+3, i+2,float(data[1].strip()), format_BG_gray_text)
                if 'Re-BT Life Index' in data[0]: ws105.write(dataStart+4, i+2, float(data[1].strip()), format_size_Pattern)

                if 'Upper Cc Area Strain' in data[0]: ws105.write(dataStart+5, i+2, float(data[1].strip()), format_BG_gray_text)
                if 'Upper Cc Area Temperature' in data[0]: ws105.write(dataStart+6, i+2,float(data[1].strip()), format_size_Pattern)
                if 'Upper Cc Area Life Index' in data[0]: ws105.write(dataStart+7, i+2, float(data[1].strip()), format_BG_gray_text)

                if 'Low Cc Area Strain' in data[0]: ws105.write(dataStart+8, i+2, float(data[1].strip()), format_size_Pattern)
                if 'Low Cc Area Temperature' in data[0]: ws105.write(dataStart+9, i+2,float(data[1].strip()), format_BG_gray_text)
                if 'Low Cc Area Life Index' in data[0]: ws105.write(dataStart+10, i+2, float(data[1].strip()), format_size_Pattern)

                if 'Cc Turn Up Strain' in data[0]: ws105.write(dataStart+11, i+2, float(data[1].strip()), format_BG_gray_text)
                if 'Cc Turn Up Temperature' in data[0]: ws105.write(dataStart+12, i+2,float(data[1].strip()), format_size_Pattern)
                if 'Cc Turn Up Life Index' in data[0]: ws105.write(dataStart+13, i+2, float(data[1].strip()), format_BG_gray_text)
            else:
                continue 

if SSS == 1: 
    simCode = "S104"

    sns = cwd+"/" + VT_0 + "/" + Model_0+"-"+simCode+"-0001/" + Model_0 +"-"+simCode+"-0001.sns"
    with open(sns) as Json: 
        Dsns = json.load(Json)

    resultfile = sns[:-4] + '-StaticStiffness.txt'
    isOldStiffness=0
    if not os.path.isfile(resultfile): 
        resultfile = sns[:-4] +'-StaticStiffnessENDU.txt'
        isOldStiffness =1 

    ws106.freeze_panes(3, 2)
    cellw = 50.0
    ws106.set_column(0, 1, 16,format_blank) 
    ws106.set_column(2, 100, cellw,format_blank) 
    ws106.set_row(0, 20, format_blank)
    ws106.set_row(1, 20, format_blank)
    ws106.set_row(2, 20, format_blank)
    ws106.set_row(3, 225, format_blank)
    for i in range(4, 15,1):     ws106.set_row(i, 20, format_blank)

    

    size = Dsns["VirtualTireBasicInfo"]["TireSize"]
    pattern = Dsns["VirtualTireBasicInfo"]["Pattern"]
    ws106.write(0,0, 'SIZE', format_size_Pattern)
    ws106.write(1,0, "PATTERN", format_size_Pattern)
    ws106.write(0,1, size, format_size_Pattern)
    ws106.write(1,1, pattern, format_size_Pattern)
    VTid =  Dsns["VirtualTireBasicInfo"]["VirtualTireID"]
    ws106.write(0,2, "VT Code: "+ VTid, format_size_Pattern)

    ws106.merge_range("A3:B3", 'Model Revision', format_BG_gray_text)
    ws106.merge_range("A4:B4", 'Layout Comparison', format_size_Pattern)
    ws106.merge_range("A5:B5", 'KV (kgf/mm)', format_size_Pattern)
    ws106.merge_range("A6:B6", 'KL (kgf/mm)', format_size_Pattern)
    ws106.merge_range("A7:B7", 'KD (kgf*m/rad)', format_size_Pattern)
    ws106.merge_range("A8:B8", 'KT (kgf/mm)', format_size_Pattern)
    ws106.merge_range("A9:B9", 'KV Linear Assumption (kgf/mm)', format_size_Pattern)

    tiregroup = Dsns["VirtualTireBasicInfo"]["ProductLine"]
    if tiregroup == "TBR": ws106.merge_range("A10:A11", "#3 BT Edge", format_size_Pattern)
    else:                  ws106.merge_range("A10:A11", "#2 BT Edge", format_size_Pattern)
    ws106.merge_range("A12:A13", 'Filler', format_size_Pattern)
    ws106.merge_range("A14:A15", 'BSW', format_size_Pattern)

    stressline = 9 
    ws106.write(stressline, 1, "SED Max (kJ/m3)", format_BG_gray_text)
    ws106.write(stressline+1, 1, "SED Amp (kJ/m3)", format_size_Pattern)
    ws106.write(stressline+2, 1, "Tresca Max (MPa)", format_BG_gray_text)
    ws106.write(stressline+3, 1, "Tresca Amp (MPa)", format_size_Pattern)
    ws106.write(stressline+4, 1, "PLE Max", format_BG_gray_text)
    ws106.write(stressline+5, 1, "PLE Amp", format_size_Pattern)


    stiffResult = cwd+"/" + doeid+"-StaticStiffness.txt"
    with open(stiffResult) as R: 
        results = R.readlines()


    for i in range(NoModels): 
        ws106.write(2, i+2, i, format_BG_gray_text)
        ws106.write(3, i+2, "", format_size_Pattern)

        spec =""
        for k in range(ndv):
            spec += dv[k].name +":"
            if k == ndv-1: spec += str(format(dv[k].value[i], ".2f")) 
            else: spec += str(format(dv[k].value[i], ".2f"))  +" / "
        ws106.write(1, i+2, spec, format_size_Pattern)


        Model = lines[i].strip()
        VT = Model.split("-")[1] +"-" + Model.split("-")[2] 
        filedir = cwd+"/" + VT + "/" + Model+"-"+simCode+"-0001"
        resultfile =    filedir +"/" + Model+"-"+simCode +'-0001-StaticStiffness.txt'
        
        Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png"
        if os.path.isfile(Meshfile) == False:
            Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png" 
        
        
        col_name = xlsxwriter.utility.xl_col_to_name(i+2, False)
        position = col_name+"4"
        xscale = 0.490 # cellw / wth 
        ws106.insert_image(position, Meshfile, {'x_scale': xscale, 'y_scale': xscale})

        
        for line in results:
            data = line.split("=")
            if int(data[0].split(",")[0].strip()) == i: 
                if 'Vertical Stiffness' in data[0]: ws106.write(4, i+2, float(data[1].strip()), format_BG_gray_text)
                if 'Lateral Stiffness' in data[0]: ws106.write(5, i+2,float(data[1].strip()), format_size_Pattern)
                if 'Tortional Stiffness' in data[0]: ws106.write(6, i+2, float(data[1].strip()), format_BG_gray_text)
                if 'Tractional Stiffness' in data[0]: ws106.write(7, i+2,float(data[1].strip()), format_size_Pattern)
                if 'Linear Assump. KV' in data[0]: ws106.write(8, i+2,float(data[1].strip()), format_BG_gray_text)

                if 'SED Max Value' in data[0]: ws106.write(stressline, i+2, float(data[1].strip()), format_size_Pattern)
                if 'SED Amplitude' in data[0]: ws106.write(stressline+1, i+2,float(data[1].strip()), format_BG_gray_text)

                if 'Tresca Max' in data[0]: ws106.write(stressline+2, i+2, float(data[1].strip()), format_size_Pattern)
                if 'Tresca Amplitude' in data[0]: ws106.write(stressline+3, i+2,float(data[1].strip()), format_BG_gray_text)

                if 'PLE Max' in data[0]: ws106.write(stressline+4, i+2, float(data[1].strip()), format_size_Pattern)
                if 'PLE Amplitude' in data[0]: ws106.write(stressline+5, i+2,float(data[1].strip()), format_BG_gray_text)

if SCS ==1:  ## cornering stiffness 
    simCode = "D205"
    ws107.freeze_panes(3, 2)
    cellw = 50.0
    cellh = 18
    cellimh = 215
    ws107.set_column(0, 1, 16,format_blank) 
    ws107.set_column(2, 100, cellw,format_blank) 
    ws107.set_row(0, cellh, format_blank)
    ws107.set_row(1, cellh, format_blank)
    ws107.set_row(2, cellh, format_blank)
    ws107.set_row(3, cellimh, format_blank)

    ws107.set_row(4, cellh, format_blank)
    ws107.set_row(5, cellh, format_blank)

    ws107.set_row(4+2, cellimh, format_blank)
    for i in range(5+2, 28+2,1):     ws107.set_row(i, cellh, format_blank)
    ws107.set_row(28+2, cellimh, format_blank)
    for i in range(29+2, 32+2,1):     ws107.set_row(i, cellh, format_blank)
    ws107.set_row(32+2, cellimh, format_blank)
    ws107.set_row(35+2, cellimh, format_blank)
    ws107.set_row(40+2, cellimh, format_blank)
    ws107.set_row(45+2, cellimh, format_blank)
    ws107.set_row(46+2, cellimh, format_blank)
    ws107.set_row(47+2, cellimh, format_blank)
    ws107.set_row(48+2, cellimh, format_blank)

    # sns = cwd+"/" + VT_0 + "/" + Model_0+"-%s-0001/"%(simCode) + Model_0 + "-%s-0001.sns"%(simCode)
    sns = cwd +"/" + VT_0 + "/"+RefModelVT+"-"+simCode+"-0001/"+RefModelVT+"-"+simCode+"-0001.sns"
    # print("SDF", sns)
    with open(sns) as Json: 
        Dsns = json.load(Json)

    size = Dsns["VirtualTireBasicInfo"]["TireSize"]
    pattern = Dsns["VirtualTireBasicInfo"]["Pattern"]
    ws107.write(0,0, 'SIZE', format_size_Pattern)
    ws107.write(1,0, "PATTERN", format_size_Pattern)
    ws107.write(0,1, size, format_size_Pattern)
    ws107.write(1,1, pattern, format_size_Pattern)
    VTid =  Dsns["VirtualTireBasicInfo"]["VirtualTireID"]
    ws107.write(0,2, "VT Code: "+ VTid, format_size_Pattern)

    nLine = 3; drange = "A%d:B%d"%(nLine, nLine)
    ws107.merge_range(drange, 'Model Revision', format_BG_gray_text)
    nLine += 1; drange = "A%d:B%d"%(nLine, nLine)
    ws107.merge_range(drange, 'Layout Comparison', format_size_Pattern)

    ##########################
    nLine += 1; drange = "A%d:B%d"%(nLine, nLine)
    ws107.merge_range(drange, 'Cornering Stiffness', format_size_Pattern)
    nLine += 1; drange = "A%d:B%d"%(nLine, nLine)
    ws107.merge_range(drange, 'Aligning-Moment Stiffness', format_size_Pattern)
    ##########################

    nLine += 1; drange = "A%d:B%d"%(nLine, nLine)
    ws107.merge_range(drange, 'Foot shape', format_size_Pattern)
    
    nLine += 1; nxLine=nLine+5; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Contact Length', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine+3; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Square Ratio', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine+1; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Contact Length Ratio(%)', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine+5; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Contact Width', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine+1; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Contact Area', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Roundness', format_BG_gray_text)

    nLine = nxLine + 1
    nxLine=nLine+1; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Rib Contact Ratio', format_size_Pattern)

    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Contact pressure along center', format_size_Pattern)
    
    nLine = nxLine + 1
    nxLine=nLine+2; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Dimension', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Profile', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Cornering Force[N]', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Aligning Moment[N-m]', format_BG_gray_text)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Temperature Distribution', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine+3; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Temperature', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Hysteresis(Energy Loss Density)', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine+3; drange = "A%d:A%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Rolling Resistance', format_size_Pattern)

    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Rib Shape', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Rib Contact Area(cm2)', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Rib Contact Force(kgf)', format_size_Pattern)
    nLine = nxLine + 1
    nxLine=nLine; drange = "A%d:B%d"%(nLine, nxLine)
    ws107.merge_range(drange, 'Rib Contact Avg. Pressure(kPa)', format_size_Pattern)
    
    nLine = 5+2
    ws107.write(nLine, 1, "Max", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "Center", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "15%", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "25%", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "75%", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "85%", format_size_Pattern); nLine+= 1

    ws107.write(nLine, 1, "15% / Center", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "25% / Center", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "75% / Center", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "85% / Center", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "25% / 75%", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "15% / 85%", format_size_Pattern); nLine+= 1

    ws107.write(nLine, 1, "Max", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "Center", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "15%", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "25%", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "75%", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "85%", format_size_Pattern); nLine+= 1

    ws107.write(nLine, 1, "Total", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "Actual", format_size_Pattern); nLine+= 2

    ws107.write(nLine, 1, "Force(1st/last)", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "Area(1st/last)", format_size_Pattern); nLine+= 2

    ws107.write(nLine, 1, "DLR", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "DLW", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "DRR", format_BG_gray_text); nLine+= 5

    ws107.write(nLine, 1, "Max Crown", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "Max Bead", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "Belt Edge: R", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "Belt Edge: L", format_BG_gray_text); nLine+= 2

    ws107.write(nLine, 1, "Total[N]", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "Crown[N]", format_BG_gray_text); nLine+= 1
    ws107.write(nLine, 1, "BSW[N]", format_size_Pattern); nLine+= 1
    ws107.write(nLine, 1, "Filler[N]", format_BG_gray_text); nLine+= 1
    nLine =2
    for i in range(NoModels): 
        ws107.write(nLine, i+2, i, format_BG_gray_text); nLine+= 1
        ws107.write(nLine, i+2, "", format_size_Pattern); nLine+= 1
        ws107.write(nLine, i+2, "", format_size_Pattern); nLine+= 1
        ws107.write(nLine, i+2, "", format_size_Pattern); nLine = 25
        ws107.write(nLine, i+2, "", format_size_Pattern); nLine+= 1
        ws107.write(nLine, i+2, "", format_size_Pattern); nLine+= 1
        ws107.write(nLine, i+2, "", format_size_Pattern); nLine+= 1
        ws107.write(nLine, i+2, "", format_size_Pattern)

        spec =""
        for k in range(ndv):
            spec += dv[k].name +":"
            if k == ndv-1: spec += str(format(dv[k].value[i], ".2f")) 
            else: spec += str(format(dv[k].value[i], ".2f"))  +" / "
        ws107.write(1, i+2, spec, format_size_Pattern)

        Model = lines[i].strip()
        
        VT = Model.split("-")[1] +"-" + Model.split("-")[2] 
        filedir = cwd+"/" + VT + "/" + Model+"-%s-0001"%(simCode)
        resultfile = filedir +"/" + Model + '-%s-0001-DOE-CorneringStiffness.txt'%(simCode)
        Meshfile = filedir + '/' + VT + "-DOELayoutCompare.png"
        Profilefile = filedir + '/' + Model + "-%s-0001-CS001-ProfileCompare.png"%(simCode)
        if os.path.isfile(Profilefile) == False:
            Profilefile = filedir + '/' + Model + "-%s-0001-CS001-Profilecompare.png"%(simCode)
        Footshapefile = filedir + '/' + Model + "-%s-0001-CS001-Footshape.png"%(simCode)
        Contactpressurefile = filedir + '/' + Model + "-%s-0001-CS001-CpressGraph.png"%(simCode)
        Ribshapefile = filedir + '/' + Model + "-%s-0001-CS001-RibShape.png"%(simCode)
        Areafile = filedir + '/' + Model + "-%s-0001-CS001-Ribarea.png"%(simCode)
        Forcefile = filedir + '/' + Model + "-%s-0001-CS001-Ribforce.png"%(simCode)
        Pressurefile = filedir + '/' + Model + "-%s-0001-CS001-Ribpressure.png"%(simCode)

        Temperaturefile = filedir + '/' + Model + "-%s-0001-CS001-Temperature.png"%(simCode)
        Hysteresisfile = filedir + '/' + Model + "-%s-0001-CS001-Hysteresis.png"%(simCode)
        
        nLine=4+2
        col_name = xlsxwriter.utility.xl_col_to_name(i+2, False)
        position = col_name+str(nLine)
        xscale = 0.490 # cellw / wth 

        
        ws107.insert_image(position, Meshfile, {'x_scale': xscale, 'y_scale': xscale})
        nLine += 1
        position = col_name+str(nLine)
        ws107.insert_image(position, Footshapefile, {'x_scale': xscale, 'y_scale': xscale})
        nLine += 24
        position = col_name+str(nLine)
        ws107.insert_image(position, Contactpressurefile, {'x_scale':xscale, 'y_scale': xscale})

        nLine += 4
        position = col_name+str(nLine)
        ws107.insert_image(position, Profilefile, {'x_scale': xscale, 'y_scale': xscale})
        nLine += 3
        position = col_name+str(nLine)
        ws107.insert_image(position, Temperaturefile, {'x_scale': xscale, 'y_scale': xscale})
        nLine += 5
        position = col_name+str(nLine)
        ws107.insert_image(position, Hysteresisfile, {'x_scale': xscale, 'y_scale': xscale})

        nLine += 5
        position = col_name+str(nLine)
        ws107.insert_image(position, Ribshapefile, {'x_scale': xscale, 'y_scale': xscale})
        xscale = 0.45
        nLine += 1
        position = col_name+str(nLine)
        ws107.insert_image(position, Areafile, {'x_scale': xscale, 'y_scale': xscale})
        nLine += 1
        position = col_name+str(nLine)
        ws107.insert_image(position, Forcefile, {'x_scale': xscale, 'y_scale': xscale})
        nLine += 1
        position = col_name+str(nLine)
        ws107.insert_image(position, Pressurefile, {'x_scale': xscale, 'y_scale': xscale})

        with open(resultfile) as R: 
            results = R.readlines()
        Ribforce =[]
        Ribarea = []
        Ribpress =[]

        nLine = 4

        row_Ca = nLine; nLine+= 1
        row_Aa = nLine; nLine+= 2

        row_ContactLenMax = nLine; nLine+= 1
        row_ContactLenCen = nLine; nLine+= 1
        row_ContactLen15 = nLine; nLine+= 1
        row_ContactLen25 = nLine; nLine+= 1
        row_ContactLen75 = nLine; nLine+= 1
        row_ContactLen85 = nLine; nLine+= 1

        row_SquRatio15 = nLine; nLine+= 1
        row_SquRatio25 = nLine; nLine+= 1
        row_SquRatio75 = nLine; nLine+= 1
        row_SquRatio85 = nLine; nLine+= 1

        row_LR2575 =  nLine; nLine+= 1
        row_LR1585 =  nLine; nLine+= 1

        row_ContactWidthMax=nLine; nLine+= 1
        row_ContactWidthCen=nLine; nLine+= 1
        row_ContactWidth15=nLine; nLine+= 1
        row_ContactWidth25=nLine; nLine+= 1
        row_ContactWidth75=nLine; nLine+= 1
        row_ContactWidth85=nLine; nLine+= 1

        row_TotalContactArea=nLine; nLine+=1
        row_ActualContactArea=nLine; nLine+=1
        row_roundness=nLine; nLine+=1

        row_ForceContactRatio=nLine; nLine+=1
        row_AreaContactRatio=nLine; nLine+=2

        row_DLR=nLine; nLine+=1
        row_DLW=nLine; nLine+=1
        row_DRR=nLine; nLine+=2

        row_CorneringForce=nLine; nLine+=1
        row_Aligning=nLine; nLine+=2

        row_TempCrown=nLine; nLine+=1
        row_TempBead=nLine; nLine+=1
        row_TempBTRight=nLine; nLine+=1
        row_TempBTLeft=nLine; nLine+=2

        row_ELossTotal=nLine; nLine+=1
        row_ELossCrown=nLine; nLine+=1
        row_ELossSide=nLine; nLine+=1
        row_ELossFiller=nLine; nLine+=4

        row_Rib = nLine 

        for line in results:
            data = line.split("=")
            if 'Cornering Stiffness' in data[0]: ws107.write(row_Ca, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Aligning-Moment Stiffness' in data[0]: ws107.write(row_Aa, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Contact Length Max' in data[0]: ws107.write(row_ContactLenMax, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length Center' in data[0]: ws107.write(row_ContactLenCen, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Contact Length 15%' in data[0]: ws107.write(row_ContactLen15, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length 25%' in data[0]: ws107.write(row_ContactLen25, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Contact Length 75%' in data[0]: ws107.write(row_ContactLen75, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length 85%' in data[0]: ws107.write(row_ContactLen85, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Square Ratio 15%' in data[0]: ws107.write(row_SquRatio15, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Square Ratio 25%' in data[0]: ws107.write(row_SquRatio25, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Square Ratio 75%' in data[0]: ws107.write(row_SquRatio75, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Square Ratio 85%' in data[0]: ws107.write(row_SquRatio85, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Contact Length Ratio 25%/75%' in data[0]: ws107.write(row_LR2575, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Length Ratio 15%/85%' in data[0]: ws107.write(row_LR1585, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Contact Width Max' in data[0]: ws107.write(row_ContactWidthMax, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width Center' in data[0]: ws107.write(row_ContactWidthCen, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Contact Width 15%' in data[0]: ws107.write(row_ContactWidth15, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width 25%' in data[0]: ws107.write(row_ContactWidth25, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Contact Width 75%' in data[0]: ws107.write(row_ContactWidth75, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Contact Width 85%' in data[0]: ws107.write(row_ContactWidth85, i+2, float(data[1].strip()), format_size_Pattern)

            if 'Total Contact Area' in data[0]: ws107.write(row_TotalContactArea, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Actual Contact Area' in data[0]: ws107.write(row_ActualContactArea, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Roundness' in data[0]: ws107.write(row_roundness, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Rib Contact Force Ratio' in data[0]: ws107.write(row_ForceContactRatio, i+2,float(data[1].strip()), format_size_Pattern)
            if 'Rib Contact Area Ratio' in data[0]: ws107.write(row_AreaContactRatio, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'DLR' in data[0]: ws107.write(row_DLR, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'DLW' in data[0]: ws107.write(row_DLW, i+2, float(data[1].strip()), format_size_Pattern)
            if 'DRR' in data[0]: ws107.write(row_DRR, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Cornering Force' in data[0]: 
                data = data[1].replace("-","") #remove minus sign from Cornering Force
                ws107.write(row_CorneringForce, i+2, float(data.strip()), format_size_Pattern)
                # ws107.write(33, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Aligning Moment' in data[0]: ws107.write(row_Aligning, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Temperature Max Crown' in data[0]: ws107.write(row_TempCrown, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Temperature Max Bead' in data[0]: ws107.write(row_TempBead, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Temperature Belt Edge Right' in data[0]: ws107.write(row_TempBTRight, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Temperature Belt Edge Left' in data[0]: ws107.write(row_TempBTLeft, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Energy Loss Total' in data[0]: ws107.write(row_ELossTotal, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Energy Loss Crown' in data[0]: ws107.write(row_ELossCrown, i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Energy Loss Sidewall' in data[0]: ws107.write(row_ELossSide, i+2, float(data[1].strip()), format_size_Pattern)
            if 'Energy Loss Filler' in data[0]: ws107.write(row_ELossFiller, i+2, float(data[1].strip()), format_BG_gray_text)

            if 'Rib' in data[0] and 'Force[kgf]' in data[0] : Ribforce.append(float(data[1].strip()))
            if 'Rib' in data[0] and 'Area[cm2]' in data[0] : Ribarea.append(float(data[1].strip()))
            if 'Rib' in data[0] and 'Press[kPa]' in data[0] : Ribpress.append(float(data[1].strip()))

            if 'Rib' in data[0] and 'Force[kgf]' in data[0]: ws107.write(row_Rib+len(Ribforce), i+2, float(data[1].strip()), format_size_Pattern)
            if 'Rib' in data[0] and 'Area[cm2]' in data[0]: ws107.write(row_Rib+len(Ribforce)+len(Ribarea), i+2, float(data[1].strip()), format_BG_gray_text)
            if 'Rib' in data[0] and 'Press[kPa]' in data[0]: ws107.write(row_Rib+len(Ribforce)+len(Ribarea) + len(Ribpress), i+2, float(data[1].strip()), format_size_Pattern)

    NoRibs = len(Ribforce)

    nLine+=2; 
    if NoRibs > 1: 
        # print (NoRibs)
        rowrange = 'A'+str(nLine) + ":" + 'A'+str (50+NoRibs-1)
        # print ("1", rowrange)
        ws107.merge_range(rowrange, 'Rib Force', format_size_Pattern)
        for k in range (NoRibs): ws107.write(nLine-1+k, 1, "#"+str(k+1), format_size_Pattern)

        rowrange = 'A'+str(nLine+NoRibs) + ":" + 'A'+str (nLine+2*NoRibs-1)
        ws107.merge_range(rowrange, 'Rib Area', format_BG_gray_text)
        for k in range (NoRibs): ws107.write(nLine-1+NoRibs+k, 1, "#"+str(k+1), format_BG_gray_text)
        # print ("2", rowrange)
        rowrange = 'A'+str(nLine+2*NoRibs) + ":" + 'A'+str (nLine+3*NoRibs-1)
        ws107.merge_range(rowrange, 'Rib Pressure', format_size_Pattern)
        for k in range (NoRibs): ws107.write(nLine-1+2*NoRibs+k, 1, "#"+str(k+1), format_size_Pattern)
        # print ("3", rowrange)

    else:
        ws107.write(nLine-1, 0, "Rib Force(kgf)", format_size_Pattern)
        ws107.write(nLine-1, 1, "#1", format_size_Pattern)

        ws107.write(nLine, 0, "Rib Area(cm2)", format_size_Pattern)
        ws107.write(nLine, 1, "#1", format_size_Pattern)

        ws107.write(nLine+1, 0, "Rib Pressure(kPa)", format_size_Pattern)
        ws107.write(nLine, 1, "#1", format_size_Pattern)




# Save Workbook
wb.close()
os.system("rm -f *sbgo_2.out")
os.system("rm -f *sbgo_1.out")
os.system("rm -f *_matrix.dat")
#os.system("rm -f *.doe")

try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
except:
    pass
exit()




