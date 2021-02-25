#!/usr/bin/python
"""******************************************************************
    This is a Python script used in DOE/Optimization set-up.

    Purpose:
        This function reads the .doe file and stores info
        about design variables, responses, DOE setup, and
        optimization set-up.

    v3.1  7/11/13 SBK - add support for Material design variables (MATV).
******************************************************************"""
import string, time
from DOE.DoeResponses import respCategories, valid_xml_files

class DesignVariable:
    def __init__(self, abbrev=None, descr=None, vnom=None, vmin=None, vmax=None):
        if abbrev is None:
           self.abbrev = ()
        if descr is None:
           self.descr = 0
        if vnom is None:
           self.vnom = ()
        if vmin is None:
           self.vmin = ()
        if vmax is None:
           self.vmax = ()

class ObjFunc:
    def __init__(self, rname=None, oflag=None, wtfac=None, colid=None):
        if rname is None:
           self.rname = ()
        if oflag is None:
           self.oflag = 0
        if wtfac is None:
           self.wtfac = 0
        if colid is None:
           self.colid = 0

class Constraint:
    def __init__(self, rname=None, lolim=None, uplim=None, colid=None, normflag=None):
        if rname is None:
           self.rname = ()
        if lolim is None:
           self.lolim = 0
        if uplim is None:
           self.uplim = 0
        if colid is None:
           self.colid = 0
        if normflag is None:
           self.normflag = 0

class DoeFile(object):
    def __init__(self, FileName=None):
        self.fileName = FileName
        self.amgfil = []		#amg file name
        self.m3droot = []		#m3d file root names
        self.nruns = None		#num of DOE runs
        self.DAK_Anal = None		#DAKOTA Analysis (0=OAS, 1=OALHS, 2=LHS)
    def read(self, FileName=None):
        if FileName:
            self.fileName = FileName

        fn = open(self.fileName, 'r')
        line = fn.readline()
        while line[0] == '#':		# skip commented lines
            line = fn.readline()
        subs = line.split(' ')
        VERSION = 0
        if str.find(line, 'VERSION'):
            VERSION = eval(subs[3])	# read version of DOE answer file
        line = fn.readline()
        while line[0] == '#':		# skip commented lines
            line = fn.readline()
        self.amgfil = line		# read amg filename
        #print self.amgfil

        self.m3droot = []
        line = fn.readline()
        while line[0] == '#':		# skip commented lines
            line = fn.readline()
        subs = line.split(' ')
        nm3d = eval(subs[0])		# read number of m3d files
        for i in range(0,nm3d):
            line = fn.readline()
            while line[0] == '#':	# skip commented lines
                line = fn.readline()
            subs = line.split(' ')
            tmp = subs[0]
            iloc = tmp.rfind('/')
            jloc = tmp.rfind('.m3d')
            self.m3droot.append(tmp[iloc+1:jloc])	# read m3d filename
            #print self.m3droot[-1]

        """*****************************
        MOLD DESIGN VARIABLES
        *****************************"""
        MV = {}
        line = fn.readline()
        while line[0] == '#':		# skip commented lines
            line = fn.readline()
        subs = line.split(' ')
        n = eval(subs[0])		# read number of mold variables
        for i in range(0,n):
            line = fn.readline()
            while line[0] == '#':	# skip commented lines
                line = fn.readline()
            subs = line.split(',')
            MV[i] = DesignVariable()
            MV[i].abbrev = subs[0].strip()
            MV[i].descr  = subs[1].strip()
            MV[i].vnom = eval(subs[2])
            MV[i].vmin = eval(subs[3])
            MV[i].vmax = eval(subs[4])
#            print(MV[i].abbrev,', ',MV[i].descr,', ',MV[i].vnom,', ',MV[i].vmin,', ',MV[i].vmax)

        """*****************************
        CONSTRUCTION DESIGN VARIABLES
        *****************************"""
        CV = {}
        line = fn.readline()
        while line[0] == '#':		# skip commented lines
            line = fn.readline()
        subs = line.split(' ')
        n = eval(subs[0])		# read number of construction variables
        for i in range(0,n):
            line = fn.readline()
            while line[0] == '#':	# skip commented lines
                line = fn.readline()
            subs = line.split(',')
            CV[i] = DesignVariable()
            CV[i].abbrev = subs[0].strip()
            CV[i].descr  = subs[1].strip()
            CV[i].vnom = eval(subs[2])
            CV[i].vmin = eval(subs[3])
            CV[i].vmax = eval(subs[4])
            #print(CV[i].abbrev,', ',CV[i].descr,', ',CV[i].vnom,', ',CV[i].vmin,', ',CV[i].vmax)

        """*********************************
        MATERIAL DESIGN VARIABLES
        *********************************"""
        MATV = {}
        line = fn.readline()
        while line[0] == '#':		# skip commented lines
            line = fn.readline()
        subs = line.split()
        n = eval(subs[0])		# read number of material modulus variables
        for i in range(0,n):
            line = fn.readline()
            while line[0] == '#':	# skip commented lines
                line = fn.readline()
            subs = line.split(',')
            MATV[i] = DesignVariable()
            MATV[i].abbrev = subs[0].strip()
            MATV[i].descr  = subs[1].strip()
            MATV[i].vnom = eval(subs[2])
            MATV[i].vmin = eval(subs[3])
            MATV[i].vmax = eval(subs[4])
            #print(MATV[i].abbrev,', ',MATV[i].descr,', ',MATV[i].vnom,', ',MATV[i].vmin,', ',MATV[i].vmax)

        """*****************************
        nruns
        *****************************"""
        #ndv = len(MV) + len(CV)	# number of user-defined design variables
        self.nruns = 121
        self.DAK_Anal = 0
        line = fn.readline()		# read type of DOE analysis (0=OAS, 1=OALHS, 2=LHS)
        while line[0] == '#':		# skip commented lines
            line = fn.readline()
        subs = line.split()
        if str.find(line, '! DOE Type'):
            self.DAK_Anal = eval(subs[0])
        line = fn.readline()		# read number of runs
        while line[0] == '#':		# skip commented lines
            line = fn.readline()
        subs = line.split()
        if str.find(line, '! number of runs'):
            self.nruns = eval(subs[0])
            #explanation for number of runs in an orthogonal design (DAK_Anal = 0 or 1)
            #nruns set by DAKOTA based on the square of a prime number (or min non-prime number 4)
            #OAS
            #nruns = [max(4, prime >= ndv)]**2
            #OA_LHS (3**ndv is a value recommended by SBK)
            #nruns = [max(4, prime >= sqrt(3**ndv))]**2
        doetype = self.DAK_Anal
        nruns = self.nruns

        """*****************************
        RESPONSE VARIABLES
        *****************************"""
        # get user-selected response variables out of the .doe file
        userRespList = {}
        nresp = 0
        opt = 0
        for im3d in range(0,nm3d):		# loop through number of m3d files
            if not line: break
            while line[0] == '#':		# skip commented lines
                line = fn.readline()
                if not line: break
            # find start of response section for this m3d file
            while opt == 0 and not line.startswith('! user-selected responses'):
                line = fn.readline()
                if not line: break
                #time.sleep(5)

            line = fn.readline()		# info for m3d file
            if not line: break
            while line[0] == '#':		# skip commented lines
                line = fn.readline()
                if not line: break
            loc = len(line) + 1			# only read up to comment symbol (if present)
            if line.find('!') > 0:
                loc = line.find('!')
            subs = line[0:loc].split(',')	# read m3d file id #, # of loads, # of responses
            nloads = eval(subs[1])
            nresp  = eval(subs[2])
            #print im3d, nloads, nresp
            #print M3D[im3d]

            # read user responses for this m3d file
            for i in range(0,nresp):		# loop through responses
                line = fn.readline()
                if not line: break
                while line[0] == '#':		# skip commented lines
                    line = fn.readline()
                    if not line: break
                resp_string = line.split()
                rkey, rname = resp_string[0].split(':')
                for xkey in valid_xml_files.keys():
                    if rkey in valid_xml_files[xkey]:
                        if xkey not in userRespList.keys():
                            userRespList[xkey] = []
                        #print xkey,':',rkey,':',rname
                        userRespList[xkey].append([rname,rkey])	#['fpc90_m1_l100', 'fpc']
                        break

        #sort responses (consistent with readXMLforDOE.py)
        #this will be their order in the dakota tabular output file
        newlist = []
        for xkey in respCategories:
            if xkey in userRespList.keys():
                #sort response keys in alphabetical order for consistency
                userRespList[xkey].sort()
                #implied do loop takes rname entries from userRespList[xkey] list
                newlist.extend([p[0] for p in userRespList[xkey]])
        #print newlist
            
        """*****************************
        OPTIMIZATION STUFF
        *****************************"""
        # get optimization inputs from the file
        eof = 0
        while not line.startswith('! objective function'):
            line = fn.readline()
            if not line or (len(line) < 3):
                eof = 1
                break

        """*********************************
        OPTIMIZATION - objective function(s)
        *********************************"""
        #print "Objective Function..."
        nobjfunc    = 0
        ObjFun = {}
        if eof == 0:
            line = fn.readline()		# read 1st objective function (response)
            if not line:
                eof = 1
            else:
                while line[0] == '#':		# skip commented lines
                    line = fn.readline()
                    if not line:
                        eof = 1
                        break
                if not line or (len(line) < 3):
                    eof = 1
        # loop to constraint section or end-of-file
        while eof == 0 and not line.startswith('! response constraints') and not line.startswith('! DV constraints'):	
            if not line or (len(line) < 3):
                eof = 1
                break
            loc = len(line) + 1			# only read up to comment symbol (if present)
            if line.find('!') > 0:
                loc = line.find('!')
            subs = line[0:loc].split()	# read opt flag, weighting factor, response name
            ObjFun[nobjfunc] = ObjFunc()
            ObjFun[nobjfunc].oflag = eval(subs[0])
            ObjFun[nobjfunc].wtfac = eval(subs[1])
            rkey, rname = subs[2].split(':')
            ObjFun[nobjfunc].rname = rname
            ObjFun[nobjfunc].colid = newlist.index(rname)
            nobjfunc = nobjfunc + 1
            #print nobjfunc, ObjFun[nobjfunc-1].colid, ObjFun[nobjfunc-1].rname, ObjFun[nobjfunc-1].oflag, ObjFun[nobjfunc-1].wtfac
            line = fn.readline()
            if not line:
                eof = 1
            else:
                while line[0] == '#':		# skip commented lines
                    line = fn.readline()
                    if not line:
                        eof = 1
                        break

        """**********************************
        OPTIMIZATION - response constraint(s)
        **********************************"""
        #print "Response Constraint..."
        nconstraint = 0
        ReConstr = {}
        if eof == 0:
            line = fn.readline()		# read 1st constraint (response)
            if not line:
                eof = 1
            else:
                while line[0] == '#':		# skip commented lines
                    line = fn.readline()
                if not line or (len(line) < 3):
                    eof = 1
        # loop to DV constraint section or end-of-file
        while eof == 0 and not line.startswith('! DV constraints'):
            if not line or (len(line) < 3):
                eof = 1
                break
            loc = len(line) + 1			# only read up to comment symbol (if present)
            if line.find('!') > 0:
                loc = line.find('!')
            subs = line[0:loc].split()	# read normflag, lower limit, upper limit, response name
            ReConstr[nconstraint] = Constraint()
            ReConstr[nconstraint].normflag = eval(subs[0])
            ReConstr[nconstraint].lolim = eval(subs[1])
            ReConstr[nconstraint].uplim = eval(subs[2])
            rkey, rname = subs[3].split(':')
            ReConstr[nconstraint].rname = rname
            ReConstr[nconstraint].colid = newlist.index(rname)
            nconstraint = nconstraint + 1
            #print nconstraint, ReConstr[nconstraint-1].colid, ReConstr[nconstraint-1].rname, ReConstr[nconstraint-1].normflag, ReConstr[nconstraint-1].lolim, ReConstr[nconstraint-1].uplim
            line = fn.readline()
            if not line:
                eof = 1
        else:
            while line[0] == '#':		# skip commented lines
                    line = fn.readline()
                    if not line:
                        eof = 1
                        break

        """**********************************
        OPTIMIZATION - DV constraint(s)
        **********************************"""
        #print "DV Constraint..."
        nconstraint = 0
        DVConstr = {}
        if eof == 0:
            line = fn.readline()		# read 1st constraint (design variable)
            if not line:
                eof = 1
            else:
                while line[0] == '#':		# skip commented lines
                    line = fn.readline()
                    if not line:
                        eof = 1
                        break
                if not line or (len(line) < 3):
                    eof = 1
        # loop to end-of-file
        while eof == 0:
            if not line or (len(line) < 3):
                eof = 1
                break
            loc = len(line) + 1			# only read up to comment symbol (if present)
            if line.find('!') > 0:
                loc = line.find('!')
            subs = line[0:loc].split()	# read lower limit, upper limit, DV name
            DVConstr[nconstraint] = Constraint()
            DVConstr[nconstraint].lolim = eval(subs[0])
            DVConstr[nconstraint].uplim = eval(subs[1])
            DVConstr[nconstraint].rname = subs[2]
            DVConstr[nconstraint].colid = -1
            nconstraint = nconstraint + 1
            #print nconstraint, DVConstr[nconstraint-1].colid, DVConstr[nconstraint-1].rname, DVConstr[nconstraint-1].lolim, DVConstr[nconstraint-1].uplim
            line = fn.readline()
            if not line:
                eof = 1
            else:
                while line[0] == '#':		# skip commented lines
                    line = fn.readline()
                    if not line:
                        eof = 1
                        break

        """*****************************
        return variables to calling program
        *****************************"""
        fn.close()
        return MV, CV, MATV, userRespList, ObjFun, ReConstr, DVConstr, doetype, nruns

#************************************************************************
#
#   MAIN SCRIPT
#
#************************************************************************
