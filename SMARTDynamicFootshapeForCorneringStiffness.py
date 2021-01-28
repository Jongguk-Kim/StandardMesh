# *******************************************************************
# Contact Characteristic Extraction Code for SMART
# Pilot Version for SLM                : 2017.04.18 by KSH
#     - Footprint characteristics addition for SMART
#     - This code has been modified to calculate property values for each rib by DJ PARK (2019.06.01)
# *******************************************************************
# *******************************************************************
#    Import library
# *******************************************************************
import matplotlib as mpl
mpl.use('Agg')
import warnings
warnings.filterwarnings('ignore') 
import os, glob, json, CheckExecution
import sys, string, struct, math, decimal
import matplotlib.pyplot as plt
import numpy as np
import array as arr
from matplotlib import mlab, cm
from matplotlib.ticker import FormatStrFormatter
from math import *
# *******************************************************************
#    Input Information 
# *******************************************************************
def func(x, a, b, c, d, e, f, g):
    return a*x**6 + b*x**5 + c*x**4 + d*x**3 + e*x**2 + f*x + g
def Division():
	Xspan = 200; Yspan = 200
	return Xspan, Yspan
# *******************************************************************
# *******************************************************************
#       Common function definition
# *******************************************************************
#Distance Calculation of two points
def Distance(fx,fy,fz,lx,ly,lz):
	xd = lx-fx
	yd = ly-fy
	zd = lz-fz
	dist = math.sqrt(xd*xd + yd*yd +zd*zd)
	return dist
def BinarySearch(NODE, tmpNode, low, high):
	mid = 0
	m = 0
	while low<=high:
		m = low+high
		m = m/2
		if tmpNode < NODE.nodelabel[m]:
			high = m-1
		elif tmpNode > NODE.nodelabel[m]:
			low = m+1
		else:
			mid = m
			return mid
	return -1
def AreaFunction(SURF, i, bnd):
	#Node1 --> 1-4 , 1-2
	if SURF.node1P[i]>=bnd and SURF.node2P[i]<bnd and SURF.node3P[i]<bnd and SURF.node4P[i]<bnd:
		Dist = Distance(SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i],SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i])
		Leng = Dist*(bnd-SURF.node2P[i])/(SURF.node1P[i]-SURF.node2P[i])
		XX1   = SURF.node1X[i]+(SURF.node2X[i]-SURF.node1X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node1Y[i]+(SURF.node2Y[i]-SURF.node1Y[i])*(Dist-Leng)/Dist
		Dist = Distance(SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i],SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i])
		Leng = Dist*(bnd-SURF.node4P[i])/(SURF.node1P[i]-SURF.node4P[i])
		XX2   = SURF.node1X[i]+(SURF.node4X[i]-SURF.node1X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node1Y[i]+(SURF.node4Y[i]-SURF.node1Y[i])*(Dist-Leng)/Dist
		AREA  = 0.5*math.fabs(XX1*SURF.node1Y[i]+SURF.node1X[i]*YY2+XX2*YY1-SURF.node1X[i]*YY1-XX2*SURF.node1Y[i]-XX1*YY2)
		return AREA
	#Node2 --> 2-1 , 2-3
	elif SURF.node1P[i]<bnd and SURF.node2P[i]>=bnd and SURF.node3P[i]<bnd and SURF.node4P[i]<bnd:
		Dist = Distance(SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i],SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i])
		Leng = Dist*(bnd-SURF.node1P[i])/(SURF.node2P[i]-SURF.node1P[i])
		XX1   = SURF.node2X[i]+(SURF.node1X[i]-SURF.node2X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node2Y[i]+(SURF.node1Y[i]-SURF.node2Y[i])*(Dist-Leng)/Dist
		Dist = Distance(SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i],SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i])
		Leng = Dist*(bnd-SURF.node3P[i])/(SURF.node2P[i]-SURF.node3P[i])
		XX2   = SURF.node2X[i]+(SURF.node3X[i]-SURF.node2X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node2Y[i]+(SURF.node3Y[i]-SURF.node2Y[i])*(Dist-Leng)/Dist
		AREA  = 0.5*math.fabs(XX1*SURF.node2Y[i]+SURF.node2X[i]*YY2+XX2*YY1-SURF.node2X[i]*YY1-XX2*SURF.node2Y[i]-XX1*YY2)
		return AREA
	#Node3 --> 3-2 , 3-4
	elif SURF.node1P[i]<bnd and SURF.node2P[i]<bnd and SURF.node3P[i]>=bnd and SURF.node4P[i]<bnd:
		Dist = Distance(SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i],SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i])
		Leng = Dist*(bnd-SURF.node2P[i])/(SURF.node3P[i]-SURF.node2P[i])
		XX1   = SURF.node3X[i]+(SURF.node2X[i]-SURF.node3X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node3Y[i]+(SURF.node2Y[i]-SURF.node3Y[i])*(Dist-Leng)/Dist
		Dist = Distance(SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i],SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i])
		Leng = Dist*(bnd-SURF.node4P[i])/(SURF.node3P[i]-SURF.node4P[i])
		XX2   = SURF.node3X[i]+(SURF.node4X[i]-SURF.node3X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node3Y[i]+(SURF.node4Y[i]-SURF.node3Y[i])*(Dist-Leng)/Dist
		AREA  = 0.5*math.fabs(XX1*SURF.node3Y[i]+SURF.node3X[i]*YY2+XX2*YY1-SURF.node3X[i]*YY1-XX2*SURF.node3Y[i]-XX1*YY2)
		return AREA
	#Node4 --> 4-3 , 4-1
	elif SURF.node1P[i]<bnd and SURF.node2P[i]<bnd and SURF.node3P[i]<bnd and SURF.node4P[i]>=bnd:
		Dist = Distance(SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i],SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i])
		Leng = Dist*(bnd-SURF.node1P[i])/(SURF.node4P[i]-SURF.node1P[i])
		XX1   = SURF.node4X[i]+(SURF.node1X[i]-SURF.node4X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node4Y[i]+(SURF.node1Y[i]-SURF.node4Y[i])*(Dist-Leng)/Dist
		Dist = Distance(SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i],SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i])
		Leng = Dist*(bnd-SURF.node3P[i])/(SURF.node4P[i]-SURF.node3P[i])
		XX2   = SURF.node4X[i]+(SURF.node3X[i]-SURF.node4X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node4Y[i]+(SURF.node3Y[i]-SURF.node4Y[i])*(Dist-Leng)/Dist
		AREA  = 0.5*math.fabs(XX1*SURF.node4Y[i]+SURF.node4X[i]*YY2+XX2*YY1-SURF.node4X[i]*YY1-XX2*SURF.node4Y[i]-XX1*YY2)
		return AREA
	#Node1 Node2 --> 1-4 , 2-3
	elif SURF.node1P[i]>=bnd and SURF.node2P[i]>=bnd and SURF.node3P[i]<bnd and SURF.node4P[i]<bnd:
		Dist = Distance(SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i],SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i])
		Leng = Dist*(bnd-SURF.node4P[i])/(SURF.node1P[i]-SURF.node4P[i])
		XX1   = SURF.node1X[i]+(SURF.node4X[i]-SURF.node1X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node1Y[i]+(SURF.node4Y[i]-SURF.node1Y[i])*(Dist-Leng)/Dist
		Dist  = Distance(SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i],SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i])
		Leng  = Dist*(bnd-SURF.node3P[i])/(SURF.node2P[i]-SURF.node3P[i])
		XX2   = SURF.node2X[i]+(SURF.node3X[i]-SURF.node2X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node2Y[i]+(SURF.node3Y[i]-SURF.node2Y[i])*(Dist-Leng)/Dist
		Foward= XX1*SURF.node1Y[i]+SURF.node1X[i]*SURF.node2Y[i]+SURF.node2X[i]*YY2+XX2*YY1
		Baward= SURF.node1X[i]*YY1+SURF.node2X[i]*SURF.node1Y[i]+XX2*SURF.node2Y[i]+XX1*YY2
		AREA  = 0.5*math.fabs(Foward - Baward)
		return AREA
	#Node2 Node3 --> 2-1 , 3-4
	elif SURF.node1P[i]<bnd and SURF.node2P[i]>=bnd and SURF.node3P[i]>=bnd and SURF.node4P[i]<bnd:
		Dist = Distance(SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i],SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i])
		Leng = Dist*(bnd-SURF.node1P[i])/(SURF.node2P[i]-SURF.node1P[i])
		XX1   = SURF.node2X[i]+(SURF.node1X[i]-SURF.node2X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node2Y[i]+(SURF.node1Y[i]-SURF.node2Y[i])*(Dist-Leng)/Dist
		Dist  = Distance(SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i],SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i])
		Leng  = Dist*(bnd-SURF.node4P[i])/(SURF.node3P[i]-SURF.node4P[i])
		XX2   = SURF.node3X[i]+(SURF.node4X[i]-SURF.node3X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node3Y[i]+(SURF.node4Y[i]-SURF.node3Y[i])*(Dist-Leng)/Dist
		Foward= XX1*SURF.node2Y[i]+SURF.node2X[i]*SURF.node3Y[i]+SURF.node3X[i]*YY2+XX2*YY1
		Baward= SURF.node2X[i]*YY1+SURF.node3X[i]*SURF.node2Y[i]+XX2*SURF.node3Y[i]+XX1*YY2
		AREA  = 0.5*math.fabs(Foward - Baward)
		return AREA
	#Node3 Node4 --> 3-2 , 4-1
	elif SURF.node1P[i]<bnd and SURF.node2P[i]<bnd and SURF.node3P[i]>=bnd and SURF.node4P[i]>=bnd:
		Dist = Distance(SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i],SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i])
		Leng = Dist*(bnd-SURF.node2P[i])/(SURF.node3P[i]-SURF.node2P[i])
		XX1   = SURF.node3X[i]+(SURF.node2X[i]-SURF.node3X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node3Y[i]+(SURF.node2Y[i]-SURF.node3Y[i])*(Dist-Leng)/Dist
		Dist  = Distance(SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i],SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i])
		Leng  = Dist*(bnd-SURF.node1P[i])/(SURF.node4P[i]-SURF.node1P[i])
		XX2   = SURF.node4X[i]+(SURF.node1X[i]-SURF.node4X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node4Y[i]+(SURF.node1Y[i]-SURF.node4Y[i])*(Dist-Leng)/Dist
		Foward= XX1*SURF.node3Y[i]+SURF.node3X[i]*SURF.node4Y[i]+SURF.node4X[i]*YY2+XX2*YY1
		Baward= SURF.node3X[i]*YY1+SURF.node4X[i]*SURF.node3Y[i]+XX2*SURF.node4Y[i]+XX1*YY2
		AREA  = 0.5*math.fabs(Foward - Baward)
		return AREA
	#Node4 Node1 --> 4-3 , 1-2
	elif SURF.node1P[i]>=bnd and SURF.node2P[i]<bnd and SURF.node3P[i]<bnd and SURF.node4P[i]>=bnd:
		Dist = Distance(SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i],SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i])
		Leng = Dist*(bnd-SURF.node3P[i])/(SURF.node4P[i]-SURF.node3P[i])
		XX1   = SURF.node4X[i]+(SURF.node3X[i]-SURF.node4X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node4Y[i]+(SURF.node3Y[i]-SURF.node4Y[i])*(Dist-Leng)/Dist
		Dist  = Distance(SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i],SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i])
		Leng  = Dist*(bnd-SURF.node2P[i])/(SURF.node1P[i]-SURF.node2P[i])
		XX2   = SURF.node1X[i]+(SURF.node2X[i]-SURF.node1X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node1Y[i]+(SURF.node2Y[i]-SURF.node1Y[i])*(Dist-Leng)/Dist
		Foward= XX1*SURF.node4Y[i]+SURF.node4X[i]*SURF.node1Y[i]+SURF.node1X[i]*YY2+XX2*YY1
		Baward= SURF.node4X[i]*YY1+SURF.node1X[i]*SURF.node4Y[i]+XX2*SURF.node1Y[i]+XX1*YY2
		AREA  = 0.5*math.fabs(Foward - Baward)
		return AREA
	#Node1 Node2 Node3 --> 1-4 , 3-4
	elif SURF.node1P[i]>=bnd and SURF.node2P[i]>=bnd and SURF.node3P[i]>=bnd and SURF.node4P[i]<bnd:
		Dist = Distance(SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i],SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i])
		Leng = Dist*(bnd-SURF.node4P[i])/(SURF.node1P[i]-SURF.node4P[i])
		XX1   = SURF.node1X[i]+(SURF.node4X[i]-SURF.node1X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node1Y[i]+(SURF.node4Y[i]-SURF.node1Y[i])*(Dist-Leng)/Dist
		Dist  = Distance(SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i],SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i])
		Leng  = Dist*(bnd-SURF.node4P[i])/(SURF.node3P[i]-SURF.node4P[i])
		XX2   = SURF.node3X[i]+(SURF.node4X[i]-SURF.node3X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node3Y[i]+(SURF.node4Y[i]-SURF.node3Y[i])*(Dist-Leng)/Dist
		Foward= XX1*SURF.node1Y[i]+SURF.node1X[i]*SURF.node2Y[i]+SURF.node2X[i]*SURF.node3Y[i]+SURF.node3X[i]*YY2+XX2*YY1
		Baward= SURF.node1X[i]*YY1+SURF.node2X[i]*SURF.node1Y[i]+SURF.node3X[i]*SURF.node2Y[i]+XX2*SURF.node3Y[i]+XX1*YY2
		AREA  = 0.5*math.fabs(Foward - Baward)
		return AREA
	#Node2 Node3 Node4 --> 2-1 , 4-1
	elif SURF.node1P[i]<bnd and SURF.node2P[i]>=bnd and SURF.node3P[i]>=bnd and SURF.node4P[i]>=bnd:
		Dist = Distance(SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i],SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i])
		Leng = Dist*(bnd-SURF.node1P[i])/(SURF.node2P[i]-SURF.node1P[i])
		XX1   = SURF.node2X[i]+(SURF.node1X[i]-SURF.node2X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node2Y[i]+(SURF.node1Y[i]-SURF.node2Y[i])*(Dist-Leng)/Dist
		Dist  = Distance(SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i],SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i])
		Leng  = Dist*(bnd-SURF.node1P[i])/(SURF.node4P[i]-SURF.node1P[i])
		XX2   = SURF.node4X[i]+(SURF.node1X[i]-SURF.node4X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node4Y[i]+(SURF.node1Y[i]-SURF.node4Y[i])*(Dist-Leng)/Dist
		Foward= XX1*SURF.node2Y[i]+SURF.node2X[i]*SURF.node3Y[i]+SURF.node3X[i]*SURF.node4Y[i]+SURF.node4X[i]*YY2+XX2*YY1
		Baward= SURF.node2X[i]*YY1+SURF.node3X[i]*SURF.node2Y[i]+SURF.node4X[i]*SURF.node3Y[i]+XX2*SURF.node4Y[i]+XX1*YY2
		AREA  = 0.5*math.fabs(Foward - Baward)
		return AREA
	#Node3 Node4 Node1 --> 3-2 , 1-2
	elif SURF.node1P[i]>=bnd and SURF.node2P[i]<bnd and SURF.node3P[i]>=bnd and SURF.node4P[i]>=bnd:
		Dist = Distance(SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i],SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i])
		Leng = Dist*(bnd-SURF.node2P[i])/(SURF.node3P[i]-SURF.node2P[i])
		XX1   = SURF.node3X[i]+(SURF.node2X[i]-SURF.node3X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node3Y[i]+(SURF.node2Y[i]-SURF.node3Y[i])*(Dist-Leng)/Dist
		Dist  = Distance(SURF.node1X[i],SURF.node1Y[i],SURF.node1Z[i],SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i])
		Leng  = Dist*(bnd-SURF.node2P[i])/(SURF.node1P[i]-SURF.node2P[i])
		XX2   = SURF.node1X[i]+(SURF.node2X[i]-SURF.node1X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node1Y[i]+(SURF.node2Y[i]-SURF.node1Y[i])*(Dist-Leng)/Dist
		Foward= XX1*SURF.node3Y[i]+SURF.node3X[i]*SURF.node4Y[i]+SURF.node4X[i]*SURF.node1Y[i]+SURF.node1X[i]*YY2+XX2*YY1
		Baward= SURF.node3X[i]*YY1+SURF.node4X[i]*SURF.node3Y[i]+SURF.node1X[i]*SURF.node4Y[i]+XX2*SURF.node1Y[i]+XX1*YY2
		AREA  = 0.5*math.fabs(Foward - Baward)
		return AREA
	#Node4 Node1 Node2 --> 4-3 , 2-3
	elif SURF.node1P[i]>=bnd and SURF.node2P[i]>=bnd and SURF.node3P[i]<bnd and SURF.node4P[i]>=bnd:
		Dist = Distance(SURF.node4X[i],SURF.node4Y[i],SURF.node4Z[i],SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i])
		Leng = Dist*(bnd-SURF.node3P[i])/(SURF.node4P[i]-SURF.node3P[i])
		XX1   = SURF.node4X[i]+(SURF.node3X[i]-SURF.node4X[i])*(Dist-Leng)/Dist
		YY1   = SURF.node4Y[i]+(SURF.node3Y[i]-SURF.node4Y[i])*(Dist-Leng)/Dist
		Dist  = Distance(SURF.node2X[i],SURF.node2Y[i],SURF.node2Z[i],SURF.node3X[i],SURF.node3Y[i],SURF.node3Z[i])
		Leng  = Dist*(bnd-SURF.node3P[i])/(SURF.node2P[i]-SURF.node3P[i])
		XX2   = SURF.node2X[i]+(SURF.node3X[i]-SURF.node2X[i])*(Dist-Leng)/Dist
		YY2   = SURF.node2Y[i]+(SURF.node3Y[i]-SURF.node2Y[i])*(Dist-Leng)/Dist
		Foward= XX1*SURF.node4Y[i]+SURF.node4X[i]*SURF.node1Y[i]+SURF.node1X[i]*SURF.node2Y[i]+SURF.node2X[i]*YY2+XX2*YY1
		Baward= SURF.node4X[i]*YY1+SURF.node1X[i]*SURF.node4Y[i]+SURF.node2X[i]*SURF.node1Y[i]+XX2*SURF.node2Y[i]+XX1*YY2
		AREA  = 0.5*math.fabs(Foward - Baward)
		return AREA
	else:
		return 0
#Interpolate Function to find the surface position of (x, y) and the interpolated pressure
def InterpolateFunction(SURF, x, y, KKK, JJJ):
	m = 0; n = 0; i = 0
	error = 0.001
	while i<len(SURF.surflabel):
		###################################################################################
		## In case of Triangle element, 
		## 1st, we have to check whether (x,y) is in Triangle element or not
		## 2nd, calculate (s,t) by using isoparametric equation
		## 3rd, calculate press by using P = a1 + a2*s + a3*t + a4*s*t equ.
		###################################################################################
		if SURF.node3[i] == SURF.node4[i]:
			no1 = (SURF.node1X[i]-x)*(SURF.node3Y[i]-y)-(SURF.node3X[i]-x)*(SURF.node1Y[i]-y)
			no2 = (SURF.node3X[i]-x)*(SURF.node2Y[i]-y)-(SURF.node2X[i]-x)*(SURF.node3Y[i]-y)
			no3 = (SURF.node2X[i]-x)*(SURF.node1Y[i]-y)-(SURF.node1X[i]-x)*(SURF.node2Y[i]-y)
			if no1 <= 0.0 and no2 <= 0.0 and no3 <= 0.0:
				#(x,y) is in this SURF without condition.
				#so P have to return
				#print "inner"
				#print x, y
				#print SURF.surflabel[i],SURF.node1[i], SURF.node2[i], SURF.node3[i]
				a1 = 0.25*( SURF.node1X[i]+SURF.node2X[i]+SURF.node3X[i]+SURF.node4X[i])
				a2 = 0.25*(-SURF.node1X[i]+SURF.node2X[i]+SURF.node3X[i]-SURF.node4X[i])
				a3 = 0.25*(-SURF.node1X[i]-SURF.node2X[i]+SURF.node3X[i]+SURF.node4X[i])
				a4 = 0.25*( SURF.node1X[i]-SURF.node2X[i]+SURF.node3X[i]-SURF.node4X[i])
				a5 = 0.25*( SURF.node1Y[i]+SURF.node2Y[i]+SURF.node3Y[i]+SURF.node4Y[i])
				a6 = 0.25*(-SURF.node1Y[i]+SURF.node2Y[i]+SURF.node3Y[i]-SURF.node4Y[i])
				a7 = 0.25*(-SURF.node1Y[i]-SURF.node2Y[i]+SURF.node3Y[i]+SURF.node4Y[i])
				a8 = 0.25*( SURF.node1Y[i]-SURF.node2Y[i]+SURF.node3Y[i]-SURF.node4Y[i])
				A = a4*a7 - a3*a8
				B = a2*a7 + a8*(x-a1) - a6*a3 - a4*(y-a5)
				C = a6*(x-a1) - a2*(y-a5)
				det = B*B-4*A*C
				#        print A, B, C, det
				#1
				if det > 0.0:
					t = (-B+math.sqrt(det))/(2*A)
					s = (x - a1 -a3*t)/(a2 + a4*t)
					err_t = math.fabs(t) - 1.0
					err_s = math.fabs(s) - 1.0
					#2
					if err_t <= error and err_s <= error:
						a1 = 0.25*( SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
						a2 = 0.25*(-SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
						a3 = 0.25*(-SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
						a4 = 0.25*( SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
						P = a1 + a2*s + a3*t + a4*s*t
						return P, i
					#2
					if math.fabs(t) > 1.0+error :
						t = (-B-math.sqrt(det))/(2*A)
						s = (x - a1 -a3*t)/(a2 + a4*t)
						err_t = math.fabs(t) - 1.0
						err_s = math.fabs(s) - 1.0
						#3
						if err_t <= error and err_s <= error:
							a1 = 0.25*( SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
							a2 = 0.25*(-SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
							a3 = 0.25*(-SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
							a4 = 0.25*( SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
							P = a1 + a2*s + a3*t + a4*s*t
							return P, i
						#3
						if math.fabs(t) > 1.0+error :
							#4
							if math.fabs(A) < 1.0e-12:
								t = -C/B
								err_t = math.fabs(t) - 1.0
								#5
								if err_t <= error:
									if math.fabs(a2+a4*t) == 0.0 : s = (y - a5 - a7*t)/(a6 +a8*t)
									else: s = (x - a1 -a3*t)/(a2 + a4*t)
									err_s = math.fabs(s) - 1.0
									if err_s <= error:
										a1 = 0.25*( SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
										a2 = 0.25*(-SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
										a3 = 0.25*(-SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
										a4 = 0.25*( SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
										P = a1 + a2*s + a3*t + a4*s*t
										return P, i
		###################################################################################
		## In case of Quad element, 
		###################################################################################
		maxX=SURF.node1X[i];minX=SURF.node1X[i];maxY=SURF.node1Y[i];minY=SURF.node1Y[i]
		if SURF.node2X[i]>=maxX: maxX=SURF.node2X[i]
		if SURF.node3X[i]>=maxX: maxX=SURF.node3X[i]
		if SURF.node4X[i]>=maxX: maxX=SURF.node4X[i]
		if SURF.node2X[i]<minX: minX=SURF.node2X[i]
		if SURF.node3X[i]<minX: minX=SURF.node3X[i]
		if SURF.node4X[i]<minX: minX=SURF.node4X[i]
		if SURF.node2Y[i]>=maxY: maxY=SURF.node2Y[i]
		if SURF.node3Y[i]>=maxY: maxY=SURF.node3Y[i]
		if SURF.node4Y[i]>=maxY: maxY=SURF.node4Y[i]
		if SURF.node2Y[i]<minY: minY=SURF.node2Y[i]
		if SURF.node3Y[i]<minY: minY=SURF.node3Y[i]
		if SURF.node4Y[i]<minY: minY=SURF.node4Y[i]
		# if x >0.047 and x < 0.048 and y > 0.086 and y < 0.087:
		# 	print SURF.surflabel[i]
		if x<=maxX and x>=minX and y<=maxY and y>=minY and SURF.node3[i]!=SURF.node4[i]:
			a1 = 0.25*( SURF.node1X[i]+SURF.node2X[i]+SURF.node3X[i]+SURF.node4X[i])
			a2 = 0.25*(-SURF.node1X[i]+SURF.node2X[i]+SURF.node3X[i]-SURF.node4X[i])
			a3 = 0.25*(-SURF.node1X[i]-SURF.node2X[i]+SURF.node3X[i]+SURF.node4X[i])
			a4 = 0.25*( SURF.node1X[i]-SURF.node2X[i]+SURF.node3X[i]-SURF.node4X[i])
			a5 = 0.25*( SURF.node1Y[i]+SURF.node2Y[i]+SURF.node3Y[i]+SURF.node4Y[i])
			a6 = 0.25*(-SURF.node1Y[i]+SURF.node2Y[i]+SURF.node3Y[i]-SURF.node4Y[i])
			a7 = 0.25*(-SURF.node1Y[i]-SURF.node2Y[i]+SURF.node3Y[i]+SURF.node4Y[i])
			a8 = 0.25*( SURF.node1Y[i]-SURF.node2Y[i]+SURF.node3Y[i]-SURF.node4Y[i])
			A = a4*a7 - a3*a8
			B = a2*a7 + a8*(x-a1) - a6*a3 - a4*(y-a5)
			C = a6*(x-a1) - a2*(y-a5)
			det = B*B-4*A*C
			#print SURF.surflabel[i], SURF.node1[i], SURF.node2[i], SURF.node3[i], SURF.node4[i] 
			#print A, B, C, det
			#1
			if det > 0.0:
				t = (-B+math.sqrt(det))/(2*A)
				s = (x - a1 -a3*t)/(a2 + a4*t)
				err_t = math.fabs(t) - 1.0
				err_s = math.fabs(s) - 1.0
				#2
				if err_t <= error and err_s <= error:
					a1 = 0.25*( SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
					a2 = 0.25*(-SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
					a3 = 0.25*(-SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
					a4 = 0.25*( SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
					P = a1 + a2*s + a3*t + a4*s*t
					return P, i
				#2
				if math.fabs(t) > 1.0+error :
					#print SURF.surflabel[i]
					#print B, det, A
					#print x, y
					t = (-B-math.sqrt(det))/(2*A)
					#print t, a2, a4, (a2+a4*t)
					s = (x - a1 -a3*t)/(a2 + a4*t)
					err_t = math.fabs(t) - 1.0
					err_s = math.fabs(s) - 1.0
					#3
					if err_t <= error and err_s <= error:
						a1 = 0.25*( SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
						a2 = 0.25*(-SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
						a3 = 0.25*(-SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
						a4 = 0.25*( SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
						P = a1 + a2*s + a3*t + a4*s*t
						return P, i
					#3
					if math.fabs(t) > 1.0+error :
						#4
						if math.fabs(A) < 1.0e-12:
							t = -C/B
							err_t = math.fabs(t) - 1.0
							#5
							if err_t <= error:
								if math.fabs(a2+a4*t) == 0.0 : s = (y - a5 - a7*t)/(a6 +a8*t)
								else: s = (x - a1 -a3*t)/(a2 + a4*t)
								err_s = math.fabs(s) - 1.0
								if err_s <= error:
									a1 = 0.25*( SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
									a2 = 0.25*(-SURF.node1P[i]+SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
									a3 = 0.25*(-SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]+SURF.node4P[i])
									a4 = 0.25*( SURF.node1P[i]-SURF.node2P[i]+SURF.node3P[i]-SURF.node4P[i])
									P = a1 + a2*s + a3*t + a4*s*t
									return P, i
								else : i = i + 1
							#5
							else : i = i + 1
						#4
						else : i = i + 1
					#3
					else : i = i + 1
				#2
				else : i = i + 1
			#1
			else: i = i + 1
		else: i = i + 1
	return 0, -1
################################################################################

################################################################################

def GaussElimination(X, Ndeg, UpXVal, UpYVal, UpValCount, UpLow):
	i = 0; j = 0; k = 0; n = 0
	RSQRT = 0.0; AVGDIFF = 0.0
	
	A = [[0.0]*(Ndeg+1) for j in xrange(Ndeg)]
	
	i = 0
	while i < Ndeg:
		j = 0
		while j < Ndeg+1:
			k = 0
			if j < Ndeg:
				while k < UpValCount:
					A[i][j] = A[i][j] + pow(UpXVal[k],i+j)
					k = k + 1
			else:
				while k < UpValCount:
					A[i][j] = A[i][j] + pow(UpXVal[k],i)*UpYVal[k]
					k = k + 1
			j = j + 1
		i = i + 1
	j = 0
	while j < Ndeg:
		i = 0
		while i < Ndeg:
			if i > j:
				c = A[i][j]/A[j][j]
				k = 0
				while k < Ndeg+1:
					A[i][k] = A[i][k] - c * A[j][k]
					k = k + 1
			i = i + 1
		j = j + 1
		
	X[Ndeg-1] = A[Ndeg-1][Ndeg]/A[Ndeg-1][Ndeg-1]
	i = Ndeg-2
	while i >= 0:
		sum = 0; j = i + 1
		while j < Ndeg:
			sum = sum + A[i][j]*X[j]
			j = j + 1
		X[i] = (A[i][Ndeg] - sum)/A[i][i]
		i = i - 1

	# if UpLow == 1:
	# 	X[0] = float(CenRibLength/(2*1000))
	# if UpLow == -1:
	# 	X[0] = -1*float(CenRibLength/(2*1000))

	i = 0; diff = 0.0; maxdiff = 0.0
	while i < UpValCount:
		j = 0; Square = 0.0
		while j < Ndeg:
			Square = Square + X[j]*pow(UpXVal[i],j)
			j = j + 1
		diff = Square - UpYVal[i]
		AVGDIFF = AVGDIFF + math.fabs(diff)
		if math.fabs(diff) > maxdiff:
			maxdiff = math.fabs(diff)
		Square = pow(diff,2)
		RSQRT = RSQRT + Square
		i = i + 1
	AVGDIFF = AVGDIFF/UpValCount
	AVGDIFF = (AVGDIFF+maxdiff)/2

	del A
	return RSQRT, AVGDIFF
################################################################################
# Reading the Binary File for *.sfric # - Addition in 17.04.21 
################################################################################
def SFRIC_READ(file, Node, Surf, RIM_ROAD, CAMBER):

	file.seek(0,2); fend = file.tell() #find the end position of binary file
	file.seek(0);   fpos = file.tell() #find the start position of binary file

	NLB = []
	XYZ = []
	ELM = []
	
	READ_LENGTH = 0

	while file.tell() < fend:
		BlockID     = struct.unpack('i', file.read(4))[0]
		# print BlockID
		if BlockID == 11:
			BlockLength = struct.unpack('i', file.read(4))[0]
			BlockTitle = ''
			i = 0
			while i < BlockLength:
				BlockTitle = BlockTitle + struct.unpack('c', file.read(1))[0]
				i = i + 1
			# print BlockTitle
		elif BlockID == 12:
			LocalCoord = []
			i = 0
			while i < 9:
				LocalCoord.append(struct.unpack('d', file.read(8))[0])
				i = i + 1
			CAMBER[0] = math.atan(LocalCoord[5]/LocalCoord[4])*180/math.pi
			# print CAMBER
			del LocalCoord
		elif BlockID == 21:
			NodesNUM = struct.unpack('i', file.read(4))[0]
			i = 0
			while i < NodesNUM:
				Label = struct.unpack('i', file.read(4))[0]
				NLB.append(Label)
				i = i + 1
			# print "Total Node Number =", len(NLB)
			i = 0
			while i < NodesNUM:
				X = struct.unpack('d', file.read(8))[0]
				Y = struct.unpack('d', file.read(8))[0]
				Z = struct.unpack('d', file.read(8))[0]
				Node.addNode(NLB[i], X, Y, Z, 0.0)
				XYZ.append([NLB[i], X, Y, Z])
				i = i + 1
		elif BlockID == 31:
			E3DNUM = struct.unpack('i', file.read(4))[0]
			E3D = ELEMENT3D()
			E3D.init()
			i = 0
			while i < E3DNUM:
				ID = struct.unpack('i', file.read(4))[0]
				N1 = struct.unpack('i', file.read(4))[0]
				N2 = struct.unpack('i', file.read(4))[0]
				N3 = struct.unpack('i', file.read(4))[0]
				N4 = struct.unpack('i', file.read(4))[0]
				N5 = struct.unpack('i', file.read(4))[0]
				N6 = struct.unpack('i', file.read(4))[0]
				N7 = struct.unpack('i', file.read(4))[0]
				N8 = struct.unpack('i', file.read(4))[0]
				E3D.addElement3D([ID, N1, N2, N3, N4, N5, N6, N7, N8])
				i  = i + 1
			del E3D
		elif BlockID == 32:
			E2DNUM = struct.unpack('i', file.read(4))[0]
			Surf.count = E2DNUM
			i = 0
			while i < E2DNUM:
				ID = struct.unpack('i', file.read(4))[0]
				N1 = struct.unpack('i', file.read(4))[0]
				N2 = struct.unpack('i', file.read(4))[0]
				N3 = struct.unpack('i', file.read(4))[0]
				N4 = struct.unpack('i', file.read(4))[0]
				SN1= BinarySearch(Node, N1, 0, NodesNUM-1)
				SN2= BinarySearch(Node, N2, 0, NodesNUM-1)
				SN3= BinarySearch(Node, N3, 0, NodesNUM-1)
				SN4= BinarySearch(Node, N4, 0, NodesNUM-1)
				Surf.addSurf(ID, Node.nodelabel[SN1],Node.x[SN1],Node.y[SN1],Node.z[SN1],Node.p[SN1],
								Node.nodelabel[SN2],Node.x[SN2],Node.y[SN2],Node.z[SN2],Node.p[SN2],
								Node.nodelabel[SN3],Node.x[SN3],Node.y[SN3],Node.z[SN3],Node.p[SN3],
								Node.nodelabel[SN4],Node.x[SN4],Node.y[SN4],Node.z[SN4],Node.p[SN4])
				ELM.append([ID, N1, N2, N3, N4])
				i  = i + 1
		elif BlockID == 51 or BlockID == 52:
			BlockLength = struct.unpack('i', file.read(4))[0]
			Eleset = ''
			i = 0
			while i < BlockLength:
				Eleset = Eleset + struct.unpack('c', file.read(1))[0]
				i = i + 1
			BlockFlag   = struct.unpack('i', file.read(4))[0]
			ENUM = struct.unpack('i', file.read(4))[0]
			ESET = []
			i = 0
			while i < ENUM:
				ESET.append(struct.unpack('i', file.read(4))[0])
				i = i + 1
			# print "Finish to Read", Eleset
			del ESET
		elif BlockID == 61:
			# print "Read Rim Information and Save them!"
			ControlNodeID = struct.unpack('i', file.read(4))[0]
			# print "Rim Control Node =", ControlNodeID
			X = struct.unpack('d', file.read(8))[0]
			Y = struct.unpack('d', file.read(8))[0]
			Z = struct.unpack('d', file.read(8))[0]
			R = struct.unpack('d', file.read(8))[0]
			W = struct.unpack('d', file.read(8))[0]
			G = struct.unpack('i', file.read(4))[0]
			RIM_ROAD.append([ControlNodeID, X, Y, Z])
			# print "R, W, G =", R, W, G
			i = 0
			while i < G:
				BlockFlag   = struct.unpack('i', file.read(4))[0]
				# print "BlockFlag = ", BlockFlag
				i = i + 1
			i = 0
			while i < G:
				X1 = struct.unpack('d', file.read(8))[0]
				Y1 = struct.unpack('d', file.read(8))[0]
				X2 = struct.unpack('d', file.read(8))[0]
				Y2 = struct.unpack('d', file.read(8))[0]
				# print "X1, Y1, X2, Y2 =", X1*1000, Y1*1000, X2*1000, Y2*1000
				i = i + 1
		elif BlockID == 62:
			# print "Read Road Information and Save them!"
			Tref = struct.unpack('d', file.read(8))[0]
			ControlNodeID = struct.unpack('i', file.read(4))[0]
			# print "Road Control Node =", ControlNodeID
			X = struct.unpack('d', file.read(8))[0]
			Y = struct.unpack('d', file.read(8))[0]
			Z = struct.unpack('d', file.read(8))[0]
			R = struct.unpack('d', file.read(8))[0]
			W = struct.unpack('d', file.read(8))[0]
			L = struct.unpack('d', file.read(8))[0]
			RIM_ROAD.append([ControlNodeID, X, Y, Z])
		elif BlockID == 999:
			BlockID     = struct.unpack('i', file.read(4))[0]
			ESP         = ''
			i = 0
			while i < 4:
				ESP     = ESP+ struct.unpack('c', file.read(1))[0]
				i = i + 1
			RecordHead  = struct.unpack('i', file.read(4))[0]
			BlockID     = struct.unpack('i', file.read(4))[0]
			SolverInfo  = ''
			i = 0
			while i < 42:
				SolverInfo = SolverInfo+ struct.unpack('c', file.read(1))[0]
				i = i + 1
			i = 0
			while i < 9:
				BlockID     = struct.unpack('i', file.read(4))[0]
				i = i + 1
			SimulationType = ''
			i = 0
			while i < 26:
				SimulationType = SimulationType+ struct.unpack('c', file.read(1))[0]
				i = i + 1
		else:
			break

	del NLB, XYZ, ELM
	
	
	if len(Node.nodelabel) > 0 and len(Surf.surflabel) > 0:
		return 0
	else:
		return -1
################################################################################
# Reading the Binary File for *.sfricXXX # - Addition in 17.04.21 
################################################################################
def SFRICxxx_READ(resultsfile, Node, Surf, Deformed_RIM_ROAD):
	resultsfile.seek(0,2); fend = resultsfile.tell() #find the end position of binary file
	resultsfile.seek(0);   fpos = resultsfile.tell() #find the start position of binary file
	# print fpos, fend
	##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	RecordHeaderID = 0
	READ_NUM       = 0
	NodeNUM        = 0
	TREAD_ELMENTNUM= 0
	PRESS          = []
	DISP           = []
	
	while resultsfile.tell() < fend:
		RecordHeaderID     = struct.unpack('i', resultsfile.read(4))[0]
		if RecordHeaderID == 13:
			RecordValue    = struct.unpack('i', resultsfile.read(4))[0]
			# print "RecordHeaderID = ", RecordHeaderID, "Record Value = ", RecordValue
			OutputStepTime = struct.unpack('d', resultsfile.read(8))[0]
			OutputStepID       = struct.unpack('i', resultsfile.read(4))[0]
			OutputStepName = ''
			i = 0 
			while i < 26:
				OutputStepName     = OutputStepName + struct.unpack('c', resultsfile.read(1))[0]
				i = i + 1
			# print OutputStepName
			OutputStepNo      = struct.unpack('i', resultsfile.read(4))[0]
			OutputStepNode    = struct.unpack('i', resultsfile.read(4))[0]
			NodeNUM           = struct.unpack('i', resultsfile.read(4))[0]
			# print "NodeNUM = ", NodeNUM
			READ_NUM     = NodeNUM
			i = 0
			while i < READ_NUM:
				NodeID = int(struct.unpack('i', resultsfile.read(4))[0])
				DISP.append([0.0,0.0,0.0])
				i = i + 1
			# print "finish to read the Node Lists!"
		elif RecordHeaderID == 14:
			RecordValue    = struct.unpack('i', resultsfile.read(4))[0]
			# print "RecordHeaderID = ", RecordHeaderID, "Record Value = ", RecordValue
			IDATA_TYPE     = struct.unpack('i', resultsfile.read(4))[0]
			IOUT_TYPE      = struct.unpack('i', resultsfile.read(4))[0]
			ICOMP1         = struct.unpack('i', resultsfile.read(4))[0]
			ICOMP2         = struct.unpack('i', resultsfile.read(4))[0]
			ICOMP3         = struct.unpack('i', resultsfile.read(4))[0]
			ICOMP4         = struct.unpack('i', resultsfile.read(4))[0]
			ICOMP5         = struct.unpack('i', resultsfile.read(4))[0]
			ICOMP6         = struct.unpack('i', resultsfile.read(4))[0]
			ICOMP7         = struct.unpack('i', resultsfile.read(4))[0]
			ICOMP8         = struct.unpack('i', resultsfile.read(4))[0]
			IDIRECTION     = struct.unpack('i', resultsfile.read(4))[0]
			ICALC_WARN     = struct.unpack('i', resultsfile.read(4))[0]
			IDMINV         = struct.unpack('i', resultsfile.read(4))[0]
			IDMAXV         = struct.unpack('i', resultsfile.read(4))[0]
			VMIN           = struct.unpack('d', resultsfile.read(8))[0]
			VMAX           = struct.unpack('d', resultsfile.read(8))[0]
			DATA_TITLE     = ''
			i = 0 
			while i < 26:
				DATA_TITLE = DATA_TITLE + struct.unpack('c', resultsfile.read(1))[0]
				i = i + 1
			# print DATA_TITLE
			i = 0
			if RecordValue == 102:
				# print READ_NUM
				while i < READ_NUM:
					Value = struct.unpack('d', resultsfile.read(8))[0]
					DISP[i][0] = Value #for making of abaqus odb file
					Node.x[i] = Node.x[i] + Value
					i = i + 1
			if RecordValue == 103:
				while i < READ_NUM:
					Value = struct.unpack('d', resultsfile.read(8))[0]
					DISP[i][1] = Value #for making of abaqus odb file
					Node.y[i] = Node.y[i] + Value
					i = i + 1
			if RecordValue == 104:
				while i < READ_NUM:
					Value = struct.unpack('d', resultsfile.read(8))[0]
					DISP[i][2] = Value #for making of abaqus odb file
					Node.z[i] = Node.z[i] + Value
					i = i + 1
			# elif RecordValue == 900000001:
			# 	while i < READ_NUM:
			# 		Value = struct.unpack('d', resultsfile.read(8))[0]
			# 		print 'NodalArea', Value
			# 		i = i + 1
			# elif RecordValue == 900000044:
			# 	while i < READ_NUM:
			# 		Value = struct.unpack('d', resultsfile.read(8))[0]
			# 		print 'CForceNorm', Value
			# 		i = i + 1
			elif RecordValue == 900000054:
				while i < READ_NUM:
					Value = struct.unpack('d', resultsfile.read(8))[0]
					PRESS.append([Value, Value, Value])
					Node.p[i] = Node.p[i] + Value
					i = i + 1
			else:
				while i < READ_NUM:
					Value = struct.unpack('d', resultsfile.read(8))[0]
					i = i + 1
			# print 'Finish to Read', DATA_TITLE
		elif RecordHeaderID == 2:
			TREAD_ELMENTNUM = struct.unpack('i', resultsfile.read(4))[0]
			# print "TREAD_ELMENTNUM = ", TREAD_ELMENTNUM
			i = 0
			while i < TREAD_ELMENTNUM:
				TreadID = struct.unpack('i', resultsfile.read(4))[0]
				i = i + 1
			READ_NUM     = TREAD_ELMENTNUM
		elif RecordHeaderID == 1:
			ELMENT_NUM   = struct.unpack('i', resultsfile.read(4))[0]
			# print "ELMENT_NUM = ", ELMENT_NUM
			i = 0
			while i < ELMENT_NUM:
				ID = struct.unpack('i', resultsfile.read(4))[0]
				Deformed_RIM_ROAD.append([ID, 0.0, 0.0, 0.0])
				i = i + 1
			READ_NUM     = ELMENT_NUM
			while resultsfile.tell() < fend:
				RecordHeaderID     = struct.unpack('i', resultsfile.read(4))[0]
				RecordValue    = struct.unpack('i', resultsfile.read(4))[0]
				# print "RecordHeaderID = ", RecordHeaderID, "Record Value = ", RecordValue
				IDATA_TYPE     = struct.unpack('i', resultsfile.read(4))[0]
				IOUT_TYPE      = struct.unpack('i', resultsfile.read(4))[0]
				ICOMP1         = struct.unpack('i', resultsfile.read(4))[0]
				ICOMP2         = struct.unpack('i', resultsfile.read(4))[0]
				ICOMP3         = struct.unpack('i', resultsfile.read(4))[0]
				ICOMP4         = struct.unpack('i', resultsfile.read(4))[0]
				ICOMP5         = struct.unpack('i', resultsfile.read(4))[0]
				ICOMP6         = struct.unpack('i', resultsfile.read(4))[0]
				ICOMP7         = struct.unpack('i', resultsfile.read(4))[0]
				ICOMP8         = struct.unpack('i', resultsfile.read(4))[0]
				IDIRECTION     = struct.unpack('i', resultsfile.read(4))[0]
				ICALC_WARN     = struct.unpack('i', resultsfile.read(4))[0]
				IDMINV         = struct.unpack('i', resultsfile.read(4))[0]
				IDMAXV         = struct.unpack('i', resultsfile.read(4))[0]
				VMIN           = struct.unpack('d', resultsfile.read(8))[0]
				VMAX           = struct.unpack('d', resultsfile.read(8))[0]
				DATA_TITLE     = ''
				i = 0 
				while i < 26:
					DATA_TITLE = DATA_TITLE + struct.unpack('c', resultsfile.read(1))[0]
					i = i + 1
				# print DATA_TITLE
				i = 0
				if RecordValue == 102:
					while i < READ_NUM:
						Value = struct.unpack('d', resultsfile.read(8))[0]
						Deformed_RIM_ROAD[i][1] = Value
						i = i + 1
				if RecordValue == 103:
					while i < READ_NUM:
						Value = struct.unpack('d', resultsfile.read(8))[0]
						Deformed_RIM_ROAD[i][2] = Value
						i = i + 1
				if RecordValue == 104:
					while i < READ_NUM:
						Value = struct.unpack('d', resultsfile.read(8))[0]
						Deformed_RIM_ROAD[i][3] = Value
						i = i + 1
				if RecordValue == 106:
					while i < READ_NUM:
						Value = struct.unpack('d', resultsfile.read(8))[0]
						# print "Value = ", Value
						i = i + 1
				if RecordValue == 107:
					while i < READ_NUM:
						Value = struct.unpack('d', resultsfile.read(8))[0]
						# print "Value = ", Value
						i = i + 1
				if RecordValue == 108:
					while i < READ_NUM:
						Value = struct.unpack('d', resultsfile.read(8))[0]
						# print "Value = ", Value
						i = i + 1
				else:
					while i < READ_NUM:
						Value = struct.unpack('d', resultsfile.read(8))[0]
						i = i + 1
		else:
			break
			
	del PRESS, DISP
	
	# print 'Lets Start to Sort the Virtual Surface Element!'
	i = 0
	while i < len(Surf.surflabel):
		SN1 = BinarySearch(Node, Surf.node1[i], 0, len(Node.nodelabel)-1) 
		SN2 = BinarySearch(Node, Surf.node2[i], 0, len(Node.nodelabel)-1) 
		SN3 = BinarySearch(Node, Surf.node3[i], 0, len(Node.nodelabel)-1) 
		SN4 = BinarySearch(Node, Surf.node4[i], 0, len(Node.nodelabel)-1)
		# print 'Check', Surf.node1[i], Node.nodelabel[SN1]
		Surf.node1X[i] = Node.x[SN1]
		Surf.node2X[i] = Node.x[SN2]
		Surf.node3X[i] = Node.x[SN3]
		Surf.node4X[i] = Node.x[SN4]
		Surf.node1Y[i] = Node.y[SN1]
		Surf.node2Y[i] = Node.y[SN2]
		Surf.node3Y[i] = Node.y[SN3]
		Surf.node4Y[i] = Node.y[SN4]
		Surf.node1Z[i] = Node.z[SN1]
		Surf.node2Z[i] = Node.z[SN2]
		Surf.node3Z[i] = Node.z[SN3]
		Surf.node4Z[i] = Node.z[SN4]
		Surf.node1P[i] = Node.p[SN1]
		Surf.node2P[i] = Node.p[SN2]
		Surf.node3P[i] = Node.p[SN3]
		Surf.node4P[i] = Node.p[SN4]
		i = i + 1
	# print 'Finish Sorting the Virtual Surface Element!'
	
	if len(Node.nodelabel) > 0 and len(Surf.surflabel) > 0:
		return 0
	else:
		return -1
# *******************************************************************
#       class definition
# *******************************************************************
class NODE:
	count = 0
	def init(self):
		self.nodelabel=[]
		self.x=[]
		self.y=[]
		self.z=[]
		self.p=[]
	def addNode(self, nd, _x, _y, _z, _p):
		self.nodelabel.append(nd)
		self.x.append(_x)
		self.y.append(_y)
		self.z.append(_z)
		self.p.append(_p)
class SURF:
	count = 0
	def init(self):
		self.surflabel=[]
		self.node1    =[]
		self.node1X   =[]
		self.node1Y   =[]
		self.node1Z   =[]
		self.node1P   =[]
		self.node2    =[]
		self.node2X   =[]
		self.node2Y   =[]
		self.node2Z   =[]
		self.node2P   =[]
		self.node3    =[]
		self.node3X   =[]
		self.node3Y   =[]
		self.node3Z   =[]
		self.node3P   =[]
		self.node4    =[]
		self.node4X   =[]
		self.node4Y   =[]
		self.node4Z   =[]
		self.node4P   =[]
	def addSurf(self,sf,n1,x1,y1,z1,p1,n2,x2,y2,z2,p2,n3,x3,y3,z3,p3,n4,x4,y4,z4,p4):
		self.surflabel.append(sf)
		self.node1.append(n1)
		self.node1X.append(x1)
		self.node1Y.append(y1)
		self.node1Z.append(z1)
		self.node1P.append(p1)
		self.node2.append(n2)
		self.node2X.append(x2)
		self.node2Y.append(y2)
		self.node2Z.append(z2)
		self.node2P.append(p2)
		self.node3.append(n3)
		self.node3X.append(x3)
		self.node3Y.append(y3)
		self.node3Z.append(z3)
		self.node3P.append(p3)
		self.node4.append(n4)
		self.node4X.append(x4)
		self.node4Y.append(y4)
		self.node4Z.append(z4)
		self.node4P.append(p4)	
class ELEMENT3D:
	count = 0
	#ELEMENT includes LABEL, NODE1, NODE2, NODE3, NODE4
	def init(self):
		self.element = []
	def addElement3D(self, _element):
		self.element.append(_element)

def GetSimSteps(lstSimConditions):
    with open(lstSimConditions) as IN:
        lines = IN.readlines()

    for line in lines:
        if 'SIMULATION_TIME' in line:
            word = list(line.split('='))
            data = list(word[1].split(','))
            Time_Final= float(data[0])

        if 'OUTPUT_CONTROL' in line:
            word = list(line.split('='))
            data = list(word[1].split(','))
            Time_Step = float(data[0])

    if Time_Final == 0.0:
        FinalStep = int(0.06 / Time_Step)
    else:
        FinalStep = int(Time_Final / Time_Step)

    return FinalStep
	
def FindFlatSpotOORNodeSet(CUTEInpFileName=''):
	if CUTEInpFileName =='':
		strJobDir = os.getcwd()
		CUTEInpFileName = strJobDir.split('/')[-2] + '.inp'
	# CUTEInpFileName = str(sys.argv[1])
	ReadCUTEInpFile = open(CUTEInpFileName, 'r')
	CUTEInpFileLine = ReadCUTEInpFile.readlines()
	
	############# Find a Elset=CTB to find CTB's Nodes #############
	ElsetCTBLine = CUTEInpFileLine.index('*ELSET, ELSET=CTB\r\n')
	FindElsetCTB = CUTEInpFileLine[ElsetCTBLine+1:-1]
	for line in range(len(FindElsetCTB)):
		if FindElsetCTB[line].split(',')[0] == '*ELSET':
			NextElsetCTB = FindElsetCTB[line]
			break
	NextElsetLine = CUTEInpFileLine.index(NextElsetCTB)
	CTBElemLine = CUTEInpFileLine[ElsetCTBLine+1:NextElsetLine]
	
	ListCTBElem = []
	for line in range(len(CTBElemLine)):
		for i in range(len(CTBElemLine[line].split('\r\n')[0].split(','))):
			Elem = CTBElemLine[line].split('\r\n')[0].split(',')[i].strip()
			ListCTBElem.append(Elem)
	############# Find a Elset=CTB to find CTB's Nodes #############	

	############# Find All Elements #############
	ListAllElemLine = []
	for line in range(len(CUTEInpFileLine)):
		if CUTEInpFileLine[line].split(',')[0] == '*ELSET':
			ElsetFisrtLine = CUTEInpFileLine[line]
			NumElsetFisrtLine = CUTEInpFileLine.index(ElsetFisrtLine)
			break
	for line in range(len(CUTEInpFileLine)):
		if CUTEInpFileLine[line] == '** Surface Definition\r\n':
			ElsetFinalLine = CUTEInpFileLine[line]
			NumElsetFinalLine = CUTEInpFileLine.index(ElsetFinalLine)
			break
	
	ListAllElemLine.append(CUTEInpFileLine[NumElsetFisrtLine+1:NumElsetFinalLine])

	ListAllElem = []
	for line in range(len(ListAllElemLine[0])):
		if ListAllElemLine[0][line].split(',')[0] == '*ELSET':
			pass
		else:
			ListAllElem.append(ListAllElemLine[0][line])
			
	ListAllIndivElem = []
	for line in range(len(ListAllElem)):
		for i in range(len(ListAllElem[line].split('\r\n')[0].split(','))):
			AllElem = ListAllElem[line].split('\r\n')[0].split(',')[i].strip()
			ListAllIndivElem.append(AllElem)
	############# Find All Elements #############

	############# Find a CTB Tri Elem's Nodes #############
	if '*ELEMENT, TYPE=CGAX3H\r\n' in CUTEInpFileLine:
		ElemCGAX3H = CUTEInpFileLine.index('*ELEMENT, TYPE=CGAX3H\r\n')
		FindCGAX3H = CUTEInpFileLine[ElemCGAX3H+1:-1]
		for line in range(len(FindCGAX3H)):
			if list(FindCGAX3H[line])[0] == '*':
				NextElemType = FindCGAX3H[line]
				break
		NextElTypeLine = CUTEInpFileLine.index(NextElemType)
		CGAX3HLine = CUTEInpFileLine[ElemCGAX3H+1:NextElTypeLine]
		
		ListCTBTriNode = []
		for line in range(len(CGAX3HLine)):
			if CGAX3HLine[line].split('\r\n')[0].split(',')[0].strip() in ListCTBElem:
				ListCTBTriNode.append(CGAX3HLine[line].split('\r\n')[0].split(',')[1].strip())
				ListCTBTriNode.append(CGAX3HLine[line].split('\r\n')[0].split(',')[2].strip())
				ListCTBTriNode.append(CGAX3HLine[line].split('\r\n')[0].split(',')[3].strip())
		############# Find a CTB Tri Elem's Nodes #############

		############# Find a CTB Quad Elem's Nodes #############
		ElemCGAX4H = CUTEInpFileLine.index('*ELEMENT, TYPE=CGAX4H\r\n')
		FindCGAX4H = CUTEInpFileLine[ElemCGAX4H+1:-1]
		for line in range(len(FindCGAX4H)):
			if FindCGAX4H[line].split(',')[0] == '*NSET':
				NextNsetType = FindCGAX4H[line]
				break
		NextNsetLine = CUTEInpFileLine.index(NextNsetType)
		CGAX4HLine = CUTEInpFileLine[ElemCGAX4H+1:NextNsetLine]
		
		ListCTBQuadNode = []
		for line in range(len(CGAX4HLine)):
			if CGAX4HLine[line].split('\r\n')[0].split(',')[0].strip() in ListCTBElem:
				ListCTBQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[1].strip())
				ListCTBQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[2].strip())
				ListCTBQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[3].strip())
				ListCTBQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[4].strip())
		ListAllQuadNode = []
		for line in range(len(CGAX4HLine)):
			if CGAX4HLine[line].split('\r\n')[0].split(',')[0].strip() in ListAllIndivElem:
				ListAllQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[1].strip())
				ListAllQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[2].strip())
				ListAllQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[3].strip())
				ListAllQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[4].strip())
				
		ListOrphanQuadNodes = []
		for i in range(len(ListAllQuadNode)):
			NumIndivNode = ListAllQuadNode.count(ListAllQuadNode[i])
			if NumIndivNode == 1:
				if ListAllQuadNode[i] in ListCTBQuadNode:
					if ListAllQuadNode[i] not in ListCTBTriNode:
						ListOrphanQuadNodes.append(ListAllQuadNode[i])
		############# Find a CTB Quad Elem's Nodes #############

		############# Find All Nodes to find a FlatSpot Nodes #############
		### Find All Nodes ###
		AllNodesLine = CUTEInpFileLine.index('*NODE, SYSTEM=R\r\n')
		FindAllNodes = CUTEInpFileLine[AllNodesLine+1:-1]
		for line in range(len(FindAllNodes)):
			if FindAllNodes[line] == '*ELEMENT, TYPE=MGAX1\r\n':
				EndAllNodes = FindAllNodes[line]
				break
		FindEndAllNodes = CUTEInpFileLine.index(EndAllNodes)
		AllNodesLines = CUTEInpFileLine[AllNodesLine+1:FindEndAllNodes]
		### Find All Nodes ###
	
		### Find a FlatSpot Nodes ###
		ListAllEdge2DNodes = []
		maxCentNode = 0
		for line in range(len(AllNodesLines)):
			NodeNum = AllNodesLines[line].split(',')[0].strip()
			XCoord  = AllNodesLines[line].split(',')[1].strip()
			YCoord  = AllNodesLines[line].split(',')[2].strip()
			ZCoord  = AllNodesLines[line].split(',')[3].strip()
			if NodeNum in ListOrphanQuadNodes:
				ListAllEdge2DNodes.append([NodeNum, XCoord, float(YCoord), ZCoord])
		sortListAllNodes = sorted(ListAllEdge2DNodes, key = lambda y : y[2])
		NumsortListAllNodes = len(sortListAllNodes)


		EachRib = []
		i = 0
		while i < NumsortListAllNodes/2 + 1:
			EachRib.append([])
			i = i + 1
		if NumsortListAllNodes == 0:	#There are no grooves
			print '	*There are no grooves'
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				EachRib[0].append(NodeNum)
		elif NumsortListAllNodes == 2:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 4:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 6:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 8:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[6][2] and float(YCoord) >= sortListAllNodes[5][2]:
					EachRib[3].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 10:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[6][2] and float(YCoord) >= sortListAllNodes[5][2]:
					EachRib[3].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[8][2] and float(YCoord) >= sortListAllNodes[7][2]:
					EachRib[4].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 12:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[6][2] and float(YCoord) >= sortListAllNodes[5][2]:
					EachRib[3].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[8][2] and float(YCoord) >= sortListAllNodes[7][2]:
					EachRib[4].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[10][2] and float(YCoord) >= sortListAllNodes[9][2]:
					EachRib[5].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 14:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[6][2] and float(YCoord) >= sortListAllNodes[5][2]:
					EachRib[3].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[8][2] and float(YCoord) >= sortListAllNodes[7][2]:
					EachRib[4].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[10][2] and float(YCoord) >= sortListAllNodes[9][2]:
					EachRib[5].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[12][2] and float(YCoord) >= sortListAllNodes[11][2]:
					EachRib[6].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)

		del sortListAllNodes
		del AllNodesLines
		del ListAllEdge2DNodes
		del FindAllNodes
		del ListOrphanQuadNodes
		del ListCTBTriNode
		del CGAX3HLine
		del CGAX4HLine
		del ListAllIndivElem
		del ListAllElem
		del ListAllElemLine
		del ListCTBElem
		return EachRib
		### Find a FlatSpot Nodes ###
		############# Find All Nodes to find a FlatSpot Nodes #############
		
	else:
		############# Find a CTB Quad Elem's Nodes #############
		ElemCGAX4H = CUTEInpFileLine.index('*ELEMENT, TYPE=CGAX4H\r\n')
		FindCGAX4H = CUTEInpFileLine[ElemCGAX4H+1:-1]
		for line in range(len(FindCGAX4H)):
			if FindCGAX4H[line].split(',')[0] == '*NSET':
				NextNsetType = FindCGAX4H[line]
				break
		NextNsetLine = CUTEInpFileLine.index(NextNsetType)
		CGAX4HLine = CUTEInpFileLine[ElemCGAX4H+1:NextNsetLine]
		
		ListCTBQuadNode = []
		for line in range(len(CGAX4HLine)):
			if CGAX4HLine[line].split('\r\n')[0].split(',')[0].strip() in ListCTBElem:
				ListCTBQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[1].strip())
				ListCTBQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[2].strip())
				ListCTBQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[3].strip())
				ListCTBQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[4].strip())
		ListAllQuadNode = []
		for line in range(len(CGAX4HLine)):
			if CGAX4HLine[line].split('\r\n')[0].split(',')[0].strip() in ListAllIndivElem:
				ListAllQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[1].strip())
				ListAllQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[2].strip())
				ListAllQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[3].strip())
				ListAllQuadNode.append(CGAX4HLine[line].split('\r\n')[0].split(',')[4].strip())
				
		ListOrphanQuadNodes = []
		for i in range(len(ListAllQuadNode)):
			NumIndivNode = ListAllQuadNode.count(ListAllQuadNode[i])
			if NumIndivNode == 1:
				if ListAllQuadNode[i] in ListCTBQuadNode:
					ListOrphanQuadNodes.append(ListAllQuadNode[i])
		############# Find a CTB Quad Elem's Nodes #############

		############# Find All Nodes to find a FlatSpot Nodes #############
		### Find All Nodes ###
		AllNodesLine = CUTEInpFileLine.index('*NODE, SYSTEM=R\r\n')
		FindAllNodes = CUTEInpFileLine[AllNodesLine+1:-1]
		for line in range(len(FindAllNodes)):
			if FindAllNodes[line] == '*ELEMENT, TYPE=MGAX1\r\n':
				EndAllNodes = FindAllNodes[line]
				break
		FindEndAllNodes = CUTEInpFileLine.index(EndAllNodes)
		AllNodesLines = CUTEInpFileLine[AllNodesLine+1:FindEndAllNodes]
		### Find All Nodes ###
	
		### Find a FlatSpot Nodes ###
		ListAllEdge2DNodes = []
		maxCentNode = 0
		for line in range(len(AllNodesLines)):
			NodeNum = AllNodesLines[line].split(',')[0].strip()
			XCoord  = AllNodesLines[line].split(',')[1].strip()
			YCoord  = AllNodesLines[line].split(',')[2].strip()
			ZCoord  = AllNodesLines[line].split(',')[3].strip()
			if NodeNum in ListOrphanQuadNodes:
				ListAllEdge2DNodes.append([NodeNum, XCoord, float(YCoord), ZCoord])

		sortListAllNodes = sorted(ListAllEdge2DNodes, key = lambda y : y[2])
		NumsortListAllNodes = len(sortListAllNodes)


		EachRib = []
		i = 0
		while i < NumsortListAllNodes/2 + 1:
			EachRib.append([])
			i = i + 1
		if NumsortListAllNodes == 0:	#There are no grooves
			print '	*There are no grooves'
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				EachRib[0].append(NodeNum)
		elif NumsortListAllNodes == 2:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 4:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 6:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 8:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[6][2] and float(YCoord) >= sortListAllNodes[5][2]:
					EachRib[3].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 10:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[6][2] and float(YCoord) >= sortListAllNodes[5][2]:
					EachRib[3].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[8][2] and float(YCoord) >= sortListAllNodes[7][2]:
					EachRib[4].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 12:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[6][2] and float(YCoord) >= sortListAllNodes[5][2]:
					EachRib[3].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[8][2] and float(YCoord) >= sortListAllNodes[7][2]:
					EachRib[4].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[10][2] and float(YCoord) >= sortListAllNodes[9][2]:
					EachRib[5].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)
		elif NumsortListAllNodes == 14:
			for line in range(len(AllNodesLines)):
				NodeNum = AllNodesLines[line].split(',')[0].strip()
				YCoord  = AllNodesLines[line].split(',')[2].strip()
				if float(YCoord) <= sortListAllNodes[0][2]:
					EachRib[0].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[2][2] and float(YCoord) >= sortListAllNodes[1][2]:
					EachRib[1].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[4][2] and float(YCoord) >= sortListAllNodes[3][2]:
					EachRib[2].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[6][2] and float(YCoord) >= sortListAllNodes[5][2]:
					EachRib[3].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[8][2] and float(YCoord) >= sortListAllNodes[7][2]:
					EachRib[4].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[10][2] and float(YCoord) >= sortListAllNodes[9][2]:
					EachRib[5].append(NodeNum)
				if float(YCoord) <= sortListAllNodes[12][2] and float(YCoord) >= sortListAllNodes[11][2]:
					EachRib[6].append(NodeNum)
				if float(YCoord) >= sortListAllNodes[-1][2]:
					EachRib[-1].append(NodeNum)

		del sortListAllNodes
		del AllNodesLines
		del ListAllEdge2DNodes
		del FindAllNodes
		del ListOrphanQuadNodes
		del CGAX4HLine
		del ListAllIndivElem
		del ListAllElem
		del ListAllElemLine
		del ListCTBElem
		return EachRib
		### Find a FlatSpot Nodes ###
		############# Find All Nodes to find a FlatSpot Nodes #############

def rotateNode(x_coord, y_coord, ang):
	rotated_x_coord = x_coord*cos(radians(ang)) - y_coord*sin(radians(ang))
	rotated_y_coord = x_coord*sin(radians(ang)) + y_coord*cos(radians(ang))
	return rotated_x_coord, rotated_y_coord
########################################################################################################################
########################################################################################################################
########################################################################################################################

def main(sfricFileName='', sfricResultFileName='', \
	trdFileName='', shistFileName='', contourFileName='', \
		SlipAngle='',	vload='', ProductLine='', CUTEInpFileName='',\
			pointFileName='', pressFileName='', valuesFileName='', areaFileName='', infoFileName=''):

	ArgIn =1 
	# CheckExecution.getProgramTime(str(sys.argv[0]), "Start")

	##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	file = open(sfricFileName,'rb')
	##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Node = NODE()
	Node.init()

	Surf = SURF()
	Surf.init()

	RIM_ROAD = []

	CAMBER = [0.0]

	if(SFRIC_READ(file, Node, Surf, RIM_ROAD, CAMBER)==-1):
		print "Error during reading the binary file!"
	#print 'Finish Reading the Tire Surface Information!'
	########################################################################################################################
	########################################################################################################################
	########################################################################################################################
	print '****************************************************'
	resultsfile = open(sfricResultFileName,'rb')

	Deformed_RIM_ROAD   = []

	if(SFRICxxx_READ(resultsfile, Node, Surf, Deformed_RIM_ROAD)==-1):
		print "Error during reading the binary file!"
		
	### [Start] Definition of Contact Pressure Criteria by Tire Segment ###
	if ProductLine == 'PCR' or ProductLine == 'LTR':
		bnd = 5.0e4
	else:
		bnd = 1.0e5
	### [End] Definition of Contact Pressure Criteria by Tire Segment ###

	MAXZ = 0
	MAXZtoROADZ = 0.0; CAMBA = 0.0	

	### [Start] Identify the lowest node coordinates in the load direction ###
	i = 0
	while i < len(Node.nodelabel):
		if MAXZ > Node.z[i]: MAXZ = Node.z[i]
		i = i + 1
	### [End] Identify the lowest node coordinates in the load direction ###

	DeformNode = NODE()
	DeformNode.init()

	OFFSET_ZCoord = -0.005
	REGION_ZCoord = MAXZ - OFFSET_ZCoord

	LatY = [] # create the temporary array for sorting

	### [Start] Add Y coordinates and pressure values to the temporary list in the width direction ###
	i = 0
	while i < len(Node.nodelabel):
		if Node.z[i] < REGION_ZCoord:
			if SlipAngle != 0:
				Node.x[i] = rotateNode(Node.x[i], Node.y[i], SlipAngle)[0]
				Node.y[i] = rotateNode(Node.x[i], Node.y[i], SlipAngle)[1]
				DeformNode.addNode(Node.nodelabel[i], Node.x[i], Node.y[i], Node.z[i], Node.p[i])
				LatY.append([Node.y[i], Node.p[i]])
				Node.x[i] = rotateNode(Node.x[i], Node.y[i], SlipAngle*-1)[0]
				Node.y[i] = rotateNode(Node.x[i], Node.y[i], SlipAngle*-1)[1]
			else:
				DeformNode.addNode(Node.nodelabel[i], Node.x[i], Node.y[i], Node.z[i], Node.p[i])
				LatY.append([Node.y[i], Node.p[i]])
		i = i + 1

	sortLatY = sorted(LatY, key = lambda x : x[0])
	### [End] Add Y coordinates and pressure values to the temporary list in the width direction ###

	ContPatch = SURF()
	ContPatch.init()
	ContPatchSlip = SURF()
	ContPatchSlip.init()
	if ProductLine == 'TBR':
		ContRegion = MAXZ + 0.005
	else:
		ContRegion = MAXZ + 0.003

	i = 0
	while i < len(Surf.surflabel):
		AverageZCoord = (Surf.node1Z[i]+Surf.node2Z[i]+Surf.node3Z[i]+Surf.node4Z[i])/4.0
		if AverageZCoord < ContRegion:
			if SlipAngle != 0:
				Surf.node1X[i] = rotateNode(Surf.node1X[i], Surf.node1Y[i], SlipAngle)[0]
				Surf.node1Y[i] = rotateNode(Surf.node1X[i], Surf.node1Y[i], SlipAngle)[1]
				Surf.node2X[i] = rotateNode(Surf.node2X[i], Surf.node2Y[i], SlipAngle)[0]
				Surf.node2Y[i] = rotateNode(Surf.node2X[i], Surf.node2Y[i], SlipAngle)[1]
				Surf.node3X[i] = rotateNode(Surf.node3X[i], Surf.node3Y[i], SlipAngle)[0]
				Surf.node3Y[i] = rotateNode(Surf.node3X[i], Surf.node3Y[i], SlipAngle)[1]
				Surf.node4X[i] = rotateNode(Surf.node4X[i], Surf.node4Y[i], SlipAngle)[0]
				Surf.node4Y[i] = rotateNode(Surf.node4X[i], Surf.node4Y[i], SlipAngle)[1]
				ContPatch.addSurf(Surf.surflabel[i],Surf.node1[i],Surf.node1X[i],Surf.node1Y[i],Surf.node1Z[i],Surf.node1P[i],
													Surf.node2[i],Surf.node2X[i],Surf.node2Y[i],Surf.node2Z[i],Surf.node2P[i],
													Surf.node3[i],Surf.node3X[i],Surf.node3Y[i],Surf.node3Z[i],Surf.node3P[i],
													Surf.node4[i],Surf.node4X[i],Surf.node4Y[i],Surf.node4Z[i],Surf.node4P[i])
			### [End] Verticalization of X, Y coordinates for FPC calculation ###
			### [Start] Reverting X, Y coordinates for footprint image plot ###
				Surf.node1X[i] = rotateNode(Surf.node1X[i], Surf.node1Y[i], SlipAngle*-1)[0]
				Surf.node1Y[i] = rotateNode(Surf.node1X[i], Surf.node1Y[i], SlipAngle*-1)[1]
				Surf.node2X[i] = rotateNode(Surf.node2X[i], Surf.node2Y[i], SlipAngle*-1)[0]
				Surf.node2Y[i] = rotateNode(Surf.node2X[i], Surf.node2Y[i], SlipAngle*-1)[1]
				Surf.node3X[i] = rotateNode(Surf.node3X[i], Surf.node3Y[i], SlipAngle*-1)[0]
				Surf.node3Y[i] = rotateNode(Surf.node3X[i], Surf.node3Y[i], SlipAngle*-1)[1]
				Surf.node4X[i] = rotateNode(Surf.node4X[i], Surf.node4Y[i], SlipAngle*-1)[0]
				Surf.node4Y[i] = rotateNode(Surf.node4X[i], Surf.node4Y[i], SlipAngle*-1)[1]
				ContPatchSlip.addSurf(Surf.surflabel[i],Surf.node1[i],Surf.node1X[i],Surf.node1Y[i],Surf.node1Z[i],Surf.node1P[i],
														Surf.node2[i],Surf.node2X[i],Surf.node2Y[i],Surf.node2Z[i],Surf.node2P[i],
														Surf.node3[i],Surf.node3X[i],Surf.node3Y[i],Surf.node3Z[i],Surf.node3P[i],
														Surf.node4[i],Surf.node4X[i],Surf.node4Y[i],Surf.node4Z[i],Surf.node4P[i])
			else:
				ContPatch.addSurf(Surf.surflabel[i],Surf.node1[i],Surf.node1X[i],Surf.node1Y[i],Surf.node1Z[i],Surf.node1P[i],
													Surf.node2[i],Surf.node2X[i],Surf.node2Y[i],Surf.node2Z[i],Surf.node2P[i],
													Surf.node3[i],Surf.node3X[i],Surf.node3Y[i],Surf.node3Z[i],Surf.node3P[i],
													Surf.node4[i],Surf.node4X[i],Surf.node4Y[i],Surf.node4Z[i],Surf.node4P[i])
				ContPatchSlip.addSurf(Surf.surflabel[i],Surf.node1[i],Surf.node1X[i],Surf.node1Y[i],Surf.node1Z[i],Surf.node1P[i],
													Surf.node2[i],Surf.node2X[i],Surf.node2Y[i],Surf.node2Z[i],Surf.node2P[i],
													Surf.node3[i],Surf.node3X[i],Surf.node3Y[i],Surf.node3Z[i],Surf.node3P[i],
													Surf.node4[i],Surf.node4X[i],Surf.node4Y[i],Surf.node4Z[i],Surf.node4P[i])
		i = i + 1

	###############################################
	###############################################
	### [Start] Find Groove position for each rib ###
	Sector = 240

	RibNodes2D = FindFlatSpotOORNodeSet(CUTEInpFileName=CUTEInpFileName)
	ReadtrdFile = open(trdFileName, 'r')
	trdFileLine = ReadtrdFile.readlines()
	NIDOFFSET   = int(trdFileLine[0].split(',')[-1].strip())
	NIDSTART    = int(trdFileLine[0].split(',')[-2].strip())

	ListRibNodes = [];GRV = [];ContRib = [];RibCpress = [];NumCpressNode = [];AREAofeachRIB = []
	RibNo = 1
	for line in range(len(RibNodes2D)):	#The number of Ribs
		print '      - During iteration for rib', RibNo
		NumEachRibNodes2D = len(RibNodes2D[line])	#The number of nodes at each rib
		ListRibNodes.append([])

		i = 0
		while i < NumEachRibNodes2D:
			j = 0
			while j < Sector:
				ListRibNodes[-1].append(int(RibNodes2D[line][i]) + NIDSTART + j*NIDOFFSET)
				j = j + 1
			i = i + 1

		### [Start] Add Y coordinates and pressure values in the width direction to the temporary list of each rib ###
		EachRibLatY = []
		i = 0
		TotalCpress = 0
		while i < len(Node.nodelabel):
			if Node.z[i] < REGION_ZCoord:
				#Node.x[i] = rotateNode(Node.x[i], Node.y[i], SlipAngle)[0]
				#Node.y[i] = rotateNode(Node.x[i], Node.y[i], SlipAngle)[1]
				if Node.nodelabel[i] in ListRibNodes[-1] and float(Node.p[i]) > bnd:
					EachRibLatY.append([Node.y[i], Node.p[i]])
					TotalCpress = TotalCpress + Node.p[i]
				#Node.x[i] = rotateNode(Node.x[i], Node.y[i], SlipAngle*-1)[0]
				#Node.y[i] = rotateNode(Node.x[i], Node.y[i], SlipAngle*-1)[1]
			i = i + 1
		NumCpressNode.append(len(EachRibLatY))
		RibCpress.append(TotalCpress)	# To calculate the contact force of each rib
		
		if TotalCpress == 0:
			print '      	* Contact Pressure (Pa)   :  0.0'
		else:
			print '      	* Contact Pressure (Pa)   : ', round(TotalCpress/len(EachRibLatY),3)

		sortEachRibLatY = sorted(EachRibLatY, key = lambda x : x[0])
		#print sortEachRibLatY
		### [End] Add Y coordinates and pressure values in the width direction to the temporary list of each rib ###
	
		EachRibContPatch = SURF()
		EachRibContPatch.init()

		if ProductLine == 'TBR':
			ContRegion = MAXZ + 0.005
		else:
			ContRegion = MAXZ + 0.003

		i = 0
		while i < len(Surf.surflabel):
			AverageZCoord = (Surf.node1Z[i]+Surf.node2Z[i]+Surf.node3Z[i]+Surf.node4Z[i])/4.0
			if AverageZCoord < ContRegion and Surf.node1[i] in ListRibNodes[-1] and Surf.node2[i] in ListRibNodes[-1] and Surf.node3[i] in ListRibNodes[-1] and Surf.node4[i] in ListRibNodes[-1]:
				#Surf.node1X[i] = rotateNode(Surf.node1X[i], Surf.node1Y[i], SlipAngle*-1)[0]
				#Surf.node1Y[i] = rotateNode(Surf.node1X[i], Surf.node1Y[i], SlipAngle*-1)[1]
				#Surf.node2X[i] = rotateNode(Surf.node2X[i], Surf.node2Y[i], SlipAngle*-1)[0]
				#Surf.node2Y[i] = rotateNode(Surf.node2X[i], Surf.node2Y[i], SlipAngle*-1)[1]
				#Surf.node3X[i] = rotateNode(Surf.node3X[i], Surf.node3Y[i], SlipAngle*-1)[0]
				#Surf.node3Y[i] = rotateNode(Surf.node3X[i], Surf.node3Y[i], SlipAngle*-1)[1]
				#Surf.node4X[i] = rotateNode(Surf.node4X[i], Surf.node4Y[i], SlipAngle*-1)[0]
				#Surf.node4Y[i] = rotateNode(Surf.node4X[i], Surf.node4Y[i], SlipAngle*-1)[1]
				EachRibContPatch.addSurf(Surf.surflabel[i],Surf.node1[i],Surf.node1X[i],Surf.node1Y[i],Surf.node1Z[i],Surf.node1P[i],
													Surf.node2[i],Surf.node2X[i],Surf.node2Y[i],Surf.node2Z[i],Surf.node2P[i],
													Surf.node3[i],Surf.node3X[i],Surf.node3Y[i],Surf.node3Z[i],Surf.node3P[i],
													Surf.node4[i],Surf.node4X[i],Surf.node4Y[i],Surf.node4Z[i],Surf.node4P[i])
			i = i + 1
	#-------------------------------------------------------------------------------------------------------------------#
		i = 0
		sumArea = 0.0
		oset = 0.001
		while i < len(Surf.surflabel):
			maxSurfy = -100.0
			AverageZCoord = (Surf.node1Z[i]+Surf.node2Z[i]+Surf.node3Z[i]+Surf.node4Z[i])/4.0
			if AverageZCoord < ContRegion and Surf.node1[i] in ListRibNodes[-1] and Surf.node2[i] in ListRibNodes[-1] and Surf.node3[i] in ListRibNodes[-1] and Surf.node4[i] in ListRibNodes[-1]:
				if Surf.node1P[i] > bnd and Surf.node2P[i] > bnd and Surf.node3P[i] > bnd and Surf.node4P[i] > bnd:
					Forward = Surf.node1X[i]*Surf.node2Y[i]+Surf.node2X[i]*Surf.node3Y[i]+Surf.node3X[i]*Surf.node4Y[i]+Surf.node4X[i]*Surf.node1Y[i]
					Bacward = Surf.node2X[i]*Surf.node1Y[i]+Surf.node3X[i]*Surf.node2Y[i]+Surf.node4X[i]*Surf.node3Y[i]+Surf.node1X[i]*Surf.node4Y[i]
					area = 0.5*math.fabs(Forward-Bacward)*10000
				elif Surf.node1P[i] > bnd or Surf.node2P[i] > bnd or Surf.node3P[i] > bnd or Surf.node4P[i] > bnd:
					area = AreaFunction(Surf, i, bnd)*10000
				else:
					area = 0.0
				sumArea = sumArea + area
			i = i + 1
		AREAofeachRIB.append(sumArea)
		print '      	* Contact Area     (cm^2) : ', round(sumArea,3)
		if TotalCpress == 0:
			print '      	* Contact force    (N)    :  0.0'
		else:
			print '      	* Contact force    (N)    : ', round((sumArea/10000*TotalCpress/len(EachRibLatY)),3)
	#-------------------------------------------------------------------------------------------------------------------#
		SPAN = [];SPAN.append([0,0])
		SPAN[0] = Division()
		Xspan = SPAN[0][0]
		Yspan = SPAN[0][1]
		del SPAN
		minX=100;maxX=-100
		minY=100;maxY=-100
		i = 0
		while i<len(DeformNode.nodelabel):
			if DeformNode.x[i] > maxX:  maxX = DeformNode.x[i]
			if DeformNode.x[i] < minX:  minX = DeformNode.x[i]
			if DeformNode.y[i] > maxY:  maxY = DeformNode.y[i]
			if DeformNode.y[i] < minY:  minY = DeformNode.y[i]
			i = i + 1
		minX = minX - 0.003; maxX = maxX + 0.003
		minY = minY - 0.003; maxY = maxY + 0.003

		i = 0; j = 0
		dxx = (maxX-minX)/10
		p1 = 0.0
		eachGRV = []
		while i < len(sortEachRibLatY)-1:
			yy    = (sortEachRibLatY[i][0]+sortEachRibLatY[i+1][0])/2.0
			isnot = 0
			j     = 0
			while j < 10:
				xx = minX + dxx*j
				pp = InterpolateFunction(EachRibContPatch, xx, yy, 0, 0)
				if pp[0] > 0.0:
					isnot = 1
				j = j + 1
			if isnot == 1:
				eachGRV.append([yy,isnot])
			i = i + 1
		if TotalCpress == 0:
			GRV.append([0.0,0.0])
			GRV.append([0.0,0.0])
		else:
			GRV.append([eachGRV[0][0],0.0])
			GRV.append([eachGRV[-1][0],0.0])
			ContRib.append(1)
		RibNo = RibNo + 1
	print '	*** Number of ribs in contact with the ground :', len(ContRib)
	del eachGRV
	del ListRibNodes
	del EachRibLatY
	### [End] Find Groove position for each rib ###
	###############################################
	###############################################
	# *******************************************************************
	# 1. define a temporary region to make the grid map
	# 2. find the surface element position of the grid point
	# 3. Calculate the interpolated pressure of the grid point
	# *******************************************************************
	dX = (maxX-minX)/Xspan
	dY = (maxY-minY)/Yspan

	CNTLENofRIB = []
	maxRibXY = []
	temp = []
	j = 0
	while j < len(GRV)/2:
		CNTLENofRIB.append([0.0,0.0,0.0])
		maxRibXY.append([0.0,0.0])
		j = j + 1

	CpressPlot = [[(0,0,0) for col in range(Yspan)] for row in range(Xspan)]
	CforcePlot = [[(0,0,0) for col in range(Yspan)] for row in range(Xspan)]
	III = 0; JJJ = 0
	# *******************************************************************
	#print '6. Interpolating at a grid point!'
	# *******************************************************************
	if pointFileName =="": 
		pointFileName = strJobDir + '/' + lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-ContactShapePoint.dat'

	dispFile = open(pointFileName,'w')
	TmpCpress = []
	TmpCpress.append([0.0,-1])
	TmpCpressSlip = []
	TmpCpressSlip.append([0.0,-1])
	UpperXVal = [];UpperYVal = [];UpperValCount = 0
	LowerXVal = [];LowerYVal = [];LowerValCount = 0
	# *******************************************************************
	#print '  6.1. Interpolating Pressure Values of a grid point!'
	# *******************************************************************
	minYinEachY = 0.0; maxYinEachY = 0.0
	minYKKK = 100; maxYKKK = -100
	while JJJ<Yspan:
		minXinEachX = 0.0; maxXinEachX = 0.0
		minXKKK = 100; maxXKKK = -100
		Y = minY + dY*JJJ
		KKK = 0
		while KKK<Xspan:
			TmpCpress[0]= [0,-1]
			TmpCpressSlip[0]= [0,-1]
			X = minX + dX*KKK
			TmpCpress[0] = InterpolateFunction(ContPatch, X, Y, KKK, JJJ)
			TmpCpressSlip[0] = InterpolateFunction(ContPatchSlip, X, Y, KKK, JJJ)
			CpressPlot[KKK][JJJ]= (X, Y, TmpCpressSlip[0][0])
			#CpressPlot[KKK][JJJ]= (X, Y, TmpCpress[0][0])
			CforcePlot[KKK][JJJ]= (X, Y, TmpCpress[0][0]*(dX*dY))
			if TmpCpress[0][0] > bnd:
				if X < minXinEachX: minXinEachX = X; minXKKK = KKK
				if X > maxXinEachX: maxXinEachX = X; maxXKKK = KKK
				if Y < minYinEachY: minYinEachY = Y; minYKKK = KKK
				if Y > maxYinEachY: maxYinEachY = Y; maxYKKK = KKK
			KKK = KKK + 1
		if minXinEachX != 0.0:
			dispFile.writelines('%10d\t%10d\t%3.7f\t%3.7f\t\n' % (JJJ, minXKKK, Y, minXinEachX))
			LowerXVal.append(Y); LowerYVal.append(minXinEachX);LowerValCount = LowerValCount + 1
		if maxXinEachX != 0.0:
			dispFile.writelines('%10d\t%10d\t%3.7f\t%3.7f\t\n' % (JJJ, maxXKKK, Y, maxXinEachX))
			#if math.fabs(Y) < 1.0e-6: Y = 0
			UpperXVal.append(Y); UpperYVal.append(maxXinEachX);UpperValCount = UpperValCount + 1
		j = 0; k = j; maxLen = math.fabs(maxXinEachX-minXinEachX)
		while j<len(GRV)/2:
			k = j*2
			if Y >= GRV[k][0] and Y <= GRV[k+1][0]:
				if CNTLENofRIB[j][2] <= maxLen:
					CNTLENofRIB[j][0] = minXinEachX
					CNTLENofRIB[j][1] = maxXinEachX
					CNTLENofRIB[j][2] = maxLen
					maxRibXY[j][0] = Y
					maxRibXY[j][1] = maxLen
			j = j + 1
		JJJ = JJJ + 1
	
	UpXVal = []; UpYVal = []
	LoXVal = []; LoYVal = []

	TotArea  = 0.0
	TotYdist = maxYinEachY-minYinEachY
	Ydist05  = minYinEachY + 0.050*TotYdist
	Ydist125 = minYinEachY + 0.125*TotYdist
	Ydist15  = minYinEachY + 0.150*TotYdist
	Ydist25  = minYinEachY + 0.250*TotYdist
	Ydist375 = minYinEachY + 0.375*TotYdist
	Ydist50  = minYinEachY + 0.500*TotYdist
	Ydist625 = minYinEachY + 0.625*TotYdist
	Ydist75  = minYinEachY + 0.750*TotYdist
	Ydist775 = minYinEachY + 0.775*TotYdist
	Ydist80  = minYinEachY + 0.800*TotYdist
	Ydist825 = minYinEachY + 0.825*TotYdist
	Ydist85  = minYinEachY + 0.850*TotYdist
	Ydist875 = minYinEachY + 0.875*TotYdist
	Ydist90  = minYinEachY + 0.900*TotYdist
	Ydist925 = minYinEachY + 0.925*TotYdist
	Ydist95  = minYinEachY + 0.950*TotYdist
	Ydist975 = minYinEachY + 0.975*TotYdist
	#-------------------------------------------------------------------------------------------------------------------#
	InnerGRV = GRV[1][0]
	OuterGRV = GRV[-2][0]
	#-------------------------------------------------------------------------------------------------------------------#
	i = 0
	while i < UpperValCount:
		if UpperXVal[i] < maxYinEachY-0.005 and UpperXVal[i] > minYinEachY+0.005:
			UpXVal.append(UpperXVal[i]);UpYVal.append(UpperYVal[i])
		if i<UpperValCount-1:
			if UpperXVal[i+1] < minYinEachY+0.005:
				TotArea = TotArea + 0.5*(UpperXVal[i+1]-UpperXVal[i])*(UpperYVal[i+1]+UpperYVal[i])
			if UpperXVal[i] > maxYinEachY-0.005:
				TotArea = TotArea + 0.5*(UpperXVal[i+1]-UpperXVal[i])*(UpperYVal[i+1]+UpperYVal[i])
		i = i + 1
	#-------------------------------------------------------------------------------------------------------------------#
	i = 0
	while i < LowerValCount:
		if LowerXVal[i] < maxYinEachY-0.005 and LowerXVal[i] > minYinEachY+0.005:
			LoXVal.append(LowerXVal[i]);LoYVal.append(LowerYVal[i])
		i = i + 1

	j = 0
	maxCNTLength = 0.0
	while j < len(GRV)/2:
		k = j * 2
		if CNTLENofRIB[j][2]*1000 > maxCNTLength:
			maxCNTLength = CNTLENofRIB[j][2]*1000
			LowerMaxCNTLength = CNTLENofRIB[j][0]*-1
			UpperMaxCNTLength = CNTLENofRIB[j][1]
		j = j + 1

	CenRibLength = 0.0
	maxUpperXVal = max(UpperXVal)
	minUpperXVal = min(UpperXVal)
	maxLowerXVal = max(LowerXVal)
	minLowerXVal = min(LowerXVal)
	if maxUpperXVal > maxLowerXVal:
		maxUpLoX = maxUpperXVal
	else:
		maxUpLoX = maxLowerXVal
		
	if minUpperXVal < minLowerXVal:
		minUpLoX = minUpperXVal
	else:
		minUpLoX = minLowerXVal
	maxYCen = ((maxUpLoX - minUpLoX)/2) + minUpLoX
	if len(ContRib) % 2 == 1:
		maxXCen = 100; minXCen = 100
		for i in range(len(UpperXVal)):
			if abs(maxYCen - UpperXVal[i]) < 1.0e-6:
				maxYCen = UpperXVal[i]
				maxXCen = UpperYVal[i]
		for i in range(len(LowerXVal)):
			if LowerXVal[i] == maxYCen:
				minXCen = LowerYVal[i]
		CenRibLength = (maxXCen - minXCen)*1000
		if maxXCen == 100 or minXCen == 100:
			CenRibLength = maxRibXY[len(ContRib)/2][1]*1000

	elif len(ContRib) % 2 == 0:
		X0 = maxYCen
		X1 = maxRibXY[(len(ContRib)/2)-1][0]
		Y1 = maxRibXY[(len(ContRib)/2)-1][1]
		X2 = maxRibXY[len(ContRib)/2][0]
		Y2 = maxRibXY[len(ContRib)/2][1]
		CenRibLength = ((Y2-Y1)*(X0-X1)/(X2-X1) + Y1)*1000
	#-------------------------------------------------------------------------------------------------------------------#
	dispFile.close()
	# *******************************************************************
	#print '  6.2 Polynomial regression Calculation for N degree !'
	# *******************************************************************
	print '\n'
	print '** Polynomial regression Calculation for Contact Length & Total Contact Area'
	print "	* Processing of the 'UPPER' XY data"
	UpLow = 1
	Ndeg = 7
	brkRR = 0
	RR = 0.80
	ValforRSQRT = []
	ValforRSQRT.append([0.0,0.0])

	Xmatrix = []
	i = 0
	while i<Ndeg:
		Xmatrix.append(0.0)
		i = i + 1

	iterationNo = 1
	PrevRR = 0.0
	while brkRR == 0:
		RSQRT = 0.0
		AVGY = 0.0
		i = 0
		while i < len(UpXVal):
			AVGY = AVGY + UpYVal[i]
			i = i + 1
		AVGY = AVGY/len(UpXVal)
		SSQRT = 0.0

		i = 0
		while i < len(UpXVal):
			SSQRT = SSQRT + pow((UpYVal[i]-AVGY),2)
			i = i + 1
	
		print '      - During ', iterationNo,' iteration for Curve Fitting!'
		iterationNo = iterationNo + 1
		ValforRSQRT[0]=GaussElimination(Xmatrix, Ndeg, UpXVal, UpYVal, len(UpXVal), UpLow)
		RR = 1 - ValforRSQRT[0][0]/SSQRT

		if abs(RR - PrevRR) > 0.001 and (RR - PrevRR) > 0:
			PrevRR = RR
	
			if RR < 0.99:
				brkRR = 0
				i = 0
				while i < len(UpXVal):
					j = 0; Square = 0.0;diff = 0.0
					while j < Ndeg:
						Square = Square + Xmatrix[j]*pow(UpXVal[i],j)
						j = j + 1
					diff = Square - UpYVal[i]
					if math.fabs(diff) > ValforRSQRT[0][1] and diff > 0:
						del UpXVal[i]; del UpYVal[i]
					else:
						i = i + 1
			else:
				brkRR = -1
		else:
			brkRR = -1

	# *******************************************************************

	#-------------------------------------------------------------------------------------------------------------------#
	#-------------------------------------------------------------------------------------------------------------------#
	print "	* Processing of the 'LOWER' XY data"
	UpLow = -1
	Ndeg = 7
	brkRR = 0
	RR = 0.80
	ValforRSQRT = []
	ValforRSQRT.append([0.0,0.0])

	XmatrixLow = []
	i = 0
	while i<Ndeg:
		XmatrixLow.append(0.0)
		i = i + 1

	iterationNo = 1
	PrevRR = 0.0
	while brkRR == 0:
		RSQRT = 0.0
		AVGY = 0.0
		i = 0
		while i < len(LoXVal):
			AVGY = AVGY + LoYVal[i]
			i = i + 1
		AVGY = AVGY/len(LoXVal)
		SSQRT = 0.0

		i = 0
		while i < len(LoXVal):
			SSQRT = SSQRT + pow((LoYVal[i]-AVGY),2)
			i = i + 1
	
		print '      - During ', iterationNo,' iteration for Curve Fitting!'
		iterationNo = iterationNo + 1
		ValforRSQRT[0]=GaussElimination(XmatrixLow, Ndeg, LoXVal, LoYVal, len(LoXVal), UpLow)
		RR = 1 - ValforRSQRT[0][0]/SSQRT

		if abs(RR - PrevRR) > 0.001:
			PrevRR = RR
	
			if RR < 0.99:
				brkRR = 0
				i = 0
				while i < len(LoXVal):
					j = 0; Square = 0.0;diff = 0.0
					while j < Ndeg:
						Square = Square + XmatrixLow[j]*pow(LoXVal[i],j)
						j = j + 1
					diff = Square - LoYVal[i]
					if math.fabs(diff) > ValforRSQRT[0][1] and diff < 0:
						del LoXVal[i]; del LoYVal[i]
					else:
						i = i + 1
			else:
				brkRR = -1
		else:
			brkRR = -1
	#-------------------------------------------------------------------------------------------------------------------#
	#-------------------------------------------------------------------------------------------------------------------#

	i = 0
	while i<len(UpXVal):
		if i<len(UpXVal)-1:
			prevY = 0.0; nextY = 0.0
			j = 0
			while j<Ndeg:
				prevY = prevY + Xmatrix[j]*pow(UpXVal[i],j)
				nextY = nextY + Xmatrix[j]*pow(UpXVal[i+1],j)
				j = j + 1
			TotArea = TotArea + 0.5*(UpXVal[i+1]-UpXVal[i])*(nextY+prevY)
		i = i + 1
	TotArea = TotArea*10000*2
	Ldist05   = 0.0
	Ldist125  = 0.0
	Ldist15   = 0.0
	Ldist25   = 0.0
	Ldist375  = 0.0
	Ldist50   = 0.0
	Ldist625  = 0.0
	Ldist75   = 0.0
	Ldist775  = 0.0
	Ldist80   = 0.0
	Ldist825  = 0.0
	Ldist85   = 0.0
	Ldist875  = 0.0
	Ldist90   = 0.0
	Ldist925  = 0.0
	Ldist95   = 0.0
	Ldist975  = 0.0
	#-------------------------------------------------------------------------------------------------------------------#
	Ldist05Low  = 0.0
	Ldist125Low = 0.0
	Ldist15Low  = 0.0
	Ldist25Low  = 0.0
	Ldist375Low = 0.0
	Ldist50Low  = 0.0
	Ldist625Low = 0.0
	Ldist75Low  = 0.0
	Ldist775Low = 0.0
	Ldist80Low  = 0.0
	Ldist825Low = 0.0
	Ldist85Low  = 0.0
	Ldist875Low = 0.0
	Ldist90Low  = 0.0
	Ldist925Low = 0.0
	Ldist95Low  = 0.0
	Ldist975Low = 0.0
	LdistInnerGRVUpper  = 0.0
	LdistOuterGRVUpper  = 0.0
	LdistInnerGRVLower  = 0.0
	LdistOuterGRVLower  = 0.0
	#-------------------------------------------------------------------------------------------------------------------#	
	j = 0
	while j<Ndeg:
		Ldist05  = Ldist05  + Xmatrix[j]*pow(Ydist05,j)
		Ldist125 = Ldist125 + Xmatrix[j]*pow(Ydist125,j)
		Ldist15  = Ldist15  + Xmatrix[j]*pow(Ydist15,j)
		Ldist25  = Ldist25  + Xmatrix[j]*pow(Ydist25,j)
		Ldist375 = Ldist375 + Xmatrix[j]*pow(Ydist375,j)
		Ldist50  = Ldist50  + Xmatrix[j]*pow(Ydist50,j)
		Ldist625 = Ldist625 + Xmatrix[j]*pow(Ydist625,j)
		Ldist75  = Ldist75  + Xmatrix[j]*pow(Ydist75,j)
		Ldist775 = Ldist775 + Xmatrix[j]*pow(Ydist775,j)
		Ldist80  = Ldist80  + Xmatrix[j]*pow(Ydist80,j)
		Ldist825 = Ldist825 + Xmatrix[j]*pow(Ydist825,j)
		Ldist85  = Ldist85  + Xmatrix[j]*pow(Ydist85,j)
		Ldist875 = Ldist875 + Xmatrix[j]*pow(Ydist875,j)
		Ldist90  = Ldist90  + Xmatrix[j]*pow(Ydist90,j)
		Ldist925 = Ldist925 + Xmatrix[j]*pow(Ydist925,j)
		Ldist95  = Ldist95  + Xmatrix[j]*pow(Ydist95,j)
		Ldist975 = Ldist975 + Xmatrix[j]*pow(Ydist975,j)
	#-------------------------------------------------------------------------------------------------------------------#
		Ldist05Low  = Ldist05Low  + XmatrixLow[j]*pow(Ydist05,j)
		Ldist125Low = Ldist125Low + XmatrixLow[j]*pow(Ydist125,j)
		Ldist15Low  = Ldist15Low  + XmatrixLow[j]*pow(Ydist15,j)
		Ldist25Low  = Ldist25Low  + XmatrixLow[j]*pow(Ydist25,j)
		Ldist375Low = Ldist375Low + XmatrixLow[j]*pow(Ydist375,j)
		Ldist50Low  = Ldist50Low  + XmatrixLow[j]*pow(Ydist50,j)
		Ldist625Low = Ldist625Low + XmatrixLow[j]*pow(Ydist625,j)
		Ldist75Low  = Ldist75Low  + XmatrixLow[j]*pow(Ydist75,j)
		Ldist775Low = Ldist775Low + XmatrixLow[j]*pow(Ydist775,j)
		Ldist80Low  = Ldist80Low  + XmatrixLow[j]*pow(Ydist80,j)
		Ldist825Low = Ldist825Low + XmatrixLow[j]*pow(Ydist825,j)
		Ldist85Low  = Ldist85Low  + XmatrixLow[j]*pow(Ydist85,j)
		Ldist875Low = Ldist875Low + XmatrixLow[j]*pow(Ydist875,j)
		Ldist90Low  = Ldist90Low  + XmatrixLow[j]*pow(Ydist90,j)
		Ldist925Low = Ldist925Low + XmatrixLow[j]*pow(Ydist925,j)
		Ldist95Low  = Ldist95Low  + XmatrixLow[j]*pow(Ydist95,j)
		Ldist975Low = Ldist975Low + XmatrixLow[j]*pow(Ydist975,j)
		LdistInnerGRVUpper  = LdistInnerGRVUpper + Xmatrix[j]*pow(InnerGRV,j)
		LdistOuterGRVUpper  = LdistOuterGRVUpper + Xmatrix[j]*pow(OuterGRV,j)
		LdistInnerGRVLower  = LdistInnerGRVLower + XmatrixLow[j]*pow(InnerGRV,j)
		LdistOuterGRVLower  = LdistOuterGRVLower + XmatrixLow[j]*pow(OuterGRV,j)
	#-------------------------------------------------------------------------------------------------------------------#
		j = j + 1
	#-------------------------------------------------------------------------------------------------------------------#
	LdistInnerGRV = LdistInnerGRVUpper - LdistInnerGRVLower
	LdistOuterGRV = LdistOuterGRVUpper - LdistOuterGRVLower
	if InnerGRV == 0.0:
		LdistInnerGRV = 0.0
	if OuterGRV == 0.0:
		LdistOuterGRV = 0.0
	#-------------------------------------------------------------------------------------------------------------------#
	#del Xmatrix
	del ValforRSQRT
	#del UpXVal; del UpYVal
	del LowerXVal;del LowerYVal
	del UpperXVal;del UpperYVal
	if pressFileName=='':
		pressFileName = strJobDir + '/' + lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-CpressAlongCenter.txt'
	Wdist15 = 0.0; Wdist25 = 0.0; Wdist50 = 0.0; Wdist75 = 0.0; Wdist85 = 0.0; WdistMax= 0.0
	dispFile = open(pressFileName,'w')
	maxWdist15 = 0.0; minWdist15 = 0.0; maxWdist25 = 0.0; minWdist25 = 0.0; maxWdist50 = 0.0; minWdist50 = 0.0; maxWdist75 = 0.0; minWdist75 = 0.0; maxWdist85 = 0.0; minWdist85 = 0.0;
	JJJ = 0
	while JJJ<Yspan:
		Y = minY + dY*JJJ
		TmpCpressSlip[0] = InterpolateFunction(ContPatchSlip, 0.0, Y, 0, JJJ)
		if TmpCpressSlip[0][0] > bnd:
			if Y >= maxWdist50:
				maxWdist50 = Y
			if Y <= minWdist50:
				minWdist50 = Y
		dispFile.writelines('%3.7f\t%3.7f\t%3.7f\n' % (0.0, Y, TmpCpressSlip[0][0]))
		TmpCpressSlip[0] = InterpolateFunction(ContPatchSlip, UpperMaxCNTLength*0.7, Y, 0, JJJ)
		if TmpCpressSlip[0][0] > bnd:
			if Y >= maxWdist15:
				maxWdist15 = Y
			if Y <= minWdist15:
				minWdist15 = Y
		TmpCpressSlip[0] = InterpolateFunction(ContPatchSlip, LowerMaxCNTLength*-0.7, Y, 0, JJJ)
		if TmpCpressSlip[0][0] > bnd:
			if Y >= maxWdist85:
				maxWdist85 = Y
			if Y <= minWdist85:
				minWdist85 = Y
		TmpCpressSlip[0] = InterpolateFunction(ContPatchSlip, UpperMaxCNTLength*0.5, Y, 0, JJJ)
		if TmpCpressSlip[0][0] > bnd:
			if Y >= maxWdist25:
				maxWdist25 = Y
			if Y <= minWdist25:
				minWdist25 = Y
		TmpCpressSlip[0] = InterpolateFunction(ContPatchSlip, LowerMaxCNTLength*-0.5, Y, 0, JJJ)
		if TmpCpressSlip[0][0] > bnd:
			if Y >= maxWdist75:
				maxWdist75 = Y
			if Y <= minWdist75:
				minWdist75 = Y
		JJJ = JJJ + 1
	dispFile.close()

	Wdist15  = (maxWdist15  - minWdist15) *1000
	Wdist25  = (maxWdist25  - minWdist25) *1000
	Wdist50  = (maxWdist50  - minWdist50) *1000
	Wdist75  = (maxWdist75  - minWdist75) *1000
	Wdist85  = (maxWdist85  - minWdist85) *1000

	if Wdist15  >= WdistMax:
		WdistMax = Wdist15
	if Wdist25  >= WdistMax:
		WdistMax = Wdist25
	if Wdist50  >= WdistMax:
		WdistMax = Wdist50
	if Wdist75  >= WdistMax:
		WdistMax = Wdist75
	if Wdist85  >= WdistMax:
		WdistMax = Wdist85
	#Ldist05  = Ldist05 *1000*2
	#Ldist125 = Ldist125*1000*2
	#Ldist15  = Ldist15 *1000*2
	#Ldist25  = Ldist25 *1000*2
	#Ldist375 = Ldist375*1000*2
	#Ldist50  = Ldist50 *1000*2
	#Ldist625 = Ldist625*1000*2
	#Ldist75  = Ldist75 *1000*2
	#Ldist85  = Ldist85 *1000*2
	#Ldist875 = Ldist875*1000*2
	#Ldist95  = Ldist95 *1000*2
	#-------------------------------------------------------------------------------------------------------------------#
	Ldist15  = (Ldist15  + abs(Ldist15Low))  *1000
	Ldist25  = (Ldist25  + abs(Ldist25Low))  *1000
	Ldist50  = (Ldist50  + abs(Ldist50Low))  *1000
	Ldist75  = (Ldist75  + abs(Ldist75Low))  *1000
	Ldist85  = (Ldist85  + abs(Ldist85Low))  *1000
	LdistInnerGRV  = LdistInnerGRV *1000
	LdistOuterGRV  = LdistOuterGRV *1000
	#-------------------------------------------------------------------------------------------------------------------#
	if valuesFileName =="":
		valuesFileName = strJobDir + '/' + lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-CharacteristicValues.txt'
	presFile = open(valuesFileName,'w')

	presFile.writelines('Xspan   Yspan        minX        maxX        minY        maxY      deltaX      deltaY      vload\n')
	presFile.writelines('%4d%8d%16.8f%12.8f%12.8f%12.8f%12.8f%12.8f%7d\n' % (Xspan, Yspan, minX, maxX, minY, maxY, dX, dY, vload))
	presFile.writelines('$$\n')

	JJJ = 0
	KKK = 0
	sumFY = 0.0
	if ArgIn ==1: 
		contourDatFileName = contourFileName + '-Contour.dat'
	else:
		contourDatFileName = strJobDir + '/' + lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-Contour.dat'
	contourFile = open(contourDatFileName, 'w')
	tmpcontourPress= []
	while KKK<Xspan:
		JJJ = 0
		while JJJ<Yspan:
			contourFile.writelines('%3.7f, %3.7f, %3.7f\n' % (CpressPlot[KKK][JJJ][0],CpressPlot[KKK][JJJ][1],CpressPlot[KKK][JJJ][2]))
			tmpcontourPress.append(CpressPlot[KKK][JJJ][2])
			JJJ = JJJ + 1
		KKK = KKK + 1
	JJJ = 0
	while JJJ<Yspan:
		KKK=0
		presFile.writelines('%3.7f\t%3.7f\t' % (CpressPlot[KKK][JJJ][0], CpressPlot[KKK][JJJ][1]))
		sumFY = sumFY + CforcePlot[KKK][JJJ][2]
		KKK = KKK +1
		while KKK<Xspan:
			if CpressPlot[KKK][JJJ][2] > bnd:
				presFile.writelines('%3.7f\t' % (CpressPlot[KKK][JJJ][2]))
			else:
				presFile.writelines('%3.7f\t' % (0.0))
			sumFY = sumFY + CforcePlot[KKK][JJJ][2]
			KKK = KKK +1
		presFile.writelines('\n')
		JJJ = JJJ + 1
	presFile.close()
	contourFile.close()
	del CpressPlot

	if areaFileName =="":
		areaFileName = strJobDir + '/' + lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-ContactSurfaceArea.txt'
	areaFile = open(areaFileName,'w')
	i = 0;j = 0
	sumArea = 0.0
	oset = 0.001
	AREAofRIB = []
	while j<len(GRV)/2:
		AREAofRIB.append(0.0)
		j = j + 1
	while i < len(Surf.surflabel):
		maxSurfy = -100.0
		CURZ = Surf.node1Y[i]*CAMBA;DELTZ = MAXZtoROADZ - CURZ;SurfN1Z = Surf.node1Z[i]+DELTZ
		CURZ = Surf.node2Y[i]*CAMBA;DELTZ = MAXZtoROADZ - CURZ;SurfN2Z = Surf.node2Z[i]+DELTZ
		CURZ = Surf.node3Y[i]*CAMBA;DELTZ = MAXZtoROADZ - CURZ;SurfN3Z = Surf.node3Z[i]+DELTZ
		CURZ = Surf.node4Y[i]*CAMBA;DELTZ = MAXZtoROADZ - CURZ;SurfN4Z = Surf.node4Z[i]+DELTZ
		if SurfN1Z<MAXZ+oset and SurfN2Z<MAXZ+oset and SurfN3Z<MAXZ+oset and SurfN4Z<MAXZ+oset:
			if Surf.node1P[i]>=bnd and Surf.node2P[i]>=bnd and Surf.node3P[i]>=bnd and Surf.node4P[i]>=bnd:
				Forward = Surf.node1X[i]*Surf.node2Y[i]+Surf.node2X[i]*Surf.node3Y[i]+Surf.node3X[i]*Surf.node4Y[i]+Surf.node4X[i]*Surf.node1Y[i]
				Bacward = Surf.node2X[i]*Surf.node1Y[i]+Surf.node3X[i]*Surf.node2Y[i]+Surf.node4X[i]*Surf.node3Y[i]+Surf.node1X[i]*Surf.node4Y[i]
				area = 0.5*math.fabs(Forward-Bacward)*10000
			else:
				area = AreaFunction(Surf, i, bnd)*10000
		else:
			area = 0.0
		sumArea = sumArea + area
		if Surf.node1Y[i] >= maxSurfy: maxSurfy = Surf.node1Y[i]
		if Surf.node2Y[i] >= maxSurfy: maxSurfy = Surf.node2Y[i]
		if Surf.node3Y[i] >= maxSurfy: maxSurfy = Surf.node3Y[i]
		if Surf.node4Y[i] >= maxSurfy: maxSurfy = Surf.node4Y[i]
		areaFile.writelines('%8d\t%8d\t%8d\t%8d\t%5.3e\t%5.3e\t%5.3e\t%5.3e\t%5.3e\t%7.7f\n' % 
							(Surf.node1[i],Surf.node2[i],Surf.node3[i],Surf.node4[i],
							Surf.node1P[i],Surf.node2P[i],Surf.node3P[i],Surf.node4P[i],maxSurfy,area))
		j = 0; k = j
		while j < len(GRV)/2:
			k = j * 2
			if maxSurfy >= GRV[k][0] and maxSurfy <= GRV[k+1][0]:
				AREAofRIB[j] = AREAofRIB[j] + area
			j = j + 1
		i = i + 1
	areaFile.close()
	if infoFileName=="":
		infoFileName = strJobDir + '/' + lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-FPC.txt'
	dispFile = open(infoFileName,'w')
	if ProductLine == 'PCR' or ProductLine == 'LTR':
		if len(ContRib) % 2 == 0:
			dispFile.writelines('ContactLength(mm) max/center/25%%/75%%=\t%5.1f/%5.1f/%5.1f/%5.1f\n' % (maxCNTLength,CenRibLength,Ldist25,Ldist75))
		else:
			#dispFile.writelines('ContactLength(mm) max/center/25%%/75%%=\t%5.1f/%5.1f/%5.1f/%5.1f\n' % (maxCNTLength,Ldist50,Ldist25,Ldist75))
			dispFile.writelines('ContactLength(mm) max/center/25%%/75%%=\t%5.1f/%5.1f/%5.1f/%5.1f\n' % (maxCNTLength,CenRibLength,Ldist25,Ldist75))
		dispFile.writelines('ContactWidth(mm)  max/center/25%%/75%%=\t%5.1f/%5.1f/%5.1f/%5.1f\n' % (WdistMax,Wdist50,Wdist25,Wdist75))
		dispFile.writelines('SquareRatio(%%)=\t%5.1f\n' % ((Ldist25+Ldist75)/(2*Ldist50)*100))
	else:
		if len(ContRib) % 2 == 0:
			dispFile.writelines('ContactLength(mm) max/center/15%%/85%%=\t%5.1f/%5.1f/%5.1f/%5.1f\n' % (maxCNTLength,CenRibLength,Ldist15,Ldist85))
		else:
			#dispFile.writelines('ContactLength(mm) max/center/15%%/85%%=\t%5.1f/%5.1f/%5.1f/%5.1f\n' % (maxCNTLength,Ldist50,Ldist15,Ldist85))
			dispFile.writelines('ContactLength(mm) max/center/15%%/85%%=\t%5.1f/%5.1f/%5.1f/%5.1f\n' % (maxCNTLength,CenRibLength,Ldist15,Ldist85))
		dispFile.writelines('ContactWidth(mm)  max/center/15%%/85%%=\t%5.1f/%5.1f/%5.1f/%5.1f\n' % (WdistMax,Wdist50,Wdist15,Wdist85))
		dispFile.writelines('SquareRatio(%%)=\t%5.1f\n' % ((Ldist15+Ldist85)/(2*Ldist50)*100))
	i = 0;ActArea = 0.0
	while i < len(GRV)/2:
		ActArea = ActArea + AREAofeachRIB[i]
		i = i + 1
	if len(RibNodes2D) == 1:
		dispFile.writelines('ContactRatio(%%)=\t%5.1f\n' % (ActArea/ActArea*100))
	else:
		dispFile.writelines('ContactRatio(%%)=\t%5.1f\n' % (ActArea/TotArea*100))
	dispFile.writelines('Roundness(%%)=\t%5.1f\n' % ((TotArea*100)/(Ldist50*WdistMax)*100))
	dispFile.writelines('ActualContactArea(cm^2)=\t%5.1f\n' % ActArea)
	if len(RibNodes2D) == 1:
		dispFile.writelines('TotalContactArea(cm^2)=\t%5.1f\n' % ActArea)
	else:
		dispFile.writelines('TotalContactArea(cm^2)=\t%5.1f\n' % TotArea)
	dispFile.writelines('DetailedContactLength(mm) 15/25/50/75/85=\t%5.1f/%5.1f/%5.1f/%5.1f/%5.1f\n' % (Ldist15,Ldist25,CenRibLength,Ldist75,Ldist85))
	dispFile.writelines('DetailedContactWidth(mm) 15/25/50/75/85=\t%5.1f/%5.1f/%5.1f/%5.1f/%5.1f\n' % (Wdist15,Wdist25,Wdist50,Wdist75,Wdist85))
	dispFile.writelines('\n')
	dispFile.writelines('From\tTo\tContact Length(mm)\tContact Area(cm^2)\tContact Pressure(pa)\tContact Force(N)\n')
	eachribCforce = []
	j = 0
	while j<len(GRV)/2:
		k = j*2
		if AREAofeachRIB[j] == 0:
			dispFile.writelines('%s\t%s\t%s\t%s\t%s\t%s\n' % 
				('0.0000', '0.0000', '0.0000', '0.0000', '0.0000', '0.0000'))
			eachribCforce.append(0.0000)
		else:
			dispFile.writelines('%7.4f\t%7.4f\t%7.4f\t%7.4f\t%7.4f\t%7.4f\n' % 
				(GRV[k][0]*1000, GRV[k+1][0]*1000, CNTLENofRIB[j][2]*1000, AREAofeachRIB[j], RibCpress[j], AREAofeachRIB[j]/10000*RibCpress[j]/NumCpressNode[j]))
			eachribCforce.append(round((AREAofeachRIB[j]/10000*RibCpress[j]/NumCpressNode[j]),3))
		j = j + 1
	
	dispFile.writelines('\n')
	print 'In-Out', LdistInnerGRV, LdistOuterGRV
	dispFile.writelines('In-OutContactLength=\t%7.4f\n' % (LdistInnerGRV-LdistOuterGRV))
	dispFile.writelines('\n')
	dispFile.writelines('Reaction Force!\n') 
	historyFile = open(shistFileName,'r')
	historyline = historyFile.readlines()
	FY_ROAD = float(historyline[11].split(':')[-1].strip())
	FZ_ROAD = float(historyline[15].split(':')[-1].strip())
	historyFile.close()
	dispFile.writelines('Fy(Lateraldir.,N)=%7.4f\n' % FY_ROAD)
	dispFile.writelines('Fz(Verticaldir.,N)=%7.4f\n' % FZ_ROAD)
	dispFile.writelines('\n')
	dispFile.writelines('Success::Post::[Simulation Result] This simulation result was created successfully!!\n')
	dispFile.close()

	### [Start] Plot footshape image ###
	xis_array = []; xis_array.append(minX); xis_array.append(maxX)
	yis_array = []; yis_array.append(minY); yis_array.append(maxY)
	xis_array = np.array(xis_array)
	yis_array = np.array(yis_array)
	xis = np.linspace(np.amin(xis_array), np.amax(xis_array), Xspan)
	yis = np.linspace(np.amin(yis_array), np.amax(yis_array), Yspan)
	xis = xis - dY/2	# Longitudinal contour position correction
	yis = yis - dX/2	# Lateral contour position correction
	Y, X= np.meshgrid(yis, xis)
	contourPress = np.array(tmpcontourPress)
	CONTOURPRESS = contourPress.reshape((len(yis),len(xis)))
	zip(*CONTOURPRESS)
	if ProductLine == 'PCR' or ProductLine == 'LTR':
		levels = np.linspace(5e4, 5e5, 91)
	else:
		levels = np.linspace(1e5, 1e6, 91)
	fig, ax = plt.subplots()
	cs = ax.contourf(Y, X, CONTOURPRESS, levels, extend='max', antialiased=True)
	cbar = fig.colorbar(cs)
	ax.set_xlim(np.amin(X), np.amax(X))
	ax.set_ylim(np.amin(Y), np.amax(Y))
	ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
	ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
	ax.set_aspect('equal')

	PCRlim = 0.15
	LTRlim = 0.16
	TBRlim = 0.20

	if ProductLine == 'PCR':
		plt.suptitle('Contact Pressure(Pa) Distribution', fontsize=16, fontweight='bold')
		plt.xlim(-PCRlim, PCRlim)
		plt.xticks(np.linspace(-PCRlim, PCRlim, 7, endpoint=True))
		plt.xlabel('Lateral Position(m)')
		plt.ylim(-PCRlim, PCRlim)
		plt.yticks(np.linspace(-PCRlim, PCRlim, 7, endpoint=True))
		plt.ylabel('Longitudinal Position(m)')
	elif ProductLine == 'LTR':
		plt.suptitle('Contact Pressure(Pa) Distribution', fontsize=16, fontweight='bold')
		plt.xlim(-LTRlim, LTRlim)
		plt.xticks(np.linspace(-LTRlim, LTRlim, 7, endpoint=True))
		plt.xlabel('Lateral Position(m)')
		plt.ylim(-LTRlim, LTRlim)
		plt.yticks(np.linspace(-LTRlim, LTRlim, 7, endpoint=True))
		plt.ylabel('Longitudinal Position(m)')
	else:
		plt.suptitle('Contact Pressure(Pa) Distribution', fontsize=16, fontweight='bold')
		plt.xlim(-TBRlim, TBRlim)
		plt.xticks(np.linspace(-TBRlim, TBRlim, 7, endpoint=True))
		plt.xlabel('Lateral Position(m)')
		plt.ylim(-TBRlim, TBRlim)
		plt.yticks(np.linspace(-TBRlim, TBRlim, 7, endpoint=True))
		plt.ylabel('Longitudinal Position(m)')
	if ArgIn ==0:
		fig.savefig(lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-Footshape.png', dpi=200)  # results in 160x120 px image
	else:
		fig.savefig(contourFileName+ '-Footshape.png', dpi=200)  # results in 160x120 px image
	
	del xis_array, yis_array, tmpcontourPress
	### [End] Plot footshape image ###
	
	### [Start] Plot Fitting Curve image ###
	Xmin = min(UpXVal)
	Xmax = max(UpXVal)
	Space = len(UpXVal)
	
	x = np.linspace(Xmin, Xmax, Space)
	a = Xmatrix[6]
	b = Xmatrix[5]
	c = Xmatrix[4]
	d = Xmatrix[3]
	e = Xmatrix[2]
	f = Xmatrix[1]
	g = Xmatrix[0]
	
	y = func(x, a, b, c, d, e, f, g)
	
	if ProductLine == 'PCR':
		plt.xlim(-PCRlim, PCRlim)
		plt.ylim(-PCRlim, PCRlim)
	if ProductLine == 'LTR':
		plt.xlim(-LTRlim, LTRlim)
		plt.ylim(-LTRlim, LTRlim)
	if ProductLine == 'TBR':
		plt.xlim(-TBRlim, TBRlim)
		plt.ylim(-TBRlim, TBRlim)
	plt.plot(x, y, 'black')
	
	
	Xmin = min(LoXVal)
	Xmax = max(LoXVal)
	Space = len(LoXVal)
	x = np.linspace(Xmin, Xmax, Space)
	a = XmatrixLow[6]
	b = XmatrixLow[5]
	c = XmatrixLow[4]
	d = XmatrixLow[3]
	e = XmatrixLow[2]
	f = XmatrixLow[1]
	g = XmatrixLow[0]
	
	y = func(x, a, b, c, d, e, f, g)
	
	if ProductLine == 'PCR':
		plt.xlim(-PCRlim, PCRlim)
		plt.ylim(-PCRlim, PCRlim)
	if ProductLine == 'LTR':
		plt.xlim(-LTRlim, LTRlim)
		plt.ylim(-LTRlim, LTRlim)
	if ProductLine == 'TBR':
		plt.xlim(-TBRlim, TBRlim)
		plt.ylim(-TBRlim, TBRlim)
	plt.plot(x, y, 'black')
	
	if ProductLine == 'PCR':
		plt.xlim(-PCRlim, PCRlim)
		plt.ylim(-PCRlim, PCRlim)
	if ProductLine == 'LTR':
		plt.xlim(-LTRlim, LTRlim)
		plt.ylim(-LTRlim, LTRlim)
	if ProductLine == 'TBR':
		plt.xlim(-TBRlim, TBRlim)
		plt.ylim(-TBRlim, TBRlim)
	plt.scatter(UpXVal, UpYVal, 1, 'red')
	plt.scatter(LoXVal, LoYVal, 1, 'red')

	if ArgIn ==0:
		fig.savefig(lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-FittingCurve.png', dpi=200)
	else:
		fig.savefig(contourFileName + '-FittingCurve.png', dpi=200)
	### [End] Plot Fitting Curve image ###	
	### [Start] Plot the contact force graph of each rib ###
	y_value = eachribCforce
	
	fig, ax = plt.subplots()
	colors = ['salmon', 'orange', 'cadetblue', 'skyblue', 'orange', 'orangered']
	
	i = 0
	x_name = [];tick_val = []
	while i < len(y_value):
		x_name.append('Rib%s' %(i+1))
		tick_val.append(i)
		i = i + 1
	
	x = np.arange(len(x_name))
	y = np.array(y_value)
	
	n_groups = len(x_name)
	x_max = max(y_value)
	index = np.arange(n_groups)
	bar_width = 0.6
	
	plt.bar(index, y_value, bar_width, align='center', color = colors[2])
	ax.set_axisbelow(True)
	ax.yaxis.grid(True, color='gray', linestyle='dashed', linewidth=0.5)
	
	plt.plot(x,y)
	for i,j in zip(x,y):
		ax.annotate(str(j),xy=(i-0.35,j+100))
	
	plt.xlabel('Ribs listed in the right direction', fontweight='bold')
	plt.ylabel('Contact Force (N)', fontweight='bold')
	
	plt.xticks(tick_val, x_name)
	plt.title('Contact Force of each Rib', fontweight='bold')
	plt.xlim( -1, n_groups)
	plt.ylim( 0, x_max + 1000)
	if ArgIn ==0:
		fig.savefig(lstSnsInfo["AnalysisInformation"]["SimulationCode"] + '-ContactForce.png', dpi=200)  # results in 160x120 px image
	else:
		fig.savefig(contourFileName + '-ContactForce.png', dpi=200)  # results in 160x120 px image
	### [End] Plot the contact force graph of each rib ###

	# *******************************************************************
	# Memory delete
	# *******************************************************************
	del GRV
	del CNTLENofRIB
	del AREAofeachRIB
	del Node, Surf, DeformNode, ContPatch
	file.close()
	print "Complete!"
	# CheckExecution.getProgramTime(str(sys.argv[0]), "End")

if __name__ == "__main__":
	sfricFileName = ''
	CUTEInpFileName = ''
	pointFileName = ''
	pressFileName = ''
	valuesFileName = ''
	areaFileName = ''
	infoFileName = ''
	ArgIn = 0 
	for i, argv in enumerate(sys.argv) : 
		if i ==0: continue 
		args= argv.split("=")
		if "sns" in args[0].strip(): snsFile=args[1].strip()
		if "sfric" in args[0].strip(): sfricFileName=args[1].strip()
		if "result" in args[0].strip(): sfricResultFileName=args[1].strip()
		if "trd" in args[0].strip(): trdFileName=args[1].strip()
		if "shist" in args[0].strip(): shistFileName=args[1].strip()
		if "contour" in args[0].strip(): contourFileName=args[1].strip()
		if 'slip' in args[0].strip(): SlipAngle=float(args[1].strip())
		if 'load' in args[0].strip(): vload=float(args[1].strip())
		if 'product' in args[0].strip(): ProductLine=args[1].strip()
		if 'mesh' in args[0].strip(): CUTEInpFileName=args[1].strip()
		if 'point' in args[0].strip(): pointFileName=args[1].strip()
		if 'press' in args[0].strip(): pressFileName=args[1].strip()
		if 'value' in args[0].strip(): valuesFileName=args[1].strip()
		if 'area' in args[0].strip(): areaFileName=args[1].strip()
		if 'fpc' in args[0].strip(): infoFileName=args[1].strip()
	


	main(sfricFileName=sfricFileName, sfricResultFileName=sfricResultFileName, \
		trdFileName=trdFileName, shistFileName=shistFileName, contourFileName=contourFileName, SlipAngle=SlipAngle,\
	vload=vload, ProductLine=ProductLine,  CUTEInpFileName=CUTEInpFileName, \
		pointFileName=pointFileName, pressFileName=pressFileName, valuesFileName=valuesFileName,\
			 areaFileName=areaFileName,infoFileName=infoFileName)