from settings import *


SEARCH_RADIUS = 3 #2.5#3 #2.5 2.2#mm 
ENGAGE_DISTANCE = 0.5 #0.25 #mm
SCREW_HEIGHT = 4.2 #5.65 #mm
SAFETY_HEIGHT = 844 #849.50 - (SCREW_HEIGHT*2)/3 - 0.2#mm
START_HEIGHT = -1.5 #m8: -1.5, m5: -2.0

MEM_DATA_LEN = 5
MOVE_DOWN = [0, 0, -1.2, 0, 0, 0] 
FORCE_LIMIT = 15 #N

RKORR = ['X', 'Y', 'Z', 'A', 'B', 'C']
START_STATE = [1269.50, -814.57, 863,14, 46.53, 89.80, 1.91] #m5
# [1232.2739, -724.8665, 882.1877, 46.53, 89.80, 1.91]  #M8

            #{'X':'1232.2739','Y':'-724.8665','Z':'882.1877',
            #  'A':'46.53','B':'89.80','C':'1.91'}

## Very first one
#              {'X':'1104.9296','Y':'-341.0582','Z':'1034.1786',
#                'A':'0.0000','B':'90.0003','C':'-43.9999'}

TEST_STATE = {'X':'1232.8590','Y':'-724.5880','Z':'881.8140',
              'A':'46.53','B':'89.80','C':'1.50'}


WORKPIECE_AREA = {#square area with z axis, to avoid contact with tcp
    'top': [1000.00, 1000.00, 1000.00], 
    'bottom': [800.00, 800.00, 1000.00]
}
#
#### Plate Angle: 45.14° hole distance 36 mm
TARGET_SCREWS_POS = {# positions of target screws
    #m8
    #'A': [1237.16+0.6, -742.95+0.45, 849.50], #upper surface
    'A': [1237.16-0.4, -742.95+0.2, 849.50],
    'B': [1215.72, -763.16, 849.50], #verified on 10.01.23
    'C': [1194.32, -785.24, 849.50], #verified on 14.12.22
    'D': [1173.72, -807.37+0.8, 849.50],
    'E': [1233.77, -696.94, 849.50],
    'F': [1212.56, -718.21, 849.50],
    'G': [1192.26, -739.71, 849.50],
    'H': [1170.17, -760.93, 849.50],    
    #m5
    # 'Am5': [1211.33, -697.46, 845.00],
    # 'Bm5': [1189,28, -719.35, 845.00],

    #Old Plate
    # 'A_m5': [1307.63, -791.00, 847.7], #Verified
    # 'B_m5': [1285.95, -812.77, 847.7], #Verified
    # 'C_m5': [1265.81, -833.48, 847.7], #Verified
    # 'D_m5': [1243.72, -855.60, 847.7], #Verified

    'A_m5': [1256.39, -753.38, 847.7], #Verified
    'B_m5': [1231.0, -778.90, 847.7], #Verified
    'C_m5': [1205.61, -804.42, 847.7], #Verified
    'D_m5': [1180.22, -829.94, 847.7], #Verified

    'A_m6': [1237.52, -910.75, 848.2], #Verified
    'B_m6': [1213.24, -886.96, 848.2], #Verified
    'C_m6': [1189.04, -863.41, 848.2], #Verified
    'D_m6': [1164.90, -839.39, 848.2], #Verified


}


OBSTACLES_POS = {# positions of obstacles
    '0': [0, 0, 0],
}

DATA_LIMIT = {
    'forces': [-10, 10],
    'torques': [-5,5],
    'tcp_pos': [-1000, 2000],
    'mo_torque': [-5, 5],
    'mo_cur': [-5, 5],
    'mo_temp': [10, 50],
    'phidget_signals': [0, 1],
    'movements': [-10, 10]
}


DATA_INFO = { #length of each data
    'forces': 3,
    'torques': 2,
    'tcp_pos': 3,
    'mo_torque': 6,
    'mo_cur': 6,
    'mo_temp': 6,
    'movements': 3,
    'phidget_signals': 3, 
  
}

PACE_MAP = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
###########  0     1    2    3    4    5    6  ###########

ACT_PACE = PACE_MAP[1] #RC.PACE #(0.05)

ACTION_MAP = {
    0: [ACT_PACE, 0, 0, 0, 0, 0], #'+X' [0, 0, ACT_PACE, 0, 0, 0]
    1: [-ACT_PACE, 0, 0, 0, 0, 0],#'-X' [0, 0, -ACT_PACE, 0, 0, 0]
    2: [0, ACT_PACE, 0, 0, 0, 0], #'+Y'
    3: [0, -ACT_PACE, 0, 0, 0, 0],#'-Y'
    #moving diagonally
    4: [ACT_PACE, ACT_PACE, 0, 0, 0, 0], 
    5: [-ACT_PACE, -ACT_PACE, 0, 0, 0, 0],
    6: [ACT_PACE, -ACT_PACE, 0, 0, 0, 0], 
    7: [-ACT_PACE, ACT_PACE, 0, 0, 0, 0],

    8: 'Finish' #[0, 0, -1.0, 0, 0, 0]
    #moving in z direction
    #4: , #'-Z'  # For now just x y
    #5: [0, 0, ACT_PACE, 0, 0, 0], #'+Z'
}

moving_down = -0.04
ACTION_MAP_R = {
    0: [ACT_PACE, 0, moving_down, 0, 0, 0], #'+X' [0, 0, ACT_PACE, 0, 0, 0]
    1: [-ACT_PACE, 0, moving_down, 0, 0, 0],#'-X' [0, 0, -ACT_PACE, 0, 0, 0]
    2: [0, ACT_PACE, moving_down, 0, 0, 0], #'+Y'
    3: [0, -ACT_PACE, moving_down, 0, 0, 0],#'-Y'
    #moving diagonally
    4: [ACT_PACE, ACT_PACE, moving_down, 0, 0, 0], 
    5: [-ACT_PACE, -ACT_PACE, moving_down, 0, 0, 0],
    6: [ACT_PACE, -ACT_PACE, moving_down, 0, 0, 0], 
    7: [-ACT_PACE, ACT_PACE, moving_down, 0, 0, 0],

    8: 'Finish' #[0, 0, -1.0, 0, 0, 0]
    #moving in z direction
    #4: , #'-Z'  # For now just x y
    #5: [0, 0, ACT_PACE, 0, 0, 0], #'+Z'
}



# data_removed =[ #hashtag means keep this data
#     'forces',
#     'torques',
#     'tcp_pos',
#     'mo_torque',
#     'mo_cur',
#     'mo_temp',
#     'movements',
#     'phidget_signals',
#     'last_act',
# ]

