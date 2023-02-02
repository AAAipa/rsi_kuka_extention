SERVER_IP = '172.22.10.72'#'192.168.0.143'# #External PC IP
XML_FILE_NAME = "ExternalData.xml" #Not so important if you define your own default command in server.py
BUFFER_SIZE = 1024

SERVER_PORT = 59152  #PC-End Port, default 49152
CLIENT_PORT = 5005  #KRC4-End, Port, default 5005

##IPA: HEADER + DEFAULT_RKORR/DEFAULT_AKORR + FOOTER is the data to send for the Kuka Controller, to tell it how to move the robot
HEADER = '<Sen Type=\"ImFree\"><EStr>KRCnexxt - RSI Object ST_ETHERNET</EStr>'
FOOTER = '<Tech T21=\"1.09\" T22=\"2.08\" T23=\"3.07\" T24=\"4.06\" T25=\"5.05\" T26=\"6.04\" T27=\"7.03\" ' \
         'T28=\"8.02\" T29=\"9.01\" T210=\"10.00\"/><DiO>125</DiO><IPOC>0000000000</IPOC></Sen>'
DEFAULT_RKORR = '<RKorr X=\"0.0000\" Y=\"0.0000\" Z=\"0.0000\" A=\"0.0000\" B=\"0.0000\" C=\"0.0000\"/>'
DEFAULT_AKORR = '<AKorr A1=\"0.0000\" A2=\"0.0000\" A3=\"0.0000\" A4=\"0.0000\" A5=\"0.0000\" A6=\"0.0000\"/>'

# RKORR = ['X', 'Y', 'Z', 'A', 'B', 'C']
# START_STATE = {'X':'1104.9296','Y':'-341.0582','Z':'1034.1786',
#                'A':'0.0000','B':'90.0003','C':'-43.9999'}

# TEST_STATE = {'X':'1114.9296','Y':'-331.0582','Z':'1044.1786',
#                'A':'0.0000','B':'90.0003','C':'-43.9999'}

'''Optional Parameters For Broadcasting'''
BROADCAST_ROBOT_POSITION = True  #Fill the optional parameters if True
RECEIVER_IP = '172.22.10.72' #Same as SERVER_IP
RECEIVER_PORT = 49100   #Default
''' '''

TERMINAL = 'gnome-terminal' 
PYTHON = 'python3'

