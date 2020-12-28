***************************************************************************
*HEADING
*PARAMETER
PRESS =   2.2
OD =  638.7
LOAD_100 =   615
CAMBER_ANGLE = 0
SPEED = 80.0
Hz = (SPEED/3.6) / (3.14*OD/1000.0)
omega = (6.28*Hz) * (6.28*Hz)
** [omega : radian/sec]**2 = (2*3.14*Hz)**2
*************************************************************************
UNIT_CONV = 1000
PLATE_HT = OD/2 + 15.0
PRESSURE = PRESS * 9.81E-2 * (UNIT_CONV)**2
PLATE = PLATE_HT/UNIT_CONV
CAMBER = CAMBER_ANGLE * 3.141592654 / 180
CAMBER_HEIGHT = 0.5 * tan(CAMBER)
UPPER = PLATE + CAMBER_HEIGHT
LOWER = PLATE - CAMBER_HEIGHT
LOAD1 = LOAD_100*9.81
*************************************************************************
*PRE PRINT,ECHO=NO,MODEL=NO,HISTORY=NO
*SYMMETRIC MODEL GENERATION,REVOLVE,NODEOFF=4000, ELEMENTOFF=4000,TRANSPORT
0.0, 0.0, 0.0,    0.0, 1.0, 0.0
1.0, 0.0, 0.0
30.0, 30
 60.0,6, 1.0, CYLINDRICAL
180.0,12, 1.0, CYLINDRICAL
 60.0,6, 1.0, CYLINDRICAL
30.0, 30
*************************************************************************
*SYMMETRIC RESULTS TRANSFER,STEP=2
*NODE,NSET=NROAD
 99999991, 0.5, 0.0, 0.0
***SURFACE,TYPE=ELEMENT, NAME=ASURF
**CTB
*NODE
90000001, <LOWER>,-0.5,-0.5
90000002, <LOWER>,-0.5, 0.5
90000003, <UPPER>, 0.5, 0.5
90000004, <UPPER>, 0.5,-0.5
*ELEMENT, TYPE=R3D4, ELSET=EROAD
1999999,90000001,90000002,90000003,90000004
*RIGID BODY, REF NODE=99999991, ELSET=EROAD
*SURFACE, TYPE=ELEMENT, NAME=BSURF
EROAD, SPOS
*CONTACT PAIR,INTERACTION=GRATING
CONT,BSURF
*SURFACE INTERACTION,NAME=GRATING
*SURFACE BEHAVIOR, AUGMENTED LAGRANGE
 ,0.0, 1.0
*FRICTION
 0.3
*ELSET, ELSET=SEC, GENERATE
1, 4000, 1
*************************************************************************
*STEP,NLGEOM,INC=50
1: 3D inflation
*STATIC
0.5, 1.0
*CONTROLS,PARAMETERS=TIME INCREMENTATION
 8, 10, 9, 16, 10, 4, 12, 5, 6, 3
 0.50, 0.50, 0.50, 0.85, 0.50, 0.50, 1.50, 0.75
*BOUNDARY
NROAD,1,6
NRFLANGE,1,,
NRFLANGE,2,,0.10
NRFLANGE,3,6,
NLFLANGE,1,,
NLFLANGE,2,,-0.10
NLFLANGE,3,6,
*DSLOAD
PRESS,P, <PRESSURE>
*NODE PRINT, NSET=NROAD, TOTALS=YES, FREQUENCY=99
 U
*NODE PRINT, NSET=NFLANGE, TOTALS=YES, FREQUENCY=99
 RF
*OUTPUT,FIELD,FREQUENCY=99
*ELEMENT OUTPUT
 S,E,SINV,ENER
*ELEMENT OUTPUT,REBAR
 S,RBFOR,RBANG
*NODE OUTPUT
 U,RF,CF,COORD,
*CONTACT OUTPUT
 CSTRESS,CDISP,
*NODE FILE,FREQ=99
 COORD,U,
*EL FILE,REBAR,FREQ=99
 S,RBFOR,
*RESTART,WRITE,FREQUENCY=99
*END STEP
*************************************************************************
*STEP,NLGEOM,INC=50
2: Add displacement to Tire and Road
*STATIC
 0.5, 1.0
*CONTROLS,PARAMETERS=TIME INCREMENTATION
 8, 10, 9, 16, 10, 4, 12, 5, 6, 3
 0.50, 0.50, 0.50, 0.85, 0.50, 0.50, 1.50, 0.75
*CHANGE FRICTION,INTERACTION=RIML
*FRICTION
 1.0
*CHANGE FRICTION,INTERACTION=RIMR
*FRICTION
 1.0
*BOUNDARY
 NROAD,1,,-0.015
*END STEP
*************************************************************************
*STEP,INC=50,NLGEOM
3: Vertical Load 100
*STATIC
0.25, 1.0
*CONTROLS,PARAMETERS=TIME INCREMENTATION
 8, 10, 9, 16, 10, 4, 12, 5, 6, 3
 0.50, 0.50, 0.50, 0.85, 0.50, 0.50, 1.50, 0.75
*BOUNDARY,OP=NEW
 NROAD,2,6,
 NRFLANGE,1,,
 NRFLANGE,2,,0.10
 NRFLANGE,3,6,
 NLFLANGE,1,,
 NLFLANGE,2,,-0.10
 NLFLANGE,3,6,
*CLOAD
 NROAD,1,-<LOAD1>
*NODE PRINT, NSET=NROAD, TOTALS=YES, FREQUENCY=99
 U
*NODE PRINT, NSET=NFLANGE, TOTALS=YES, FREQUENCY=99
 RF
*OUTPUT,FIELD,FREQUENCY=99
*ELEMENT OUTPUT
 S,E,SINV,ENER
*ELEMENT OUTPUT,REBAR
 S,RBFOR,RBANG,RBROT
*NODE OUTPUT
 U,RF,CF,COORD,
*CONTACT OUTPUT
 CSTRESS,CDISP,
*NODE FILE,FREQ=99
 COORD,U,
*EL FILE, POSITION=CENTROIDAL, FREQUENCY=100
S,SINV,E,ENER,
*EL FILE,REBAR,FREQ=99
 S,RBFOR,
*RESTART,WRITE,FREQUENCY=99
*END STEP
***************************************************************************
*STEP,INC=50,NLGEOM
4: Vertical Load 100 + Centrifugal Load
*STATIC
0.25, 1.0
*CONTROLS,PARAMETERS=TIME INCREMENTATION
 8, 10, 9, 16, 10, 4, 12, 5, 6, 3
 0.50, 0.50, 0.50, 0.85, 0.50, 0.50, 1.50, 0.75
*DLOAD, OP=NEW
 ALLELSET, CENTRIF, <omega>, 0.0, 0.0, 0.0,   0.0, 1.0, 0.0
*NODE PRINT, NSET=NROAD, TOTALS=YES, FREQUENCY=99
 U
*NODE PRINT, NSET=NFLANGE, TOTALS=YES, FREQUENCY=99
 RF
*OUTPUT,FIELD,FREQUENCY=99
*ELEMENT OUTPUT
 S,E,SINV,ENER
*ELEMENT OUTPUT,REBAR
 S,RBFOR,RBANG,RBROT
*NODE OUTPUT
 U,RF,CF,COORD,
*CONTACT OUTPUT
 CSTRESS,CDISP,
*NODE FILE,FREQ=99
 COORD,U,
*EL FILE, POSITION=CENTROIDAL, FREQUENCY=100
S,SINV,E,ENER,
*EL FILE,REBAR,FREQ=99
 S,RBFOR,
*RESTART,WRITE,FREQUENCY=99
*END STEP
***************************************************************************
