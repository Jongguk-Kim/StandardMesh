#!/usr/bin/python
"""******************************************************************
	This is a Python script used in DOE/Optimization set-up.

	Purpose:
		Initialize response categories and valid xml file
		extensions from which responses are extracted.

	6/21/13 - SBK
		updated valid keyname for skstr step from "SSRoll Load:' to "Rolling Load:"
******************************************************************"""

respCategories = ['MEAS', 'DUR', 'FP', 'FAM', 'RR']

valid_xml_files = {
		   'MEAS'  : ['dim2d', 'kfac', 'sws'],
		   'DUR'   : ['skstr'],
		   'FP'    : ['kv', 'klkt', 'fpc'],
		   'FAM'   : ['dlr', 'cornforce'],
		   'RR'    : ['h_rr']
		  }

steps = {
         #MEAS
         'dim2d'    : ['ANALYSIS INFLATION'],
         'kfac'     : ['ANALYSIS INFLATION'],
         'sws'      : ['SW LATERAL STIFFNESS', 'SW RADIAL STIFFNESS', 'SW TWIST STIFFNESS'],
         #DUR
         'skstr'    : ['Static Load:', 'Rolling Load:'],
         #FP
         'kv'       : ['TARGET LOAD'],
         'klkt'     : ['TARGET LOAD'],
         'fpc'      : ['TARGET LOAD'],
         #FAM
         'dlr'      : ['SS ROLL SLIP ANGLE 0.0'],
         'cornforce': ['SS ROLL SLIP ANGLE 1.0'],
         #RR
         'h_rr'     : ['TARGET LOAD']
        }

respKeys = {
            #MEAS
            'dim2d'     : {'SW'				: 'maxsec',		#1
                           'OD'				: 'od',			#2
                           'TreadRadius'		: 'trad',		#3
                           'BreakPointDrop'		: 'bpdrop',		#4
                           'ShoulderDrop'		: 'sdrop',		#5
                           'PlyPeriphery'		: 'plyperiph'		#6
		          },
            'kfac'      : {'K-Factor'			: 'kfac'		#7
                          },
            'sws'       : {'Lateral Sidewall Stiffness'	: 'klsws',		#8
                           'Radial Sidewall Stiffness'	: 'krsws',		#9
                           'Twist Sidewall Stiffness'	: 'ktsws'		#10
                          },
            #DUR
            'skstr'     : {'RHS Max Cyclic SENER'	: 'rhs-cyc-sener',	#1
                           'RHS Inflation SENER'	: 'rhs-inf-sener',	#2
                           'LHS Max Cyclic SENER'	: 'lhs-cyc-sener',	#3
                           'LHS Inflation SENER'	: 'lhs-inf-sener',	#4
                           'RHS Max Cyclic LE12'	: 'rhs-cyc-le12',	#5
                           'RHS Inflation LE12'		: 'rhs-inf-le12',	#6
                           'LHS Max Cyclic LE12'	: 'lhs-cyc-le12',	#7
                           'LHS Inflation LE12'		: 'lhs-inf-le12',	#8
                           'RHS Max Cyclic LE13'	: 'rhs-cyc-le13',	#9
                           'RHS Inflation LE13'		: 'rhs-inf-le13',	#10
                           'LHS Max Cyclic LE13'	: 'lhs-cyc-le13',	#11
                           'LHS Inflation LE13'		: 'lhs-inf-le13',	#12
                           'RHS Max Cyclic LE23'	: 'rhs-cyc-le23',	#13
                           'RHS Inflation LE23'		: 'rhs-inf-le23',	#14
                           'LHS Max Cyclic LE23'	: 'lhs-cyc-le23',	#15
                           'LHS Inflation LE23'		: 'lhs-inf-le23'	#16
                          },
            #FP
            'kv'        : {'Vertical Stiffness'				: 'kv',			#1
                           'Belt/Tread Portion of Vertical Stiffness'	: 'kvbelt',		#2
                           'Sidewall Portion of Vertical Stiffness'	: 'kvsidewall'		#3
                          },
            'klkt'      : {'Lateral Stiffness'				: 'kl',			#4
                           'Longitudinal Stiffness'			: 'kx',			#5
                           'Torsional Stiffness Between 0.5 and 1.5 deg': 'ktsmall',		#6
                           'Torsional Stiffness Between 0.0 and 0.3 deg': 'ktbig'		#7
                          },
            'fpc'       : {'Rib Pressure Range'				: 'rprange',		#8
                           'Rib Pressure Max'				: 'rpmax',		#9
                           'Rib Load Range'				: 'rlrange',		#10
                           'Rib Load Max'				: 'rlmax',		#11
                           'Gullwing Global Shape Factor'		: 'gullglo',		#12
                           'Gullwing  Local Shape Factor'		: 'gullloc',		#13
                           'Roundness  Shape Factor'			: 'round',		#14
                           'Squareness  Shape Factor'			: 'square',		#15
                           'Overall footprint length'			: 'fplen',		#16
                           'Overall footprint width'			: 'fpwid',		#17
                           'Total footprint contact area'		: 'fparea',		#18
                           'Coef of Variation along mean lateral'	: 'latcov',		#19
                           'FPR50'					: 'fpr50',		#20
                           'FPR80'					: 'fpr80',		#21
                           'FPR85'					: 'fpr85',		#22
                           'FPR90'					: 'fpr90',		#23
                           'FPR95'					: 'fpr95',		#24
                           'FPRminDelta'				: 'mindelfpr',		#25
                           'FPRmaxDelta'				: 'maxdelfpr'		#26
                          },
            #FAM
            'dlr'       : {'dlr'			: 'dlr',		#1 (not currently available in xml file)
                           'drr'			: 'drr',		#2 (not currently available in xml file)
                           'rpk'			: 'rpk'			#3 (not currently available in xml file)
                          },
            'cornforce' : {'Slip Angle'			: 'slipang',		#4
                           'Lateral Load'		: 'fy',			#5
                           'Aligning Moment'		: 'mz',			#6
                           'SLAT'			: 'slat',		#7
                           'Lateral Coefficient'	: 'fycoef',		#8
                           'Aligning Coefficient'	: 'mzcoef'		#9
                          },
            #RR
            'h_rr'      : {'SpindleRR'			: 'rrspind',		#1
                           'DrumSurfaceRR'		: 'rrdrumsurf',		#2
                           'FlatSurfaceRR'		: 'rrflatsurf'		#3
                          }
           }	#respKeys


