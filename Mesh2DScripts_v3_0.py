import matplotlib as mpl
mpl.use('Agg')
import math, time
import os, glob, sys, json
import numpy as np
import matplotlib.pyplot as plt
import _islm

# if in PC, delete import _islm

class NODE:
    def __init__(self):
        self.Node = []

    def Add(self, d):
        self.Node.append(d)

    def NodeByID(self, n, SORT=0, **args):
        callfrom=''
        for key, value in args.items():
            if key == 'sort':
                SORT=int(value)
            if key == 'name': 
                callfrom = value 

        N = len(self.Node)
        if SORT ==1:
            sorted(self.Node, key=lambda x:x[0])
        if N>100:
            if self.Node[int(N / 4)][0] > n:
                k1 = 0
                k2 = int(N / 4)
            elif self.Node[int(N / 2)][0] > n:
                k1 = int(N / 4)
                k2 = int(N / 2)
            elif self.Node[int(3 * N / 4)][0] > n:
                k1 = int(N / 2)
                k2 = 3 * int(N / 4)
            else:
                k1 = 3 * int(N / 4)
                k2 = N
            for i in range(k1, k2):
                if self.Node[i][0] == n:
                    return self.Node[i]
        for i in range(N):
            if self.Node[i][0] == n:
                return self.Node[i]
        if callfrom == '':  print ("Cannot Find the Node (%d)"%(n))
        else: print ("Cannot Find the Node (%d) for %s"%(n, callfrom))
        NullList = [0, 0.0, 0.0, 0.0]
        return NullList

class ELEMENT:
    def __init__(self):
        self.Element = []

    def Add(self, e):
        self.Element.append(e)

    def AllEdge(self):
        Name = EDGE()
        N = len(self.Element)
        for i in range(N):
            if self.Element[i][6] == 4:
                Name.Add([self.Element[i][1], self.Element[i][2], self.Element[i][5], 'S1', self.Element[i][0], -1])
                Name.Add([self.Element[i][2], self.Element[i][3], self.Element[i][5], 'S2', self.Element[i][0], -1])
                Name.Add([self.Element[i][3], self.Element[i][4], self.Element[i][5], 'S3', self.Element[i][0], -1])
                Name.Add([self.Element[i][4], self.Element[i][1], self.Element[i][5], 'S4', self.Element[i][0], -1])
            elif self.Element[i][6] == 3:
                Name.Add([self.Element[i][1], self.Element[i][2], self.Element[i][5], 'S1', self.Element[i][0], -1])
                Name.Add([self.Element[i][2], self.Element[i][3], self.Element[i][5], 'S2', self.Element[i][0], -1])
                Name.Add([self.Element[i][3], self.Element[i][1], self.Element[i][5], 'S3', self.Element[i][0], -1])
        return Name

    def FreeEdge(self):
        edges = self.AllEdge()
        freeEdge = FreeEdge(edges)
        return freeEdge

    def OuterEdge(self, Node):
        FEdges = self.FreeEdge()
        # print(len(FEdges.Edge))
        OEdges = OuterEdge(FEdges, Node, self)
        return OEdges

    def TieEdge(self, Node):
        AllEdges=FindEdge(self.Element)
        FreeEdges=FindFreeEdge(AllEdges)
        CenterNodes = FindCenterNodes(Node)
        if len(CenterNodes): 
            CenterNodes = FindBottomNodes(Node)

        OutEdges=FindOutEdges(FreeEdges, CenterNodes, Node.Node, self.Element)

        InnerFreeEdges = FindInnerFreeEdges(FreeEdges, OutEdges)
        ND =NODE()
        for n in Node.Node:
            ND.Add(n)
        MasterEdges, SlaveEdges, Tie_error = DivideInnerFreeEdgesToMasterSlave(InnerFreeEdges, ND)
        medge = EDGE()
        for edge in MasterEdges: 
            medge.Add(edge)
        sedge = EDGE()
        for edge in SlaveEdges: 
            sedge.Add(edge)

        return medge, sedge


    def TieEdge_2019(self, Node):
        FreeEdge = self.FreeEdge()
        OuterEdge(FreeEdge, Node, self)  # Don't Delete this line.
        TieNum = 1
        i = 0;        iTemp = 0;        j = 0
        connectedEdge = []
        TEdge = EDGE()
        while i < len(FreeEdge.Edge):
            if FreeEdge.Edge[i][5] < 1:
                TieNum += 1
                nodeStart = FreeEdge.Edge[i][0]
                FreeEdge.Edge[i][5] = TieNum
                TEdge.Add(FreeEdge.Edge[i])  # marked as TIE edge with No.
                iTemp = i
                while FreeEdge.Edge[iTemp][1] != nodeStart:
                    j += 1
                    if j > 100:
                        break  # in case infinite loop
                    connectedEdge = NextEdge(FreeEdge, iTemp)  # find next edge
                    if len(connectedEdge) == 1:  # in case of being found just 1 edge
                        iTemp = connectedEdge[0]
                    elif len(connectedEdge) == 2:  # when other tie is connected (2 ties are connected)
                        if FreeEdge.Edge[connectedEdge[0]][1] == nodeStart:
                            iTemp = connectedEdge[0]
                        elif FreeEdge.Edge[connectedEdge[1]][1] == nodeStart:
                            iTemp = connectedEdge[1]
                        else:
                            if FreeEdge.Edge[connectedEdge[0]][5] < 1 and FreeEdge.Edge[connectedEdge[1]][5] < 1:
                                iTemp = FindTieLoop(nodeStart, connectedEdge, FreeEdge)
                            elif FreeEdge.Edge[connectedEdge[0]][5] < 1:
                                iTemp = connectedEdge[0]
                            elif FreeEdge.Edge[connectedEdge[1]][5] < 1:
                                iTemp = connectedEdge[1]
                            else:
                                print ('[INPUT] {' + str(FreeEdge.Edge[connectedEdge[0]]) + ',' + str(FreeEdge.Edge[connectedEdge[1]]) + ' (0) TIE Conection InCompletion')
                                break
                    else:
                        print ('[INPUT] 2 or more Ties are Connected.')
                        break
                    # After finding next TIE Edge ################################
                    FreeEdge.Edge[iTemp][5] = TieNum
                    TEdge.Add(FreeEdge.Edge[iTemp])
                del connectedEdge
                connectedEdge = []
            i += 1
        return TEdge
        
    def MasterSlaveEdge(self, Node, Op = 0, **args):
        for key, value in args.items():
            if key == 'op':
                Op = int(value)
        
        TieEdge, _ = self.TieEdge(Node)
        iNum = 2
        mlength = 0 
        ErrRatio = 0.01
        
        NumTie = 0 
        N = len(TieEdge.Edge)
        for i in range(N):
            if TieEdge.Edge[i][5] > NumTie:
                NumTie = TieEdge.Edge[i][5]
            
        iMaster = []
        while iNum <=NumTie:
            MaxLength = 0.0
            SumLength = 0.0
            k = 0
            Save = 0
            while k < N:
                if TieEdge.Edge[k][5] == iNum:
                    N1 = Node.NodeByID(TieEdge.Edge[k][0])
                    N2 = Node.NodeByID(TieEdge.Edge[k][1])
                    Length = math.sqrt((N1[2]-N2[2])* (N1[2]-N2[2]) + (N1[3]-N2[3])*(N1[3]-N2[3]))
                    SumLength += Length
                    if Length > MaxLength:
                        MaxLength = Length
                        Save = k
                k += 1
            SumLength -= MaxLength
            if SumLength > MaxLength * (1+ErrRatio) or SumLength < MaxLength * (1-ErrRatio):
                print ('ERROR::PRE::TIE CREATION INCOMPLETE ON', TieEdge.Edge[Save][3])
            iMaster.append(Save)
            iNum += 1
        
        MasterEdge=EDGE()
        SlaveEdge =EDGE()
        M = len(iMaster)
        for i in range(N):
            exist = 0
            for j in range(M):
                if i == iMaster[j]:
                    MasterEdge.Add(TieEdge.Edge[i])
                    exist =1
                    break
            if exist == 0:
                SlaveEdge.Add(TieEdge.Edge[i])
        SlaveGroup = FindSlave(self.Element, MasterEdge, SlaveEdge)
        
        ## Op == 0 return MasterEdge and SlaveEdge
        ## Op == 1 return only Master Edge
        ## Op == 2 return Only Slave Edge
        if Op == 0:
            return MasterEdge, SlaveGroup
        elif Op == 1:
            return MasterEdge
        else:
            return SlaveGroup
        
    def Nodes(self, Node=NODE(), **args):

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

class ELSET:
    def __init__(self):
        self.Elset = []

    def Add(self, n, name): 
        ex = -1

        for i, eset in enumerate(self.Elset): 
            if eset[0]== name:
                ex = i 
                break
        if ex == -1:
            self.Elset.append([name])
            ex = len(self.Elset)-1

        self.Elset[ex].append(n) 


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

    def AddNumber(self, n):
        self.Surface.append(n)

    def AddName(self, name):
        exist = 0
        for i in range(len(self.Surface)):
            if self.Surface[i][0] == name:
                exist = 1
                break
        if exist == 0:
            self.Surface.append([name])

    def AddNumber_face(self, n, name):
        #        print (name, "- Surface ADDING", n )
        for i in range(len(self.Surface)):
            if self.Surface[i][0] == name:
                self.Surface[i].append(n)

class EDGE:
    def __init__(self):
        self.Edge = []

    def Add(self, edge):
        self.Edge.append(edge)

    def Combine(self, iEdge):
        if type(iEdge) == type(self.Edge): 
            N = len(iEdge)
            for i in range(N): 
                self.Add(iEdge[i])

        else: 
            N = len(iEdge.Edge)
            for i in range(N): 
                self.Add(iEdge.Edge[i])


    def Image(self, Node, file='EDGE', marker ="", dpi=100):
        MembWidth = 0.5
        color = 'black'

        fig, ax = plt.subplots()
        ax.axis('equal')
        ax.axis('on')
        N = len(self.Edge)
        MinX = 100000.0
        MaxX = -100000.0
        MinY = 100000.0
        MaxY = -100000.0
        for i in range(N):
            N1 = Node.NodeByID(self.Edge[i][0])
            N2 = Node.NodeByID(self.Edge[i][1])
            x1 = N1[2]
            y1 = N1[3]
            x2 = N2[2]
            y2 = N2[3]
            plt.plot([x1, x2], [y1, y2], color, lw=MembWidth, marker=marker)
            if MinX > x1:
                MinX = x1
            if MaxX < x1:
                MaxX = x1
            if MinY > y1:
                MinY = y1
            if MaxY < y1:
                MaxY = y1
            if MinX > x2:
                MinX = x2
            if MaxX < x2:
                MaxX = x2
            if MinY > y2:
                MinY = y2
            if MaxY < y2:
                MaxY = y2
        plt.xlim(MinX - 0.01, MaxX + 0.01)
        plt.ylim(MinY - 0.01, MaxY + 0.01)
        plt.savefig(file, dpi=dpi)

def Coordinates(n, N):
    C=np.zeros(3)
    for i in range(len(N.Node)):
        if N.Node[i][0] == n:
            C[0] = N.Node[i][1]  #
            C[1] = N.Node[i][2]  # lateral direction
            C[2] = N.Node[i][3]  # radial direction
            break
    return C

def Area(Ns, N):
    n = len(Ns)
    x = [];
    y = []
    for i in range(n):
        C = Coordinates(Ns[i], N)
        x.append(C[1])
        y.append(C[2])
    x.append(x[0])
    y.append(y[0])
    A = np.zeros(3)

    for i in range(n):
        s = x[i] * y[i + 1] - x[i + 1] * y[i]
        A[0] += s
        A[1] += (x[i] + x[i + 1]) * s
        A[2] += (y[i] + y[i + 1]) * s
    
    A[0] = A[0] / 2.0
    try:
        A[1] = A[1] / A[0] / 6
        A[2] = A[2] / A[0] / 6
    except:
        print (A, x, y)

    if A[0] < 0:
        A[0] = -A[0]
        # print 'Negative Area Calculation! '
    return A
    #     print "A

def find_r(No, Node):
    i = 0
    x = 0.0
    while i < len(Node):
        if No == Node[i][0]:
            x = Node[i][3]
            break
        i += 1
    return x

def find_z(No, Node):
    i = 0
    y = 0.0
    while i < len(Node):
        if No == Node[i][0]:
            y = Node[i][2]
            break
        i += 1
    return y

def Jacobian(x1, x2, x3, x4, y1, y2, y3, y4):
    count = 0
    for s in [1.0, -1.0]:
        for t in [1.0, -1.0]:
            xs = 0.25 * ((-x1 + x2 + x3 - x4) + (x1 - x2 + x3 - x4) * t)
            ys = 0.25 * ((-y1 + y2 + y3 - y4) + (y1 - y2 + y3 - y4) * t)
            xt = 0.25 * ((-x1 - x2 + x3 + x4) + (x1 - x2 + x3 - x4) * s)
            yt = 0.25 * ((-y1 - y2 + y3 + y4) + (y1 - y2 + y3 - y4) * s)
            jacobian = xs * yt - ys * xt

            if jacobian <= 0:
                count += 1
    return count

def NormalVector(x1, x2, x3, y1, y2, y3):
    det = 0.0
    a1 = x2 - x1;
    a2 = y2 - y1
    b1 = x3 - x2;
    b2 = y3 - y2

    det = a1 * b2 - a2 * b1
    return det

def ElementShape(k, Elements):
    # k = element No.
    tmplist = []
    if type(Elements) == type(tmplist): 
        N=len(Elements)
        for i in range(N):
            if k == Elements[i][0]:
                return Elements[i][6]
    else: 
        for el in Elements.Element:
            if k == el[0]: 
                return el[6]

    print (k, 'Element was not found')
    return 0
	
def ShareEdge(m, n, Elements):
    p=ElementShape(m,Elements)
    q=ElementShape(n, Elements)
    tmplist = []
    if type(Elements) == type(tmplist): 
        N = len(Elements)
        for i in range(N):
            if m == Elements[i][0]:
                k = i
            if n == Elements[i][0]:
                l = i
        count =0
        for i in range(1, p+1):
            for j in range(1,q+1):
                if Elements[k][i] == Elements[l][j]:
                    count += 1
    else: 
        for i, el in enumerate(Elements.Element): 
            if m == el[0]: k = i 
            if n == el[0]: l = i

        count =0
        for i in range(1, p+1):
            for j in range(1,q+1):
                if Elements.Element[k][i] == Elements.Element[l][j]:
                    count += 1

    

    if count >= 2:
        return 1 # Edge shared
    else:
        return 0


def Mesh2DInformation(InpFileName):
    with open(InpFileName) as INP:
        lines = INP.readlines()

    Node = NODE()
    Element = ELEMENT()
    Elset = ELSET()
    Surface = SURFACE()
    
    Comments = []
    iComment = 0
    

    for line in lines:
        if "**" in line: 
            pass 

        else:
            iComment += 1
            if "*" in line: 
                word = list(line.split(','))
                command = list(word[0].split('*'))
                if "*HEADING" in line.upper(): 
                    spt = 'HD'
                elif "*NODE" in line.upper(): 
                    spt = 'ND'
                elif "*ELEMENT" in line.upper(): 
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
                elif "*SURFACE," in line.upper(): 
                    spt = 'SF'
                    name = word[2].split('=')[1].strip()
                    Surface.AddName(name)
                #                    print ('Name=', name, 'was stored', Surface.Surface)
                elif "*TIE," in line.upper(): 
                    spt = 'TI'
                    name = word[1].split('=')[1].strip()
                elif "*ELSET," in line.upper(): 
                    spt = 'ES'
                    name = word[1].split('=')[1].strip()
                    if name != "BETWEEN_BELTS" and name != "BD1" and name != "BetweenBelts":
                        Elset.AddName(name)

                elif "*NSET," in line.upper(): 
                    spt = 'NS'
                    name = word[1].split('=')[1].strip()

                else:
                    spt = ''
            else:
                word = list(line.split(','))
                for i, w in enumerate(word): 
                    word[i] =w.strip()

                if spt == 'HD':
                    pass
                if spt == 'ND':
                    
                    Node.Add([int(word[0]), float(word[3]), float(word[2]), float(word[1])])
                if spt == 'M1':
                    # Element   [EL No,                  N1,          N2,  N3, N4,'elset Name', N,  Area/length, CenterX, CenterY]
                    C1 = Coordinates(int(word[1]), Node)
                    C2 = Coordinates(int(word[2]), Node)
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), '', '', '', 2, math.sqrt(math.pow(C1[1] - C2[1], 2) + math.pow(C1[2] - C2[2], 2)), (C1[1] + C2[1]) / 2.0, (C1[2] + C2[2]) / 2.0])
                if spt == 'C3':
                    #print ("3", word)
                    A = Area([int(word[3]), int(word[2]), int(word[1])], Node)
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), int(word[3]), '', '', 3, A[0], A[1], A[2]])
                if spt == 'C4':
                    #print ("4", word)
                    A = Area([int(word[4]), int(word[3]), int(word[2]), int(word[1])], Node)
                    Element.Add([int(word[0]), int(word[1]), int(word[2]), int(word[3]), int(word[4]), '', 4, A[0], A[1], A[2]])
                if spt == 'NS':
                    pass
                if spt == 'ES':
                    if name != "BETWEEN_BELTS" and name != "BD1" and name != "BetweenBelts":
                        if isNumber(word[0]) == True:
                            for i in range(len(word)):
                                if word[i] !="": Elset.AddNumber(int(word[i]), name)
                if spt == 'SF':
                    pass

                else:
                    pass

    for i in range(len(Elset.Elset)):
        for j in range(1, len(Elset.Elset[i])):
            for k in range(len(Element.Element)):
                if Elset.Elset[i][j] == Element.Element[k][0]:
                    Element.Element[k][5] = Elset.Elset[i][0]
                    break

    return Node, Element, Elset, Comments
    
def isNumber(s):
  try:
    float(s)
    return True
  except ValueError:
    return False


def IsPointInPolygon(Point, Polygon):
    # Point = [a, b]
    # Polygon = [[x1, y1], [x2, y2], ... ]

    # check if the point is on the edge of the polygon
    #      xi <= a <= xj & y = (yj-yi)/(xj-xi) * (x-xi) + yi |x=a = b
    #   if function of the edge is y=b or x=a,
    #####################################################################
    OutofPolygon = -1
    OnLine = 0
    InPolygon = 1
    counting = 0

    Point[0] = float(Point[0])
    Point[1] = float(Point[1])
    for i in range(len(Polygon)):
        for j in range(len(Polygon[i])):
            Polygon[i][j] = float(Polygon[i][j])

    for i in range(len(Polygon)):
        if i != len(Polygon) - 1:
            m = i
            n = i + 1
        else:
            m = i
            n = 0
        if Polygon[m][0] == Point[0] and Polygon[m][1] == Point[1]:
            return OnLine
        elif Polygon[m][0] == Polygon[n][0]:
            if Polygon[m][0] == Point[0]:
                if Polygon[m][1] > Polygon[n][1] and Point[1] < Polygon[m][1] and Point[1] > Polygon[n][1]:
                    return OnLine
                elif Polygon[m][1] < Polygon[n][1] and Point[1] > Polygon[m][1] and Point[1] < Polygon[n][1]:
                    return OnLine
                else:
                    return OutofPolygon
        elif Polygon[m][1] == Polygon[n][1]:
            if Polygon[m][1] == Point[1]:
                if Polygon[m][0] > Polygon[n][0] and Point[0] < Polygon[m][0] and Point[0] > Polygon[n][0]:
                    return OnLine
                elif Polygon[m][0] < Polygon[n][0] and Point[0] > Polygon[m][0] and Point[0] < Polygon[n][0]:
                    return OnLine
                else:
                    return OutofPolygon
            else:
                if Polygon[m][0] > Polygon[n][0] and Point[0] < Polygon[m][0] and Point[0] > Polygon[n][0] and Point[1] < Polygon[m][1]:
                    # print 'c1'
                    counting += 1
                elif Polygon[m][0] < Polygon[n][0] and Point[0] < Polygon[n][0] and Point[0] > Polygon[m][0] and Point[1] < Polygon[n][1]:
                    # print 'c2'
                    counting += 1
        else:
            y0 = (Polygon[n][1] - Polygon[m][1]) / (Polygon[n][0] - Polygon[m][0]) * (Point[0] - Polygon[m][0]) + Polygon[m][1]
            if y0 >= Point[1]:
                if Polygon[m][0] > Polygon[n][0]:
                    if Point[0] < Polygon[m][0] and Point[0] > Polygon[n][0]:
                        # print y0, Point[1]
                        if y0 == Point[1]:
                            return OnLine
                        counting += 1
                        if Polygon[m][1] == y0:
                            counting -= 1
                if Polygon[m][0] < Polygon[n][0]:
                    if Point[0] > Polygon[m][0] and Point[0] < Polygon[n][0]:
                        # print y0, Point[1]
                        if y0 == Point[1]:
                            return OnLine
                        counting += 1
                        if Polygon[m][1] == y0:
                            counting -= 1

    print ('meet', counting)

    if counting % 2 == 0:
        return OutofPolygon
    else:
        return InPolygon

def ChaferDivide(Elements, ChaferName, Elset, Node):

    asymmetric =0
    I = len(Elements)
    J = len(Node)
    for i in range(I):
        if Elements[i][5]=="BT2":
            for j in range(J):
                if Node[j][0] == Elements[i][1]:
                    if Node[j][2] == 0:
                        relement=Elements[i][0]
                if Node[j][0] == Elements[i][2]:
                    if Node[j][2] == 0:
                        lelement=Elements[i][0]
    
    Offset = abs(relement - lelement )
    if Offset != 2000:
        for j in range(J):
            if Node[j][2] > 0.0 :
                Offset = Node[j][0]
                break
        print ("Asymmetric Model %d"%(Offset))
        asymmetric =1

    
    for i in range(len(Elements)):
        for j in range(len(ChaferName)):
            if Elements[i][5] == ChaferName[j]:
                
                if Elements[i][8] > 0:
                    NewName = Elements[i][5] + '_R'
                else:
                    NewName = Elements[i][5] + '_L'
                Elements[i][5] = NewName
                    
    for i in range(len(Elements)):
        if Elements[i][5] == "BEAD_R" and Elements[i][8] < 0.0 :
            Elements[i][5] = 'BEAD_L'


    for i in range(len(Elset)):
        for j in range(len(ChaferName)):
            if Elset[i][0] == "CH1" or Elset[i][0] == "CH2" or Elset[i][0] == "CH3" : 
                left=[]
                right=[]
                left.append(Elset[i][0] + '_L')
                right.append(Elset[i][0] + '_R')
                for k in range(1, len(Elset[i])):
                    for el in Elements:
                        if el[0] == Elset[i][k]: 
                            if el[8] > 0: 
                                right.append(Elset[i][k])
                            else: 
                                left.append(Elset[i][k])
                            break

                del(Elset[i])

                Elset.append(right)
                Elset.append(left)
                
    if asymmetric ==1:
        Offset = 0
    return Elements, Elset, Offset

def ElementDuplicationCheck(AllElements):

    try:
        tupleElement = ()
        for i in range(len(AllElements)):
            tList = []
            for k in range(len(AllElements[i])):
                if AllElements[i][k] == '':
                    tList.append(0)
                elif k == 5 or k > 6:
                    tList.append(0)
                else:
                    tList.append(AllElements[i][k])
            tupleElement = tupleElement + tuple(tList)

        N=len(AllElements[0])
        N=_islm.CheckElementDuplication(tupleElement, N)
        print ("* Element Duplication = %d" % (N))
        if N>0:
            print ("* Element Duplication = %d" %(N))
            return 0
        else:
            return 1
    except:
        print ("* Element Duplication Check by Python Script")

        i = 0
        while i < len(AllElements):
            if AllElements[i][6] == 2:
                j = 0;
                match = 0
                while j < len(AllElements):
                    if AllElements[j][6] == 2:
                        if i != j:
                            if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][2]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][1]:
                                match = 1
                            if match > 0:
                                print (' Rebar Element '+ str(AllElements[i][0]) + ', ' + str(AllElements[j][0]) + ' are Defined TWICE. ')
                                # logline.append([' - Rebar Element' + str(AllElements[j][0]) + 'was deleted. Twice defined. CHECK MODEL\n'])
                                return 0
                    j += 1

            if AllElements[i][6] == 3:
                match = 0
                j = 0
                while j < len(AllElements):
                    if AllElements[j][6] == 3:
                        if i != j:
                            if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][2] and AllElements[i][3] == AllElements[j][3]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][3] and AllElements[i][3] == AllElements[j][1]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][3] and AllElements[i][2] == AllElements[j][1] and AllElements[i][3] == AllElements[j][2]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][3] and AllElements[i][3] == AllElements[j][2]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][1] and AllElements[i][3] == AllElements[j][3]:
                                match = 1
                            if AllElements[i][1] == AllElements[j][3] and AllElements[i][2] == AllElements[j][2] and AllElements[i][3] == AllElements[j][1]:
                                match = 1
                            if match > 0:
                                print (' CGAX3H Elements ' + str(AllElements[i][0]) + ', ' + str(AllElements[j][0]) + ' are Defined TWICE. ')
                                return 0
                    j += 1

            if AllElements[i][6] == 4:
                j = 0
                while j < len(AllElements):
                    if AllElements[i][6] == 4 and AllElements[j][6] == 4 and i != j:
                        match = 0
                        k1 = 0;
                        k2 = 0;
                        k3 = 0;
                        k4 = 0
                        for k in range(1, 5):
                            if AllElements[i][1] == AllElements[j][k] and k1 == 0:
                                match += 1
                                k1 = 1
                                continue
                            if AllElements[i][2] == AllElements[j][k] and k2 == 0:
                                match += 1
                                k2 = 1
                                continue
                            if AllElements[i][3] == AllElements[j][k] and k3 == 0:
                                match += 1
                                k3 = 1
                                continue
                            if AllElements[i][4] == AllElements[j][k] and k4 == 0:
                                match += 1
                                k4 = 1
                                continue

                        if match == 4:
                            print (' CGAX4H Elements '+ str(AllElements[i][0]) + ', ' + str(AllElements[j][0]) + ' are Defined TWICE. ')
                            return 0
                    j += 1
            i += 1

    return 1

def RebarConnectivity(AllElements):
    i = 0
    while i < len(AllElements):
        if AllElements[i][6] == 2:
            j = 0
            while j < len(AllElements):
                if AllElements[j][6] == 2:
                    if i != j:
                        if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][2]:
                            print('[INPUT] Rebar(' + str(AllElements[i][0]) + ') needs to be checked the numbering order.')
                            # logline.append(['[INPUT] Rebar(' + str(AllElements[i][0]) + ') needs to be checked the numbering order.\n'])
                            return 0
                        if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][1]:
                            print('[INPUT] Rebar(' + str(AllElements[i][0]) + ') needs to be checked the numbering order!')
                            return 0
                j += 1
        i += 1

    i = 0
    while i < len(AllElements):
        if AllElements[i][6] == 2:
            j = 0
            count = 0
            while j < len(AllElements):
                if AllElements[j][6] == 3:
                    if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][2]:
                        count += 1
                    if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][3]:
                        count += 1
                    if AllElements[i][1] == AllElements[j][3] and AllElements[i][2] == AllElements[j][1]:
                        count += 1
                    if AllElements[i][2] == AllElements[j][1] and AllElements[i][1] == AllElements[j][2]:
                        count += 1
                    if AllElements[i][2] == AllElements[j][2] and AllElements[i][1] == AllElements[j][3]:
                        count += 1
                    if AllElements[i][2] == AllElements[j][3] and AllElements[i][1] == AllElements[j][1]:
                        count += 1
                elif AllElements[j][6] == 4:
                    if AllElements[i][1] == AllElements[j][1] and AllElements[i][2] == AllElements[j][2]:
                        count += 1
                    if AllElements[i][1] == AllElements[j][2] and AllElements[i][2] == AllElements[j][3]:
                        count += 1
                    if AllElements[i][1] == AllElements[j][3] and AllElements[i][2] == AllElements[j][4]:
                        count += 1
                    if AllElements[i][1] == AllElements[j][4] and AllElements[i][2] == AllElements[j][1]:
                        count += 1
                    if AllElements[i][2] == AllElements[j][1] and AllElements[i][1] == AllElements[j][2]:
                        count += 1
                    if AllElements[i][2] == AllElements[j][2] and AllElements[i][1] == AllElements[j][3]:
                        count += 1
                    if AllElements[i][2] == AllElements[j][3] and AllElements[i][1] == AllElements[j][4]:
                        count += 1
                    if AllElements[i][2] == AllElements[j][4] and AllElements[i][1] == AllElements[j][1]:
                        count += 1
                j += 1

            if count < 2:
                print('Rebar(' + str(AllElements[i][0]) + ') needs to be checked the Element Connection.', count)
                # logline.append(['ERROR::PRE::[INPUT] Rebar(' + str(AllElements[i][0]) + ') needs to be checked the Element Connection.\n'])
                return 0
        i += 1
    print ("* Rebar Connectivity Check Completion")
    return 1

def SolidElementOrderCheck(elements, Nodes):

    # Solid element Order Check

    i = 0
    while i < len(elements):
        if elements[i][6] == 4:
            x1 = find_z(elements[i][1], Nodes) * -1
            x2 = find_z(elements[i][2], Nodes) * -1
            x3 = find_z(elements[i][3], Nodes) * -1
            x4 = find_z(elements[i][4], Nodes) * -1
            y1 = find_r(elements[i][1], Nodes)
            y2 = find_r(elements[i][2], Nodes)
            y3 = find_r(elements[i][3], Nodes)
            y4 = find_r(elements[i][4], Nodes)

            distortion = Jacobian(x1, x2, x3, x4, y1, y2, y3, y4)
            # print x1, ',', y1, ', ', x2, ',', y2, ', ', x3, ',', y3, ', ', x4, ',', y4

            if distortion > 0:
                print ('[INPUT] Clockwise order or Distorted Element CGAX4H (' + str(elements[i][0]) + ')')
                # logline.append(['[INPUT] Clockwise order : CGAX4H (' + str(elements[i][0]) + ')\n The nodes are reordered to CCW\n'])
                if distortion == 4:
                    j = elements[i][2]
                    elements[i][2] = elements[i][4]
                    elements[i][4] = j
                    # logline.append(['   - The nodes are reordered to CCW.\n'])
                    print ('   - The nodes are reordered to CCW.')
                else:
                    print ('[INPUT] The Element is distorted.')
                    # logline.append(['ERROR::PRE::[INPUT] The Element is distorted.\n'])
                    return 0
        elif elements[i][6] == 3:
            x1 = find_z(elements[i][1], Nodes) * -1
            x2 = find_z(elements[i][2], Nodes) * -1
            x3 = find_z(elements[i][3], Nodes) * -1
            y1 = find_r(elements[i][1], Nodes)
            y2 = find_r(elements[i][2], Nodes)
            y3 = find_r(elements[i][3], Nodes)

            Det1 = NormalVector(x1, x2, x3, y1, y2, y3)
            if Det1 < 0:
                j = elements[i][2]
                elements[i][2] = elements[i][3]
                elements[i][3] = j
                print ('[INPUT] Clockwise order : CGAX3H (' + str(elements[i][0]) + ')')
                print ('   - The nodes are reordered to CCW.')
                # logline.append(['[INPUT] Clockwise order : CGAX3H (' + str(elements[i][0]) + ')\n The nodes are reordered to CCW\n'])
        i += 1

    return 1

def SolidElementShapeCheck(Elements, Nodes, CriticalAngle, CriticalLength):

    NarrowElement = 0
    x1 = 0;    x2 = 0;    x3 = 0;    x4 = 0
    y1 = 0;    y2 = 0;    y3 = 0;    y4 = 0

    for i in range(len(Elements)):
        distance = []

        if Elements[i][6] == 3:
            for j in range(len(Nodes)):
                if Elements[i][1] == Nodes[j][0]:
                    x1 = Nodes[j][3];                    y1 = Nodes[j][2]
                if Elements[i][2] == Nodes[j][0]:
                    x2 = Nodes[j][3];                    y2 = Nodes[j][2]
                if Elements[i][3] == Nodes[j][0]:
                    x3 = Nodes[j][3];                    y3 = Nodes[j][2]
            distance.append(math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2)))
            distance.append(math.sqrt(math.pow(x3 - x2, 2) + math.pow(y3 - y2, 2)))
            distance.append(math.sqrt(math.pow(x1 - x3, 2) + math.pow(y1 - y3, 2)))
            fmin = distance[0];            fmax = distance[0]

            for m in range(3):
                if fmin > distance[m]:
                    fmin = distance[m]
                if fmax < distance[m]:
                    fmax = distance[m]

            if fmax / fmin > 30:
                # print 'Warning! Element(3 Node %d) is Too NARROW. Length Ratio(Max/Min)=%10.2f' % (Elements[i][0], fmax / fmin)
            # ErrorFile.writelines( '[Input] Element(3 Node) Too NARROW. No. %5d, Length Ratio(Max/Min)=%10.2f\n' % (Elements[i][0], fmax / fmin))
            # NarrowElement+=1
                pass
            if fmin < CriticalLength:
                print ('Warning! One of the edges in the Element(3 Node, %d) is too small(%10.7fmm)' % (Elements[i][0], fmin*1000))


            ####### Angle between edges
            angle = []
            DX1 = x2 - x1;            DY1 = y2 - y1
            DX2 = x3 - x2;            DY2 = y3 - y2
            DX3 = x1 - x3;            DY3 = y1 - y3

            cos = (DX1 * DX2 + DY1 * DY2) / (distance[0] * distance[1])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX2 * DX3 + DY2 * DY3) / (distance[1] * distance[2])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX3 * DX1 + DY3 * DY1) / (distance[2] * distance[0])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            for m in range(len(angle)):
                if angle[m] < CriticalAngle or angle[m] > 180.0-CriticalAngle:
                    print ('Warning! Element 3 Node %5d(%s) is sharp or almost line shape. Angle between Edge : %6.4f' % (Elements[i][0], Elements[i][5], angle[m]))

        distance = []
        if Elements[i][6] == 4:
            for j in range(len(Nodes)):
                if Elements[i][1] == Nodes[j][0]:
                    x1 = Nodes[j][3];                     y1 = Nodes[j][2]
                if Elements[i][2] == Nodes[j][0]:
                    x2 = Nodes[j][3];                    y2 = Nodes[j][2]
                if Elements[i][3] == Nodes[j][0]:
                    x3 = Nodes[j][3];                    y3 = Nodes[j][2]
                if Elements[i][4] == Nodes[j][0]:
                    x4 = Nodes[j][3];                    y4 = Nodes[j][2]
            distance.append(math.sqrt(math.pow(x4 - x2, 2) + math.pow(y4 - y2, 2)))
            distance.append(math.sqrt(math.pow(x1 - x3, 2) + math.pow(y1 - y3, 2)))
            distance.append(math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2)))
            distance.append(math.sqrt(math.pow(x3 - x2, 2) + math.pow(y3 - y2, 2)))
            distance.append(math.sqrt(math.pow(x4 - x3, 2) + math.pow(y4 - y3, 2)))
            distance.append(math.sqrt(math.pow(x1 - x4, 2) + math.pow(y1 - y4, 2)))

            fmin = distance[0];            fmax = distance[0]

            for m in range(6):
                if fmin > distance[m]:
                    fmin = distance[m]
                if fmax < distance[m]:
                    fmax = distance[m]

            if fmin == 0:
                print (distance, Elements[i])

            if fmax / fmin > 10:
                # print 'Warning! Element(4 Node %d) is Too NARROW. Diagonal/Edge Length Ratio(Max/Min)=%10.2f' % (Elements[i][0], fmax / fmin)
                pass
            #   ErrorFile.writelines( 'Pre::[Input] Element(4 Node) Too NARROW. No. %5d, Diagonal/Edge Length Ratio(Max/Min)=%10.2f\n' % (Elements[i][0], fmax / fmin))
            #   NarrowElement+=1
            if fmin < CriticalLength:
                print ('Warning! One of the edges in the Element(4 Node %d) is too small(%10.7fmm)' % (Elements[i][0], fmin*1000))

            ####### Angle between edges
            angle = []
            DX1 = x2 - x1;            DY1 = y2 - y1
            DX2 = x3 - x2;            DY2 = y3 - y2
            DX3 = x4 - x3;            DY3 = y4 - y3
            DX4 = x1 - x4;            DY4 = y1 - y4

            cos = (DX1 * DX2 + DY1 * DY2) / (distance[2] * distance[3])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX2 * DX3 + DY2 * DY3) / (distance[3] * distance[4])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX3 * DX4 + DY3 * DY4) / (distance[4] * distance[5])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            cos = (DX4 * DX1 + DY4 * DY1) / (distance[5] * distance[2])
            radian = math.acos(round(cos, 10))
            angle.append(180 - math.degrees(radian))

            for m in range(len(angle)):
                if angle[m] < CriticalAngle or angle[m] > 180.0 - CriticalAngle:
                    print ('Warning! Element %5d is Sharp or almost Triangular shape. Angle between Edge : %6.4f' % (Elements[i][0], angle[m]))

    if NarrowElement > 0:
        print ('No. of NarrowElement = ', NarrowElement)
        return 0

    return 1

def FindEdge(elements):
    # elements=[Element No, 1st Node, 2nd Node, 3rd Node, 4th Node, Mat_name, '']
    # edge element [node1, node2, ElsetName, FaceID, elementNo, Tie Definition No]
    i = 0
    edges = []
    while i < len(elements):
        if elements[i][6] == 4:
            edges.append([elements[i][1], elements[i][2], elements[i][5], 'S1', elements[i][0], -1])
            edges.append([elements[i][2], elements[i][3], elements[i][5], 'S2', elements[i][0], -1])
            edges.append([elements[i][3], elements[i][4], elements[i][5], 'S3', elements[i][0], -1])
            edges.append([elements[i][4], elements[i][1], elements[i][5], 'S4', elements[i][0], -1])
        elif elements[i][6] == 3:
            edges.append([elements[i][1], elements[i][2], elements[i][5], 'S1', elements[i][0], -1])
            edges.append([elements[i][2], elements[i][3], elements[i][5], 'S2', elements[i][0], -1])
            edges.append([elements[i][3], elements[i][1], elements[i][5], 'S3', elements[i][0], -1])
        i += 1
    return edges

def FindFreeEdge(edges):
    freeEdge = []
    npedge = []
    for e in edges: 
        npedge.append([e[0], e[1]])
    npedge = np.array(npedge)

    free = []
    cnt = 0 
    for ed in npedge: 
        idx1 = np.where(npedge[:,:]==int(ed[0]))[0]
        idx2 = np.where(npedge[:,:]==int(ed[1]))[0]
        idx = np.intersect1d(idx1, idx2) 
            
        if len(idx) == 1: 
            free.append(edges[cnt])
        cnt += 1 
    # print ("NO of Free Edge=", len(free))
    return free


def BeadWidth(Element, Node):
    BDCore = []

    for i in range(len(Element)):
        if Element[i][5] == 'BEAD_L':
            BDCore.append(Element[i])
    if len(BDCore) == 0:
        for i in range(len(Element)):
            if Element[i][5] == 'BEAD_R':
                BDCore.append(Element[i])
    BDEdge = FindEdge(BDCore)
    BDFree = FindFreeEdge(BDEdge)

    nodes = []
    for i in range(len(BDFree)):
        if i == 0:
            nodes.append(BDFree[i][0])
            nodes.append(BDFree[i][1])
        else:
            N = len(nodes)
            match1 = 0
            match2 = 0
            for j in range(N):
                if BDFree[i][0] == nodes[j]:
                    match1 = 1
                if BDFree[i][1] == nodes[j]:
                    match2 = 1
            if match1 == 0:
                nodes.append(BDFree[i][0])
            if match2 == 0:
                nodes.append(BDFree[i][1])
    N = len(nodes)
    center = Area(nodes, Node)
    min = 100000.0
    max = -100000.0

    for i in range(N):
        C = Coordinates(nodes[i], Node)
        if abs(C[1]) > max:
            max = abs(C[1])
        if abs(C[1]) < min:
            min = abs(C[1])

    if abs(center[1]) > abs(max) or abs(center[1]) < abs(min):
        center[1] = (abs(max)+abs(min))/2.0

    return abs(min), abs(max), abs(center[1])

def FindNextEdge(refEdge, Edges):
    tmpi = refEdge;
    connected = []
    for m in range(len(Edges)):
        if tmpi != m:
            if Edges[tmpi][1] == Edges[m][0]:
                connected.append(m)
    return connected

def FindPreviousEdge(refEdge, Edges):
    tmpi = refEdge;
    connected = []
    for m in range(len(Edges)):
        if tmpi != m:
            if Edges[tmpi][0] == Edges[m][1]:
                connected.append(m)
    return connected

def FindOutEdges(FreeEdge, CenterNodes, Nodes, Elements):
    # node of free edge is shared with another tie node
    # ShareNodePos -> 1 or 2
    # for fe in FreeEdge:
        # if fe[2] == "SUT":        print fe
    # for i in range(I):
    MAX = 10000
    ShareNodePos = []
    outEdge = []

    ## Find a 1st surround edge (IL at the center)
    # low = 1000000.0
    # i = 0
    # savei = 0
    # while i < len(CenterNodes):
    #     j = 0
    #     while j < len(Nodes):
    #         if CenterNodes[i] == Nodes[j][0]:
    #             if Nodes[j][3] < low:
    #                 low = Nodes[j][3]
    #                 savei = j
    #         j += 1
    #     i += 1
    # i = 0
    # while i < len(FreeEdge):
    #     if Nodes[savei][0] == FreeEdge[i][0]:
    #         break
    #     i += 1

    # print ("i=", i) 
    # print ("Center node", CenterNodes)
    # print ("fd index", savei)
    # print (Nodes[savei])

    nodes = np.array(Nodes)
    idx = np.where(nodes[:,2]<0.1E-03)[0]
    idx1 = np.where(nodes[:,2]>-0.1E-03)[0]
    idx = np.intersect1d(idx, idx1)
    cnodes = nodes[idx]
    cmin = np.min(cnodes[:,3])
    idx = np.where(nodes[:,3]==cmin)[0][0]
    center_minnode = Nodes[idx]

    for i, edge in enumerate(FreeEdge): 
        if center_minnode[0] == edge[0]: 
            break 

    ## End of 1st Outer Edge finding (IL1)


    # if len(FreeEdge) == i: 


    FreeEdge[i][5] = 1
    outEdge.append(FreeEdge[i])
    iFirstNode = FreeEdge[i][0]

    count = 0

    #    i=  # i is no matter how big, because i is redefined when next edge is found

    while i < len(FreeEdge):
        count += 1
        if count > MAX:
            print ('[INPUT] CANNOT FIND OUTER EDGES IN THE MODEL (too much iteration)')
            outEdge = []
            return outEdge
        j = 0
        while j < len(FreeEdge):
            if i != j:
                if FreeEdge[i][1] == FreeEdge[j][0]:
                    # print 'edge[i][1], [j][0] ', FreeEdge.edge[i], FreeEdge.edge[j], 'i=', i
                    ShareNodePos.append(j)
            j = j + 1
        #        print ('**', ShareNodePos)

        #        ShareNodePos=FindNextEdge()
        #        print (ShareNodePos, FreeEdge[ShareNodePos[0]][0])
        if len(ShareNodePos) != 0:
            if FreeEdge[ShareNodePos[0]][0] == iFirstNode:
                break
        else:
            print ('[INPUT] CANNOT FIND CONNECTED FREE EDGE. CHECK TIE CONDITION')
            outEdge=[]
            return outEdge
        # print 'sharenodePos count = ', len(ShareNodePos)
        if len(ShareNodePos) == 1:
            FreeEdge[ShareNodePos[0]][5] = 1
            outEdge.append(FreeEdge[ShareNodePos[0]])
            # print ("1,", FreeEdge[ShareNodePos[0]])
            i = ShareNodePos[0]

            del ShareNodePos
            ShareNodePos = []
        else:
            if FreeEdge[i][4] == FreeEdge[ShareNodePos[0]][4]:
                tmpPos = ShareNodePos[1]
                # print ("passed here")
            else:
                SHARE = ShareEdge(FreeEdge[i][4], FreeEdge[ShareNodePos[1]][4], Elements)
                if SHARE ==1:
                    tmpPos = ShareNodePos[0]
                else:
                    tmpPos = ShareNodePos[1]
                    nfe1 = 0; nfe2 = 0
                    for fe in FreeEdge:
                        if fe[4] == FreeEdge[tmpPos][4]:
                            # print (fe)
                            nfe1 += 1
                        if fe[4] == FreeEdge[ShareNodePos[0]][4]:
                            # print (fe)
                            nfe2 += 1
                    # print ("nfe=", nfe, FreeEdge[tmpPos])
                    if nfe1 < nfe2:
                        tmpPos = ShareNodePos[0]
                    elif nfe1 == nfe2:
                        tienode = FreeEdge[tmpPos][0]
                        nc = 0
                        for fe in FreeEdge:
                            if fe[4] == FreeEdge[tmpPos][4] and fe[1] == tienode: 
                                nc += 1
                                break
                        if nc == 0:   tmpPos = ShareNodePos[0]
                    

            FreeEdge[tmpPos][5] = 1
            outEdge.append(FreeEdge[tmpPos])
            # print ("2, ", FreeEdge[ShareNodePos[0]], FreeEdge[ShareNodePos[1]], "-", FreeEdge[tmpPos])
            i = tmpPos
            del ShareNodePos
            ShareNodePos = []
            

    return outEdge


def FindGeneralOutEdges(freeedges, centernodes, node, TieEdges):
    # freeedges & centernodes is lists
    # node of free edge is shared with another tie node
    # ShareNodePos -> 1 or 2

    ShareNodePos = []
    outEdge = []
    MAX = 2000

    ## Find a 1st surround edge (IL at the center)
    low = 1000000.0
    i = 0;
    savei = 0
    while i < len(centernodes):
        j = 0
        while j < len(node):
            if centernodes[i] == node[j][0]:
                if node[j][1] < low:
                    low = node[j][1]
                    savei = j
            j += 1
        i += 1

    ################ START right side OUTEDGES ###################################
    i = 0
    while i < len(freeedges):
        if node[savei][0] == freeedges[i][0]:
            break
        i += 1

    freeedges[i][5] = 1
    outEdge.append(freeedges[i])
    iFirstNode = freeedges[i][0]

    #    i=  # i is no matter how big, because i is redefined when next edge is found
    iteration = 0
    while i < len(freeedges):
        iteration += 1
        if iteration > MAX:
            print ('ERROR::PRE::[INPUT] Too many ITERATION FOR SEARCHING OUTEDGE')
            break


        ShareNodePos = FindNextEdge(i, freeedges)
        if freeedges[ShareNodePos[0]][0] == iFirstNode:
            break
        # print 'sharenodePos count = ', len(ShareNodePos)

        if len(ShareNodePos) == 1:
            freeedges[ShareNodePos[0]][5] = 1
            outEdge.append(freeedges[ShareNodePos[0]])
            i = ShareNodePos[0]

            del ShareNodePos;
            ShareNodePos = []
        elif len(ShareNodePos) == 2:
            #
            fn = ShareNodePos[0];
            sn = ShareNodePos[1]
            #
            if freeedges[fn][5] == 0:
                count = 0
                for j in range(len(TieEdges)):
                    if freeedges[fn][0] == TieEdges[j][0] and freeedges[fn][1] == TieEdges[j][1]:
                        i = sn
                        freeedges[sn][5] = 1
                        outEdge.append(freeedges[sn])
                        count += 1
                        break

                if count == 0:
                    i = fn
                    freeedges[fn][5] = 1
                    outEdge.append(freeedges[fn])
            else:
                i = sn
                freeedges[sn][5] = 1
                outEdge.append(freeedges[sn])

            ShareNodePos = []

        else:  # if 3, can be infinite loop
            exist = 0;
            save = 0;
            count = 0
            for i in range(len(ShareNodePos)):
                for j in range(len(outEdge)):
                    if freeedges[ShareNodePos[i]] == outEdge[j]:
                        exist = 1
                        break
                if exist == 0:
                    save = i
                    count += 1
            if count > 1:
                print ('ERROR::PRE::[INPUT] Cannot know where to go. 2 Way to go.', ShareNodePos)
            elif count == 0:
                print ('ERROR::PRE::[INPUT] No Way to go. ')
            else:
                freeedges[ShareNodePos[save]][5] = 1
                outEdge.append(freeedges[ShareNodePos[save]])
                i = ShareNodePos[save]

                del ShareNodePos;
                ShareNodePos = []

        cent = 0
        for m in range(len(centernodes)):
            if freeedges[i][0] == centernodes[m]:
                cent = 1
                break
        if cent == 1:
            break  # until center node edge... -> the end of right side Outedge finding

    ################ START left side OUTEDGES ###################################
    i = 0
    while i < len(freeedges):
        if node[savei][0] == freeedges[i][1]:
            break
        i += 1

    freeedges[i][5] = 1
    outEdge.append(freeedges[i])
    ilastNode = freeedges[i][1]

    ShareNodePos = []
    iteration = 0
    while i < len(freeedges):
        iteration += 1
        if iteration > MAX:
            print ('ERROR::PRE::[INPUT] Too many ITERATION FOR SEARCHING OUTEDGE')
            break

        ShareNodePos = FindPreviousEdge(i, freeedges)
        if freeedges[ShareNodePos[0]][1] == ilastNode:
            break

        if len(ShareNodePos) == 1:
            freeedges[ShareNodePos[0]][5] = 1
            outEdge.append(freeedges[ShareNodePos[0]])
            i = ShareNodePos[0]
            ShareNodePos = []
        elif len(ShareNodePos) == 2:
            #
            fn = ShareNodePos[0];
            sn = ShareNodePos[1]
            #
            if freeedges[fn][5] == 0:
                count = 0
                for j in range(len(TieEdges)):
                    if freeedges[fn][0] == TieEdges[j][0] and freeedges[fn][1] == TieEdges[j][1]:
                        i = sn
                        freeedges[sn][5] = 1
                        outEdge.append(freeedges[sn])
                        count += 1
                        break

                if count == 0:
                    i = fn
                    freeedges[fn][5] = 1
                    outEdge.append(freeedges[fn])
            else:
                i = sn
                freeedges[sn][5] = 1
                outEdge.append(freeedges[sn])

            ShareNodePos = []

        else:  # if 3, can be infinite loop
            exist = 0;
            save = 0;
            count = 0
            for i in range(len(ShareNodePos)):
                for j in range(len(outEdge)):
                    if freeedges[ShareNodePos[i]] == outEdge[j]:
                        exist = 1
                        break
                if exist == 0:
                    save = i
                    count += 1
            if count > 1:
                print ('ERROR::PRE::[INPUT] Cannot know where to go. 2 Way to go.')
                # logline.append(['ERROR::PRE::[INPUT] Cannot know where to go. 2 Way to go.\n'])
            elif count == 0:
                print ('ERROR::PRE::[INPUT] No Way to go. ')
                # logline.append(['ERROR::PRE::[INPUT] No Way where to go. \n'])
            else:
                freeedges[ShareNodePos[save]][5] = 1
                outEdge.append(freeedges[ShareNodePos[save]])
                i = ShareNodePos[save]

                ShareNodePos = []

        cent = 0
        for m in range(len(centernodes)):
            if freeedges[i][1] == centernodes[m]:
                cent = 1
                break
        if cent == 1:
            break  # until center node edge... -> the end of left side Outedge finding

    return outEdge

def FindTieLoop(TieStartNode, nextEdge, FreeEdge):
    # len(nextEdge) == 2

    MAX = 50
    NextWay = 0
    iNext = []
    startNode = FreeEdge[nextEdge[0]][0]

    if FreeEdge[nextEdge[0]][5] < 1:
        testEdge = nextEdge[0]
        saveEdge = testEdge
        if FreeEdge[testEdge][1] == TieStartNode:
            NextWay = testEdge
            return NextWay
    elif FreeEdge[nextEdge[1]][5] < 1:
        testEdge = nextEdge[1]
        saveEdge = testEdge
        if FreeEdge[testEdge][1] == TieStartNode:
            NextWay = testEdge
            return NextWay
    else:
        print ('[INPUT]', FreeEdge[nextEdge[0]], ',', FreeEdge[nextEdge[1]], ' (1) TIE Conection InCompletion')
        # logline.append(['ERROR::PRE::[INPUT] {' + str(FreeEdge[nextEdge[0]]) + ', ' + str(FreeEdge[nextEdge[1]] + '} - (1) TIE Connection Incompletion\n')])
        return 0

    #    print ('TieStart', TieStartNode, 'Node start', startNode)
    #    print ('**', FreeEdge[testEdge]) # 1st Edge

    for i in range(MAX):
        iNext = []

        iNext = FindNextEdge(testEdge, FreeEdge)

        if len(iNext) == 1:
            if FreeEdge[iNext[0]][5] < 1:
                if FreeEdge[iNext[0]][1] == TieStartNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[0]
                    else:
                        NextWay = nextEdge[1]
                    #                    print ('1.1',  FreeEdge[iNext[0]])
                    return NextWay
                elif FreeEdge[iNext[0]][1] == startNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[1]
                    else:
                        NextWay = nextEdge[0]
                    #                    print ('1.2',  FreeEdge[iNext[0]])
                    return NextWay
                else:
                    #                    print ('1', FreeEdge[iNext[0]])
                    testEdge = iNext[0]
            else:
                print ('[INPUT]', FreeEdge[iNext[0]], ' (2) TIE Conection InCompletion')
                # logline.append(['ERROR::PRE::[INPUT] {' + str(FreeEdge[nextEdge[0]]) + '} - (2) TIE Connection Incompletion\n'])
                return 0
        ##################### ***************** #########################

        elif len(iNext) == 2:  # if another tie is connected
            if FreeEdge[iNext[0]][5] < 1:
                testEdge = iNext[0]
                #                print ('3.1', FreeEdge[iNext[0]])

                if FreeEdge[iNext[0]][1] == TieStartNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[0]
                    else:
                        NextWay = nextEdge[1]
                    #                    print ('3.1.1',  FreeEdge[iNext[0]])
                    return NextWay
                elif FreeEdge[iNext[0]][1] == startNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[1]
                    else:
                        NextWay = nextEdge[0]
                    #                    print ('3.1.2',  FreeEdge[iNext[0]])
                    return NextWay

            elif FreeEdge[iNext[1][5]] < 1:
                testEdge = iNext[1]
                #                print ('3.2', FreeEdge[iNext[1]])

                if FreeEdge[iNext[1]][1] == TieStartNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[0]
                    else:
                        NextWay = nextEdge[1]
                    #                    print ('3.2.1',  FreeEdge[iNext[0]])
                    return NextWay
                elif FreeEdge[iNext[1]][1] == startNode:
                    if saveEdge == nextEdge[0]:
                        NextWay = nextEdge[1]
                    else:
                        NextWay = nextEdge[0]
                    #                    print ('3.2.2',  FreeEdge[iNext[1]])
                    return NextWay
    return NextWay

def FindTies(FreeEdge):
    global TIENUM
    TIENUM = 1
    i = 0;
    iTemp = 0;
    j = 0
    connectedEdge = []
    TieEdge = []
    while i < len(FreeEdge):

        if FreeEdge[i][5] < 1:
            TIENUM += 1
            nodeStart = FreeEdge[i][0]
            FreeEdge[i][5] = TIENUM
            TieEdge.append(FreeEdge[i])  # marked as TIE edge with No.
            iTemp = i
            #            print ('$$', FreeEdge[i])
            while FreeEdge[iTemp][1] != nodeStart:
                j += 1;
                if j > 100:
                    break  # in case infinite loop
                connectedEdge = FindNextEdge(iTemp, FreeEdge)  # find next edge

                if len(connectedEdge) == 1:  # in case of being found just 1 edge
                    iTemp = connectedEdge[0]

                elif len(connectedEdge) == 2:  # when other tie is connected (2 ties are connected)
                    if FreeEdge[connectedEdge[0]][1] == nodeStart:
                        iTemp = connectedEdge[0]
                    elif FreeEdge[connectedEdge[1]][1] == nodeStart:
                        iTemp = connectedEdge[1]
                    else:
                        if FreeEdge[connectedEdge[0]][5] < 1 and FreeEdge[connectedEdge[1]][5] < 1:
                            iTemp = FindTieLoop(nodeStart, connectedEdge, FreeEdge)
                        elif FreeEdge[connectedEdge[0]][5] < 1:
                            iTemp = connectedEdge[0]
                        elif FreeEdge[connectedEdge[1]][5] < 1:
                            iTemp = connectedEdge[1]
                        else:
                            print ('[INPUT] {' + str(FreeEdge[connectedEdge[0]]) + ',' + str(FreeEdge[connectedEdge[1]]) + ' (0) TIE Conection InCompletion')
                            # logline.append(['ERROR::PRE::[INPUT] {' + str(FreeEdge[connectedEdge[0]]) + ', ' + str(FreeEdge[connectedEdge[1]]) + '} - (0) TIE Connection Incompletion\n'])
                            break
                else:
                    print ('[INPUT] 2 or more Ties are Connected.')
                    # logline.append(['ERROR::PRE::[INPUT] 2 or more Ties are Connected.\n'])
                    break

                # After finding next TIE Edge ################################
                FreeEdge[iTemp][5] = TIENUM
                TieEdge.append(FreeEdge[iTemp])
            #                print ('  -', FreeEdge[iTemp])

            # print 'TIENUM = ', TIENUM, 'edge Node=', FreeEdge.edge[connectedEdge[0]][0], \
            # FreeEdge.edge[connectedEdge[0]][1], 'ref node = ', FreeEdge.edge[i][0], FreeEdge.edge[i][1]

            del connectedEdge;
            connectedEdge = []

        i += 1

    #    print ('** TIE EDGE*************')
    #    for i in range(len(TieEdge)):
    #        print (TieEdge[i])
    return TieEdge
    #### Found all Tie surfaces

def FindMaster(edges, Nodes):
    iNum = 2
    Tedges = [];
    length = 0.0
    sLength = 0.0;
    ratio = 0.01
    # logline.append(['* Master Edges\n'])
    while iNum <= TIENUM:
        k = 0;
        saveK = 0
        maxLength = 0.0
        sLength = 0
        while k < len(edges):
            if edges[k][5] == iNum:
                x1 = find_r(edges[k][0], Nodes)
                x2 = find_r(edges[k][1], Nodes)
                y1 = find_z(edges[k][0], Nodes)
                y2 = find_z(edges[k][1], Nodes)
                length = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
                sLength += length
                if length > maxLength:
                    maxLength = length
                    saveK = k
            k += 1

        sLength += -maxLength
        if sLength > maxLength * (1.0 + ratio) or sLength < maxLength * (1.0 - ratio):
            print ('[INP] TIE CREATION INCOMPLETE Master %s' % (edges[saveK]))
            # logline.append(['ERROR::PRE::[INP] TIE CREATION INCOMPLETE Master %s\n' % (edges[saveK])])

        Tedges.append(edges[saveK])
        # logline.append([' ' + str(edges[saveK]) + '\n'])
        iNum += 1
    # logline.append(['  Found ' + str(len(Tedges)) + ' Tie Masters\n'])
    return Tedges

def FindSlave(Elements, medge, edges):
    i = 0
    slaveedge = []
    # logline.append(['* Slave Edges\n'])
    if type(edges) != type(slaveedge): edges = edges.Edge
    if type(medge) != type(slaveedge): medge = medge.Edge
    while i < len(edges):
        j = 0
        slave = 0
        while j < len(medge):
            if edges[i][3] == medge[j][3] and edges[i][4] == medge[j][4]:
                slave = 0
                break
            else:
                slave = 1
                j += 1
        if slave == 1:
            slaveedge.append(edges[i])
            # logline.append([' ' + str(edges[i]) + '\n'])
        i += 1
    # logline.append(['  Found ' + str(len(slaveedge)) + ' Tie Slaves\n'])

    for i in range(len(slaveedge)):
        for j in range(len(Elements)):
            if slaveedge[i][4] == Elements[j][0] and Elements[j][6] == 3:
                print ('[INPUT] TIE Slave (%4d) Edge is a part of Triangular Element' % (slaveedge[i][4]))
                # logline.append(['ERROR::PRE::[INPUT] TIE Slave (%4d) Edge should not be a Triangular Element\n' % (slaveedge[i][4])])

    return slaveedge

def FindCenterNodes(Nodes):
    tlist = []
    if type(tlist) == type(Nodes):
        centers=[]
        for i in range(len(Nodes)):
            if Nodes[i][2] == 0:
                centers.append(Nodes[i][0])
    else: 
        centers=[]
        for i in range(len(Nodes.Node)):
            if Nodes.Node[i][2] == 0:
                centers.append(Nodes.Node[i][0])
    return centers
def FindBottomNodes(Nodes):
    tlist = []
    if type(tlist) == type(Nodes): 
        nds = np.array(Nodes) 
    else: 
        nds = np.array(Nodes.Node) 
    minz = np.min(nds[:, 3])
    idx = np.where(nds[:, 3] == minz)[0][0]
    if type(tlist) == type(Nodes): 
        minnode=[Nodes[idx]]
    else: 
        minnode=[Nodes.Node[idx]]
    return minnode 


def FindInnerFreeEdges(Oedge, medge): 
    residuals=[]
    for ed1 in Oedge: 
        mch = 0 
        for ed2 in medge: 
            if ed1[0] == ed2[0] and ed1[1] == ed2[1] : 
                mch = 1 
                break 
        if mch == 0: 
            residuals.append(ed1)
    return residuals 

def DivideInnerFreeEdgesToMasterSlave(edges, node_class): 
    nodes = node_class 

    masters=[]
    i = 0 
    while i < len(edges): 
        con1 = 0;         con2 = 0 
        c1e = [];         c2e = []
        
        N01 = nodes.NodeByID(edges[i][0])
        N02 = nodes.NodeByID(edges[i][1])
        ML = NodeDistance(N01, N02) 
        Ly=[N01[2], N02[2]]; Lz=[N01[3], N02[3]]
        MinY = min(Ly); MaxY = max(Ly)
        MinZ = min(Lz); MaxZ = max(Lz)
        tslave = []
        for j in range(len(edges)): 
            
            if i == j : continue 
            
            if edges[i][0] == edges[j][0] or edges[i][0] == edges[j][1] :
                N1 = nodes.NodeByID(edges[j][0])
                N2 = nodes.NodeByID(edges[j][1])
                SL = NodeDistance(N1, N2)  
                if ML < SL: 
                    continue 
                if edges[i][0] == edges[j][0]: 
                    if N2[2] >= MinY and N2[2] <= MaxY and N2[3] >= MinZ and N2[3] <= MaxZ: 
                        dist = DistanceFromLineToNode2D(N2, [N01, N02], onlydist=1)
                        if dist < .10E-03 : 
                            con1 = 1 
                            c1e = edges[j]
                            tslave.append(edges[j])
                else: 
                    if N1[2] >= MinY and N1[2] <= MaxY and N1[3] >= MinZ and N1[3] <= MaxZ: 
                        dist = DistanceFromLineToNode2D(N1, [N01, N02], onlydist=1)
                        if dist < .10E-03 : 
                            con1 = 1 
                            c1e = edges[j]
                            tslave.append(edges[j])

            if edges[i][1] == edges[j][0] or edges[i][1] == edges[j][1] : 
                N1 = nodes.NodeByID(edges[j][0])
                N2 = nodes.NodeByID(edges[j][1])
                SL = NodeDistance(N1, N2)  
                if ML < SL: 
                    continue 

                if edges[i][1] == edges[j][0]: 
                    if N2[2] >= MinY and N2[2] <= MaxY and N2[3] >= MinZ and N2[3] <= MaxZ: 
                        dist = DistanceFromLineToNode2D(N2, [N01, N02], onlydist=1)
                        if dist < .10E-03 : 
                            con2 = 1 
                            c2e = edges[j]
                            tslave.append(edges[j])
                else: 
                    if N1[2] >= MinY and N1[2] <= MaxY and N1[3] >= MinZ and N1[3] <= MaxZ: 
                        dist = DistanceFromLineToNode2D(N1, [N01, N02], onlydist=1)
                        if dist < .10E-03 : 
                            con2 = 1 
                            c2e = edges[j]
                            tslave.append(edges[j])

            if con1 == 1 and con2 ==1: 
                break 
        
        if con1 ==1 or con2 == 1: 
            masters.append([edges[i], tslave])
        i+=1 

    
    excluding = []
    isError = 0 
    TIE_ERROR = []
    for e in masters: 
        excluding.append(e[0])
        excluding.append(e[1][0])
        if len(e[1]) <2: 
            print ("## Error to fine Tie Master surface (%d)"%(e[0][4]))
            TIE_ERROR.append(e[0][4])
            isError = 1
            continue 
        excluding.append(e[1][1])
    if isError == 1: 
        master_edge=[];  slave_edge=[]
        return master_edge, slave_edge, TIE_ERROR

    print ("*No. of Master edges =%d"%(len(masters)))
    master_edge = []
    slave_edge = []
    for i, ed in enumerate(masters): 
        master_edge.append(ed[0])
        s_temp=[]
        s_temp.append(ed[1][0])
        s_temp.append(ed[1][1])
        if ed[1][0][0] == ed[1][1][1] or ed[1][0][1] == ed[1][1][0] : 
            slave_edge.append(s_temp)
            # print ("* Slave Edges %2d, No=%d"%(i, len(s_temp)))
            continue 

        nexts = ConnectedEdge(ed[1][0], edges, exclude=excluding)
        s_temp.append(nexts[0])
        # print (ed[0], ":", nexts)
        if nexts[0][0] != ed[1][1][1] and nexts[0][1] != ed[1][1][0] : 
            excluding.append(nexts[0]) 
            nexts = ConnectedEdge(nexts[0], edges, exclude=excluding)
            s_temp.append(nexts[0])
            # print (ed[0], ":::", nexts)
        slave_edge.append(s_temp)
        # print ("**Slave Edges %2d, No=%d"%(i, len(s_temp)))

    return master_edge, slave_edge, TIE_ERROR

def ConnectedEdge(edge, edges, exclude=[]): 
    con = []
    for e in edges: 
        if e[0] == edge[0] and e[1] == edge[1]: 
            continue 
        if e[1] == edge[0] or e[0] == edge[0]: 
            exc= 0 
            for ex in exclude: 
                if ex[0] == e[0] and ex[1] == e[1] : exc = 1
            if exc == 0:  con.append(e)
        if e[1] == edge[1] or e[0] == edge[1]: 
            exc= 0 
            for ex in exclude: 
                if ex[0] == e[0] and ex[1] == e[1] : exc = 1
            if exc == 0:  con.append(e)

    return con 


def TieSurface(Elements, Nodes):
    AllEdges=FindEdge(Elements)
    FreeEdges=FindFreeEdge(AllEdges)
    CenterNodes = FindCenterNodes(Nodes)
    OutEdges=FindOutEdges(FreeEdges, CenterNodes, Nodes, Elements)

    InnerFreeEdges = FindInnerFreeEdges(FreeEdges, OutEdges)
    ND =NODE()
    for n in Nodes:
        ND.Add(n)
    MasterEdges, SlaveEdges, Tie_error = DivideInnerFreeEdgesToMasterSlave(InnerFreeEdges, ND)
    # for ma, sl, in zip(MasterEdges, SlaveEdges): 
    #     print ("*******************")
    #     print (ma)
    #     print (sl)

    if len(Tie_error) > 0: 
        print ("## ERROR to find Tie Surfaces")
        print (Tie_error)
        sys.exit()
    
    ## generating surface for SWS 
    f = open("SWS_Elements.inp", 'w')
    f.write("*ELEMENT, TYPE=MGAX1, ELSET=SWS\n")
    el = []
    for e in Elements: 
        el.append(e[0])
    npel = np.array(el)
    elmax = np.max(npel)
    addnumber = (int(elmax)/1000+1)*1000 
    swscount = 100 
    for edge in OutEdges: 
        # print (edge, addnumber)
        # if edge[2] == "BSW":  f.write("%4d, %4d, %4d\n"%(edge[4]+addnumber, edge[0], edge[1]))
        if edge[2] == "BSW":  
            # print (elmax+swscount)
            f.write("%4d, %4d, %4d\n"%(elmax+swscount, edge[0], edge[1]))
            swscount += 1
        # if edge[2] == "BSW": 
        #     f.write("%d, %s\n"%(edge[4], edge[3]))

    # f.write("*MEMBRANE SECTION, ELSET=SWS, MATERIAL=S24\n0.00001\n")
    f.close()
    ####################################
    
    # OUT=EDGE()
    # for edge in OutEdges: 
    #   # if edge[4] == 2044: print ("Outer", edge)
    #    OUT.Add(edge)
    # OUT.Image(ND, file="OUT_EDGES")
    # FREE=EDGE()
    # for edge in FreeEdges: 
    #     # if edge[4] == 2044: print ("Free", edge)
    #     FREE.Add(edge)
    # FREE.Image(ND, file="FREE_EDGES")

    # FREE=EDGE()
    # for edge in InnerFreeEdges: 
    #     # print (edge)
    #     FREE.Add(edge)
    # FREE.Image(ND, file="Inner_FREE_EDGES")
    
    
    # sys.exit()

    # TieEdges=FindTies(FreeEdges)
    # MasterEdges=FindMaster(TieEdges, Nodes)
    # SlaveEdges=FindSlave(Elements, MasterEdges, TieEdges)
    return MasterEdges, SlaveEdges, OutEdges,CenterNodes, FreeEdges, AllEdges

def Change3DFace(Id):
    face=''
    if Id =='S1':
        face='S3'
    elif Id=='S2':
        face='S4'
    elif Id=='S3':
        face='S5'
    elif Id=='S4':
        face='S6'
    return face

def Surfaces(OutEdges, Node, OffsetLeftRight, TreadElset, AllElements):
    Press=[]; RimContact=[]; TreadToRoad=[]
    
    EOffset = NOffset = OffsetLeftRight
    

    Offset=[EOffset, NOffset]

    low = 100000000.0
    startNode = 0
    nextedge = []
    edgeNo = 0
    i = 0
    opposite = 0
    tmpY=0
    while i < len(Node):
        if Node[i][3] < low and Node[i][0] > Offset[0] and Node[i][2] > 0:
            low = Node[i][3]
            startNode = Node[i][0]
            tmpY = Node[i][2]
        i += 1
        if i > 100000:
            print ("[INPUT] Cannot Find the 1st Node for Pressure")
            return Press, RimContact, TreadToRoad

    for i in range(len(Node)):
        if low == Node[i][3] and tmpY == -Node[i][2]:
            opposite = Node[i][0]
            break

    i = 0
    while i < len(OutEdges):
        if OutEdges[i][0] == startNode:
            edgeNo = i
            break
        i += 1
        if i > 100000:
            print ("[INPUT] Cannot Find the 1st Edge for Pressure")
            return Press, RimContact, TreadToRoad

    i = edgeNo
    # print ('**', OutEdges[i]); count=0
    Press.append(OutEdges[edgeNo])
    count = 0
    while OutEdges[i][1] != opposite:
        nextedge = FindNextEdge(i, OutEdges)
        i = nextedge[0]
        # print ('**', OutEdges[i])
        Press.append(OutEdges[i])
        if count > 2 and Press[len(Press)-2][4]  == OutEdges[i][4]:
            break
        if count > 1000:  # in case of infinite loop!!
            break
        count+=1
    #    print ('No of press', len(Press))
    # ADD Bead Base Edge as Pressure Surface
    #    print (AllElements[0])

    MAXY = 0
    MINY = 100000000.0
    for i in range(len(AllElements)):
        if AllElements[i][5] == 'BEAD_R' or AllElements[i][5] == 'BEAD_L' or AllElements[i][5] == 'BD1':
            # print ("BD1 Elements", AllElements[i])
            for j in [1, 2, 3, 4]:
                if AllElements[i][j] != '':
                    ValueY = find_z(AllElements[i][j], Node)
                    if math.fabs(ValueY) > MAXY:
                        MAXY = math.fabs(ValueY)
                    if math.fabs(ValueY) < MINY:
                        MINY = math.fabs(ValueY)
    AVGY = (MAXY + MINY) / 2.0
    # print ("find No", AVGY, MAXY, MINY)

    iNext = nextedge[0]
    nextedge = FindNextEdge(iNext, OutEdges)
    ValueY = find_z(OutEdges[nextedge[0]][1], Node)
    c=0

    # while math.fabs(ValueY) < AVGY:
    while math.fabs(ValueY) < MINY:
        Press.append(OutEdges[nextedge[0]])
        iNext = nextedge[0]
        nextedge = FindNextEdge(iNext, OutEdges)
        ValueY = find_z(OutEdges[nextedge[0]][1], Node)
        c += 1
        if c > 100000:
            print ('[INPUT] Cannot Find the next Pressure Edge (Right)')
            return Press, RimContact, TreadToRoad


    previousedge = FindPreviousEdge(edgeNo, OutEdges)
    ValueY = find_z(OutEdges[previousedge[0]][0], Node)
    c=0
    # while math.fabs(ValueY) < AVGY:
    while math.fabs(ValueY) < MINY:
        Press.append(OutEdges[previousedge[0]])
        iNext = previousedge[0]
        previousedge = FindPreviousEdge(iNext, OutEdges)
        ValueY = find_z(OutEdges[previousedge[0]][0], Node)
        c += 1
        if c > 100000:
            print ('[INPUT] Cannot Find the next Pressure Edge (Left)')
            return Press, RimContact, TreadToRoad

    #    print ('No of press', len(Press))

    if len(Press) < 1:
        print ('[INPUT] No Surface was created for Inner Pressure')
        return Press, RimContact, TreadToRoad
        # logline.append(['ERROR::PRE::[INPUT] No Surface was created for Inner Pressure\n'])
    else:
        print ('* All Edges for Pressure are searched.')
        # logline.append(['* All Surfaces for Pressure are searched. \n'])

    i = 0
    while i < len(OutEdges):
        if OutEdges[i][2] == 'HUS' or OutEdges[i][2] == 'RIC':
            ipress = 0
            if ipress == 0:
                RimContact.append(OutEdges[i])
                # print "Rim Contact", OutEdges[i]
        i += 1
        if i > 100000:
            print ('[INPUT] Cannot Find the Next Outer Edges ')
            return Press, RimContact, TreadToRoad

    #############################################
    ## ADD 5 edges of BSW
    #############################################
    NoOfAddingEdge = 5
    for i in range(len(RimContact)):
        for j in range(len(OutEdges)):
            if RimContact[i] == OutEdges[j]:
                break
        ne = FindNextEdge(j, OutEdges)
        m=ne[0]
        if OutEdges[m][2] == 'BSW':
            RimContact.append(OutEdges[m])
            for j in range(NoOfAddingEdge-1):
                ne= FindNextEdge(m, OutEdges)
                n=ne[0]
                if OutEdges[n][2] == 'BSW':
                    RimContact.append(OutEdges[n])
                m = n
        ne = FindPreviousEdge(j, OutEdges)
        m = ne[0]
        if OutEdges[m][2] == 'BSW':
            RimContact.append(OutEdges[m])
            for j in range(NoOfAddingEdge-1):
                ne= FindPreviousEdge(m, OutEdges)
                n = ne[0]
                if OutEdges[n][2] == 'BSW':
                    RimContact.append(OutEdges[n])
                m = n
    ###############################################

    if len(RimContact) < 1:
        print ('ERROR::PRE::[INPUT] No Surface was created for Rim Contact  ')
        return Press, RimContact, TreadToRoad
        # logline.append(['ERROR::PRE::[INPUT] No Surface was created for Rim Contact\n'])
    else:
        print ('* All Edges for Rim Contact are searched.')
        # logline.append(['* All Surfaces for Rim Contact are searched. \n'])
    i = 0
    while i < len(OutEdges):
        j = 0
        while j < len(TreadElset):
            if OutEdges[i][2] == TreadElset[j]:
                TreadToRoad.append(OutEdges[i])
                break
            j += 1
            if j > 100000:
                print ('[INPUT]Cannot Find the Next Tread To Road Edges ')
                return Press, RimContact, TreadToRoad
        i += 1


    if len(TreadToRoad) < 1:
        print ('[INPUT] No Surface was created for Road Contact')
        return Press, RimContact, TreadToRoad
        # logline.append(['ERROR::PRE::[INPUT] No Surface was created for Road Contact\n'])
    else:
        print ('* All Edges for Road Contact are searched.')
        # logline.append(['* All Surfaces for Road Contact are searched. \n'])

    return Press, RimContact, TreadToRoad

def FindSolidElementBetweenMembrane(m1, m2, Elements):
    # Data types of m1, m2 are string
    between = []
    Elm1 = []
    Elm2 = []

    for i in range(len(Elements)):
        if Elements[i][5] == m1 or Elements[i][5] == m2:
            for j in range(len(Elements)):
                if j != i and Elements[j][6] == 3:
                    for k in range(1, 3):
                        if k == 1:
                            m = 2
                        else:
                            m = 1
                        for l in range(1, 4):
                            n = l + 1
                            if n > 3:
                                n = l - 3

                            if Elements[i][k] == Elements[j][l] and Elements[i][m] == Elements[j][n]:
                                if Elements[i][5] == m1:
                                    Elm1.append(Elements[j])
                                else:
                                    Elm2.append(Elements[j])
                                break

                elif j != i and Elements[j][6] == 4:
                    for k in range(1, 3):
                        if k == 1:
                            m = 2
                        else:
                            m = 1
                        for l in range(1, 5):
                            n = l + 1
                            if n > 4:
                                n = l - 4

                            if Elements[i][k] == Elements[j][l] and Elements[i][m] == Elements[j][n]:
                                if Elements[i][5] == m1:
                                    Elm1.append(Elements[j])
                                else:
                                    Elm2.append(Elements[j])
                                break

    for i in range(len(Elm1)):
        for j in range(len(Elm2)):
            if Elm1[i][0] == Elm2[j][0]:
                between.append(Elm2[j][0])
                break

    m1f=[]
    m2f=[]
    for i in range(len(Elm1)):
        match=0
        for j in range(len(between)):
            if Elm1[i][0] == between[j]:
                match = 1
                break
        if match == 0:
            m1f.append(Elm1[i])

    for i in range(len(Elm2)):
        match = 0
        for j in range(len(between)):
            if Elm2[i][0] == between[j]:
                match = 1
                break
        if match == 0:
            m2f.append(Elm2[i])
    ########################################################
    for i in range(len(m2f)):
        for j in range(len(m1f)):
            match = 0
            for m in range(1, 5):
                for n in range(1, 5):
                    if m2f[i][m] == m1f[j][n] and m1f[j][n] != '':
                        match += 1
            if match == 2:
                between.append(m2f[i][0])
                between.append(m1f[j][0])
                # print "Between Appended"
                break


    return between

def DivideTreadAndBody(AllElements, TreadElset, Node):

    Tread=[]
    Body = []

    i = 0
    while i < len(AllElements):
        j = 0;
        tread = 0
        while j < len(TreadElset):
            if AllElements[i][5] == TreadElset[j]:
                tread = 1
                break
            j += 1
        if tread == 1:
            Tread.append(AllElements[i])
        else:
            Body.append(AllElements[i])

        i += 1

    BodyNode=[]
    TreadNode=[]
    for i in range(len(Node)):
        match = 0
        for j in range(len(Tread)):
            for m in range(1, 5):
                if Tread[j][m] == Node[i][0]:
                    match =1
                    break
            if match == 1:
                break
        if match ==1:
            TreadNode.append(Node[i])
        match =0
        for j in range(len(Body)):
            match = 0
            for m in range(1, 5):
                if Body[j][m] == Node[i][0]:
                    match =1
                    break
            if match ==1:
                break
        if match ==1 :
            BodyNode.append(Node[i])


    print ('* Number of TREAD NODEs : ' + str(len(TreadNode)))
    print ('* Number of BODY NODEs  : ' + str(len(BodyNode)))

    return TreadNode, BodyNode, Tread, Body

def Divide_Tread_Body_TBR_StandardMesh(AllElements, Node, TreadSurf, OutEdges): 

    print ("## TBR STANDARD MESH #######################")

    nd = NODE()
    for n in Node: 
        nd.Add(n)
    
    Tread = []
    Body = []
    
    membrane = []; solids = []
    Temps = []
    for e in AllElements: 
        if e[3] == "":   e[3] = 0
        if e[4] == "":   e[4] = 0
        if e[6] == 2:
            membrane.append([e[0], e[1], e[2], 2])
        else: 
            
            solids.append([e[0], e[1], e[2], e[3], e[4], e[6]])
        
        Temps.append([e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9]])
    AllElements = Temps 
    solids= np.array(solids)

    

    center = []
    for mem in membrane: 
        N = nd.NodeByID(mem[1])
        if N[2] ==0: 
            center.append([mem[0], mem[1], mem[2], N[3]])
            continue
        N = nd.NodeByID(mem[2])
        if N[2] ==0: 
            center.append([mem[0], mem[1], mem[2], N[3]])
            continue

    center = sorted(center, key=lambda x: x[3])
    topmembrane = center[len(center)-1]

    n1 = topmembrane[1]; n2 = topmembrane[2]
    solid_on_membrane = []
    pos = 0; neg = 0 
    for e in AllElements:
        cnt = 0
        f = 0
        if e[6] == 3: 
            if n1 == e[1] or n2 == e[1]: 
                cnt += 1
                f+=1
            if n1 == e[2] or n2 == e[2]: 
                cnt += 1
                f+=2
            if n1 == e[3] or n2 == e[3]: 
                cnt += 1
                f+=3
        elif e[6] == 4: 
            if n1 == e[1] or n2 == e[1]: 
                cnt += 1
                f+=0
            if n1 == e[2] or n2 == e[2]: 
                cnt += 1
                f+=2
            if n1 == e[3] or n2 == e[3]: 
                cnt += 1
                f+=3
            if n1 == e[4] or n2 == e[4]: 
                cnt += 1
                f+=4
        ht = []
        if cnt > 1: 
            N = nd.NodeByID(e[1])
            ht.append(N[3])
            N = nd.NodeByID(e[2])
            ht.append(N[3])
            N = nd.NodeByID(e[3])
            ht.append(N[3])
            if e[6] == 4: 
                N = nd.NodeByID(e[4])
                ht.append(N[3])

        if cnt == 2 and max(ht) > topmembrane[3]: 
            solid_on_membrane = e 
            if e[6] == 3 and f == 3: btm_face = 1
            if e[6] == 3 and f == 5: btm_face = 2
            if e[6] == 3 and f == 4: btm_face = 3
            if e[6] == 4 and f == 2: btm_face = 1
            if e[6] == 4 and f == 5: btm_face = 2
            if e[6] == 4 and f == 7: btm_face = 3
            if e[6] == 4 and f == 4: btm_face = 4

            if e[5] != 'CTB' and e[5] != 'CTR' and e[5] != 'SUT' and e[5] != 'UTR'  and e[5] != 'TRW': 
                nf = btm_face + 2 
                if nf > e[6]: nf -= e[6] 
                
                ns = [solid_on_membrane[0], solid_on_membrane[1], solid_on_membrane[2], solid_on_membrane[3], solid_on_membrane[4], solid_on_membrane[6]]
                # print (solid_on_membrane, nf)
                ns, nf = SearchNextSolids(ns, face=nf, np_solid=solids, direction=1)
                # print (ns, nf)
                elno = int(ns[0])
                for en in AllElements:
                    if en[0] == elno: 
                        solid_on_membrane = en 
                        break 
            pos = btm_face -1 
            neg = btm_face + 1
            if pos == 0 : pos = e[6]
            if neg > e[6] : neg = 1 
            break 

    print ("* Center element above the top memebrane: %d"%(solid_on_membrane[0]))

    debug = 0
    MaxLdist = 10.0; MaxRdist = 10.0


    nextsolid = [solid_on_membrane[0], solid_on_membrane[1], solid_on_membrane[2], solid_on_membrane[3], solid_on_membrane[4], solid_on_membrane[6]]
    element_to_delete=[]
    Pos_elements=[]
    Pos_elements.append(nextsolid)
    #############################################################       
    element_to_delete.append(nextsolid[0])
    nf = pos - 1 
    if nf == 0 : nf = nextsolid[5] 
    ns = nextsolid
    cnt = 0 
    while nf != 0 : 
        ns, nf = SearchNextSolids(ns, face=nf, np_solid=solids, direction=1)
        if len(ns) > 0: element_to_delete.append(ns[0])
        cnt += 1
        if cnt > 100: 
            print ("Too many interation.. to search the element to delete")
            break 
    #############################################################       

    next_face = pos
    cnt = 0 
    start_triangular = 0 
    while next_face != 0: 
        ## WARNING!! if there is a tie surface on the element, errer may occur  ###########################
        ps = nextsolid
        
        nextsolid, next_face = SearchNextSolids(nextsolid, face=next_face, np_solid=solids, direction=1)
        if len(nextsolid) == 0: break 

        if start_triangular == 0: 
            _, face = Contact_relation_2Elements(nextsolid, ps)
            nf = face + 1 
            if nf > nextsolid[5] : nf = 1 
        else: 
            nf = next_face 
        
        #############################################################            
        temp = [nextsolid[0]]
        if debug ==1: print ("#", nextsolid, next_face, ps)   ########### 
        ns = nextsolid


        cnt = 0 
        while nf != 0 and len(ns): 
            cnt += 1
            if cnt > 20:  
                print ("Too many interation.. to search the element to delete (tread element divided)")
                break 

            tns = ns; tnf = nf 
            ns, nf = SearchNextSolids(ns, face=nf, np_solid=solids, direction=1)
            if len(ns) == 0: break 

            if debug ==1: print ("  : ", ns, nf, "     (Previous : ", tns, tnf, ")")
            
            if len(ns)> 0 and ns[0] == temp[len(temp)-2]:  ## check the searching direction. if the IDs are the same, it goes back again (searched the element that it already had). 
                    nf -= 1
                    if nf ==0: nf = tns[5] 
                    ns, nf = SearchNextSolids(tns, face=nf, np_solid=solids, direction=1)
                    # print ("  Corrected ->  ", ns, nf)
            if len(ns) > 0:  
                if ns[5] ==3: ## including elements to delete surrounding 3-node element
                    
                    tmp_solid = [int(ns[0]), int(ns[1]),int(ns[2]),int(ns[3]),int(ns[4]), "", int(ns[5])]
                    connected = SearchConnectedElement(tmp_solid, AllElements)
                    # print ("         ", ns, nf,  len(connected))
                    ii = 0
                    while ii < len(connected): 
                        jj = ii+1 
                        while jj < len(connected): 
                            if connected[ii][0] == connected[jj][0]: 
                                del(connected[jj])
                                jj -= 1
                            jj += 1
                        ii += 1

                    # for ii in connected:
                        # print ("         >>> ", ii[0])
                    if len(connected) <3: 
                        temp.append(ns[0])
                        ns=[]
                    else: 
                        nf -= 1
                        if nf ==0 : nf = ns[5] 

            if len(ns) > 0:  ## residual elements to delete by dividing 2 elements 
                temp.append(ns[0])
                ## in case of dividing into 2 elements,  collecting all elements which are connected. 
            
                tmp_solid = [int(ns[0]), int(ns[1]),int(ns[2]),int(ns[3]),int(ns[4]), "", int(ns[5])]
                connected = SearchConnectedElement(tmp_solid, AllElements)

                baseht = []
                bht = 0 
                n1 =tmp_solid[1]; n2 = tmp_solid[2]; n3=tmp_solid[3]
                N1 = nd.NodeByID(n1); N2 = nd.NodeByID(n2); N3 = nd.NodeByID(n3)
                baseht.append(abs(N1[3])); baseht.append(abs(N2[3])); baseht.append(abs(N3[3]) )
                if tmp_solid[6] ==4: 
                    n4=tmp_solid[4]
                    N4 = nd.NodeByID(n4)
                    baseht.append(abs(N4[3]) )
                bht = max(baseht)

                k = 0
                while k < len(connected):
                    if connected[k][6] == 2: 
                        del(connected[k])
                        break 
                    k+=1
                
                for cn in connected: 
                    lat = []
                    hts = []
                    try: 
                        N1 = nd.NodeByID(cn[1]); N2 = nd.NodeByID(cn[2]); N3 = nd.NodeByID(cn[3])
                    except: 
                        print (cn)
                    lat.append(abs(N1[2])); lat.append(abs(N2[2])); lat.append(abs(N3[2]) )
                    hts.append(abs(N1[3])); hts.append(abs(N2[3])); hts.append(abs(N3[3]) )
                    if cn[6] ==4: 
                        N4 = nd.NodeByID(cn[4])
                        lat.append(abs(N4[2]) )
                        hts.append(abs(N4[3]) )
                    MaxY = max(lat)
                    MaxZ = max(hts)
                    if MaxY <= MaxRdist and (cn[5] == 'CTR' or cn[5] == 'CTB' or cn[5] == 'SUT' or cn[5] == 'UTR' or cn[5] == 'TRW' or cn[5] == 'BSW') and bht < MaxZ: 
                        element_to_delete.append(cn[0])
            if len(ns) > 0 : 
                if ns[5] ==3:
                    _, face = Contact_relation_2Elements(ns, tns)
                    nf = face -1 
                    if nf ==0: nf = 3 
                    if debug ==1: print ("   Face corrected to ", nf)
                
        for tm in temp: 
            element_to_delete.append(tm)
        
        # if temp[len(temp)-1] == LastRight_EL: 
        #     break 

        if debug ==1: print ("previous elemetn checking before going next ", nextsolid, next_face)# , end="   >> ")

        if nextsolid[5] ==3: 
            _, face = Contact_relation_2Elements(nextsolid, ps)
            face += 1 
            if face == 4: face = 1 
            nxsolid, nxface = SearchNextSolids(nextsolid, face=face, np_solid=solids, direction=1)
            _, nxface = Contact_relation_2Elements(nxsolid, nextsolid)
            face = nxface - 1
            if face == 0 : face =  nxsolid[5]
            ps = nextsolid 
            nextsolid, _ = SearchNextSolids(nxsolid, face=face, np_solid=solids, direction=1)

            _, face = Contact_relation_2Elements(nextsolid, nxsolid)
            next_face = face + 1 
            if next_face >  nextsolid[5] : next_face = 1

            element_to_delete.append(nextsolid[0])
            start_triangular = 1 

            if debug ==1: print (" Found elements next to 3-node element", nextsolid, next_face, " << ", ps)


        else:
            if start_triangular == 1: 
                next_face += 1
                if next_face > nextsolid[5]: next_face = 1
            start_triangular = 0 

        if debug ==1: print (nextsolid, next_face)
        ###########################################################
        
        if len(nextsolid) > 0: Pos_elements.append(nextsolid)
        cnt += 1
        if cnt > 200:# or nextsolid[5] == 3: 
            break 

    
    nextsolid = [solid_on_membrane[0], solid_on_membrane[1], solid_on_membrane[2], solid_on_membrane[3], solid_on_membrane[4], solid_on_membrane[6]]

    #############################################################       
    element_to_delete.append(nextsolid[0])
    nf = neg + 1 
    if neg > nextsolid[5] : nf = 1 
    ns = nextsolid
    cnt = 0 
    while nf != 0 : 
        ns, nf = SearchNextSolids(ns, face=nf, np_solid=solids, direction=1)
        if len(ns) > 0: element_to_delete.append(ns[0])
        cnt += 1
        if cnt > 100: 
            print ("Too many interation... to search the element to delete")
            break 
    #############################################################
    
    Neg_elements=[]
    next_face = neg
    cnt = 0 
    start_triangular = 0 
    while next_face != 0:
        ## WARNING!! if there is a tie surface on the element, errer may occur  ###########################
        ps = nextsolid         
        nextsolid, next_face = SearchNextSolids(nextsolid, face=next_face, np_solid=solids, direction=-1)
        if len(nextsolid) == 0: break 
        if start_triangular == 0: 
            _, face = Contact_relation_2Elements(nextsolid, ps)
            nf = face - 1 
            if nf ==0: nf = nextsolid[5]
        else: 
            nf = next_face 

        if debug ==1: print ("\n* ", nextsolid, next_face, ps)   ###########   
        #############################################################  
        # if len(nextsolid) == 0: break 
        
        temp = [nextsolid[0]]
        ns = nextsolid
        cnt = 0 
        while nf != 0 and len(ns):   ## search the above elements  
            cnt += 1
            if cnt > 20:  
                print ("Too many interation.... to search the element to delete (tread element divided)")
                break 
            tns = ns; tnf = nf 
            ns, nf = SearchNextSolids(ns, face=nf, np_solid=solids, direction=1)
            if len(ns) == 0: break 
            if debug ==1: print ("  : ", ns, nf, "(Previous : ", tns, tnf, ")")
            if len(ns)> 0 and  ns[0] == temp[len(temp)-2]:   ## check the searching direction. if the IDs are the same, it goes back again (searched the element that it already had). 
                nf += 1
                if nf > 3: nf -= 3 
                ns, nf = SearchNextSolids(tns, face=nf, np_solid=solids, direction=1)
                # print ("  Corrected ->  ", ns, nf)

            if len(ns) > 0:   ## including elements to delete surrounding 3-node element
                if ns[5] ==3: 
                    
                    tmp_solid = [int(ns[0]), int(ns[1]),int(ns[2]),int(ns[3]),int(ns[4]), "", int(ns[5])]
                    connected = SearchConnectedElement(tmp_solid, AllElements)
                    # print ("         ", ns, nf,  len(connected))

                    ii = 0
                    while ii < len(connected): 
                        jj = ii+1 
                        while jj < len(connected): 
                            if connected[ii][0] == connected[jj][0]: 
                                del(connected[jj])
                                jj -= 1
                            jj += 1
                        ii += 1

                    # for ii in connected:
                    #     print ("         >>> ", ii[0])
                    if len(connected) <3: 
                        temp.append(ns[0])
                        ns=[]
                    else: 
                        nf += 1
                        if nf > ns[5]: nf -= ns[5]

                    # print ('nf=%d'%(nf))

            if len(ns) > 0:  ## residual elements to delete by dividing 2 elements 
                ## There are 2 possible cases 
                ## 1. in case that the tread element is not divided but just surrounded by other elements 
                ## 2. in case of dividing into 2 elements

                ## the below is for case 2 residual elements: 
                temp.append(ns[0])
                
            
                tmp_solid = [int(ns[0]), int(ns[1]),int(ns[2]),int(ns[3]),int(ns[4]), "", int(ns[5])]
                connected = SearchConnectedElement(tmp_solid, AllElements)

                baseht = []
                bht = 0 
                n1 =tmp_solid[1]; n2 = tmp_solid[2]; n3=tmp_solid[3]
                N1 = nd.NodeByID(n1); N2 = nd.NodeByID(n2); N3 = nd.NodeByID(n3)
                baseht.append(abs(N1[3])); baseht.append(abs(N2[3])); baseht.append(abs(N3[3]) )
                if tmp_solid[6] ==4: 
                    n4=tmp_solid[4]
                    N4 = nd.NodeByID(n4)
                    baseht.append(abs(N4[3]) )
                bht = max(baseht)

                k = 0
                while k < len(connected):
                    if connected[k][6] == 2: 
                        del(connected[k])
                        break 
                    k+=1
                
                for cn in connected: 
                    lat = []
                    hts = []
                    try: 
                        N1 = nd.NodeByID(cn[1]); N2 = nd.NodeByID(cn[2]); N3 = nd.NodeByID(cn[3])
                    except: 
                        print ("*** ", cn)
                    lat.append(abs(N1[2])); lat.append(abs(N2[2])); lat.append(abs(N3[2]) )
                    hts.append(abs(N1[3])); hts.append(abs(N2[3])); hts.append(abs(N3[3]) )
                    if cn[6] ==4: 
                        N4 = nd.NodeByID(cn[4])
                        lat.append(abs(N4[2]) )
                        hts.append(abs(N4[3]) )
                    MaxY = max(lat)
                    MaxZ = max(hts)
                    if MaxY <= MaxLdist and (cn[5] == 'CTR' or cn[5] == 'CTB' or cn[5] == 'SUT' or cn[5] == 'UTR' or cn[5] == 'TRW' or cn[5] == 'BSW') and bht < MaxZ: 
                        element_to_delete.append(cn[0])

            if len(ns) > 0 : 
                if ns[5] ==3:
                    _, face = Contact_relation_2Elements(ns, tns)
                    nf = face +1 
                    if nf ==4: nf = 1 
                    if debug ==1: print ("   Face corrected to ", nf)
                


        for tm in temp: 
            element_to_delete.append(tm)
        # if temp[len(temp)-1] == LastLeftt_EL: 
        #     break 

        # print ("previous elemetn checking before going next ", nextsolid, next_face)

        if nextsolid[5] ==3: 
            _, face = Contact_relation_2Elements(nextsolid, ps)
            face -= 1 
            if face ==0: face = 3 
            nxsolid, nxface = SearchNextSolids(nextsolid, face=face, np_solid=solids, direction=1)
            _, nxface = Contact_relation_2Elements(nxsolid, nextsolid)
            face = nxface + 1
            if face > nxsolid[5]:   face = 1 
            nextsolid, _ = SearchNextSolids(nxsolid, face=face, np_solid=solids, direction=1)

            _, face = Contact_relation_2Elements(nextsolid, nxsolid)
            next_face = face -1 
            if next_face == 0: next_face = nextsolid[5] 

            element_to_delete.append(nextsolid[0])
            start_triangular = 1 

            if debug ==1: print (" Found elements next to 3-node element", nextsolid, next_face)


        else:
            if start_triangular == 1: 
                next_face -= 1
                if next_face ==0: next_face =  nextsolid[5]
            start_triangular = 0 

        ###########################################################


        if len(nextsolid) > 0: Neg_elements.append(nextsolid)
        cnt += 1
        if cnt > 200 :#or nextsolid[5] == 3:  
            break 

    element_to_delete = np.array(element_to_delete)
    element_to_delete = np.unique(element_to_delete)

    NEL=ELEMENT()
    undelete = []
    cnt = 0 
    for e in AllElements: 
        f = 0 
        for number in element_to_delete: 
            if e[0] == number: 
                f = 1 
                break
        if e[5] != "CTR" and e[5] != "CTB" and e[5] != "SUT" and e[5] != "UTR" and e[5] != "BSW" and e[5] != "TRW": 
            f = 0
            undelete.append(e[0])
        if f ==0: 
            NEL.Add(e)
            # print ("Remain")
            continue
        cnt += 1 
        # print (" %4d : Deleted (%d)"%(e[0], cnt))
    # print (len(el.Element), len(NEL.Element), len(element_to_delete), len(el.Element) - len(NEL.Element))
    
    for en in undelete: 
        i = 0 
        while i < len(element_to_delete): 
            if en == element_to_delete[i] : 
                element_to_delete= np.delete(element_to_delete, i)
                break 
            i += 1
    
    Body = []
    top_el=[]
    for e in AllElements: 
        if e[5] == "CTR" or e[5] == "CTB" or e[5] == "UTR" or e[5] == "SUT" or e[5] == "TRW": 
            top_el.append(e)
        else: 
            if e[3] == 0: e[3] = ""
            if e[4] == 0: e[4] = ""
            Body.append([e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9]])

    Tread = []
    cand=[]
    for e in top_el: 
        f = 0
        for d in element_to_delete: 
            if e[0] == d: 
                f = 1
                break 
        if f == 0: 
            cand.append(e) 
        else: 
            if e[3] == 0: e[3] = ""
            if e[4] == 0: e[4] = ""
            Tread.append([e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9]])
            
    
    del_el = []
    hts = []
    for d in element_to_delete: 
        for e in top_el: 
            if e[0] == d: 
                del_el.append([d, e[9]])
                hts.append(e[9])
                break 
    minht = min(hts)
    new=[]
    # print (len(cand))
    for i, e in enumerate(cand): 
        # print ("%2d, %4d, Min ht = %7.2f, EL Ht = %7.2f, Diff= %7.2f"%(i, e[0], minht*1000, e[9]*1000, (minht-e[9])*1000))
        if minht < e[9]: 
            # print ("                              >>>>> add ")
            f = 0 
            for de in element_to_delete: 
                if de == e[0] : 
                    f = 1
                    break 
            if f == 0: 
                element_to_delete = np.append(element_to_delete, e[0])
                new.append(e[0])
    # print ("Tread Elements to separate")
    # print (element_to_delete)

    for e in top_el: 
        f = 0
        for d in new: 
            if e[0] == d: 
                f = 1
                break 
        if f == 1: 
            if e[3] == 0: e[3] = ""
            if e[4] == 0: e[4] = ""
            Tread.append([e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9]])
        else: 
            j = 0 
            for de in element_to_delete: 
                if de == e[0]: 
                    j = 1
                    break 
            if j == 0: 
                if e[3] == 0: e[3] = ""
                if e[4] == 0: e[4] = ""
                Body.append([e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], e[9]])

        
    if len(AllElements) != len(Tread) + len(Body) : 
        print ("ERROR!!, It may be error to distinguish between TREAD and Body, Total Elements=%d, Body=%d, Tread=%d Sum=%d"%(len(AllElements), len(Body), len(Tread), len(Body)+len(Tread)))

    TNode=[]
    BNode=[]

    nds = []
    for td in Tread: 
        nds.append(td[1])
        nds.append(td[2])
        if td[3] != "": nds.append(td[3])
        if td[4] != "": nds.append(td[4])
    nds = np.array(nds)
    nds = np.unique(nds)

    for n in nds: 
        for d in nd.Node: 
            if n == d[0]: 
                TNode.append(d)
                break 

    nds = []
    for td in Body: 
        nds.append(td[1])
        nds.append(td[2])
        if td[3] != "": nds.append(td[3])
        if td[4] != "": nds.append(td[4])
    nds = np.array(nds)
    nds = np.unique(nds)

    for n in nds: 
        for d in nd.Node: 
            if n == d[0]: 
                BNode.append(d)
                break 

    ## TreadSurf [N1, N2, "SET_NAME", "FACE", EL_Num, 1]

    # print ("Total Tread Surface =%d"%(len(TreadSurf)))

    i=0
    while i <len(TreadSurf):
        f = 0 
        for e in Tread: 
            if TreadSurf[i][4] == e[0]: 
                f = 1
                break
        if f ==0: 
            del(TreadSurf[i])
            i -= 1
        i += 1

    # print ("Total Tread Surface =%d"%(len(TreadSurf)))

    BodyEdges = FindEdge(Body)
    BodyFreeEdges = FindFreeEdge(BodyEdges)
    CenterNodes = FindCenterNodes(BNode)
    BodyOutEdges = FindOutEdges(BodyFreeEdges, CenterNodes, BNode, Body)

    TreadEdges = FindEdge(Tread)
    TreadFreeEdges = FindFreeEdge(TreadEdges)
    CenterNodes = FindCenterNodes(TNode)
    TreadOutEdges = FindOutEdges(TreadFreeEdges, CenterNodes, TNode, Tread)

    TreadBottom = []
    TreadRes = []
    for edge in TreadOutEdges: 
        f = 0 
        for ts in TreadSurf: 
            if edge[0] == ts[0] and edge[1] == ts[1]: 
                f = 1 
                break 
        if f == 0 : 
            TreadBottom.append(edge)
        else: 
            TreadRes.append(edge)

    # print ("Tread outer edges %d, %d"%(len(TreadRes), len(TreadBottom)))
    
    ## outedges 
    BodyUp = []
    BodyRes = []
    for edge in BodyOutEdges: 
        f = 0 
        if ts in TreadOutEdges: 
            if (edge[0] == ts[1] and edge[1] == ts[0]) or (edge[0] == ts[0] and edge[1] == ts[1]): 
                f = 1 
                break 
        if f == 1 : 
            BodyUp.append(edge)
        else:
            BodyRes.append(edge)

    # print ("Body outer edges %d, %d (body res edges=%d)"%(len(BodyOutEdges), len(BodyUp), len(BodyRes)))
   

    return TNode, BNode, Tread, Body, TreadSurf, TreadBottom, BodyOutEdges, BodyOutEdges, TreadRes 

def Divide_Tread_Body_PCR_StandardMesh(Elements, Node, TreadSurf, OutEdges):
    
    TEL=["CTB", "CTR", "SUT", "UTR", "TRW"]
    TD_EL=ELEMENT(); BD_EL=ELEMENT()
    for el in Elements.Element: 
        if el[5] == "CTB"  or el[5] == "CTR" or el[5] == "SUT" or el[5] == "UTR" or el[5] == "TRW": TD_EL.Add(el)
        else: BD_EL.Add(el)

    Body_out = BD_EL.OuterEdge(Node)
    Tread_out = TD_EL.OuterEdge(Node) 

    BodyMaster, BodySlave = BD_EL.MasterSlaveEdge(Node)
    TDMaster, TDSlave = TD_EL.MasterSlaveEdge(Node)

    TreadBottom = EDGE()
    for edge in Tread_out.Edge: 
        f = 0 
        for sf in TreadSurf: 
            if (edge[0] == sf[0] and edge[1] == sf[1]) or (edge[0] == sf[1] and edge[1] == sf[0]) : 
                f =1 
                break 
        if f == 0 : 
            TreadBottom.Add(edge)

    Body_top = EDGE()
    for edge in Body_out.Edge: 
        f = 0 
        for sf in TreadBottom.Edge: 
            if edge[0] == sf[0] or edge[1] == sf[1] or edge[0] == sf[1] or edge[1] == sf[0] : 
                f =1 
                break 
        if f == 0 : 
            Body_top.Add(edge)


    TD_node = TD_EL.Nodes(Node)    
    BD_node = BD_EL.Nodes(Node)
    
    return TD_node.Node, BD_node.Node, TD_EL.Element, BD_EL.Element, TreadSurf, TreadBottom.Edge, Body_top.Edge, Body_out.Edge, Tread_out.Edge,  BodyMaster, BodySlave, TDMaster, TDSlave


def Contact_relation_2Elements(e1, e2): 
    # print (" contact relation", e1, e2)
    m1=[]; m2=[]
    for i in range(1, 5):
        if e1[i] ==0 or e1[i]=="": continue 
        for j in range(1, 5): 
            if e2[j] == 0 or e2[j] == "": continue 
            if e1[i] == e2[j] : 
                if i == 1: m1.append([e1[i], 0])
                else: m1.append([e1[i], i])
                m2.append([e2[j], j])

    if len(m1) == 0: 
        return None, 0 
    elif len(m1) ==1: 
        if m1[0][1] == 0: 
            pos = 1
        else: pos = m1[0][1] 
        return 'Point', pos 
    else:
        if int(e1[4]) != 0: 
            if m1[0][1] + m1[1][1] == 2 : face = 1
            if m1[0][1] + m1[1][1] == 5 : face = 2
            if m1[0][1] + m1[1][1] == 7 : face = 3
            if m1[0][1] + m1[1][1] == 4 : face = 4
        else: 
            if m1[0][1] + m1[1][1] == 2 : face = 1
            if m1[0][1] + m1[1][1] == 5 : face = 2
            if m1[0][1] + m1[1][1] == 3 : face = 3
        return 'Edge', face 


def SearchConnectedElement(element, ELEMENT): 
    elem = ELEMENT
    ns = []
    ns.append(element[1])
    ns.append(element[2])
    if element[6] == 3:   ns.append(element[3])
    elif element[6] == 4: 
        ns.append(element[3])
        ns.append(element[4])

    el = []
    for e in elem: 
        cnt = 0 
        for i in range(1, e[6]+1):
            for n in ns: 
                if e[i] == n: cnt += 1
            if cnt == 2 and e[0] != element[0]: 
                el.append(e)
    i = 0
    while i < len(el): 
        j = i+1
        while j < len(el): 
            if el[i][0] == el[j][0]: 
                del(el[j])
                j -= 1
            j += 1
        i += 1 

    return el



def SearchNextSolids(el, face=0, np_solid=[], direction=0):  ## side 0: left/rigth direction, side -1: neg direction +1 : pos direction 
    solids = np_solid
    n1 = el[face]
    face += 1
    if face > int(el[5]): face = 1 
    n2 = el[face]

    idxs1 = np.where(solids[:, 1:5] == n1)[0]
    idxs2 = np.where(solids[:, 1:5] == n2)[0]

    idxs = np.intersect1d(idxs1, idxs2) 
    if len(idxs)>1: 
        if solids[idxs[0]][0] == el[0]: next_solid = solids[idxs[1]]
        else: next_solid = solids[idxs[0]]
        f = 0 
        for i in range(1, int(next_solid[5]) + 1): 
            if i ==1 and (next_solid[i] == n1 or next_solid[i] == n2): f+= 0 
            elif (next_solid[i] == n1 or next_solid[i] == n2): f+= i  

        btm_face = 0 
        if next_solid[5] == 3 and f == 3: btm_face = 1
        if next_solid[5] == 3 and f == 5: btm_face = 2
        if next_solid[5] == 3 and f == 4: btm_face = 3
        if next_solid[5] == 4 and f == 2: btm_face = 1
        if next_solid[5] == 4 and f == 5: btm_face = 2
        if next_solid[5] == 4 and f == 7: btm_face = 3
        if next_solid[5] == 4 and f == 4: btm_face = 4
        if direction == 1: 
            next_face = btm_face - 2 
            if next_face <= 0 : next_face += next_solid[5]
        if direction == -1: 
            next_face = btm_face + 2 
            if next_face >  next_solid[5] : next_face -= next_solid[5]  

        return next_solid, int(next_face)
    else:  
        NOLIST=[]
        return NOLIST, 0


def BodyTopTreadBottomEdge(TreadNode, BodyNode, TreadElement, BodyElement, TreadToRoadSurface, MasterEdges, SlaveEdges, TreadElset):

    BodyEdges = FindEdge(BodyElement)
    BodyFreeEdges = FindFreeEdge(BodyEdges)
    CenterNodes = FindCenterNodes(BodyNode)
    BodyOutEdges = FindOutEdges(BodyFreeEdges, CenterNodes, BodyNode, BodyElement)

    TreadEdges = FindEdge(TreadElement)
    TreadFreeEdges = FindFreeEdge(TreadEdges)
    CenterNodes = FindCenterNodes(TreadNode)
    TreadOutEdges = FindOutEdges(TreadFreeEdges, CenterNodes, TreadNode, TreadElement)

    BodyTop = []
    TreadBottom =[]

    for i in range(len(TreadOutEdges)):
        match = 0
        for j in range(len(TreadToRoadSurface)):
            if (TreadOutEdges[i][0] == TreadToRoadSurface[j][0]) and (TreadOutEdges[i][1] == TreadToRoadSurface[j][1]):
                match =1
        if match == 0:
            TreadBottom.append(TreadOutEdges[i])


    for i in range(len(TreadOutEdges)):
        for j in range(len(BodyOutEdges)):
            if (BodyOutEdges[j][0] == TreadOutEdges[i][0] and BodyOutEdges[j][1] == TreadOutEdges[i][1]) or (BodyOutEdges[j][0] == TreadOutEdges[i][1] and BodyOutEdges[j][1] == TreadOutEdges[i][0]):
                BodyTop.append(BodyOutEdges[j])
                break


    for i in range(len(MasterEdges)):
        Mno =0
        for j in range(len(TreadElset)):
            # print (" i=%d, j=%d  Master edges"%(i, j), MasterEdges[i])
            if MasterEdges[i][2] == TreadElset[j]:
                Mno = MasterEdges[i][5]
                break
        if Mno > 0:
            Sno=[]
            for j in range(len(SlaveEdges)):
                if Mno == SlaveEdges[j][5]:
                    Sno.append(SlaveEdges[j])

            for j in range(len(Sno)):
                for k in range(len(BodyOutEdges)):
                    if (Sno[j][0] == BodyOutEdges[k][0]) and (Sno[j][1] == BodyOutEdges[k][1]):
                        BodyTop.append(BodyOutEdges[k])
                        # print 'Add BODY TOP Surface '
                        break

    for i in range(len(SlaveEdges)):
        Mno = 0
        for j in range(len(TreadElset)):
            # print ("**  i=%d, j=%d  Slave edges"%(i, j), SlaveEdges[i])
            # print ("     tread elset j=%d"%(j), TreadElset[j])
            if SlaveEdges[i][0][2] == TreadElset[j]:
                Mno = SlaveEdges[i][0][5]
                break
        if Mno > 0:
            Sno = []
            for j in range(len(MasterEdges)):
                if Mno == MasterEdges[j][5]:
                    Sno.append(MasterEdges[j])

            for j in range(len(Sno)):
                for k in range(len(BodyOutEdges)):
                    if (Sno[j][0] == BodyOutEdges[k][0]) and (Sno[j][1] == BodyOutEdges[k][1]):
                        m=0
                        match =0
                        while m <len(BodyTop):
                            if BodyTop[m][4] == Sno[j][4]:
                                match = 1
                                break
                            m += 1
                        if match == 0:
                            BodyTop.append(BodyOutEdges[k])
                        break

    return TreadBottom, BodyTop, BodyOutEdges, TreadOutEdges

def TreadTieCheck(MasterEdges, SlaveEdges, TreadBottom, BodyTop):

    M=[]
    S = []
    for i in range(len(MasterEdges)):
        match = 0
        for j in range(len(TreadBottom)):
            if TreadBottom[j][0] == MasterEdges[i][0] and TreadBottom[j][1] == MasterEdges[i][1]:
                match += 1
                break
        for j in range(len(BodyTop)):
            if BodyTop[j][0] == MasterEdges[i][0] and BodyTop[j][1] == MasterEdges[i][1]:
                match += 1
                if MasterEdges[i][2] == 'BSW':
                    match += -1
                break
        if match == 0:
            M.append(MasterEdges[i])

    for i in range(len(SlaveEdges)):
        match = 0
        for j in range(len(TreadBottom)):
            if TreadBottom[j][0] == SlaveEdges[i][0] and TreadBottom[j][1] == SlaveEdges[i][1]:
                match += 1 
                break
        for j in range(len(BodyTop)):
            if BodyTop[j][0] == SlaveEdges[i][0] and BodyTop[j][1] == SlaveEdges[i][1]:
                match += 1
                break
        if match == 0:
            S.append(SlaveEdges[i])

    return M, S

def Write2DFile(fileFullName, Node, AllElements, Elset, TreadToRoad, Press, RimContact, MasterEdges, SlaveEdges, Offset, CenterNodes, Comments, fullpath=0):
    ####################################################################################################
    ## Changed Scripts for DOE
    ####################################################################################################
    if fullpath == 0:
        FileName = os.path.basename(fileFullName)
    else:
        FileName = fileFullName
    ####################################################################################################
    
    FileName = FileName + '.msh'
    f = open(FileName, 'w')

    fline = []
    for i in range(len(Comments)):
        fline.append([Comments[i]])
    fline.append(['*NODE, SYSTEM=R, NSET=ALLNODES\n'])

    i = 0
    while i < len(Node):
        fline.append(['%10d, %15.6E, %15.6E, %15.6E\n' % (Node[i][0], Node[i][3], Node[i][2], Node[i][1])])
        i += 1
    i = 0
    fline.append(['*ELEMENT, TYPE=MGAX1, ELSET=ALLELSET\n'])
    while i < len(AllElements):
        if AllElements[i][6] == 2:
            fline.append(['%10d, %10d, %10d\n' % (AllElements[i][0], AllElements[i][1], AllElements[i][2])])
        i += 1
    i = 0
    fline.append(['*ELEMENT, TYPE=CGAX3H, ELSET=ALLELSET\n'])
    while i < len(AllElements):
        if AllElements[i][6] == 3:
            fline.append(['%10d, %10d, %10d, %10d\n' % (AllElements[i][0], AllElements[i][1], AllElements[i][2], AllElements[i][3])])
        i += 1
    i = 0
    fline.append(['*ELEMENT, TYPE=CGAX4H, ELSET=ALLELSET\n'])
    while i < len(AllElements):
        if AllElements[i][6] == 4:
            fline.append(['%10d, %10d, %10d, %10d, %10d\n' % (AllElements[i][0], AllElements[i][1], AllElements[i][2], AllElements[i][3], AllElements[i][4])])
        i += 1
    isCH1=0
    isCH2=0
    isBDr=0
    isBDl=0
    for i in range(len(Elset)):
        fline.append(["*ELSET, ELSET=%s\n" %(Elset[i][0])])
        if 'CH1' in Elset[i][0]:
            isCH1=1
        if 'CH2' in Elset[i][0]:
            isCH2=1
        if 'BEAD_R' in Elset[i][0]:
            isBDr =1
        if 'BEAD_L' in Elset[i][0]:
            isBDl =1


        k = 0
        for j in range(1, len(Elset[i])):
            if ((k + 1) % 10 != 0):
                if (k +2) == len(Elset[i]):
                    fline.append(['%8d,\n' % (Elset[i][j])])
                else:
                    fline.append(['%8d,' % (Elset[i][j])])
            else:
                fline.append(['%8d,\n' % (Elset[i][j])])
            k += 1
    if isCH1 == 1:
        fline.append(['*ELSET,  ELSET=CH1\n'])
        fline.append([' CH1_R, CH1_L\n'])
    if isCH2 == 1:
        fline.append(['*ELSET,  ELSET=CH2\n'])
        fline.append([' CH2_R, CH2_L\n'])

    i = 0
    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=CONT\n'])
    while i < len(TreadToRoad):
        fline.append(['%6d, %s\n' % (TreadToRoad[i][4], TreadToRoad[i][3])])
        i += 1

    i = 0
    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=PRESS\n'])
    while i < len(Press):
        fline.append(['%6d, %s\n' % (Press[i][4], Press[i][3])])
        i += 1

    i = 0
    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=RIC_R\n'])
    i=0
    while i < len(RimContact):
        for nd in Node:
            if RimContact[i][0] == nd[0]: 
                if nd[2]<0: 
                    fline.append(['%6d, %s\n' % (RimContact[i][4], RimContact[i][3])])
                    break
        i += 1

    i = 0
    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=RIC_L\n'])
    while i < len(RimContact):
        for nd in Node:
            if RimContact[i][0] == nd[0]: 
                if nd[2]>0: 
                    fline.append(['%6d, %s\n' % (RimContact[i][4], RimContact[i][3])])
                    break
        i += 1

    ###########################################################
    # sorted(MasterEdges, key=lambda element: element[4])
    # i = 0;
    # while i < len(MasterEdges):
    #     fline.append(['*SURFACE, TYPE=ELEMENT, NAME=Tie_m' + str(i + 1) + '\n'])
    #     fline.append(['%6d, %s\n' % (MasterEdges[i][4], MasterEdges[i][3])])
    #     fline.append(['*SURFACE, TYPE=ELEMENT, NAME=Tie_s' + str(i + 1) + '\n'])
    #     j = 0
    #     while j < len(SlaveEdges):
    #         if SlaveEdges[j][5] == MasterEdges[i][5]:
    #             fline.append(['%6d, %s\n' % (SlaveEdges[j][4], SlaveEdges[j][3])])
    #         j += 1
    #     i += 1

    # i = 0
    # while i < len(MasterEdges):
    #     fline.append(['*TIE, NAME=TIE_' + str(i + 1) + '\n'])
    #     fline.append(['Tie_s' + str(i + 1) + ', ' + 'Tie_m' + str(i + 1) + '\n'])
    #     i += 1

    # print (len(MasterEdges), len(SlaveEdges))

    cnt = 0 
    for mst in MasterEdges: 
        cnt += 1
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=Tie_m' + str(cnt) + '\n'])
        fline.append(['%6d, %s\n' % (mst[4], mst[3])])
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=Tie_s' + str(cnt) + '\n'])

        for slt in SlaveEdges[cnt-1]: 
            fline.append(['%6d, %s\n' % (slt[4], slt[3])])
        
        fline.append(['*TIE, NAME=TIE_' + str(cnt) + '\n'])
        fline.append(['Tie_s' + str(cnt) + ', ' + 'Tie_m' + str(cnt) + '\n'])
        





    ###########################################################


    if isBDr ==1 and isBDl ==1:
        fline.append(['*ELSET, ELSET=BD1\n BEAD_R, BEAD_L\n'])
    elif isBDr == 1 :
        fline.append(['*ELSET, ELSET=BD1\n BEAD_R\n'])
    elif isBDl ==1:
        fline.append(['*ELSET, ELSET=BD1\n BEAD_L\n'])

    Bdr = [0, 0]
    for i in range(len(AllElements)):
        if AllElements[i][5] == 'BEAD_L':
            Bdr[0] = AllElements[i][1]
        if AllElements[i][5] == 'BEAD_R':
            Bdr[1] = AllElements[i][1]

    if Bdr[0] != 0:
        fline.append(['\n*NSET, NSET=BD_L\n'])
        fline.append([str(Bdr[0])])
    if Bdr[1] != 0:
        fline.append(['\n*NSET, NSET=BD_R\n'])
        fline.append([str(Bdr[1])])


    if Bdr[0] != 0 and Bdr[1] != 0:
        fline.append(['\n*NSET, NSET=BDR\n BD_R, BD_L\n'])
    elif Bdr[1] != 0:
        fline.append(['\n*NSET, NSET=BDR\n BD_R\n'])
    elif Bdr[0] != 0 :
        fline.append(['\n*NSET, NSET=BDR\n BD_L\n'])
    else:
        pass

    fline.append(['*NSET, NSET=CENTER\n'])

    i = 0
    while i < len(CenterNodes):
        if ((i + 1) % 10 == 0):
            fline.append(['%8d\n' % (CenterNodes[i])])
        else:
            fline.append(['%8d,' % (CenterNodes[i])])
        i += 1

    f.writelines('%s' % str(item[0]) for item in fline)

    f.close()


def Color(elsetname):
    c = ''
    if elsetname == 'CTR' or elsetname == 'CTB':
        c = 'darkgray'
    elif elsetname == 'UTR' or elsetname == 'SUT':
        c = 'lightpink'
    elif elsetname == 'CC1' or elsetname == 'C01' or elsetname == 'C02':
        c = 'lightsalmon'
    elif elsetname == 'CCT':
        c = 'purple'
    elif elsetname == 'BTT':
        c = 'steelblue'
    elif elsetname == 'FIL' or elsetname == 'LBF':
        c = 'green'
    elif elsetname == 'UBF':
        c = 'lightpink'
    elif elsetname == 'IL1' or elsetname == 'L11':
        c = 'y'
    elif elsetname == 'BSW':
        c = 'yellowgreen'
    elif elsetname == 'HUS':
        c = 'steelblue'
    elif elsetname == 'RIC':
        c = 'darkgray'
    elif elsetname == 'SHW':
        c = 'darkcyan'
    elif elsetname == 'BD1':
        c = 'dimgray'
    elif elsetname == 'BDC':
        c = 'black'
    elif elsetname == 'MEMB':
        c = 'black'
    elif elsetname == 'DOT':
        c = 'red'
    elif elsetname == 'PRESS':
        c = 'blue'
    elif elsetname == 'RIM':
        c = 'red'
    elif elsetname == 'TDBASE':
        c = 'aqua'
    elif elsetname == 'TDROAD':
        c = 'coral'
    elif elsetname == 'BDTOP':
        c = 'gray'
    else:
        c = 'silver'
    return c

def plot_geometry(imagefile, viewNode, viewElement, AllElements, Node, Elset, MasterEdges=[], SlaveEdges=[], Press=[], RimContact=[], TreadToRoad=[], TreadBaseEdges=[], BodyToTreadEdges=[], TreadNode=[]):
    #    print ('*******************************************************')
    #    print (' View Option (Default - Node No : off, Element No.: Off)')
    #    print ('  - Node Number veiw : node/n=on')
    #    print ('  - Element Number view : element/eL/e=on')
    #    print ('    ex) python ...py n=on e=on')
    #    print ('*******************************************************')

    textsize = 10
    cdepth = 0.8

    NodeSize =0.1
    viewMembrane =1
    viewTDNode = 0

    MeshLineWidth = 0.1
    MembWidth = 0.3
    
    if len(Press) > 0 and len(RimContact) > 0 : 
        viewSurface =1
    else:
        viewSurface =0
    
    if len(MasterEdges) > 0:
        viewTie = 1
    else:
        viewTie = 0


    fig, ax=plt.subplots()
    ax.axis('equal')
    ax.axis('off')

    i = 0
    c = 0
    
    while i < len(AllElements):
        if AllElements[i][6] == 3:
            hatch = 0
            x1 = find_z(AllElements[i][1], Node) * -1
            x2 = find_z(AllElements[i][2], Node) * -1
            x3 = find_z(AllElements[i][3], Node) * -1
            y1 = find_r(AllElements[i][1], Node)
            y2 = find_r(AllElements[i][2], Node)
            y3 = find_r(AllElements[i][3], Node)
            
            j = 0
            # color = 'b'

            icolor = Color(AllElements[i][5])

            for m in range(len(Elset)):
                if Elset[m][0] == 'BETWEEN_BELTS':
                    break
            for k in range(len(Elset[m])):
                if Elset[m][k] == AllElements[i][0]:
                    hatch = 1;
                    c += 1
                    break
            if hatch == 1:
                if c == 1:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth*2, hatch='//', label='BETWEEN BELTS')
                else:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth*2, hatch='//')
            else:
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
            ax.add_patch(polygon)

            if viewElement == 1:
                plt.text((x1 + x2 + x3) / 3, (y1 + y2 + y3) / 3, AllElements[i][0], color='blue', size=textsize)
                
        if AllElements[i][6] == 4:
            hatch = 0
            x1 = find_z(AllElements[i][1], Node) * -1;            x2 = find_z(AllElements[i][2], Node) * -1;            x3 = find_z(AllElements[i][3], Node) * -1;            x4 = find_z(AllElements[i][4], Node) * -1
            y1 = find_r(AllElements[i][1], Node);             y2 = find_r(AllElements[i][2], Node);             y3 = find_r(AllElements[i][3], Node);             y4 = find_r(AllElements[i][4], Node)
            j = 0;
            # color = 'b'
            icolor = Color(AllElements[i][5])
            for m in range(len(Elset)):
                if Elset[m][0] == 'BETWEEN_BELTS':
                    break
            for k in range(len(Elset[m])):
                if Elset[m][k] == AllElements[i][0]:
                    hatch = 1;
                    c += 1
                    break
            if hatch == 1:
                if c == 1:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth, hatch='//', label='BETWEEN BELTS')
                else:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth, hatch='//')
            else:
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
            ax.add_patch(polygon)

            if viewElement == 1:
                plt.text((x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4, AllElements[i][0], color='blue', size=textsize)
        
        i += 1

    PressWidth = 0.5
    RimWidth = 0.5
    TDBaseWidth = 0.4
    TieWidth = 0.8
    BDTopWidth = TDBaseWidth * 0.5
    TreadRoadWidth = 0.3

    if viewSurface == 1:
        i = 0
        while i < len(Press):
            x1 = find_z(Press[i][0], Node) * -1;            x2 = find_z(Press[i][1], Node) * -1;
            y1 = find_r(Press[i][0], Node);            y2 = find_r(Press[i][1], Node);
            color = Color('PRESS')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=PressWidth, label='Pressure')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=PressWidth)
            i += 1

        i = 0
        while i < len(RimContact):
            x1 = find_z(RimContact[i][0], Node) * -1;            x2 = find_z(RimContact[i][1], Node) * -1;
            y1 = find_r(RimContact[i][0], Node);            y2 = find_r(RimContact[i][1], Node);
            color = Color('RIM')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=RimWidth, label='Rim Contact', linestyle=':')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=RimWidth, linestyle=':' )
            i += 1
    
    if viewTie == 1: 
        j = 0
        iColor = ['midnightblue', 'magenta', 'violet', 'brown', 'aqua', 'coral', 'chocolate',
                  'orange', 'steelblue', 'teal', 'dimgray']

        i = 0
        while i < len(MasterEdges):
            x1 = find_z(MasterEdges[i][0], Node) * -1;            x2 = find_z(MasterEdges[i][1], Node) * -1
            y1 = find_r(MasterEdges[i][0], Node);            y2 = find_r(MasterEdges[i][1], Node)
            if (i + 1) % len(iColor) == 0 or (i + 1) % len(MasterEdges) == 0:
                j = 0
            else:
                j += 1
            if i == 0:
                plt.plot([x1, x2], [y1, y2], iColor[j], linestyle='-', linewidth=TieWidth, label='Tie Master, White line - Slave')
            else:
                plt.plot([x1, x2], [y1, y2], iColor[j], linestyle='-', linewidth=TieWidth)
            i += 1

        i = 0
        while i < len(SlaveEdges):
            x1 = find_z(SlaveEdges[i][0], Node) * -1;            x2 = find_z(SlaveEdges[i][1], Node) * -1
            y1 = find_r(SlaveEdges[i][0], Node);            y2 = find_r(SlaveEdges[i][1], Node)
            plt.plot([x1, x2], [y1, y2], 'white', linewidth=TieWidth*0.5)
            i += 1
    
    if len(TreadBaseEdges) > 0: 
        i = 0
        while i < len(TreadBaseEdges):
            x1 = find_z(TreadBaseEdges[i][0], Node) * -1;            x2 = find_z(TreadBaseEdges[i][1], Node) * -1
            y1 = find_r(TreadBaseEdges[i][0], Node);            y2 = find_r(TreadBaseEdges[i][1], Node)
            color = Color('TDBASE')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, linewidth=TDBaseWidth, linestyle='-', label='Tread Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, linewidth=TDBaseWidth, linestyle='-')
            i += 1
    if len(TreadToRoad)> 0:
        i = 0
        while i < len(TreadToRoad):
            x1 = find_z(TreadToRoad[i][0], Node) * -1;            x2 = find_z(TreadToRoad[i][1], Node) * -1;
            y1 = find_r(TreadToRoad[i][0], Node);            y2 = find_r(TreadToRoad[i][1], Node);
            color = Color('TDROAD')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=TreadRoadWidth, linestyle=':', label='Road Contact Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=TreadRoadWidth, linestyle=':')
            i += 1
    
    if len(BodyToTreadEdges) > 0 :
        i = 0
        while i < len(BodyToTreadEdges):
            x1 = find_z(BodyToTreadEdges[i][0], Node) * -1;        x2 = find_z(BodyToTreadEdges[i][1], Node) * -1
            y1 = find_r(BodyToTreadEdges[i][0], Node);             y2 = find_r(BodyToTreadEdges[i][1], Node);
            color = Color('BDTOP')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=BDTopWidth, linestyle=':', label='Body Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=BDTopWidth, linestyle=':')
            i += 1

    i = 0
    while i < len(AllElements):
        if AllElements[i][6] == 2:
            x1 = find_z(AllElements[i][1], Node) * -1;            x2 = find_z(AllElements[i][2], Node) * -1
            y1 = find_r(AllElements[i][1], Node);            y2 = find_r(AllElements[i][2], Node)
            
            color = Color("MEMB")
            if viewMembrane == 1:
                plt.plot([x1, x2], [y1, y2], color, lw=MembWidth)
                if viewElement == 1:
                    plt.text((x1 + x2) / 2, (y1 + y2) / 2, AllElements[i][0], color=color, size=textsize)
        i += 1

    # View Nodes In Tread 
    x = []
    y = []  # NodeX
    i = 0
    if viewTDNode == 1:
        while i < len(TreadNode):
            x.append(TreadNode[i][2] * -1)
            y.append(TreadNode[i][3])
            i += 1
        color = Color("DOT")
        plt.scatter(x, y, color=color, s=NodeSize, marker='o', label='Tread Nodes')

    # View All Nodes 
    x = [];    y = []  # NodeX
    i = 0
    while i < len(Node):
        x.append(Node[i][2] * -1)
        y.append(Node[i][3])
        i += 1

    if viewNode == 1:
        Num = len(Node)
        ax.scatter(x, y)
        i = 0
        for i, txt in enumerate(Num):
            ax.annotate(txt, (x[i], y[i]), size=textsize)

    allx=[]
    ally=[]
    for nd in Node: 
        allx.append(nd[2])
        ally.append(nd[3])

    min_x=min(allx); max_x=max(allx)
    min_y=min(ally); max_y=max(ally)
    ax.set_xlim([min_x, max_x])
    ax.set_ylim([min_y, max_y])
    # plt.scatter(allx, ally, color='red', s=NodeSize, marker='o')
    plt.savefig(imagefile, dpi=500)
    print ('* The 2D Mesh Image is created successfully!')



def Write3DBodyMeshWithC(Mesh3DBody, BodyNode, BodyElement, MasterEdges, SlaveEdges, PressureSurface, RimContactSurface, BodyOut, OffsetSector, OffsetLeftRight, Elset, TreadElset, SectorOption, Div):
    Mesh3DBody = Mesh3DBody[:-4]
    if SectorOption == 1:
        MaxR =0
        for i in range(len(BodyNode)):
            if BodyNode[i][3] > MaxR:
                MaxR = BodyNode[i][3]
        cir = math.pi*2*MaxR
        sectors =int(cir/Div)
        iAngle = (math.pi*2) / float(sectors)
        print ('* Body Sectors  : %d (Element Length=%5.2fmm, Initial Body MAX Dia.= %6.1fmm), Each Sector Angle=%6.4f deg' %(sectors, Div*1000, MaxR*2000, iAngle*180/math.pi))
    else:
        sectors = int(Div)
        # iAngle = (math.pi*2) / float(sectors)
        print ("* Body Sectors : %d,  Each Sector Angle : %6.4f deg" %(sectors, 360/float(sectors)))

    tupleNode =()
    for i in range(len(BodyNode)):
        tupleNode = tupleNode + tuple(BodyNode[i])
    Nset = len(BodyNode[0])
    tupleElement = ()
    for i in range(len(BodyElement)):
        tList=[]
        for k in range(len(BodyElement[i])):
            if BodyElement[i][k] == '':
                tList.append(0)
            elif k == 5 or k > 6:
                tList.append(0)
            else:
                tList.append(BodyElement[i][k])
        # print tList
        tupleElement = tupleElement + tuple(tList)
    Eset = len(BodyElement[0])
    _islm.CreateTireBody(Mesh3DBody, tupleNode, Nset, tupleElement, Eset, 5000, 5000, OffsetSector, sectors)

    i =0
    while i < len(Elset):
    # for i in range(len(Elset)):
        match = 0
        # print TreadElset, Elset[i][0]
        N = len(TreadElset)
        # for j in range(N):
        j=0
        while j < N:
            if Elset[i][0] == TreadElset[j]:
                match =1
                break
            j += 1
        if match == 0:
            list=[]
            k=1
            while k < len(Elset[i]):
            # for k in range(1, len(Elset[i])):
                list.append(Elset[i][k])
                k += 1
            ElsetName = Elset[i][0]
            tupleList = tuple(list)

            _islm.Write3DElset(sectors, OffsetSector, ElsetName, tupleList, Mesh3DBody+'.axi')
        i += 1

    
    fline = []
    fulltext=''
    #######################################################################################
    ## BD1 : ELSET 
    #######################################################################################
    fline.append(["*ELSET, ELSET=BD1\n"])
    fulltext+= "*ELSET, ELSET=BD1\n"
    i = 0
    while i < len(Elset):
    # for i in range(len(Elset)):
        if "BEAD" in Elset[i][0]:
            k = 0
            while k < sectors:
            # for k in range(sectors):
                count = 0
                m = 1
                while m < len(Elset[i]):
                # for m in range(1, len(Elset[i])):
                    newEL = Elset[i][m] + k * OffsetSector
                    count += 1
                    if count % 16 == 0 or count == len(Elset[i])-1:
                        fline.append(["%d,\n" % (newEL)])
                        fulltext += str(newEL)+",\n"
                    else:
                        fline.append(["%d, " % (newEL)])
                        fulltext += str(newEL)+", "
                    m += 1
                k+=1
        i += 1
    ############################################################################################
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=TIREBODY\n"])
    fulltext += "*SURFACE, TYPE=ELEMENT, NAME=TIREBODY\n"
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(BodyOut):
            # for j in range(len(BodyOut)):
            newEL = BodyOut[j][4] + i * OffsetSector
            face = Change3DFace(BodyOut[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += str(newEL)+", " + str(face) + "\n"
            j += 1
        i += 1
    

    RicR = []
    RicL = []
    for ric in RimContactSurface:
        for nd in BodyNode:
            if nd[0] == ric[1] and nd[2] < 0: 
                RicR.append(ric)
                break
    for ric in RimContactSurface:
        for nd in BodyNode:        
            if nd[0] == ric[1] and nd[2] > 0: 
                RicL.append(ric)
                break
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=RIC_R\n"])
    fulltext += "*SURFACE, TYPE=ELEMENT, NAME=RIC_R\n"
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(RicR):
            newEL = RicR[j][4] + i * OffsetSector
            face = Change3DFace(RicR[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += str(newEL)+", " + str(face) + "\n"
            j += 1
        i += 1
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=RIC_L\n"])
    fulltext += "*SURFACE, TYPE=ELEMENT, NAME=RIC_L\n"
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(RicL):
            newEL = RicL[j][4] + i * OffsetSector
            face = Change3DFace(RicL[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += str(newEL)+", " + str(face) + "\n"
            j += 1
        i += 1
    ############################################################################################
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=PRESS\n"])
    fulltext += "*SURFACE, TYPE=ELEMENT, NAME=PRESS\n"
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(PressureSurface):
            # for j in range(len(PressureSurface)):
            newEL = PressureSurface[j][4] + i * OffsetSector
            face = Change3DFace(PressureSurface[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += str(newEL)+", " + str(face) + "\n"
            j += 1
        i += 1

    for i, edge in enumerate(MasterEdges): 
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (i+1)])
        fulltext += '*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (i+1)
        # print ("********* ", edge, SlaveEdges[i])
        for k in range(sectors): 
            newEL = edge[4] + k * OffsetSector
            face = Change3DFace(edge[3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += '%10d, %s\n' % (newEL, face)
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (i+1)])
        fulltext += '*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (i+1)
        for k in range(sectors):
            for edges in  SlaveEdges[i]: 
                newEL = edges[4] + k * OffsetSector
                face = Change3DFace(edges[3])
                fline.append(['%10d, %s\n' % (newEL, face)])
                fulltext += '%10d, %s\n' % (newEL, face)
        fline.append(['*TIE, NAME=T%d_TIE\n' % (i+1)])
        fulltext += '*TIE, NAME=T%d_TIE\n' % (i+1)
        fline.append(['S%d_TIE, M%d_TIE\n'%(i+1, i+1)])
        fulltext += 'S%d_TIE, M%d_TIE\n'%(i+1, i+1)

    
    f = open(Mesh3DBody+'.axi', "a")
    f.writelines(fulltext)
    f.close()

def Write3DTreadMeshWithC(Mesh3DTread, TreadNode, TreadElement, MasterEdges, SlaveEdges, TreadToRoadSurface, TreadBottom, TreadNumber, OffsetSector, Elset, TreadElset, SectorOption, Div):
    if SectorOption == 1:
        MaxR =0
        for i in range(len(TreadNode)):
            if TreadNode[i][3] > MaxR:
                MaxR = TreadNode[i][3]
        cir = math.pi*2*MaxR
        sectors =int(cir/Div)
        iAngle = (math.pi*2) / float(sectors)
        print ('* Tread Sectors : %d (Element Length=%5.2fmm, Initial Tire OD = %6.1fmm), Each Sector Angle=%6.4f deg' %(sectors, Div*1000, MaxR*2000, iAngle*180/math.pi))
    else:
        sectors = int(Div)
        iAngle = (math.pi*2) / float(sectors)
        print ("* Tread Sectors : %d, Each Sector Angle : %6.4f deg" %(sectors, 360/float(sectors)))

    Mesh3DTread = Mesh3DTread[:-4]



    tupleNode = ()
    i = 0
    while i < len(TreadNode):
        tupleNode = tupleNode + tuple(TreadNode[i])
        i += 1

    tupleElement = ()
    for i in range(len(TreadElement)):
        tList=[]
        for k in range(len(TreadElement[i])):
            if TreadElement[i][k] == '':
                tList.append(0)
            elif k == 5:
                tList.append(1)
            elif k > 6:
                tList.append(0)
            else:
                tList.append(TreadElement[i][k])
        # print tList
        tupleElement = tupleElement + tuple(tList)
    # print TreadElement[0]
    # print tupleElement[0], tupleElement[1],tupleElement[2], tupleElement[3], tupleElement[4], tupleElement[5], tupleElement[6], tupleElement[7], tupleElement[8], tupleElement[9]
    # print sectors, OffsetSector, TreadNumber, len(TreadNode[0]), len(TreadElement[0]), len(TreadElement)

    _islm.CreateTireTread(Mesh3DTread, tupleNode, len(TreadNode[0]), tupleElement, len(TreadElement[0]), OffsetSector, TreadNumber, sectors)

    f = open(Mesh3DTread + '.trd', "a")
    fline =""
    i = 0
    while i < len(Elset):
        match = 0
        N = len(TreadElset)
        j = 0
        while j < N:
            if Elset[i][0] == TreadElset[j]:
                match = 1
                break
            j += 1
        if match == 1:
            ElsetName = Elset[i][0]
            line = "*ELSET, ELSET=" + ElsetName + "\n"
            for m in range(sectors): 
                dline = ""
                for k, no in enumerate(Elset[i]): 
                    if k == 0: continue     ## %9d 

                    if k == len(Elset[i]) - 1:                   word = "%9d,\n"%(no+TreadNumber + m * OffsetSector) 
                    elif k % 15 !=0 and k < len(Elset[i]) -1:    word = "%9d,"%(no+TreadNumber + m * OffsetSector) 
                    else:                                        word = "%9d,\n"%(no+TreadNumber + m * OffsetSector) 

                    dline += word 
                line += dline 
            fline += line 
        i += 1
    f.write(fline)
    f.close()

    ############################################################################################
    f = open(Mesh3DTread + '.trd', "a")
    fline = []


    for i, edge in enumerate(MasterEdges): 
        # print ("Master len(%d)"%(len(MasterEdges)), edge)
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (i+100)])
        for k in range(sectors): 
            newEL = edge[4] + k * OffsetSector + TreadNumber
            face = Change3DFace(edge[3])
            fline.append(['%10d, %s\n' % (newEL, face)])
        fline.append(['*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (i+100)])
        
        for k in range(sectors):
            for ed in  SlaveEdges[i]: 
                newEL = ed[4] + k * OffsetSector + TreadNumber
                face = Change3DFace(ed[3])
                fline.append(['%10d, %s\n' % (newEL, face)])
        fline.append(['*TIE, NAME=T%d_TIE\n' % (i+100)])
        fline.append([' S%d_TIE, M%d_TIE\n'%(i+100, i+100)])



    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=XTRD1001\n'])
    i=0
    while i < sectors:
    # for i in range(sectors):
        j=0
        while j < len(TreadToRoadSurface):
        # for j in range(len(TreadRoad)):
            newEL = TreadToRoadSurface[j][4] + i * OffsetSector + TreadNumber
            face = Change3DFace(TreadToRoadSurface[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            j+=1
        i+=1

    fline.append(['*SURFACE, TYPE=ELEMENT, NAME=YTIE1001\n'])
    i=0
    while i < sectors:
    # for i in range(sectors):
        j=0
        while j < len(TreadBottom):
        # for j in range(len(TreadOut)):
            newEL = TreadBottom[j][4] + i * OffsetSector + TreadNumber
            face = Change3DFace(TreadBottom[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            j+=1
        i+=1

    fline.append(['*TIE, NAME=TBD2TRD, ADJUST=YES, POSITION TOLERANCE= 0.0001\n'])
    fline.append([' YTIE1001, TIREBODY\n'])
    # f.writelines('%s' % str(item[0]) for item in fline)
    i = 0
    while i < len(fline):
        f.writelines('%s' % str(fline[i][0]))
        i += 1
    f.close()

def Write3DTreadMeshWithC_TBR(Mesh3DTread, TreadNode, TreadElement, MasterEdges, SlaveEdges, TreadToRoadSurface, TreadBottom, TreadNumber, OffsetSector, Elset, TreadElset, SectorOption, Div):
    if SectorOption == 1:
        MaxR =0
        for i in range(len(TreadNode)):
            if TreadNode[i][3] > MaxR:
                MaxR = TreadNode[i][3]
        cir = math.pi*2*MaxR
        sectors =int(cir/Div)
        iAngle = (math.pi*2) / float(sectors)
        print ('* Tread Sectors : %d (Element Length=%5.2fmm, Initial Tire OD = %6.1fmm), Each Sector Angle=%6.4f deg' %(sectors, Div*1000, MaxR*2000, iAngle*180/math.pi))
    else:
        sectors = int(Div)
        iAngle = (math.pi*2) / float(sectors)
        print ("* Tread Sectors : %d, Each Sector Angle : %6.4f deg" %(sectors, 360/float(sectors)))

    Mesh3DTread = Mesh3DTread[:-4]



    tupleNode = ()
    i = 0
    while i < len(TreadNode):
        tupleNode = tupleNode + tuple(TreadNode[i])
        i += 1

    tupleElement = ()
    TreadSet=ELSET()
    for i in range(len(TreadElement)):
        tList=[]
        for k in range(len(TreadElement[i])):
            if TreadElement[i][k] == '':
                tList.append(0)
            elif k == 5:
                tList.append(1)
            elif k > 6:
                tList.append(0)
            else:
                tList.append(TreadElement[i][k])
        # print tList
        tupleElement = tupleElement + tuple(tList)
        TreadSet.Add(TreadElement[i][0], TreadElement[i][5])        
    # print TreadElement[0]
    # print tupleElement[0], tupleElement[1],tupleElement[2], tupleElement[3], tupleElement[4], tupleElement[5], tupleElement[6], tupleElement[7], tupleElement[8], tupleElement[9]
    # print sectors, OffsetSector, TreadNumber, len(TreadNode[0]), len(TreadElement[0]), len(TreadElement)

    _islm.CreateTireTread(Mesh3DTread, tupleNode, len(TreadNode[0]), tupleElement, len(TreadElement[0]), OffsetSector, TreadNumber, sectors)

    
    fline =""
    i = 0
    while i < len(TreadSet.Elset):
        ElsetName = TreadSet.Elset[i][0]
        # if "CTB" == ElsetName.upper() : ElsetName += "1"
        # elif "SUT" == ElsetName.upper() : ElsetName += "1"
        # elif "UTR" == ElsetName.upper() : ElsetName += "1"
        # elif "CTR" == ElsetName.upper() : ElsetName += "1"
        # elif "TRW" == ElsetName.upper() : ElsetName += "1"

        line = "*ELSET, ELSET=" + ElsetName + "\n"
        for m in range(sectors): 
            dline = ""
            for k, no in enumerate(TreadSet.Elset[i]): 
                if k == 0: continue     ## %9d 

                if k == len(TreadSet.Elset[i]) - 1:          word = "%9d,\n"%(no+TreadNumber + m * OffsetSector) 
                elif k % 15 == 0:                            word = "%9d,\n"%(no+TreadNumber + m * OffsetSector)  
                else:                                        word = "%9d,"%(no+TreadNumber + m * OffsetSector) 

                dline += word 
            line += dline 
        fline += line 
        i += 1

    f = open(Mesh3DTread + '.trd', "a")
    f.write(fline)
    f.close()
    
    ############################################################################################
    
    fline ="" 
    for i, me in enumerate(MasterEdges): ## edge=[N1, N2, "name", face, el No]
        f = 0 
        for te in TreadElement: 
            if me[4] == te[0]: 
                f=1
                break 
        if f == 1: 
            fline += '*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (i+1)
            # fline.append(['*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (i+1)])
            for k in range(sectors): 
                newel = me[4] + k  * OffsetSector + TreadNumber
                face = Change3DFace(me[3])
                # fline.append(['%10d, %s\n' % (newel, face)])
                fline += '%10d, %s\n' % (newel, face)

            # fline.append(['*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (i+1)])
            fline += '*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (i+1)
            for se in SlaveEdges[i]: 
                for k in range(sectors): 
                    newel = se[4] + k  * OffsetSector + TreadNumber
                    face = Change3DFace(se[3])
                    # fline.append(['%10d, %s\n' % (newel, face)])
                    fline += '%10d, %s\n' % (newel, face)

            # fline.append(['*TIE, NAME=T%d_TIE\n' % (i+1)])
            # fline.append(['S%d_TIE, M%d_TIE\n' % (i+1, i+1)])

            fline += '*TIE, NAME=T%d_TIE\n' % (i+1)
            fline +=  ' S%d_TIE, M%d_TIE\n' % (i+1, i+1)


    ############################################################################################

    # fline.append(['*SURFACE, TYPE=ELEMENT, NAME=XTRD1001\n'])
    fline += '*SURFACE, TYPE=ELEMENT, NAME=XTRD1001\n'
    i=0
    while i < sectors:
    # for i in range(sectors):
        j=0
        while j < len(TreadToRoadSurface):
        # for j in range(len(TreadRoad)):
            newEL = TreadToRoadSurface[j][4] + i * OffsetSector + TreadNumber
            face = Change3DFace(TreadToRoadSurface[j][3])
            # fline.append(['%10d, %s\n' % (newEL, face)])
            fline += '%10d, %s\n' % (newEL, face)
            j+=1
        i+=1

    # fline.append(['*SURFACE, TYPE=ELEMENT, NAME=YTIE1001\n'])
    fline += '*SURFACE, TYPE=ELEMENT, NAME=YTIE1001\n'
    i=0
    while i < sectors:
    # for i in range(sectors):
        j=0
        while j < len(TreadBottom):
        # for j in range(len(TreadOut)):
            newEL = TreadBottom[j][4] + i * OffsetSector + TreadNumber
            face = Change3DFace(TreadBottom[j][3])
            # fline.append(['%10d, %s\n' % (newEL, face)])
            fline += '%10d, %s\n' % (newEL, face)
            j+=1
        i+=1

    # fline.append(['*TIE, NAME=TBD2TRD, ADJUST=YES, POSITION TOLERANCE= 0.0001\n'])
    # fline.append([' YTIE1001, TIREBODY\n'])
    fline += '*TIE, NAME=TBD2TRD, ADJUST=YES, POSITION TOLERANCE= 0.0001\n'
    fline += ' YTIE1001, TIREBODY\n'
    f = open(Mesh3DTread + '.trd', "a")
    f.write(fline)
    f.close()
def Write3DBodyMeshWithC_TBR(Mesh3DBody, BodyNode, BodyElement, MasterEdges, SlaveEdges, PressureSurface, RimContactSurface, BodyOut, OffsetSector, OffsetLeftRight, Elset, TreadElset, SectorOption, Div):
    Mesh3DBody = Mesh3DBody[:-4]
    if SectorOption == 1:
        MaxR =0
        for i in range(len(BodyNode)):
            if BodyNode[i][3] > MaxR:
                MaxR = BodyNode[i][3]
        cir = math.pi*2*MaxR
        sectors =int(cir/Div)
        iAngle = (math.pi*2) / float(sectors)
        print ('* Body Sectors  : %d (Element Length=%5.2fmm, Initial Body MAX Dia.= %6.1fmm), Each Sector Angle=%6.4f deg' %(sectors, Div*1000, MaxR*2000, iAngle*180/math.pi))
    else:
        sectors = int(Div)
        # iAngle = (math.pi*2) / float(sectors)
        print ("* Body Sectors : %d,  Each Sector Angle : %6.4f deg" %(sectors, 360/float(sectors)))

    tupleNode =()
    for i in range(len(BodyNode)):
        tupleNode = tupleNode + tuple(BodyNode[i])
    Nset = len(BodyNode[0])
    tupleElement = ()
    # cnt2 = 0; cnt3 = 0;cnt4 = 0
    BodySet=ELSET()
    ## Elset.AddNumber(int(word[i]), name)


    for i in range(len(BodyElement)):
        tList=[]
        for k in range(len(BodyElement[i])):
            if BodyElement[i][k] == '':
                tList.append(0)
            elif k == 5 or k > 6:
                tList.append(0)
            else:
                tList.append(BodyElement[i][k])
        BodySet.Add(BodyElement[i][0], BodyElement[i][5])        
        # print tList
        # if BodyElement[i][6] == 2: cnt2 += 1
        # if BodyElement[i][6] == 3: cnt3 += 1
        # if BodyElement[i][6] == 4: cnt4 += 1
        
        tupleElement = tupleElement + tuple(tList)
    Eset = len(BodyElement[0])
    # print ("solid 2Node=%d"%(cnt2))
    # print ("solid 3Node=%d"%(cnt3))
    # print ("solid 4Node=%d"%(cnt4))
    _islm.CreateTireBody(Mesh3DBody, tupleNode, Nset, tupleElement, Eset, 5000, 5000, OffsetSector, sectors)

    
    fline =""
    i = 0
    while i < len(BodySet.Elset):
        ElsetName = BodySet.Elset[i][0]
        line = "*ELSET, ELSET=" + ElsetName + "\n"
        # print (ElsetName)
        for m in range(sectors): 
            dline = ""
            for k, no in enumerate(BodySet.Elset[i]): 
                if k == 0: continue     ## %9d 

                if k == len(BodySet.Elset[i]) - 1:                   word = "%9d,\n"%(no+ m * OffsetSector) 
                elif k % 15 == 0:                            word = "%9d,\n"%(no+ m * OffsetSector)  
                else:                                        word = "%9d,"%(no+ m * OffsetSector) 

                dline += word 
            line += dline 
        fline += line 
        i += 1
    
    for en in Elset:
        if "BETWEEN" in en[0].upper(): 
            line = "*ELSET, ELSET=BETWEEN_BELTS\n"
            # print (ElsetName)
            for m in range(sectors): 
                dline = ""
                for k, no in enumerate(en): 
                    if k == 0: continue     ## %9d 

                    if k == len(en) - 1:                   word = "%9d,\n"%(no+ m * OffsetSector) 
                    elif k % 15 == 0:                      word = "%9d,\n"%(no+ m * OffsetSector)  
                    else:                                  word = "%9d,"%(no+ m * OffsetSector) 

                    dline += word 
                line += dline 
            fline += line 


    f = open(Mesh3DBody+'.axi', "a")
    f.writelines(fline)
    f.close()


    
    fline = []
    fulltext=''
    #######################################################################################
    ## BD1 : ELSET 
    #######################################################################################
    fline.append(["*ELSET, ELSET=BD1\n"])
    fulltext+= "*ELSET, ELSET=BD1\n"
    i = 0
    while i < len(Elset):
    # for i in range(len(Elset)):
        if "BEAD" in Elset[i][0]:
            k = 0
            while k < sectors:
            # for k in range(sectors):
                count = 0
                m = 1
                while m < len(Elset[i]):
                # for m in range(1, len(Elset[i])):
                    newEL = Elset[i][m] + k * OffsetSector
                    count += 1
                    if count % 16 == 0 or count == len(Elset[i])-1:
                        fline.append(["%d,\n" % (newEL)])
                        fulltext += str(newEL)+",\n"
                    else:
                        fline.append(["%d, " % (newEL)])
                        fulltext += str(newEL)+", "
                    m += 1
                k+=1
        i += 1
    ############################################################################################
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=TIREBODY\n"])
    fulltext += "*SURFACE, TYPE=ELEMENT, NAME=TIREBODY\n"
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(BodyOut):
            # for j in range(len(BodyOut)):
            newEL = BodyOut[j][4] + i * OffsetSector
            face = Change3DFace(BodyOut[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += str(newEL)+", " + str(face) + "\n"
            j += 1
        i += 1

    RicR = []
    RicL = []
    for ric in RimContactSurface:
        for nd in BodyNode:
            if nd[0] == ric[1] and nd[2] < 0: 
                RicR.append(ric)
                break
    for ric in RimContactSurface:
        for nd in BodyNode:        
            if nd[0] == ric[1] and nd[2] > 0: 
                RicL.append(ric)
                break
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=RIC_R\n"])
    fulltext += "*SURFACE, TYPE=ELEMENT, NAME=RIC_R\n"
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(RicR):
            newEL = RicR[j][4] + i * OffsetSector
            face = Change3DFace(RicR[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += str(newEL)+", " + str(face) + "\n"
            j += 1
        i += 1
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=RIC_L\n"])
    fulltext += "*SURFACE, TYPE=ELEMENT, NAME=RIC_L\n"
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(RicL):
            newEL = RicL[j][4] + i * OffsetSector
            face = Change3DFace(RicL[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += str(newEL)+", " + str(face) + "\n"
            j += 1
        i += 1
    ############################################################################################
    fline.append(["*SURFACE, TYPE=ELEMENT, NAME=PRESS\n"])
    fulltext += "*SURFACE, TYPE=ELEMENT, NAME=PRESS\n"
    i = 0
    while i < sectors:
        # for i in range(sectors):
        j = 0
        while j < len(PressureSurface):
            # for j in range(len(PressureSurface)):
            newEL = PressureSurface[j][4] + i * OffsetSector
            face = Change3DFace(PressureSurface[j][3])
            fline.append(['%10d, %s\n' % (newEL, face)])
            fulltext += str(newEL)+", " + str(face) + "\n"
            j += 1
        i += 1

    f = open(Mesh3DBody+'.axi', "a")
    f.writelines(fulltext)
    f.close()

    fline ="********************************************************************************************************\n" 
    for i, me in enumerate(MasterEdges): ## edge=[N1, N2, "name", face, el No]
        f = 0 
        for te in BodyElement: 
            if me[4] == te[0]: 
                f=1
                break 
        if f == 1: 
            fline += '*SURFACE, TYPE=ELEMENT, NAME=M%d_TIE\n' % (i+1)
            for k in range(sectors): 
                newel = me[4] + k  * OffsetSector 
                face = Change3DFace(me[3])
                fline += '%10d, %s\n' % (newel, face)

            fline += '*SURFACE, TYPE=ELEMENT, NAME=S%d_TIE\n' % (i+1)
            for se in SlaveEdges[i]: 
                for k in range(sectors): 
                    newel = se[4] + k  * OffsetSector 
                    face = Change3DFace(se[3])
                    fline += '%10d, %s\n' % (newel, face)

            fline += '*TIE, NAME=T%d_TIE\n' % (i+1)
            fline +=  ' S%d_TIE, M%d_TIE\n' % (i+1, i+1)

    
    f = open(Mesh3DBody+'.axi', "a")
    f.writelines(fline)
    f.close()


def ElementCheck (Elements, Nodes):
    # rebar Connectivity
    # Element Shape 
    
    tmpEL = []
    for i in range(len(Elements)):
        tmpEL.append(Elements[i][0])
        tmpEL.append(Elements[i][1])
        tmpEL.append(Elements[i][2])
        if Elements[i][3] == '':
            tmpEL.append(0)
        else:
            tmpEL.append(Elements[i][3])
        if Elements[i][4] == '':
            tmpEL.append(0)
        else:
            tmpEL.append(Elements[i][4])
        tmpEL.append(Elements[i][6])

    tmpND = []
    tmpCoord = []
    for i in range(len(Nodes)):
        tmpND.append(Nodes[i][0])
        tmpCoord.append(Nodes[i][1])
        tmpCoord.append(Nodes[i][2])
        tmpCoord.append(Nodes[i][3])
    
    tupleEL =tuple(tmpEL)
    tupleND =tuple(tmpND)
    tupleCo = tuple(tmpCoord)


    Results  = _islm.SolidRebarCheck(tupleEL, 6, tupleND, tupleCo, 3, 5)

    Message=[]
    if Results > 100000:
        if Results % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] More than 1 Sold Element is distorted."])
            Results = 0
        if (Results/10) % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] More than 1 Rebar is disconnected."])
            Results = 0
        if (Results/100) % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] Some Rebar Elements are Defined Twice or More."])
            Results = 0
        if (Results/1000) % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] Some CGAX3H Elements are Defined Twice or More."])
            Results = 0
        if (Results/10000) % 10 == 1:
            Message.append(["ERROR::PRE::[INPUT] Some CGAX4H Elements are Defined Twice or More."])
            Results = 0
    else:
        Results = 1

    return Results, Message


def plot_geometry_Deformed(imagefile, viewNode, viewElement, AllElements, Node, Elset, OrgNode, MasterEdges=[], SlaveEdges=[], Press=[], RimContact=[], TreadToRoad=[], TreadBaseEdges=[], BodyToTreadEdges=[], TreadNode=[]):
    #    print ('*******************************************************')
    #    print (' View Option (Default - Node No : off, Element No.: Off)')
    #    print ('  - Node Number veiw : node/n=on')
    #    print ('  - Element Number view : element/eL/e=on')
    #    print ('    ex) python ...py n=on e=on')
    #    print ('*******************************************************')

    textsize = 10
    cdepth = 0.8

    NodeSize = 0.1
    viewMembrane = 1
    viewTDNode = 0

    MeshLineWidth = 0.1
    MembWidth = 0.3

    if len(Press) > 0 and len(RimContact) > 0:
        viewSurface = 1
    else:
        viewSurface = 0

    if len(MasterEdges) > 0:
        viewTie = 1
    else:
        viewTie = 0

    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('off')

    deformedcolor = 'tomato'

    i = 0
    while i < len(AllElements):
        if AllElements[i][6] == 2:
            x1 = find_z(AllElements[i][1], OrgNode) * -1;
            x2 = find_z(AllElements[i][2], OrgNode) * -1
            y1 = find_r(AllElements[i][1], OrgNode);
            y2 = find_r(AllElements[i][2], OrgNode)

            color = deformedcolor
            if viewMembrane == 1:
                plt.plot([x1, x2], [y1, y2], color, lw=MembWidth)
                if viewElement == 1:
                    plt.text((x1 + x2) / 2, (y1 + y2) / 2, AllElements[i][0], color=color, size=textsize)
        i += 1

    # View Org Nodes
    x = [];
    y = []  # NodeX
    i = 0
    while i < len(OrgNode):
        x.append(OrgNode[i][2] * -1)
        y.append(OrgNode[i][3])
        i += 1

    plt.scatter(x, y, color=deformedcolor, s=NodeSize*5, marker=',', label='Initial Nodes', edgecolors='none')

    ########################################################################################

    i = 0;
    c = 0
    while i < len(AllElements):
        if AllElements[i][6] == 3:
            hatch = 0
            x1 = find_z(AllElements[i][1], Node) * -1
            x2 = find_z(AllElements[i][2], Node) * -1
            x3 = find_z(AllElements[i][3], Node) * -1
            y1 = find_r(AllElements[i][1], Node)
            y2 = find_r(AllElements[i][2], Node)
            y3 = find_r(AllElements[i][3], Node)
            j = 0
            # color = 'b'

            icolor = Color(AllElements[i][5])

            for m in range(len(Elset)):
                if Elset[m][0] == 'BETWEEN_BELTS':
                    break
            for k in range(len(Elset[m])):
                if Elset[m][k] == AllElements[i][0]:
                    hatch = 1;
                    c += 1
                    break
            if hatch == 1:
                if c == 1:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth * 2, hatch='//')
                else:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth * 2, hatch='//')
            else:
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
            ax.add_patch(polygon)

            if viewElement == 1:
                plt.text((x1 + x2 + x3) / 3, (y1 + y2 + y3) / 3, AllElements[i][0], color='blue', size=textsize)

        if AllElements[i][6] == 4:
            hatch = 0
            x1 = find_z(AllElements[i][1], Node) * -1;
            x2 = find_z(AllElements[i][2], Node) * -1;
            x3 = find_z(AllElements[i][3], Node) * -1;
            x4 = find_z(AllElements[i][4], Node) * -1
            y1 = find_r(AllElements[i][1], Node)
            y2 = find_r(AllElements[i][2], Node)
            y3 = find_r(AllElements[i][3], Node)
            y4 = find_r(AllElements[i][4], Node)
            j = 0;
            # color = 'b'
            icolor = Color(AllElements[i][5])
            for m in range(len(Elset)):
                if Elset[m][0] == 'BETWEEN_BELTS':
                    break
            for k in range(len(Elset[m])):
                if Elset[m][k] == AllElements[i][0]:
                    hatch = 1;
                    c += 1
                    break
            if hatch == 1:
                if c == 1:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth, hatch='//')
                else:
                    polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth, hatch='//')
            else:
                polygon = plt.Polygon([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], color=icolor, alpha=cdepth, lw=MeshLineWidth)
            ax.add_patch(polygon)

            if viewElement == 1:
                plt.text((x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4, AllElements[i][0], color='blue', size=textsize)

        i += 1

    if viewSurface == 1:
        PressWidth = 0.5
        RimWidth = 0.5
        TieWidth = 0.8
        TDBaseWidth = 0.4
        BDTopWidth = TDBaseWidth * 0.5
        TreadRoadWidth = 0.3

        i = 0
        while i < len(Press):
            x1 = find_z(Press[i][0], Node) * -1;
            x2 = find_z(Press[i][1], Node) * -1;
            y1 = find_r(Press[i][0], Node);
            y2 = find_r(Press[i][1], Node);
            color = Color('PRESS')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=PressWidth, label='Pressure')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=PressWidth)
            i += 1

        i = 0
        while i < len(RimContact):
            x1 = find_z(RimContact[i][0], Node) * -1;
            x2 = find_z(RimContact[i][1], Node) * -1;
            y1 = find_r(RimContact[i][0], Node);
            y2 = find_r(RimContact[i][1], Node);
            color = Color('RIM')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=RimWidth, label='Rim Contact', linestyle=':')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=RimWidth, linestyle=':')
            i += 1

    if viewTie == 1:
        i = 0;
        j = 0
        iColor = ['midnightblue', 'magenta', 'violet', 'brown', 'aqua', 'coral', 'chocolate',
                  'orange', 'steelblue', 'teal', 'dimgray']

        i = 0
        while i < len(MasterEdges):
            x1 = find_z(MasterEdges[i][0], Node) * -1;
            x2 = find_z(MasterEdges[i][1], Node) * -1
            y1 = find_r(MasterEdges[i][0], Node);
            y2 = find_r(MasterEdges[i][1], Node)
            if (i + 1) % len(iColor) == 0 or (i + 1) % len(MasterEdges) == 0:
                j = 0
            else:
                j += 1
            if i == 0:
                plt.plot([x1, x2], [y1, y2], iColor[j], linestyle='-', linewidth=TieWidth, label='Tie Master, White line - Slave')
            else:
                plt.plot([x1, x2], [y1, y2], iColor[j], linestyle='-', linewidth=TieWidth)
            i += 1

        i = 0
        while i < len(SlaveEdges):
            x1 = find_z(SlaveEdges[i][0], Node) * -1;
            x2 = find_z(SlaveEdges[i][1], Node) * -1
            y1 = find_r(SlaveEdges[i][0], Node);
            y2 = find_r(SlaveEdges[i][1], Node)
            plt.plot([x1, x2], [y1, y2], 'white', linewidth=TieWidth * 0.5)
            i += 1

    if len(TreadBaseEdges) > 0:
        i = 0
        while i < len(TreadBaseEdges):
            x1 = find_z(TreadBaseEdges[i][0], Node) * -1;
            x2 = find_z(TreadBaseEdges[i][1], Node) * -1
            y1 = find_r(TreadBaseEdges[i][0], Node);
            y2 = find_r(TreadBaseEdges[i][1], Node)
            color = Color('TDBASE')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, linewidth=TDBaseWidth, linestyle='-', label='Tread Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, linewidth=TDBaseWidth, linestyle='-')
            i += 1
    if len(TreadToRoad) > 0:
        i = 0
        while i < len(TreadToRoad):
            x1 = find_z(TreadToRoad[i][0], Node) * -1;
            x2 = find_z(TreadToRoad[i][1], Node) * -1;
            y1 = find_r(TreadToRoad[i][0], Node);
            y2 = find_r(TreadToRoad[i][1], Node);
            color = Color('TDROAD')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=TreadRoadWidth, linestyle=':', label='Road Contact Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=TreadRoadWidth, linestyle=':')
            i += 1

    if len(BodyToTreadEdges) > 0:
        i = 0
        while i < len(BodyToTreadEdges):
            x1 = find_z(BodyToTreadEdges[i][0], Node) * -1;
            x2 = find_z(BodyToTreadEdges[i][1], Node) * -1;
            y1 = find_r(BodyToTreadEdges[i][0], Node);
            y2 = find_r(BodyToTreadEdges[i][1], Node);
            color = Color('BDTOP')
            if i == 0:
                plt.plot([x1, x2], [y1, y2], color, lw=BDTopWidth, linestyle=':', label='Body Surface')
            else:
                plt.plot([x1, x2], [y1, y2], color, lw=BDTopWidth, linestyle=':')
            i += 1

    i = 0
    counting = 0
    while i < len(AllElements):
        if AllElements[i][6] == 2:
            x1 = find_z(AllElements[i][1], Node) * -1;
            x2 = find_z(AllElements[i][2], Node) * -1
            y1 = find_r(AllElements[i][1], Node);
            y2 = find_r(AllElements[i][2], Node)

            color = Color("MEMB")
            if viewMembrane == 1:
                if counting ==0:
                    plt.plot([x1, x2], [y1, y2], color, lw=MembWidth, label = 'Inflated Shape')
                    counting +=1
                else:
                    plt.plot([x1, x2], [y1, y2], color, lw=MembWidth)
                if viewElement == 1:
                    plt.text((x1 + x2) / 2, (y1 + y2) / 2, AllElements[i][0], color=color, size=textsize)
        i += 1

    # View Nodes In Tread
    x = [];
    y = []  # NodeX
    i = 0
    if viewTDNode == 1:
        while i < len(TreadNode):
            x.append(TreadNode[i][2] * -1)
            y.append(TreadNode[i][3])
            i += 1
        color = Color("DOT")
        plt.scatter(x, y, color=color, s=NodeSize, marker='o', label='Tread Nodes')

    # View All Nodes
    x = [];
    y = []  # NodeX
    i = 0
    while i < len(Node):
        x.append(Node[i][2] * -1)
        y.append(Node[i][3])
        i += 1

    if viewNode == 1:
        Num = len(Node)
        ax.scatter(x, y)
        i = 0
        for i, txt in enumerate(Num):
            ax.annotate(txt, (x[i], y[i]), size=textsize)

    # first_legend=plt.legend(handles=[TreadNode], loc=1)
    leg = ax.legend(loc='upper left', frameon=False, fontsize=5)
    # leg.get_frame().set_alpha(0.4)
    #    items=[nodeText]

    # plt.show()
    # plt.subplots_adjust(wspace=0.001, hspace=0.001)
    plt.savefig(imagefile, dpi=500)

    return 1

def plot_lines(imagefileName, Line, Line1=[], Line2=[], Line3=[], Line4=[], Line5=[]):
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('off')
    bar = '-'
    L0c = 'gray'
    L1c = 'gray'
    L2c = 'red'
    L3c = 'red'
    L4c = 'gray'
    L5c = 'orange'
    LineWidth = 0.2

    # Line = [[x11, y11, x12, y12], [x21, y21, x22, y22], [ ... ], ...]
    # you can make Line of list with function below
    # freeEdges= FindElsetFreeEdges(element, Elsetname)
    # Line = MakeLineSetsForPlots(freeEdges, Node)
    # line style = '-'

    N0 = len(Line)
    N1 = len(Line1)
    N2 = len(Line2)
    N3 = len(Line3)
    N4 = len(Line4)
    N5 = len(Line5)

    for i in range(N0):
        plt.plot([Line[i][0], Line[i][2]], [Line[i][1], Line[i][3]], L0c, lw=LineWidth, linestyle = bar)
    for i in range(N1):
        plt.plot([Line1[i][0], Line1[i][2]], [Line1[i][1], Line1[i][3]], L1c, lw=LineWidth, linestyle = bar)
    for i in range(N2):
        plt.plot([Line2[i][0], Line2[i][2]], [Line2[i][1], Line2[i][3]], L2c, lw=LineWidth, linestyle = bar)
    for i in range(N3):
        plt.plot([Line3[i][0], Line3[i][2]], [Line3[i][1], Line3[i][3]], L3c, lw=LineWidth, linestyle = bar)
    for i in range(N4):
        plt.plot([Line4[i][0], Line4[i][2]], [Line4[i][1], Line4[i][3]], L4c, lw=LineWidth, linestyle = bar)
    for i in range(N5):
        plt.plot([Line5[i][0], Line5[i][2]], [Line5[i][1], Line5[i][3]], L5c, lw=LineWidth, linestyle = bar)



    plt.savefig(imagefileName, dpi=500)

def FindElsetFreeEdges(element, setname):

    N=len(element)

    TargetElements=[]

    for i in range(N):
        if setname == element[i][5]:
            TargetElements.append(element[i])

    edges = FindEdge(TargetElements)
    fEdges = FindFreeEdge(edges)

    ########################################################################################
    ## # elements=[Element No, 1st Node, 2nd Node, 3rd Node, 4th Node, Mat_name, '']
    # edge element [node1, node2, ElsetName, FaceID, elementNo, 0]

    return fEdges

def MakeLineSetsForPlots(EdgeList, uNode):

    pointSets =[]
    N = len(EdgeList)
    for i in range(N):
        Nc1 = Coordinates(EdgeList[i][0], uNode)
        Nc2 = Coordinates(EdgeList[i][1], uNode)
        pointSets.append([Nc1[1], Nc1[2], Nc2[1], Nc2[2]])

    return pointSets

def MakeMembLineSetsForPlots(Membsets, uNode):
    pointSets = []
    N = len(Membsets)
    for i in range(N):
        Nc1 = Coordinates(Membsets[i][1], uNode)
        Nc2 = Coordinates(Membsets[i][2], uNode)
        pointSets.append([Nc1[1], Nc1[2], Nc2[1], Nc2[2]])

    return pointSets


def NodeDistance(N1, N2): 
    return math.sqrt((N2[1]-N1[1])*(N2[1]-N1[1]) + (N2[2]-N1[2])*(N2[2]-N1[2]) + (N2[3]-N1[3])*(N2[3]-N1[3]))

def DistanceFromLineToNode2D(N0, nodes=[], xy=23, onlydist=0):
    x = int(xy/10)
    y = int(xy%10)

    N1=nodes[0]
    N2=nodes[1]
    if len(nodes) ==2: 
        if round(N2[x]-N1[x], 6) !=0: 
            a = (N2[y]-N1[y])/(N2[x]-N1[x])
            A = -a
            C = a * N1[x] - N1[y]

            ## intersection position : N 
            cx = (-a * (-a*N1[x] + N1[y]) +     (N0[x] + a * N0[y]) )/ (1 + a*a)
            cy = (     (-a*N1[x] + N1[y]) + a * (N0[x] + a * N0[y]) )/ (1 + a*a)
            N=[-1, 0, 0, 0]
            N[x] = cx
            N[y] = cy
            distance = abs(A*N0[x]+N0[y]+C) / math.sqrt(A*A+1)
        else: 
            distance = abs(N0[x] - N1[x])
            N=[-1, 0, 0, 0]
            N[x] = N1[x]
            N[y] = N0[y]
        if onlydist ==1: 
            return distance
        else: 
            return distance, N 

def NextEdge(edge, k):
    tmp = k
    connected = []
    N = len(edge.Edge)
    for i in range(N):
        if tmp != i:
            if edge.Edge[tmp][1] == edge.Edge[i][0]:
                connected.append(i)
    return connected

def PreviousEdge(edge, k):
    tmp = k
    connected = []
    N = len(edge.Edge)
    for i in range(N):
        if tmp != i:
            if edge.Edge[tmp][0] == edge.Edge[i][1]:
                connected.append(i)
    return connected

def FreeEdge(edge):
    FEdge = EDGE()
    try:
        tupleL = ()
        for i in range(len(edge.Edge)):
            list = []
            list.append(edge.Edge[i][0])
            list.append(edge.Edge[i][1])
            list.append(0)
            if edge.Edge[i][3] == 'S1':
                list.append(1)
            elif edge.Edge[i][3] == 'S2':
                list.append(2)
            elif edge.Edge[i][3] == 'S3':
                list.append(3)
            elif edge.Edge[i][3] == 'S4':
                list.append(4)
            list.append(edge.Edge[i][4])
            if edge.Edge[i][5] == '':
                edge.Edge[i][5] = -2
            list.append(edge.Edge[i][5])
            tupleL = tupleL + tuple(list)

        flist = _islm.FindFreeEdgePylist(tupleL, 6)

        for i in range(len(edge.Edge)):
            edge.Edge[i][5] = flist[i]
            if flist[i] == 0:
                FEdge.Add(edge.Edge[i])
    except:
        print ("* Finding Free Edges by Python Script")

        for i in range(len(edge.Edge)):
            if edge.Edge[i][5] == -1:
                j = i + 1
                count = 0
                while j < len(edge.Edge):
                    if edge.Edge[j][5] == -1:
                        if edge.Edge[i][0] == edge.Edge[j][0] and edge.Edge[i][1] == edge.Edge[j][1]:
                            count += 1
                            edge.Edge[i][5] = -2
                            edge.Edge[j][5] = -2
                            break
                        elif edge.Edge[i][0] == edge.Edge[j][1] and edge.Edge[i][1] == edge.Edge[j][0]:
                            count += 1
                            edge.Edge[i][5] = -2
                            edge.Edge[j][5] = -2
                            break
                    j += 1
                if count == 0:
                    edge.Edge[i][5] = 0
                    FEdge.Add(edge.Edge[i])

    return FEdge

def OuterEdge(FreeEdge, Node, Element):

    # FreeEdge.Image(Node, "EDGEIMAGE")
    
    N = len(FreeEdge.Edge)
    
    MinY = 9.9E20
    
    cNodes = [0]
    for i in range(N):
        N1 = Node.NodeByID(FreeEdge.Edge[i][0])
        N2 = Node.NodeByID(FreeEdge.Edge[i][1])
        if N1[3] < MinY:
            MinY = N1[3]
            cNodes[0] = N1[0]
        if N2[3] < MinY:
            MinY = N2[3]
            cNodes[0] = N2[0]
    if cNodes[0] == 0:
        cNodes[0] = Node.NodeIDByCoordinate('z', 0, closest=1)

    MAX = 10000   ## max iteration for searching  error
    ShareNodePos = []
    #    connectedEdge = []
    outEdge = EDGE()

    ## Find a 1st surround edge (IL at the center)
    low = 9.9E20
    i = 0
    savei = 0
    while i < len(cNodes):
        j = 0
        while j < len(Node.Node):
            if cNodes[i] == Node.Node[j][0]:
                if Node.Node[j][3] < low:
                    low = Node.Node[j][3]
                    savei = j
            j += 1
        i += 1

    i = 0
    while i < len(FreeEdge.Edge):
        if Node.Node[savei][0] == FreeEdge.Edge[i][0]:
            break
        i += 1

    ## End of 1st Outer Edge finding (IL1)
    # print (i, len(FreeEdge.Edge))
    # print (FreeEdge.Edge[i])
    FreeEdge.Edge[i][5] = 1
    outEdge.Add(FreeEdge.Edge[i])
    iFirstNode = FreeEdge.Edge[i][0]

    count = 0

    #    i=  # i is no matter how big, because i is redefined when next edge is found

    while i < len(FreeEdge.Edge):
        count += 1
        if count > MAX:
            print ('[INPUT] CANNOT FIND OUTER EDGES IN THE MODEL')
            del (outEdge)
            outEdge = EDGE()
            return outEdge
        j = 0
        while j < len(FreeEdge.Edge):
            if i != j:
                if FreeEdge.Edge[i][1] == FreeEdge.Edge[j][0]:
                    # print ('edge[i][1], [j][0] ', FreeEdge.Edge[i], FreeEdge.Edge[j], 'i=', i)
                    ShareNodePos.append(j)
                    # print (ShareNodePos, FreeEdge.Edge[ShareNodePos[0]][0])
            j = j + 1
        if len(ShareNodePos) != 0:
            if FreeEdge.Edge[ShareNodePos[0]][0] == iFirstNode:
                break
        else:
            print ('[INPUT] CANNOT FIND CONNECTED FREE EDGE. CHECK TIE CONDITION')
            del (outEdge)
            outEdge = EDGE()
            return outEdge
        # print ('sharenodePos count = ', len(ShareNodePos))

        if len(ShareNodePos) == 1:
            FreeEdge.Edge[ShareNodePos[0]][5] = 1
            outEdge.Add(FreeEdge.Edge[ShareNodePos[0]])
            i = ShareNodePos[0]
            del ShareNodePos
            ShareNodePos = []
        else:
            if FreeEdge.Edge[i][4] == FreeEdge.Edge[ShareNodePos[0]][4]:
                tmpPos = ShareNodePos[1]
            else:
                SHARE = ShareEdge(FreeEdge.Edge[i][4], FreeEdge.Edge[ShareNodePos[1]][4], Element)
                if SHARE == 1:
                    tmpPos = ShareNodePos[0]
                else:
                    tmpPos = ShareNodePos[1]

                    #######################################################
                    nfe1 = 0; nfe2 = 0
                    for fe in FreeEdge.Edge:
                        if fe[4] == FreeEdge.Edge[tmpPos][4]:
                            # print (fe)
                            nfe1 += 1
                        if fe[4] == FreeEdge.Edge[ShareNodePos[0]][4]:
                            # print (fe)
                            nfe2 += 1
                    # print ("nfe=", nfe, FreeEdge[tmpPos])
                    if nfe1 < nfe2:
                        tmpPos = ShareNodePos[0]
                    elif nfe1 == nfe2:
                        tienode = FreeEdge.Edge[tmpPos][0]
                        nc = 0
                        for fe in FreeEdge.Edge:
                            if fe[4] == FreeEdge.Edge[tmpPos][4] and fe[1] == tienode: 
                                nc += 1
                                break
                        if nc == 0:   tmpPos = ShareNodePos[0]
                    ########################################################

            FreeEdge.Edge[tmpPos][5] = 1
            outEdge.Add(FreeEdge.Edge[tmpPos])
            i = tmpPos
            del ShareNodePos
            ShareNodePos = []
            
    return outEdge