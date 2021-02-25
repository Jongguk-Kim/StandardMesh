
try:
    import CommonFunction as TIRE
except: 
    import CommonFunction_v2_0 as TIRE

import glob, os, sys, json, time


if __name__ == "__main__":
    try:
        strJobDir = os.getcwd()
        lstSmartFileNames = glob.glob(strJobDir + '/*.sns')
        strSnsFileName = lstSmartFileNames[0]
        strSnsFileName = strSnsFileName.split("/")[-1]
        lstSnsfilename = strSnsFileName.split("-")
        str2DInp = lstSnsfilename[1] +"-" +  lstSnsfilename[2] + ".inp"
        

        doewdir =  os.getcwd()
        namedoewdir = doewdir.split("-")
        namedoewdir[-3] = "0"
        namedoewdir[-5] = "0/"+ namedoewdir[-5].split("/")[1] 
        dirname = ""
        for name in namedoewdir:
            dirname += name + "-"
        dirname = dirname[:-1]

        tmp=str2DInp.split("/")[-1]
        tmp = tmp.split("-")
        DoeBase2DInp = dirname +"/" + tmp[0] + "-0.inp"

        Node, Element, Elset, Comment = TIRE.Mesh2DInformation(str2DInp)
        baseNode, baseElement, baseElset, baseComment = TIRE.Mesh2DInformation(DoeBase2DInp)
        imagename = str2DInp[:-4]+"-DOELayoutCompare.png"

        TIRE.Plot_LayoutCompare(imagename, L1="Base Model", N1=baseNode, E1=baseElement, L2="Generated Model", N2=Node, E2=Element, dpi=150)
    except:
        pass