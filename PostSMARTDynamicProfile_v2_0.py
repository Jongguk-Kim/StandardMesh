# *******************************************************************
#    Import library
# *******************************************************************
import matplotlib
matplotlib.use('Agg')
# import os, glob, json
import os, sys, glob, json, CheckExecution
# import sys, string, struct, math
import time, math
import matplotlib.pyplot as plt
try:
    import CommonFunction as TIRE
except: 
    import CommonFunction_v2_0 as TIRE

def PrintBeltLiftDynamic3(BF0, BF1, BF2, BF3, SP1, SP2, SP3, PR0, RimCenter):
    with open(BF0) as IF0:
        lines0 = IF0.readlines()
    with open(BF1) as IF1:
        lines1 = IF1.readlines()
    with open(BF2) as IF2:
        lines2 = IF2.readlines()
    with open(BF3) as IF3:
        lines3 = IF3.readlines()

    deformedSP0 = []
    for line in lines0:
        # print line
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP0.append([int(data[0]), float(data[1]), float(data[2]), float(data[3]) - RimCenter[0]])
                # print data

    deformedSP1 = []
    for line in lines1:
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP1.append([int(data[0]), float(data[1]), float(data[2]), float(data[3])- RimCenter[1]])

    deformedSP2 = []
    for line in lines2:
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP2.append([int(data[0]), float(data[1]), float(data[2]), float(data[3])- RimCenter[2]])

    deformedSP3 = []
    for line in lines3:
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP3.append([int(data[0]), float(data[1]), float(data[2]), float(data[3]) - RimCenter[3]])

    center = 1000.0
    ic = 0
    no = len(deformedSP0)
    for i in range(no):
        if center > abs(deformedSP0[i][2]):
            center = abs(deformedSP0[i][2])
            ic = i

    # print (no, ic, len(deformedSP0), len(deformedSP1), len(deformedSP2), len(deformedSP3))
    Sp1CenLift = (deformedSP1[ic][3] - deformedSP0[ic][3])*1000
    Sp2CenLift = (deformedSP2[ic][3] - deformedSP0[ic][3])*1000
    Sp3CenLift = (deformedSP3[ic][3] - deformedSP0[ic][3])*1000

    Sp1EdgeLift = ((deformedSP1[0][3] - deformedSP0[0][3]) + (deformedSP1[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000
    Sp2EdgeLift = ((deformedSP2[0][3] - deformedSP0[0][3]) + (deformedSP2[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000
    Sp3EdgeLift = ((deformedSP3[0][3] - deformedSP0[0][3]) + (deformedSP3[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000


    # tline = str(format(PR0, '10.2f')) + '\t\t' + str(format(SP1, '4.0f')) + '\t\t' + str(format(Sp1CenLift, '6.2f')) + '\t\t\t' + str(format(Sp1EdgeLift, '6.2f')) + '\n'
    # tf.write(tline)
    # tline = str(format(PR0, '10.2f')) + '\t\t' + str(format(SP2, '4.0f')) + '\t\t' + str(format(Sp2CenLift, '6.2f')) + '\t\t\t' + str(format(Sp2EdgeLift, '6.2f')) + '\n'
    # tf.write(tline)
    # tline = str(format(PR0, '10.2f')) + '\t\t' + str(format(SP3, '4.0f')) + '\t\t' + str(format(Sp3CenLift, '6.2f')) + '\t\t\t' + str(format(Sp3EdgeLift, '6.2f')) + '\n'
    # tf.write(tline)

    tline = str(format(PR0, '10.2f')) + '              ' + str(format(SP1, '4.0f')) + '                ' + str(format(Sp1CenLift, '6.2f')) + '                ' + str(format(Sp1EdgeLift, '6.2f')) + '\n'
    tf.write(tline)
    tline = str(format(PR0, '10.2f')) + '              ' + str(format(SP2, '4.0f')) + '                ' + str(format(Sp2CenLift, '6.2f')) + '                ' + str(format(Sp2EdgeLift, '6.2f')) + '\n'
    tf.write(tline)
    tline = str(format(PR0, '10.2f')) + '              ' + str(format(SP3, '4.0f')) + '                ' + str(format(Sp3CenLift, '6.2f')) + '                ' + str(format(Sp3EdgeLift, '6.2f')) + '\n'
    tf.write(tline)


    tline = '*BT Deformed Coordinates in the Uppermost Sector(Node No, X = 0, Y, Z) \n'
    bf.write(tline)
    tline = '*Speed : 0 km/h ' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP0)):
        line = str(format(deformedSP0[i][0], '10d')) + ', ' + str(format(deformedSP0[i][1], '9.6E')) + ', ' + str(format(deformedSP0[i][2], '9.6E'))+ ', ' + str(format(deformedSP0[i][3], '9.6E')) + '\n'
        bf.write(line)
    tline = '*Speed : ' + str(SP1) + ' km/h' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP1)):
        line = str(format(deformedSP1[i][0], '10d')) + ', ' + str(format(deformedSP1[i][1], '9.6E')) + ', ' + str(format(deformedSP1[i][2], '9.6E'))+ ', ' + str(format(deformedSP1[i][3], '9.6E'))+ '\n'
        bf.write(line)
    tline = '*Speed : ' + str(SP2) + ' km/h' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP0)):
        line = str(format(deformedSP2[i][0], '10d')) + ', ' + str(format(deformedSP2[i][1], '9.6E')) + ', ' + str(format(deformedSP2[i][2], '9.6E'))+ ', ' + str(format(deformedSP2[i][3], '9.6E'))+ '\n'
        bf.write(line)
    tline = '*Speed : ' + str(SP3) + ' km/h' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP0)):
        line = str(format(deformedSP3[i][0], '10d')) + ', ' + str(format(deformedSP3[i][1], '9.6E')) + ', ' + str(format(deformedSP3[i][2], '9.6E'))+ ', ' + str(format(deformedSP3[i][3], '9.6E'))+ '\n'
        bf.write(line)

def PrintBeltLiftDynamic2(BF0, BF1, BF2, SP1, SP2, PR0, RimCenter):
    with open(BF0) as IF0:
        lines0 = IF0.readlines()
    with open(BF1) as IF1:
        lines1 = IF1.readlines()
    with open(BF2) as IF2:
        lines2 = IF2.readlines()

    deformedSP0 = []
    for line in lines0:
        # print line
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP0.append([int(data[0]), float(data[1]), float(data[2]), float(data[3]) - RimCenter[0]])
                # print data

    deformedSP1 = []
    for line in lines1:
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP1.append([int(data[0]), float(data[1]), float(data[2]), float(data[3]) - RimCenter[1]])

    deformedSP2 = []
    for line in lines2:
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP2.append([int(data[0]), float(data[1]), float(data[2]), float(data[3]) - RimCenter[2]])

    center = 1000.0
    ic = 0
    no = len(deformedSP0)
    for i in range(no):
        if center > abs(deformedSP0[i][2]):
            center = abs(deformedSP0[i][2])
            ic = i

    # print (no, ic, len(deformedSP0), len(deformedSP1), len(deformedSP2), len(deformedSP3))
    Sp1CenLift = (deformedSP1[ic][3] - deformedSP0[ic][3]) * 1000
    Sp2CenLift = (deformedSP2[ic][3] - deformedSP0[ic][3]) * 1000
    #
    Sp1EdgeLift = ((deformedSP1[0][3] - deformedSP0[0][3]) + (deformedSP1[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000
    Sp2EdgeLift = ((deformedSP2[0][3] - deformedSP0[0][3]) + (deformedSP2[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000
    # Sp1CenLift = (deformedSP1[ic][2] - deformedSP0[ic][2] ) *1000
    # Sp2CenLift = (deformedSP2[ic][2] - deformedSP0[ic][2]) *1000
    #
    # Sp1EdgeLift = ((deformedSP1[0][2] - deformedSP0[0][2]) + (deformedSP1[no - 1][2] - deformedSP0[no - 1][2])) / 2 * 1000
    # Sp2EdgeLift = ((deformedSP2[0][2] - deformedSP0[0][2]) + (deformedSP2[no - 1][2] - deformedSP0[no - 1][2])) / 2 * 1000

    # tline = str(format(PR0, '10.2f')) + '\t\t' + str(format(SP1, '4.0f')) + '\t\t' + str(format(Sp1CenLift, '6.2f')) + '\t\t\t' + str(format(Sp1EdgeLift, '6.2f')) + '\n'
    # tf.write(tline)
    # tline = str(format(PR0, '10.2f')) + '\t\t' + str(format(SP2, '4.0f')) + '\t\t' + str(format(Sp2CenLift, '6.2f')) + '\t\t\t' + str(format(Sp2EdgeLift, '6.2f')) + '\n'
    # tf.write(tline)
    tline = str(format(PR0, '10.2f')) + '              ' + str(format(SP1, '4.0f')) + '                ' + str(format(Sp1CenLift, '6.2f')) + '                ' + str(format(Sp1EdgeLift, '6.2f')) + '\n'
    tf.write(tline)
    tline = str(format(PR0, '10.2f')) + '              ' + str(format(SP2, '4.0f')) + '                ' + str(format(Sp2CenLift, '6.2f')) + '                ' + str(format(Sp2EdgeLift, '6.2f')) + '\n'
    tf.write(tline)

    # tline = str(PR0) + ', ' + str(SP1) + ', ' + str(format(Sp1CenLift, '9.6E')) + ', ' + str(format(Sp1EdgeLift, '9.6E')) + '\n'
    # tf.write(tline)
    # tline = str(PR0) + ', ' + str(SP2) + ', ' + str(format(Sp2CenLift, '9.6E')) + ', ' + str(format(Sp2EdgeLift, '9.6E')) + '\n'
    # tf.write(tline)

    tline = '*BT Deformed Coordinates in the Uppermost Sector(Node No, X = 0, Y, Z) \n'
    bf.write(tline)
    tline = '*Speed : 0 km/h ' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP0)):
        line = str(format(deformedSP0[i][0], '10d')) + ', ' + str(format(deformedSP0[i][1], '9.6E')) + ', ' + str(format(deformedSP0[i][2], '9.6E'))+ ', ' + str(format(deformedSP0[i][3], '9.6E')) + '\n'
        bf.write(line)
    tline = '*Speed : ' + str(SP1) + ' km/h' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP1)):
        line = str(format(deformedSP1[i][0], '10d')) + ', ' + str(format(deformedSP1[i][1], '9.6E')) + ', ' + str(format(deformedSP1[i][2], '9.6E'))+ ', ' + str(format(deformedSP1[i][3], '9.6E'))+ '\n'
        bf.write(line)
    tline = '*Speed : ' + str(SP2) + ' km/h' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP0)):
        line = str(format(deformedSP2[i][0], '10d')) + ', ' + str(format(deformedSP2[i][1], '9.6E')) + ', ' + str(format(deformedSP2[i][2], '9.6E'))+ ', ' + str(format(deformedSP2[i][3], '9.6E'))+ '\n'
        bf.write(line)

def PrintBeltLiftDynamic1(BF0, BF1, SP1, PR0, RimCenter):
    with open(BF0) as IF0:
        lines0 = IF0.readlines()
    with open(BF1) as IF1:
        lines1 = IF1.readlines()

    deformedSP0 = []
    for line in lines0:
        # print line
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP0.append([int(data[0]), float(data[1]), float(data[2]), float(data[3]) - RimCenter[0]])
                # print data

    deformedSP1 = []
    for line in lines1:
        if (line[0] == '*'):
            if (line[:3] == '*BT'):
                spt = 'O'
            else:
                spt = 'X'
        else:
            if spt == 'O':
                data = list(line.split(','))
                deformedSP1.append([int(data[0]), float(data[1]), float(data[2]), float(data[3]) - RimCenter[1]])

    center = 1000.0
    ic = 0
    no = len(deformedSP0)
    for i in range(no):
        if center > abs(deformedSP0[i][2]):
            center = abs(deformedSP0[i][2])
            ic = i

    # print (no, ic, len(deformedSP0), len(deformedSP1), len(deformedSP2), len(deformedSP3))
    # Sp1CenLift = (deformedSP1[ic][3] - deformedSP0[ic][3]) * 1000
    # Sp2CenLift = (deformedSP2[ic][3] - deformedSP0[ic][3]) * 1000
    # Sp3CenLift = (deformedSP3[ic][3] - deformedSP0[ic][3]) * 1000
    #
    # Sp1EdgeLift = ((deformedSP1[0][3] - deformedSP0[0][3]) + (deformedSP1[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000
    # Sp2EdgeLift = ((deformedSP2[0][3] - deformedSP0[0][3]) + (deformedSP2[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000
    # Sp3EdgeLift = ((deformedSP3[0][3] - deformedSP0[0][3]) + (deformedSP3[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000
    Sp1CenLift = (deformedSP1[ic][3] - deformedSP0[ic][3]) * 1000
    Sp1EdgeLift = ((deformedSP1[0][3] - deformedSP0[0][3]) + (deformedSP1[no - 1][3] - deformedSP0[no - 1][3])) / 2 * 1000

    # tline = str(format(PR0, '10.2f')) + '\t\t' + str(format(SP1, '4.0f')) + '\t\t' + str(format(Sp1CenLift, '6.2f')) + '\t\t\t' + str(format(Sp1EdgeLift, '6.2f')) + '\n'
    # tf.write(tline)
    tline = str(format(PR0, '10.2f')) + '              ' + str(format(SP1, '4.0f')) + '                ' + str(format(Sp1CenLift, '6.2f')) + '                ' + str(format(Sp1EdgeLift, '6.2f')) + '\n'
    tf.write(tline)

 # 14, 16, 16

    # tline = str(PR0) + ', ' + str(SP1) + ', ' + str(format(Sp1CenLift, '9.6E')) + ', ' + str(format(Sp1EdgeLift, '9.6E')) + '\n'
    # tf.write(tline)

    tline = '*BT Deformed Coordinates in the Uppermost Sector(Node No, X = 0, Y, Z) \n'
    bf.write(tline)
    tline = '*Speed : 0 km/h ' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP0)):
        line = str(format(deformedSP0[i][0], '10d')) + ', ' + str(format(deformedSP0[i][1], '9.6E')) + ', ' + str(format(deformedSP0[i][2], '9.6E')) + ', ' + str(format(deformedSP0[i][3], '9.6E')) + '\n'
        bf.write(line)
    tline = '*Speed : ' + str(SP1) + ' km/h' + ' Pressure: ' + str(PR0) + ' kgf/cm2\n'
    bf.write(tline)
    for i in range(len(deformedSP1)):
        line = str(format(deformedSP1[i][0], '10d')) + ', ' + str(format(deformedSP1[i][1], '9.6E')) + ', ' + str(format(deformedSP1[i][2], '9.6E')) + ', ' + str(format(deformedSP1[i][3], '9.6E')) + '\n'
        bf.write(line)

def PlotProfile_Lift(ImageFileName, ProfileEdge, CLift, imagewidth=6.0, imageheight=8.0, offset=10000, **args):
    tN1 = TIRE.NODE()
    tN2 = TIRE.NODE()
    tN3 = TIRE.NODE()
    tN4 = TIRE.NODE()
    tN5 = TIRE.NODE()
    tN6 = TIRE.NODE()
    dpi = 150
    Ymin = 0.0
    Ymax = 0.0
    for key, value in args.items():
        if key == "n1":
            tN1 = value
            for node in tN1.Node:
                node[0] = node[0]%offset
                node[1] = 0.0
                node[3] = math.sqrt(node[1]*node[1]+node[3]*node[3])
        if key == "n2":
            tN2 = value
            for node in tN2.Node:
                node[0] = node[0]%offset
                node[1] = 0.0
                node[3] = math.sqrt(node[1]*node[1]+node[3]*node[3])
        if key == "n3":
            tN3 = value
            for node in tN3.Node:
                node[0] = node[0]%offset
                node[1] = 0.0
                node[3] = math.sqrt(node[1]*node[1]+node[3]*node[3])
        if key == "n4":
            tN4 = value
            for node in tN4.Node:
                node[0] = node[0]%offset
                node[1] = 0.0
                node[3] = math.sqrt(node[1]*node[1]+node[3]*node[3])
        if key == "n5":
            tN5 = value
            for node in tN5.Node:
                node[0] = node[0]%offset
                node[1] = 0.0
                node[3] = math.sqrt(node[1]*node[1]+node[3]*node[3])
        if key == "n6":
            tN6 = value
            for node in tN6.Node:
                node[0] = node[0]%offset
                node[1] = 0.0
                node[3] = math.sqrt(node[1]*node[1]+node[3]*node[3])
        if key =="dpi":
            dpi = value
        if key == "vmin":
            Ymin = value
        if key =="vmax":
            Ymax = value

    if len(tN1.Node) == 0:
        print ("ERROR!! No Node Information ")

    cf = plt.figure(figsize=(imagewidth, imageheight))
    fig = cf.add_subplot(2,1,2)
        
    # plt.axis('off')
    xList = []
    yList = []
    LineWidth = 0.5
    textsize = 8
    plt.xticks(size=textsize)
    plt.yticks(size=textsize)

    L1 = ""; L2=""; L3=""; L4=""; L5=""; L6=""

    N = len(ProfileEdge.Edge)
    for i in range(N):
        N1 = tN1.NodeByID(ProfileEdge.Edge[i][0])
        N2 = tN1.NodeByID(ProfileEdge.Edge[i][1])
        color = 'black'
        if L1 and i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, label=L1)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
        N1 = tN2.NodeByID(ProfileEdge.Edge[i][0])
        N2 = tN2.NodeByID(ProfileEdge.Edge[i][1])
        color = 'red'
        if L2 and i == 0:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth, label=L2)
        else:
            plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth)
        xList.append(N1[2])
        xList.append(N2[2])
        yList.append(N1[3])
        yList.append(N2[3])
        if len(tN3.Node) > 0:
            N1 = tN3.NodeByID(ProfileEdge.Edge[i][0])
            N2 = tN3.NodeByID(ProfileEdge.Edge[i][1])
            color = 'blue'
            linetype ='-'
            if L3 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L3, linestyle=linetype)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(tN4.Node) > 0:
            N1 = tN4.NodeByID(ProfileEdge.Edge[i][0])
            N2 = tN4.NodeByID(ProfileEdge.Edge[i][1])
            color = 'green'
            linetype ='-'
            if L4 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L3, linestyle=linetype)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(tN5.Node) > 0:
            N1 = tN5.NodeByID(ProfileEdge.Edge[i][0])
            N2 = tN5.NodeByID(ProfileEdge.Edge[i][1])
            color = 'gray'
            linetype ='-'
            if L5 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L3, linestyle=linetype)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])
        if len(tN6.Node) > 0:
            N1 = tN6.NodeByID(ProfileEdge.Edge[i][0])
            N2 = tN6.NodeByID(ProfileEdge.Edge[i][1])
            color = 'gray'
            linetype ='--'
            if L6 and i == 0:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth*0.5, label=L3, linestyle=linetype)
            else:
                plt.plot([N1[2], N2[2]], [N1[3], N2[3]], color, linewidth=LineWidth)
            xList.append(N1[2])
            xList.append(N2[2])
            yList.append(N1[3])
            yList.append(N2[3])

    MinX = xList[0]
    MaxX = xList[0]
    MinY = yList[0]
    MaxY = yList[0]

    N = len(xList)
    for i in range(N):
        if MinX > xList[i]:
            MinX = xList[i]
        if MaxX < xList[i]:
            MaxX = xList[i]
        if MinY > yList[i]:
            MinY = yList[i]
        if MaxY < yList[i]:
            MaxY = yList[i]

    plt.xlim(MinX - 0.01, MaxX + 0.01)
    plt.ylim(MinY - 0.01, MaxY + 0.01)
    if L1 or L2 or L3:
        plt.legend(fontsize=textsize)

    lim = [[MinX - 0.01, MaxX + 0.01], [MinY - 0.01, MaxY + 0.01] ]

    fig1 = cf.add_subplot(2,1,1)

    textsize = 8
    # plt.title(TITLE, fontsize=textsize+1)
    ylabel = "Lift[mm]"
    xlabel = "Distance from center[m]"
    plt.ylabel(ylabel, fontsize=textsize)
    plt.xlabel(xlabel, fontsize=textsize)
    plt.xticks(size=textsize)
    plt.yticks(size=textsize)
    plt.grid()
    plt.axis("on")
    
    marker='o'
    markersize=3
    c1 = "red"; c2= "blue"; c3="green"; c4="black"; c5="gray"
    N = len(CLift)
    yMin= CLift[0][1][1]
    yMax = CLift[0][1][1]
    for i in range(N):
        M = len(CLift[i])
        Pos = []
        Val = []
        for j in range(1, M):
            Pos.append(CLift[i][j][0])
            Val.append(CLift[i][j][1])
            if yMin > CLift[i][j][1]:
                yMin = CLift[i][j][1]
            if yMax < CLift[i][j][1]:
                yMax = CLift[i][j][1]
            # print CLift[i][0], ',', CLift[i][j][0], ',', CLift[i][j][1]
        if i % 5 == 0:
            iColor = c1
        elif i % 5 == 1:
            iColor = c2
        elif i % 5 == 2:
            iColor = c3
        elif i % 5 == 3:
            iColor = c4
        else:
            iColor = c5

        if int(i / 5) == 0:
            ls = '-'
            lw = 1
        elif int(i / 5) == 1:
            ls = '--'
            lw = 0.5
        elif int(i / 5) == 2:
            ls = '-.'
            lw = 0.25
        else:
            ls = ':'
            lw = 0.1

        plt.plot(Pos, Val, color=iColor, linestyle=ls, linewidth=lw, label=str(CLift[i][0]), marker=marker, markersize=markersize, markeredgecolor='none')
    plt.legend(fontsize=8)
    
    plt.xlim(lim[0][0], lim[0][1])

    if Ymax != 0:
        yMax = Ymax
        yMin = Ymin
        
    if yMin > 0: 
        plt.ylim(0.0, yMax *1.7)
    elif yMax < 0: 
        plt.ylim(yMin*1.05, yMax *0.1)
    else: 
        plt.ylim(yMin*1.05, yMax *1.7)

    plt.savefig(ImageFileName, dpi=dpi)
    plt.clf()

    

########################################################################################################################
########################################################################################################################
########################################################################################################################
if __name__ == "__main__":
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "Start")
    except:
        pass 

    debug = 0

    os.system('rm -f node.txt')
    t0 = time.time()
    Offset = 10000
    Treadno = 10000000

    strJobDir = os.getcwd()
    lstSmartFileNames = glob.glob(strJobDir + '/*.sns')
    strSmartFileName = lstSmartFileNames[0]

    with open(strSmartFileName) as Sns_file:
        lstSnsInfo = json.load(Sns_file)

    # strSimCode = lstSnsInfo["AnalysisInformation"]["SimulationCode"]
    strSimCode = strSmartFileName.split('/')[-1][:-4]      # Simulation Code from 'SNS' file name
    strSimGroup = strSimCode.split('-')[-2]

    strProductLine = lstSnsInfo["VirtualTireBasicInfo"]["ProductLine"]
    TreadDesignWidth = float(lstSnsInfo["VirtualTireParameters"]["TreadDesignWidth"])
    SimulationPressure = []
    SimulationSpeed = []

    ###################################################################################################################
    word = list(strSimCode.split("-"))
    simcode = word[1]+"-"+word[2]+'.inp'
    Node, Element, Elset, Comment = TIRE.Mesh2DInformation(simcode)
    OuterEdge = Element.OuterEdge(Node)
    ProfileEdge=TIRE.EDGE()
    I = len(OuterEdge.Edge)
    for i in range(I):
        if OuterEdge.Edge[i][2] == 'CTB' or OuterEdge.Edge[i][2] == 'SUT' or OuterEdge.Edge[i][2] == 'CTR' or OuterEdge.Edge[i][2] == 'TRW' or OuterEdge.Edge[i][2] == 'BSW' :
            ProfileEdge.Add([OuterEdge.Edge[i][0]%Offset, OuterEdge.Edge[i][1]%Offset, OuterEdge.Edge[i][2], OuterEdge.Edge[i][3], OuterEdge.Edge[i][4] ])
    ###################################################################################################################
    if debug > 0: 
        count = 0 
        BeltEdge = Element.ElsetToEdge("BT1")
        OuterEdge.Combine(BeltEdge)
    

    sdbFileName = ''
    sfricResultFileName = ''
    # errFileName = strSimCode +'.err'
    # err=open(errFileName, 'w')

    TotalSimNoPCR = 12
    TotalSimNoLTR = 6
    TotalSimNoTBR = 2
    subFolderBasicName = 'DP'
    subFolderSerialDigit = '03'
    subFileBasicName = '-DP'
    subFileSerialDigit = '03'
    RimCenter=[0.0, 0.0, 0.0, 0.0]

    subFolderName = subFolderBasicName + '001'
    subFileName = strSimCode + subFileBasicName + '001'
    SmartInpFileName001 = strJobDir + '/' + subFolderName + '/' + subFileName + '.inp'

    SimTime = TIRE.SIMTIME(SmartInpFileName001)
    strResultStep = str(format(SimTime.LastStep, '03'))

    
    NodeOffset = []
    NodeOffset.append(Offset)
    ElementOffset = Offset
    TreadNodeStart = []
    TreadNodeStart.append(Treadno)
    ResultSector = 0  # should find the uppermost section so need all node information
    ResultContactPressure = 81


    Success = 1

    if strProductLine == 'PCR':
        SimulationRuns = 12
    elif strProductLine == 'LTR':
        SimulationRuns = 6
    else:
        SimulationRuns = 2

    for i in range(1, SimulationRuns + 1):
        Serial = str(format(i, subFolderSerialDigit))
        subFolderName = subFolderBasicName + Serial
        Serial = str(format(i, subFileSerialDigit))
        subFileName = strSimCode + subFileBasicName + Serial
        SmartInpFileNames = glob.glob(strJobDir + '/' + subFolderName + '/*.inp')
       
        
        if len(SmartInpFileNames) > 1:
            if 'RND' in SmartInpFileNames[1].split('/')[-1]:
                SmartInpFileName = SmartInpFileNames[1]
            else:
                SmartInpFileName = SmartInpFileNames[0]
        else:
            SmartInpFileName = SmartInpFileNames[0]
        # print SmartInpFileName
        SimConditions = TIRE.CONDITION(SmartInpFileName)
        SimulationPressure.append(SimConditions.Pressure)
        SimulationSpeed.append(SimConditions.FreeSpin)
        
    # print SimulationSpeed    


    ##################################################################################################
    ## DEFORMED SHAPE COMPARISON
    #
    # SurfaceNodePosition1.tmp Data format
    # 313,       1635,       1637, 0.000000E+00,    9.752745E-02,    2.295368E-01, 0.000000E+00,    9.479543E-02,    2.292978E-01, 1
    # faceID,    Node1,     Node2, Node1-Coord1, Node1-Coord2(X), Node1-Coord3(Z), Node2-Coord1, Node2-Coord2(X), Node2-Coord3(Z), OuterSurfaceID (1=Yes, 0=No)
    ##################################################################################################
    SurfacePostionFileName = ['', '', '', '']
    MainBeltPositionFileName = ['', '', '', '']

    ##############################################################################################################################################################################################
    ## Speed CHANGE (The Same Pressure)
    ################################################################################################################################################################################################

    CrownGrowthFileName = strSimCode + '-CrownODExpansion.txt'
    BeltGrowthFilename = strSimCode + '-BeltODExpansionRaw.txt'
    bf = open(BeltGrowthFilename, 'w')

    PrintFileName = strSimCode + '-BeltODExpansion.txt'
    tf = open(PrintFileName, 'w')
    # tline = "Pressure(kgf/cm2)\tVelocity(km/h)\tBelt Center Lift(mm)\tBelt Edge Lift(mm) \n"
    # tf.write(tline)
    tline = "Pressure(kgf/cm2)    Velocity(km/h)    Belt Center Lift(mm)    Belt Edge Lift(mm) \n"
    tf.write(tline)

    f = open(CrownGrowthFileName, 'w')
    textline = '* Nodes on the profile Coordintates\n'
    f.write(textline)
    # textline = '* Distance from Crown Center, OD Expansion[mm]\n'
    # f.write(textline)

    isFile = [0, 0, 0, 0]
    NR = 0
    imagewidth = 8.0
    imageheight = 10.0
    Ymin = 0.0
    Ymax = 0.0
    
    NullNode = TIRE.NODE()
    
    if strProductLine == 'PCR':

        for i in range(1, TotalSimNoPCR + 1):
            Serial = str(format(i, subFolderSerialDigit))
            subFolderName = subFolderBasicName + Serial
            Serial = str(format(i, subFileSerialDigit))
            subFileName = strSimCode + subFileBasicName + Serial

            if SimTime.SimulationTime == 0.0:
                sfricFileName = strJobDir + '/' + subFolderName + '/SFRIC_PCI.' + subFileName + '/' + subFileName + '.sfric'
                strlstSFRICFileName = strJobDir + '/' + subFolderName + '/SFRIC_PCI.' + subFileName + '/' + subFileName + '.sfric' + strResultStep
                SDBFileName = strJobDir + '/' + subFolderName + '/SDB_PCI.' + subFileName + '/' + subFileName + '.sdb'
                strlstSDBFileName = strJobDir + '/' + subFolderName + '/SDB_PCI.' + subFileName + '/' + subFileName + '.sdb' + strResultStep
            else:
                sfricFileName = strJobDir + '/' + subFolderName + '/SFRIC.' + subFileName + '/' + subFileName + '.sfric'
                strlstSFRICFileName = strJobDir + '/' + subFolderName + '/SFRIC.' + subFileName + '/' + subFileName + '.sfric' + strResultStep
                SDBFileName = strJobDir + '/' + subFolderName + '/SDB.' + subFileName + '/' + subFileName + '.sdb'
                strlstSDBFileName = strJobDir + '/' + subFolderName + '/SDB.' + subFileName + '/' + subFileName + '.sdb' + strResultStep
            # print sfricFileName

            if debug > 0:
                if i%4 == 1:    Node1 = TIRE.ResultSDB(SDBFileName, strlstSDBFileName, NodeOffset[0], TreadNodeStart[0], 1, -1)
                if i%4 == 2:    Node2 = TIRE.ResultSDB(SDBFileName, strlstSDBFileName, NodeOffset[0], TreadNodeStart[0], 1, -1)
                if i%4 == 3:    Node3 = TIRE.ResultSDB(SDBFileName, strlstSDBFileName, NodeOffset[0], TreadNodeStart[0], 1, -1)
                if debug == 1 and i%4 ==0: 

                    for n in Node1.Node:
                        n[0] = n[0]%Offset
                    for n in Node2.Node:
                        n[0] = n[0]%Offset
                    for n in Node3.Node:
                        n[0] = n[0]%Offset

                    # TIRE.Plot_EdgeComparison(strSimCode+"-comparison-" + str(count), OuterEdge, Node1, Node2, Node3=Node3,\
                    #                     L1="Speed 1", L2="Speed 2", L3="Speed 3", ls1="-")
                    TIRE.Plot_EdgeComparison(strSimCode+"-comparison-" + str(count), OuterEdge, Node1, Node3, #Node3=Node3,\
                                        L1="Speed 1", L2="Speed 2")
                    count += 1
                    count += 1

            IsFric = os.path.isfile(sfricFileName)
            IsFricResult = os.path.isfile(strlstSFRICFileName)

            if IsFric == True and IsFricResult == True:
                isFile[(i - 1) % 4] = 1
                ResultOption = 1
                TIRE.SFRICResults(sfricFileName, strlstSFRICFileName, ResultOption, ResultSector, NodeOffset[0], TreadNodeStart[0])
                ResultOption = 7
                TIRE.SDBResults(SDBFileName, strlstSDBFileName, ResultOption, ResultSector, NodeOffset[0], ElementOffset, TreadNodeStart[0])
                
                if i % 4 == 1:
                    Rim1 = TIRE.GetRimCenter()
                elif i % 4 == 2:
                    Rim2 = TIRE.GetRimCenter()
                elif i % 4 == 3:
                    Rim3 = TIRE.GetRimCenter()
                else:
                    Rim4 = TIRE.GetRimCenter()
                    
                with open('rigid.tmp') as RIGID:
                    lines = RIGID.readlines()
                for m in range(len(lines)):
                    if '*RIM' in lines[m] :
                        RimCenter[(i-1)%4] = float(lines[m+1].split(',')[3])
                        break


            if i % 4 == 1:
                SurfacePostionFileName[0] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[0] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'
            elif i % 4 == 2:
                SurfacePostionFileName[1] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[1] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'
            elif i % 4 == 3:
                SurfacePostionFileName[2] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[2] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'
            else:
                SurfacePostionFileName[3] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[3] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'

            if i % 4 == 0:
                PR0 = SimulationPressure[i - 4]
                SP0 = SimulationSpeed[i - 4]
                PR1 = SimulationPressure[i - 3]
                SP1 = SimulationSpeed[i - 3]
                PR2 = SimulationPressure[i - 2]
                SP2 = SimulationSpeed[i - 2]
                PR3 = SimulationPressure[i - 1]
                SP3 = SimulationSpeed[i - 1]
                NR = isFile[0] + isFile[1] + isFile[2] + isFile[3]
                
                ImageFileName = strSimCode + '-CrownODExpansionDynamicPress' + str(int(i / 4)) #+ '.png'

                if NR == 4:
                    # textline = '* Speed [km/h]: 0 -> ' + str(SP1) + ' -> ' + str(SP2) + ' -> ' + str(SP3) + '  Pressure: ' + str(PR0) + ' [kgf/cm2]\n'
                    # f.write(textline)
                    SurfaceNodeFiles=[SurfacePostionFileName[0], SurfacePostionFileName[1], SurfacePostionFileName[2], SurfacePostionFileName[3]]
                    Legend1 = 'Value=(Speed '+str(SP1)+') - (Speed'+ str(SP0)+ ') ' +'[Pressure:'+str(PR0)+'kgf/cm2]'
                    Legend2 = 'Value=(Speed '+str(SP2)+') - (Speed'+ str(SP0)+ ') ' +'[Pressure:'+str(PR0)+'kgf/cm2]'
                    Legend3 = 'Value=(Speed '+str(SP3)+') - (Speed'+ str(SP0)+ ') ' +'[Pressure:'+str(PR0)+'kgf/cm2]'
                    ImageProfileName = strSimCode + '-ProfileLift' + str(int(i / 4))

                    resultlist = TIRE.Plot_ProfileLiftForCrownLift(ImageProfileName, SurfaceNodeFiles, TreadDesignWidth, '', \
                                Legend1, Legend2, Legend3, "", "", "Distance From Center[m]", "Lift[mm]", 120 , simcode=strSimCode,\
                                time=SimTime, rim1=Rim1, rim2=Rim2, rim3=Rim3, rim4=Rim4)
                    
                    CrownEdge = resultlist[0]
                    N1  = resultlist[1]
                    N2 = resultlist[2]
                    N3 = resultlist[3]
                    N4 = resultlist[4]
                    
                    MM = len(CrownEdge.Edge)
                    textline = '* Speed [km/h]: 0 -> ' + str(SP1) + ' -> ' + str(SP2) + ' -> ' + str(SP3) + '  Pressure: ' + str(PR0) + ' [kgf/cm2]\n'
                    f.write(textline)
                    for m in range(MM):
                        if m == 0:
                            nn0 = N1.NodeByID(CrownEdge.Edge[m][0])
                            nn1 = N2.NodeByID(CrownEdge.Edge[m][0])
                            nn2 = N3.NodeByID(CrownEdge.Edge[m][0])
                            nn3 = N4.NodeByID(CrownEdge.Edge[m][0])
                            textline = str(CrownEdge.Edge[m][0]) +', ' + str(nn0[1]) + ', ' + str(nn0[2]) + ', '+ str(nn0[3]) + ', , ' + ', ' + str(nn1[1]) + ', ' + str(nn1[2]) + ', '+ str(nn1[3]) + ', , ' + ', ' + str(nn2[1]) + ', ' + str(nn2[2]) + ', '+ str(nn2[3]) + ', , ' + ', ' + str(nn3[1]) + ', ' + str(nn3[2]) + ', '+ str(nn3[3]) + '\n'
                            f.write(textline)
                    
                        nn0 = N1.NodeByID(CrownEdge.Edge[m][1])
                        nn1 = N2.NodeByID(CrownEdge.Edge[m][1])
                        nn2 = N3.NodeByID(CrownEdge.Edge[m][1])
                        nn3 = N4.NodeByID(CrownEdge.Edge[m][1])
                        textline = str(CrownEdge.Edge[m][0]) +', ' + str(nn0[1]) + ', ' + str(nn0[2]) + ', '+ str(nn0[3]) + ', , ' + ', ' + str(nn1[1]) + ', ' + str(nn1[2]) + ', '+ str(nn1[3]) + ', , ' + ', ' + str(nn2[1]) + ', ' + str(nn2[2]) + ', '+ str(nn2[3]) + ', , ' + ', ' + str(nn3[1]) + ', ' + str(nn3[2]) + ', '+ str(nn3[3]) + '\n'
                        f.write(textline)
                        
                    CrownLift = TIRE.Plot_CrownLiftAfterProfileLift(ImageFileName, TreadDesignWidth, CrownEdge, N1, N2, N3, N4, NullNode, NullNode, '', \
                        Legend1, Legend2, Legend3, "", "", "Distance From Center[m]", "Lift[mm]", 120, subplot=1) 
                    ###############################################################################################
                    ## Combined Image
                    ###############################################################################################
                    # print (CrownLift)
                    N = len(CrownLift)
                    yMin= CrownLift[0][1][1]
                    yMax = CrownLift[0][1][1]
                    for i in range(N):
                        M = len(CrownLift[i])
                        for j in range(1, M):
                            if yMin > CrownLift[i][j][1]:
                                yMin = CrownLift[i][j][1]
                            if yMax < CrownLift[i][j][1]:
                                yMax = CrownLift[i][j][1]

                    if Ymax == 0:
                        Ymax = yMax
                        Ymin = yMin

                    Node1 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[0], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    Node2 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[1], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    Node3 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[2], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    Node4 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[3], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    PlotProfile_Lift(ImageFileName, ProfileEdge, CrownLift, n1=Node1, n2=Node2, n3=Node3, n4=Node4, width=imagewidth, height=imageheight, vmin=Ymin, vmax=Ymax)
                    if Ymax < yMax :
                        Ymax = yMax
                    if Ymin > yMin:
                        Ymin = yMin
                    ###############################################################################################

                    # PlotTreadLiftDynamic3(SurfacePostionFileName[0], SurfacePostionFileName[1], SurfacePostionFileName[2], SurfacePostionFileName[3], ImageFileName, 5.0, TreadDesignWidth, SP1, SP2, SP3, PR0, RimCenter)
                    PrintBeltLiftDynamic3(MainBeltPositionFileName[0], MainBeltPositionFileName[1], MainBeltPositionFileName[2], MainBeltPositionFileName[3], SP1, SP2, SP3, PR0, RimCenter)

                   
                else:
                    textline = 'ERROR::POST::DynamicProfile - All the Dynamic Profile Simulations on Pressure ' + str(PR0) + ' were not completed.\n'
                    # err.write(textline)
                    print (textline)
                    Success = 0

                isFile = [0, 0, 0, 0]

    elif strProductLine == 'LTR':
        for i in range(1, TotalSimNoLTR + 1):
            Serial = str(format(i, subFolderSerialDigit))
            subFolderName = subFolderBasicName + Serial
            Serial = str(format(i, subFileSerialDigit))
            subFileName = strSimCode + subFileBasicName + Serial

            if SimTime.SimulationTime == 0.0:
                sfricFileName = strJobDir + '/' + subFolderName + '/SFRIC_PCI.' + subFileName + '/' + subFileName + '.sfric'
                strlstSFRICFileName = strJobDir + '/' + subFolderName + '/SFRIC_PCI.' + subFileName + '/' + subFileName + '.sfric' + strResultStep
                SDBFileName = strJobDir + '/' + subFolderName + '/SDB_PCI.' + subFileName + '/' + subFileName + '.sdb'
                strlstSDBFileName = strJobDir + '/' + subFolderName + '/SDB_PCI.' + subFileName + '/' + subFileName + '.sdb' + strResultStep
            else:
                sfricFileName = strJobDir + '/' + subFolderName + '/SFRIC.' + subFileName + '/' + subFileName + '.sfric'
                strlstSFRICFileName = strJobDir + '/' + subFolderName + '/SFRIC.' + subFileName + '/' + subFileName + '.sfric' + strResultStep
                SDBFileName = strJobDir + '/' + subFolderName + '/SDB.' + subFileName + '/' + subFileName + '.sdb'
                strlstSDBFileName = strJobDir + '/' + subFolderName + '/SDB.' + subFileName + '/' + subFileName + '.sdb' + strResultStep

            IsFric = os.path.isfile(sfricFileName)
            IsFricResult = os.path.isfile(strlstSFRICFileName)

            if IsFric == True and IsFricResult == True:
                isFile[(i - 1) % 3] = 1
                ResultOption = 1
                TIRE.SFRICResults(sfricFileName, strlstSFRICFileName, ResultOption, ResultSector, NodeOffset[0], TreadNodeStart[0])
                ResultOption = 7
                TIRE.SDBResults(SDBFileName, strlstSDBFileName, ResultOption, ResultSector, NodeOffset[0], ElementOffset, TreadNodeStart[0])
                
                
                if i % 3 == 1:
                    Rim1 = TIRE.GetRimCenter()
                elif i % 3 == 2:
                    Rim2 = TIRE.GetRimCenter()
                else:
                    Rim3 = TIRE.GetRimCenter()
                    
                with open('rigid.tmp') as RIGID:
                    lines = RIGID.readlines()
                for m in range(len(lines)):
                    if '*RIM' in lines[m] :
                        RimCenter[(i-1)%3] = float(lines[m+1].split(',')[3])
                        break

            if i % 3 == 1:
                SurfacePostionFileName[0] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[0] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'
            elif i % 3 == 2:
                SurfacePostionFileName[1] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[1] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'
            else:
                SurfacePostionFileName[2] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[2] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'

            if i % 3 == 0:
                PR0 = SimulationPressure[i - 3]
                SP0 = SimulationSpeed[i - 3]
                PR1 = SimulationPressure[i - 2]
                SP1 = SimulationSpeed[i - 2]
                PR2 = SimulationPressure[i - 1]
                SP2 = SimulationSpeed[i - 1]
                NR = isFile[0] + isFile[1] + isFile[2]

                ImageFileName = strSimCode + '-CrownODExpansionDynamicPress' + str(int(i / 3)) #+ '.png'
                if NR == 3:
                    # textline = '* Speed [km/h]: 0 -> ' + str(SP1) + ' -> ' + str(SP2) + '  Pressure: ' + str(PR0) + ' [kgf/cm2]\n'
                    # f.write(textline)
                    SurfaceNodeFiles=[SurfacePostionFileName[0], SurfacePostionFileName[1], SurfacePostionFileName[2]]
                    # TIRE.PrintList(SurfaceNodeFiles)
                    
                    Legend1 = 'Value=(Speed '+str(SP1)+') - (Speed'+ str(SP0)+ ') ' +'[Pressure:'+str(PR0)+'kgf/cm2]'
                    Legend2 = 'Value=(Speed '+str(SP2)+') - (Speed'+ str(SP0)+ ') ' +'[Pressure:'+str(PR0)+'kgf/cm2]'
                    Legend3 = ''
                                                                                    
                                                                                                                                                                                                           
                    
                    
                    ImageProfileName = strSimCode + '-ProfileLift' + str(int(i / 3))
                    resultlist = TIRE.Plot_ProfileLiftForCrownLift(ImageProfileName,SurfaceNodeFiles, TreadDesignWidth, '', Legend1, Legend2, Legend3, "", "", "Distance From Center[m]", "Lift[mm]", 120 , simcode=strSimCode, time=SimTime, rim1=Rim1, rim2=Rim2, rim3=Rim3)
                    
                    CrownEdge = resultlist[0]
                    N1  = resultlist[1]
                    N2 = resultlist[2]
                    N3 = resultlist[3]
                    # N4 = resultlist[4]
                    # TIRE.PrintList(resultlist)
                    
                    MM = len(CrownEdge.Edge)
                    textline = '* Speed [km/h]: 0 -> ' + str(SP1) + ' -> ' + str(SP2) + '  Pressure: ' + str(PR0) + ' [kgf/cm2]\n'
                    f.write(textline)
                    for m in range(MM):
                        if m == 0:
                            nn0 = N1.NodeByID(CrownEdge.Edge[m][0])
                            nn1 = N2.NodeByID(CrownEdge.Edge[m][0])
                            nn2 = N3.NodeByID(CrownEdge.Edge[m][0])
                            textline = str(CrownEdge.Edge[m][0]) +', ' + str(nn0[1]) + ', ' + str(nn0[2]) + ', '+ str(nn0[3]) + ', , ' +', ' + str(nn1[1]) + ', ' + str(nn1[2]) + ', '+ str(nn1[3]) + ', , ' +', ' + str(nn2[1]) + ', ' + str(nn2[2]) + ', '+ str(nn2[3]) + '\n'
                            f.write(textline)
                    
                        nn0 = N1.NodeByID(CrownEdge.Edge[m][1])
                        nn1 = N2.NodeByID(CrownEdge.Edge[m][1])
                        nn2 = N3.NodeByID(CrownEdge.Edge[m][1])
                        textline = str(CrownEdge.Edge[m][0]) +', ' + str(nn0[1]) + ', ' + str(nn0[2]) + ', '+ str(nn0[3]) + ', , ' +', ' + str(nn1[1]) + ', ' + str(nn1[2]) + ', '+ str(nn1[3]) + ', , ' +', ' + str(nn2[1]) + ', ' + str(nn2[2]) + ', '+ str(nn2[3]) + '\n'
                        f.write(textline)
                    
                    
                    
                    
                    CrownLift= TIRE.Plot_CrownLiftAfterProfileLift(ImageFileName, TreadDesignWidth, CrownEdge, N1, N2, N3, NullNode, NullNode, NullNode, '', Legend1, Legend2, Legend3, "", "", "Distance From Center[m]", "Lift[mm]", 120, subplot=1) 
                    ###############################################################################################
                    ## Combined Image
                    ###############################################################################################
                    N = len(CrownLift)
                    yMin= CrownLift[0][1][1]
                    yMax = CrownLift[0][1][1]
                    for i in range(N):
                        M = len(CrownLift[i])
                        for j in range(1, M):
                            if yMin > CrownLift[i][j][1]:
                                yMin = CrownLift[i][j][1]
                            if yMax < CrownLift[i][j][1]:
                                yMax = CrownLift[i][j][1]

                    if Ymax == 0:
                        Ymax = yMax
                        Ymin = yMin
                    Node1 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[0], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    Node2 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[1], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    Node3 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[2], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    PlotProfile_Lift(ImageFileName, ProfileEdge, CrownLift, n1=Node1, n2=Node2, n3=Node3, width=imagewidth, height=imageheight, vmin=Ymin, vmax=Ymax)
                    if Ymax < yMax :
                        Ymax = yMax
                    if Ymin > yMin:
                        Ymin = yMin
                    ###############################################################################################
                    # PlotTreadLiftDynamic2(SurfacePostionFileName[0], SurfacePostionFileName[1], SurfacePostionFileName[2], ImageFileName, 5.0, TreadDesignWidth, SP1, SP2, PR0, RimCenter)
                    PrintBeltLiftDynamic2(MainBeltPositionFileName[0], MainBeltPositionFileName[1], MainBeltPositionFileName[2], SP1, SP2, PR0, RimCenter)

                else:
                    textline = 'ERROR::POST::DynamicProfile - All the Dynamic Profile Simulations on Pressure ' + str(PR0) + ' were not completed.\n'
                    # err.write(textline)
                    print (textline)
                    Success = 0

                isFile = [0, 0, 0, 0]
            
    else:

        for i in range(1, TotalSimNoTBR + 1):
            Serial = str(format(i, subFolderSerialDigit))
            subFolderName = subFolderBasicName + Serial
            Serial = str(format(i, subFileSerialDigit))
            subFileName = strSimCode + subFileBasicName + Serial

            if SimTime.SimulationTime == 0.0:
                sfricFileName = strJobDir + '/' + subFolderName + '/SFRIC_PCI.' + subFileName + '/' + subFileName + '.sfric'
                strlstSFRICFileName = strJobDir + '/' + subFolderName + '/SFRIC_PCI.' + subFileName + '/' + subFileName + '.sfric' + strResultStep
                SDBFileName = strJobDir + '/' + subFolderName + '/SDB_PCI.' + subFileName + '/' + subFileName + '.sdb'
                strlstSDBFileName = strJobDir + '/' + subFolderName + '/SDB_PCI.' + subFileName + '/' + subFileName + '.sdb' + strResultStep
            else:
                sfricFileName = strJobDir + '/' + subFolderName + '/SFRIC.' + subFileName + '/' + subFileName + '.sfric'
                strlstSFRICFileName = strJobDir + '/' + subFolderName + '/SFRIC.' + subFileName + '/' + subFileName + '.sfric' + strResultStep
                SDBFileName = strJobDir + '/' + subFolderName + '/SDB.' + subFileName + '/' + subFileName + '.sdb'
                strlstSDBFileName = strJobDir + '/' + subFolderName + '/SDB.' + subFileName + '/' + subFileName + '.sdb' + strResultStep

            IsFric = os.path.isfile(sfricFileName)
            IsFricResult = os.path.isfile(strlstSFRICFileName)

            if IsFric == True and IsFricResult == True:
                isFile[(i - 1) % 2] = 1
                ResultOption = 1
                TIRE.SFRICResults(sfricFileName, strlstSFRICFileName, ResultOption, ResultSector, NodeOffset[0], TreadNodeStart[0])
                ResultOption = 7
                TIRE.SDBResults(SDBFileName, strlstSDBFileName, ResultOption, ResultSector, NodeOffset[0], ElementOffset, TreadNodeStart[0])
                
                if i % 2 == 1:
                    Rim1 = TIRE.GetRimCenter()
                else:
                    Rim2 = TIRE.GetRimCenter()
                
                with open('rigid.tmp') as RIGID:
                    lines = RIGID.readlines()
                for m in range(len(lines)):
                    if '*RIM' in lines[m] :
                        RimCenter[(i-1)%2] = float(lines[m+1].split(',')[3])
                        break

            if i % 2 == 1:
                SurfacePostionFileName[0] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[0] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'
            else:
                SurfacePostionFileName[1] = strJobDir + '/' + subFileName + '-SurfaceNodePosition.tmp'
                MainBeltPositionFileName[1] = strJobDir + '/' + subFileName + '-DynamicProfileBeltCoord.tmp'

            if i % 2 == 0:
                PR0 = SimulationPressure[i - 2]
                SP0 = SimulationSpeed[i - 2]
                PR1 = SimulationPressure[i - 1]
                SP1 = SimulationSpeed[i - 1]
                NR = isFile[0] + isFile[1]

                ImageFileName = strSimCode + '-CrownODExpansionDynamicPress' + str(int(i / 2)) #+ '.png'
                if NR == 2:
                    # textline = '* Speed [km/h]: 0 -> ' + str(SP1) + '  Pressure: ' + str(PR0) + ' [kgf/cm2]\n'
                    # f.write(textline)
                    SurfaceNodeFiles=[SurfacePostionFileName[0], SurfacePostionFileName[1]]
                    # TIRE.PrintList(SurfaceNodeFiles)
                    
                    Legend1 = 'Value=(Speed '+str(SP1)+') - (Speed'+ str(SP0)+ ') ' +'[Pressure:'+str(PR0)+'kgf/cm2]'
                    Legend2 = ''
                    Legend3 = ''
                                                                                    
                                                                                                                                                                                                           
                    
                    ImageProfileName = strSimCode + '-ProfileLift' + str(int(i / 2))
                    resultlist = TIRE.Plot_ProfileLiftForCrownLift(ImageProfileName,SurfaceNodeFiles, TreadDesignWidth, '', Legend1, Legend2, Legend3, "", "", "Distance From Center[m]", "Lift[mm]", 120 ,simcode=strSimCode, time=SimTime, rim1=Rim1, rim2=Rim2)
                    
                    CrownEdge = resultlist[0]
                    N1  = resultlist[1]
                    N2 = resultlist[2]
                    
                    MM = len(CrownEdge.Edge)
                    textline = '* Speed [km/h]: 0 -> ' + str(SP1) + '  Pressure: ' + str(PR0) + ' [kgf/cm2]\n'
                    f.write(textline)
                    for m in range(MM):
                        if m == 0:
                            nn0 = N1.NodeByID(CrownEdge.Edge[m][0])
                            nn1 = N2.NodeByID(CrownEdge.Edge[m][0])
                            textline = str(CrownEdge.Edge[m][0]) +', ' + str(nn0[1]) + ', ' + str(nn0[2]) + ', '+ str(nn0[3]) + ', , ' +', ' + str(nn1[1]) + ', ' + str(nn1[2]) + ', '+ str(nn1[3]) + '\n'
                            f.write(textline)
                    
                        nn0 = N1.NodeByID(CrownEdge.Edge[m][1])
                        nn1 = N2.NodeByID(CrownEdge.Edge[m][1])
                        textline = str(CrownEdge.Edge[m][0]) +', ' + str(nn0[1]) + ', ' + str(nn0[2]) + ', '+ str(nn0[3]) + ', , '  +', ' + str(nn1[1]) + ', ' + str(nn1[2]) + ', '+ str(nn1[3]) + '\n'
                        f.write(textline)
                    
                    
                    CrownLift = TIRE.Plot_CrownLiftAfterProfileLift(ImageFileName, TreadDesignWidth, CrownEdge, N1, N2, NullNode, NullNode, NullNode, NullNode, '', Legend1, Legend2, Legend3, "", "", "Distance From Center[m]", "Lift[mm]", 120, subplot=1) 
                    ###############################################################################################
                    ## Combined Image
                    ###############################################################################################
                    N = len(CrownLift)
                    yMin= CrownLift[0][1][1]
                    yMax = CrownLift[0][1][1]
                    for i in range(N):
                        M = len(CrownLift[i])
                        for j in range(1, M):
                            if yMin > CrownLift[i][j][1]:
                                yMin = CrownLift[i][j][1]
                            if yMax < CrownLift[i][j][1]:
                                yMax = CrownLift[i][j][1]

                    if Ymax == 0:
                        Ymax = yMax
                        Ymin = yMin

                    Node1 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[0], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    Node2 = TIRE.GetDeformedNodeFromSFRIC(SurfaceNodeFiles[1], SimTime, ResultSector =1001, Step=0, Offset=Offset, TreadNo = Treadno)
                    PlotProfile_Lift(ImageFileName, ProfileEdge, CrownLift, n1=Node1, n2=Node2, width=imagewidth, height=imageheight, vmin=Ymin, vmax=Ymax)
                    if Ymax < yMax :
                        Ymax = yMax
                    if Ymin > yMin:
                        Ymin = yMin
                    ###############################################################################################
                    # PlotTreadLiftDynamic1(SurfacePostionFileName[0], SurfacePostionFileName[1], ImageFileName, 5.0, TreadDesignWidth, SP1, PR0, RimCenter)
                    PrintBeltLiftDynamic1(MainBeltPositionFileName[0], MainBeltPositionFileName[1], SP1, PR0, RimCenter)

                else:
                    textline = 'ERROR::POST::DynamicProfile - All the Dynamic Profile Simulations on Pressure ' + str(PR0) + ' were not completed.\n'
                    # err.write(textline)
                    print (textline)
                    Success = 0

                isFile = [0, 0, 0, 0]

    if Success == 1:
        # err.write("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!\n")
        tf.write("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!\n")
    else:
        # err.write("ERROR::POST::[Simulation Result] No Results \n")
        tf.write("ERROR::POST::[Simulation Result] No Results \n")
    f.write("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!\n")
    bf.write("\nSuccess::Post::[Simulation Result] This simulation result was created successfully!!\n")
    
    f.close()
    tf.close()
    bf.close()
    # err.close()
    t1 = time.time()
    os.system('rm -f *.tmp')
    print ("Duration :", t1 - t0, "sec")
    try:
        CheckExecution.getProgramTime(str(sys.argv[0]), "End")
    except:
        pass 





