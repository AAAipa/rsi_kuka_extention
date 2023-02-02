#!usr/bin/env python3
"""
Author: Yandong Wang (nick.wangyd@gmail.com)
Date: March 09, 2022

Description: This is an RSI Communicator, which can send and receive messages (commands) to the Robot Controller,
in our case it is the KRC4 and KUKA KR16-2. 

Status: Working

Dependencies: socket, multiprocessing

Known bugs: -

License: 

"""

"""
ISSUES: 

-- Multiple threads have data syncing problem. 0.05s refresh rate might be too slow. 

"""

#from cmath import inf
from Env_extend import MEM_DATA_LEN
import re
import numpy as np
import socket, os
import settings, Env_extend
from multiprocessing import Process, Pipe

import sys, signal, time
from math import floor
from decimal import Decimal
#from waiting import wait

import xml.etree.ElementTree as ET

#for class server and client
HEADER = settings.HEADER
FOOTER = settings.FOOTER
DEFAULT_RKORR = settings.DEFAULT_RKORR
DEFAULT_AKORR = settings.DEFAULT_AKORR

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
        
class client:

    def __init__(self):
        self.invalid_count = 0

    def initialize_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((settings.SERVER_IP, settings.CLIENT_PORT))
        s.listen(1)
        conn, addr = s.accept()
        return conn

    def is_terminate_command(self, input_text):
        if input_text == 'q' or input_text == 'Q':
            return True
        else:
            return False

    def process_text(self, input_text):  #TODO This is not robust at all, regex?

        text_without_spaces = input_text.replace(' ', '')  #get rid of the spaces
        string_list = text_without_spaces.split(',')
        if '' in string_list: #to drop extra ',', get num between all ','
            string_list = list(filter(lambda x: x!='', string_list))
        
        if len(string_list) == 7:
            if string_list[0] == 'r' or string_list[0] == 'a':
                coordinates = []
                for i in range(1, len(string_list)):
                    coordinates.append(float(string_list[i]))
                return string_list[0], coordinates
        else:  # Erroneous command
            return None, []


    def get_rkorr_string(self, command_list):
        command_list = map(lambda x: str(x), command_list) #map useses Iterator in py3

        return '<RKorr X=\"' + next(command_list) + '\" Y=\"' + next(command_list) + '\" Z=\"' + next(command_list) + '\" A=\"' + \
                next(command_list) + '\" B=\"' + next(command_list) + '\" C=\"' + next(command_list) + '\" />'


    def get_akorr_string(self, command_list):
        command_list = map(lambda x: str(x), command_list) #map useses Iterator in py3
        return '<AKorr A1=\"' + next(command_list) + '\" A2=\"' + next(command_list) + '\" A3=\"' + next(command_list) + '\" A4=\"' + \
            next(command_list) + '\" A5=\"' + next(command_list) + '\" A6=\"' + next(command_list) + '\" />'
        

    def create_command_string(self, type, command_list):
        if type == 'r':
            return HEADER + self.get_rkorr_string(command_list) + FOOTER
        elif type == 'a':
            return HEADER + self.get_akorr_string(command_list) + FOOTER


    def run_client(self, connection):
        sock = self.initialize_socket()
        a = ''
        print_time = 0
        while True:

            input_text = sock.recv(settings.BUFFER_SIZE)
            sock.send(b'sent')

            if input_text:
                input_text = input_text.decode('utf-8') #IPA: input text into strings, for process_text function
                type, command_list = self.process_text(input_text)
                if type is not None and len(command_list) == 6:
                    string_to_send = self.create_command_string(type, command_list)
                    string_to_send = bytes(string_to_send, 'utf-8') #IPA: stringtosend into bytes, for socket
                    
                    print_time +=1
                    if print_time%5000 == 0:
                        a += '.'
                    if len(a) >= 6:
                        a = ''
    
                    #print('Sending'+a+'     ', end='\r')
                    
                    #print (string_to_send)
                    connection.send(string_to_send)


                elif self.is_terminate_command(input_text):
                    print ("Terminating...")
                     #sock.shutdown(socket.SHUT_RDWR)     # Don't allow reads & writes
                    sock.close() 
                    return
                else:
                    print ("The command is not valid.")
                    self.invalid_count += 1
                    print(input_text)
            
class server:

    def __init__(self):
        self.robot_state = []

    def send_robot_data(self, sock, data):
        if settings.BROADCAST_ROBOT_POSITION is False:
            pass
        else:
            sock.sendto(bytes(data), (settings.RECEIVER_IP, settings.RECEIVER_PORT)) #IPA: changed data type

    def run_server(self, connection):
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket
        sock.bind((settings.SERVER_IP, settings.SERVER_PORT))
        
        default_a_command = HEADER + DEFAULT_AKORR + FOOTER
        default_a_command = bytes(default_a_command, 'utf-8') # IPA: default joints correction xml

        default_r_command = HEADER + DEFAULT_RKORR + FOOTER
        default_r_command = bytes(default_r_command, 'utf-8') # IPA: default cartesian correction xml
        
        #IPA: Get and store informations from robot
        state_log = []
        a = ''
        print_timer = 0
        while True:
            received_data, socket_of_krc = sock.recvfrom(settings.BUFFER_SIZE)
            ##to check socket_of_krc
            #print("socket_of_krc: ",socket_of_krc)
            
            self.send_robot_data(sock, received_data)
            if connection.poll():
                print_timer += 1
                if print_timer%5000 == 0:
                    a += '.'
                if len(a) >= 6:
                    a = ''
                #print('Data receiving'+a+'     ', end='\r')
                
                data_to_send = connection.recv()

            else:  # send the default
                data_to_send = default_r_command #IPA: depends on correction type (Joints or Cartesian)
            
            #state_log.append(received_data.decode('utf-8'))
            data_to_send = self.mirror_timestamp(received_data.decode('utf-8'), data_to_send.decode('utf-8')) 
            #print("data_to_send final: ",data_to_send)#check data2send format
            
            #IPA: convert received_data and data2send from bytes to strings, so that the mirror_timestamp function can work fine.
            sock.sendto(data_to_send, socket_of_krc)


    # Updates the timestamp of the data to send based on the timestamp of the received data
    def mirror_timestamp(self, received_data, data_to_send):
        ipoc_begin_index = received_data.index("<IPOC>")
        ipoc_end_index = received_data.index("</IPOC>")
        received_ipoc = str(received_data[ipoc_begin_index + 6: ipoc_end_index])
        
        self.robot_state.append(received_data) 
        #print(received_data) #IPA: print current state of robot
        old_ipoc_begin_index = data_to_send.index("<IPOC>")
        old_ipoc_end_index = data_to_send.index("</IPOC>")
        old_ipoc = data_to_send[old_ipoc_begin_index + 6: old_ipoc_end_index]

        return bytes(data_to_send.replace("<IPOC>" + old_ipoc + "</IPOC>", "<IPOC>" + received_ipoc + "</IPOC>"), 'utf-8')#IPA: convert datatosend into bytes before sending to socket

class RSI_Communicator:
    def __init__(   self,
                    PACE = 0.025,
                    PACE_MAX = 0.05,
                    refresh_rate =  0.004, #tested for tcp_sender
                    buffer_size = settings.BUFFER_SIZE,
                    server_ip = settings.SERVER_IP,
                    server_port = settings.SERVER_PORT,
                    client_port = settings.CLIENT_PORT,
                    dataLoader = None,
                    data_method = 'memcache',
                    CS = 'BASE', #Reference Coordinate System: BASE (WORLD), TCP
                    len_avg_data = 5,                    
                    ):
        if dataLoader is None:
            from DataLoader import DataLoader as dataLoader
            
        self.dataloader = dataLoader(method=data_method, len_avg_data=len_avg_data)
        self.CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
        self.LOG_PATH = os.path.join(self.CURRENT_PATH, 'Data')
        if not os.path.exists(self.LOG_PATH):
            os.mkdir(self.LOG_PATH)
            
        self.robot_state_file_location = os.path.join(self.LOG_PATH, 'end_pos.json')
        #print(os.path.join(self.LOG_PATH, 'end_pos.txt'))
        #print(self.robot_state_file_location)

        self.CS = CS
        self.PACE = PACE
        self.PACE_MAX = PACE_MAX
        self.refresh_rate = refresh_rate
        self.isdone = False
        self.ROBOT_STATE = self.process_robot_state(self.robot_state_file_location) if os.path.exists(self.robot_state_file_location) else False
        self.state_length = 10000 
        #cartesian start state 
        self.RKORR = Env_extend.RKORR #list
        self.START_STATE = Env_extend.START_STATE #dict
        #server and client
        self.parent_connection, self.child_connection = Pipe()
        self.server, self.client = server(), client()
        self.server_port, self.client_port  = server_port, client_port
        self.server_ip = server_ip

        self.buffer_size = buffer_size #defines the rate of communication between PC and robot
        
        

    def quit(self,signum, frame):
        print("\nKillng Everything...")
        print('\nInvalid commands: %d'%self.client.invalid_count)
        #print('Start pos:\n', self.start_pos)
        #print('End_pos:\n', self.end_pos)
        sys.exit()

    def connect(self): 
    #Need to be able to pass the state of robotand ROS sensors (force torque) data to the Enviroment 
        try:
            signal.signal(signal.SIGINT, self.quit)
            signal.signal(signal.SIGTERM, self.quit)

            server_process = Process(target=self.server.run_server, args=(self.parent_connection, ))
            server_process.start()
            #server_thread = threading.Thread(target=self.server.run_server, args=(self.parent_connection, ))
            #server_thread.setDaemon(True)
            #server_thread.start()
            print("Build RSI Connection successfully! ")
            self.client.run_client(self.child_connection)
            #client_process = Process(target=self.run_client)
            # client_thread = threading.Thread(target=self.client.run_client,args=(self.child_connection, self.refresh_rate,))
            # client_thread.setDaemon(True)
            # client_thread.start()
            server_process.terminate()
        
        except Exception as exc:
            print(exc)


    def tcp_sender(self, target_move=[0,0,0,0,0,0], test= True): #command should be strings or list in the right format
        TCP_IP = self.server_ip
        TCP_PORT = self.client_port
        BUFFER_SIZE = self.buffer_size
       
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))

        try: 
            while True:   
                
                if test:
                    confirm = input('[0]-Enter yourself \n[1]-Run Test \n[2]-Reset \n-->')  #could be done state from env 
                    if confirm == '0':       
                        command = input("Enter a command: ") #cartesian r,x,y,z,a,b,c
                        if '[' in list(command) or ']' in list(command):
                            command = command.split(',')
                    elif confirm == '1':
                        if isinstance(target_move, str):
                            target_move = [float(s) for s in re.split(',', target_move) if isfloat(s)]
                            print(target_move) #still has bugs
                        self.ROBOT_STATE = self.process_robot_state(self.robot_state_file_location)
                        command = self.get_reset_corr(current_state=self.ROBOT_STATE, target_move=target_move)
                    elif confirm == '2':
                        self.ROBOT_STATE = self.process_robot_state(self.robot_state_file_location)
                        #print(self.ROBOT_STATE)
                        command = self.get_reset_corr(current_state=self.ROBOT_STATE, reset=True)
                        #command = False
                    else:
                        command = False
                        
                else:
                    #action
                    command = target_move  #       
                
                if not command:
                    print('Waiting for command...')
                    time.sleep(1)

                else:
                    if isinstance(command, str):
                        command = bytes(command, 'utf-8') #IPA: turn input text into bytes, for socket
                        s.send(command)
                        message = s.recv(BUFFER_SIZE) #IPA: to receive message sent from client (b'sent')
                        #print ("Sending data...")
                        #print ('receice message: ', self.server.robot_state)
                    
                    elif isinstance(command, list):
                        print('Sending multiplle data...')
                        for i in range(len(command)):
                            command_i = bytes(command[i], 'utf-8')
                            #check if command_i contains only 6 cartesian values
                            time.sleep(self.refresh_rate) #if invalid commands show up should change this
                            s.send(command_i)
                                
                    else:
                        print('Command type wrong. Need to be strings to list.')

        except KeyboardInterrupt or self.isdone:
            print('\nClosing socket...')
            s.close() #We don't need this for training

    def get_reset_corr(self, current_state, target_move=[], reset = False, reset_wait_time = 0.5): #,target_state
        """
        bring tcp back to start position using RSI_MOVECORR. 
        for now no change of orientations of robot. 
        current_state be like ['1100.1234',-698.2333,'920.324',0,0,0]
        target_move be like [10.0, -10.0, 0.0, 0.0, 0.0, 0.0]
        get current state, xo-xi... , create a command in r,x,x,x,x,x,x

        When reset = True, the movement in z-axis direction should be executed first.
        """
            
        pace = self.PACE
        null_element = 0.000

        if reset: 
            if not current_state or float('inf') in current_state or float('-inf') in current_state:
                n, nmax = 0, 3
                while n < nmax: 
                    current_state = self.ROBOT_STATE = self.process_robot_state(self.robot_state_file_location) #update current state
                    if not current_state or float('inf') in current_state or float('-inf') in current_state:
                        print('Current state is not valid. Retrying for %d more times.'%(nmax-n))
                        time.sleep(reset_wait_time)
                    else:
                        print('Got valid state.')
                        break
                    n += 1
                
                if n >= nmax:
                    print('Cannot get valid state. No reset move executed.')
                    return 'r,0,0,0,0,0,0'
            else:
                
                target = self.START_STATE#list(self.START_STATE.values())
                #print('TARGET: ',target)
                #print('CSTATE: ',current_state)
                diff = [] 
                abs_diff = []
                #print('Target length: ',len(target), self.START_STATE)
                for j in range(len(target)-3):
                    diff_j = float(target[j])-float(current_state[j])
                    abs_diff_j = abs(float(target[j])-float(current_state[j]))
                    #diff_j = '%.4f'%diff_j
                    diff.append(diff_j)
                    abs_diff.append(abs_diff_j)
                for h in range(3):# Now cut of change of abc
                    diff.append(0.0)
                    abs_diff.append(0.0)
                #print('diff: ',diff)
            #sys.exit()
        else:
            
            diff = target_move #list of floats for move distance in each axis
            abs_diff = [abs(i) for i in diff]
            #print('diff: ',diff)
        #process current state, extract current cartesian coodinates, put them into list

        max_diff = max(abs_diff) #see if max diff is bigger than max pace
        
        if max_diff <= self.PACE_MAX:
            reset_corr = 'r,'
            #print('diff length: ',len(diff))
            for i in range(len(diff)):
                corr_i = '%.4f'%diff[i] + ','
                reset_corr += corr_i

        else: #command will be list, each element represents the move command with set pace
            ex_reminder = Decimal(str(max_diff))%Decimal(str(pace))
            ex_len = 0 if float(ex_reminder) == 0.0 else 1 #extra length of command list
            comm_len = floor(max_diff/pace) + ex_len #len of command list
            #print('Command Length: ',ex_reminder,comm_len)
            reset_corr = []
            comm_dict = {} #each step value change for the whole movement
            
            for i in range(len(diff)):
                r_i = [] #each axis change every step
                r_len = floor(float(Decimal(str(abs_diff[i]))/Decimal(str(pace)))) #length of actual comm
                r_rest = float(Decimal(str(diff[i]))%Decimal(str(pace))) #reminder
                r_pace = -pace if diff[i]<0 else pace
                #print(r_len)
                for j in range(r_len): 
                    r_i.append(r_pace) 
                if r_rest != 0.0 or r_rest != 0:
                    r_i.append(r_rest)
                
                rest_len = comm_len-len(r_i)
                if rest_len > 0:
                    for k in range(rest_len):
                        r_i.append(null_element)

                dict_i = {i:r_i}
                comm_dict.update(dict_i)
            
            #print(comm_dict)
            for i in range(comm_len):
                corr_i = 'r,'
                for j in range(len(comm_dict.keys())):
                    corr_i += '%.4f'%comm_dict[j][i] + ','
                reset_corr.append(corr_i)

        return reset_corr
        
        # else:
        #     print('No current state found.')
        #     return 'r,0,0,0,0,0,0'
        
    def state_sock_connect(self):#, connection): #connection using Pipe for environment
        
        rstate = [] 
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.server_ip, settings.RECEIVER_PORT))
        #file_location = os.path.join(self.LOG_PATH, 'end_pos.txt')
        
        print('RSI State Process connected!')
        try:
            signal.signal(signal.SIGINT, self.quit)
            signal.signal(signal.SIGTERM, self.quit)
            n = 0
            while True:
                n+=1 
                received_data, sock_of_krc = sock.recvfrom(settings.BUFFER_SIZE) #59152
                #received_data = self.process_robot_state(received_data)
                #rstate.append(received_data.decode())
                tree = ET.ElementTree(ET.fromstring(received_data.decode()))
                root = tree.getroot()
                
                tags = []
                values = []
                for child in root:
                    tags.append(child.tag)
                    if tree.find('./'+child.tag).text != None:
                        #print(tree.find('./'+child.tag).tag, tree.find('./'+child.tag).text)
                        values.append(tree.find('./'+child.tag).text)
                    else: 
                        #print(child.tag, child.attrib)
                        values.append(child.attrib)
                    
                rstate.append(dict(zip(tags, values)))
                

                if len(rstate)==1:
                    self.start_pos = rstate[0]
                    
                if len(rstate) > self.state_length: 
                    for i in range(len(rstate)-self.state_length):
                        rstate.pop(0)
                
                self.end_pos = rstate[len(rstate)-1]

                #print(len(rstate))
                if n%500 == 0:
                    print('Start pos:\n', self.start_pos, '\n')
                    print('End_pos:\n', self.end_pos, '\n')
                
                    print('Log: ',n/500,' State length:',len(rstate), '\n')


                if len(rstate) <= MEM_DATA_LEN:
                    self.dataloader.store_data(rstate, self.robot_state_file_location, tag='end_pos')
                else:
                    self.dataloader.store_data(rstate[-MEM_DATA_LEN:], self.robot_state_file_location, tag='end_pos')

        except Exception as e:
            print(e)
            sock.close()

    def process_robot_state(self, end_pos):#returns a list of x,y,z,a,b,c in float
        #end_pos = open(end_pos, 'r').read()#.decode('utf-8').split(' |" |< |> |= |\n')
        
        # cstate = []
        # tags = ['RIst', 'RSol', 'Delay', 'Tech', 'Digout']
        # tag = ''
        # count = 0 
        # #time.sleep(self.refresh_rate)
        # with open(end_pos,'r') as end_pos_file:
        #     ff = end_pos_file.read()#.split('"')
        #     ff = re.split(' |"|<|>|=|\n',ff)
        #     for ist in ff:
        #         #print(ist)
        #         if ist in tags:
        #             tag = ist
        #             if ist == 'RIst':
        #                 count += 1
                
        #         try: 
        #             if tag == 'RIst':
        #                 if count < 2:
        #                     cstate.append(float(ist))
        #                     global arr
        #                     arr = np.array(cstate)
        #                 else:
        #                     cstate.append(float(ist))
        #                     if len(cstate)%6 == 0 and len(cstate)>6:
        #                         arr2 = np.array(cstate[(count-1)*6:])
        #                         arr += arr2
        #                         #print('added')
        #             else:
        #                 continue
        #         except ValueError:
        #             continue
      
        # arr_avr = arr/count

        #cstate 
        # arr = np.array(6*[0.])#[]

        # with open(end_pos, 'r') as f:
        #     try:
        #         end_state = json.load(f)
        #     except:
        #         return False
        
        # for item in end_state:
        #     rist = np.array([float(val) for val in item['RIst'].values()])
        #     arr += rist
        
        # avr_arr = arr/len(end_state)
        data = self.dataloader.load_data(tag='end_pos')
        if data != None:
            avr_arr = np.append(data['tcp_pos'], 3*[0.])

            cstate = avr_arr.tolist()
            return cstate
        else:
            return False

        
